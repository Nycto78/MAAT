from abc import ABC, abstractmethod

class IInventarioService(ABC):
    @abstractmethod
    def actualizar_stock(self, producto_id: str, cantidad: int) -> bool:
        pass

    @abstractmethod
    def obtener_producto(self, producto_id: str) -> dict:
        pass