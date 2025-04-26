# Now, models/qwen_model.py
# models/qwen_model.py
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class QwenModel:
    def __init__(self, model_name="Qwen/Qwen-VL-Chat", device="cuda"):
        print("Initializing Qwen VL model...")
        self.device = "cuda" if torch.cuda.is_available() and device == "cuda" else "cpu"
        
        # Use 4-bit quantization for efficiency
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.float16,  # Use half precision
        )
        print(f"Qwen VL model loaded on {self.device}")
    
    def process_image_query(self, image_path, query, history=None):
        """Process image and a query to generate a response"""
        if history is None:
            history = []
            
        response, history = self.model.chat(
            self.tokenizer,
            query=query,
            image=image_path,
            history=history
        )
        return response, history
    
    def generate_response(self, query, history=None):
        """Generate a text response based on the query and conversation history"""
        if history is None:
            history = []
            
        # Convert conversation history to the format expected by Qwen
        qwen_history = []
        for entry in history:
            if entry["role"] == "user":
                qwen_history.append((entry["content"], None))
            elif entry["role"] == "assistant":
                qwen_history.append((None, entry["content"]))
        
        # Get response
        response, _ = self.model.chat(
            self.tokenizer,
            query=query,
            history=qwen_history
        )
        return response