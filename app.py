from flask import Flask, request, render_template, send_file
import pandas as pd
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/')
def upload_file():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    
    # Process the file
    df = pd.read_csv(filepath, encoding="utf-8-sig")
    df = df.dropna(how='all')  # Remove empty rows
    df = df.loc[:, ~df.columns.str.contains("Unnamed", case=False)]  # Remove unnamed columns
    df = df.iloc[:, [0]]  # Keep only first column (barcode column)
    df.iloc[:, 0] = df.iloc[:, 0].astype(str).str.replace(r'\.0$', '', regex=True).str.rstrip('.')  # Remove decimals
    
    processed_filename = "cleaned_" + file.filename
    processed_filepath = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
    df.to_csv(processed_filepath, index=False, encoding="utf-8")
    
    return send_file(processed_filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
