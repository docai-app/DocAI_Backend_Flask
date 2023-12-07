from langchain.tools import BaseTool, StructuredTool, Tool, tool
from typing import Optional, Type

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from services.document import DocumentService


class RetrivalQuestionAnswerTool(BaseTool):
    name = "retrival_question_answer"
    description = "use this tool for retrival question answering"

    def __init__(self, query, schema_name, document_ids, additional_param=''):
        super().__init__()
        self.schema_name = schema_name
        self.query = query
        self.document_ids = document_ids
        self.additional_param = additional_param

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        agent_res = DocumentService.qaDocuments(
            query, self.environment, {'document_id': self.document_ids}, self.additional_param)
        return agent_res

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")
