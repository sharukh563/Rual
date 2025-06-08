import sqlite3
from datetime import datetime
import os
import streamlit as st # Added for UI rendering
from cognition.gemini_api import generate_gemini_response # For LLM calls

# Database path - dynamically set
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # superbot/
DB_PATH = os.path.join(BASE_DIR, 'db', "theory_of_mind.db")

# Ensure the directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_tom_db_if_not_exists():
    """Initializes the database if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS theory_of_mind (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT,
            beliefs TEXT,
            desires TEXT,
            emotions TEXT,
            intentions TEXT,
            timestamp TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS empathy_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT,
            predicted_emotion TEXT,
            actual_emotion TEXT,
            timestamp TEXT
        )
    ''') # For meta-learning
    conn.commit()
    conn.close()

# Ensure DB is initialized when module is loaded (for Streamlit Cloud)
init_tom_db_if_not_exists()

def store_perspective(agent_id, beliefs, desires, emotions, intentions):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO theory_of_mind (agent_id, beliefs, desires, emotions, intentions, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (agent_id, beliefs, desires, emotions, intentions, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def simulate_perspective(agent_id, recent_input):
    """Simulates another agent's mental state (beliefs, desires, emotions, intentions)."""
    prompt = f"""Analyze the following user input and infer their mental state.
    User Input: "{recent_input}"
    What might this person be thinking (Beliefs), feeling (Emotions), wanting (Desires), and planning to do (Intentions)?
    Format your response clearly, like:
    Beliefs: ...
    Emotions: ...
    Desires: ...
    Intentions: ...
    """
    response_text = generate_gemini_response(prompt, max_tokens=250)
    parsed = parse_perspective_response(response_text)
    store_perspective(agent_id, **parsed)
    return parsed

def parse_perspective_response(response_text):
    """Parses LLM response to extract mental state components."""
    def extract_between(text, start, end):
        try:
            # Handle potential variations or missing sections
            start_idx = text.find(start)
            if start_idx == -1: return "Unknown"
            text_after_start = text[start_idx + len(start):]
            end_idx = text_after_start.find(end)
            if end_idx == -1: return text_after_start.strip() # If end not found, take till end
            return text_after_start[:end_idx].strip()
        except Exception:
            return "Unknown"

    beliefs = extract_between(response_text, "Beliefs:", "\nEmotions:").strip()
    emotions = extract_between(response_text, "Emotions:", "\nDesires:").strip()
    desires = extract_between(response_text, "Desires:", "\nIntentions:").strip()
    intentions = extract_between(response_text, "Intentions:", "\n").strip() # Take till end

    return {
        "beliefs": beliefs if beliefs else "Unknown",
        "desires": desires if desires else "Unknown",
        "emotions": emotions if emotions else "Unknown",
        "intentions": intentions if intentions else "Unknown",
    }

def log_empathy_feedback(agent_id, predicted_emotion, actual_emotion):
    """Logs data for empathy calibration."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO empathy_logs (agent_id, predicted_emotion, actual_emotion, timestamp) VALUES (?, ?, ?, ?)",
                   (agent_id, predicted_emotion, actual_emotion, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_empathy_logs(limit=10):
    """Retrieves recent empathy logs for meta-learning."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT agent_id, predicted_emotion, actual_emotion, timestamp FROM empathy_logs ORDER BY id DESC LIMIT ?", (limit,))
    logs = cursor.fetchall()
    conn.close()
    return [{"agent_id": r[0], "predicted_emotion": r[1], "actual_emotion": r[2], "timestamp": r[3]} for r in logs]


# UI Rendering for Streamlit
def render_ui():
    st.subheader("🧠 Super-Bot's Theory of Mind")
    st.write("This module allows Super-Bot to simulate the mental states of other agents (e.g., users).")

    st.markdown("### Simulate Other's Perspective")
    user_input_for_tom = st.text_area("Enter user's statement/situation for perspective simulation:", "I'm worried about my job security and future.")
    
    if st.button("Simulate Perspective"):
        if user_input_for_tom:
            with st.spinner("Inferring mental state..."):
                perspective = simulate_perspective(agent_id="current_user_tom_test", recent_input=user_input_for_tom)
                st.success("Inferred Perspective:")
                st.json(perspective)
            st.markdown("---")
            st.subheader("Empathy Calibration Feedback")
            predicted_emotion = perspective.get("emotions", "Unknown")
            actual_emotion = st.text_input(f"What was the actual emotion of the user (e.g., 'worried', 'stressed')?", "worried")
            if st.button("Submit Empathy Feedback"):
                log_empathy_feedback("current_user_tom_test", predicted_emotion, actual_emotion)
                st.success("Empathy feedback logged for calibration.")
        else:
            st.info("Please enter a statement.")

    st.markdown("### Recent Simulated Perspectives")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT agent_id, beliefs, emotions, intentions, timestamp FROM theory_of_mind ORDER BY id DESC LIMIT 5")
    recent_perspectives = cursor.fetchall()
    conn.close()

    if recent_perspectives:
        st.table(recent_perspectives)
    else:
        st.info("No simulated perspectives logged yet.")

    st.markdown("### Recent Empathy Logs (for Meta-Learning)")
    empathy_logs = get_empathy_logs(limit=5)
    if empathy_logs:
        st.table(empathy_logs)
    else:
        st.info("No empathy calibration logs yet.")
