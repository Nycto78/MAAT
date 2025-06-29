from abc import ABC, abstractmethod
import mysql.connector
from mysql.connector import Error
from tkinter import messagebox
from infrastructure.config.database import DatabaseConnector


class Command(ABC):
    """Interfaz base para los comandos"""
    @abstractmethod
    def execute(self):
        pass
    
    @abstractmethod
    def undo(self):
        pass

class GuardarEncargoCommand(Command):
    def __init__(self, datos):
        self.datos = datos
        self.encargo_id = None
    
    def execute(self):
        conn = DatabaseConnector.get_connection()
        try:
            cursor = conn.cursor()
            # Verificar que los datos tienen todos los campos necesarios
            required_fields = ['nombre_conductor', 'apellido_conductor', 'patente', 
                            'fecha_reparto', 'producto', 'cantidad', 'repartiendo']
            
            for field in required_fields:
                if field not in self.datos:
                    raise ValueError(f"Falta el campo requerido: {field}")
            
            cursor.execute("""
                INSERT INTO encargos 
                (nombre_conductor, apellido_conductor, patente, fecha_reparto, producto, cantidad, repartiendo)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                self.datos['nombre_conductor'],
                self.datos['apellido_conductor'],
                self.datos['patente'],
                self.datos['fecha_reparto'],
                self.datos['producto'],
                int(self.datos['cantidad']),  # Asegurar que es entero
                bool(self.datos['repartiendo'])  # Asegurar que es booleano
            ))
            self.encargo_id = cursor.lastrowid
            conn.commit()
            return True
        except Exception as e:
            print(f"Error al guardar encargo: {e}")
            return False
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def undo(self):
        if self.encargo_id:
            conn = DatabaseConnector.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM encargos WHERE id = %s", (self.encargo_id,))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error al deshacer guardado: {e}")
                return False
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
        return False

class ActualizarEncargoCommand(Command):
    def __init__(self, datos):
        self.datos = datos
        self.estado_anterior = None  # Para almacenar el estado antes de la actualización
    
    def execute(self):
        conn = DatabaseConnector.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Primero obtenemos el estado actual para poder deshacer
            cursor.execute("SELECT * FROM encargos WHERE id = %s", (self.datos['id'],))
            self.estado_anterior = cursor.fetchone()
            
            # Realizamos la actualización
            cursor.execute("""
                UPDATE encargos SET
                nombre_conductor = %s,
                apellido_conductor = %s,
                patente = %s,
                fecha_reparto = %s,
                producto = %s,
                cantidad = %s,
                repartiendo = %s
                WHERE id = %s
            """, (
                self.datos['nombre_conductor'],
                self.datos['apellido_conductor'],
                self.datos['patente'],
                self.datos['fecha_reparto'],
                self.datos['producto'],
                self.datos['cantidad'],
                self.datos['repartiendo'],
                self.datos['id']
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar encargo: {e}")
            return False
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def undo(self):
        if self.estado_anterior:
            conn = DatabaseConnector.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE encargos SET
                    nombre_conductor = %s,
                    apellido_conductor = %s,
                    patente = %s,
                    fecha_reparto = %s,
                    producto = %s,
                    cantidad = %s,
                    repartiendo = %s
                    WHERE id = %s
                """, (
                    self.estado_anterior['nombre_conductor'],
                    self.estado_anterior['apellido_conductor'],
                    self.estado_anterior['patente'],
                    self.estado_anterior['fecha_reparto'],
                    self.estado_anterior['producto'],
                    self.estado_anterior['cantidad'],
                    self.estado_anterior['repartiendo'],
                    self.estado_anterior['id']
                ))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error al deshacer actualización: {e}")
                return False
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
        return False
    
    def execute(self):
        conn = DatabaseConnector.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE encargos SET
                nombre_conductor = %s,
                apellido_conductor = %s,
                patente = %s,
                fecha_reparto = %s,
                producto = %s,
                cantidad = %s,
                repartiendo = %s
                WHERE id = %s
            """, (
                self.datos['nombre_conductor'],
                self.datos['apellido_conductor'],
                self.datos['patente'],
                self.datos['fecha_reparto'],
                self.datos['producto'],
                self.datos['cantidad'],
                self.datos['repartiendo'],
                self.datos['id']
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar encargo: {e}")
            return False
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def undo(self):
        """Restaura el estado anterior"""
        if not self.estado_anterior:
            return
            
        conn = DatabaseConnector.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE encargos SET
                nombre_conductor = %s,
                apellido_conductor = %s,
                patente = %s,
                fecha_reparto = %s,
                producto = %s,
                cantidad = %s,
                repartiendo = %s
                WHERE id = %s
            """, (
                self.estado_anterior['nombre_conductor'],
                self.estado_anterior['apellido_conductor'],
                self.estado_anterior['patente'],
                self.estado_anterior['fecha_reparto'],
                self.estado_anterior['producto'],
                self.estado_anterior['cantidad'],
                self.estado_anterior['repartiendo'],
                self.estado_anterior['id']
            ))
            conn.commit()
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

class EliminarEncargoCommand(Command):
    def __init__(self, encargo_id):
        self.encargo_id = encargo_id
        self.datos_eliminados = None  # Para almacenar los datos del encargo eliminado
    
    def execute(self):
        conn = DatabaseConnector.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Primero obtenemos los datos para poder deshacer
            cursor.execute("SELECT * FROM encargos WHERE id = %s", (self.encargo_id,))
            self.datos_eliminados = cursor.fetchone()
            
            if not self.datos_eliminados:
                return False
                
            # Realizamos la eliminación
            cursor.execute("DELETE FROM encargos WHERE id = %s", (self.encargo_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al eliminar encargo: {e}")
            return False
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def undo(self):
        if self.datos_eliminados:
            conn = DatabaseConnector.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO encargos 
                    (id, nombre_conductor, apellido_conductor, patente, fecha_reparto, producto, cantidad, repartiendo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    self.datos_eliminados['id'],
                    self.datos_eliminados['nombre_conductor'],
                    self.datos_eliminados['apellido_conductor'],
                    self.datos_eliminados['patente'],
                    self.datos_eliminados['fecha_reparto'],
                    self.datos_eliminados['producto'],
                    self.datos_eliminados['cantidad'],
                    self.datos_eliminados['repartiendo']
                ))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error al deshacer eliminación: {e}")
                return False
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
        return False