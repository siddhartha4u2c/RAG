import streamlit as st
from openai import OpenAI
import os
from gtts import gTTS
from audiorecorder import audiorecorder
import tempfile

# ------------------------
# OPENAI CLIENT
# ------------------------
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ------------------------
# TTS FUNCTION (gTTS)
# ------------------------
def speak(text, lang_code="en"):
    tts = gTTS(text=text, lang=lang_code)
    audio_path = "temp.mp3"
    tts.save(audio_path)

    with open(audio_path, "rb") as audio_file:
        st.audio(audio_file.read(), format="audio/mp3")

    os.remove(audio_path)

# ------------------------
# SPEECH TO TEXT FUNCTION
# ------------------------
def transcribe_audio(audio_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    with open(tmp_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=audio_file
        )

    os.remove(tmp_path)
    return transcript.text

# ------------------------
# ASK FUNCTION (Direct multilingual — no translation step)
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
# STREAMLIT UI
# ------------------------
st.title("🌐 Siddhartha's Multilingual Voice Chatbot")
st.write("Speak or type in your selected language and hear the response!")

# Language selection
languages = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "mr": "Marathi",
    "gu": "Gujarati"
}

selected_language_full = st.selectbox("Select Language", list(languages.values()))
selected_language_code = [code for code, name in languages.items() if name == selected_language_full][0]

# Text input
query = st.text_input("✍️ Enter your question (or use voice below):")

# Audio recorder
st.write("🎤 Or record your question:")
audio = audiorecorder("Click to record", "Recording... Click to stop")

# Ask button
if st.button("Ask"):

    # If audio recorded, override text input
    if len(audio) > 0:
        query = transcribe_audio(audio.export().read())
        st.write(f"📝 You said: {query}")

    if query.strip():
        answer = ask_chatbot(query, selected_language_full)

        st.markdown(f"**🤖 Answer:** {answer}")

        speak(answer, lang_code=selected_language_code)
    else:
        st.warning("Please type or record a question!")
