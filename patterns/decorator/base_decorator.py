class InventarioDecorator:
    def __init__(self, wrapped):
        self._wrapped = wrapped  # Servicio/repositorio a decorar

    def actualizar_stock(self, producto_id: str, cantidad: int) -> bool:
        return self._wrapped.actualizar_cantidad(producto_id, cantidad)

    def obtener_producto(self, producto_id: str) -> dict:
        return self._wrapped.obtener_por_id(producto_id)