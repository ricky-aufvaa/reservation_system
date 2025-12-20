"""
Self-correcting agent for restaurant search and booking operations.
"""

import json
import sys
import os
from huggingface_hub import InferenceClient

# Add project root to path for absolute imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.tools.restaurant_tools import search_rests_tool, book_reservation_tool, get_conversation_history_tool
from src.prompts.system_prompts import get_restaurant_system_message, get_refinement_message

class SelfCorrectingAgent:
    def __init__(self, client: InferenceClient, system: str = "", tools: list = None, max_retries: int = 3):
        self.client = client
        self.system = system or get_restaurant_system_message()
        self.messages: list = []
        self.tools = tools if tools is not None else []
        self.max_retries = max_retries
        if self.system:
            self.messages.append({"role": "system", "content": self.system})

    def __call__(self, message=""):
        if message:
            self.messages.append({"role": "user", "content": message})

        final_assistant_content = self.execute()

        if final_assistant_content:
            self.messages.append({"role": "assistant", "content": final_assistant_content})

        return final_assistant_content

    def execute(self):
        retry_count = 0
        
        while True:
            completion = self.client.chat.completions.create(
                messages=self.messages,
                tools=self.tools,
                tool_choice="auto"
            )

            response_message = completion.choices[0].message
            print("\n" + "="*60)
            print("AGENT RESPONSE DEBUG")
            print("="*60)
            print(f"Response Type: {type(response_message).__name__}")
            print(f"Has Tool Calls: {bool(response_message.tool_calls)}")
            if response_message.content:
                print(f"Content Length: {len(response_message.content)} characters")
                print(f"Content Preview: {response_message}...")
            if response_message.tool_calls:
                print(f"Number of Tool Calls: {len(response_message.tool_calls)}")
                for i, tool_call in enumerate(response_message.tool_calls):
                    print(f"  Tool {i+1}: {tool_call.function.name}")
            print("="*60 + "\n")

            if response_message.tool_calls:
                self.messages.append(response_message)

                tool_outputs = []
                tool_failed = False
                
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    print(f"\nExecuting tool: {function_name}")
                    print(f"Arguments: {function_args}")

                    # Execute the tool - Fixed multi-tool execution bug
                    current_tool_failed = False
                    
                    try:
                        if function_name == "search_rests_tool":
                            executed_output = search_rests_tool(**function_args)
                        elif function_name == "book_reservation_tool":
                            executed_output = book_reservation_tool(**function_args)
                        elif function_name == "get_conversation_history_tool":
                            executed_output = get_conversation_history_tool(**function_args)
                        else:
                            executed_output = f"Error: Unknown function '{function_name}'"
                            current_tool_failed = True
                        
                        current_tool_output = str(executed_output)
                        
                        print(f"Tool Output Preview: {current_tool_output[:200]}...")
                        
                        # Check if THIS specific tool failed
                        if self.is_tool_failure(current_tool_output):
                            current_tool_failed = True
                            print(f"Tool failed (attempt {retry_count + 1}): {function_name}")
                        else:
                            print(f"Tool succeeded: {function_name}")
                            
                    except Exception as e:
                        current_tool_output = f"Error executing {function_name}: {str(e)}"
                        current_tool_failed = True
                        print(f"Exception in {function_name}: {e}")

                    # Store result for THIS tool
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": current_tool_output,
                    })
                    
                    # Update overall failure status
                    if current_tool_failed:
                        tool_failed = True

                self.messages.extend(tool_outputs)
                
                # If tool failed and we haven't exceeded retry limit, add refinement instruction
                if tool_failed and retry_count < self.max_retries:
                    retry_count += 1
                    refinement_message = {
                        "role": "user", 
                        "content": get_refinement_message(retry_count, self.max_retries)
                    }
                    self.messages.append(refinement_message)
                    continue  # Go back to LLM for refinement
                
                # If tool succeeded or max retries reached, continue normally
                
            else:
                return response_message.content

    def is_tool_failure(self, tool_output: str) -> bool:
        """
        Determine if the tool execution failed based on output content
        Customize this based on your specific failure patterns
        """
        failure_indicators = [
            "No restaurants found matching your criteria",
            "No restaurants found",
            "Error searching restaurants",
            "Error:",
            "not found"
        ]
        
        return any(indicator.lower() in tool_output.lower() for indicator in failure_indicators)

    def get_conversation_info(self):
        """Get information about the current conversation"""
        return {
            "total_messages": len(self.messages),
            "user_messages": len([m for m in self.messages if m["role"] == "user"]),
            "assistant_messages": len([m for m in self.messages if m["role"] == "assistant"]),
            "tool_calls": len([m for m in self.messages if m["role"] == "tool"])
        }

    def reset_conversation(self):
        """Reset the conversation history"""
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": self.system})
