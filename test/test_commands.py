# TO RUN THE TEST (please follow the README)
# PYTHONPATH="." pytest test -W ignore::DeprecationWarning 

from project.commands import *
from project.example_map import ExampleHouse
from project.GameStateManager import GameStateManager
from project.imports import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from Player import HumanPlayer

from project.GameStateManager import GameStateManager
from project.Animal import Cow  # or whatever item

class TestCommands:

    def setup_method(self):
        """
        Setup method to initialize the room and player for each test.
        """
        self.room = ExampleHouse()
        self.player = HumanPlayer("test player")
        self.start = Coord(5, 5)
        self.jump_target = Coord(3, 5)

        self.player.set_position(self.start)
        self.room.add_player(self.player, self.start)
        self.player.update_position(self.start, self.room)
        self.player.set_facing_direction("up")
        GameStateManager().reset_game_state()  # clean state for each test


    def test_jump_command(self):
        """
        Test that the jump command executes successfully and moves the player.
        """
        for obj in self.room.get_map_objects_at(self.jump_target):
            self.room.remove_from_grid(obj, self.jump_target)

        command = JumpCommand()
        messages = command.execute(self.player)

        assert self.player.get_current_position() == self.jump_target
        assert any(isinstance(m, GridMessage) for m in messages)

    def test_undo_command(self):
        """
        Test that the undo command correctly removes an item from the player's inventory
        """
        cow = Cow()
        gsm = GameStateManager()
        self.player.inventory = [cow]
        gsm.tracked_picked_items = [(self.start, cow)]
        gsm.collected_items.append("animal")
        gsm.collected_animals = 1

        command = UndoCommand()
        messages = command.execute(self.player)

        assert cow not in self.player.inventory
        assert gsm.collected_animals == 0
        assert cow in self.room.get_map_objects_at(self.start)

    def test_reset_command(self): 
        """
        Test that the ResetCommand properly resets the game state and repositions the player to the starting location.
        """
        gsm = GameStateManager()
        cow = Cow()
        self.room.add_to_grid(cow, self.start)
        gsm.tracked_picked_items = [(self.start, cow)]
        gsm.collected_items.append("animal")
        gsm.collected_animals = 1

        # Set state to WIN so reset is allowed
        gsm.set_game_state(GameState.WIN)

        # Execute reset
        command = ResetCommand()
        messages = command.execute(self.player)

        assert gsm.collected_animals == 0
        assert gsm.collected_items == []
        assert any(isinstance(m, GridMessage) for m in messages)
