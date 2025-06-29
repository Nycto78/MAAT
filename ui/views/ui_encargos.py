import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from infrastructure.config.database import DatabaseConnector
from infrastructure.repositories.repositorio_encargos import obtener_todos_encargos, guardar_encargo
from patterns.command.command_manager import CommandManager
from patterns.command.command_encargos import (
    GuardarEncargoCommand,
    ActualizarEncargoCommand,
    EliminarEncargoCommand
)


class InterfazEncargos(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill="both", expand=True)
        self.entries = {}
        self.encargo_seleccionado_id = None
        self.configurar_interfaz()
        self.crear_widgets()
        self.cargar_encargos()
    

    def conectar_db(self):
        try:
            conexion = mysql.connector.connect(
                host='localhost',
                user='root',
                password='Agu_!123',
                database='inventario',
            )
            print("Conexion creada:", conexion)
            return conexion
        except Error as e:
            print(f"Error de conexion: {e}")
            messagebox.showerror("Error de conexion", f"No se pudo conectar a MySQL: {e}")
            return None

    def configurar_interfaz(self):
        estilo = ttk.Style()
        estilo.theme_use('clam')
        
        color_fondo = "#f6a136"
        color_encabezado = "#3A3A3A"
        color_fila_impar ="#fea13d" 
        color_seleccion = "#0078D7"
        color_texto_encabezado = "white"
        color_borde = "#C0C0C0"

        estilo.configure("Treeview",
                        background=color_fila_impar,
                        foreground="black",
                        rowheight=25,
                        fieldbackground=color_fondo,
                        bordercolor="black",
                        lightcolor=color_borde,
                        darkcolor=color_borde,
                        font=('Arial', 10))

        estilo.configure("Treeview.Heading",
                        background=color_encabezado,
                        foreground=color_texto_encabezado,
                        padding=5,
                        font=('Arial', 10, 'bold'),
                        relief="flat")

        estilo.map('Treeview',
                background=[('selected', color_seleccion)],
                foreground=[('selected', 'white')])

        estilo.configure('TFrame', background=color_fondo)
        estilo.configure('TLabel', background=color_fondo, font=('Arial', 10))
        estilo.configure('TButton', font=('Arial', 10), background='#E0E0E0')
        estilo.configure('TEntry', font=('Arial', 10))
        
        color_base = '#30a56f'
        color_hover = '#248055' 

        estilo.configure('Colores.TButton', 
                        background=color_base,
                        foreground='white',
                        bordercolor=color_hover,
                        borderradius=12)

        estilo.configure('Blanco.TLabel', 
                        font=('Arial', 10, 'bold'),
                        foreground='white',  
                        background=color_fondo,
                        padding=5,
                        relief='flat')

        estilo.map('Colores.TButton', 
                background=[('active', color_hover)],
                foreground=[('active', 'white')])

    def crear_widgets(self):
        frame_form = ttk.Frame(self, padding="10")
        frame_form.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        campos = [
        ("Nombre Conductor:", "nombre_conductor"),
        ("Apellido Conductor:", "apellido_conductor"),
        ("Patente:", "patente"),
        ("Fecha Reparto (YYYY-MM-DD):", "fecha_reparto"),
        ("Producto:", "producto"),
        ("Cantidad:", "cantidad")
        ]

        for i, (texto, nombre) in enumerate(campos):
            ttk.Label(frame_form, text=texto, style='Blanco.TLabel').grid(row=i, column=0, sticky="e", pady=8, padx=5)
            entry = ttk.Entry(frame_form, width=25)
            entry.grid(row=i, column=1, pady=5)
            self.entries[nombre] = entry

        self.repartiendo_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame_form, text="En reparto", variable=self.repartiendo_var).grid(row=6, column=1, sticky="w", pady=5)

        frame_botones = ttk.Frame(frame_form)
        frame_botones.grid(row=7, column=0, columnspan=2, pady=10)

        ttk.Button(frame_botones, text="Guardar", style='Colores.TButton', command=self.guardar_encargo).grid(row=0, column=0, padx=5)
        ttk.Button(frame_botones, text="Actualizar", style='Colores.TButton', command=self.actualizar_encargo).grid(row=0, column=1, padx=5)
        ttk.Button(frame_botones, text="Eliminar", style='Colores.TButton', command=self.eliminar_encargo).grid(row=0, column=2, padx=5)
        ttk.Button(frame_botones, text="Limpiar", style='Colores.TButton', command=self.limpiar_campos).grid(row=0, column=3, padx=5)

        frame_lista = ttk.Frame(self, padding="10")
        frame_lista.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        columns = ("ID", "Conductor", "Patente", "Fecha Reparto", "Producto", "Cantidad", "En reparto")
        self.tree = ttk.Treeview(frame_lista, columns=columns, show="headings", height=20)

        anchos = [30, 70, 70, 60, 70, 70, 100]
        for col, ancho in zip(columns, anchos):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=ancho, anchor="center")

        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_encargo)

    # Métodos CRUD implementados
    def guardar_encargo(self):
        """Guarda un nuevo encargo"""
        try:
            # Validar campos
            campos_requeridos = ['nombre_conductor', 'apellido_conductor', 
                                'patente', 'fecha_reparto', 'producto', 'cantidad']
            for campo in campos_requeridos:
                if not self.entries[campo].get().strip():
                    raise ValueError(f"El campo {campo.replace('_', ' ')} es requerido")
            
            # Validar fecha
            try:
                datetime.strptime(self.entries['fecha_reparto'].get(), '%Y-%m-%d')
            except ValueError:
                raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD")
            
            # Validar cantidad
            try:
                cantidad = int(self.entries['cantidad'].get())
                if cantidad <= 0:
                    raise ValueError
            except ValueError:
                raise ValueError("La cantidad debe ser un número entero positivo")
            
            # Preparar datos
            datos = {
                'nombre_conductor': self.entries['nombre_conductor'].get(),
                'apellido_conductor': self.entries['apellido_conductor'].get(),
                'patente': self.entries['patente'].get().upper(),
                'fecha_reparto': self.entries['fecha_reparto'].get(),
                'producto': self.entries['producto'].get(),
                'cantidad': cantidad,
                'repartiendo': self.repartiendo_var.get()
            }
            
            # Guardar en la base de datos
            if guardar_encargo(datos):
                messagebox.showinfo("Éxito", "Encargo guardado correctamente")
                self.limpiar_campos()
                self.cargar_encargos()  # Actualizar tabla
            else:
                messagebox.showerror("Error", "No se pudo guardar el encargo")
                
        except ValueError as ve:
            messagebox.showwarning("Validación", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar:\n{str(e)}")
            
    def actualizar_encargo(self):
        """Actualiza el encargo seleccionado"""
        try:
            if not self.encargo_seleccionado_id:
                messagebox.showwarning("Advertencia", "Seleccione un encargo para actualizar")
                return
                
            # Validar campos
            if not all([self.entries[field].get().strip() for field in ['nombre_conductor', 'apellido_conductor', 'patente', 'producto']]):
                messagebox.showwarning("Advertencia", "Complete todos los campos obligatorios")
                return
                
            # Preparar datos
            datos = {
                'id': self.encargo_seleccionado_id,
                'nombre_conductor': self.entries['nombre_conductor'].get().strip(),
                'apellido_conductor': self.entries['apellido_conductor'].get().strip(),
                'patente': self.entries['patente'].get().strip().upper(),
                'fecha_reparto': self.entries['fecha_reparto'].get().strip(),
                'producto': self.entries['producto'].get().strip(),
                'cantidad': int(self.entries['cantidad'].get()),
                'repartiendo': self.repartiendo_var.get()
            }
            
            # Actualizar en la base de datos
            if self.actualizar_encargo_en_db(datos):
                messagebox.showinfo("Éxito", "Encargo actualizado correctamente")
                self.cargar_encargos()
                self.limpiar_campos()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el encargo")
                
        except ValueError as ve:
            messagebox.showerror("Error", f"Datos inválidos: {str(ve)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar: {str(e)}")
            
    def actualizar_encargo_en_db(self, datos):
        """Actualiza un encargo en la base de datos"""
        conn = None
        try:
            conn = DatabaseConnector.get_connection()
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
                datos['nombre_conductor'],
                datos['apellido_conductor'],
                datos['patente'],
                datos['fecha_reparto'],
                datos['producto'],
                datos['cantidad'],
                datos['repartiendo'],
                datos['id']
            ))
            
            conn.commit()
            return cursor.rowcount > 0  # Retorna True si se actualizó alguna fila
            
        except Exception as e:
            print(f"Error al actualizar en DB: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
        
    def actualizar_tabla(self):
        """Actualiza la tabla con los datos más recientes de la base de datos"""
        try:
            # Limpiar tabla existente
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Obtener datos actualizados
            from infrastructure.repositories.repositorio_encargos import obtener_todos_encargos
            encargos = obtener_todos_encargos()
            
            # Insertar nuevos datos
            for encargo in encargos:
                self.tree.insert("", "end", values=(
                    encargo['id'],
                    f"{encargo['nombre_conductor']} {encargo['apellido_conductor']}",
                    encargo['patente'],
                    encargo['fecha_reparto'].strftime('%Y-%m-%d') if encargo['fecha_reparto'] else '',
                    encargo['producto'],
                    encargo['cantidad'],
                    "Sí" if encargo['repartiendo'] else "No"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar la tabla:\n{str(e)}")
        
    def eliminar_encargo(self):
        try:
            # Verificar selección
            seleccionado = self.tree.focus()
            if not seleccionado:
                messagebox.showwarning("Advertencia", "Por favor seleccione un encargo para eliminar")
                return

            # Obtener ID del encargo seleccionado
            item = self.tree.item(seleccionado)
            encargo_id = item['values'][0]
            
            # Confirmar eliminación
            if not messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este encargo?"):
                return

            # Eliminar de la base de datos
            if self.eliminar_encargo_de_db(encargo_id):
                messagebox.showinfo("Éxito", "Encargo eliminado correctamente")
                self.limpiar_campos()
                self.cargar_encargos()  # Refrescar la tabla
            else:
                messagebox.showerror("Error", "No se pudo eliminar el encargo")

        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar el encargo:\n{str(e)}")
            
    def eliminar_encargo_de_db(self, encargo_id):
        """Elimina un encargo de la base de datos"""
        conn = None
        try:
            conn = DatabaseConnector.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM encargos WHERE id = %s", (encargo_id,))
            conn.commit()
            return cursor.rowcount > 0  # Retorna True si se eliminó alguna fila
            
        except Exception as e:
            print(f"Error al eliminar de DB: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    def limpiar_campos(self):
        """Limpia todos los campos y restablece los colores"""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
            entry.config(background='white')  # Restablecer color
        
        self.repartiendo_var.set(True)
        self.encargo_seleccionado_id = None
        self.tree.selection_remove(self.tree.selection())

    def cargar_encargos(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            encargos = obtener_todos_encargos()  # Usar el nuevo nombre
            
            # Insertar nuevos datos
            for encargo in encargos:
                self.tree.insert("", "end", values=(
                    encargo['id'],
                    f"{encargo['nombre_conductor']} {encargo['apellido_conductor']}",
                    encargo['patente'],
                    encargo['fecha_reparto'].strftime('%Y-%m-%d') if encargo['fecha_reparto'] else '',
                    encargo['producto'],
                    encargo['cantidad'],
                    "Sí" if encargo['repartiendo'] else "No"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar los encargos:\n{str(e)}")

def seleccionar_encargo(self, event):
    """Autocompleta el formulario al seleccionar un encargo de la tabla"""
    try:
        # Obtener el item seleccionado
        seleccionado = self.tree.focus()
        if not seleccionado:
            return
            
        item = self.tree.item(seleccionado)
        valores = item['values']
        
        # Guardar el ID del encargo seleccionado
        self.encargo_seleccionado_id = valores[0]
        
        # Limpiar los campos antes de autocompletar
        self.limpiar_campos()
        
        # Extraer nombres (asumiendo formato "Nombre Apellido")
        nombre_completo = valores[1].split()
        nombre = nombre_completo[0] if len(nombre_completo) > 0 else ""
        apellido = nombre_completo[1] if len(nombre_completo) > 1 else ""
        
        # Autocompletar los campos del formulario
        self.entries['nombre_conductor'].insert(0, nombre)
        self.entries['apellido_conductor'].insert(0, apellido)
        self.entries['patente'].insert(0, valores[2])
        self.entries['fecha_reparto'].insert(0, valores[3])
        self.entries['producto'].insert(0, valores[4])
        self.entries['cantidad'].insert(0, valores[5])
        
        # Establecer el estado de "En reparto"
        self.repartiendo_var.set(valores[6] == "Sí")
        
        # Cambiar color de fondo para indicar selección
        for entry in self.entries.values():
            entry.config(background='#F0F8FF')  # Color azul claro
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar datos del encargo:\n{str(e)}")