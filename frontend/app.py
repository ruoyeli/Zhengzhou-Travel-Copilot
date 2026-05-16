import json
import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8001/chat"

st.set_page_config(page_title="郑州AI旅游助手", page_icon="🏯")
st.title("🏯 郑州本地AI旅游助手")
st.caption("可以问我：天气查询 / 二七纪念塔导览 / 郑州旅游建议")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "user_001"

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("tool_calls"):
            with st.expander("🔍 查看工具调用（验证非幻觉）"):
                for tc in msg["tool_calls"]:
                    st.info(f"**调用工具：{tc['tool']}**\n\n{tc['result']}")

# 输入框
if user_input := st.chat_input("请输入你的问题..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_text = ""
        tool_calls = []
        current_tool = None

        try:
            with requests.post(
                BACKEND_URL,
                json={"message": user_input, "thread_id": st.session_state.thread_id},
                stream=True,
                timeout=120
            ) as resp:
                for line in resp.iter_lines():
                    if not line:
                        continue
                    line_str = line.decode("utf-8")
                    if not line_str.startswith("data: "):
                        continue
                    event = json.loads(line_str[6:])

                    if event["type"] == "token":
                        full_text += event["content"]
                        placeholder.markdown(full_text + "▌")

                    elif event["type"] == "tool_start":
                        current_tool = {"tool": event["tool"], "result": ""}
                        placeholder.markdown(f"🔧 正在调用工具：**{event['tool']}** ...")

                    elif event["type"] == "tool_end":
                        if current_tool:
                            current_tool["result"] = event["result"]
                            tool_calls.append(current_tool)
                            current_tool = None

                    elif event["type"] == "done":
                        placeholder.markdown(full_text)
                        break

        except requests.exceptions.ConnectionError:
            full_text = "❌ 无法连接后端，请确认backend已启动"
            placeholder.error(full_text)

        if tool_calls:
            with st.expander("🔍 查看工具调用（验证非幻觉）"):
                for tc in tool_calls:
                    st.info(f"**调用工具：{tc['tool']}**\n\n{tc['result']}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_text,
        "tool_calls": tool_calls
    })