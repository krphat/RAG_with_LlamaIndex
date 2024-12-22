from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.core.extractors import TitleExtractor
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from llama_parse import LlamaParse
from llama_index.llms.groq import Groq

from src.global_settings import FILES_PATH, CACHE_FILE
from src.env import LLAMA_CLOUD_API_KEY, GROQ_API_KEY
from src.prompts import CUSTOM_TITLE_NODE_TEMPLATE, CUSTOM_TITLE_COMBINE_TEMPLATE

import os
import torch

def ingest_documents():

    # Set LLM and Embedding model
    llm = Groq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

    device_type = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"--> Running on device: {device_type}")
    local_embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2", device=device_type)

    Settings.llm = llm
    Settings.embed_model = local_embed_model

    # Setting for LlamaParse
    os.environ["LLAMA_CLOUD_API_KEY"] = LLAMA_CLOUD_API_KEY
    parser = LlamaParse(result_type="text")
    file_extractor = {".pdf": parser}

    # Create documents from availabel file
    documents = SimpleDirectoryReader(
        input_files=FILES_PATH,
        filename_as_id=True,
        file_extractor=file_extractor
    ).load_data()
    
    for doc in documents:
        print(doc.id_)


    try:
        cached_hashes = IngestionCache.from_persist_path(CACHE_FILE)
        print("--> Cache file found. Running using cache...")
    except:
        cached_hashes = ""
        print("--> No cache file found. Running without cache...")

    pipeline = IngestionPipeline(
        transformations=[
            SemanticSplitterNodeParser(
                buffer_size=1,
                breakpoint_percentile_threshold=95,
                embed_model=local_embed_model
            ),
            TitleExtractor(nodes=3, node_template=CUSTOM_TITLE_NODE_TEMPLATE, combine_template=CUSTOM_TITLE_COMBINE_TEMPLATE),
            local_embed_model
        ],
        cache = cached_hashes
    )

    nodes = pipeline.run(documents=documents)
    pipeline.cache.persist(CACHE_FILE)

    return nodes