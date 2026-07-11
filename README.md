# BOSS - Voice Assistant Cloud Edition

A production-ready Python-based voice assistant service that runs on AWS with Flask REST API, PostgreSQL database, and modern cloud architecture.

## 📋 Overview

**BOSS** (previously a desktop assistant) has been refactored as a **scalable cloud microservice** that:

- ✅ Processes voice commands via REST API
- ✅ Transcribes audio to text using Google Speech Recognition
- ✅ Converts text responses to speech
- ✅ Stores user data and command history in PostgreSQL
- ✅ Manages user memories across sessions
- ✅ Integrates with external APIs (Wikipedia, web browsing, etc.)
- ✅ Runs on AWS EC2 with Nginx + Gunicorn
- ✅ Supports multi-user architecture

## 🏗️ Architecture

```
Client Apps (Web/Mobile/Desktop)
        ↓
   Nginx (Reverse Proxy)
        ↓
   Gunicorn WSGI Server
        ↓
   Flask REST API
        ↓
┌──────────────────────────────┐
│ Speech Service    │
│ Command Service   │
│ Memory Service    │
└──────────────────┬───────────┘
         ↓
    AWS RDS PostgreSQL
```

## 🚀 Quick Start

### Local Setup

```bash
# Clone repository
git clone https://github.com/famidha2004/ai_project.git
cd ai_project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your database credentials

# Initialize database (optional for local testing)
python setup_db.py

# Run development server
python app.py
```

Server runs on `http://localhost:5000`

### AWS EC2 Deployment

See `AWS_DEPLOYMENT_GUIDE.md` for complete step-by-step instructions.

## 📁 Project Structure

```
boss-assistant/
├── app.py                      # Main Flask application
├── config.py                   # Configuration management
├── database.py                 # Database connection & queries
├── setup_db.py                 # Database initialization
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── gunicorn_config.py          # Production WSGI config
├── AWS_DEPLOYMENT_GUIDE.md     # Comprehensive deployment guide
├── ORIGINAL_PROJECT.md         # Original desktop assistant docs
│
├── services/
│   ├── __init__.py
│   ├── speech_service.py       # Speech recognition & TTS
│   ├── command_service.py      # Command processing logic
│   └── external_apis.py        # Wikipedia, web API integrations
│
├── routes/
│   ├── __init__.py
│   ├── auth.py                 # User authentication endpoints
│   ├── commands.py             # Command processing endpoints
│   ├── speech.py               # Speech transcription/synthesis
│   └── memories.py             # Memory management endpoints
│
├── models/
│   ├── __init__.py
│   └── database_models.py      # SQLAlchemy/Psycopg2 models
│
└── tests/
    ├── test_api.py
    ├── test_speech_service.py
    └── test_command_service.py
```

## 🔧 API Endpoints

### Health Check
```bash
GET /health
Response: {"status": "healthy", "version": "1.0.0"}
```

### User Management
```bash
POST /api/users/register
Body: {"username": "john_doe", "email": "john@example.com"}
Response: {"user_id": 1, "message": "User created"}
```

### Speech Processing
```bash
POST /api/speech/transcribe
Body: multipart/form-data with audio file
Response: {"text": "transcribed text"}

POST /api/speech/speak
Body: {"text": "text to speak"}
Response: {"message": "Spoken successfully"}
```

### Command Processing
```bash
POST /api/commands/process
Body: {"user_id": 1, "command": "search wikipedia python"}
Response: {"status": "success", "result": "..."}
```

### Memory Management
```bash
POST /api/memory/save
Body: {"user_id": 1, "memory": "remember this"}
Response: {"message": "Memory saved"}

GET /api/memory/get/<user_id>
Response: {"memories": [{"text": "...", "created_at": "..."}]}
```

## 📝 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Commands History Table
```sql
CREATE TABLE commands_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    command_text VARCHAR(500),
    action_performed VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    result TEXT
);
```

### Memories Table
```sql
CREATE TABLE memories (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    memory_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Voice Settings Table
```sql
CREATE TABLE voice_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    voice_speed FLOAT DEFAULT 1.0,
    voice_volume FLOAT DEFAULT 1.0,
    wake_word VARCHAR(100) DEFAULT 'hello boss'
);
```

## 📦 Supported Commands

- `search wikipedia [topic]` - Get Wikipedia summary
- `open youtube` - Open YouTube
- `open google` - Open Google
- `open stackoverflow` - Open Stack Overflow
- `weather [location]` - Get weather (TODO)
- Custom command processing

## 📚 Dependencies

```
Flask==2.3.0
Flask-CORS==4.0.0
python-dotenv==1.0.0
psycopg2-binary==2.9.6
wikipedia==1.4.0
pyttsx3==2.90
SpeechRecognition==3.10.0
Gunicorn==20.1.0
```

See `requirements.txt` for complete list.

## 🚀 Deployment

### Prerequisites
- AWS Account
- EC2 instance (Ubuntu 22.04 LTS, t2.medium or larger)
- RDS PostgreSQL database
- SSH key pair

### Quick Deploy

1. **Launch AWS Resources** (EC2 + RDS)
2. **Connect to EC2** via SSH
3. **Clone Repository** and install dependencies
4. **Configure Environment** (.env file)
5. **Run Database Setup** (`python setup_db.py`)
6. **Start Service** with Systemd
7. **Configure Nginx** as reverse proxy

Detailed instructions in `AWS_DEPLOYMENT_GUIDE.md`

## 🔐 Security

- Environment variables for sensitive data
- Database connection pooling
- CORS protection
- HTTPS support (with Let's Encrypt)
- Input validation
- SQL injection prevention (parameterized queries)

## 📊 Monitoring

```bash
# Check service status
sudo systemctl status boss-api

# View logs
sudo journalctl -u boss-api -f

# Monitor performance
top
df -h
free -m
```

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/

# Test specific endpoint
python tests/test_api.py

# Test with curl
curl -X POST http://localhost:5000/health
```

## 🐛 Troubleshooting

### Connection Refused
- Check if Flask app is running: `ps aux | grep python`
- Verify port 5000 is open: `sudo netstat -tlnp | grep 5000`

### Database Connection Failed
- Verify RDS endpoint in `.env`
- Check security group allows traffic from EC2
- Test connection: `psql -h <rds-endpoint> -U admin -d boss_db`

### Speech Recognition Not Working
- Check microphone permissions
- Verify internet connection (Google API)
- Test with: `python -c "import speech_recognition; print(speech_recognition.__version__)"`

## 📖 Documentation

- `AWS_DEPLOYMENT_GUIDE.md` - Complete cloud deployment instructions
- `ORIGINAL_PROJECT.md` - Original desktop assistant documentation
- `API_DOCUMENTATION.md` - Detailed API reference

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

Original BOSS Assistant created by Akshay Sharda
Cloud refactoring and AWS deployment by Famidha

## 🏄 Future Enhancements

- [ ] Add JWT authentication
- [ ] Implement WebSocket for real-time streaming
- [ ] Replace Google Speech API with open-source (Whisper, Vosk)
- [ ] Add NLP for better intent recognition
- [ ] Support multiple languages
- [ ] Implement scheduled tasks
- [ ] Add analytics dashboard
- [ ] Support voice settings per user
- [ ] Integrate with calendar, email, messaging
- [ ] Mobile app (iOS/Android)

## 📞 Support

For issues, questions, or suggestions, please open a GitHub issue.
