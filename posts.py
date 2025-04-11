import sqlite3
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
    sql = """SELECT p.id, p.title, p.image_id, p.sent_at, p.user_id, u.username
             FROM posts p, users u
             WHERE u.id = p.user_id
             ORDER BY p.id DESC"""
    return db.query(sql)

def get_user(post_id):
    sql = 'SELECT user_id FROM posts WHERE id = ?'
    result = db.query(sql, [post_id])
    return result[0][0] if result else None

def get_tags(post_id):
    sql = 'SELECT tag FROM tags WHERE post_id = ?'
    return [t[0] for t in db.query(sql, [post_id])]

def search(query, tag_only):
    words = query.split()

    if tag_only:
        where = 'AND p.id IN (SELECT post_id FROM tags WHERE tag LIKE ?)'
    else:
        where = """AND (p.title LIKE ? OR p.description LIKE ?
                   OR (p.id IN (SELECT post_id FROM tags WHERE tag LIKE ?)))"""

    sql = f"""SELECT DISTINCT p.id, p.title, p.image_id, p.sent_at, u.username
             FROM posts p, users u
             WHERE u.id = p.user_id {where * len(words)}
             ORDER BY p.id DESC"""

    params = []
    for word in words:
        if not tag_only:
            params.append('%' + word + '%')
            params.append('%' + word + '%')
        params.append(word)

    return db.query(sql, params)

def add(title, image, file_format, description, tags, user_id):
    image_id = images.add(image, file_format)
    sql = """INSERT INTO posts (title, image_id, description, sent_at, user_id)
             VALUES (?, ?, ?, datetime('now'), ?)"""
    db.execute(sql, [title, image_id, description, user_id])

    post_id = db.last_insert_id()
    tags = tags.lower().split()
    add_tags(post_id, tags)

    return post_id

def edit(post_id, title, description, tags):
    sql = 'UPDATE posts SET title = ?, description = ? WHERE id = ?'
    db.execute(sql, [title, description, post_id])

    new_tags = tags.lower().split()
    old_tags = get_tags(post_id)
    added_tags = set(new_tags).difference(old_tags)
    removed_tags = set(old_tags).difference(new_tags)

    add_tags(post_id, added_tags)
    remove_tags(post_id, removed_tags)

def remove(post_id):
    sql = 'SELECT image_id FROM posts WHERE id = ?'
    image_id = db.query(sql, [post_id])[0][0]

    sql = 'DELETE FROM posts WHERE id = ?'
    db.execute(sql, [post_id])
    images.remove(image_id)

def add_tags(post_id, tags):
    sql = 'INSERT INTO tags (tag, post_id) VALUES (?, ?)'
    for tag in tags:
        try:
            db.execute(sql, [tag, post_id])
        except sqlite3.IntegrityError:
            pass

def remove_tags(post_id, tags):
    sql = 'DELETE FROM tags WHERE tag = ? AND post_id = ?'
    for tag in tags:
        db.execute(sql, [tag, post_id])

def get_comment(comment_id):
    sql = 'SELECT id, content, user_id, post_id FROM comments WHERE id = ?'
    result = db.query(sql, [comment_id])
    return result[0] if result else None

def get_comments(post_id):
    sql = """SELECT c.id, c.content, c.sent_at, c.user_id, u.username
             FROM comments c, posts p, users u
             WHERE p.id = ? AND c.post_id = p.id AND u.id = c.user_id
             ORDER BY c.id"""
    return db.query(sql, [post_id])

def add_comment(content, user_id, post_id):
    sql = """INSERT INTO comments (content, sent_at, user_id, post_id)
             VALUES (?, datetime('now'), ?, ?)"""
    db.execute(sql, [content, user_id, post_id])

def edit_comment(comment_id, content):
    sql = 'UPDATE comments SET content = ? WHERE id = ?'
    db.execute(sql, [content, comment_id])

def remove_comment(comment_id):
    sql = 'DELETE FROM comments WHERE id = ?'
    db.execute(sql, [comment_id])