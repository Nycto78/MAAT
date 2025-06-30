# infrastructure/repositories/repositorio_mysql.py

import mysql.connector
from infrastructure.config.database import DatabaseConnector
from domain.entities.producto import Producto

class RepositorioMySQL:
    def __init__(self):
        self.conn = DatabaseConnector().conn


    def obtener_todos(self):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, categoria, cantidad, precio FROM productos")
        resultados = cursor.fetchall()
        cursor.close()
        return resultados
    
    def obtener_por_id(self, id: int):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, categoria, cantidad, precio FROM productos WHERE id = %s", (id,))
        resultado = cursor.fetchone()
        cursor.close()
        return resultado
    def actualizar(self, id: int, producto: Producto):
        cursor = self.conn.cursor()
        query = """
            UPDATE productos
            SET nombre = %s, categoria = %s, cantidad = %s, precio = %s
            WHERE id = %s
        """
        valores = (
            producto.nombre,
            producto.categoria,
            producto.cantidad,
            producto.precio,
            id
        )
        cursor.execute(query, valores)
        self.conn.commit()
        cursor.close()

    def guardar(self, producto: Producto):
        cursor = self.conn.cursor()
        query = """
            INSERT INTO productos (nombre, categoria, cantidad, precio)
            VALUES (%s, %s, %s, %s)
        """
        valores = (
            producto.nombre,
            producto.categoria,
            producto.cantidad,
            producto.precio
        )
        cursor.execute(query, valores)
        self.conn.commit()
        cursor.close()
        
        
    def eliminar(self, id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
        self.conn.commit()
        cursor.close()
