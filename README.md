# Financial Q&A System with RAG + Agent Capabilities

This project implements a focused **Retrieval-Augmented Generation (RAG)** system with **basic agent capabilities** to answer financial questions about **Google (GOOGL)**, **Microsoft (MSFT)**, and **NVIDIA (NVDA)** using their **10-K filings (2022–2024)**.

---

## Features
- ✅ **Data Acquisition**: Automatic downloader for SEC EDGAR 10-K filings (2022–2024).  
- ✅ **RAG Pipeline**:
  - Text extraction and chunking (200–1000 tokens)
  - Embedding with OpenAI/Sentence Transformers
  - In-memory vector search (FAISS/Chroma optional)  
- ✅ **Agent Query Engine**:
  - Query decomposition (breaks complex queries into sub-queries)
  - Multi-step retrieval across multiple companies/years
  - Synthesis into final answers  
- ✅ **Output Format**:
  Returns structured JSON with:
  - query
  - answer
  - reasoning
  - sub_queries
  - sources (company, year, excerpt, page)

---

## Example Queries

```bash

"What was Microsoft's total revenue in 2023?"

"How did NVIDIA’s data center revenue grow from 2022 to 2023?"

"Which company had the highest operating margin in 2023?"

"What percentage of Google’s revenue came from cloud in 2023?"

"Compare AI investments mentioned by all three companies in their 2024 10-Ks"


# Example output 
{
  "query": "Which company had the highest operating margin in 2023?",
  "answer": "Microsoft had the highest operating margin at 42.1% in 2023, followed by Google at 29.8% and NVIDIA at 29.6%.",
  "reasoning": "Retrieved operating margins for all three companies from their 2023 10-K filings and compared values.",
  "sub_queries": [
    "Microsoft operating margin 2023",
    "Google operating margin 2023",
    "NVIDIA operating margin 2023"
  ],
  "sources": [
    {"company": "MSFT", "year": "2023", "excerpt": "Operating margin was 42.1%...", "page": 10},
    {"company": "GOOGL", "year": "2023", "excerpt": "Operating margin of 29.8%...", "page": 42},
    {"company": "NVDA", "year": "2023", "excerpt": "We achieved operating margin of 29.6%...", "page": 37}
  ]
}
