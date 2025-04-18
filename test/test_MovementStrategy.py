# TO RUN THE TEST (please follow the README): 
# PYTHONPATH="." pytest test -W ignore::DeprecationWarning 

import pytest
from project.Hunter import Hunter
from project.MovementStrategy import *
from project.imports import *
from project.imports import Coord
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord

# Stub Coord
class Coord:
    def __init__(self, y, x):
        self.y = y
        self.x = x

    def to_tuple(self):
        return (self.y, self.x)

# Stub Room
class Room:
    def __init__(self):
        self.removed = False
        self.added_coord = None

    def get_map_objects_at(self, coord):
        return []  # No trees

    def remove_from_grid(self, hunter, coord):
        self.removed = True
        return True, None

    def add_to_grid(self, hunter, coord):
        self.added_coord = coord

    def get_info(self, player):
        return {} 

# Stub Player
class Player:
    def __init__(self, y, x):
        self.pos = Coord(y, x)
    def get_current_position(self):
        return self.pos
    def get_current_room(self):
        return Room()

# Stub Hunter
class Hunter:
    def __init__(self, y, x):
        self.pos = Coord(y, x)
        self.move_log = []
        self.updated = False  

    def get_current_position(self):
        return self.pos

    def get_current_room(self):
        return self.room  

    def base_move(self, direction):
        self.move_log.append(direction)
        if direction == "left":
            self.pos.x -= 1
        elif direction == "right":
            self.pos.x += 1
        elif direction == "up":
            self.pos.y -= 1
        elif direction == "down":
            self.pos.y += 1
        return [f"moved {direction}"]

    def update_position(self, new_pos, room):
        self.pos = new_pos
        self.updated = True


# Define fixtures 
@pytest.fixture
def room():
    return Room()

@pytest.fixture
def hunter(room):
    h = Hunter(2, 2)
    h.room = room                   
    h.get_current_room = lambda: room 
    return h

@pytest.fixture
def player():
    return Player(2, 5)

@pytest.fixture
def shortest_path_strategy():
    return ShortestPathMovement()

@pytest.fixture
def teleport_strategy():
    strat = TeleportMovement()
    strat.last_teleport_time = time.time() - 3  
    return strat

@pytest.fixture
def random_strategy():
    return RandomMovement()


class TestMovementStrategies:
    def test_random_movement(self, hunter, random_strategy):
        """
        Test that the hunter moves randomly in one of the four directions.
        """
        msgs = random_strategy.move(hunter)
        assert hunter.move_log[-1] in ["left", "right", "up", "down"]
        assert "moved" in msgs[0]

    def test_shortest_path_movement(self, hunter, player, shortest_path_strategy):
        """
        Test that the hunter moves towards the player using the shortest path.
        """
        original_distance = abs(hunter.pos.y - player.pos.y) + abs(hunter.pos.x - player.pos.x)

        msgs = shortest_path_strategy.move(hunter, direction=None, player=player)

        assert hunter.move_log[-1] in ["left", "right", "up", "down"]
        new_distance = abs(hunter.pos.y - player.pos.y) + abs(hunter.pos.x - player.pos.x)
        assert new_distance < original_distance
        assert msgs == [f"moved {hunter.move_log[-1]}"]

    def test_teleport(self, hunter, player, teleport_strategy, room):
        """
        Test that the hunter teleports to a position close to the player.
        """
        msgs = teleport_strategy.move(hunter, direction="up", player=player)

        # Hunter should teleport close to player
        assert hunter.updated, "Hunter should have updated position"
        assert isinstance(msgs[0], GridMessage), "Expected a GridMessage after teleport"
        assert room.removed, "Hunter should be removed from grid"
        assert room.added_coord is not None, "Hunter should be added to new coord"
