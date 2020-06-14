import mysql.connector

db = None
def initialize(config):
    global db
    db = mysql.connector.connect(**config)
    return db
  
def db_do(query, data):
    db.ping(True, 3, 1)
    cursor = db.cursor()
    cursor.execute(query, data)
    db.commit()
    cursor.close()

def db_fetchone(query, data):
    db.ping(True, 3, 1)
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, data)
    result = cursor.fetchone()
    cursor.close()
    return result

def db_fetchall(query, data):
    db.ping(True, 3, 1)
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, data)
    result = cursor.fetchall()
    cursor.close()
    return result
