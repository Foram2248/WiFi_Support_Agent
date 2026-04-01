from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import time

from app.state import ConversationState
from app.controller import handle_user_input
from app.parser import parse_user_input

app = FastAPI()

# CORS (for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# session_id -> { state, last_updated }
sessions = {}

# Session expiry time (in seconds)
SESSION_TTL = 1800  # 30 minutes

# Request / Response models
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    ended: bool  


# Cleanup
def cleanup_sessions():
    current_time = time.time()

    expired_sessions = [
        session_id
        for session_id, data in sessions.items()
        if current_time - data["last_updated"] > SESSION_TTL
    ]

    for session_id in expired_sessions:
        del sessions[session_id]


# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    # --- Step 0: Cleanup old sessions ---
    cleanup_sessions()

    # --- Step 1: Validate input ---
    if not request.message or not request.message.strip():
        session_id = request.session_id or str(uuid.uuid4())
        return ChatResponse(
            reply="Please enter a message so I can help you.",
            session_id=session_id,
            ended=False
        )

    # --- Step 2: Get or create session ---
    if not request.session_id:
        session_id = str(uuid.uuid4())
    else:
        session_id = request.session_id

    if session_id not in sessions:
        sessions[session_id] = {
            "state": ConversationState(),
            "last_updated": time.time()
        }

    state = sessions[session_id]["state"]

    # Update timestamp
    sessions[session_id]["last_updated"] = time.time()

    # --- Step 3: Parse input ---
    parsed_input = parse_user_input(request.message)
    parsed_input["raw_message"] = request.message

    # --- Debug logs  ---
    print("\n================ NEW MESSAGE ================")
    print(f"[USER]: {request.message}")
    print(f"[PARSED]: {parsed_input}")
    print(f"[STATE BEFORE]: {state.to_dict()}")

    # --- Step 4: Handle flow ---
    try:
        reply = handle_user_input(state, parsed_input)
    except Exception as e:
        print("[ERROR]:", str(e))
        # reset state on failure (prevents broken sessions)
        sessions[session_id]["state"] = ConversationState()
        reply = "Something went wrong. Let's start again."

    # --- Debug logs after processing ---
    print(f"[STATE AFTER]: {state.to_dict()}")
    print(f"[BOT]: {reply}")
    print("=============================================\n")

    # --- Step 5: Return response ---
    return ChatResponse(
        reply=reply,
        session_id=session_id,
        ended=state.stage == "end"
    )