import os
import json
from PyPDF2 import PdfReader

# Root of the entire project
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def extract_toc_from_pdf(pdf_path):
    """
    Extract Table of Contents (TOC) from a PDF (if available).
    """
    reader = PdfReader(pdf_path)
    toc = []

    # Some PDFs have no outline
    try:
        outlines = reader.outline
    except Exception:
        return []

    def parse_outline(outline, depth=0):
        for item in outline:
            if isinstance(item, list):
                parse_outline(item, depth + 1)
            else:
                title = item.title if hasattr(item, "title") else str(item)
                try:
                    page_num = reader.get_destination_page_number(item) + 1
                except Exception:
                    page_num = None
                toc.append({"depth": depth, "title": title, "page": page_num})

    parse_outline(outlines)
    return toc


def process_textbooks():
    """
    Scan all textbooks in /data/textbooks/
    and save the extracted TOC into /processed/toc_data.json.
    """

    # Absolute folder path
    folder = os.path.join(ROOT_DIR, "data", "textbooks")

    # Ensure folder exists
    if not os.path.isdir(folder):
        raise FileNotFoundError(f"Textbook folder not found: {folder}")

    # JSON save path
    save_path = os.path.join(ROOT_DIR, "processed", "toc_data.json")

    # Load existing data
    if os.path.exists(save_path):
        with open(save_path, "r", encoding="utf-8") as f:
            all_tocs = json.load(f)
    else:
        all_tocs = {}

    # Process each PDF
    for filename in os.listdir(folder):
        if filename.endswith(".pdf") and filename not in all_tocs:
            pdf_path = os.path.join(folder, filename)

            print(f"\n📖 Processing: {filename}")
            toc = extract_toc_from_pdf(pdf_path)

            all_tocs[filename] = toc

            if not toc:
                print("⚠️ No TOC found.")
            else:
                # Print TOC to console (optional)
                for entry in toc:
                    indent = "  " * entry["depth"]
                    page = f"(Page {entry['page']})" if entry["page"] else ""
                    print(f"{indent}- {entry['title']} {page}")

        elif filename in all_tocs:
            print(f"⏩ Skipping {filename} (already processed)")

    # Ensure processed folder exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Save updated JSON
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(all_tocs, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Updated TOC saved to: {save_path}")
    return all_tocs


if __name__ == "__main__":
    process_textbooks()
