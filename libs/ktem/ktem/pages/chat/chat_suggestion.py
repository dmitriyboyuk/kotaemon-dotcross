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
        default_suggestions = [
            "Tell me about patient's clinical context",
            "What is the patient diagnosis based on the clinical evidence?",
            "What is the date of cancer diagnosis?",
            "What is the patient's current treatment plan?",
            "What is the patient's treatment history?"
        ]
        
        try:
            # Try to load suggestions from environment
            raw_env_suggestions = config('KH_FEATURE_CHAT_SUGGESTION_SAMPLES')
            cleaned_suggestions = raw_env_suggestions.strip()
            suggestions = json.loads(cleaned_suggestions)
            
            # Validate suggestions format
            if not isinstance(suggestions, list) or not all(isinstance(s, str) for s in suggestions):
                logger.warning("Invalid suggestion format in environment, using defaults")
                suggestions = default_suggestions
        except (UndefinedValueError, json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Error loading suggestions from environment: {e}")
            suggestions = default_suggestions

        # Remove duplicates while preserving order
        seen = set()
        self.default_suggestions = [x for x in suggestions if not (x in seen or seen.add(x))]
        self.chat_samples = [[s] for s in self.default_suggestions]
        
        # Create the suggestions panel - ensure it's always visible at startup
        with gr.Accordion(
            label="Suggested Questions",
            visible=True,  # Always show suggestions by default
            open=True,  # Always open by default
            elem_id="chat-suggestions-accordion",
            elem_classes=["suggestions-container"]  # Add a class for better styling
        ) as self.accordion:
            self.examples = gr.DataFrame(
                value=self.chat_samples,
                headers=[""],
                interactive=False,
                wrap=True,
                elem_id="chat-suggestions",
                elem_classes=["suggestions-table"],
                height=400,
                column_widths=["100%"],
                visible=True
            )

    def update_visibility(self, data_source):
        """Update suggestions visibility based on conversation data source"""
        if data_source and isinstance(data_source, dict):
            is_visible = data_source.get("chat_suggestions_visible", True)
            return gr.update(visible=is_visible)
        return gr.update(visible=True)  # Default to visible if no data source

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
