
import re
from flask import Blueprint, jsonify, request
from database.services.AutogenAgents import AutogenAgentService
import time
import autogen
# from langchain_tools.DuckduckgoSearchTool import duckduckgo_search
import importlib

autogen_api = Blueprint('autogen', __name__)


def transform_tool_name(tool_name):
    # 將 camel case 轉換為 snake case
    transformed_name = re.sub(r'(?<!^)(?=[A-Z])', '_', tool_name).lower()
    # 去除尾部的 "Tool"
    transformed_name = re.sub(r'_tool$', '', transformed_name)
    return transformed_name


def import_agent_tool(agent_tool, config):

    invoke_name = agent_tool['invoke_name']
    tool_name = agent_tool['name']  # 調用人使用的名稱, 非 class name

    print("come to here")
    print(tool_name)
    print(agent_tool['meta'])
    print(config)
    print("=======================================================")
    # agent tool 分為需要初始化 同 不需要初始化兩種
    # 需要初始化的話，例如要從指定的 folder 中提取資料的 qa tool，就要從參數中讀取
    if "initialize" in agent_tool['meta'] and tool_name in config:
        print("fuck ?")
        # 需要初始化, 則 import class
        module = importlib.import_module(f"langchain_tools.{invoke_name}")
        class_ = getattr(module, invoke_name)
        metadata = config[tool_name]['initialize']['metadata']
        print("metadata")
        print(metadata)
        function = class_(metadata=metadata)
        print("fuck here?")
        return (transform_tool_name(agent_tool['invoke_name']), function)

    if agent_tool['invoke_name'] == "DuckDuckgoSearchTool":
        module = importlib.import_module(f"langchain_tools.{agent_tool['invoke_name']}")
        function = getattr(module, "duckduckgo_search")
        return ("duckduckgo_search", function)
    else:
        module = importlib.import_module(f"langchain_tools.{agent_tool['invoke_name']}")
        function = getattr(module, transform_tool_name(agent_tool['invoke_name']))
        # 處理其他函數名稱的情況
        return (transform_tool_name(agent_tool['invoke_name']), function)


def sql_result_2dict(cursor, result):
    if result:
        if isinstance(result[0], tuple):  # 檢查結果是否為陣列
            columns = [desc[0] for desc in cursor.description]
            result_dicts = [dict(zip(columns, row)) for row in result]
            return result_dicts
        else:
            columns = [desc[0] for desc in cursor.description]
            result_dict = dict(zip(columns, result))
            return result_dict
    else:
        return None


def create_ask_expert_function(expert, agent_tools_config, config):

    config_list = autogen.config_list_from_json("OAI_CONFIG_LIST")

    def ask_expert_function(message):
        # 实现专家回答问题的逻辑

        # 讀取 expert 可以使用的工具(s)
        functions = []
        function_map = {}
        for agent_tool in expert['agent_tools']:
            name, function = import_agent_tool(agent_tool, agent_tools_config)
            functions.append({
                "name": name,
                "description": agent_tool['description'],
                "parameters": agent_tool['meta']['parameters']
            })

            # 创建函数映射表
            function_map[name] = function._run

        # assistant_for_expert = autogen.AssistantAgent(
        #     name=f"assistant_for_{expert['name_en']}",
        #     max_consecutive_auto_reply=3,
        #     llm_config={
        #         "seed": 42,
        #         "temperature": 0,
        #         "config_list": config_list,
        #         "functions": [
        #             {
        #                 "name": duckduckgo_search.name,
        #                 "description": duckduckgo_search.description,
        #                 'parameters': {
        #                     "type": "object",
        #                     "properties": {'query': {'description': 'search query to look up', 'type': 'string'}},
        #                     "required": ["query"]
        #                 },
        #             }
        #         ],
        #     },
        # )
        assistant_for_expert = autogen.AssistantAgent(
            name=f"assistant_for_{expert['name_en']}",
            max_consecutive_auto_reply=3,
            llm_config={
                "seed": 42,
                "temperature": 0,
                "config_list": config_list,
                "functions": functions,
            },
        )
        # expert_agent = autogen.UserProxyAgent(
        #     name=f"{expert['name_en']}",
        #     # human_input_mode="ALWAYS",
        #     human_input_mode="NEVER",
        #     code_execution_config={"work_dir": f"{expert['name_en']}"},
        #     function_map={
        #         "duckduckgo_search": duckduckgo_search._run,
        #     }
        # )
        expert_agent = autogen.UserProxyAgent(
            name=f"{expert['name_en']}",
            # human_input_mode="ALWAYS",
            human_input_mode="NEVER",
            code_execution_config={"work_dir": f"{expert['name_en']}"},
            function_map=function_map
        )

        assistant_for_expert.register_reply(
            [autogen.Agent, None],
            reply_func=print_messages,
            config=config,
        )

        expert_agent.register_reply(
            [autogen.Agent, None],
            reply_func=print_messages,
            config=config,
        )

        expert_agent.initiate_chat(assistant_for_expert, message=message)
        expert_agent.stop_reply_at_receive(assistant_for_expert)
        # expert.human_input_mode, expert.max_consecutive_auto_reply = "NEVER", 3
        # final message sent from the expert
        expert_agent.send(
            "總結答案和解法方法，然後用一個簡單易懂的方式說明", assistant_for_expert)
        # return the last message the expert received

        print("expert saying")
        print(expert_agent.last_message()["content"])
        return expert_agent.last_message()["content"]

    return ask_expert_function


def print_messages(recipient, messages, sender, config):

    print(f"[{recipient}]: {messages[-1]}")
    if "callback" in config and config["callback"] is not None:
        callback = config["callback"]
        callback(sender, recipient, messages[-1])

    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(socketManager.broadcast(messages[-1]))
    # loop.close()
    # asyncio.ensure_future(socketManager.broadcast(json.dumps(messages[-1])))
    print(sender)
    if 'emit' in config:
        config['emit'](
            'message', {"sender": sender.name, "message": messages[-1]}, room=config['room'])

    return False, None  # required to ensure the agent communication flow continues


def assistant_core(data, config):
    assistant_name = data['assistant']
    expert_names = data['experts']
    prompt = data['prompt']
    history = data.get('history', "")
    agent_tools_config = data.get('agent_tools', {})

    print("agent tools config")
    print(agent_tools_config)

    # 將 history 拼入去 prompt
    prompt = f"{history}\n\n{prompt}"

    agent = AutogenAgentService.get_assistant_agent_by_name(assistant_name)

    experts = AutogenAgentService.get_experts_by_names(expert_names)

    # 创建函数映射表
    function_map = {}
    for expert in experts:
        function_key = f"ask_{expert['name_en']}"
        function_map[function_key] = create_ask_expert_function(expert, agent_tools_config, config)

    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=3,
        code_execution_config={"work_dir": "user_proxy"},
        function_map=function_map
    )

    assistant_agent = autogen.AssistantAgent(
        name=agent['name_en'],
        system_message=agent['system_message'],
        llm_config=agent['llm_config']
    )

    # 合并個 config 傳入去比 print_messages
    merged_config = {**{
        "callback": None
    }, **config}

    user_proxy.register_reply(
        [autogen.Agent, None],
        reply_func=print_messages,
        config=merged_config,
    )

    assistant_agent.register_reply(
        [autogen.Agent, None],
        reply_func=print_messages,
        config=merged_config,
    )

    user_proxy.initiate_chat(assistant_agent, message=prompt)

    messages = user_proxy.chat_messages[assistant_agent]

    return messages


@autogen_api.route('/autogen/assistant', methods=['POST'])
def assistant():
    requestData = request.get_json()

    start_time = time.time()
    messages = assistant_core(requestData)

    autogen.ChatCompletion.stop_logging()
    response = {
        "messages": messages[1:],
        "usage": "",  # parse_token_usage(logged_history),
        "duration": time.time() - start_time,
    }
    return response
