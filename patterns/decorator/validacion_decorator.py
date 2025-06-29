from patterns.decorator.base_decorator import InventarioDecorator

class ValidacionStockDecorator(InventarioDecorator):
    def actualizar_stock(self, producto_id: str, cantidad: int) -> bool:
        producto = self._wrapped.obtener_producto(producto_id)
        
        if cantidad < 0 and abs(cantidad) > producto.get("cantidad", 0):
            print("❌ No hay suficiente stock para descontar.")
            return False
            
        return super().actualizar_stock(producto_id, cantidad)