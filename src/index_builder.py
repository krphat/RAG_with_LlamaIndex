from llama_index.core import VectorStoreIndex, load_index_from_storage
from llama_index.core import StorageContext
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq

from src.global_settings import INDEX_STORAGE
from src.env import GROQ_API_KEY

import torch

def build_indexes(nodes):

    try:

        storage_context = StorageContext.from_defaults(
            persist_dir=INDEX_STORAGE
        )
        vector_index = load_index_from_storage(
            storage_context
        )
        print("--> All indices loaded from storage...")

    except Exception as e:

        print(f"--> Error occurred while loading indices: {e}")

        storage_context = StorageContext.from_defaults()

        # Set LLM and Embedding model
        llm = Groq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

        device_type = "cuda" if torch.cuda.is_available() else "cpu"
        local_embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2", device=device_type)

        Settings.llm = llm
        Settings.embed_model = local_embed_model

        vector_index = VectorStoreIndex(
            nodes, storage_context=storage_context, embed_model=local_embed_model
        )

        storage_context.persist(
            persist_dir=INDEX_STORAGE
        )
        print("New indexes created and persisted.")

    return vector_index