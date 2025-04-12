import pytest
from project.GameStateManager import GameStateManager 

def test_singleton_identity():
    manager1 = GameStateManager()
    manager2 = GameStateManager()
    
    assert manager1 is manager2, "GameManager should return the same instance"

def test_singleton_state_shared():
    manager1 = GameStateManager()
    manager2 = GameStateManager()

    manager1.game_state = "playing"
    assert manager2.game_state == "playing", "GameManager instances should share state"

def test_singleton_id_is_same():
    manager1 = GameStateManager()
    manager2 = GameStateManager()
    assert id(manager1) == id(manager2), "Singleton instances should have the same memory address"
