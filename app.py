from flask import Flask, render_template, request, session
import os
import re
from datetime import date, datetime

import pytesseract
from PIL import Image


app = Flask(__name__)

app.secret_key = "ciphernest-secret-key"

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


def extract_required_data(text, purpose, custom_fields=None):

    # ---------------- AGE ----------------

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

            return (
                f"DOB: {match.group(1)}\n"
                f"Age: {age}"
            )

        return "DOB not found."


    # ---------------- IDENTITY ----------------

    elif purpose == "identity":

        match = re.search(
            r"Name\s*[:\-]\s*(.+)",
            text,
            re.IGNORECASE
        )

        if match:

            return f"Name: {match.group(1).strip()}"

        return "Required identity information not found."


    # ---------------- ADDRESS ----------------

    elif purpose == "address":

        match = re.search(
            r"Address\s*[:\-]\s*(.+)",
            text,
            re.IGNORECASE
        )

        if match:

            return f"Address: {match.group(1).strip()}"

        return "Address not found."


    # ---------------- CUSTOM ----------------

    elif purpose == "custom":

        if not custom_fields:

            return "Please select at least one custom field."


        results = []


        # NAME

        if "name" in custom_fields:

            match = re.search(
                r"Name\s*[:\-]\s*(.+)",
                text,
                re.IGNORECASE
            )

            if match:

                results.append(
                    f"Name: {match.group(1).strip()}"
                )


        # DOB

        if "dob" in custom_fields:

            match = re.search(
                r"DOB\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})",
                text,
                re.IGNORECASE
            )

            if match:

                results.append(
                    f"DOB: {match.group(1)}"
                )


        # ADDRESS

        if "address" in custom_fields:

            match = re.search(
                r"Address\s*[:\-]\s*(.+)",
                text,
                re.IGNORECASE
            )

            if match:

                results.append(
                    f"Address: {match.group(1).strip()}"
                )


        if results:

            return "\n".join(results)


        return "Selected information not found."


    return "Please select a valid purpose."


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_document():

    document = request.files.get("document")


    if not document or document.filename == "":
        return "Please upload a document."


    filename = document.filename

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )


    document.save(file_path)


    session["file_path"] = file_path
    session["file_name"] = filename


    return render_template(
        "purpose.html",
        filename=filename
    )


@app.route("/process", methods=["POST"])
def process_document():

    purpose = request.form.get("purpose")

    custom_fields = request.form.getlist(
        "custom_fields"
    )

    file_path = session.get("file_path")


    if not purpose:

        return "Please select a verification purpose."


    if purpose == "custom" and not custom_fields:

        return "Please select at least one custom field."


    if not file_path or not os.path.exists(file_path):

        return "Document not found. Please upload again."


    try:

        image = Image.open(file_path)

        extracted_text = pytesseract.image_to_string(
            image
        )


        required_data = extract_required_data(
            extracted_text,
            purpose,
            custom_fields
        )


        session["purpose"] = purpose

        session["required_data"] = required_data

        session["custom_fields"] = custom_fields


        os.remove(file_path)

        session.pop("file_path", None)


    except Exception as e:

        return f"OCR Error: {e}"


    return render_template(
        "processing.html",
        purpose=purpose,
        required_data=required_data
    )


@app.route("/result", methods=["POST"])
def show_result():

    purpose = request.form.get("purpose")

    required_data = request.form.get(
        "required_data"
    )


    return render_template(
        "result.html",
        purpose=purpose,
        required_data=required_data
    )


if __name__ == "__main__":

    app.run(debug=True)