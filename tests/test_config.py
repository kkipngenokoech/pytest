import os
import pytest
from unittest.mock import patch
from src.core.config import DatabaseConfig, AppConfig


class TestDatabaseConfig:
    def test_default_values(self):
        db_config = DatabaseConfig()
        assert db_config.host == "localhost"
        assert db_config.port == 5432
        assert db_config.name == "myapp"
        assert db_config.user == "postgres"
        assert db_config.password == ""
    
    def test_custom_values(self):
        db_config = DatabaseConfig(
            host="remote-host",
            port=3306,
            name="testdb",
            user="testuser",
            password="testpass"
        )
        assert db_config.host == "remote-host"
        assert db_config.port == 3306
        assert db_config.name == "testdb"
        assert db_config.user == "testuser"
        assert db_config.password == "testpass"
    
    @patch.dict(os.environ, {
        'DB_HOST': 'env-host',
        'DB_PORT': '9999',
        'DB_NAME': 'env-db',
        'DB_USER': 'env-user',
        'DB_PASSWORD': 'env-pass'
    })
    def test_from_env_with_all_vars(self):
        db_config = DatabaseConfig.from_env()
        assert db_config.host == "env-host"
        assert db_config.port == 9999
        assert db_config.name == "env-db"
        assert db_config.user == "env-user"
        assert db_config.password == "env-pass"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_with_defaults(self):
        db_config = DatabaseConfig.from_env()
        assert db_config.host == "localhost"
        assert db_config.port == 5432
        assert db_config.name == "myapp"
        assert db_config.user == "postgres"
        assert db_config.password == ""


class TestAppConfig:
    def test_default_values(self):
        app_config = AppConfig()
        assert app_config.debug is False
        assert app_config.secret_key == "dev-secret-key"
        assert isinstance(app_config.database, DatabaseConfig)
    
    def test_custom_values(self):
        db_config = DatabaseConfig(host="custom-host")
        app_config = AppConfig(
            debug=True,
            secret_key="custom-key",
            database=db_config
        )
        assert app_config.debug is True
        assert app_config.secret_key == "custom-key"
        assert app_config.database.host == "custom-host"
    
    @patch.dict(os.environ, {
        'DEBUG': 'true',
        'SECRET_KEY': 'env-secret',
        'DB_HOST': 'env-db-host'
    })
    def test_from_env_with_vars(self):
        app_config = AppConfig.from_env()
        assert app_config.debug is True
        assert app_config.secret_key == "env-secret"
        assert app_config.database.host == "env-db-host"
    
    @patch.dict(os.environ, {'DEBUG': 'false'})
    def test_from_env_debug_false(self):
        app_config = AppConfig.from_env()
        assert app_config.debug is False
    
    @patch.dict(os.environ, {'DEBUG': 'True'})
    def test_from_env_debug_case_insensitive(self):
        app_config = AppConfig.from_env()
        assert app_config.debug is True
    
    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_with_defaults(self):
        app_config = AppConfig.from_env()
        assert app_config.debug is False
        assert app_config.secret_key == "dev-secret-key"
        assert app_config.database.host == "localhost"
