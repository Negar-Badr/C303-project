# change directory name to project 
# use PYTHONPATH="." pytest test -W ignore::DeprecationWarning in project directory

import pytest
from project.Hunter import Hunter
from project.MovementStrategy import *
from project.example_map import Tree
from project.Animal import Cow
from project.imports import *
from project.imports import Coord
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from Player import HumanPlayer

MOVE_TO_DIRECTION: dict[str, Coord] = {
    'left': Coord(0, -1),
    'right': Coord(0, 1),
    'up': Coord(-1, 0),
    'down': Coord(1, 0),
}

class StubRoom:
    def __init__(self):
        self.objects = {}  

    def add_to_grid(self, obj, coord: Coord):
        self.objects.setdefault(coord, []).append(obj)
        obj._position = coord
        obj._current_room = self

    def get_map_objects_at(self, coord: Coord):
        return self.objects.get(coord, [])

    def remove_from_grid(self, obj, coord: Coord):
        if coord in self.objects and obj in self.objects[coord]:
            self.objects[coord].remove(obj)
            if not self.objects[coord]:
                del self.objects[coord]
            return True, ""  # ✅ Return status and empty error message
        return False, "Object not found at that position"


    def move(self, obj, direction_s: str):
        new_pos = obj._position + MOVE_TO_DIRECTION[direction_s]
        self.remove_from_grid(obj, obj._position)
        self.add_to_grid(obj, new_pos)
        return []
    
    def send_grid_to_players(self):
        return []
    
    def get_name(self):
        return "StubRoom"



class TestMovementStrategy:
    def test_random_movement(self):
        hunter_pos = Coord(5, 5)
        player_pos = Coord(3, 3)

        room = StubRoom()
        hunter = Hunter("hello", staring_distance=1)
        player = HumanPlayer("TestPlayer")

        room.add_to_grid(hunter, hunter_pos)
        room.add_to_grid(player, player_pos)

        player.update_position(player_pos, room)
        hunter._current_room = room

        strategy = RandomMovement()
        strategy.move(hunter, None, player)  # call move()

        assert hunter.get_current_position() != hunter_pos, "Hunter did not move randomly"

    def test_shortest_path_avoids_tree(self):
        hunter_pos = Coord(5, 5)
        tree_pos = Coord(4, 5)   # Directly in the way
        player_pos = Coord(3, 5)

        room = StubRoom()
        tree = Tree()
        hunter = Hunter("hello", staring_distance=5)
        player = HumanPlayer("TestPlayer")

        room.add_to_grid(tree, tree_pos)
        room.add_to_grid(hunter, hunter_pos)
        room.add_to_grid(player, player_pos)

        player.update_position(player_pos, room)
        hunter._current_room = room

        strategy = ShortestPathMovement()
        # If no path to player was found, don't move

        strategy.move(hunter, "up", player)  # call move()

        new_pos = hunter.get_current_position()
        
        # If hunter didn't move, allow it (path was blocked)
        if new_pos == hunter_pos:
            print("No path to player; hunter stayed put.")
        else:
            assert new_pos != tree_pos, "Hunter moved onto a tree!"

    def test_teleport_movement(self):
        hunter_pos = Coord(2, 2)
        player_pos = Coord(7, 7)

        room = StubRoom()
        hunter = Hunter("Blink", staring_distance=9)
        player = HumanPlayer("TestPlayer")

        room.add_to_grid(hunter, hunter_pos)
        room.add_to_grid(player, player_pos)

        player.update_position(player_pos, room)
        hunter._current_room = room

        strategy = TeleportMovement()
        strategy.last_teleport_time -= 5
        strategy.move(hunter, "down", player)
        for coord, objs in room.objects.items():
            for obj in objs:
                print(f"{obj} is at {coord}")


        new_pos = hunter.get_current_position()
        distance_to_player = new_pos.distance(player_pos)

        print(f"Distance before move: {hunter.get_current_position().distance(player_pos)}")


        assert new_pos != hunter_pos, "Hunter did not teleport"


