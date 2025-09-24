# app.py — Deepfake Defender (starter with ELA image check + mini-game)
import streamlit as st
from PIL import Image
import numpy as np
import io
import requests
import random
import os

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
    # Recompress to JPEG in memory
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
    # scale difference to full 0-255 for visual ELA image
    ela_np = np.clip((diff_np.astype("float32") * (255.0 / float(max_val))), 0, 255).astype("uint8")
    ela_img = Image.fromarray(ela_np)
    mean_diff = float(diff_np.mean())
    return ela_img, mean_diff

def score_to_likelihood(mean_diff):
    """
    Convert mean ELA diff -> rough 'manipulation likelihood' percentage.
    Heuristic: larger mean_diff => more likely edited.
    Tune divisor (15.0) later if needed.
    """
    likelihood = min(100.0, (mean_diff / 15.0) * 100.0)
    return likelihood

# --- UI ---
st.title("Deepfake Defender")
st.write("Use AI tools to *detect* possible manipulations and learn how to protect identity & creativity online.")

tab1, tab2, tab3 = st.tabs(["Upload & Detect", "Mini-Game", "Tips & Safety"])

# ---------------- Tab 1: Upload & Detect ----------------
with tab1:
    st.header("Upload an image for a quick manipulation check (ELA)")
    uploaded_file = st.file_uploader("Upload an image file (png, jpg, jpeg)", type=["png","jpg","jpeg"])
    if uploaded_file is not None:
        try:
            img = Image.open(uploaded_file).convert("RGB")
            st.image(img, caption="Uploaded image", use_column_width=True)

            with st.spinner("Running quick analysis..."):
                ela_img, mean_diff = ela_image_pil(img, quality=90)
                likelihood = score_to_likelihood(mean_diff)
                verdict = "Likely manipulated" if likelihood > 30 else "Likely real / no strong edit signature"
