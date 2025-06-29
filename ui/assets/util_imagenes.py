from PIL import ImageTk, Image
import os

def leer_imagen(nombre_archivo, size):
    try:
        ruta_base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'images'))

        path = os.path.join(ruta_base, nombre_archivo)
        return ImageTk.PhotoImage(Image.open(path).resize(size, Image.Resampling.LANCZOS))
    except FileNotFoundError:
        print(f"⚠️ Imagen no encontrada: {nombre_archivo}")
        return None
