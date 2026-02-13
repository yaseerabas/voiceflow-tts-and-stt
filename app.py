from flask import Flask, render_template, jsonify
import os
import sys
from routes import stt_bp, tts_bp, voice_list_bp
from utils.kk_speech_model import init_kazakh_model
from utils.text_translator import init_translator

def _resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


app = Flask(
    __name__,
    template_folder=_resource_path('templates'),
    static_folder=_resource_path('static')
)

app.register_blueprint(stt_bp)
app.register_blueprint(tts_bp)
app.register_blueprint(voice_list_bp)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)