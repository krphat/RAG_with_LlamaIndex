from src import ingest_pipeline, index_builder

def main():

    nodes = ingest_pipeline.ingest_documents()
    vector_index = index_builder.build_indexes(nodes)

    print("~~~> It's Phary on the code, Yahhhh!")
    print("~~~> Welcome to my world!")

if __name__ == "__main__":
    main()