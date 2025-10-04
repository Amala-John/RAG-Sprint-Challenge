
import re

def smart_chunk_text(text, chunk_size=800, overlap=100):
    if not text or not text.strip():
        return []
    
    text = re.sub(r'\s+', ' ', text.strip())
    
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    
    for para in paragraphs:
        if not para.strip():
            continue
            
        if len(para) <= chunk_size:
            chunks.append(para.strip())
            continue
        
        sentences = re.split(r'(?<=[.!?])\s+', para)
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if current_length + len(sentence) > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                
                if overlap > 0 and len(current_chunk) > 1:
                    overlap_sentences = []
                    overlap_length = 0
                    for i in range(len(current_chunk) - 1, -1, -1):
                        if overlap_length + len(current_chunk[i]) <= overlap:
                            overlap_sentences.insert(0, current_chunk[i])
                            overlap_length += len(current_chunk[i])
                        else:
                            break
                    current_chunk = overlap_sentences
                    current_length = overlap_length
                else:
                    current_chunk = []
                    current_length = 0
            
            current_chunk.append(sentence)
            current_length += len(sentence)
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
    
    return [c for c in chunks if len(c.strip()) >= 200]
