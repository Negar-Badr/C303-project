# change directory name to project 
# use PYTHONPATH="." pytest test -W ignore::DeprecationWarning in project directory
from project.commands import *
from project.example_map import ExampleHouse
from project.imports import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from Player import HumanPlayer

from project.GameStateManager import GameStateManager
from project.Animal import Cow  # or whatever item

def test_jump_command():
    room = ExampleHouse()
    player = HumanPlayer("Emily")
    start = Coord(5, 5)
    jump_target = Coord(3, 5)

    # Clear jump target tile
    for obj in room.get_map_objects_at(jump_target):
        room.remove_from_grid(obj, jump_target)

    player.set_position(start)
    room.add_player(player, start)
    player.update_position(start, room)
    player.set_facing_direction("up")

    command = JumpCommand()
    messages = command.execute(player)

    assert player.get_current_position() == jump_target
    assert any(isinstance(m, GridMessage) for m in messages)


