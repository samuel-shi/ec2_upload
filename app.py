import os
from flask import Flask, request, render_template, send_from_directory, jsonify, redirect, url_for

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/api/browse')
def api_browse():
    # Set the root for browsing to /home for Linux, or user's home for other OS
    root = '/home' if os.name != 'nt' else os.path.expanduser('~')
    
    path = request.args.get('path', '')
    current_path = os.path.join(root, path)

    # Security check to prevent directory traversal attacks
    if not os.path.abspath(current_path).startswith(os.path.abspath(root)):
        return jsonify({"error": "Invalid path"}), 400

    dirs = []
    files = []
    try:
        if os.path.isdir(current_path):
            for item in os.listdir(current_path):
                if os.path.isdir(os.path.join(current_path, item)):
                    dirs.append(item)
                else:
                    files.append(item)
    except FileNotFoundError:
        return jsonify({"error": "Directory not found"}), 404
    
    dirs.sort()
    files.sort()
    
    # The parent path is the relative path from the root
    parent_path = os.path.relpath(os.path.dirname(current_path), root) if path and os.path.abspath(current_path) != os.path.abspath(root) else ''

    return jsonify({
        "path": path,
        "dirs": dirs,
        "files": files,
        "parent_path": parent_path,
        "current_path": current_path
    })

@app.route('/api/create_folder', methods=['POST'])
def api_create_folder():
    root = '/home' if os.name != 'nt' else os.path.expanduser('~')
    path = request.form.get('path', '')
    folder_name = request.form.get('folder_name')
    
    if not folder_name or '/' in folder_name or '..' in folder_name:
        return jsonify({"error": "Invalid folder name"}), 400

    current_path = os.path.join(root, path)
    
    # Security check
    if not os.path.abspath(current_path).startswith(os.path.abspath(root)):
        return jsonify({"error": "Invalid path"}), 400

    try:
        os.makedirs(os.path.join(current_path, folder_name))
    except FileExistsError:
        return jsonify({"error": "Folder already exists"}), 400
    except Exception as e:
        return jsonify({"error": f"Error creating folder: {e}"}), 500

    return jsonify({"success": True})


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            path = request.form.get('path', UPLOAD_FOLDER)
            if not os.path.exists(path):
                os.makedirs(path)
            filename = file.filename
            file.save(os.path.join(path, filename))
            return 'File uploaded successfully to: ' + os.path.join(path, filename)
    return render_template('index.html')

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=8088)
