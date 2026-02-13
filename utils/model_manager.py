"""
Model Manager for VoiceFlow Desktop App
Handles downloading, caching, and loading of AI models with progress tracking
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional, Callable
import threading


class ModelManager:
    """Manages AI model downloads and caching for offline use"""
    
    # Model configurations
    MODELS = {
        'whisper': {
            'name': 'OpenAI Whisper',
            'size': '2GB',
            'size_bytes': 2_000_000_000,
            'model_id': 'medium',
            'type': 'whisper'
        },
        'kazakh_tts': {
            'name': 'Kazakh TTS',
            'size': '273MB',
            'size_bytes': 273_000_000,
            'model_id': 'facebook/mms-tts-kaz',
            'type': 'huggingface'
        },
        'translator': {
            'name': 'NLLB Translator',
            'size': '800MB',
            'size_bytes': 800_000_000,
            'model_id': 'Emilio407/nllb-200-distilled-600M-8bit',
            'type': 'huggingface'
        }
    }
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize ModelManager
        
        Args:
            cache_dir: Custom cache directory. If None, uses %APPDATA%/VoiceFlowApp/models
        """
        if cache_dir is None:
            # Use Windows AppData for model storage
            appdata = os.getenv('APPDATA', os.path.expanduser('~'))
            cache_dir = os.path.join(appdata, 'VoiceFlowApp', 'models')
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Set environment variables for HuggingFace and Whisper
        self._setup_cache_paths()
        
        # Track loaded models
        self._loaded_models = {}
        self._download_locks = {}
    
    def _setup_cache_paths(self):
        """Configure cache paths for model libraries"""
        # HuggingFace cache
        hf_cache = str(self.cache_dir / 'huggingface')
        os.environ['TRANSFORMERS_CACHE'] = hf_cache
        os.environ['HF_HOME'] = hf_cache
        os.environ['HF_DATASETS_CACHE'] = hf_cache
        
        # Whisper cache
        whisper_cache = str(self.cache_dir / 'whisper')
        os.environ['WHISPER_CACHE'] = whisper_cache
        Path(whisper_cache).mkdir(parents=True, exist_ok=True)

    def _get_app_root(self) -> Path:
        """Resolve app root for bundled assets"""
        if getattr(sys, 'frozen', False):
            return Path(getattr(sys, '_MEIPASS', Path(sys.argv[0]).resolve().parent))
        return Path(__file__).resolve().parents[1]

    def get_bundled_models_dir(self) -> Path:
        """Return bundled models directory path"""
        return self._get_app_root() / 'bundled_models'

    def has_bundled_models(self) -> bool:
        """Check if bundled models are present in the app directory"""
        bundled_dir = self.get_bundled_models_dir()
        return (bundled_dir / 'whisper').exists() or (bundled_dir / 'huggingface').exists()

    def _copy_dir_contents(self, src: Path, dst: Path):
        """Copy directory contents while keeping existing files"""
        if not src.exists():
            return
        dst.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            target = dst / item.name
            if item.is_dir():
                shutil.copytree(item, target, dirs_exist_ok=True)
            else:
                shutil.copy2(item, target)

    def bootstrap_bundled_models(self) -> bool:
        """Copy bundled models into cache when missing"""
        bundled_dir = self.get_bundled_models_dir().resolve()
        if not bundled_dir.exists():
            return False

        copied_any = False

        whisper_src = bundled_dir / 'whisper'
        if not self._check_whisper_model() and whisper_src.exists():
            try:
                self._copy_dir_contents(whisper_src, self.cache_dir / 'whisper')
                copied_any = True
            except OSError as exc:
                print(f"Failed to copy bundled Whisper model: {exc}")

        hf_src = bundled_dir / 'huggingface'
        need_hf = (
            not self._check_huggingface_model(self.MODELS['kazakh_tts']['model_id'])
            or not self._check_huggingface_model(self.MODELS['translator']['model_id'])
        )
        if need_hf and hf_src.exists():
            try:
                self._copy_dir_contents(hf_src, self.cache_dir / 'huggingface')
                copied_any = True
            except OSError as exc:
                print(f"Failed to copy bundled HuggingFace models: {exc}")

        return copied_any
    
    def is_model_downloaded(self, model_key: str) -> bool:
        """
        Check if a model is already downloaded
        
        Args:
            model_key: One of 'whisper', 'kazakh_tts', 'translator'
        
        Returns:
            True if model exists in cache
        """
        if model_key not in self.MODELS:
            raise ValueError(f"Unknown model: {model_key}")
        
        model_info = self.MODELS[model_key]
        
        if model_info['type'] == 'whisper':
            return self._check_whisper_model()
        elif model_info['type'] == 'huggingface':
            return self._check_huggingface_model(model_info['model_id'])
        
        return False
    
    def _check_whisper_model(self) -> bool:
        """Check if Whisper medium model exists"""
        whisper_cache = Path(os.environ.get('WHISPER_CACHE', ''))
        if not whisper_cache.exists():
            return False
        
        # Whisper saves models as medium.pt
        model_file = whisper_cache / 'medium.pt'
        return model_file.exists() and model_file.stat().st_size > 1_000_000_000  # > 1GB
    
    def _check_huggingface_model(self, model_id: str) -> bool:
        """Check if HuggingFace model exists in cache"""
        hf_cache = Path(os.environ.get('TRANSFORMERS_CACHE', ''))
        if not hf_cache.exists():
            return False
        
        # HuggingFace uses hash-based folders, check if any model files exist
        model_folders = list(hf_cache.glob('models--*'))
        
        # Convert model_id to folder format: facebook/mms-tts-kaz -> models--facebook--mms-tts-kaz
        normalized_id = model_id.replace('/', '--')
        expected_folder = f'models--{normalized_id}'
        
        for folder in model_folders:
            if expected_folder in str(folder):
                # Check if snapshots exist
                snapshots = folder / 'snapshots'
                if snapshots.exists() and any(snapshots.iterdir()):
                    return True
        
        return False
    
    def get_download_status(self) -> dict:
        """
        Get download status of all models
        
        Returns:
            Dict with model status: {model_key: {'downloaded': bool, 'name': str, 'size': str}}
        """
        status = {}
        for key, info in self.MODELS.items():
            status[key] = {
                'downloaded': self.is_model_downloaded(key),
                'name': info['name'],
                'size': info['size'],
                'model_id': info['model_id']
            }
        return status
    
    def download_model(self, model_key: str, progress_callback: Optional[Callable] = None) -> bool:
        """
        Download a model with progress tracking
        
        Args:
            model_key: One of 'whisper', 'kazakh_tts', 'translator'
            progress_callback: Optional callback function(current, total, status_msg)
        
        Returns:
            True if download successful
        """
        if model_key not in self.MODELS:
            raise ValueError(f"Unknown model: {model_key}")

        if self.is_model_downloaded(model_key):
            if progress_callback:
                progress_callback(100, 100, "Model already available")
            return True

        if self.bootstrap_bundled_models() and self.is_model_downloaded(model_key):
            if progress_callback:
                progress_callback(100, 100, "Using bundled model")
            return True
        
        # Prevent concurrent downloads of same model
        if model_key not in self._download_locks:
            self._download_locks[model_key] = threading.Lock()
        
        if not self._download_locks[model_key].acquire(blocking=False):
            if progress_callback:
                progress_callback(0, 100, "Download already in progress")
            return False
        
        try:
            model_info = self.MODELS[model_key]
            
            if progress_callback:
                progress_callback(0, 100, f"Starting download of {model_info['name']}...")
            
            if model_info['type'] == 'whisper':
                return self._download_whisper(progress_callback)
            elif model_info['type'] == 'huggingface':
                return self._download_huggingface(model_info['model_id'], progress_callback)
            
            return False
        finally:
            self._download_locks[model_key].release()
    
    def _download_whisper(self, progress_callback: Optional[Callable] = None) -> bool:
        """Download Whisper model"""
        try:
            import whisper
            from whisper import _download
            
            if progress_callback:
                progress_callback(10, 100, "Downloading Whisper model...")
            
            # Download with custom progress tracking
            whisper_cache = os.environ.get('WHISPER_CACHE')
            model = whisper.load_model("medium", download_root=whisper_cache)
            
            if progress_callback:
                progress_callback(100, 100, "Whisper model downloaded successfully")
            
            return True
        except Exception as e:
            if progress_callback:
                progress_callback(0, 100, f"Error downloading Whisper: {str(e)}")
            print(f"Error downloading Whisper model: {e}")
            return False
    
    def _download_huggingface(self, model_id: str, progress_callback: Optional[Callable] = None) -> bool:
        """Download HuggingFace model with progress tracking"""
        try:
            from huggingface_hub import snapshot_download
            
            if progress_callback:
                progress_callback(10, 100, f"Downloading {model_id}...")
            
            # Download model files
            snapshot_download(
                repo_id=model_id,
                cache_dir=os.environ.get('TRANSFORMERS_CACHE'),
                resume_download=True,
                local_files_only=False
            )
            
            if progress_callback:
                progress_callback(100, 100, f"{model_id} downloaded successfully")
            
            return True
        except Exception as e:
            if progress_callback:
                progress_callback(0, 100, f"Error downloading {model_id}: {str(e)}")
            print(f"Error downloading {model_id}: {e}")
            return False
    
    def load_whisper_model(self):
        """Load Whisper model (downloads if not cached)"""
        if 'whisper' in self._loaded_models:
            return self._loaded_models['whisper']
        
        try:
            import whisper
            
            print("Loading Whisper model...")
            whisper_cache = os.environ.get('WHISPER_CACHE')
            model = whisper.load_model("medium", download_root=whisper_cache)
            
            self._loaded_models['whisper'] = model
            print("✔ Whisper model loaded successfully")
            return model
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            raise
    
    def load_kazakh_tts_model(self):
        """Load Kazakh TTS model (downloads if not cached)"""
        if 'kazakh_tts' in self._loaded_models:
            return self._loaded_models['kazakh_tts']
        
        try:
            from transformers import VitsModel, AutoTokenizer
            
            print("Loading Kazakh TTS model...")
            model_id = self.MODELS['kazakh_tts']['model_id']
            
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            model = VitsModel.from_pretrained(model_id)
            
            self._loaded_models['kazakh_tts'] = {
                'model': model,
                'tokenizer': tokenizer
            }
            
            print("✔ Kazakh TTS model loaded successfully")
            return self._loaded_models['kazakh_tts']
        except Exception as e:
            print(f"Error loading Kazakh TTS model: {e}")
            raise
    
    def load_translator_model(self):
        """Load translation model (downloads if not cached)"""
        if 'translator' in self._loaded_models:
            return self._loaded_models['translator']
        
        try:
            from transformers import pipeline
            
            print("Loading translation model...")
            model_id = self.MODELS['translator']['model_id']
            
            translator = pipeline("translation", model=model_id)
            
            self._loaded_models['translator'] = translator
            print("✔ Translation model loaded successfully")
            return translator
        except Exception as e:
            print(f"Error loading translation model: {e}")
            raise
    
    def unload_model(self, model_key: str):
        """Unload a model from memory"""
        if model_key in self._loaded_models:
            del self._loaded_models[model_key]
            print(f"✔ {model_key} model unloaded from memory")
    
    def unload_all_models(self):
        """Unload all models from memory"""
        self._loaded_models.clear()
        print("✔ All models unloaded from memory")


# Global instance
_model_manager = None

def get_model_manager() -> ModelManager:
    """Get or create global ModelManager instance"""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager
