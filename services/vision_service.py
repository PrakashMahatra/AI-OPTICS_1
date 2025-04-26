# services/vision_service.py
import cv2
import numpy as np
import os
import tempfile

class VisionService:
    def __init__(self, qwen_model):
        self.qwen_model = qwen_model
    
    def process_image(self, image):
        """Process image and return description"""
        # Save image to temporary file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            filename = f.name
            cv2.imwrite(filename, image)
        
        # Process with Qwen-VL
        query = "Describe this image in detail. What do you see?"
        description, _ = self.qwen_model.process_image_query(filename, query)
        
        # Clean up
        os.unlink(filename)
        
        return description