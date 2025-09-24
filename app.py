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
            # Initialize decks
            if "ai_deck" not in st.session_state:
                st.session_state.ai_deck = ai_images.copy()
            if "real_deck" not in st.session_state:
                st.session_state.real_deck = real_images.copy()

            # End of game check
            if len(st.session_state.ai_deck) == 0 or len(st.session_state.real_deck) == 0:
                st.success("🎉 You’ve completed all challenges! Great job!")

                # Random tip/hint at the end
                tips = [
                    "Check for unnatural shadows or inconsistent lighting.",
                    "Look closely at the eyes — AI-generated faces often have asymmetrical reflections.",
                    "Check hair and ears — AI sometimes messes up fine details.",
                    "If something feels off, it might be AI-generated.",
                    "Use multiple sources when verifying content online.",
                    "AI often struggles with text or logos in images."
                ]
                st.info("Tip: " + random.choice(tips))
            else:
                # Pick images if not already set
                if "left_img" not in st.session_state or "right_img" not in st.session_state:
                    # Pick one random AI and one random real image
                    ai_img_name = random.choice(st.session_state.ai_deck)
                    st.session_state.ai_deck.remove(ai_img_name)

                    real_img_name = random.choice(st.session_state.real_deck)
                    st.session_state.real_deck.remove(real_img_name)

                    ai_img = Image.open(os.path.join(ai_folder, ai_img_name)).resize((400, 400))
                    real_img = Image.open(os.path.join(real_folder, real_img_name)).resize((400, 400))

                    # Randomize left/right
                    left_is_fake = random.choice([True, False])
                    if left_is_fake:
                        st.session_state.left_img = ai_img
                        st.session_state.right_img = real_img
                        st.session_state.left_is_fake = True
                    else:
                        st.session_state.left_img = real_img
                        st.session_state.right_img = ai_img
                        st.session_state.left_is_fake = False

                # Display images
                col1, col2 = st.columns([1,1])
                with col1:
                    st.image(st.session_state.left_img, caption="Left", use_container_width=True)
                with col2:
                    st.image(st.session_state.right_img, caption="Right", use_container_width=True)

                # Guess radio button
                guess = st.radio("Which is AI-generated?", ["Left", "Right"], key="guess")

                if st.button("Submit Guess"):
                    correct = "Left" if st.session_state.left_is_fake else "Right"
                    if guess == correct:
                        st.balloons()
                        st.success("Correct! 🎉")
                    else:
                        st.error(f"Wrong — the AI image was on the **{correct}**.")

                if st.button("New Challenge"):
                    # Clear current images for next round
                    st.session_state.left_img = None
                    st.session_state.right_img = None

# --- Tab 3: Tips & Safety ---
with tab3:
    st.header("Tips & Safety")
    st.write("""
    - Always be cautious with online AI tools and deepfake content.
    - Protect your personal photos and videos.
    - Learn to spot deepfakes using visual cues or detection tools.
    - Remember: AI can be used both creatively and maliciously.
    """)
