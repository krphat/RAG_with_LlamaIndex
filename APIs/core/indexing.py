from llama_index.core import VectorStoreIndex, load_index_from_storage
from llama_index.core import StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq

from core.utils import configure_logging, initialize_settings

from config.settings import INDEX_STORAGE, GROQ_API_KEY

import asyncio
import nest_asyncio
from llama_index.core import Settings

async def build_indexes(nodes):

    logger = await asyncio.to_thread(configure_logging)
    nest_asyncio.apply()

    try:

        storage_context = StorageContext.from_defaults(
            persist_dir=INDEX_STORAGE
        )
        
        vector_index = await asyncio.to_thread(load_index_from_storage, storage_context)

        logger.info("All indices loaded from storage...")

        await asyncio.to_thread(vector_index.insert_nodes, nodes)
        await asyncio.to_thread(vector_index.storage_context.persist, INDEX_STORAGE)

        logger.info("New indexes have been added!")

    except Exception as e:

        logger.warning(f"Error occurred while loading indices: {e}")

        storage_context = StorageContext.from_defaults()


        embedding_model, llm = await asyncio.to_thread(initialize_settings)

        Settings.llm = llm
        Settings.embed_model = embedding_model

        vector_index = await asyncio.to_thread(
            VectorStoreIndex, 
            nodes, 
            storage_context=storage_context, 
            embed_model=embedding_model
        )

        await asyncio.to_thread(storage_context.persist, persist_dir=INDEX_STORAGE)
        logger.info("New indexes created and persisted.")

    return vector_index