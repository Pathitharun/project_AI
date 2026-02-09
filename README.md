# 🤖 Hybrid AI Chat Assistant

A powerful AI assistant that **automatically switches between online (Groq) and offline (Ollama) modes**, with intelligent auto-search, file operations, app control, voice capabilities, and real-time information access.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- [Ollama](https://ollama.ai) installed with `llama3.2` model
- Groq API key (for online features)

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
echo "SERPAPI_API_KEY=your_serpapi_key_here" >> .env
echo "NEWSAPI_KEY=your_newsapi_key_here" >> .env  # Optional

# Run the assistant
python main.py
```

## ✨ Core Features

### 🌐 Hybrid AI System
- **Online Mode (Groq)**: Uses `llama-3.3-70b-versatile` with function calling for intelligent search
- **Offline Mode (Ollama)**: Uses local `llama3.2` model when internet is unavailable
- **Auto-Switch**: Seamlessly switches between modes based on connectivity

### 🔍 Intelligent Auto-Search
The AI automatically detects when you need current information and searches the web:
- News search for latest events
- Web search for general queries
- Automatic detection of temporal queries (2024, 2025, 2026, "latest", "recent", etc.)

### 📁 File Operations
Create, read, edit, delete, and list files - with AI code generation!
- **AI-Powered**: Ask AI to generate code for you
- **Manual Mode**: Type content yourself
- **Direct Commands**: Support for quick file operations
- **Smart Defaults**: Files saved to Desktop by default

### 🖥️ App Control (macOS)
Open, close, and manage applications with natural language:
- Automatic detection ("open Safari", "close Chrome")
- Manual commands (`/app open Safari`)
- List running applications

### 🎤 Voice Capabilities
- **Voice Input (STT)**: Speak instead of typing (online + offline support!)
- **Voice Output (TTS)**: Hear responses aloud (offline capable!)
- **Voice Mode**: Completely hands-free conversation
- **Persistent STT**: Enable "always listening" mode
- **Hybrid Recognition**: Auto-switches between Google (online) and Vosk (offline)

### 🌤️ Real-Time Information
- **Current Time**: Get time in any timezone
- **Current Date**: Date with day-of-year and week number
- **Weather**: Real-time weather for any location (auto-detects using GPS!)
- **GPS Location**: Get precise coordinates, address, and location data (macOS only)

### ⚡ Internet Tools
- **Speed Test**: Test your internet connection
- **Web Search**: SerpApi (Google Search) integration
- **News Search**: NewsAPI + SerpApi (Google News) fallback

## 📖 Commands Reference

### General Commands
| Command | Description |
|---------|-------------|
| `/help` | Show all available commands |
| `/quit` or `/exit` | Exit the assistant |

### Search & Information
| Command | Description | Example |
|---------|-------------|---------|
| `/search <query>` | Web search with AI summary | `/search Python tutorials` |
| `/news <topic>` | Latest news with AI summary | `/news climate change` |
| `/speed` | Test internet speed | `/speed` |
| **Natural queries** | Auto-search enabled | `what happened with India EU?` |

### File Operations
| Command | Description | Example |
|---------|-------------|---------|
| `/file create <path>` | Create new file | `/file create notes.txt` |
| `/file read <path>` | Read file contents | `/file read script.py` |
| `/file edit <path>` | Edit file (AI or manual) | `/file edit app.py` |
| `/file delete <path>` | Delete file (with confirmation) | `/file delete old.txt` |
| `/file list [path]` | List directory contents | `/file list ~/Documents` |
| **Natural commands** | Direct file operations | `create file`, `edit demo.py` |

### App Control (macOS)
| Command | Description | Example |
|---------|-------------|---------|
| `/app open <name>` | Open application | `/app open Safari` |
| `/app close <name>` | Close application | `/app close Chrome` |
| `/app list` | List running applications | `/app list` |
| **Natural commands** | Auto-detection | `open VS Code`, `close Safari` |

### Voice Features
| Command | Description | Example |
|---------|-------------|---------|
| `/listen` | Single voice input | `/listen` |
| `/speak` | Toggle voice output (TTS) | `/speak` |
| `/voicemode` | Hands-free conversation | `/voicemode` |
| `STT on` | Enable persistent voice input | Type or say: `STT on` |
| `STT off` | Disable voice input | Say: `STT off` |
| `TTS on/off` | Toggle voice output | Say: `TTS on` |

### Time, Date & Weather
| Query Pattern | Description | Example |
|---------------|-------------|---------|
| Time queries | Get current time | `what time is it?`, `current time` |
| Date queries | Get current date | `what's the date?`, `today's date` |
| Weather queries | Get weather info | `weather in Mumbai`, `weather` (auto GPS) |
| Location queries | Get GPS location | `where am I?`, `my location` |

## 💡 Usage Examples

### Automatic Search Detection
```bash
You: What happened with the India EU trade deal in 2026?
AI: 🔍 Searching for current information...
    [Automatically searches and provides answer with sources]

You: Latest news on AI developments
AI: 🔍 Searching for current information...
    [Fetches recent news articles and summarizes]
```

### File Operations with AI

```bash
# AI-powered file creation
You: create a file with a Python script to calculate fibonacci
AI: 🤖 Generating content...
    📝 Enter filename: fib.py
    ✅ Created file: /Users/you/Desktop/fib.py

# Edit files with AI
You: edit demo.py
AI: 📝 How to update? [ai/manual]: ai
You: make it print hello world 10 times
AI: 🤖 Generating content...
    ✅ Edited file: demo.py

# Quick file operations
You: read notes.txt
AI: 📄 File: notes.txt
    --- Content ---
    [File contents shown]

You: rename notes.txt to important.txt
AI: ✅ Renamed: notes.txt → important.txt

You: delete old.txt
AI: ⚠️  Delete old.txt? [y/n]: y
    ✅ Deleted file: old.txt
```

### App Control
```bash
# Natural language
You: open Safari
AI: 🚀 Opening Safari...
    ✅ Opened app: Safari

You: launch VS Code
AI: 🚀 Opening VS Code...
    ✅ Opened app: VS Code

You: close Chrome please
AI: 🛑 Closing Chrome...
    ✅ Closed app: Chrome

# Manual commands
You: /app list
AI: 🖥️  Running Applications:
    • Finder
    • Safari
    • Terminal
    Total: 15 apps
```

### Voice Features
```bash
# Enable persistent voice input
You: STT on
AI: 🎤 Voice input enabled - you can now speak instead of type!

You: [Speak] "what's the weather in New York?"
AI: ✅ Heard: what's the weather in New York?
    🌤️ Weather in New York, USA:
    🌡️  Temperature: 15°C / 59°F
    [More weather details...]

# Voice mode (hands-free)
You: /voicemode
AI: 🎤 Voice Mode Activated
    [Say "stop listening" to exit]

You: [Speak] "tell me a joke"
AI: [Responds and speaks the joke aloud]

You: [Speak] "stop listening"
AI: � Voice mode deactivated
```

### Time, Date & Weather
```bash
You: what time is it?
AI: 🕐 Current Time (Asia/Kolkata):
    ⏰ 09:31:52 PM
    🕰️  21:31:52
    📅 Friday, January 31, 2026

You: what's the date?
AI: 📅 Current Date (Asia/Kolkata):
    📆 Friday, January 31, 2026
    📍 Day 31 of 2026
    📊 Week 5 of the year

You: weather in Mumbai
AI: 🌤️ Weather in Mumbai, India:
    🌡️  Temperature: 28°C / 82°F
    ☁️  Condition: Partly cloudy
    💧 Humidity: 65%
    [More details...]

You: where am I?
AI: 📍 Current Location:

    🌍 Coordinates: 19.0760, 72.8777
    🏙️  City: Mumbai, Maharashtra
    🌏 Country: India
    📮 Postal Code: 400001

    📬 Full Address:
    Main Street, Mumbai, Maharashtra 400001, India

You: weather
AI: 📍 Using GPS location: Mumbai
    🌤️ Weather in Mumbai, India:
    [Weather details for your current location...]
```

## 🛠️ Technical Architecture

### Key Components

1. **`main.py`**: Main entry point with command parsing and UI
2. **`ollama_ai.py`**: Ollama AI system with function calling
3. **`tools.py`**: All tool functions (search, files, apps, voice, weather, etc.)

### Technology Stack

- **AI Models**:
  - Groq API (`llama-3.3-70b-versatile`)
  - Ollama (`llama3.2`)
- **Search**: SerpApi (Google Search & News), NewsAPI
- **Voice**: SpeechRecognition + pyttsx3
- **Weather**: wttr.in API
- **UI**: Rich console library

### Dependencies

See [`requirements.txt`](requirements.txt) for full list:
- `groq` - Groq API client
- `ollama` - Ollama local AI
- `requests` - SearchApi.io HTTP client
- `newsapi-python` - News API client
- `SpeechRecognition` - Speech-to-text
- `pyttsx3` - Text-to-speech
- `rich` - Terminal UI
- `requests`, `beautifulsoup4` - Web operations
- `speedtest-cli` - Internet speed testing

## 🎯 Smart Features

### Automatic Detection Triggers

The assistant automatically detects and handles:

**Search Triggers**: `latest`, `recent`, `current`, `2024`, `2025`, `2026`, `news`, `what happened`, `when did`

**File Triggers**: `create file`, `read file`, `edit file`, `delete file`, `rename X to Y`

**App Triggers**: `open <app>`, `launch <app>`, `close <app>`, `quit <app>`

**Time Triggers**: `what time`, `current time`, `time now`

**Date Triggers**: `what date`, `today's date`, `current date`

**Weather Triggers**: `weather`, `temperature`, `forecast`, `how hot`, `how cold`

**Location Triggers**: `where am I`, `my location`, `current location`, `GPS`

**Voice Triggers**: `STT on/off`, `TTS on/off`, `voice mode`, `talk to me`

## 🔧 Configuration

### Environment Variables (`.env`)

```bash
# Required for online mode and auto-search
GROQ_API_KEY=your_groq_api_key_here

# Required for web search and news search
SERPAPI_API_KEY=your_serpapi_key_here

# Optional: for NewsAPI integration (falls back to SerpApi if not set)
NEWSAPI_KEY=your_newsapi_key_here
```

### Models Configuration

Edit `main.py` to change models:

```python
ai = HybridAI(
    groq_model="llama-3.3-70b-versatile",  # Groq model
    ollama_model="llama3.2",               # Ollama model
    enable_tools=True                       # Enable auto-search
)
```

## 📝 Notes

- **Voice Input**: Works both online (Google Speech Recognition) and offline (Vosk)
  - First offline use will auto-download a small model (~40MB)
  - Automatically falls back to offline when internet is unavailable
- **Voice Output**: Works completely offline using pyttsx3
- **File Operations**: Default save location is Desktop (`~/Desktop`)
- **macOS Only**: App control features are macOS-specific (uses AppleScript)
- **Auto-Search**: Only works in online mode (Groq), not available with Ollama

## 🚀 Pro Tips

1. **Voice + AI Code Generation**: Enable STT and ask AI to create code files hands-free!
2. **Natural Language**: Just type naturally - most features auto-detect your intent
3. **Offline Capable**: Works without internet (limited features via Ollama)
4. **Batch Operations**: Chain commands naturally: "create notes.txt then read it"

## 📜 License

This project is open source and available for personal and educational use.

---

**Made with ❤️ using Groq + Ollama + Python**


## Copyright

© 2026 Tharun Naidu. All rights reserved.

Licensed under the MIT License.
