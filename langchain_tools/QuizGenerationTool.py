from langchain.tools import BaseTool, StructuredTool, Tool, tool
from typing import Optional, Type
import sys
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from services.document import DocumentService
from database.pgvector import PGVectorDB
from langchain_community.chat_models import ChatOpenAI
import os
import json
from langchain.vectorstores.pgvector import PGVector
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.schema.messages import SystemMessage
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent

from langchain.agents import AgentExecutor


class QuizGenerationTool(BaseTool):
    name = "quiz_generation_tool"
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
        result_coult = 8
        llm = ChatOpenAI(model_name=os.getenv("OPENAI_MODEL_NAME"), temperature=0.2)

        # if "document_id" in metadata:
        #     filter["document_id"] = {"in": [str(i) for i in metadata["document_id"]]}

        filter["document_id"] = {"in": [str(i) for i in document_ids]}

        COLLECTION_NAME = "DocAI_Documents_{schema}_Collection".format(schema=schema_name)

        print(COLLECTION_NAME)

        store = PGVector(
            collection_name=COLLECTION_NAME,
            connection_string=DocumentService.CONNECTION_STRING,
            embedding_function=DocumentService.embeddings,
        )

        retriever = store.as_retriever(
            search_kwargs={"filter": filter, "k": result_coult}
        )

        search_documents_tool = create_retriever_tool(
            retriever,
            "random_retrieval",
            "Randomly retrieve and select some documents from the retrieved data.",
        )
        tools = [search_documents_tool]

        # print("sys message: ")
        # print(system_message)
        # print(system_message_from_expert)

        system_message = SystemMessage(
            content=(
                "Feel free to use any tools available to look up. "
                "The generated question must ask the key point of the each retrieved data. "
                "Try your best to generate 1 question!"
            )
        )

        # system_message = SystemMessage(
        #     content=system_message_from_expert
        # )

        prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=system_message,
        )

        # import pdb
        # pdb.set_trace()

        agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)

        agent_executor = AgentExecutor(
            agent=agent, tools=tools, verbose=True, return_intermediate_steps=True
        )

        agent_res = agent_executor(
            {
                "input": '"请确保您的题目紧密相关于文件内容，并能够反映出文件的主要观点或知识点。题目应包含四个选项（A、B、C、D），其中只有一个选项是正确的，並且應該隨時分佈，不能是以上全對或以上全錯"。\n\nCould you please generate some summary questions related to the retrieved documents to help the readers understand the content easily? The output result is a JSON object string and the format must be like this: ```{"question": "[the question description]", "options": [{"A": ""}, {"B": ""}, {"C": ""}, {"D": ""}], "answer": "[the answer]"}```'
            }
        )

        return agent_res

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")
