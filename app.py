import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)
DB_FILE = "data.db"

# --- Initialize database ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            value REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()


# --- Routes ---
@app.route('/')
def home():
    return jsonify({"message": "Database server is running successfully!"})


@app.route('/add', methods=['POST'])
def add_record():
    data = request.get_json()
    name = data.get('name')
    value = data.get('value')

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO readings (name, value) VALUES (?, ?)", (name, value))
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "name": name, "value": value})


@app.route('/all')
def get_all():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM readings")
    rows = cursor.fetchall()
    conn.close()

    return jsonify([{"id": r[0], "name": r[1], "value": r[2]} for r in rows])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
