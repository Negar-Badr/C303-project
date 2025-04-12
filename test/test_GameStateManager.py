import pytest
from project.GameStateManager import GameStateManager, GameState

class TestGameStateManagerSingleton:

    def setup_method(self):
        # Reset game state before each test
        GameStateManager().reset_game_state()

    def test_singleton_identity(self):
        """
        Test that the GameStateManager is a singleton.
        """
        manager1 = GameStateManager()
        manager2 = GameStateManager()
        assert manager1 is manager2, "GameManager should return the same instance"

    def test_singleton_state_shared(self):
        """
        Test that the game state is shared across instances.
        """
        manager1 = GameStateManager()
        manager2 = GameStateManager()
        manager1.state = GameState.PLAYING
        assert manager2.state == GameState.PLAYING, "GameManager instances should share state"

    def test_singleton_id_is_same(self):
        """
        Test that the GameStateManager is a singleton by checking the memory address.
        """
        manager1 = GameStateManager()
        manager2 = GameStateManager()
        assert id(manager1) == id(manager2), "Singleton instances should have the same memory address"

    def test_reset_affects_all_references(self):
        """
        Test that resetting the game state affects all references to the singleton.
        """
        manager1 = GameStateManager()
        manager2 = GameStateManager()

        manager1.collected_items.append("flower")
        manager1.collected_animals = 5

        manager2.reset_game_state()

        assert manager1.collected_items == [], "Reset should clear collected items"
        assert manager1.collected_animals == 0, "Reset should reset animal count"
        assert manager1.state == GameState.PLAYING, "Reset should set state to PLAYING"

    def test_original_objects_storage(self):
        """
        Test that original objects are stored correctly in the singleton.
        """
        manager1 = GameStateManager()
        obj1 = object()
        coord1 = (1, 2)
        manager1.store_original_objects([(obj1, coord1)])

        manager2 = GameStateManager()
        stored = manager2.get_original_objects()

        assert stored[0][1] == coord1, "Original object coord should be stored"
        assert stored[0][0] is not obj1, "Original object should be deepcopied"

    class MockObserver:
        def __init__(self):
            self.notifications = []

        def on_notify(self, event):
            self.notifications.append(event)

    def test_observer_shared_across_instances(self):
        """
        Test that observers are shared across instances of the singleton.
        """
        observer = self.MockObserver()
        manager1 = GameStateManager()
        manager2 = GameStateManager()

        manager1.add_observer(observer)
        manager2.collect_item("rock")

        assert "ITEM_COLLECTED" in observer.notifications, "Observer should be notified from any instance"

    class DummyFlower:
        pass

    def test_undo_behavior_reflects_globally(self):
        """
        Test that undo behavior reflects across all instances of the singleton.
        """
        manager1 = GameStateManager()
        manager2 = GameStateManager()

        flower = self.DummyFlower()
        manager1.collect_item("flower")
        manager2.undo_collect_item(flower)

        assert "flower" not in manager1.collected_items, "Undo should reflect across singleton references"
