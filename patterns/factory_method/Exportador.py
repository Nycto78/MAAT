
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd


class Exportador(ABC):
    @abstractmethod
    def exportar(self, charts): pass


class ExportadorPDF(Exportador):
    def exportar(self, charts):
        pdf_file = "informe_bodega.pdf"
        c = pdf_canvas.Canvas(pdf_file, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width / 2, height - 100, "Informe de Inventario y Ventas")
        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2, height - 130, f"Generado el {datetime.now().strftime('%d-%m-%Y %H:%M')}")
        c.showPage()

        for chart in charts:
            fig = chart.render()
            img_path = "temp_chart.png"
            fig.savefig(img_path, bbox_inches='tight')
            plt.close(fig)

            labels = chart.data_source.get_labels()
            values = chart.data_source.get_values()

            max_val = max(values)
            min_val = min(values)
            avg_val = sum(values) / len(values)
            total_val = sum(values)

            max_label = labels[values.index(max_val)]
            min_label = labels[values.index(min_val)]

            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 70, chart.data_source.get_title())

            c.setFont("Helvetica", 12)
            c.drawString(50, height - 100, f"🔹 Mayor valor: '{max_label}' con {max_val} unidades.")
            c.drawString(50, height - 120, f"🔹 Menor valor: '{min_label}' con {min_val} unidades.")
            c.drawString(50, height - 140, f"🔹 Promedio: {avg_val:.2f}")
            c.drawString(50, height - 160, f"🔹 Total acumulado: {total_val}")

            c.drawImage(img_path, 50, height - 680, width=500, preserveAspectRatio=True)
            c.showPage()
            os.remove(img_path)

        c.save()
        print(f"PDF exportado como {pdf_file}")


class ExportadorExcel(Exportador):
    def exportar(self, charts):
        with pd.ExcelWriter("informe_bodega.xlsx") as writer:
            for chart in charts:
                title = chart.data_source.get_title().replace(" ", "_")
                labels = chart.data_source.get_labels()
                values = chart.data_source.get_values()
                df = pd.DataFrame({"Etiqueta": labels, "Valor": values})
                df.to_excel(writer, sheet_name=title[:31], index=False)
        print("Excel exportado como informe_bodega.xlsx")


class ExportadorImagenes(Exportador):
    def exportar(self, charts):
        for i, chart in enumerate(charts, start=1):
            fig = chart.render()
            filename = f"grafico_{i}_{chart.data_source.get_title().replace(' ', '_')}.png"
            fig.savefig(filename, bbox_inches='tight')
            plt.close(fig)
            print(f"Imagen exportada: {filename}")


# --- Fábricas para integración ---
class ExportadorFactory(ABC):
    @abstractmethod
    def crear_exportador(self) -> Exportador:
        pass

class PDFExportadorFactory(ExportadorFactory):
    def crear_exportador(self) -> Exportador:
        return ExportadorPDF()

class ExcelExportadorFactory(ExportadorFactory):
    def crear_exportador(self) -> Exportador:
        return ExportadorExcel()

class ImagenExportadorFactory(ExportadorFactory):
    def crear_exportador(self) -> Exportador:
        return ExportadorImagenes()


def exportar_documento(factory: ExportadorFactory, charts):
    exportador = factory.crear_exportador()
    exportador.exportar(charts)
