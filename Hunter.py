from .imports import *
from typing import Literal, List, Optional, Any
from .GameStateManager import GameStateManager, GameState
from .MovementStrategy import *  
from .Observer import Observer

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    from tiles.base import MapObject
    from tiles.map_objects import *
    from NPC import NPC  
        
class Hunter(NPC, Observer):
    def __init__(self, encounter_text: str, staring_distance: int = 0, facing_direction: Literal['up', 'down', 'left', 'right'] = 'down') -> None:
        super().__init__(
            name="Hunter",
            image="hunter",
            encounter_text=encounter_text,
            facing_direction=facing_direction,
            staring_distance=staring_distance,
        )
        self.movement_strategy = RandomMovement()
        self.is_hunter: bool = True

    def on_notify(self, event: str) -> None:
        """
        Handle notifications from the subject to update the hunter's movement strategy.

        Preconditions:
          - event is a non-empty string.
        Postconditions:
          - self.movement_strategy is updated based on the event and current game state.
        """
        assert isinstance(event, str) and event, "event must be a non-empty string."
        gsm = GameStateManager()
        if event in (["ITEM_COLLECTED", "ANIMAL_COLLECTED"]):
            collected_items = gsm.get_collected_items()
            if not collected_items:
                self.movement_strategy = RandomMovement()
                return

            # Determine the indices of the last occurrence of specific item types.
            last_rock_index: int = max((i for i, item in enumerate(collected_items) if "rock" in item), default=-1)
            last_flower_index: int = max((i for i, item in enumerate(collected_items) if "flower" in item), default=-1)
            has_animal: bool = any("animal" in item for item in collected_items)

            if last_rock_index > last_flower_index: # it will always be teleport until the player picks up a flower
                self.movement_strategy = TeleportMovement()
            elif has_animal: # at least once animal, then the hunter never goes back to shortest path
                self.movement_strategy = ShortestPathMovement()
            elif last_flower_index != -1:
                self.movement_strategy = RandomMovement()
        elif event == "WIN":
            self.movement_strategy = ShortestPathMovement()
        elif event == "LOSE":
            self.movement_strategy = RandomMovement()

    def _find_player(self) -> Optional[Player]:
        """
        Retrieve the player instance from the current room.

        Preconditions:
          - self.get_current_room() returns an object that may contain a 'player_instance' attribute.
        Postconditions:
          - Returns the player instance if found; otherwise, returns None.
        """
        room = self.get_current_room()
        if hasattr(room, 'player_instance'):
            return room.player_instance
        return None

    def update(self) -> List["Message"]:
        """
        Update the hunter's position based on the current movement strategy and apply win-lose conditions.

        Preconditions:
          - The hunter's _current_position and player's current position are valid and support distance calculation.
          - The player instance is found via _find_player().
        Postconditions:
          - Returns a list of Message objects reflecting movement, jumpscare, or win conditions.
        """
        gsm = GameStateManager()
        messages: List["Message"] = []
        player = self._find_player()
        assert player is not None, "Player must be present in the current room."

        # Calculate direction toward the player
        direction_to_player: str = self.get_direction_toward(player.get_current_position())
        messages += self.movement_strategy.move(self, direction_to_player, player)

        # Calculate distance between Hunter and Player
        dist = self._current_position.distance(player.get_current_position())
        
        if gsm.is_game_over() or gsm.is_win():
            return []

        if -2 <= dist <= 1.5:
            # Hunter is close enough to trigger Game Over
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
                    sprite_size=500,
                    orientation="portrait",
                    width=500,
                    height=500,
                    offset_x=0,
                    offset_y=0,
                    gap=0,
                    label_height=0,
                )
            )
            messages.append(DialogueMessage(
                self,
                player,
                "GAME OVER! The hunter caught you MOUAHAHA.",
                self.get_image_name(),
                auto_delay=1000,
                bg_color=(0, 0, 0),
                text_color=(255, 255, 255)
            ))
            messages.append(DialogueMessage(
                self,
                player,
                "To restart the game...\nLeave the room, come back, and press 'r'",
                self.get_image_name(),
                auto_delay=1000,
                bg_color=(0, 0, 0),
                text_color=(255, 255, 255)
            ))
            gsm.set_game_state(GameState.LOSE)  # Lose condition triggered
            return messages

        if gsm.collected_animals >= gsm.total_animals:
            gsm.set_game_state(GameState.WIN)  # Win condition triggered
            messages.append(
                SoundMessage(
                    recipient=player,
                    sound_path="win.mp3",
                    volume=1.0,
                    repeat=False
                )
            )
            messages.append(
                ChooseObjectMessage(
                    sender=self,
                    recipient=player,
                    options=[{"": "image/tile/utility/win/winimage.png"}],
                    window_title="WIN",
                    sprite_size=500,
                    orientation="portrait",
                    width=500,
                    height=500,
                    offset_x=0,
                    offset_y=0,
                    gap=0,
                    label_height=0,
                )
            )
            messages.append(DialogueMessage(
                self,
                player,
                "CONGRATULATIONS, YOU WIN!\n",
                self.get_image_name(),
                bg_color=(255, 182, 193),
                text_color=(0, 0, 0)
            ))
            messages.append(DialogueMessage(
                self,
                player,
                "Please leave the room.\nTo restart the game, come back and press 'r'",
                self.get_image_name(),
                bg_color=(255, 182, 193),
                text_color=(0, 0, 0)
            ))
            return messages
        
        return messages

    def base_move(self, direction: str) -> list[Message]:
        """
        Perform a basic move in the given direction using the inherited move function.

        Preconditions:
          - direction must be a non-empty string indicating the move direction.
        """
        assert isinstance(direction, str) and direction, "direction must be a non-empty string."
        return self.move(direction)

    def get_direction_toward(self, target_position: "Coord") -> str:
        """
        Calculate the best move direction toward a target position.

        Preconditions:
          - target_position must have numeric attributes 'x' and 'y'.
          - self._current_position must be set and have numeric attributes 'x' and 'y'.
        Postconditions:
          - Returns one of 'up', 'down', 'left', or 'right'.
        """
        # Ensure target_position has 'x' and 'y'
        assert hasattr(target_position, 'x') and hasattr(target_position, 'y'), "target_position must have x and y coordinates."
        # Ensure self._current_position exists and has 'x' and 'y'
        assert hasattr(self, '_current_position'), "Hunter must have a _current_position attribute."
        assert hasattr(self._current_position, 'x') and hasattr(self._current_position, 'y'), "self._current_position must have x and y coordinates."

        dx = target_position.x - self._current_position.x
        dy = target_position.y - self._current_position.y

        if abs(dx) > abs(dy):
            return 'right' if dx > 0 else 'left'
        else:
            return 'down' if dy > 0 else 'up'