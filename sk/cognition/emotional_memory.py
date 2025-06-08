import sqlite3
from datetime import datetime
import os
import streamlit as st

# Database path - dynamically set
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # superbot/
DB_PATH = os.path.join(BASE_DIR, 'memory', "emotional_memory.db")

# Ensure the directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_emotional_db_if_not_exists():
    """Initializes the database if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emotional_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            emotion TEXT,
            intensity REAL,
            context TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Ensure DB is initialized when module is loaded (for Streamlit Cloud)
init_emotional_db_if_not_exists()

# Save emotional event
def store_emotion(event, emotion, intensity=1.0, context=""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO emotional_memory (event, emotion, intensity, context, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (event, emotion, intensity, context, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# Recall related emotional memories
def recall_emotion(event_query, top_n=5):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT event, emotion, intensity, context, timestamp
        FROM emotional_memory
        WHERE event LIKE ? ORDER BY intensity DESC, timestamp DESC LIMIT ?
    ''', ('%' + event_query + '%', top_n))
    data = cursor.fetchall()
    conn.close()
    return [{"event": r[0], "emotion": r[1], "intensity": r[2], "context": r[3], "timestamp": r[4]} for r in data]

# Influence analysis
def emotional_influence_analysis(current_event):
    recalled = recall_emotion(current_event)
    if not recalled:
        return None

    # Aggregate emotional impact
    emotion_scores = {}
    for entry in recalled:
        emotion = entry["emotion"]
        intensity = entry["intensity"]
        emotion_scores[emotion] = emotion_scores.get(emotion, 0) + intensity
    
    if emotion_scores:
        max_emotion = max(emotion_scores, key=emotion_scores.get)
        max_intensity = emotion_scores[max_emotion]
        return {"emotion": max_emotion, "total_intensity": max_intensity, "recalled_events": recalled}
    return None

# UI Rendering for Streamlit
def render_ui():
    st.subheader("💓 Super-Bot's Emotional Memory")
    st.write("This module stores and recalls emotional contexts of past events.")

    st.markdown("### Store New Emotional Event")
    event_input = st.text_input("Event Description:", "User praised my response.")
    emotion_input = st.selectbox("Emotion:", ["joy", "sadness", "anger", "fear", "surprise", "disgust", "neutral"])
    intensity_input = st.slider("Intensity:", 0.0, 1.0, 0.5)
    context_input = st.text_area("Context (optional):", "It was related to ethical reasoning.")
    if st.button("Store Emotion"):
        store_emotion(event_input, emotion_input, intensity_input, context_input)
        st.success("Emotional event stored!")

    st.markdown("### Recall Emotional Memories")
    recall_query = st.text_input("Query for related emotional memories:", "positive interaction")
    if st.button("Recall Memories"):
        recalled_memories = recall_emotion(recall_query)
        if recalled_memories:
            for mem in recalled_memories:
                st.markdown(f"- **Event:** {mem['event']}")
                st.write(f"  Emotion: {mem['emotion'].capitalize()}, Intensity: {mem['intensity']:.2f}")
                st.write(f"  Context: {mem['context']}")
                st.write(f"  Timestamp: {mem['timestamp']}")
        else:
            st.info("No related emotional memories found.")

    st.markdown("### Recent Emotional Memories Panel")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT event, emotion, intensity, timestamp FROM emotional_memory ORDER BY id DESC LIMIT 5")
    recent_logs = cursor.fetchall()
    conn.close()

    if recent_logs:
        st.table(recent_logs)
    else:
        st.info("No recent emotional memories.")

