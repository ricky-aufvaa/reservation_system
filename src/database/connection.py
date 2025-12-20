"""
Database connection manager for the restaurant reservation system.
"""

import sqlite3
import json
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Restaurant, ConversationHistory

class DatabaseManager:
    def __init__(self):
        self.db_path = Path("data/simple_restaurants.db")
        self.db_path.parent.mkdir(exist_ok=True)
        
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()
    
    def load_restaurants(self):
        """Load restaurant data from JSON file"""
        session = self.get_session()
        try:
            # Check if data already exists
            if session.query(Restaurant).count() > 0:
                print("✅ Restaurant data already loaded")
                return
            
            # Load from JSON
            with open("data/restaurants.json", 'r', encoding='utf-8') as f:
                restaurants_data = json.load(f)
            
            for restaurant_data in restaurants_data:
                restaurant = Restaurant(**restaurant_data)
                session.add(restaurant)
            
            session.commit()
            print(f"✅ Loaded {len(restaurants_data)} restaurants")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error loading restaurants: {e}")
        finally:
            session.close()
    
    def save_conversation_message(self, role: str, content: str):
        """Save a conversation message to the database"""
        print(f"🔄 Attempting to save {role} message: '{content[:50]}...'")
        session = self.get_session()
        try:
            # Get the next message index
            print("📊 Getting last message for index calculation...")
            last_message = session.query(ConversationHistory).order_by(ConversationHistory.id.desc()).first()
            next_index = (last_message.message_index + 1) if last_message else 1
            print(f"📈 Next message index will be: {next_index}")
            
            print("🏗️ Creating ConversationHistory object...")
            message = ConversationHistory(
                message_index=next_index,
                role=role,
                content=content
            )
            print(f"✅ ConversationHistory object created: {message}")
            
            print("💾 Adding to session and committing...")
            session.add(message)
            session.commit()
            print(f"✅ Successfully saved {role} message to conversation history")
        except Exception as e:
            session.rollback()
            print(f"❌ Error saving conversation message: {e}")
            print(f"❌ Error type: {type(e).__name__}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            
            # If it's a schema error, try to recreate the table
            if "NOT NULL constraint failed" in str(e) or "no such column" in str(e):
                print("🔄 Attempting to fix database schema...")
                try:
                    self.recreate_conversation_table()
                    print("✅ Database schema recreated, retrying save...")
                    # Retry the save operation
                    message = ConversationHistory(
                        message_index=1,  # Start fresh
                        role=role,
                        content=content
                    )
                    session.add(message)
                    session.commit()
                    print(f"✅ Successfully saved {role} message after schema fix")
                except Exception as retry_error:
                    print(f"❌ Failed to save even after schema fix: {retry_error}")
        finally:
            session.close()
    
    def get_all_conversations(self):
        """Retrieve all conversation history from the database"""
        session = self.get_session()
        try:
            conversations = session.query(ConversationHistory).order_by(ConversationHistory.id).all()
            return conversations
        except Exception as e:
            print(f"❌ Error retrieving conversations: {e}")
            return []
        finally:
            session.close()
    
    def get_recent_conversations(self, limit: int = 10):
        """Retrieve recent conversation history"""
        session = self.get_session()
        try:
            conversations = session.query(ConversationHistory).order_by(
                ConversationHistory.id.desc()
            ).limit(limit).all()
            # Reverse to get chronological order
            return list(reversed(conversations))
        except Exception as e:
            print(f"❌ Error retrieving recent conversations: {e}")
            return []
        finally:
            session.close()
    
    def clear_conversation_history(self):
        """Clear all conversation history (for testing/reset)"""
        session = self.get_session()
        try:
            session.query(ConversationHistory).delete()
            session.commit()
            print("🗑️ Cleared all conversation history")
        except Exception as e:
            session.rollback()
            print(f"❌ Error clearing conversation history: {e}")
        finally:
            session.close()
    
    def recreate_conversation_table(self):
        """Recreate the conversation history table with correct schema"""
        try:
            # Drop and recreate the conversation_history table
            ConversationHistory.__table__.drop(self.engine, checkfirst=True)
            ConversationHistory.__table__.create(self.engine)
            print("✅ Recreated conversation_history table with correct schema")
        except Exception as e:
            print(f"❌ Error recreating conversation table: {e}")

# Global database manager instance
db_manager = DatabaseManager()
