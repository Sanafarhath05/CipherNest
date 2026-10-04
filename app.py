from flask import Flask, render_template, request
import os
import re
from datetime import date, datetime

import pytesseract
from PIL import Image

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def calculate_age(dob):
    today = date.today()

    return (
        today.year
        - dob.year
        - ((today.month, today.day) < (dob.month, dob.day))
    )


def extract_required_data(text, purpose):

    if purpose == "age":
        match = re.search(
            r"DOB\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})",
            text,
            re.IGNORECASE
        )

        if match:
            dob = datetime.strptime(
                match.group(1),
                "%d/%m/%Y"
            ).date()

            age = calculate_age(dob)

            return f"DOB: {match.group(1)}\nAge: {age}"

        return "DOB not found."

    elif purpose == "identity":
        match = re.search(
            r"Name\s*[:\-]\s*(.+)",
            text,
            re.IGNORECASE
        )

        if match:
            return f"Name: {match.group(1).strip()}"

        return "Required identity information not found."

    elif purpose == "address":
        match = re.search(
            r"Address\s*[:\-]\s*(.+)",
            text,
            re.IGNORECASE
        )

        if match:
            return f"Address: {match.group(1).strip()}"

        return "Address not found."

    return "Please select a valid purpose."


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process_document():

    document = request.files.get("document")
    purpose = request.form.get("purpose")

    if not document:
        return "Please upload a document."

    if not purpose:
        return "Please select a verification purpose."

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        document.filename
    )

    document.save(file_path)

    try:
        image = Image.open(file_path)

        extracted_text = pytesseract.image_to_string(image)

        required_data = extract_required_data(
            extracted_text,
            purpose
        )

    except Exception as e:
        return f"OCR Error: {e}"

    return f"""
    <h1>CipherNest</h1>

    <h2>Privacy-First Result</h2>

    <p><b>Purpose:</b> {purpose}</p>

    <h3>Required Information</h3>

    <pre>{required_data}</pre>

    <p>Only purpose-relevant information is displayed.</p>
    """


if __name__ == "__main__":
    app.run(debug=True)