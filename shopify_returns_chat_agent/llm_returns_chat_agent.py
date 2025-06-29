"""
LLM-powered Returns Chat Agent with OpenAI Function Calling

This enhanced version uses OpenAI's function calling capabilities to provide
more natural conversations while still leveraging our specialized tools.
"""

import json
import uuid
import os
from typing import Dict, Any, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

from tools.order_lookup import OrderLookup
from tools.policy_checker import PolicyChecker
from tools.refund_processor import RefundProcessor
from tools.conversation_logger import ConversationLogger

# Load environment variables (override system env vars)
load_dotenv(override=True)


class LLMReturnsChatAgent:
    """Enhanced returns chat agent powered by OpenAI with function calling."""

    def __init__(self, config: Dict[str, str]):
        """Initialize the LLM-powered returns chat agent.
        
        Args:
            config: Configuration dictionary with API keys and settings
        """
        # Initialize OpenAI client
        project_id = config.get('OPENAI_PROJECT_ID')
        org_id = config.get('OPENAI_ORG_ID')
        
        client_kwargs = {'api_key': config.get('OPENAI_API_KEY')}
        
        if project_id:
            client_kwargs['project'] = project_id
        if org_id:
            client_kwargs['organization'] = org_id
            
        self.client = OpenAI(**client_kwargs)
        self.model = config.get('OPENAI_MODEL', 'gpt-4o')
        
        # Initialize tools
        self.order_lookup = OrderLookup(
            admin_token=config['SHOPIFY_ADMIN_TOKEN'],
            store_domain=config['SHOPIFY_STORE_DOMAIN']
        )
        self.policy_checker = PolicyChecker()
        self.refund_processor = RefundProcessor(
            admin_token=config['SHOPIFY_ADMIN_TOKEN'],
            store_domain=config['SHOPIFY_STORE_DOMAIN']
        )
        self.logger = ConversationLogger()
        
        # Conversation state
        self.conversation_id = None
        self.messages = []
        self.context = {}
        
        # Define function schemas for OpenAI
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "lookup_order_by_id",
                    "description": "Look up a Shopify order by its order number or ID",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {
                                "type": "string",
                                "description": "The Shopify order ID or order number (e.g., #1001)"
                            }
                        },
                        "required": ["order_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "lookup_order_by_email",
                    "description": "Look up Shopify orders by customer email address",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "email": {
                                "type": "string",
                                "description": "The customer's email address"
                            }
                        },
                        "required": ["email"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_return_eligibility",
                    "description": "Check if an item is eligible for return based on store policy",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_date": {
                                "type": "string",
                                "description": "The date the order was placed (ISO format)"
                            },
                            "item_id": {
                                "type": "string",
                                "description": "The ID of the item to be returned"
                            },
                            "return_reason": {
                                "type": "string",
                                "description": "The reason for the return",
                                "enum": ["wrong_size", "defective", "not_as_described", "changed_mind", "damaged", "other"]
                            }
                        },
                        "required": ["order_date", "item_id", "return_reason"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "process_refund",
                    "description": "Process a refund for an order item",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {
                                "type": "string",
                                "description": "The Shopify order ID"
                            },
                            "line_item_id": {
                                "type": "string",
                                "description": "The ID of the line item to refund"
                            },
                            "quantity": {
                                "type": "integer",
                                "description": "The quantity to refund (optional, defaults to full quantity)"
                            },
                            "reason": {
                                "type": "string",
                                "description": "The reason for the refund",
                                "default": "customer_request"
                            }
                        },
                        "required": ["order_id", "line_item_id"]
                    }
                }
            }
        ]

    def start_conversation(self) -> str:
        """Start a new conversation with an AI-generated greeting."""
        # Generate new conversation ID
        self.conversation_id = str(uuid.uuid4())
        
        # Initialize conversation with system prompt
        self.messages = [
            {
                "role": "system", 
                "content": """You are a helpful and friendly returns assistant for an apparel e-commerce store. 

Your role is to:
1. Help customers process returns and exchanges for their orders
2. Look up order information when needed
3. Check return eligibility based on store policies
4. Process approved refunds
5. Provide clear, helpful guidance throughout the process

Store policies:
- 30-day return window from order date
- Items must be in original condition
- Some items may be excluded from returns
- Valid return reasons include: wrong size, defective, not as described, changed mind, damaged

Be friendly, professional, and concise. Always ask for order information first (order number or email address) if the customer hasn't provided it. Guide them step by step through the return process."""
            }
        ]
        
        # Get initial greeting from LLM
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages + [{"role": "user", "content": "Hi, I'd like to start a return."}],
                max_tokens=150,
                temperature=0.7
            )
            
            greeting = response.choices[0].message.content
            
            # Add greeting to message history
            self.messages.append({"role": "user", "content": "Hi, I'd like to start a return."})
            self.messages.append({"role": "assistant", "content": greeting})
            
            # Log the interaction
            self.logger.log_interaction(
                conversation_id=self.conversation_id,
                user_msg="Hi, I'd like to start a return.",
                agent_msg=greeting
            )
            
            return greeting
            
        except Exception as e:
            # Fallback greeting if OpenAI fails
            fallback_greeting = (
                "Hello! I'm here to help you with your return. "
                "To get started, I'll need either your order number or the email address "
                "you used when placing the order. How can I assist you today?"
            )
            
            self.messages.append({"role": "user", "content": "Hi, I'd like to start a return."})
            self.messages.append({"role": "assistant", "content": fallback_greeting})
            
            self.logger.log_interaction(
                conversation_id=self.conversation_id,
                user_msg="Hi, I'd like to start a return.",
                agent_msg=fallback_greeting,
                metadata={"error": f"OpenAI API error: {str(e)}"}
            )
            
            return fallback_greeting

    def process_message(self, user_message: str) -> str:
        """Process user message using LLM with function calling."""
        try:
            # Log user message
            self.logger.log_interaction(
                conversation_id=self.conversation_id,
                user_msg=user_message
            )
            
            # Add user message to history
            self.messages.append({"role": "user", "content": user_message})
            
            # Get response from LLM with function calling
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools,
                tool_choice="auto",
                max_tokens=500,
                temperature=0.7
            )
            
            response_message = response.choices[0].message
            
            # Check if LLM wants to call functions
            if response_message.tool_calls:
                # Add assistant message with tool calls to history
                self.messages.append({
                    "role": "assistant",
                    "content": response_message.content,
                    "tool_calls": response_message.tool_calls
                })
                
                # Execute each tool call
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Execute the function
                    function_response = self._execute_function(function_name, function_args)
                    
                    # Add function result to message history
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(function_response)
                    })
                
                # Get final response from LLM after function calls
                second_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    max_tokens=500,
                    temperature=0.7
                )
                
                final_response = second_response.choices[0].message.content
                
                # Add final response to message history
                self.messages.append({"role": "assistant", "content": final_response})
                
                # Log interaction with tool calls
                tool_calls_info = []
                for tool_call in response_message.tool_calls:
                    tool_calls_info.append({
                        "tool": tool_call.function.name,
                        "args": json.loads(tool_call.function.arguments),
                        "result": self._execute_function(
                            tool_call.function.name, 
                            json.loads(tool_call.function.arguments)
                        )
                    })
                
                self.logger.log_interaction(
                    conversation_id=self.conversation_id,
                    agent_msg=final_response,
                    tool_calls=tool_calls_info
                )
                
                return final_response
                
            else:
                # No function calls, just return the response
                response_content = response_message.content
                
                # Add to message history
                self.messages.append({"role": "assistant", "content": response_content})
                
                # Log interaction
                self.logger.log_interaction(
                    conversation_id=self.conversation_id,
                    agent_msg=response_content
                )
                
                return response_content
                
        except Exception as e:
            error_msg = (
                "I apologize, but I'm experiencing some technical difficulties. "
                "Please try again in a moment, or contact our customer service team directly."
            )
            
            # Print the actual error for debugging
            print(f"DEBUG - LLM processing error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            self.logger.log_interaction(
                conversation_id=self.conversation_id,
                agent_msg=error_msg,
                metadata={"error": f"LLM processing error: {str(e)}"}
            )
            
            return error_msg

    def _execute_function(self, function_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the specified function with the given arguments."""
        try:
            if function_name == "lookup_order_by_id":
                result = self.order_lookup.lookup_by_id(args["order_id"])
                # Store order in context for future reference
                if not result.get("error"):
                    self.context['current_order'] = result
                return result
                
            elif function_name == "lookup_order_by_email":
                result = self.order_lookup.lookup_by_email(args["email"])
                # Store orders in context for future reference
                if isinstance(result, list) and result:
                    self.context['available_orders'] = result
                return result
                
            elif function_name == "check_return_eligibility":
                result = self.policy_checker.check_eligibility(
                    args["order_date"],
                    args["item_id"],
                    args["return_reason"]
                )
                # Store eligibility result in context
                self.context['last_eligibility_check'] = result
                return result
                
            elif function_name == "process_refund":
                result = self.refund_processor.process_refund(
                    order_id=args["order_id"],
                    line_item_id=args["line_item_id"],
                    quantity=args.get("quantity"),
                    reason=args.get("reason", "customer_request")
                )
                # Store refund result in context
                self.context['last_refund'] = result
                return result
                
            else:
                return {"error": f"Unknown function: {function_name}"}
                
        except Exception as e:
            return {"error": f"Function execution failed: {str(e)}"}

    def get_conversation_summary(self) -> str:
        """Get a summary of the current conversation."""
        if not self.conversation_id:
            return "No active conversation."
            
        summary_dict = self.logger.summarize_conversation(self.conversation_id)
        if "error" in summary_dict:
            return summary_dict["error"]
        
        # Format the summary nicely
        messages = summary_dict.get("messages", {})
        duration = summary_dict.get("duration", {})
        
        summary_text = f"""Conversation Summary:
- User messages: {messages.get('user', 0)}
- Agent messages: {messages.get('agent', 0)}
- Total interactions: {messages.get('total_interactions', 0)}
- Tool calls: {summary_dict.get('tool_calls', 0)}
- Duration: {duration.get('seconds', 'Unknown')} seconds"""
        
        return summary_text

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the full conversation history."""
        if not self.conversation_id:
            return []
            
        return self.logger.get_conversation_history(self.conversation_id)


if __name__ == "__main__":
    # Test the LLM agent
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    config = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'OPENAI_MODEL': os.getenv('OPENAI_MODEL', 'gpt-4o'),
        'SHOPIFY_ADMIN_TOKEN': os.getenv('SHOPIFY_ADMIN_TOKEN'),
        'SHOPIFY_STORE_DOMAIN': os.getenv('SHOPIFY_STORE_DOMAIN')
    }
    
    if not all([config['OPENAI_API_KEY'], config['SHOPIFY_ADMIN_TOKEN'], config['SHOPIFY_STORE_DOMAIN']]):
        print("Error: Missing required environment variables")
        print("Please set OPENAI_API_KEY, SHOPIFY_ADMIN_TOKEN, and SHOPIFY_STORE_DOMAIN")
        exit(1)
    
    # Test the agent
    agent = LLMReturnsChatAgent(config)
    
    print("Testing LLM Returns Chat Agent...")
    print("=" * 50)
    
    # Start conversation
    greeting = agent.start_conversation()
    print(f"Agent: {greeting}")
    
    # Test with a sample message
    test_message = "I want to return an item from order #1001"
    print(f"\nUser: {test_message}")
    response = agent.process_message(test_message)
    print(f"Agent: {response}")
    
    print("\n" + "=" * 50)
    print("LLM agent test completed successfully!") 