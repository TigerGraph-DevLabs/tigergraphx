from typing import Optional
from pydantic import HttpUrl, Field, model_validator

from tigergraphx.config import BaseConfig


class TigerGraphConnectionConfig(BaseConfig):
    """
    Configuration for connecting to a TigerGraph instance.

    This class supports:
    1. User/password authentication
    2. Secret-based authentication
    3. Token-based authentication
    """

    host: HttpUrl = Field(
        default=HttpUrl("http://127.0.0.1"),
        description="The host URL for the TigerGraph connection.",
    )
    restpp_port: int | str = Field(
        default="14240", description="The port for REST++ API."
    )
    gsql_port: int | str = Field(
        default="14240", description="The port for GSQL."
    )

    # User/password authentication
    username: Optional[str] = Field(
        default="tigergraph",
        description="The username for TigerGraph authentication. Use only for user/password authentication.",
    )
    password: Optional[str] = Field(
        default="tigergraph",
        description="The password for TigerGraph authentication. Use only for user/password authentication.",
    )

    # Secret-based authentication
    secret: Optional[str] = Field(
        default=None,
        description="The secret for TigerGraph authentication. Use only for secret-based authentication.",
    )

    # Token-based authentication
    api_token: Optional[str] = Field(
        default=None,
        description="The API token for TigerGraph authentication. Use only for token-based authentication.",
    )

    @model_validator(mode="before")
    def check_exclusive_authentication(cls, values):
        """
        Ensure that exactly one authentication method is provided:
        - username/password together, or
        - secret, or
        - api_token.
        If all fields are empty, username/password will default.
        """
        # Extract the values of the fields
        username = values.get("username")
        password = values.get("password")
        secret = values.get("secret")
        api_token = values.get("api_token")

        # Case 1: If all fields are empty, set default values for username and password
        if not username and not password and not secret and not api_token:
            # If all fields are empty, username/password will default.
            return values

        # Case 2: Both username and password provided (valid)
        if username and password:
            # Case 2A: Ensure secret and api_token are not provided
            if secret or api_token:
                raise ValueError(
                    "You can only use 'username/password' OR 'secret' OR 'api_token', not both."
                )
            return values

        # Case 3: Secret is provided (valid)
        if secret:
            # Case 3A: Ensure username/password and api_token are not provided
            if username or password or api_token:
                raise ValueError(
                    "You can only use 'username/password' OR 'secret' OR 'api_token', not both."
                )
            return values

        # Case 4: API token is provided (valid)
        if api_token:
            # Case 4A: Ensure username/password and secret are not provided
            if username or password or secret:
                raise ValueError(
                    "You can only use 'username/password' OR 'secret' OR 'api_token', not both."
                )
            return values

        # Case 5: If none of the valid authentication methods are provided
        raise ValueError(
            "You must provide either 'username/password', 'secret', or 'api_token' for authentication."
        )
