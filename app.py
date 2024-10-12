import streamlit as st
import numpy as np
import cv2 as cv
import exifread
from PIL import Image
import io
import pandas as pd
import matplotlib.pyplot as plt

# Function to extract EXIF metadata
def extract_exif(image):
    exif_data = {}
    tags = exifread.process_file(image)
    for tag in tags.keys():
        if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
            exif_data[tag] = str(tags[tag])
    return exif_data

# Function for JPEG Ghost detection by recompressing the image
def jpeg_ghost_detection(image, quality=75):
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    compressed_image = Image.open(buffer)

    # Convert images to grayscale for comparison
    original_gray = np.array(image.convert('L'))
    compressed_gray = np.array(compressed_image.convert('L'))

    # Compute the absolute difference between the original and recompressed image
    difference = cv.absdiff(original_gray, compressed_gray)

    return difference

# Streamlit App
st.set_page_config(page_title="Image Forensics", layout="wide")
st.title("Digital Image Forensics Tool")
st.markdown("Analyze images for EXIF metadata and JPEG Ghost artifacts to detect possible forgeries.")

# Sidebar options
st.sidebar.title("Options")
analysis_choice = st.sidebar.radio("Choose Analysis", ["EXIF Metadata", "JPEG Ghost Detection"])

# Upload image
uploaded_file = st.file_uploader("Upload a JPEG image for analysis", type="jpg")

if uploaded_file is not None:
    image = Image.open(uploaded_file)

    # Display the uploaded image
    st.image(image, caption="Uploaded Image", use_column_width=True)

    if analysis_choice == "EXIF Metadata":
        # EXIF Metadata Analysis
        st.subheader("EXIF Metadata")

        exif_data = extract_exif(uploaded_file)

        if exif_data:
            # Convert EXIF data into a pandas DataFrame for a clean table display
            exif_df = pd.DataFrame(list(exif_data.items()), columns=['Tag', 'Value'])

            # Display the EXIF metadata as a table
            st.table(exif_df)

            # Alternatively, you could display using st.markdown for customized formatting:
            st.markdown("### EXIF Metadata Information")
            for tag, value in exif_data.items():
                st.markdown(f"**{tag}:** {value}")
        else:
            st.write("No EXIF metadata found.")

    elif analysis_choice == "JPEG Ghost Detection":
        # JPEG Ghost Detection Analysis
        st.subheader("JPEG Ghost Detection")

        quality = st.sidebar.slider("Select recompression quality", 10, 95, 75)
        st.write(f"Recompression quality set to {quality}% for JPEG Ghost analysis.")

        with st.spinner("Analyzing JPEG Ghost artifacts..."):
            ghost_result = jpeg_ghost_detection(image, quality)

            # Display the original and ghost-detected image side by side
            fig, ax = plt.subplots(1, 2, figsize=(12, 6))
            
            # Show original image
            ax[0].imshow(image)
            ax[0].set_title("Original Image")
            ax[0].axis("off")

            # Show JPEG ghost result (difference) with color map
            ax[1].imshow(ghost_result, cmap="gray")
            ax[1].set_title("JPEG Ghost Detection Result")
            ax[1].axis("off")

            st.pyplot(fig)

# Footer for better UI/UX
st.markdown("""
    <style>
    footer {visibility: hidden;}
    footer:after {
        content:'Developed with Streamlit | Image Forensics Tool'; 
        visibility: visible;
        display: block;
        position: relative;
        padding: 5px;
        top: 2px;
    }
    </style>
""", unsafe_allow_html=True)
