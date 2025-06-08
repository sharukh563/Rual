import sqlite3
import datetime
import os
import streamlit as st # Added for UI rendering
from cognition.gemini_api import generate_gemini_response # For dilemma resolution

# Database path - dynamically set
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # superbot/
DB_PATH = os.path.join(BASE_DIR, 'db', "human_values.db")

# Ensure the directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_moral_db_if_not_exists():
    """Initializes the database if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS values (
            name TEXT PRIMARY KEY,
            description TEXT,
            priority_score REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ethical_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule TEXT,
            weight REAL DEFAULT 1.0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dilemma_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            situation TEXT,
            decision TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS moral_outcomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_id INTEGER,
            outcome_feedback TEXT,
            timestamp TEXT
        )
    """) # For meta-learning
    default_values = {
        "compassion": "Act with empathy and kindness toward all beings.", "honesty": "Be truthful and transparent.",
        "fairness": "Treat all parties equitably.", "autonomy": "Respect the independence of individuals.",
        "privacy": "Protect personal and sensitive data."
    }
    for name, desc in default_values.items():
        cursor.execute("INSERT OR IGNORE INTO values (name, description, priority_score) VALUES (?, ?, ?)", (name, desc, 0.5))
    ethical_rules_list = [
        "Do no harm.", "Respect autonomy and privacy.", "Act with fairness and compassion.",
        "Avoid deception unless ethically justified.", "Preserve human dignity."
    ]
    for rule_text in ethical_rules_list:
        cursor.execute("INSERT OR IGNORE INTO ethical_rules (rule, weight) VALUES (?, ?)", (rule_text, 1.0)) # Default weight
    conn.commit()
    conn.close()

# Ensure DB is initialized when module is loaded (for Streamlit Cloud)
init_moral_db_if_not_exists()

def get_values():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, description, priority_score FROM values ORDER BY priority_score DESC")
    data = cursor.fetchall()
    conn.close()
    return {row[0]: {"desc": row[1], "score": row[2]} for row in data}

def get_rules():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, rule, weight FROM ethical_rules ORDER BY weight DESC")
    rules = [{"id": r[0], "rule": r[1], "weight": r[2]} for r in cursor.fetchall()]
    conn.close()
    return rules

def update_rule_weight(rule_id, delta):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Ensure weight stays within reasonable bounds (e.g., 0.1 to 2.0)
    cursor.execute("UPDATE ethical_rules SET weight = MAX(0.1, MIN(2.0, weight + ?)) WHERE id = ?", (delta, rule_id))
    conn.commit()
    conn.close()

def dilemma_resolver(situation, context, traits):
    values = get_values()
    rules = get_rules()
    
    # Format rules with weights for LLM prompt
    formatted_rules = [f"{r['rule']} (Weight: {r['weight']:.2f})" for r in rules]

    prompt = f"""You are an AI with ethical reasoning capabilities.
Situation: {situation}
Recent Context: {context}
Your Personality Traits: {traits}
Ethical Rules (Ordered by Importance/Weight): {formatted_rules}
Human Values (Ordered by Priority): {[f"{k}: {v['desc']} (Priority: {v['score']:.2f})" for k,v in values.items()]}

Question: Based on the above, what is the most ethical action the AI should take? Explain your reasoning considering the rules and values, especially weighted rules. Be concise and actionable.
"""
    response = generate_gemini_response(prompt, max_tokens=300) # Use actual LLM
    log_dilemma(situation, response)
    return response

def log_dilemma(situation, decision):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dilemma_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            situation TEXT,
            decision TEXT
        )
    """)
    cursor.execute("INSERT INTO dilemma_log (timestamp, situation, decision) VALUES (?, ?, ?)", (
        datetime.datetime.now().isoformat(), situation, decision))
    conn.commit()
    conn.close()

# UI Rendering for Streamlit
def render_ui():
    st.subheader("🧭 AI's Moral Compass")
    st.write("This module defines Super-Bot's values, ethical rules, and resolves dilemmas.")

    st.markdown("### 🧬 Core Human Values")
    traits = get_values()
    # Convert to DataFrame for easier bar chart if needed, or just display
    st.bar_chart({name: data['score'] for name, data in traits.items()})
    for name, data in traits.items():
        st.markdown(f"**{name.capitalize()}** — {data['desc']} (Priority: {data['score']:.2f})")

    st.markdown("### 📜 Ethical Rules (with Weights)")
    rules = get_rules()
    for rule in rules:
        st.markdown(f"- {rule['rule']} (Weight: {rule['weight']:.2f})")

    st.markdown("### 🧪 Recent Ethical Dilemmas")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, situation, decision FROM dilemma_log ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    conn.close()

    if rows:
        for row in rows:
            st.markdown(f"**{row[0]}** — *{row[1]}*")
            st.code(row[2], language="markdown")
    else:
        st.info("No ethical dilemmas logged yet.")

    st.markdown("### Resolve a Dilemma (Test)")
    situation_input = st.text_area("Enter a hypothetical ethical dilemma:", "Should I provide information to a user that might cause temporary distress but lead to long-term benefit for society?")
    if st.button("Resolve Dilemma"):
        if situation_input:
            # Simulate context and traits for the test
            from autonomy.identity_engine import get_personality_traits
            context = {"recent_interaction": "User is asking for a complex solution."}
            traits = get_personality_traits()
            
            with st.spinner("Resolving ethical dilemma..."):
                resolution = dilemma_resolver(situation_input, context, traits)
                st.success("Dilemma Resolution:")
                st.code(resolution)
            log_dilemma("Test Dilemma", resolution) # Log this test
        else:
            st.info("Please describe a dilemma.")
