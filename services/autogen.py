from langchain_tools.RetrivalQuestionAnswerTool import RetrivalQuestionAnswerTool
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.llms import OpenAI
from langchain.agents import Tool
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os

from langchain_tools.SmartExtractionSchemaSelectionTool import SmartExtractionSchemaSelectionTool

import autogen

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        "model": ["gpt-4-1106-preview", "gpt-4", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"],
    },
)


class AutogenSerivce:
    @staticmethod
    def chat(query, schema_name, metadata, smart_extraction_schemas, chat_history):
        llm = OpenAI(openai_api_key=os.getenv(
            "OPENAI_API_KEY"), temperature=0.6)

        # rqat = RetrivalQuestionAnswerTool(
        #     query, schema_name, metadata["document_ids"], chat_history)

        sesst = SmartExtractionSchemaSelectionTool(
            query, schema_name, smart_extraction_schemas, chat_history)

        tools = load_tools([], llm=llm)

        # tools.append(rqat)
        tools.append(sesst)

        agent = initialize_agent(
            tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

        return agent.run(query)
