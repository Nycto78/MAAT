# domain/entities/producto.py

class Producto:
    def __init__(self, nombre, categoria, cantidad, precio, id=None):
        self.id = id
        self.nombre = nombre
        self.categoria = categoria
        self.cantidad = cantidad
        self.precio = precio

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "cantidad": self.cantidad,
            "precio": self.precio
        }
