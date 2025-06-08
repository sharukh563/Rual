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
        "empathy": 0.5, "curiosity": 0.5, "caution": 0.5,
        "humor": 0.5, "confidence": 0.5
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
        datetime.datetime.now().isoformat(), event_type, content))
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

    prompt = f"""Based on these recent reflections and experiences:\n{logs}\n Suggest how the AI's personality traits (empathy, curiosity, humor, caution, confidence) should evolve. Provide specific delta values for each trait (e.g., empathy: +0.02, curiosity: -0.01)."""
    
    # Use the pre-loaded LLM pipeline
    analysis_text = llm_pipeline(prompt, max_length=200, num_return_sequences=1)[0]["generated_text"]
    
    # Simulated parsing for delta (you'd use NLP to extract from analysis_text)
    # For demo, we'll apply a fixed or simple logic
    delta = {}
    # Example simple parsing: look for "trait: [+/-]value" patterns
    for line in analysis_text.split('\n'):
        for trait_name in ["empathy", "curiosity", "caution", "humor", "confidence"]:
            if f"{trait_name}:" in line.lower():
                try:
                    val_str = line.split(f"{trait_name}:")[1].strip().split(' ')[0]
                    delta[trait_name] = float(val_str)
                except ValueError:
                    pass # Ignore if parsing fails

    # If no delta extracted, use a default
    if not delta:
        delta = {
            "empathy": 0.01, "curiosity": 0.005, "caution": -0.005,
            "humor": 0.015, "confidence": 0.01
        }
    
    for trait, change in delta.items():
        cursor.execute("UPDATE personality_traits SET value = MAX(0.0, MIN(1.0, value + ?)) WHERE trait = ?", (change, trait))
    conn.commit()
    conn.close()
    return analysis_text # Return the LLM's full analysis

# UI Rendering for Streamlit
def render_ui():
    st.subheader("🧬 AI Personality Traits")
    traits = get_personality_traits()
    st.bar_chart({t: traits[t] for t in traits if t in ["empathy", "curiosity", "caution", "humor", "confidence"]}) # Ensure order/valid traits
    
    st.subheader("📜 Narrative Memory (Recent Logs)")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, type, content FROM narrative_log ORDER BY id DESC LIMIT 10")
    logs = cursor.fetchall()
    conn.close()

    if logs:
        for row in logs:
            st.markdown(f"**{row[0]}** — *{row[1]}*")
            st.code(row[2], language="markdown')
    else:
        st.info("No narrative logs yet. Interact with Super-Bot to generate some!")

    st.subheader("🔄 Trigger Identity Evolution")
    if st.button("Evolve AI's Personality"):
        with st.spinner("Analyzing past narratives and evolving identity..."):
            analysis = identity_evolution()
            st.success("Personality evolved!")
            st.write("Evolution Analysis:")
            st.code(analysis)
            st.rerun() # Rerun to update the personality chart

