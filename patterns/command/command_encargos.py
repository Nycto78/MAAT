from abc import ABC, abstractmethod
import mysql.connector
from mysql.connector import Error
from tkinter import messagebox


class Command(ABC):
    """Interfaz base para los comandos"""
    @abstractmethod
    def execute(self):
        pass
    
    @abstractmethod
    def undo(self):
        pass

        
class GuardarEncargoCommand(Command):
    def __init__(self, conexion, datos_encargo):
        self.conexion = conexion
        self.datos = datos_encargo
        self.ultimo_id = None

    def execute(self):
        try:
            cursor = self.conexion.cursor()
            query = """
                INSERT INTO encargos 
                (nombre_conductor, apellido_conductor, pantente, fecha_reparto, producto, cantidad, repartiendo)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, self.datos)
            self.conexion.commit()
            self.ultimo_id = cursor.lastrowid
            return True
        except Error as e:
            messagebox.showerror("Error", f"No se pudo guardar el encargo: {e}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def undo(self):
        if self.ultimo_id:
            try:
                cursor = self.conexion.cursor()
                cursor.execute("DELETE FROM encargos WHERE id = %s", (self.ultimo_id,))
                self.conexion.commit()
                return True
            except Error as e:
                messagebox.showerror("Error", f"No se pudo deshacer la operacion: {e}")
                return False
            finally:
                if 'cursor' in locals():
                    cursor.close()
        return False

class ActualizarEncargoCommand(Command):
    """Comando concreto para actualizar un encargo existente"""
    def __init__(self, conexion, entries, repartiendo_var, tree, encargo_seleccionado):
        self.conexion = conexion
        self.entries = entries
        self.repartiendo_var = repartiendo_var
        self.tree = tree
        self.encargo_seleccionado = encargo_seleccionado
        self.datos_anteriores = None
        
    def execute(self):
        if not self.encargo_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un encargo primero")
            return False

        try:
            # Guardar datos anteriores para posible undo
            cursor = self.conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM encargos WHERE id = %s", (self.encargo_seleccionado[0],))
            self.datos_anteriores = cursor.fetchone()
            
            query = """
                UPDATE encargos SET
                nombre_conductor = %s,
                apellido_conductor = %s,
                pantente = %s,
                fecha_reparto = %s,
                producto = %s,
                cantidad = %s,
                repartiendo = %s
                WHERE id = %s
            """
            valores = (
                self.entries['nombre_conductor'].get(),
                self.entries['apellido_conductor'].get(),
                self.entries['patente'].get(),
                self.entries['fecha_reparto'].get(),
                self.entries['producto'].get(),
                int(self.entries['cantidad'].get()),
                self.repartiendo_var.get(),
                self.encargo_seleccionado[0]
            )

            cursor.execute(query, valores)
            self.conexion.commit()
            messagebox.showinfo("Exito", "Encargo actualizado correctamente")
            return True

        except Error as e:
            messagebox.showerror("Error", f"No se pudo actualizar el encargo: {e}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def undo(self):
        if self.datos_anteriores:
            try:
                cursor = self.conexion.cursor()
                query = """
                    UPDATE encargos SET
                    nombre_conductor = %s,
                    apellido_conductor = %s,
                    pantente = %s,
                    fecha_reparto = %s,
                    producto = %s,
                    cantidad = %s,
                    repartiendo = %s
                    WHERE id = %s
                """
                valores = (
                    self.datos_anteriores['nombre_conductor'],
                    self.datos_anteriores['apellido_conductor'],
                    self.datos_anteriores['pantente'],
                    self.datos_anteriores['fecha_reparto'],
                    self.datos_anteriores['producto'],
                    self.datos_anteriores['cantidad'],
                    self.datos_anteriores['repartiendo'],
                    self.datos_anteriores['id']
                )

                cursor.execute(query, valores)
                self.conexion.commit()
                return True
            except Error as e:
                messagebox.showerror("Error", f"No se pudo deshacer la operacion: {e}")
                return False
            finally:
                if 'cursor' in locals():
                    cursor.close()
        return False

class EliminarEncargoCommand(Command):
    """Comando concreto para eliminar un encargo"""
    def __init__(self, conexion, tree, encargo_seleccionado):
        self.conexion = conexion
        self.tree = tree
        self.encargo_seleccionado = encargo_seleccionado
        self.datos_eliminados = None
        
    def execute(self):
        if not self.encargo_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un encargo primero")
            return False

        try:
            # Guardar datos para posible undo
            cursor = self.conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM encargos WHERE id = %s", (self.encargo_seleccionado[0],))
            self.datos_eliminados = cursor.fetchone()
            
            cursor.execute("DELETE FROM encargos WHERE id = %s", (self.encargo_seleccionado[0],))
            self.conexion.commit()
            messagebox.showinfo("Exito", "Encargo eliminado correctamente")
            return True

        except Error as e:
            messagebox.showerror("Error", f"No se pudo eliminar el encargo: {e}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def undo(self):
        if self.datos_eliminados:
            try:
                cursor = self.conexion.cursor()
                query = """
                    INSERT INTO encargos 
                    (id, nombre_conductor, apellido_conductor, pantente, fecha_reparto, producto, cantidad, repartiendo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                valores = (
                    self.datos_eliminados['id'],
                    self.datos_eliminados['nombre_conductor'],
                    self.datos_eliminados['apellido_conductor'],
                    self.datos_eliminados['pantente'],
                    self.datos_eliminados['fecha_reparto'],
                    self.datos_eliminados['producto'],
                    self.datos_eliminados['cantidad'],
                    self.datos_eliminados['repartiendo']
                )

                cursor.execute(query, valores)
                self.conexion.commit()
                return True
            except Error as e:
                messagebox.showerror("Error", f"No se pudo deshacer la operacion: {e}")
                return False
            finally:
                if 'cursor' in locals():
                    cursor.close()
        return False
    