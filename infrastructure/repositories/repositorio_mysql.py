from infrastructure.config.database import DatabaseConnector

class RepositorioMySQL:
    """Implementación concreta para operaciones de inventario."""
    
    def actualizar_cantidad(self, producto_id: str, cantidad: int) -> bool:
        """Actualiza el stock de un producto."""
        conn = DatabaseConnector.get_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE productos SET cantidad = cantidad + %s WHERE id = %s",
                (cantidad, producto_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al actualizar stock: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def obtener_por_id(self, producto_id: str) -> dict:
        """Obtiene un producto por su ID."""
        conn = DatabaseConnector.get_connection()
        if not conn:
            return {}
            
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM productos WHERE id = %s", (producto_id,))
            return cursor.fetchone() or {}
        except Exception as e:
            print(f"Error al obtener producto: {e}")
            return {}
        finally:
            cursor.close()
            conn.close()