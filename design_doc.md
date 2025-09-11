
---

## 📄 design_doc.md  

```markdown
# Design Document – Financial Q&A RAG System

## 1. Chunking Strategy
- Each 10-K filing is parsed into plain text.
- Text is split into **chunks of 500–1000 tokens** with overlaps.
- This ensures coherent retrieval and prevents context loss.

## 2. Embedding Model Choice
- **Sentence Transformers (open-source)** or **OpenAI Embeddings** used.
- Chosen for:
  - Strong performance on semantic similarity
  - Low setup complexity
  - Free/open alternatives available

## 3. Agent / Query Decomposition
- **Simple function-based agent**:
  - If query contains comparative language ("highest", "compare", "growth"), it is decomposed into sub-queries.
  - Each sub-query is independently retrieved from the vector store.
  - Results are synthesized into a structured JSON answer.

Example:
Query: "Which company had the highest operating margin in 2023?"
Sub-queries:

"Microsoft operating margin 2023"

"Google operating margin 2023"

"NVIDIA operating margin 2023"

## 4. Multi-Step Retrieval and Synthesis
- Each sub-query is embedded and matched against the vector DB.
- Top-k chunks are returned with metadata (company, year, excerpt).
- Agent logic computes comparisons (e.g., growth %, highest margin).
- Final result is a JSON object with:
  - query, answer, reasoning, sub_queries, sources.

## 5. Challenges & Decisions
- **Table parsing** in 10-Ks is complex → skipped (bonus, not required).
- Ensured **output explainability** via JSON with sources + reasoning.
- Implemented a **lightweight in-memory vector store** to keep repo simple.
- Focused on **agent orchestration correctness** over exact financial accuracy.

## 6. Deliverables
- ✅ 9 filings (GOOGL/MSFT/NVDA × 2022–2024)
- ✅ CLI interface (`main.py`)
- ✅ RAG pipeline
- ✅ Agent query decomposition
- ✅ JSON answers with sources
- ✅ README + this design doc
