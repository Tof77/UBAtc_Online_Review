# app.py

from flask import Flask, request, render_template_string, redirect, url_for
from werkzeug.utils import secure_filename
import os
import uuid
from docx import Document

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Simuler une base de commentaires (clé = paragraphe ID, valeur = liste de commentaires)
comments_db = {}
users_db = {}

HTML_TEMPLATE = '''
<!doctype html>
<html>
<head>
  <title>Relecture document</title>
</head>
<body>
  <h1>Document : {{ filename }}</h1>
  <p>Connecté en tant que : <strong>{{ user }}</strong></p>
  <hr>
  {% for idx, para in enumerate(paragraphs) %}
    <div style="margin-bottom: 20px;">
      <p><strong>[{{ idx }}]</strong> {{ para }}</p>
      <form method="post" action="/comment">
        <input type="hidden" name="para_id" value="{{ idx }}">
        <input type="hidden" name="user" value="{{ user }}">
        <textarea name="comment" placeholder="Votre commentaire" rows="2" cols="50"></textarea><br>
        <button type="submit">Commenter</button>
      </form>
      {% if comments.get(idx) %}
        <ul>
        {% for c in comments[idx] %}
          <li><strong>{{ c['user'] }}</strong> : {{ c['text'] }}</li>
        {% endfor %}
        </ul>
      {% endif %}
    </div>
  {% endfor %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        user = request.form['username']
        file = request.files['wordfile']
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        users_db[user] = {'filename': filename}
        return redirect(url_for('review', user=user))
    return '''
    <h1>Envoyer un document Word pour relecture</h1>
    <form method="post" enctype="multipart/form-data">
      Votre nom : <input type="text" name="username"><br><br>
      Fichier Word : <input type="file" name="wordfile"><br><br>
      <input type="submit" value="Envoyer">
    </form>
    '''

@app.route('/review/<user>', methods=['GET'])
def review(user):
    filename = users_db[user]['filename']
    doc = Document(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return render_template_string(HTML_TEMPLATE, filename=filename, paragraphs=paragraphs, user=user, comments=comments_db)

@app.route('/comment', methods=['POST'])
def comment():
    para_id = int(request.form['para_id'])
    text = request.form['comment']
    user = request.form['user']
    if para_id not in comments_db:
        comments_db[para_id] = []
    comments_db[para_id].append({'user': user, 'text': text})
    return redirect(url_for('review', user=user))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000, debug=True)
