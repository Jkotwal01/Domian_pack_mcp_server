import streamlit as st
import requests
import json
import time
from uuid import UUID

# Configuration
API_URL = "http://localhost:8000/api/v1"

st.set_page_config(page_title="LangGraph Workflow Tester", layout="wide")

st.title("🚀 LangGraph Workflow Tester")

# Sidebar for Authentication and Session Info
with st.sidebar:
    st.header("🔑 Authentication")
    email = st.text_input("Email", value="admin@example.com")
    password = st.text_input("Password", type="password", value="admin123")
    
    if st.button("Login"):
        # FastAPI OAuth2PasswordRequestForm expects form-data with 'username' and 'password'
        response = requests.post(f"{API_URL}/auth/login", data={
            "username": email,
            "password": password
        })
        if response.status_code == 200:
            st.session_state.token = response.json().get("access_token")
            st.success("Logged in!")
        else:
            st.error("Login failed")

    if "token" in st.session_state:
        st.header("📂 Session Management")
        
        # Get existing sessions
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        sessions_resp = requests.get(f"{API_URL}/chat/sessions", headers=headers)
        
        if sessions_resp.status_code == 200:
            sessions = sessions_resp.json()
            session_options = {f"Session {s['id'][:8]}...": s['id'] for s in sessions}
            session_id_label = st.selectbox("Select Session", options=list(session_options.keys()))
            if session_id_label:
                st.session_state.current_session_id = session_options[session_id_label]
            
            if st.button("New Session"):
                # Default domain pack ID
                DOMAIN_PACK_ID = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
                new_resp = requests.post(f"{API_URL}/chat/sessions", 
                                        headers=headers,
                                        json={"domain_pack_id": DOMAIN_PACK_ID})
                if new_resp.status_code == 201:
                    st.session_state.current_session_id = new_resp.json()["id"]
                    st.rerun()

# Main Chat Interface
if "token" not in st.session_state:
    st.warning("Please login first in the sidebar.")
else:
    if "current_session_id" not in st.session_state:
        st.info("Select or create a session in the sidebar.")
    else:
        st.info(f"Active Session: {st.session_state.current_session_id}")
        
        # Chat history container
        chat_container = st.container()
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display historical messages
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    if "proposal" in msg and msg["proposal"]:
                        st.json(msg["proposal"])

        # Chat input
        if prompt := st.chat_input("What would you like to change in the domain pack?"):
            # Add user message to UI
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.write(prompt)

            # Call API
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            with st.spinner("LangGraph is thinking..."):
                resp = requests.post(
                    f"{API_URL}/chat/sessions/{st.session_state.current_session_id}/messages",
                    headers=headers,
                    json={
                        "message": prompt,
                        "domain_pack_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6" # Fixed for now
                    }
                )

            if resp.status_code == 200:
                data = resp.json()
                ai_message = data.get("message", "No response content")
                proposal = data.get("proposal")
                requires_confirmation = data.get("requires_confirmation", False)
                
                # Add AI message to UI
                msg_entry = {"role": "assistant", "content": ai_message, "proposal": proposal}
                st.session_state.messages.append(msg_entry)
                
                with chat_container:
                    with st.chat_message("assistant"):
                        st.write(ai_message)
                        if proposal:
                            st.json(proposal)
                            if requires_confirmation:
                                st.warning("⚠️ This proposal requires confirmation!")
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("Confirm Proposal", key=f"conf_{proposal['id']}"):
                                        conf_resp = requests.post(
                                            f"{API_URL}/proposals/{proposal['id']}/confirm",
                                            headers=headers
                                        )
                                        if conf_resp.status_code == 200:
                                            st.success("Proposal confirmed and committed!")
                                with col2:
                                    if st.button("Reject Proposal", key=f"rej_{proposal['id']}"):
                                        rej_resp = requests.post(
                                            f"{API_URL}/proposals/{proposal['id']}/reject",
                                            headers=headers
                                        )
                                        if rej_resp.status_code == 200:
                                            st.info("Proposal rejected.")
            else:
                st.error(f"Error calling API: {resp.text}")

st.markdown("---")
st.caption("Backend must be running at http://localhost:8000")
