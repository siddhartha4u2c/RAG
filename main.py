import streamlit as st
from openai import OpenAI
import os
from gtts import gTTS

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ------------------------
# TTS FUNCTION (gTTS)
# ------------------------
def speak(text, lang_code="en"):
    """Generate speech from text and play in Streamlit"""
    tts = gTTS(text=text, lang=lang_code)
    audio_path = "temp.mp3"
    tts.save(audio_path)
    audio_file = open(audio_path, "rb")
    st.audio(audio_file.read(), format="audio/mp3")
    audio_file.close()
    os.remove(audio_path)

# ------------------------
# ASK FUNCTION
# ------------------------
def ask_chatbot(question, lang="en"):
    # Step 1: Translate question to English if needed
    if lang != "en":
        translation_prompt = f"Translate this question to English:\n{question}"
        question_en = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a translation assistant."},
                {"role": "user", "content": translation_prompt}
            ]
        ).choices[0].message.content
    else:
        question_en = question

    # Step 2: Generate answer in English
    answer_en = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question_en}
        ]
    ).choices[0].message.content

    # Step 3: Translate answer back if needed
    if lang != "en":
        translation_prompt = f"Translate this text to {lang}:\n{answer_en}"
        answer = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a translation assistant."},
                {"role": "user", "content": translation_prompt}
            ]
        ).choices[0].message.content
    else:
        answer = answer_en

    return answer

# ------------------------
# STREAMLIT UI
# ------------------------
st.title("🌐 Multilingual Chatbot with Voice")
st.write("Ask a question in English or any Indian language and hear the answer!")

# Language selection
languages = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "ml": "Malayalam",
    "mr": "Marathi",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "kn": "Kannada"
}

selected_language_full = st.selectbox("Select Language", list(languages.values()))
selected_language_code = [code for code, name in languages.items() if name == selected_language_full][0]

# User input
query = st.text_input("Enter your question:")

# Submit button
if st.button("Ask"):
    if query.strip():
        answer = ask_chatbot(query, lang=selected_language_code)
        st.markdown(f"**🤖 Answer:** {answer}")
        speak(answer, lang_code=selected_language_code)
    else:
        st.warning("Please type a question!")


