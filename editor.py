from flask import Flask, request, render_template, jsonify, redirect, url_for, send_file, send_from_directory, abort
import xml.etree.ElementTree as ET
import os
import sys
from zipfile import ZipFile, ZIP_DEFLATED
from index import translate_text
import shutil
from dotenv import load_dotenv

app = Flask(__name__, template_folder='templates', static_folder='static')

UPLOAD_FOLDER = 'uploads/extracted'
ALLOWED_EXTENSIONS = {'xml'}
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB

# Initialize variables
tree = None
root = None
file_path = None
pak_file_path = None
extracted_dir = "extracted_files"
open_ai_key = None
api_token = os.getenv("OPENAI_API_KEY")


load_dotenv()

def delete_folders_and_files():
    paths_to_delete = [
        './uploads',
        # 'path/to/folder2',
        # 'path/to/file1.txt',
        # 'path/to/file2.log'
    ]
    print('Delete files')
    for path in paths_to_delete:
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
                print(f"Directory {path} removed successfully")
            elif os.path.isfile(path):
                os.remove(path)
                print(f"File {path} removed successfully")
            else:
                print(f"{path} does not exist")
        except Exception as e:
            print(f"Error removing {path}: {e}")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def initialize_variables():
    global tree, root, file_path, pak_file_path, extracted_dir
    extracted_dir = resource_path(os.path.join('uploads', 'extracted'))
    
    # Check if extracted directory exists and contains files
    if os.path.exists(extracted_dir):
        # Check if XML file exists
        xml_files = [f for f in os.listdir(extracted_dir) if f.endswith('.xml')]
        if xml_files:
            file_path = os.path.join(extracted_dir, xml_files[0])
            tree = ET.parse(file_path)
            root = tree.getroot()
        else:
            file_path = None

        # Check if PAK file exists
        uploads_dir = resource_path('uploads')
        pak_files = [f for f in os.listdir(uploads_dir) if f.endswith('.pak')]
        if pak_files:
            pak_file_path = os.path.join(uploads_dir, pak_files[0])
        else:
            pak_file_path = None
    else:
        file_path = None
        pak_file_path = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/load-ai-key', methods=['POST'])
def load_ai_key():
    global open_ai_key
    updates = request.get_json()
    text = updates.get('text')
    open_ai_key = text
    print(open_ai_key)
    return jsonify({"status": "success", "message": "OpenAI API key loaded successfully!"})

# get suggestions from OpenAI
@app.route('/get-suggestions', methods=['POST'])
def get_suggestions():
    updates = request.get_json()
    text = updates.get('text')
    if open_ai_key or api_token:
        return jsonify({ "suggestion": translate_text(text, open_ai_key or api_token) })
    else:
        return jsonify({"status": "error", "message": "OpenAI API key not loaded"})

@app.route('/load-pak', methods=['POST'])
def load_pak_file():
    global pak_file_path, extracted_dir
    delete_folders_and_files()

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
    tree.write(file_path, encoding="utf-8", xml_declaration=None)
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

    # Create a new PAK file and add the extracted contents and the new XML file
    new_pak_file_path = resource_path(os.path.join('uploads', os.path.basename(pak_file_path)))
    temp_dir = resource_path(os.path.join('uploads', 'extracted'))
    print(pak_file_path, new_pak_file_path, temp_dir)
    with ZipFile(new_pak_file_path, 'w', ZIP_DEFLATED) as pak:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_full_path = os.path.join(root, file)
                print(file_full_path)
                arcname = os.path.relpath(file_full_path, temp_dir)
                pak.write(file_full_path, arcname)
        pak.write(file_path, os.path.basename(file_path))

    # Update global pak_file_path to the new PAK file path
    pak_file_path = new_pak_file_path

    return jsonify({"status": "success", "message": "Files packed successfully!", "download_url": url_for('download_pak', filename=os.path.basename(pak_file_path))})

@app.route('/download-pak')
def download_pak():
    global pak_file_path
    if not pak_file_path or not os.path.exists(pak_file_path):
        return jsonify({"status": "error", "message": "PAK file not found"})
    return send_file(pak_file_path, as_attachment=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        filename = file.filename
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return 'File uploaded successfully', 200
    else:
        return 'Invalid file type', 400

@app.route('/download/<filename>', methods=['GET'])
def download_xml(filename):
    print(filename)
    if allowed_file(filename):
        if os.path.exists(os.path.join(UPLOAD_FOLDER, filename)):
            return send_from_directory(UPLOAD_FOLDER, filename)
        else:
            abort(404)
    else:
        return 'Invalid file type', 400
    
@app.route('/files', methods=['GET'])
def list_xml_files():
    files = os.listdir(UPLOAD_FOLDER)
    print(files)
    xml_files = [file for file in files if file.endswith('.xml')]
    return jsonify(xml_files)

if __name__ == '__main__':
    # initialize_variables()
    app.run(host='0.0.0.0',debug=True)
