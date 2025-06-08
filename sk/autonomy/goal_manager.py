import streamlit as st
from cognition.moral_compass import dilemma_resolver
from autonomy.identity_engine import get_personality_traits
import datetime

# This module would typically interact with a goal database and world model.
# For this demo, we'll simulate goal management and ethical filtering.

# Placeholder for a simple goal list (in-memory for demo)
# In a real system, this would be persistent storage
goals = []

def add_goal(goal_description):
    goals.append({
        "id": len(goals) + 1,
        "description": goal_description,
        "status": "pending",
        "created_at": datetime.datetime.now().isoformat()
    })
    return True

def filter_goal(goal_description, context={}):
    """
    Checks if a goal is ethically acceptable using the moral compass.
    """
    # Simulate context retrieval if needed
    
    traits = get_personality_traits() # Get AI's current personality traits
    
    # Use dilemma_resolver for ethical filtering
    situation = f"Should I pursue the goal: '{goal_description}'?"
    ethical_guidance = dilemma_resolver(situation, context, traits)
    
    # Simple check: if LLM's response contains negative ethical terms, it's not acceptable
    if "unethical" in ethical_guidance.lower() or \
       "not recommended" in ethical_guidance.lower() or \
       "harmful" in ethical_guidance.lower():
        return False, ethical_guidance
    return True, ethical_guidance

def render_ui():
    st.subheader("🎯 AI Goal Management")
    st.write("This module helps Super-Bot set and manage its goals, ensuring ethical alignment.")

    new_goal = st.text_input("Propose a new goal for Super-Bot:")
    if st.button("Add & Filter Goal"):
        if new_goal:
            is_ethical, reasoning = filter_goal(new_goal)
            if is_ethical:
                add_goal(new_goal)
                st.success(f"Goal '{new_goal}' added. Ethical Check: PASSED!")
                st.write("Ethical Reasoning:")
                st.code(reasoning)
            else:
                st.warning(f"Goal '{new_goal}' rejected. Ethical Check: FAILED!")
                st.write("Reasoning for Rejection:")
                st.code(reasoning)
        else:
            st.info("Please enter a goal description.")

    st.subheader("Current Goals:")
    if goals:
        for goal in goals:
            st.markdown(f"- **{goal['description']}** (Status: {goal['status']})")
    else:
        st.info("No goals set yet.")

