# TO RUN THE TEST (please follow the README): 
# PYTHONPATH="." pytest test -W ignore::DeprecationWarning 
import pytest
from project.GameStateManager import GameStateManager, GameState
from project.example_map import LockableDoor
from project.Hunter import Hunter
from project.imports import * 
from project.MovementStrategy import RandomMovement, TeleportMovement, ShortestPathMovement

class DummyObserver:
    def __init__(self):
        self.notifications = []

    def on_notify(self, event):
        self.notifications.append(event)

class TestObserverPattern:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """
        Setup method to initialize the GameStateManager and reset the game state for each test.
        """
        self.gsm = GameStateManager()
        self.gsm.reset_game_state()

    def test_add_and_notify_observer(self):
        """
        Test that an observer can be added and notified correctly.
        """
        observer = DummyObserver()
        self.gsm.add_observer(observer)

        self.gsm.notify_observers("ITEM_COLLECTED")

        assert "ITEM_COLLECTED" in observer.notifications, "Observer should receive notifications"

    def test_remove_observer(self):
        """
        Test that an observer can be removed and should not receive notifications.
        """
        observer = DummyObserver()
        self.gsm.add_observer(observer)
        self.gsm.remove_observer(observer)

        self.gsm.notify_observers("ITEM_COLLECTED")

        assert "ITEM_COLLECTED" not in observer.notifications, "Removed observer should not receive notifications"

    def test_lockable_door_unlocks_on_win(self): 
        """
        Test that a lockable door unlocks when the game state changes to GameState.WIN.
        """
        door = LockableDoor("int_entrance")
        door.lock()  # Manually lock the door
        assert door._locked is True

        self.gsm.add_observer(door)
        self.gsm.set_game_state(GameState.WIN)

        assert door._locked is False, "Door should unlock on WIN state"

    def test_lockable_door_locks_on_lose(self):
        """
        Test that a lockable door locks when the game state changes to GameState.LOSE.
        """
        door = LockableDoor("int_entrance")
        door.unlock()
        assert door._locked is False        

        self.gsm.add_observer(door)
        self.gsm.set_game_state(GameState.LOSE)
        assert door._locked is False, "Door should lock on LOSE state"

    def test_hunter_strategy_switches_on_flower_vs_rock(self):
        """
        Test that the hunter's movement strategy switches based on collected items.
        """
        hunter = Hunter(encounter_text="I caught you!")
        self.gsm.add_observer(hunter)

        # Case 1: Player picks up a rock first = TeleportMovement
        self.gsm.collected_items = ["rock"]
        self.gsm.notify_observers("ITEM_COLLECTED")
        assert isinstance(hunter.movement_strategy, TeleportMovement)

        # Case 2: Player picks up a flower after the rock = RandomMovement
        self.gsm.collected_items = ["rock", "flower"]
        self.gsm.notify_observers("ITEM_COLLECTED")
        assert isinstance(hunter.movement_strategy, RandomMovement)

        # Case 3: Player collects animal = ShortestPathMovement
        self.gsm.collected_items = ["rock", "flower", "animal"]
        self.gsm.notify_observers("ANIMAL_COLLECTED")
        assert isinstance(hunter.movement_strategy, ShortestPathMovement)

