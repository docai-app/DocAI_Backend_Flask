from database.pgvector import PGVectorDB
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.pgvector import PGVector
from langchain.document_loaders import TextLoader
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import FAISS
import os
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

            print(content)

            docs = text_splitter.create_documents(content)

            print(docs)

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
    def qaDocuments(query, schema, metadata):
        filter = {}

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

        docs = store.similarity_search(query, filter=filter, k=10)

        print(docs)

        chain = load_qa_chain(ChatOpenAI(model_name=os.getenv(
            "OPENAI_MODEL_NAME"), temperature=0.7), chain_type="stuff")
        res = chain({"input_documents": docs, "question": query},
                    return_only_outputs=True)

        return res