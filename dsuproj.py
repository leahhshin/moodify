import streamlit as st
import pandas as pd
import string
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from textblob import TextBlob
from spotify_genius import get_recently_played_songs

st.set_page_config(page_title="Moodify", page_icon="🎵")
st.title("Moodify!")
st.markdown("How are you feeling? Here are songs for you!")

@st.cache_data
def load_tracks():
    tracks_data = get_recently_played_songs()
    df = pd.DataFrame(tracks_data)
    df['lyrics'] = df['lyrics'].str.replace(r'\[.*?\]', '', regex=True)
    df['lyrics'] = df['lyrics'].str.replace(f"[{string.punctuation}]", '', regex=True)
    df['lyrics'] = df['lyrics'].str.replace(r'\n', ' ', regex=True)
    df['lyrics'] = df['lyrics'].fillna('')
    df = df[df['lyrics'].str.strip() != '']
    return df

df = load_tracks()

@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

with st.spinner("Loading embedding model..."):
    model = load_model()

def get_sentiment(text):
    score = TextBlob(text).sentiment.polarity
    if score > 0:
        return 'positive'
    elif score < 0:
        return 'negative'
    else:
        return 'neutral'

def recommend_songs(user_text):
    if df.empty:
        st.warning("No track data available.")
        return
    user_sentiment = get_sentiment(user_text)
    df['sentiment'] = df['lyrics'].apply(get_sentiment)
    filtered_df = df[df['sentiment'] == user_sentiment]
    if filtered_df.empty:
        st.warning(f"No songs found matching {user_sentiment} sentiment.")
        return
    user_embed = model.encode([user_text])[0].reshape(1, -1)
    lyric_embeds = model.encode(filtered_df['lyrics'].tolist())
    scores = cosine_similarity(user_embed, lyric_embeds)[0]
    top_indices = np.argsort(scores)[::-1][:5]
    st.subheader("Your Top 5 Song Recommendations!")
    for i in top_indices:
        song = filtered_df.iloc[i]
        st.markdown(f"**{song['track_name']}** by *{song['artist_name']}*")

user_input = st.text_input("How are you feeling today?")

if user_input:
    recommend_songs(user_input)
