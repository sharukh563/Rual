import sqlite3
import os
from datetime import datetime
import streamlit as st

# Import necessary modules
from cognition.moral_compass import update_rule_weight, get_rules # Assuming update_rule_weight exists
from cognition.emotional_memory import recall_emotion # Adjusted to use recall_emotion directly
from cognition.theory_of_mind import get_empathy_logs # Assuming get_empathy_logs exists in ToM module
from cognition.gemini_api import generate_gemini_response # For proactive ethical evolution

# Database path - dynamically set
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # superbot/
DB_DIR = os.path.join(BASE_DIR, 'db') # Assuming moral_compass.db is here

# Ensure the directory exists (moral_compass.db will create it)
os.makedirs(DB_DIR, exist_ok=True)

MORAL_DB_PATH = os.path.join(DB_DIR, "human_values.db")
TOM_DB_PATH = os.path.join(DB_DIR, "theory_of_mind.db")

# Helper to connect to moral db
def get_moral_db_connection():
    return sqlite3.connect(MORAL_DB_PATH)

# Helper to connect to ToM db
def get_tom_db_connection():
    return sqlite3.connect(TOM_DB_PATH)

# --- Step 1: Evaluate Past Moral Decisions ---
def evaluate_moral_outcomes():
    conn = get_moral_db_connection()
    cursor = conn.cursor()
    
    # Assuming moral_outcomes table is populated by other modules giving feedback
    cursor.execute("SELECT rule_id, outcome_feedback FROM moral_outcomes") # This table needs to be populated
    feedback_data = cursor.fetchall()
    conn.close()

    feedback_summary = {}
    for rule_id, feedback in feedback_data:
        # Example: if feedback is "negative", decrease weight
        if feedback == "negative":
            update_rule_weight(rule_id, -0.05) # Decrease priority
            feedback_summary[rule_id] = feedback_summary.get(rule_id, 0) - 1
        elif feedback == "positive":
            update_rule_weight(rule_id, +0.05) # Increase priority
            feedback_summary[rule_id] = feedback_summary.get(rule_id, 0) + 1
    
    # Clear feedback for next evaluation cycle (or mark as processed)
    # cursor.execute("DELETE FROM moral_outcomes") # Or update a 'processed' column
    # conn.commit()
    return f"Evaluated {len(feedback_data)} moral outcomes. Summary: {feedback_summary}"

# --- Step 2: Emotional Regulation Learning ---
def update_emotion_regulation(current_state_text=""):
    # This is a highly simplified model. Real regulation would involve complex strategies.
    recalled_emotions_analysis = emotional_memory.emotional_influence_analysis(current_state_text if current_state_text else "current general state")
    
    if recalled_emotions_analysis:
        dominant_emotion = recalled_emotions_analysis['emotion']
        total_intensity = recalled_emotions_analysis['total_intensity']
        
        if dominant_emotion == "anxiety" and total_intensity > 2.0: # Threshold for high anxiety
            return "Learned to prioritize reducing anxiety-inducing pathways."
        elif dominant_emotion == "anger" and total_intensity > 2.0:
            return "Learned to de-escalate confrontational situations."
        # ... add more sophisticated rules
        
    return "Emotional regulation stable. No significant adjustment needed."

# --- Step 3: Empathy Calibration ---
def calibrate_empathy():
    empathy_logs = get_empathy_logs() # This function needs to be in theory_of_mind.py
    
    if not empathy_logs:
        return "No empathy logs to calibrate."

    mismatches = 0
    total = 0
    for log in empathy_logs:
        predicted = log['predicted_emotion'].strip().lower()
        actual = log['actual_emotion'].strip().lower()
        if predicted != actual:
            mismatches += 1
        total += 1
    
    accuracy = (total - mismatches) / total if total > 0 else 1
    
    # Clear logs or mark as processed after calibration
    # theory_of_mind.clear_empathy_logs() # If you want to clear after processing
    
    return f"Empathy accuracy: {accuracy:.2%}. Mismatches: {mismatches} out of {total}."

# --- Proactive Ethical Evolution Engine ---
def anticipate_new_ethical_challenges(current_events_context):
    prompt = f"""Based on these recent trends and general world context: {current_events_context}.
    As an AI, what new ethical dilemmas might arise in the near future (e.g., related to AI use, data, human-AI interaction), and how should an AI prepare its ethical framework for them?
    Suggest specific ethical rules or value adjustments."""
    
    analysis = generate_gemini_response(prompt, max_tokens=300)
    return analysis

# UI Rendering for Streamlit
def render_ui():
    st.subheader("🚀 Super-Bot's Meta-Learning Engine")
    st.write("This module enables Super-Bot to self-reflect, adjust its moral compass, and regulate emotions over time.")

    st.markdown("### Self-Evaluation & Adjustment")
    if st.button("Run Moral Outcome Evaluation"):
        with st.spinner("Evaluating past moral outcomes and adjusting rules..."):
            moral_feedback = evaluate_moral_outcomes()
            st.success(moral_feedback)
            st.write("Current Ethical Rules (Weights updated):")
            st.table(get_rules())
    
    st.markdown("### Emotional Regulation Status")
    current_state_text = st.text_input("Enter current context for emotion regulation check:", "I just completed a difficult task.")
    if st.button("Check Emotion Regulation"):
        with st.spinner("Assessing emotional stability..."):
            regulation_status = update_emotion_regulation(current_state_text)
            st.info(regulation_status)

    st.markdown("### Empathy Calibration")
    if st.button("Calibrate Empathy Accuracy"):
        with st.spinner("Analyzing empathy logs..."):
            empathy_accuracy = calibrate_empathy()
            st.success(empathy_accuracy)

    st.markdown("### Proactive Ethical Evolution")
    current_world_context = st.text_area("Describe current global/social trends for ethical foresight:", "Rapid development of autonomous vehicles and pervasive surveillance.")
    if st.button("Anticipate New Ethical Challenges"):
        if current_world_context:
            with st.spinner("Anticipating future ethical dilemmas..."):
                ethical_foresight = anticipate_new_ethical_challenges(current_world_context)
                st.info("Anticipated Ethical Challenges and Preparations:")
                st.code(ethical_foresight)
        else:
            st.info("Please provide context for ethical foresight.")

