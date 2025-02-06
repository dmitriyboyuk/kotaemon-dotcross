import json
import os
from decouple import config

import gradio as gr
import requests
from ktem.app import BasePage
from ktem.embeddings.manager import embedding_models_manager as embeddings
from ktem.llms.manager import llms
from ktem.rerankings.manager import reranking_models_manager as rerankers
from theflow.settings import settings as flowsettings

# Debug prints commented out
# print("\n=== Debug - Setup Environment ===")
# print("Current working directory:", os.getcwd())
# print("Environment variables from config:")
# for key in os.environ:
#     if 'KH_FEEDBACK' in key:
#         print(f"{key} = {os.environ[key]}")
# print("===============================\n")

KH_DEMO_MODE = getattr(flowsettings, "KH_DEMO_MODE", False)
LOCAL_API_BASE = config("LOCAL_API_BASE", default="http://localhost:11434/v1/")
DEFAULT_OLLAMA_URL = LOCAL_API_BASE.replace("v1", "api")
if DEFAULT_OLLAMA_URL.endswith("/"):
    DEFAULT_OLLAMA_URL = DEFAULT_OLLAMA_URL[:-1]


DEMO_MESSAGE = (
    "This is a public space. Please use the "
    '"Duplicate Space" function on the top right '
    "corner to setup your own space."
)


def pull_model(name: str, stream: bool = True):
    payload = {"name": name}
    headers = {"Content-Type": "application/json"}

    response = requests.post(
        DEFAULT_OLLAMA_URL + "/pull", json=payload, headers=headers, stream=stream
    )

    # Check if the request was successful
    response.raise_for_status()

    if stream:
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                yield data
                if data.get("status") == "success":
                    break
    else:
        data = response.json()

    return data


class SetupPage(BasePage):

    public_events = ["onFirstSetupComplete"]

    def __init__(self, app):
        self._app = app
        self.on_building_ui()

    def on_building_ui(self):
        gr.Markdown(f"# Welcome to {self._app.app_name} first setup!")
        # Set default value based on environment configuration
        openai_api_key = config("OPENAI_API_KEY", default="")
        default_provider = "openai" if openai_api_key else "ollama"
        
        self.radio_model = gr.Radio(
            [
                ("OpenAI API (for GPT-based models)", "openai"),
                ("Local LLM (for completely *private RAG*)", "ollama"),
                ("Cohere API (*free registration*)", "cohere"),
                ("Google API (*free registration*)", "google"),
            ],
            label="Select your model provider",
            value=default_provider,
            info=(
                "Note: You can change this later. "
                "OpenAI is recommended for best performance, "
                "local Ollama models for privacy."
            ),
            interactive=True,
        )

        with gr.Column(visible=not bool(openai_api_key)) as self.openai_option:
            gr.Markdown(
                (
                    "#### OpenAI API Key\n\n"
                    "(create at https://platform.openai.com/api-keys)"
                )
            )
            self.openai_api_key = gr.Textbox(
                show_label=False, placeholder="OpenAI API Key"
            )

        with gr.Column(visible=True) as self.cohere_option:
            gr.Markdown(
                (
                    "#### Cohere API Key\n\n"
                    "(register your free API key "
                    "at https://dashboard.cohere.com/api-keys)"
                )
            )
            self.cohere_api_key = gr.Textbox(
                show_label=False, placeholder="Cohere API Key"
            )

        with gr.Column(visible=False) as self.google_option:
            gr.Markdown(
                (
                    "#### Google API Key\n\n"
                    "(register your free API key "
                    "at https://aistudio.google.com/app/apikey)"
                )
            )
            self.google_api_key = gr.Textbox(
                show_label=False, placeholder="Google API Key"
            )

        with gr.Column(visible=False) as self.ollama_option:
            gr.Markdown(
                (
                    "#### Setup Ollama\n\n"
                    "Download and install Ollama from "
                    "https://ollama.com/"
                )
            )

        self.setup_log = gr.HTML(
            show_label=False,
        )

        with gr.Row():
            self.btn_finish = gr.Button("Proceed", variant="primary")
            self.btn_skip = gr.Button(
                "I am an advance user. Skip this.", variant="stop"
            )

    def on_register_events(self):
        onFirstSetupComplete = gr.on(
            triggers=[
                self.btn_finish.click,
                self.cohere_api_key.submit,
                self.openai_api_key.submit,
            ],
            fn=self.update_model,
            inputs=[
                self.cohere_api_key,
                self.openai_api_key,
                self.google_api_key,
                self.radio_model,
            ],
            outputs=[self.setup_log],
            show_progress="hidden",
        )
        if not KH_DEMO_MODE:
            onSkipSetup = gr.on(
                triggers=[self.btn_skip.click],
                fn=lambda: None,
                inputs=[],
                show_progress="hidden",
                outputs=[self.radio_model],
            )

            for event in self._app.get_event("onFirstSetupComplete"):
                onSkipSetup = onSkipSetup.success(**event)

        onFirstSetupComplete = onFirstSetupComplete.success(
            fn=self.update_default_settings,
            inputs=[self.radio_model, self._app.settings_state],
            outputs=self._app.settings_state,
        )
        for event in self._app.get_event("onFirstSetupComplete"):
            onFirstSetupComplete = onFirstSetupComplete.success(**event)

        self.radio_model.change(
            fn=self.switch_options_view,
            inputs=[self.radio_model],
            show_progress="hidden",
            outputs=[
                self.cohere_option,
                self.openai_option,
                self.ollama_option,
                self.google_option,
            ],
        )

    def update_model(
        self,
        cohere_api_key,
        openai_api_key,
        google_api_key,
        radio_model_value,
    ):
        # skip if KH_DEMO_MODE
        if KH_DEMO_MODE:
            raise gr.Error(DEMO_MESSAGE)

        log_content = ""
        if not radio_model_value:
            gr.Info("Skip setup models.")
            yield gr.value(visible=False)
            return

        if radio_model_value == "cohere":
            if cohere_api_key:
                chat_model = config('COHERE_CHAT_MODEL', default='command-r-plus-08-2024')
                embedding_model = config('COHERE_EMBEDDING_MODEL', default='embed-multilingual-v3.0')
                rerank_model = config('COHERE_RERANK_MODEL', default='rerank-multilingual-v2.0')
                
                llms.update(
                    name="cohere",
                    spec={
                        "__type__": "kotaemon.llms.chats.LCCohereChat",
                        "model_name": chat_model,
                        "api_key": cohere_api_key,
                    },
                    default=True,
                )
                embeddings.update(
                    name="cohere",
                    spec={
                        "__type__": "kotaemon.embeddings.LCCohereEmbeddings",
                        "model": embedding_model,
                        "cohere_api_key": cohere_api_key,
                        "user_agent": "default",
                    },
                    default=True,
                )
                rerankers.update(
                    name="cohere",
                    spec={
                        "__type__": "kotaemon.rerankings.CohereReranking",
                        "model_name": rerank_model,
                        "cohere_api_key": cohere_api_key,
                    },
                    default=True,
                )
        elif radio_model_value == "openai":
            if openai_api_key:
                chat_model = config('OPENAI_CHAT_MODEL', default='gpt-4o-mini')
                embedding_model = config('OPENAI_EMBEDDINGS_MODEL', default='text-embedding-ada-002')
                base_url = config('OPENAI_API_BASE', default='https://api.openai.com/v1')
                
                llms.update(
                    name="openai",
                    spec={
                        "__type__": "kotaemon.llms.ChatOpenAI",
                        "base_url": base_url,
                        "model": chat_model,
                        "api_key": openai_api_key,
                        "timeout": 60,
                    },
                    default=True,
                )
                embeddings.update(
                    name="openai",
                    spec={
                        "__type__": "kotaemon.embeddings.OpenAIEmbeddings",
                        "base_url": base_url,
                        "model": embedding_model,
                        "api_key": openai_api_key,
                        "timeout": 30,
                        "context_length": 8191,
                    },
                    default=True,
                )
        elif radio_model_value == "google":
            if google_api_key:
                chat_model = config('GOOGLE_CHAT_MODEL', default='gemini-1.5-flash')
                embedding_model = config('GOOGLE_EMBEDDING_MODEL', default='models/text-embedding-004')
                
                llms.update(
                    name="google",
                    spec={
                        "__type__": "kotaemon.llms.chats.LCGeminiChat",
                        "model_name": chat_model,
                        "api_key": google_api_key,
                    },
                    default=True,
                )
                embeddings.update(
                    name="google",
                    spec={
                        "__type__": "kotaemon.embeddings.LCGoogleEmbeddings",
                        "model": embedding_model,
                        "google_api_key": google_api_key,
                    },
                    default=True,
                )
        elif radio_model_value == "ollama":
            local_model = config('LOCAL_MODEL', default='deepseek-r1:1.5b')
            local_embeddings = config('LOCAL_MODEL_EMBEDDINGS', default='nomic-embed-text')
            local_api_base = config('LOCAL_API_BASE', default='http://localhost:11434/v1/')
            
            llms.update(
                name="ollama",
                spec={
                    "__type__": "kotaemon.llms.ChatOpenAI",
                    "base_url": local_api_base,
                    "model": local_model,
                    "api_key": "ollama",
                    "timeout": 60,
                },
                default=True,
            )
            embeddings.update(
                name="ollama",
                spec={
                    "__type__": "kotaemon.embeddings.OpenAIEmbeddings",
                    "base_url": local_api_base,
                    "model": local_embeddings,
                    "api_key": "ollama",
                },
                default=True,
            )

            # download required models through ollama
            llm_model_name = llms.get("ollama").model  # type: ignore
            emb_model_name = embeddings.get("ollama").model  # type: ignore

            try:
                for model_name in [emb_model_name, llm_model_name]:
                    log_content += f"- Downloading model `{model_name}` from Ollama<br>"
                    yield log_content

                    pre_download_log = log_content

                    for response in pull_model(model_name):
                        complete = response.get("completed", 0)
                        total = response.get("total", 0)
                        if complete > 0 and total > 0:
                            ratio = int(complete / total * 100)
                            log_content = (
                                pre_download_log
                                + f"- {response.get('status')}: {ratio}%<br>"
                            )
                        else:
                            if "pulling" not in response.get("status", ""):
                                log_content += f"- {response.get('status')}<br>"

                        yield log_content
            except Exception as e:
                log_content += (
                    "Make sure you have download and installed Ollama correctly. "
                    f"Got error: {str(e)}"
                )
                yield log_content
                raise gr.Error("Failed to download model from Ollama.")

        # test models connection
        llm_output = emb_output = None

        # LLM model
        log_content += f"- Testing LLM model: {radio_model_value}<br>"
        yield log_content

        llm = llms.get(radio_model_value)  # type: ignore
        log_content += "- Sending a message `Hi`<br>"
        yield log_content
        try:
            llm_output = llm("Hi")
        except Exception as e:
            log_content += (
                f"<mark style='color: yellow; background: red'>- Connection failed. "
                f"Got error:\n {str(e)}</mark>"
            )

        if llm_output:
            log_content += (
                "<mark style='background: green; color: white'>- Connection success. "
                "</mark><br>"
            )
        yield log_content

        if llm_output:
            # embedding model
            log_content += f"- Testing Embedding model: {radio_model_value}<br>"
            yield log_content

            emb = embeddings.get(radio_model_value)
            assert emb, f"Embedding model {radio_model_value} not found."

            log_content += "- Sending a message `Hi`<br>"
            yield log_content
            try:
                emb_output = emb("Hi")
            except Exception as e:
                log_content += (
                    f"<mark style='color: yellow; background: red'>"
                    "- Connection failed. "
                    f"Got error:\n {str(e)}</mark>"
                )

            if emb_output:
                log_content += (
                    "<mark style='background: green; color: white'>"
                    "- Connection success. "
                    "</mark><br>"
                )
            yield log_content

        if llm_output and emb_output:
            gr.Info("Setup models completed successfully!")
        else:
            raise gr.Error(
                "Setup models failed. Please verify your connection and API key."
            )

    def update_default_settings(self, radio_model_value, default_settings):
        # revise default settings
        # reranking llm
        default_settings["index.options.1.reranking_llm"] = radio_model_value
        if radio_model_value == "ollama":
            default_settings["index.options.1.use_llm_reranking"] = False
            
        # Ensure chat suggestions are enabled and visible by default
        default_settings["chat.suggestions.enabled"] = config('KH_FEATURE_CHAT_SUGGESTION', default=True, cast=bool)
        default_settings["chat.suggestions.visible"] = True
        default_settings["chat.suggestions.open"] = True
        
        # Try to load suggestions from environment
        try:
            raw_env_suggestions = config('KH_FEATURE_CHAT_SUGGESTION_SAMPLES')
            if raw_env_suggestions:
                suggestions = json.loads(raw_env_suggestions.strip())
                if isinstance(suggestions, list) and all(isinstance(s, str) for s in suggestions):
                    # Remove duplicates while preserving order
                    seen = set()
                    suggestions = [x for x in suggestions if not (x in seen or seen.add(x))]
                    default_settings["chat.suggestions.samples"] = suggestions
                    logger.info(f"Successfully loaded {len(suggestions)} suggestions from environment during setup")
                else:
                    logger.warning("Invalid suggestion format in environment, using defaults")
                    raise ValueError("Invalid suggestion format")
        except (UndefinedValueError, json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Could not load suggestions from environment: {e}, using defaults")
            # Load default medical suggestions if not set or if environment loading fails
            default_settings["chat.suggestions.samples"] = [
                "Summarize the patient clinical context",
                "What is the patient diagnosis and evidence?",
                "What is the patient's medication history?",
                "What is the patient's current treatment plan?"
            ]

        return default_settings

    def switch_options_view(self, radio_model_value):
        components_visible = [gr.update(visible=False) for _ in range(4)]

        values = ["cohere", "openai", "ollama", "google", None]
        assert radio_model_value in values, f"Invalid value {radio_model_value}"

        if radio_model_value is not None:
            idx = values.index(radio_model_value)
            components_visible[idx] = gr.update(visible=True)

            # If OpenAI is selected but no API key, show the input
            if radio_model_value == "openai":
                openai_api_key = config("OPENAI_API_KEY", default="")
                components_visible[1] = gr.update(visible=not bool(openai_api_key))

        return components_visible
