import os
from dataclasses import dataclass
import numpy as np
from tqdm.asyncio import tqdm as tqdm_async
import asyncio

from lightrag.base import BaseVectorStorage
from lightrag.utils import logger

from tigergraphx import Graph


@dataclass
class TigerVectorStorage(BaseVectorStorage):
    def __post_init__(self):
        try:
            # Define the graph schema
            graph_schema = {
                "graph_name": f"Vector_{self.namespace}",
                "nodes": {
                    "Table": {
                        "primary_key": "id",
                        "attributes": {
                            "id": "STRING",
                            **{field: "STRING" for field in self.meta_fields},
                        },
                        "vector_attributes": {
                            "vector_attribute": self.embedding_func.embedding_dim,
                        },
                    }
                },
                "edges": {},
            }

            # Retrieve connection configuration from environment variables
            connection_config = {
                "host": os.environ.get("TG_HOST", "http://127.0.0.1"),
                "restpp_port": os.environ.get("TG_RESTPP_PORT", "14240"),
                "gsql_port": os.environ.get("TG_GSQL_PORT", "14240"),
                # Option 1: User/password authentication
                "username": os.environ.get("TG_USERNAME"),
                "password": os.environ.get("TG_PASSWORD"),
                # Option 2: Secret-based authentication
                "secret": os.environ.get("TG_SECRET"),
                # Option 3: Token-based authentication
                "token": os.environ.get("TG_TOKEN"),
            }

            # Initialize the graph
            self._graph = Graph(graph_schema, connection_config)
            self._max_batch_size = self.global_config["embedding_batch_num"]
        except Exception as e:
            logger.error(f"An error occurred during initialization: {e}")
            raise

    async def upsert(self, data: dict[str, dict]):
        """
        Insert or update data in the TigerGraph vector storage.
        """
        logger.info(f"Inserting {len(data)} vectors to {self.namespace}")
        if not len(data):
            logger.warning("No data to insert into the vector DB.")
            return []

        # Preparing the data for insertion
        list_data = [
            {
                "id": k,
                **{k1: v1 for k1, v1 in v.items() if k1 in self.meta_fields},
            }
            for k, v in data.items()
        ]

        contents = [v["content"] for v in data.values()]

        # Batch the data for embedding
        batches = [
            contents[i : i + self._max_batch_size]
            for i in range(0, len(contents), self._max_batch_size)
        ]

        async def wrapped_task(batch):
            result = await self.embedding_func(batch)
            pbar.update(1)
            return result

        embedding_tasks = [wrapped_task(batch) for batch in batches]
        pbar = tqdm_async(
            total=len(embedding_tasks), desc="Generating embeddings", unit="batch"
        )
        embeddings_list = await asyncio.gather(*embedding_tasks)

        embeddings = np.concatenate(embeddings_list)
        if len(embeddings) == len(list_data):
            for i, d in enumerate(list_data):
                d["vector_attribute"] = embeddings[i].tolist()
            results = self._graph.upsert(data=list_data, node_type="Table")
            return results
        else:
            # sometimes the embedding is not returned correctly. just log it.
            logger.error(
                f"embedding is not 1-1 with data, {len(embeddings)} != {len(list_data)}"
            )

    async def query(self, query: str, top_k=5):
        """
        Perform a vector search to find the most similar nodes based on the query vector.
        """
        embedding = await self.embedding_func([query])
        embedding = embedding[0]
        results = self._graph.search(
            data=embedding,
            vector_attribute_name="vector_attribute",
            node_type="Table",  # Specify the node type
            limit=top_k,  # Retrieve the top_k closest nodes
        )
        return results
