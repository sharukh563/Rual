import streamlit as st
import datetime
from autonomy.identity_engine import get_personality_traits
from cognition.moral_compass import dilemma_resolver
from cognition.emotional_memory import emotional_influence_analysis
from cognition.theory_of_mind import simulate_perspective
from cognition.gemini_api import generate_gemini_response

# LLM for general reasoning and response generation
@st.cache_resource
def get_llm_pipeline():
    from transformers import pipeline
    return pipeline("text-generation", model="gpt2")

llm_pipeline = get_llm_pipeline() # Load once

def make_decision(context_data):
    """
    Super-Bot's central decision-making unit, integrating all cognitive layers.
    context_data should be a dict with keys like 'scenario', 'ethics_flag',
    'user_input', etc.
    """
    scenario = context_data.get("scenario", "a general situation")
    user_input = context_data.get("user_input", scenario) # User input is part of scenario

    traits = get_personality_traits()
    
    # 1. Emotional Influence
    emotional_bias_info = emotional_influence_analysis(user_input)
    emotional_influence_str = f"Emotional bias from past memories: {emotional_bias_info['emotion']} (Intensity: {emotional_bias_info['total_intensity']:.2f})" if emotional_bias_info else "No strong emotional bias."

    # 2. Theory of Mind (User Perspective)
    # Simulate user's perspective based on their input/scenario
    user_perspective = simulate_perspective(agent_id="current_user", recent_input=user_input)
    user_perspective_str = f"User perspective inferred: Beliefs: {user_perspective['beliefs']}, Desires: {user_perspective['desires']}, Emotions: {user_perspective['emotions']}, Intentions: {user_perspective['intentions']}."

    # 3. Ethical Decision Filter
    ethical_guidance = "No specific ethical dilemma detected or guidance needed."
    if context_data.get("ethics_flag", False) or "ethical dilemma" in scenario.lower():
        ethical_guidance = dilemma_resolver(scenario, context_data, traits)

    # 4. Core Reasoning with all influences
    prompt = f"""You are Super-Bot, an advanced AGI.
    Scenario: {scenario}
    Your current personality traits: {traits}
    Emotional influence from your memory: {emotional_influence_str}
    Inferred user's perspective: {user_perspective_str}
    Ethical guidance for this situation: {ethical_guidance}

    Based on all these factors, what is the most logical, ethical, and empathetic decision or response? Provide a concise action or thought process.
    """
    
    # Use LLM for final reasoning synthesis
    final_response = generate_gemini_response(prompt, max_tokens=250)
    
    return final_response

# UI Rendering for Streamlit
def render_ui():
    st.subheader("🧩 Super-Bot's Reasoning Core")
    st.write("This module represents Super-Bot's central decision-making and thought process, integrating all its cognitive layers.")

    st.markdown("### Test Reasoning Process")
    scenario_input = st.text_area("Enter a scenario for Super-Bot to reason about:", "A user is asking for financial advice, but seems emotionally distressed. What should I do?")
    ethics_flag = st.checkbox("Is this an ethical dilemma?")

    if st.button("Trigger Decision-Making"):
        if scenario_input:
            context_data = {
                "scenario": scenario_input,
                "user_input": scenario_input, # Assuming scenario is directly from user input for simplicity
                "ethics_flag": ethics_flag
            }
            with st.spinner("Super-Bot is thinking deeply..."):
                decision_output = make_decision(context_data)
                st.success("Super-Bot's Decision/Reasoning:")
                st.code(decision_output)
        else:
            st.info("Please enter a scenario.")

