from flask import Flask, request, jsonify
from flask_cors import CORS
from config import get_db_connection

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"mensaje": "API del parqueadero funcionando"})

# --- LOGIN ---
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, nombre, rol_id
        FROM usuarios
        WHERE email = %s AND password = %s
    """, (email, password))

    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        return jsonify({
            "success": True,
            "usuario": {
                "id": user[0],
                "nombre": user[1],
                "rol_id": user[2]
            }
        })
    else:
        return jsonify({"success": False, "mensaje": "Credenciales incorrectas"}), 401


if __name__ == '__main__':
    app.run(debug=True)