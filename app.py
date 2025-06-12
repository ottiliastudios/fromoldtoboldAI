
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import tempfile

st.set_page_config(page_title="From Old to Bold – OpenCV Measurement")

st.markdown("<h2 style='text-align: center;'>Measure Jewelry Size from Image</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Upload a photo of your jewelry next to a visible ruler. The system estimates the size using OpenCV.</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload image with visible ruler (horizontal)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(img)

    st.image(img, caption="Uploaded Image", use_container_width=True)

    # Konvertieren in Graustufen + Kanten finden
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    # Linien mit Hough-Transformation finden (versucht horizontale Lineale zu erkennen)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)

    scale_pixels = None

    if lines is not None:
        # Suche längste horizontale Linie → potenzielles Lineal
        max_len = 0
        for line in lines:
            x1, y1, x2, y2 = line[0]
            length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            angle = abs(np.arctan2(y2 - y1, x2 - x1)) * 180 / np.pi
            if length > max_len and angle < 10:  # nahezu horizontal
                max_len = length
                scale_pixels = length

    if scale_pixels:
        cm_in_pixels = scale_pixels / 10  # Angenommen, sichtbare Linie = 10 cm
        st.write(f"📏 Estimated scale: 1 cm ≈ {cm_in_pixels:.2f} pixels")

        # Schmuckstück-Fläche grob berechnen
        height, width = img_np.shape[:2]
        area_cm2 = (width / cm_in_pixels) * (height / cm_in_pixels)
        st.write(f"📐 Approximate image area: {area_cm2:.2f} cm²")

        assumed_thickness_cm = 0.3
        volume_cm3 = area_cm2 * assumed_thickness_cm
        st.write(f"📦 Estimated volume: {volume_cm3:.2f} cm³")

    else:
        st.warning("Could not detect a horizontal reference line (ruler). Try clearer image.")

