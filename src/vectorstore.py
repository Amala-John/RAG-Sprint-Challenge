import faiss
import numpy as np

class VectorStore:
    def __init__(self, dim):
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []

    def add(self, embeddings, texts):
        self.index.add(np.array(embeddings).astype('float32'))
        self.texts.extend(texts)

    def search(self, query_emb, k=3):
        D, I = self.index.search(np.array([query_emb]).astype('float32'), k)
        results = []
        for idx in I[0]:
            if idx < len(self.texts):
                results.append(self.texts[idx])
        return results
