import json
from datetime import datetime
from typing import AsyncIterator
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from backend.core.config import DEEPSEEK_API_KEY
from backend.tools.weather import get_weather
from backend.tools.rag_search import search_erzhi_tower

memory = MemorySaver()

def _build_agent():
    model = ChatOpenAI(
        model="deepseek-chat",
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com/v1"
    )
    system_prompt = f"""
你是郑州本地AI旅游助手，今天是{datetime.now().strftime('%Y年%m月%d日')}。
严格规则：
1. 用户问天气 → 必须调用 get_weather，绝不猜测
2. 用户问二七纪念塔 → 必须调用 search_erzhi_tower
3. 工具资料中没有的信息 →可以根据大模型自带的常识回答，但必须明确告知“上述信息来源于大模型自带的常识”
4. 回答简洁友好，基于工具返回的真实数据
"""
    return create_react_agent(
        model=model,
        tools=[get_weather, search_erzhi_tower],
        prompt=system_prompt,
        checkpointer=memory
    )

agent = _build_agent()

async def stream_agent(message: str, thread_id: str) -> AsyncIterator[str]:
    """流式返回Agent的回答，格式为SSE"""
    config = {"configurable": {"thread_id": thread_id}}

    async for event in agent.astream_events(
        {"messages": [{"role": "user", "content": message}]},
        config=config,
        version="v2"
    ):
        kind = event["event"]

        # 流式输出最终文字（过滤掉工具调用时的空chunk）
        if kind == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            if chunk.content and not getattr(chunk, "tool_call_chunks", []):
                yield json.dumps(
                    {"type": "token", "content": chunk.content},
                    ensure_ascii=False
                )

        # 工具开始调用
        elif kind == "on_tool_start":
            yield json.dumps(
                {"type": "tool_start", "tool": event["name"]},
                ensure_ascii=False
            )

        # 工具返回结果
        elif kind == "on_tool_end":
            yield json.dumps(
                {
                    "type": "tool_end",
                    "tool": event["name"],
                    "result": str(event["data"].get("output", ""))
                },
                ensure_ascii=False
            )

    yield json.dumps({"type": "done"}, ensure_ascii=False)