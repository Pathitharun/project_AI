"""
Ollama AI with OpenAI SDK - Local AI with streaming tool calls
Uses OpenAI SDK to connect to Ollama with automatic tool calling
"""

import os
import json
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from rich.console import Console
from openai import OpenAI

# Import available tools
import tools

load_dotenv()
console = Console()


def load_memory() -> str:
    """
    Load memory from memory.md file
    
    Returns:
        Memory content as string, or empty string if no memory exists
    """
    try:
        if os.path.exists("memory.md"):
            with open("memory.md", "r", encoding="utf-8") as f:
                content = f.read()
                return content if content.strip() else ""
        return ""
    except Exception as e:
        console.print(f"[yellow]⚠️  Could not load memory: {str(e)}[/yellow]")
        return ""


def get_memory_summary() -> str:
    """
    Get a brief summary of what's in memory
    
    Returns:
        Status message about memory
    """
    try:
        if not os.path.exists("memory.md"):
            return "No memory file found"
        
        with open("memory.md", "r", encoding="utf-8") as f:
            content = f.read()
            
        if not content.strip():
            return "Memory file is empty"
        
        # Count lines and get file size
        lines = len(content.strip().split('\n'))
        size = len(content)
        
        # Get last modified time
        import time
        mod_time = os.path.getmtime("memory.md")
        mod_date = time.strftime('%Y-%m-%d', time.localtime(mod_time))
        
        return f"Memory loaded: {lines} lines, {size} bytes (last updated: {mod_date})"
    
    except Exception as e:
        return f"Error reading memory: {str(e)}"


# Tool schemas for OpenAI function calling
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information, facts, or general knowledge. Use this when the user asks about recent events, current information, or needs up-to-date facts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find information about"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of search results to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "news_search",
            "description": "Search for recent news articles on a specific topic. Use this when the user asks about latest news, current events, or recent developments.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The news topic or keyword to search for"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of news articles to return (default: 5)",
                        "default": 5
                    },
                    "days_back": {
                        "type": "integer",
                        "description": "How many days back to search for news (default: 7)",
                        "default": 7
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "manage_memory",
            "description": "Manage persistent memory across conversations. Use this to remember user preferences, personal information, and conversation context. Always read memory when the user introduces themselves or asks 'who am I'. Save important information about the user immediately.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "description": "Operation mode: 'r' to read memory, 'w' to write/overwrite memory, 'a' to append to memory",
                        "enum": ["r", "w", "a"]
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write or append (required for 'w' and 'a' modes). Should be in markdown format."
                    },
                    "filepath": {
                        "type": "string",
                        "description": "Path to memory file (default: 'memory.md')",
                        "default": "memory.md"
                    }
                },
                "required": ["mode"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_category_news",
            "description": "Get top news headlines by category and country. Categories: general, technology, business, entertainment, health, science, sports. Countries: us, in, gb, au, ca, and 50+ others.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "News category: 'general', 'technology', 'business', 'entertainment', 'health', 'science', 'sports'",
                        "enum": ["general", "technology", "business", "entertainment", "health", "science", "sports"]
                    },
                    "country": {
                        "type": "string",
                        "description": "Two-letter country code (default: 'us'). Examples: 'us' (USA), 'in' (India), 'gb' (UK), 'au' (Australia), 'ca' (Canada)",
                        "default": "us"
                    },
                    "save_file": {
                        "type": "boolean",
                        "description": "Save full news data to JSON file (default: false)",
                        "default": False
                    }
                },
                "required": ["category"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_location",
            "description": "Get current GPS location using device location services. Returns coordinates, city, state, country, address, and altitude. Use this when the user asks 'where am I', 'my location', or needs location information.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


def execute_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """
    Execute a tool by name with given arguments
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Arguments to pass to the tool
        
    Returns:
        Tool execution result as string
    """
    try:
        # Map tool names to functions
        tool_map = {
            "web_search": tools.web_search,
            "news_search": tools.news_search,
            "manage_memory": tools.manage_memory,
            "get_category_news": tools.get_news_formatted,
            "get_location": tools.get_location
        }
        
        if tool_name not in tool_map:
            return f"❌ Unknown tool: {tool_name}"
        
        console.print(f"[dim]🔧 Calling {tool_name}...[/dim]")
        
        # Execute the tool
        tool_func = tool_map[tool_name]
        result = tool_func(**arguments)
        
        console.print(f"[dim]✓ {tool_name} completed[/dim]\n")
        
        return str(result)
        
    except Exception as e:
        error_msg = f"❌ Error executing {tool_name}: {str(e)}"
        console.print(f"[red]{error_msg}[/red]\n")
        return error_msg


class OllamaAI:
    """
    Ollama AI with OpenAI SDK and automatic tool calling
    """
    
    def __init__(
        self,
        model: str = "llama3.2",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        system_message: str = None,
        base_url: str = "http://localhost:11434/v1"
    ):
        """
        Initialize Ollama AI with OpenAI SDK
        
        Args:
            model: Ollama model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            system_message: Custom system message (optional)
            base_url: Ollama API endpoint (default: http://localhost:11434/v1)
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = base_url
        
        # Initialize OpenAI client with Ollama endpoint
        self.client = OpenAI(
            base_url=base_url,
            api_key="ollama"  # Ollama doesn't require authentication
        )
        
        # Load existing memory
        memory_content = load_memory()
        
        # Create enhanced system message with memory awareness
        if system_message:
            self.system_message = system_message
        else:
            # Put memory FIRST if it exists
            if memory_content:
                self.system_message = f"""You are ELLI (Everyday Lightweight Learning Intelligence), a confident, knowledgeable AI assistant with access to real-time information through tools.
You provide accurate, clear, and direct answers without unnecessary disclaimers or hedging.

IMPORTANT - YOU HAVE TOOLS:
- You can search the web for current information using web_search
- You can search for latest news using news_search or get_category_news
- You can get GPS location using get_location
- You can manage persistent memory using manage_memory (read, write, append)
- Use tools when needed - you decide when to call them
- Cite sources and provide up-to-date information confidently
- Don't say "I don't know" when you can search for the answer

WHAT YOU KNOW ABOUT THE USER:
{memory_content}

Be direct, confident, and helpful. Use your tools wisely to provide accurate, current information."""
            else:
                self.system_message = """You are ELLI (Everyday Lightweight Learning Intelligence), a confident, knowledgeable AI assistant with access to real-time information through tools.
You provide accurate, clear, and direct answers without unnecessary disclaimers or hedging.

IMPORTANT - YOU HAVE TOOLS:
- You can search the web for current information using web_search
- You can search for latest news using news_search or get_category_news
- You can get GPS location using get_location
- You can manage persistent memory using manage_memory (read, write, append)
- Use tools when needed - you decide when to call them
- Cite sources and provide up-to-date information confidently
- Don't say "I don't know" when you can search for the answer

Be direct, confident, and helpful. Use your tools wisely to provide accurate, current information."""
        
        # Display initialization status
        console.print(f"[green]✓[/green] Ollama AI initialized ({self.model})")
        console.print(f"[dim]  🔌 Connected to: {self.base_url}[/dim]")
        console.print("[dim]  🔧 Tool calling enabled (auto)[/dim]")
        
        # Show memory status
        if memory_content:
            memory_summary = get_memory_summary()
            console.print(f"[dim]  💾 {memory_summary}[/dim]")
    
    def chat(self, message: str, stream: bool = True) -> str:
        """
        Send message and get response with automatic tool calling
        
        Args:
            message: User message
            stream: Whether to stream response
            
        Returns:
            AI response
        """
        # Initialize conversation with system message
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": message}
        ]
        
        console.print("\n[bold magenta]AI (Ollama):[/bold magenta] ", end="")
        
        if stream:
            return self._chat_streaming(messages)
        else:
            return self._chat_non_streaming(messages)
    
    def _chat_streaming(self, messages: List[Dict[str, str]]) -> str:
        """
        Handle streaming chat with tool calls
        
        Args:
            messages: Conversation messages
            
        Returns:
            Complete AI response
        """
        full_response = ""
        tool_calls = []
        current_tool_call = None
        
        try:
            # Create streaming chat completion
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",  # Let AI decide when to use tools
                stream=True,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Process streaming chunks
            for chunk in response:
                if not chunk.choices:
                    continue
                
                delta = chunk.choices[0].delta
                
                # Handle content chunks (text response)
                if delta.content:
                    content = delta.content
                    full_response += content
                    console.print(content, end="")
                
                # Handle tool call chunks
                if delta.tool_calls:
                    for tool_call_chunk in delta.tool_calls:
                        # Start a new tool call
                        if tool_call_chunk.index is not None:
                            # If we have a current tool call, save it
                            if current_tool_call is not None:
                                tool_calls.append(current_tool_call)
                            
                            # Start new tool call
                            current_tool_call = {
                                "id": tool_call_chunk.id or "",
                                "type": "function",
                                "function": {
                                    "name": tool_call_chunk.function.name or "",
                                    "arguments": tool_call_chunk.function.arguments or ""
                                }
                            }
                        # Continue building current tool call
                        elif current_tool_call is not None:
                            if tool_call_chunk.function.name:
                                current_tool_call["function"]["name"] += tool_call_chunk.function.name
                            if tool_call_chunk.function.arguments:
                                current_tool_call["function"]["arguments"] += tool_call_chunk.function.arguments
            
            # Add the last tool call if exists
            if current_tool_call is not None:
                tool_calls.append(current_tool_call)
            
            console.print()  # New line after streaming
            
            # If there are tool calls, execute them
            if tool_calls:
                console.print()  # Extra line before tool execution
                full_response = self._handle_tool_calls(messages, tool_calls)
            else:
                console.print()  # Extra line after response
            
            return full_response
            
        except Exception as e:
            error_msg = f"\n[red]❌ Error during streaming: {str(e)}[/red]\n"
            console.print(error_msg)
            return full_response if full_response else f"Error: {str(e)}"
    
    def _chat_non_streaming(self, messages: List[Dict[str, str]]) -> str:
        """
        Handle non-streaming chat with tool calls
        
        Args:
            messages: Conversation messages
            
        Returns:
            Complete AI response
        """
        try:
            # Create chat completion
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            message = response.choices[0].message
            
            # If there are tool calls, execute them
            if message.tool_calls:
                console.print("[dim]🔧 Tools requested...[/dim]\n")
                return self._handle_tool_calls(messages, message.tool_calls)
            else:
                # Just return the text response
                text = message.content or ""
                console.print(f"{text}\n")
                return text
                
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            console.print(f"[red]{error_msg}[/red]\n")
            return error_msg
    
    def _handle_tool_calls(self, messages: List[Dict[str, str]], tool_calls: List) -> str:
        """
        Execute tool calls and get final response
        
        Args:
            messages: Conversation messages
            tool_calls: List of tool calls to execute
            
        Returns:
            Final AI response after tool execution
        """
        # Add assistant message with tool calls to conversation
        assistant_message = {
            "role": "assistant",
            "content": None,
            "tool_calls": []
        }
        
        # Execute each tool call
        for tool_call in tool_calls:
            # Handle both dict and object formats
            if isinstance(tool_call, dict):
                tool_id = tool_call.get("id", "")
                tool_name = tool_call.get("function", {}).get("name", "")
                tool_args_str = tool_call.get("function", {}).get("arguments", "{}")
            else:
                tool_id = tool_call.id
                tool_name = tool_call.function.name
                tool_args_str = tool_call.function.arguments
            
            # Parse arguments
            try:
                tool_args = json.loads(tool_args_str) if tool_args_str else {}
            except json.JSONDecodeError:
                tool_args = {}
            
            # Add to assistant message
            assistant_message["tool_calls"].append({
                "id": tool_id,
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": tool_args_str
                }
            })
            
            # Execute tool
            tool_result = execute_tool_call(tool_name, tool_args)
            
            # Add tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_id,
                "name": tool_name,
                "content": tool_result
            })
        
        # Add assistant message with tool calls
        if assistant_message["tool_calls"]:
            messages.insert(-len(tool_calls), assistant_message)
        
        # Get final response from AI with tool results
        try:
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            final_text = final_response.choices[0].message.content or ""
            console.print(final_text)
            console.print()
            
            return final_text
            
        except Exception as e:
            error_msg = f"❌ Error getting final response: {str(e)}"
            console.print(f"[red]{error_msg}[/red]\n")
            return error_msg
    
    def get_response(self, message: str) -> str:
        """
        Get AI response without printing (for code generation)
        
        Args:
            message: User message
            
        Returns:
            Clean AI response text only
        """
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": message}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content or ""
            
        except Exception as e:
            return f"Error: {str(e)}"
