import pytest

from project.example_map import ExampleHouse, Tree
from project.imports import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from Player import HumanPlayer

class TestExampleHouse:

    @pytest.fixture
    def house(self) -> tuple[ExampleHouse, HumanPlayer]:
        """
        Setup method to initialize the room and player for each test.
        """
        room = ExampleHouse()
        player = HumanPlayer("test player")
        player.change_room(room)
        return room, player

    def test_player_starts_in_house(self, house):
        """
        Test that the player starts in the house.
        """
        room, player = house
        pos = player.get_current_position()
        # Check that the player is indeed on the map at their position
        assert player in room.get_map_objects_at(pos)

    def test_player_can_move(self, house):
        """
        Test that the player can move to a new position.
        """
        room, player = house
        start = player.get_current_position()
        player.move("right")
        end = player.get_current_position()

        assert start != end, "Player did not move"
        assert player in room.get_map_objects_at(end), "Player not found at new position"
