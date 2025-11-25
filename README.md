# 📘 Syllabus–Textbook Mapping System

Automatically map syllabus topics to relevant textbook chapters using TF-IDF & Cosine Similarity.

---

## 🔍 Overview

In higher education, students often rely on multiple reference textbooks while studying from a syllabus that does not clearly indicate where specific topics are located. This system bridges that gap by **automatically mapping syllabus topics to related textbook sections**, saving significant lookup time for students and assisting instructors while designing syllabus structures.

---

## ✨ Features

* **Upload or paste syllabus text**
  → Automatically extracts individual syllabus topics using delimiters (`-`, `.`, `;`).

* **Extract textbook Table of Contents (TOC) from PDFs**
  → Processes multiple textbooks and stores their chapter/section titles.

* **TF-IDF Vectorization + Cosine Similarity**
  → Computes similarity scores between each syllabus topic and every textbook section.

* **Top-N Matches**
  → Returns top 3 most relevant chapter titles for each topic.

* **Gap Topic Detection**
  → Topics with similarity score below threshold (e.g., 0.20) are flagged as unmatched.

* **Textbook Ranking Metrics**
  → Precision, Recall, F1-score, and total hits computed per textbook.

* **Streamlit UI**
  → Simple interface to input syllabus, load textbooks, run mapping, and view results.

---

## 📁 Project Structure

```
project-root/
│
├── src/
│   ├── syllabus_loader.py
│   ├── textbook_scanner.py
│   ├── main_corpus.py
│   ├── app.py                 # Streamlit frontend
│
├── data/
│   └── textbooks/             # Store textbook PDFs here
│
├── processed/
│   ├── syllabus.json          # Extracted syllabus topics
│   ├── toc_data.json          # Saved textbook TOCs
│
└── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone this repository

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

### 2️⃣ Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Streamlit App

```bash
streamlit run src/app.py
```

The app will open in your browser.
From there you can:

1. Paste syllabus text
2. Load textbook PDFs
3. Run TF-IDF and similarity matching
4. View mapping + gap topics + textbook ranking

---

## 📊 Methodology Summary

### **1. Syllabus Extraction**

* User pastes syllabus text
* Automatic splitting using `-`, `;`, `.`
* Saved as structured JSON

### **2. Textbook TOC Extraction**

* PDF TOCs parsed using PyPDF
* Stored as chapter/section entries
* Merged into uniform format for matching

### **3. TF-IDF Vectorization**

* Unified corpus = syllabus topics + textbook TOC titles
* Convert text into numerical vectors

### **4. Cosine Similarity**

* Compute similarity between each syllabus topic and every textbook topic

### **5. Threshold-Based Mapping**

* Top-K matches selected
* Topics with scores below threshold → gap topics

---

## 📌 Example Output (Simplified)

### **Top Matches**

```
Text Classification →
  - Clustering and classification (Score: 0.602, TB3)
  - Hypertext classification (Score: 0.588, TB3)
```

### **Gap Topics**

```
Stop word removal — Score 0.298
N-gram language models — Score 0.402
```

### **Textbook Ranking**

```
TB3: Precision 0.698 | Hits: 5
TB1: Precision 0.605 | Hits: 4
TB2: Precision 0.729 | Hits: 1
```

---

## 📝 Notes

Results vary depending on the syllabus and textbooks used as input.
The example results shown in documentation correspond to the sample syllabus and textbooks used during testing.

---


## 👩‍💻 Future Enhancements

* BERT / SentenceTransformer semantic similarity
* Full-text extraction instead of TOC only
* Interactive visualizations
* API endpoints for integration into LMS systems

---


https://github.com/user-attachments/assets/624a960b-f81b-47ab-9eef-8a1951513478
