import streamlit as st
import requests
import random
from urllib.parse import quote

st.set_page_config(page_title="AI Image Studio", page_icon="🎨")

st.title("🎨 AI Image Studio")

# Sidebar
st.sidebar.header("Settings")

art_style = st.sidebar.selectbox(
    "🎨 Choose Art Style",
    [
        "Photorealistic",
        "Anime",
        "Sketch",
        "Watercolor",
        "3D Render",
        "Fantasy",
        "Cyberpunk"
    ]
)

width = st.sidebar.slider(
    "Image Width",
    min_value=256,
    max_value=1024,
    value=768,
    step=64
)

height = st.sidebar.slider(
    "Image Height",
    min_value=256,
    max_value=1024,
    value=768,
    step=64
)

magic_enhance = st.sidebar.checkbox("✨ Enable Magic Enhance")

surprise_prompts = [
    "An astronaut riding a horse on Mars",
    "A cyberpunk street food vendor in Tokyo",
    "A dragon flying over the Himalayas",
    "A futuristic underwater city",
    "A cute panda driving a sports car"
]

user_prompt = st.text_input(
    "Describe the image you want to generate"
)

def generate_image(prompt):

    full_prompt = f"{prompt}, {art_style}"

    if magic_enhance:
        full_prompt += ", masterpiece, 8k resolution, highly detailed, trending on artstation, unreal engine 5 render"

    encoded_prompt = quote(full_prompt)

    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}"

    with st.spinner("Generating Image..."):

        response = requests.get(url)

        if response.status_code == 200:

            st.success("Image Generated Successfully!")

            st.image(
                response.content,
                caption=full_prompt,
                use_container_width=True
            )

            st.download_button(
                label="📥 Download Image",
                data=response.content,
                file_name=f"{art_style}_image.png",
                mime="image/png"
            )

        else:
            st.error("Failed to generate image.")

# Generate Button
if st.button("🚀 Generate Image"):

    if user_prompt.strip() == "":
        st.warning("Please enter a prompt.")
    else:
        generate_image(user_prompt)

# Surprise Me Button
if st.button("🎲 Surprise Me!"):

    random_prompt = random.choice(surprise_prompts)

    st.info(f"Prompt: {random_prompt}")

    generate_image(random_prompt)