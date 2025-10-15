import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        host="dpg-d3o1kuc9c44c739mv3s0-a.oregon-postgres.render.com",
        database="bdparqueadero",
        user="bdparqueadero_user",
        password="qKFzObbHeP7FHHegUa2PryHlKy7Umxne",
        port="5432",
        sslmode="require"
    )
    return conn
