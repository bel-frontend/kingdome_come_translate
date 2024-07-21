from flask import Flask, request, render_template, jsonify, redirect, url_for, send_file
import xml.etree.ElementTree as ET
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 
tree = None
root = None
file_path = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/load', methods=['POST'])
def load_file():
    global tree, root, file_path
    file = request.files['file']
    if not file:
        return redirect(url_for('index'))

    # Save the file to the 'uploads' directory
    file_path = os.path.join('uploads', file.filename)
    os.makedirs('uploads', exist_ok=True)
    file.save(file_path)

    print(f"File saved to: {file_path}")  # Debugging statement

    tree = ET.parse(file_path)
    root = tree.getroot()

    # Extract and trim the second and third cell from each row
    rows = [
        {'id': idx, 'text': (cell[2].text or '').strip(), 'context': (cell[1].text or '').strip()}
        for idx, cell in enumerate(root.findall(".//Row"))
    ]
    return render_template('edit.html', rows=rows, file_path=file_path)

@app.route('/save', methods=['POST'])
def save_file():
    global tree, root, file_path
    if not tree or not root or not file_path:
        return jsonify({"status": "error", "message": "No file loaded"})

    # Update the XML with new values
    for key, value in request.form.items():
        idx = int(key.replace('cell_', ''))
        cell = root.findall(".//Row/Cell[3]")[idx]
        cell.text = value.strip()

    # Save the updated XML back to the file
    tree.write(file_path, encoding="utf-8", xml_declaration=True)
    return jsonify({"status": "success", "message": "XML file saved successfully!","download_url": url_for('download_file')})

@app.route('/download')
def download_file():
    global file_path
    if not file_path or not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "File not found"})
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
