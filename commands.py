from abc import ABC, abstractmethod
from .imports import *
from .GameStateManager import GameStateManager
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

        direction = player.get_facing_direction()
        print("Last direction:", direction)
        if not direction:
            print("No last direction stored.")
            return []

        dy, dx = {             # bcz they are flipped
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
        }[direction]

        current_pos = player.get_current_position()
        room = player.get_current_room()
        jumped_pose = current_pos + Coord(2 * dx, 2 * dy)

        # Check bounds
        if not (1 <= jumped_pose.x < 14 and 1 <= jumped_pose.y < 14):
            print(f"Jumped to invalid position {jumped_pose} (out of bounds)")
            return []

        # # Check passability
        # target_obj = room.get_object(jumped_pose)
        # if target_obj and not target_obj.is_passable():
        #     print(f"Jumped to blocked tile at {jumped_pose} ({target_obj})")
        #     return []
    
        # Set the postions of the player
        room.remove_player(player)
        player.set_position(jumped_pose)  
        room.add_player(player, jumped_pose)
        print(f"Jumped from {current_pos} to {jumped_pose} in direction '{direction}'")

        return [GridMessage(player)]


class UndoCommand(Command):
    def execute(self, player):
        gsm = GameStateManager()

        if gsm.tracked_picked_items:
            _, item = gsm.tracked_picked_items.pop()

            if hasattr(player, "inventory") and item in player.inventory:
                player.inventory.remove(item)

            drop_coord = player.get_current_position()
            room = player.get_current_room()
            room.add_to_grid(item, drop_coord)

            gsm.undo_collect_item(item)

            if "animal" in str(type(item)).lower():
                msg = f"Dropped {type(item).__name__} at your current location. ({gsm.collected_animals}/{gsm.total_animals} animals rescued)"
            else:
                msg = f"Dropped {type(item).__name__} at your current location."

            return [
                ChatMessage(player, room, msg),
                GridMessage(player, send_desc=False)
            ]

        return [ChatMessage(player, player.get_current_room(), "Nothing to undo.")]
    
