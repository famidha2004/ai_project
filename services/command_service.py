# services/command_service.py
import wikipedia
import webbrowser

class CommandService:
    def __init__(self):
        self.supported_commands = {
            "wikipedia": self.search_wikipedia,
            "open youtube": self.open_youtube,
            "open google": self.open_google,
            "open stackoverflow": self.open_stackoverflow,
            "weather": self.get_weather,
        }
    
    def search_wikipedia(self, query):
        try:
            query = query.replace("wikipedia", "").strip()
            result = wikipedia.summary(query, sentences=2)
            return {"status": "success", "result": result}
        except:
            return {"status": "error", "result": "Could not find on Wikipedia"}
    
    def open_youtube(self, query=None):
        webbrowser.open("https://www.youtube.com")
        return {"status": "success", "result": "Opening YouTube"}
    
    def open_google(self, query=None):
        webbrowser.open("https://www.google.com")
        return {"status": "success", "result": "Opening Google"}
    
    def open_stackoverflow(self, query=None):
        webbrowser.open("https://www.stackoverflow.com")
        return {"status": "success", "result": "Opening Stack Overflow"}
    
    def get_weather(self, location=""):
        return {"status": "info", "result": "Weather API not implemented yet"}
    
    def process_command(self, command_text):
        """Process voice command and return action"""
        command_lower = command_text.lower()
        
        for key, handler in self.supported_commands.items():
            if key in command_lower:
                return handler(command_text)
        
        return {"status": "unknown", "result": "Command not recognized"}
