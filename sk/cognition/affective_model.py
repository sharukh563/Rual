import streamlit as st
from transformers import pipeline
import os

# Load sentiment analysis model once
@st.cache_resource
def get_sentiment_pipeline():
    return pipeline("sentiment-analysis")

sentiment_analyzer = get_sentiment_pipeline()

def process_sentiment(text):
    """Analyzes the sentiment of a given text."""
    result = sentiment_analyzer(text)
    if result:
        return result[0]['label'], result[0]['score']
    return "neutral", 0.0

def predict_emotion(text):
    """Predicts a general emotion based on sentiment."""
    sentiment, score = process_sentiment(text)
    if sentiment == 'POSITIVE':
        return 'joy', score
    elif sentiment == 'NEGATIVE':
        return 'sadness', score
    return 'neutral', score

def render_ui():
    st.subheader("💡 AI's Affective Model")
    st.write("This module analyzes text for sentiment and predicts general emotions.")
    
    user_text = st.text_area("Enter text to analyze sentiment/emotion:", "I am feeling very happy today!")
    if st.button("Analyze Emotion"):
        if user_text:
            emotion, intensity = predict_emotion(user_text)
            st.info(f"Detected Emotion: **{emotion.capitalize()}** with intensity **{intensity:.2f}**")
        else:
            st.info("Please enter some text.")

