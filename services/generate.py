import os
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from ext import db
from utils.generate import generateSQLByViews
from dotenv import load_dotenv

load_dotenv()

connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container = os.getenv("AZURE_STORAGE_CONTAINER")

llm = ChatOpenAI(
    temperature=0.3,
    model_name=os.getenv("OPENAI_MODEL_NAME"),
)

llm_gpt4_turbo = ChatOpenAI(
    temperature=0.3,
    model_name=os.getenv("OPENAI_GPT4_MODEL_NAME"),
)

summaryFormDataPrompt = PromptTemplate(
    input_variables=["query", "content"],
    template="""
        Let's think step by step! \n
        Acts as a Data Engineer, could you help me to summarize the reference data to match \
        the description about '''{query}''' by highcharts. You can only extract the necessary \
        data from the reference data and extract them to match the demand description. \
        Maybe, you have to do some calculation to summarize the data if you meet the statistics \
        scenario. \
        Use the json format to output the summarize result. \
        Summary Data: {{ data: []}}
        Here is the reference data you need to summarize: \
        '''{content}'''
        Output Result:
    """,
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

generateStatisticsPrompt = PromptTemplate(
    input_variables=["query", "data"],
    template="""
        Let's think step by step! \n
        Acts as a Statistics Engineer, could you help me to generate the statistics detailed report \
        by using the user's query: '''{query}'''? The output result I just want you to write the \
        detailed text report. You have better to make it very detailed and clear. \
        Here is the reference data you have to use: \
        ```{data}``` \
        Use the user's query language (繁體中文) to generate the statistics detailed report. \
        Output Result: \
    """,
)

# generateSimpleStatisticsPrompt = PromptTemplate(
#     input_variables=["query", "data"],
#     template="""
#         Let's think step by step! \n
#         Acts as a Statistics Engineer, could you help me to generate the statistics simple report \
#         by using the user's query: '''{query}'''? The output result I just want you to write the \
#         simple text listed format report. You have better to make it very simple list and clear. \
#         Here is the reference data you have to use: \
#         ```{data}``` \
#         Use the user's query language (繁體中文) to generate the statistics detailed report. \
#         Output Result: \
#     """,
# )

generateSimpleStatisticsPrompt = PromptTemplate(
    input_variables=["query", "data"],
    template="""
        Let's think step by step! \n
        Acts as a Statistics Engineer, could you help me to generate the statistics simple result \
        by using the user's query: '''{query}'''? The output result I just want you to write the \
        summary result. You have better to make it very simple and clear. \
        Here is the reference data you have to use: \
        ```{data}``` \
        Use the user's query language (繁體中文) to generate the statistics result. \
        Output Result: \
    """,
)


class GenerateService:
    @staticmethod
    def generateChart(query, content):
        chain1 = LLMChain(llm=llm_gpt4_turbo, prompt=summaryFormDataPrompt)
        summarizedData = chain1.run(query=query, content=content)
        print(summarizedData)
        print("----------------------")

        chain2 = LLMChain(llm=llm_gpt4_turbo, prompt=generateChartPrompt)
        chart = chain2.run(query=query, data=summarizedData)
        print(chart)
        print("----------------------")

        return chart

    @staticmethod
    def generateChartFromDBData(viewsName, tenant, query, dataSchema=None, schema=None):
        try:
            extractedData = {
                "dataSchema": [],
                "data": [],
            }

            sql = generateSQLByViews(viewsName, tenant, query, schema)

            print("SQL: ", sql)

            rows = db.session.execute(sql)

            extractedData["dataSchema"] = list(rows.keys())

            for row in rows:
                extractedData["data"].append(dict(row))
                print(row)

            print(extractedData)

            chain = LLMChain(llm=llm_gpt4_turbo, prompt=generateChartPrompt)
            chart = chain.run(query=query, data=extractedData)
            print(chart)
            print("----------------------")

            return (chart, sql, 1)
        except Exception as e:
            print("Error: ", e)
            return (str(e), "", 0)

    @staticmethod
    def generateStatisticsFromDBData(
        viewsName, tenant, query, dataSchema=None, schema=None
    ):
        try:
            extractedData = {
                "dataSchema": [],
                "data": [],
            }

            sql = generateSQLByViews(viewsName, tenant, query, schema)

            print("SQL: ", sql)

            rows = db.session.execute(sql)

            extractedData["dataSchema"] = list(rows.keys())

            for row in rows:
                extractedData["data"].append(dict(row))
                print(row)

            print(extractedData)

            chain = LLMChain(llm=llm_gpt4_turbo, prompt=generateSimpleStatisticsPrompt)
            report = chain.run(query=query, data=extractedData)
            print(report)
            print("----------------------")

            return (report, sql, 1)
        except Exception as e:
            print("Error: ", e)
            return (str(e), "", 0)
