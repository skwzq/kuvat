import db
import images

def get(post_id):
    sql = """SELECT p.id,
                    p.title,
                    p.image_id,
                    p.description,
                    p.sent_at,
                    p.user_id,
                    u.username
             FROM posts p, users u
             WHERE p.id = ? AND u.id = p.user_id"""
    result = db.query(sql, [post_id])
    return result[0] if result else None

def get_list():
    sql = """SELECT p.id, p.title, p.image_id, p.sent_at, u.username
             FROM posts p, users u
             WHERE u.id = p.user_id
             ORDER BY p.id DESC"""
    return db.query(sql)

def get_user(post_id):
    sql = 'SELECT user_id FROM posts WHERE id = ?'
    result = db.query(sql, [post_id])
    return result[0][0] if result else None

def search(query):
    sql = """SELECT p.id, p.title, p.image_id, p.sent_at, u.username
             FROM posts p, users u
             WHERE u.id = p.user_id
             AND (p.title LIKE ? OR p.description LIKE ?)
             ORDER BY p.id DESC"""
    return db.query(sql, ['%' + query + '%'] * 2)

def add(title, image, file_format, description, user_id):
    image_id = images.add(image, file_format)
    sql = """INSERT INTO posts (title, image_id, description, sent_at, user_id)
             VALUES (?, ?, ?, datetime('now'), ?)"""
    db.execute(sql, [title, image_id, description, user_id])

def edit(post_id, title, description):
    sql = 'UPDATE posts SET title = ?, description = ? WHERE id = ?'
    db.execute(sql, [title, description, post_id])

def remove(post_id):
    sql = 'SELECT image_id FROM posts WHERE id = ?'
    image_id = db.query(sql, [post_id])[0][0]

    sql = 'DELETE FROM posts WHERE id = ?'
    db.execute(sql, [post_id])
    images.remove(image_id)