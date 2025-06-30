import mysql.connector
from mysql.connector import connect, Error
from infrastructure.config.db_config import DB_CONFIG

class DatabaseConnector:
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializar_conexion()
        return cls._instancia

    def _inicializar_conexion(self):
        try:
            self.conn = connect(**DB_CONFIG)
            self.cursor = self.conn.cursor(dictionary=True)
            print("✅ Conexión a MySQL establecida correctamente.")
        except Error as e:
            print(f"❌ Error de conexión: {e}")
            self.conn = None
            self.cursor = None

    def obtener_cursor(self):
        return self.cursor

    def commit(self):
        if self.conn:
            self.conn.commit()

    def cerrar(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
            DatabaseConnector._instancia = None
    def close(self):
        if self.conn and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
            DatabaseConnector._instancia = None

    def verificar_estructura(self):
        try:
            temp_conn = mysql.connector.connect(
                host=DB_CONFIG["host"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                port=DB_CONFIG["port"]
            )
            cursor = temp_conn.cursor()
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
            if temp_conn.is_connected():
                cursor.close()
                temp_conn.close()
