from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from infrastructure.repositories.repositorio_mysql import RepositorioMySQL

router = APIRouter()
repo = RepositorioMySQL()

# Pydantic model (validador de entrada/salida)
class ProductoInput(BaseModel):
    nombre: str
    categoria: str
    cantidad: int
    precio: float

@router.get("/productos/")
def listar_productos():
    return repo.obtener_todos()

@router.get("/productos/{id}")
def obtener_producto(id: int):
    producto = repo.obtener_por_id(id)
    if producto:
        return producto
    raise HTTPException(status_code=404, detail="Producto no encontrado")

@router.post("/productos/", status_code=201)
def crear_producto(producto: ProductoInput):
    from domain.entities.producto import Producto
    nuevo = Producto(**producto.dict())
    repo.guardar(nuevo)
    return {"mensaje": "Producto creado"}

@router.put("/productos/{id}")
def actualizar_producto(id: int, producto: ProductoInput):
    if repo.obtener_por_id(id) is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    from domain.entities.producto import Producto
    actualizado = Producto(**producto.dict())
    repo.actualizar(id, actualizado)
    return {"mensaje": "Producto actualizado"}

@router.delete("/productos/{id}")
def eliminar_producto(id: int):
    if repo.obtener_por_id(id) is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    repo.eliminar(id)
    return {"mensaje": "Producto eliminado"}
