"""Retrieval-Augmented Generation (RAG) module."""
import cohere
import weaviate


def retrieve(
    query: str, co_client: cohere.Client, weaviate_client: weaviate.Client, k: int = 3
) -> list:
    """Return the response vectors to query.

    :param query: Input query string.
    :param k: Number of k like in k-nearest neighbors.
        Define the number of results that get returned by the db query.
    :return: Response list of dicts.
        Single dict contains the keys: { _additional:  { id }, orgText, cik, source }.
    """
    resp = co_client.embed(model="small", texts=[query])
    query_vector = resp.embeddings[0]
    result = (
        weaviate_client.query.get("DocText", ["orgText", "cik", "source"])
        .with_additional(["id"])
        .with_near_vector({"vector": query_vector})
        .with_limit(k)
        .do()
    )
    try:
        return result["data"]["Get"]["DocText"]
    except KeyError:
        return []


def augment_prompt(
    query: str,
    co_client: cohere.Client,
    weaviate_client: weaviate.Client,
    k: int = 3,
    use_rerank: bool = False,
) -> str:
    """Augment the prompt with the best retrievals."""
    res = retrieve(query, co_client, weaviate_client, k=k)

    if use_rerank:
        rerank_docs = co_client.rerank(
            query=query,
            documents=[x["orgText"] for x in res],
            top_n=k,
            model="rerank-english-v2.0",
        )
        context = "".join(rerank_docs.results[0].document["text"])
    else:
        context = res[0]["orgText"]

    return f"""Using the contexts below, answer the query. Contexts: {context} Query: {query} source: {res[0]['source']}"""
