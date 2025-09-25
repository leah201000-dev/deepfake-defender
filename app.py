import streamlit as st
from PIL import Image, ImageOps, ImageEnhance
import os
import random

# --- Page config ---
st.set_page_config(
    page_title="Deepfake Defender 🛡️ — AI Powered",
    page_icon="🛡️",
    layout="centered"
)

# --- Global page title ---
st.markdown("<h1 style='text-align: center;'>Deepfake Defender 🛡️ — AI Powered</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["AI Playground", "Mini-Game", "Tips & Safety"])

# --- Tab 1: AI Playground ---
with tab1:
    st.header("AI Playground — Experiment with Images")
    uploaded_file = st.file_uploader("Upload an image to experiment with:", type=["jpg", "png"])

    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Original Image", use_container_width=True)

        # Transform options
        st.subheader("Image Transformations")
        col1, col2 = st.columns(2)

        with col1:
            if st.checkbox("Convert to Grayscale"):
                img = ImageOps.grayscale(img)
            if st.checkbox("Invert Colors"):
                img = ImageOps.invert(img.convert("RGB"))

        with col2:
            brightness = st.slider("Adjust Brightness", 0.5, 2.0, 1.0)
            contrast = st.slider("Adjust Contrast", 0.5, 2.0, 1.0)
            img = ImageEnhance.Brightness(img).enhance(brightness)
            img = ImageEnhance.Contrast(img).enhance(contrast)

        # Flip and rotate options
        flip_h = st.checkbox("Flip Horizontally")
        flip_v = st.checkbox("Flip Vertically")
        rotate = st.slider("Rotate Degrees", 0, 360, 0)

        if flip_h:
            img = ImageOps.mirror(img)
        if flip_v:
            img = ImageOps.flip(img)
        if rotate != 0:
            img = img.rotate(rotate)

        st.subheader("Transformed Image")
        st.image(img, use_container_width=True)

# --- Tab 2: Mini-Game ---
with tab2:
    st.header("Mini-Game — Guess the AI Image")
    ai_folder = "ai_faces"
    real_folder = "real_faces"

    # Check folders
    if not os.path.exists(ai_folder) or not os.path.exists(real_folder):
        st.error("AI or Real images folder not found. Make sure 'ai_faces' and 'real_faces' exist with images inside.")
    else:
        valid_extensions = [".jpg", ".jpeg", ".png"]
        ai_images = [f for f in os.listdir(ai_folder) if os.path.splitext(f)[1].lower() in valid_extensions]
        real_images = [f for f in os.listdir(real_folder) if os.path.splitext(f)[1].lower() in valid_extensions]

        if len(ai_images) == 0 or len(real_images) == 0:
            st.warning("No images found in one of the folders.")
        else:
            if "ai_deck" not in st.session_state:
                st.session_state.ai_deck = ai_images.copy()
            if "real_deck" not in st.session_state:
                st.session_state.real_deck = real_images.copy()
            if "round_active" not in st.session_state:
                st.session_state.round_active = True
            if "guess_submitted" not in st.session_state:
                st.session_state.guess_submitted = False

            # End-of-game
            if len(st.session_state.ai_deck) == 0 or len(st.session_state.real_deck) == 0:
                st.success("🎉 You’ve completed all challenges! Great job!")
                tips = [
                    "Look for unnatural blurs or smudges around facial features.",
                    "Notice weird facial expressions or asymmetry.",
                    "Check for distorted or misaligned facial proportions.",
                    "Eyes, ears, and teeth can sometimes appear distorted in AI images.",
                    "Shadows and lighting might look unnatural or inconsistent."
                ]
                st.info("Tip: " + random.choice(tips))
            else:
                # Pick new images if starting or after correct guess
                if "left_img" not in st.session_state or not st.session_state.round_active:
                    if len(st.session_state.ai_deck) > 0 and len(st.session_state.real_deck) > 0:
                        ai_img_name = random.choice(st.session_state.ai_deck)
                        st.session_state.ai_deck.remove(ai_img_name)

                        real_img_name = random.choice(st.session_state.real_deck)
                        st.session_state.real_deck.remove(real_img_name)

                        ai_img = Image.open(os.path.join(ai_folder, ai_img_name)).resize((400, 400))
                        real_img = Image.open(os.path.join(real_folder, real_img_name)).resize((400, 400))

                        # Random left/right placement
                        left_is_fake = random.choice([True, False])
                        if left_is_fake:
                            st.session_state.left_img = ai_img
                            st.session_state.right_img = real_img
                            st.session_state.left_is_fake = True
                        else:
                            st.session_state.left_img = real_img
                            st.session_state.right_img = ai_img
                            st.session_state.left_is_fake = False

                        st.session_state.round_active = True
                        st.session_state.guess_submitted = False

                # Display images
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.image(st.session_state.left_img, caption="Left", use_container_width=True)
                with col2:
                    st.image(st.session_state.right_img, caption="Right", use_container_width=True)

                # Only allow guess if not yet submitted
                if not st.session_state.guess_submitted:
                    guess = st.radio("Which is AI-generated?", ["Left", "Right"], key="guess")

                    if st.button("Submit Guess"):
                        correct = "Left" if st.session_state.left_is_fake else "Right"
                        if guess == correct:
                            st.balloons()
                            st.success("Correct! 🎉")
                            st.session_state.guess_submitted = True
                            st.session_state.round_active = False
                        else:
                            st.error(f"Wrong — try again! The AI image was not {guess}.")

                # Show New Challenge button only after correct guess
                if st.session_state.guess_submitted:
                    if st.button("New Challenge"):
                        st.session_state.left_img = None
                        st.session_state.right_img = None
                        st.session_state.round_active = True
                        st.session_state.guess_submitted = False

# --- Tab 3: Tips & Safety ---
with tab3:
    st.header("Tips & Safety")
    st.write("""
    - Always be cautious with online AI tools and deepfake content.
    - Protect your personal photos and videos.
    - Learn to spot deepfakes using visual cues or detection tools.
    - Remember: AI can be used both creatively and maliciously.
    """)
