from abc import ABC, abstractmethod

class RepositorioProducto(ABC):

    @abstractmethod
    def obtener_todos(self):
        pass

    @abstractmethod
    def obtener_por_id(self, id: int):
        pass

    @abstractmethod
    def crear(self, producto):
        pass

    @abstractmethod
    def actualizar(self, id: int, producto):
        pass

    @abstractmethod
    def eliminar(self, id: int):
        pass
