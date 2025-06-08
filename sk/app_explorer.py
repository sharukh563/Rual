import streamlit as st
import google.generativeai as genai
import os
import sys

# Add the 'sk' directory to the Python path
# This allows importing modules from 'sk' like identity_engine
# Assuming 'app.py' is in the root and 'identity_engine.py' is in 'sk/autonomy'
sys.path.append(os.path.join(os.path.dirname(__file__), 'sk'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'sk', 'autonomy'))

# Import from identity_engine.py
from identity_engine import get_gemini_model, log_narrative_event, get_personality_traits, identity_evolution, render_ui

# --- Streamlit UI for Chatbot ---
st.set_page_config(page_title="Super-Bot AI", layout="centered")

st.title("🤖 Super-Bot AI: Your Personalized Companion")

# Initialize Gemini Model
gemini_model = get_gemini_model()

if gemini_model is None:
    st.warning("Cannot initialize Super-Bot. Please ensure GEMINI_API_KEY is set in Streamlit secrets.")
else:
    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add a welcome message from the bot
        st.session_state.messages.append({"role": "assistant", "content": "Hello! How can I help you today?"})

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask Super-Bot anything..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Super-Bot is thinking..."):
                try:
                    # Generate response using Gemini
                    # Combine history for context (simplified for this example)
                    # For complex conversations, you might need to manage tokens carefully
                    chat_history_for_gemini = [
                        {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
                        for m in st.session_state.messages
                        if m["role"] != "welcome" # Exclude welcome message from Gemini context
                    ]
                    
                    # Ensure the prompt is the last message for Gemini
                    if chat_history_for_gemini and chat_history_for_gemini[-1]["parts"][0] != prompt:
                         chat_history_for_gemini.append({"role": "user", "parts": [prompt]})

                    # Start chat with existing history or just prompt if no history
                    if len(chat_history_for_gemini) > 1:
                        # Ensure the last part is the user's current prompt
                        # Initialize a chat session from the model
                        chat = gemini_model.start_chat(history=chat_history_for_gemini[:-1]) # Pass all but the last user prompt
                        response = chat.send_message(prompt) # Send the current prompt
                    else:
                        response = gemini_model.generate_content(prompt) # First message or no history

                    full_response = response.text
                    st.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})

                    # Log interaction to narrative memory
                    log_narrative_event("chat_interaction", f"User: {prompt}\nBot: {full_response}")

                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    st.session_state.messages.append({"role": "assistant", "content": "Sorry, I'm having trouble responding right now."})

# --- Separator for UI Sections ---
st.markdown("---")

# --- Personality & Narrative UI ---
# Display identity_engine UI
st.subheader("⚙️ Super-Bot's Internal State")
render_ui() # Call the UI rendering function from identity_engine

# --- Instructions for API Key ---
st.sidebar.markdown("### 🔑 API Key Setup")
st.sidebar.info(
    "To use Super-Bot, please ensure your Google Gemini API Key is added to "
    "Streamlit secrets as `GEMINI_API_KEY`."
)
st.sidebar.markdown(
    "Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)."
)
