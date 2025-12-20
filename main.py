"""
Main application for the restaurant reservation system with intent classification.
"""

import os
from huggingface_hub import InferenceClient
from src.database.connection import db_manager
from src.tools.restaurant_tools import search_rests_tool, book_reservation_tool
from src.tools.schemas import search_rests_tool_schema, book_reservation_tool_schema, get_conversation_history_tool_schema
from src.agent.restaurant_agent import SelfCorrectingAgent
from src.agent.intent_agent import IntentClassifierAgent
from src.prompts.system_prompts import get_restaurant_system_message, get_intent_system_message

# Setup environment
os.environ["HF_TOKEN"] = "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"

# Initialize LLM client
client = InferenceClient(model="moonshotai/Kimi-K2-Thinking")

def initialize_system():
    """Initialize the database and load restaurant data"""
    print("🚀 Initializing Restaurant Reservation System...")
    
    # Load restaurant data
    db_manager.load_restaurants()
    
    print("✅ System initialized successfully!")

def create_agents():
    """Create and return configured agents"""
    # Create restaurant agent with dynamic system message (includes current date)
    restaurant_agent = SelfCorrectingAgent(
        client=client,
        system=get_restaurant_system_message(),  # Uses current date
        tools=[search_rests_tool_schema, book_reservation_tool_schema, get_conversation_history_tool_schema],
        max_retries=3
    )
    
    # Create intent classification agent
    intent_agent = IntentClassifierAgent(
        client=client,
        system=get_intent_system_message()
    )
    
    return restaurant_agent, intent_agent

def run_interactive_session():
    """Run an interactive session with both agents"""
    restaurant_agent, intent_agent = create_agents()
    
    print("\n🤖 Restaurant Assistant Ready!")
    print("=" * 60)
    print("Features:")
    print("• 🧠 Smart intent classification")
    print("• 🔍 Restaurant search with self-correction")
    print("• 📅 Reservation booking with date context")
    print("• 💬 Conversation memory")
    print("• Type 'quit' to exit")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Thank you for using the Restaurant Assistant!")
                break
            
            if not user_input:
                continue
            
            print("\n🔍 Analyzing intent...")
            
            # Step 1: Classify intent
            intent_result = intent_agent(user_input)
            print(f"intent output --{intent_result}")
            print(f"Intent: {intent_result.description}")
            print(f"Restaurant-related: {intent_result.decision} (confidence: {intent_result.relevance_score:.2f})")
            
            # Save user message to database
            db_manager.save_conversation_message("user", user_input)
            
            # Step 2: Process based on intent
            if intent_result.decision:
                print("\n🤖 Restaurant Assistant:")
                print("-" * 30)
                # Use the intent description for better context
                response = restaurant_agent(intent_result.description)
                print(f"{response}")
                
                # Save assistant response to database
                db_manager.save_conversation_message("assistant", response)
            else:
                print("\n🤖 Assistant:")
                print("-" * 30)
                non_restaurant_response = ("I'm a restaurant assistant and can help you with:\n"
                                         "• Finding restaurants by cuisine, location, or features\n"
                                         "• Making restaurant reservations\n"
                                         "• Restaurant recommendations\n\n"
                                         "Your query doesn't seem to be restaurant-related. Could you ask about restaurants instead?")
                print(non_restaurant_response)
                
                # Save assistant response to database
                db_manager.save_conversation_message("assistant", non_restaurant_response)
            
            print("\n" + "="*60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again.")

def run_test_queries():
    """Run predefined test queries to demonstrate functionality"""
    restaurant_agent, intent_agent = create_agents()
    
    print("\n🧪 Running Test Queries...")
    print("=" * 60)
    
    test_queries = [
        "Find me some good Italian restaurants in Connaught Place",
        "What's the weather like today?",  # Non-restaurant query
        "Show me Chinese restaurants with high ratings",
        "Book Giovanni's for tomorrow 7 PM for 4 people. My name is Rahul Sharma, phone +91-9876543210",
        "I'm hungry, what should I eat?",  # Ambiguous query
        "List some restaurants in CP"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 50)
        
        try:
            # Classify intent
            intent_result = intent_agent(query)
            print(f"Intent Classification:")
            print(f"  Description: {intent_result.description}")
            print(f"  Restaurant-related: {intent_result.decision}")
            print(f"  Confidence: {intent_result.relevance_score:.2f}")
            
            # Process based on intent
            if intent_result.decision:
                print(f"\n🤖 Restaurant Response:")
                response = restaurant_agent(intent_result.description)
                print(f"{response[:200]}..." if len(response) > 200 else response)
            else:
                print(f"\n🤖 Non-restaurant query detected - skipping restaurant processing")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "="*60)

def run_intent_analysis():
    """Run intent analysis on various queries"""
    _, intent_agent = create_agents()
    
    print("\n🧠 Intent Analysis Demo...")
    print("=" * 60)
    
    analysis_queries = [
        "Find Italian restaurants",
        "What's the weather?", 
        "Book a table for 4",
        "I'm hungry",
        "Show me the menu",
        "What time is it?",
        "Best restaurants in Delhi",
        "How to cook pasta?"
    ]
    
    for query in analysis_queries:
        result = intent_agent.get_classification_summary(query)
        print(f"Query: '{result['query']}'")
        print(f"  Classification: {result['classification']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Description: {result['description']}")
        print()

def main():
    """Main function"""
    print("🍽️ Restaurant Reservation System with AI Intent Classification")
    print("=" * 65)
    
    # Initialize system
    initialize_system()
    
    # Choose mode
    print("\nChoose mode:")
    print("1. Interactive session (with intent classification)")
    print("2. Run test queries")
    print("3. Intent analysis demo")
    print("4. All demos")
    
    try:
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            run_interactive_session()
        elif choice == "2":
            run_test_queries()
        elif choice == "3":
            run_intent_analysis()
        elif choice == "4":
            run_test_queries()
            run_intent_analysis()
            run_interactive_session()
        else:
            print("Invalid choice. Running interactive session...")
            run_interactive_session()
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
