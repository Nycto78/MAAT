import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from infrastructure.config.database import DatabaseConnector
from infrastructure.repositories.repositorio_encargos import obtener_todos_encargos
from patterns.command.command_manager import CommandManager
from patterns.command.command_encargos import (
    GuardarEncargoCommand,
    ActualizarEncargoCommand,
    EliminarEncargoCommand
)


class InterfazEncargos(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        self.conexion = DatabaseConnector.get_connection()
        self.entries = {}
        self.command_manager = CommandManager()
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
        try:
            # Obtener datos de los campos de entrada
            datos = {
                'nombre_conductor': self.entries['nombre_conductor'].get().strip(),
                'apellido_conductor': self.entries['apellido_conductor'].get().strip(),
                'patente': self.entries['patente'].get().strip().upper(),
                'fecha_reparto': self.entries['fecha_reparto'].get().strip(),
                'producto': self.entries['producto'].get().strip(),
                'cantidad': self.entries['cantidad'].get().strip(),
                'repartiendo': self.repartiendo_var.get()
            }

            # Validar campos obligatorios
            campos_obligatorios = ['nombre_conductor', 'apellido_conductor', 'patente', 'producto']
            for campo in campos_obligatorios:
                if not datos[campo]:
                    messagebox.showwarning("Advertencia", f"El campo {campo.replace('_', ' ')} es obligatorio")
                    return

            # Validar formato de fecha
            try:
                datetime.strptime(datos['fecha_reparto'], '%Y-%m-%d')
            except ValueError:
                messagebox.showwarning("Advertencia", "Formato de fecha inválido. Use YYYY-MM-DD")
                return

            # Validar cantidad
            try:
                cantidad = int(datos['cantidad'])
                if cantidad <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Advertencia", "La cantidad debe ser un número entero positivo")
                return

            # Crear y ejecutar comando para guardar
            command = GuardarEncargoCommand(self.conexion, datos)
            self.command_manager.execute(command)
            
            # Mostrar mensaje de éxito y actualizar lista
            messagebox.showinfo("Éxito", "Encargo guardado correctamente")
            self.limpiar_campos()
            self.cargar_encargos()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el encargo: {str(e)}")

    def actualizar_encargo(self):
        try:
            seleccionado = self.tree.focus()
            if not seleccionado:
                messagebox.showwarning("Advertencia", "Seleccione un encargo para actualizar")
                return
                
            item = self.tree.item(seleccionado)
            encargo_id = item['values'][0]
            
            datos = {
                'id': encargo_id,
                'nombre_conductor': self.entries['nombre_conductor'].get().strip(),
                'apellido_conductor': self.entries['apellido_conductor'].get().strip(),
                'patente': self.entries['patente'].get().strip().upper(),
                'fecha_reparto': self.entries['fecha_reparto'].get().strip(),
                'producto': self.entries['producto'].get().strip(),
                'cantidad': self.entries['cantidad'].get().strip(),
                'repartiendo': self.repartiendo_var.get()
            }
            
            # Validaciones
            campos_obligatorios = ['nombre_conductor', 'apellido_conductor', 'patente', 'producto']
            for campo in campos_obligatorios:
                if not datos[campo]:
                    messagebox.showwarning("Advertencia", f"El campo {campo.replace('_', ' ')} es obligatorio")
                    return

            try:
                datetime.strptime(datos['fecha_reparto'], '%Y-%m-%d')
            except ValueError:
                messagebox.showwarning("Advertencia", "Formato de fecha inválido. Use YYYY-MM-DD")
                return

            try:
                cantidad = int(datos['cantidad'])
                if cantidad <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Advertencia", "La cantidad debe ser un número entero positivo")
                return

            command = ActualizarEncargoCommand(self.conexion, datos)
            self.command_manager.execute(command)
            
            messagebox.showinfo("Éxito", "Encargo actualizado correctamente")
            self.cargar_encargos()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar el encargo: {str(e)}")

    def eliminar_encargo(self):
        try:
            seleccionado = self.tree.focus()
            if not seleccionado:
                messagebox.showwarning("Advertencia", "Seleccione un encargo para eliminar")
                return
                
            item = self.tree.item(seleccionado)
            encargo_id = item['values'][0]
            
            if not messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este encargo?"):
                return
                
            command = EliminarEncargoCommand(self.conexion, {'id': encargo_id})
            self.command_manager.execute(command)
            
            messagebox.showinfo("Éxito", "Encargo eliminado correctamente")
            self.limpiar_campos()
            self.cargar_encargos()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar el encargo: {str(e)}")

    def limpiar_campos(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.repartiendo_var.set(True)
        self.tree.selection_remove(self.tree.selection())

    def cargar_encargos(self):
        try:
            # Limpiar treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Obtener encargos de la base de datos
            encargos = obtener_todos_encargos(self.conexion)
            
            # Insertar datos en el treeview
            for encargo in encargos:
                conductor = f"{encargo['nombre_conductor']} {encargo['apellido_conductor']}"
                en_reparto = "Sí" if encargo['repartiendo'] else "No"
                self.tree.insert("", "end", values=(
                    encargo['id'],
                    conductor,
                    encargo['patente'],
                    encargo['fecha_reparto'],
                    encargo['producto'],
                    encargo['cantidad'],
                    en_reparto
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar encargos: {str(e)}")

    def seleccionar_encargo(self, event):
        seleccionado = self.tree.focus()
        if seleccionado:
            item = self.tree.item(seleccionado)
            valores = item['values']
            
            # Limpiar campos primero
            self.limpiar_campos()
            
            # Rellenar campos con los valores seleccionados
            nombres = valores[1].split()
            self.entries['nombre_conductor'].insert(0, nombres[0] if nombres else "")
            self.entries['apellido_conductor'].insert(0, nombres[1] if len(nombres) > 1 else "")
            self.entries['patente'].insert(0, valores[2])
            self.entries['fecha_reparto'].insert(0, valores[3])
            self.entries['producto'].insert(0, valores[4])
            self.entries['cantidad'].insert(0, valores[5])
            self.repartiendo_var.set(valores[6] == "Sí")