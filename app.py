import streamlit as st
from PIL import Image
import os
import random
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# --- Page config ---
st.set_page_config(
    page_title="Deepfake Defender",
    page_icon="🛡️",
    layout="centered"
)

# --- Global page title ---
st.markdown("<h1 style='text-align: center;'>Deepfake Defender</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["Upload & Detect", "Mini-Game", "Tips & Safety"])

# ---------------------------
# Tab 1: Upload & Detect
# ---------------------------
with tab1:
    st.header("Upload a File to Detect AI")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png"])

    if uploaded_file is not None:
        st.image(uploaded_file, use_container_width=True)
        img = Image.open(uploaded_file).convert("RGB")

        # --- Lightweight AI detection ---
        def extract_features(img):
            img = img.resize((64, 64))
            img = img.convert("RGB")
            arr = np.array(img)
            return arr.mean()

        # Load images for training
        ai_folder = "ai_faces"
        real_folder = "real_faces"
        valid_exts = [".jpg", ".jpeg", ".png"]

        ai_images = [f for f in os.listdir(ai_folder) if os.path.splitext(f)[1].lower() in valid_exts]
        real_images = [f for f in os.listdir(real_folder) if os.path.splitext(f)[1].lower() in valid_exts]

        X = []
        y = []

        for f in ai_images:
            feature = extract_features(Image.open(os.path.join(ai_folder,f)))
            X.append([feature])
            y.append(1)
        for f in real_images:
            feature = extract_features(Image.open(os.path.join(real_folder,f)))
            X.append([feature])
            y.append(0)

        X = np.array(X)
        y = np.array(y)

        clf = RandomForestClassifier(n_estimators=50)
        clf.fit(X, y)

        features = np.array([[extract_features(img)]])
        likelihood = clf.predict_proba(features)[0][1]*100
        verdict = "⚠️ Likely AI-generated" if likelihood > 50 else "✅ Likely Real"
        st.success("Scan complete!")
        st.write(f"{verdict} ({likelihood:.1f}%)")
        st.info("Tip: Look for unnatural blurs, weird facial expressions, or distorted features.")

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
        # initialize session state
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
            # Pick new images if starting or after clicking New Challenge
            if "left_img" not in st.session_state or not st.session_state.round_active:
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

            # Display images side by side
            col1, col2 = st.columns([1,1])
            with col1:
                st.image(st.session_state.left_img, caption="Left", use_container_width=True)
            with col2:
                st.image(st.session_state.right_img, caption="Right", use_container_width=True)

            # --- Display guess UI below images, only if not submitted ---
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
                        st.error("Wrong — try again! You must guess correctly to continue.")

            # --- New Challenge button ---
            if st.session_state.guess_submitted:
                if st.button("New Challenge"):
                    st.session_state.left_img = None
                    st.session_state.right_img = None
                    st.session_state.round_active = True
                    st.session_state.guess_submitted = False

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
