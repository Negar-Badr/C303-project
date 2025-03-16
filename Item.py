from abc import ABC, abstractmethod

class Item(ABC):
    @abstractmethod
    def something(self):
        pass 


class Flower(Item):
    def __init__(self):
        pass
    

class Rock(Item):
    def __init__(self):
        pass