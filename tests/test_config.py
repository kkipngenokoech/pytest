import os
import pytest
from unittest.mock import patch
from src.core.config import Config

class TestConfig:
    def test_default_values(self):
        """Test that default configuration values are set correctly."""
        config = Config()
        assert config.debug is False
        assert config.database_url == 'sqlite:///app.db'
        assert config.secret_key == 'dev-secret-key'
        assert config.port == 8000
        assert config.host == '0.0.0.0'
    
    @patch.dict(os.environ, {
        'DEBUG': 'true',
        'DATABASE_URL': 'postgresql://localhost/test',
        'SECRET_KEY': 'test-secret',
        'PORT': '3000',
        'HOST': '127.0.0.1'
    })
    def test_environment_variables(self):
        """Test that environment variables override defaults."""
        config = Config()
        assert config.debug is True
        assert config.database_url == 'postgresql://localhost/test'
        assert config.secret_key == 'test-secret'
        assert config.port == 3000
        assert config.host == '127.0.0.1'
    
    def test_get_method(self):
        """Test the get method for retrieving config values."""
        config = Config()
        assert config.get('debug') is False
        assert config.get('nonexistent') is None
        assert config.get('nonexistent', 'default') == 'default'
    
    def test_set_method(self):
        """Test the set method for updating config values."""
        config = Config()
        config.set('custom_key', 'custom_value')
        assert config.get('custom_key') == 'custom_value'
    
    @patch.dict(os.environ, {'DEBUG': 'false'})
    def test_debug_false(self):
        """Test that DEBUG=false sets debug to False."""
        config = Config()
        assert config.debug is False
    
    @patch.dict(os.environ, {'PORT': 'invalid'})
    def test_invalid_port(self):
        """Test that invalid PORT value raises ValueError."""
        with pytest.raises(ValueError):
            Config()