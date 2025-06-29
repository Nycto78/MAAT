import sys
from pathlib import Path

# Añade esto AL PRINCIPIO
sys.path.insert(0, str(Path(__file__).parent))

def main():
    from ui.views.inicioUsuario import VentanaLogin
    ventana = VentanaLogin()
    ventana.mainloop()

if __name__ == "__main__":
    main()