from flask import Flask, request, jsonify
import base64
from config_connect import get_db_connection

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT username, balance FROM users WHERE username = %s AND password = %s"
    cursor.execute(query % (username, password))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        token = base64.b64encode(result[0].encode()).decode()
        return jsonify({"token": token, "balance": result[1]})
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

    conn = get_db_connection()
    cursor = conn.cursor()
    select_query = "SELECT balance FROM users WHERE username = %s"
    cursor.execute(select_query % (username,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return jsonify({"error": "User not found"}), 400

    current_balance = row[0]
    if not isinstance(amount, (int, float)):
        cursor.close()
        conn.close()
        return jsonify({"error": "Invalid amount"}), 400

    new_balance = current_balance - amount
    update_query = "UPDATE users SET balance = %s WHERE username = %s"
    cursor.execute(update_query % (new_balance, username))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Payment successful", "new_balance": new_balance})

if __name__ == '__main__':
    app.run(debug=True)