import os
import unittest
from flowsettings import KH_LLMS

# Import the ChatOpenAI handler.
# (Ensure that this is the class your application uses for API calls.)
from kotaemon.llms import ChatOpenAI

class TestDeepseekConfig(unittest.TestCase):
    def test_deepseek_llm_present(self):
        # Verify that the "deepseek" key is added to the KH_LLMS dictionary
        self.assertIn("deepseek", KH_LLMS)

        deepseek_conf = KH_LLMS["deepseek"]["spec"]

        # Check that the API key, base URL and model match the environment variables.
        self.assertEqual(deepseek_conf["api_key"], os.getenv("DEEPSEEK_API_KEY", ""))
        # The base_url may contain extra spaces from .env so we compare after stripping any whitespace.
        self.assertEqual(deepseek_conf["base_url"], os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1").strip())
        self.assertEqual(deepseek_conf["model"], os.getenv("DEEPSEEK_CHAT_MODEL", "deepseek-reasoner"))

    @unittest.skipIf(not os.getenv("DEEPSEEK_API_KEY"), "DeepSeek API key not set in environment")
    def test_deepseek_api_call_with_chatopenai_handler(self):
        """
        Instantiates the ChatOpenAI handler using DeepSeek configuration values
        and makes an API call using a sample prompt.
        """
        # Get the DeepSeek configuration from the global KH_LLMS dictionary
        deepseek_spec = KH_LLMS["deepseek"]["spec"]

        # Instantiate the ChatOpenAI LLM handler using DeepSeek settings.
        llm = ChatOpenAI(
            api_key=deepseek_spec["api_key"],
            base_url=deepseek_spec["base_url"],
            model=deepseek_spec["model"],
            temperature=deepseek_spec["temperature"],
            timeout=deepseek_spec["timeout"],
        )

        # Define a sample prompt.
        prompt = "Hello, DeepSeek! Can you tell me about how RAG is integrated?"

        # Make a call to the DeepSeek API via the ChatOpenAI handler.
        response = llm.invoke(prompt)

        # Validate that we received a response.
        self.assertIsNotNone(response, "Expected a non-None response.")
        self.assertTrue(hasattr(response, "content"), "Response should have content attribute.")

if __name__ == "__main__":
    unittest.main() 