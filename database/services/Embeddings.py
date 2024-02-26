from sqlalchemy import func
from database.pgvector_session import get_session  # 导入上面定义的get_session函数
from database.models.LangchainPgEmbedding import LangchainPgEmbedding  # 确保导入你的模型


class EmbeddingsQueryService:
    @staticmethod
    def get_random_embedding_by_ids(document_ids, limit=10):
        """
        根据给定的document_ids随机获取限定数量的记录，不需要外部传入session。
        """

        # import pdb
        # pdb.set_trace()
        # 使用get_session获取session
        session = get_session()

        # 构建查询
        filtered_query = session.query(LangchainPgEmbedding).filter(
            LangchainPgEmbedding.cmetadata['document_id'].astext.in_(document_ids)
        ).order_by(func.random()).limit(limit)

        # 执行查询并获取结果
        results = filtered_query.all()

        # 关闭session
        session.close()

        return results
