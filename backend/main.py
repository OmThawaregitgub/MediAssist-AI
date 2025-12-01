from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uvicorn
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="MediAssist AI API",
    description="Medical Research Assistant Backend",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class ChatRequest(BaseModel):
    query: str
    conversation_id: str = None
    use_reranking: bool = True
    top_k: int = 10

class ChatResponse(BaseModel):
    answer: str
    conversation_id: str
    message_id: int
    sources: list
    confidence: float
    is_hallucination: bool
    hallucination_confidence: float
    suggested_questions: list

# Mock user database
users_db = {
    "testuser": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpass",  # In real app, this would be hashed
        "is_active": True,
        "is_admin": False
    }
}

# Mock conversations
conversations_db = {}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MediAssist AI API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    """Register a new user (mock)"""
    if user_data.username in users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create user
    user_id = len(users_db) + 1
    users_db[user_data.username] = {
        "id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "password": user_data.password,  # Should be hashed in production
        "is_active": True,
        "is_admin": False
    }
    
    return Token(
        access_token=f"mock_token_{user_id}",
        token_type="bearer",
        user={
            "id": user_id,
            "username": user_data.username,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "is_active": True,
            "is_admin": False
        }
    )

@app.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    """Login user (mock)"""
    user = users_db.get(user_data.username)
    
    if not user or user["password"] != user_data.password:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    return Token(
        access_token=f"mock_token_{user['id']}",
        token_type="bearer",
        user={
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "is_active": user["is_active"],
            "is_admin": user["is_admin"]
        }
    )

@app.get("/auth/me")
async def get_current_user(authorization: str = None):
    """Get current user info (mock)"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    
    # Find user by token (mock)
    for user in users_db.values():
        if token == f"mock_token_{user['id']}":
            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "full_name": user["full_name"],
                "is_active": user["is_active"],
                "is_admin": user["is_admin"]
            }
    
    raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/chat/query", response_model=ChatResponse)
async def chat_query(request: ChatRequest, authorization: str = None):
    """Process a chat query (mock)"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Mock response
    return ChatResponse(
        answer=f"I'm a mock response to: {request.query}. In the real application, I would search through medical research to provide evidence-based answers.",
        conversation_id=request.conversation_id or f"conv_{datetime.now().timestamp()}",
        message_id=1,
        sources=[{"text": "Sample source text from medical research.", "score": 0.95}],
        confidence=0.85,
        is_hallucination=False,
        hallucination_confidence=0.1,
        suggested_questions=[
            "What are the benefits of this approach?",
            "Are there any risks I should know about?",
            "How does this compare to other methods?"
        ]
    )

@app.get("/chat/conversations")
async def get_conversations(authorization: str = None):
    """Get user's conversations (mock)"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Mock conversations
    return [
        {
            "id": "conv_1",
            "title": "First conversation",
            "created_at": "2024-01-01T10:00:00",
            "updated_at": "2024-01-01T10:30:00",
            "message_count": 5
        },
        {
            "id": "conv_2",
            "title": "About intermittent fasting",
            "created_at": "2024-01-02T14:00:00",
            "updated_at": "2024-01-02T14:45:00",
            "message_count": 8
        }
    ]

@app.get("/chat/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, authorization: str = None):
    """Get a specific conversation (mock)"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Mock conversation
    return {
        "id": conversation_id,
        "title": "Mock Conversation",
        "created_at": "2024-01-01T10:00:00",
        "messages": [
            {
                "role": "user",
                "content": "Hello, what is intermittent fasting?",
                "timestamp": "2024-01-01T10:00:00"
            },
            {
                "role": "assistant",
                "content": "Intermittent fasting is an eating pattern that cycles between periods of fasting and eating.",
                "timestamp": "2024-01-01T10:00:30"
            }
        ]
    }

@app.post("/chat/conversations/new")
async def create_new_conversation(title: str = "New Conversation", authorization: str = None):
    """Create a new conversation (mock)"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    conv_id = f"conv_{datetime.now().timestamp()}"
    return {"conversation_id": conv_id, "message": "Conversation created"}

@app.delete("/chat/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, authorization: str = None):
    """Delete a conversation (mock)"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {"message": "Conversation deleted successfully"}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )