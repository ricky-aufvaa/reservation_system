"""
FastAPI application for restaurant reservation system.
"""

import os
import traceback
import logging
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from huggingface_hub import InferenceClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our existing modules
import sys
import os
# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.database.connection import db_manager
from src.agent.restaurant_agent import SelfCorrectingAgent
from src.agent.intent_agent import IntentClassifierAgent
from src.tools.schemas import search_rests_tool_schema, book_reservation_tool_schema, get_conversation_history_tool_schema
from src.prompts.system_prompts import get_restaurant_system_message, get_intent_system_message
from dotenv import load_dotenv
load_dotenv() 

# Setup environment

os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")

# Initialize FastAPI app
app = FastAPI(
    title="Restaurant Reservation System API",
    description="AI-powered restaurant search and booking system with conversation memory",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM client
client = InferenceClient(model="Qwen/Qwen3-8B")
# client = InferenceClient(model="moonshotai/Kimi-K2-Thinking")



# API Models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    intent_classification: dict
    is_restaurant_related: bool

class RestaurantSearchRequest(BaseModel):
    cuisine: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    features: Optional[str] = None

class ReservationRequest(BaseModel):
    restaurant_name: str
    customer_name: str
    customer_phone: str
    party_size: int
    date: str
    time: str
    special_requests: Optional[str] = None

class ConversationHistoryRequest(BaseModel):
    limit: Optional[int] = None

# Dependency to get agents
def get_agents():
    """Create and return configured agents"""
    restaurant_agent = SelfCorrectingAgent(
        client=client,
        system=get_restaurant_system_message(),
        tools=[search_rests_tool_schema, book_reservation_tool_schema, get_conversation_history_tool_schema],
        max_retries=3
    )
    
    intent_agent = IntentClassifierAgent(
        client=client,
        system=get_intent_system_message()
    )
    
    return restaurant_agent, intent_agent

# Initialize system on startup
@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup"""
    print(" Initializing Restaurant Reservation System API...")
    db_manager.load_restaurants()
    print(" API initialized successfully!")

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Restaurant Reservation System API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

# Main chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint that handles user queries with intent classification
    """
    logger.info(f" Received chat request: {request.message}")
    
    try:
        # Step 1: Create agents
        restaurant_agent, intent_agent = get_agents()
        logger.info(" Agents created successfully")
        
        # Step 2: Classify intent
        logger.info(" Classifying intent...")
        intent_result = intent_agent(request.message)
        logger.info(f" Intent classified: {intent_result.decision} (confidence: {intent_result.relevance_score})")
        
        # Step 3: Save user message to database
        # logger.info(" Saving user message to database...")
        try:
            db_manager.save_conversation_message("user", request.message)
            logger.info(" User message saved successfully")
        except Exception as db_error:
            # logger.error(f" Database error saving user message: {db_error}")
            logger.error(f"Database error traceback: {traceback.format_exc()}")
            # Continue processing even if database save fails
        
        # Step 4: Process based on intent
        logger.info(" Processing based on intent...")
        if intent_result.decision:
            # Restaurant-related query
            logger.info("️ Processing restaurant-related query...")
            try:
                response = restaurant_agent(intent_result.description)
                # logger.info(f" Restaurant agent response received (length: {len(response)})")
            except Exception as agent_error:
                logger.error(f" Restaurant agent error: {agent_error}")
                logger.error(f"Agent error traceback: {traceback.format_exc()}")
                response = f"Sorry, I encountered an error processing your restaurant query: {str(agent_error)}"
            
            # Save assistant response
            try:
                db_manager.save_conversation_message("assistant", response)
                # logger.info(" Assistant response saved to database")
            except Exception as db_error:
                logger.error(f" Database error saving assistant message: {db_error}")
        else:
            # Non-restaurant query
            logger.info(" Non-restaurant query detected")
            response = ("I'm a restaurant assistant and can help you with:\n"
                       "• Finding restaurants by cuisine, location, or features\n"
                       "• Making restaurant reservations\n"
                       "• Restaurant recommendations\n\n"
                       "Your query doesn't seem to be restaurant-related. Could you ask about restaurants instead?")
            
            # Save assistant response
            try:
                db_manager.save_conversation_message("assistant", response)
                logger.info(" Non-restaurant response saved to database")
            except Exception as db_error:
                logger.error(f" Database error saving non-restaurant message: {db_error}")
        
        # Step 5: Prepare response
        logger.info(" Preparing response...")
        chat_response = ChatResponse(
            response=response,
            intent_classification={
                "description": intent_result.description,
                "confidence": intent_result.relevance_score
            },
            is_restaurant_related=intent_result.decision
        )
        
        logger.info(" Chat request processed successfully")
        return chat_response
        
    except Exception as e:
        logger.error(f" Critical error in chat endpoint: {e}")
        logger.error(f"Critical error traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, 
            detail={
                "error": f"Error processing chat: {str(e)}",
                "type": type(e).__name__,
                "traceback": traceback.format_exc()
            }
        )

# Restaurant search endpoint
@app.post("/search-restaurants")
async def search_restaurants(request: RestaurantSearchRequest):
    """
    Search for restaurants based on criteria
    """
    try:
        from src.tools.restaurant_tools import search_rests_tool
        
        result = search_rests_tool(
            cuisine=request.cuisine,
            location=request.location,
            capacity=request.capacity,
            features=request.features
        )
        print(f"response from search tool {result}")
        return {"result": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching restaurants: {str(e)}")

# Reservation booking endpoint
@app.post("/book-reservation")
async def book_reservation(request: ReservationRequest):
    """
    Book a restaurant reservation
    """
    try:
        from src.tools.restaurant_tools import book_reservation_tool
        
        result = book_reservation_tool(
            restaurant_name=request.restaurant_name,
            customer_name=request.customer_name,
            customer_phone=request.customer_phone,
            party_size=request.party_size,
            date=request.date,
            time=request.time,
            special_requests=request.special_requests
        )
        
        return {"result": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error booking reservation: {str(e)}")

# Conversation history endpoint
@app.post("/conversation-history")
async def get_conversation_history(request: ConversationHistoryRequest):
    """
    Get conversation history from database
    """
    try:
        from src.tools.restaurant_tools import get_conversation_history_tool
        
        result = get_conversation_history_tool(limit=request.limit)
        
        return {"result": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving conversation history: {str(e)}")

# Get all restaurants endpoint
@app.get("/restaurants")
async def get_all_restaurants():
    """
    Get all available restaurants
    """
    try:
        session = db_manager.get_session()
        from src.database.models import Restaurant
        
        restaurants = session.query(Restaurant).filter(Restaurant.is_active == True).all()
        
        restaurant_list = []
        for restaurant in restaurants:
            restaurant_list.append({
                "id": restaurant.restaurant_id,
                "name": restaurant.name,
                "cuisine": restaurant.cuisine,
                "location": restaurant.location,
                "address": restaurant.address,
                "capacity": restaurant.capacity,
                "price_range": restaurant.price_range,
                "rating": restaurant.rating,
                "features": restaurant.features,
                "phone": restaurant.phone,
                "description": restaurant.description
            })
        
        session.close()
        return {"restaurants": restaurant_list}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving restaurants: {str(e)}")

# Clear conversation history endpoint (for testing)
@app.delete("/conversation-history")
async def clear_conversation_history():
    """
    Clear all conversation history (for testing purposes)
    """
    try:
        db_manager.clear_conversation_history()
        return {"message": "Conversation history cleared successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing conversation history: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
