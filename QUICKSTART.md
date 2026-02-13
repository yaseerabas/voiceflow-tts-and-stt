# Quick Start Guide - VoiceFlow Desktop

## For End Users

### First Time Setup

1. **Download and Extract**
   - Extract `VoiceFlow.zip` to a folder (e.g., `C:\VoiceFlow\`)

2. **Run the Application**
   - Double-click `VoiceFlow.exe`

3. **Download AI Models (One-Time)**
   - On first launch, you'll see a download window
   - Click "Download All Models" button
   - Wait ~10-20 minutes (downloading 3GB)
   - Requires internet connection only for this step

4. **Use the App**
   - After download, click "Continue to App"
   - The app now works fully offline!

### Daily Use

- **Just run `VoiceFlow.exe`** - models are already cached
- **Minimize to system tray** - app keeps running in background
- **No internet needed** - all processing is local

---

## For Developers

### Testing the Desktop App

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run desktop app:**
   ```bash
   python desktop_app.py
   ```

3. **First run will show download manager:**
   - Download models or skip for testing
   - Models cache to `%APPDATA%\VoiceFlowApp\models\`

### Building the Executable

1. **Ensure PyInstaller is installed:**
   ```bash
   pip install pyinstaller
   ```

2. **Build:**
   ```bash
   pyinstaller desktop.spec
   ```

3. **Test the build:**
   ```bash
   cd dist\VoiceFlow
   VoiceFlow.exe
   ```

4. **Distribute:**
   ```bash
   # Create ZIP for distribution
   Compress-Archive -Path dist\VoiceFlow -DestinationPath VoiceFlow-v1.0.zip
   ```

### Build Output

```
dist/
  VoiceFlow/              # Distribute this entire folder
    VoiceFlow.exe         # Main executable
    templates/            # Flask templates
    static/               # CSS/JS files
    _internal/            # Python runtime and dependencies
    [various DLLs]
```

### Debugging

**If build fails:**
- Set `console=True` in `desktop.spec` to see errors
- Check that all imports work: `python desktop_app.py`

**If models won't download:**
- Check internet connection
- Try downloading individually in the GUI
- Check `%APPDATA%\VoiceFlowApp\models\` for partial downloads

**Memory issues on 8GB RAM:**
- Close other applications
- Consider building with single-file mode (slower but uses less RAM at runtime)

### Build Configuration

Edit `desktop.spec` to customize:
- `console=False` → Set to `True` for debugging
- `icon='icon.ico'` → Add custom icon
- `name='VoiceFlow'` → Change app name
- `upx=True` → Compression (makes .exe smaller)

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | Windows 10 64-bit | Windows 11 |
| CPU | Intel Core i5 8th Gen | Core i7+ |
| RAM | 8GB | 16GB |
| Storage | 5GB free | 10GB+ SSD |
| Internet | First download only | Not required |

---

## Folder Structure After Build

```
VoiceFlow/
├── VoiceFlow.exe              # Main application
├── templates/                 # HTML files
│   └── index.html
├── static/                    # Frontend assets
│   ├── style.css
│   └── script.js
└── _internal/                 # Python runtime (don't modify)
    ├── Python DLLs
    ├── PyQt5 libraries
    └── Other dependencies
```

---

## Troubleshooting

### "Windows protected your PC" warning
- Click "More info" → "Run anyway"
- This is normal for unsigned executables
- Consider code signing for production

### Antivirus blocking .exe
- Add exception for VoiceFlow.exe
- PyInstaller executables may trigger false positives

### Port 5000 already in use
- App automatically finds free port (5000-5009)
- Close other Flask/development servers

### High CPU usage during first use
- Normal during model download/loading
- CPU usage drops after models are loaded

---

## Model Cache Location

Models download to:
```
C:\Users\<YourName>\AppData\Roaming\VoiceFlowApp\models\
```

**To reset:**
1. Close VoiceFlow
2. Delete the `VoiceFlowApp` folder
3. Restart and re-download

**To backup models:**
- Copy the `VoiceFlowApp` folder to external drive
- Restore by copying back to `%APPDATA%`

---

## Tips for Low-RAM Systems (8GB)

1. **Close unnecessary programs** before launching
2. **Download models one at a time** instead of "Download All"
3. **Restart VoiceFlow** if it becomes slow
4. **Use built-in Task Manager** to monitor RAM usage

---

## Next Steps

- ✅ Basic desktop app with model downloads
- 🔄 Add progress bars with actual download percentage
- 🔄 Implement model auto-updates
- 🔄 Add settings panel (change model cache location)
- 🔄 Create proper installer with Inno Setup
- 🔄 Add automatic startup option
- 🔄 Implement crash reporting
