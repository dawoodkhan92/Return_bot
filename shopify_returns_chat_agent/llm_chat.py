#!/usr/bin/env python3
"""
Enhanced CLI for LLM-powered Shopify Returns Chat Agent

This enhanced version uses OpenAI function calling for more natural conversations
while maintaining all the specialized tools and functionality.
"""

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the current directory to Python path for imports
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

from llm_returns_chat_agent import LLMReturnsChatAgent


def validate_environment(env_file: str = None) -> dict:
    """Validate that all required environment variables are set."""
    
    # Load environment variables (override system env vars)
    if env_file:
        load_dotenv(env_file, override=True)
    else:
        load_dotenv(override=True)
    
    # Required environment variables
    required_vars = {
        'OPENAI_API_KEY': 'OpenAI API key for LLM functionality',
        'SHOPIFY_ADMIN_TOKEN': 'Shopify Admin API token',
        'SHOPIFY_STORE_DOMAIN': 'Shopify store domain (e.g., store.myshopify.com)'
    }
    
    # Optional environment variables with defaults
    optional_vars = {
        'OPENAI_MODEL': 'gpt-4.1-mini-2025-04-14',
        'OPENAI_MAX_TOKENS': '1000',
        'OPENAI_TEMPERATURE': '0.7',
        'OPENAI_PROJECT_ID': '',
        'OPENAI_ORG_ID': ''
    }
    
    config = {}
    missing_vars = []
    
    # Check required variables
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing_vars.append(f"  {var}: {description}")
        else:
            config[var] = value
    
    # Add optional variables with defaults
    for var, default in optional_vars.items():
        config[var] = os.getenv(var, default)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        print("\n".join(missing_vars))
        print(f"\nPlease set these in your .env file or environment.")
        return None
    
    return config


def print_help():
    """Print available commands."""
    help_text = """
🤖 LLM-Powered Returns Chat Agent - Available Commands:

• help     - Show this help message
• summary  - Get conversation summary  
• history  - Show conversation history
• restart  - Start a new conversation
• exit     - Exit the chat

💡 Tips:
- Speak naturally! The AI will understand and use the right tools
- You can provide order numbers (#1001) or email addresses
- Ask questions like "Can I return my shirt?" or "Process refund for item X"
- The AI will guide you through the return process step by step

Examples:
- "I want to return something from order #1001"
- "Can you look up orders for john@example.com?"
- "I need to return a damaged shirt"
"""
    print(help_text)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="LLM-powered Shopify Returns Chat Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python llm_chat.py
  python llm_chat.py --env-file ../shopify_returns_agency/.env
  python llm_chat.py --debug
        """
    )
    
    parser.add_argument(
        '--env-file', 
        help='Path to .env file (default: .env in current directory)'
    )
    parser.add_argument(
        '--debug', 
        action='store_true', 
        help='Enable debug mode with detailed error messages'
    )
    
    args = parser.parse_args()
    
    # Validate environment
    config = validate_environment(args.env_file)
    if not config:
        return 1
    
    try:
        # Initialize the LLM-powered agent
        print("🤖 Initializing LLM-powered Returns Chat Agent...")
        agent = LLMReturnsChatAgent(config)
        
        print("✅ Agent initialized successfully!")
        print("=" * 60)
        
        # Start conversation
        greeting = agent.start_conversation()
        print(f"Agent: {greeting}")
        print("\n💡 Type 'help' for available commands or just start chatting naturally!")
        print("=" * 60)
        
        # Main conversation loop
        while True:
            try:
                # Get user input
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() == 'exit':
                    print("\n👋 Thank you for using the Returns Chat Agent. Goodbye!")
                    break
                
                elif user_input.lower() == 'help':
                    print_help()
                    continue
                
                elif user_input.lower() == 'summary':
                    summary = agent.get_conversation_summary()
                    print(f"\n📋 Conversation Summary:\n{summary}")
                    continue
                
                elif user_input.lower() == 'history':
                    history = agent.get_conversation_history()
                    print(f"\n📚 Conversation History:")
                    for i, entry in enumerate(history, 1):
                        print(f"{i}. {entry}")
                    continue
                
                elif user_input.lower() == 'restart':
                    print("\n🔄 Starting new conversation...")
                    greeting = agent.start_conversation()
                    print(f"Agent: {greeting}")
                    continue
                
                # Process regular message with LLM
                print("🤔 Thinking...")
                response = agent.process_message(user_input)
                print(f"Agent: {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            
            except Exception as e:
                if args.debug:
                    print(f"\n❌ Error: {str(e)}")
                    import traceback
                    traceback.print_exc()
                else:
                    print(f"\n❌ An error occurred. Use --debug for details.")
                    print("You can continue chatting or type 'exit' to quit.")
    
    except Exception as e:
        if args.debug:
            print(f"\n❌ Failed to initialize agent: {str(e)}")
            import traceback
            traceback.print_exc()
        else:
            print(f"\n❌ Failed to initialize agent. Use --debug for details.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 