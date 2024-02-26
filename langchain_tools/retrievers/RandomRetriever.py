from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from typing import List

# 假设这是你的数据库模型和获取session的方法
from database.services.Embeddings import EmbeddingsQueryService


class RandomRetriever(BaseRetriever):

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun = None
    ) -> List[Document]:

        # import pdb
        # pdb.set_trace()
        limit = self.metadata['limit'] or 10
        # 执行查询并获取结果
        langchain_pg_embeddings = EmbeddingsQueryService.get_random_embedding_by_ids(
            self.metadata['document_ids'], limit)

        # 将结果转换为Document对象的列表
        documents = [Document(page_content=embedding.document, metadata={
                              "custom_id": embedding.custom_id}) for embedding in langchain_pg_embeddings]

        return documents


# # 示例使用
# document_ids = ["c6fae7b1-ed8b-49eb-806e-875f9cd84d9d",
#                 "54b00b41-cd41-4fa2-be36-800ca0d7718c", "fa671e9c-76ef-4b68-a034-086099827735"]
# retriever = RandomRetriever(document_ids=document_ids)
# documents = retriever.get_relevant_documents("bar")

# for doc in documents:
#     print(doc.page_content, doc.metadata)
