
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

class ScorePressurePlate(PressurePlate):
    def __init__(self, image_name='pressure_plate'):
        super().__init__(image_name)

    def player_entered(self, player) -> list[Message]:
        """ Prevents the player from interacting after game over. """
        game_state_manager = GameStateManager()  # Singleton instance
        
        # If game is over, prevent movement or interaction
        if game_state_manager.is_game_over():
            print("GAME OVER! Player cannot interact anymore.")
            return []  # Return an empty message list to block actions

        messages = super().player_entered(player)

        # Add score to player
        player.set_state("score", player.get_state("score") + 1)
        return messages

# -------------------------------------- BACKGROUND -----------------------------------------------------------------
class Tree(MapObject): 
    def __init__(self, image_name: str = 'tree_heart'):
        super().__init__(f"tile/background/{image_name}", passable=False)

# -------------------------------------- ANIMALS -----------------------------------------------------------------
class Cow(PressurePlate):
    def __init__(self, image_name='animals/cow'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        """Handles when the player steps on a Cow."""
        game_state_manager = GameStateManager()  
        game_state_manager.collect_animal("cow")  # Update game state

        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())
        return [] 
    
class Monkey(PressurePlate):
    def __init__(self, image_name='animals/monkey'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        """Handles when the player steps on a Monkey."""
        game_state_manager = GameStateManager()  
        game_state_manager.collect_animal("monkey")  # Update game state

        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())
        return [] 
    
class Owl(PressurePlate):
    def __init__(self, image_name='animals/owl'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        """Handles when the player steps on a Owl."""
        game_state_manager = GameStateManager()  
        game_state_manager.collect_animal("owl")  # Update game state

        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())
        return []
    
class Rabbit(PressurePlate):
    def __init__(self, image_name='animals/rabbit'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        """Handles when the player steps on a Rabbit."""
        game_state_manager = GameStateManager()  
        game_state_manager.collect_animal("rabbit")  # Update game state

        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())
        return []

# -------------------------------------- ROCKS -----------------------------------------------------------------
class Rock(PressurePlate):
    def __init__(self, image_name='rock'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        """Handles when the player steps on a Rock."""
        game_state_manager = GameStateManager()  # Singleton instance
        game_state_manager.collect_item("rock")  # Notify game state
        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())
        return []

# -------------------------------------- FLOWERS -----------------------------------------------------------------
class Daisy(PressurePlate):
    def __init__(self, image_name='flowers/Daisy'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        """Handles when the player steps on a Daisy."""
        game_state_manager = GameStateManager()  # Singleton instance
        game_state_manager.collect_item("flower")  # Notify game state
        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())
        return []

class Orchid(PressurePlate):
    def __init__(self, image_name='flowers/Orchid'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        """Handles when the player steps on an Orchid."""
        game_state_manager = GameStateManager()  # Singleton instance
        game_state_manager.collect_item("flower")  # Notify game state
        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())
        return [] 
    
class Daffodil(PressurePlate):
    def __init__(self, image_name='flowers/Daffodil'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        """Handles when the player steps on an Daffodil."""
        game_state_manager = GameStateManager()  # Singleton instance
        game_state_manager.collect_item("flower")  # Notify game state
        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())
        return []
    
class Tulip(PressurePlate):
    def __init__(self, image_name='flowers/Tulip'):
        super().__init__(image_name)
        
    def player_entered(self, player) -> list[Message]:
        """Handles when the player steps on an Tulip."""
        game_state_manager = GameStateManager()  # Singleton instance
        game_state_manager.collect_item("flower")  # Notify game state
        room = player.get_current_room()
        room.remove_from_grid(self, self.get_position())
        return []
  
# -------------------------------------- HUNTER -----------------------------------------------------------------
class Hunter(NPC):
    """ A hunter NPC that moves randomly but chases the player when close. """
    
    def __init__(self, encounter_text: str, staring_distance: int = 0, facing_direction: Literal['up', 'down', 'left', 'right'] = 'down') -> None:
        super().__init__(
            name="Hunter",
            image="prof",
            encounter_text=encounter_text,
            facing_direction=facing_direction,
            staring_distance=staring_distance,
        )
        self.game_over_triggered = False  # Flag to stop movement after game over
        self.movement_strategy = RandomMovement
    
    def _find_player(self):
        room = self.get_current_room()
        if hasattr(room, 'player_instance'):
            return room.player_instance
        return None
        
    def update(self) -> list["Message"]:
        """
        This method is called periodically (similar to WalkingProfessor.update)
        so that the hunter moves even when the player is not directly triggering movement.
        It uses the current movement strategy.
        """
        # Get the current movement strategy from the game state
        gsm = GameStateManager()
        gsm.update_hunter_strategy()
        current_strategy = gsm.get_hunter_strategy()
        messages = []
        player = self._find_player()
        
        self.movement_strategy = current_strategy
    
        direction_to_player = self.get_direction_toward(player.get_current_position())
        self.movement_strategy.move(self, direction_to_player)
            
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

# -------------------------------------- OUR HOUSE -----------------------------------------------------------------
class ExampleHouse(Map):
    def __init__(self) -> None:
        super().__init__(
            name="Test House",
            description="Welcome to Paws Peril House! Please help us save the animals",
            size=(15, 15), #size of the area in the example house  
            entry_point=Coord(14, 7),
            background_tile_image='grass',
            background_music='blithe', #todo
        )
        
    def add_player(self, player: "Player", entry_point=None) -> None:
        super().add_player(player, entry_point)
        self.player_instance = player
        print(f"Player {player.get_name()} has entered the map.")
        
    def update(self) -> list[Message]:
        messages = []
        objects = getattr(self, '_Map__objects', [])
        for obj in list(objects):  # iterate over a copy
            messages.extend(obj.update())
        return messages
    
    def get_objects(self) -> list[tuple[MapObject, Coord]]:
        objects: list[tuple[MapObject, Coord]] = []

        # Crearte a list of reserved positions to avoid overlapping objects
        reserved_positions = set()

        #adding trees
        tree = Tree() 
        for i in range(14):
            for pos in [Coord(0, i), Coord(14, i), Coord(i, 0), Coord(i, 14)]:
                objects.append((tree, pos))
                reserved_positions.add(pos.to_tuple())
        objects.append((tree, Coord(14, 14)))
        reserved_positions.add(Coord(14, 14).to_tuple())

        # Remove trees for the entrance
        objects.remove((tree, Coord(14,7)))
        objects.remove((tree, Coord(14,8)))
        # Remove trees for the exit
        objects.remove((tree, Coord(0,4)))
        objects.remove((tree, Coord(0,5)))

        # add a door(entrance)
        door = Door('int_entrance', linked_room="Trottier Town")
        objects.append((door, Coord(14, 7)))
        # add a door(exit)
        door = Door('int_entrance', linked_room="Paws in Peril House")
        objects.append((door, Coord(0, 4)))

        all_positions = [Coord(x, y).to_tuple() for x in range(15) for y in range(15)]
        free_positions = set(all_positions) - reserved_positions

        # print(free_positions)

        # add rocks
        for _ in range(5):
            rock = Rock()
            pos = random.choice(list(free_positions))
            objects.append((rock, Coord(pos[1], pos[0])))
            free_positions.remove(pos)
        
        # add flowers
        for _ in range(5):
            flower = random.choice([Daisy(), Orchid(), Daffodil(), Tulip()])
            pos = random.choice(list(free_positions))
            objects.append((flower, Coord(pos[1], pos[0])))
            free_positions.remove(pos)

        # add cows
        for _ in range(3):
            cow = Cow()
            pos = random.choice(list(free_positions))
            objects.append((cow, Coord(pos[1], pos[0])))
            free_positions.remove(pos)

        # add monkeys
        for _ in range(3):
            monkey = Monkey()
            pos = random.choice(list(free_positions))
            objects.append((monkey, Coord(pos[1], pos[0])))
            free_positions.remove(pos)
        
        # add owls
        for _ in range(3):
            owl = Owl()
            pos = random.choice(list(free_positions))
            objects.append((owl, Coord(pos[1], pos[0])))
            free_positions.remove(pos)

        # add rabbits
        for _ in range(3):
            rabbit = Rabbit()
            pos = random.choice(list(free_positions))
            objects.append((rabbit, Coord(pos[1], pos[0])))
            free_positions.remove(pos)
        
        # add the npc
        hunter = Hunter( #todo
            encounter_text="I will hunt you down",
            staring_distance=1,
        )
        objects.append((hunter, Coord(3,8)))

        # add a pressure plate
        # pressure_plate = ScorePressurePlate()
        # objects.append((pressure_plate, Coord(13, 7)))

        return objects
