import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import config
import db

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registration')
def registration():
    return render_template('registration.html')

@app.route('/create-user', methods=['POST'])
def create_user():
    username = request.form['username']
    password1 = request.form['password1']
    password2 = request.form['password2']
    
    if password1 != password2:
        return 'Virhe: Salasanat eivät ole samat'
    password_hash = generate_password_hash(password1)

    sql = 'INSERT INTO users (username, password_hash) VALUES (?, ?)'
    try:
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return 'Virhe: Tunnus on jo varattu'

    return 'Tunnuksen luominen onnistui'

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/log-user-in', methods=['POST'])
def log_user_in():
    username = request.form['username']
    password = request.form['password']

    sql = 'SELECT id, password_hash FROM users WHERE username = ?'
    user_id, password_hash = db.query(sql, [username])[0]

    if check_password_hash(password_hash, password):
        session['user_id'] = user_id
        session['username'] = username
        return redirect('/')
    else:
        return 'Virhe: Väärä käyttäjätunnus tai salasana'

@app.route('/logout')
def logout():
    del session['user_id']
    del session['username']
    return redirect('/')

@app.route('/new-image', methods=['GET', 'POST'])
def new_image():
    if request.method == 'GET':
        return render_template('new_image.html')

    if request.method == 'POST':
        file = request.files['image']
        if not file.filename.endswith(('.jpg', '.png')):
            return 'Virhe: Väärä tiedostomuoto'

        image = file.read()
        title = request.form['title']
        description = request.form['description']
        user_id = session['user_id']

        sql = 'INSERT INTO images (data) VALUES (?)'
        db.execute(sql, [image])

        sql = """INSERT INTO posts (title, image_id, description, sent_at, user_id)
                 VALUES (?, ?, ?, datetime('now'), ?)"""
        db.execute(sql, [title, db.last_insert_id(), description, user_id])

        return 'Kuvan lähettäminen onnistui'

@app.teardown_appcontext
def teardown_appcontext(exception):
    db.close_connection()