from langchain.tools import DuckDuckGoSearchResults, DuckDuckGoSearchRun
from langchain.utilities import DuckDuckGoSearchAPIWrapper
from flask import Blueprint, jsonify, request
from database.services.AutogenAgents import AutogenAgentService
import time
import autogen

autogen_api = Blueprint('autogen', __name__)

duckduckgo_search = DuckDuckGoSearchResults(
    name="duckduckgo_search",
    description=("當需要通過網絡去查找資料的時候，就使用這個功能"),
    api_wrapper=DuckDuckGoSearchAPIWrapper(
        region="wt-wt", time="d", max_results=8)
)


def create_ask_expert_function(expert):

    config_list = autogen.config_list_from_json("OAI_CONFIG_LIST")

    def ask_expert_function(message):
        # 实现专家回答问题的逻辑
        assistant_for_expert = autogen.AssistantAgent(
            name=f"assistant_for_{expert['name_en']}",
            max_consecutive_auto_reply=3,
            llm_config={
                "seed": 42,
                "temperature": 0,
                "config_list": config_list,
                "functions": [
                    {
                        "name": duckduckgo_search.name,
                        "description": duckduckgo_search.description,
                        'parameters': {
                            "type": "object",
                            "properties": {'query': {'description': 'search query to look up', 'type': 'string'}},
                            "required": ["query"]
                        },
                    }
                ],
            },
        )
        expert_agent = autogen.UserProxyAgent(
            name=f"{expert['name_en']}",
            # human_input_mode="ALWAYS",
            human_input_mode="NEVER",
            code_execution_config={"work_dir": f"{expert['name_en']}"},
            function_map={
                "duckduckgo_search": duckduckgo_search._run,
            }
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
    if 'emit' in config:
        config['emit']('message', messages[-1], room=config['room'])

    return False, None  # required to ensure the agent communication flow continues


def assistant_core(data, config={}):
    assistant_name = data['assistant']
    expert_names = data['experts']
    prompt = data['prompt']
    history = data.get('history', "")

    # 將 history 拼入去 prompt
    prompt = f"{history}\n\n{prompt}"

    agent = AutogenAgentService.get_assistant_agent_by_name(assistant_name)

    experts = AutogenAgentService.get_experts_by_names(expert_names)

    # 创建函数映射表
    function_map = {}
    for expert in experts:
        function_key = f"ask_{expert['name_en']}"
        function_map[function_key] = create_ask_expert_function(expert)

    print(function_map)

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
