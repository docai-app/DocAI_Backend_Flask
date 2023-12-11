from langchain.tools import BaseTool, StructuredTool, Tool, tool
from typing import Optional, Type
import sys
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from services.document import DocumentService


class RetrivalQuestionAnswerTool(BaseTool):
    name = "retrieval_question_answer"
    # description = "這段代碼實現了名為 qaDocuments 的功能，旨在從指定文檔集合中檢索信息並回答用戶查詢。它是一個複雜的問答系統的組成部分，整合了多個組件，包括數據庫連接、文檔檢索、自然語言處理和對話管理。 功能初始化時，首先創建一個空的過濾條件字典和基於環境變量設定的語言模型實例。然後根據傳入的 metadata（可能包含文檔 ID）來構建檢索的過濾條件。進一步，它會動態生成與特定 schema 相關聯的文檔集合名稱，並使用此名稱創建 PGVector 實例進行文檔檢索。 基於 PGVector 檢索器，系統創建了兩種工具：一種用於文檔搜索，另一種用於文檔和查詢的總結。此外，代碼還創建了一個對話記憶實例來管理用戶和 AI 的對話歷史，並根據信息類型（用戶或 AI）來更新這些對話記憶。 為了引導對話代理，代碼通過整合系統消息和其他提示構建了一個提示信息。接著，它創建了一個包含語言模型和工具的對話代理。使用代理執行器來運行對話代理，處理用戶查詢，並處理打印代理的輸出，這可能包括回答和信息摘要等。 最後，系統基於更新後的對話記憶構建了包含完整對話歷史的列表，並返回代理的回答和整理後的對話歷史。這個系統的核心功能是能夠高效地從特定文檔中檢索信息，並通過自然語言處理技術生成有意義的回答，這對於需要從大量文檔中快速找到特定信息的場景特別有用。"
    description = "這個工具會提供需要的文件資訊和內容，可以回答問題，生成總結"

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""

        schema_name = self.metadata['schema']
        document_ids = self.metadata['metadata']['document_ids']
        chat_history = self.metadata['history']

        agent_res = DocumentService.qaDocuments(
            query, schema_name, {'document_id': document_ids}, chat_history)
        return agent_res

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")
