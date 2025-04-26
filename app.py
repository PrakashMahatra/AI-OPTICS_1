# app.py
import os
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from models123.qwen_model import QwenModel
from models123.whisper_model import WhisperSTT
from models123.tts_model import KokoroTTS
from services.vision_service import VisionService
from services.audio_service import AudioService
from services.websocket_manager import ConnectionManager
import base64
import numpy as np
import cv2
from io import BytesIO
import asyncio
app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize services
qwen_model = QwenModel()
whisper_stt = WhisperSTT()
kokoro_tts = KokoroTTS()
vision_service = VisionService(qwen_model)
audio_service = AudioService(whisper_stt, kokoro_tts)
manager = ConnectionManager()

# Main page
@app.get("/", response_class=HTMLResponse)
async def get():
    with open('static/index.html', 'r') as f:
        return HTMLResponse(content=f.read())

# WebSocket endpoint for real-time communication
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    conversation_history = []
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "image":
                # Process image
                image_data = base64.b64decode(data["data"].split(",")[1])
                image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
                
                # Vision processing
                description = vision_service.process_image(image)
                await manager.send_message({"type": "vision_result", "result": description}, websocket)
                
                # Add to conversation history
                conversation_history.append({"role": "system", "content": f"Visual context: {description}"})
            
            elif data["type"] == "audio":
                # Process audio
                audio_data = base64.b64decode(data["data"].split(",")[1])
                
                # Speech-to-text
                text = audio_service.transcribe_audio(audio_data)
                await manager.send_message({"type": "transcription", "text": text}, websocket)
                
                # Add to conversation history
                conversation_history.append({"role": "user", "content": text})
                
                # Generate response with Qwen
                response = qwen_model.generate_response(text, conversation_history)
                conversation_history.append({"role": "assistant", "content": response})
                
                # Text-to-speech
                audio_response = audio_service.synthesize_speech(response)
                await manager.send_message({
                    "type": "response", 
                    "text": response,
                    "audio": base64.b64encode(audio_response).decode('utf-8')
                }, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

