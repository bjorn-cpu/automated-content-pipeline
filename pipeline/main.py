from pipeline.sheets import get_pending_topics, update_status, update_score, add_topic_to_sheet
from pipeline.llm import generate_content, score_content
from pipeline.drive import save_to_drive
from pipeline.sheets import get_pending_topics, update_status, update_score, add_topic_to_sheet, reset_error_rows

def run_pipeline():
    print("Starting content pipeline...")
    
    # Auto-retry any failed rows first
    reset_error_rows()
    
    topics = get_pending_topics()
    # ... rest stays the same

AUTO_TOPICS = [
    "The future of AI in education",
    "How blockchain is changing finance",
    "Climate tech innovations in 2026",
    "The rise of edge computing",
    "Mental health apps and AI therapy",
    "Quantum computing explained simply",
    "How 5G is transforming industries",
    "The ethics of facial recognition",
    "Renewable energy breakthroughs",
    "AI in healthcare diagnostics"
]

def generate_auto_topics():
    """Add a few auto topics to the sheet if none are pending."""
    import random
    topics = random.sample(AUTO_TOPICS, 3)
    for topic in topics:
        add_topic_to_sheet(topic)
    print(f"Auto-added {len(topics)} topics to Sheet1")

def run_pipeline():
    print("Starting content pipeline...")
    topics = get_pending_topics()

    if not topics:
        print("No pending topics — auto-generating...")
        generate_auto_topics()
        topics = get_pending_topics()

    for item in topics:
        topic = item["topic"]
        row = item["row"]
        print(f"Processing: {topic}")

        try:
            update_status(row, "processing")

            # Generate content
            content = generate_content(topic)

            # Score content
            scores = score_content(topic, content)
            print(f"Scores: {scores}")

            # Save to Google Drive as a Doc
            filename = topic.replace(" ", "_")[:50]
            drive_url = save_to_drive(filename, content)

            # Update sheet
            update_status(row, f"done: {drive_url}")
            update_score(row, scores)

            print(f"Done: {drive_url}")

        except Exception as e:
            print(f"Failed for '{topic}': {e}")
            update_status(row, "error")

if __name__ == "__main__":
    run_pipeline()