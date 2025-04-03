import pytest

# from ..imports import *
from ..MovementStrategy import RandomMovement
# from ..MovementStrategy import ShortestPathMovement
# , TeleportMovement, MovementStrategy

# from ..MovementStrategy import RandomMovement, ShortestPathMovement, TeleportMovement, MovementStrategy
# import time

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

def test_random_movement():
    class PredictableRandom(RandomMovement):
        def move(self, hunter, direction=None, player=None):
            return hunter.base_move("left")

    hunter = Hunter(1, 1, Room())
    strat = PredictableRandom()
    msgs = strat.move(hunter)
    assert msgs == ["moved left"]
    assert hunter.move_log == ["left"]