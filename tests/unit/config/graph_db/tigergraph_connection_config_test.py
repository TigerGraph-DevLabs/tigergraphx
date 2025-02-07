import pytest
from pydantic import ValidationError

from tigergraphx.config import TigerGraphConnectionConfig


class TestTigerGraphConnectionConfig:
    @pytest.fixture(autouse=True)
    def reset_env(self, monkeypatch):
        """
        Reset environment variables before each test to ensure a clean test environment.
        """
        env_vars = [
            "TG_HOST",
            "TG_RESTPP_PORT",
            "TG_GSQL_PORT",
            "TG_USERNAME",
            "TG_PASSWORD",
            "TG_SECRET",
            "TG_TOKEN",
        ]
        for var in env_vars:
            monkeypatch.delenv(var, raising=False)

    def test_default_values(self):
        """
        Test that the default configuration uses username/password authentication.
        """
        config = TigerGraphConnectionConfig()
        assert config.username is None
        assert config.password is None
        assert config.secret is None
        assert config.token is None
        assert str(config.host) == "http://127.0.0.1/"
        assert str(config.restpp_port) == "14240"
        assert str(config.gsql_port) == "14240"

    def test_valid_username_password(self):
        """
        Test configuration with valid username/password authentication.
        """
        config = TigerGraphConnectionConfig(
            username="admin", password="password123"
        )
        assert config.username == "admin"
        assert config.password == "password123"
        assert config.secret is None
        assert config.token is None

    def test_valid_secret_authentication(self):
        """
        Test configuration with valid secret-based authentication.
        """
        config = TigerGraphConnectionConfig(secret="my_secret")
        assert config.secret == "my_secret"
        assert config.username is None
        assert config.password is None
        assert config.token is None

    def test_valid_token_authentication(self):
        """
        Test configuration with valid token-based authentication.
        """
        config = TigerGraphConnectionConfig(token="my_token")
        assert config.token == "my_token"
        assert config.username is None
        assert config.password is None
        assert config.secret is None

    @pytest.mark.parametrize(
        "params",
        [
            {"username": "admin", "password": "password", "secret": "my_secret"},
            {"username": "admin", "password": "password", "token": "my_token"},
            {"secret": "my_secret", "token": "my_token"},
            {
                "username": "admin",
                "password": "password",
                "secret": "my_secret",
                "token": "my_token",
            },
        ],
    )
    def test_invalid_authentication_combinations(self, params):
        """
        Test that providing more than one authentication method raises a validation error.
        """
        with pytest.raises(
            ValueError,
            match="You can only use 'username/password' OR 'secret' OR 'token', not both.",
        ):
            TigerGraphConnectionConfig(**params)

    def test_missing_authentication(self):
        """
        Test that missing all authentication fields does not raise an error (defaults apply).
        """
        config = TigerGraphConnectionConfig()
        assert config.username is None
        assert config.password is None
        assert config.secret is None
        assert config.token is None

    @pytest.mark.parametrize(
        "port_value",
        ["14240", 14240, "9000", 9000],
    )
    def test_valid_port_values(self, port_value):
        """
        Test valid integer and string values for ports.
        """
        config = TigerGraphConnectionConfig(
            restpp_port=port_value, gsql_port=port_value
        )
        assert str(config.restpp_port) == str(port_value)
        assert str(config.gsql_port) == str(port_value)

    @pytest.mark.parametrize(
        "invalid_url",
        ["invalid_url", "htp://badurl.com", "://missing_scheme.com"],
    )
    def test_invalid_host_url(self, invalid_url):
        """
        Test that an invalid host URL raises a validation error.
        """
        with pytest.raises(ValidationError):
            TigerGraphConnectionConfig(host=invalid_url)
