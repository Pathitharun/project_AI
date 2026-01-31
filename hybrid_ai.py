"""
Hybrid AI - Automatically switches between Groq (online) and Ollama (offline)
Note: Function calling (auto-search) only works with Groq, not Ollama yet
"""

import os
import json
import socket
from typing import Optional
from groq import Groq
import ollama
import tools
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()


def check_internet_connection(host="8.8.8.8", port=53, timeout=3) -> bool:
    """
    Check if internet connection is available
    
    Args:
        host: Host to check (default: Google DNS)
        port: Port to check
        timeout: Timeout in seconds
        
    Returns:
        True if online, False if offline
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except (socket.error, socket.timeout):
        return False


class HybridAI:
    """
    Hybrid AI that uses Groq when online and Ollama when offline
    """
    
    def __init__(
        self,
        groq_model: str = "llama-3.3-70b-versatile",
        ollama_model: str = "llama3.2",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        system_message: Optional[str] = None,
        enable_tools: bool = True
    ):
        """
        Initialize Hybrid AI
        
        Args:
            groq_model: Groq model to use when online
            ollama_model: Ollama model to use when offline
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            system_message: System message
            enable_tools: Enable automatic search using tools (Groq only)
        """
        self.groq_model = groq_model
        self.ollama_model = ollama_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_message = system_message
        self.enable_tools = enable_tools
        
        # Conversation history for function calling
        self.conversation_history = []
        if system_message:
            self.conversation_history.append({"role": "system", "content": system_message})
        
        # Initialize Groq client
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if self.groq_api_key:
            self.groq_client = Groq(api_key=self.groq_api_key)
        else:
            self.groq_client = None
            console.print("[yellow]⚠️  No GROQ_API_KEY found. Will use Ollama only.[/yellow]")
        
        # Check initial connectivity
        self.is_online = check_internet_connection()
        self.current_provider = "groq" if self.is_online and self.groq_client else "ollama"
        
        # Display status
        if self.current_provider == "groq":
            console.print(f"[green]✓[/green] Online - Using Groq ({self.groq_model})")
            if enable_tools:
                console.print("[dim]  🔍 Auto-search enabled[/dim]")
        else:
            console.print(f"[yellow]🔌[/yellow] Offline - Using Ollama ({self.ollama_model})")
            console.print("[dim]  ⚠️  Auto-search not available offline[/dim]")
    
    def refresh_connection_status(self) -> str:
        """
        Check connection and update provider
        
        Returns:
            Current provider ("groq" or "ollama")
        """
        old_status = self.current_provider
        self.is_online = check_internet_connection()
        
        if self.is_online and self.groq_client:
            self.current_provider = "groq"
        else:
            self.current_provider = "ollama"
        
        # Notify if status changed
        if old_status != self.current_provider:
            if self.current_provider == "groq":
                console.print("[green]🌐 Switched to online mode (Groq)[/green]")
            else:
                console.print("[yellow]🔌 Switched to offline mode (Ollama)[/yellow]")
        
        return self.current_provider
    
    def chat(self, message: str, stream: bool = True) -> str:
        """
        Send message and get response (auto-switches between providers)
        
        Args:
            message: User message
            stream: Whether to stream response
            
        Returns:
            AI response
        """
        # Refresh connection status
        provider = self.refresh_connection_status()
        
        try:
            if provider == "groq":
                return self._chat_groq(message, stream)
            else:
                return self._chat_ollama(message, stream)
        except Exception as e:
            # If Groq fails, try Ollama as fallback
            if provider == "groq":
                console.print(f"[yellow]⚠️  Groq failed, falling back to Ollama[/yellow]")
                return self._chat_ollama(message, stream)
            else:
                error_msg = str(e)
                console.print(f"[bold red]{error_msg}[/bold red]")
                return error_msg
    
    def get_response(self, message: str) -> str:
        """
        Get AI response without printing (for code generation)
        
        Args:
            message: User message
            
        Returns:
            Clean AI response text only
        """
        provider = self.refresh_connection_status()
        
        # Add message to history
        self.conversation_history.append({"role": "user", "content": message})
        
        try:
            if provider == "groq":
                # Call Groq API
                chat_completion = self.groq_client.chat.completions.create(
                    messages=self.conversation_history,
                    model=self.groq_model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    stream=False
                )
                response_text = chat_completion.choices[0].message.content
            else:
                # Call Ollama
                response = ollama.chat(
                    model=self.ollama_model,
                    messages=self.conversation_history
                )
                response_text = response['message']['content']
            
            # Add to history
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            return response_text
            
        except Exception as e:
            if provider == "groq":
                # Fallback to Ollama
                try:
                    response = ollama.chat(
                        model=self.ollama_model,
                        messages=self.conversation_history
                    )
                    response_text = response['message']['content']
                    self.conversation_history.append({"role": "assistant", "content": response_text})
                    return response_text
                except:
                    return f"Error: {str(e)}"
            return f"Error: {str(e)}"
    
    def _chat_groq(self, message: str, stream: bool) -> str:
        """Chat using Groq API with function calling support"""
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Prepare messages (use history for function calling)
        messages = self.conversation_history.copy()
        
        # Prepare tool parameters if enabled
        tool_params = {}
        if self.enable_tools:
            tool_params = {
                "tools": tools.TOOL_SCHEMAS,
                "tool_choice": "auto"
            }
        
        console.print("\n[bold cyan]AI (Groq):[/bold cyan] ", end="")
        
        try:
            # Make initial API call
            chat_completion = self.groq_client.chat.completions.create(
                messages=messages,
                model=self.groq_model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=False,  # Function calling doesn't work with streaming
                **tool_params
            )
            
            response_message = chat_completion.choices[0].message
            
            # Check if there are tool calls
            if hasattr(response_message, 'tool_calls') and response_message.tool_calls:
                # Add assistant message to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in response_message.tool_calls
                    ]
                })
                
                # Execute each tool call
                for tool_call in response_message.tool_calls:
                    tool_name = tool_call.function.name
                    
                    try:
                        tool_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError as e:
                        console.print(f"\n[red]Error parsing tool arguments: {str(e)}[/red]")
                        continue
                    
                    console.print(f"\n[yellow]🔧 Using tool: {tool_name}[/yellow]")
                    
                    # Execute the tool
                    try:
                        result = tools.execute_tool(tool_name, tool_args)
                    except Exception as e:
                        result = f"Error executing tool: {str(e)}"
                        console.print(f"[red]{result}[/red]")
                    
                    # Add tool response to history
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": result
                    })
                    
                    # Show preview of tool result
                    preview = result[:200] + "..." if len(result) > 200 else result
                    console.print(f"[dim]{preview}[/dim]\n")
                
                # Get final response from AI with tool results
                console.print("[bold cyan]AI (Groq):[/bold cyan] ", end="")
                final_completion = self.groq_client.chat.completions.create(
                    messages=self.conversation_history,
                    model=self.groq_model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    stream=stream
                )
                
                if stream:
                    response_text = ""
                    for chunk in final_completion:
                        if chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            response_text += content
                            console.print(content, end="")
                    console.print("\n")
                    
                    # Add final response to history
                    self.conversation_history.append({"role": "assistant", "content": response_text})
                    return response_text
                else:
                    response_text = final_completion.choices[0].message.content
                    console.print(f"{response_text}\n")
                    
                    # Add final response to history
                    self.conversation_history.append({"role": "assistant", "content": response_text})
                    return response_text
            
            else:
                # No tool calls, just return the response
                response_text = response_message.content or ""
                console.print(response_text)
                
            # Add assistant response to history
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            return response_text
        
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's a tool use failure - this is common and we should fallback gracefully
            if "tool_use_failed" in error_msg or "Failed to call a function" in error_msg:
                console.print(f"\n[yellow]⚠️  Auto-search unavailable, using direct response[/yellow]")
                
                # Remove the failed user message and try again without tools
                if self.conversation_history and self.conversation_history[-1]["role"] == "user":
                    self.conversation_history.pop()
                
                # Retry without tools
                self.conversation_history.append({"role": "user", "content": message})
                
                completion = self.groq_client.chat.completions.create(
                    messages=self.conversation_history,
                    model=self.groq_model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    stream=stream
                )
                
                if stream:
                    response_text = ""
                    for chunk in completion:
                        if chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            response_text += content
                            console.print(content, end="")
                    console.print("\n")
                else:
                    response_text = completion.choices[0].message.content
                    console.print(f"{response_text}\n")
                
                self.conversation_history.append({"role": "assistant", "content": response_text})  
                console.print("[dim]💡 Tip: Use /search or /news commands for current information[/dim]\n")
                return response_text
            else:
                console.print(f"\n[red]Error in Groq API: {error_msg}[/red]\n")
                # Remove last user message on error
                if self.conversation_history and self.conversation_history[-1]["role"] == "user":
                    self.conversation_history.pop()
                raise
    
    def _chat_ollama(self, message: str, stream: bool) -> str:
        """Chat using Ollama"""
        messages = []
        if self.system_message:
            messages.append({"role": "system", "content": self.system_message})
        messages.append({"role": "user", "content": message})
        
        console.print("\n[bold magenta]AI (Ollama):[/bold magenta] ", end="")
        
        if stream:
            response_text = ""
            stream_response = ollama.chat(
                model=self.ollama_model,
                messages=messages,
                stream=True,
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            )
            
            for chunk in stream_response:
                if chunk['message']['content']:
                    content = chunk['message']['content']
                    response_text += content
                    console.print(content, end="")
            
            console.print("\n")
            return response_text
        else:
            response = ollama.chat(
                model=self.ollama_model,
                messages=messages,
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            )
            text = response['message']['content']
            console.print(f"{text}\n")
            return text
    
    def get_current_provider(self) -> str:
        """Get current provider name"""
        self.refresh_connection_status()
        return self.current_provider
    
    def get_current_model(self) -> str:
        """Get current model name"""
        if self.current_provider == "groq":
            return self.groq_model
        else:
            return self.ollama_model
