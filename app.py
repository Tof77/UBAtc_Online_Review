from flask import Flask, request, render_template, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Assure que le dossier uploads existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Chargement des commentaires depuis JSON
def load_comments(filename):
    comments_file = os.path.join(UPLOAD_FOLDER, f"{filename}-comments.json")
    if os.path.exists(comments_file):
        with open(comments_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Sauvegarde des commentaires dans JSON
def save_comments(filename, comments):
    comments_file = os.path.join(UPLOAD_FOLDER, f"{filename}-comments.json")
    with open(comments_file, 'w', encoding='utf-8') as f:
        json.dump(comments, f, indent=2)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part", 400
        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('review', filename=filename))
    return '''
    <!doctype html>
    <title>Uploader un PDF</title>
    <h1>Uploader un document PDF</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file accept="application/pdf">
      <input type=submit value=Uploader>
    </form>
    '''

@app.route('/review/<filename>')
def review(filename):
    return render_template('viewer.html', filename=filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/get_comments/<filename>')
def get_comments(filename):
    comments = load_comments(filename)
    return jsonify(comments)

@app.route('/save_comment/<filename>', methods=['POST'])
def save_comment(filename):
    page = int(request.form.get('page'))
    x = float(request.form.get('x'))
    y = float(request.form.get('y'))
    text = request.form.get('text')
    author = request.form.get('author', 'Anonymous')
    initials = request.form.get('initials', 'AA')
    status = request.form.get('status', 'open')
    createdAt = request.form.get('createdAt')

    comments = load_comments(filename)

    if str(page) not in comments:
        comments[str(page)] = []

    comments[str(page)].append({
        'text': text,
        'x': x,
        'y': y,
        'author': author,
        'initials': initials,
        'status': status,
        'createdAt': createdAt,
        'replies': []
    })

    save_comments(filename, comments)
    return 'OK', 200

# Route pour mettre à jour un commentaire
@app.route('/update_comment/<filename>', methods=['POST'])
def update_comment(filename):
    page = request.form.get('page')
    index = int(request.form.get('index'))
    text = request.form.get('text')

    comments = load_comments(filename)
    comments[page][index]['text'] = text

    save_comments(filename, comments)
    return 'OK', 200

# Route pour résoudre ou réouvrir un commentaire
@app.route('/toggle_resolve/<filename>', methods=['POST'])
def toggle_resolve(filename):
    page = request.form.get('page')
    index = int(request.form.get('index'))
    new_status = request.form.get('status')

    comments = load_comments(filename)
    comments[page][index]['status'] = new_status

    save_comments(filename, comments)
    return 'OK', 200

# Route pour supprimer un commentaire
@app.route('/delete_comment/<filename>', methods=['POST'])
def delete_comment(filename):
    page = request.form.get('page')
    index = int(request.form.get('index'))

    comments = load_comments(filename)
    comments[page].pop(index)

    save_comments(filename, comments)
    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=True)
