from patterns.strategy.pricing_strategy import PricingStrategy

class Producto:
    def __init__(self, id: str, nombre: str, precio_base: float, estrategia: PricingStrategy):
        self.id = id
        self.nombre = nombre
        self.precio_base = precio_base
        self.estrategia = estrategia
    
    def precio_final(self) -> float:
        return self.estrategia.calcular_precio(self.precio_base)
    
    def cambiar_estrategia(self, nueva_estrategia: PricingStrategy):
        self.estrategia = nueva_estrategia