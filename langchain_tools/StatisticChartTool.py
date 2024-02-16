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
from ext import db
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

llm_gpt4_turbo = ChatOpenAI(
    temperature=0.3,
    model_name=os.getenv("OPENAI_GPT4_MODEL_NAME"),
)

generateChartPrompt = PromptTemplate(
    input_variables=["query", "data"],
    template="""
        Let's think step by step! \n
        Acts as a Data Engineer, could you help me to implement the data analysis task on \
        '''{query}''' The output result I want you to make some charts by using highcharts.js \
        and give me an directly runnable HTML code. If the user have not provided specific \
        details about the desired analysis or visualization requirements. Just make a chart \
        such as the following example for the user ! \
        Here is the example for your reference and please use this format \
        ```html \
        <html> \
            <head> \
                <script src="https://code.highcharts.com/highcharts.js"></script> \
            </head> \
            <body> \
                <div id="chart-container-1" style="width:100%; height:500px;"></div> \
                <script> \
                    var data = [...] \
                    Highcharts.chart('chart-container-1', ...) \
                </script> \
            </body> \
        </html> \
        ``` \
        Here is the reference data you have to use: \
        {data}
        Output Result:
    """,
)


class StatisticChartTool(BaseTool):
    name = "statistic_chart"
    description = "只要知道 schema 的 uuid, 就可以使用這個工具去生成有關統計數據的圖表"

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

        sql = generateSQLByViews(
            viewsName, schema_name, query, dataSchema=dataSchema, returnSQL=True)

        print("SQL: ", sql)

        rows = db.session.execute(sql)

        extractedData = {
            "dataSchema": [],
            "data": [],
        }

        extractedData["dataSchema"] = list(rows.keys())

        for row in rows:
            extractedData["data"].append(dict(row))
            print(row)

        chain = LLMChain(llm=llm_gpt4_turbo, prompt=generateChartPrompt)
        chart = chain.run(query=query, data=extractedData)

        return chart

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")
