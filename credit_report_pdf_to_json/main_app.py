import re
import json
from datetime import datetime, date
import pdfplumber
import requests
from function import process_text_to_json
import streamlit as st
import io

# 🧱 Streamlit UI
st.set_page_config(page_title="PDF to JSON Converter", page_icon="📄")
st.title("📄 CREDIT REPORT PDF → JSON Converter")

st.write("Upload a PDF file, and this app will extract text and return it as JSON.")

# Input box for URL
url = st.text_input("Enter a URL:", placeholder="https://api.aurumkuberx.com/api/s3/getImage?url=cibil_reports/cibil_report_ASIPV8810F_1760002364126.pdf")
# Button to fetch content
if st.button("Fetch Content"):
    if url:
        try:
            
            # Step 1: Download the PDF file in memory
            
            response = requests.get(url)
            response.raise_for_status()  # ensure the request was successful

            # Step 2: Open it with pdfplumber from bytes buffer
            with pdfplumber.open(io.BytesIO(response.content)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() 


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