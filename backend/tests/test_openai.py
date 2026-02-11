"""
Test script to verify OpenAI API key works with Chat Completions API
Run with: python test_openai.py
"""
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("Testing OpenAI Chat Completions API...")
print("=" * 60)

try:
    # Test with gpt-3.5-turbo (the model used in backend)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'API key is working!' if you can read this."}
        ],
        max_tokens=50
    )
    
    print("✅ SUCCESS!")
    print(f"Model: {response.model}")
    print(f"Response: {response.choices[0].message.content}")
    print("=" * 60)
    print("\nYour API key works with gpt-3.5-turbo!")
    print("The backend should work now.")
    
except Exception as e:
    print("❌ ERROR!")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    print("=" * 60)
    
    if "429" in str(e) or "quota" in str(e).lower():
        print("\n⚠️  QUOTA ISSUE:")
        print("Your API key has exceeded its quota for the Chat Completions API.")
        print("\nSolutions:")
        print("1. Check your usage at: https://platform.openai.com/usage")
        print("2. Add credits at: https://platform.openai.com/account/billing")
        print("3. Check if you have rate limits: https://platform.openai.com/account/limits")
    elif "401" in str(e) or "authentication" in str(e).lower():
        print("\n⚠️  AUTHENTICATION ISSUE:")
        print("Your API key is invalid or expired.")
        print("Get a new one at: https://platform.openai.com/api-keys")
    elif "404" in str(e) or "model" in str(e).lower():
        print("\n⚠️  MODEL ACCESS ISSUE:")
        print("Your API key doesn't have access to gpt-3.5-turbo.")
        print("This usually means you need to upgrade your OpenAI plan.")
