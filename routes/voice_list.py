from flask import Blueprint, jsonify
import pyttsx3

voice_list_bp = Blueprint("voices", __name__)

@voice_list_bp.route('/list-voices', methods=['GET'])
def list_voices():
    """Debug endpoint to list all available voices"""
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        voice_list = []
        for voice in voices:
            voice_list.append({
                'id': voice.id,
                'name': voice.name,
                'languages': voice.languages if hasattr(voice, 'languages') else [],
                'gender': voice.gender if hasattr(voice, 'gender') else 'unknown'
            })
        
        del engine
        return jsonify({'voices': voice_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500