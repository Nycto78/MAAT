
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt

class IDataSource(ABC):
    @abstractmethod
    def get_labels(self): pass

    @abstractmethod
    def get_values(self): pass

    @abstractmethod
    def get_title(self): pass

class SalesData(IDataSource):
    def __init__(self, data): self.data = data
    def get_labels(self): return list(self.data.keys())
    def get_values(self): return list(self.data.values())
    def get_title(self): return "Sales by Product"

class InventoryData(IDataSource):
    def __init__(self, data): self.data = data
    def get_labels(self): return list(self.data.keys())
    def get_values(self): return list(self.data.values())
    def get_title(self): return "Inventory by Product"

class Chart(ABC):
    def __init__(self, data_source: IDataSource): self.data_source = data_source
    @abstractmethod
    def render(self): pass

class BarChart(Chart):
    def render(self):
        fig, ax = plt.subplots()
        ax.bar(self.data_source.get_labels(), self.data_source.get_values())
        ax.set_title(self.data_source.get_title())
        return fig
