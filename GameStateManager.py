from .imports import *
from .Subject import Subject
from .Observer import Observer
import copy

class GameStateManager(Subject):
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
            self.state = "playing"  # Possible states: "playing", "win", "lose"
            self.collected_items = []  # Stores collected items (e.g., rock, flower)
            self.collected_animals = 0  # Count of collected animals
            self.total_animals = 12 # total animal to save
            self._initialized = True  # Mark as true at first 
            self.tracked_picked_items = []  # for undo support
            self.current_map = None
            self._original_objects = []  # NEW: original layout
            self._observers = [] # for the observer pattern
    
    def store_original_objects(self, objects):
        self._original_objects = [(copy.deepcopy(obj), coord) for obj, coord in objects]

    def get_original_objects(self):
        return self._original_objects

    def reset_game_state(self):
        self.state = "playing"
        self.collected_items.clear()
        self.collected_animals = 0
        self.tracked_picked_items.clear()
            
    def add_observer(self, observer: Observer):
        self._observers.append(observer)

    def remove_observer(self, observer: Observer):
        if observer in self._observers:
            self._observers.remove(observer)  
    
    def notify_observers(self, event):
        for observer in self._observers:
            observer.on_notify(self, event)  

    def collect_item(self, item):
        """Update game state when the player collects an item."""
        self.collected_items.append(item)
        self.notify_observers("ITEM_COLLECTED")
    
    def track_picked_item(self, item, coord):
        self.tracked_picked_items.append((coord, item))

    def collect_animal(self, animal_name):
        """Update game state when the player collects an animal."""
        self.collected_animals += 1
        self.collected_items.append("animal")  
        self.notify_observers("ANIMAL_COLLECTED")
        
        # if self.collected_animals >= self.total_animals:
        #     self.notify_observers("WIN")

    def undo_collect_item(self, item):
        item_type = None
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

    def set_game_state(self, state):
        """Change the game state."""
        if state in ["playing", "win", "lose"]:
            self.state = state
        if state == "lose":
            self.notify_observers("LOSE")
        if state == "win":
            self.notify_observers("WIN")

    def get_state(self):
        """Retrieve the current game state."""
        return self.state

    def get_collected_items(self):
        """Retrieve the collected items."""
        return self.collected_items
    
    def is_game_over(self):
        """Returns True if the game is over, preventing further movement."""
        return self.state == "lose"
    
    def is_win(self):
        """Returns True if the player has reached the door after collecting all 12 animals."""
        return self.state == "win"