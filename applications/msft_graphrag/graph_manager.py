from dataclasses import dataclass
from tigergraphx import (
    Graph,
    GraphSchema,
    LoadingJobConfig,
)


@dataclass
class GraphManager:
    to_load_data: bool = True
    schema_path: str = "resources/graph_schema.yaml"
    loading_job_path: str = "resources/loading_job_config.yaml"

    def __post_init__(self):
        self.graph = Graph(
            graph_schema=GraphSchema.ensure_config(self.schema_path),
            drop_existing_graph=False,
        )
        if self.to_load_data:
            self.graph.load_data(
                loading_job_config=LoadingJobConfig.ensure_config(self.loading_job_path)
            )
            self.to_load_data = False
