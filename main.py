import streamlit as st
from openai import OpenAI
import os
from gtts import gTTS
import tempfile

# ------------------------
# PAGE CONFIG
# ------------------------
st.set_page_config(page_title="Multilingual Voice Chatbot")
st.title("🌐 Siddhartha's Multilingual Voice Chatbot")
st.write("🎤 Speak your question and hear the answer!")

# ------------------------
# OPENAI CLIENT
# ------------------------
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ------------------------
# SESSION STATE (IMPORTANT FOR RERUNS)
# ------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ------------------------
# LANGUAGE OPTIONS
# ------------------------
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

st.warning("🎤 Click the microphone, speak, then click again to STOP recording.")

# ------------------------
# TEXT TO SPEECH
# ------------------------
def speak(text, lang_code="en"):
    try:
        tts = gTTS(text=text, lang=lang_code)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tts.save(tmp.name)
            tmp_path = tmp.name

        with open(tmp_path, "rb") as audio_file:
            st.audio(audio_file.read(), format="audio/mp3")

        os.remove(tmp_path)

    except Exception as e:
        st.error(f"TTS Error: {e}")

# ------------------------
# SPEECH TO TEXT
# ------------------------
def transcribe_audio(audio_bytes):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes.read())
            tmp_path = tmp.name

        with open(tmp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=f
            )

        os.remove(tmp_path)
        return transcript.text

    except Exception as e:
        st.error(f"Transcription Error: {e}")
        return None

# ------------------------
# CHAT FUNCTION
# ------------------------
def ask_chatbot(question, language_name):
    try:
        messages = [
            {
                "role": "system",
                "content": f"You are a helpful assistant. Always reply in {language_name}."
            }
        ] + st.session_state.messages + [
            {"role": "user", "content": question}
        ]

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        return response.choices[0].message.content

    except Exception as e:
        st.error(f"Chat Error: {e}")
        return None

# ------------------------
# DISPLAY CHAT HISTORY
# ------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ------------------------
# AUDIO INPUT
# ------------------------
audio_file = st.audio_input("Record your question")

if audio_file is not None:

    st.info("Processing... Please wait.")

    query = transcribe_audio(audio_file)

    if query:

        # Show user message
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        # Get assistant response
        answer = ask_chatbot(query, selected_language_full)

        if answer:
            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

            with st.chat_message("assistant"):
                st.markdown(answer)

            # Speak response
            speak(answer, selected_language_code)
