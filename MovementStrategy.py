from abc import ABC, abstractmethod

class MovementStrategy(ABC):
    @abstractmethod
    def move(self):
        pass
    
    
class RandomMovement(MovementStrategy):
    def __init__(self):
        pass
    
    def move(self):
        pass
    

class ShortestPathMovement(MovementStrategy):
    def __init__(self):
        pass
    
    def move(self):
        pass
    
    
class TeleportMovement(MovementStrategy):
    def __init__(self):
        pass
    
    def move(self):
        pass
    
    