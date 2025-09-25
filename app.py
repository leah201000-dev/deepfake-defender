import streamlit as st
from PIL import Image
import numpy as np
import os
import random
import time
from sklearn.ensemble import RandomForestClassifier
import cv2

# ---------------------------
# Dummy lightweight AI detector
# ---------------------------
# This simple detector uses average color features as a placeholder
# for demonstration. In practice, you'd replace it with a small ML model.
def extract_features(img):
    img = img.resize((64, 64)).convert("RGB")
    arr = np.array(img)
    return arr.mean(axis=(0,1))  # simple RGB averages

# Train a dummy classifier on your AI vs real images
ai_images = [os.path.join("ai_faces", f) for f in os.listdir("ai_faces")]
real_images = [os.path.join("real_faces", f) for f in os.listdir("real_faces")]

X = []
y = []

for path in ai_images:
    img = Image.open(path)
    X.append(extract_features(img))
    y.append(1)  # 1 = AI

for path in real_images:
    img = Image.open(path)
    X.append(extract_features(img))
    y.append(0)  # 0 = Real

clf = RandomForestClassifier(n_estimators=50)
clf.fit(X, y)

def detect_ai(img):
    features = extract_features(img)
    prob = clf.predict_proba([features])[0][1] * 100
    return prob

# ---------------------------
# App title
# ---------------------------
st.title("🎮 Deepfake Defender")

# ---------------------------
# Tabs
# ---------------------------
tab1, tab2 = st.tabs(["Mini-Game", "Upload to Detect"])

# ---------------------------
# Mini-Game Tab
# ---------------------------
with tab1:
    if 'round' not in st.session_state:
        st.session_state.round = 0
        st.session_state.correct_count = 0
        st.session_state.images = list(zip(
            os.listdir("ai_faces"), 
            os.listdir("real_faces")
        ))
        random.shuffle(st.session_state.images)
        st.session_state.show_tip = False

    if st.session_state.round < len(st.session_state.images):
        ai_img_name, real_img_name = st.session_state.images[st.session_state.round]
        left_right = random.choice(["left_ai", "right_ai"])
        
        if left_right == "left_ai":
            left_img = Image.open(os.path.join("ai_faces", ai_img_name)).resize((400,400))
            right_img = Image.open(os.path.join("real_faces", real_img_name)).resize((400,400))
            st.session_state.correct_answer = "left"
        else:
            right_img = Image.open(os.path.join("ai_faces", ai_img_name)).resize((400,400))
            left_img = Image.open(os.path.join("real_faces", real_img_name)).resize((400,400))
            st.session_state.correct_answer = "right"

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Left"):
                if st.session_state.correct_answer == "left":
                    st.success("✅ Correct!")
                    st.session_state.correct_count +=1
                    st.session_state.round +=1
                else:
                    st.error("❌ Wrong! Try again.")
        with col2:
            if st.button("Right"):
                if st.session_state.correct_answer == "right":
                    st.success("✅ Correct!")
                    st.session_state.correct_count +=1
                    st.session_state.round +=1
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
    uploaded_file = st.file_uploader("Upload an image to detect AI", type=["jpg","jpeg","png"])
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
