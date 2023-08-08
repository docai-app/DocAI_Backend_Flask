from database.pgvector import PGVectorDB
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.pgvector import PGVector
from langchain.document_loaders import TextLoader
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
            "OPENAI_MODEL_NAME"), temperature=0.7)
        memory_key = "agent_history"

        if 'document_id' in metadata:
            filter['document_id'] = {
                "in": [str(i) for i in metadata['document_id']]}

        COLLECTION_NAME = 'DocAI_Documents_{schema}_Collection'.format(
            schema=schema)

        store = PGVector(
            collection_name=COLLECTION_NAME,
            connection_string=DocumentService.CONNECTION_STRING,
            embedding_function=DocumentService.embeddings,
        )

        retriever = store.as_retriever()

        print(len(metadata['document_id']))
        
        print(history)

        # docs = store.similarity_search(
        #     query, filter=filter, k=len(metadata['document_id']) or 10)

        # print(len(docs))

        # chain = load_qa_chain(ChatOpenAI(model_name=os.getenv(
        #     "OPENAI_MODEL_NAME"), temperature=0.7), chain_type="stuff")
        # res = chain({"input_documents": docs, "question": query},
        #             return_only_outputs=True)

        # print(res)

        # messagesHistory = [HumanMessage(**message) if 'human' in message
        #                    else AIMessage(**message) for message in chatHistory]

        # print(messagesHistory)

        # memory = ConversationSummaryMemory(llm=ChatOpenAI(model_name=os.getenv(
        #     "OPENAI_MODEL_NAME")), memory_key="chat_history", return_messages=True)
        memory = ConversationBufferWindowMemory(
            memory_key="chat_history", k=5, return_messages=True)

        memory.chat_memory.add_user_message(
            "這裏有人因為生病原因而請假嗎？這個人是誰？幫我整理一下他的個人資料，順便幫我寫一封200字的慰問信給這個人")
        memory.chat_memory.add_ai_message(
            "是的，有一位名叫李太白的員工因為孩子生病而請了病假。以下是他的個人資料：\n\n員工編號：456\n員工姓名：李太白\n職稱：員工\n\n關於慰問信，我很抱歉，根據提供的資料，我無法為您寫一封200字的慰問信。這份資料只提供了李太白請假的原因和相關細節，沒有提供其他個人資訊。如果您有其他需要，請提供更多資料，我將竭力協助您。")
        # memory.chat_memory.add_user_message(
        #     "你剛才生成的內容可以幫我翻譯成英文嗎？"
        # )
        # memory.chat_memory.add_ai_message(
        #     "I'm sorry, but I'm not able to generate a condolence letter for you."
        # )

        tool = create_retriever_tool(
            retriever,
            "search_documents",
            "Searches and returns answer regarding the documents."
        )
        tools = [tool]

        # agent_executor = create_conversational_retrieval_agent(
        #     llm=llm, tools=tools, verbose=True)

        agent_memory = AgentTokenBufferMemory(memory_key=memory_key, llm=llm)
        # agent_memory.chat_memory.add_user_message(
        #     "這裏有人因為生病原因而請假嗎？這個人是誰？幫我整理一下他的個人資料，順便幫我寫一封200字的慰問信給這個人")
        # agent_memory.chat_memory.add_ai_message(
        #     "是的，有一位名叫李太白的員工因為孩子生病而請了病假。以下是他的個人資料：\n\n員工編號：456\n員工姓名：李太白\n職稱：員工\n\n關於慰問信，我很抱歉，根據提供的資料，我無法為您寫一封200字的慰問信。這份資料只提供了李太白請假的原因和相關細節，沒有提供其他個人資訊。如果您有其他需要，請提供更多資料，我將竭力協助您。")
        # agent_memory.chat_memory.add_user_message(
        #     "你剛才生成的一封200字慰問信可以幫我翻譯成英文嗎？"
        # )
        # agent_memory.chat_memory.add_ai_message(
        #     "當然可以！以下是翻譯成英文的慰問信：\n\nDear Mr. Li Taibai,\n\nI hope this letter finds you well. I recently learned that you have taken sick leave due to your child's illness, and I wanted to extend my heartfelt sympathies and wishes for a speedy recovery.\n\nI understand that dealing with a sick child can be emotionally and physically challenging, and I want you to know that you are not alone during this difficult time. The well-being of your family is of utmost importance, and I hope that your child receives the necessary care and attention to regain good health.\n\nPlease take all the time you need to be with your child and prioritize their well-being. Your presence and support are invaluable during this period, and I encourage you to reach out if there is anything we can do to assist you or alleviate any additional stress.\n\nWishing you strength, resilience, and comfort during this challenging time. Please remember that your colleagues and I are here to support you.\n\nSincerely,\n[Your Name]\n\n請注意，這是一份自动生成的翻譯，可能會有一些語言或文化上的差異。如有需要，您可以對信件進行進一步的修改和調整，以確保表達出您想要傳達的意思。"
        # )
        
        for message in history:
            if 'human' in message:
                agent_memory.chat_memory.add_user_message(message['human'])
            elif 'ai' in message:
                agent_memory.chat_memory.add_ai_message(message['ai'])
                
        print(agent_memory.load_memory_variables({}))

        system_message = SystemMessage(
            content=(
                "Do your best to answer the questions. "
                "Feel free to use any tools available to look up "
                "relevant information, only if neccessary"
            )
        )

        prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=system_message,
            extra_prompt_messages=[
                MessagesPlaceholder(variable_name=memory_key)]
        )

        agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)

        agent_executor = AgentExecutor(agent=agent, tools=tools, memory=agent_memory, verbose=True,
                                       return_intermediate_steps=True)

        agent_res = agent_executor({"input": query})

        print(agent_res["output"])

        # chat_history = memory.load_memory_variables({})['chat_history']
        # chat_history = agent_memory.load_memory_variables({})['agent_history']

        # print(chat_history)

        # print(chat_history)

        # chat = ConversationalRetrievalChain.from_llm(llm=ChatOpenAI(model_name=os.getenv(
        #     "OPENAI_MODEL_NAME"), temperature=0.7), retriever=retriever, memory=memory)

        # res = chat({"question": query, "chat_history": chat_history})

        # print(res)

        # # print(memory.load_memory_variables({'input', 'output'}))

        print(agent_memory.dict())

        # print(memory.dict())

        chat_history = []
        for message in agent_memory.load_memory_variables({})['agent_history']:
            if type(message) == HumanMessage:
                chat_history.append({"human": message.content})
            elif type(message) == AIMessage and message.content != "":
                chat_history.append({"ai": message.content})

        return agent_res['output'], chat_history
