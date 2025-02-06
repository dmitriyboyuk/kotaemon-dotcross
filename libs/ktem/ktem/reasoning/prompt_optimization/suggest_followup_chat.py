import logging
import json
from decouple import config, UndefinedValueError

from ktem.llms.manager import llms

from kotaemon.base import AIMessage, BaseComponent, Document, HumanMessage, Node
from kotaemon.llms import ChatLLM, PromptTemplate

logger = logging.getLogger(__name__)


class SuggestFollowupQuesPipeline(BaseComponent):
    """Suggest a list of follow-up questions based on the chat history."""

    llm: ChatLLM = Node(default_callback=lambda _: llms.get_default())
    
    # Default suggestions will be loaded from environment or fallback to these
    FALLBACK_SUGGESTIONS = [
        "Tell me more about patient clinical context",
        "What is the patient diagnosis?", 
        "What is the date of cancer diagnosis?",
        "What is the patient's current treatment plan?",
        "What is the patient's treatment history?"
    ]
    
    def get_default_suggestions(self):
        """Get default suggestions from environment or fallback to defaults"""
        try:
            raw_env_suggestions = config('KH_FEATURE_CHAT_SUGGESTION_SAMPLES')
            if raw_env_suggestions:
                try:
                    suggestions = json.loads(raw_env_suggestions.strip())
                    if isinstance(suggestions, list) and all(isinstance(s, str) for s in suggestions):
                        # Remove duplicates while preserving order
                        seen = set()
                        return [x for x in suggestions if not (x in seen or seen.add(x))]
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"Error parsing suggestions from environment: {e}")
            
        except UndefinedValueError:
            logger.info("No environment suggestions found, using fallback suggestions")
        
        return self.FALLBACK_SUGGESTIONS

    SUGGEST_QUESTIONS_PROMPT_TEMPLATE = (
        "Based on the chat history above. "
        "your task is to generate 3 to 5 relevant follow-up questions. "
        "These questions should be simple, clear, "
        "and designed to guide the conversation further. "
        "Ensure that the questions are open-ended to encourage detailed responses. "
        "Respond in JSON format with 'questions' key. "
        "Answer using the language {lang} same as the question. "
        "If the question uses Chinese, the answer should be in Chinese.\n"
    )
    prompt_template: str = SUGGEST_QUESTIONS_PROMPT_TEMPLATE
    extra_prompt: str = """Example of valid response:
```json
{
    "questions": ["the weather is good", "what's your favorite city"]
}
```"""
    lang: str = "English"

    def run(self, chat_history: list[tuple[str, str]]) -> Document:
        # For empty chat history or no valid messages, return a response with default suggestions
        if not chat_history:
            return Document(text=json.dumps({"questions": self.get_default_suggestions()}))
            
        prompt_template = PromptTemplate(self.prompt_template)
        prompt = prompt_template.populate(lang=self.lang) + self.extra_prompt

        messages = []
        # Only process valid message pairs
        for human, ai in chat_history[-3:]:
            if human and ai:  # Check that both messages exist
                messages.append(HumanMessage(content=human))
                messages.append(AIMessage(content=ai))

        # If no valid messages were found, return default suggestions
        if not messages:
            return Document(text=json.dumps({"questions": self.get_default_suggestions()}))

        messages.append(HumanMessage(content=prompt))

        return self.llm(messages)
