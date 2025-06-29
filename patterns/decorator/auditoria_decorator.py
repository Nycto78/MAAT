from patterns.decorator.base_decorator import InventarioDecorator
from datetime import datetime

class AuditoriaDecorator(InventarioDecorator):
    def actualizar_stock(self, producto_id: str, cantidad: int) -> bool:
        resultado = super().actualizar_stock(producto_id, cantidad)
        
        with open("auditoria.log", "a") as f:
            f.write(
                f"[{datetime.now()}] Producto {producto_id} - "
                f"Cambio: {cantidad} - "
                f"Resultado: {'Éxito' if resultado else 'Fallo'}\n"
            )
        
        return resultado