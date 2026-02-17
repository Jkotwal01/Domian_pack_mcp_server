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

def get_chat_history(session_id: str):
    """Fetch chat history from API."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/chat/sessions/{session_id}/messages",
            headers=get_headers()
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Error fetching history: {str(e)}")
        return []

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
            # Check if it's a validation error
            try:
                detail = response.json().get('detail', 'Unknown error')
            except:
                detail = response.text
            st.error(f"Error: {detail}")
            return None
    except Exception as e:
        st.error(f"Error sending message: {str(e)}")
        return None

# Page configuration
st.set_page_config(
    page_title="Domain Pack AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better aesthetics
st.markdown("""
<style>
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .stChatMessageUser {
        background-color: #f0f2f6;
    }
    .diff-added { color: #28a745; font-weight: bold; }
    .diff-removed { color: #d73a49; font-weight: bold; }
    .diff-modified { color: #005cc5; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Main UI
st.title("🤖 Domain Pack AI Assistant")

# Sidebar for authentication and domain selection
with st.sidebar:
    st.header("🔐 Authentication")
    
    if not st.session_state.token:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login", key="login_btn", use_container_width=True):
                success, message = login(email, password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        with tab2:
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            if st.button("Sign Up", key="signup_btn", use_container_width=True):
                success, message = signup(email, password)
                if success:
                    st.success(message)
                else:
                    st.error(message)
    else:
        st.success(f"Logged in as: {st.session_state.user_email}")
        if st.button("Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.user_email = None
            st.session_state.selected_domain = None
            st.session_state.session_id = None
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        st.header("📁 Domain Selection")
        
        # Domain selection
        domains = get_domains()
        if domains:
            domain_options = {d["name"]: d for d in domains}
            selected_name = st.selectbox(
                "Select Domain",
                options=list(domain_options.keys()),
                index=0 if not st.session_state.selected_domain else 
                      [d["id"] for d in domains].index(st.session_state.selected_domain) 
                      if st.session_state.selected_domain in [d["id"] for d in domains] else 0
            )
            
            selected_domain_obj = domain_options[selected_name]
            
            if st.button("Open Chat Session", use_container_width=True):
                st.session_state.selected_domain = selected_domain_obj["id"]
                session_id = start_chat_session(selected_domain_obj["id"])
                if session_id:
                    st.session_state.session_id = session_id
                    # Load history
                    history = get_chat_history(session_id)
                    st.session_state.messages = [
                        {"role": m["role"], "content": m["message"], "timestamp": m["created_at"]}
                        for m in history
                    ]
                    st.success(f"Session active!")
                    st.rerun()
        
        # Domain creation
        with st.expander("➕ Create New Domain"):
            domain_name = st.text_input("Domain Name")
            domain_desc = st.text_area("Description")
            if st.button("Create Domain", use_container_width=True):
                if domain_name:
                    success, result = create_domain(domain_name, domain_desc)
                    if success:
                        st.success(f"Created!")
                        st.rerun()
                    else:
                        st.error(f"Error: {result}")
                else:
                    st.warning("Enter name")

# Layout with two columns: Chat and Live Config
col1, col2 = st.columns([2, 1])

with col1:
    if st.session_state.token and st.session_state.session_id:
        st.subheader("💬 Conversation")
        
        # Display chat messages
        chat_container = st.container(height=500)
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
        
        # Confirmation buttons if last message needs it
        if st.session_state.messages and "apply?" in st.session_state.messages[-1]["content"].lower():
            c1, c2, _ = st.columns([1, 1, 4])
            with c1:
                if st.button("✅ Yes, Apply", type="primary", use_container_width=True):
                    with st.spinner("Applying..."):
                        response = send_message(st.session_state.session_id, "yes")
                        if response:
                            st.session_state.messages.append({"role": "user", "content": "yes"})
                            st.session_state.messages.append({"role": "assistant", "content": response["message"]})
                            st.rerun()
            with c2:
                if st.button("❌ No, Cancel", type="secondary", use_container_width=True):
                    with st.spinner("Cancelling..."):
                        response = send_message(st.session_state.session_id, "no")
                        if response:
                            st.session_state.messages.append({"role": "user", "content": "no"})
                            st.session_state.messages.append({"role": "assistant", "content": response["message"]})
                            st.rerun()

        # Chat input
        if prompt := st.chat_input("E.g., 'Add email attribute to User entity' or 'Rename OWNS to OWNS_PRODUCT'"):
            # Add user message to state
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Send to API
            with st.spinner("Thinking..."):
                response_data = send_message(st.session_state.session_id, prompt)
                
                if response_data:
                    assistant_message = response_data["message"]
                    
                    # If we have proposed changes, we can display them more prominently
                    if response_data.get("proposed_changes"):
                        st.session_state.last_proposed_patch = response_data["proposed_changes"]
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": assistant_message
                    })
                    st.rerun()

    elif st.session_state.token:
        st.info("👈 Select a domain and start a session to begin editing.")
    else:
        st.info("👈 Login to start using the Domain Pack AI Assistant.")

with col2:
    if st.session_state.token and st.session_state.selected_domain:
        st.subheader("📊 Live Configuration")
        
        # Fetch latest domain data to show live config
        domains = get_domains()
        selected_domain = next((d for d in domains if d["id"] == st.session_state.selected_domain), None)
        
        if selected_domain:
            # Stats
            s1, s2 = st.columns(2)
            s1.metric("Entities", selected_domain["entity_count"])
            s2.metric("Relationships", selected_domain["relationship_count"])
            
            # Config preview
            st.write("Current Schema:")
            st.json(selected_domain["config_json"], expanded=1)
            
            # Operations Guide
            with st.expander("📖 Supported Operations"):
                st.markdown("""
                - **Entities**: Add, Rename, Delete, Update Description
                - **Attributes**: Add, Rename, Delete, Update Examples
                - **Relationships**: Add, Rename, Delete, Update From/To
                - **Metadata**: Update Domain Name, Version, Description
                - **Extraction**: Patterns, Key Terms
                - **Synonyms**: Add/Update/Delete
                """)
        else:
            st.warning("Domain not found")

# Footer
st.divider()
st.caption("🚀 Optimized with LangGraph | Cost: ~$0.0006/edit | Token Reduction: ~90%")
