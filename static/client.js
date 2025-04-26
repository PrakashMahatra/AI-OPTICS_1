// static/client.js
let ws;
let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let videoStream;

// DOM Elements
const videoElement = document.getElementById('videoElement');
const canvasElement = document.getElementById('canvasElement');
const chatMessages = document.getElementById('chatMessages');
const connectionStatus = document.getElementById('connectionStatus');
const modelStatus = document.getElementById('modelStatus');
const startVideoButton = document.getElementById('startVideo');
const captureImageButton = document.getElementById('captureImage');
const startRecordingButton = document.getElementById('startRecording');
const audioIndicator = document.getElementById('audioIndicator');

// Connect WebSocket
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

    ws.onopen = () => {
        connectionStatus.textContent = 'Connected';
        connectionStatus.style.color = '#2ecc71';
        enableControls();
    };

    ws.onclose = () => {
        connectionStatus.textContent = 'Disconnected';
        connectionStatus.style.color = '#e74c3c';
        disableControls();
        
        // Try to reconnect after 2 seconds
        setTimeout(connectWebSocket, 2000);
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        connectionStatus.textContent = 'Error';
        connectionStatus.style.color = '#e74c3c';
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
}

// Handle WebSocket messages
function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'vision_result':
            addMessage('Vision: ' + data.result, 'vision-message');
            break;
        
        case 'transcription':
            addMessage('You: ' + data.text, 'user-message');
            break;
        
        case 'response':
            addMessage('Assistant: ' + data.text, 'assistant-message');
            
            // Play audio response if available
            if (data.audio) {
                const audio = new Audio('data:audio/wav;base64,' + data.audio);
                audio.play();
            }
            break;
        
        case 'status':
            modelStatus.textContent = 'Models: ' + data.message;
            break;
    }
}

// Add message to chat
function addMessage(text, className) {
    const messageElement = document.createElement('div');
    messageElement.textContent = text;
    messageElement.className = 'message ' + className;
    chatMessages.appendChild(messageElement);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Start video stream
async function startVideo() {
    try {
        videoStream = await navigator.mediaDevices.getUserMedia({ 
            video: true
        });
        videoElement.srcObject = videoStream;
        captureImageButton.disabled = false;
        startVideoButton.textContent = 'Stop Camera';
        startVideoButton.onclick = stopVideo;
    } catch (error) {
        console.error('Error accessing camera:', error);
        addMessage('Error: Could not access camera', 'error-message');
    }
}

// Stop video stream
function stopVideo() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoElement.srcObject = null;
        captureImageButton.disabled = true;
        startVideoButton.textContent = 'Start Camera';
        startVideoButton.onclick = startVideo;
    }
}

// Capture image from video
function captureImage() {
    if (!videoStream) return;
    
    const context = canvasElement.getContext('2d');
    canvasElement.width = videoElement.videoWidth;
    canvasElement.height = videoElement.videoHeight;
    context.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
    
    // Get base64 image data
    const imageData = canvasElement.toDataURL('image/jpeg');
    
    // Send to server
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'image',
            data: imageData
        }));
        
        // Add preview to chat
        const previewImage = document.createElement('img');
        previewImage.src = imageData;
        previewImage.className = 'image-preview';
        
        const messageElement = document.createElement('div');
        messageElement.textContent = 'Processing image...';
        messageElement.className = 'message user-message';
        messageElement.appendChild(previewImage);
        chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Start audio recording
async function startRecording() {
    if (isRecording) return;
    
    try {
        const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioIndicator.style.backgroundColor = '#e74c3c';
        
        mediaRecorder = new MediaRecorder(audioStream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = sendAudioData;
        
        mediaRecorder.start();
        isRecording = true;
    } catch (error) {
        console.error('Error accessing microphone:', error);
        addMessage('Error: Could not access microphone', 'error-message');
    }
}

// Stop audio recording
function stopRecording() {
    if (!isRecording) return;
    
    mediaRecorder.stop();
    audioIndicator.style.backgroundColor = '#95a5a6';
    isRecording = false;
}

// Send audio data to server
function sendAudioData() {
    if (audioChunks.length === 0) return;
    
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    const reader = new FileReader();
    
    reader.onloadend = () => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: 'audio',
                data: reader.result
            }));
        }
    };
    
    reader.readAsDataURL(audioBlob);
}

// Enable UI controls
function enableControls() {
    startVideoButton.disabled = false;
    startRecordingButton.disabled = false;
}

// Disable UI controls
function disableControls() {
    startVideoButton.disabled = true;
    captureImageButton.disabled = true;
    startRecordingButton.disabled = true;
}

// Initialize
function init() {
    // Connect to WebSocket
    connectWebSocket();
    
    // Set up event listeners
    startVideoButton.onclick = startVideo;
    captureImageButton.onclick = captureImage;
    
    startRecordingButton.addEventListener('mousedown', startRecording);
    startRecordingButton.addEventListener('touchstart', startRecording);
    
    startRecordingButton.addEventListener('mouseup', stopRecording);
    startRecordingButton.addEventListener('touchend', stopRecording);
    startRecordingButton.addEventListener('mouseleave', stopRecording);
    
    // Initial state
    captureImageButton.disabled = true;
    disableControls();
    
    // Add welcome message
    setTimeout(() => {
        addMessage('Assistant: Hello! I am your AI assistant with vision capabilities. You can capture an image or talk to me.', 'assistant-message');
    }, 1000);
}

// Start the application
window.onload = init;