from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os
from functools import wraps

app = Flask(__name__)
DB_NAME = "data.db"

# ----------------------
# Database utilities
# ----------------------
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if os.path.exists(DB_NAME):
        return
    
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

# ----------------------
# Error handling
# ----------------------
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

def validate_json(*args):
    @wraps(validate_json)
    def wrapper(f):
        @wraps(f)
        def decorated_function(*func_args, **func_kwargs):
            if not request.is_json:
                return jsonify({"error": "Request must be JSON"}), 400
            return f(*func_args, **func_kwargs)
        return decorated_function
    return wrapper

# ----------------------
# API Routes
# ----------------------
@app.route('/')
def home():
    return jsonify({
        "message": "Database server is running successfully!",
        "endpoints": {
            "GET /": "This message",
            "POST /add_user": "Add a new user",
            "GET /get_users": "Retrieve all users",
            "GET /dashboard": "View users dashboard"
        }
    }), 200

@app.route('/add_user', methods=['POST'])
@validate_json()
def add_user():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    
    if not name or not email:
        return jsonify({"error": "Both 'name' and 'email' are required"}), 400
    
    if '@' not in email:
        return jsonify({"error": "Invalid email format"}), 400
    
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                'INSERT INTO users (name, email) VALUES (?, ?)',
                (name, email)
            )
            conn.commit()
            user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409
    
    return jsonify({
        "message": "User added successfully!",
        "id": user_id,
        "name": name,
        "email": email
    }), 201

@app.route('/get_users', methods=['GET'])
def get_users():
    try:
        with get_db_connection() as conn:
            cursor = conn.execute('SELECT id, name, email, created_at FROM users ORDER BY id DESC')
            users = [dict(row) for row in cursor.fetchall()]
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            
            if cursor.rowcount == 0:
                return jsonify({"error": "User not found"}), 404
        
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------
# Dashboard route
# ----------------------
@app.route('/dashboard')
def dashboard():
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT id, name, email, created_at FROM users ORDER BY id DESC")
            users = cursor.fetchall()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Users Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h2 { color: #333; }
                table { border-collapse: collapse; width: 100%; max-width: 800px; }
                th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                th { background-color: #4CAF50; color: white; }
                tr:nth-child(even) { background-color: #f9f9f9; }
                tr:hover { background-color: #f5f5f5; }
                .btn { padding: 6px 12px; background-color: #dc3545; color: white; border: none; cursor: pointer; border-radius: 4px; }
                .btn:hover { background-color: #c82333; }
            </style>
        </head>
        <body>
            <h2>Users Dashboard</h2>
            {% if users %}
            <table>
                <tr><th>ID</th><th>Name</th><th>Email</th><th>Created</th></tr>
                {% for u in users %}
                <tr>
                    <td>{{ u['id'] }}</td>
                    <td>{{ u['name'] }}</td>
                    <td>{{ u['email'] }}</td>
                    <td>{{ u['created_at'] }}</td>
                </tr>
                {% endfor %}
            </table>
            {% else %}
            <p>No users found.</p>
            {% endif %}
        </body>
        </html>
        """
        return render_template_string(html, users=users)
    except Exception as e:
        return f"<p>Error loading dashboard: {str(e)}</p>", 500

# ----------------------
# Run server
# ----------------------
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
