from flask import Flask, request, jsonify
import base64

app = Flask(__name__)

users = {
    "user1": {"password": "pass123", "balance": 1000}
}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if username in users and users[username]['password'] == password:
        token = base64.b64encode(username.encode()).decode()
        return jsonify({"token": token})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/pay', methods=['POST'])
def pay():
    data = request.get_json()
    token = data.get('token')
    amount = data.get('amount')
    if not token or amount is None:
        return jsonify({"error": "Missing token or amount"}), 400
    try:
        username = base64.b64decode(token.encode()).decode()
    except:
        return jsonify({"error": "Invalid token"}), 400
    if username not in users:
        return jsonify({"error": "User not found"}), 400
    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400
    if users[username]['balance'] < amount:
        return jsonify({"error": "Insufficient balance"}), 400
    users[username]['balance'] -= amount
    return jsonify({"message": "Payment successful", "new_balance": users[username]['balance']})

if __name__ == '__main__':
    app.run(debug=True)