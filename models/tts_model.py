# models/tts_model.py
import io
import numpy as np
import torch
import tempfile
import os

class KokoroTTS:
    def __init__(self):
        try:
            from kokoro.models import parse_model_string
            from kokoro.inference import TextToSpeechEngine
            
            print("Initializing Kokoro TTS...")
            self.kokoro_model = parse_model_string("kokoro/kokoro-small-en")
            self.tts_engine = TextToSpeechEngine(self.kokoro_model, device="cuda" if torch.cuda.is_available() else "cpu")
            print("Kokoro TTS initialized")
        except ImportError:
            print("Warning: Kokoro TTS not found. Using fallback TTS.")
            self.kokoro_model = None
            self.tts_engine = None
    
    def synthesize(self, text):
        """Convert text to speech"""
        if self.tts_engine:
            # Use Kokoro TTS
            try:
                audio = self.tts_engine.tts(text)
                
                # Save audio to byte buffer
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    filename = f.name
                    self.tts_engine.save_wav(filename, audio)
                
                with open(filename, 'rb') as f:
                    audio_data = f.read()
                
                # Clean up
                os.unlink(filename)
                return audio_data
            except Exception as e:
                print(f"Error with Kokoro TTS: {e}")
                return self._fallback_tts(text)
        else:
            # Use fallback TTS
            return self._fallback_tts(text)
    
    def _fallback_tts(self, text):
        """Fallback TTS method if Kokoro is not available"""
        # This would implement a simple alternative TTS
        # For this example, we'll just return empty audio data
        print("Using fallback TTS")
        return b''  # Would be audio data in real implementation