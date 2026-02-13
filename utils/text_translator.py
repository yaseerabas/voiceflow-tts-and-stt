from utils.model_manager import get_model_manager

translator = None

def init_translator():
    """Initialize translation model using ModelManager (downloads if needed)"""
    global translator

    if not translator:
        print("Translation Model is initializing for the first time...")
        manager = get_model_manager()
        translator = manager.load_translator_model()
        print("✔ Translation Model has been initialized.")

    return translator