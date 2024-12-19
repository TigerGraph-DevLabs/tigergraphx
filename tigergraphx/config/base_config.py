import yaml
import json
from typing import Type, TypeVar, Dict
from pathlib import Path
from pydantic_settings import BaseSettings

T = TypeVar("T", bound="BaseConfig")


class BaseConfig(BaseSettings):
    """
    Base configuration class that extends Pydantic's BaseSettings.
    Provides utility methods to load configurations from various sources.
    """

    @classmethod
    def ensure_config(cls: Type[T], config: T | Path | str | Dict) -> T:
        """
        Ensure the config is an instance of the current config class.

        If the input is a dictionary, string, or path to a YAML/JSON file,
        it is loaded and converted into an instance of the class.

        Args:
            config (T | Path | str | Dict): The input configuration, which can be an instance
                of the config class, a dictionary, a file path, or a string.

        Returns:
            T: An instance of the current configuration class.

        Raises:
            FileNotFoundError: If the provided file path does not exist.
            ValueError: If the file type is unsupported.
            TypeError: If the input type is not supported.
        """
        if isinstance(config, cls):
            return config
        elif isinstance(config, Dict):
            return cls(**config)
        elif isinstance(config, (Path, str)):
            path = Path(config) if isinstance(config, str) else config
            if not path.exists():
                raise FileNotFoundError(f"Configuration file not found: {path}")
            if path.suffix in [".yaml", ".yml"]:
                with open(path, "r") as file:
                    config_data = yaml.safe_load(file)
            elif path.suffix == ".json":
                with open(path, "r") as file:
                    config_data = json.load(file)
            else:
                raise ValueError(f"Unsupported file type: {path.suffix}")
            return cls(**config_data)
        else:
            raise TypeError(
                f"Expected a {cls.__name__} instance, dict, str, or Path, but got {type(config)}."
            )
