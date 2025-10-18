from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_NAME = "data.db"

# ----------------------
# Initialize database
# ----------------------
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT
            )
        ''')
        conn.commit()

init_db()

# ----------------------
# Routes
# ----------------------
@app.route('/')
def home():
    return jsonify({"message": "Database server is running successfully!"})

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    if not name or not email:
        return jsonify({"error": "Both 'name' and 'email' are required"}), 400

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))
        conn.commit()

    return jsonify({"message": "User added successfully!", "name": name, "email": email})

@app.route('/get_users', methods=['GET'])
def get_users():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute('SELECT * FROM users')
        users = [{"id": row[0], "name": row[1], "email": row[2]} for row in cursor.fetchall()]
    return jsonify(users)

# ----------------------
# Run server
# ----------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
