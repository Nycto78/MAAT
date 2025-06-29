from infrastructure.config.database import DatabaseConnector
from mysql.connector import Error

def obtener_todos_encargos():
    """Obtiene todos los encargos de la base de datos"""
    conn = None
    try:
        conn = DatabaseConnector.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, nombre_conductor, apellido_conductor, 
            patente, fecha_reparto, producto, cantidad, repartiendo
            FROM encargos
            ORDER BY fecha_reparto DESC
        """)
        return cursor.fetchall()
    except Error as e:
        print(f"Error al obtener encargos: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def guardar_encargo(datos):
    """Guarda un nuevo encargo en la base de datos"""
    conn = None
    try:
        conn = DatabaseConnector.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO encargos 
            (nombre_conductor, apellido_conductor, patente, 
            fecha_reparto, producto, cantidad, repartiendo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            datos['nombre_conductor'],
            datos['apellido_conductor'],
            datos['patente'],
            datos['fecha_reparto'],
            datos['producto'],
            datos['cantidad'],
            datos['repartiendo']
        ))
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error al guardar encargo: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()