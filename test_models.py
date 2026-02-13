"""
Test script to verify model manager functionality
Run this to test model download and caching without full desktop app
"""

from utils.model_manager import get_model_manager

def test_model_manager():
    """Test model manager functionality"""
    print("=" * 60)
    print("VoiceFlow Model Manager Test")
    print("=" * 60)
    
    # Get model manager instance
    manager = get_model_manager()
    
    print(f"\n✓ Model Manager initialized")
    print(f"  Cache directory: {manager.cache_dir}")
    
    # Check download status
    print("\n" + "=" * 60)
    print("Checking Model Download Status")
    print("=" * 60)
    
    status = manager.get_download_status()
    
    for model_key, info in status.items():
        print(f"\n{info['name']}:")
        print(f"  Model ID: {info['model_id']}")
        print(f"  Size: {info['size']}")
        print(f"  Downloaded: {'✓ Yes' if info['downloaded'] else '✗ No'}")
    
    # Count downloaded models
    downloaded_count = sum(1 for s in status.values() if s['downloaded'])
    total_count = len(status)
    
    print("\n" + "=" * 60)
    print(f"Summary: {downloaded_count}/{total_count} models downloaded")
    print("=" * 60)
    
    if downloaded_count == total_count:
        print("\n✓ All models are ready!")
        print("  You can run the desktop app: python desktop_app.py")
    else:
        print("\n⚠ Some models are missing")
        print("  Run desktop_app.py to download them via GUI")
        print("  Or download manually:")
        
        for model_key, info in status.items():
            if not info['downloaded']:
                print(f"\n  To download {info['name']}:")
                print(f"    manager.download_model('{model_key}')")
    
    return status


def test_download_single_model(model_key='translator'):
    """
    Test downloading a single model (smallest one for testing)
    WARNING: This will download ~800MB!
    """
    print("\n" + "=" * 60)
    print(f"Testing Single Model Download: {model_key}")
    print("=" * 60)
    
    manager = get_model_manager()
    
    # Check if already downloaded
    if manager.is_model_downloaded(model_key):
        print(f"\n✓ {model_key} is already downloaded!")
        return True
    
    print(f"\nStarting download of {model_key}...")
    print("This may take several minutes depending on your connection.")
    print("Press Ctrl+C to cancel\n")
    
    def progress_callback(current, total, message):
        """Print progress updates"""
        if total > 0:
            percent = int((current / total) * 100)
            print(f"\r[{'=' * (percent // 2)}{' ' * (50 - percent // 2)}] {percent}% - {message}", end='')
        else:
            print(f"\r{message}", end='')
    
    try:
        success = manager.download_model(model_key, progress_callback)
        print()  # New line after progress
        
        if success:
            print(f"\n✓ Successfully downloaded {model_key}!")
            return True
        else:
            print(f"\n✗ Failed to download {model_key}")
            return False
    except KeyboardInterrupt:
        print("\n\n⚠ Download cancelled by user")
        return False
    except Exception as e:
        print(f"\n✗ Error during download: {e}")
        return False


def test_model_loading():
    """Test loading models (only if downloaded)"""
    print("\n" + "=" * 60)
    print("Testing Model Loading")
    print("=" * 60)
    
    manager = get_model_manager()
    status = manager.get_download_status()
    
    # Test Whisper
    if status['whisper']['downloaded']:
        print("\nTesting Whisper model loading...")
        try:
            model = manager.load_whisper_model()
            print("  ✓ Whisper model loaded successfully")
            manager.unload_model('whisper')
            print("  ✓ Whisper model unloaded")
        except Exception as e:
            print(f"  ✗ Error loading Whisper: {e}")
    else:
        print("\n⚠ Whisper not downloaded, skipping load test")
    
    # Test Kazakh TTS
    if status['kazakh_tts']['downloaded']:
        print("\nTesting Kazakh TTS model loading...")
        try:
            model = manager.load_kazakh_tts_model()
            print("  ✓ Kazakh TTS model loaded successfully")
            print(f"  ✓ Model type: {type(model['model'])}")
            print(f"  ✓ Tokenizer type: {type(model['tokenizer'])}")
            manager.unload_model('kazakh_tts')
            print("  ✓ Kazakh TTS model unloaded")
        except Exception as e:
            print(f"  ✗ Error loading Kazakh TTS: {e}")
    else:
        print("\n⚠ Kazakh TTS not downloaded, skipping load test")
    
    # Test Translator
    if status['translator']['downloaded']:
        print("\nTesting Translator model loading...")
        try:
            model = manager.load_translator_model()
            print("  ✓ Translator model loaded successfully")
            print(f"  ✓ Model type: {type(model)}")
            manager.unload_model('translator')
            print("  ✓ Translator model unloaded")
        except Exception as e:
            print(f"  ✗ Error loading Translator: {e}")
    else:
        print("\n⚠ Translator not downloaded, skipping load test")


if __name__ == '__main__':
    import sys
    
    print("\n" + "=" * 60)
    print("VoiceFlow Model Manager Test Suite")
    print("=" * 60)
    
    # Test 1: Check status
    status = test_model_manager()
    
    # Test 2: Offer to download if missing
    all_downloaded = all(s['downloaded'] for s in status.values())
    
    if not all_downloaded:
        print("\n" + "=" * 60)
        print("Download Options")
        print("=" * 60)
        print("\n1. Test download of smallest model (translator ~800MB)")
        print("2. Skip and test only downloaded models")
        print("3. Exit and use desktop app GUI instead")
        
        choice = input("\nEnter choice (1/2/3): ").strip()
        
        if choice == '1':
            test_download_single_model('translator')
        elif choice == '2':
            pass  # Continue to loading test
        else:
            print("\nℹ Use 'python desktop_app.py' to download via GUI")
            sys.exit(0)
    
    # Test 3: Try loading models
    print("\n" + "=" * 60)
    proceed = input("\nTest model loading? (downloads may occur) [y/N]: ").strip().lower()
    
    if proceed == 'y':
        test_model_loading()
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Run desktop app: python desktop_app.py")
    print("  2. Build executable: pyinstaller desktop.spec")
    print("  3. Check documentation: README_DESKTOP.md")
    print()
