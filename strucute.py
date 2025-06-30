import os

# Estructura adicional necesaria basada en el proyecto actual, evitando duplicados
estructura_nueva = [
    "app/controllers",
    "app/entities",
    "app/models",
    "app/repositories",
    "app/use_cases"
]

# Crear carpetas solo si no existen
for carpeta in estructura_nueva:
    os.makedirs(carpeta, exist_ok=True)

# Crear archivos si no existen ya en el proyecto original
archivos_nuevos = [
    "app/__init__.py",
    "app/controllers/product_controller.py",
    "app/entities/product.py",
    "app/models/product_model.py",
    "app/repositories/product_repository.py",
    "app/use_cases/product_use_case.py"
]

for archivo in archivos_nuevos:
    if not os.path.exists(archivo):
        with open(archivo, "w") as f:
            pass

"✔️ Carpetas y archivos adicionales para Flask creados sin duplicar lo existente."
