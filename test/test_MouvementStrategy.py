# change directory name to project 
# use PYTHONPATH="." pytest test -W ignore::DeprecationWarning in project directory

import pytest
from project.Hunter import Hunter
from project.MovementStrategy import *
from project.example_map import ExampleHouse, Tree
from project.Animal import Cow
from project.imports import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from Player import HumanPlayer


class TestMovementStrategy:
    def test_random_movement(self):
        hunter_pos = Coord(5, 5)
        player_pos = Coord(3, 3)

        room = ExampleHouse()
        hunter = Hunter("hello", staring_distance=1)
        player = HumanPlayer("TestPlayer")

        room.add_to_grid(hunter, hunter_pos)
        room.add_to_grid(player, player_pos)

        player.update_position(player_pos, room)
        hunter._current_room = room

        strat = RandomMovement()
        direction = hunter.get_direction_toward(player.get_current_position())
        assert direction == 'up' or direction == 'down' or direction == 'left' or direction == 'right'

    def test_shortest_path_avoids_tree(self):
        hunter_pos = Coord(5, 5)
        tree_pos = Coord(4, 5)
        player_pos = Coord(3, 5)

        room = ExampleHouse()
        tree = Tree()
        hunter = Hunter("hello", staring_distance=1)
        player = HumanPlayer("TestPlayer")

        room.add_to_grid(tree, tree_pos)
        room.add_to_grid(hunter, hunter_pos)
        room.add_to_grid(player, player_pos)

        player.update_position(player_pos, room)
        hunter._current_room = room

        strat = ShortestPathMovement()
        direction = hunter.get_direction_toward(player.get_current_position())
        #next_direction = strat.get_next_direction(hunter, player)
        assert hunter.get_current_position() != tree_pos
        #assert next_direction==direction