
# from IPython import get_ipython
import sys
import re
from flask import Blueprint, jsonify, request
from database.services.AutogenAgents import AutogenAgentService
import time
import autogen
# from langchain_tools.DuckduckgoSearchTool import duckduckgo_search
import importlib
from datetime import date
import json

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


def exec_html(cell: str):
    return cell


def transform_tool_name(tool_name):
    # 將 camel case 轉換為 snake case
    transformed_name = re.sub(r'(?<!^)(?=[A-Z])', '_', tool_name).lower()
    # 去除尾部的 "Tool"
    transformed_name = re.sub(r'_tool$', '', transformed_name)
    return transformed_name


def import_agent_tool(expert, agent_tool, tools_config, app_config):

    invoke_name = agent_tool['invoke_name']
    tool_name = agent_tool['name']  # 調用人使用的名稱, 非 class name

    # agent tool 分為需要初始化 同 不需要初始化兩種
    # 需要初始化的話，例如要從指定的 folder 中提取資料的 qa tool，就要從參數中讀取
    if "initialize" in agent_tool['meta'] and tool_name in tools_config:
        # 需要初始化, 則 import class
        module = importlib.import_module(f"langchain_tools.{invoke_name}")
        class_ = getattr(module, invoke_name)
        metadata = tools_config[tool_name]['initialize']['metadata']
        metadata['expert'] = expert
        metadata['history'] = app_config['history']

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
        functions = [
            {
                "name": "html",
                "parameters": {
                    "type": "object",
                    "required": [
                        "cell"
                    ],
                    "properties": {
                        "cell": {
                            "type": "string",
                            "description": "處理 html 內容"
                        }
                    }
                },
                "description": "run cell in html and return the execution result."
            }
        ]
        function_map = {
            'html': exec_html
        }

        for agent_tool in expert['agent_tools']:
            name, function = import_agent_tool(expert, agent_tool, agent_tools_config, config)

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
            system_message=f"{expert['helper_agent_system_message']}",
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
            # system_message=f"選擇一條問題作為最終結果，確保輸出是 json 格式",
            system_message=f"{expert['system_message']}",
            # human_input_mode="ALWAYS",
            human_input_mode="NEVER",
            code_execution_config={"work_dir": f"{expert['name_en']}"},
            function_map=function_map
        )

        assistant_config = config.copy()
        expert_config = config.copy()
        assistant_config.update({'category': 'expert_assistant'})
        expert_config.update({'category': 'expert'})

        assistant_for_expert.register_reply(
            [autogen.Agent, None],
            reply_func=print_messages,
            config=assistant_config,
        )

        expert_agent.register_reply(
            [autogen.Agent, None],
            reply_func=print_messages,
            config=expert_config,
        )

        expert_agent.initiate_chat(assistant_for_expert, message=message)
        expert_agent.stop_reply_at_receive(assistant_for_expert)
        # expert.human_input_mode, expert.max_consecutive_auto_reply = "NEVER", 3
        # final message sent from the expert
        # expert_agent.send(
        #     "如果返回的是 html 代碼，則直接返回 html 的內容, 否則總結答案和解法方法，然後用一個簡單易懂的方式說明", assistant_for_expert)
        # return the last message the expert received

        print("expert saying")
        # print(expert_agent.last_message()["content"])
        # import pdb
        # pdb.set_trace()

        all_messages = [item for sublist in expert_agent.chat_messages.values() for item in sublist]
        filtered_messages = [item for item in all_messages if item['content'] not in ['', 'TERMINATE']]

        return filtered_messages[-1]["content"].strip().replace("TERMINATE", "")

    return ask_expert_function


def print_messages(recipient, messages, sender, config):

    print(f"[{recipient}]: {messages[-1]}")
    if "callback" in config and config["callback"] is not None:
        callback = config["callback"]
        callback(sender, recipient, messages[-1])

    # 空白就唔出了
    if messages[-1]['content'] == "":
        return False, None

    # 如果係 development mode, 就全部都輸出, 否則只輸出 user_proxy 同 assistant category 的回覆
    if config['development'] == False and config['category'] not in ['user_proxy', 'assistant']:
        return False, None

    display_method = "voice"
    print(sender)
    if 'emit' in config:

        # if sender.name == "ask_make_quiz_expert":
        #     import pdb
        #     pdb.set_trace()

        # 如果 content 係 json 的話，要處理一下
        if 'content' in messages[-1] and messages[-1]['content'] is not None:
            try:
                keep_something = messages[-1]['content']
                clean_json = json.loads(messages[-1]['content'])

                messages[-1]['content'] = json.dumps(clean_json)

                # 如果係純 json 的 content, 應該就唔洗讀出黎
                if 'content' in clean_json and not isinstance(clean_json['content'], str):
                    display_method = "show"

            except json.JSONDecodeError as e:
                # 如果唔係 json, 咁唔洗理
                # import pdb
                # pdb.set_trace()
                pass

        # pattern = config['prompt_header']
        # import pdb
        # pdb.set_trace()
        # msg = re.sub(pattern, "", messages[-1]['content'])
        if config['development'] == False and 'content' in messages[-1] and messages[-1]['content'] is not None:
            # import pdb
            # pdb.set_trace()
            messages[-1]['content'] = messages[-1]['content'].replace(config['prompt_header'], "")
            messages[-1]['content'] = messages[-1]['content'].lstrip("\n\n")

        config['emit'](
            'message', {"sender": sender.name, "message": messages[-1], "response_to": config['prompt'], "display_method": display_method}, room=config['room'], prompt_header=config['prompt_header'])

        # if sender.name == 'user_proxy':
        #     import pdb
        #     pdb.set_trace()

    return False, None  # required to ensure the agent communication flow continues


def assistant_core(data, config):
    assistant_name = data['assistant']
    expert_names = data['experts']
    prompt = data['prompt']
    raw_history = data.get('history', "")
    agent_tools_config = data.get('agent_tools', {})
    development_mode = data.get('development', False)

    print("agent tools config")
    print(agent_tools_config)

    history = ''
    for h in raw_history:
        history += f"{h['by']}: {h['content']}\n"

    # 將 history 拼入去 prompt
    if history != "":
        prompt = f"history:```{history}```\n\nprompt```{prompt}```"

    agent = AutogenAgentService.get_assistant_agent_by_name(assistant_name)
    prompt_header = agent['prompt_header']

    if len(expert_names) > 0:
        experts = AutogenAgentService.get_experts_by_names(expert_names)
    else:
        experts = []

    # 合并個 config 傳入去比 print_messages
    merged_config = {**{
        "callback": None,
        "prompt_header": prompt_header,
        "prompt": prompt,
        "development": development_mode,
        "history": history
    }, **config}

    # 创建函数映射表
    function_map = {
        "html": exec_html
    }

    # 專家的 functions
    for expert in experts:
        function_key = f"ask_{expert['name_en']}"
        function_map[function_key] = create_ask_expert_function(expert, agent_tools_config, merged_config)

    # 助理的 llm_config 係要根據傳入的 experts 去調整的
    # 因為助理要知道有咩 experts 係可以調用的
    agent_llm_config = agent['llm_config']
    for expert in experts:
        if 'function_config' in expert['meta']:
            function_config = expert['meta']['function_config']
            agent_llm_config['functions'].append(function_config)

    agent_llm_config['functions'].append(
        {
            "name": "html",
            "parameters": {
                "type": "object",
                "required": [
                    "cell"
                ],
                "properties": {
                    "cell": {
                        "type": "string",
                        "description": "處理 html 內容"
                    }
                }
            },
            "description": "run cell in html and return the execution result."
        }
    )
    # 專屬助手的 functions
    for agent_tool in agent['agent_tools']:
        name, function = import_agent_tool(agent, agent_tool, agent_tools_config, merged_config)

        # override 預設的 description
        tool_name = agent_tool['name']
        if tool_name in agent_tools_config and 'description' in agent_tools_config[tool_name]:
            customize_description = agent_tools_config[tool_name]['description']
        else:
            customize_description = agent_tool['description']

        agent_llm_config['functions'].append({
            "name": name,
            "description": customize_description,
            "parameters": agent_tool['meta']['parameters']
        })

        # 创建函数映射表
        function_map[name] = function._run

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
        # is_termination_msg=lambda x: x.get("content", "").rstrip() == "",
        system_message="Reply TERMINATE when the task is done.",
        function_map=function_map
    )

    system_message_header = "Today is {today}, weekday is {weekday}! Monday is 0 and Sunday is 6. ".format(today=date.today(),
                                                                                                           weekday=date.today().weekday())
    system_message_add_date = f"{system_message_header}\n{agent['system_message']}\n{prompt_header}"

    system_message_add_date = system_message_add_date + "\n 當用戶輸入空白時，不要回覆"

    assistant_agent = autogen.AssistantAgent(
        name=agent['name_en'],
        system_message=system_message_add_date,
        llm_config=agent_llm_config
    )

    user_proxy_config = merged_config.copy()
    assistant_config = merged_config.copy()
    user_proxy_config.update({'category': 'user_proxy'})
    assistant_config.update({'category': 'assistant'})

    user_proxy.register_reply(
        [autogen.Agent, None],
        reply_func=print_messages,
        config=user_proxy_config,
    )

    assistant_agent.register_reply(
        [autogen.Agent, None],
        reply_func=print_messages,
        config=assistant_config,
    )

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
