"""
Tool functions for restaurant search and booking operations.
"""

import uuid
import sys
import os
from typing import Optional
from datetime import datetime, timedelta

# Add project root to path for absolute imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.database.connection import db_manager
from src.database.models import Restaurant, Reservation, ConversationHistory

def search_rests_tool(cuisine: Optional[str] = None, location: Optional[str] = None, 
                     capacity: Optional[int] = None, features: Optional[str] = None):
    """
    Search for restaurants based on user criteria using OR logic.
    Returns restaurants that match ANY of the provided criteria.
    """
    session = db_manager.get_session()
    try:
        from sqlalchemy import or_
        
        # Start with base query for active restaurants
        base_query = session.query(Restaurant).filter(Restaurant.is_active == True)
        
        # Build OR conditions list
        or_conditions = []
        
        if cuisine:
            or_conditions.append(Restaurant.cuisine.ilike(f"%{cuisine}%"))
        
        if location:
            or_conditions.append(Restaurant.location.ilike(f"%{location}%"))
        
        if capacity:
            or_conditions.append(Restaurant.capacity >= capacity)
        
        if features:
            # Check if features match any of the restaurant's features
            or_conditions.append(Restaurant.features.ilike(f"%{features}%"))
        
        # If no search criteria provided, return all active restaurants
        if not or_conditions:
            restaurants = base_query.order_by(Restaurant.rating.desc()).all()
        else:
            # Apply OR logic - restaurants matching ANY criteria
            restaurants = base_query.filter(or_(*or_conditions)).order_by(Restaurant.rating.desc()).all()
        
        if not restaurants:
            return f"No restaurants found matching your criteria."
        
        # Build result with match indicators
        result = f"Found {len(restaurants)} restaurants (OR search - matching ANY criteria):\n\n"
        
        for i, restaurant in enumerate(restaurants, 1):
            restaurant_features = ", ".join(restaurant.features[:3]) if restaurant.features else "No special features"
            
            # Show which criteria matched
            matches = []
            if cuisine and cuisine.lower() in restaurant.cuisine.lower():
                matches.append(f"Cuisine: {restaurant.cuisine}")
            if location and location.lower() in restaurant.location.lower():
                matches.append(f"Location: {restaurant.location}")
            if capacity and restaurant.capacity >= capacity:
                matches.append(f"Capacity: {restaurant.capacity}+ people")
            if features and any(features.lower() in feature.lower() for feature in restaurant.features):
                matching_features = [f for f in restaurant.features if features.lower() in f.lower()]
                matches.append(f"Features: {', '.join(matching_features)}")
            
            match_info = f" (Matches: {', '.join(matches)})" if matches else ""
            
            result += f"{i}. **{restaurant.name}**{match_info}\n"
            result += f"    Location: {restaurant.location}\n"
            result += f"   ️ Cuisine: {restaurant.cuisine}\n"
            result += f"    Rating: {restaurant.rating}/5.0\n"
            result += f"    Price: {restaurant.price_range}\n"
            result += f"    Capacity: {restaurant.capacity}\n"
            result += f"    Features: {restaurant_features}\n"
            result += f"    Phone: {restaurant.phone}\n\n"
        
        print(result)
        return result
        
    except Exception as e:
        return f"Error searching restaurants: {str(e)}"
    finally:
        session.close()

def book_reservation_tool(restaurant_name: str, customer_name: str, customer_phone: str, 
                         party_size: int, date: str, time: str, special_requests: str = None):
    """
    Book a reservation at a restaurant
    """
    session = db_manager.get_session()
    try:
        # Step 1: Find the restaurant
        restaurant = session.query(Restaurant).filter(
            Restaurant.name.ilike(f"%{restaurant_name}%"),
            Restaurant.is_active == True
        ).first()
        
        if not restaurant:
            return f" Restaurant '{restaurant_name}' not found. Please check the name and try again."
        
        # Step 2: Basic validation
        if party_size > restaurant.capacity:
            return f" Sorry, {restaurant.name} has a maximum capacity of {restaurant.capacity} people. Your party size of {party_size} exceeds this limit."
        
        if party_size < 1:
            return f" Party size must be at least 1 person."
        
        # Step 3: Validate phone number (basic)
        if not customer_phone or len(customer_phone.replace('+', '').replace('-', '').replace(' ', '')) < 10:
            return f" Please provide a valid phone number."
        
        # Step 4: Create reservation
        reservation_id = str(uuid.uuid4())[:8].upper()  # Short ID like "A1B2C3D4"
        
        new_reservation = Reservation(
            reservation_id=reservation_id,
            restaurant_id=restaurant.restaurant_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            party_size=party_size,
            reservation_date=date,
            reservation_time=time,
            special_requests=special_requests,
            status='confirmed'
        )
        
        session.add(new_reservation)
        session.commit()
        
        # Step 5: Generate confirmation
        result = f" **Reservation Confirmed!**\n\n"
        result += f" **Reservation ID:** {reservation_id}\n"
        result += f" **Restaurant:** {restaurant.name}\n"
        result += f" **Location:** {restaurant.location}\n"
        result += f" **Date:** {date}\n"
        result += f" **Time:** {time}\n"
        result += f" **Party Size:** {party_size} people\n"
        result += f" **Name:** {customer_name}\n"
        result += f" **Phone:** {customer_phone}\n"
        
        if special_requests:
            result += f" **Special Requests:** {special_requests}\n"
        
        result += f"\n **Restaurant Details:**\n"
        result += f"   Address: {restaurant.address}\n"
        result += f"   Phone: {restaurant.phone}\n"
        result += f"   Rating:  {restaurant.rating}/5.0\n"
        
        result += f"\n **Important Notes:**\n"
        result += f"   • Please arrive 10 minutes before your reservation time\n"
        result += f"   • Call {restaurant.phone} if you need to make changes\n"
        result += f"   • Keep your reservation ID: {reservation_id}\n"
        
        print(f"Reservation created: {reservation_id}")
        return result
        
    except Exception as e:
        session.rollback()
        return f" Error creating reservation: {str(e)}. Please try again."
    finally:
        session.close()

def get_conversation_history_tool(limit: Optional[int] = 5):
    """
    Retrieve recent conversation history from the database for contextual follow-up questions.
    Use this tool for booking-related follow-up questions like "book the 2nd restaurant", 
    "what are the features of this place?", "which restaurant did I book last time?".
    Defaults to last 3 conversations to provide context for ambiguous references.
    """
    try:
        # Always use a limit, default to 3 for contextual queries
        conversations = db_manager.get_recent_conversations(limit or 3)
        
        if not conversations:
            return " No previous conversations found in the database."
        
        result = f" **Conversation History** ({len(conversations)} messages):\n\n"
        
        for i, conv in enumerate(conversations, 1):
            # Format timestamp for better readability
            timestamp = conv.timestamp
            
            result += f"{i}.  **{conv.role.title()}** ({timestamp}):\n"
            result += f"   {conv.content}\n\n"
        
        print(f" Retrieved {len(conversations)} conversation messages")
        return result
        
    except Exception as e:
        return f" Error retrieving conversation history: {str(e)}"
