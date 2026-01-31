#!/bin/bash
# Setup script for Vosk offline voice recognition model

echo "🎤 Setting up offline voice recognition..."
echo ""

# Create directory
echo "📁 Creating model directory..."
mkdir -p ~/.vosk/models
cd ~/.vosk/models

# Check if model already exists
if [ -d "vosk-model-small-en-us-0.15" ]; then
    echo "✅ Model already installed!"
    echo "📍 Location: ~/.vosk/models/vosk-model-small-en-us-0.15"
    exit 0
fi

# Download model
echo "📦 Downloading Vosk model (~40MB)..."
echo "🌐 URL: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
echo ""

if command -v curl &> /dev/null; then
    curl -L -O https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
elif command -v wget &> /dev/null; then
    wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
else
    echo "❌ Error: Neither curl nor wget found. Please install one of them."
    exit 1
fi

# Check if download succeeded
if [ ! -f "vosk-model-small-en-us-0.15.zip" ]; then
    echo "❌ Download failed. Please check your internet connection."
    echo ""
    echo "Manual download:"
    echo "1. Download: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    echo "2. Extract to: ~/.vosk/models/"
    exit 1
fi

# Extract
echo ""
echo "📂 Extracting model..."
unzip -q vosk-model-small-en-us-0.15.zip

# Clean up
echo "🧹 Cleaning up..."
rm vosk-model-small-en-us-0.15.zip

# Verify
if [ -d "vosk-model-small-en-us-0.15" ]; then
    echo ""
    echo "✅ Success! Offline voice recognition is ready!"
    echo "📍 Model installed at: ~/.vosk/models/vosk-model-small-en-us-0.15"
    echo ""
    echo "🎤 You can now use voice commands offline!"
    echo "   Just restart your AI assistant and say 'STT on'"
else
    echo "❌ Extraction failed. Please try again."
    exit 1
fi
