"""
Search and News Tools for AI
Provides web search and news retrieval capabilities
"""

import os
import json
from typing import Optional
from datetime import datetime, timedelta
import pytz
from ddgs import DDGS
from newsapi import NewsApiClient
import speedtest
from rich.console import Console
from dotenv import load_dotenv
import subprocess
from pathlib import Path
import requests

load_dotenv()

console = Console()


def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo
    
    Args:
        query: Search query
        max_results: Maximum number of results
        
    Returns:
        Formatted search results
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        
        if not results:
            return f"No search results found for: {query}"
        
        # Format results
        output = f"🔍 Web Search Results for '{query}':\n\n"
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            body = result.get('body', 'No description')
            url = result.get('href', '')
            
            output += f"{i}. **{title}**\n"
            output += f"   {body}\n"
            if url:
                output += f"   🔗 {url}\n"
            output += "\n"
        
        return output.strip()
    
    except Exception as e:
        return f"Error performing web search: {str(e)}"


def news_search(query: str, max_results: int = 5, days_back: int = 7) -> str:
    """
    Search for recent news articles
    
    Args:
        query: News topic or keyword
        max_results: Maximum number of articles
        days_back: How many days back to search
        
    Returns:
        Formatted news results
    """
    newsapi_key = os.getenv("NEWSAPI_KEY")
    
    # If no NewsAPI key, fall back to DuckDuckGo news search
    if not newsapi_key:
        return _ddg_news_search(query, max_results)
    
    try:
        newsapi = NewsApiClient(api_key=newsapi_key)
        
        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_back)
        
        # Search for news
        response = newsapi.get_everything(
            q=query,
            from_param=from_date.strftime('%Y-%m-%d'),
            to=to_date.strftime('%Y-%m-%d'),
            language='en',
            sort_by='publishedAt',
            page_size=max_results
        )
        
        articles = response.get('articles', [])
        
        if not articles:
            return f"No recent news found for: {query}"
        
        # Format results
        output = f"📰 Latest News on '{query}':\n\n"
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'No title')
            description = article.get('description', 'No description')
            source = article.get('source', {}).get('name', 'Unknown')
            published = article.get('publishedAt', '')
            url = article.get('url', '')
            
            # Format date
            if published:
                try:
                    pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                    published = pub_date.strftime('%Y-%m-%d %H:%M')
                except:
                    pass
            
            output += f"{i}. **{title}**\n"
            output += f"   📍 {source} | {published}\n"
            output += f"   {description}\n"
            if url:
                output += f"   🔗 {url}\n"
            output += "\n"
        
        return output.strip()
    
    except Exception as e:
        # Fall back to DuckDuckGo on error
        return _ddg_news_search(query, max_results)


def _ddg_news_search(query: str, max_results: int = 5) -> str:
    """
    Fallback news search using DuckDuckGo
    
    Args:
        query: News topic or keyword
        max_results: Maximum number of results
        
    Returns:
        Formatted news results
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=max_results))
        
        if not results:
            return f"No recent news found for: {query}"
        
        # Format results
        output = f"📰 Latest News on '{query}':\n\n"
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            body = result.get('body', 'No description')
            source = result.get('source', 'Unknown')
            date = result.get('date', '')
            url = result.get('url', '')
            
            output += f"{i}. **{title}**\n"
            output += f"   📍 {source}"
            if date:
                output += f" | {date}"
            output += "\n"
            output += f"   {body}\n"
            if url:
                output += f"   🔗 {url}\n"
            output += "\n"
        
        return output.strip()
    
    except Exception as e:
        return f"Error fetching news: {str(e)}"


# Function schemas for Groq function calling
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
    }
]


# Tool functional mapping
AVAILABLE_TOOLS = {
    "web_search": web_search,
    "news_search": news_search
}


def execute_tool(tool_name: str, arguments: dict) -> str:
    """
    Execute a tool by name with given arguments
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Arguments to pass to the tool
        
    Returns:
        Tool execution result
    """
    if tool_name not in AVAILABLE_TOOLS:
        return f"Error: Unknown tool '{tool_name}'"
    
    try:
        tool_func = AVAILABLE_TOOLS[tool_name]
        result = tool_func(**arguments)
        return result
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"


def internet_speed_test() -> str:
    """
    Test internet connection speed
    
    Returns:
        Formatted string with download/upload speeds and ping
    """
    try:
        console.print("[dim]🌐 Testing internet speed...[/dim]")
        st = speedtest.Speedtest()
        
        console.print("[dim]📡 Finding best server...[/dim]")
        st.get_best_server()
        
        console.print("[dim]⬇️  Testing download speed...[/dim]")
        download_bps = st.download()
        
        console.print("[dim]⬆️  Testing upload speed...[/dim]")
        upload_bps = st.upload()
        
        ping = st.results.ping
        
        # Convert to Mbps
        download_mbps = download_bps / 1_000_000
        upload_mbps = upload_bps / 1_000_000
        
        # Format results
        output = "🚀 Internet Speed Test Results:\n\n"
        output += f"⬇️  Download: {download_mbps:.2f} Mbps\n"
        output += f"⬆️  Upload: {upload_mbps:.2f} Mbps\n"
        output += f"📶 Ping: {ping:.2f} ms"
        
        return output
        
    except Exception as e:
        return f"❌ Error testing internet speed: {str(e)}"


# ============================================================================
# FILE OPERATIONS
# ============================================================================

def create_file(path: str, content: str = "") -> str:
    """Create a new file with content"""
    try:
        file_path = Path(path).expanduser()
        
        # Check if file already exists
        if file_path.exists():
            return f"❌ File already exists: {file_path}"
        
        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        file_path.write_text(content)
        
        return f"✅ Created file: {file_path}"
        
    except Exception as e:
        return f"❌ Error creating file: {str(e)}"


def read_file(path: str) -> str:
    """Read file contents"""
    try:
        file_path = Path(path).expanduser()
        
        if not file_path.exists():
            return f"❌ File not found: {file_path}"
        
        if not file_path.is_file():
            return f"❌ Not a file: {file_path}"
        
        content = file_path.read_text()
        
        output = f"📄 File: {file_path.name}\n"
        output += f"📍 Path: {file_path}\n"
        output += f"📏 Size: {len(content)} characters\n\n"
        output += "--- Content ---\n"
        output += content
        
        return output
        
    except Exception as e:
        return f"❌ Error reading file: {str(e)}"


def edit_file(path: str, new_content: str) -> str:
    """Edit/replace file content"""
    try:
        file_path = Path(path).expanduser()
        
        if not file_path.exists():
            return f"❌ File not found: {file_path}"
        
        # Backup old content
        old_content = file_path.read_text()
        old_size = len(old_content)
        
        # Write new content
        file_path.write_text(new_content)
        new_size = len(new_content)
        
        return f"✅ Edited file: {file_path}\n📏 Old: {old_size} chars → New: {new_size} chars"
        
    except Exception as e:
        return f"❌ Error editing file: {str(e)}"


def delete_file(path: str) -> str:
    """Delete a file"""
    try:
        file_path = Path(path).expanduser()
        
        if not file_path.exists():
            return f"❌ File not found: {file_path}"
        
        if not file_path.is_file():
            return f"❌ Not a file: {file_path}"
        
        # Get file info before deleting
        size = file_path.stat().st_size
        
        # Delete
        file_path.unlink()
        
        return f"✅ Deleted file: {file_path} ({size} bytes)"
        
    except Exception as e:
        return f"❌ Error deleting file: {str(e)}"


def list_directory(path: str = ".") -> str:
    """List files and directories"""
    try:
        dir_path = Path(path).expanduser()
        
        if not dir_path.exists():
            return f"❌ Directory not found: {dir_path}"
        
        if not dir_path.is_dir():
            return f"❌ Not a directory: {dir_path}"
        
        items = sorted(dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        
        output = f"📂 Directory: {dir_path}\n\n"
        
        dirs = [item for item in items if item.is_dir()]
        files = [item for item in items if item.is_file()]
        
        if dirs:
            output += "📁 Directories:\n"
            for item in dirs:
                output += f"  • {item.name}/\n"
            output += "\n"
        
        if files:
            output += "📄 Files:\n"
            for item in files:
                size = item.stat().st_size
                output += f"  • {item.name} ({size:,} bytes)\n"
        
        if not dirs and not files:
            output += "Empty directory"
        
        return output
        
    except Exception as e:
        return f"❌ Error listing directory: {str(e)}"


# ============================================================================
# APP CONTROL (macOS)
# ============================================================================

def open_app(app_name: str) -> str:
    """Open a macOS application"""
    try:
        result = subprocess.run(
            ['open', '-a', app_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return f"✅ Opened app: {app_name}"
        else:
            return f"❌ Failed to open {app_name}: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return f"❌ Timeout opening {app_name}"
    except Exception as e:
        return f"❌ Error opening app: {str(e)}"


def close_app(app_name: str) -> str:
    """Close a macOS application"""
    try:
        script = f'tell application "{app_name}" to quit'
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return f"✅ Closed app: {app_name}"
        else:
            error = result.stderr.strip()
            if "not running" in error.lower():
                return f"ℹ️  App not running: {app_name}"
            return f"❌ Failed to close {app_name}: {error}"
            
    except subprocess.TimeoutExpired:
        return f"❌ Timeout closing {app_name}"
    except Exception as e:
        return f"❌ Error closing app: {str(e)}"


def list_running_apps() -> str:
    """List currently running applications"""
    try:
        script = 'tell application "System Events" to get name of every process whose background only is false'
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            apps = result.stdout.strip().split(', ')
            apps = sorted(apps)
            
            output = "🖥️  Running Applications:\n\n"
            for app in apps:
                output += f"  • {app}\n"
            
            output += f"\nTotal: {len(apps)} apps"
            return output
        else:
            return f"❌ Failed to list apps: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return "❌ Timeout listing apps"
    except Exception as e:
        return f"❌ Error listing apps: {str(e)}"


# ============================================================================
# TIME, DATE, AND WEATHER INFORMATION
# ============================================================================

def get_current_time(timezone: str = "Asia/Kolkata") -> str:
    """
    Get current time in specified timezone
    
    Args:
        timezone: Timezone name (e.g., "Asia/Kolkata", "America/New_York", "UTC")
        
    Returns:
        Formatted current time
    """
    try:
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        
        # Format time in 12-hour format with AM/PM
        time_12hr = current_time.strftime("%I:%M:%S %p")
        # Format time in 24-hour format
        time_24hr = current_time.strftime("%H:%M:%S")
        
        output = f"🕐 Current Time ({timezone}):\n\n"
        output += f"⏰ {time_12hr}\n"
        output += f"🕰️  {time_24hr}\n"
        output += f"📅 {current_time.strftime('%A, %B %d, %Y')}"
        
        return output
        
    except Exception as e:
        return f"❌ Error getting time: {str(e)}\nAvailable timezones: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"


def get_current_date(timezone: str = "Asia/Kolkata") -> str:
    """
    Get current date in specified timezone
    
    Args:
        timezone: Timezone name (e.g., "Asia/Kolkata", "America/New_York", "UTC")
        
    Returns:
        Formatted current date with additional info
    """
    try:
        tz = pytz.timezone(timezone)
        current_date = datetime.now(tz)
        
        # Calculate day of year
        day_of_year = current_date.timetuple().tm_yday
        # Calculate week number
        week_number = current_date.isocalendar()[1]
        
        output = f"📅 Current Date ({timezone}):\n\n"
        output += f"📆 {current_date.strftime('%A, %B %d, %Y')}\n"
        output += f"📍 Day {day_of_year} of {current_date.year}\n"
        output += f"📊 Week {week_number} of the year\n"
        output += f"🕐 Time: {current_date.strftime('%I:%M %p')}"
        
        return output
        
    except Exception as e:
        return f"❌ Error getting date: {str(e)}"


def get_weather(location: str = "auto") -> str:
    """
    Get current weather information for a location
    
    Args:
        location: City name (e.g., "Mumbai", "New York") or "auto" for automatic detection
        
    Returns:
        Formatted weather information
    """
    try:
        # Using wttr.in API (no key required, simple and reliable)
        if location.lower() == "auto":
            # Auto-detect location
            url = "https://wttr.in/?format=j1"
        else:
            # Specific location
            url = f"https://wttr.in/{location}?format=j1"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract current conditions
        current = data.get('current_condition', [{}])[0]
        location_data = data.get('nearest_area', [{}])[0]
        
        # Get location info
        area_name = location_data.get('areaName', [{}])[0].get('value', 'Unknown')
        country = location_data.get('country', [{}])[0].get('value', 'Unknown')
        
        # Get weather details
        temp_c = current.get('temp_C', 'N/A')
        temp_f = current.get('temp_F', 'N/A')
        feels_like_c = current.get('FeelsLikeC', 'N/A')
        feels_like_f = current.get('FeelsLikeF', 'N/A')
        weather_desc = current.get('weatherDesc', [{}])[0].get('value', 'N/A')
        humidity = current.get('humidity', 'N/A')
        wind_speed_kmph = current.get('windspeedKmph', 'N/A')
        wind_speed_mph = current.get('windspeedMiles', 'N/A')
        wind_dir = current.get('winddir16Point', 'N/A')
        pressure = current.get('pressure', 'N/A')
        visibility = current.get('visibility', 'N/A')
        uv_index = current.get('uvIndex', 'N/A')
        
        # Weather emoji based on condition
        weather_emoji = "🌤️"
        desc_lower = weather_desc.lower()
        if 'rain' in desc_lower or 'drizzle' in desc_lower:
            weather_emoji = "🌧️"
        elif 'snow' in desc_lower:
            weather_emoji = "❄️"
        elif 'cloud' in desc_lower:
            weather_emoji = "☁️"
        elif 'clear' in desc_lower or 'sunny' in desc_lower:
            weather_emoji = "☀️"
        elif 'thunder' in desc_lower or 'storm' in desc_lower:
            weather_emoji = "⛈️"
        elif 'fog' in desc_lower or 'mist' in desc_lower:
            weather_emoji = "🌫️"
        
        output = f"{weather_emoji} Weather in {area_name}, {country}:\n\n"
        output += f"🌡️  Temperature: {temp_c}°C / {temp_f}°F\n"
        output += f"🤔 Feels Like: {feels_like_c}°C / {feels_like_f}°F\n"
        output += f"☁️  Condition: {weather_desc}\n"
        output += f"💧 Humidity: {humidity}%\n"
        output += f"💨 Wind: {wind_speed_kmph} km/h ({wind_speed_mph} mph) {wind_dir}\n"
        output += f"🔽 Pressure: {pressure} mb\n"
        output += f"👁️  Visibility: {visibility} km\n"
        output += f"☀️  UV Index: {uv_index}"
        
        return output
        
    except requests.exceptions.Timeout:
        return "❌ Weather request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return f"❌ Error fetching weather data: {str(e)}\nTip: Check your internet connection or try a different location."
    except Exception as e:
        return f"❌ Error getting weather: {str(e)}"


# ================================
# VOICE CAPABILITIES (TTS & STT)
# ================================

def listen_voice() -> str:
    """
    Listen to microphone and convert speech to text
    Tries online recognition first, falls back to offline Vosk if unavailable
    
    Returns:
        Transcribed text or error message
    """
    try:
        import speech_recognition as sr
        
        recognizer = sr.Recognizer()
        
        with sr.Microphone() as source:
            console.print("[yellow]🎤 Listening... (speak now)[/yellow]")
            
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            # Listen for audio
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
        console.print("[dim]⏳ Processing...[/dim]")
        
        # Try online recognition first (Google Speech Recognition)
        try:
            text = recognizer.recognize_google(audio)
            console.print(f"[green]✅ Heard (online):[/green] {text}\n")
            return text
        except sr.UnknownValueError:
            error_msg = "❌ Could not understand audio. Please try again."
            console.print(f"[red]{error_msg}[/red]\n")
            return error_msg
        except sr.RequestError as e:
            # Online recognition failed, try offline Vosk
            console.print(f"[yellow]⚠️  Online recognition unavailable, switching to offline...[/yellow]")
            return _vosk_recognize(audio)
            
    except ImportError:
        error_msg = "❌ Speech recognition not installed. Run: pip install SpeechRecognition PyAudio"
        console.print(f"[red]{error_msg}[/red]\n")
        return error_msg
    except OSError as e:
        if "No Default Input Device Available" in str(e):
            error_msg = "❌ No microphone detected. Please connect a microphone."
        else:
            error_msg = f"❌ Microphone error: {str(e)}"
        console.print(f"[red]{error_msg}[/red]\n")
        return error_msg
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        console.print(f"[red]{error_msg}[/red]\n")
        return error_msg


def _vosk_recognize(audio) -> str:
    """
    Offline speech recognition using Vosk
    
    Args:
        audio: AudioData object from speech_recognition
        
    Returns:
        Transcribed text or error message
    """
    try:
        import vosk
        import json
        import wave
        import tempfile
        import os
        
        # Get model path
        model_path = os.path.expanduser("~/.vosk/models/vosk-model-small-en-us-0.15")
        
        # Check if model exists, if not provide download instructions
        if not os.path.exists(model_path):
            console.print("[yellow]📦 Downloading offline speech model (one-time setup)...[/yellow]")
            # Create directory
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            
            # Download small English model
            import zipfile
            import urllib.request
            
            model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
            zip_path = os.path.expanduser("~/.vosk/models/model.zip")
            
            try:
                urllib.request.urlretrieve(model_url, zip_path)
                console.print("[dim]📦 Extracting model...[/dim]")
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(os.path.expanduser("~/.vosk/models/"))
                
                os.remove(zip_path)
                console.print("[green]✅ Offline model installed![/green]")
            except Exception as e:
                error_msg = f"❌ Failed to download model: {str(e)}\nManually download from: {model_url}"
                console.print(f"[red]{error_msg}[/red]\n")
                return error_msg
        
        # Initialize Vosk
        vosk.SetLogLevel(-1)  # Suppress logs
        model = vosk.Model(model_path)
        
        # Convert audio to WAV format for Vosk
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
            temp_path = temp_wav.name
            
            # Write audio data to temporary WAV file
            with wave.open(temp_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                # Convert audio data
                wf.writeframes(audio.get_wav_data(convert_rate=16000))
        
        # Recognize
        try:
            with wave.open(temp_path, 'rb') as wf:
                rec = vosk.KaldiRecognizer(model, wf.getframerate())
                
                # Process audio
                while True:
                    data = wf.readframes(4000)
                    if len(data) == 0:
                        break
                    rec.AcceptWaveform(data)
                
                # Get result
                result = json.loads(rec.FinalResult())
                text = result.get('text', '')
                
                if text:
                    console.print(f"[green]✅ Heard (offline):[/green] {text}\n")
                    return text
                else:
                    error_msg = "❌ Could not understand audio (offline). Please try again."
                    console.print(f"[red]{error_msg}[/red]\n")
                    return error_msg
        finally:
            # Clean up temp file
            os.unlink(temp_path)
            
    except ImportError:
        error_msg = "❌ Offline recognition not available. Install with: pip install vosk"
        console.print(f"[red]{error_msg}[/red]\n")
        return error_msg
    except Exception as e:
        error_msg = f"❌ Offline recognition error: {str(e)}"
        console.print(f"[red]{error_msg}[/red]\n")
        return error_msg


def speak_text(text: str) -> bool:
    """
    Convert text to speech and play it
    
    Args:
        text: Text to speak
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import pyttsx3
        
        # Initialize TTS engine
        engine = pyttsx3.init()
        
        # Set properties (optional)
        engine.setProperty('rate', 175)  # Speed (words per minute)
        engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
        
        # Speak the text
        engine.say(text)
        engine.runAndWait()
        
        return True
        
    except ImportError:
        console.print("[red]❌ TTS not installed. Run: pip install pyttsx3[/red]\n")
        return False
    except Exception as e:
        console.print(f"[red]❌ TTS error: {str(e)}[/red]\n")
        return False


# Tool schemas for AI function calling (if needed in the future)
VOICE_TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "listen_voice",
            "description": "Listen to microphone input and convert speech to text",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "speak_text",
            "description": "Convert text to speech and play it aloud",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to speak"
                    }
                },
                "required": ["text"]
            }
        }
    }
]
