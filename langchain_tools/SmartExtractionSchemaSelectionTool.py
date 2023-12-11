from langchain.tools import BaseTool, StructuredTool, Tool, tool
from typing import Optional, Type

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate


def smart_extraction_schema_selector(query, smart_extraction_schemas):
    prompt_template = "What is a good name for a company that makes {product}?"
    llm = OpenAI(temperature=0)
    llm_chain = LLMChain(
        llm=llm, prompt=PromptTemplate.from_template(prompt_template))
    return llm_chain.run("colorful socks")


class SmartExtractionSchemaSelectionTool(BaseTool):
    name = "smart_extraction_schema_selection"
    description = "當問到有關統計上的問題時，需要先在相關的 schema 中選擇一個最相關的 schema 來回答問題"

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        agent_res = smart_extraction_schema_selector(
            query, self.metadata['smart_extraction_schemas'])
        return agent_res

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")
