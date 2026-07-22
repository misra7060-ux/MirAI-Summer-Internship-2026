import streamlit as st
import requests
import json
import tempfile
from gtts import gTTS
from groq import Groq
from dotenv import load_dotenv
import os
from PIL import Image
from io import BytesIO

# --------------------------
# PAGE CONFIG
# --------------------------

st.set_page_config(
    page_title="AI Visual Novel",
    page_icon="🎮",
    layout="wide"
)

# --------------------------
# CUSTOM CSS
# --------------------------

st.markdown("""
<style>
.main {
    background-color: #0f172a;
}

.story-box {
    padding:20px;
    border-radius:15px;
    background:#1e293b;
    color:white;
    font-size:18px;
}

.option-btn {
    width:100%;
}

div.stButton > button {
    width:100%;
    border-radius:12px;
    height:50px;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# --------------------------
# LOAD ENV
# --------------------------

load_dotenv()

# --------------------------
# CACHE GROQ CLIENT
# --------------------------

@st.cache_resource
def get_client():
    return Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )

client = get_client()

# --------------------------
# SIDEBAR
# --------------------------

with st.sidebar:

    st.title("📖 Story Settings")

    genre = st.selectbox(
        "Story Genre",
        [
            "Fantasy",
            "Sci-Fi",
            "Cyberpunk",
            "Mystery",
            "Horror",
            "Adventure"
        ]
    )

    art_style = st.selectbox(
        "Art Style",
        [
            "Anime",
            "Cinematic",
            "Pixel Art",
            "Fantasy Painting",
            "Realistic",
            "3D Render"
        ]
    )
    STYLE_PROMPTS = {
    "Anime": "anime style, manga style, studio ghibli, vibrant anime colors, japanese animation",
    "Cinematic": "cinematic movie scene, dramatic lighting, film still, depth of field, unreal engine",
    "Pixel Art": "pixel art, retro video game graphics, 16-bit pixel style",
    "Fantasy Painting": "fantasy concept art, magical world, epic fantasy painting",
    "Realistic": "photorealistic, ultra realistic photography, highly detailed, 8k",
    "3D Render": "3d render, octane render, ray tracing, blender render"
    }

    if st.button("🔄 Restart Story"):
        st.session_state.story_history = []
        st.session_state.messages = []
        st.rerun()

# --------------------------
# SESSION STATE
# --------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "story_history" not in st.session_state:
    st.session_state.story_history = []

if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

# --------------------------
# GENERATE STORY
# --------------------------

def generate_story(user_choice):

    system_prompt = f"""
You are an advanced Visual Novel Director.

Genre: {genre}
Selected Art Style: {art_style}

The image_prompt must strongly follow the selected art style.

Anime:
- anime
- manga
- japanese animation
- colorful anime scene

Cinematic:
- movie scene
- dramatic lighting
- realistic

Pixel Art:
- retro game graphics
- pixel art

Fantasy Painting:
- fantasy artwork
- magical environment

Realistic:
- photorealistic
- real world photography

3D Render:
- octane render
- ray tracing
- blender render

Always respond ONLY in valid JSON.

Required format:

{{
  "story_text":"Narrative here",
  "image_prompt":"Highly detailed image prompt",
  "options":["Choice1","Choice2","Choice3"]
}}

Rules:

1. story_text must be 100-150 words.
2. image_prompt must be extremely detailed.
3. options must contain 2-3 choices.
4. Never output markdown.
5. Never output explanations.
6. Output valid JSON only.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    for msg in st.session_state.messages:
        messages.append(msg)

    messages.append({
        "role":"user",
        "content":user_choice
    })

    try:

        response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=messages,
    temperature=0.9
)

        result = response.choices[0].message.content

        parsed = json.loads(result)

        st.session_state.messages.append({
            "role":"user",
            "content":user_choice
        })

        st.session_state.messages.append({
            "role":"assistant",
            "content":result
        })

        return parsed

    except Exception as e:

        st.error(f"Story generation failed: {e}")

        return None

# --------------------------
# POLLINATIONS IMAGE
# --------------------------

def generate_image(prompt):

    style_prefix = STYLE_PROMPTS.get(art_style, "")

    final_prompt = f"""
    {style_prefix}

    {prompt}

    masterpiece,
    best quality,
    highly detailed,
    8k
    """

    try:

        url = (
            f"https://image.pollinations.ai/prompt/"
            f"{requests.utils.quote(final_prompt)}"
            "?width=1024&height=1024&enhance=true&nologo=true"
            )
        response = requests.get(
            url,
            timeout=30
        )

        image = Image.open(
            BytesIO(response.content)
        )

        return image

    except:

        st.toast(
            "Image server busy, skipping visual..."
        )

        return None

# --------------------------
# TTS
# --------------------------

def create_audio(text):

    try:

        tts = gTTS(
            text=text,
            lang="en"
        )

        tmp = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp3"
        )

        tts.save(tmp.name)

        return tmp.name

    except:

        st.toast(
            "Audio generation failed."
        )

        return None

# --------------------------
# TITLE
# --------------------------

st.title("🎮 AI Multi-Modal Visual Novel")

st.caption(
    "JSON Parsing • Dynamic UI • Pollinations • TTS • Streamlit"
)

# --------------------------
# START GAME
# --------------------------

if not st.session_state.chat_started:

    if st.button("🚀 Start Adventure"):

        st.session_state.chat_started = True

        result = generate_story(
            "Start the story"
        )

        if result:
            st.session_state.story_history.append(
                result
            )

        st.rerun()

# --------------------------
# DISPLAY STORY
# --------------------------

for idx, scene in enumerate(
        st.session_state.story_history):

    st.markdown(
        f"## Scene {idx+1}"
    )

    image = generate_image(
        scene["image_prompt"]
    )

    if image:
        st.image(
            image,
            use_container_width=True
        )

    st.markdown(
        f"""
<div class='story-box'>
{scene['story_text']}
</div>
""",
        unsafe_allow_html=True
    )

    audio_file = create_audio(
        scene["story_text"]
    )

    if audio_file:
        st.audio(audio_file)

# --------------------------
# CURRENT OPTIONS
# --------------------------

if (
    len(st.session_state.story_history)
    > 0
):

    latest = st.session_state.story_history[-1]

    st.subheader(
        "What will you do next?"
    )

    cols = st.columns(
        len(latest["options"])
    )

    for i, option in enumerate(
        latest["options"]
    ):

        with cols[i]:

            if st.button(
                option,
                key=f"{i}_{option}"
            ):

                with st.spinner(
                    "Creating next scene..."
                ):

                    result = generate_story(
                        option
                    )

                    if result:

                        st.session_state.story_history.append(
                            result
                        )

                st.rerun()

# --------------------------
# STATS
# --------------------------

st.divider()

c1, c2, c3 = st.columns(3)

c1.metric(
    "Scenes Generated",
    len(st.session_state.story_history)
)

c2.metric(
    "Genre",
    genre
)

c3.metric(
    "Art Style",
    art_style
)