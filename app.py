from flask import Flask, render_template, request, send_file
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/')
def upload_file():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400

    # Save the uploaded file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Process the file (convert to UTF-8, clean empty cells & unnamed columns)
    df = pd.read_csv(file_path, encoding="utf-8-sig")
    df = df.loc[:, ~df.columns.str.contains("Unnamed", case=False)]  # Remove "Unnamed" columns
    df = df.dropna(how='all')  # Remove completely empty rows
    df.iloc[:, 0] = df.iloc[:, 0].astype(str).str.replace(r'\.0$', '', regex=True).str.rstrip('.')  # Clean barcodes

    # Save the cleaned file
    cleaned_file_path = os.path.join(PROCESSED_FOLDER, "cleaned_" + file.filename)
    df.to_csv(cleaned_file_path, index=False, encoding="utf-8")

    # Store the cleaned file name for downloading
    global last_cleaned_file
    last_cleaned_file = cleaned_file_path

    return "File processed successfully", 200

@app.route('/download')
def download_file():
    """Handles file downloads after processing."""
    global last_cleaned_file
    if not os.path.exists(last_cleaned_file):
        return "File not found", 404
    return send_file(last_cleaned_file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
