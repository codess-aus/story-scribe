"""Test Azure OpenAI connection directly"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_openai():
    try:
        from openai import AzureOpenAI
        
        endpoint = os.getenv("OPENAI_ENDPOINT")
        deployment = os.getenv("OPENAI_DEPLOYMENT", "gpt-4o-mini")
        api_version = os.getenv("OPENAI_API_VERSION", "2024-08-01-preview")
        api_key = os.getenv("OPENAI_API_KEY")
        
        print(f"Endpoint: {endpoint}")
        print(f"Deployment: {deployment}")
        print(f"API Version: {api_version}")
        print(f"API Key: {'*' * 20}{api_key[-10:] if api_key else 'NOT SET'}")
        
        if not endpoint or not api_key:
            print("\n❌ Missing credentials!")
            return False
        
        print("\n🔄 Creating Azure OpenAI client...")
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        
        print("✅ Client created successfully!")
        
        print("\n🔄 Testing prompt generation...")
        completion = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are a creative writing assistant. Generate ONE short writing prompt under 40 words."},
                {"role": "user", "content": "Generate a memoir writing prompt"}
            ],
            max_tokens=80,
            temperature=0.7
        )
        
        prompt = completion.choices[0].message.content.strip()
        print(f"\n✅ AI-Generated Prompt:\n{prompt}\n")
        print(f"📊 Tokens used: {completion.usage.total_tokens}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_openai()
    exit(0 if success else 1)
