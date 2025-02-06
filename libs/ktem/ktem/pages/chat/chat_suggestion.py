import json
import logging
import gradio as gr
from ktem.app import BasePage
from theflow.settings import settings as flowsettings
from decouple import config, UndefinedValueError

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)  # Change to WARNING level

class ChatSuggestion(BasePage):
    def __init__(self, app):
        self._app = app
        self.on_building_ui()

    def on_building_ui(self):
        # Default medical/patient-focused suggestions
        default_suggestions = [
            "Tell me more about patient clinical context",
            "What is the patient diagnosis?",
            "What is the date of cancer diagnosis?",
            "What is the patient's current treatment plan?",
            "What is the patient's treatment history?",
        ]
        
        try:
            # First check if the feature is enabled
            is_enabled = config('KH_FEATURE_CHAT_SUGGESTION', default=True, cast=bool)
            logger.debug(f"Chat suggestion feature enabled: {is_enabled}")  # Changed to debug
            
            if not is_enabled:
                logger.debug("Chat suggestions feature is disabled")  # Changed to debug
                suggestions = []
            else:
                # Get raw value from environment
                try:
                    raw_env_suggestions = config('KH_FEATURE_CHAT_SUGGESTION_SAMPLES')
                    logger.debug(f"Raw suggestions loaded from environment: {raw_env_suggestions}")  # Changed to debug
                    
                    # Clean the string and try to parse JSON
                    cleaned_suggestions = raw_env_suggestions.strip()
                    logger.debug(f"Cleaned suggestions string: {cleaned_suggestions}")  # Changed to debug
                    
                    suggestions = json.loads(cleaned_suggestions)
                    logger.debug(f"Parsed suggestions from JSON: {suggestions}")  # Changed to debug
                    
                    # Validate suggestions format
                    if not isinstance(suggestions, list):
                        logger.warning(f"Environment suggestions must be a list, got {type(suggestions)}")
                        logger.debug("Falling back to default suggestions")  # Changed to debug
                        suggestions = default_suggestions
                    elif not all(isinstance(s, str) for s in suggestions):
                        logger.warning("All suggestions must be strings")
                        logger.debug("Falling back to default suggestions")  # Changed to debug
                        suggestions = default_suggestions
                    else:
                        # Remove duplicates while preserving order
                        seen = set()
                        suggestions = [x for x in suggestions if not (x in seen or seen.add(x))]
                        logger.debug(f"Successfully loaded {len(suggestions)} unique suggestions from environment: {suggestions}")  # Changed to debug
                
                except (UndefinedValueError, json.JSONDecodeError) as e:
                    logger.warning(f"Error loading suggestions from environment: {e}")
                    logger.debug("Falling back to default suggestions")  # Changed to debug
                    suggestions = default_suggestions
        except Exception as e:
            logger.error(f"Unexpected error loading suggestions: {e}")
            logger.debug("Falling back to default suggestions")  # Changed to debug
            suggestions = default_suggestions
        
        self.default_suggestions = suggestions
        self.chat_samples = [[s] for s in self.default_suggestions]
        logger.debug(f"Final chat samples configured: {self.chat_samples}")  # Changed to debug
        
        # Create the suggestions panel
        with gr.Accordion(
            label="Suggested Questions",
            visible=True,  # Always show suggestions
            open=True,  # Open by default
            elem_id="chat-suggestions-accordion"
        ) as self.accordion:
            try:
                # Create DataFrame with initial suggestions
                initial_value = self.chat_samples
                logger.debug(f"Setting initial DataFrame value to: {initial_value}")
                
                self.examples = gr.DataFrame(
                    value=initial_value,
                    # headers=["Click a suggestion to use it"],
                    headers=[""],  # Empty header instead of "Click a suggestion to use it"
                    interactive=False,
                    wrap=True,
                    elem_id="chat-suggestions",
                    elem_classes=["suggestions-table"],
                    height=300,  # Increased height for better visibility
                    column_widths=["100%"],  # Make the column take full width
                )
                logger.debug(f"Successfully created suggestions panel with initial suggestions: {initial_value}")
            except Exception as e:
                logger.error(f"Error creating suggestions panel: {e}")
                raise

    def as_gradio_component(self):
        return self.examples

    def select_example(self, ev: gr.SelectData):
        """Handle suggestion selection"""
        try:
            logger.debug(f"Selected suggestion: {ev.value}")
            return {"text": ev.value}
        except Exception as e:
            logger.error(f"Error handling suggestion selection: {e}")
            return {"text": ""}
