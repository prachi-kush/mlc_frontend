import streamlit as st
import requests
import json
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="RAG Chatbot",
    layout="wide"
)

# Backend API configuration
# API_BASE_URL = "http://192.168.0.18:8080"
API_BASE_URL = "http://aqai8080.elb.cisinlive.com"

CHAT_ENDPOINT = f"{API_BASE_URL}/query-response"

def check_api_health():
    """Check if the FastAPI backend is available"""
    try:
        response = requests.get(f"{API_BASE_URL}/docs", timeout=30)
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
            answer = data.get("answer", "No answer provided")

            # Try to extract a 'message' from answer if it's JSON
            if isinstance(answer, str):
                try:
                    answer_json = json.loads(answer)
                    if isinstance(answer_json, dict) and "message" in answer_json:
                        answer = answer_json["message"]
                except (json.JSONDecodeError, TypeError):
                    pass
            elif isinstance(answer, dict) and "message" in answer:
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
api_available = check_api_health()

# Display connection status
if api_available:
    st.success("Connected to backend API")
else:
    st.error(f"Backend API not available. Please ensure the FastAPI server is running {API_BASE_URL}.")
    if st.button("Retry Connection"):
        st.rerun()

# Sidebar with info
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

# Temporary local chat history (will reset on refresh)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Show chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(f"**{message['timestamp']}**")
        st.write(message["content"])
        if "processing_time" in message:
            st.caption(f"*Response time: {message['processing_time']:.2f}s*")

# Chat input
if api_available:
    user_input = st.chat_input("Ask about MLC...")
    if user_input:
        user_timestamp = format_timestamp()
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": user_timestamp
        })
        with st.chat_message("user"):
            st.write(f"**{user_timestamp}**")
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("RAG Chatbot is thinking..."):
                response = send_message_to_bot(user_input)
            bot_timestamp = format_timestamp()

            if response["success"]:
                st.write(f"**{bot_timestamp}**")
                st.write(response["answer"])
                if response["processing_time"] > 0:
                    st.caption(f"*Response time: {response['processing_time']:.2f}s*")

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response["answer"],
                    "timestamp": bot_timestamp,
                    "processing_time": response["processing_time"]
                })
            else:
                st.error(f"**{bot_timestamp}**")
                st.error(f"Error: {response['error']}")
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"Error: {response['error']}",
                    "timestamp": bot_timestamp
                })
        st.rerun()
else:
    st.warning("Please ensure the FastAPI backend is running before sending messages.")

# Footer
st.markdown("---")
st.markdown("*RAG Chatbot - Maritime Labour Convention Assistant*")
