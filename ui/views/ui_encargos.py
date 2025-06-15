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

