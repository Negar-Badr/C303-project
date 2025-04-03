from .MovementStrategy import TeleportMovement, ShortestPathMovement, RandomMovement

class GameStateManager:
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
            self.hunter_strategy = RandomMovement()  # Strategy pattern for hunter movement
            self._initialized = True  # Mark as true at first 

    def collect_item(self, item):
        """Update game state when the player collects an item."""
        self.collected_items.append(item)
        print(f"Player collected: {item}")
        self.update_hunter_strategy() 

    def collect_animal(self, animal_name):
        """Update game state when the player collects an animal."""
        self.collected_animals += 1
        print(f"Player collected an animal: {animal_name} ({self.collected_animals}/{self.total_animals})")  

        self.collected_items.append("animal")  
        self.update_hunter_strategy()  

        if self.collected_animals >= self.total_animals:
            self.set_game_state("win")  #  Win condition triggered!

    def update_hunter_strategy(self):
        if not self.collected_items:
            self.hunter_strategy = RandomMovement()
            return

        last_rock_index = max((i for i, item in enumerate(self.collected_items) if "rock" in item), default=-1)
        last_flower_index = max((i for i, item in enumerate(self.collected_items) if "flower" in item), default=-1)
        has_animal = any("animal" in item for item in self.collected_items)

        if last_rock_index > last_flower_index: # it will always be teleport until the player picks up a flower
            self.hunter_strategy = TeleportMovement()

        elif has_animal: # at least once animal, then the hunter never goes back to shortest path
            self.hunter_strategy = ShortestPathMovement()

        elif last_flower_index != -1: # if doesnt have at least once animal, and we have a flower, hunter will be random 
            self.hunter_strategy = RandomMovement()

        print(f"Hunter strategy updated to: {self.hunter_strategy.__class__.__name__}")

    def set_game_state(self, state):
        """Change the game state."""
        if state in ["playing", "win", "lose"]:
            self.state = state
            print(f"Game state changed to: {self.state}")

    def get_state(self):
        """Retrieve the current game state."""
        return self.state

    def get_collected_items(self):
        """Retrieve the collected items."""
        return self.collected_items

    def get_hunter_strategy(self):
        """Retrieve the current hunter strategy."""
        return self.hunter_strategy
    
    def is_game_over(self):
        """Returns True if the game is over, preventing further movement."""
        return self.state == "lose"

