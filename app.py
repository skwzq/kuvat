from functools import wraps
import sqlite3
from flask import Flask
from flask import abort, make_response, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import config
import db

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            abort(403)
        return f(*args, **kwargs)
    return wrapper

@app.route('/')
def index():
    sql = """SELECT p.id, p.title, p.image_id, p.sent_at, u.username
             FROM posts p, users u
             WHERE u.id = p.user_id
             ORDER BY p.id DESC"""
    posts = db.query(sql)
    return render_template('index.html', posts=posts)

@app.route('/registration')
def registration():
    return render_template('registration.html')

@app.route('/create-user', methods=['POST'])
def create_user():
    username = request.form['username']
    if not username or len(username) > 20:
        abort(403)

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
        return redirect('/')
    else:
        return 'Virhe: Väärä käyttäjätunnus tai salasana'

@app.route('/logout')
def logout():
    if 'user_id' in session:
        del session['user_id']
    return redirect('/')

@app.route('/new-image', methods=['GET', 'POST'])
@require_login
def new_image():
    if request.method == 'GET':
        return render_template('new_image.html')

    if request.method == 'POST':
        file = request.files['image']
        if not file:
            abort(403)

        if file.filename.endswith('.jpg'):
            file_format = 'jpeg'
        elif file.filename.endswith('.png'):
            file_format = 'png'
        else:
            return 'Virhe: Väärä tiedostomuoto'

        image = file.read()
        if len(image) > 1024**2:
            return 'Virhe: Liian suuri tiedosto'

        title = request.form['title']
        description = request.form['description']
        if not title or len(title) > 100 or len(description) > 2000:
            abort(403)

        user_id = session['user_id']

        sql = 'INSERT INTO images (data, format) VALUES (?, ?)'
        db.execute(sql, [image, file_format])

        sql = """INSERT INTO posts (title, image_id, description, sent_at, user_id)
                 VALUES (?, ?, ?, datetime('now'), ?)"""
        db.execute(sql, [title, db.last_insert_id(), description, user_id])

        return 'Kuvan lähettäminen onnistui'

@app.route('/image/<int:image_id>')
def show_image(image_id):
    sql = 'SELECT data, format FROM images WHERE id = ?'
    result = db.query(sql, [image_id])
    if not result:
        abort(404)
    image, file_format = result[0]

    response = make_response(bytes(image))
    response.headers.set('Content-Type', 'image/'+file_format)
    return response

@app.route('/post/<int:post_id>')
def show_post(post_id):
    sql = """SELECT p.id, p.title, p.image_id, p.description, p.sent_at, u.username, p.user_id
             FROM posts p, users u
             WHERE p.id = ? AND u.id = p.user_id"""
    result = db.query(sql, [post_id])
    if not result:
        abort(404)
    return render_template('post.html', post=result[0])

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@require_login
def edit_post(post_id):
    sql = 'SELECT id, title, description, user_id FROM posts WHERE id = ?'
    result = db.query(sql, [post_id])
    if not result:
        abort(404)
    post = result[0]
    if session['user_id'] != post['user_id']:
        abort(403)

    if request.method == 'GET':
        return render_template('edit.html', post=post)

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        if not title or len(title) > 100 or len(description) > 2000:
            abort(403)

        sql = 'UPDATE posts SET title = ?, description = ? WHERE id = ?'
        db.execute(sql, [title, description, post_id])
        return redirect('/post/' + str(post_id))

@app.route('/remove/<int:post_id>', methods=['GET', 'POST'])
@require_login
def remove_post(post_id):
    sql = 'SELECT id, image_id, user_id FROM posts WHERE id = ?'
    result = db.query(sql, [post_id])
    if not result:
        abort(404)
    post = result[0]
    if session['user_id'] != post['user_id']:
        abort(403)

    if request.method == 'GET':
        return render_template('remove.html', post=post)

    if request.method == 'POST':
        if 'continue' in request.form:
            sql = 'DELETE FROM posts WHERE id = ?'
            db.execute(sql, [post_id])
            sql = 'DELETE FROM images WHERE id = ?'
            db.execute(sql, [post['image_id']])
            return redirect('/')
        else:
            return redirect('/post/' + str(post_id))

@app.route('/search')
def search():
    query = request.args.get('query')
    sql = """SELECT p.id, p.title, p.image_id, p.sent_at, u.username
             FROM posts p, users u
             WHERE u.id = p.user_id
             AND (p.title LIKE ? OR p.description LIKE ?)
             ORDER BY p.id DESC"""
    if query:
        results = db.query(sql, ['%' + query + '%'] * 2)
    else:
        results = []
    return render_template('search.html', query=query, results=results)

@app.teardown_appcontext
def teardown_appcontext(exception):
    db.close_connection()