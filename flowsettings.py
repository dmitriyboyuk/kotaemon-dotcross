import os
from importlib.metadata import version
from inspect import currentframe, getframeinfo
from pathlib import Path
import dotenv

from decouple import AutoConfig, Config, RepositoryEnv
from ktem.utils.lang import SUPPORTED_LANGUAGE_MAP

# Debug prints commented out
# print("\n=== Debug - Environment Setup ===")
# print("Current working directory:", os.getcwd())
# print("Environment files in directory:")
# for file in os.listdir():
#     if file.startswith('.env'):
#         print(f"Found: {file}")
env_path = os.path.join(os.getcwd(), '.env')
# print(f"Using .env file at: {env_path}")

# Load environment variables directly using python-dotenv
dotenv.load_dotenv(env_path, override=True)

# print("Environment file contents:")
# with open(env_path, 'r') as f:
#     for line in f:
#         if 'OPENAI' in line:
#             print(f"  {line.strip()}")

# print("\nEnvironment variables after loading:")
# for key in os.environ:
#     if 'OPENAI' in key:
#         value = os.environ[key]
#         print(f"  {key} = {value[:10]}..." if 'KEY' in key else f"  {key} = {value}")

# Force python-decouple to use our specific .env file
config = Config(RepositoryEnv(env_path))

# Initialize empty dictionaries for settings
KH_LLMS = {}
KH_EMBEDDINGS = {}
KH_RERANKINGS = {}

# Basic app settings
KH_OLLAMA_URL = config("KH_OLLAMA_URL", default="http://localhost:11434/v1/")
KH_APP_DATA_DIR = Path(os.getcwd()) / "ktem_app_data"
KH_USER_DATA_DIR = KH_APP_DATA_DIR / "user_data"
KH_APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
KH_USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Load OpenAI settings
OPENAI_API_KEY = config('OPENAI_API_KEY')  # Remove default='' to ensure it's required
OPENAI_API_BASE = config('OPENAI_API_BASE', default='https://api.openai.com/v1')
OPENAI_CHAT_MODEL = config('OPENAI_CHAT_MODEL', default='gpt-4o-mini')
OPENAI_EMBEDDINGS_MODEL = config('OPENAI_EMBEDDINGS_MODEL', default='text-embedding-ada-002')

# print("\n=== Debug - OpenAI Settings ===")
# print(f"OPENAI_API_KEY = {OPENAI_API_KEY[:10]}...")
# print(f"OPENAI_API_BASE = {OPENAI_API_BASE}")
# print(f"OPENAI_CHAT_MODEL = {OPENAI_CHAT_MODEL}")
# print(f"OPENAI_EMBEDDINGS_MODEL = {OPENAI_EMBEDDINGS_MODEL}")
# print("===============================\n")

# Set OpenAI environment variables explicitly
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
os.environ['OPENAI_API_BASE'] = OPENAI_API_BASE
os.environ['OPENAI_CHAT_MODEL'] = OPENAI_CHAT_MODEL
os.environ['OPENAI_EMBEDDINGS_MODEL'] = OPENAI_EMBEDDINGS_MODEL

# print("=== Debug - Environment Variables After Setting ===")
# for key in os.environ:
#     if 'OPENAI' in key:
#         value = os.environ[key]
#         print(f"  {key} = {value[:10]}..." if 'KEY' in key else f"  {key} = {value}")
# print("===============================\n")

# Configure OpenAI LLM settings
# print("\n=== Debug - Configuring OpenAI LLM Settings ===")
# print(f"Using API key: {OPENAI_API_KEY[:10]}...")

# Add our OpenAI settings
KH_LLMS["openai"] = {
    "spec": {
        "__type__": "kotaemon.llms.ChatOpenAI",
        "temperature": 0,
        "base_url": OPENAI_API_BASE,
        "api_key": OPENAI_API_KEY,
        "model": OPENAI_CHAT_MODEL,
        "timeout": 30,
    },
    "default": True,
}

KH_EMBEDDINGS["openai"] = {
    "spec": {
        "__type__": "kotaemon.embeddings.OpenAIEmbeddings",
        "base_url": OPENAI_API_BASE,
        "api_key": OPENAI_API_KEY,
        "model": OPENAI_EMBEDDINGS_MODEL,
        "timeout": 30,
        "context_length": 8191,
    },
    "default": True,
}

# print("OpenAI LLM and Embeddings settings configured with API key")
# print("Current OpenAI LLM settings:")
# print(f"  API Key: {KH_LLMS['openai']['spec']['api_key'][:10]}...")
# print(f"  Base URL: {KH_LLMS['openai']['spec']['base_url']}")
# print(f"  Model: {KH_LLMS['openai']['spec']['model']}")
# print(f"  Temperature: {KH_LLMS['openai']['spec']['temperature']}")
# print(f"  Timeout: {KH_LLMS['openai']['spec']['timeout']}")
# print("===============================\n")

# Configure other LLM settings
if config("LOCAL_MODEL", default=""):
    # print("\n=== Debug - Configuring Ollama Settings ===")
    local_model = config("LOCAL_MODEL", default="deepseek-r1:1.5b")
    local_embeddings_model = config("LOCAL_MODEL_EMBEDDINGS", default="nomic-embed-text")
    # print(f"Local Model: {local_model}")
    # print(f"Local Embeddings Model: {local_embeddings_model}")
    # print(f"Ollama URL: {KH_OLLAMA_URL}")
    
    KH_LLMS["ollama"] = {
        "spec": {
            "__type__": "kotaemon.llms.ChatOpenAI",
            "base_url": KH_OLLAMA_URL,
            "model": local_model,
            "api_key": "ollama",
        },
        "default": False,
    }
    KH_EMBEDDINGS["ollama"] = {
        "spec": {
            "__type__": "kotaemon.embeddings.OpenAIEmbeddings",
            "base_url": KH_OLLAMA_URL,
            "model": local_embeddings_model,
            "api_key": "ollama",
        },
        "default": False,
    }
    # print("Ollama settings configured")
    # print("===============================\n")

# Configure Azure OpenAI if enabled
if config("AZURE_OPENAI_API_KEY", default="") and config("AZURE_OPENAI_ENDPOINT", default=""):
    # print("\n=== Debug - Configuring Azure OpenAI Settings ===")
    azure_endpoint = config("AZURE_OPENAI_ENDPOINT", default="")
    azure_api_key = config("AZURE_OPENAI_API_KEY", default="")
    azure_api_version = config("OPENAI_API_VERSION", default="") or "2024-02-15-preview"
    azure_chat_deployment = config("AZURE_OPENAI_CHAT_DEPLOYMENT", default="")
    azure_embeddings_deployment = config("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT", default="")
    
    # print(f"Azure Endpoint: {azure_endpoint}")
    # print(f"Azure API Version: {azure_api_version}")
    # print(f"Azure Chat Deployment: {azure_chat_deployment}")
    # print(f"Azure Embeddings Deployment: {azure_embeddings_deployment}")
    
    if azure_chat_deployment:
        KH_LLMS["azure"] = {
            "spec": {
                "__type__": "kotaemon.llms.AzureChatOpenAI",
                "temperature": 0,
                "azure_endpoint": azure_endpoint,
                "api_key": azure_api_key,
                "api_version": azure_api_version,
                "azure_deployment": azure_chat_deployment,
                "timeout": 20,
            },
            "default": False,
        }
    if azure_embeddings_deployment:
        KH_EMBEDDINGS["azure"] = {
            "spec": {
                "__type__": "kotaemon.embeddings.AzureOpenAIEmbeddings",
                "azure_endpoint": azure_endpoint,
                "api_key": azure_api_key,
                "api_version": azure_api_version,
                "azure_deployment": azure_embeddings_deployment,
                "timeout": 10,
            },
            "default": False,
        }
    # print("Azure OpenAI settings configured")
    # print("===============================\n")

# print("\n=== Debug - Final LLM Configuration ===")
# print("Available LLMs:", list(KH_LLMS.keys()))
# print("Default LLM:", next((k for k, v in KH_LLMS.items() if v.get("default")), None))
# for llm_name, llm_config in KH_LLMS.items():
#     print(f"\n{llm_name} configuration:")
#     for key, value in llm_config["spec"].items():
#         if 'api_key' in key:
#             print(f"  {key}: {value[:10]}...")
#         else:
#             print(f"  {key}: {value}")
# print("===============================\n")

# Import default settings after configuring our settings
from theflow.settings.default import *  # noqa

cur_frame = currentframe()
if cur_frame is None:
    raise ValueError("Cannot get the current frame.")
this_file = getframeinfo(cur_frame).filename
this_dir = Path(this_file).parent

# change this if your app use a different name
KH_PACKAGE_NAME = "kotaemon_app"

KH_APP_VERSION = config("KH_APP_VERSION", None)
if not KH_APP_VERSION:
    try:
        # Caution: This might produce the wrong version
        # https://stackoverflow.com/a/59533071
        KH_APP_VERSION = version(KH_PACKAGE_NAME)
    except Exception:
        KH_APP_VERSION = "local"

KH_ENABLE_FIRST_SETUP = config("KH_ENABLE_FIRST_SETUP", default=True, cast=bool)
KH_DEMO_MODE = config("KH_DEMO_MODE", default=False, cast=bool)
KH_OLLAMA_URL = config("KH_OLLAMA_URL", default="http://localhost:11434/v1/")

# App can be ran from anywhere and it's not trivial to decide where to store app data.
# So let's use the same directory as the flowsetting.py file.
KH_APP_DATA_DIR = this_dir / "ktem_app_data"
KH_APP_DATA_EXISTS = KH_APP_DATA_DIR.exists()
KH_APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

# markdown output directory
KH_MARKDOWN_OUTPUT_DIR = KH_APP_DATA_DIR / "markdown_cache_dir"
KH_MARKDOWN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# chunks output directory
KH_CHUNKS_OUTPUT_DIR = KH_APP_DATA_DIR / "chunks_cache_dir"
KH_CHUNKS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# zip output directory
KH_ZIP_OUTPUT_DIR = KH_APP_DATA_DIR / "zip_cache_dir"
KH_ZIP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# zip input directory
KH_ZIP_INPUT_DIR = KH_APP_DATA_DIR / "zip_cache_dir_in"
KH_ZIP_INPUT_DIR.mkdir(parents=True, exist_ok=True)

# HF models can be big, let's store them in the app data directory so that it's easier
# for users to manage their storage.
# ref: https://huggingface.co/docs/huggingface_hub/en/guides/manage-cache
os.environ["HF_HOME"] = str(KH_APP_DATA_DIR / "huggingface")
os.environ["HF_HUB_CACHE"] = str(KH_APP_DATA_DIR / "huggingface")

# doc directory
KH_DOC_DIR = this_dir / "docs"

KH_MODE = "dev"
KH_FEATURE_CHAT_SUGGESTION = config(
    "KH_FEATURE_CHAT_SUGGESTION", default=False, cast=bool
)
KH_FEATURE_USER_MANAGEMENT = config(
    "KH_FEATURE_USER_MANAGEMENT", default=True, cast=bool
)
KH_USER_CAN_SEE_PUBLIC = None
KH_FEATURE_USER_MANAGEMENT_ADMIN = str(
    config("KH_FEATURE_USER_MANAGEMENT_ADMIN", default="admin")
)
KH_FEATURE_USER_MANAGEMENT_PASSWORD = str(
    config("KH_FEATURE_USER_MANAGEMENT_PASSWORD", default="admin")
)
KH_ENABLE_ALEMBIC = False
KH_DATABASE = f"sqlite:///{KH_USER_DATA_DIR / 'sql.db'}"
KH_FILESTORAGE_PATH = str(KH_USER_DATA_DIR / "files")
KH_WEB_SEARCH_BACKEND = (
    "kotaemon.indices.retrievers.tavily_web_search.WebSearch"
    # "kotaemon.indices.retrievers.jina_web_search.WebSearch"
)

KH_DOCSTORE = {
    # "__type__": "kotaemon.storages.ElasticsearchDocumentStore",
    # "__type__": "kotaemon.storages.SimpleFileDocumentStore",
    "__type__": "kotaemon.storages.LanceDBDocumentStore",
    "path": str(KH_USER_DATA_DIR / "docstore"),
}
KH_VECTORSTORE = {
    # "__type__": "kotaemon.storages.LanceDBVectorStore",
    "__type__": "kotaemon.storages.ChromaVectorStore",
    # "__type__": "kotaemon.storages.MilvusVectorStore",
    # "__type__": "kotaemon.storages.QdrantVectorStore",
    "path": str(KH_USER_DATA_DIR / "vectorstore"),
}

# populate options from config
if config("AZURE_OPENAI_API_KEY", default="") and config(
    "AZURE_OPENAI_ENDPOINT", default=""
):
    if config("AZURE_OPENAI_CHAT_DEPLOYMENT", default=""):
        KH_LLMS["azure"] = {
            "spec": {
                "__type__": "kotaemon.llms.AzureChatOpenAI",
                "temperature": 0,
                "azure_endpoint": config("AZURE_OPENAI_ENDPOINT", default=""),
                "api_key": config("AZURE_OPENAI_API_KEY", default=""),
                "api_version": config("OPENAI_API_VERSION", default="")
                or "2024-02-15-preview",
                "azure_deployment": config("AZURE_OPENAI_CHAT_DEPLOYMENT", default=""),
                "timeout": 20,
            },
            "default": False,
        }
    if config("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT", default=""):
        KH_EMBEDDINGS["azure"] = {
            "spec": {
                "__type__": "kotaemon.embeddings.AzureOpenAIEmbeddings",
                "azure_endpoint": config("AZURE_OPENAI_ENDPOINT", default=""),
                "api_key": config("AZURE_OPENAI_API_KEY", default=""),
                "api_version": config("OPENAI_API_VERSION", default="")
                or "2024-02-15-preview",
                "azure_deployment": config(
                    "AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT", default=""
                ),
                "timeout": 10,
            },
            "default": False,
        }

if config("LOCAL_MODEL", default=""):
    KH_LLMS["ollama"] = {
        "spec": {
            "__type__": "kotaemon.llms.ChatOpenAI",
            "base_url": KH_OLLAMA_URL,
            "model": config("LOCAL_MODEL", default="llama3.1:8b"),
            "api_key": "ollama",
        },
        "default": False,
    }
    KH_EMBEDDINGS["ollama"] = {
        "spec": {
            "__type__": "kotaemon.embeddings.OpenAIEmbeddings",
            "base_url": KH_OLLAMA_URL,
            "model": config("LOCAL_MODEL_EMBEDDINGS", default="nomic-embed-text"),
            "api_key": "ollama",
        },
        "default": False,
    }

    KH_EMBEDDINGS["fast_embed"] = {
        "spec": {
            "__type__": "kotaemon.embeddings.FastEmbedEmbeddings",
            "model_name": "BAAI/bge-base-en-v1.5",
        },
        "default": False,
    }

# additional LLM configurations
KH_LLMS["claude"] = {
    "spec": {
        "__type__": "kotaemon.llms.chats.LCAnthropicChat",
        "model_name": "claude-3-5-sonnet-20240620",
        "api_key": "your-key",
    },
    "default": False,
}
KH_LLMS["google"] = {
    "spec": {
        "__type__": "kotaemon.llms.chats.LCGeminiChat",
        "model_name": "gemini-1.5-flash",
        "api_key": config("GOOGLE_API_KEY", default="your-key"),
    },
    "default": False,
}
KH_LLMS["groq"] = {
    "spec": {
        "__type__": "kotaemon.llms.ChatOpenAI",
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.1-8b-instant",
        "api_key": "your-key",
    },
    "default": False,
}
KH_LLMS["cohere"] = {
    "spec": {
        "__type__": "kotaemon.llms.chats.LCCohereChat",
        "model_name": "command-r-plus-08-2024",
        "api_key": config("COHERE_API_KEY", default="your-key"),
    },
    "default": False,
}

# Additional embeddings configurations
KH_EMBEDDINGS["cohere"] = {
    "spec": {
        "__type__": "kotaemon.embeddings.LCCohereEmbeddings",
        "model": "embed-multilingual-v3.0",
        "cohere_api_key": config("COHERE_API_KEY", default="your-key"),
        "user_agent": "default",
    },
    "default": False,
}
KH_EMBEDDINGS["google"] = {
    "spec": {
        "__type__": "kotaemon.embeddings.LCGoogleEmbeddings",
        "model": "models/text-embedding-004",
        "google_api_key": config("GOOGLE_API_KEY", default="your-key"),
    }
}
# KH_EMBEDDINGS["huggingface"] = {
#     "spec": {
#         "__type__": "kotaemon.embeddings.LCHuggingFaceEmbeddings",
#         "model_name": "sentence-transformers/all-mpnet-base-v2",
#     },
#     "default": False,
# }

# default reranking models
KH_RERANKINGS["cohere"] = {
    "spec": {
        "__type__": "kotaemon.rerankings.CohereReranking",
        "model_name": "rerank-multilingual-v2.0",
        "cohere_api_key": config("COHERE_API_KEY", default=""),
    },
    "default": True,
}

KH_REASONINGS = [
    "ktem.reasoning.simple.FullQAPipeline",
    "ktem.reasoning.simple.FullDecomposeQAPipeline",
    "ktem.reasoning.react.ReactAgentPipeline",
    "ktem.reasoning.rewoo.RewooAgentPipeline",
]
KH_REASONINGS_USE_MULTIMODAL = config("USE_MULTIMODAL", default=False, cast=bool)
KH_VLM_ENDPOINT = "{0}/openai/deployments/{1}/chat/completions?api-version={2}".format(
    config("AZURE_OPENAI_ENDPOINT", default=""),
    config("OPENAI_VISION_DEPLOYMENT_NAME", default="gpt-4o"),
    config("OPENAI_API_VERSION", default=""),
)


SETTINGS_APP: dict[str, dict] = {}


SETTINGS_REASONING = {
    "use": {
        "name": "Reasoning options",
        "value": None,
        "choices": [],
        "component": "radio",
    },
    "lang": {
        "name": "Language",
        "value": "en",
        "choices": [(lang, code) for code, lang in SUPPORTED_LANGUAGE_MAP.items()],
        "component": "dropdown",
    },
    "max_context_length": {
        "name": "Max context length (LLM)",
        "value": 32000,
        "component": "number",
    },
}

KH_REMOVE_QUICK_UPLOAD_BOX = config("KH_REMOVE_QUICK_UPLOAD_BOX", default=False, cast=bool)
KH_REMOVE_HELP_TAB = config("KH_REMOVE_HELP_TAB", default=False, cast=bool)
KH_RENAME_UI = config("KH_RENAME_UI", default=False, cast=bool)
KH_RENAME_UI_CONVERSATIONS = config("KH_RENAME_UI_CONVERSATIONS", default="", cast=str)
KH_UPLOAD_MULTIPLE_PIPELINES = config(
    "KH_UPLOAD_MULTIPLE_PIPELINES", default=False, cast=bool
)
KH_RENAME_UI_FILES_TAB = config("KH_RENAME_UI_FILES_TAB", default="Files", cast=str)
# KH_CHAT_CUSTOM_PLACEHOLDER = config("KH_CHAT_CUSTOM_PLACEHOLDER", default="", cast=str)
KH_CHAT_CUSTOM_PLACEHOLDER = config("KH_CHAT_CUSTOM_PLACEHOLDER", default=False, cast=bool)
KH_FEEDBACK_CORRECTNESS_LABEL = os.environ.get("KH_FEEDBACK_CORRECTNESS_LABEL", "Was the response correct?")
KH_FEEDBACK_CORRECT = os.environ.get("KH_FEEDBACK_CORRECT", "Correct")
KH_FEEDBACK_INCORRECT = os.environ.get("KH_FEEDBACK_INCORRECT", "Incorrect")
KH_FEEDBACK_DATA_LABEL = os.environ.get("KH_FEEDBACK_DATA_LABEL", "Was data retrieved sufficient?")
KH_FEEDBACK_DATA_SUFFICIENT = os.environ.get("KH_FEEDBACK_DATA_SUFFICIENT", "Sufficient")
KH_FEEDBACK_DATA_INSUFFICIENT = os.environ.get("KH_FEEDBACK_DATA_INSUFFICIENT", "Insufficient")

USE_NANO_GRAPHRAG = config("USE_NANO_GRAPHRAG", default=False, cast=bool)
USE_LIGHTRAG = config("USE_LIGHTRAG", default=False, cast=bool)
USE_MS_GRAPHRAG = config("USE_MS_GRAPHRAG", default=False, cast=bool)

GRAPHRAG_INDEX_TYPES = []

if USE_MS_GRAPHRAG:
    GRAPHRAG_INDEX_TYPES.append("ktem.index.file.graph.GraphRAGIndex")
if USE_NANO_GRAPHRAG:
    GRAPHRAG_INDEX_TYPES.append("ktem.index.file.graph.NanoGraphRAGIndex")
if USE_LIGHTRAG:
    GRAPHRAG_INDEX_TYPES.append("ktem.index.file.graph.LightRAGIndex")

KH_INDEX_TYPES = [
    "ktem.index.file.FileIndex",
    *GRAPHRAG_INDEX_TYPES,
]

GRAPHRAG_INDICES = [
    {
        "name": (graph_type.split(".")[-1].replace("Index", "")
        + " Collection" if (
            graph_type != "ktem.index.file.graph.NanoGraphRAGIndex" 
            and not KH_RENAME_UI)
            else "Knowledge"
            ),  # get last name
        "config": {
            "max_file_size": 100000,
            "chunk_size": 500,
            "chunk_overlap": 100,
            "supported_file_types": (
                ".png, .jpeg, .jpg, .tiff, .tif, .pdf, .xls, .xlsx, .doc, .docx, "
                ".pptx, .csv, .html, .mhtml, .txt, .md, .zip"
            ),
            "private": False,
        },
        "index_type": graph_type,
    }
    for graph_type in GRAPHRAG_INDEX_TYPES
]

KH_INDICES = [
    {
        "name": "Documents",
        "config": {
            "max_file_size": 100000,
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "supported_file_types": (
                ".png, .jpeg, .jpg, .tiff, .tif, .pdf, .xls, .xlsx, .doc, .docx, "
                ".pptx, .csv, .html, .mhtml, .txt, .md, .zip"
            ),
            "private": False,
        },
        "index_type": "ktem.index.file.FileIndex",
    },
    *GRAPHRAG_INDICES,
]

# Add these to SETTINGS_APP to make them available throughout the application
SETTINGS_APP = {
    "feedback": {
        "name": "Feedback Settings",
        "value": "",
        "component": "text",
        "settings": {
            "correctness_label": {
                "name": "Feedback Correctness Label",
                "value": KH_FEEDBACK_CORRECTNESS_LABEL,
                "component": "text"
            },
            "correct_label": {
                "name": "Correct Feedback Label",
                "value": KH_FEEDBACK_CORRECT,
                "component": "text"
            },
            "incorrect_label": {
                "name": "Incorrect Feedback Label",
                "value": KH_FEEDBACK_INCORRECT,
                "component": "text"
            },
            "data_label": {
                "name": "Data Feedback Label",
                "value": KH_FEEDBACK_DATA_LABEL,
                "component": "text"
            },
            "data_sufficient": {
                "name": "Data Sufficient Label",
                "value": KH_FEEDBACK_DATA_SUFFICIENT,
                "component": "text"
            },
            "data_insufficient": {
                "name": "Data Insufficient Label",
                "value": KH_FEEDBACK_DATA_INSUFFICIENT,
                "component": "text"
            }
        }
    }
}
