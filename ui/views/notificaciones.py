# 📍 Archivo: mi_aplicacion/ui/views/notificaciones.py

import tkinter as tk
from tkinter import ttk
from infrastructure.config.colores import COLOR_CUERPO_PRINCIPAL


class Notificaciones:
    def __init__(self, panel_principal, logo=None):
        self.panel = panel_principal
        self.lista_notificaciones = []
        self.visible = True

        self.barra_superior = tk.Frame(panel_principal, bg=COLOR_CUERPO_PRINCIPAL)
        self.barra_superior.pack(side=tk.TOP, fill=tk.X)

        self.barra_inferior = tk.Frame(panel_principal, bg=COLOR_CUERPO_PRINCIPAL)
        self.barra_inferior.pack(side=tk.BOTTOM, fill='both', expand=True)

        self.labelTitulo = tk.Label(
            self.barra_superior,
            text="Notificaciones del Sistema",
            fg="white",
            font=("Roboto", 26, "bold"),
            bg=COLOR_CUERPO_PRINCIPAL,
            pady=20
        )
        self.labelTitulo.pack()

        self.mostrar_notificaciones()

    def update(self, mensaje):
        if not hasattr(self, "barra_inferior") or not self.barra_inferior.winfo_exists():
            return

        if mensaje not in self.lista_notificaciones:
            self.lista_notificaciones.append(mensaje)
            self.mostrar_notificaciones()

    def mostrar_notificaciones(self):
        if not hasattr(self, "barra_inferior") or not self.barra_inferior.winfo_exists():
            return

        for widget in self.barra_inferior.winfo_children():
            widget.destroy()

        contenedor = tk.Frame(self.barra_inferior, bg=COLOR_CUERPO_PRINCIPAL)
        contenedor.pack(fill='both', expand=True)

        canvas = tk.Canvas(contenedor, bg=COLOR_CUERPO_PRINCIPAL, highlightthickness=0)
        scrollbar = ttk.Scrollbar(contenedor, orient="vertical", command=canvas.yview)
        frame_scroll = tk.Frame(canvas, bg=COLOR_CUERPO_PRINCIPAL)

        frame_scroll.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame_scroll, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for i, mensaje in enumerate(self.lista_notificaciones):
            self.crear_card(frame_scroll, mensaje, i)

    def crear_card(self, contenedor, mensaje, row):
        card = tk.Frame(
            contenedor,
            bg="white",
            bd=2,
            relief="groove",
            padx=15,
            pady=10,
            width=600
        )
        card.grid(row=row, column=0, pady=10, padx=10)
        card.grid_propagate(False)

        label = tk.Label(
            card,
            text=mensaje,
            font=("Roboto", 12),
            bg="white",
            fg="#222",
            anchor="w",
            justify="left",
            wraplength=560
        )
        label.pack(fill="both")
