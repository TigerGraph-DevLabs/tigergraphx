from dataclasses import dataclass


@dataclass
class TigerGraphConnectionConfig:
    host: str = "http://127.0.0.1"
    user_name: str = "tigergraph"
    password: str = "tigergraph"
    restpp_port: int | str = "9000"
    graph_studio_port: int | str = "14240"
