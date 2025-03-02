from elasticsearch import Elasticsearch, helpers
import os
import csv
import tqdm

DATASET_PATH = "data/cv-valid-dev.csv"


def download_dataset():
    if not os.path.exists(DATASET_PATH):
        print("dataset not found, exiting")
        exit(1)
    # -1 because the first line is the header
    return len(open(DATASET_PATH).readlines()) - 1


def generate_actions():
    """Reads the file through csv.DictReader() and for each row
    yields a single document. This function is passed into the bulk()
    helper to create many documents in sequence.
    """
    with open(DATASET_PATH) as f:
        reader = csv.DictReader(f)

        for row in reader:
            doc = {
                "_id": row["filename"],
                "filename": row["filename"],
                "text": row["text"],
                "up_votes": row["up_votes"],
                "down_votes": row["down_votes"],
                "age": row["age"],
                "gender": row["gender"],
                "duration": row["duration"],
            }

            yield doc


def create_index(client: Elasticsearch, index_name: str):
    """Creates an index in Elasticsearch if one isn't already there."""
    client.indices.create(
        index=index_name,
        body={
            "settings": {"number_of_shards": 1},
            "mappings": {
                "properties": {
                    "filename": {"type": "text"},
                    "text": {"type": "text"},
                    "up_votes": {"type": "integer"},
                    "down_votes": {"type": "integer"},
                    "age": {"type": "text"},
                    "gender": {"type": "text"},
                    "duration": {"type": "float"},
                }
            },
        },
        ignore=400,
    )


def main():
    print("Loading dataset...")
    number_of_docs = download_dataset()
    print(f"Number of documents to index: {number_of_docs}")

    ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")

    # get the current directory of this file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Create the client instance
    client = Elasticsearch(
        "https://localhost:9200",
        ca_certs=os.path.join(current_dir, "ca.crt"),
        basic_auth=("elastic", ELASTIC_PASSWORD)
    )

    print('Connected to Elasticsearch')
    # {'name': 'instance-0000000000', 'cluster_name': ...}
    print(client.info())

    index_name = "cv-transcriptions"

    create_index(client, index_name)

    print(f"Indexing documents into {index_name}...")
    progress = tqdm.tqdm(unit="docs", total=number_of_docs)
    successes = 0
    for ok, action in helpers.streaming_bulk(
        client=client, index=index_name, actions=generate_actions(),
    ):
        progress.update(1)
        successes += ok
    print("Indexed %d/%d documents" % (successes, number_of_docs))


if __name__ == "__main__":
    if os.getenv("ELASTIC_PASSWORD") is None:
        print("ELASTIC_PASSWORD is not set, exiting")
        exit(1)
    main()
