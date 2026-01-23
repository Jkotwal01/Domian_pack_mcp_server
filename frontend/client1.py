# app.py — Minimal MCP + Streamlit chat (Groq API from .env)

import os
import json
import asyncio
import streamlit as st
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    ToolMessage,
    SystemMessage,
)

# ─────────────────────────────
# Load environment variables
# ─────────────────────────────
load_dotenv(override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("GROQ_API_KEY not found in .env file")
    st.stop()

# Optional sanity check
# st.write("Groq key loaded:", GROQ_API_KEY[:8])

# ─────────────────────────────
# MCP servers (LangChain format)
# ─────────────────────────────
SERVERS = {
    "Domain Pack MCP Server": {
        "transport": "stdio",
        "command": r"D:\My Code\Enable\domain-pack-mcp\.venv\Scripts\python.exe",
        "args": [r"D:\My Code\Enable\domain-pack-mcp\main.py"],
        "env": {},
    }
}

SYSTEM_PROMPT = (
    "You have access to tools. When you choose to call a tool, do not narrate status updates. "
    "After tools run, return only a concise final answer."
)

# ─────────────────────────────
# Streamlit setup
# ─────────────────────────────
st.set_page_config(page_title="MCP Chat", page_icon="🧰", layout="centered")
st.title("🧰 MCP Chat (Groq)")

# ─────────────────────────────
# One-time initialization
# ─────────────────────────────
if "initialized" not in st.session_state:
    # 1) LLM (Groq)
    st.session_state.llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama-3.1-8b-instant",  # excellent tool-use support
        temperature=0,
    )

    # 2) MCP client + tools
    st.session_state.client = MultiServerMCPClient(SERVERS)
    st.session_state.tools = asyncio.run(
        st.session_state.client.get_tools()
    )
    st.session_state.tool_by_name = {
        t.name: t for t in st.session_state.tools
    }

    # 3) Bind tools
    st.session_state.llm_with_tools = st.session_state.llm.bind_tools(
        st.session_state.tools
    )

    # 4) Conversation state
    st.session_state.history = [
        SystemMessage(content=SYSTEM_PROMPT)
    ]
    st.session_state.initialized = True

# ─────────────────────────────
# Render chat history
# ─────────────────────────────
for msg in st.session_state.history:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)

    elif isinstance(msg, AIMessage):
        # Skip intermediate assistant messages that contain tool_calls
        if getattr(msg, "tool_calls", None):
            continue
        with st.chat_message("assistant"):
            st.markdown(msg.content)

    # ToolMessage and SystemMessage are not rendered

# ─────────────────────────────
# Chat input
# ─────────────────────────────
user_text = st.chat_input("Type a message…")

if user_text:
    with st.chat_message("user"):
        st.markdown(user_text)

    st.session_state.history.append(
        HumanMessage(content=user_text)
    )

    # 1️⃣ First pass: model decides whether to call tools
    first = asyncio.run(
        st.session_state.llm_with_tools.ainvoke(
            st.session_state.history
        )
    )

    tool_calls = getattr(first, "tool_calls", None)

    if not tool_calls:
        # No tools → show response
        with st.chat_message("assistant"):
            st.markdown(first.content or "")
        st.session_state.history.append(first)

    else:
        # 2️⃣ Append assistant message WITH tool_calls (do not render)
        st.session_state.history.append(first)

        # 3️⃣ Execute tools
        tool_messages = []
        for tc in tool_calls:
            name = tc["name"]
            args = tc.get("args") or {}

            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except Exception:
                    pass

            tool = st.session_state.tool_by_name[name]
            result = asyncio.run(tool.ainvoke(args))

            tool_messages.append(
                ToolMessage(
                    tool_call_id=tc["id"],
                    content=json.dumps(result),
                )
            )

        st.session_state.history.extend(tool_messages)

        # 4️⃣ Final assistant response
        final = asyncio.run(
            st.session_state.llm.ainvoke(
                st.session_state.history
            )
        )

        with st.chat_message("assistant"):
            st.markdown(final.content or "")

        st.session_state.history.append(
            AIMessage(content=final.content or "")
        )
