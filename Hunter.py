
from .imports import *
import math
import random
from typing import Literal
from .GameStateManager import GameStateManager
from .MovementStrategy import RandomMovement
from PIL import Image, ImageTk
import tkinter as tk
from abc import ABC

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
    from NPC import NPC

class ScaryPopup(ABC):
    def __init__(self, root_window, image_path: str, text: str = "You're mine now!"):
        self._window = tk.Toplevel(root_window)
        self._window.title("GAME OVER")
        self._window.geometry("400x300")
        self._window.configure(bg="black")
        self._window.resizable(False, False)

        # Load and place the image
        img = Image.open(image_path)
        img = img.resize((200, 200))
        self._tk_img = ImageTk.PhotoImage(img)

        image_label = tk.Label(self._window, image=self._tk_img, bg="black")
        image_label.pack(pady=10)

        # Add text label
        text_label = tk.Label(self._window, text=text, fg="white", bg="black", font=("Consolas", 14, "bold"))
        text_label.pack()

        # Close on click or key
        self._window.bind("<Return>", lambda e: self._window.destroy())
        self._window.bind("<Escape>", lambda e: self._window.destroy())
        self._window.focus_set()

    def run(self):
        self._window.wait_window()
        
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
        current_strategy = gsm.get_hunter_strategy()
        messages = []
        player = self._find_player()
        
        self.movement_strategy = current_strategy
    
        direction_to_player = self.get_direction_toward(player.get_current_position())
        messages += self.movement_strategy.move(self, direction_to_player, player)
            
        if gsm.is_game_over():
            return []  # Block all movement
        
        if gsm.is_win():
            return [DialogueMessage(self, player, "CONGRATULATIONS, YOU WIN!", self.get_image_name())]

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

            messages.append(DialogueMessage(self, player, "GAME OVER! The hunter caught you.", self.get_image_name(), auto_delay=1000))

            self.game_over_triggered = True  # Stop future movement
            gsm.set_game_state("lose")
            room = player.get_current_room()
            if room:
                room.remove_from_grid(player, player.get_current_position())  # Player stops moving
                #TODO Player should be given an option here to restart or leave the game, and then the correct action would be taken
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