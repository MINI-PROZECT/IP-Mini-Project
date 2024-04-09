import os
import streamlit as st
import tempfile
import base64
from PIL import Image
import numpy as np
import io

def compress_image(image, compression_quality, output_format, png_compression_level=None):
    # Convert image to RGB mode if it has an alpha channel
    if image.mode == 'RGBA':
        image = image.convert('RGB')

    # Resize if necessary
    image = image.resize((target_width, target_height), Image.LANCZOS) if not use_original_dimensions else image

    # Save the compressed image
    compressed_image = io.BytesIO()
    if output_format.lower() == 'png':
        image.save(compressed_image, format='PNG', optimize=True, quality=png_compression_level)
    else:
        image.save(compressed_image, format=output_format, quality=compression_quality)

    # Calculate sizes
    original_size = image.size
    compressed_size = len(compressed_image.getvalue())

    return compressed_image, original_size, compressed_size

# UI
st.title("Image Compression App")

compression_quality = st.slider("Compression Quality (0-100)", 0, 100, 80)  # Increased default quality for JPEG
use_original_dimensions = st.radio("Use Original Dimensions?", ("Yes", "No")) == "Yes"

if not use_original_dimensions:
    target_width = st.number_input("Enter Target Width", value=100)
    target_height = st.number_input("Enter Target Height", value=100)

output_format = st.selectbox("Output Format", ("JPEG", "PNG"))

if output_format.lower() == 'png':
    png_compression_level = st.slider("PNG Compression Level", 0, 9, 3)
else:
    png_compression_level = None

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Original Image", use_column_width=True)

    if st.button("Compress Image"):
        # Process and compress the uploaded image
        compressed_image, original_size, compressed_size = compress_image(image, compression_quality, output_format, png_compression_level)

        # Display compressed image
        st.image(compressed_image, caption="Compressed Image", use_column_width=True)

        # Show size comparison
        st.write(f"Original Size: {original_size[0]}x{original_size[1]} pixels")
        st.write(f"Compressed Size: {compressed_size} bytes")
        st.write(f"Compression Ratio: {original_size[0]*original_size[1]/compressed_size:.2f}x")

        # Add download button for compressed image
        st.markdown("<h2>Download Compressed Image</h2>", unsafe_allow_html=True)
        compressed_image.seek(0)
        btn = st.download_button(
            label="Download",
            data=compressed_image,
            file_name=f"compressed_image.{output_format.lower()}"
        )
