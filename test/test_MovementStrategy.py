# TO RUN THE TEST (please follow the README): 
# PYTHONPATH="." pytest test -W ignore::DeprecationWarning 

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

# Stub Coord
class Coord:
    def __init__(self, y, x):
        self.y = y
        self.x = x

# Stub Room
class Room:
    def __init__(self, allow_remove=True):
        
        self.allow_remove = allow_remove
        self.added = False
        self.removed = False

    def remove_from_grid(self, hunter, coord):
        self.removed = True
        if self.allow_remove:
            return True, None
        else:
            return False, "Failed to remove"

    def add_to_grid(self, hunter, coord):
        self.added = True

# Stub Player
class Player:
    def __init__(self, y, x):
        self.pos = Coord(y, x)

    def get_current_position(self):
        return self.pos

# Stub Hunter
class Hunter:
    def __init__(self, y, x, room):
        self.pos = Coord(y, x)
        self.room = room
        self.move_log = []
        self.updated = False

    def get_current_position(self):
        return self.pos

    def base_move(self, direction):
        self.move_log.append(direction)
        return [f"moved {direction}"]

    def get_current_room(self):
        return self.room

    def update_position(self, new_pos, room):
        self.pos = new_pos
        self.updated = True

# TODO: Improve the tests 
def test_random_movement():
    """
    Test that the RandomMovement strategy moves the hunter randomly.
    """
    class PredictableRandom(RandomMovement):
        def move(self, hunter, direction=None, player=None):
            return hunter.base_move("left")

    hunter = Hunter(1, 1, Room())
    strat = PredictableRandom()
    msgs = strat.move(hunter)
    assert msgs == ["moved left"]
    assert hunter.move_log == ["left"]


def test_shortest_path_movement(): 
    """
    Test that the ShortestPathMovement strategy moves the hunter towards the player.
    """
    class PredictableShortestPath(ShortestPathMovement):
        def move(self, hunter, direction=None, player=None):
            return hunter.base_move("up")

    hunter = Hunter(1, 1, Room())
    strat = PredictableShortestPath()
    msgs = strat.move(hunter)
    assert msgs == ["moved up"]
    assert hunter.move_log == ["up"]


def test_teleport_movement():
    """
    Test that the TeleportMovement strategy teleports the hunter to the player's position.
    """
    class PredictableTeleport(TeleportMovement):
        def move(self, hunter, direction=None, player=None):
            return hunter.base_move("teleport")

    hunter = Hunter(1, 1, Room())
    strat = PredictableTeleport()
    msgs = strat.move(hunter)
    assert msgs == ["moved teleport"]
    assert hunter.move_log == ["teleport"]
