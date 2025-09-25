import streamlit as st
from PIL import Image
import os
import random
import numpy as np
import cv2
from sklearn.ensemble import RandomForestClassifier

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
tab1, tab2, tab3 = st.tabs(["Upload & Detect", "Mini-Game", "Tips & Safety"])

# ---------------------------
# Tab 1: Upload & Detect
# ---------------------------
with tab1:
    st.header("Upload a File to Detect Deepfake")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png"])

    if uploaded_file is not None:
        st.image(uploaded_file, use_container_width=True)
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)

        try:
            # Simple "fake detection" using mean RGB features for demo
            def extract_features(image: Image.Image):
                arr = np.array(image.resize((64,64)))
                return arr.mean(axis=(0,1,2))

            X = []
            y = []
            for f in os.listdir("ai_faces"):
                if f.lower().endswith((".jpg",".jpeg",".png")):
                    X.append(extract_features(Image.open(os.path.join("ai_faces",f))))
                    y.append(1)  # AI
            for f in os.listdir("real_faces"):
                if f.lower().endswith((".jpg",".jpeg",".png")):
                    X.append(extract_features(Image.open(os.path.join("real_faces",f))))
                    y.append(0)  # Real

            X = np.array(X)
            y = np.array(y)

            clf = RandomForestClassifier()
            clf.fit(X, y)

            uploaded_features = extract_features(Image.open(uploaded_file))
            pred = clf.predict([uploaded_features])[0]

            if pred == 1:
                st.error("⚠️ Likely AI-generated")
            else:
                st.success("✅ Likely real / no strong AI signature")

        except Exception as e:
            st.error(f"Could not analyze the image. Error: {e}")

# ---------------------------
# Tab 2: Mini-Game
# ---------------------------
with tab2:
    st.write("Guess which image is AI-generated!")

    ai_folder = "ai_faces"
    real_folder = "real_faces"
    valid_exts = [".jpg", ".jpeg", ".png"]

    ai_images = [f for f in os.listdir(ai_folder) if os.path.splitext(f)[1].lower() in valid_exts]
    real_images = [f for f in os.listdir(real_folder) if os.path.splitext(f)[1].lower() in valid_exts]

    if len(ai_images) == 0 or len(real_images) == 0:
        st.warning("No images found in one of the folders.")
    else:
        # Initialize session state
        if "ai_deck" not in st.session_state:
            st.session_state.ai_deck = ai_images.copy()
        if "real_deck" not in st.session_state:
            st.session_state.real_deck = real_images.copy()
        if "round_active" not in st.session_state:
            st.session_state.round_active = True
        if "guess_submitted" not in st.session_state:
            st.session_state.guess_submitted = False
        if "current_round_completed" not in st.session_state:
            st.session_state.current_round_completed = False
        if "round_number" not in st.session_state:
            st.session_state.round_number = 0

        # End-of-game
        if len(st.session_state.ai_deck) == 0 or len(st.session_state.real_deck) == 0:
            st.success("🎉 You’ve completed all challenges!")
            tips = [
                "Look for unnatural blurs or smudges around facial features.",
                "Notice weird facial expressions or asymmetry.",
                "Check for distorted or misaligned facial proportions.",
                "Eyes, ears, and teeth can sometimes appear distorted in AI images.",
                "Shadows and lighting might look unnatural or inconsistent."
            ]
            st.info("Tip: " + random.choice(tips))

        else:
            # Pick new images if starting or after New Challenge
            if st.session_state.round_active and not st.session_state.current_round_completed:
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

                st.session_state.guess_submitted = False
                st.session_state.current_round_completed = False
                st.session_state.round_number += 1

            # Display images
            col1, col2 = st.columns([1,1])
            with col1:
                st.image(st.session_state.left_img, caption="Left", use_container_width=True)
            with col2:
                st.image(st.session_state.right_img, caption="Right", use_container_width=True)

            # Guess only if not yet submitted
            if not st.session_state.guess_submitted and not st.session_state.current_round_completed:
                guess = st.radio("Which is AI-generated?", ["Left", "Right"], key=f"guess_{st.session_state.round_number}")
                if st.button("Submit Guess", key=f"submit_{st.session_state.round_number}"):
                    correct = "Left" if st.session_state.left_is_fake else "Right"
                    if guess == correct:
                        st.balloons()
                        st.success("Correct! 🎉")
                        st.session_state.guess_submitted = True
                        st.session_state.current_round_completed = True
                        st.session_state.round_active = False
                    else:
                        st.error("Wrong — try again! You must guess correctly to continue.")

            # New Challenge button only appears after correct guess
            if st.session_state.guess_submitted:
                if st.button("New Challenge"):
                    st.session_state.left_img = None
                    st.session_state.right_img = None
                    st.session_state.round_active = True
                    st.session_state.guess_submitted = False
                    st.session_state.current_round_completed = False

# ---------------------------
# Tab 3: Tips & Safety
# ---------------------------
with tab3:
    st.header("Tips & Safety")
    st.write("""
    - Always be cautious with online AI tools and deepfake content.
    - Protect your personal photos and videos.
    - Learn to spot deepfakes using visual cues or detection tools.
    - Remember: AI can be used both creatively and maliciously.
    """)
