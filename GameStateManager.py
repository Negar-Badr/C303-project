
class GameStateManager:
    
    def __init__(self) -> None:
        self.__collected_animals = 0
        self.__state = ""
    
    def get_instance(self):
        return self.__state
    
    def update_state(self, newState):
        self.__state = newState
        
    def collect_animal(self):
        self.__collected_animals += 1
        
    def collect_item(self, item):
        if item.isInstance(Rock):
            self.__state = "teleport"
    