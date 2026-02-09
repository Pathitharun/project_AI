# 🤖 ELLI - AI Assistant

**ELLI** (Everyday Lightweight Learning Intelligence) is a smart AI assistant with web search, GPS location, voice control, and file management.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Add API keys to .env file
GROQ_API_KEY=your_key
SERPAPI_API_KEY=your_key
NEWSAPI_KEY=your_key  # Optional

# Run
python main.py
```

### Prerequisites
- Python 3.8+
- [Ollama](https://ollama.ai) with `llama3.2` model
- Groq API key

## ✨ Features

- 🌐 **Hybrid AI**: Auto-switches between Groq (online) and Ollama (offline)
- 🔍 **Smart Search**: Automatically searches the web when needed
- � **GPS Location**: Get your current location (macOS only)
- 🌤️ **Weather**: Real-time weather with GPS auto-detection
- 🎤 **Voice**: Speak to AI and hear responses
- 📁 **File Operations**: Create, edit, delete files
- 🖥️ **App Control**: Open/close apps (macOS)
- 🧠 **Memory**: Remembers preferences and information

## 💬 How to Use

Just chat naturally! ELLI automatically detects what you need:

```
You: what's the weather?
You: where am I?
You: latest news on AI
You: create a Python script
You: open Safari
```

### Quick Commands

| Command | Description |
|---------|-------------|
| `/help` | Show all commands |
| `/search <query>` | Web search |
| `/news <topic>` | Latest news |
| `/file create <name>` | Create file |
| `/quit` | Exit |

## 🎤 Voice Mode

```
You: voice mode
[Speak]: what's the weather?
[Speak]: stop listening
```

## 📝 Memory

ELLI remembers information about you in `memory.md`. You can:
- Let AI save information automatically
- Edit `memory.md` manually

## 🛠️ Technical Details

**Files:**
- `main.py` - Main entry point
- `ollama_ai.py` - AI with function calling
- `tools.py` - All tool functions
- `memory.md` - Persistent memory

**Tools:** Web search, news, GPS location, weather, file ops, app control, memory management

## 📍 GPS Location (macOS)

First run requires permission:
1. System Settings → Privacy & Security → Location Services
2. Enable for Terminal/CoreLocationCLI

## � License

Copyright © 2026 Pathitharun. All rights reserved.

---

**Made with ❤️ by Tharun**
