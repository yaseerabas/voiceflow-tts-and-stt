# VoiceFlow Desktop Application

VoiceFlow is a desktop application for voice translation supporting English, Russian, and Kazakh languages. It features speech-to-text, text-to-speech, and translation capabilities powered by AI models.

## Features

- **Speech-to-Text (STT)**: Convert voice to text using OpenAI Whisper
- **Text-to-Speech (TTS)**: Generate speech from text using Kazakh TTS and system voices
- **Translation**: Translate between English, Russian, and Kazakh using NLLB
- **Offline Mode**: All models cached locally for offline use after first download or bundled build
- **Desktop App**: Standalone Windows executable with GUI

## AI Models Used

1. **OpenAI Whisper** (medium) - ~2GB - Speech recognition
2. **Facebook MMS-TTS-Kaz** - ~273MB - Kazakh text-to-speech
3. **NLLB-200-distilled-600M** - ~800MB - Multi-language translation

## Installation & Setup

### Option 1: Run from Source

1. **Install Python 3.8+**

2. **Clone or extract the project**

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the desktop app:**
   ```bash
   python desktop_app.py
   ```

5. **First Launch:**
   - The app will show a download manager
   - Download all three AI models (requires internet)
   - Models will be cached in `%APPDATA%/VoiceFlowApp/models/`
   - After first download, app works fully offline

### Option 2: Use Pre-built .exe

1. **Download VoiceFlow.exe** from releases
2. **Run VoiceFlow.exe**
3. **On first launch**, download models via the GUI (if not bundled)
4. **Use offline** after initial setup

### Option 3: Pre-built Offline Bundle (Recommended for Clients)

1. **Get the bundled build** (includes models)
2. **Run VoiceFlow.exe**
3. **No downloads needed** on first launch

## Building Executable

To create a standalone .exe file:

### Prerequisites

```bash
pip install pyinstaller
```

### Build Steps

1. **Ensure all dependencies are installed:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Build with PyInstaller:**
   ```bash
   pyinstaller desktop.spec
   ```

3. **Output location:**
   ```
   dist/VoiceFlow/VoiceFlow.exe
   ```

4. **Distribute:**
   - Compress the entire `dist/VoiceFlow/` folder as a ZIP
   - Users extract and run `VoiceFlow.exe`
   - Models download on first use (~3GB total)

### Build Configuration

The `desktop.spec` file configures:
- **Single-folder distribution** (recommended for 8GB RAM)
- **No console window** (set `console=True` for debugging)
- **Includes Flask templates and static files**
- **Optimized with UPX compression**
- **Custom icon support** (add `icon.ico` to project root)

## Usage

### Desktop Application

1. **Launch VoiceFlow**
2. **Download models** (first time only)
3. **Select languages** for input/output
4. **Record audio** or **type text**
5. **Get translation** and **listen to speech**

### System Tray

- **Double-click tray icon**: Show/hide window
- **Right-click**: Access menu (Show, Hide, Quit)
- **Runs in background**: Minimize to tray

## Development

### Running in Development Mode

```bash
# Run Flask app directly (for testing backend)
python app.py

# Run desktop app (recommended)
python desktop_app.py
```

### Project Structure

```
VoiceFlow/
├── app.py                  # Flask application
├── desktop_app.py          # PyQt5 desktop wrapper
├── desktop.spec            # PyInstaller configuration
├── requirements.txt        # Python dependencies
├── routes/                 # Flask routes
│   ├── stt_route.py       # Speech-to-text endpoint
│   ├── tts_route.py       # Text-to-speech endpoint
│   └── voice_list.py      # Voice listing endpoint
├── utils/                  # Utilities
│   ├── model_manager.py   # AI model management
│   ├── text_translator.py # Translation utilities
│   ├── kk_speech_model.py # Kazakh TTS utilities
│   └── detect_voice.py    # Voice detection
├── templates/              # HTML templates
│   └── index.html
└── static/                 # CSS and JavaScript
    ├── style.css
    └── script.js
```

## System Requirements

### Minimum

- **OS**: Windows 10/11 (64-bit)
- **CPU**: Intel Core i5 8th gen or equivalent
- **RAM**: 8GB (4GB free for models)
- **Disk**: 5GB free (3GB for models, 2GB for app)
- **Internet**: Required only if models are not bundled

### Recommended

- **RAM**: 16GB (for better performance with all models)
- **CPU**: Intel Core i7 or equivalent
- **SSD**: For faster model loading

## Performance Notes

### Memory Usage on 8GB RAM

- **All models loaded**: ~3GB
- **Windows + Chrome**: ~2GB
- **App overhead**: ~500MB
- **Total**: ~5.5GB (leaves 2.5GB for system)

### Optimization Tips

1. **Close unused apps** before using VoiceFlow
2. **Models load on-demand** - only used features consume memory
3. **Restart app** if memory usage increases over time
4. **Use SSD** for faster model loading

## Troubleshooting

### Models Won't Download

- **Check internet connection**
- **Disable VPN/firewall** temporarily
- **Try downloading individually** instead of "Download All"
- **Check disk space** (need 5GB free)

### App Won't Start

- **Check antivirus** - may block .exe
- **Run as administrator** if permission issues
- **Enable console** (`console=True` in spec) to see errors

### High Memory Usage

- **Close other applications**
- **Restart VoiceFlow**
- **Consider using web version** on low-RAM systems

### Port Already in Use

- The app automatically finds free ports (5000-5009)
- If issues persist, close other Flask/Python apps

## Model Cache Location

Models are stored in:
```
%APPDATA%\VoiceFlowApp\models\
```

Example:
```
C:\Users\YourName\AppData\Roaming\VoiceFlowApp\models\
```

To **reset models**, delete this folder and re-download.

## Building for Distribution

### Steps for Client Deployment

1. **Build the executable:**
   ```bash
   pyinstaller desktop.spec
   ```

2. **Test the build:**
   ```bash
   dist\VoiceFlow\VoiceFlow.exe
   ```

3. **Create installer (optional):**
   - Use Inno Setup or NSIS
   - Include in installer script
   - Auto-create desktop shortcut

4. **Package for distribution:**
   ```bash
   # Compress the folder
   Compress-Archive -Path dist\VoiceFlow -DestinationPath VoiceFlow-v1.0.zip
   ```

5. **Send to client:**
   - Upload to cloud storage or email
   - No internet required if bundled models are included

## License

[Specify your license here]

## Support

For issues or questions:
- Open an issue on GitHub
- Contact: [your-email@example.com]

## Credits

- **OpenAI Whisper**: Speech recognition
- **Meta AI**: Kazakh TTS model
- **NLLB Team**: Translation model
- **PyQt5**: Desktop GUI framework
- **Flask**: Web framework
