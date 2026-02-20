from google import genai
from google.genai import types
import os
from config import GEMINI_API_KEY

class LLMService:
    def __init__(self, api_key=GEMINI_API_KEY):
        if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
            api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("Gemini API Key is missing. Please set it in config.py or environment variable GEMINI_API_KEY.")

        # Initialize the modern Client
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-flash-lite-latest'

    def generate_response(self, prompt, image_data=None, system_instruction=None):
        """
        Generates a response from the LLM using the modern google-genai SDK.
        Supports automatic Google Search grounding.
        """
        try:
            contents = [prompt]
            if image_data:
                # Handle image data (assuming it's a PIL Image or compatible format)
                contents.append(image_data)

            # Modern tools configuration for Google Search grounding
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )
            return response.text
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return f"Xin lỗi, tôi đang gặp sự cố khi kết nối với AI: {str(e)}"

if __name__ == "__main__":
    # Test execution
    try:
        service = LLMService()
        print(service.generate_response("Hôm nay là ngày bao nhiêu và có sự kiện gì hot?"))
    except Exception as e:
        print(f"Setup failed: {e}")
