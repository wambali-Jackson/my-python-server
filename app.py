from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Server is running successfully!"})

@app.route('/hello/<name>')
def hello(name):
    return jsonify({"greeting": f"Hello, {name}!"})

@app.route('/sum', methods=['POST'])
def sum_numbers():
    data = request.get_json()
    a = data.get('a', 0)
    b = data.get('b', 0)
    return jsonify({"sum": a + b})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
