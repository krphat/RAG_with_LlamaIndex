from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings

import torch
import logging

from config.settings import GROQ_API_KEY

def configure_device():

    return "cuda" if torch.cuda.is_available() else "cpu"


def initialize_settings():

    device_type = configure_device()
    print(f"--> Running on device: {device_type}")

    embedding_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2", device=device_type
    )

    llm = Groq(model="gemma2-9b-it", api_key=GROQ_API_KEY, temperature=0.2, device_type=device_type)
    
    return embedding_model, llm


def configure_logging():

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)

    return logger