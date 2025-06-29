from .pricing_strategy import PricingStrategy

class IVAStrategy(PricingStrategy):
    def calcular_precio(self, precio_base: float) -> float:
        return precio_base * 1.21