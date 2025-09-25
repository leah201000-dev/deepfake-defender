import streamlit as st
from PIL import Image
import numpy as np
import os
import random
import time
from sklearn.ensemble import RandomForestClassifier
import cv2

# ---------------------------
# App title
# ---------------------------
st.title("🎮 Deepfake Defender")

# ---------------------------
# Lightweight AI detection model
# ---------------------------
def extract_features(img):
    img = img.resize((64, 64)).convert("RGB")
    arr = np.array(img)
    return arr.mean(axis=(0,1))

# Train classifier on AI vs real images
ai_images = [os.path.join("ai_faces", f) for f in os.listdir("ai_faces")]
real_images = [os.path.join("real_faces", f) for f in os.listdir("real_faces")]

X = []
y = []

for path in ai_images:
    img = Image.open(path)
    X.append(extract_features(img))
    y.append(1)

for path in real_images:
    img = Image.open(path)
    X.append(extract_features(img))
    y.append(0)

clf = RandomForestClassifier(n_estimators=50)
clf.fit(X, y)

def detect_ai(img):
    features = extract_features(img)
    prob = clf.predict_proba([features])[0][1] * 100
    return prob

# ---------------------------
# Tabs
# ---------------------------
tab1, tab2, tab3 = st.tabs(["Mini-Game", "Upload to Detect", "Info"])

# ---------------------------
# Mini-Game Tab
# ---------------------------
with tab1:
    st.header("Mini-Game: Spot the AI image!")
    if 'round' not in st.session_state:
        st.session_state.round = 0
        st.session_state.correct_count = 0
        st.session_state.images = list(zip(
            os.listdir("ai_faces"), 
            os.listdir("real_faces")
        ))
        random.shuffle(st.session_state.images)
        st.session_state.show_tip = False
        st.session_state.left_img_name = None
        st.session_state.right_img_name = None
        st.session_state.correct_answer = None

    def new_challenge():
        if st.session_state.round < len(st.session_state.images):
            ai_img_name, real_img_name = st.session_state.images[st.session_state.round]
            left_right = random.choice(["left_ai", "right_ai"])
            if left_right == "left_ai":
                st.session_state.left_img_name = ai_img_name
                st.session_state.right_img_name = real_img_name
                st.session_state.correct_answer = "left"
            else:
                st.session_state.right_img_name = ai_img_name
                st.session_state.left_img_name = real_img_name
                st.session_state.correct_answer = "right"

    if st.session_state.left_img_name is None or st.session_state.right_img_name is None:
        new_challenge()

    if st.session_state.round < len(st.session_state.images):
        col1, col2 = st.columns(2)
        left_img = Image.open(os.path.join("ai_faces" if st.session_state.correct_answer=="left" else "real_faces", st.session_state.left_img_name if st.session_state.correct_answer=="left" else st.session_state.left_img_name)).resize((400,400))
        right_img = Image.open(os.path.join("ai_faces" if st.session_state.correct_answer=="right" else "real_faces", st.session_state.right_img_name if st.session_state.correct_answer=="right" else st.session_state.right_img_name)).resize((400,400))

        with col1:
            if st.button("Left"):
                if st.session_state.correct_answer == "left":
                    st.success("✅ Correct!")
                    st.session_state.correct_count +=1
                    st.session_state.round +=1
                    new_challenge()
                else:
                    st.error("❌ Wrong! Try again.")
        with col2:
            if st.button("Right"):
                if st.session_state.correct_answer == "right":
                    st.success("✅ Correct!")
                    st.session_state.correct_count +=1
                    st.session_state.round +=1
                    new_challenge()
                else:
                    st.error("❌ Wrong! Try again.")

        col1.image(left_img, use_container_width=True)
        col2.image(right_img, use_container_width=True)
    else:
        st.success(f"🎉 All rounds completed! Correct guesses: {st.session_state.correct_count}/{len(st.session_state.images)}")
        st.info("Tip: Look for unnatural blurs, weird facial expressions, or distorted features in AI-generated images.")

# ---------------------------
# Upload Tab
# ---------------------------
with tab2:
    st.header("Upload an image to detect AI")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg","jpeg","png"])
    if uploaded_file is not None:
        pil_img = Image.open(uploaded_file).convert("RGB")
        st.image(pil_img, use_container_width=True)
        with st.spinner("Scanning for AI artifacts..."):
            likelihood = detect_ai(pil_img)
            time.sleep(1)
        verdict = "⚠️ Likely AI-generated" if likelihood > 50 else "✅ Likely Real"
        st.success("Scan complete!")
        st.write(f"{verdict} ({likelihood:.1f}%)")
        st.info("Tip: Check for unnatural blurs, weird facial expressions, or distorted features.")

# ---------------------------
# Info Tab
# ---------------------------
with tab3:
    st.header("About Deepfake Defender")
    st.write("""
    This website lets you play a mini-game to spot AI-generated images and also upload your own images to check if they are AI-generated.  
    Developed for the Girls Who Code Challenge 2025-2026.
    """)
