import sqlite3
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

    sql = """INSERT INTO users (username, password_hash, registration_date)
             VALUES (?, ?, date())"""
    try:
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return False
    return True

def get(user_id):
    sql = 'SELECT id, username, registration_date FROM users WHERE id = ?'
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_posts(user_id):
    sql = """SELECT p.id, p.title, p.image_id, p.sent_at
             FROM posts p, users u
             WHERE u.id = ? AND u.id = p.user_id
             ORDER BY p.id DESC"""
    return db.query(sql, [user_id])

def count_comments(user_id):
    sql = 'SELECT COUNT(*) FROM comments c, users u WHERE u.id = ? AND c.user_id = u.id'
    return db.query(sql, [user_id])[0][0]