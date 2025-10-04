# Financial Q&A System with RAG + Agent Capabilities

 **AI Engineering Assignment: RAG Sprint Challenge**

This project implements a focused **Retrieval-Augmented Generation (RAG)** system with **agent capabilities** to answer financial questions about **Google (GOOGL)**, **Microsoft (MSFT)**, and **NVIDIA (NVDA)** using their **10-K filings (2022–2024)**.

##  Quick Start

### 1. Setup Environment
```bash
# Clone the repository
git clone https://github.com/your-username/rag-financial-qa.git
cd rag-financial-qa

# Install dependencies
pip install -r requirements.txt

# Set up OpenAI API key (optional - system works with HuggingFace as fallback)
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

### 2. Download SEC Filings
```bash
# Download all required 10-K filings automatically
python src/downloader.py
```

### 3. Run the System
```bash
# Run the main Q&A system
python src/main.py
```

## 📋 Features

### ✅ **Data Acquisition**
- Automatic SEC EDGAR 10-K filing downloader
- Companies: Google (CIK: 1652044), Microsoft (789019), NVIDIA (1045810)
- Years: 2022, 2023, 2024 (9 total documents)
- Respectful rate limiting for SEC servers

### ✅ **RAG Pipeline**
- **Text Extraction**: HTML parsing with BeautifulSoup
- **Smart Chunking**: Sentence/paragraph-aware chunking (200-1000 tokens)
- **Embeddings**: Sentence Transformers (`all-MiniLM-L6-v2`)
- **Vector Store**: FAISS in-memory index for fast retrieval

### ✅ **Agent Capabilities**
- **Query Decomposition**: Breaks complex queries into sub-queries
- **Multi-step Retrieval**: Handles comparative and cross-company analysis
- **Synthesis**: LLM-powered answer generation with reasoning

### ✅ **Supported Query Types**

1. **Basic Metrics**
   ```
   "What was Microsoft's total revenue in 2023?"
   ```

2. **YoY Comparison**
   ```
   "How did NVIDIA's data center revenue grow from 2022 to 2023?"
   ```

3. **Cross-Company Analysis**
   ```
   "Which company had the highest operating margin in 2023?"
   ```

4. **Segment Analysis**
   ```
   "What percentage of Google's revenue came from cloud in 2023?"
   ```

5. **Complex Multi-step**
   ```
   "Compare AI investments mentioned by all three companies in their 2024 10-Ks"
   ```

## 📊 Sample Output

```json
{
  "query": "Which company had the highest operating margin in 2023?",
  "answer": "Microsoft had the highest operating margin at 42.1% in 2023, followed by Google at 29.8% and NVIDIA at 29.6%.",
  "reasoning": "Used agent decomposition with 3 sub-queries and openai LLM for synthesis.",
  "sub_queries": [
    "microsoft operating margin 2023",
    "google operating margin 2023", 
    "nvidia operating margin 2023"
  ],
  "sources": [
    {
      "company": "Microsoft",
      "year": "2023",
      "excerpt": "Operating margin was 42.1% compared to 37.7% in fiscal year 2022...",
      "section": "Item 7"
    }
  ]
}
```

## 🏗️ Architecture

```
User Query → Agent Decomposition → Multi-step Retrieval → LLM Synthesis → JSON Response
```

### Core Components

- **`downloader.py`**: SEC EDGAR filing downloader with CIK codes
- **`extractor.py`**: HTML text extraction using BeautifulSoup
- **`chunker.py`**: Smart paragraph/sentence-aware chunking
- **`embeddings.py`**: Sentence transformer embedding generation
- **`vectorstore.py`**: FAISS-based vector similarity search
- **`agent.py`**: Query decomposition and multi-step reasoning
- **`main.py`**: Main system orchestration and LLM integration

## 🔧 Configuration

### LLM Options
```python
# In main.py, configure your preferred LLM:
llm_mode = "openai"          # Uses GPT-3.5-turbo (requires API key)
# llm_mode = "hf"            # Uses HuggingFace BART (free, offline)
```

### Chunking Parameters
```python
# In chunker.py:
chunk_size = 800      # Target chunk size (200-1000 token range)  
overlap = 100         # Overlap between chunks for context
```

## 📁 Project Structure

```
rag-financial-qa/
├── src/
│   ├── main.py           # Main system entry point
│   ├── downloader.py     # SEC filing downloader
│   ├── agent.py          # Query decomposition logic
│   ├── chunker.py        # Smart text chunking
│   ├── embeddings.py     # Embedding generation
│   ├── vectorstore.py    # Vector similarity search
│   └── extractor.py      # Text extraction utilities
├── data/                 # Downloaded 10-K filings (created by downloader)
├── requirements.txt      # Python dependencies
├── design_doc.md         # Technical design document
└── README.md            # This file
```

## 🎯 Assignment Requirements Met

- ✅ **Data Acquisition**: Automated SEC EDGAR downloader
- ✅ **RAG Pipeline**: Complete text processing and retrieval
- ✅ **Agent Capabilities**: Query decomposition and multi-step reasoning
- ✅ **Output Format**: Structured JSON with sources and reasoning
- ✅ **Query Types**: All 5 required patterns supported
- ✅ **Clean Code**: Modular architecture with clear separation
- ✅ **Documentation**: README + design document

## 🚦 Usage Examples

```python
# After running python src/main.py, the system processes these queries:

test_queries = [
    "What was Microsoft's total revenue in 2023?",
    "How did NVIDIA's data center revenue grow from 2022 to 2023?", 
    "Which company had the highest operating margin in 2023?",
    "What percentage of Google's revenue came from cloud in 2023?",
    "Compare AI investments mentioned by all three companies in their 2024 10-Ks"
]
```

## 🔍 How It Works

1. **Query Analysis**: Agent analyzes the query pattern
2. **Decomposition**: Complex queries broken into sub-queries  
3. **Retrieval**: Each sub-query retrieves relevant document chunks
4. **Synthesis**: LLM combines context into coherent answer
5. **Response**: Structured output with sources and reasoning

## 💡 Technical Highlights

- **Smart Chunking**: Preserves paragraph/sentence boundaries
- **Multi-hop Retrieval**: Handles comparative questions across companies/years
- **Metadata Enrichment**: Tracks company, year, section for each chunk
- **Graceful Degradation**: Works with partial data, indicates missing info
- **Extensible Design**: Easy to add new LLMs or improve components

## 🛠️ Troubleshooting

### No data files found
```bash
# Make sure to run the downloader first:
python src/downloader.py
```

### OpenAI API errors
```python
# Switch to HuggingFace mode in main.py:
llm_mode = "hf"
```

### Memory issues
```python
# Reduce chunk retrieval in main.py:
retrieved = vs.search(emb, k=3)  # Reduce from k=5 to k=3
```

## 📈 Performance

- **Setup Time**: ~2-3 minutes (download + indexing)
- **Query Speed**: 2-5 seconds per query
- **Memory Usage**: ~50-100MB for embeddings + index
- **Accuracy**: Depends on document relevance and LLM quality
