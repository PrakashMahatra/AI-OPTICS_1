# services/audio_service.py
class AudioService:
    def __init__(self, stt_model, tts_model):
        self.stt_model = stt_model
        self.tts_model = tts_model
    
    def transcribe_audio(self, audio_data):
        """Convert audio to text"""
        return self.stt_model.transcribe(audio_data)
    
    def synthesize_speech(self, text):
        """Convert text to speech"""
        return self.tts_model.synthesize(text)

