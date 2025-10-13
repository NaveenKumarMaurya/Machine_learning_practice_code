import re
import json
from datetime import datetime, date
import pdfplumber

from function import process_text_to_json
import streamlit as st

# 🧱 Streamlit UI
st.set_page_config(page_title="PDF to JSON Converter", page_icon="📄")
st.title("📄 CREDIT REPORT PDF → JSON Converter")

st.write("Upload a PDF file, and this app will extract text and return it as JSON.")

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    try:
        # Read the PDF
        with pdfplumber.open(uploaded_file) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        # Convert extracted text to JSON
        data = process_text_to_json(text)

        # Display formatted JSON
        st.subheader("🧾 Extracted JSON")
        st.json(data)

        # Option to download JSON
        json_str = json.dumps(data, indent=2)
        st.download_button("⬇️ Download JSON", json_str, file_name="output.json")

    except Exception as e:
        st.error(f"Error processing file: {e}")
