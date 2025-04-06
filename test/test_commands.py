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

def test_jump_command_executes_jump_successfully():
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



# def test_show_intro_command_returns_dialogues():
#     player = HumanPlayer("Emily")
#     fake_plate = PressurePlate()
#     command = ShowIntroCommand(fake_plate)

#     messages = command.execute(player)

#     assert len(messages) == 2
#     assert all(isinstance(m, DialogueMessage) for m in messages)
#     assert player.get_state("current_menu") == fake_plate



# def test_undo_command_drops_item():
#     room = ExampleHouse()
#     player = HumanPlayer("Emily")
#     item = Cow()
#     coord = Coord(2, 2)

#     player.set_position(coord)
#     room.add_player(player, coord)
#     player.update_position(coord, room)

#     player.set_state("inventory", [item])  
#     gsm = GameStateManager()
#     gsm.tracked_picked_items.append((None, item))
#     gsm.collected_animals = 1
#     gsm.total_animals = 1

#     cmd = UndoCommand()
#     messages = cmd.execute(player)

#     assert item in room.get_map_objects_at(coord)
#     assert item not in player.get_state("inventory")
#     assert any("Dropped Cow" in m.msg for m in messages if isinstance(m, ChatMessage))
