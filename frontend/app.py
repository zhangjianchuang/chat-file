import streamlit as st
import requests

# Backend Configuration
BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="DeepSeek Chat File", page_icon="📄", layout="wide")

st.title("📄 Chat with your Files (DeepSeek)")

# --- Session State Management ---
# Fetch backend status on app load
if "backend_status" not in st.session_state:
    try:
        status_res = requests.get(f"{BACKEND_URL}/status", timeout=2)
        if status_res.status_code == 200:
            st.session_state.backend_status = status_res.json()
        else:
            st.session_state.backend_status = {"active": False}
    except:
        st.session_state.backend_status = {"active": False}

# --- Sidebar: File Upload & Status ---
with st.sidebar:
    st.header("Upload Document")
    
    # Show Active File info if exists
    status = st.session_state.backend_status
    if status.get("active"):
        st.info(f"✅ **Active File:**\n\n`{status['filename']}`\n\nMode: **{status['type'].upper()}**")
        st.caption("Upload a new file below to replace it.")
    
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "md", "csv", "xlsx"])
    
    if uploaded_file is not None:
        if st.button("Process File"):
            with st.spinner("Uploading and Indexing..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    response = requests.post(f"{BACKEND_URL}/upload", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success(data.get("message", "File processed!"))
                        # Update session state locally to reflect change immediately
                        st.session_state.backend_status = {
                            "active": True,
                            "filename": data["filename"],
                            "type": "pandas" if data["filename"].endswith((".csv", ".xlsx", ".xls")) else "rag"
                        }
                        st.rerun() # Refresh to show new status
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection failed: {e}")

    st.markdown("---")
    st.markdown("### Instructions")
    st.markdown("1. Upload a document.")
    st.markdown("2. Click **Process File**.")
    st.markdown("3. Start chatting!")

# --- Main Chat Interface ---

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask something about your document..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            with st.spinner("Analyzing context..."):
                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"message": prompt}
                )
                
            if response.status_code == 200:
                data = response.json()
                full_response = data.get("response", "")
                steps = data.get("steps", [])

                # Show reasoning steps if available (e.g. for Excel analysis)
                if steps:
                    with st.expander("🕵️ Agent Reasoning & Code Execution", expanded=False):
                        for step in steps:
                            st.markdown(f"**Action:** `{step['tool']}`")
                            # Highlight Python code if present
                            if "python" in step['tool'].lower():
                                st.code(step['input'].get('query', step['input']), language='python')
                            else:
                                st.text(f"Input: {step['input']}")
                            
                            st.markdown("**Result:**")
                            st.text(step['output'])
                            st.divider()

                message_placeholder.markdown(full_response)
                
                # Add to history (we only store the final answer for simplicity, or could store steps too)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.error(f"Backend Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the backend. Is it running?")