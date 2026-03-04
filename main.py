import streamlit as st
from openai import OpenAI
import os
from gtts import gTTS
import tempfile

# ------------------------
# PAGE CONFIG
# ------------------------
st.set_page_config(page_title="Multilingual Voice Chatbot")

# ------------------------
# OPENAI CLIENT
# ------------------------
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ------------------------
# TEXT TO SPEECH
# ------------------------
def speak(text, lang_code="en"):
    tts = gTTS(text=text, lang=lang_code)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tts.save(tmp.name)
        tmp_path = tmp.name

    with open(tmp_path, "rb") as audio_file:
        st.audio(audio_file.read(), format="audio/mp3")

    os.remove(tmp_path)

# ------------------------
# SPEECH TO TEXT
# ------------------------
def transcribe_audio(audio_file):
    transcript = client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",
        file=audio_file
    )
    return transcript.text

# ------------------------
# CHAT FUNCTION
# ------------------------
def ask_chatbot(question, language_name):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"You are a helpful assistant. Always reply in {language_name}."
            },
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content


# ------------------------
# UI
# ------------------------
st.title("🌐 Siddhartha's Multilingual Voice Chatbot")
st.write("🎤 Speak your question and hear the answer!")

languages = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "mr": "Marathi",
    "gu": "Gujarati"
}

selected_language_full = st.selectbox("Select Language", list(languages.values()))
selected_language_code = [
    code for code, name in languages.items()
    if name == selected_language_full
][0]

# 🎤 BUILT-IN MIC INPUT (WORKS ON RENDER)
audio_file = st.audio_input("Click to record your question")

if audio_file is not None:

    st.info("Processing... Please wait.")

    # Convert speech to text
    query = transcribe_audio(audio_file)
    st.write(f"📝 You said: {query}")

    # Get answer
    answer = ask_chatbot(query, selected_language_full)

    st.markdown(f"**🤖 Answer:** {answer}")

    # Speak answer
    speak(answer, lang_code=selected_language_code)
