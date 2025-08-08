import streamlit as st
import requests
import json
from datetime import datetime
import time

# Configure Streamlit page
st.set_page_config(
    page_title="RAG Chatbot",
    # page_icon="🤖",
    layout="wide"
)

# Backend API configuration  
# API_BASE_URL = "http://127.0.0.1:8000"
API_BASE_URL = "http://192.168.0.18:8080" # Update with your FastAPI server URL


CHAT_ENDPOINT = f"{API_BASE_URL}/query-response"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_available" not in st.session_state:
    st.session_state.api_available = None

def check_api_health():
    """Check if the FastAPI backend is available"""
    try:
        response = requests.get(f"{API_BASE_URL}/docs", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def send_message_to_bot(message):
    """Send message to FastAPI backend and get response"""
    try:
        payload = {"query": message}
        response = requests.post(
            CHAT_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract message from the answer if it's in JSON format
            answer = data.get("answer", "No answer provided")
            if isinstance(answer, str):
                try:
                    # Try to parse the answer as JSON to extract message
                    answer_json = json.loads(answer)
                    if isinstance(answer_json, dict) and "message" in answer_json:
                        answer = answer_json["message"]
                except (json.JSONDecodeError, TypeError):
                    # If parsing fails, use the original answer
                    pass
            elif isinstance(answer, dict) and "message" in answer:
                # If answer is already a dict with message key
                answer = answer["message"]
            
            return {
                "success": True,
                "answer": answer,
                "processing_time": data.get("processing_time", 0)
            }
        else:
            return {
                "success": False,
                "error": f"API Error: {response.status_code} - {response.text}"
            }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timed out. The server might be processing a complex query."
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Connection error: {str(e)}"
        }

def format_timestamp():
    """Format current timestamp for display"""
    return datetime.now().strftime("%H:%M:%S")

# Main UI
st.title("Testing RAG Chatbot")
st.subheader("Maritime Labour Convention (MLC) Assistant")

# API Health Check
if st.session_state.api_available is None:
    with st.spinner("Checking backend connection..."):
      st.session_state.api_available = check_api_health()

# Display connection status
if st.session_state.api_available:
    st.success("Connected to backend API")
else:
    st.error(f"Backend API not available. Please ensure the FastAPI server is running {API_BASE_URL}.")
    if st.button("Retry Connection"):
        st.session_state.api_available = check_api_health()
        st.rerun()

# Sidebar with information
with st.sidebar:
    st.header("About RAG Chatbot")
    st.info(
        "RAG Chatbot is an AI assistant specialized in Maritime Labour Convention (MLC) 2006. "
        "Ask questions about maritime labor standards, seafarer rights, and MLC regulations."
    )
    
    st.header("Tips")
    st.write("• Ask specific questions about MLC")
    st.write("• Use clear, detailed queries")
    st.write("• The bot searches through official MLC documents")
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Display chat history
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(f"**{message['timestamp']}**")
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(f"**{message['timestamp']}**")
                st.write(message["content"])
                if "processing_time" in message:
                    st.caption(f"*Response time: {message['processing_time']:.2f}s*")

# Chat input
if st.session_state.api_available:
    user_input = st.chat_input("Ask about MLC...")
    
    if user_input:
        # Add user message to chat history
        timestamp = format_timestamp()
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": timestamp
        })
        
        # Display user message immediately
        with st.chat_message("user"):
            st.write(f"**{timestamp}**")
            st.write(user_input)
        
        # Show typing indicator and get bot response
        with st.chat_message("assistant"):
            with st.spinner("RAG Chatbot is thinking..."):
                response = send_message_to_bot(user_input)
            
            bot_timestamp = format_timestamp()
            
            if response["success"]:
                st.write(f"**{bot_timestamp}**")
                st.write(response["answer"])
                if response["processing_time"] > 0:
                    st.caption(f"*Response time: {response['processing_time']:.2f}s*")
                
                # Add bot response to chat history
                st.session_state.messages.append({
                    "role": "assistant",  
                    "content": response["answer"],
                    "timestamp": bot_timestamp,
                    "processing_time": response["processing_time"]
                })
            else:
                st.error(f"**{bot_timestamp}**")
                st.error(f"Error: {response['error']}")
                
                # Add error to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Error: {response['error']}",
                    "timestamp": bot_timestamp
                })
        
        st.rerun()

else:
    st.warning("Please ensure the FastAPI backend is running before sending messages.")
    st.code("cd /home/cis/RAG_backend && python main.py")

# Footer
st.markdown("---")
st.markdown("*RAG Chatbot - Maritime Labour Convention Assistant*")