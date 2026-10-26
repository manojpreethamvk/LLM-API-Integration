
# Context-Aware AI Chatbot

A multi-turn AI chatbot powered by Google's Gemini API.
Built with Python, FastAPI, and Streamlit.

## Features

- Gemini API integration
- Multi-turn conversation history
- Separate memory for each conversation ID
- Context window management using last-N-message truncation
- Custom system prompt and chatbot personality
- API error handling and timeout messages
- Streamlit chat interface
- Environment-based API key configuration

## Technology Stack

- Python
- Google Gemini API
- Google Gen AI Python SDK
- FastAPI
- Streamlit
- Requests
- python-dotenv

## Project Structure

```text
context-aware-chatbot/
├── main.py
├── app.py
├── test_gemini.py
├── list_models.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

The `.env` file is local and must not be committed to GitHub.

## Setup Instructions

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd context-aware-chatbot
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a `.env` file in the project root:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
```

Replace the example value with your own key.

### 5. Start the backend

```bash
uvicorn main:app --reload
```

Backend URL: http://127.0.0.1:8000

Interactive API documentation:
http://127.0.0.1:8000/docs

### 6. Start the frontend

Open a second terminal and run:

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit.

## Context Management

The backend stores conversation messages by conversation ID.
For each new request, it sends only the latest 10 previous
messages plus the current user message to Gemini.

This limits the amount of conversation history sent with
each API request.

## Error Handling

The application handles failed Gemini requests and returns
a readable error response. The Streamlit frontend displays
messages when the backend cannot be reached or a request
times out.

## Limitations

- Conversation history is stored in memory and is lost when
  the backend restarts.
- The context limit is based on message count, not tokens.
- Gemini availability and quotas depend on the API account.

## Security

- API keys are loaded from environment variables.
- Never commit `.env` or publish API keys.
- Revoke and replace any key accidentally exposed publicly.

## Author

Manoj Preetham

## License

Add an appropriate license if you intend to distribute this
project publicly.
