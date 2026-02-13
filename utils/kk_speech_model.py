from utils.model_manager import get_model_manager


kazakh_tts_model = None
kazakh_tts_tokenizer = None

def init_kk_tokenizer():
    """Get Kazakh TTS tokenizer from ModelManager"""
    global kazakh_tts_tokenizer

    if not kazakh_tts_tokenizer:
        manager = get_model_manager()
        loaded = manager.load_kazakh_tts_model()
        kazakh_tts_tokenizer = loaded['tokenizer']
    
    return kazakh_tts_tokenizer

def init_kk_model():
    """Get Kazakh TTS model from ModelManager"""
    global kazakh_tts_model

    if not kazakh_tts_model:
        manager = get_model_manager()
        loaded = manager.load_kazakh_tts_model()
        kazakh_tts_model = loaded['model']

    return kazakh_tts_model

def init_kazakh_model():
    """Initialize Kazakh TTS model using ModelManager (downloads if needed)"""
    print("Loading Kazakh TTS model...")
    init_kk_tokenizer()
    init_kk_model()
    print("Kazakh TTS model loaded successfully!")