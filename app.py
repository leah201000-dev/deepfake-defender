import os
from PIL import Image
import random

# --- Mini-Game tab ---
with tab2:
    st.header("Mini-Game — Spot the AI image")
    st.write("Guess which image is AI-generated!")

    # Paths to image folders
    ai_folder = "assets/ai_faces"
    real_folder = "assets/real_faces"

    # Get list of image filenames
    ai_images = os.listdir(ai_folder)
    real_images = os.listdir(real_folder)

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
        real_img_name = random.choice(real_images)
        ai_img = Image.open(os.path.join(ai_folder, ai_img_name)).resize((400, 400))
        real_img = Image.open(os.path.join(real_folder, real_img_name)).resize((400, 400))

        if st.session_state.left_is_fake:
            st.session_state.left_img = ai_img
            st.session_state.right_img = real_img
        else:
            st.session_state.left_img = real_img
            st.session_state.right_img = ai_img

    # Display images
    col1, col2 = st.columns(2)
    with col1:
        st.image(st.session_state.left_img, caption="Left", use_container_width=True)
    with col2:
        st.image(st.session_state.right_img, caption="Right", use_container_width=True)

    # Guess
    guess = st.radio("Which is AI-generated?", ["Left", "Right"])
    if st.button("Submit Guess"):
        correct = "Left" if st.session_state.left_is_fake else "Right"
        if guess == correct:
            st.balloons()
            st.success("Correct! 🎉")
        else:
            st.error(f"Wrong — the AI image was on the **{correct}**.")
