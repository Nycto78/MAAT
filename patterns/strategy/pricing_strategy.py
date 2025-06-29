from abc import ABC, abstractmethod

class PricingStrategy(ABC):
    @abstractmethod
    def calcular_precio(self, precio_base: float) -> float:
        pass