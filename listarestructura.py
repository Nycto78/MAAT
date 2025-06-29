import os

def listar_directorios(ruta, prefijo=""):
    for nombre in os.listdir(ruta):
        ruta_completa = os.path.join(ruta, nombre)
        print(prefijo + "|-- " + nombre)
        if os.path.isdir(ruta_completa):
            listar_directorios(ruta_completa, prefijo + "    ")

listar_directorios(".")
