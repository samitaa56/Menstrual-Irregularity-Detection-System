import streamlit as st
import pandas as pd
import os
import json
from sentence_transformers import SentenceTransformer
import faiss

DATA_DIR = "./data"
CSV_PATH = os.path.join(DATA_DIR, "train24K.csv")
INDEX_PATH = os.path.join(DATA_DIR, "faiss_index.idx")
META_PATH = os.path.join(DATA_DIR, "meta.json")


@st.cache_resource(show_spinner=True)
def load_index_and_data():
    if not os.path.exists(INDEX_PATH):
        st.error("FAISS index file missing. Run embedding generation script first.")
        return None, None, None

    # Load FAISS index
    index = faiss.read_index(INDEX_PATH)

    # Load metadata
    with open(META_PATH) as f:
        meta = json.load(f)

    embedder = SentenceTransformer(meta["embedding_model"])

    # Load dataset
    df = pd.read_csv(CSV_PATH)
    df = df[['Question', 'Answer']].dropna().reset_index(drop=True)

    return index, embedder, df


def search_answers(query, index, embedder, df, top_k=3):
    # Encode query
    q_emb = embedder.encode([query], convert_to_numpy=True).astype('float32')
    faiss.normalize_L2(q_emb)

    # Search in FAISS
    D, I = index.search(q_emb, top_k)

    results = []
    for idx in I[0]:
        if idx < len(df):
            results.append({
                'question': df.iloc[idx]['Question'],
                'answer': df.iloc[idx]['Answer']
            })

    return results


def main():
    st.title("Women's Health Chatbot")
    st.write("Ask questions about periods, menstrual health, and related topics.")

    index, embedder, df = load_index_and_data()
    if index is None:
        return

    user_question = st.text_input("Ask your question about periods:")

    if user_question:
        results = search_answers(user_question, index, embedder, df)

        if results:
            st.markdown("### Chatbot Answer (from RAG)")
            for i, r in enumerate(results, 1):
                st.markdown(f"**Answer {i}:** {r['answer']}")

            # Optional: show retrieved questions
            with st.expander("Show retrieved questions"):
                for i, r in enumerate(results, 1):
                    st.markdown(f"- {r['question']}")

        else:
            st.write("No relevant answers found. Try rephrasing your question.")


if __name__ == "__main__":
    main()