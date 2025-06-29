# 📍 Archivo: mi_aplicacion/patterns/command/command_base.py

from abc import ABC, abstractmethod

class Comando(ABC):
    @abstractmethod
    def execute(self):  # Ejecuta la acción
        pass

    @abstractmethod
    def undo(self):  # Deshace la acción
        pass