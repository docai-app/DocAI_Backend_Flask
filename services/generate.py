import os
import pickle
from unittest import result
import uuid
from azure.storage.blob import BlobServiceClient, ContentSettings
from database.services.Documents import DocumentsQueryService
from services.database import DatabaseService
from services.ocr import OCRService
from utils.utils import getExtension
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.chains import SimpleSequentialChain
from dotenv import load_dotenv

connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
container = os.getenv('AZURE_STORAGE_CONTAINER')

llm = ChatOpenAI(temperature=0.9, openai_api_key=os.getenv(
    "OPENAI_API_ACCESS_TOKEN"), model_name=os.getenv("OPENAI_MODEL_NAME"))

summaryFormDataPrompt = PromptTemplate(
    input_variables=["query", "content"],
    template="""
        Acts as a Data Engineer, could you help me to summarize the reference data to match \
        the description about '''{query}'''. You only extract the necessary data and process \
        them to match the demand description. The unnecessary data you have to remove them. \
        You may have to do some calculation to summarize the data if you meet the statistics \
        scenario. \
        Use the Markdown format such as table or anything to output the summarize result. \
        Summary Data: 'xxx' \
        Here is the reference data you need to summarize: \
        '''{content}'''
        Summary Data:
    """,
)

generateChartPrompt = PromptTemplate(
    input_variables=["query", "summarizedData"],
    template="""
        Acts as a Data Engineer, could you help me to implement the data analysis task on \
        '''{query}''' The output result I want you to make a chart by using highcharts.js and \
        give me an directly runnable HTML file!
        Use the format \
        ```html \
        <html> \
            <head> \
                <script src="https://code.highcharts.com/highcharts.js"></script> \
            </head> \
            <body> \
                <div id="container" style="width:100%; height:500px;"></div> \
            </body> \
        </html> \
        ``` \
        Here is the reference data you have to use: \
        {summarizedData}
        Output Result:
    """,
)


class GenerateService:
    @ staticmethod
    def generateChart(query, content):
        chain1 = LLMChain(llm=llm, prompt=summaryFormDataPrompt)
        summarizedData = chain1.run(query=query, content=content)
        print(summarizedData)
        print("----------------------")

        chain2 = LLMChain(llm=llm, prompt=generateChartPrompt)
        chart = chain2.run(query=query, summarizedData=summarizedData)
        print(chart)
        print("----------------------")
        
        return chart
