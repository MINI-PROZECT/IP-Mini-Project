import streamlit as st
import cv2
import numpy as np
import zlib
from io import BytesIO
from PIL import Image

# Set page configuration
st.set_page_config(page_title="Image Compression App", page_icon=":compression:", layout="wide")

# CSS styles
css = """
<style>
h1 {
    color: #2c3e50;
    font-weight: bold;
    text-align: center;
}
h2 {
    color: #2c3e50;
    font-weight: bold;
}
p {
    color: #34495e;
    font-size: 16px;
}
.info-box {
    background-color: #f5f5f5;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# Lossless Compression (Deflate)
def compress_lossless(image_bytes):
    compressed_bytes = zlib.compress(image_bytes, 9)
    return compressed_bytes

# Lossy Compression (JPEG)
def compress_lossy(image, quality):
    _, compressed_bytes = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return compressed_bytes.tobytes()

# Calculate Compression Metrics
def calculate_metrics(original_size, compressed_size):
    compression_ratio = original_size / compressed_size
    return {
        "Original Size (bytes)": original_size,
        "Compressed Size (bytes)": compressed_size,
        "Compression Ratio": compression_ratio,
    }

# Streamlit App
def main():
    st.title("Image Compression App")

    st.sidebar.title("Select Compression Algorithm")
    algorithm = st.sidebar.radio("", ("Lossless (Deflate)", "Lossy (JPEG)"))

    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "bmp", "tiff"])

    if uploaded_file is not None:
        image_bytes = np.frombuffer(uploaded_file.getvalue(), np.uint8)
        original_size = len(image_bytes)
        original_image = Image.open(BytesIO(image_bytes))

        st.subheader("Original Image")
        st.image(original_image, caption=f"Size: {original_size} bytes", use_column_width=True)

        if algorithm == "Lossy (JPEG)":
            quality = st.slider("Quality", 0, 100, value=80, help="Higher values result in better image quality (0-100)")

            with st.expander("About Lossy Compression"):
                st.markdown("""
                    <div class="info-box">
                    <h2>Lossy Compression (JPEG)</h2>
                    <p>Lossy compression algorithms, like JPEG, reduce the file size by removing some non-essential data from the original image. This results in a smaller file size, but it also introduces some quality loss and artifacts in the compressed image.</p>
                    <p>The JPEG compression algorithm works by dividing the image into 8x8 pixel blocks and applying a discrete cosine transform (DCT) to each block. The DCT helps to separate the image data into parts that are more easily compressible. The compression is achieved by quantizing and encoding the DCT coefficients.</p>
                    <p>The quality slider adjusts the level of quantization, allowing you to balance between file size and image quality. Higher quality settings retain more image details but result in larger file sizes, while lower quality settings produce smaller files but with more visible compression artifacts.</p>
                    </div>
                """, unsafe_allow_html=True)

        else:
            with st.expander("About Lossless Compression"):
                st.markdown("""
                    <div class="info-box">
                    <h2>Lossless Compression (Deflate)</h2>
                    <p>Lossless compression algorithms, like Deflate, reduce the file size without any loss of image data. This means that the decompressed image will be identical to the original image, with no quality loss or artifacts.</p>
                    <p>The Deflate algorithm, implemented using the zlib library in Python, is a combination of the LZ77 algorithm and Huffman coding. It works by identifying and replacing repeated sequences of bytes with shorter codes, and then compressing these codes using a technique called Huffman coding.</p>
                    <p>Lossless compression is particularly useful for images with large areas of solid colors or simple patterns, where data redundancy can be effectively exploited. However, for complex or highly detailed images, lossless compression may not achieve as significant file size reductions as lossy compression.</p>
                    </div>
                """, unsafe_allow_html=True)

        compress_button = st.button("Compress Image")
        if compress_button:
            if algorithm == "Lossless (Deflate)":
                compressed_bytes = compress_lossless(image_bytes)
                decompressed_bytes = zlib.decompress(compressed_bytes)
                compressed_image = Image.open(BytesIO(decompressed_bytes))
            else:
                image = cv2.imdecode(image_bytes, cv2.IMREAD_UNCHANGED)
                compressed_bytes = compress_lossy(image, quality)
                compressed_image = cv2.imdecode(np.frombuffer(compressed_bytes, np.uint8), cv2.IMREAD_UNCHANGED)

            compressed_size = len(compressed_bytes)
            metrics = calculate_metrics(original_size, compressed_size)

            st.subheader("Compressed Image")
            st.image(compressed_image, caption=f"Size: {compressed_size} bytes", use_column_width=True)

            st.subheader("Compression Metrics")
            st.table(metrics.items())

            st.download_button(
                label="Download Compressed Image",
                data=compressed_bytes,
                file_name=f"compressed_image.{'png' if algorithm == 'Lossless (Deflate)' else 'jpg'}",
                mime="image/png" if algorithm == "Lossless (Deflate)" else "image/jpeg",
            )

if __name__ == "__main__":
    main()