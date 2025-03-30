from functools import wraps
import sqlite3
from flask import Flask
from flask import abort, make_response, redirect, render_template, request, session
import config
import db
import images
import posts
import users

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
    posts_list = posts.get_list()
    return render_template('index.html', posts=posts_list)

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

    if not users.create(username, password1):
        return 'Virhe: Tunnus on jo varattu'

    return 'Tunnuksen luominen onnistui'

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/log-user-in', methods=['POST'])
def log_user_in():
    username = request.form['username']
    password = request.form['password']

    user_id = users.login(username, password)
    if user_id:
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

        posts.add(title, image, file_format, description, user_id)
        return 'Kuvan lähettäminen onnistui'

@app.route('/image/<int:image_id>')
def show_image(image_id):
    result = images.get(image_id)
    if not result:
        abort(404)
    image, file_format = result

    response = make_response(bytes(image))
    response.headers.set('Content-Type', 'image/'+file_format)
    return response

@app.route('/post/<int:post_id>')
def show_post(post_id):
    post = posts.get(post_id)
    if not post:
        abort(404)
    return render_template('post.html', post=post)

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@require_login
def edit_post(post_id):
    post = posts.get(post_id)
    if not post:
        abort(404)
    if session['user_id'] != post['user_id']:
        abort(403)

    if request.method == 'GET':
        return render_template('edit.html', post=post)

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        if not title or len(title) > 100 or len(description) > 2000:
            abort(403)

        posts.edit(post_id, title, description)
        return redirect('/post/' + str(post_id))

@app.route('/remove/<int:post_id>', methods=['GET', 'POST'])
@require_login
def remove_post(post_id):
    user_id = posts.get_user(post_id)
    if not user_id:
        abort(404)
    if session['user_id'] != user_id:
        abort(403)

    if request.method == 'GET':
        return render_template('remove.html', post_id=post_id)

    if request.method == 'POST':
        if 'continue' in request.form:
            posts.remove(post_id)
            return redirect('/')
        else:
            return redirect('/post/' + str(post_id))

@app.route('/search')
def search():
    query = request.args.get('query')
    if query:
        results = posts.search(query)
    else:
        results = []
    return render_template('search.html', query=query, results=results)

@app.teardown_appcontext
def teardown_appcontext(exception):
    db.close_connection()