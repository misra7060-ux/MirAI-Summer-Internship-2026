import streamlit as st
import json
import requests
from io import BytesIO
from gtts import gTTS
from google import genai
from google.genai import types

# Set up page layout
st.set_page_config(page_title="Visual Novel AI Engine", layout="centered")

from dotenv import load_dotenv
load_dotenv()
# ==========================================
# PHASE 1: Director's Cut (UI & Configuration)
# ==========================================

# 1. Securely cache Gemini Client
@st.cache_resource
def get_gemini_client():
    # Ensure GEMINI_API_KEY environment variable is set, or pass api_key="YOUR_KEY" here
    return genai.Client()

client = get_gemini_client()

# 2. Sidebar Configuration
st.sidebar.title("Story Settings")
genre = st.sidebar.selectbox("Story Genre", ["Cyberpunk", "Fantasy", "Sci-Fi", "Mystery", "Post-Apocalyptic"])
art_style = st.sidebar.selectbox("Art Style", ["Anime", "Digital Art", "Pixel Art", "Cinematic Realism", "Oil Painting"])

st.title("📖 AI Visual Novel Engine")

# 3. System Prompt enforcing JSON output structure (PHASE 2)
SYSTEM_PROMPT = f"""
You are a master interactive story writer for a visual novel.
Genre: {genre}
Art Style: {art_style}

You MUST ALWAYS reply in strict, valid JSON without Markdown wrapping or extra text.
The JSON object must have these EXACT keys:
1. "story_text": A compelling narrative paragraph (2-4 sentences).
2. "image_prompt": A highly detailed prompt tailored for an image generator (style: {art_style}).
3. "options": A JSON array containing 2 to 3 distinct string options for the player's next move.

Example format:
{{
  "story_text": "You stand before the dark citadel.",
  "image_prompt": "A towering dark obsidian citadel under a red sky, {art_style}",
  "options": ["Enter the main gate", "Search for a side entrance", "Turn back"]
}}
"""

# Initialize Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_scene" not in st.session_state:
    st.session_state.current_scene = None

# ==========================================
# Helper Functions (PHASE 2, 4 & 5)
# ==========================================

def get_next_scene(user_input: str = None):
    """Sends prompt/choice to Gemini and parses structured JSON output."""
    try:
        # Construct message context
        messages = [{"role": "user", "content": SYSTEM_PROMPT}]
        for turn in st.session_state.chat_history:
            messages.append(turn)
        
        if user_input:
            messages.append({"role": "user", "content": f"Player chose: {user_input}"})
            st.session_state.chat_history.append({"role": "user", "content": f"Player chose: {user_input}"})

        # Call Gemini API requesting structured JSON
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=messages,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )

        # Parse JSON
        parsed_data = json.loads(response.text)
        st.session_state.current_scene = parsed_data
        st.session_state.chat_history.append({"role": "model", "content": response.text})

    except Exception as e:
        st.error(f"Error generating narrative: {e}")

def generate_image(prompt: str):
    """PHASE 4 & 5: Fetches visual asset with Graceful Failure (try-except)."""
    try:
        encoded_prompt = requests.utils.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=450&nologo=true"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.content
        else:
            st.toast("Image server is busy, skipping visual...", icon="⚠️")
            return None
    except Exception:
        st.toast("Network issue with image generator, continuing story...", icon="⚠️")
        return None

def generate_tts(text: str):
    """PHASE 4: Text-to-Speech using gTTS."""
    try:
        tts = gTTS(text=text, lang="en")
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return mp3_fp
    except Exception as e:
        st.toast("TTS Audio generation failed.", icon="⚠️")
        return None

# ==========================================
# App Execution & UI Rendering
# ==========================================

# Start button for fresh adventure
if st.session_state.current_scene is None:
    if st.button("🚀 Start Adventure"):
        with st.spinner("Initializing story world..."):
            get_next_scene("Begin the adventure.")
            st.rerun()

# Display active scene
scene = st.session_state.current_scene
if scene:
    st.markdown(f"### {scene.get('story_text')}")

    # Audio Narration Rendering
    audio_data = generate_tts(scene.get('story_text', ''))
    if audio_data:
        st.audio(audio_data, format="audio/mp3", autoplay=True)

    # Visual Asset Rendering
    with st.spinner("Rendering scene background..."):
        img_bytes = generate_image(scene.get('image_prompt', ''))
        if img_bytes:
            st.image(img_bytes, caption=f"Style: {art_style}", use_container_width=True)

    st.markdown("---")
    st.subheader("What will you do next?")

    # PHASE 3: Dynamic UI Generation (Choice Buttons)
    options = scene.get("options", [])
    for idx, choice in enumerate(options):
        if st.button(choice, key=f"btn_{idx}"):
            with st.spinner("Crafting next outcome..."):
                get_next_scene(choice)
                st.rerun()

    # Restart button
    if st.sidebar.button("🔄 Reset Story"):
        st.session_state.chat_history = []
        st.session_state.current_scene = None
        st.rerun()