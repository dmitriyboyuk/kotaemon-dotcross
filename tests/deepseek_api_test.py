import requests
import json

# DeepSeek API credentials
API_KEY = "sk-024edc8440824c93b1b48ebf5c38619d"
API_BASE = "https://api.deepseek.com/v1"
MODEL = "deepseek-reasoner"

# Headers for authentication
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Test message
data = {
    "model": MODEL,
    "messages": [
        {"role": "user", "content": "Hello, how are you?"}
    ]
}

# Make the API call with a 10-second timeout
try:
    response = requests.post(
        f"{API_BASE}/chat/completions",
        headers=headers,
        json=data,
        timeout=10
    )
    
    if response.status_code == 200:
        print("✅ API credentials are working!")
        print("\nResponse from DeepSeek API:")
        result = response.json()
        print(result['choices'][0]['message']['content'])
    else:
        print(f"❌ API request failed with status code: {response.status_code}")
        print("\nError details:")
        print(json.dumps(response.json(), indent=2))

except requests.exceptions.Timeout:
    print("❌ The request timed out after 10 seconds.")
except requests.exceptions.RequestException as e:
    print(f"❌ An error occurred while making the request: {e}")
except Exception as e:
    print(f"❌ An unexpected error occurred: {e}")