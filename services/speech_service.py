# services/speech_service.py
import speech_recognition as sr
import pyttsx3

class SpeechService:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
    
    def speak(self, text):
        """Text-to-speech"""
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen(self, timeout=5):
        """Speech-to-text from microphone"""
        try:
            with sr.Microphone() as source:
                audio = self.recognizer.listen(source, timeout=timeout)
                text = self.recognizer.recognize_google(audio, language="en-US")
                return text
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError:
            return "API error"
    
    def transcribe_audio_file(self, audio_file_path):
        """Transcribe uploaded audio file"""
        try:
            with sr.AudioFile(audio_file_path) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)
                return text
        except Exception as e:
            return f"Error: {str(e)}"
