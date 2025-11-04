import re
import json
from datetime import datetime, date
import pdfplumber
import requests
from flask import Flask, request, jsonify
# from function2 import process_text_to_json
from function import process_text_to_json
import io
import flask


from flask_cors import CORS
app = flask.Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the PDF to JSON API!"
@app.route('/upload_url', methods=['POST'])
def convert_pdf_to_json():
    data = request.get_json()
    
    if not data:
        return "No url in the input", 400
    
    

    
    if data:
        try:
            
            # Step 1: Download the PDF file in memory
            pdf_url=data["pdf_url"]
            response = requests.get(pdf_url)
            response.raise_for_status()  # ensure the request was successful

            # Step 2: Open it with pdfplumber from bytes buffer
            with pdfplumber.open(io.BytesIO(response.content)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text()  
            # Process the text to extract structured data
            data = process_text_to_json(text)
            return  flask.jsonify(data)
        except Exception as e:
            return str(e), 500
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=4008,debug=True)