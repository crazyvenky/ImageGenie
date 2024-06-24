import streamlit as st
from PIL import Image
import google.generativeai as genai
import re

API_KEY = 'AIzaSyDZX1YJjjTIomxfOmkAyzXXnuiKe5tuitk'
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("Auto Edit Image")
instructions = st.text_area("paste the copied instructions here :", "")

# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    width, height = image.size
    size_bytes = len(uploaded_file.getvalue())
    size_kb = size_bytes / 1024
    format = image.format
    image_details_str = f"Width: {width} px, Height: {height} px, Size: {int(size_kb + 1)} KB, Format: {format}"
    
    st.write("Original Image Details:",image_details_str)
    
    suffix = f"Respond with the optimal width, height, and quality as a Python list in this format: [width, height, quality]. Do not include any additional text or explanations."
    prompt = f"Instructions:({instructions} )  ;  Original Image details:( {image_details_str}), {suffix}"

    response = model.generate_content(prompt)
    gemini_reply = response.text

    pattern = r"\[(\d+),\s*(\d+),\s*(\d+)\]"
    match = re.search(pattern, gemini_reply)

    if match:
        update_width, update_height, update_quality = map(int, match.groups())  
        st.write("Recommended Image Details:")
        st.write(f"Width: {update_width} px, Height: {update_height} px, Quality: {update_quality}")
    else:
        st.error("Gemini did not provide a valid response. Please check the instructions and try again.")


#############################################################################################################################################################################################################


if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Original Image", use_column_width=True)

    # Input fields for modifications (using session state for live updates)
    if "new_width" not in st.session_state:
        st.session_state.new_width = update_width
    if "new_height" not in st.session_state:
        st.session_state.new_height = update_height
    if "quality" not in st.session_state:
        st.session_state.quality = update_quality

    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.new_width = st.number_input("New Width (pixels)", value=st.session_state.new_width, min_value=1)
    with col2:
        st.session_state.new_height = st.number_input("New Height (pixels)", value=st.session_state.new_height, min_value=1)
    with col3:
        if uploaded_file.type == "image/jpeg":
            st.session_state.quality = st.slider("Quality (JPEG only)", 1, 100, st.session_state.quality)

    # Live modification and display
    resized_image = image.resize((st.session_state.new_width, st.session_state.new_height))

    # Apply quality (if JPEG)
    if uploaded_file.type == "image/jpeg":
        resized_image = resized_image.convert("RGB")  
        resized_image.save("modified_image.jpg", quality=st.session_state.quality)
        modified_image = Image.open("modified_image.jpg")
    else:
        resized_image.save("modified_image.png")
        modified_image = Image.open("modified_image.png")
        

    st.image(modified_image, caption="Modified Image", use_column_width=True)

    # Download button
    st.download_button(
        label="Download Modified Image",
        data=open("modified_image.jpg", "rb").read() if uploaded_file.type == "image/jpeg" else open("modified_image.png", "rb").read(),
        file_name="modified_image.jpg" if uploaded_file.type == "image/jpeg" else "modified_image.png",
        mime=uploaded_file.type,
    )
