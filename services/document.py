from database.pgvector import PGVectorDB
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.pgvector import PGVector
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from functools import partial
from langchain.chains.question_answering import load_qa_chain
from langchain.memory import (
    ConversationBufferMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryMemory,
)
from langchain.schema.messages import HumanMessage, AIMessage
from langchain.chains import ConversationalRetrievalChain
from langchain_community.chat_models import ChatOpenAI
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import (
    AgentTokenBufferMemory,
)
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.schema.messages import SystemMessage
from langchain.prompts import MessagesPlaceholder
from langchain.agents import AgentExecutor
from langchain_community.document_loaders import PyPDFLoader
from langchain.docstore.document import Document
from langchain.storage import InMemoryStore
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.prompt_template import format_document
from langchain.schema.runnable import RunnableParallel, RunnablePassthrough
from langchain.chains.combine_documents import collapse_docs, split_list_of_docs
from langchain.docstore.document import Document
from utils.utils import getExtension, cleansingContentFromGpt
import os
import json
from datetime import date

load_dotenv()


class DocumentService:
    embeddings = OpenAIEmbeddings()
    CONNECTION_STRING = os.getenv("PGVECTOR_DB_CONNECTION_STRING")
    pgvector_db = PGVectorDB("PGVECTOR_DB")

    @staticmethod
    def saveDocument(document, schema):
        COLLECTION_NAME = "DocAI_Documents_{schema}_Collection".format(schema=schema)

        try:
            docs = []
            if getExtension(document["name"]) == "pdf":
                print("Extension: ", getExtension(document["name"]))
                loader = PyPDFLoader(document["storage_url"], extract_images=False)
                pages = loader.load()
                docs = pages
            else:
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=2000, chunk_overlap=300
                )
                content = text_splitter.split_text(document["content"])
                docs = text_splitter.create_documents(content)

            print("Docs: ", docs)

            for doc in docs:
                doc.page_content = doc.page_content.replace("\x00", "\uFFFD")
                doc.metadata = {
                    "document_id": document["id"],
                    "schema": schema,
                    "document_created_at": document["created_at"],
                    "document_updated_at": document["updated_at"],
                    "folder_id": document["folder_id"],
                    "user_id": document["user_id"],
                    "page": doc.metadata["page"] if "page" in doc.metadata else 0,
                }

            PGVector.from_documents(
                embedding=DocumentService.embeddings,
                documents=docs,
                collection_name=COLLECTION_NAME,
                connection_string=DocumentService.CONNECTION_STRING,
            )
        except Exception as e:
            print(e)
            return False

        return True

    @staticmethod
    def similaritySearch(query, schema, metadata):
        filter = {}

        COLLECTION_NAME = "DocAI_Documents_{schema}_Collection".format(schema=schema)

        store = PGVector(
            collection_name=COLLECTION_NAME,
            connection_string=DocumentService.CONNECTION_STRING,
            embedding_function=DocumentService.embeddings,
        )

        res = store.similarity_search(query, filter=filter, k=3)
        return [i.metadata for i in res]

    @staticmethod
    def smartExtractionSchemaSearch(query, schema, metdata, history):
        pass

    @staticmethod
    def qaDocuments(query, schema, metadata, history):
        filter = {}
        llm = ChatOpenAI(model_name=os.getenv("OPENAI_MODEL_NAME"), temperature=0.2)
        memory_key = "agent_history"

        if "document_id" in metadata:
            filter["document_id"] = {"in": [str(i) for i in metadata["document_id"]]}

        COLLECTION_NAME = "DocAI_Documents_{schema}_Collection".format(schema=schema)

        print(COLLECTION_NAME)

        store = PGVector(
            collection_name=COLLECTION_NAME,
            connection_string=DocumentService.CONNECTION_STRING,
            embedding_function=DocumentService.embeddings,
        )

        print(len(metadata["document_id"]))

        retriever = store.as_retriever(
            search_kwargs={
                "filter": filter,
                "k": 5,
                "fetch_k": len(metadata["document_id"]),
            }
        )

        # Agent QA
        search_documents_tool = create_retriever_tool(
            retriever,
            "search_documents",
            "Searches and returns answer regarding the documents.",
        )
        summary_documents_tool = create_retriever_tool(
            retriever,
            "summary_documents_and_query",
            "Summarizes the documents and the query. If the query is not related to the documents, just say I don't know or cannot find the answer.",
        )
        tools = [search_documents_tool, summary_documents_tool]

        agent_memory = AgentTokenBufferMemory(
            memory_key=memory_key, llm=llm, max_token_limit=10000
        )

        for message in history:
            if "human" in message:
                agent_memory.chat_memory.add_user_message(message["human"])
            elif "ai" in message:
                agent_memory.chat_memory.add_ai_message(message["ai"])

        print(agent_memory.load_memory_variables({}))

        system_message = SystemMessage(
            content=(
                "First, modify the user's input based on the context to create a coherent and logical sentence."
                "Let's think step by step! Today is {today}, weekday is {weekday}! Monday is 0 and Sunday is 6. The day is very important when the user is asking for the documents related to the day. Maybe they will ask you tomorrow and next week for an answer. "
                "Only use the {language} language to answer the questions! "
                "You have to use the {tone} tone to answer the questions! "
                "Please do your best to provide {length} answers to the questions. "
                "Feel free to use any tools available to look up. "
                "Relevant information, only if neccessary. "
                "If you cannot answer the question, just say I don't know or cannot find the answer. You cannot generate some fake content and anything which cannot find from the retrived data. "
            ).format(
                language=metadata["language"] if "language" in metadata else "繁體中文",
                tone=metadata["tone"] if "tone" in metadata else "專業",
                today=date.today(),
                weekday=date.today().weekday(),
                length=metadata["length"] if "length" in metadata else "normal",
            )
        )

        prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=system_message,
            extra_prompt_messages=[MessagesPlaceholder(variable_name=memory_key)],
        )

        print(prompt)

        agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)

        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=agent_memory,
            verbose=True,
            return_intermediate_steps=True,
        )

        agent_res = agent_executor({"input": query})

        print(agent_res["output"])

        print(agent_memory.dict())

        chat_history = []

        for message in agent_memory.load_memory_variables({})["agent_history"]:
            if type(message) == HumanMessage:
                chat_history.append({"human": message.content})
            elif type(message) == AIMessage and message.content != "":
                chat_history.append({"ai": message.content})

        return agent_res["output"], chat_history

    @staticmethod
    def suggestionDocumentQA(schema, metadata):
        filter = {}
        result_coult = 8
        llm = ChatOpenAI(model_name=os.getenv("OPENAI_MODEL_NAME"), temperature=0.2)

        if "document_id" in metadata:
            filter["document_id"] = {"in": [str(i) for i in metadata["document_id"]]}

        COLLECTION_NAME = "DocAI_Documents_{schema}_Collection".format(schema=schema)

        print(COLLECTION_NAME)

        store = PGVector(
            collection_name=COLLECTION_NAME,
            connection_string=DocumentService.CONNECTION_STRING,
            embedding_function=DocumentService.embeddings,
        )

        retriever = store.as_retriever(
            search_kwargs={"filter": filter, "k": result_coult}
        )

        search_documents_tool = create_retriever_tool(
            retriever,
            "random_retrieval",
            "Randomly retrieve and select some documents from the retrieved data.",
        )
        tools = [search_documents_tool]

        system_message = SystemMessage(
            content=(
                "Generate results using the language of retrieval data. "
                "Feel free to use any tools available to look up. "
                "The generated 10 questions must ask the key point of the each retrieved data. "
                'The output result is a JSON object string and the format must be like this: ```{"assistant_questions": ["question_1", "question_2", "question_3"]}``` '
                "Try your best to generate 10 questions! "
            )
        )

        prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=system_message,
        )

        agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)

        agent_executor = AgentExecutor(
            agent=agent, tools=tools, verbose=True, return_intermediate_steps=True
        )

        agent_res = agent_executor(
            {
                "input": "Could you please generate some summary questions related to the retrieved documents to help the readers understand the content easily?"
            }
        )

        print("Agent Res: ", agent_res["output"])
        
        print("Format: ", cleansingContentFromGpt(agent_res["output"]))

        data = cleansingContentFromGpt(agent_res["output"])
        
        print(data)

        return data

    # @staticmethod
    # def generateQuestionsFromChunks(chunks):
    #     question = []
    #     for chunk in chunks:
    #         prompt = """generate one question and the corresponding answer from the chunk,
    #                     the question must satisfy the following rules:
    #                     1. The question should ask the key point of the chunk
    #                     2. A person must have a thorough understanding of the content of the chunk to answer correctly,
    #                     3. The question should only ask about the content of the chunk,
    #                     4. format is Q:.... A:....,
    #                     5. do not use the word "chunk",
    #                     6. no \n between Q and A
    #                     The chunk : {}""".format(str(chunk.page_content))
    #         response = call_gpt(prompt)
    #         question.append(response["choices"][0]["message"]["content"])
    #     for i in range(len(question)):
    #         doc_mid = Document(
    #             page_content=chunks[i].page_content,
    #             metadata={"chunk_id": i,
    #                       "assist_question": question[i]}
    #         )
    #         question[i] = doc_mid
    #     qdb = PGVector.from_documents(
    #         documents=question,
    #         embedding=embeddings_model,
    #         collection_name=COLLECTION_NAME,
    #         distance_strategy=DistanceStrategy.COSINE,
    #         connection_string="postgresql+psycopg2://postgres:akl123123@103.20.60.31:5435/postgres")

    #     return qdb
