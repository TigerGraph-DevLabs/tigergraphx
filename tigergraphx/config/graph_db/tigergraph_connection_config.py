from pydantic import HttpUrl, Field, field_validator

from tigergraphx.config import BaseConfig


class TigerGraphConnectionConfig(BaseConfig):
    host: HttpUrl = Field(
        default=HttpUrl("http://127.0.0.1"),
        description="The host URL for the TigerGraph connection.",
    )
    username: str = Field(
        default="tigergraph", description="The username for TigerGraph authentication."
    )
    password: str = Field(
        default="tigergraph", description="The password for TigerGraph authentication."
    )
    restpp_port: int | str = Field(
        default="9000", description="The port for REST++ API."
    )
    graph_studio_port: int | str = Field(
        default="14240", description="The port for Graph Studio."
    )

    @field_validator("host", mode="before")
    def add_http_if_missing(cls, value: str | HttpUrl) -> str | HttpUrl:
        # Add "http://" if the value doesn't already start with a scheme
        if isinstance(value, str) and not value.startswith(("http://", "https://")):
            value = f"http://{value}"
        return value
