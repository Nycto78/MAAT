# interface_adapters/controllers/api/api_encargos.py
from fastapi import APIRouter, HTTPException
from infrastructure.repositories.repositorio_encargos import (
    obtener_todos_encargos,
    guardar_encargo,
    actualizar_encargo,
    eliminar_encargo
)

router = APIRouter(prefix="/encargos")

@router.get("/")
def listar_encargos():
    return obtener_todos_encargos()

@router.post("/")
def crear_encargo(encargo: dict):
    try:
        guardar_encargo(encargo)
        return {"mensaje": "Encargo creado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{encargo_id}")
def modificar_encargo(encargo_id: int, encargo: dict):
    try:
        actualizar_encargo(encargo_id, encargo)
        return {"mensaje": "Encargo actualizado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{encargo_id}")
def borrar_encargo(encargo_id: int):
    try:
        eliminar_encargo(encargo_id)
        return {"mensaje": "Encargo eliminado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
