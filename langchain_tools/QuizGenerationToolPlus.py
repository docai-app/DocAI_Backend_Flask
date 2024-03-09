from langchain.tools import BaseTool, StructuredTool, Tool, tool
from typing import Optional, Type
import sys
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
import os
import json
from openai import OpenAI
from langchain_core.documents import Document


from database.services.Embeddings import EmbeddingsQueryService

openai = OpenAI()


def generate_mc_question_from_embedding(input_text):
    # 构造prompt文本，包括system message和实际的问题内容

    output_format = {"questions": [{"question": "[the question description]", "options": [{"A": ""}, {"B": ""}, {"C": ""}, {
        "D": ""}], "answer": "[the answer]", "type": "multiple_choice_question"}], "response_type": "multiple_choice_question"}

    # 将对象转换为JSON字符串，并将双引号转义
    output_format_str = json.dumps(output_format).replace('"', '\\"')

    prompt_text = f'''
    System Message: 
    Feel free to use any tools available to look up.
    The generated question must ask the key point of the each retrieved data.
    Try your best to generate only 1 question!
    
    根据以下内容出题：
    {input_text}
    请确保您的题目紧密相关于文件内容，并能够反映出文件的主要观点或知识点。题目应包含四个选项（A、B、C、D），其中只能有一个选项是正确的單選題，並且應該隨機分佈，不能是以上全對或以上全錯"。\n\nCould you please generate some summary questions related to the retrieved documents to help the readers understand the content easily? The output result is a JSON object string and the format must be like this: {output_format_str}
    
    '''

    response = openai.chat.completions.create(
        model=os.getenv("OPENAI_MODEL_NAME"),  # 或者其他可用的模型
        messages=[{"role": "user", "content": prompt_text}],
        stream=False
    )

    # 返回生成的文本
    return response.choices[0].message.content


class QuizGenerationToolPlus(BaseTool):
    name = "quiz_generation_tool_plus"
    description = "這個工具會提供需要的文件資訊和內容，生成選擇題，用作測驗"

    def _run(
        self,
        query: str,
        schema_uuid: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""

        schema_name = self.metadata['schema']
        document_ids = self.metadata['metadata']['document_ids']
        chat_history = self.metadata['history']
        system_message_from_expert = self.metadata['expert']['system_message'] or ''

        filter = {}
        filter["document_id"] = {"in": [str(i) for i in document_ids]}

        COLLECTION_NAME = "DocAI_Documents_{schema}_Collection".format(schema=schema_name)

        print(COLLECTION_NAME)

        langchain_pg_embeddings = EmbeddingsQueryService.get_random_embedding_by_ids(
            self.metadata['document_ids'], limit)

        documents = [Document(page_content=embedding.document, metadata={
                              "custom_id": embedding.custom_id}) for embedding in langchain_pg_embeddings]

        return agent_res

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")
