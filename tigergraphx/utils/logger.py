# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

import logging
import logging.config
import os
from pathlib import Path
import yaml

DEFAULT_LOGGING_CONFIG = (
    Path(__file__).resolve().parent.parent / "config/logging_config.yaml"
)


def setup_logging(config_path=None):
    """Setup logging configuration from YAML file."""
    config_path = config_path or DEFAULT_LOGGING_CONFIG
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Logging configuration file not found: {config_path}")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        logging.config.dictConfig(config)


# Automatically setup logging when the module is imported
setup_logging()
