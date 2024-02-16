import os
from langchain.prompts import PromptTemplate
# from langchain_community.llms import OpenAI
from experimental.llms.openai import OpenAI

from langchain.chains import LLMChain
from langchain import SQLDatabase
# from langchain_experimental.sql import SQLDatabaseChain
from experimental.sql import SQLDatabaseChain
# from langchain.chains.sql_database.base import SQLDatabaseChain
from ext import db
from dotenv import load_dotenv
from datetime import date

load_dotenv()


def generateSQLByViews(viewsName, tenant, query, dataSchema=None, returnSQL=True):
    llm2 = OpenAI(temperature=0, model_name=os.getenv("OPENAI_MODEL_NAME"))

    if isinstance(viewsName, list):
        include_table_names = viewsName
    elif isinstance(viewsName, str):
        include_table_names = [viewsName]

    pgdb = SQLDatabase.from_uri(
        os.getenv("DATABASE_URL"),
        schema=tenant,
        include_tables=include_table_names,
        view_support=True,
    )

    if isinstance(viewsName, list):
        include_table_names = viewsName
    elif isinstance(viewsName, str):
        include_table_names = [viewsName]

    pgdb = SQLDatabase.from_uri(os.getenv("DATABASE_URL"), schema=tenant,
                                include_tables=include_table_names, view_support=True)

    records_example = pgdb.run("""
                               select * from \"{tenant}\".\"{viewsName}\"
                               limit 10
                               """.format(
        tenant=tenant, viewsName=viewsName
    )
    )

    print("records example")
    print(records_example)

    dataSchemaString = {d["key"]: d["data_type"] for d in dataSchema}
    QUERY = """
            Given an input question, first create a syntactically correct postgresql query to run,
            this query can only access the table named \"{tenant}\".\"{viewsName}\",
            \"{tenant}\".\"{viewsName}\" schema has many columns representing in hash {dataSchemaString} and an (uploaded_at: datetime) column,
            all the data_type is datetime column should always query by TO_DATE([(the_column_name)::text], 'YYYY/MM/DD'),
            當需要查詢日期時, 先使用除 uploaded_at 外的其他日期, 除非 uploaded_at 是唯一一個日期類型
            then look at the results of the query and return the answer,
            Don't add the LIMIT amount on the SQLQuery result,
            使用與 query 相同的語言來回答問題!

            Use the following data as references:
            {records_example}

            Use the following format:

            Question: Question here
            SQLQuery: SQL Query to run only on the \"{tenant}\".\"{viewsName}\" table
            SQLResult: Result of the SQLQuery
            Answer: Final answer here

            {query}
            """.format(
        query=query,
        viewsName=viewsName,
        tenant=tenant,
        dataSchemaString=dataSchemaString,
        records_example=records_example
    )

    print("Query: ", QUERY)

    db_chain = SQLDatabaseChain(
        llm=llm2, database=pgdb, verbose=True, return_sql=returnSQL
    )

    print("DB Chain: ", db_chain)
    # import pdb
    # pdb.set_trace()

    sql = db_chain.run(QUERY)

    return sql


# def generateSQLByViews(viewsName, tenant, query, dataSchema=None, returnSQL=True):
#     dataSchemaString = ", ".join(dataSchema.keys())
#     llm2 = OpenAI(
#         temperature=0,
#         model_name=os.getenv("OPENAI_MODEL_NAME"),
#     )

#     QUERY = """
#             Let's think step by step!
#             Given an input question, first create a syntactically correct postgresql query to run,
#             this query can only access the table named \"{tenant}\".\"{viewsName}\",
#             \"{tenant}\".\"{viewsName}\" schema has many columns named {dataSchemaString} and uploaded_at,
#             then look at the results of the query and return the answer. Don't add the LIMIT amount on the SQLQuery result!
#             Use the following format:

#             Question: Question here
#             SQLQuery: SQL Query to run only on the \"{tenant}\".\"{viewsName}\" table
#             SQLResult: Result of the SQLQuery
#             Answer: Final answer here

#             {query}
#             """.format(
#         query=query,
#         viewsName=viewsName,
#         tenant=tenant,
#         dataSchemaString=dataSchemaString,
#     )

#     print("Query: ", QUERY)

#     pgdb = SQLDatabase.from_uri(os.getenv("DATABASE_URL"))

#     db_chain = SQLDatabaseChain(
#         llm=llm2, database=pgdb, verbose=True, return_sql=returnSQL)

#     print("DB Chain: ", db_chain)

#     sql = db_chain.run(QUERY)

#     return sql
