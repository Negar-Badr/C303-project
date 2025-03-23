from abc import ABC, abstractmethod
import random
import time

class MovementStrategy(ABC):
    """Defines how the Hunter should move"""
    @abstractmethod
    def move(self, hunter):
        pass
    
    
class RandomMovement(MovementStrategy):
    def move(self, hunter, direction: str = None) -> list:
        random_direction = random.choice(['up', 'down', 'left', 'right'])
        return hunter.base_move(random_direction)
    

class ShortestPathMovement(MovementStrategy):
    def move(self, hunter, direction: str) -> list:
        # Use the given direction (computed via hunter.get_direction_toward)
        return hunter.base_move(direction)
    
    
class TeleportMovement(MovementStrategy):
    def __init__(self):
        self.last_teleport_time = time.time()
    
    def move(self, hunter, direction: str) -> list:
        now = time.time()
        if now - self.last_teleport_time >= 10:
            self.last_teleport_time = now
            messages = []
            print(f"Teleporting towards {direction}!")
            # Teleport two tiles toward the player by invoking base_move twice in the provided direction.
            for _ in range(2):
                messages.extend(hunter.base_move(direction))
            return messages
        else:
            return hunter.base_move(direction)


    
    