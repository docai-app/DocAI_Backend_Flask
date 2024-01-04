# from ..docai import docai_db
from database.pgvector import PGVectorDB


class AutogenAgentService:

    @staticmethod
    def get_experts_by_names(names):
        docai_db = PGVectorDB("DATABASE_URL")
        cursor = docai_db.conn.cursor()

        query = """
            SELECT * FROM assistant_agents
            WHERE name IN %s AND version = 'production'
        """

        cursor.execute(query, (tuple(names),))
        results = cursor.fetchall()

        cursor.close()
        docai_db.conn.close()

        expert_list = []
        columns = [desc[0] for desc in cursor.description]
        for result in results:
            expert_dict = dict(zip(columns, result))
            expert_list.append(expert_dict)

        return expert_list

    @staticmethod
    def get_assistant_agent_by_name(name):
        docai_db = PGVectorDB("DATABASE_URL")
        cursor = docai_db.conn.cursor()

        query = """
            SELECT * FROM assistant_agents
            WHERE name = %s AND version = 'production'
        """

        cursor.execute(query, (name,))
        result = cursor.fetchone()

        cursor.close()
        docai_db.conn.close()

        if result:
            columns = [desc[0] for desc in cursor.description]
            result_dict = dict(zip(columns, result))
            return result_dict
        else:
            return None
