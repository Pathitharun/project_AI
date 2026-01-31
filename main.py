"""
Hybrid Groq/Ollama AI Chat - Auto-switches between online and offline
"""

import os
import tools
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from hybrid_ai import HybridAI

console = Console()


def main():
    """Main function for hybrid chat"""
    console.print(Panel.fit(
        "[bold cyan]Hybrid AI Chat[/bold cyan]\n"
        "Groq (online) + Ollama (offline)",
        border_style="cyan"
    ))
    
    # Initialize Hybrid AI
    ai = HybridAI(
        groq_model="llama-3.3-70b-versatile",
        ollama_model="llama3.2",
        system_message="You are a helpful, friendly, and knowledgeable AI assistant. "
                      "When users ask about recent events, current news, latest information, "
                      "or anything that happened after 2023, use the available search tools to "
                      "find up-to-date information. Today's date is January 31, 2026."
    )
    
    # Show current status
    provider = ai.get_current_provider()
    model = ai.get_current_model()
    console.print(f"[dim]Current: {provider.upper()} - {model}[/dim]\n")
    """Main chat loop"""
    console.print("[bold cyan]💬 Hybrid AI Chat (with Auto-Search)[/bold cyan]")
    console.print("[dim]Automatically switches between Groq (online) and Ollama (offline)[/dim]")
    console.print("[dim]Type /help for commands, /quit to exit[/dim]\n")
    
    # Initialize AI
    ai = HybridAI(enable_tools=True)
    
    # Voice states
    voice_output_enabled = False
    voice_input_enabled = False  # Persistent STT mode
    
    while True:
        try:
            # Get user input (voice if enabled, otherwise typed)
            if voice_input_enabled:
                user_input = tools.listen_voice()
                # If voice failed, ask for typed input as fallback
                if user_input.startswith("❌"):
                    console.print("[dim]Falling back to text input...[/dim]")
                    user_input = Prompt.ask("\n[bold green]You[/bold green]").strip()
            else:
                user_input = Prompt.ask("\n[bold green]You[/bold green]").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith("/"):
                command = user_input.split()[0].lower()
                
                if command == "/quit" or command == "/exit":
                    console.print("\n[yellow]👋 Goodbye![/yellow]\n")
                    break
                
                elif command == "/help":
                    console.print("\n[bold cyan]Available Commands:[/bold cyan]")
                    console.print("  [cyan]/help[/cyan]          - Show this help")
                    console.print("  [cyan]/quit[/cyan]          - Exit chat")
                    console.print("  [cyan]/file[/cyan]          - File operations (create, read, edit, delete, list)")
                    console.print("  [cyan]/app[/cyan]           - App control (open, close, list)")
                    console.print("  [cyan]/listen[/cyan]        - Voice input (speak your message)")
                    console.print("  [cyan]/speak[/cyan]         - Toggle voice output (TTS)")
                    console.print("  [cyan]/voicemode[/cyan]     - Hands-free voice conversation")
                    console.print("\n[dim]Auto-features:[/dim]")
                    console.print("  [dim]• Just ask naturally - search happens automatically![/dim]")
                    console.print("  [dim]• Say 'open Safari' - apps open automatically![/dim]")
                    console.print("  [dim]• Say 'edit demo.py' - file ops work directly![/dim]")
                    console.print("  [dim]• Ask 'what time is it' - get current time![/dim]")
                    console.print("  [dim]• Ask 'what's the date' - get current date![/dim]")
                    console.print("  [dim]• Ask 'weather in Mumbai' - get weather info![/dim]\n")
                    continue
                
                elif command == "/search":
                    if len(user_input.split()) < 2:
                        console.print("[red]Usage: /search <query>[/red]")
                    else:
                        query = " ".join(user_input.split()[1:])
                        console.print(f"\n[yellow]🔍 Searching for: {query}[/yellow]")
                        result = tools.web_search(query)
                        # Don't show the raw results, just summarize
                        
                        # Ask AI to summarize the search results
                        console.print("[dim]📝 Getting answer...[/dim]")
                        summary_prompt = f"Based on these search results, provide a clear and concise answer about when and what happened:\n\n{result}"
                        ai.chat(summary_prompt, stream=True)
                    continue
                
                elif command == "/news":
                    if len(user_input.split()) < 2:
                        console.print("[red]Usage: /news <topic>[/red]")
                    else:
                        topic = " ".join(user_input.split()[1:])
                        console.print(f"\n[yellow]📰 Fetching news on: {topic}[/yellow]")
                        result = tools.news_search(topic)
                        # Don't show the raw results, just summarize
                        
                        # Ask AI to summarize the news results
                        console.print("[dim]📝 Getting answer...[/dim]")
                        summary_prompt = f"Based on these news articles, provide a clear summary with the key facts and dates:\n\n{result}"
                        ai.chat(summary_prompt, stream=True)
                    continue
                
                elif command == "/speed":
                    console.print(f"\n[yellow]🚀 Running speed test...[/yellow]")
                    result = tools.internet_speed_test()
                    console.print(f"\n{result}\n")
                    continue
                
                elif command == "/file":
                    # File operations command
                    parts = user_input.split(maxsplit=2)
                    if len(parts) < 2:
                        console.print("[red]Usage: /file <create|read|edit|delete|list> <path> [content][/red]")
                        continue
                    
                    subcommand = parts[1].lower()
                    
                    if subcommand == "create":
                        if len(parts) < 3:
                            console.print("[red]Usage: /file create <path>[/red]")
                        else:
                            path = parts[2]
                            content = Prompt.ask("📝 Enter file content (or press Enter for empty file)", default="")
                            result = tools.create_file(path, content)
                            console.print(f"\n{result}\n")
                    
                    elif subcommand == "read":
                        if len(parts) < 3:
                            console.print("[red]Usage: /file read <path>[/red]")
                        else:
                            path = parts[2]
                            result = tools.read_file(path)
                            console.print(f"\n{result}\n")
                    
                    elif subcommand == "edit":
                        if len(parts) < 3:
                            console.print("[red]Usage: /file edit <path>[/red]")
                        else:
                            path = parts[2]
                            content = Prompt.ask("📝 Enter new content")
                            result = tools.edit_file(path, content)
                            console.print(f"\n{result}\n")
                    
                    elif subcommand == "delete":
                        if len(parts) < 3:
                            console.print("[red]Usage: /file delete <path>[/red]")
                        else:
                            path = parts[2]
                            confirm = Prompt.ask(f"⚠️  Delete {path}?", choices=["y", "n"], default="n")
                            if confirm == "y":
                                result = tools.delete_file(path)
                                console.print(f"\n{result}\n")
                            else:
                                console.print("[dim]Cancelled.[/dim]")
                    
                    elif subcommand == "list":
                        path = parts[2] if len(parts) >= 3 else "."
                        result = tools.list_directory(path)
                        console.print(f"\n{result}\n")
                    
                    else:
                        console.print(f"[red]Unknown subcommand: {subcommand}[/red]")
                    
                    continue
                
                elif command == "/app":
                    # App control command
                    parts = user_input.split(maxsplit=2)
                    if len(parts) < 2:
                        console.print("[red]Usage: /app <open|close|list> [app_name][/red]")
                        continue
                    
                    subcommand = parts[1].lower()
                    
                    if subcommand == "open":
                        if len(parts) < 3:
                            console.print("[red]Usage: /app open <app_name>[/red]")
                        else:
                            app_name = parts[2]
                            console.print(f"\n[yellow]🚀 Opening {app_name}...[/yellow]")
                            result = tools.open_app(app_name)
                            console.print(f"{result}\n")
                    
                    elif subcommand == "close":
                        if len(parts) < 3:
                            console.print("[red]Usage: /app close <app_name>[/red]")
                        else:
                            app_name = parts[2]
                            console.print(f"\n[yellow]🛑 Closing {app_name}...[/yellow]")
                            result = tools.close_app(app_name)
                            console.print(f"{result}\n")
                    
                    elif subcommand == "list":
                        console.print(f"\n[yellow]🖥️  Listing running apps...[/yellow]")
                        result = tools.list_running_apps()
                        console.print(f"\n{result}\n")
                    
                    else:
                        console.print(f"[red]Unknown subcommand: {subcommand}[/red]")
                    
                    continue
                
                elif command == "/listen":
                    # Voice input command
                    voice_input = tools.listen_voice()
                    if not voice_input.startswith("❌"):
                        # Use the voice input as the user message
                        user_input = voice_input
                        # Continue to process as normal message
                    else:
                        # Error occurred, skip processing
                        continue
                
                elif command == "/speak":
                    # Toggle voice output
                    voice_output_enabled = not voice_output_enabled
                    status = "enabled" if voice_output_enabled else "disabled"
                    emoji = "🔊" if voice_output_enabled else "🔇"
                    console.print(f"\n{emoji} Voice output {status}\n")
                    continue
                
                elif command == "/voicemode":
                    # Hands-free voice conversation mode
                    console.print("\n[bold cyan]🎤 Voice Mode Activated[/bold cyan]")
                    console.print("[dim]Say 'stop listening' or 'exit' to quit voice mode[/dim]\n")
                    
                    voice_mode_active = True
                    while voice_mode_active:
                        try:
                            # Listen for voice input
                            voice_input = tools.listen_voice()
                            
                            # Check for exit commands
                            if voice_input.lower() in ["stop listening", "exit", "quit", "stop"]:
                                console.print("[yellow]🔇 Voice mode deactivated[/yellow]\n")
                                break
                            
                            # Check for errors
                            if voice_input.startswith("❌"):
                                continue
                            
                            # Get AI response
                            response = ai.chat(voice_input, stream=False)
                            
                            # Speak the response
                            if response:
                                console.print("\n[dim]🔊 Speaking response...[/dim]")
                                tools.speak_text(response)
                        
                        except KeyboardInterrupt:
                            console.print("\n[yellow]🔇 Voice mode deactivated[/yellow]\n")
                            break
                    
                    continue
                
                else:
                    console.print(f"[red]Unknown command: {command}[/red]")
                    continue
            
            # **AUTOMATIC APP CONTROL DETECTION**
            user_lower = user_input.lower()
            app_action_handled = False
            
            # Detect open app requests
            if any(phrase in user_lower for phrase in ['open ', 'launch ', 'start ']):
                for trigger in ['open ', 'launch ', 'start ']:
                    if trigger in user_lower:
                        app_name = user_input[user_lower.index(trigger) + len(trigger):].strip()
                        # Remove common words at the end
                        for word in [' please', ' app', ' application']:
                            app_name = app_name.replace(word, '')
                        
                        if app_name:
                            console.print(f"\n[yellow]🚀 Opening {app_name}...[/yellow]")
                            result = tools.open_app(app_name)
                            console.print(f"{result}\n")
                            app_action_handled = True
                            break
            
            # Detect close app requests
            if not app_action_handled and any(phrase in user_lower for phrase in ['close ', 'quit ', 'exit ']):
                for trigger in ['close ', 'quit ', 'exit ']:
                    if trigger in user_lower:
                        # Make sure it's not the general exit command
                        if trigger == 'exit ' and user_lower.strip() == 'exit':
                            break
                        
                        app_name = user_input[user_lower.index(trigger) + len(trigger):].strip()
                        for word in [' please', ' app', ' application']:
                            app_name = app_name.replace(word, '')
                        
                        if app_name:
                            console.print(f"\n[yellow]🛑 Closing {app_name}...[/yellow]")
                            result = tools.close_app(app_name)
                            console.print(f"{result}\n")
                            app_action_handled = True
                            break
            
            # Skip to next iteration if app action was handled
            if app_action_handled:
                continue
            
            # **AUTOMATIC VOICE COMMAND DETECTION**
            user_lower = user_input.lower()
            voice_action_handled = False
            
            # Detect voice output toggle (TTS)
            if any(phrase in user_lower for phrase in ['tts on', 'turn on tts', 'enable tts', 'voice output on', 'speak on']):
                if not voice_output_enabled:
                    voice_output_enabled = True
                    console.print("\n🔊 Voice output enabled\n")
                else:
                    console.print("\n🔊 Voice output already enabled\n")
                voice_action_handled = True
            
            elif any(phrase in user_lower for phrase in ['tts off', 'turn off tts', 'disable tts', 'voice output off', 'speak off']):
                if voice_output_enabled:
                    voice_output_enabled = False
                    console.print("\n🔇 Voice output disabled\n")
                else:
                    console.print("\n🔇 Voice output already disabled\n")
                voice_action_handled = True
            
            # Detect voice input toggle (STT persistent mode)
            elif any(phrase in user_lower for phrase in ['stt on', 'turn on stt', 'enable stt', 'voice input on', 'keep listening']):
                if not voice_input_enabled:
                    voice_input_enabled = True
                    console.print("\n🎤 Voice input enabled - you can now speak instead of type!\n")
                    console.print("[dim]Say 'STT off' or 'stop listening' to disable[/dim]\n")
                else:
                    console.print("\n🎤 Voice input already enabled\n")
                voice_action_handled = True
            
            elif any(phrase in user_lower for phrase in ['stt off', 'turn off stt', 'disable stt', 'voice input off', 'stop listening']):
                if voice_input_enabled:
                    voice_input_enabled = False
                    console.print("\n⌨️  Voice input disabled - back to typing\n")
                else:
                    console.print("\n⌨️  Voice input already disabled\n")
                voice_action_handled = True
            
            # Detect exit/quit commands
            elif user_lower in ['exit', 'quit', 'goodbye', 'bye']:
                console.print("\n[yellow]👋 Goodbye![/yellow]\n")
                break
            
            # Detect voice mode request
            elif any(phrase in user_lower for phrase in ['voice mode', 'talk to me', 'voice conversation', 'hands free mode']):
                console.print("\n[bold cyan]🎤 Voice Mode Activated[/bold cyan]")
                console.print("[dim]Say 'stop listening' or 'exit' to quit voice mode[/dim]\n")
                
                voice_mode_active = True
                while voice_mode_active:
                    try:
                        voice_input = tools.listen_voice()
                        
                        if voice_input.lower() in ["stop listening", "exit", "quit", "stop"]:
                            console.print("[yellow]🔇 Voice mode deactivated[/yellow]\n")
                            break
                        
                        if voice_input.startswith("❌"):
                            continue
                        
                        response = ai.chat(voice_input, stream=False)
                        
                        if response:
                            console.print("\n[dim]🔊 Speaking response...[/dim]")
                            tools.speak_text(response)
                    
                    except KeyboardInterrupt:
                        console.print("\n[yellow]🔇 Voice mode deactivated[/yellow]\n")
                        break
                
                voice_action_handled = True
            
            # Skip AI response if voice action was handled
            if voice_action_handled:
                continue
            
            # **AUTOMATIC FILE OPERATION DETECTION**
            file_action_handled = False
            
            # Detect AI-powered file creation (e.g., "create a Python file with hello world")
            if any(phrase in user_lower for phrase in ['create file with', 'create a file with', 'make file with', 'new file with']):
                # Extract what comes after "with"
                for trigger in ['create file with', 'create a file with', 'make file with', 'new file with']:
                    if trigger in user_lower:
                        description = user_input[user_lower.index(trigger) + len(trigger):].strip()
                        
                        # Ask AI to generate the code
                        console.print(f"\n[yellow]🤖 Generating content...[/yellow]")
                        code_prompt = f"Generate code for: {description}\n\nOnly output the code, no explanations."
                        
                        # Get clean AI response
                        raw_output = ai.get_response(code_prompt)
                        
                        # Clean up markdown code blocks if present
                        generated_code = raw_output.strip()
                        if generated_code.startswith('```'):
                            lines = generated_code.split('\n')
                            lines = lines[1:]  # Remove first line (```language)
                            if lines and lines[-1].strip() == '```':
                                lines = lines[:-1]  # Remove last line (```)
                            generated_code = '\n'.join(lines).strip()
                        
                        # Ask for filename
                        filename = Prompt.ask("\n📝 Enter filename (e.g., script.py)")
                        
                        import os
                        from pathlib import Path
                        
                        # Extract just filename if full path given
                        filename = os.path.basename(filename) if '/' in filename else filename
                        
                        if '.' not in filename:
                            console.print("[red]⚠️  Please include a file extension[/red]\n")
                            file_action_handled = True
                            continue
                        
                        # Save to Desktop
                        desktop_path = os.path.expanduser("~/Desktop")
                        full_path = os.path.join(desktop_path, filename)
                        
                        result = tools.create_file(full_path, generated_code)
                        console.print(f"\n{result}\n")
                        file_action_handled = True
                        break
            
            # Detect manual file creation
            elif any(phrase in user_lower for phrase in ['create file', 'create a file', 'make file', 'make a file', 'new file']):
                filename = Prompt.ask("📝 Enter filename only (e.g., notes.txt)")
                content = Prompt.ask("📝 Enter file content (or press Enter for empty file)", default="")
                
                import os
                from pathlib import Path
                
                # If user entered a full path, extract just the filename
                filename = os.path.basename(filename) if '/' in filename else filename
                
                # Validate filename has an extension
                if '.' not in filename:
                    console.print("[red]⚠️  Please include a file extension (e.g., .txt, .py, .md)[/red]\n")
                    file_action_handled = True
                    continue
                
                # Build full path - use Desktop as default directory
                desktop_path = os.path.expanduser("~/Desktop")
                full_path = os.path.join(desktop_path, filename)
                
                result = tools.create_file(full_path, content)
                console.print(f"\n{result}\n")
                file_action_handled = True
            
            # Detect read file requests (including direct filename)
            elif any(phrase in user_lower for phrase in ['read file', 'read the file', 'read a file', 'show file', 'show the file', 'open file', 'open the file']) or (user_lower.startswith('read ') and '.' in user_input):
                # Check if filename was provided directly
                if user_lower.startswith('read ') and '.' in user_input:
                    filename = user_input[5:].strip()  # Remove "read "
                else:
                    filename = Prompt.ask("📄 Enter filename (on Desktop)")
                
                import os
                desktop_path = os.path.expanduser("~/Desktop")
                full_path = os.path.join(desktop_path, filename)
                
                result = tools.read_file(full_path)
                console.print(f"\n{result}\n")
                file_action_handled = True
            
            # Detect edit file requests (including direct filename)
            elif any(phrase in user_lower for phrase in ['edit file', 'edit the file', 'edit a file', 'modify file', 'modify the file', 'update file', 'update the file']) or (user_lower.startswith('edit ') and '.' in user_input):
                # Check if filename was provided directly
                if user_lower.startswith('edit ') and '.' in user_input:
                    filename = user_input[5:].strip()  # Remove "edit "
                else:
                    filename = Prompt.ask("✏️  Enter filename to edit (on Desktop)")
                
                # Ask if user wants AI to generate content or type manually
                choice = Prompt.ask("📝 How to update?", choices=["ai", "manual"], default="manual")
                
                if choice == "ai":
                    # AI-powered content generation
                    description = Prompt.ask("💡 Describe what code/content you want")
                    console.print(f"\n[yellow]🤖 Generating content...[/yellow]")
                    
                    code_prompt = f"Generate code/content for: {description}\n\nOnly output the code/content, no explanations."
                    
                    # Get clean AI response
                    raw_output = ai.get_response(code_prompt)
                    
                    # Clean up markdown code blocks if present
                    new_content = raw_output.strip()
                    if new_content.startswith('```'):
                        lines = new_content.split('\n')
                        lines = lines[1:]  # Remove first line (```language)
                        if lines and lines[-1].strip() == '```':
                            lines = lines[:-1]  # Remove last line (```)
                        new_content = '\n'.join(lines).strip()
                else:
                    # Manual content entry
                    new_content = Prompt.ask("📝 Enter new content")
                
                import os
                desktop_path = os.path.expanduser("~/Desktop")
                full_path = os.path.join(desktop_path, filename)
                
                result = tools.edit_file(full_path, new_content)
                console.print(f"\n{result}\n")
                file_action_handled = True
            
            # Detect rename file requests (including direct filenames)
            elif ' to ' in user_lower and any(word in user_lower for word in ['rename ', 'move ']):
                # Extract old and new names from "rename X to Y"
                parts = user_input.lower().split(' to ')
                if len(parts) == 2:
                    old_name = parts[0].replace('rename', '').replace('move', '').strip()
                    new_name = parts[1].strip()
                    
                    import os
                    desktop_path = os.path.expanduser("~/Desktop")
                    old_path = os.path.join(desktop_path, old_name)
                    new_path = os.path.join(desktop_path, new_name)
                    
                    try:
                        from pathlib import Path
                        Path(old_path).rename(new_path)
                        console.print(f"\n✅ Renamed: {old_name} → {new_name}\n")
                    except Exception as e:
                        console.print(f"\n❌ Error renaming file: {str(e)}\n")
                    file_action_handled = True
            
            # Fallback: prompt for rename if just "rename file" said
            elif any(phrase in user_lower for phrase in ['rename file', 'rename the file', 'rename a file']):
                old_name = Prompt.ask("📄 Enter current filename (on Desktop)")
                new_name = Prompt.ask("📝 Enter new filename")
                
                import os
                desktop_path = os.path.expanduser("~/Desktop")
                old_path = os.path.join(desktop_path, old_name)
                new_path = os.path.join(desktop_path, new_name)
                
                try:
                    from pathlib import Path
                    Path(old_path).rename(new_path)
                    console.print(f"\n✅ Renamed: {old_name} → {new_name}\n")
                except Exception as e:
                    console.print(f"\n❌ Error renaming file: {str(e)}\n")
                file_action_handled = True
            
            # Detect delete file requests (including direct filename)
            elif any(phrase in user_lower for phrase in ['delete file', 'delete the file', 'delete a file', 'remove file', 'remove the file', 'remove a file']) or (user_lower.startswith('delete ') and '.' in user_input):
                # Check if filename was provided directly
                if user_lower.startswith('delete ') and '.' in user_input:
                    filename = user_input[7:].strip()  # Remove "delete "
                else:
                    filename = Prompt.ask("🗑️  Enter filename to delete (on Desktop)")
                confirm = Prompt.ask(f"⚠️  Delete {filename}?", choices=["y", "n"], default="n")
                
                if confirm == "y":
                    import os
                    desktop_path = os.path.expanduser("~/Desktop")
                    full_path = os.path.join(desktop_path, filename)
                    
                    result = tools.delete_file(full_path)
                    console.print(f"\n{result}\n")
                else:
                    console.print("[dim]Cancelled.[/dim]\n")
                file_action_handled = True
            
            # Skip AI response if file action was handled
            if file_action_handled:
                continue
            
            # **AUTOMATIC TIME, DATE, AND WEATHER DETECTION**
            time_date_weather_handled = False
            
            # Detect time requests
            if any(phrase in user_lower for phrase in ['what time', 'current time', 'what is the time', "what's the time", 'time now', 'tell me the time']):
                console.print(f"\n[yellow]🕐 Getting current time...[/yellow]")
                result = tools.get_current_time()
                console.print(f"\n{result}\n")
                time_date_weather_handled = True
            
            # Detect date requests
            elif any(phrase in user_lower for phrase in ['what date', 'current date', "what's the date", 'date today', 'today date', 'tell me the date', "today's date"]):
                console.print(f"\n[yellow]📅 Getting current date...[/yellow]")
                result = tools.get_current_date()
                console.print(f"\n{result}\n")
                time_date_weather_handled = True
            
            # Detect weather requests
            elif any(phrase in user_lower for phrase in ['weather', 'temperature', 'how hot', 'how cold', 'forecast', 'climate']):
                # Try to extract location from the query
                location = "auto"
                
                # Common patterns to extract location
                for pattern in ['weather in ', 'weather at ', 'temperature in ', 'temperature at ', 'forecast for ', 'forecast in ']:
                    if pattern in user_lower:
                        location = user_input[user_lower.index(pattern) + len(pattern):].strip()
                        # Remove trailing punctuation and common words
                        for word in [' please', '?', '.', '!', ' now', ' right now', ' today', ' currently']:
                            location = location.replace(word, '')
                        location = location.strip()
                        break
                
                console.print(f"\n[yellow]🌤️  Getting weather information...[/yellow]")
                result = tools.get_weather(location)
                console.print(f"\n{result}\n")
                time_date_weather_handled = True
            
            # Skip to next iteration if time/date/weather was handled
            if time_date_weather_handled:
                continue
            
            # **AUTOMATIC SEARCH DETECTION**
            
            # Check if user is asking about current/recent events
            search_triggers = [
                'latest', 'recent', 'current', 'today', 'yesterday',
                'this week', 'this month', 'this year',
                'what happened', 'when did', 'when was', 'when is',
                '2024', '2025', '2026',  # Recent years
                'news', 'update', 'just announced'
            ]
            
            # Specific topics that need search
            topic_triggers = [
                'mother of all', 'india eu', 'trade deal', 'trump',
                'election', 'war', 'climate', 'covid', 'ai news'
            ]
            
            should_search = any(trigger in user_lower for trigger in search_triggers + topic_triggers)
            
            if should_search:
                # Automatically search for current information
                console.print(f"\n[dim]🔍 Searching for current information...[/dim]")
                
                # Determine if it's news or general search
                if any(word in user_lower for word in ['news', 'latest', 'recent', 'announced']):
                    search_result = tools.news_search(user_input, max_results=5)
                else:
                    search_result = tools.web_search(user_input, max_results=5)
                
                # Add search results as context to the AI
                enhanced_prompt = f"""User question: {user_input}

Current information from search:
{search_result}

Based on the above search results, please provide a clear and accurate answer to the user's question."""
                
                console.print("[dim]📝 Analyzing results...[/dim]")
                response = ai.chat(enhanced_prompt, stream=True)
            else:
                # Normal chat without search
                response = ai.chat(user_input, stream=True)
            
            # Speak response if voice output is enabled
            if voice_output_enabled and response:
                console.print("\n[dim]🔊 Speaking response...[/dim]")
                tools.speak_text(response)
            
        except KeyboardInterrupt:
            console.print("\n\n[cyan]Goodbye! 👋[/cyan]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}")


if __name__ == "__main__":
    main()
