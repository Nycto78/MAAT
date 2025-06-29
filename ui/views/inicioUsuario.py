# 📍 Archivo: mi_aplicacion/ui/views/inicio_usuario.py

import customtkinter as ctk
from tkinter import PhotoImage
import tkinter.messagebox as messagebox
import smtplib
from email.mime.text import MIMEText

from patterns.command.command_base import Comando

from ui.main_view import FormularioMaestroDesign
import os
from PIL import Image, ImageTk
from ui.assets.util_imagenes import leer_imagen


usuario_mailtrap = '02c5d9a1b22d6b'
clave_mailtrap = 'e354b8255143ee'
servidor_smtp = 'sandbox.smtp.mailtrap.io'
puerto_smtp = 2525


class IniciarSesionCommand(Comando):
    def __init__(self, correo, clave):
        self.correo = correo
        self.clave = clave
        self.exito = False

    def execute(self):
        if not self.correo or not self.clave:
            messagebox.showerror("Campos vacíos", "Por favor, completa tu correo y la contraseña.")
            return

        try:
            cuerpo_mensaje = MIMEText("¡Te has conectado correctamente!")
            cuerpo_mensaje['Subject'] = "Acceso a bodega"
            cuerpo_mensaje['From'] = "noreply@bodega.com"
            cuerpo_mensaje['To'] = self.correo

            conexion = smtplib.SMTP(servidor_smtp, puerto_smtp)
            conexion.login(usuario_mailtrap, clave_mailtrap)
            conexion.sendmail(cuerpo_mensaje['From'], [cuerpo_mensaje['To']], cuerpo_mensaje.as_string())
            conexion.quit()

            messagebox.showinfo("Correo enviado", "Correo de confirmación enviado (capturado por Mailtrap).")
        except Exception as error_envio:
            messagebox.showerror("Fallo al enviar", f"Error al enviar correo: {str(error_envio)}")
            return

        usuario = self.correo.split("@")[0]
        messagebox.showinfo("Bienvenido", f"¡Hola {usuario}!")
        self.exito = True

    def undo(self):
        pass
class VentanaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.title("Inicio Sesión")
        self.geometry("800x500")
        self.configure(fg_color="#0d4020")

        contenedor = ctk.CTkFrame(self, fg_color="#14532d", corner_radius=20)
        contenedor.pack(pady=50, padx=50, fill="both", expand=True)

        ctk.CTkLabel(contenedor, text="Inicio", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 20))

        try:
            logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', 'logo.png')
            imagen_logo = ctk.CTkImage(dark_image=Image.open(logo_path), size=(100, 100))
            etiqueta_logo = ctk.CTkLabel(contenedor, image=imagen_logo, text="")
            etiqueta_logo.pack(pady=(20, 10))
        except Exception as error:
            print("No se pudo cargar la imagen:", error)

        ctk.CTkLabel(contenedor, text="Inicia sesión", font=ctk.CTkFont(size=16)).pack(pady=(0, 10))

        self.campo_email = ctk.CTkEntry(contenedor, placeholder_text="Correo electrónico",
        fg_color="#f7e7a9", text_color="black", placeholder_text_color="grey20")
        self.campo_email.pack(pady=10, padx=20)

        self.campo_password = ctk.CTkEntry(contenedor, placeholder_text="Contraseña", show="*",
        fg_color="#f7e7a9", text_color="black", placeholder_text_color="grey20")
        self.campo_password.pack(pady=10, padx=20)

        ctk.CTkButton(contenedor, text="Entrar", command=self.ejecutar_login,
        fg_color="#f57c00", hover_color="#fb8c00", text_color="white").pack(pady=10, padx=20)

        ctk.CTkLabel(contenedor, text="¿Olvidaste tu contraseña?", font=ctk.CTkFont(size=12)).pack(pady=(0, 20))

    def ejecutar_login(self):
        correo = self.campo_email.get()
        clave = self.campo_password.get()
        comando = IniciarSesionCommand(correo, clave)
        comando.execute()

        if comando.exito:
            self.destroy()
            app = FormularioMaestroDesign()
            app.mainloop()