from flask import Blueprint, request, jsonify
import tempfile
import os
from utils.model_manager import get_model_manager

# Whisper model loaded on-demand (lazy loading)
whisper_model = None

def get_whisper_model():
    """Get Whisper model, loading it if needed"""
    global whisper_model
    if whisper_model is None:
        print("Loading Whisper model...")
        manager = get_model_manager()
        whisper_model = manager.load_whisper_model()
        print("Whisper model loaded successfully!")
    return whisper_model

WHISPER_LANGUAGES = {
    'english': 'en',
    'russian': 'ru',
    'kazakh': 'kk'
}

stt_bp = Blueprint("stt_route", __name__)

@stt_bp.route('/stt', methods=['POST'])
def speech_to_text():
    try:
        audio_file = request.files.get('audio')
        language = request.form.get('language', 'english')
        
        if not audio_file:
            return jsonify({'error': 'No audio file received'}), 400
        
        if language not in WHISPER_LANGUAGES:
            return jsonify({'error': 'Unsupported language'}), 400
        
        # Check audio file size
        audio_data = audio_file.read()
        audio_size = len(audio_data)
        
        if audio_size < 1000:  # Reduced minimum for Whisper
            return jsonify({'error': f'Audio recording too short. Please record for at least 2-3 seconds.'}), 400
        
        # Determine audio suffix from filename or mimetype
        mime_type = (audio_file.mimetype or '').lower()
        filename = audio_file.filename or ''
        ext = os.path.splitext(filename)[1].lower()
        if not ext:
            if 'wav' in mime_type:
                ext = '.wav'
            elif 'ogg' in mime_type:
                ext = '.ogg'
            else:
                ext = '.webm'

        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            temp_path = temp_file.name
            temp_file.write(audio_data)
            
        try:
            # Use Whisper to transcribe audio
            whisper_lang = WHISPER_LANGUAGES[language]
            
            # Get Whisper model (loads if not already loaded)
            try:
                model = get_whisper_model()
            except Exception as model_error:
                return jsonify({
                    'error': f'Whisper model unavailable: {str(model_error)}. Please download models first.'
                }), 503
            
            # Transcribe with Whisper (handles WebM format directly)
            result = model.transcribe(
                temp_path, 
                language=whisper_lang,
                fp16=False  # Better compatibility
            )
            
            text = result["text"].strip()
            
            if not text:
                text = "No speech detected. Please speak clearly."
            
        except Exception as e:
            text = f"Recognition error: {str(e)}"
        
        finally:
            # Clean up temp file
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            except:
                pass
        
        return jsonify({'success': True, 'text': text})
        
    except Exception as e:
        return jsonify({'error': f'STT Error: {str(e)}'}), 500