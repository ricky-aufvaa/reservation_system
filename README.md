



# Restaurant Reservation System - Comprehensive Documentation

## 📋 **Project Overview**

The Restaurant Reservation System is an AI-powered conversational application that enables users to search for restaurants and make reservations through natural language interactions. The system combines modern AI agents, contextual memory, and a clean web interface to provide an intuitive restaurant booking experience.

## 🏗️ **System Architecture**

### **High-Level Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   Database      │
│   (Streamlit)   │◄──►│   Backend       │◄──►│   (SQLite)      │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   AI Agents     │
                    │   (HuggingFace) │
                    └─────────────────┘
```

### **Detailed Backend Architecture**

For a comprehensive visual representation of the backend architecture, including the detailed `/chat` endpoint flow with gate-based decision making and self-correcting agent loops, see:


## 🚀 **Demo Video**

[📹 **Watch Demo Video**](https://youtu.be/xnpNjlhLBQQ) 
[📹 **Watch technical Demo Video**](https://youtu.be/UhjfKGW3KnU) 

## Conversation screenshots: - 

### 1st conversation
[1st](screenshots/1.1.jpg)
[2nd](screenshots/1.2.jpg)

### 2nd conversation
[1st](screenshots/2.1.jpg)
[2nd](screenshots/2.2.jpg)
[3rd](screenshots/2.3.jpg)
[4th](screenshots/2.4.jpg)

### 3rd conversation
[1st](screenshots/3.1.jpg)


** [Backend Architecture Diagram](architecture/architecture.png)**

This diagram illustrates:
- **Gate-Based Flow Control**: Intent Classification Agent as the critical decision gate
- **Self-Correcting Mechanism**: Restaurant(reflection) Agent with reflection logic and refinement guidance
- **Tool Execution Flow**: Search, booking, and memory tools with failure recovery
- **Database Integration**: Conversation persistence and data management
- **Multi-Path Processing**: Different flows for restaurant vs non-restaurant queries

### **Component Architecture**
```
Restaurant Reservation System
├── Frontend Layer (Streamlit)
│   ├── Chat Interface
│   ├── Restaurant Listings
│   └── Conversation History
│
├── API Layer (FastAPI)
│   ├── Chat Endpoints (main)
│   ├── Restaurant Endpoints (for debugging the db)
│   └── Reservation Endpoints (for debugging the db)
│
├── Agent Layer
│   ├── Intent Classification Agent
│   ├── Restaurant Agent (Reflection agent)
│   └── Memory/Context Management
│
├── Tools Layer
│   ├── Restaurant Search Tool (OR Logic)
│   ├── Reservation Booking Tool 
│   └── Conversation History Tool 
│
└── Data Layer
    ├── Restaurant Database
    ├── Reservation Database
    └── Conversation History Database
```

## 🔧 **Core Components**

### **1. Frontend (Streamlit)**
**File**: `frontend/app.py`

**Features**:
- Minimal red and white design 
- Real-time chat interface 
- Sidebar navigation (Chat, History, Restaurants)
- API health monitoring



### **2. API Backend (FastAPI)**
**File**: `src/api/main.py`

**Endpoints**:
- `POST /chat`: Main conversation endpoint 
- `GET /restaurants`: List all restaurants
- `POST /search-restaurants`: Search with criteria
- `POST /book-reservation`: Make reservations
- `POST /conversation-history`: Get chat history
- `DELETE /conversation-history`: Clear history
- `GET /health`: Health check

**Features**:
- Comprehensive error handling 
- CORS middleware for frontend integration
- Step-by-step request logging

### **3. AI Agents**

#### **Intent Classification Agent**
**File**: `src/agent/intent_agent.py`

**Purpose**: Determines if user queries are restaurant-related
**Features**:
- Binary classification (bool)
- Confidence scoring (0.0 - 1.0)
- Structured response format
- Context-aware classification

#### **Restaurant Agent (Self-Correcting)**
**File**: `src/agent/restaurant_agent.py`

**Purpose**: Handles restaurant search and booking operations
**Features**:
- Self-correction with reflection logic (max 3 attempts)
- Multi-tool execution capability
- Conversation state management
- Tool failure detection and refinement 

### **4. Tools System**

#### **Restaurant Search Tool**
**File**: `src/tools/restaurant_tools.py` - `search_rests_tool()`

**Features**:
- **OR Logic Search**: Returns restaurants matching any criteria
- Search by: cuisine, location, capacity, features
- Match indicators showing which criteria matched
- Rating-based sorting (highest first)
- Detailed restaurant information display

#### **Reservation Booking Tool**
**File**: `src/tools/restaurant_tools.py` - `book_reservation_tool()`

**Features**:
- Restaurant validation and capacity checking
- Phone number validation
- Unique reservation ID generation
- Comprehensive confirmation details
- Error handling with helpful messages

#### **Conversation History Tool (Memory)**
**File**: `src/tools/restaurant_tools.py` - `get_conversation_history_tool()`

**Purpose**: Provides contextual memory for follow-up questions
**Features**:
- Defaults to last 5 conversations for context
- Handles queries like "book the 2nd restaurant"
- Formatted conversation display
- Contextual reference resolution

### **5. Database Layer**

#### **Database Models**
**File**: `src/database/models.py`

**Tables**:
1. **Restaurant**: Core restaurant data
2. **Reservation**: Booking information
3. **ConversationHistory**: Chat memory with message indexing

#### **Database Manager**
**File**: `src/database/connection.py`

**Features**:
- SQLAlchemy ORM integration
- Conversation indexing and retrieval
- Restaurant data loading from JSON

### **6. System Prompts**
**File**: `src/prompts/system_prompts.py`

**Components**:
- **Restaurant System Message**: Guides agent behavior
- **Intent System Message**: Classification instructions
- **Memory Tool Integration**: Contextual usage guidelines
- **Refinement Messages**: Self-correction prompts

## 🔄 **User Flows**

### **1. Restaurant Search Flow**
```
User Input: "Find Italian restaurants in CP"
    ↓
Intent Agent: Classifies as restaurant-related (confidence: 0.95)
    ↓
Restaurant Agent: Uses search_rests_tool
    ↓
Search Logic: Finds restaurants matching "Italian" OR "CP"
    ↓
Results: Formatted list with match indicators
    ↓
Database: Saves conversation to memory
    ↓
Frontend: Displays with markdown formatting
```

### **2. Contextual Booking Flow**
```
User Input: "Book the 2nd restaurant for tomorrow 7 PM, 4 people"
    ↓
Intent Agent: Restaurant-related (confidence: 0.92)
    ↓
Restaurant Agent: Detects ambiguous reference "2nd restaurant"
    ↓
Memory Tool: Retrieves last 5 conversations
    ↓
Context Resolution: Identifies specific restaurant from previous search
    ↓
Booking Tool: Creates reservation with resolved restaurant name
    ↓
Confirmation: Detailed booking confirmation with ID
    ↓
Database: Saves booking and conversation
```

### **3. Memory-Enhanced Interaction Flow**
```
Previous: Assistant recommended "Le Jardin in Saket"
User Input: "Book the one you recommend"
    ↓
Intent Agent: Restaurant-related booking query
    ↓
Restaurant Agent: Recognizes contextual reference
    ↓
Memory Tool: Automatically called for "the one you recommend"
    ↓
Context Analysis: Finds "Le Jardin" in recent conversation
    ↓
Booking Process: Proceeds with identified restaurant
```

## 🛠️ **Technical Implementation Details**

### **1. OR Search Logic**
```python
# Build OR conditions for flexible matching
or_conditions = []
if cuisine: or_conditions.append(Restaurant.cuisine.ilike(f"%{cuisine}%"))
if location: or_conditions.append(Restaurant.location.ilike(f"%{location}%"))
if capacity: or_conditions.append(Restaurant.capacity >= capacity)

# Apply OR logic - restaurants matching ANY criteria
restaurants = base_query.filter(or_(*or_conditions))
```

### **2. Memory Tool Integration**
```python
# System prompt guidance for memory usage
CONVERSATION HISTORY USAGE:
- Use get_conversation_history_tool for contextual follow-up questions
- Examples: "book the 2nd restaurant", "what are the features of this place?"
- Defaults to last 5 conversations for context
- Resolves ambiguous references like "this restaurant", "the second one"
```

### **3. Self-Correction Mechanism**
```python
# Retry logic with refinement
while retry_count < max_retries:
    if tool_failed:
        retry_count += 1
        refinement_message = get_refinement_message(retry_count, max_retries)
        self.messages.append(refinement_message)
        continue  # Retry with guidance
```


## 📊 **Data Flow Architecture**

### **Request Processing Pipeline**
```
1. Frontend (Streamlit)
   ├── User input capture
   ├── API request formation
   └── Response rendering

2. API Layer (FastAPI)
   ├── Request validation
   ├── Agent orchestration
   └── Response formatting

3. Agent Processing
   ├── Intent classification
   ├── Tool selection and execution
   └── Response generation

4. Database Operations
   ├── Restaurant queries
   ├── Reservation creation
   └── Conversation storage

5. Response Delivery
   ├── Markdown formatting
   ├── Error handling
   └── Frontend display
```

## 🔧 **Configuration & Setup**

### **Environment Variables**
```bash
HF_TOKEN=hf_.......... # HuggingFace API token
```

### **Database Configuration**
- **Type**: SQLite
- **Location**: `data/simple_restaurants.db`

### **API Configuration**
- **Host**: localhost
- **Port**: 8000
- **CORS**: Enabled for all origins

### **Frontend Configuration**
- **Framework**: Streamlit
- **Port**: 8501
- **Theme**: Red and white, minimal design
- **Features**: Markdown parsing, session management


### __Prerequisites__

```bash
# Required Software
- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)

# Required API Access
- HuggingFace API token (free account available at https://huggingface.co/)
```

### __Step 1: Clone the Repository__

```bash
git clone <repository-url>
cd reservation_system
```

### __Step 2: Create Virtual Environment (Recommended)__

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### __Step 3: Install Dependencies__

```bash
pip install -r requirements.txt
```

### __Step 4: Environment Configuration__

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file and add your HuggingFace token
# .env file should contain:
HF_TOKEN=your_huggingface_token_here
```

__Getting Your HuggingFace Token:__

1. Visit [HuggingFace](https://huggingface.co/) and create a free account
2. Go to Settings → Access Tokens
3. Create a new token with "Read" permissions
4. Copy the token and paste it in your `.env` file

### __Step 5: Initialize Database__

```bash
# The database will be automatically created when you first run the API
# Restaurant data will be loaded from data/restaurants.json
```

### __Step 6: Start the Application__

__Terminal 1 - Start API Backend:__

```bash
python run_api.py
```

You should see:

```javascript
 Initializing Restaurant Reservation System API...
 API initialized successfully!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

__Terminal 2 - Start Frontend (New Terminal):__

```bash
python run_frontend.py
```

You should see:

```javascript
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

### __Step 7: Access the Application__

- __Frontend Interface__: [](http://localhost:8501)<http://localhost:8501>
- __API Documentation__: [](http://localhost:8000/docs)<http://localhost:8000/docs>
- __API Health Check__: [](http://localhost:8000/health)<http://localhost:8000/health>

### __Verification Steps__

1. __Check API Health__: Visit [](http://localhost:8000/health)<http://localhost:8000/health> - should return `{"status": "healthy"}`
2. __Test Frontend__: Visit [](http://localhost:8501)<http://localhost:8501> - should show the chat interface
3. __Test Basic Query__: Try asking "Find Italian restaurants" in the chat



### __Development Setup (Optional)__

For development and testing:

```bash
# Start Jupyter for experimentation
jupyter notebook reference/testing.ipynb
```

### __Project Structure Overview__

```javascript
reservation_system/
├── src/                    # Core application code
│   ├── agent/             # AI agents (intent & restaurant)
│   ├── api/               # FastAPI backend
│   ├── database/          # Database models & connection
│   ├── prompts/           # System prompts for agents
│   └── tools/             # Business logic tools
├── frontend/              # Streamlit web interface
├── data/                  # Restaurant data & databases
├── architecture/          # System architecture diagrams
├── screenshots/           # Application screenshots
├── run_api.py            # API server launcher
├── run_frontend.py       # Frontend launcher
└── requirements.txt      # Python dependencies
```




### **Key Features for Users**
1. **Natural Language Queries**: "Find Italian restaurants in CP"
2. **Contextual Follow-ups**: "Book the 2nd one for tomorrow"
3. **Memory-Aware Conversations**: "What did I search for before?"
4. **Rich Formatting**: Bold text, lists, headers in responses
5. **Multiple Views**: Chat, restaurant listings, conversation history

## 🛡️ **Error Handling & Reliability**

### **Error Handling Layers**
1. **Frontend**: Connection error detection and user feedback
2. **API**: Global exception handler with detailed logging
3. **Database**: Schema validation and auto-repair
4. **Agents**: Retry logic with graceful degradation
5. **Tools**: Input validation and error recovery



## 🎯 **Key Achievements**

### **Technical Achievements**
1. **AI Agent Integration**: Successfully integrated HuggingFace models
2. **Contextual Memory**: Implemented conversation-aware interactions
3. **OR Search Logic**: Flexible restaurant search capabilities
4. **Reflection Agent**: Robust error handling and retry mechanisms

### **User Experience Achievements**
1. **Natural Conversations**: Intuitive restaurant booking through chat
2. **Contextual Understanding**: Handles follow-up questions intelligently
3. **Clean Interface**: Minimal, professional design
5. **Comprehensive Information**: Detailed restaurant and booking data

### **System Architecture Achievements**
1. **Modular Design**: Clean separation of concerns
2. **Scalable Architecture**: Easy to extend and modify
3. **Robust Error Handling**: Multiple layers of error recovery
5. **Documentation**: Extensive documentation for maintenance and development

This Restaurant Reservation System represents a complete, production-ready conversational AI application with advanced features like contextual memory, self-correction, and intelligent search capabilities, all wrapped in a clean, user-friendly interface.
