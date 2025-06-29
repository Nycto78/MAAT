# 📍 Archivo: mi_aplicacion/infrastructure/config/database.py

import mysql.connector

from mysql.connector import connect, Error
from infrastructure.config.db_config import DB_CONFIG
# Puedes mover esto a un archivo separado si quieres


class DatabaseConnector:
    @staticmethod
    def get_connection():
        try:
            conn = connect(**DB_CONFIG)
            print("✅ Conexión a MySQL establecida correctamente.")
            return conn
        except Error as e:
            print(f"❌ Error de conexión: {e}")
            return None
    @staticmethod
    def verificar_estructura():
        try:
            conn = mysql.connector.connect(
                host=DB_CONFIG["host"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                port=DB_CONFIG["port"]
            )

            cursor = conn.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS productos_1")
            cursor.execute("USE productos_1")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS encargos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre_conductor VARCHAR(100) NOT NULL,
                    apellido_conductor VARCHAR(100) NOT NULL,
                    pantente VARCHAR(20) NOT NULL,
                    fecha_reparto DATE NOT NULL,
                    producto VARCHAR(100) NOT NULL,
                    cantidad INT NOT NULL,
                    repartiendo BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Tabla 'encargos' verificada o creada correctamente.")
            return True
        except Error as e:
            print(f"❌ Error al verificar estructura: {e}")
            return False
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
