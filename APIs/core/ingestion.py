from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.core.extractors import TitleExtractor
from llama_parse import LlamaParse
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
import asyncio
import os

from config.settings import CACHE_FILE
from config.prompts import CUSTOM_TITLE_NODE_TEMPLATE, CUSTOM_TITLE_COMBINE_TEMPLATE
from core.utils import configure_logging, initialize_settings
from config.settings import LLAMA_CLOUD_API_KEY, GROQ_API_KEY
import nest_asyncio
from llama_index.core import Settings

from tenacity import retry, stop_after_attempt, wait_exponential


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=10))
async def process_documents_with_retries(pipeline, documents):

    return await pipeline.arun(documents=documents)

async def ingest_documents(file_path:str):

    try:

        nest_asyncio.apply()

        logger = await asyncio.to_thread(configure_logging)
        
        embedding_model, llm = await asyncio.to_thread(initialize_settings)

        Settings.llm = llm
        Settings.embed_model = embedding_model

        os.environ["LLAMA_CLOUD_API_KEY"] = LLAMA_CLOUD_API_KEY

        parser = LlamaParse(result_type="text")
        file_extractor = {".pdf": parser}

        documents = SimpleDirectoryReader(
            input_files=[file_path],
            filename_as_id=True,
            file_extractor=file_extractor
        ).load_data()

        for doc in documents:
            logger.info(f"Processing document: {doc.id_}")

        try:
            cached_hashes = IngestionCache.from_persist_path(CACHE_FILE)
            logger.info("Cache file found. Running using cache...")

        except FileNotFoundError:
            cached_hashes = ""
            logger.info("No cache file found. Running without cache...")

        pipeline = IngestionPipeline(
            transformations=[
                SemanticSplitterNodeParser(
                    buffer_size=1,
                    breakpoint_percentile_threshold=95,
                    embed_model=embedding_model
                ),
                TitleExtractor(nodes=5, node_template=CUSTOM_TITLE_NODE_TEMPLATE, combine_template=CUSTOM_TITLE_COMBINE_TEMPLATE),
                embedding_model
            ],
            cache = cached_hashes
        )

        nodes = pipeline.run(documents=documents)

        pipeline.cache.persist(CACHE_FILE)

        return nodes
    
    except Exception as e:
        logger.error(f"Error during document ingestion: {e}")
        
        return None

