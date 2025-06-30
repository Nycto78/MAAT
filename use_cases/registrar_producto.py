# use_cases/registrar_producto.py

from infrastructure.repositories.repositorio_mysql import RepositorioMySQL
from domain.entities.producto import Producto

def listar_productos():
    repo = RepositorioMySQL()
    productos_data = repo.obtener_todos()
    return [Producto(**data) for data in productos_data]

def agregar_producto(producto: Producto):
    repo = RepositorioMySQL()
    repo.guardar(producto)
