# infrastructure/repositories/repositorio_encargos.py

from infrastructure.config.database import DatabaseConnector

def obtener_todos_encargos():
    conexion = DatabaseConnector.get_connection()
    if not conexion:
        return []
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM encargos ORDER BY fecha_reparto DESC")
        return cursor.fetchall()
    except Exception as e:
        print(f"❌ Error al obtener encargos: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()

def guardar_encargo(data):
    conexion = DatabaseConnector.get_connection()
    cursor = conexion.cursor()
    try:
        query = """
            INSERT INTO encargos (
                nombre_conductor, apellido_conductor, patente,
                fecha_reparto, producto, cantidad, repartiendo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        valores = (
            data["nombre_conductor"],
            data["apellido_conductor"],
            data["patente"],
            data["fecha_reparto"],
            data["producto"],
            data["cantidad"],
            data["repartiendo"],
        )
        cursor.execute(query, valores)
        conexion.commit()
    finally:
        cursor.close()
        conexion.close()

def actualizar_encargo(id, data):
    conexion = DatabaseConnector.get_connection()
    cursor = conexion.cursor()
    try:
        query = """
            UPDATE encargos SET
                nombre_conductor = %s,
                apellido_conductor = %s,
                patente = %s,
                fecha_reparto = %s,
                producto = %s,
                cantidad = %s,
                repartiendo = %s
            WHERE id = %s
        """
        valores = (
            data["nombre_conductor"],
            data["apellido_conductor"],
            data["patente"],
            data["fecha_reparto"],
            data["producto"],
            data["cantidad"],
            data["repartiendo"],
            id
        )
        cursor.execute(query, valores)
        conexion.commit()
    finally:
        cursor.close()
        conexion.close()

def eliminar_encargo(id):
    conexion = DatabaseConnector.get_connection()
    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM encargos WHERE id = %s", (id,))
        conexion.commit()
    finally:
        cursor.close()
        conexion.close()
