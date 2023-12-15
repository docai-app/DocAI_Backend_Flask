from langchain_tools.RetrivalQuestionAnswerTool import RetrivalQuestionAnswerTool
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.llms import OpenAI
from langchain.agents import Tool
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
import sys

from langchain_tools.SmartExtractionSchemaSelectionTool import SmartExtractionSchemaSelectionTool
from langchain_tools.StatisticAnswerTool import StatisticAnswerTool

import autogen

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        "model": ["gpt-4-1106-preview", "gpt-4", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"],
    },
)


class AutogenSerivce:
    @staticmethod
    def chat(tool_metadata):
        llm = OpenAI(openai_api_key=os.getenv(
            "OPENAI_API_KEY"), temperature=0.6)

        # retrieval_qa_tool = RetrivalQuestionAnswerTool(
        #     query, schema_name, metadata["document_ids"], chat_history, metadata={'custom_variable': {'hello': 'world'}})

        retrieval_qa_tool = RetrivalQuestionAnswerTool(metadata=tool_metadata)

        smart_extraction_schema_selection_tool = SmartExtractionSchemaSelectionTool(
            metadata=tool_metadata)

        statistic_answer_tool = StatisticAnswerTool(metadata=tool_metadata)

        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            is_termination_msg=lambda x: x.get("content", "") and x.get(
                "content", "").rstrip().endswith("TERMINATE"),
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            code_execution_config={
                "last_n_messages": 2, "work_dir": "groupchat"},
            # human_input_mode="TERMINATE",
            system_message="Reply TERMINATE when the task is done."
        )

        user_proxy.register_function(
            function_map={
                retrieval_qa_tool.name: retrieval_qa_tool._run,
                smart_extraction_schema_selection_tool.name: smart_extraction_schema_selection_tool._run,
                statistic_answer_tool.name: statistic_answer_tool._run
                # summary_documents_tool.name: summary_documents_tool._run,
                # search_documents_tool.name: search_documents_tool._run
            }
        )

        llm_config = {
            "functions": [{
                'name': retrieval_qa_tool.name,
                'description': retrieval_qa_tool.description,
                'parameters': {
                    'type': 'object',
                    'properties': {'query': {'type': 'string'}},
                    'required': []
                }
            }, {
                'name': smart_extraction_schema_selection_tool.name,
                'description': smart_extraction_schema_selection_tool.description,
                'parameters': {
                    'type': 'object',
                    'properties': {'query': {'type': 'string'}},
                    'required': []
                }
            }, {
                'name': statistic_answer_tool.name,
                'description': statistic_answer_tool.description,
                'parameters': {
                    'type': 'object',
                    'properties': {'query': {'type': 'string'}},
                    'required': []
                }
            }],
            "config_list": config_list,  # Assuming you have this defined elsewhere
            "timeout": 120,
        }

        assistant = autogen.AssistantAgent(
            name="assistant",
            # system_message="Reply TERMINATE when the task is done.",
            system_message="回答用戶的問題",
            llm_config=llm_config,
        )

        coder = autogen.AssistantAgent(
            name="Coder",
            system_message='''Engineer. You write python/shell code to solve tasks. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Execute the code and report the result
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
''',
            llm_config=llm_config,
            code_execution_config={
                "last_n_messages": 3, "work_dir": "groupchat"},
        )

        groupchat = autogen.GroupChat(
            agents=[user_proxy, coder, assistant], messages=[], max_round=12)
        manager = autogen.GroupChatManager(
            groupchat=groupchat, llm_config=llm_config)

        print("開始 user proxy initiate chat", file=sys.stderr)
        user_proxy.initiate_chat(
            manager, message=f'{tool_metadata["query"]} TERMINATE', llm_config=llm_config)

        # user_proxy.initiate_chat(
        #     assistant,
        #     message=f'{tool_metadata["query"]} TERMINATE',
        #     llm_config=llm_config
        # )

        print("結果", file=sys.stderr)
        print(groupchat.messages, file=sys.stderr)

        ai_responses = [record for record in groupchat.messages if record.get(
            'role') != 'user_proxy']
        last_response = ai_responses[-1]
        return last_response
