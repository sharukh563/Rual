            "caution": -0.005,
            "humor": 0.015,
            "confidence": 0.01
        }

    for trait, change in delta.items():
        cursor.execute("UPDATE personality_traits SET value = MAX(0.0, MIN(1.0, value + ?)) WHERE trait = ?", (change, trait))

    conn.commit()
    conn.close()
    return analysis_text  # Return the LLM's full analysis

# UI Rendering for Streamlit
def render_ui():
    st.subheader("🧬 AI Personality Traits")
    traits = get_personality_traits()
    st.bar_chart({t: traits[t] for t in traits if t in ["empathy", "curiosity", "caution", "humor", "confidence"]})  # Ensure order/valid traits

    st.subheader("📜 Narrative Memory (Recent Logs)")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, type, content FROM narrative_log ORDER BY id DESC LIMIT 10")
    logs = cursor.fetchall()
    conn.close()

    if logs:
        for row in logs:
            st.markdown(f"**{row[0]}** — *{row[1]}*")
            st.code(row[2], language="markdown")  # <--- Yahan theek kiya gaya hai
    else:
        st.info("No narrative logs yet. Interact with Super-Bot to generate some!")

    st.subheader("🔄 Trigger Identity Evolution")
    if st.button("Evolve AI's Personality"):
        with st.spinner("Analyzing past narratives and evolving identity..."):
            analysis_text = identity_evolution()
        st.success("Personality evolved!")
        st.write(analysis_text)
