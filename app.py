# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from services.speech_service import SpeechService
from services.command_service import CommandService
from database import create_user, save_memory, log_command, get_user_memories
import os
import json

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

speech_service = SpeechService()
command_service = CommandService()

# ==================== Health Check ====================
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "version": "1.0.0"}), 200

# ==================== User Management ====================
@app.route('/api/users/register', methods=['POST'])
def register_user():
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        
        if not username or not email:
            return jsonify({"error": "Username and email required"}), 400
        
        user_id = create_user(username, email)
        return jsonify({"user_id": user_id, "message": "User created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== Speech Processing ====================
@app.route('/api/speech/transcribe', methods=['POST'])
def transcribe_audio():
    """Transcribe uploaded audio file"""
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        audio_file.save('temp_audio.wav')
        
        text = speech_service.transcribe_audio_file('temp_audio.wav')
        os.remove('temp_audio.wav')
        
        return jsonify({"text": text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/speech/speak', methods=['POST'])
def speak_text():
    """Convert text to speech"""
    try:
        data = request.json
        text = data.get('text')
        
        if not text:
            return jsonify({"error": "Text required"}), 400
        
        # For production, you'd stream audio or save to S3
        speech_service.speak(text)
        
        return jsonify({"message": "Spoken successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== Command Processing ====================
@app.route('/api/commands/process', methods=['POST'])
def process_command():
    """Process a voice command"""
    try:
        data = request.json
        user_id = data.get('user_id')
        command_text = data.get('command')
        
        if not command_text:
            return jsonify({"error": "Command text required"}), 400
        
        # Process command
        result = command_service.process_command(command_text)
        
        # Log to database
        if user_id:
            log_command(user_id, command_text, result.get("status"), json.dumps(result))
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== Memory Management ====================
@app.route('/api/memory/save', methods=['POST'])
def save_user_memory():
    """Save a memory for user"""
    try:
        data = request.json
        user_id = data.get('user_id')
        memory_text = data.get('memory')
        
        if not user_id or not memory_text:
            return jsonify({"error": "User ID and memory text required"}), 400
        
        save_memory(user_id, memory_text)
        
        return jsonify({"message": "Memory saved"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/memory/get/<user_id>', methods=['GET'])
def get_memories(user_id):
    """Retrieve user memories"""
    try:
        memories = get_user_memories(int(user_id))
        
        return jsonify({
            "memories": [{"text": m[0], "created_at": str(m[1])} for m in memories]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== Error Handling ====================
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host=Config.API_HOST, port=Config.API_PORT, debug=Config.DEBUG)
