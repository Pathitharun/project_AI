"""
Search and News Tools for AI
Provides web search and news retrieval capabilities
"""

import os
import json
from typing import Optional
from datetime import datetime, timedelta
import pytz
import speedtest
from rich.console import Console
from dotenv import load_dotenv
import subprocess
from pathlib import Path
import requests
from news_sources import get_news, get_news_formatted, CATEGORIES, COUNTRIES

load_dotenv()

console = Console()


def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using SerpApi (Google Search)
    
    Args:
        query: Search query
        max_results: Maximum number of results
        
    Returns:
        Formatted search results
    """
    try:
        # Get API key from environment
        api_key = os.getenv("SERPAPI_API_KEY")
        
        if not api_key or api_key == "your_serpapi_key_here":
            return "❌ SerpApi API key not configured. Please add SERPAPI_API_KEY to your .env file.\nGet your API key at: https://serpapi.com"
        
        # SerpApi endpoint
        url = "https://serpapi.com/search"
        
        # API parameters
        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "num": max_results
        }
        
        # Make API request
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract organic results
        organic_results = data.get("organic_results", [])
        
        if not organic_results:
            return f"No search results found for: {query}"
        
        # Format results
        output = f"🔍 Web Search Results for '{query}':\n\n"
        for i, result in enumerate(organic_results[:max_results], 1):
            title = result.get('title', 'No title')
            snippet = result.get('snippet', 'No description')
            link = result.get('link', '')
            
            output += f"{i}. **{title}**\n"
            output += f"   {snippet}\n"
            if link:
                output += f"   🔗 {link}\n"
            output += "\n"
        
        return output.strip()
    
    except requests.exceptions.Timeout:
        return f"❌ Search request timed out. Please try again."
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return "❌ Invalid SerpApi API key. Please check your SERPAPI_API_KEY in .env file."
        elif e.response.status_code == 429:
            return "❌ SerpApi rate limit exceeded. Please try again later."
        else:
            return f"❌ SerpApi error: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error performing web search: {str(e)}"


def news_search(query: str, max_results: int = 5, days_back: int = 7) -> str:
    """
    Search for recent news articles using NewsAPI.org
    
    Args:
        query: News topic or keyword
        max_results: Maximum number of articles
        days_back: How many days back to search (not used, kept for compatibility)
        
    Returns:
        Formatted news results with only useful info (title, content, source, URL)
    """
    # Use the clean NewsAPI implementation from news_sources.py
    return get_news_formatted(query=query, max_results=max_results)


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
    }
]


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
            # Try to get GPS location first
            try:
                location_result = get_location()
                # Extract city from location result if successful
                if "❌" not in location_result:
                    # Parse the city from the location output
                    import re
                    city_match = re.search(r'🏙️  City: ([^,\n]+)', location_result)
                    if city_match:
                        detected_city = city_match.group(1).strip()
                        console.print(f"[dim]📍 Using GPS location: {detected_city}[/dim]")
                        url = f"https://wttr.in/{detected_city}?format=j1"
                    else:
                        # Fallback to IP-based detection
                        url = "https://wttr.in/?format=j1"
                else:
                    # GPS failed, use IP-based detection
                    console.print("[dim]📍 GPS unavailable, using IP-based location[/dim]")
                    url = "https://wttr.in/?format=j1"
            except:
                # Any error, fallback to IP-based detection
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


def get_location(**kwargs) -> str:
    """
    Get current GPS location using CoreLocationCLI
    
    Args:
        **kwargs: Accepts any arguments (for compatibility with tool calling)
    
    Returns:
        Formatted location information with coordinates, city, address, etc.
    """
    try:
        # Get the script directory
        script_dir = Path(__file__).parent
        script_path = script_dir / "get_location.sh"
        
        # Check if script exists
        if not script_path.exists():
            return "❌ Location script not found. Please ensure get_location.sh exists in the project directory."
        
        # Run the location script
        result = subprocess.run(
            [str(script_path)],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode != 0:
            # Check error message
            if "not installed" in result.stderr:
                return "❌ CoreLocationCLI not installed. Installing via Homebrew...\n" + result.stderr
            elif "timed out" in result.stderr or "Location Services" in result.stderr:
                return "❌ Could not get location. Please ensure:\n1. Location Services are enabled in System Settings > Privacy & Security\n2. Terminal has location permissions"
            elif "approve" in result.stderr.lower():
                return "❌ CoreLocationCLI needs approval. Please:\n1. Go to System Settings > Privacy & Security\n2. Approve CoreLocationCLI in the bottom-right corner\n3. Try again"
            else:
                return f"❌ Error getting location: {result.stderr}"
        
        # Parse JSON output
        location_data = json.loads(result.stdout)
        
        # Extract location information
        latitude = location_data.get('latitude', 'N/A')
        longitude = location_data.get('longitude', 'N/A')
        address = location_data.get('address', 'N/A')
        city = location_data.get('locality', 'Unknown')
        state = location_data.get('administrativeArea', '')
        country = location_data.get('country', 'Unknown')
        postal_code = location_data.get('postalCode', '')
        altitude = location_data.get('altitude', 'N/A')
        
        # Format output
        output = "📍 Current Location:\\n\\n"
        output += f"🌍 Coordinates: {latitude}, {longitude}\\n"
        output += f"🏙️  City: {city}"
        if state:
            output += f", {state}"
        output += f"\\n🌏 Country: {country}\\n"
        
        if postal_code:
            output += f"📮 Postal Code: {postal_code}\\n"
        
        if altitude != 'N/A':
            output += f"⛰️  Altitude: {altitude}m\\n"
        
        output += f"\\n📬 Full Address:\\n{address}"
        
        return output
        
    except subprocess.TimeoutExpired:
        return "❌ Location request timed out. Please ensure Location Services are enabled."
    except json.JSONDecodeError:
        return "❌ Failed to parse location data. Please try again."
    except Exception as e:
        return f"❌ Error getting location: {str(e)}"


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


# ============================================================================
# MEMORY MANAGEMENT
# ============================================================================

def manage_memory(mode: str, content: Optional[str] = None, filepath: str = "memory.md") -> Optional[str]:
    """
    Manage a markdown memory file with read, write, and append operations.
    
    Args:
        mode (str): Operation mode - 'r' (read), 'w' (write), 'a' (append)
        content (str, optional): Content to write or append. Required for 'w' and 'a' modes
        filepath (str): Path to the memory file. Defaults to "memory.md"
    
    Returns:
        str: File content for read mode, success message for write/append modes
        None: If operation fails
    
    Examples:
        # Read memory
        memory = manage_memory('r')
        
        # Write new memory (overwrites existing)
        manage_memory('w', "# My Memory\n\nImportant notes here")
        
        # Append to memory
        manage_memory('a', "\n\n## New Section\n\nAdditional information")
    """
    
    try:
        if mode == 'r':
            # Read mode
            if not os.path.exists(filepath):
                return "Memory file does not exist yet."
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif mode == 'w':
            # Write mode (overwrite)
            if content is None:
                raise ValueError("Content is required for write mode")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"✅ Successfully wrote to {filepath}"
        
        elif mode == 'a':
            # Append mode
            if content is None:
                raise ValueError("Content is required for append mode")
            
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(content)
            
            return f"✅ Successfully appended to {filepath}"
        
        else:
            raise ValueError(f"Invalid mode: {mode}. Use 'r', 'w', or 'a'")
    
    except Exception as e:
        return f"❌ Error: {str(e)}"


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


# Tool functional mapping
AVAILABLE_TOOLS = {
    "web_search": web_search,
    "news_search": news_search,
    "manage_memory": manage_memory,
    "get_category_news": get_news_formatted,
    "get_location": get_location
}
