import os
from dotenv import load_dotenv
from google import genai

def run_test():
    # Load environment variables from .env
    load_dotenv()
    
    api_key = os.environ.get("GEMINI_API_KEY")
    model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    
    print("Initializing Gemini client...")
    # Initialize the Gemini client using the loaded API key
    client = genai.Client(api_key=api_key)
    
    print(f"Sending prompt to {model_name}: 'Say hello in one sentence.'")
    # Send a simple prompt to generate content
    response = client.models.generate_content(
        model=model_name,
        contents="Say hello in one sentence."
    )
    
    print("\nResponse:")
    print(response.text)

if __name__ == "__main__":
    run_test()
