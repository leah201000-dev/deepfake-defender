# ---------------- Tab 2: Mini-Game ----------------
with tab2:
    st.header("Mini-Game — Spot the AI image")
    st.write("You will see two images: one AI-generated and one real. Guess which one is AI-generated.")

    # Initialize session state
    if "left_is_fake" not in st.session_state:
        st.session_state.left_is_fake = random.choice([True, False])
        st.session_state.seed = random.randint(1, 99999)
        st.session_state.left_img = None
        st.session_state.right_img = None

    if st.button("New Challenge"):
        st.session_state.left_is_fake = random.choice([True, False])
        st.session_state.seed = random.randint(1, 99999)
        st.session_state.left_img = None
        st.session_state.right_img = None

    # Retry function
    def load_image_with_retry(url, retries=5):
        for _ in range(retries):
            try:
                return load_image_from_url(url)
            except:
                continue
        return None

    # Only load images if not cached
    if st.session_state.left_img is None or st.session_state.right_img is None:
        fake_url = "https://thispersondoesnotexist.com/image"
        real_url = f"https://picsum.photos/seed/{st.session_state.seed}/400/300"

        if st.session_state.left_is_fake:
            st.session_state.left_img = load_image_with_retry(fake_url)
            st.session_state.right_img = load_image_with_retry(real_url)
        else:
            st.session_state.left_img = load_image_with_retry(real_url)
            st.session_state.right_img = load_image_with_retry(fake_url)

    # Display images
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.left_img is not None:
            st.image(st.session_state.left_img, caption="Left", use_container_width=True)
        else:
            st.write("Failed to load left image. Try 'New Challenge'.")
    with col2:
        if st.session_state.right_img is not None:
            st.image(st.session_state.right_img, caption="Right", use_container_width=True)
        else:
            st.write("Failed to load right image. Try 'New Challenge'.")

    guess = st.radio("Which is AI-generated?", options=["Left", "Right"])
    if st.button("Submit Guess"):
        correct_side = "Left" if st.session_state.left_is_fake else "Right"
        if guess == correct_side:
            st.balloons()
            st.success("Correct! 🎉")
        else:
            st.error(f"Not quite — the AI-generated image was on the **{correct_side}**.")
