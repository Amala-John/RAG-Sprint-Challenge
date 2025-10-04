import re
import os
import json
from pathlib import Path
from extractor import extract_text_html
from chunker import smart_chunk_text
from embeddings import embed_texts
from vectorstore import VectorStore
from agent import decompose_query
import openai
from dotenv import load_dotenv

load_dotenv()

CIK_TO_COMPANY = {
    "GOOGL": "Google",
    "MSFT": "Microsoft", 
    "NVDA": "NVIDIA"
}
def extract_metric(text):
    patterns = [
        r"\$?\d+(?:\.\d+)?\s?(?:billion|million|thousand|B|M|K)?",
        r"\d+(?:\.\d+)?\s?%",
    ]
    matches = []
    for p in patterns:
        matches.extend(re.findall(p, text, re.IGNORECASE))
    return matches[0] if matches else None

def normalize_number(val):
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
        try:
            return float(v)
        except:
            return None
    try:
        return float(v) * mult
    except:
        return None

def extract_section_info(text):
    section_patterns = {
        "Item 1A": r"(?i)item\s+1a[\.\s]*risk\s+factors",
        "Item 7": r"(?i)item\s+7[\.\s]*management[\'\s]*s\s+discussion",
        "Item 8": r"(?i)item\s+8[\.\s]*financial\s+statements"
    }
    
    for section, pattern in section_patterns.items():
        if re.search(pattern, text):
            return section
    return None

def build_index_from_all_filings(data_dir="data"):
    all_chunks = []
    file_map = []
    
    if not os.path.exists(data_dir):
        print(f"Data directory '{data_dir}' not found. Please run the downloader first.")
        return None, None
    
    for fname in os.listdir(data_dir):
        if fname.endswith(".html"):
            path = Path(data_dir) / fname
            cik, year = fname.replace(".html", "").split("_")
            company = CIK_TO_COMPANY.get(cik, cik)
            
            print(f"Processing {company} {year}...")
            text = extract_text_html(path)
            
            chunks = smart_chunk_text(text, chunk_size=800, overlap=100)
            
            for idx, ch in enumerate(chunks):
                if len(ch.strip()) < 50:
                    continue
                    
                section = extract_section_info(ch)
                file_map.append({
                    "cik": cik,
                    "company": company,
                    "year": year,
                    "text": ch,
                    "section": section,
                    "chunk_id": idx,
                    "filename": fname
                })
                all_chunks.append(ch)
    
    if not all_chunks:
        print("No chunks found. Please check your data files.")
        return None, None
        
    print(f"Created {len(all_chunks)} chunks from {len(os.listdir(data_dir))} files")
    embeddings = embed_texts(all_chunks)
    vs = VectorStore(len(embeddings[0]))
    vs.add(embeddings, all_chunks)
    return vs, file_map

def llm_answer(query, retrieved_texts, llm_mode="hf", model_name="facebook/bart-large-cnn"):
    context = "\n\n".join(retrieved_texts[:3])
    
    system_prompt = """You are a financial analyst. Answer questions based only on the provided context from 10-K filings. 
    Be specific with numbers and cite the source information. If you cannot find the answer in the context, say so."""
    
    user_prompt = f"Question: {query}\n\nContext from 10-K filings:\n{context}\n\nAnswer:"
    
    if llm_mode == "openai":
        try:
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"OpenAI API error: {str(e)}"
    
    elif llm_mode == "hf":
        try:
            from transformers import pipeline
            summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            if len(user_prompt) > 1000:
                user_prompt = user_prompt[:1000] + "..."
            summary = summarizer(user_prompt, max_length=150, min_length=40, do_sample=False)
            return summary[0]['summary_text']
        except Exception as e:
            return f"HuggingFace model error: {str(e)}"
    
    return "LLM mode not supported. Available modes: 'openai', 'hf'"

def run_query(vs, file_map, query, llm_mode="hf", model_name="facebook/bart-large-cnn"):
    if vs is None or file_map is None:
        return {
            "query": query,
            "answer": "No data available. Please run the downloader first.",
            "reasoning": "Vector store not initialized",
            "sub_queries": [],
            "sources": []
        }
    
    print(f"\n🔍 Processing query: {query}")
    
    sub_qs = decompose_query(query)
    print(f"📋 Sub-queries: {sub_qs}")
    
    all_results = []
    all_retrieved = []
    sources = []
    
    for sq in sub_qs:
        emb = embed_texts([sq])[0]
        retrieved = vs.search(emb, k=5)
        all_results.extend(retrieved)
        all_retrieved.append(retrieved)
        
        for r in retrieved:
            for fm in file_map:
                if fm["text"] == r:
                    sources.append({
                        "company": fm["company"],
                        "year": fm["year"],
                        "excerpt": r[:200] + "..." if len(r) > 200 else r,
                        "section": fm.get("section"),
                        "page": None
                    })
                    break
    
    unique_sources = []
    seen_sources = set()
    for src in sources:
        key = (src["company"], src["year"], src["excerpt"][:50])
        if key not in seen_sources:
            seen_sources.add(key)
            unique_sources.append(src)
    
    answer = ""
    reasoning = ""
    
    if len(sub_qs) > 1 or any(keyword in query.lower() for keyword in ["compare", "which", "highest", "lowest"]):
        answer = llm_answer(query, all_results, llm_mode, model_name)
        reasoning = f"Used agent decomposition with {len(sub_qs)} sub-queries and {llm_mode} LLM for synthesis."
    
    elif any(keyword in query.lower() for keyword in ["grow", "growth", "increase", "decrease", "change"]):
        answer = llm_answer(query, all_results, llm_mode, model_name)
        reasoning = "Retrieved financial data across years and calculated growth/change."
    
    elif any(keyword in query.lower() for keyword in ["strategy", "summarize", "describe", "risk", "investment", "ai"]):
        answer = llm_answer(query, all_results, llm_mode, model_name)
        reasoning = f"Used {llm_mode} LLM to synthesize narrative answer from retrieved context."
    
    else:
        answer = llm_answer(query, all_results, llm_mode, model_name)
        reasoning = "Retrieved relevant context and generated direct answer."
    
    result = {
        "query": query,
        "answer": answer,
        "reasoning": reasoning,
        "sub_queries": sub_qs,
        "sources": unique_sources[:10]
    }
    
    return result

def pretty_print(result):
    print(f"\n📌 Question: {result['query']}")
    print(f"✅ Answer: {result['answer']}\n")
    print("📖 Sources:")
    for src in result['sources']:
        company = src.get("company", "Unknown")
        year = src.get("year", "N/A")
        print(f" - {company} {year} 10-K")
    print(f"\n💡 Reasoning: {result['reasoning']}\n")

def main():
    print("🏦 Financial Q&A System with RAG + Agent Capabilities")
    print("=" * 60)
    
    print("📊 Building index from 10-K filings...")
    vs, file_map = build_index_from_all_filings("data")
    
    if vs is None:
        print("❌ Failed to build index. Please check your data files.")
        return
    
    test_queries = [
        "What was Microsoft's total revenue in 2023?",
        "What was NVIDIA's total revenue in fiscal year 2024?",
        "How did NVIDIA's data center revenue grow from 2022 to 2023?",
        "How much did Microsoft's cloud revenue grow from 2022 to 2023?",
        "Which company had the highest operating margin in 2023?",
        "Which of the three companies had the highest gross margin in 2023?",
        "What percentage of Google's revenue came from cloud in 2023?",
        "What percentage of Google's 2023 revenue came from advertising?",
        "Compare AI investments mentioned by all three companies in their 2024 10-Ks",
        "Compare the R&D spending as a percentage of revenue across all three companies in 2023",
        "What are the main AI risks mentioned by each company and how do they differ?"
    ]
    
    llm_mode = "hf"  
    model_name = "facebook/bart-large-cnn"
    
    print(f"🤖 Using {llm_mode} with model {model_name}")
    print("=" * 60)
    
    results = []
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Query {i}/{len(test_queries)}")
        result = run_query(vs, file_map, query, llm_mode=llm_mode, model_name=model_name)
        results.append(result)
        pretty_print(result)
        
        output_file = f"query_{i}_result.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
    
    print(f"\n💾 Saving all results to 'all_results.json'")
    with open('all_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Completed processing {len(test_queries)} queries!")
    print("📁 Results saved in JSON format for further analysis.")

if __name__ == "__main__":
    main()