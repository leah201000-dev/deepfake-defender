import streamlit as st
from PIL import Image
import numpy as np
import io
import random
import requests

st.set_page_config(page_title="Deepfake Defender", layout="centered")

# --- helper functions ---
def load_image_from_bytes(bytes_data):
    return Image.open(io.BytesIO(bytes_data)).convert("RGB")

def load_image_from_url(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return load_image_from_bytes(r.content)

def ela_image_pil(pil_im, quality=90):
    """
    Error Level Analysis (ELA) — simple heuristic for detecting edits.
    Returns (ela_image (PIL), mean_difference_score (float))
    """
    with io.BytesIO() as f:
        pil_im.save(f, "JPEG", quality=quality)
        f.seek(0)
        recompressed = Image.open(f).convert("RGB")

    original = pil_im.convert("RGB")
    orig_np = np.array(original).astype("int32")
    recomp_np = np.array(recompressed).astype("int32")
    diff_np = np.abs(orig_np - recomp_np).astype("uint8")

    max_val = diff_np.max()
    if max_val == 0:
        max_val = 1
    ela_np = np.clip((diff_np.astype("float32") * (255.0 / float(max_val))), 0, 255).astype("uint8")
    ela_img = Image.fromarray(ela_np)
    mean_diff = float(diff_np.mean())
    return ela_img, mean_diff

def score_to_likelihood(mean_diff):
    likelihood = min(100.0, (mean_diff / 15.0) * 100.0)
    return likelihood

# --- UI ---
st.title("Deepfake Defender")
st.write("Use AI tools to detect possible manipulations and learn how to protect your identity & creativity online.")

tab1, tab2, tab3 = st.tabs(["Upload & Detect", "Mini-Game", "Tips & Safety"])

# ---------------- Tab 1: Upload & Detect ----------------
with tab1:
    st.header("Upload an image for a quick manipulation check (ELA)")
    uploaded_file = st.file_uploader("Upload an image file (png, jpg, jpeg)", type=["png","jpg","jpeg"])
    
    if uploaded_file is not None:
        try:
            img = Image.open(uploaded_file).convert("RGB")
            st.image(img, caption="Uploaded image", use_container_width=True)

            with st.spinner("Running quick analysis..."):
                ela_img, mean_diff = ela_image_pil(img, quality=90)
                likelihood = score_to_likelihood(mean_diff)
                verdict = "Likely manipulated" if likelihood > 30 else "Likely real / no strong edit signature"

            st.markdown(f"**Detection verdict:** {verdict}")
            st.metric("Manipulation likelihood", f"{likelihood:.0f}%")
            st.write("ELA (bright areas may indicate edits):")
            st.image(ela_img, use_container_width=True)

        except Exception as e:
            st.error("Sorry — couldn't process that image. Try a different file.")
            st.exception(e)

# ---------------- Tab 2: Mini-Game ----------------
with tab2:
    st.header("Mini-Game — Spot the AI image")
    st.write("You will see two images: one AI-generated and one real. Guess which one is AI-generated.")

    # Initialize session state
    if "left_is_fake" not in st.session_state:
        st.session_state.left_is_fake = random.choice([True, False])
        st.session_state.seed = random.randint(1, 99999)

    if st.button("New Challenge"):
        st.session_state.left_is_fake = random.choice([True, False])
        st.session_state.seed = random.randint(1, 99999)

    # Image URLs
    fake_url = "https://thispersondoesnotexist.com/image"
    real_url = f"https://picsum.photos/seed/{st.session_state.seed}/400/300"

    if st.session_state.left_is_fake:
        left_url, right_url = fake_url, real_url
    else:
        left_url, right_url = real_url, fake_url

    # Load images
    try:
        left_img = load_image_from_url(left_url)
        right_img = load_image_from_url(right_url)
    except Exception as e:
        st.warning("Could not load images for this round.")
        left_img, right_img = None, None

    # Display images
    col1, col2 = st.columns(2)
    with col1:
        if left_img is not None:
            st.image(left_img, caption="Left", use_container_width=True)
    with col2:
        if right_img is not None:
            st.image(right_img, caption="Right", use_container_width=True)

    guess = st.radio("Which is AI-generated?", options=["Left", "Right"])
    if st.button("Submit Guess"):
        correct_side = "Left" if st.session_state.left_is_fake else "Right"
        if guess == correct_side:
            st.balloons()
            st.success("Correct! 🎉")
        else:
            st.error(f"Not quite — the AI-generated image was on the **{correct_side}**.")

# ---------------- Tab 3: Tips & Safety ----------------
with tab3:
    st.header("Tips & Safety — Protect your identity and creativity")
    st.write("""
    **Quick safety tips**
    - Keep private voice recordings off public sites.
    - Use subtle watermarks on published artwork.
    - Verify sources: if you see a shocking video, check trustworthy outlets.
    - Keep raw high-quality originals offline or private.
    """)
