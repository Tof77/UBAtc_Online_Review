from flask import Flask, request, redirect, url_for, render_template, send_from_directory
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

comments_db = {}  # {page: [{x: float, y: float, text: str, type: str, reactions: []}]}

@app.route('/', methods=['GET', 'POST'])
def upload_pdf():
    if request.method == 'POST':
        file = request.files['pdf']
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('view_pdf', filename=filename))
    return '''
    <h1>Uploader un fichier PDF</h1>
    <form method="post" enctype="multipart/form-data">
      <input type="file" name="pdf" accept="application/pdf"><br><br>
      <input type="submit" value="Envoyer">
    </form>
    '''

@app.route('/view/<filename>')
def view_pdf(filename):
    return render_template('viewer.html', filename=filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/add_comment', methods=['POST'])
def add_comment():
    page = int(request.form['page'])
    x = float(request.form['x'])
    y = float(request.form['y'])
    text = request.form['text']
    type_comment = request.form['type']
    
    if page not in comments_db:
        comments_db[page] = []
    comments_db[page].append({
        'x': x,
        'y': y,
        'text': text,
        'type': type_comment,
        'author': 'anonymous',  # Placeholder
        'created_at': '2025-04-26T17:00:00Z',  # Pourra être dynamisé plus tard
        'status': 'open',
        'reactions': []
    })
    return 'OK'

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
