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
        self.last_teleport_time = None

    def move(self, hunter, direction: str) -> list:
        now = time.time()
        if self.last_teleport_time is None or now - self.last_teleport_time >= 5:
            self.last_teleport_time = now
            # Teleport: move two tiles in the opposite direction of the chase
            opposite = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}
            teleport_direction = opposite[direction] if direction in opposite else random.choice(['up', 'down', 'left', 'right'])
            messages = []
            # “Teleport” by moving two tiles immediately
            for _ in range(2):
                messages.extend(hunter.base_move(teleport_direction))
            return messages
        else:
            # Fall back to shortest-path behavior if not time to teleport
            return hunter.base_move(direction)

    
    