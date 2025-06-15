# 📍 Archivo: mi_aplicacion/ui/views/form_graficas.py

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from infrastructure.config.colores import COLOR_CUERPO_PRINCIPAL
from patterns.factory_method.Exportador import exportar_documento, PDFExportadorFactory, ExcelExportadorFactory, ImagenExportadorFactory
from patterns.bridge.chart_bridge import BarChart, SalesData, InventoryData


# Simulated data (puedes reemplazar esto con tu origen real)
sales_data = {"A": 120, "B": 150, "C": 90}
inventory_data = {"A": 30, "B": 45, "C": 60}


class Formulario_graficas:
    def __init__(self, panel_principal, imagen):
        self.panel_principal = panel_principal
        self.imagen = imagen
        self.barra_superior = tk.Frame(panel_principal, bg=COLOR_CUERPO_PRINCIPAL)
        self.barra_superior.pack(side=tk.TOP, fill=tk.X, expand=False)

        self.barra_inferior = tk.Frame(panel_principal, bg=COLOR_CUERPO_PRINCIPAL)
        self.barra_inferior.pack(side=tk.LEFT, fill='both', expand=True)

        self.panel_botones = tk.Frame(panel_principal, bg=COLOR_CUERPO_PRINCIPAL)
        self.panel_botones.pack(side=tk.RIGHT, fill="y", padx=10, pady=10)

        self.labelTitulo = tk.Label(
            self.barra_superior, 
            text="Dashboard: Inventario y Ventas",
            fg="#222d33", 
            font=("Roboto", 26), 
            bg=COLOR_CUERPO_PRINCIPAL
        )
        self.labelTitulo.pack(side=tk.TOP, fill='both', expand=True)

        self.charts = [
            BarChart(SalesData(sales_data)),
            BarChart(InventoryData(inventory_data))
        ]

        self.mostrar_graficos()
        self.crear_botones_exportacion()

    def mostrar_graficos(self):
        for chart in self.charts:
            fig = chart.render()
            canvas = FigureCanvasTkAgg(fig, master=self.barra_inferior)
            canvas.draw()
            canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH, pady=10)

    def crear_botones_exportacion(self):
        btn_pdf = tk.Button(self.panel_botones, text="Exportar PDF", command=lambda: exportar_documento(PDFExportadorFactory(), self.charts))
        btn_pdf.pack(pady=10, fill="x")

        btn_excel = tk.Button(self.panel_botones, text="Exportar Excel", command=lambda: exportar_documento(ExcelExportadorFactory(), self.charts))
        btn_excel.pack(pady=10, fill="x")

        btn_img = tk.Button(self.panel_botones, text="Exportar Imágenes", command=lambda: exportar_documento(ImagenExportadorFactory(), self.charts))
        btn_img.pack(pady=10, fill="x")
