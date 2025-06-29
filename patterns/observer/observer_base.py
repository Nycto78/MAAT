from abc import ABC, abstractmethod

# Interfaz Observable
class Observable(ABC):
    @abstractmethod
    def attach(self, observer):
        pass

    @abstractmethod
    def detach(self, observer):
        pass

    @abstractmethod
    def notify(self, message):
        pass

# Interfaz Observer
class Observer(ABC):
    @abstractmethod
    def update(self, message):
        pass


# ✅ Clase concreta que implementa Observable
class ObservableBase(Observable):
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self, message):
        for observer in self._observers:
            observer.update(message)
