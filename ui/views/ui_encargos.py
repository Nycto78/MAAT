import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import requests

from infrastructure.repositories.repositorio_encargos import obtener_todos_encargos
from patterns.command.command_manager import CommandManager
from patterns.command.command_encargos import (
    GuardarEncargoCommand,
    ActualizarEncargoCommand,
    EliminarEncargoCommand
)

API_ENCARGOS_URL = "http://127.0.0.1:8000/encargos"

class InterfazEncargos(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        self.entries = {}
        self.command_manager = CommandManager()
        self.configurar_interfaz()
        self.crear_widgets()
        self.cargar_encargos()

    def configurar_interfaz(self):
        estilo = ttk.Style()
        estilo.theme_use('clam')
        estilo.configure("Treeview", rowheight=25, font=('Arial', 10))
        estilo.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        estilo.configure('TFrame', background="#f6a136")
        estilo.configure('TLabel', background="#f6a136", font=('Arial', 10))
        estilo.configure('TButton', font=('Arial', 10))
        estilo.configure('TEntry', font=('Arial', 10))

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
            ttk.Label(frame_form, text=texto).grid(row=i, column=0, sticky="e", pady=5)
            entry = ttk.Entry(frame_form, width=25)
            entry.grid(row=i, column=1, pady=5)
            self.entries[nombre] = entry

        self.repartiendo_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame_form, text="En reparto", variable=self.repartiendo_var).grid(row=6, column=1, sticky="w", pady=5)

        frame_botones = ttk.Frame(frame_form)
        frame_botones.grid(row=7, column=0, columnspan=2, pady=10)
        ttk.Button(frame_botones, text="Guardar", command=self.guardar_encargo).grid(row=0, column=0, padx=5)
        ttk.Button(frame_botones, text="Actualizar", command=self.actualizar_encargo).grid(row=0, column=1, padx=5)
        ttk.Button(frame_botones, text="Eliminar", command=self.eliminar_encargo).grid(row=0, column=2, padx=5)
        ttk.Button(frame_botones, text="Limpiar", command=self.limpiar_campos).grid(row=0, column=3, padx=5)

        frame_lista = ttk.Frame(self, padding="10")
        frame_lista.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        columns = ("ID", "Conductor", "Patente", "Fecha Reparto", "Producto", "Cantidad", "En reparto")
        self.tree = ttk.Treeview(frame_lista, columns=columns, show="headings", height=20)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_encargo)

    def cargar_encargos(self):
        try:
            response = requests.get(API_ENCARGOS_URL)
            response.raise_for_status()
            encargos = response.json()
            self.tree.delete(*self.tree.get_children())
            for encargo in encargos:
                fila = (
                    encargo["id"],
                    f"{encargo['nombre_conductor']} {encargo['apellido_conductor']}",
                    encargo["patente"],
                    encargo["fecha_reparto"],
                    encargo["producto"],
                    encargo["cantidad"],
                    "Sí" if encargo["repartiendo"] else "No"
                )
                self.tree.insert("", "end", values=fila)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los encargos:\n{e}")

    def obtener_datos_formulario(self):
        return {
            "nombre_conductor": self.entries["nombre_conductor"].get(),
            "apellido_conductor": self.entries["apellido_conductor"].get(),
            "patente": self.entries["patente"].get(),
            "fecha_reparto": self.entries["fecha_reparto"].get(),
            "producto": self.entries["producto"].get(),
            "cantidad": int(self.entries["cantidad"].get()),
            "repartiendo": self.repartiendo_var.get()
        }

    def guardar_encargo(self):
        try:
            data = self.obtener_datos_formulario()
            response = requests.post(API_ENCARGOS_URL, json=data)
            response.raise_for_status()
            self.cargar_encargos()
            self.limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el encargo:\n{e}")

    def actualizar_encargo(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Advertencia", "Selecciona un encargo para actualizar.")
            return
        try:
            encargo_id = self.tree.item(item)["values"][0]
            data = self.obtener_datos_formulario()
            response = requests.put(f"{API_ENCARGOS_URL}/{encargo_id}", json=data)
            response.raise_for_status()
            self.cargar_encargos()
            self.limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el encargo:\n{e}")

    def eliminar_encargo(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Advertencia", "Selecciona un encargo para eliminar.")
            return
        try:
            encargo_id = self.tree.item(item)["values"][0]
            response = requests.delete(f"{API_ENCARGOS_URL}/{encargo_id}")
            response.raise_for_status()
            self.cargar_encargos()
            self.limpiar_campos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el encargo:\n{e}")

    def seleccionar_encargo(self, event):
        item = self.tree.selection()
        if not item:
            return
        valores = self.tree.item(item)["values"]
        nombre, apellido = valores[1].split(" ", 1)
        self.entries["nombre_conductor"].delete(0, tk.END)
        self.entries["nombre_conductor"].insert(0, nombre)
        self.entries["apellido_conductor"].delete(0, tk.END)
        self.entries["apellido_conductor"].insert(0, apellido)
        self.entries["patente"].delete(0, tk.END)
        self.entries["patente"].insert(0, valores[2])
        self.entries["fecha_reparto"].delete(0, tk.END)
        self.entries["fecha_reparto"].insert(0, valores[3])
        self.entries["producto"].delete(0, tk.END)
        self.entries["producto"].insert(0, valores[4])
        self.entries["cantidad"].delete(0, tk.END)
        self.entries["cantidad"].insert(0, valores[5])
        self.repartiendo_var.set(valores[6] == "Sí")

    def limpiar_campos(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.repartiendo_var.set(True)
