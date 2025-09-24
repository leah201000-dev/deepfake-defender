import streamlit as st
from PIL import Image
import os
import random

# --- Page config ---
st.set_page_config(page_title="Deepfake Defender", layout="centered")

# --- Define Tabs ---
tab1, tab2, tab3 = st.tabs(["Upload & Detect", "Mini-Game", "Tips & Safety"])

# --- Tab 1: Upload & Detect ---
with tab1:
    st.header("Upload a File to Detect Deepfake")
    uploaded_file = st.file_uploader("Choose an image or video...", type=["jpg", "png", "mp4"])
    
    if uploaded_file is not None:
        st.write("File uploaded! You can implement detection here.")
        st.image(uploaded_file, use_container_width=True)

# --- Tab 2: Mini-Game ---
with tab2:
    st.header("Mini-Game — Spot the AI image")
    st.write("Guess which image is AI-generated!")

    # Paths to image folders
    ai_folder = "ai_faces"
    real_folder = "real_faces"

    # Check if folders exist
    if not os.path.exists(ai_folder) or not os.path.exists(real_folder):
        st.error("AI or Real images folder not found. Make sure 'ai_faces' and 'real_faces' exist with images inside.")
    else:
        # List only image files
        valid_extensions = [".jpg", ".jpeg", ".png"]
        ai_images = [f for f in os.listdir(ai_folder) if os.path.splitext(f)[1].lower() in valid_extensions]
        real_images = [f for f in os.listdir(real_folder) if os.path.splitext(f)[1].lower() in valid_extensions]

        if len(ai_images) == 0 or len(real_images) == 0:
            st.warning("No images found in one of the folders.")
        else:
            # Initialize session state
            if "left_is_fake" not in st.session_state:
                st.session_state.left_is_fake = random.choice([True, False])
                st.session_state.left_img = None
                st.session_state.right_img = None

            if st.button("New Challenge"):
                st.session_state.left_is_fake = random.choice([True, False])
                st.session_state.left_img = None
                st.session_state.right_img = None

            # Pick images if not already chosen
            if st.session_state.left_img is None or st.session_state.right_img is None:
                ai_img_name = random.choice(ai_images)
                # Ensure the real image is not the same filename (just in case)
                real_img_name = random.choice([img for img in real_images if img != ai_img_name])

                ai_img = Image.open(os.path.join(ai_folder, ai_img_name)).resize((400, 400))
                real_img = Image.open(os.path.join(real_folder, real_img_name)).resize((400, 400))

                # Randomize left/right
                if st.session_state.left_is_fake:
                    st.session_state.left_img = ai_img
                    st.session_state.right_img = real_img
                else:
                    st.session_state.left_img = real_img
                    st.session_state.right_img = ai_img

            # Display images in equal columns
            col1, col2 = st.columns([1,1])
            with col1:
                st.image(st.session_state.left_img, caption="Left", use_container_width=True)
            with col2:
                st.image(st.session_state.right_img, caption="Right", use_container_width=True)

            # Guess radio button
            guess = st.radio("Which is AI-generated?", ["Left", "Right"])
            if st.button("Submit Guess"):
                correct = "Left" if st.session_state.left_is_fake else "Right"
                if guess == correct:
                    st.balloons()
                    st.success("Correct! 🎉")
                else:
                    st.error(f"Wrong — the AI image was on the **{correct}**.")

# --- Tab 3: Tips & Safety ---
with tab3:
    st.header("Tips & Safety")
    st.write("""
    - Always be cautious with online AI tools and deepfake content.
    - Protect your personal photos and videos.
    - Learn to spot deepfakes using visual cues or detection tools.
    - Remember: AI can be used both creatively and maliciously.
    """)
