import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import requests
from patterns.observer.observer_base import ObservableBase

API_URL = "http://127.0.0.1:8000/productos"

class FormularioInventario(ObservableBase):
    def __init__(self, panel_principal):
        super().__init__()

        self.panel = panel_principal
        self.ultima_accion = None

        self.estilizar()
        self.crear_buscador()
        self.crear_tabla_componentes()
        self.crear_botones_accion()
        self.cargar_datos()

    def estilizar(self):
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Roboto", 12, "bold"))
        style.configure("Treeview", font=("Roboto", 11), rowheight=25)

    def crear_buscador(self):
        frame_busqueda = tk.Frame(self.panel)
        frame_busqueda.pack(pady=10)

        tk.Label(frame_busqueda, text="Buscar componente:", font=("Roboto", 11)).pack(side=tk.LEFT, padx=5)

        self.entry_busqueda = tk.Entry(frame_busqueda, width=30)
        self.entry_busqueda.pack(side=tk.LEFT, padx=5)

        btn_buscar = tk.Button(frame_busqueda, text="Aplicar", command=self.aplicar_filtro,
                               bg="#4CAF50", fg="white", font=("Roboto", 10, "bold"))
        btn_buscar.pack(side=tk.LEFT, padx=5)

    def crear_tabla_componentes(self):
        columnas = ("ID", "Nombre", "Categoria", "Cantidad", "Precio")
        self.tabla = ttk.Treeview(self.panel, columns=columnas, show='headings')

        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=120, anchor=tk.CENTER)

        self.scrollbar = ttk.Scrollbar(self.panel, orient=tk.VERTICAL, command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=self.scrollbar.set)

        self.tabla.pack(fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def obtener_datos_api(self, filtro=""):
        try:
            response = requests.get(API_URL)
            response.raise_for_status()
            productos = response.json()
            if filtro:
                productos = [p for p in productos if filtro.lower() in p["nombre"].lower()]
            return productos
        except Exception as e:
            tk.messagebox.showerror("Error", f"No se pudo obtener datos desde la API:\n{e}")
            return []

    def notificar(self):
        data = self.obtener_datos_api()
        for producto in data:
            nombre = producto["nombre"]
            cantidad = producto["cantidad"]
            if cantidad < 30:
                self.notify(f"Stock bajo: {nombre} (cantidad: {cantidad})")

    def cargar_datos(self, filtro=""):
        datos = self.obtener_datos_api(filtro)

        for item in self.tabla.get_children():
            self.tabla.delete(item)

        for componente in datos:
            self.tabla.insert("", tk.END, values=tuple(componente.values()))

    def crear_botones_accion(self):
        frame_botones = tk.Frame(self.panel)
        frame_botones.pack(pady=10)

        btn_agregar = tk.Button(frame_botones, text="Agregar producto", bg="green", fg="white",
                                command=self.abrir_ventana_agregar)
        btn_agregar.pack(side=tk.LEFT, padx=5)

        btn_quitar = tk.Button(frame_botones, text="Quitar producto", bg="red", fg="white",
                               command=self.quitar_producto)
        btn_quitar.pack(side=tk.LEFT, padx=5)

        btn_editar = tk.Button(frame_botones, text="Editar producto", bg="#2196F3", fg="white",
                               command=self.editar_producto)
        btn_editar.pack(side=tk.LEFT, padx=5)

    def abrir_ventana_agregar(self):
        self.abrir_formulario_producto(titulo="Agregar nuevo producto", modo="agregar")

    def editar_producto(self):
        item = self.tabla.selection()
        if not item:
            tk.messagebox.showwarning("Advertencia", "Selecciona un producto para editar.")
            return

        valores = self.tabla.item(item)["values"]
        self.abrir_formulario_producto(titulo="Editar producto", modo="editar", valores=valores)

    def abrir_formulario_producto(self, titulo, modo, valores=None):
        ventana = tk.Toplevel(self.panel)
        ventana.title(titulo)

        labels = ["Nombre", "Categoria", "Cantidad", "Precio"]
        entradas = {}

        for i, label in enumerate(labels):
            tk.Label(ventana, text=label).grid(row=i, column=0, padx=10, pady=5)
            entrada = tk.Entry(ventana)
            entrada.grid(row=i, column=1, padx=10, pady=5)
            entradas[label] = entrada

        if modo == "editar" and valores:
            for i, label in enumerate(labels):
                entradas[label].insert(0, valores[i + 1])

        def confirmar():
            try:
                producto = {
                    "nombre": entradas["Nombre"].get(),
                    "categoria": entradas["Categoria"].get(),
                    "cantidad": int(entradas["Cantidad"].get()),
                    "precio": float(entradas["Precio"].get())
                }
                if modo == "agregar":
                    response = requests.post(API_URL, json=producto)
                else:
                    producto_id = valores[0]
                    response = requests.put(f"{API_URL}/{producto_id}", json=producto)
                response.raise_for_status()
                self.cargar_datos()
                ventana.destroy()
            except Exception as e:
                tk.messagebox.showerror("Error", f"Error al guardar el producto:\n{e}")

        texto_boton = "Guardar" if modo == "editar" else "Agregar"
        btn = tk.Button(ventana, text=texto_boton, command=confirmar, bg="#4CAF50", fg="white")
        btn.grid(row=len(labels), column=0, columnspan=2, pady=10)

    def quitar_producto(self):
        item = self.tabla.selection()
        if not item:
            tk.messagebox.showwarning("Advertencia", "Selecciona un producto para eliminar.")
            return

        producto = self.tabla.item(item)["values"]
        producto_id = producto[0]

        respuesta = tk.messagebox.askyesno("Confirmar", f"¿Eliminar producto ID {producto_id}?")
        if respuesta:
            try:
                response = requests.delete(f"{API_URL}/{producto_id}")
                response.raise_for_status()
                self.cargar_datos()
            except Exception as e:
                tk.messagebox.showerror("Error", f"Error al eliminar producto:\n{e}")

    def aplicar_filtro(self):
        texto = self.entry_busqueda.get()
        self.cargar_datos(filtro=texto)
