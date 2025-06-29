from infrastructure.repositories.inventario_service import InventarioService
from patterns.decorator.validacion_decorator import ValidacionStockDecorator
from patterns.decorator.auditoria_decorator import AuditoriaDecorator

class InventarioController:
    def __init__(self):
        # Servicio base + decoradores
        self.servicio = AuditoriaDecorator(
            ValidacionStockDecorator(
                InventarioService()  # Servicio concreto
            )
        )

    def actualizar_stock(self, producto_id: str, cantidad: int) -> bool:
        return self.servicio.actualizar_stock(producto_id, cantidad)