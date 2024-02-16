import re
from concurrent.futures import ThreadPoolExecutor

from openai import OpenAI

from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

import replicate
import os, uuid
import json
import requests

load_dotenv()

BOOK_TEXT_PROMPT = """
Write an engaging, great 3-6 page children's picture book. Each page should have 2-3 sentences. There should be rhymes.
We will be adding pictures of the environment/scenery for each page, so pick a pretty setting/place. Limit of 6 pages,
do not exceed 4 sentences per page. Do not exceed 6 pages.

Before the story begins, write a "Page 0: {title}" page. The title should be the name of the book, no more than four words.


Format like: Page 0: {title}, Page 1: {text}, etc. Do not write anything else. 
"""

get_visual_description_function = [
    {
        "name": "get_passage_setting",
        "description": "Generate and describe the visuals of a passage in a book. Visuals only, no characters, plot, or people. Highly detailed",
        "parameters": {
            "type": "object",
            "properties": {
                "base_setting": {
                    "type": "string",
                    "description": "The base setting of the passage, e.g. ancient Rome, Switzerland, etc.",
                },
                "setting": {
                    "type": "string",
                    "description": "The detailed visual setting of the passage, e.g. a a snowy mountain village",
                },
                "time_of_day": {
                    "type": "string",
                    "description": "The detailed time of day of the passage, e.g. nighttime, daytime, dawn.",
                },
                "weather": {
                    "type": "string",
                    "description": "The detailed weather of the passage, eg. heavy rain with dark clouds.",
                },
                "key_elements": {
                    "type": "string",
                    "description": "The detailed key visual elements of the passage, eg colorful houses, a church, and a lake. ",
                },
                "specific_details": {
                    "type": "string",
                    "description": "The detailed specific visual details of the passage, eg lake reflecting the sky.",
                },
            },
            "required": [
                "base_setting",
                "setting",
                "time_of_day",
                "weather",
                "key_elements",
                "specific_details",
            ],
        },
    }
]

get_lighting_and_atmosphere_function = [
    {
        "name": "get_lighting_and_atmosphere",
        "description": "Generate a  highly detailed visual description of the overall atmosphere and color palette of a book",
        "parameters": {
            "type": "object",
            "properties": {
                "lighting": {
                    "type": "string",
                    "description": "The lighting atmosphere of the book, eg. cheerful atmosphere",
                },
                "mood": {
                    "type": "string",
                    "description": "The mood of the book, eg. lively mood",
                },
                "color_palette": {
                    "type": "string",
                    "description": "The color palette of the book, eg. bright and vivid color palette",
                },
            },
            "required": ["lighting", "mood", "color_palette"],
        },
    }
]


class BuildBook:  # The do-it-all class that builds the book (and creates streamlit elements!)
    book_text_prompt = BOOK_TEXT_PROMPT

    def __init__(self, model_name, input_text, style):
        self.chat = ChatOpenAI(model_name=model_name)
        self.openai = OpenAI()
        self.input_text = input_text
        self.style = style

        self.book_text = self.get_pages()
        self.book_id = str(uuid.uuid4())

        self.pages_list = self.get_list_from_text(self.book_text)

        self.sd_prompts_list = self.get_prompts()

        self.source_files = self.download_images()
        self.list_of_tuples = self.create_list_of_tuples()

    def get_pages(self):
        pages = self.chat(
            [HumanMessage(content=f"{self.book_text_prompt} Topic: {self.input_text}")]
        ).content
        return pages

    def get_prompts(self):
        base_atmosphere = self.chat(
            [
                HumanMessage(
                    content=f"Generate a visual description of the overall lightning/atmosphere of this book using the function."
                    f"{self.book_text}"
                )
            ],
            functions=get_lighting_and_atmosphere_function,
        )
        base_dict = func_json_to_dict(base_atmosphere)

        summary = self.chat(
            [
                HumanMessage(
                    content=f"Generate a concise summary of the setting and visual details of the book"
                )
            ]
        ).content

        base_dict["summary_of_book_visuals"] = summary

        def generate_prompt(page, base_dict):
            prompt = self.chat(
                [
                    HumanMessage(
                        content=f"General book info: {base_dict}. General style: {self.style} Passage: {page}."
                        f" Generate a visual description of the passage using the function."
                        f"Creatively fill all parameters with guessed/assumed values if they are missing."
                    )
                ],
                functions=get_visual_description_function,
            )
            return func_json_to_dict(prompt)

        with ThreadPoolExecutor(max_workers=10) as executor:
            prompt_list = list(
                executor.map(
                    generate_prompt, self.pages_list, [base_dict] * len(self.pages_list)
                )
            )

        prompts = prompt_combiner(prompt_list, base_dict, self.style)

        return prompts

    def get_list_from_text(self, text):
        new_list = re.split("Page \d+:", text)
        new_list.pop(0)
        return new_list

    def generate_image_with_openai(self, i, prompt):
        try:
            client = OpenAI()
            print(f"{prompt} is the prompt for page {i + 1}")
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1792x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            print(f"Page {i + 1} image url: {image_url}")
            return image_url
        except Exception as e:
            print(e)
            pass

    def create_images(self):
        if len(self.pages_list) != len(self.sd_prompts_list):
            raise ValueError("Pages and Prompts do not match")

        print("Generating images...")

        image_urls = []
        # for i, prompt in enumerate(self.sd_prompts_list):
        #     image_url = self.generate_image_with_openai(i, prompt)
        #     image_urls.append(image_url)

        # def generate_image(i, prompt):
        #     print(f"{prompt} is the prompt for page {i + 1}")
        #     output = replicate.run(
        #         "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf",
        #         input={
        #             "prompt": "art," + prompt,
        #             "negative_prompt": "photorealistic, photograph, bad anatomy, blurry, gross,"
        #             "weird eyes, creepy, text, words, letters, realistic",
        #         },
        #     )
        #     print("Page {i} image url: ".format(i=i + 1) + output[0])
        #     return output[0]

        def generate_image_with_openai(i, prompt):
            try:
                client = OpenAI()
                print(f"{prompt} is the prompt for page {i + 1}")
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                image_url = response.data[0].url
                print(f"Page {i + 1} image url: {image_url}")
                return image_url
            except Exception as e:
                print(e)
                pass

        with ThreadPoolExecutor(max_workers=10) as executor:
            image_urls = list(
                executor.map(
                    # generate_image,
                    generate_image_with_openai,
                    range(len(self.sd_prompts_list)),
                    self.sd_prompts_list,
                )
            )
            print(image_urls)

        return image_urls

    def download_images(self):
        image_urls = self.create_images()
        # print(image_urls)
        source_files = []
        for i, url in enumerate(image_urls):
            r = requests.get(url, stream=True)
            file_path = f"images/{self.book_id}_{i+1}.png"
            with open(file_path, "wb") as file:
                source_files.append(file_path)
                for chunk in r.iter_content():
                    file.write(chunk)
        return source_files

    def create_list_of_tuples(self):
        files = self.source_files
        text = self.pages_list
        return list(zip(files, text))


def func_json_to_dict(response):
    return json.loads(response.additional_kwargs["function_call"]["arguments"])


def prompt_combiner(prompt_list, base_dict, style):
    prompts = []
    for i, prompt in enumerate(prompt_list):
        entry = (
            f"{prompt['base_setting']}, {prompt['setting']}, {prompt['time_of_day']}, {prompt['weather']}, {prompt['key_elements']}, {prompt['specific_details']}, "
            f"{base_dict['lighting']}, {base_dict['mood']}, {base_dict['color_palette']}, in the style of {style}"
        )
        prompts.append(entry)
    return prompts


def process_page(chat, page, base_dict):
    prompt = chat(
        [HumanMessage(content=f"General book info: {base_dict}. Passage: {page}")],
        functions=get_visual_description_function,
    )
    return func_json_to_dict(prompt)
