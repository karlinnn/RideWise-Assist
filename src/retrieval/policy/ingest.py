import os
import json
from pypdf import PdfReader

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DEFAULT_DATA_DIR = os.path.join(_PROJECT_ROOT, "data", "policies")
DEFAULT_OUTPUT_DIR = os.path.join(_PROJECT_ROOT, "storage", "policy_index")

def extract_chunks_from_pdf(filepath, chunk_size=300, overlap=50):
    reader = PdfReader(filepath)
    filename = os.path.basename(filepath)
    chunks = []
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if not text:
            continue
            
        words = text.split()
        for j in range(0, len(words), chunk_size - overlap):
            chunk_words = words[j:j + chunk_size]
            if not chunk_words:
                break
            chunk_text = " ".join(chunk_words)
            chunks.append({
                "filename": filename,
                "page": i + 1,
                "text": chunk_text
            })
            if j + chunk_size >= len(words):
                break
    return chunks

def build_index(data_dir=None, output_dir=None):
    if data_dir is None:
        data_dir = DEFAULT_DATA_DIR
    elif not os.path.isabs(data_dir):
        data_dir = os.path.join(_PROJECT_ROOT, data_dir)
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    elif not os.path.isabs(output_dir):
        output_dir = os.path.join(_PROJECT_ROOT, output_dir)

    all_chunks = []
    if not os.path.exists(data_dir):
        print(f"Data directory {data_dir} does not exist.")
        return
        
    for fname in os.listdir(data_dir):
        if fname.lower().endswith(".pdf"):
            fpath = os.path.join(data_dir, fname)
            try:
                all_chunks.extend(extract_chunks_from_pdf(fpath))
                print(f"Indexed {fname}")
            except Exception as e:
                print(f"Failed to read {fname}: {e}")
                
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "chunks.json"), "w", encoding="utf-8") as f:
        json.dump(all_chunks, f)
