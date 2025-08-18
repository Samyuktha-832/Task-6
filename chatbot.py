#!/usr/bin/env python3
"""
Terminal Chatbot Application
A simple chatbot that runs in your VS Code terminal using OpenAI API
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from typing import List, Dict, Optional

class TerminalChatbot:
    def __init__(self, api_key: str = None):
        # Use the provided API key or default
        self.api_key = api_key or "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"
        self.conversation_history: List[Dict[str, str]] = []
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "deepseek/deepseek-r1-0528:free"
        self.max_tokens = 1000
        
    def make_api_request(self, message: str) -> Optional[str]:
        """Make a request to the OpenAI API"""
        try:
            # Add user message to conversation history
            self.conversation_history.append({"role": "user", "content": message})
            
            # Prepare the request data
            data = {
                "model": self.model,
                "messages": self.conversation_history,
                "max_tokens": self.max_tokens,
                "temperature": 0.7
            }
            
            # Convert to JSON
            json_data = json.dumps(data).encode('utf-8')
            
            # Create the request
            request = urllib.request.Request(
                self.api_url,
                data=json_data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                }
            )
            
            # Make the request
            with urllib.request.urlopen(request) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            # Extract the assistant's response
            if 'choices' in result and len(result['choices']) > 0:
                assistant_response = result['choices'][0]['message']['content']
                # Add assistant response to conversation history
                self.conversation_history.append({"role": "assistant", "content": assistant_response})
                return assistant_response
            else:
                return "I'm sorry, I couldn't generate a response."
                
        except urllib.error.HTTPError as e:
            error_msg = e.read().decode('utf-8')
            if e.code == 401:
                return "❌ Authentication failed. Please check your API key."
            elif e.code == 429:
                return "❌ Rate limit exceeded. Please wait a moment and try again."
            elif e.code == 400:
                return "❌ Bad request. Please check your message format."
            else:
                try:
                    error_data = json.loads(error_msg)
                    if 'error' in error_data and 'message' in error_data['error']:
                        return f"❌ API Error: {error_data['error']['message']}"
                except:
                    pass
                return f"❌ API Error ({e.code}): {error_msg}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print the chatbot header"""
        print("=" * 60)
        print("🤖 OPENAI TERMINAL CHATBOT")
        print("=" * 60)
        print("Type 'quit', 'exit', or 'bye' to end the conversation")
        print("Type 'clear' to clear the screen")
        print("Type 'history' to see conversation history")
        print("Type 'help' for more commands")
        print("-" * 60)
    
    def print_help(self):
        """Print help information"""
        print("\n📚 Available Commands:")
        print("  help     - Show this help message")
        print("  quit     - Exit the chatbot")
        print("  exit     - Exit the chatbot") 
        print("  bye      - Exit the chatbot")
        print("  clear    - Clear the screen")
        print("  history  - Show conversation history")
        print("  reset    - Reset conversation history")
        print("  model    - Show current model information")
        print("  models   - Switch between available models")
        print()
    
    def show_history(self):
        """Show conversation history"""
        if not self.conversation_history:
            print("\n📝 No conversation history yet.")
            return
        
        print(f"\n📝 Conversation History ({len(self.conversation_history)} messages):")
        print("-" * 50)
        
        for i, msg in enumerate(self.conversation_history, 1):
            role = "You" if msg["role"] == "user" else "AI"
            timestamp = datetime.now().strftime("%H:%M")
            content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            print(f"{i:2d}. [{timestamp}] {role}: {content}")
        print()
    
    def reset_history(self):
        """Reset conversation history"""
        self.conversation_history.clear()
        print("🔄 Conversation history has been reset.")
    
    def show_model_info(self):
        """Show current model information"""
        print(f"\n🔧 Current Configuration:")
        print(f"  Model: {self.model}")
        print(f"  Max Tokens: {self.max_tokens}")
        print(f"  Messages in History: {len(self.conversation_history)}")
        print(f"  API Key: {self.api_key[:20]}...{self.api_key[-10:]}")
        print()
    
    def switch_models(self):
        """Allow user to switch between available models"""
        models = [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo-preview"
        ]
        
        print(f"\n🤖 Available Models:")
        for i, model in enumerate(models, 1):
            current = " (current)" if model == self.model else ""
            print(f"  {i}. {model}{current}")
        
        try:
            choice = input("\nSelect model number (or press Enter to cancel): ").strip()
            if choice and choice.isdigit():
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(models):
                    self.model = models[choice_idx]
                    print(f"✅ Switched to model: {self.model}")
                else:
                    print("❌ Invalid selection.")
            else:
                print("Cancelled.")
        except Exception as e:
            print(f"❌ Error switching models: {e}")
        print()
    
    def run(self):
        """Main chatbot loop"""
        self.clear_screen()
        self.print_header()
        
        print("Hello! I'm your AI assistant. How can I help you today?")
        
        while True:
            try:
                # Get user input
                user_input = input("\n💬 You: ").strip()
                
                # Handle empty input
                if not user_input:
                    continue
                
                # Handle commands
                command = user_input.lower()
                
                if command in ['quit', 'exit', 'bye']:
                    print("\n👋 Goodbye! Thanks for chatting with me!")
                    break
                
                elif command == 'clear':
                    self.clear_screen()
                    self.print_header()
                    continue
                
                elif command == 'help':
                    self.print_help()
                    continue
                
                elif command == 'history':
                    self.show_history()
                    continue
                
                elif command == 'reset':
                    self.reset_history()
                    continue
                
                elif command == 'model':
                    self.show_model_info()
                    continue
                
                elif command == 'models':
                    self.switch_models()
                    continue
                
                # Make API request
                print("\n🤔 AI is thinking...")
                response = self.make_api_request(user_input)
                
                # Display response
                print(f"\n🤖 AI: {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! (Interrupted by user)")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {str(e)}")
                print("Please try again or type 'quit' to exit.")

def main():
    """Main function"""
    try:
        print("🚀 Starting OpenAI Terminal Chatbot...")
        print()
        
        # Create and run chatbot with embedded API key
        chatbot = TerminalChatbot()
        chatbot.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Failed to start chatbot: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()