import streamlit as st
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import torch
import re

def simple_sentence_split(text):
    # Basic sentence splitter using regex
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


# Load cleaned context
def load_chunks(file_path, chunk_size=300):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

st.title(" IITK Chatbot")
st.markdown("Ask me anything about IIT Kanpur ")

chunks = load_chunks("cleaned_context.txt")
embedder = SentenceTransformer("all-MiniLM-L6-v2")
chunk_embeddings = embedder.encode(chunks, convert_to_tensor=True)
qa_model = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

question = st.text_input("Your Question:")

if question:
    
    import os
    

    # Step 1: Find best chunk
    q_emb = embedder.encode(question, convert_to_tensor=True)
    scores = util.cos_sim(q_emb, chunk_embeddings)[0]
    best_idx = torch.argmax(scores).item()
    best_chunk = chunks[best_idx]

    try:
        # Step 2: Ask the model
        result = qa_model(question=question, context=best_chunk)
        raw_answer = result.get("answer", "").strip()

        # Step 3: Extract full sentence + next sentence
        sentences = simple_sentence_split(best_chunk)

        matched_sentences = []
        for i, sent in enumerate(sentences):
            if raw_answer in sent:
                matched_sentences.append(sent.strip())
                if i + 1 < len(sentences):
                    matched_sentences.append(sentences[i + 1].strip())
                break

        final_answer = " ".join(matched_sentences) if matched_sentences else raw_answer

        # Limit to 400 chars
        if len(final_answer) > 400:
            final_answer = final_answer[:400].strip() + "..."

        st.markdown("#### ✅ Answer:")
        st.success(final_answer or "Sorry, I couldn’t find a good answer.")

    except Exception as e:
        st.error(f"⚠️ Model error: {e}")
