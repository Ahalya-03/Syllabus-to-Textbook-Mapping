import re
import json
import os

# def get_syllabus_from_user(json_path="processed/syllabus.json"):
#     """
#     Prompts the user to enter the entire syllabus as a block of text.
#     Automatically extracts and structures the syllabus into individual topics.

#     Returns:
#         list of dict: Each dict contains 'source' and 'text' keys.
#     """
#     print("\nPaste your entire syllabus content below.")
#     print("Type 'done' on a new line when you are finished.\n")

#     # Collect multi-line input
#     syllabus_lines = []
#     while True:
#         line = input()
#         if line.strip().lower() == "done":
#             break
#         syllabus_lines.append(line.strip())

#     # Combine lines into a single string
#     syllabus_text = " ".join(syllabus_lines)

#     # Normalize spaces
#     syllabus_text = re.sub(r'\s+', ' ', syllabus_text)

#     # Split on common delimiters like '-', '.', or ';' followed by space
#     raw_topics = re.split(r'\s*[-.;]\s*', syllabus_text)

#     # Clean up and remove empty strings
#     topics = [topic.strip() for topic in raw_topics if topic.strip()]

#     # Convert to structured format with source info
#     # Wrap as dict for JSON compatibility
#     syllabus_data = [{"source": "syllabus", "text": t} for t in topics]

#     # Save JSON (overwrite each run)
#     with open(json_path, "w", encoding="utf-8") as f:
#         json.dump(syllabus_data, f, indent=2, ensure_ascii=False)

#     # Print numbered list
#     print("\nStructured Syllabus:")
#     for i, topic in enumerate(topics, start=1):
#         print(f"{i}. {topic}")
#     print("\nSaved syllabus to", json_path)

#     return syllabus_data

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def process_syllabus_from_text(syllabus_text):
    """
    Processes syllabus text provided directly (no console input),
    extracts individual topics, and saves them to JSON.
    """

    # Normalize spaces
    syllabus_text = re.sub(r'\s+', ' ', syllabus_text)

    json_path = os.path.join(ROOT_DIR, "processed", "syllabus.json")

    # Split into topics
    raw_topics = re.split(r'\s*[-.;]\s*', syllabus_text)
    topics = [t.strip() for t in raw_topics if t.strip()]

    # Create dict structure
    syllabus_data = [{"source": "syllabus", "text": t} for t in topics]

    # Save JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(syllabus_data, f, indent=2, ensure_ascii=False)

    #print(syllabus_data)

    return syllabus_data



def display_syllabus(topics):
    """Prints a numbered list of syllabus topics."""
    print("\nStructured Syllabus:")
    for i, t in enumerate(topics, start=1):
        print(f"{i}. {t['text']}")
    print("\n")


def main():
    syllabus_data = process_syllabus_from_text()
    display_syllabus(syllabus_data)
    # Now syllabus_data can be merged with textbook data for vectorization


if __name__ == "__main__":
    main()
