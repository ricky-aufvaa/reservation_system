"""
Pydantic schemas for tool function parameters and intent classification.
"""

from pydantic import BaseModel, Field, ValidationError
from typing import Optional

class GetSearchArgs(BaseModel):
    cuisine: Optional[str] = Field(None, description="The cuisine type the user is looking for (e.g., Italian, Chinese, Indian)")
    location: Optional[str] = Field(None, description="The location where user wants to find restaurants")
    capacity: Optional[int] = Field(None, description="Minimum capacity/party size needed")
    features: Optional[str] = Field(None, description="Special features like 'outdoor seating', 'live music', etc.")

class BookReservationArgs(BaseModel):
    restaurant_name: str = Field(..., description="Name of the restaurant to book")
    customer_name: str = Field(..., description="Customer's full name")
    customer_phone: str = Field(..., description="Customer's phone number")
    party_size: int = Field(..., description="Number of people for the reservation")
    date: str = Field(..., description="Reservation date (e.g., '2025-12-15' or 'tomorrow')")
    time: str = Field(..., description="Reservation time (e.g., '19:00' or '7:00 PM')")
    special_requests: Optional[str] = Field(None, description="Any special requests or dietary requirements")

# Tool schemas for the LLM
search_rests_tool_schema = {
    "type": "function",
    "function": {
        "name": "search_rests_tool",
        "description": "Gets a list of restaurants pertaining to the user's request based on cuisine, location, capacity, and features.",
        "parameters": GetSearchArgs.model_json_schema()
    }
}

book_reservation_tool_schema = {
    "type": "function",
    "function": {
        "name": "book_reservation_tool",
        "description": "Book a reservation at a restaurant. Requires restaurant name, customer details, party size, date, and time.",
        "parameters": BookReservationArgs.model_json_schema()
    }
}

class GetConversationHistoryArgs(BaseModel):
    limit: Optional[int] = Field(5, description="Maximum number of recent conversations to retrieve. Defaults to 5 for contextual follow-up questions during booking.")

get_conversation_history_tool_schema = {
    "type": "function",
    "function": {
        "name": "get_conversation_history_tool",
        "description": "Retrieve recent conversation history for contextual follow-up questions during booking. Use for queries like 'book the 2nd restaurant', 'what are the features of this place?', 'which restaurant did I book last time?'. Fetches last 5 conversations by default.",
        "parameters": GetConversationHistoryArgs.model_json_schema()
    }
}

class IntentResponse(BaseModel):
    """
    Intent classification response for restaurant-related queries.
    
    This model determines whether a user query is related to restaurants and provides
    a confidence score for the classification decision.
    
    Attributes:
        description (str): A clear, concise description of what the query is asking for
        decision (bool): True if the query is restaurant-related, False otherwise
        relevance_score (float): Confidence score between 0.0 and 1.0 indicating how
                                relevant the query is to restaurant services
    
    Examples:
        Restaurant-related query:
        {
            "description": "User is looking for Italian restaurants in a specific location",
            "decision": true,
            "relevance_score": 0.95
        }
        
        Non-restaurant query:
        {
            "description": "User is asking about weather information",
            "decision": false,
            "relevance_score": 0.1
        }
    """
    description: str = Field(
        ..., 
        description="Clear, detailed description of what the user query is requesting. Should be specific and informative.",
    )
    
    decision: bool = Field(
        ..., 
        description="Boolean decision: True if query is related to restaurants (search, booking, recommendations, reviews), False otherwise"
    )
    
    relevance_score: float = Field(
        ..., 
        description="Confidence score between 0.0 and 1.0. Higher scores (0.8-1.0) indicate strong restaurant relevance, lower scores (0.0-0.3) indicate non-restaurant queries",
        ge=0.0,
        le=1.0
    )
