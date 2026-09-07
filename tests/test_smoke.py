import pytest


class TestSmoke:
    """Quick sanity checks for plugin functionality."""

    def test_plugin_imports(self, mock_qgis_modules):
        """Test plugin can be imported."""
        from ohsome_osm_downloader import MinimalPlugin, classFactory
        assert MinimalPlugin is not None
        assert classFactory is not None

    def test_plugin_instantiates(self, plugin_instance):
        """Test plugin can be instantiated."""
        assert plugin_instance is not None

    def test_plugin_initGui(self, plugin_instance):
        """Test plugin initialization."""
        plugin_instance.initGui()
        assert plugin_instance.action is not None

    def test_plugin_run(self, plugin_instance):
        """Test plugin run method."""
        plugin_instance.initGui()
        plugin_instance.run()

    def test_plugin_unload(self, plugin_instance):
        """Test plugin cleanup."""
        plugin_instance.initGui()
        plugin_instance.unload()