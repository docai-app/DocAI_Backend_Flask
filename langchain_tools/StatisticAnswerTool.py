from langchain.tools import BaseTool, StructuredTool, Tool, tool
from typing import Optional, Type
import sys
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

from utils.generate import generateSQLByViews
from langchain import SQLDatabase
import os
import json
import ast


class StatisticAnswerTool(BaseTool):
    name = "statistic_answer"
    description = "只要知道 schema 的 uuid, 就可以使用這個工具去回答有關統計數據的問題"

    def read_dataSchema_from_database(self, tenant, schema_uuid):
        pgdb = SQLDatabase.from_uri(os.getenv("DATABASE_URL"))
        result = pgdb.run("""
                               select schema from \"{tenant}\".\"smart_extraction_schemas\" where id ='{schema_uuid}'
                               """.format(tenant=tenant, schema_uuid=schema_uuid))

        print(" -- read from database dataSchema --")
        array = ast.literal_eval(result)
        print(array)
        return array[0][0]

    def _run(
        self,
        query: str,
        schema_uuid: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        viewsName = f"smart_extraction_schema_{schema_uuid}"

        schema_name = self.metadata['schema']
        dataSchema = self.read_dataSchema_from_database(
            schema_name, schema_uuid)

        agent_res = generateSQLByViews(
            viewsName, schema_name, query, dataSchema=dataSchema, returnSQL=False)
        return agent_res

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")
