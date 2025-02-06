import os
import requests
import json
from openai import OpenAI
from dotenv import load_dotenv
from decouple import config

# Load environment variables
load_dotenv()

# Test with API key from .env
API_KEY = config('OPENAI_API_KEY')
print(f"Using API key: {API_KEY[:10]}...")

def test_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")
    chat_model = os.getenv("OPENAI_CHAT_MODEL")
    embedding_model = os.getenv("OPENAI_EMBEDDINGS_MODEL")
    
    client = OpenAI(api_key=api_key, base_url=api_base)
    
    print("\n=== Testing OpenAI Connection ===")
    print("API Base:", api_base)
    print("Chat Model:", chat_model)
    print("Embedding Model:", embedding_model)
    
    try:
        # Test Chat Completion
        chat_response = client.chat.completions.create(
            model=chat_model,
            messages=[{"role": "user", "content": "What is machine learning?"}]
        )
        print("\n✅ Chat Completion Test Passed")
        print("Model used:", chat_model)
        print("Response:", chat_response.choices[0].message.content[:100] + "...")
        
        # Test Embeddings
        embed_response = client.embeddings.create(
            model=embedding_model,
            input="Hello, world!"
        )
        print("\n✅ Embeddings Test Passed")
        print("Model used:", embedding_model)
        print("Embedding dimension:", len(embed_response.data[0].embedding))
        
        return True
    except Exception as e:
        print("\n❌ OpenAI Test Failed")
        print("Error:", str(e))
        return False

def test_ollama():
    print("\n=== Testing Ollama Connection ===")
    local_model = os.getenv("LOCAL_MODEL")
    local_embeddings = os.getenv("LOCAL_MODEL_EMBEDDINGS")
    embedding_dim = int(os.getenv("LOCAL_EMBEDDING_MODEL_DIM", "768"))
    max_tokens = int(os.getenv("LOCAL_EMBEDDING_MODEL_MAX_TOKENS", "8192"))
    
    print("Local Chat Model:", local_model)
    print("Local Embedding Model:", local_embeddings)
    print("Expected Embedding Dimension:", embedding_dim)
    print("Max Tokens:", max_tokens)
    
    def test_chat_completion():
        url = "http://localhost:11434/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": local_model,
            "messages": [
                {"role": "user", "content": "What is machine learning?"}
            ]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            print("\n✅ Ollama Chat Completion Test Passed")
            print("Model used:", local_model)
            print("Response:", response.json()["choices"][0]["message"]["content"][:100] + "...")
            return True
        except Exception as e:
            print("\n❌ Ollama Chat Completion Test Failed")
            print("Error:", str(e))
            return False

    def test_embeddings():
        url = "http://localhost:11434/v1/embeddings"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": local_embeddings,
            "input": "Hello, world!"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            print("\n✅ Ollama Embeddings Test Passed")
            print("Model used:", local_embeddings)
            actual_dim = len(response.json()["data"][0]["embedding"])
            print("Embedding dimension:", actual_dim)
            if actual_dim != embedding_dim:
                print("⚠️ Warning: Actual dimension", actual_dim, "differs from configured dimension", embedding_dim)
            return True
        except Exception as e:
            print("\n❌ Ollama Embeddings Test Failed")
            print("Error:", str(e))
            return False
    
    chat_success = test_chat_completion()
    embed_success = test_embeddings()
    return chat_success and embed_success

if __name__ == "__main__":
    print("Testing API Connections...")
    
    openai_success = test_openai()
    ollama_success = test_ollama()
    
    print("\n=== Final Results ===")
    if openai_success:
        print("✅ OpenAI connection is working")
    else:
        print("❌ OpenAI connection failed")
        
    if ollama_success:
        print("✅ Ollama connection is working")
    else:
        print("❌ Ollama connection failed")

# Create OpenAI client
client = OpenAI(api_key=API_KEY)

try:
    # Test embeddings
    print('Testing embeddings...')
    response = client.embeddings.create(
        model='text-embedding-ada-002',
        input='Hello world'
    )
    print('✅ Embeddings API working!')
    
    # Test chat completion
    print('\nTesting chat completion...')
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',  # Using a known valid model
        messages=[{'role': 'user', 'content': 'Say hello'}],
        max_tokens=10
    )
    print('✅ Chat API working!')
    
except Exception as e:
    print('❌ Error:', str(e)) 