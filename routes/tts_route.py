from flask import Blueprint, request, jsonify, send_from_directory, url_for
import pyttsx3
import os
import torch
import scipy.io.wavfile
import uuid
from datetime import datetime
from utils.text_translator import init_translator
from utils.kk_speech_model import init_kk_tokenizer, init_kk_model
from utils.detect_voice import detect_voice_gender

# Create audio output directory if it doesn't exist
AUDIO_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'audio')
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

LANGUAGE_CODE = {
    "english": "eng_Latn",
    "russian": "rus_Cyrl",
    "kazakh":  "kaz_Cyrl"
}

tts_bp = Blueprint("tts_route", __name__)


@tts_bp.route('/audio/<path:filename>', methods=['GET'])
def get_audio(filename):
    audio_path = os.path.join(AUDIO_OUTPUT_DIR, filename)
    if not os.path.isfile(audio_path):
        return jsonify({'error': 'Audio file not found'}), 404
    return send_from_directory(AUDIO_OUTPUT_DIR, filename)


@tts_bp.route('/download/<path:filename>', methods=['GET'])
def download_audio(filename):
    audio_path = os.path.join(AUDIO_OUTPUT_DIR, filename)
    if not os.path.isfile(audio_path):
        return jsonify({'error': 'Audio file not found'}), 404
    return send_from_directory(AUDIO_OUTPUT_DIR, filename, as_attachment=True, download_name=filename)

@tts_bp.route('/tts', methods=['POST'])
def text_to_speech():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        src_language = data.get("src_language", "english")
        tgt_language = data.get('tgt_language', 'english')
        gender_preference = data.get('gender', 'any').lower()
        
        # Validation
        if not text:
            return jsonify({'error': 'Text cannot be empty'}), 400
        if src_language not in LANGUAGE_CODE or tgt_language not in LANGUAGE_CODE:
            return jsonify({'error': 'Unsupported language selection'}), 400
        
        # Translate text to selected LANGUAGE_CODE[tgt_language]
        try:
            if LANGUAGE_CODE[tgt_language] == LANGUAGE_CODE[src_language]:
                translated_text = text
            else:
                translator = init_translator()
                response = translator(text, src_lang=LANGUAGE_CODE[src_language], tgt_lang=LANGUAGE_CODE[tgt_language])
                translated_text = response[0]["translation_text"]
        except:
            translated_text = text
        
        # Create new TTS engine for each request
        try:
            if LANGUAGE_CODE[tgt_language] == 'kazakh':
                # Use Kazakh TTS model
                try:
                    # Tokenize the translated text
                    kazakh_tts_tokenizer = init_kk_tokenizer()
                    inputs = kazakh_tts_tokenizer(translated_text, return_tensors="pt")
                    
                    # Generate speech
                    with torch.no_grad():
                        kazakh_tts_model = init_kk_model()
                        output = kazakh_tts_model(**inputs).waveform
                    
                    # Generate unique filename
                    filename = f"tts_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
                    audio_file_path = os.path.join(AUDIO_OUTPUT_DIR, filename)
                    
                    # Save to file
                    scipy.io.wavfile.write(
                        audio_file_path, 
                        rate=kazakh_tts_model.config.sampling_rate, 
                        data=output.cpu().numpy().squeeze()
                    )

                    if not os.path.exists(audio_file_path):
                        return jsonify({'error': 'Failed to save audio file'}), 500
                    
                    return jsonify({
                        'success': True, 
                        'message': 'Speech generated successfully',
                        'translated_text': translated_text,
                        'voice_used': 'Kazakh MMS-TTS Model',
                        'gender_used': gender_preference,
                        'language_selected': LANGUAGE_CODE[tgt_language],
                        'audio_url': url_for('tts_route.get_audio', filename=filename),
                        'download_url': url_for('tts_route.download_audio', filename=filename),
                        'audio_filename': filename
                    })
                except Exception as kaz_error:
                    return jsonify({'error': f'Kazakh TTS Error: {str(kaz_error)}'}), 500

            print(f"Initializing TTS engine for language: {tgt_language}")
            engine = pyttsx3.init()
            engine.setProperty('volume', 1.0)
            
            voices = engine.getProperty('voices')
            selected_voice = None
            gender_found = False
            
            # Select voice based on tgt_language and gender
            if voices:
                selected_voice = voices[0]  # Default English
                
                if LANGUAGE_CODE[tgt_language] == 'russian':
                    # Look for Russian voice with gender preference
                    matching_voices = []
                    for voice in voices:
                        if 'ru' in voice.id.lower() or 'russian' in voice.name.lower():
                            matching_voices.append(voice)
                    
                    if matching_voices:
                        selected_voice = matching_voices[0]
                        # Try to match gender preference
                        if gender_preference != 'any':
                            for voice in matching_voices:
                                voice_gender = detect_voice_gender(voice)
                                if voice_gender == gender_preference:
                                    selected_voice = voice
                                    gender_found = True
                                    break
                    elif len(voices) > 1:
                        selected_voice = voices[1]
                
                elif LANGUAGE_CODE[tgt_language] == 'english':
                    # Filter English voices by gender
                    if gender_preference != 'any':
                        for voice in voices:
                            voice_gender = detect_voice_gender(voice)
                            if voice_gender == gender_preference:
                                selected_voice = voice
                                gender_found = True
                                break
                
                engine.setProperty('voice', selected_voice.id)
            
            engine.setProperty('rate', 150)
            
            # Generate unique filename
            filename = f"tts_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            audio_file_path = os.path.join(AUDIO_OUTPUT_DIR, filename)
            
            # Save to file using pyttsx3
            engine.save_to_file(translated_text, audio_file_path)
            engine.runAndWait()

            if not os.path.exists(audio_file_path):
                return jsonify({'error': 'Failed to save audio file'}), 500
            
            # Clean up engine properly
            try:
                engine.stop()
            except:
                pass
            del engine
            
            # Add warning if requested gender not found
            response_data = {
                'success': True, 
                'message': 'Speech generated successfully',
                'translated_text': translated_text,
                'voice_used': selected_voice.name if voices else 'Default Voice',
                'gender_used': gender_preference,
                'language_selected': LANGUAGE_CODE[tgt_language],
                'audio_url': url_for('tts_route.get_audio', filename=filename),
                'download_url': url_for('tts_route.download_audio', filename=filename),
                'audio_filename': filename
            }
            
            if gender_preference != 'any' and not gender_found:
                response_data['warning'] = f'No {gender_preference} voice available. Used default voice instead.'
            
            return jsonify(response_data)
        except Exception as tts_error:
            return jsonify({'error': f'TTS Engine Error: {str(tts_error)}'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Request Error: {str(e)}'}), 500