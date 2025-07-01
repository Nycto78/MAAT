import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk
import sys
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Esto asegura que se puedan importar módulos como infrastructure, ui, etc.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from infrastructure.config.colores import (
    COLOR_BARRA_SUPERIOR,
    COLOR_MENU_LATERAL,
    COLOR_CUERPO_PRINCIPAL,
    COLOR_MENU_CURSOR_ENCIMA
)

from ui.utils.util_ventana import centrar_ventana as util_ventana
from ui.assets import util_imagenes as util_img
from ui.views.form_graficas import Formulario_graficas
from ui.views.inventario_pruebas import FormularioInventario
from ui.views.notificaciones import Notificaciones
from ui.views.ui_encargos import InterfazEncargos
class FormularioMaestroDesign(tk.Tk):
     
    def __init__(self):
        super().__init__()

        # Ruta base segura para imágenes
        base_path = os.path.join(os.path.dirname(__file__), '..', 'imagenes')

        # Cargar imágenes con manejo de errores
        self.logo = util_img.leer_imagen("logo.png", (100, 100))

        self.perfil = util_img.leer_imagen("Perfil.png", (100, 100))
        self.img_sitio_construccion = util_img.leer_imagen("sitio_construccion.png", (200, 200))

        icono_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', 'icono2.png'))

        if os.path.exists(icono_path):
            icono_img = Image.open(icono_path).resize((120, 100))
            self.icono_tk = ImageTk.PhotoImage(icono_img)
        else:
            self.icono_tk = None
            print(f"⚠️ Imagen no encontrada: {icono_path}")

        self.config_window()
        self.paneles()
        self.controles_barra_superior()
        self.controles_menu_lateral()
        self.formulario = None
        self.notificaciones = None

    def config_window(self):
        self.title('MAAT GUI')
        w, h = 1024, 600
        self.geometry(f"{w}x{h}+0+0")
        util_ventana(self, w, h)


    def paneles(self):
        self.barra_superior = tk.Frame(self, bg=COLOR_BARRA_SUPERIOR, height=50)
        self.barra_superior.pack(side=tk.TOP, fill='both')

        self.menu_lateral = tk.Frame(self, bg=COLOR_MENU_LATERAL, width=150)
        self.menu_lateral.pack(side=tk.LEFT, fill='both', expand=False)

        self.cuerpo_principal = tk.Frame(self, bg=COLOR_CUERPO_PRINCIPAL, width=150)
        self.cuerpo_principal.pack(side=tk.RIGHT, fill='both', expand=True)

    def controles_barra_superior(self):
        if self.icono_tk:
            self.labelIcono = tk.Label(self.barra_superior, image=self.icono_tk, bg=COLOR_BARRA_SUPERIOR)
            self.labelIcono.pack(side=tk.LEFT, padx=(10, 0))

        font_awesome = font.Font(family='FontAwesome', size=12)

        self.buttonMenuLateral = tk.Button(self.barra_superior, text="\uf0c9", font=font_awesome,
                                           command=self.toggle_panel, bd=0, bg=COLOR_BARRA_SUPERIOR, fg="white")
        self.buttonMenuLateral.pack(side=tk.LEFT)

        self.labelTitulo = tk.Label(self.barra_superior, text="amonsalve@gmail.com", fg="#fff",
                                    font=("Roboto", 10), bg=COLOR_BARRA_SUPERIOR, padx=10, width=20)
        self.labelTitulo.pack(side=tk.RIGHT)

    def controles_menu_lateral(self):
        ancho_menu = 20
        alto_menu = 2
        font_awesome = font.Font(family='FontAwesome', size=15)

        self.buttonDashBoard = tk.Button(self.menu_lateral)
        self.buttonProfile = tk.Button(self.menu_lateral)
        self.buttonPicture = tk.Button(self.menu_lateral)
        self.buttonInfo = tk.Button(self.menu_lateral)
        self.buttonSettings = tk.Button(self.menu_lateral)

        buttons_info = [
            ("Inventario", "\uf109", self.buttonDashBoard, self.abrir_panel_graficas),
            ("Estadistica", "\uf681", self.buttonProfile, self.abrir_panel_en_construccion),
            ("Perfil", "\uf007", self.buttonPicture, self.abrir_panel_en_construccion),
            ("Encargos", "\uf0d1", self.buttonInfo, self.abrir_panel_encargos),  # ← este
            ("Notificaciones", "\uf013", self.buttonSettings, self.abrir_panel_notificaciones)
        ]

        for text, icon, button, comando in buttons_info:
            self.configurar_boton_menu(button, text, icon, font_awesome, ancho_menu, alto_menu, comando)

    def configurar_boton_menu(self, button, text, icon, font_awesome, ancho_menu, alto_menu, comando):
        button.config(text=f"  {icon}    {text}", anchor="w", font=font_awesome,
                      bd=0, bg=COLOR_MENU_LATERAL, fg="white", width=ancho_menu, height=alto_menu, command=comando)
        button.pack(side=tk.TOP)
        self.bind_hover_events(button)

    def bind_hover_events(self, button):
        button.bind("<Enter>", lambda event: self.on_enter(event, button))
        button.bind("<Leave>", lambda event: self.on_leave(event, button))

    def on_enter(self, event, button):
        button.config(bg=COLOR_MENU_CURSOR_ENCIMA, fg='white')

    def on_leave(self, event, button):
        button.config(bg=COLOR_MENU_LATERAL, fg='white')

    def toggle_panel(self):
        if self.menu_lateral.winfo_ismapped():
            self.menu_lateral.pack_forget()
        else:
            self.menu_lateral.pack(side=tk.LEFT, fill='y')


    def abrir_panel_encargos(self):
        self.limpiar_panel(self.cuerpo_principal)
        self.formulario = InterfazEncargos(self.cuerpo_principal)
        self.formulario.pack(fill="both", expand=True)

        # Si notificaciones ya está, conectar
        if self.notificaciones:
            self.formulario.attach(self.notificaciones)
        self.formulario.notificar()
    

    def abrir_panel_en_construccion(self):
        self.limpiar_panel(self.cuerpo_principal)
        Formulario_graficas(self.cuerpo_principal, self.img_sitio_construccion)

    def abrir_panel_notificaciones(self):
        self.limpiar_panel(self.cuerpo_principal)
        self.notificaciones = Notificaciones(self.cuerpo_principal)

        if self.formulario:
            self.formulario.attach(self.notificaciones)
            self.formulario.notificar()

    def abrir_panel_graficas(self):
        self.limpiar_panel(self.cuerpo_principal)
        self.formulario = FormularioInventario(self.cuerpo_principal)

        if self.notificaciones:
            self.formulario.attach(self.notificaciones)
            self.formulario.notificar()

    def limpiar_panel(self, panel):
        for widget in panel.winfo_children():
            if isinstance(widget, Notificaciones):
                widget.visible = False
            widget.destroy()
