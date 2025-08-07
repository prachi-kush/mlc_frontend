# RAG Chatbot - Streamlit Frontend

A clean, functional chat interface for the FastAPI chatbot backend, specialized in Maritime Labour Convention (MLC) 2006 assistance.

## Features

- **Real-time Chat Interface**: Send messages and receive responses from the chatbot
- **Connection Health Check**: Automatically verifies backend API availability
- **Chat History**: Persistent conversation history within the session
- **Response Time Display**: Shows processing time for each bot response
- **Error Handling**: Graceful handling of API connection issues and timeouts
- **Clean UI**: Modern chat interface with user/bot message differentiation
- **Sidebar Information**: About section and usage tips

## Prerequisites

- Python 3.12
- FastAPI backend running on `http://127.0.0.1:8000`

## Installation

1. **Install dependencies:**
   ```bash
   cd frontend_path
   pip install -r requirements.txt
   ```

## Running the Application

### Step 1: Start the FastAPI Backend
```bash
cd backend_path
source venv/bin/activate
python run.py
```
The backend should be running on `http://127.0.0.1:8000`

#### Network Access (Option 1 - Standard Port):
```bash
cd frontend_path
streamlit run chat_ui.py --server.address 0.0.0.0 --server.port 8501
```
Clients access at: `http://YOUR_SERVER_IP:8501`

#### Network Access (Option 2 - Web Port):
```bash
cd frontend_path
streamlit run chat_ui.py --server.address 0.0.0.0 --server.port 80
```
Clients access at: `http://YOUR_SERVER_IP` (may require sudo for port 80)

## Usage

1. **Start Chatting**: Type your question about Maritime Labour Convention (MLC) in the chat input
2. **View Responses**: Bot will search through MLC documents and provide detailed answers
3. **Monitor Performance**: Response times are displayed for each interaction
4. **Clear History**: Use the "Clear Chat History" button in the sidebar to reset the conversation
5. **Connection Status**: The app displays whether the backend API is available

## API Integration

The frontend connects to the FastAPI backend via:
- **Endpoint**: `POST /query-response`
- **Payload**: `{"query": "your question here"}`
- **Response**: JSON with answer and processing time


### Backend Not Available
- Ensure the FastAPI server is running: `source venv/bin/activate && python main.py` in the backend directory
- Check that port 8000 is not blocked by firewall
- Verify the backend is accessible at `http://127.0.0.1:8000/docs`

### Slow Responses
- Response times depend on query complexity and semantic search
- Typical response times: 2-10 seconds for complex queries
- Timeout is set to 30 seconds

### Connection Errors
- Check your internet connection
- Verify the backend API is running and accessible
- Use the "Retry Connection" button to reconnect

## Technical Details

- **Frontend Framework**: Streamlit
- **HTTP Client**: Python requests library
- **Session Management**: Streamlit session state
- **Response Timeout**: 30 seconds
- **Health Check**: Automatic backend availability verification