from flask import Flask, request, jsonify
from flask_cors import CORS
from config import get_db_connection
from datetime import datetime

app = Flask(__name__)
CORS(app)

# --- HOME ---
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


# --- REGISTRAR ENTRADA DE VEHÍCULO ---
@app.route("/registrar_entrada", methods=["POST"])
def registrar_entrada():
    data = request.get_json()
    placa = data.get("placa")
    tipo_vehiculo_id = data.get("tipo_vehiculo_id")
    usuario_id = data.get("usuario_id")

    if not placa or not tipo_vehiculo_id or not usuario_id:
        return jsonify({"error": "Faltan datos"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    # Verificar si el vehículo ya está dentro
    cur.execute("SELECT * FROM registros_vehiculos WHERE placa = %s AND pagado = false", (placa,))
    existente = cur.fetchone()

    if existente:
        cur.close()
        conn.close()
        return jsonify({"error": "El vehículo ya está registrado y no ha salido"}), 400

    # Insertar nuevo registro
    cur.execute("""
        INSERT INTO registros_vehiculos (placa, tipo_vehiculo_id, usuario_id)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (placa, tipo_vehiculo_id, usuario_id))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"mensaje": "Entrada registrada correctamente"})


# --- REGISTRAR SALIDA DE VEHÍCULO ---
@app.route("/registrar_salida", methods=["POST"])
def registrar_salida():
    data = request.get_json()
    placa = data.get("placa")
    metodo_pago = data.get("metodo_pago")

    if not placa or not metodo_pago:
        return jsonify({"error": "Faltan datos"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    # Buscar el registro activo
    cur.execute("""
        SELECT rv.id, rv.fecha_hora_entrada, tv.tarifa_por_minuto
        FROM registros_vehiculos rv
        JOIN tipos_vehiculos tv ON rv.tipo_vehiculo_id = tv.id
        WHERE rv.placa = %s AND rv.pagado = false
    """, (placa,))
    registro = cur.fetchone()

    if not registro:
        cur.close()
        conn.close()
        return jsonify({"error": "No hay registro activo para esa placa"}), 404

    id_registro = registro[0]
    entrada = registro[1]
    tarifa = registro[2]

    # Calcular total según minutos
    minutos = (datetime.now() - entrada).total_seconds() / 60
    valor_total = round(minutos * tarifa, 2)

    cur.execute("""
        UPDATE registros_vehiculos
        SET fecha_hora_salida = NOW(),
            valor_total = %s,
            metodo_pago = %s,
            pagado = true
        WHERE id = %s
    """, (valor_total, metodo_pago, id_registro))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "mensaje": "Salida registrada correctamente",
        "total": valor_total
    })


# --- OBTENER VEHÍCULOS ACTIVOS (opcional para el panel) ---
@app.route("/vehiculos_activos", methods=["GET"])
def vehiculos_activos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT rv.id, rv.placa, tv.nombre AS tipo, rv.fecha_hora_entrada
        FROM registros_vehiculos rv
        JOIN tipos_vehiculos tv ON rv.tipo_vehiculo_id = tv.id
        WHERE rv.pagado = false
        ORDER BY rv.fecha_hora_entrada ASC
    """)
    registros = cur.fetchall()
    cur.close()
    conn.close()

    resultado = []
    for r in registros:
        resultado.append({
            "id": r[0],
            "placa": r[1],
            "tipo": r[2],
            "entrada": r[3].strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify(resultado)


# --- MAIN ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
