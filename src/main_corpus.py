import json
import os

def load_textbooks():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # src/
    json_full_path = os.path.join(base_dir, "..", "processed", "toc_data.json")
    json_full_path = os.path.normpath(json_full_path)

    if not os.path.exists(json_full_path):
        print(f"Error: JSON file not found at {json_full_path}")
        return []

    with open(json_full_path, "r", encoding="utf-8") as f:
        textbooks = json.load(f)
    
    converted = []
    for book_title, toc_entries in textbooks.items():
        for entry in toc_entries:
            title = entry.get("title", "").strip()
            if title:
                converted.append({"source": book_title, "text": title})

    return converted



def load_syllabus():
    """
    Loads syllabus topics from JSON.
    Returns a list of dicts with 'source' and 'text'.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_full_path = os.path.join(base_dir, "..", "processed", "syllabus.json")
    json_full_path = os.path.normpath(json_full_path)

    if not os.path.exists(json_full_path):
        print(f"Error: Syllabus JSON not found at {json_full_path}")
        return []

    with open(json_full_path, "r", encoding="utf-8") as f:
        syllabus = json.load(f)

    cleaned_syllabus = []
    for entry in syllabus:
        text = entry.get("text", "").strip()
        source = entry.get("source", "syllabus")
        if text:
            cleaned_syllabus.append({"source": source, "text": text})

    print("\nSyllabus sample:")
    for t in cleaned_syllabus[:5]:
        print(f"[{t['source']}] {t['text']}")

    return cleaned_syllabus

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def build_similarity_matrix(corpus):
    # Extract text only
    texts = [item["text"] for item in corpus]

    # 1. Vectorize with TF-IDF
    vectorizer = TfidfVectorizer(stop_words="english")  
    tfidf_matrix = vectorizer.fit_transform(texts)

    print(f"TF-IDF matrix shape: {tfidf_matrix.shape}")  
    # (num_docs, num_features)

    # 2. Cosine similarity
    similarity_matrix = cosine_similarity(tfidf_matrix)

    print("\nSample cosine similarity (first 5x5):")
    print(similarity_matrix[:5, :5])

    return similarity_matrix, tfidf_matrix, vectorizer

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Map full textbook titles → short names
BOOK_SHORTNAMES = {
    "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow": "ML_Book",
    "Reinforcement Learning: An Introduction": "RL_Book",
    # add more as needed...
}

def get_short_name(full_name):
    if full_name in BOOK_SHORTNAMES:
        return BOOK_SHORTNAMES[full_name]
    return "_".join(full_name.split()[:2])  # fallback: first 2 words

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def match_syllabus_to_textbooks(syllabus, textbooks, vectorizer, top_n=3, threshold=0.0):
    syllabus_texts = [s["text"] for s in syllabus]
    textbook_texts = [t["text"] for t in textbooks]

    tfidf_syllabus = vectorizer.transform(syllabus_texts)
    tfidf_textbooks = vectorizer.transform(textbook_texts)

    sim_matrix = cosine_similarity(tfidf_syllabus, tfidf_textbooks)

    results = []
    for i, syllabus_entry in enumerate(syllabus):
        scores = sim_matrix[i]

        # Filter based on threshold
        valid_indices = np.where(scores >= threshold)[0]

        # If no match meets threshold → keep the best one anyway
        if len(valid_indices) == 0:
            valid_indices = np.argsort(scores)[::-1][:1]

        # Sort and take top-N
        sorted_indices = valid_indices[np.argsort(scores[valid_indices])[::-1]]
        top_indices = sorted_indices[:top_n]

        matches=[]

        for idx in top_indices:
            matches.append({
                "textbook_topic": textbook_texts[idx],
                "source": textbooks[idx]["source"],   # full source, not short name
                "book_index": idx,                    # <-- IMPORTANT
                "score": scores[idx]
            })


        best_score = scores[top_indices[0]]

        results.append({
            "syllabus": syllabus_entry["text"],
            "highest_score": best_score,
            "matches": matches
        })

    return results

def print_matches(results):
    for res in results:
        print(f"📌 Syllabus Topic: {res['syllabus']}")
        print(f"  Highest Score: {res['highest_score']:.3f}\n")
        print("  Top 3 Textbook Matches:")

        for m in res["matches"]:
            print(f"  - {m['textbook_topic']} ({m['source']}) (Score: {m['score']:.3f})")

        print("\n" + "-" * 80 + "\n")

def highlight_unmatched(results, threshold):
    return [r for r in results if r["highest_score"] < threshold]



def main():
    syllabus_data = load_syllabus()
    textbook_data = load_textbooks()
    combined_corpus = syllabus_data + textbook_data

    texts = [item["text"] for item in combined_corpus]
    vectorizer = TfidfVectorizer(stop_words="english")
    vectorizer.fit(texts)

    results = match_syllabus_to_textbooks(syllabus_data, textbook_data, vectorizer, top_n=3)
    print_matches(results)

    # # Now check for unmatched topics
    # unmatched = highlight_unmatched(results, threshold=0.2)
    # if unmatched:
    #     print("\n⚠️  Unmatched syllabus topics (low similarity):")
    #     for u in unmatched:
    #         print(f"- {u['syllabus']} (best score {u['highest_score']:.3f})")
    # else:
    #     print("\n✅  All syllabus topics have good matches!")


if __name__ == "__main__":
    main()
