
# from IPython import get_ipython
import sys
import re
from flask import Blueprint, jsonify, request
from database.services.AutogenAgents import AutogenAgentService
import time
import autogen
# from langchain_tools.DuckduckgoSearchTool import duckduckgo_search
import importlib

autogen_api = Blueprint('autogen', __name__)


# def exec_python(cell):
#     ipython = get_ipython()
#     result = ipython.run_cell(cell)
#     log = str(result.result)
#     if result.error_before_exec is not None:
#         log += f"\n{result.error_before_exec}"
#     if result.error_in_exec is not None:
#         log += f"\n{result.error_in_exec}"
#     return log


def exec_python(cell: str):
    # if "cell" in args:
    #     cell_content = args["cell"]
    # else:
    #     cell_content = args

    cell_content = cell

    # 将代码分割成单独的语句
    statements = cell_content.strip().split('\n')

    # 准备一个字典来存储执行过程中的局部变量
    local_vars = {}

    # 执行所有除最后一个语句以外的代码
    for statement in statements[:-1]:
        exec(statement, globals(), local_vars)

    # 执行最后一个语句并返回结果
    return eval(statements[-1], globals(), local_vars)


def transform_tool_name(tool_name):
    # 將 camel case 轉換為 snake case
    transformed_name = re.sub(r'(?<!^)(?=[A-Z])', '_', tool_name).lower()
    # 去除尾部的 "Tool"
    transformed_name = re.sub(r'_tool$', '', transformed_name)
    return transformed_name


def import_agent_tool(agent_tool, config):

    invoke_name = agent_tool['invoke_name']
    tool_name = agent_tool['name']  # 調用人使用的名稱, 非 class name

    # agent tool 分為需要初始化 同 不需要初始化兩種
    # 需要初始化的話，例如要從指定的 folder 中提取資料的 qa tool，就要從參數中讀取
    if "initialize" in agent_tool['meta'] and tool_name in config:
        # 需要初始化, 則 import class
        module = importlib.import_module(f"langchain_tools.{invoke_name}")
        class_ = getattr(module, invoke_name)
        metadata = config[tool_name]['initialize']['metadata']
        function = class_(metadata=metadata)
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

            # override 預設的 description
            tool_name = agent_tool['name']
            if tool_name in agent_tools_config and 'description' in agent_tools_config[tool_name]:
                customize_description = agent_tools_config[tool_name]['description']
            else:
                customize_description = agent_tool['description']

            functions.append({
                "name": name,
                "description": customize_description,
                "parameters": agent_tool['meta']['parameters']
            })

            # 创建函数映射表
            function_map[name] = function._run

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
            'message', {"sender": sender.name, "message": messages[-1]}, room=config['room'], prompt_header=config['prompt_header'])

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
    prompt_header = agent['prompt_header']

    experts = AutogenAgentService.get_experts_by_names(expert_names)

    # 合并個 config 傳入去比 print_messages
    merged_config = {**{
        "callback": None,
        "prompt_header": prompt_header
    }, **config}

    # 创建函数映射表
    function_map = {
        "python": exec_python
    }
    for expert in experts:
        function_key = f"ask_{expert['name_en']}"
        function_map[function_key] = create_ask_expert_function(expert, agent_tools_config, merged_config)

    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=3,
        code_execution_config={
            "work_dir": 'user_proxy',
            "use_docker": True,
            "last_n_messages": 1,
        },
        # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        system_message="Reply TERMINATE when the task is done.",
        function_map=function_map
    )

    assistant_agent = autogen.AssistantAgent(
        name=agent['name_en'],
        system_message=agent['system_message'],
        # is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        # code_execution_config={
        #     "work_dir": "assistant_agent",
        #     "use_docker": "python:latest"
        # },
        llm_config=agent['llm_config']
    )

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

    # f"{prompt_header}\n\n{prompt}"

    user_proxy.initiate_chat(assistant_agent, message=f"{prompt_header}\n\n{prompt}")

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
