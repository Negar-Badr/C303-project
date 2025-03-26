
from .imports import *
import math
import random
from typing import Literal
from .GameStateManager import GameStateManager
from .MovementStrategy import RandomMovement

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
    from NPC import NPC

class Hunter(NPC):
    """ A hunter NPC that moves randomly but chases the player when close. """
    
    def __init__(self, encounter_text: str, staring_distance: int = 0, facing_direction: Literal['up', 'down', 'left', 'right'] = 'down') -> None:
        super().__init__(
            name="Hunter",
            image="hunter",
            encounter_text=encounter_text,
            facing_direction=facing_direction,
            staring_distance=staring_distance,
        )
        self.game_over_triggered = False  # Flag to stop movement after game over
        self.movement_strategy = RandomMovement
        self.is_hunter = True
    
    def _find_player(self):
        room = self.get_current_room()
        if hasattr(room, 'player_instance'):
            return room.player_instance
        return None
        
    def update(self) -> list["Message"]:
        """Update hunter's position using the current movement strategy from GameStateManager."""
        # Get the current movement strategy from the game state
        gsm = GameStateManager()
        gsm.update_hunter_strategy()
        current_strategy = gsm.get_hunter_strategy()
        messages = []
        player = self._find_player()
        
        self.movement_strategy = current_strategy
    
        direction_to_player = self.get_direction_toward(player.get_current_position())
        messages += self.movement_strategy.move(self, direction_to_player)
            
        if gsm.is_game_over():
            print("GAME OVER! Player cannot move anymore.")
            return []  # Block all movement

        # Get distance between Hunter and Player
        dist = self._current_position.distance(player.get_current_position())

        if dist == 1:
            # Hunter is 1 tile away → Trigger Game Over
            messages.append(EmoteMessage(self, player, 'exclamation', emote_pos=self._current_position))
            messages.append(DialogueMessage(self, player, "GAME OVER! The hunter caught you.", self.get_image_name()))

            self.game_over_triggered = True  # Stop future movement
            self.game_over(player)
            return messages
        
        return messages
    
    def base_move(self, direction):
        return self.move(direction)

    def get_direction_toward(self, target_position):
        """ Calculate the best move direction toward the player. """
        dx = target_position.x - self._current_position.x
        dy = target_position.y - self._current_position.y

        if abs(dx) > abs(dy):
            return 'right' if dx > 0 else 'left'
        else:
            return 'down' if dy > 0 else 'up'

    def game_over(self, player):
        """ Handles game over logic when the hunter catches the player. """
        game_state_manager = GameStateManager()  # Singleton instance

        # Set game over state
        game_state_manager.set_game_state("lose")

        # Remove the player from the room to stop movement
        room = player.get_current_room()
        if room:
            print(f"Removing player {player} from room after game over.")
            room.remove_from_grid(player, player.get_current_position())  # Removes the player from the game

        print("GAME OVER: The player has been caught by the hunter!")