# interface_adapters/controllers/api/app.py

from fastapi import FastAPI
from interface_adapters.controllers.api.api import router
from interface_adapters.controllers.api.api_encargos import router as encargos_router

app = FastAPI()
app.include_router(router)
app.include_router(encargos_router)

app.include_router(encargos_router, prefix="/encargos")