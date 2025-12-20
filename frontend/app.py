"""
Minimal Streamlit frontend for Restaurant Reservation System.
Simple red and white design with no emojis.
"""

import streamlit as st
import requests
import json
from datetime import datetime

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="GoodFoods Reservation System",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal CSS - Red and White theme, no emojis
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stApp > header {visibility: hidden;}
    
    /* Main container */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #dc3545;
    }
    
    .css-1d391kg .css-1v0mbdj {
        color: white;
    }
    
    /* Chat container */
    .chat-container {
        height: 500px;
        overflow-y: auto;
        padding: 1rem;
        background-color: white;
        border: 2px solid #dc3545;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    
    /* Message styling */
    .message {
        margin: 0.5rem 0;
        padding: 0.75rem;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
    }
    
    .user-message {
        background-color: #fff5f5;
        margin-left: 2rem;
    }
    
    .assistant-message {
        background-color: #f8f9fa;
        margin-right: 2rem;
    }
    
    /* Input area */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: white;
        padding: 1rem;
        border-top: 2px solid #dc3545;
        z-index: 1000;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #dc3545;
        color: white;
        border: none;
        border-radius: 3px;
        width: 100%;
        margin-bottom: 0.5rem;
    }
    
    .stButton > button:hover {
        background-color: #c82333;
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        border: 2px solid #dc3545;
        border-radius: 3px;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #dc3545;
        margin: 0.5rem 0;
    }
    
    /* Markdown styling within messages */
    .message h1, .message h2, .message h3 {
        color: #dc3545;
        margin: 0.25rem 0;
        font-size: 1.1em;
    }
    
    .message ul {
        margin: 0.5rem 0;
        padding-left: 1.5rem;
    }
    
    .message li {
        margin: 0.25rem 0;
    }
    
    .message strong {
        color: #dc3545;
        font-weight: bold;
    }
    
    .message em {
        font-style: italic;
        color: #666;
    }
    
    /* Numbered list styling */
    .message .numbered-item {
        margin: 0.5rem 0;
        margin-left: 1rem;
    }
    
    /* Restaurant cards */
    .restaurant-card {
        border: 1px solid #dc3545;
        border-radius: 5px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: white;
    }
    
    /* Status indicators */
    .status-connected {
        color: #dc3545;
        font-weight: bold;
    }
    
    .status-disconnected {
        color: #6c757d;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def make_api_request(endpoint, method="GET", data=None):
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, )
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to API. Make sure the API server is running on http://localhost:8000"}
    except requests.exceptions.RequestException as e:
        return {"error": f"API Error: {str(e)}"}

def parse_markdown(text):
    """Parse markdown formatting to HTML"""
    import re
    
    # Convert **bold** to <strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Convert *italic* to <em>
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    
    # Convert ### Headers to <h3>
    text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    
    # Convert ## Headers to <h2>
    text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    
    # Convert # Headers to <h1>
    text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    
    # Convert bullet points (- or •)
    lines = text.split('\n')
    formatted_lines = []
    in_list = False
    
    for line in lines:
        stripped = line.strip()
        
        # Check if line is a bullet point
        if stripped.startswith('- ') or stripped.startswith('• '):
            if not in_list:
                formatted_lines.append('<ul>')
                in_list = True
            bullet_text = stripped[2:].strip()  # Remove bullet marker
            formatted_lines.append(f'<li>{bullet_text}</li>')
        else:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append(line)
    
    # Close list if still open
    if in_list:
        formatted_lines.append('</ul>')
    
    # Join lines back
    text = '\n'.join(formatted_lines)
    
    # Convert line breaks to <br>
    text = text.replace('\n', '<br>')
    
    # Convert numbered lists (1. 2. 3.)
    text = re.sub(r'<br>(\d+)\.\s+(.*?)<br>', r'<br><div style="margin-left: 1rem;"><strong>\1.</strong> \2</div><br>', text)
    
    return text

def display_message(message, is_user=True):
    """Display a message in the chat with markdown parsing"""
    message_class = "user-message" if is_user else "assistant-message"
    role = "You" if is_user else "Assistant"
    
    # Parse markdown content
    formatted_content = parse_markdown(message['content'])
    
    st.markdown(f"""
    <div class="message {message_class}">
        <strong>{role}:</strong><br>
        {formatted_content}
    </div>
    """, unsafe_allow_html=True)

def show_conversation_history():
    """Show conversation history from database"""
    st.header("Conversation History")
    
    response = make_api_request("/conversation-history", "POST", {"limit": 20})
    
    if response and "error" not in response:
        result_text = response["result"]
        if "No previous conversations" in result_text:
            st.info("No conversation history found.")
        else:
            st.text_area("History", value=result_text, height=400)
    else:
        st.error("Failed to load conversation history")

def show_all_restaurants():
    """Show all available restaurants"""
    st.header("All Restaurants")
    
    response = make_api_request("/restaurants")
    
    if response and "restaurants" in response:
        restaurants = response["restaurants"]
        
        st.write(f"Total restaurants: {len(restaurants)}")
        
        for restaurant in restaurants:
            st.markdown(f"""
            <div class="restaurant-card">
                <h4>{restaurant['name']}</h4>
                <p><strong>Cuisine:</strong> {restaurant['cuisine']}</p>
                <p><strong>Location:</strong> {restaurant['location']}</p>
                <p><strong>Rating:</strong> {restaurant['rating']}/5.0</p>
                <p><strong>Price:</strong> {restaurant['price_range']}</p>
                <p><strong>Capacity:</strong> {restaurant['capacity']} people</p>
                <p><strong>Phone:</strong> {restaurant['phone']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("Failed to load restaurants")

def main():
    """Main application"""
    
    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "current_view" not in st.session_state:
        st.session_state.current_view = "chat"
    if "input_key" not in st.session_state:
        st.session_state.input_key = 0
    
    # API Health Check
    health_check = make_api_request("/health")
    api_connected = health_check and "error" not in health_check
    
    # Sidebar
    with st.sidebar:
        st.title("Restaurant System")
        
        # Status
        status_class = "status-connected" if api_connected else "status-disconnected"
        status_text = "Connected" if api_connected else "Disconnected"
        st.markdown(f'<div class="{status_class}">Status: {status_text}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation buttons
        if st.button("Chat"):
            st.session_state.current_view = "chat"
            st.rerun()
        
        if st.button("Conversation History"):
            st.session_state.current_view = "history"
            st.rerun()
        
        if st.button("All Restaurants"):
            st.session_state.current_view = "restaurants"
            st.rerun()
        
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.current_view = "chat"
            st.rerun()
    
    # Main content area
    if not api_connected:
        st.error("API server is not running. Please start it with: python run_api.py")
        return
    
    # Show different views based on selection
    if st.session_state.current_view == "history":
        show_conversation_history()
    elif st.session_state.current_view == "restaurants":
        show_all_restaurants()
    else:
        # Chat view
        st.title("GoodFoods Restaurant Assistant")
        
        # Chat container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Welcome message if no chat history
        if not st.session_state.chat_history:
            st.markdown("""
            <div class="message assistant-message">
                <strong>Assistant:</strong><br>
                Hello! I can help you find restaurants and make reservations. 
                Try asking me to find restaurants by cuisine or location, or ask me to book a table.
            </div>
            """, unsafe_allow_html=True)
        
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                display_message(message, is_user=True)
            else:
                display_message(message, is_user=False)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Input area at bottom
        st.markdown("---")
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "Type your message:",
                placeholder="Ask me about restaurants or make a reservation...",
                key=f"chat_input_{st.session_state.input_key}",
                label_visibility="collapsed"
            )
        
        with col2:
            send_clicked = st.button("Send")
        
        # Handle message sending
        if (send_clicked or user_input) and user_input and user_input.strip():
            # Add user message
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input.strip()
            })
            
            # Make API request
            with st.spinner("Processing..."):
                response = make_api_request("/chat", "POST", {"message": user_input.strip()})
            
            if response and "error" not in response:
                # Add assistant response
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response["response"]
                })
            else:
                # Add error message
                error_msg = response.get("error", "Sorry, I encountered an error.") if response else "Connection error."
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"Error: {error_msg}"
                })
            
            # Clear input and refresh
            st.session_state.input_key += 1
            st.rerun()

if __name__ == "__main__":
    main()
