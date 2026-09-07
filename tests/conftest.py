"""Pytest configuration and fixtures for plugin tests."""

import sys
from unittest.mock import MagicMock, patch
from pathlib import Path

import pytest

# Add parent directory to path to import plugin modules
sys.path.insert(0, str(Path(__file__).parent.parent))


# Mock objects for QGIS components
class MockQAction(MagicMock):
    """Mock QAction class."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.triggered = MagicMock()


class MockQMessageBox(MagicMock):
    """Mock QMessageBox class."""
    @staticmethod
    def information(parent, title, message):
        """Mock information dialog."""
        pass

    @staticmethod
    def warning(parent, title, message):
        """Mock warning dialog."""
        pass

    @staticmethod
    def critical(parent, title, message):
        """Mock critical dialog."""
        pass


class MockInterface:
    """Mock QGIS interface (iface) object."""
    def __init__(self):
        self.mainWindow = MagicMock()
        self.addToolBarIcon = MagicMock()
        self.removeToolBarIcon = MagicMock()
        self.addDockWidget = MagicMock()
        self.removeDockWidget = MagicMock()
        self.layerTreeView = MagicMock()
        self.legendInterface = MagicMock()


@pytest.fixture
def mock_qgis_modules():
    """Mock QGIS modules to avoid import errors."""
    mocked_modules = {
        'qgis': MagicMock(),
        'qgis.PyQt': MagicMock(),
        'qgis.PyQt.QtWidgets': MagicMock(),
        'qgis.PyQt.QtCore': MagicMock(),
        'qgis.core': MagicMock(),
    }
    
    # Set up QtWidgets mocks
    mocked_modules['qgis.PyQt.QtWidgets'].QAction = MockQAction
    mocked_modules['qgis.PyQt.QtWidgets'].QMessageBox = MockQMessageBox
    
    sys.modules.update(mocked_modules)
    yield mocked_modules
    
    # Cleanup
    for key in mocked_modules:
        sys.modules.pop(key, None)


@pytest.fixture
def mock_iface(mock_qgis_modules):
    """Provide a mock QGIS interface object."""
    return MockInterface()


@pytest.fixture
def plugin_class(mock_qgis_modules):
    """Import and return the plugin class."""
    from minimal import MinimalPlugin
    return MinimalPlugin


@pytest.fixture
def plugin_instance(plugin_class, mock_iface):
    """Provide an initialized plugin instance."""
    return plugin_class(mock_iface)
