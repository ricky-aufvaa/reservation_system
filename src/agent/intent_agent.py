"""
Intent classification agent for restaurant-related queries.
"""

import json
import sys
import os
from huggingface_hub import InferenceClient

# Add project root to path for absolute imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.tools.schemas import IntentResponse, ValidationError
from src.prompts.system_prompts import get_intent_system_message

class IntentClassifierAgent:
    """
    Agent that classifies user queries to determine if they are restaurant-related.
    
    This agent uses structured output to return a classification decision with
    confidence score for restaurant relevance.
    """
    
    def __init__(self, client: InferenceClient, system: str = ""):
        """
        Initialize the intent classification agent.
        
        Args:
            client (InferenceClient): The LLM client for making API calls
            system (str): Custom system message (optional, uses default if empty)
        """
        self.client = client
        self.system = system or get_intent_system_message()
        self.messages: list = []
        
    def __call__(self, message: str = "") -> IntentResponse:
        """
        Classify user intent and return structured response.
        
        Args:
            message (str): User query to classify
            
        Returns:
            IntentResponse: Structured classification result with description,
                          decision, and relevance score
        """
        if message:
            # Reset messages for each query to ensure clean classification
            self.messages = [{"role": "system", "content": self.system}]
            self.messages.append({"role": "user", "content": message})
        
        response_content = self.execute()
        # print(f"response content is {response_content}")
        # print(f"{type(response_content)}")
        
        try:
            # Parse and validate the response
            response_data = json.loads(response_content)
            return IntentResponse(**response_data)
        except (json.JSONDecodeError, ValidationError) as e:
            # Fallback response for parsing errors
            print(f"Intent classification error: {e}")
            return IntentResponse(
                description=f"Error parsing response: {str(e)}",
                decision=False,
                relevance_score=0.0
            )
    
    def execute(self) -> str:
        """
        Execute the intent classification request.
        
        Returns:
            str: Raw JSON response from the LLM
        """
        try:
            completion = self.client.chat.completions.create(
                messages=self.messages,
                max_tokens=800,  # Reduced for more focused responses
                temperature=0.1,  # Lower temperature for more consistent classification
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "IntentResponse",
                        "schema": IntentResponse.model_json_schema(),
                        "strict": True,
                    },
                }
            )
            response = completion.choices[0].message.content
            # print(f"response from intent agent is {response}")
            return response
        except Exception as e:
            print(f"LLM API error: {e}")
            # Return a fallback JSON response
            return json.dumps({
                "description": f"API error occurred: {str(e)}",
                "decision": False,
                "relevance_score": 0.0
            })
