from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import json
import requests
import google.generativeai as genai

# Load configuration from constants.json
with open("constants.json", "r") as config_file:
    config = json.load(config_file)
    email_prompt_template = config["email_prompt_template"]
    model_type = config["model_type"]  # Determines which model to use (local or API)
    gemini_api_key = config.get("gemini_api_key", "")

# Detect Apple Silicon (MPS) or CPU
device = "mps" if torch.backends.mps.is_available() else "cpu"


# Define AI Client class with Local and Google Gemini options
class AIClient:
    def __init__(self):
        if model_type == "local":
            self.setup_local_model()
        elif model_type == "gemini":
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel("gemini-1.5-pro")
        else:
            raise ValueError("Invalid model_type in constants.json. Choose 'local' or 'gemini'.")

    def setup_local_model(self):
        model_name = "llama-2-model"  # Ensure you have this model downloaded
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map={"": device},
            low_cpu_mem_usage=True
        )
        self.model = torch.compile(self.model)

    def generate_text(self, prompt):
        if model_type == "local":
            return self.generate_text_local(prompt)
        elif model_type == "gemini":
            return self.generate_text_gemini(prompt)
        else:
            return "Invalid model type specified."

    def generate_text_local(self, prompt):
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(device)
            outputs = self.model.generate(**inputs, max_length=300, do_sample=True, temperature=0.7)
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        except Exception as e:
            return f"Error generating text locally: {str(e)}"

    def generate_text_gemini(self, prompt):
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error generating text with Gemini: {str(e)}"
