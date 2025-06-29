# MAAT/view/formularios/formulario_encargos.py

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from view.componentes.tabla_datos import TablaDatos
from infrastructure.repositories.repositorio_encargos import obtener_todos_encargos
from patterns.command.command_manager import CommandManager
from patterns.command.command_encargos import (
    GuardarEncargoCommand,
    ActualizarEncargoCommand,
    EliminarEncargoCommand
)

class FormularioEncargos(ttk.Frame):
    def __init__(self, parent, conexion):
        super().__init__(parent)
        self.conexion = conexion
        self.command_manager = CommandManager()
        
        self._configurar_estilos()
        self._inicializar_ui()
        self._cargar_datos_iniciales()
    
    def _configurar_estilos(self):
        """Configura los estilos visuales."""
        self.estilo = ttk.Style()
        
        # Colores base
        self.color_fondo = "#f6a136"
        self.color_encabezado = "#3A3A3A"
        self.color_fila = "#fea13d"
        self.color_seleccion = "#0078D7"
        
        # Configurar estilo de la tabla
        estilo_tabla = {
            "general": {
                "background": self.color_fila,
                "fieldbackground": self.color_fondo,
                "foreground": "black",
                "font": ('Arial', 10)
            },
            "encabezado": {
                "background": self.color_encabezado,
                "foreground": "white",
                "font": ('Arial', 10, 'bold'),
                "relief": "flat"
            }
        }
        
        # Configuración de columnas para la tabla
        self.columnas_tabla = [
            {"nombre": "ID", "ancho": 50, "anchor": "center"},
            {"nombre": "Conductor", "ancho": 150},
            {"nombre": "Patente", "ancho": 80},
            {"nombre": "Fecha Reparto", "ancho": 100, "anchor": "center"},
            {"nombre": "Producto", "ancho": 120},
            {"nombre": "Cantidad", "ancho": 70, "anchor": "center"},
            {"nombre": "En reparto", "ancho": 90, "anchor": "center"}
        ]
        
        return estilo_tabla
    
    def _inicializar_ui(self):
        """Inicializa los componentes de la interfaz."""
        # Frame principal con grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Frame de formulario (izquierda)
        frame_form = ttk.Frame(self, padding=10)
        frame_form.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Frame de tabla (derecha)
        frame_tabla = ttk.Frame(self)
        frame_tabla.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Diccionario para almacenar los entries
        self.entries = {}
        
        # Campos del formulario
        campos = [
            ("Nombre Conductor:", "nombre_conductor"),
            ("Apellido Conductor:", "apellido_conductor"),
            ("Patente:", "patente"),
            ("Fecha Reparto (YYYY-MM-DD):", "fecha_reparto"),
            ("Producto:", "producto"),
            ("Cantidad:", "cantidad")
        ]
        
        # Crear campos de entrada
        for i, (texto, nombre) in enumerate(campos):
            ttk.Label(frame_form, text=texto).grid(row=i, column=0, sticky="e", pady=5, padx=5)
            entry = ttk.Entry(frame_form, width=25)
            entry.grid(row=i, column=1, pady=5, padx=5)
            self.entries[nombre] = entry
        
        # Checkbutton para "En reparto"
        self.repartiendo_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            frame_form, 
            text="En reparto", 
            variable=self.repartiendo_var
        ).grid(row=len(campos), column=1, sticky="w", pady=5)
        
        # Frame de botones
        frame_botones = ttk.Frame(frame_form)
        frame_botones.grid(row=len(campos)+1, column=0, columnspan=2, pady=10)
        
        # Botones CRUD
        ttk.Button(frame_botones, text="Guardar", command=self._guardar_encargo).grid(row=0, column=0, padx=5)
        ttk.Button(frame_botones, text="Actualizar", command=self._actualizar_encargo).grid(row=0, column=1, padx=5)
        ttk.Button(frame_botones, text="Eliminar", command=self._eliminar_encargo).grid(row=0, column=2, padx=5)
        ttk.Button(frame_botones, text="Limpiar", command=self._limpiar_campos).grid(row=0, column=3, padx=5)
        
        # Crear tabla de datos
        self.tabla = TablaDatos(
            frame_tabla,
            config_columnas=self.columnas_tabla,
            altura=20,
            estilo_personalizado=self._configurar_estilos()
        )
        self.tabla.pack(fill="both", expand=True)
        
        # Configurar eventos
        self.tabla.configurar_evento("seleccion", self._on_seleccion_tabla)
    
    def _cargar_datos_iniciales(self):
        """Carga los datos iniciales en la tabla."""
        encargos = obtener_todos_encargos(self.conexion)
        datos_para_tabla = []
        
        for encargo in encargos:
            datos_para_tabla.append({
                "ID": encargo['id'],
                "Conductor": f"{encargo['nombre_conductor']} {encargo['apellido_conductor']}",
                "Patente": encargo['patente'],
                "Fecha Reparto": encargo['fecha_reparto'],
                "Producto": encargo['producto'],
                "Cantidad": encargo['cantidad'],
                "En reparto": "Sí" if encargo['repartiendo'] else "No"
            })
        
        self.tabla.cargar_datos(datos_para_tabla)
    
    def _on_seleccion_tabla(self, item):
        """Manejador de selección en la tabla."""
        if item:
            # Separar nombre y apellido del conductor
            nombres = item['Conductor'].split()
            
            self._limpiar_campos()
            
            self.entries['nombre_conductor'].insert(0, nombres[0] if nombres else "")
            self.entries['apellido_conductor'].insert(0, nombres[1] if len(nombres) > 1 else "")
            self.entries['patente'].insert(0, item['Patente'])
            self.entries['fecha_reparto'].insert(0, item['Fecha Reparto'])
            self.entries['producto'].insert(0, item['Producto'])
            self.entries['cantidad'].insert(0, item['Cantidad'])
            self.repartiendo_var.set(item['En reparto'] == "Sí")
    
    def _limpiar_campos(self):
        """Limpia todos los campos del formulario."""
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.repartiendo_var.set(True)
        self.tabla.limpiar_seleccion()
    
    def _validar_formulario(self, datos):
        """Valida los datos del formulario."""
        # Validar campos obligatorios
        campos_obligatorios = ['nombre_conductor', 'apellido_conductor', 'patente', 'producto']
        for campo in campos_obligatorios:
            if not datos.get(campo, '').strip():
                messagebox.showwarning("Advertencia", f"El campo {campo.replace('_', ' ')} es obligatorio")
                return False
        
        # Validar formato de fecha
        try:
            datetime.strptime(datos['fecha_reparto'], '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Advertencia", "Formato de fecha inválido. Use YYYY-MM-DD")
            return False
        
        # Validar cantidad
        try:
            cantidad = int(datos['cantidad'])
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Advertencia", "La cantidad debe ser un número entero positivo")
            return False
        
        return True
    
    def _guardar_encargo(self):
        """Guarda un nuevo encargo."""
        try:
            datos = {
                'nombre_conductor': self.entries['nombre_conductor'].get().strip(),
                'apellido_conductor': self.entries['apellido_conductor'].get().strip(),
                'patente': self.entries['patente'].get().strip().upper(),
                'fecha_reparto': self.entries['fecha_reparto'].get().strip(),
                'producto': self.entries['producto'].get().strip(),
                'cantidad': self.entries['cantidad'].get().strip(),
                'repartiendo': self.repartiendo_var.get()
            }
            
            if not self._validar_formulario(datos):
                return
            
            command = GuardarEncargoCommand(self.conexion, datos)
            self.command_manager.execute(command)
            
            messagebox.showinfo("Éxito", "Encargo guardado correctamente")
            self._limpiar_campos()
            self._cargar_datos_iniciales()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el encargo: {str(e)}")
    
    def _actualizar_encargo(self):
        """Actualiza un encargo existente."""
        try:
            item = self.tabla.obtener_seleccion()
            if not item:
                messagebox.showwarning("Advertencia", "Seleccione un encargo para actualizar")
                return
            
            datos = {
                'id': item['ID'],
                'nombre_conductor': self.entries['nombre_conductor'].get().strip(),
                'apellido_conductor': self.entries['apellido_conductor'].get().strip(),
                'patente': self.entries['patente'].get().strip().upper(),
                'fecha_reparto': self.entries['fecha_reparto'].get().strip(),
                'producto': self.entries['producto'].get().strip(),
                'cantidad': self.entries['cantidad'].get().strip(),
                'repartiendo': self.repartiendo_var.get()
            }
            
            if not self._validar_formulario(datos):
                return
            
            command = ActualizarEncargoCommand(self.conexion, datos)
            self.command_manager.execute(command)
            
            messagebox.showinfo("Éxito", "Encargo actualizado correctamente")
            self._cargar_datos_iniciales()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar el encargo: {str(e)}")
    
    def _eliminar_encargo(self):
        """Elimina un encargo."""
        try:
            item = self.tabla.obtener_seleccion()
            if not item:
                messagebox.showwarning("Advertencia", "Seleccione un encargo para eliminar")
                return
            
            if not messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este encargo?"):
                return
            
            command = EliminarEncargoCommand(self.conexion, {'id': item['ID']})
            self.command_manager.execute(command)
            
            messagebox.showinfo("Éxito", "Encargo eliminado correctamente")
            self._limpiar_campos()
            self._cargar_datos_iniciales()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar el encargo: {str(e)}")