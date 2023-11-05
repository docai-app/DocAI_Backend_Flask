from database.pgvector import PGVectorDB
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.pgvector import PGVector
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from functools import partial
from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory, ConversationSummaryMemory
from langchain.schema.messages import HumanMessage, AIMessage
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import AgentTokenBufferMemory
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.schema.messages import SystemMessage
from langchain.prompts import MessagesPlaceholder
from langchain.agents import AgentExecutor
from langchain.document_loaders import PyPDFLoader
from langchain.docstore.document import Document
from langchain.storage import InMemoryStore
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.prompt_template import format_document
from langchain.schema.runnable import RunnableParallel, RunnablePassthrough
from langchain.chains.combine_documents import collapse_docs, split_list_of_docs
from langchain.docstore.document import Document
from utils.utils import getExtension
import os
import json
load_dotenv()


class SmartExtractionService():
    embeddings = OpenAIEmbeddings()
    CONNECTION_STRING = os.getenv("PGVECTOR_DB_CONNECTION_STRING")
    pgvector_db = PGVectorDB("PGVECTOR_DB")

    @staticmethod
    def createMapReduceChain(docs, map_prompt, reduce_prompt, logObject):
        llm = ChatOpenAI(model_name=os.getenv("OPENAI_MODEL_NAME"), temperature=0.2)
        
        # Prompt and method for converting Document -> str.
        document_prompt = PromptTemplate.from_template("{page_content}")
        partial_format_document = partial(format_document, prompt=document_prompt)

        map_chain = (
            {"context": partial_format_document}
            | PromptTemplate.from_template(map_prompt)
            | llm
            | StrOutputParser()
        )

        # A wrapper chain to keep the original Document metadata
        map_as_doc_chain = (
            RunnableParallel({"doc": RunnablePassthrough(), "content": map_chain})
            | (lambda x: Document(page_content=x["content"], metadata=x["doc"].metadata))
        ).with_config(run_name="Summarize (return doc)")

        # The chain we'll repeatedly apply to collapse subsets of the documents format_docs
        # into a consolidate document until the total token size of our
        # documents is below some max size.
        def format_docs(docs):
            return "\n\n".join(partial_format_document(doc) for doc in docs)

        collapse_chain = (
            {"context": format_docs}
            | PromptTemplate.from_template("Collapse this content:\n\n{context}")
            | llm
            | StrOutputParser()
        )

        def get_num_tokens(docs):
            return llm.get_num_tokens(format_docs(docs))


        def collapse(
            docs,
            config,
            token_max=4000,
        ):
            collapse_ct = 1
            while get_num_tokens(docs) > token_max:
                config["run_name"] = f"Collapse {collapse_ct}"
                invoke = partial(collapse_chain.invoke, config=config)
                split_docs = split_list_of_docs(docs, get_num_tokens, token_max)
                docs = [collapse_docs(_docs, invoke) for _docs in split_docs]
                collapse_ct += 1

            logObject['after_maps'] = docs
            return docs

        # The chain we'll use to combine our individual document summaries
        # (or summaries over subset of documents if we had to collapse the map results)
        # into a final summary.

        reduce_chain = (
            {"context": format_docs}
            | PromptTemplate.from_template(reduce_prompt)
            | llm
            | StrOutputParser()
        ).with_config(run_name="Reduce")

        # The final full chain
        map_reduce = (map_as_doc_chain.map() | collapse | reduce_chain).with_config(
            run_name="Map reduce")

        return map_reduce
    
    @staticmethod
    def mapReduce(storage_url, schema, data_schema):
        loader = PyPDFLoader(storage_url, extract_images=True)
        pages = loader.load()
        docs = pages
        res_data_schema = data_schema
        for s in schema:
            res_map_reduce = SmartExtractionService.createMapReduceChain(docs, s['query'][0] + "\n\n{context}", s['query'][1] + "\n\n{context}", {})
            res = res_map_reduce.invoke(docs, config={"max_concurrency": 5})
            res_data_schema[s['key']] = res
        return res_data_schema
    
        