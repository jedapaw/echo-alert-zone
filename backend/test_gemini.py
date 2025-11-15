import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ GEMINI_API_KEY not found in .env")
    exit(1)

print(f"✅ API Key found: {api_key[:10]}...{api_key[-10:]}")

try:
    genai.configure(api_key=api_key)
    
    # Use the correct model name
    print("\n🔄 Testing translation with gemini-2.5-flash...")
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = """Translate "Please evacuate immediately" to Hindi.
Respond with ONLY a JSON object: {"hi": "hindi translation here"}"""
    
    response = model.generate_content(prompt)
    print(f"\n✅ Gemini works! Response:\n{response.text}")
    
except Exception as e:
    print(f"\n❌ Gemini error: {e}")
    import traceback
    traceback.print_exc()
