import google.generativeai as genai
import os
from config import GEMINI_API_KEY

class LLMService:
    def __init__(self, api_key=GEMINI_API_KEY):
        if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
            # Try getting from environment variable as fallback
            api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("Gemini API Key is missing. Please set it in config.py or environment variable GEMINI_API_KEY.")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def generate_response(self, prompt, image_data=None, system_instruction=None):
        """
        Generates a response from the LLM.
        :param prompt: Text prompt
        :param image_data: Optional PIL Image object or bytes
        :param system_instruction: Optional system instruction to guide the LLM
        """
        try:
            full_prompt = prompt
            if system_instruction:
                full_prompt = f"{system_instruction}\n\n{prompt}"

            if image_data:
                # Multimodal request
                response = self.model.generate_content([full_prompt, image_data])
            else:
                # Text-only request
                response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return "Xin lỗi, tôi đang gặp sự cố khi kết nối với AI."
            
if __name__ == "__main__":
    # Test
    try:
        service = LLMService()
        print(service.generate_response("Hello, are you working?"))
    except Exception as e:
        print(f"Setup failed: {e}")
