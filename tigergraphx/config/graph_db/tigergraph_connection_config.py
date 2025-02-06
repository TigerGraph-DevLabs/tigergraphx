from typing import Any, Dict, Optional
from pydantic import HttpUrl, Field, model_validator
from pydantic_settings import SettingsConfigDict

from tigergraphx.config import BaseConfig


class TigerGraphConnectionConfig(BaseConfig):
    """
    Configuration for connecting to a TigerGraph instance.

    This class supports:

    1. User/password authentication
    2. Secret-based authentication
    3. Token-based authentication
    """

    model_config = SettingsConfigDict(populate_by_name=True)

    host: HttpUrl = Field(
        default=HttpUrl("http://127.0.0.1"),
        validation_alias="TG_HOST",
        description="The host URL for the TigerGraph connection.",
    )
    restpp_port: int | str = Field(
        default="14240", validation_alias="TG_RESTPP_PORT", description="The port for REST++ API."
    )
    gsql_port: int | str = Field(
        default="14240", validation_alias="TG_GSQL_PORT", description="The port for GSQL."
    )

    # User/password authentication
    username: Optional[str] = Field(
        default=None,
        validation_alias="TG_USERNAME",
        description="The username for TigerGraph authentication. Use only for user/password authentication.",
    )
    password: Optional[str] = Field(
        default=None,
        validation_alias="TG_PASSWORD",
        description="The password for TigerGraph authentication. Use only for user/password authentication.",
    )

    # Secret-based authentication
    secret: Optional[str] = Field(
        default=None,
        validation_alias="TG_SECRET",
        description="The secret for TigerGraph authentication. Use only for secret-based authentication.",
    )

    # Token-based authentication
    token: Optional[str] = Field(
        default=None,
        validation_alias="TG_TOKEN",
        description="The API token for TigerGraph authentication. Use only for token-based authentication.",
    )

    @model_validator(mode="before")
    def check_exclusive_authentication(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure that exactly one authentication method is provided:

        - username/password together, or
        - secret, or
        - token.
        If all fields are empty, username/password will default.

        Args:
            values: The input values for validation.

        Returns:
            The validated values.

        Raises:
            ValueError: If more than one authentication method is provided.
        """
        # Extract the values of the fields
        username = values.get("TG_USERNAME", values.get("username"))
        password = values.get("TG_PASSWORD", values.get("password"))
        secret = values.get("TG_SECRET", values.get("secret"))
        token = values.get("TG_TOKEN", values.get("token"))

        # Case 1: If all fields are empty, set default values for username and password
        if not username and not password and not secret and not token:
            # If all fields are empty, username/password will default.
            return values

        # Case 2: Both username and password provided (valid)
        if username and password:
            # Case 2A: Ensure secret and token are not provided
            if secret or token:
                raise ValueError(
                    "You can only use 'username/password' OR 'secret' OR 'token', not both."
                )
            return values

        # Case 3: Secret is provided (valid)
        if secret:
            # Case 3A: Ensure username/password and token are not provided
            if username or password or token:
                raise ValueError(
                    "You can only use 'username/password' OR 'secret' OR 'token', not both."
                )
            return values

        # Case 4: API token is provided (valid)
        if token:
            # Case 4A: Ensure username/password and secret are not provided
            if username or password or secret:
                raise ValueError(
                    "You can only use 'username/password' OR 'secret' OR 'token', not both."
                )
            return values

        # Case 5: If none of the valid authentication methods are provided
        raise ValueError(
            "You must provide either 'username/password', 'secret', or 'token' for authentication."
        )

    @classmethod
    def create(cls, **kwargs):
        """
        Allows initialization using both field names and aliases.
        """
        return cls.model_construct(**{**kwargs}, _by_alias=True)
