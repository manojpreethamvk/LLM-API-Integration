
import os
import uuid
import logging
from threading import Lock
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from google.genai.errors import ServerError

# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("contextbot")

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Check your .env file."
    )

# Try the working model first, then a fallback.
MODELS_TO_TRY = [
    "gemini-flash-lite-latest",
    "gemini-3.1-flash-lite",
]

client = genai.Client(
    api_key=API_KEY,
    http_options=types.HttpOptions(timeout=30000),
)

# --------------------------------------------------
# 2. FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="Context-Aware AI Chatbot",
    description="A Gemini chatbot with conversation memory.",
    version="1.0.0",
)

# --------------------------------------------------
# 3. System prompt
# --------------------------------------------------

SYSTEM_PROMPT = """
You are ContextBot, a friendly and helpful AI assistant.

Your responsibilities:
1. Answer questions clearly and accurately.
2. Use earlier messages in the current conversation
   when relevant.
3. Maintain a friendly and professional tone.
4. Do not invent facts when you do not know the answer.
5. Keep answers concise unless more detail is requested.
"""

# --------------------------------------------------
# 4. Conversation memory
# --------------------------------------------------

# Each conversation ID has a separate message history.
conversations = {}

conversation_lock = Lock()

# Send at most 10 previous messages plus the current message.
MAX_HISTORY_MESSAGES = 10


# --------------------------------------------------
# 5. Request and response schemas
# --------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=10000,
        description="The user's message",
    )

    conversation_id: Optional[str] = Field(
        default=None,
        description="Existing conversation ID",
    )


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str


# --------------------------------------------------
# 6. Health endpoint
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "status": "running",
        "project": "Context-Aware AI Chatbot",
        "models": MODELS_TO_TRY,
    }


# --------------------------------------------------
# 7. Chat endpoint
# --------------------------------------------------

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    conversation_id = (
        request.conversation_id or str(uuid.uuid4())
    )

    # Get the previous conversation history.
    with conversation_lock:
        history = conversations.setdefault(
            conversation_id, []
        )

        recent_history = [
            item.copy() for item
            in history[-MAX_HISTORY_MESSAGES:]
        ]

    # Add the current user message to the context.
    recent_history.append({
        "role": "user",
        "parts": [{"text": message}],
    })

    # --------------------------------------------------
    # 8. Call Gemini with model fallback
    # --------------------------------------------------

    reply = None
    last_error = None

    for model_name in MODELS_TO_TRY:
        try:
            logger.info(
                "Sending request using model: %s",
                model_name,
            )

            response = client.models.generate_content(
                model=model_name,
                contents=recent_history,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.7,
                ),
            )

            if response.text and response.text.strip():
                reply = response.text.strip()

                logger.info(
                    "Gemini succeeded using %s",
                    model_name,
                )
                break

            logger.warning(
                "Model %s returned an empty response.",
                model_name,
            )

        except ServerError as error:
            last_error = error

            logger.warning(
                "Server error using %s. Trying next model.",
                model_name,
                exc_info=True,
            )

        except Exception as error:
            # Authentication, quota, invalid requests and
            # other errors may need a different fix.
            last_error = error

            logger.exception(
                "Gemini request failed using %s",
                model_name,
            )

            # Do not repeatedly call another model for
            # every type of error.
            break

    if reply is None:
        if last_error is not None:
            logger.error(
                "All usable Gemini attempts failed. "
                "Last error type: %s",
                type(last_error).__name__,
            )

        raise HTTPException(
            status_code=502,
            detail=(
                "Gemini could not generate a response. "
                "Check the backend terminal for details "
                "and try again later."
            ),
        )

    # --------------------------------------------------
    # 9. Save successful conversation messages
    # --------------------------------------------------

    with conversation_lock:
        conversations.setdefault(
            conversation_id, []
        ).extend([
            {
                "role": "user",
                "parts": [{"text": message}],
            },
            {
                "role": "model",
                "parts": [{"text": reply}],
            },
        ])

    logger.info(
        "Chat response successful. Conversation ID: %s",
        conversation_id,
    )

    # --------------------------------------------------
    # 10. Return the response
    # --------------------------------------------------

    return ChatResponse(
        conversation_id=conversation_id,
        reply=reply,
    )
