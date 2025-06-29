from infrastructure.config.database import DatabaseConnector

def obtener_todos_encargos():
    conexion = DatabaseConnector.get_connection()
    if not conexion:
        return []

    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM encargos ORDER BY fecha_reparto DESC")
        resultados = cursor.fetchall()
        return resultados
    except Exception as e:
        print(f" Error al obtener encargos: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()
