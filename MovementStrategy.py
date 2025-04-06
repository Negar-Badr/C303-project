from abc import ABC, abstractmethod
import random
import time
from .imports import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord

class MovementStrategy(ABC):
    """Defines how the Hunter should move"""
    @abstractmethod
    def move(self, hunter, direction):
        pass
    
    
class RandomMovement(MovementStrategy):
    def move(self, hunter, direction = None, player = None) -> list["Message"]:
        random_direction = random.choice(['up', 'down', 'left', 'right'])
        return hunter.base_move(random_direction)


class ShortestPathMovement(MovementStrategy):
    def move(self, hunter, direction: str, player = None) -> list:
        # Use the given direction (computed via hunter.get_direction_toward)
        return hunter.base_move(direction)
    
    
class TeleportMovement(MovementStrategy):
    def __init__(self):
        self.last_teleport_time = time.time()

    def move(self, hunter, direction, player=None) -> list:

        room = hunter.get_current_room()
        now = time.time()

        if now - self.last_teleport_time >= 1:
            self.last_teleport_time = now

            hunter_pos = hunter.get_current_position()
            player_pos = player.get_current_position()
            dy = player_pos.y - hunter_pos.y
            dx = player_pos.x - hunter_pos.x

            if dx != 0:
                dx = dx // abs(dx)
            if dy != 0:
                dy = dy // abs(dy)

            #teleports 2 tiles away
            #teleport_target = Coord(player_pos.y - 2 * dy, player_pos.x - 2 * dx) 
            teleport_target = Coord(player_pos.y, player_pos.x)
            
            status, err = room.remove_from_grid(hunter, hunter.get_current_position())
            if not status:
                return []
            room.add_to_grid(hunter, teleport_target)
            hunter.update_position(teleport_target, room)

            return [GridMessage(player)]
        
        else:
            return hunter.base_move(direction)
