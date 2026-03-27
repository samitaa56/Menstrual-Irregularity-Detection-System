import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import json
import os

# Always points to the data folder inside the chatbot folder
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CSV_PATH = os.path.join(DATA_DIR, "train24K.csv")
EMB_PATH = os.path.join(DATA_DIR, "embeddings.npy")
INDEX_PATH = os.path.join(DATA_DIR, "faiss_index.idx")
META_PATH = os.path.join(DATA_DIR, "meta.json")

# Check if index exists AND is newer than the CSV
csv_mtime = os.path.getmtime(CSV_PATH) if os.path.exists(CSV_PATH) else 0
index_mtime = os.path.getmtime(INDEX_PATH) if os.path.exists(INDEX_PATH) else 0

if os.path.exists(EMB_PATH) and os.path.exists(INDEX_PATH) and index_mtime > csv_mtime:
    print("✅ Knowledge base is up to date. Loading embeddings and FAISS index...")
    embeddings = np.load(EMB_PATH)
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH) as f:
        meta = json.load(f)
    EMBED_MODEL_NAME = meta["embedding_model"]
else:
    if index_mtime <= csv_mtime and os.path.exists(INDEX_PATH):
        print("🔄 Knowledge base updated. Re-computing embeddings and rebuilding FAISS index...")
    else:
        print("🚀 First-time setup: Computing embeddings and building FAISS index...")
    df = pd.read_csv(CSV_PATH)
    df = df[['Question', 'Answer']].dropna().reset_index(drop=True)
    EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
    embedder = SentenceTransformer(EMBED_MODEL_NAME)
    questions = df['Question'].tolist()

    embeddings = embedder.encode(questions, show_progress_bar=True, convert_to_numpy=True).astype('float32')
    faiss.normalize_L2(embeddings)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    os.makedirs(DATA_DIR, exist_ok=True)
    np.save(EMB_PATH, embeddings)
    faiss.write_index(index, INDEX_PATH)

    meta = {
        "embedding_model": EMBED_MODEL_NAME,
        "csv_saved": "train24K.csv",
        "embeddings_file": "embeddings.npy",
        "faiss_index_file": "faiss_index.idx",
        "n_rows": len(df),
        "dim": dim
    }
    with open(META_PATH, "w") as f:
        json.dump(meta, f, indent=2)

    df.to_csv(os.path.join(DATA_DIR, "train24K_saved.csv"), index=False)

# Reload embedder
embedder = SentenceTransformer(EMBED_MODEL_NAME)

# Load dataframe to query answers
df = pd.read_csv(CSV_PATH)
df = df[['Question', 'Answer']].dropna().reset_index(drop=True)

# Example query test
query = "What to do if periods are missed for 3 months?"
q_emb = embedder.encode([query], convert_to_numpy=True).astype('float32')
faiss.normalize_L2(q_emb)
D, I = index.search(q_emb, 3)

print(f"Top 3 answers for: {query}\n")
for idx in I[0]:
    print("Q:", df.iloc[idx]['Question'])
    print("A:", df.iloc[idx]['Answer'])
    print("---")
