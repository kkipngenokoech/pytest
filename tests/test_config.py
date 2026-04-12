import os
import pytest
from unittest.mock import patch
from src.core.config import Config, config

class TestConfig:
    def test_default_values(self):
        with patch.dict(os.environ, {}, clear=True):
            test_config = Config()
            assert test_config.debug is False
            assert test_config.database_url == 'sqlite:///app.db'
            assert test_config.secret_key == 'dev-secret-key'
            assert test_config.port == 8000
            assert test_config.host == '0.0.0.0'
    
    def test_environment_variables(self):
        env_vars = {
            'DEBUG': 'true',
            'DATABASE_URL': 'postgresql://localhost/test',
            'SECRET_KEY': 'test-secret',
            'PORT': '3000',
            'HOST': '127.0.0.1'
        }
        with patch.dict(os.environ, env_vars, clear=True):
            test_config = Config()
            assert test_config.debug is True
            assert test_config.database_url == 'postgresql://localhost/test'
            assert test_config.secret_key == 'test-secret'
            assert test_config.port == 3000
            assert test_config.host == '127.0.0.1'
    
    def test_debug_parsing(self):
        with patch.dict(os.environ, {'DEBUG': 'True'}, clear=True):
            test_config = Config()
            assert test_config.debug is True
        
        with patch.dict(os.environ, {'DEBUG': 'false'}, clear=True):
            test_config = Config()
            assert test_config.debug is False
        
        with patch.dict(os.environ, {'DEBUG': 'invalid'}, clear=True):
            test_config = Config()
            assert test_config.debug is False
    
    def test_get_method(self):
        test_config = Config()
        assert test_config.get('debug') == test_config.debug
        assert test_config.get('DATABASE_URL') == test_config.database_url
        assert test_config.get('nonexistent') is None
        assert test_config.get('nonexistent', 'default') == 'default'
    
    def test_global_config_instance(self):
        assert config is not None
        assert isinstance(config, Config)
