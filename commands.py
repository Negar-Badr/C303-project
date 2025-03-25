from abc import ABC, abstractmethod
from .imports import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord

class Command(ABC):
    @abstractmethod
    def execute(self, player: "HumanPlayer") -> list["Message"]:
        pass

class JumpCommand(Command):
    def execute(self, player: "HumanPlayer") -> list["Message"]:
        print("JumpCommand triggered")

        direction = player.get_state("last_direction")
        if not direction:
            print("No last direction stored.")
            return []

        dx, dy = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
        }[direction]

        current_pos = player.get_current_position()
        print("Current position:", current_pos)
        room = player.get_current_room()

        pos1 = current_pos + Coord(dx, dy)
        pos2 = current_pos + Coord(2 * dx, 2 * dy)

        print("Jumping to:", pos2)
        #TODO NEED TO ADD THIS FUNCTIONALITY TO THE ROOM CLASS OR IMPLEMENT PASSABLE FROM MAP OBJECTS HERE
        # print("Is pos1 passable?", room.is_passable(pos1))
        # print("Is pos2 passable?", room.is_passable(pos2))
        # # Ensure both positions are passable
        # if not room.is_passable(pos1) or not room.is_passable(pos2):
        #     print("Jump blocked: one or both tiles are impassable.")
        #     return []
    
        # Manual repositioning
        room.remove_from_grid(player, current_pos)
        player.set_position(pos2)  # or use: player._current_position = pos2 if no setter
        room.place_on_grid(player, pos2)
        print("New player position:", player.get_current_position())

        print(f"Jumped from {current_pos} to {pos2} in direction '{direction}'")

        return [GridMessage(player)]
