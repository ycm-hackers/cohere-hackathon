"""Push SEC filings to Weaviate."""
import glob
import json
import os
import sys
import time
from tqdm import tqdm

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
                    "name": "orgText",
                    "dataType": ["text"],
                    "description": "Original text of the document.",
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


def read_json_document(
    dir_path: str = "data/10k", ff: str = "*.json", continue_from: int = 0
):
    """Reads document and pushes data to weaviate db."""
    for idx, file in enumerate(glob.glob(os.path.join(dir_path, ff))):
        if idx < continue_from:
            continue
        with open(file, "r") as f:
            print(f"Reading file: {file}")
            yield json.loads(f.read())


def store_to_weaviate(
    continue_from: int = 0,
    chunk_size: int = 8184,
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
    doc = read_json_document(continue_from=continue_from)
    try:
        while True:
            next_doc = next(doc)

            txt = "".join(next_doc[k] for k in relevant_keys if k in next_doc)
            for i in tqdm(range(0, len(txt), chunk_size)):
                try:
                    response = co_client.embed(
                        model="small", texts=[txt[i : i + chunk_size]]
                    )
                    emb = response.embeddings[0]
                except Exception as e:
                    print(e, "\nWaiting for 60s.")
                    time.sleep(60_000)

                data_object = {
                    "class": "DocText",
                    "vector": emb,
                    "orgText": txt[i : i + chunk_size],
                    "cik": next_doc["cik"],
                    "source": next_doc["htm_filing_link"],
                }
                weaviate_client.data_object.create(data_object, "DocText")
    except StopIteration:
        pass


def count_chunks(
    chunk_size: int = 8184,
    continue_from: int = 0,
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
    """Count the number of text chunks."""
    res = 0
    doc = read_json_document(continue_from=continue_from)
    try:
        while True:
            next_doc = next(doc)

            txt = "".join(next_doc[k] for k in relevant_keys if k in next_doc)
            for i in range(0, len(txt), chunk_size):
                res += 1
    except StopIteration:
        pass
    return res


def find_nn_token(query: str, k: int = 1) -> list:
    """Return the response vector to query.

    :param query: Input query string.
    :param k: Number of k like in k-nearest neighbors.
        Define the number of results that get returned by the db query.
    :return: Response Dict.
    """
    resp = co_client.embed(model="small", texts=[query])
    query_vector = resp.embeddings[0]

    result = (
        weaviate_client.query.get("DocText", ["vector", "orgText", "cik", "source"])
        .with_additional(["id"])
        .with_near_vector({"vector": query_vector})
        .with_limit(k)
        .do()
    )
    try:
        res = result["data"]["Get"]["DocText"]
        return res
    except KeyError:
        print("No results found.")
        return []


def augment_prompt(query: str, k: int = 3):
    """Augment the prompt with the best retrievals."""
    res = find_nn_token(query, k=3)
    source_knowledge = "\n".join([x["orgText"] for x in res])

    augmented_prompt = f"""Using the contexts below, answer the query.
    Contexts:
    {source_knowledge}
    Query: {query}"""
    return augmented_prompt


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
        store_to_weaviate(continue_from=args.continue_from)
    if args.test:
        res = find_nn_token("What did lattice do in 2021?", k=3)
        [print(f"{x['orgText']}\n") for x in res]
