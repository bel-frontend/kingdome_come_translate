from flask import Flask, request, render_template, jsonify, redirect, url_for
import xml.etree.ElementTree as ET
import os

app = Flask(__name__)
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

    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Extract the third cell from each row
    rows = [{'id': idx, 'text': cell.text} for idx, cell in enumerate(root.findall(".//Row/Cell[3]"))]
    return render_template('edit.html', rows=rows)

@app.route('/save', methods=['POST'])
def save_file():
    global tree, root, file_path
    if not tree or not root or not file_path:
        return jsonify({"status": "error", "message": "No file loaded"})

    # Update the XML with new values
    for key, value in request.form.items():
        idx = int(key.replace('cell_', ''))
        cell = root.findall(".//Row/Cell[3]")[idx]
        cell.text = value

    # Save the updated XML back to the file
    tree.write(file_path, encoding="utf-8", xml_declaration=True)
    return jsonify({"status": "success", "message": "XML file saved successfully!"})

if __name__ == '__main__':
    app.run(debug=True)
