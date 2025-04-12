from enum import Enum
from .imports import *
from .Subject import Subject
from .Observer import Observer
import copy
from typing import List, Tuple, Optional, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from coord import Coord
    from maps.base import Map
    
class GameState(Enum):
    PLAYING = "playing"
    WIN = "win"
    LOSE = "lose"

class GameStateManager(Subject):
    """
    A singleton class responsible for managing high-level game state,
    such as current play state, collected items, animals, observers, etc.
    Also the subject in the observer pattern.

    Invariants:
        - self.state must be one of GameState enums.
        - self.collected_animals >= 0.
        - len(self.collected_items) >= 0.
        - 0 <= self.collected_animals <= self.total_animals.
    """
    _instance = None  

    def __new__(cls):
        """Ensure only one instance of GameStateManager is created."""
        if cls._instance is None:
            cls._instance = super(GameStateManager, cls).__new__(cls)
            cls._instance._initialized = False  # To track if __init__ is already called
        return cls._instance

    def __init__(self):
        """Initialize game state variables only once."""
        if not self._initialized:
            self.state: GameState = GameState.PLAYING # Initial state is PLAYING
            self.collected_items: List[Any] = []  # Stores collected items (e.g., "rock", "flower", "animal")
            self.collected_animals: int = 0     
            self.total_animals: int = 12        
            self._initialized = True            # Mark as initialized once setup is done
            self.tracked_picked_items: List[Tuple[Any, Coord]] = []  # For undo support
            self.current_map: Optional[Map] = None
            self._original_objects: List[Tuple[Any, Coord]] = []  # Original layout (list of (object, coord))
            self._observers: List[Observer] = []  # For the Observer pattern
    
    def store_original_objects(self, objects: List[Tuple[Any, Coord]]) -> None:
        """
        Store the original objects (deep-copied) and their coordinates.
        Precondition:
            - objects is a list of (obj, coord) tuples.
        Postcondition:
            - self._original_objects is replaced with a list of (deepcopy(obj), coord).
        """
        assert isinstance(objects, list), "objects must be a list of tuples."
        self._original_objects = [(copy.deepcopy(obj), coord) for obj, coord in objects]

    def get_original_objects(self) -> List[Tuple[Any, Coord]]:
        """Retrieve the stored original objects."""
        return self._original_objects

    def reset_game_state(self) -> None:
        """
        Reset the game to a fresh state.
        Postcondition:
            - self.state == GameState.PLAYING
            - self.collected_items is empty
            - self.collected_animals == 0
            - self.tracked_picked_items is empty
        """
        self.state = GameState.PLAYING
        self.collected_items.clear()
        self.collected_animals = 0
        self.tracked_picked_items.clear()
            
    def add_observer(self, observer: Observer) -> None:
        """
        Add a new observer.
        Precondition:
            - observer is not None
        Postcondition:
            - observer is in self._observers
        """
        assert observer is not None, "observer must not be None."
        self._observers.append(observer)

    def remove_observer(self, observer: Observer) -> None:
        """
        Remove an observer from the list if present.
        Precondition:
            - observer is not None
        Postcondition:
            - if observer was in self._observers, it is removed
        """
        assert observer is not None, "observer must not be None."
        if observer in self._observers:
            self._observers.remove(observer)  
    
    def notify_observers(self, event: str) -> None:
        """
        Notify all registered observers about an event.
        Precondition:
            - event is a non-empty string
        """
        assert event, "event must be a valid, non-empty identifier."
        for observer in self._observers:
            observer.on_notify(event)  

    def collect_item(self, item: Any) -> None:
        """
        Update game state when the player collects an item.
        Precondition:
            - item is not None
        Postcondition:
            - item is appended to self.collected_items
            - Observers are notified with "ITEM_COLLECTED"
        """
        assert item is not None, "item must not be None."
        self.collected_items.append(item)
        self.notify_observers("ITEM_COLLECTED")
    
    def track_picked_item(self, item: Any, coord: Coord) -> None:
        """
        Record an item that was picked up along with its coordinate.
        Precondition:
            - item is not None
            - coord is a valid coordinate
        Postcondition:
            - (coord, item) is appended to self.tracked_picked_items
        """
        assert item is not None, "item must not be None."
        self.tracked_picked_items.append((coord, item))

    def collect_animal(self) -> None:
        """
        Update game state when the player collects an animal.
        Postcondition:
            - self.collected_animals is incremented by 1
            - "animal" is appended to self.collected_items
            - Observers are notified with "ANIMAL_COLLECTED"
        """
        self.collected_animals += 1
        assert self.collected_animals <= self.total_animals, (
            "collected_animals cannot exceed total_animals."
        )
        self.collected_items.append("animal")  
        self.notify_observers("ANIMAL_COLLECTED")

    def undo_collect_item(self, item: Any) -> None:
        """
        Undo collection of a previously collected item.
        This method finds the last matching item (by type) and removes it.
        Precondition:
            - item is not None
        Postcondition:
            - If item was of type 'rock', 'flower', or 'animal', that item type is removed 
              once from self.collected_items
            - If item was an animal, self.collected_animals is decremented by 1, down to 0
            - Observers are notified with "ITEM_COLLECTED"
        """
        assert item is not None, "item must not be None."
        item_type: Optional[str] = None
        if "rock" in str(type(item)).lower():
            item_type = "rock"
        elif "flower" in str(type(item)).lower():
            item_type = "flower"
        elif "animal" in str(type(item)).lower():
            item_type = "animal"

        # Remove the LAST matching item from collected_items (to preserve strategy logic)
        for i in reversed(range(len(self.collected_items))):
            if self.collected_items[i] == item_type:
                del self.collected_items[i]
                break

        if item_type == "animal":
            self.collected_animals = max(0, self.collected_animals - 1)

        self.notify_observers("ITEM_COLLECTED")

    def set_game_state(self, new_state: GameState) -> None:
        """
        Change the game state if it is valid.
        
        Preconditions:
            - new_state must be one of GameState.PLAYING, GameState.WIN, or GameState.LOSE.

        Postcondition:
            - self.state is updated accordingly
            - If state == GameState.LOSE, notify observers with "LOSE"
            - If state == GameState.WIN, notify observers with "WIN"
        """
        assert isinstance(new_state, GameState), "new_state must be an instance of GameState enum."
        assert new_state in (GameState.PLAYING, GameState.WIN, GameState.LOSE), "new_state must be a valid GameState."
        if isinstance(new_state, GameState):
            self.state = new_state
        else:
            raise ValueError("new_state must be an instance of GameState enum.")
        
        if new_state == GameState.LOSE:
            self.notify_observers("LOSE")
        elif new_state == GameState.WIN:
            self.notify_observers("WIN")

    def get_state(self) -> GameState:
        """Retrieve the current game state."""
        return self.state

    def get_collected_items(self) -> List[Any]:
        """Retrieve the collected items."""
        return self.collected_items
    
    def is_game_over(self) -> bool:
        """Returns True if the game is over."""
        return self.state == GameState.LOSE
    
    def is_win(self) -> bool:
        """Returns True if the game is won."""
        return self.state == GameState.WIN