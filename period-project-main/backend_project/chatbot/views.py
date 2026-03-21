# backend_project/chatbot/views.py
import os
import json
import pandas as pd
from functools import lru_cache

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from sentence_transformers import SentenceTransformer
import faiss
from transformers import pipeline

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_PATH = os.path.join(DATA_DIR, "train24K.csv")
INDEX_PATH = os.path.join(DATA_DIR, "faiss_index.idx")
META_PATH = os.path.join(DATA_DIR, "meta.json")

# Load embeddings, FAISS index, and dataset safely (lazy-loaded on first request)

@lru_cache(maxsize=1)
def _load_resources():
    """Load the FAISS index, embeddings model, and dataset on demand."""

    if not (os.path.exists(INDEX_PATH) and os.path.exists(META_PATH) and os.path.exists(CSV_PATH)):
        print("⚠ FAISS index, metadata, or CSV not found. Chatbot will not work until files are in place.")
        return None, None, None

    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH) as f:
        meta = json.load(f)
    embedder = SentenceTransformer(meta["embedding_model"])
    df = pd.read_csv(CSV_PATH)[['Question', 'Answer']].dropna().reset_index(drop=True)
    return index, embedder, df

@lru_cache(maxsize=1)
def _load_generator():
    """Load the text generation model on demand."""
    try:
        generator = pipeline("text-generation", model="gpt2", max_length=200, truncation=True)
        return generator
    except Exception as e:
        print(f"⚠ Could not load generator: {e}")
        return None

def search_answers(query, top_k=6):
    index, embedder, df = _load_resources()
    if index is None or embedder is None or df is None:
        return []

    q_emb = embedder.encode([query], convert_to_numpy=True).astype('float32')
    faiss.normalize_L2(q_emb)
    D, I = index.search(q_emb, top_k)

    results = []
    for score, idx in zip(D[0], I[0]):
        if idx < len(df):
            results.append({
                "question": df.iloc[idx]['Question'],
                "answer": df.iloc[idx]['Answer'],
                "score": float(score)
            })
    return results

def _best_answer_for_question(question: str, results: list[dict]) -> str | None:
    """Choose the best single answer from a list of candidates."""
    if not results:
        return None
    return results[0].get("answer", "").strip()

def _generate_response(question: str, context: str) -> str:
    """Generate a response using the provided context (Strictly for Research)."""
    generator = _load_generator()
    if generator is None:
        return context 

    prompt = (
        f"Instructions: Using ONLY the provided context, answer the user question. "
        f"Do NOT mention articles, links, emails, or 'checking below'. Keep it factual.\n\n"
        f"Context: {context}\n"
        f"Question: {question}\n"
        f"Answer:"
    )
    
    try:
        # Even stricter parameters for GPT-2 to keep it grounded
        output = generator(
            prompt,
            max_new_tokens=60,       # Shorter is safer
            num_return_sequences=1,
            do_sample=True,
            temperature=0.2,         # Extremely low for "factuality"
            top_k=20,
            top_p=0.8,
            repetition_penalty=1.5,
            no_repeat_ngram_size=3,
            return_full_text=False,
        )
        generated = output[0]["generated_text"].strip()

        # Cleanup
        if "Answer:" in generated:
            generated = generated.split("Answer:")[-1].strip()

        blacklist = ["see my article", "check below", "email here", "contact us", "click the link", "read more"]
        sentences = [s for s in generated.split(". ") if s.strip()]
        clean_sentences = [s for s in sentences if not any(p in s.lower() for p in blacklist)]
        generated = ". ".join(clean_sentences).strip()
        
        # No Research Tag as requested
        return generated if len(generated) > 10 else context[:300]
    except Exception as e:
        print(f"Generation error: {e}")
        return context

@api_view(["POST"])
@permission_classes([AllowAny])
def chatbot_response(request):
    """Hybrid RAG implementation with no labels/disclaimers."""
    user_question = request.data.get("message", "").strip()
    if not user_question:
        return Response({"error": "No question provided."}, status=400)

    results = search_answers(user_question)

    if not results:
        return Response({
            "reply": "I'm sorry, I don't have that information in my database."
        })

    top_result = results[0]
    top_score = top_result.get("score", 0)
    
    # Selective Logic
    CONFIDENCE_THRESHOLD = 0.70 
    generative_keywords = ["how", "why", "explain", "describe", "process"]
    is_generative_request = any(word in user_question.lower() for word in generative_keywords)

    if top_score >= CONFIDENCE_THRESHOLD:
        best_match = _best_answer_for_question(user_question, results)
        return Response({
            "reply": best_match,
            "source": "verified_retrieval",
            "confidence": round(top_score, 4)
        })
    elif is_generative_request:
        context_parts = [f"Knowledge {i+1}: {str(res.get('answer','')).strip()}" for i, res in enumerate(results[:3])]
        combined_context = "\n".join(context_parts)
        generated = _generate_response(user_question, combined_context)
        
        return Response({
            "reply": generated,
            "source": "generation",
            "confidence": round(top_score, 4)
        })
    else:
        return Response({
            "reply": results[0].get("answer", "I'm not sure. Please rephrase."),
            "source": "none",
            "confidence": round(top_score, 4)
        })
