import sqlite3
import datetime
import os
import streamlit as st # Added for UI rendering

# Database path - dynamically set based on where it's run
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # superbot/
DB_PATH = os.path.join(BASE_DIR, 'db', "narrative_memory.db")

# Ensure the directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Using a simple text-generation pipeline for demonstration
# For real use, replace with Google Gemini API
@st.cache_resource
def get_llm_pipeline():
    from transformers import pipeline
    return pipeline("text-generation", model="gpt2")

llm_pipeline = get_llm_pipeline() # Load LLM once

def init_narrative_db_if_not_exists():
    """Initializes the database if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS narrative_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            type TEXT,
            content TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personality_traits (
            trait TEXT PRIMARY KEY,
            value REAL
        )
    """)

    default_traits = {
        "empathy": 0.5,
        "curiosity": 0.5,
        "caution": 0.5,
        "humor": 0.5,
        "confidence": 0.5
    }

    for trait, val in default_traits.items():
        cursor.execute("INSERT OR IGNORE INTO personality_traits (trait, value) VALUES (?, ?)", (trait, val))

    conn.commit()
    conn.close()

# Ensure DB is initialized when module is loaded (for Streamlit Cloud)
init_narrative_db_if_not_exists()

# Log life events
def log_narrative_event(event_type, content):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO narrative_log (timestamp, type, content) VALUES (?, ?, ?)", (
        datetime.datetime.now().isoformat(),
        event_type,
        content
    ))
    conn.commit()
    conn.close()

# Fetch and return current traits
def get_personality_traits():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT trait, value FROM personality_traits")
    traits = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return traits

# Update traits from introspection
def identity_evolution():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM narrative_log ORDER BY id DESC LIMIT 10")
    logs = [row[0] for row in cursor.fetchall()]

    prompt = f"""Based on these recent reflections and experiences:\n{logs}\nSuggest how the AI's personality traits (empathy, curiosity, humor, caution, confidence) should evolve. Provide specific delta values for each trait (e.g., empathy: +0.02, curiosity: -0.01)."""

    # Use the pre-loaded LLM pipeline
    analysis_text = llm_pipeline(prompt, max_length=200, num_return_sequences=1)[0]["generated_text"]

    # Simulated parsing for delta (you'd use NLP to extract from analysis_text)
    # For demo, we'll apply a fixed or simple logic
    delta = {}

    # Example simple parsing:


