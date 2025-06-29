from patterns.strategy.pricing_strategy import PricingStrategy

class DiscountStrategy(PricingStrategy):
    def __init__(self, discount_percent: float):
        self.discount_percent = discount_percent
    
    def calcular_precio(self, precio_base: float) -> float:
        return precio_base * (1 - self.discount_percent / 100)