import yaml
import json
from typing import Type, TypeVar, Dict
from pathlib import Path
from pydantic_settings import BaseSettings

T = TypeVar("T", bound="BaseConfig")


class BaseConfig(BaseSettings):
    @classmethod
    def ensure_config(cls: Type[T], config: T | Path | str | Dict) -> T:
        """
        Ensure the config is an instance of the current config class.
        If it's a path (YAML/JSON), string, or dictionary, load it as the current config class.
        """
        if isinstance(config, cls):
            return config
        elif isinstance(config, Dict):
            # Initialize from a dictionary
            return cls(**config)
        elif isinstance(config, (Path, str)):
            # Determine file type and load accordingly
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
