import os
from decouple import config
from ktem.pages.setup import SetupPage
from ktem.llms.manager import llms
from ktem.embeddings.manager import embedding_models_manager as embeddings

def test_openai_setup():
    print("\n=== Testing OpenAI Setup ===")
    # Create mock app with all required attributes
    class MockApp:
        def __init__(self):
            self.settings_state = {}
            self.app_name = "Test App"
            self.app = None
            
        def get_event(self, _):
            return []
    
    setup_page = SetupPage(MockApp())
    
    # Test OpenAI configuration
    print("Testing OpenAI configuration...")
    api_key = config('OPENAI_API_KEY', default='test-key')  # Use actual API key from env
    
    # Get expected values from env or defaults
    expected_chat_model = config('OPENAI_CHAT_MODEL', default='gpt-4o-mini')
    expected_embedding_model = config('OPENAI_EMBEDDINGS_MODEL', default='text-embedding-ada-002')
    expected_base_url = config('OPENAI_API_BASE', default='https://api.openai.com/v1')
    
    # Call update_model
    try:
        next(setup_page.update_model(None, api_key, None, "openai"))
        
        # Verify LLM config
        llm_config = llms.get("openai")
        print("\nLLM Configuration:")
        print(f"Base URL: {llm_config.base_url} (Expected: {expected_base_url})")
        print(f"Model: {llm_config.model} (Expected: {expected_chat_model})")
        print(f"Timeout: {llm_config.timeout} (Expected: 60)")
        print(f"API Key: {'[SET]' if llm_config.api_key else '[NOT SET]'}")
        print(f"API Key Length: {len(llm_config.api_key) if llm_config.api_key else 0}")
        
        # Verify Embeddings config
        emb_config = embeddings.get("openai")
        print("\nEmbeddings Configuration:")
        print(f"Base URL: {emb_config.base_url} (Expected: {expected_base_url})")
        print(f"Model: {emb_config.model} (Expected: {expected_embedding_model})")
        print(f"Timeout: {emb_config.timeout} (Expected: 30)")
        print(f"API Key: {'[SET]' if emb_config.api_key else '[NOT SET]'}")
        print(f"API Key Length: {len(emb_config.api_key) if emb_config.api_key else 0}")
        
        # Verify API keys match expected
        assert llm_config.api_key == api_key, "LLM API key mismatch"
        assert emb_config.api_key == api_key, "Embeddings API key mismatch"
        
        print("\n✅ OpenAI setup test completed")
    except AssertionError as e:
        print(f"\n❌ OpenAI setup test failed: {str(e)}")
    except Exception as e:
        print(f"\n❌ OpenAI setup test failed: {str(e)}")

def test_ollama_setup():
    print("\n=== Testing Ollama Setup ===")
    # Create mock app with all required attributes
    class MockApp:
        def __init__(self):
            self.settings_state = {}
            self.app_name = "Test App"
            self.app = None
            
        def get_event(self, _):
            return []
    
    setup_page = SetupPage(MockApp())
    
    # Test Ollama configuration
    print("Testing Ollama configuration...")
    
    # Get expected values from env or defaults
    expected_model = config('LOCAL_MODEL', default='deepseek-r1:1.5b')
    expected_embeddings = config('LOCAL_MODEL_EMBEDDINGS', default='nomic-embed-text')
    expected_url = config('LOCAL_API_BASE', default='http://localhost:11434/v1/')
    
    # Call update_model (skip actual model download)
    try:
        # Initialize the configuration without downloading models
        for output in setup_page.update_model(None, None, None, "ollama"):
            if "Downloading model" in str(output):
                break
        
        # Verify LLM config
        llm_config = llms.get("ollama")
        print("\nLLM Configuration:")
        print(f"Base URL: {llm_config.base_url} (Expected: {expected_url})")
        print(f"Model: {llm_config.model} (Expected: {expected_model})")
        print(f"Timeout: {llm_config.timeout} (Expected: 60)")
        
        # Verify Embeddings config
        emb_config = embeddings.get("ollama")
        print("\nEmbeddings Configuration:")
        print(f"Base URL: {emb_config.base_url} (Expected: {expected_url})")
        print(f"Model: {emb_config.model} (Expected: {expected_embeddings})")
        
        # Verify configurations match expected values
        assert llm_config.base_url == expected_url, "LLM base URL mismatch"
        assert llm_config.model == expected_model, "LLM model mismatch"
        assert llm_config.timeout == 60, "LLM timeout mismatch"
        assert emb_config.base_url == expected_url, "Embeddings base URL mismatch"
        assert emb_config.model == expected_embeddings, "Embeddings model mismatch"
        
        print("\n✅ Ollama setup test completed")
    except AssertionError as e:
        print(f"\n❌ Ollama setup test failed: {str(e)}")
    except Exception as e:
        print(f"\n❌ Ollama setup test failed with unexpected error: {str(e)}")

if __name__ == "__main__":
    print("Starting setup.py tests...")
    test_openai_setup()
    test_ollama_setup() 