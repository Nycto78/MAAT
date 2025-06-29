import tkinter as tk
from tkinter import ttk
import mysql.connector
from patterns.observer.observer_base import ObservableBase
from infrastructure.config.database import DatabaseConnector
import uuid # Para generar IDs únicos
from patterns.strategy.pricing_strategy import PricingStrategy
from patterns.strategy.iva_strategy import IVAStrategy
from patterns.strategy.discount_strategy import DiscountStrategy
from domain.entities.producto import Producto

def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="caca123",
        database="inventario",
        port= '3306'
    )

class FormularioInventario(ObservableBase):  # <- hereda directamente
    """Clase que representa el formulario de inventario, hereda de ObservableBase para notificar cambios."""
    def __init__(self, panel_principal):
        super().__init__()   # Inicializa lista de observers
        self.panel = panel_principal
        self.ultima_accion = None
        self.estilizar()
        self.crear_buscador()
        self.crear_tabla_componentes()
        self.crear_botones_accion()
        self.cargar_datos()
        self.notificar()  # Notifica al inicio para mostrar stock bajo

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

    def obtener_datos_mysql(self, filtro=""):
        conn = DatabaseConnector.get_connection()

        cursor = conn.cursor()

        if filtro:
            query = "SELECT id, nombre, categoria, cantidad, precio FROM productos WHERE LOWER(nombre) LIKE %s"
            cursor.execute(query, (f"%{filtro.lower()}%",))
        else:
            cursor.execute("SELECT id, nombre, categoria, cantidad, precio FROM productos")

        datos = cursor.fetchall()
        conn.close()

        return datos

    def notificar(self):
        data = self.obtener_datos_mysql()
        for producto in data:
            nombre = producto[1]
            cantidad = producto[3]
            if cantidad < 30:
                self.notify(f"Stock bajo: {nombre} (cantidad: {cantidad})")
        
    def cargar_datos(self, filtro=""):
        datos = self.obtener_datos_mysql(filtro)

        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        # Insertar datos
        for componente in datos:
            self.tabla.insert("", tk.END, values=componente)

    def crear_botones_accion(self):
        frame_botones = tk.Frame(self.panel)
        frame_botones.pack(pady=10)

        # Botón Agregar
        btn_agregar = tk.Button(frame_botones, text="Agregar producto", bg="green", fg="white",
            command=self.abrir_ventana_agregar)
        btn_agregar.pack(side=tk.LEFT, padx=5)

        # Botón Quitar
        btn_quitar = tk.Button(frame_botones, text="Quitar producto", bg="red", fg="white",
            command=self.quitar_producto)
        btn_quitar.pack(side=tk.LEFT, padx=5)

        # Botón Deshacer
        btn_deshacer = tk.Button(frame_botones, text="Deshacer", bg="#FF9800", fg="white",
            command=self.deshacer_ultima_accion)
        btn_deshacer.pack(side=tk.LEFT, padx=5)
        
    def abrir_ventana_agregar(self):
        ventana = tk.Toplevel(self.panel)
        ventana.title("Agregar nuevo producto")

        # Define labels y entradas primero (Error 9 y Errores 2-3)
        labels = ["Nombre", "Categoria", "Cantidad", "Precio"]
        entradas = {}

        for i, label in enumerate(labels):
            tk.Label(ventana, text=label).grid(row=i, column=0, padx=10, pady=5)
            entrada = tk.Entry(ventana)
            entrada.grid(row=i, column=1, padx=10, pady=5)
            entradas[label] = entrada

        # Selector de estrategia de precios
        ttk.Label(ventana, text="Tipo de precio:").grid(row=4, column=0, padx=10, pady=5)
        estrategia_var = tk.StringVar(value="iva")
        ttk.Radiobutton(ventana, text="Con IVA (21%)", variable=estrategia_var, value="iva").grid(row=4, column=1, sticky="w")
        ttk.Radiobutton(ventana, text="Con Descuento (10%)", variable=estrategia_var, value="descuento").grid(row=5, column=1, sticky="w")

        def confirmar():
            try:
                nombre = entradas["Nombre"].get()
                categoria = entradas["Categoria"].get()
                cantidad = int(entradas["Cantidad"].get())
                precio_base = float(entradas["Precio"].get())
                
                # Configura la estrategia de precio
                if estrategia_var.get() == "iva":
                    from patterns.strategy.iva_strategy import IVAStrategy
                    estrategia = IVAStrategy()
                else:
                    from patterns.strategy.discount_strategy import DiscountStrategy
                    estrategia = DiscountStrategy(10)  # 10% de descuento
                
                # Calcula el precio final
                precio_final = estrategia.calcular_precio(precio_base)
                
                # Inserta en la base de datos (sin especificar ID)
                conn = DatabaseConnector.get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO productos (nombre, categoria, cantidad, precio)
                    VALUES (%s, %s, %s, %s)
                """, (nombre, categoria, cantidad, precio_final))
                conn.commit()
                
                # Obtiene el ID generado automáticamente
                nuevo_id = cursor.lastrowid
                print(f"Producto agregado con ID: {nuevo_id}")
                
                self.cargar_datos()
                ventana.destroy()
                
            except Exception as e:
                tk.messagebox.showerror("Error", f"No se pudo agregar el producto:\n{e}")
            finally:
                if 'conn' in locals() and conn.is_connected():
                    cursor.close()
                    conn.close()

        btn = tk.Button(ventana, text="Agregar", command=confirmar, bg="#4CAF50", fg="white")
        btn.grid(row=6, column=0, columnspan=2, pady=10)

    def quitar_producto(self):
        item_seleccionado = self.tabla.selection()
        if not item_seleccionado:
            return

        producto = self.tabla.item(item_seleccionado)["values"]
        producto_id = producto[0] 
        

        respuesta = tk.messagebox.askyesno("Confirmar", f"¿Eliminar producto ID {producto_id}?")
        if respuesta:
            conn = DatabaseConnector.get_connection()

            cursor = conn.cursor()
            cursor.execute("DELETE FROM productos WHERE id = %s", (producto_id,))
            conn.commit()

            # Guardar acción para deshacer
            self.ultima_accion = ("eliminar", producto)

            conn.close()
            self.cargar_datos()
            
    def deshacer_ultima_accion(self):
        if not self.ultima_accion:
            tk.messagebox.showinfo("Deshacer", "No hay acción para deshacer.")
            return

        accion, datos = self.ultima_accion

        conn = DatabaseConnector.get_connection()

        cursor = conn.cursor()

        if accion == "agregar":
            cursor.execute("DELETE FROM productos WHERE id = %s", (datos,))
        elif accion == "eliminar":
            cursor.execute("""
                INSERT INTO productos (id, nombre, categoria, cantidad, precio)
                VALUES (%s, %s, %s, %s, %s)
            """, datos[:5])  # No insertamos fecha_ingreso

        conn.commit()
        conn.close()

        self.cargar_datos()
        self.ultima_accion = None

    def aplicar_filtro(self):
        texto = self.entry_busqueda.get()
        self.cargar_datos(filtro=texto)
        