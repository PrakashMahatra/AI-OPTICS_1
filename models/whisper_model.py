# models/whisper_model.py
import torch
import whisper
from io import BytesIO
import numpy as np

class WhisperSTT:
    def __init__(self, model_size="base"):
        print(f"Loading Whisper {model_size} model...")
        self.model = whisper.load_model(model_size)
        print("Whisper model loaded")
    
    def transcribe(self, audio_data):
        """Transcribe audio data to text"""
        # Convert audio data to format expected by whisper
        audio_array = self._process_audio(audio_data)
        
        # Transcribe
        result = self.model.transcribe(audio_array)
        return result["text"]
    
    def _process_audio(self, audio_data):
        """Process audio data from WebSocket to format expected by Whisper"""
        # In a real implementation, you would convert the WebSocket audio data
        # to the format expected by Whisper
        # This is a simplified version
        audio_array = np.frombuffer(audio_data, np.float32)
        return audio_array
