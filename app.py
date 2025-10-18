from flask import Flask, request, jsonify, render_template_string
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# ----------------------
# Initialize Firebase
# ----------------------
cred = credentials.Certificate("myserverdb-26697-firebase-adminsdk-fbsvc-ab7a87079a.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
users_collection = db.collection("users")

# ----------------------
# API Routes
# ----------------------
@app.route('/')
def home():
    return jsonify({"message": "Firebase server is running successfully!"})

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    if not name or not email:
        return jsonify({"error": "Both 'name' and 'email' are required"}), 400

    doc_ref = users_collection.document()  # auto-generated ID
    doc_ref.set({"name": name, "email": email})

    return jsonify({"message": "User added successfully!", "name": name, "email": email})

@app.route('/get_users', methods=['GET'])
def get_users():
    users = []
    docs = users_collection.stream()
    for doc in docs:
        u = doc.to_dict()
        u["id"] = doc.id
        users.append(u)
    return jsonify(users)

# ----------------------
# Dashboard route
# ----------------------
@app.route('/dashboard')
def dashboard():
    docs = users_collection.stream()
    users = []
    for doc in docs:
        d = doc.to_dict()
        d["id"] = doc.id
        users.append(d)

    html = """
    <h2>Users Dashboard (Firebase)</h2>
    <table border="1" cellpadding="5">
        <tr><th>ID</th><th>Name</th><th>Email</th></tr>
        {% for u in users %}
        <tr>
            <td>{{u['id']}}</td>
            <td>{{u['name']}}</td>
            <td>{{u['email']}}</td>
        </tr>
        {% endfor %}
    </table>
    """
    return render_template_string(html, users=users)

# ----------------------
# Run server
# ----------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



