import streamlit as st
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import os
import random
import time

# --- Page config ---
st.set_page_config(
    page_title="Deepfake Defender",
    page_icon="🛡️",
    layout="centered"
)

# --- Global title ---
st.markdown("<h1 style='text-align: center;'>Deepfake Defender</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["AI Playground", "Mini-Game", "Tips & Safety"])

# --- Tab 1: AI Playground ---
with tab1:
    st.header("AI Playground / Experiment")
    st.write("Upload an image and try out different AI-style transformations!")

    uploaded_file = st.file_uploader("Upload image (JPG/PNG)...", type=["jpg", "png"])

    if uploaded_file is not None:
        img = Image.open(uploaded_file).convert("RGB")
        st.subheader("Original Image")
        st.image(img, use_column_width=True)

        # --- Controls under the image ---
        st.markdown("### Transformation Options")

        transformation_group = st.selectbox("Select Transformation Category:", [
            "Color",
            "Mirror/Flip",
            "Stylize"
        ])

        # Sub-options
        if transformation_group == "Color":
            option = st.selectbox("Select Color Effect:", [
                "Grayscale",
                "Invert Colors",
                "Sepia",
                "Solarize"
            ])
        elif transformation_group == "Mirror/Flip":
            option = st.selectbox("Select Mirror/Flip Effect:", [
                "Mirror Horizontally",
                "Mirror Vertically",
                "Rotate 90°",
                "Rotate 180°"
            ])
        else:  # Stylize
            option = st.selectbox("Select Stylize Effect:", [
                "Edge Enhance",
                "Emboss",
                "Blur",
                "Sharpen",
                "Posterize",
                "Pixelate"
            ])

        apply_btn = st.button("Apply Transformation")

        if apply_btn:
            with st.spinner("Processing image..."):
                time.sleep(0.5)  # simulate processing

                transformed = img.copy()

                # --- Color ---
                if option == "Grayscale":
                    transformed = ImageOps.grayscale(transformed)
                elif option == "Invert Colors":
                    transformed = ImageOps.invert(transformed)
                elif option == "Sepia":
                    sepia = ImageOps.colorize(ImageOps.grayscale(transformed),
                                              black="#704214", white="#FFDAB9")
                    transformed = sepia
                elif option == "Solarize":
                    transformed = ImageOps.solarize(transformed, threshold=128)

                # --- Mirror/Flip/Rotate ---
                elif option == "Mirror Horizontally":
                    transformed = ImageOps.mirror(transformed)
                elif option == "Mirror Vertically":
                    transformed = ImageOps.flip(transformed)
                elif option == "Rotate 90°":
                    transformed = transformed.rotate(90, expand=True)
                elif option == "Rotate 180°":
                    transformed = transformed.rotate(180, expand=True)

                # --- Stylize ---
                elif option == "Edge Enhance":
                    transformed = transformed.filter(ImageFilter.EDGE_ENHANCE)
                elif option == "Emboss":
                    transformed = transformed.filter(ImageFilter.EMBOSS)
                elif option == "Blur":
                    transformed = transformed.filter(ImageFilter.GaussianBlur(3))
                elif option == "Sharpen":
                    transformed = transformed.filter(ImageFilter.SHARPEN)
                elif option == "Posterize":
                    transformed = ImageOps.posterize(transformed, bits=3)
                elif option == "Pixelate":
                    small = transformed.resize((transformed.width // 16, transformed.height // 16), Image.NEAREST)
                    transformed = small.resize(transformed.size, Image.NEAREST)

                st.subheader("Transformed Image")
                st.image(transformed, use_container_width=True)

# --- Tab 2: Mini-Game ---
with tab2:
    st.write("Guess which image is AI-generated!")

    ai_folder = "ai_faces"
    real_folder = "real_faces"

    if not os.path.exists(ai_folder) or not os.path.exists(real_folder):
        st.error("AI or Real images folder not found. Make sure 'ai_faces' and 'real_faces' exist with images inside.")
    else:
        valid_extensions = [".jpg", ".jpeg", ".png"]
        ai_images = [f for f in os.listdir(ai_folder) if os.path.splitext(f)[1].lower() in valid_extensions]
        real_images = [f for f in os.listdir(real_folder) if os.path.splitext(f)[1].lower() in valid_extensions]

        if len(ai_images) == 0 or len(real_images) == 0:
            st.warning("No images found in one of the folders.")
        else:
            # Initialize decks and round state
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
                if "left_img" not in st.session_state or not st.session_state.round_active:
                    if len(st.session_state.ai_deck) > 0 and len(st.session_state.real_deck) > 0:
                        ai_img_name = random.choice(st.session_state.ai_deck)
                        st.session_state.ai_deck.remove(ai_img_name)

                        real_img_name = random.choice(st.session_state.real_deck)
                        st.session_state.real_deck.remove(real_img_name)

                        ai_img = Image.open(os.path.join(ai_folder, ai_img_name)).resize((400, 400))
                        real_img = Image.open(os.path.join(real_folder, real_img_name)).resize((400, 400))

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

                col1, col2 = st.columns([1, 1])
                with col1:
                    st.image(st.session_state.left_img, caption="Left", use_container_width=True)
                with col2:
                    st.image(st.session_state.right_img, caption="Right", use_container_width=True)

                if st.session_state.round_active and not st.session_state.guess_submitted:
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
    
