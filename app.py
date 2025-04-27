from functools import wraps
import secrets
from flask import Flask
from flask import abort, flash, make_response, redirect, render_template, request, session
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

def check_csrf():
    if request.form['csrf_token'] != session['csrf_token']:
        abort(403)

@app.route('/')
def index():
    posts_list = posts.get_list()
    return render_template('index.html', posts=posts_list)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    if request.method == 'POST':
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']
        if not username or len(username) > 20 or not password1:
            abort(403)

        if password1 != password2:
            flash('Virhe: Salasanat eivät ole samat')
            return render_template('register.html', username=username)

        if not users.create(username, password1):
            flash('Virhe: Tunnus on jo varattu')
            return render_template('register.html', username=username)

        flash('Tunnuksen luominen onnistui')
        return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', next_page=request.referrer)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        next_page = request.form['next_page']

        user_id = users.login(username, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            session['csrf_token'] = secrets.token_hex(16)
            return redirect(next_page)
        else:
            flash('Virhe: Väärä käyttäjätunnus tai salasana')
            return render_template('login.html', username=username, next_page=next_page)

@app.route('/logout')
def logout():
    if 'user_id' in session:
        del session['user_id']
        del session['username']
        del session['csrf_token']
    return redirect('/')

@app.route('/new-post', methods=['GET', 'POST'])
@require_login
def new_post():
    if request.method == 'GET':
        return render_template('new_post.html')

    if request.method == 'POST':
        check_csrf()

        title = request.form['title']
        description = request.form['description']
        tags = request.form['tags']
        if not title or len(title) > 100 or len(description) > 2000 or len(tags) > 500:
            abort(403)

        file = request.files['image']
        if not file:
            abort(403)

        if file.filename.endswith('.jpg'):
            file_format = 'jpeg'
        elif file.filename.endswith('.png'):
            file_format = 'png'
        else:
            flash('Virhe: Väärä tiedostomuoto')
            return render_template('new_post.html', title=title,
                                   description=description, tags=tags)

        image = file.read()
        if len(image) > 1024**2:
            flash('Virhe: Liian suuri tiedosto')
            return render_template('new_post.html', title=title,
                                   description=description, tags=tags)

        user_id = session['user_id']

        post_id = posts.add(title, image, file_format, description, tags, user_id)
        return redirect('/post/' + str(post_id))

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
    comments = posts.get_comments(post_id)
    tags = posts.get_tags(post_id)
    return render_template('post.html', post=post, comments=comments, tags=tags)

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@require_login
def edit_post(post_id):
    post = posts.get(post_id)
    if not post:
        abort(404)
    if session['user_id'] != post['user_id']:
        abort(403)

    if request.method == 'GET':
        tags = posts.get_tags(post_id)
        return render_template('edit.html', post=post, tags=tags)

    if request.method == 'POST':
        check_csrf()

        title = request.form['title']
        description = request.form['description']
        tags = request.form['tags']
        if not title or len(title) > 100 or len(description) > 2000 or len(tags) > 500:
            abort(403)

        posts.edit(post_id, title, description, tags)
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
        check_csrf()

        if 'continue' in request.form:
            posts.remove(post_id)
            return redirect('/')
        else:
            return redirect('/post/' + str(post_id))

@app.route('/search')
def search():
    query = request.args.get('query')
    tag_only = request.args.get('tag_only')
    if query:
        results = posts.search(query, tag_only)
    else:
        results = []
    return render_template('search.html', query=query, tag_only=tag_only,
                           results=results)

@app.route('/new-comment', methods=['POST'])
@require_login
def new_comment():
    check_csrf()

    content = request.form['content']
    if len(content) > 2000:
        abort(403)

    user_id = session['user_id']
    post_id = request.form['post_id']

    posts.add_comment(content, user_id, post_id)
    return redirect('/post/' + str(post_id))

@app.route('/edit/comment<int:comment_id>', methods=['GET', 'POST'])
@require_login
def edit_comment(comment_id):
    comment = posts.get_comment(comment_id)
    if not comment:
        abort(404)
    if session['user_id'] != comment['user_id']:
        abort(403)

    if request.method == 'GET':
        return render_template('edit.html', comment=comment)

    if request.method == 'POST':
        check_csrf()

        content = request.form['content']
        if len(content) > 2000:
            abort(403)

        posts.edit_comment(comment_id, content)
        return redirect('/post/' + str(comment['post_id']))

@app.route('/remove/comment<int:comment_id>', methods=['GET', 'POST'])
@require_login
def remove_comment(comment_id):
    comment = posts.get_comment(comment_id)
    if not comment:
        abort(404)
    if session['user_id'] != comment['user_id']:
        abort(403)

    if request.method == 'GET':
        return render_template('remove.html', comment=comment)

    if request.method == 'POST':
        check_csrf()

        if 'continue' in request.form:
            posts.remove_comment(comment_id)
        return redirect('/post/' + str(comment['post_id']))

@app.route('/user/<int:user_id>')
def show_user(user_id):
    user = users.get(user_id)
    if not user:
        abort(404)
    posts = users.get_posts(user_id)
    comment_count = users.count_comments(user_id)
    return render_template('user.html', user=user, posts=posts,
                           comment_count=comment_count)

@app.teardown_appcontext
def teardown_appcontext(exception):
    db.close_connection()