"""Push SEC filings to Weaviate."""
import os
import sys
import glob
import json
import cohere
import weaviate
from dotenv import load_dotenv

from tools.utils import create_arg_parser

# Get the secrets
load_dotenv()
weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
weaviate_url = os.getenv("WEAVIATE_URL")
co_api_key = os.getenv("COHERE_API_KEY")

weaviate_client = weaviate.Client(
    url=weaviate_url,
    auth_client_secret=weaviate.AuthApiKey(api_key=weaviate_api_key),
    additional_headers={
        "X-Cohere-Api-Key": co_api_key,
    },
)
co_client = cohere.Client(co_api_key)


SCHEMA = {
    "classes": [
        {
            "class": "DocText",
            "description": "Store document information as vectors with minimal metadata.",
            "vectorizer": "text2vec-cohere",
            "vectorIndexConfig": {"distance": "cosine"},
            "properties": [
                {
                    "name": "vector",
                    "dataType": ["number[]"],
                    "description": "Vector embedding",
                },
                {
                    "name": "cik",
                    "dataType": ["text"],
                    "description": "Cik associated with the vector.",
                },
                {
                    "name": "source",
                    "dataType": ["text"],
                    "description": "html link of the document.",
                },
            ],
        }
    ]
}


def read_json_document(dir_path: str = "data/10k", ff: str = "*.json"):
    """Reads document and pushes data to weaviate db."""
    for file in glob.glob(os.path.join(dir_path, ff)):
        with open(file, "r") as f:
            print(f"Reading file: {file}")
            yield json.loads(f.read())


def store_to_weaviate(
    token_limit: int = 1024,
    relevant_keys: list = [
        "item_1",
        "item_1A",
        "item_1B",
        "item_2",
        "item_3",
        "item_4",
        "item_5",
        "item_6",
        "item_7",
        "item_7A",
        "item_8",
        "item_9",
        "item_9A",
        "item_9B",
        "item_10",
        "item_11",
        "item_12",
        "item_13",
        "item_14",
        "item_15",
    ],
):
    """Store data to weaviate."""
    doc = read_json_document()
    try:
        while True:
            next_doc = next(doc)

            txt = "".join(next_doc[k] for k in relevant_keys if k in next_doc)

            for i in range(0, len(txt), token_limit):
                response = co_client.embed(
                    model="small", texts=[txt[i : i + token_limit]]
                )
                emb = response.embeddings[0]

                data_object = {
                    "class": "DocText",
                    "vector": emb,
                    "cik": next_doc["cik"],
                    "source": next_doc["htm_filing_link"],
                }

                weaviate_client.data_object.create(data_object, "DocText")
            break
    except StopIteration:
        pass


def find_nn_token(query: str) -> dict:
    """Return the response vector to query."""
    resp = co_client.embed(
        model="small", texts=["What is lattice semiconductors doing?"]
    )
    query_vector = resp.embeddings[0]

    result = (
        weaviate_client.query.get("DocText", ["cik", "vector", "source"])
        .with_near_vector({"vector": query_vector})
        .with_limit(1)
        .do()
    )
    try:
        res = result["data"]["Get"]["DocText"]
        return res[0]
    except KeyError:
        print("No results found.")


if __name__ == "__main__":
    arg_parser = create_arg_parser()
    args = arg_parser.parse_args(sys.argv[1:])

    if args.schema:
        import yaml

        print("Creating schema.\n", yaml.dump(SCHEMA, default_flow_style=False))
        weaviate_client.schema.create(SCHEMA)
        exit()

    if args.delete:
        weaviate_client.schema.delete_all()
        exit()

    if args.store:
        store_to_weaviate()

    res = find_nn_token("What has Apple been doing in 2022?")
    print(res)
