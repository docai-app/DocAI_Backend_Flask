import os
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from ext import db


connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
container = os.getenv('AZURE_STORAGE_CONTAINER')

llm = ChatOpenAI(temperature=0.3, openai_api_key=os.getenv(
    "OPENAI_API_ACCESS_TOKEN"), model_name=os.getenv("OPENAI_MODEL_NAME"))

summaryFormDataPrompt = PromptTemplate(
    input_variables=["query", "content"],
    template="""
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
        Acts as a Data Engineer, could you help me to implement the data analysis task on \
        '''{query}''' The output result I want you to make some charts by using highcharts.js \
        and give me an directly runnable HTML code. If the user have not provided specific \
        details about the desired analysis or visualization requirements. Just make three charts \
        such as the following example for the user ! \
        Here is the example for your reference and please use this format \
        ```html \
        <html> \
            <head> \
                <script src="https://code.highcharts.com/highcharts.js"></script> \
            </head> \
            <body> \
                <div id="chart-container-1" style="width:100%; height:500px;"></div> \
                <div id="chart-container-2" style="width:100%; height:500px;"></div> \
                <div id="chart-container-3" style="width:100%; height:500px;"></div> \
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
    # template="""
    #     Acts as a Data Engineer, could you help me to implement the data analysis task on \
    #     '''{query}''' The output result I want you to make some charts by using highcharts.js \
    #     and give me an directly runnable HTML code. If the user have not provided specific \
    #     details about the desired analysis or visualization requirements. Just make three charts \
    #     such as the following example for the user ! \
    #     Here is the example for your reference and please use this format \
    #     ```html \
    #     <html> \
    #         <head> \
    #             <script src="https://code.highcharts.com/highcharts.js"></script> \
    #         </head> \
    #         <body> \
    #             <div id="chart-container-1" style="width:100%; height:500px;"></div> \
    #             <div id="chart-container-2" style="width:100%; height:500px;"></div> \
    #             <div id="chart-container-3" style="width:100%; height:500px;"></div> \
    #             <script> \
    #                 var data = [...] \
    #                 Highcharts.chart('chart-container', \
    #                     {{ \
    #                         title: {{ \
    #                             text: 'Sales of petroleum products March, Norway', \
    #                             align: 'left' \
    #                         }}, \
    #                         xAxis: {{ \
    #                             categories: ['Jet fuel', 'Duty-free diesel', 'Petrol', 'Diesel', 'Gas oil'] \
    #                         }}, \
    #                         yAxis: {{ \
    #                             title: {{ \
    #                                 text: 'Million liters' \
    #                             }} \
    #                         }}, \
    #                         tooltip: {{ \
    #                             valueSuffix: ' million liters' \
    #                         }}, \
    #                         plotOptions: {{ \
    #                             series: {{ \
    #                                 borderRadius: '25%' \
    #                             }} \
    #                     }}, \
    #                     series: [{{
    #                                 type: 'column', \
    #                                 name: '2020', \
    #                                 data: [59, 83, 65, 228, 184] \
    #                             }}, {{
    #                                 type: 'column', \
    #                                 name: '2021', \
    #                                 data: [24, 79, 72, 240, 167] \
    #                             }}, {{
    #                                 type: 'column', \
    #                                 name: '2022', \
    #                                 data: [58, 88, 75, 250, 176] \
    #                             }}, {{
    #                                 type: 'spline', \
    #                                 name: 'Average', \
    #                                 data: [47, 83.33, 70.66, 239.33, 175.66], \
    #                                 marker: {{ \
    #                                     lineWidth: 2, \
    #                                     lineColor: Highcharts.getOptions().colors[3], \
    #                                     fillColor: 'white' \
    #                                 }} \
    #                             }}, {{
    #                         type: 'pie', \
    #                         name: 'Total', \
    #                         data: [{{
    #                             name: '2020', \
    #                             y: 619, \
    #                             color: Highcharts.getOptions().colors[0], \
    #                             dataLabels: {{ \
    #                                 enabled: true, \
    #                                 distance: -50, \
    #                                 format: '{{point.total}} M', \
    #                                 style: {{ \
    #                                     fontSize: '15px' \
    #                                 }} \
    #                             }} \
    #                         }}, {{ \
    #                             name: '2021', \
    #                             y: 586, \
    #                             color: Highcharts.getOptions().colors[1] \
    #                         }}, {{
    #                             name: '2022', \
    #                             y: 647, \
    #                             color: Highcharts.getOptions().colors[2] \
    #                         }}], \
    #                         center: [75, 65], \
    #                         size: 100, \
    #                         innerSize: '70%', \
    #                         showInLegend: false, \
    #                         dataLabels: {{ \
    #                             enabled: false \
    #                         }} \
    #                     }}] \
    #                 }}); \
    #             </script> \
    #         </body> \
    #     </html> \
    #     ``` \
    #     Here is the reference data you have to use: \
    #     '''{data}'''
    #     Output Result: \
    # """
)


class GenerateService:
    @ staticmethod
    def generateChart(query, content):
        chain1 = LLMChain(llm=llm, prompt=summaryFormDataPrompt)
        summarizedData = chain1.run(query=query, content=content)
        print(summarizedData)
        print("----------------------")

        chain2 = LLMChain(llm=llm, prompt=generateChartPrompt)
        chart = chain2.run(query=query, data=summarizedData)
        print(chart)
        print("----------------------")

        return chart

    @staticmethod
    def generateChartFromDBData(viewsName, tenant, query, dataSchema=None):
        extractedData = {
            "dataSchema": [],
            "data": [],
        }
        dataSchemaString = ', '.join(dataSchema.keys())
        llm2 = OpenAI(temperature=0, openai_api_key=os.getenv(
            "OPENAI_API_ACCESS_TOKEN"), model_name=os.getenv("OPENAI_MODEL_NAME"))

        QUERY = """
                Given an input question, first create a syntactically correct postgresql query to run, 
                this query can only access the table named \"{tenant}\".\"{viewsName}\", 
                \"{tenant}\".\"{viewsName}\" schema has many columns named {dataSchemaString} and uploaded_at, 
                then look at the results of the query and return the answer. Don't add the LIMIT amount on the SQLQuery result! 
                Use the following format: 

                Question: Question here 
                SQLQuery: SQL Query to run only on the \"{tenant}\".\"{viewsName}\" table 
                SQLResult: Result of the SQLQuery 
                Answer: Final answer here 

                {query}
                """.format(query=query, viewsName=viewsName, tenant=tenant, dataSchemaString=dataSchemaString)

        print("Query: ", QUERY)

        pgdb = SQLDatabase.from_uri(os.getenv("DATABASE_URL"))

        db_chain = SQLDatabaseChain(
            llm=llm2, database=pgdb, verbose=True, return_sql=True)

        print("DB Chain: ", db_chain)

        result = db_chain.run(QUERY)

        print("Result: ", result)

        rows = db.session.execute(result)

        extractedData['dataSchema'] = list(rows.keys())

        for row in rows:
            extractedData['data'].append(dict(row))
            print(row)

        print(extractedData)

        chain = LLMChain(llm=llm, prompt=generateChartPrompt)
        chart = chain.run(query=query, data=extractedData)
        print(chart)
        print("----------------------")

        return chart
