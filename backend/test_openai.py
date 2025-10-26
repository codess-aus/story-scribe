"""Test Azure OpenAI connection directly"""
import os
import pytest
from dotenv import load_dotenv
from pathlib import Path

# Print current working directory and .env file location
print(f"\nCurrent working directory: {os.getcwd()}")
env_path = Path(__file__).parent / '.env'
print(f".env file path: {env_path}")
print(f".env file exists: {env_path.exists()}")

# Load environment variables
load_dotenv(env_path)

def test_openai():
    try:
        from openai import AzureOpenAI
        
        from azure.identity import DefaultAzureCredential

        endpoint = os.getenv("OPENAI_ENDPOINT")
        deployment = os.getenv("OPENAI_DEPLOYMENT", "gpt-4o-mini")
        api_version = os.getenv("OPENAI_API_VERSION", "2024-08-01-preview")
        
        print(f"Endpoint: {endpoint}")
        print(f"Deployment: {deployment}")
        print(f"API Version: {api_version}")
        print("Authentication: Using Azure Managed Identity with RBAC")
        
        if not endpoint:
            print("\n❌ Missing endpoint!")
            pytest.fail("Missing required OPENAI_ENDPOINT environment variable")
            
        # Get Azure credential token
        print("\n🔄 Getting Azure credentials...")
        credential = DefaultAzureCredential()
        token = credential.get_token("https://cognitiveservices.azure.com/.default")
        print("✅ Got Azure token")
        
        print("\n🔄 Creating Azure OpenAI client...")
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=token.token,
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
        
        assert prompt, "No prompt was generated"
        assert len(prompt.split()) <= 40, "Generated prompt exceeds 40 words"
        assert completion.usage.total_tokens > 0, "No tokens were used"
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        pytest.fail(f"Test failed with error: {str(e)}")

if __name__ == "__main__":
    test_openai()
    print("\n✅ All tests passed!")
