import pytest


class TestMinimalPlugin:
    """Concise tests for MinimalPlugin."""

    def test_init(self, plugin_instance):
        """Plugin initializes with iface."""
        assert plugin_instance.iface is not None

    def test_initGui(self, plugin_instance, mock_iface):
        """initGui creates action and adds to toolbar."""
        plugin_instance.initGui()
        assert plugin_instance.action is not None
        mock_iface.addToolBarIcon.assert_called_once()

    def test_run(self, plugin_instance):
        """run executes without error."""
        plugin_instance.initGui()
        plugin_instance.run()

    def test_unload(self, plugin_instance, mock_iface):
        """unload removes toolbar icon."""
        plugin_instance.initGui()
        plugin_instance.unload()
        mock_iface.removeToolBarIcon.assert_called_once()