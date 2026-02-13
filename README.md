# Offline TTS & STT Flask Application

A complete offline Flask web application that provides Text-to-Speech and Speech-to-Text functionality without requiring internet connection.

## Features

- **Text to Speech**: Convert text to speech using offline TTS engine
- **Speech to Text**: Real-time microphone recording and speech recognition
- **Offline Operation**: Works completely offline, no internet required
- **Multi-language Support**: English, Russian, Kazakh
- **Clean UI**: Simple single-page interface with mode switching
- **Real-time Recording**: Uses browser's MediaRecorder API for microphone access

## Requirements

- Python 3.7+
- Microphone access for Speech-to-Text
- Modern web browser with MediaRecorder API support

## Installation

1. **Clone or download the project**
   ```
   cd jawad-tts-to-stt-project
   ```

2. **Install Python dependencies**
   ```
   pip install -r requirements.txt
   ```

3. **Install system dependencies & Download Vosk models**
   ```
   # Install Vosk
   pip install vosk
   
   # Download language models (choose one or more):
   # English (22MB)
   wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
   unzip vosk-model-small-en-us-0.15.zip
   
   # Russian (42MB) 
   wget https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip
   unzip vosk-model-small-ru-0.22.zip
   
   # Or use larger models for better accuracy
   ```

## Usage

1. **Start the application**
   ```
   python app.py
   ```

2. **Open your browser**
   ```
   http://127.0.0.1:5000
   ```

3. **Use the application**
   - Click "Text to Speech" or "Speech to Text" buttons to switch modes
   - For TTS: Enter text, select language, click "Speak"
   - For STT: Select language, click "Start Recording", speak, then "Stop Recording"

## Troubleshooting

- **Microphone not working**: Ensure browser has microphone permissions
- **TTS not working**: Check if system has TTS voices installed
- **Vosk models missing**: Download required language models from https://alphacephei.com/vosk/models/
- **Speech recognition accuracy**: Speak clearly and ensure quiet environment

## Project Structure

```
jawad-tts-to-stt-project/
├── app.py              # Main Flask application
├── templates/
│   └── index.html      # HTML template
├── static/
│   ├── style.css       # CSS styles
│   └── script.js       # JavaScript functionality
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Technical Details

- **Backend**: Flask with pyttsx3 and Vosk
- **Frontend**: HTML5, CSS3, JavaScript with MediaRecorder API
- **TTS Engine**: pyttsx3 (offline)
- **STT Engine**: Vosk (offline)
- **Audio Processing**: Browser's MediaRecorder API

## Limitations

- Speech recognition accuracy depends on microphone quality and environment
- Language support limited to English, Russian, and Kazakh
- TTS voice quality depends on system's installed voices
- Requires modern browser for microphone access