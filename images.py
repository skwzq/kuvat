import db

def get(image_id):
    sql = 'SELECT data, format FROM images WHERE id = ?'
    result = db.query(sql, [image_id])
    return result[0] if result else None

def add(image, file_format):
    sql = 'INSERT INTO images (data, format) VALUES (?, ?)'
    db.execute(sql, [image, file_format])
    return db.last_insert_id()

def remove(image_id):
    sql = 'DELETE FROM images WHERE id = ?'
    db.execute(sql, [image_id])