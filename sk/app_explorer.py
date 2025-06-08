import streamlit as st
import importlib
import os

st.set_page_config(page_title="🤖 Super-Bot AGI Interface", layout="wide")
st.title("🧠 Super-Bot AGI System")
st.markdown("---")

# Define phase ranges (for modular UI loading)
# Note: For this ZIP, only phase_1_to_20 interface is provided as a placeholder.
# You can expand phases/ folder for 21-40, etc. later.
phase_ranges = {
    "🧱 Phase 1–20: Foundation & Core Intelligence": "phase_1_to_20",
    # "🧠 Phase 21–40: Emotion, Robotics & Creativity": "phase_21_to_40", # Add later
    # "🌍 Phase 41–60: Social, Global, Political": "phase_41_to_60",     # Add later
    # "🚀 Phase 61–80: Transcendence & Unknown": "phase_61_to_80",       # Add later
    # "🧬 Phase 81–100: Hyper-Intelligence & Singularity": "phase_81_to_100", # Add later
}

selected_range = st.sidebar.selectbox("📦 Choose Phase Block", list(phase_ranges.keys()))
selected_module = phase_ranges[selected_range]

# Try importing the selected module's interface
try:
    module_path = f"phases.{selected_module}.interface"
    # Ensure the parent directory is in sys.path if not already
    import sys
    # Add superbot/ to sys.path for relative imports to work when app_explorer.py is run
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    phase_ui = importlib.import_module(module_path)
    phase_ui.render()
except Exception as e:
    st.error(f"⚠️ Could not load {selected_module}: {e}")
    st.write("Please ensure the folder structure `phases/<selected_module>/interface.py` exists and is correct.")


# Memory / Cognition / Emotion access tools
st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Core Modules (Tools)")

if st.sidebar.button("🧠 View Theory of Mind"):
    try:
        from cognition import theory_of_mind # Import directly for button action
        theory_of_mind.render_ui() # Assuming a render_ui method in the module
    except Exception as e:
        st.error(f"Theory of Mind module not found or render_ui failed: {e}")
        st.code(f"Error details: {e}")

if st.sidebar.button("💓 Emotional Memory"):
    try:
        from cognition import emotional_memory
        emotional_memory.render_ui() # Assuming a render_ui method in the module
    except Exception as e:
        st.error(f"Emotional Memory module not found or render_ui failed: {e}")
        st.code(f"Error details: {e}")

if st.sidebar.button("🧩 Reasoning Core"):
    try:
        from cognition import reasoning_core
        reasoning_core.render_ui() # Assuming a render_ui method in the module
    except Exception as e:
        st.error(f"Reasoning Core module not found or render_ui failed: {e}")
        st.code(f"Error details: {e}")

if st.sidebar.button("🧭 Moral Compass"):
    try:
        from cognition import moral_compass
        moral_compass.render_ui() # Assuming a render_ui method in the module
    except Exception as e:
        st.error(f"Moral Compass module not found or render_ui failed: {e}")
        st.code(f"Error details: {e}")

if st.sidebar.button("🧬 Identity Engine"):
    try:
        from autonomy import identity_engine
        identity_engine.render_ui() # Assuming a render_ui method in the module
    except Exception as e:
        st.error(f"Identity Engine module not found or render_ui failed: {e}")
        st.code(f"Error details: {e}")

if st.sidebar.button("🚀 Meta-Learning"):
    try:
        from cognition import meta_learning
        meta_learning.render_ui() # Assuming a render_ui method in the module
    except Exception as e:
        st.error(f"Meta-Learning module not found or render_ui failed: {e}")
        st.code(f"Error details: {e}")


# Main application area placeholder - you'll add specific UI components here or within phases/
st.markdown("## Main Application Area")
st.write("Select a Phase Block from the sidebar or click a tool to explore Super-Bot's capabilities.")

# Example: Simple interaction area for testing
st.markdown("---")
st.subheader("💬 Super-Bot Interaction (General Test)")
user_input = st.text_input("Enter your query or situation for Super-Bot:")

if user_input:
    st.markdown("---")
    st.subheader("Super-Bot's Response:")
    try:
        # A simplified main interaction flow (you'll expand this with more sophisticated calls)
        from cognition import reasoning_core
        from autonomy import identity_engine
        from cognition import moral_compass
        from cognition import emotional_memory
        from cognition import theory_of_mind

        # Simulate a quick interaction flow for the general test
        st.write(f"User Input: `{user_input}`")

        # 1. Log narrative event
        identity_engine.log_narrative_event("user_interaction", user_input)

        # 2. Simulate perspective (if it's about a user)
        if "user" in user_input.lower() or "i am" in user_input.lower():
            perspective = theory_of_mind.simulate_perspective(agent_id="user", recent_input=user_input)
            st.write(f"**AI's Inferred User Perspective:**")
            st.json(perspective)

        # 3. Decision making (simplified for general interaction)
        decision_context = {
            "scenario": user_input,
            "ethics_flag": "ethical" in user_input.lower() or "right" in user_input.lower(),
            "emotional_context": emotional_memory.emotional_influence_analysis(user_input), # Check for emotional influence
            "traits": identity_engine.get_personality_traits()
        }
        
        superbot_response = reasoning_core.make_decision(decision_context)
        st.success(f"**Super-Bot's Action/Thought:** {superbot_response}")

        # 4. Log AI's thought/action as narrative
        identity_engine.log_narrative_event("superbot_response", superbot_response)

        # 5. Update identity and meta-learn (periodically or on trigger)
        # For simplicity, trigger on every interaction for demo, but typically this is less frequent
        st.markdown("---")
        st.write("🧠 **AI's Self-Reflection & Learning:**")
        identity_evolution_analysis = identity_engine.identity_evolution()
        st.write(f"Identity Evolved: {identity_evolution_analysis}")
        
        moral_evaluation = moral_compass.get_rules() # Simulate evaluation
        st.write(f"Moral Check: {moral_evaluation}") # Placeholder, real meta_learning would evaluate outcomes
        
        st.write(f"Emotional Regulation Status: {meta_learning.update_emotion_regulation()}")
        st.write(f"Empathy Accuracy: {meta_learning.calibrate_empathy()}")

    except Exception as e:
        st.error(f"An error occurred during interaction: {e}")
        st.code(f"Error details: {e}")

