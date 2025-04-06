# change directory name to project 
# use PYTHONPATH="." pytest test -W ignore::DeprecationWarning in project directory
import pytest

from ..imports import *
from ..example_map import ExampleHouse, Tree
from project.Animal import Cow

from typing import TYPE_CHECKING
from project.Hunter import Hunter
if TYPE_CHECKING:
    from coord import Coord
    from Player import HumanPlayer

class TestExampleHouse:
    @pytest.fixture
    def house(self) -> tuple[ExampleHouse, HumanPlayer, Hunter]:
        room = ExampleHouse()
        player = HumanPlayer("test player")
        hunter = Hunter("hunter", staring_distance=1)

        # Set positions
        player_pos = Coord(3, 3)
        hunter_pos = Coord(5, 5)

        room.add_to_grid(player, player_pos)
        room.add_to_grid(hunter, hunter_pos)

        player.update_position(player_pos, room)
        hunter.update_position(hunter_pos, room)
        hunter._current_room = room
        room.player_instance = player  # if your logic uses this

        return room, player, hunter
    
    def test_hunter_and_player_added_to_house(self, house):
        room, player, hunter = house

        player_objects = room.get_map_objects_at(player.get_current_position())
        hunter_objects = room.get_map_objects_at(hunter.get_current_position())

        assert player in player_objects, "Player should be at their position in the house grid"
        assert hunter in hunter_objects, "Hunter should be at their position in the house grid"

    def test_static_items_exist_in_example_house(self):
        room = ExampleHouse()

        found_tree = False
        found_cow = False

        for y in range(15):  # Assuming grid size is 15x15
            for x in range(15):
                objs = room.get_map_objects_at(Coord(y, x))
                for obj in objs:
                    if isinstance(obj, Tree):
                        found_tree = True
                    if isinstance(obj, Cow):
                        found_cow = True

        assert found_tree, "Expected at least one Tree in ExampleHouse"
        assert found_cow, "Expected at least one Cow in ExampleHouse"

