import streamlit as st
from syllabus_loader import process_syllabus_from_text
from textbook_scanner import process_textbooks
from main_corpus import load_syllabus, load_textbooks, match_syllabus_to_textbooks, highlight_unmatched
import pandas as pd
import matplotlib.pyplot as plt


from sklearn.feature_extraction.text import TfidfVectorizer

st.title("📘 Syllabus–Textbook Mapping System")

# --------------------------
# 1. Enter Syllabus
# --------------------------

st.header("1. Enter Syllabus")
syllabus_text = st.text_area("Paste the entire syllabus and click submit:")

if st.button("Extract Syllabus Topics", key="extract_syllabus"):
    syllabus_data = process_syllabus_from_text(syllabus_text)
    st.success("Syllabus topics extracted and saved.")
    
    st.subheader("📄 Extracted Syllabus Topics")

    if syllabus_data:
        for idx, item in enumerate(syllabus_data, start=1):
            st.write(f"**{idx}. {item['text'].capitalize()}**")




# --------------------------
# 2. Process Textbooks
# --------------------------

st.header("2. Process Textbooks")

if st.button("Scan Textbooks", key="scan_textbooks"):
    process_textbooks()
    st.success("Textbooks scanned and TOC extracted.")

    from main_corpus import load_textbooks
    scanned_textbooks = load_textbooks()



# --------------------------
# 3. Generate Mapping
# --------------------------

st.header("3. Generate Mapping")

threshold = st.slider("Similarity Threshold", 0.0, 1.0, 0.5, 0.01)
top_n = st.number_input("Top-N Matches", 1, 10, 3)

if st.button("Run Mapping", key="run_mapping"):
    syllabus = load_syllabus()
    textbooks = load_textbooks()

    combined = syllabus + textbooks
    texts = [item["text"] for item in combined]

    vectorizer = TfidfVectorizer(stop_words="english")
    vectorizer.fit(texts)

    results = match_syllabus_to_textbooks(
        syllabus,
        textbooks,
        vectorizer,
        top_n=top_n,
        threshold=threshold
    )

    # ---------- helper: normalize source names ----------
    def normalize_source(name):
        if not isinstance(name, str):
            name = str(name)
        name = name.replace(".pdf", "")
        name = name.split("/")[-1]
        name = name.split("\\")[-1]
        return name.strip()

    # Build short names for textbooks (from the loaded textbooks list)
    unique_books = sorted({normalize_source(t["source"]) for t in textbooks})
    book_short_map = {name: f"TB{idx+1}" for idx, name in enumerate(unique_books)}

    # Display textbook key
    st.subheader("📘 Textbook Key")
    for full_name in unique_books:
        st.write(f"**{book_short_map[full_name]}** → {full_name}")

    # SPLIT RESULTS
    matched_results = [r for r in results if r["highest_score"] >= threshold]
    gap_topics = [r for r in results if r["highest_score"] < threshold]

    # Show matched results (use normalized source when showing)
    st.header("📘 Mapping Results (Above Threshold)")
    for res in matched_results:
        st.subheader(res["syllabus"].capitalize())
        st.write(f"Highest Score: {res['highest_score']:.3f}")

        for m in res["matches"]:
            src_norm = normalize_source(m.get("source", m.get("source", "")))
            short = book_short_map.get(src_norm, src_norm)  # fall back to norm name
            st.write(f"- **{m['textbook_topic']}** ({m['score']:.3f}) — *{short}*")
        st.write("---")

    # Gap Topics (below threshold)
    st.header("🚨 Gap Topics (Below Threshold)")
    if gap_topics:
        for g in gap_topics:
            st.warning(f"{g['syllabus'].capitalize()} — score {g['highest_score']:.3f}")
    else:
        st.success("No gap topics! All topics meet the threshold. 🎉")

    # ---------- Textbook Relevance Ranking (IR Metrics) ----------
    st.header("📚 Textbook Relevance Ranking (IR Metrics)")

    # Normalize source names
    def normalize_source(name):
        if not isinstance(name, str):
            name = str(name)
            name = name.replace(".pdf", "")
            name = name.split("/")[-1]
            name = name.split("\\")[-1]
        return name.strip()

    # Build ranking dictionary at textbook level
    ranking = {}
    for t in textbooks:
        src = normalize_source(t["source"])
        ranking[src] = {
            "hits": 0,
            "total_score": 0.0,
            "highest": 0.0
        }

    # Aggregate chapter matches into textbook totals
    for res in matched_results:
        for m in res["matches"]:
            src_norm = normalize_source(m.get("source", ""))

            if src_norm not in ranking:
                continue  # skip unmatched or weird entries

            score = float(m.get("score", 0.0))

            ranking[src_norm]["hits"] += 1
            ranking[src_norm]["total_score"] += score
            ranking[src_norm]["highest"] = max(ranking[src_norm]["highest"], score)

    total_topics = len(syllabus)

    # Convert to ranking_list with Precision, Recall, F1
    ranking_list = []
    for full_name, stats in ranking.items():
        if stats["hits"] > 0:

            recall = stats["hits"] / total_topics
            precision = stats["total_score"] / stats["hits"]

            f1 = (2 * precision * recall / (precision + recall)) if (precision + recall > 0) else 0.0

            ranking_list.append({
                "full": full_name.replace(".pdf",""),                "hits": stats["hits"],
                "precision": round(precision, 3),
                "recall": round(recall, 3),
                "f1": round(f1, 3),
                "highest": round(stats["highest"], 3)
            })

    # Sort by best F1
    ranking_list = sorted(ranking_list, key=lambda x: -x["f1"])

    # Display nicely
    if ranking_list:
        for idx, item in enumerate(ranking_list, start=1):
            st.markdown(
                f"""
                **{idx}. {item['full']}**  
                - Precision: **{item['precision']}**  
                - Recall: **{item['recall']}**  
                - F1-Score: **{item['f1']}**  
                - Hits: **{item['hits']}**  
                - Highest Match Score: **{item['highest']}**  
                """
            )
    else:
        st.info("No textbook relevance statistics available.")

# ---------- Prepare DataFrame ----------
    if ranking_list:
        df = pd.DataFrame(ranking_list)

        # Ensure a stable sort order (by hits then avg), descending (already sorted earlier)
        df = df.sort_values(by="hits", ascending=False).reset_index(drop=True)

        # Short label + full name as hover text
        df["label"] = df["full"].apply(
            lambda x: " ".join(x.replace("_", " ").split()[:3]).title()
        )


        st.subheader("📊 Textbook Relevance Charts")

        # --- MAIN GRAPH: Normalized Coverage Score ---
        st.markdown("### ⭐ Normalized Coverage Score")
        fig, ax = plt.subplots(figsize=(max(10, len(df) ), 8))
        ax.bar(df["label"], df["hits"])
        ax.set_ylabel("Number of Hits")
        ax.set_xlabel("Textbook")
        for i, v in enumerate(df["hits"]):
            ax.text(i, v + 0.01, v, ha='center')
        st.pyplot(fig)

    else:
        st.info("No textbook ranking data to plot.")



