# CipherNest

### Extract Smart. Expose Less.

CipherNest is a privacy-first document parsing engine designed to extract only the information required for a specific verification purpose.

## Problem

Sensitive documents often contain more personal information than a verification task actually requires. Extracting and displaying everything can increase unnecessary data exposure.

## Solution

CipherNest follows a purpose-based minimum-data extraction approach:

Document → Purpose Selection → Local OCR → Required Field Extraction → Privacy-Focused Result

## Key Features

- Purpose-based document processing
- Local OCR using Tesseract
- Required-field extraction
- Privacy-focused result display
- Age verification
- Identity verification
- Address verification
- Offline-first document processing

## Technology Stack

- Python
- Flask
- HTML/CSS
- Tesseract OCR
- PyTesseract
- Pillow

## Current Status

Working prototype with:

- Document upload
- Verification purpose selection
- Local OCR
- Age-based DOB and age extraction
- Identity/name extraction
- Address extraction
- Purpose-relevant result display

## Future Scope

- Better document classification
- Sensitive-data masking
- Temporary file cleanup
- Support for additional document formats
- More robust extraction for different document layouts