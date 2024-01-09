# from ..docai import docai_db
from database.pgvector import PGVectorDB


class AutogenAgentService:

    @staticmethod
    def get_experts_by_names(names):
        docai_db = PGVectorDB("DATABASE_URL")
        cursor = docai_db.conn.cursor()

        query = """
            SELECT 
                aa.id, aa.name, aa.name_en, aa.system_message, aa.description, aa.llm_config, aa.meta,
                json_agg(agent_tools.*) as agent_tools
            FROM assistant_agents as aa
            LEFT OUTER JOIN agent_use_tools ON agent_use_tools.assistant_agent_id = aa.id
            LEFT OUTER JOIN agent_tools ON agent_tools.id = agent_use_tools.agent_tool_id
            WHERE aa.name IN %s AND aa.version = 'production'
            GROUP BY aa.id, aa.name, aa.name_en, aa.system_message, aa.description, aa.llm_config, aa.meta;
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
            SELECT 
                aa.id, aa.name, aa.name_en, aa.system_message, aa.description, aa.llm_config, aa.meta, aa.prompt_header,
                json_agg(agent_tools.*) as agent_tools
            FROM assistant_agents as aa
            LEFT OUTER JOIN agent_use_tools ON agent_use_tools.assistant_agent_id = aa.id
            LEFT OUTER JOIN agent_tools ON agent_tools.id = agent_use_tools.agent_tool_id
            WHERE aa.name = %s AND aa.version = 'production'
            GROUP BY aa.id, aa.name, aa.name_en, aa.system_message, aa.description, aa.llm_config, aa.meta, aa.prompt_header;
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
