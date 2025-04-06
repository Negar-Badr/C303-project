from abc import ABC, abstractmethod
import random
import time
from .imports import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
from heapq import *

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
        # Direction mappings
        direc_map = {
            'up': (-1, 0),
            'down': (1, 0),
            'left': (0, -1),
            'right': (0, 1)
        }
        direc_map_inverse = {
            (-1, 0): 'up',
            (1, 0): 'down',
            (0, -1): 'left',
            (0, 1): 'right'}

        def distance(pos1, pos2):
            """Calculate Manhattan distance between two positions."""
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) 

        # Use the given direction (computed via hunter.get_direction_toward)
        hunter_pos: Coord = hunter.get_current_position()
        player_pos: Coord = player.get_current_position()
        room = hunter.get_current_room()

        prev_map = {}

        pq = [(0, (hunter_pos.y, hunter_pos.x))]
        visited = set()
        
        def is_tree_at_Coord(coord):
            """Check if a Tree object exists at the given coordinate."""
            obj_list = room.get_map_objects_at(coord)
            for obj in obj_list:
                if str(type(obj)) == "<class 'C303-project.example_map.Tree'>":
                    return True
            return False
        
        # Dijkstra's algorithm        
        while pq:
            dist, pos = heappop(pq)
            if pos in visited or is_tree_at_Coord(Coord(pos[0], pos[1])):
                continue
            visited.add(pos)
            if pos == (player_pos.y, player_pos.x):
                break
            for direction, (dy, dx) in direc_map.items():
                new_pos = (pos[0] + dy, pos[1] + dx)
                # Boundary check
                if 0 <= new_pos[0] < 15 and 0 <= new_pos[1] < 15:
                    heappush(pq, (distance(new_pos, (player_pos.y, player_pos.x)), new_pos))
                    if new_pos not in prev_map:
                        prev_map[new_pos] = pos
        
        # Backtrack to find the path
        pos = (player_pos.y, player_pos.x)
        while pos in prev_map:
            if prev_map[pos] == (hunter_pos.y, hunter_pos.x):
                break
            else:
                pos = prev_map[pos]
        # Determine the direction to move
        delta_pos = (pos[0] - hunter_pos.y, pos[1] - hunter_pos.x)
        if delta_pos in direc_map_inverse:
            direction = direc_map_inverse[delta_pos]
            
        return hunter.base_move(direction)
    
    
class TeleportMovement(MovementStrategy):
    def __init__(self):
        self.last_teleport_time = time.time()

    def move(self, hunter, direction, player=None) -> list:

        room = hunter.get_current_room()
        now = time.time()

        if now - self.last_teleport_time >= 2:
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

            distance = abs(dx) + abs(dy)
            if distance <= 1:
                teleport_target = player_pos  # teleport ONTO player if one tile away (in case the player isnt moving)
            else:
                teleport_target = Coord(player_pos.y - dy, player_pos.x - dx)  # 1 tile away
            
            status, err = room.remove_from_grid(hunter, hunter.get_current_position())
            if not status:
                return []
            room.add_to_grid(hunter, teleport_target)
            hunter.update_position(teleport_target, room)

            return [GridMessage(player)]
        
        else:
            return hunter.base_move(direction)
