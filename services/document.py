from database.pgvector import PGVectorDB
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.pgvector import PGVector
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory, ConversationSummaryMemory
from langchain.schema.messages import HumanMessage, AIMessage
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import AgentTokenBufferMemory
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.schema.messages import SystemMessage
from langchain.prompts import MessagesPlaceholder
from langchain.agents import AgentExecutor
import os
import json
load_dotenv()


class DocumentService():
    embeddings = OpenAIEmbeddings()
    CONNECTION_STRING = os.getenv("PGVECTOR_DB_CONNECTION_STRING")
    pgvector_db = PGVectorDB("PGVECTOR_DB")

    @staticmethod
    def saveDocument(document, schema):
        COLLECTION_NAME = 'DocAI_Documents_{schema}_Collection'.format(
            schema=schema)

        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=3000, chunk_overlap=400)

            content = text_splitter.split_text(document['content'])

            docs = text_splitter.create_documents(content)

            for doc in docs:
                doc.metadata = {'document_id': document['id'], 'schema': schema,
                                'document_created_at': document['created_at'], 'document_updated_at': document['updated_at'],
                                'folder_id': document['folder_id'], 'user_id': document['user_id']}

            PGVector.from_documents(
                embedding=DocumentService.embeddings,
                documents=docs,
                collection_name=COLLECTION_NAME,
                connection_string=DocumentService.CONNECTION_STRING
            )
        except Exception as e:
            print(e)
            return False

        return True

    @staticmethod
    def similaritySearch(query, schema, metadata):
        filter = {}

        COLLECTION_NAME = 'DocAI_Documents_{schema}_Collection'.format(
            schema=schema)

        store = PGVector(
            collection_name=COLLECTION_NAME,
            connection_string=DocumentService.CONNECTION_STRING,
            embedding_function=DocumentService.embeddings,
        )

        res = store.similarity_search(query, filter=filter, k=3)
        return [i.metadata for i in res]

    @staticmethod
    def qaDocuments(query, schema, metadata, history):
        filter = {}
        llm = ChatOpenAI(model_name=os.getenv(
            "OPENAI_MODEL_NAME"), temperature=0.3)
        memory_key = "agent_history"

        if 'document_id' in metadata:
            filter['document_id'] = {
                "in": [str(i) for i in metadata['document_id']]}

        COLLECTION_NAME = 'DocAI_Documents_{schema}_Collection'.format(
            schema=schema)

        print(COLLECTION_NAME)

        store = PGVector(
            collection_name=COLLECTION_NAME,
            connection_string=DocumentService.CONNECTION_STRING,
            embedding_function=DocumentService.embeddings,
        )

        print(len(metadata['document_id']))

        retriever = store.as_retriever(
            search_kwargs={'filter': filter, 'k': 5,
                           'fetch_k': len(metadata['document_id'])}
        )

        # Normal QA
        # memory = ConversationBufferWindowMemory(
        #     memory_key="chat_history", k=len(metadata['document_id']) or 10, return_messages=True)

        # chat = ConversationalRetrievalChain.from_llm(llm=ChatOpenAI(model_name=os.getenv(
        #     "OPENAI_MODEL_NAME"), temperature=0.3), retriever=retriever, memory=memory)

        # for message in history:
        #     if 'human' in message:
        #     memory.chat_memory.add_user_message(message['human'])
        # elif 'ai' in message:
        #     memory.chat_memory.add_ai_message(message['ai'])

        # res = chat({"question": query}, return_only_outputs=False)

        # Agent QA
        search_documents_tool = create_retriever_tool(
            retriever,
            "search_documents",
            "Searches and returns answer regarding the documents."
        )
        summary_documents_tool = create_retriever_tool(
            retriever,
            "summary_documents_and_query",
            "Summarizes the documents and the query. If the query is not related to the documents, just say I don't know or cannot find the answer."
        )
        tools = [search_documents_tool, summary_documents_tool]

        agent_memory = AgentTokenBufferMemory(
            memory_key=memory_key, llm=llm, max_token_limit=10000)

        for message in history:
            if 'human' in message:
                agent_memory.chat_memory.add_user_message(message['human'])
            elif 'ai' in message:
                agent_memory.chat_memory.add_ai_message(message['ai'])

        print(agent_memory.load_memory_variables({}))

        system_message = SystemMessage(
            content=(
                "Only use the English and Traditional Chinese(繁體中文) language to answer the questions! "
                "Do your best to answer the questions. "
                "Feel free to use any tools available to look up "
                "Relevant information, only if neccessary"
            )
        )

        prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=system_message,
            extra_prompt_messages=[
                MessagesPlaceholder(variable_name=memory_key)
            ]
        )

        print(prompt)

        agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)

        agent_executor = AgentExecutor(agent=agent, tools=tools, memory=agent_memory, verbose=True,
                                       return_intermediate_steps=True)

        agent_res = agent_executor({"input": query})

        print(agent_res["output"])

        print(agent_memory.dict())

        chat_history = []

        for message in agent_memory.load_memory_variables({})['agent_history']:
            if type(message) == HumanMessage:
                chat_history.append({"human": message.content})
            elif type(message) == AIMessage and message.content != "":
                chat_history.append({"ai": message.content})

        # for message in memory.load_memory_variables({})['chat_history']:
        #     if type(message) == HumanMessage:
        #         chat_history.append({"human": message.content})
        #     elif type(message) == AIMessage and message.content != "":
        #         chat_history.append({"ai": message.content})

        return agent_res['output'], chat_history
        # return res['answer'], chat_history

    @staticmethod
    def suggestionDocumentQA(schema, metadata):
        filter = {}
        llm = ChatOpenAI(model_name=os.getenv(
            "OPENAI_MODEL_NAME"), temperature=0.3)

        if 'document_id' in metadata:
            filter['document_id'] = {
                "in": [str(i) for i in metadata['document_id']]}

        COLLECTION_NAME = 'DocAI_Documents_{schema}_Collection'.format(
            schema=schema)

        print(COLLECTION_NAME)

        store = PGVector(
            collection_name=COLLECTION_NAME,
            connection_string=DocumentService.CONNECTION_STRING,
            embedding_function=DocumentService.embeddings,
        )

        print(len(metadata['document_id']))

        retriever = store.as_retriever(
            search_kwargs={'filter': filter, 'k': 5,
                           'fetch_k': len(metadata['document_id'])}
        )

        search_documents_tool = create_retriever_tool(
            retriever,
            "search_documents",
            "Randomly selects some documents for the user initial search suggestion."
        )
        question_suggestion_tool = create_retriever_tool(
            retriever,
            "question_suggestion",
            "Based on the user documents, generates a question for the beginner user to let them know what are the documents related to."
        )
        tools = [search_documents_tool, question_suggestion_tool]

        system_message = SystemMessage(
            content=(
                "Only use the Traditional Chinese(繁體中文) language to answer the questions! "
                "Do your best to answer the questions. "
                "Feel free to use any tools available to look up "
                "relevant information, only if neccessary"
                "Returns 4 questions related to the user documents"
            )
        )

        prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=system_message,
        )

        agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)

        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True,
                                       return_intermediate_steps=True)

        agent_res = agent_executor(
            {"input": "Acts as a documents question suggestion tool. Could you please suggest some questions related to the documents? Since I am a beginner, I need some help."})

        print(agent_res["output"])

        return agent_res['output']
