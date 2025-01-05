from llama_index.core import VectorStoreIndex, load_index_from_storage
from llama_index.core import StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq

from core.utils import configure_logging, initialize_settings

from config.settings import INDEX_STORAGE, GROQ_API_KEY, VECTOR_DB_PATH

import asyncio
import nest_asyncio
from llama_index.core import Settings
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore

async def get_or_create_vector_store(storage_path: str=VECTOR_DB_PATH, collection_name: str="index_collection"):

    logger = await asyncio.to_thread(configure_logging)
    nest_asyncio.apply()

    try:

        db = chromadb.PersistentClient(path=storage_path)
        chroma_collection = db.get_or_create_collection(collection_name)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

        return vector_store

    except Exception as e:

        logger.warning(f"Error occurred while loading vector store: {e}")

        return None

async def build_indexes(nodes):

    logger = await asyncio.to_thread(configure_logging)
    nest_asyncio.apply()

    try:

        embedding_model, llm = await asyncio.to_thread(initialize_settings)

        Settings.llm = llm
        Settings.embed_model = embedding_model

        vector_store = await get_or_create_vector_store()

        if vector_store is not None:

            storage_context = StorageContext.from_defaults(vector_store=vector_store)

            vector_index = await asyncio.to_thread(
                VectorStoreIndex, 
                nodes, 
                storage_context=storage_context, 
                embed_model=embedding_model
            )

            logger.info("New indexes created and persisted.")
        
        else:

            logger.warning("Vector store not found. Index creation failed.")

        return vector_index

    except Exception as e:

        logger.warning(f"Error occurred while loading and creating indices: {e}")

        return None
    
    
async def load_vector_index():

    logger = await asyncio.to_thread(configure_logging)
    nest_asyncio.apply()

    try:

        embedding_model, llm = await asyncio.to_thread(initialize_settings)

        Settings.llm = llm
        Settings.embed_model = embedding_model

        vector_store = await get_or_create_vector_store()
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        index = await asyncio.to_thread(
            VectorStoreIndex.from_vector_store,
            vector_store=vector_store,
            storage_context=storage_context,
            embed_model=embedding_model
        )

        return index
    
    except Exception as e:
        
        logger.warning(f"Error occurred while loading vector index: {e}")

        return None
