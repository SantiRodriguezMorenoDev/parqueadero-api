from flask import Flask, request, jsonify
from flask_cors import CORS
from config import get_db_connection

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"mensaje": "API del parqueadero funcionando"})

# --- LOGIN ---
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, email, password, rol_id FROM usuarios WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Comparar contraseña (por ahora texto plano)
    if password != user[3]:
        return jsonify({"error": "Contraseña incorrecta"}), 401

    # Enviar datos al frontend
    return jsonify({
        "id": user[0],
        "nombre": user[1],
        "email": user[2],
        "rol_id": user[4]
    })