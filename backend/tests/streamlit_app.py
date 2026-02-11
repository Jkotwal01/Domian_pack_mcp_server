"""
Streamlit UI for Domain Pack Generator Chatbot
Run with: streamlit run streamlit_app.py
"""
import streamlit as st
import requests
from datetime import datetime
import json

# Configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if "token" not in st.session_state:
    st.session_state.token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "selected_domain" not in st.session_state:
    st.session_state.selected_domain = None
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Helper functions
def get_headers():
    """Get authorization headers."""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

def login(email: str, password: str):
    """Login user and get token."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.session_state.user_email = email
            return True, "Login successful!"
        else:
            return False, f"Login failed: {response.json().get('detail', 'Unknown error')}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def signup(email: str, password: str):
    """Sign up new user."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/signup",
            json={"email": email, "password": password}
        )
        if response.status_code == 200 or response.status_code == 201:
            return True, "Signup successful! Please login."
        else:
            return False, f"Signup failed: {response.json().get('detail', 'Unknown error')}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_domains():
    """Get user's domains."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/domains",
            headers=get_headers()
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching domains: {str(e)}")
        return []

def create_domain(name: str, description: str):
    """Create a new domain."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/domains",
            headers=get_headers(),
            json={"name": name, "description": description, "version": "1.0.0"}
        )
        if response.status_code == 200 or response.status_code == 201:
            return True, response.json()
        else:
            return False, response.json().get('detail', 'Unknown error')
    except Exception as e:
        return False, str(e)

def start_chat_session(domain_id: str):
    """Start or get active chat session."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat/sessions",
            headers=get_headers(),
            json={"domain_config_id": domain_id}
        )
        if response.status_code == 200 or response.status_code == 201:
            return response.json()["id"]
        return None
    except Exception as e:
        st.error(f"Error starting session: {str(e)}")
        return None

def send_message(session_id: str, message: str):
    """Send message to chatbot."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat/sessions/{session_id}/message",
            headers=get_headers(),
            json={"message": message}
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Error sending message: {str(e)}")
        return None

# Page configuration
st.set_page_config(
    page_title="Domain Pack Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Main UI
st.title("🤖 Domain Pack Generator Chatbot")

# Sidebar for authentication and domain selection
with st.sidebar:
    st.header("🔐 Authentication")
    
    if not st.session_state.token:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login", key="login_btn"):
                success, message = login(email, password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        with tab2:
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            if st.button("Sign Up", key="signup_btn"):
                success, message = signup(email, password)
                if success:
                    st.success(message)
                else:
                    st.error(message)
    else:
        st.success(f"Logged in as: {st.session_state.user_email}")
        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.user_email = None
            st.session_state.selected_domain = None
            st.session_state.session_id = None
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        st.header("📁 Domain Selection")
        
        # Domain creation
        with st.expander("➕ Create New Domain"):
            domain_name = st.text_input("Domain Name")
            domain_desc = st.text_area("Description")
            if st.button("Create Domain"):
                if domain_name:
                    success, result = create_domain(domain_name, domain_desc)
                    if success:
                        st.success(f"Domain '{domain_name}' created!")
                        st.rerun()
                    else:
                        st.error(f"Error: {result}")
                else:
                    st.warning("Please enter a domain name")
        
        # Domain selection
        domains = get_domains()
        if domains:
            domain_options = {d["name"]: d["id"] for d in domains}
            selected_name = st.selectbox(
                "Select Domain",
                options=list(domain_options.keys()),
                index=0 if not st.session_state.selected_domain else 
                      list(domain_options.values()).index(st.session_state.selected_domain) 
                      if st.session_state.selected_domain in domain_options.values() else 0
            )
            
            if st.button("Start Chat"):
                domain_id = domain_options[selected_name]
                st.session_state.selected_domain = domain_id
                session_id = start_chat_session(domain_id)
                if session_id:
                    st.session_state.session_id = session_id
                    st.session_state.messages = []
                    st.success(f"Chat session started for '{selected_name}'!")
                    st.rerun()
        else:
            st.info("No domains found. Create one to get started!")

# Main chat area
if st.session_state.token and st.session_state.session_id:
    st.subheader("💬 Chat with AI Assistant")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                if "timestamp" in msg:
                    st.caption(msg["timestamp"])
    
    # Chat input
    if prompt := st.chat_input("Ask me to add entities, relationships, or query your domain..."):
        # Add user message to chat
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": timestamp
        })
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
            st.caption(timestamp)
        
        # Send to API and get response
        with st.spinner("Thinking..."):
            response_data = send_message(st.session_state.session_id, prompt)
            
            if response_data:
                assistant_message = response_data.get("response", "No response")
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Add assistant message to chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message,
                    "timestamp": timestamp
                })
                
                # Display assistant message
                with st.chat_message("assistant"):
                    st.write(assistant_message)
                    st.caption(timestamp)
                    
                    # Show reasoning if available
                    if "reasoning" in response_data:
                        with st.expander("🧠 Reasoning Steps"):
                            for step in response_data["reasoning"]:
                                st.write(f"• {step}")
                
                st.rerun()

elif st.session_state.token:
    st.info("👈 Please select a domain and start a chat session from the sidebar")
else:
    st.info("👈 Please login or sign up to get started")

# Footer
st.divider()
st.caption("Domain Pack Generator - Powered by FastAPI + LangGraph + GPT-3.5-Turbo")
