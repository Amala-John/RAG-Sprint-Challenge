import re
from extractor import extract_text_html
from chunker import chunk_text
from embeddings import embed_texts
from agent import decompose_query
from vectorstore import VectorStore
from pathlib import Path
import os

def extract_metric(text):
    """Extract numeric financial metric (%, $B, $M, raw numbers)."""
    patterns = [
        r"\$?\d+(?:\.\d+)?\s?(?:billion|million|thousand|B|M|K)?",
        r"\d+(?:\.\d+)?\s?%",
    ]
    matches = []
    for p in patterns:
        matches.extend(re.findall(p, text, re.IGNORECASE))
    return matches[0] if matches else None

def normalize_number(val):
    """Convert $X billion/million/percent to float for calculations."""
    if val is None:
        return None
    v = val.lower().replace("$", "").replace(",", "").strip()
    mult = 1
    if "billion" in v or v.endswith("b"):
        mult = 1e9
        v = v.replace("billion", "").replace("b", "")
    elif "million" in v or v.endswith("m"):
        mult = 1e6
        v = v.replace("million", "").replace("m", "")
    elif "thousand" in v or v.endswith("k"):
        mult = 1e3
        v = v.replace("thousand", "").replace("k", "")
    elif "%" in v:
        v = v.replace("%", "")
        return float(v)
    try:
        return float(v) * mult
    except:
        return None

def build_index_from_all_filings(data_dir="data"):
    all_chunks = []
    file_map = []
    for fname in os.listdir(data_dir):
        if fname.endswith(".html"):
            path = Path(data_dir) / fname
            cik, year = fname.replace(".html", "").split("_")
            text = extract_text_html(path)
            chunks = chunk_text(text, 500, 50)
            for ch in chunks:
                all_chunks.append(ch)
                file_map.append({"cik": cik, "year": year, "text": ch})
    embeddings = embed_texts(all_chunks)
    vs = VectorStore(len(embeddings[0]))
    vs.add(embeddings, all_chunks)
    return vs, file_map

def run_query(vs, file_map, query):
    sub_qs = decompose_query(query)
    results = []
    for q in sub_qs:
        emb = embed_texts([q])[0]
        retrieved = vs.search(emb, k=3)
        results.extend(retrieved)

    sources = []
    seen = set()
    metrics = {}
    for r in results:
        for fm in file_map:
            if fm["text"] == r:
                key = (fm["cik"], fm["year"])
                if key not in seen:
                    seen.add(key)
                    raw_metric = extract_metric(r)
                    norm_val = normalize_number(raw_metric)
                    metrics[key] = norm_val
                    sources.append({
                        "company": fm["cik"],
                        "year": fm["year"],
                        "excerpt": r[:150],
                        "page": None
                    })
                break

    answer = ""
    reasoning = ""
    if "grow" in query.lower() or "increase" in query.lower():
        if len(metrics) >= 2:
            years = sorted(metrics.keys(), key=lambda x: x[1])
            vals = [metrics[y] for y in years]
            if all(vals):
                growth = (vals[1] - vals[0]) / vals[0] * 100
                answer = f"{years[0][0]} revenue grew from {vals[0]:,.0f} in {years[0][1]} to {vals[1]:,.0f} in {years[1][1]} ({growth:.1f}%)."
                reasoning = "Calculated year-over-year growth using retrieved values."
    elif "highest" in query.lower() or "compare" in query.lower():
        if metrics:
            best = max(metrics.items(), key=lambda x: x[1] or 0)
            answer = f"{best[0][0]} had the highest value ({best[1]:,.1f}) in {best[0][1]}."
            reasoning = "Compared values across companies and selected the maximum."
    else:
        answer = "; ".join([f"{c} {y}: {v:,.1f}" for (c, y), v in metrics.items() if v])
        reasoning = "Retrieved direct values from filings."

    return {
        "query": query,
        "answer": answer,
        "reasoning": reasoning,
        "sub_queries": sub_qs,
        "sources": sources
    }

def pretty_print(result):
    print(f"\n📌 Question: {result['query']}")
    print(f"✅ Answer: {result['answer']}\n")
    
    print("📖 Sources:")
    for src in result['sources']:
        company = src.get("company", "Unknown")
        year = src.get("year", "N/A")
        print(f" - {company} {year} 10-K")

    print(f"\n💡 Reasoning: {result['reasoning']}\n")

if __name__ == "__main__":
    vs, file_map = build_index_from_all_filings("data")
    queries = [
        "What was Microsoft's total revenue in 2023?",
        "How did NVIDIA’s data center revenue grow from 2022 to 2023?",
        "Which company had the highest operating margin in 2023?",
        "What percentage of Google’s revenue came from cloud in 2023?",
        "Compare AI investments mentioned by all three companies in their 2024 10-Ks"
    ]
    for q in queries:
        ans = run_query(vs, file_map, q)
        pretty_print(ans)
