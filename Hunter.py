
from .imports import *
import math
import random
from typing import Literal
from .GameStateManager import GameStateManager
from .MovementStrategy import *
from PIL import Image, ImageTk
import tkinter as tk
from abc import ABC
from .Observer import Observer

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
    from NPC import NPC
        
class Hunter(NPC, Observer):
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
        self.movement_strategy = RandomMovement()
        self.is_hunter = True
        
    def on_notify(self, subject, event):
        if event in (["ITEM_COLLECTED", "ANIMAL_COLLECTED"]):
            collected_items = subject.get_collected_items()
            if not collected_items:
                self.movement_strategy = RandomMovement()
                return

            last_rock_index = max((i for i, item in enumerate(collected_items) if "rock" in item), default=-1)
            last_flower_index = max((i for i, item in enumerate(collected_items) if "flower" in item), default=-1)
            has_animal = any("animal" in item for item in collected_items)

            if last_rock_index > last_flower_index: # it will always be teleport until the player picks up a flower
                self.movement_strategy = TeleportMovement()

            elif has_animal: # at least once animal, then the hunter never goes back to shortest path
                self.movement_strategy = ShortestPathMovement()

            elif last_flower_index != -1: # if doesnt have at least once animal, and we have a flower, hunter will be random 
                self.movement_strategy = RandomMovement()
        elif event == "WIN":
            self.handle_win()
        elif event == "LOSE":
            self.handle_lose()
            
    def handle_lose(self):
        return [] 

    def handle_win(self):
        player = self._find_player()
        return [DialogueMessage(self, player, "CONGRATULATIONS, YOU WIN!", self.get_image_name())]
    
    def _find_player(self):
        room = self.get_current_room()
        if hasattr(room, 'player_instance'):
            return room.player_instance
        return None
        
    def update(self) -> list["Message"]:
        """Update hunter's position using the current movement strategy from GameStateManager."""
        gsm = GameStateManager()
        messages = []
        player = self._find_player()
    
        direction_to_player = self.get_direction_toward(player.get_current_position())
        messages += self.movement_strategy.move(self, direction_to_player, player)

        # Get distance between Hunter and Player
        dist = self._current_position.distance(player.get_current_position())

        if -2 <= dist <= 1.5:
            # Hunter is 1 tile away → Trigger Game Over
            messages.append(EmoteMessage(self, player, 'exclamation', emote_pos=self._current_position))
            
            messages.append(
                SoundMessage(
                    recipient=player,
                    sound_path="jumpscaresound.mp3",  
                    volume=1.0,                        
                    repeat=False                      
                )
            )

            messages.append(
                ChooseObjectMessage(
                    sender=self,
                    recipient=player,
                    options=[{"": "image/tile/utility/jumpscare/scary1.png"}], 
                    window_title="JUMPSCARE",
                    sprite_size=500,           # Match the size of the window
                    orientation="portrait",
                    width=500,
                    height=500,
                    offset_x=0,
                    offset_y=0,
                    gap=0,
                    label_height=0   # No label  
                )
            )

            messages.append(DialogueMessage(
                self, 
                player, 
                "GAME OVER! The hunter caught you.", 
                self.get_image_name(), 
                auto_delay=1000,
                bg_color=(0, 0, 0),      # black background
                text_color=(255, 255, 255)  # white text
            ))
            
            self.game_over_triggered = True  # Stop future movement
            gsm.set_game_state("lose")
            # room = player.get_current_room()
            # if room:
            #     room.remove_from_grid(player, player.get_current_position())  # Player stops moving
            #     #TODO Player should be given an option here to restart or leave the game, and then the correct action would be taken
            return messages
           
        if gsm.collected_animals >= gsm.total_animals and (player._current_position == Coord(14,7) or player._current_position == Coord(14,8)):
            gsm.set_game_state("win") #  Win condition triggered!
        
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