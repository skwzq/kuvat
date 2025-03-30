from werkzeug.security import check_password_hash, generate_password_hash
import db

def login(username, password):
    sql = 'SELECT id, password_hash FROM users WHERE username = ?'
    result = db.query(sql, [username])
    if not result:
        return None
    user_id, password_hash = result[0]
    if check_password_hash(password_hash, password):
        return user_id
    else:
        return None

def create(username, password):
    password_hash = generate_password_hash(password)

    sql = 'INSERT INTO users (username, password_hash) VALUES (?, ?)'
    try:
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return False
    return True