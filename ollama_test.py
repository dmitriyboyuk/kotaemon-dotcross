import requests
import json

def test_chat_completion():
    url = "http://localhost:11434/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "deepseek-r1:1.5b",
        "messages": [
            {"role": "user", "content": "What is machine learning?"}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("\n=== Chat Completion Test ===")
        print("Status Code:", response.status_code)
        print("Response:", response.json())
        return True
    except Exception as e:
        print("\n=== Chat Completion Test Failed ===")
        print("Error:", str(e))
        return False

def test_embeddings():
    url = "http://localhost:11434/v1/embeddings"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "nomic-embed-text",
        "input": "Hello, world!"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("\n=== Embedding Test ===")
        print("Status Code:", response.status_code)
        print("Response:", response.json())
        return True
    except Exception as e:
        print("\n=== Embedding Test Failed ===")
        print("Error:", str(e))
        return False

if __name__ == "__main__":
    print("Testing Ollama API...")
    
    chat_success = test_chat_completion()
    embed_success = test_embeddings()
    
    if chat_success and embed_success:
        print("\n✅ All tests passed! Your Ollama setup appears to be working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.") 