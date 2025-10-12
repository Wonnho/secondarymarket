import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage,ToolMessage
from dotenv import load_dotenv
import os
from header import render_header

st.set_page_config(
    page_title="상장종목조회",
    page_icon="📊",
    layout="wide"
)

render_header()

#st.title("📊 상장종목조회")

load_dotenv('../.env')
api_key = os.getenv("OPENAI_API_KEY")

llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.9,api_key=api_key)

from langchain_core.tools import tool
from datetime import datetime
from zoneinfo import ZoneInfo
import pytz
  
@tool
def get_current_time(timezone: str, location: str) -> str:
    """Get the current time in a given location."""
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")  # ← 이 줄 수정
        result = f'{timezone} ({location}) current time is {now}'
        print(result)
        return result
    except pytz.UnknownTimeZoneError as e:
        return f"Unknown timezone: {timezone}"
    
tools=[get_current_time]
tool_dict={"get_current_time":get_current_time}

llm_with_tools=llm.bind_tools(tools)

def get_ai_response(messages):
    response = llm_with_tools.stream(messages)
    
    gethered=None
    for chunk in response:
        yield chunk

        if gethered is None:
            gethered = chunk
        else:
            gethered += chunk
    
    if gethered.tool_calls:
        st.session_state.messages.append(gethered)

    
        for tool_call in gethered.tool_calls:
            selected_tool = tool_dict[tool_call['name']]
            tool_msg=selected_tool.invoke(tool_call)
            print(tool_msg,type(tool_msg))
            st.session_state.messages.append(tool_msg)

        for chunk in get_ai_response(st.session_state["messages"]):
            yield chunk

st.title("StockBot, LangChain RAG Chatbot with Streamlit")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        SystemMessage(content="You are a helpful assistant."),
        AIMessage(content="Hello! How can I assist you today?")
        
    ]

for msg in st.session_state.messages:
    if msg.content:
        if isinstance(msg, SystemMessage):
            st.chat_message("system").write(msg.content)
        elif isinstance(msg, AIMessage):
            st.chat_message("assistant").write(msg.content)
        elif isinstance(msg, HumanMessage):
            st.chat_message("user").write(msg.content)
        elif isinstance(msg, ToolMessage):
            st.chat_message("tool").write(msg.content)

if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    st.session_state.messages.append(HumanMessage(prompt))

    response=get_ai_response(st.session_state["messages"])
    result=st.chat_message("assistant").write_stream(response)
    st