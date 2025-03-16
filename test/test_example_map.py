import pytest

from ..imports import *
from ..example_map import ExampleHouse

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from Player import HumanPlayer

class TestExampleHouse:

    @pytest.fixture
    def house(self) -> tuple[ExampleHouse, HumanPlayer]:
        # create a new house and player
        room = ExampleHouse()
        player = HumanPlayer("test player")
        player.change_room(room)
        player.set_state("score", 0)
        return room, player

    def test_pplate_score(self, house) -> None:
        room, player = house
        player.move("up")
        assert player.get_state("score") == 1, "Player should have a score of 1 after stepping on the pressure plate"