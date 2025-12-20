"""
Database models for the restaurant reservation system.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, JSON
from datetime import datetime

Base = declarative_base()

class Restaurant(Base):
    __tablename__ = 'restaurants'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_id = Column(String(36), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    cuisine = Column(String(50), nullable=False)
    location = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    capacity = Column(Integer, nullable=False)
    price_range = Column(String(10), nullable=False)  # ₹, ₹₹, ₹₹₹, ₹₹₹₹
    rating = Column(Float, nullable=False)
    features = Column(JSON)  # Store as JSON array
    operating_hours = Column(JSON)  # Store operating hours as JSON
    phone = Column(String(20), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Restaurant(name='{self.name}', cuisine='{self.cuisine}', location='{self.location}')>"

class Reservation(Base):
    __tablename__ = 'reservations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    reservation_id = Column(String(36), unique=True, nullable=False)
    restaurant_id = Column(String(36), nullable=False)  # Links to restaurant
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    party_size = Column(Integer, nullable=False)
    reservation_date = Column(String(20), nullable=False)  # Store as string for simplicity
    reservation_time = Column(String(10), nullable=False)  # e.g., "19:00"
    special_requests = Column(Text)
    status = Column(String(20), default='confirmed')  # confirmed, cancelled
    created_at = Column(String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    def __repr__(self):
        return f"<Reservation(id='{self.reservation_id}', restaurant_id='{self.restaurant_id}', customer='{self.customer_name}')>"

class ConversationHistory(Base):
    __tablename__ = 'conversation_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_index = Column(Integer, nullable=False, default=0)  # Add missing column
    role = Column(String(20), nullable=False)  # 'user', 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    def __repr__(self):
        return f"<ConversationHistory(id={self.id}, role='{self.role}', timestamp='{self.timestamp}')>"
