from flask import Flask, request, render_template, jsonify, redirect, url_for, send_file
import xml.etree.ElementTree as ET
import os
import sys
from zipfile import ZipFile, ZIP_DEFLATED

app = Flask(__name__, template_folder='templates', static_folder='static')

app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB
tree = None
root = None
file_path = None
pak_file_path = None
extracted_dir = "extracted_files"

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/load-pak', methods=['POST'])
def load_pak_file():
    global pak_file_path, extracted_dir
    file = request.files['file']
    if not file:
        return redirect(url_for('index'))

    # Save the file to the 'uploads' directory
    pak_file_path = resource_path(os.path.join('uploads', file.filename))
    os.makedirs(os.path.dirname(pak_file_path), exist_ok=True)
    file.save(pak_file_path)

    # Extract PAK file contents
    extracted_dir = resource_path(os.path.join('uploads', 'extracted'))
    os.makedirs(extracted_dir, exist_ok=True)
    with ZipFile(pak_file_path, 'r') as pak:
        pak.extractall(extracted_dir)

    # List XML files
    xml_files = [f for f in os.listdir(extracted_dir) if f.endswith('.xml')]
    return render_template('select_xml.html', xml_files=xml_files)

@app.route('/select-xml', methods=['POST'])
def select_xml():
    global tree, root, file_path, extracted_dir
    file_name = request.form.get('file_name')
    if not file_name:
        return redirect(url_for('index'))

    file_path = os.path.join(extracted_dir, file_name)

    tree = ET.parse(file_path)
    root = tree.getroot()

    rows = []
    for idx, row in enumerate(root.findall(".//Row")):
        cells = row.findall("Cell")
        if len(cells) > 2:
            rows.append({
                'id': idx,
                'text': (cells[2].text or '').strip(),
                'context': (cells[1].text or '').strip()
            })

    return render_template('edit.html', rows=rows, file_path=file_path)

@app.route('/edit')
def edit_form():
    global tree, root, file_path
    if not tree or not root or not file_path:
        return redirect(url_for('index'))

    rows = []
    for idx, row in enumerate(root.findall(".//Row")):
        cells = row.findall("Cell")
        if len(cells) > 2:
            rows.append({
                'id': idx,
                'text': (cells[2].text or '').strip(),
                'context': (cells[1].text or '').strip()
            })

    return render_template('edit.html', rows=rows, file_path=file_path)


@app.route('/save', methods=['POST'])
def save_file():
    global tree, root, file_path
    if not tree or not root or not file_path:
        return jsonify({"status": "error", "message": "No file loaded"})

    # Update the XML with new values
    updates = request.get_json()
    cells = root.findall(".//Row")

    for key, value in updates.items():
        if key == 'file_path':
            continue
        idx = int(key.replace('cell_', ''))
        if len(cells) > idx:
            cell = cells[idx].findall("Cell")
            if len(cell) > 2:
                cell[2].text = value.strip()

    # Save the updated XML back to the file
    tree.write(file_path, encoding="utf-8", xml_declaration=True)
    return jsonify({"status": "success", "message": "XML file saved successfully!"})


@app.route('/download')
def download_file():
    global file_path
    if not file_path or not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "File not found"})
    return send_file(file_path, as_attachment=True)

@app.route('/pack', methods=['POST'])
def pack_files():
    global file_path, pak_file_path
    if not file_path or not pak_file_path:
        return jsonify({"status": "error", "message": "Files not loaded"})

    # Create a temporary directory to extract current PAK contents
    temp_dir = resource_path('temp')
    os.makedirs(temp_dir, exist_ok=True)
    with ZipFile(pak_file_path, 'r') as pak:
        pak.extractall(temp_dir)

    # Replace or add the XML file
    with ZipFile(pak_file_path, 'w', ZIP_DEFLATED) as pak:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_full_path = os.path.join(root, file)
                arcname = os.path.relpath(file_full_path, temp_dir)
                pak.write(file_full_path, arcname)
        pak.write(file_path, os.path.basename(file_path))

    # Clean up temporary directory
    for root, dirs, files in os.walk(temp_dir, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))
    os.rmdir(temp_dir)

    return jsonify({"status": "success", "message": "Files packed successfully!", "download_url": url_for('download_pak')})

@app.route('/download-pak')
def download_pak():
    global pak_file_path
    if not pak_file_path or not os.path.exists(pak_file_path):
        return jsonify({"status": "error", "message": "PAK file not found"})
    return send_file(pak_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
