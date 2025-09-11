from embeddings import embed_texts
from vectorstore import VectorStore

def decompose_query(query):
    if "compare" in query.lower() or "which" in query.lower():
        return [q.strip() for q in query.split("?") if q.strip()]
    return [query]

def synthesize(query, sub_results):
    return {
        "query": query,
        "answer": " | ".join([r[:100] for r in sub_results]),
        "reasoning": "Retrieved relevant chunks and combined.",
        "sub_queries": sub_results,
        "sources": [{"company": "demo", "year": "demo", "excerpt": r[:80], "page": None} for r in sub_results]
    }
