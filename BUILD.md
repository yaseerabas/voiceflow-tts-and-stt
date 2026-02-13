# Build Instructions for VoiceFlow Desktop

## Prerequisites

1. **Python 3.8 or higher** installed
2. **Git** (optional, for cloning)
3. **Windows 10/11** (64-bit)

## Step-by-Step Build Process

### 1. Setup Environment

```bash
# Navigate to project directory
cd "c:\Users\yasir\OneDrive\Desktop\VoiceFlow-Jawad---TTS---STT-Disable-person-"

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip
```

### 2. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

**This will install:**
- Flask and web dependencies
- OpenAI Whisper (STT)
- Transformers and PyTorch (AI models)
- PyQt5 (Desktop GUI)
- PyInstaller (Executable builder)

**Installation time:** ~5-10 minutes depending on internet speed

### 3. Test the Application

```bash
# Test desktop app before building
python desktop_app.py
```

**What to expect:**
- Download manager window opens
- You can skip downloads for testing
- Flask server starts in background
- Web interface opens in PyQt5 window

**Close the app** (File → Quit or System Tray → Quit)

### 4. Build the Executable

```bash
# Build using the spec file
pyinstaller desktop.spec
```

### 4.1 Bundle Models for Offline Build (Optional)

If you want a client-ready offline build, copy the already-downloaded models into
`bundled_models` before running PyInstaller. The app will copy these into the
normal cache on first run.

**Expected structure:**
```
bundled_models/
  whisper/
    medium.pt
  huggingface/
    models--facebook--mms-tts-kaz/
    models--Emilio407--nllb-200-distilled-600M-8bit/
```

**Copy from your local cache (example):**
```
C:\Users\YourName\AppData\Roaming\VoiceFlowApp\models\whisper
C:\Users\YourName\AppData\Roaming\VoiceFlowApp\models\huggingface
```

**Build process:**
- Analyzes dependencies
- Collects all files
- Bundles Python runtime
- Creates executable
- **Time:** ~2-5 minutes

**Output location:**
```
dist/VoiceFlow/VoiceFlow.exe
```

### 5. Test the Executable

```bash
# Navigate to build folder
cd dist\VoiceFlow

# Run the executable
.\VoiceFlow.exe
```

**Verify:**
- ✅ App launches without errors
- ✅ Download manager appears
- ✅ Can download models
- ✅ Flask server starts
- ✅ Web interface loads
- ✅ System tray icon works

### 6. Package for Distribution

```bash
# Return to project root
cd ..\..

# Create ZIP file (PowerShell)
Compress-Archive -Path dist\VoiceFlow -DestinationPath VoiceFlow-v1.0-Windows.zip -Force
```

**Result:**
- `VoiceFlow-v1.0-Windows.zip` (size depends on bundled models)
- Ready to send to client

## Build Options

### Debug Build (with console)

Edit `desktop.spec`, change:
```python
console=False,  # Change to True
```

Rebuild:
```bash
pyinstaller desktop.spec
```

**Use for:**
- Debugging issues
- Seeing error messages
- Development testing

### Release Build (no console)

Keep `console=False` in `desktop.spec`

**Use for:**
- Production deployment
- Client distribution
- Professional appearance

## Advanced Configuration

### Custom Icon

1. **Create or download** an `.ico` file (256x256 recommended)
2. **Save as** `icon.ico` in project root
3. **Rebuild:**
   ```bash
   pyinstaller desktop.spec
   ```

The spec file automatically includes icon if present.

### Reducing Build Size

Edit `desktop.spec` and add to `excludes`:
```python
excludes=[
    'matplotlib',
    'pandas',
    'numpy.distutils',
    'setuptools',
    'pip',
    'tkinter',  # If not using
],
```

### One-File Build (Not Recommended for 8GB RAM)

Create new spec: `desktop_onefile.spec`
```python
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,    # Add these
    a.zipfiles,    # Add these
    a.datas,       # Add these
    [],
    name='VoiceFlow',
    # ... other options
    onefile=True,  # Add this
)

# Remove COLLECT section
```

**Pros:**
- Single .exe file
- Easier distribution

**Cons:**
- Slower startup (extracts to temp)
- Higher memory usage during extraction
- Not recommended for 8GB RAM systems

## Troubleshooting Build Issues

### ImportError during build

**Solution:** Add missing module to `hiddenimports` in `desktop.spec`:
```python
hiddenimports=[
    'your_missing_module',
],
```

### Templates/Static not included

**Solution:** Check `datas` in `desktop.spec`:
```python
datas=[
    ('templates', 'templates'),
    ('static', 'static'),
],
```

### PyQt5 WebEngine missing

**Solution:**
```bash
pip install PyQtWebEngine==5.15.6
pyinstaller desktop.spec
```

### Build is too large (>500MB)

**Solutions:**
1. Add more modules to `excludes`
2. Use `upx=True` for compression (already enabled)
3. Remove unused dependencies from requirements.txt

### "Python.dll not found" error

**Solution:** Ensure virtual environment is activated:
```bash
venv\Scripts\activate
pyinstaller desktop.spec
```

## Clean Build (Start Fresh)

```bash
# Remove previous build artifacts
rmdir /s build
rmdir /s dist
del desktop.spec.lock

# Rebuild
pyinstaller desktop.spec
```

## CI/CD Build (Automated)

### GitHub Actions Example

Create `.github/workflows/build.yml`:
```yaml
name: Build VoiceFlow

on: [push, pull_request]

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Build executable
      run: |
        pyinstaller desktop.spec
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: VoiceFlow-Windows
        path: dist/VoiceFlow/
```

## Distribution Checklist

Before sending to client:

- [ ] Build with `console=False`
- [ ] Test executable on clean Windows system
- [ ] Verify all models download correctly
- [ ] Check memory usage on 8GB RAM
- [ ] Include README_DESKTOP.md in ZIP
- [ ] Include QUICKSTART.md for easy setup
- [ ] Test on Windows 10 and 11
- [ ] Verify antivirus doesn't block (test with Windows Defender)
- [ ] Create release notes with version info
- [ ] Add support contact information

## File Sizes

Expected sizes:

| Item | Size |
|------|------|
| Executable (.exe) | ~50-80MB |
| Total build folder | ~150-250MB |
| Distribution ZIP | ~100-200MB |
| With models downloaded | ~3.2GB total |

## Build Time Estimates

On typical development machine:

| Step | Time |
|------|------|
| Install dependencies | 5-10 min |
| First PyInstaller build | 2-5 min |
| Subsequent builds | 1-2 min |
| Testing | 2-5 min |
| Creating ZIP | 1 min |
| **Total** | **11-23 min** |

## Next Steps After Build

1. **Test on client's system** (if possible)
2. **Create installer** using Inno Setup (optional)
3. **Code sign** the executable (recommended for production)
4. **Create auto-updater** for future versions
5. **Set up crash reporting** (e.g., Sentry)

## Support

For build issues:
- Check PyInstaller documentation: https://pyinstaller.org
- Review logs in `build/` folder
- Test with `console=True` to see errors
- Verify all dependencies install correctly

## Building Different Versions

### Development Build
```bash
# Set console=True in spec
pyinstaller desktop.spec
# Output: dist/VoiceFlow/VoiceFlow.exe (with console)
```

### Production Build
```bash
# Set console=False in spec
pyinstaller desktop.spec
# Output: dist/VoiceFlow/VoiceFlow.exe (no console)
```

### Portable Build
```bash
# Same as production, but add version info
# Include all documentation files in dist folder
pyinstaller desktop.spec
copy README_DESKTOP.md dist\VoiceFlow\
copy QUICKSTART.md dist\VoiceFlow\
```

---

**Ready to build?** Run:
```bash
pip install -r requirements.txt
pyinstaller desktop.spec
```

**Questions?** Check QUICKSTART.md or README_DESKTOP.md for more info.
