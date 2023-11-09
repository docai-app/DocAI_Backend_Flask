import os
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from ext import db

def generateSQLByViews(viewsName, tenant, query, dataSchema=None):
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

    sql = db_chain.run(QUERY)
    
    return sql