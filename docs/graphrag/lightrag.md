[LightRAG](https://github.com/HKUDS/LightRAG) is an open-source RAG system that enhances LLMs by integrating graph-based structures into text indexing and retrieval. It overcomes the limitations of traditional RAG systems, such as fragmented answers and weak contextual awareness, by enabling dual-level retrieval for more comprehensive knowledge discovery. With support for incremental data updates, LightRAG ensures timely integration of new information while delivering improved retrieval accuracy and efficiency.

To run this Jupyter Notebook, you can download the original `.ipynb` file from [lightrag.ipynb](https://github.com/tigergraph/tigergraphx/tree/main/docs/graphrag/lightrag.ipynb).

---

## Prerequisites

Before proceeding, ensure you’ve completed the installation and setup steps outlined in the [Installation Guide](../getting_started/installation.md), including:

- Setting up Python and TigerGraph. For more details, refer to the [Requirements](../../getting_started/installation/#requirements) section.
- Install TigerGraphX along with its development dependencies. For more details, refer to the [Development Installation](../../getting_started/installation/#development-installation) section.
- Set the environment variables **`TG_HOST`**, **`TG_USERNAME`**, and **`TG_PASSWORD`**, which are required to connect to the TigerGraph server, as well as **`OPENAI_API_KEY`** for connecting to OpenAI. Use a command like the following to set these variables:  

   ```bash
   export TG_HOST=https://127.0.0.1
   export TG_USERNAME=tigergraph
   export TG_PASSWORD=tigergraph
   export OPENAI_API_KEY=<your_key>
   ```


---

## Implement Graph and Vector Storage with TigerGraph

In LightRAG, storage layers are abstracted into components such as graph storage, key-value storage, and vector storage. You can explore the base classes **BaseGraphStorage**, **BaseVectorStorage**, and **BaseKVStorage** in the [source code](https://github.com/HKUDS/LightRAG/blob/main/lightrag/base.py).

In this section, we will demonstrate how to use TigerGraphX to implement the `BaseGraphStorage` class for storing and retrieving graph data in TigerGraph. Additionally, we will show how to implement the `BaseVectorStorage` class for storing vector data and performing vector searches using the TigerVector feature in TigerGraph.

### Implement Graph Storage with TigerGraph


```python
import os
from dataclasses import dataclass
from typing import Any, Dict
import numpy as np

from lightrag.base import BaseGraphStorage
from lightrag.utils import logger

from tigergraphx import Graph


@dataclass
class TigerGraphStorage(BaseGraphStorage):
    def __post_init__(self):
        try:
            # Define the graph schema
            graph_schema = {
                "graph_name": "LightRAG",
                "nodes": {
                    "Entity": {
                        "primary_key": "id",
                        "attributes": {
                            "id": "STRING",
                            "entity_type": "STRING",
                            "description": "STRING",
                            "source_id": "STRING",
                        },
                    }
                },
                "edges": {
                    "relationship": {
                        "is_directed_edge": False,
                        "from_node_type": "Entity",
                        "to_node_type": "Entity",
                        "attributes": {
                            "weight": "DOUBLE",
                            "description": "STRING",
                            "keywords": "STRING",
                            "source_id": "STRING",
                        },
                    }
                },
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
        except Exception as e:
            logger.error(f"An error occurred during initialization: {e}")
            raise

    @staticmethod
    def clean_quotes(value: str) -> str:
        """Remove leading and trailing &quot; from a string if present."""
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        return value

    async def has_node(self, node_id: str) -> bool:
        return self._graph.has_node(self.clean_quotes(node_id))

    async def has_edge(self, source_node_id: str, target_node_id: str) -> bool:
        return self._graph.has_edge(
            self.clean_quotes(source_node_id), self.clean_quotes(target_node_id)
        )

    async def node_degree(self, node_id: str) -> int:
        result = self._graph.degree(self.clean_quotes(node_id))
        return result

    async def edge_degree(self, src_id: str, tgt_id: str) -> int:
        return self._graph.degree(self.clean_quotes(src_id)) + self._graph.degree(
            self.clean_quotes(tgt_id)
        )

    async def get_node(self, node_id: str) -> dict | None:
        result = self._graph.get_node_data(self.clean_quotes(node_id))
        return result

    async def get_edge(self, source_node_id: str, target_node_id: str) -> dict | None:
        result = self._graph.get_edge_data(
            self.clean_quotes(source_node_id), self.clean_quotes(target_node_id)
        )
        return result

    async def get_node_edges(self, source_node_id: str) -> list[tuple[str, str]] | None:
        source_node_id = self.clean_quotes(source_node_id)
        if self._graph.has_node(source_node_id):
            edges = self._graph.get_node_edges(source_node_id)
            return list(edges)
        return None

    async def upsert_node(self, node_id: str, node_data: Dict[str, Any]):
        node_id = self.clean_quotes(node_id)
        self._graph.add_node(node_id, **node_data)

    async def upsert_edge(
        self, source_node_id: str, target_node_id: str, edge_data: Dict[str, Any]
    ):
        source_node_id = self.clean_quotes(source_node_id)
        target_node_id = self.clean_quotes(target_node_id)
        self._graph.add_edge(source_node_id, target_node_id, **edge_data)

    async def delete_node(self, node_id: str):
        if self._graph.has_node(node_id):
            self._graph.remove_node(node_id)
            logger.info(f"Node {node_id} deleted from the graph.")
        else:
            logger.warning(f"Node {node_id} not found in the graph for deletion.")

    async def embed_nodes(self, algorithm: str) -> tuple[np.ndarray, list[str]]:
        return np.array([]), []

    def drop_graph(self) -> None:
        self._graph.drop_graph()
```

This code defines the `TigerGraphStorage` class, which interacts with **TigerGraphX** to manage graph data in TigerGraph.

#### Key Features:

1. **Graph Schema**  
   - Defines a node type `"Entity"` with attributes like `id`, `entity_type`, `description`, and `source_id`.
   - Defines an edge type `"relationship"` with attributes like `weight`, `description`, and `source_id`.

2. **Graph Initialization**  
   - Initializes the graph with the schema using **TigerGraphX**.
   - Connection details (host, ports, authentication) are fetched from environment variables.

3. **Node and Edge Operations**  
   - **Node Operations**:
     - `has_node`: Checks if a node exists.
     - `get_node`: Gets data for a node.
     - `upsert_node`: Adds or updates a node.
     - `delete_node`: Deletes a node.
   - **Edge Operations**:
     - `has_edge`: Checks if an edge exists.
     - `get_edge`: Gets data for an edge.
     - `upsert_edge`: Adds or updates an edge.

4. **Graph Metrics**  
   - `node_degree`: Returns the number of connections a node has.
   - `edge_degree`: Calculates the combined degrees of two nodes.

5. **Additional Functions**  
   - **`clean_quotes`**: Strips quotes from strings.
   - **`drop_graph`**: Deletes the entire graph.

#### Conclusion:
The `TigerGraphStorage` class helps manage and interact with graph data in TigerGraph by offering simple methods for storing, retrieving, and managing nodes, edges, and graph metrics.

### Implement Vector Storage with TigerGraph


```python
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
        embedding = embedding[0].tolist()
        results = self._graph.search(
            data=embedding,
            vector_attribute_name="vector_attribute",
            node_type="Table",  # Specify the node type
            limit=top_k,  # Retrieve the top_k closest nodes
        )
        return results
```

This code defines the `TigerVectorStorage` class, which is used for storing and querying vector data (like embeddings) in a TigerGraph database using **TigerGraphX**.

#### Key Features:

1. **Graph Schema**  
   - The graph schema defines a node type called `"Table"`, which has attributes including an `id` and a vector attribute for storing embeddings. The vector attribute's dimension is based on the `embedding_func`.

2. **Upsert Method**  
   - The `upsert` method inserts or updates vector data in the TigerGraph database. It batches the data and generates embeddings asynchronously using `embedding_func`, then stores these embeddings in the graph.

3. **Query Method**  
   - The `query` method performs a vector search in the TigerGraph database to find the most similar nodes based on a query vector. It uses the `embedding_func` to generate the query vector and then queries the database for the closest nodes.

#### Conclusion:
`TigerVectorStorage` enables the use of vector embeddings in TigerGraph, allowing for efficient storage and search of vector data.

## Integrating Custom Graph and Vector Storage with LightRAG

After defining the `TigerGraphStorage` and `TigerVectorStorage` classes, we integrate them into LightRAG. By subclassing LightRAG and extending its storage mapping, you can easily replace or augment the default storage backends with your custom solutions.

While modifying the LightRAG source code is another option, this example demonstrates how to achieve the integration without altering the original source code.

Below is the code for creating a `CustomLightRAG` class that incorporates both `TigerGraphStorage` and `TigerVectorStorage` into its storage mapping.



```python
from lightrag import LightRAG


# Define a subclass to include your custom graph storage in the storage mapping
class CustomLightRAG(LightRAG):
    def _get_storage_class(self):
        # Extend the default storage mapping with your custom storage
        base_mapping = super()._get_storage_class()
        base_mapping["TigerGraphStorage"] = TigerGraphStorage
        base_mapping["TigerVectorStorage"] = TigerVectorStorage
        return base_mapping
```

---

## Indexing
### Data Preparation
#### Set Up Working Directory
Create a folder to serve as the working directory. For this demo, we will use `applications/lightrag/data`.

Next, create an `input` folder inside the `data` directory to store the documents you want to index:  

```bash
mkdir -p applications/lightrag/data/input
```

#### Add Documents to the Input Folder
Copy your documents (e.g., `fin.txt`) into the `applications/lightrag/data/input` folder. Ensure that the JSON files in the `applications/lightrag/data` folder are removed before rerunning the Jupyter Notebook.

---

### Indexing
The following code sets up a working directory and demonstrates how to index a given document using LightRAG.


```python
import logging
import nest_asyncio
# Use the nest_asyncio package to allow running nested event loops in Jupyter Notebook without conflicts.
nest_asyncio.apply()


working_dir = "../../applications/lightrag/data"

custom_rag = CustomLightRAG(
    working_dir=working_dir,
    graph_storage="TigerGraphStorage",
    # Use TigerGraph for storing vectors.
    # To switch to the default vector database in LightRAG, comment out the line below.
    vector_storage="TigerVectorStorage",
)

with open(working_dir + "/input/book.txt") as f:
    custom_rag.insert(f.read())
```

    2025-01-09 17:01:20,891 - lightrag - INFO - Logger initialized for working directory: ../../applications/lightrag/data
    2025-01-09 17:01:20,893 - lightrag - INFO - Load KV llm_response_cache with 2 data
    2025-01-09 17:01:20,896 - lightrag - INFO - Load KV full_docs with 1 data
    2025-01-09 17:01:20,900 - lightrag - INFO - Load KV text_chunks with 42 data
    2025-01-09 17:01:21,017 - tigergraphx.core.graph.base_graph - INFO - Creating schema for graph LightRAG...
    2025-01-09 17:01:21,052 - tigergraphx.core.graph.base_graph - INFO - Schema created successfully.
    2025-01-09 17:01:21,054 - tigergraphx.core.graph.base_graph - INFO - Creating schema for graph Vector_entities...
    2025-01-09 17:01:21,064 - tigergraphx.core.graph.base_graph - INFO - Schema created successfully.
    2025-01-09 17:01:21,066 - tigergraphx.core.graph.base_graph - INFO - Creating schema for graph Vector_relationships...
    2025-01-09 17:01:21,076 - tigergraphx.core.graph.base_graph - INFO - Schema created successfully.
    2025-01-09 17:01:21,078 - tigergraphx.core.graph.base_graph - INFO - Creating schema for graph Vector_chunks...
    2025-01-09 17:01:21,105 - tigergraphx.core.graph.base_graph - INFO - Schema created successfully.
    2025-01-09 17:01:21,108 - lightrag - WARNING - All docs are already in the storage


Please note that the output has been cleared here due to its length, as most of the content consists of logs.

Additionally, TigerVector is supported only in TigerGraph version 4.2.0 and later. If you're using a version prior to 4.2.0, you can comment out the line `vector_storage="TigerVectorStorage",` to use the default vector database in LightRAG.

## Querying
The following code demonstrates how to perform a query in LightRAG using the TigerGraph graph storage implementation.


```python
from lightrag import QueryParam

query = "What are the top themes in this story?"

result = custom_rag.query(query=query, param=QueryParam(mode="hybrid"))

print("------------------- Query Result:  -------------------")
print(result)
```

    2025-01-09 17:01:24,700 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    2025-01-09 17:01:24,709 - lightrag - INFO - kw_prompt result:
    {
      "high_level_keywords": ["Themes", "Story analysis"],
      "low_level_keywords": ["Character development", "Conflict", "Symbolism", "Plot", "Setting"]
    }
    2025-01-09 17:01:25,732 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-01-09 17:03:32,444 - lightrag - INFO - Local query uses 60 entites, 80 relations, 3 text units
    2025-01-09 17:03:33,135 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
    2025-01-09 17:04:46,561 - lightrag - INFO - Global query uses 47 entites, 60 relations, 3 text units
    2025-01-09 17:05:01,598 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
    ------------------- Query Result:  -------------------
    In Charles Dickens' "A Christmas Carol," several prominent themes intertwine within the narrative, reflecting the transformative journey of the central character, Ebenezer Scrooge. These themes serve as moral lessons that resonate deeply with readers and highlight the societal issues of Dickens' time.
    
    ### Redemption and Transformation
    
    The theme of redemption stands out as one of the most significant aspects of Scrooge's character arc. Initially portrayed as a miserly and cold-hearted individual, Scrooge’s encounters with various spirits—most notably the Spirit of Christmas Past, the Spirit of Christmas Present, and the Spirit of Christmas Yet to Come—underscore his potential for change. Through these supernatural visitations, Scrooge comes to realize the consequences of his actions and attitudes toward others, particularly his neglect of the less fortunate. This realization serves as a catalyst for his transformation from a figure of disdain to one of generosity and kindness, ultimately embodying the spirit of Christmas.
    
    ### The Spirit of Christmas
    
    Another essential theme revolves around the essence of Christmas itself, characterized by joy, goodwill, and communal spirit. Christmas is portrayed as a time of reflection, compassion, and generosity, contrasting sharply with Scrooge’s initial cynicism. Dickens emphasizes that the holiday season is an opportunity for individuals to reconnect with their humanity, fostering relationships and nurturing feelings of empathy. Instances within the story, such as the Cratchit family's humble Christmas dinner, reveal how love and celebration can thrive even amidst hardship, highlighting the importance of community and kind-heartedness.
    
    ### Compassion and Social Responsibility
    
    Compassion emerges as a vital theme, urging recognition of the struggles faced by the less fortunate. Scrooge’s initial apathy towards the needy epitomizes societal indifference, reflected in his dismissive responses to the pleas for charitable contributions. In stark contrast, the Cratchit family, particularly through the character of Tiny Tim, embodies the spirit of resilience and hope despite their economic hardships. Dickens employs Tiny Tim's situation to showcase the impact of poverty, advocating for social responsibility and awareness of those less fortunate. Scrooge's eventual embracing of compassion signifies a shift from self-interest to a broader understanding that one’s moral obligations extend to the community at large.
    
    ### The Consequences of Isolation
    
    The narrative also explores the repercussions of isolation and disconnection. Scrooge, who initially chooses solitude over companionship, experiences profound loneliness, which blinds him to the joys of life and the importance of human connections. His relationships with characters such as his nephew Fred, who embodies the spirit of family and celebration, illustrate the positive impact of social ties. The evolution of Scrooge's character highlights the essential human need for connection, revealing that true wealth lies not in material possessions but in shared experiences and relationships.
    
    ### Time and Reflection
    
    Lastly, the theme of time plays a critical role in Scrooge's transformation. His encounters with the spirits allow him to reflect on his past choices, current realities, and potential futures. The narrative demonstrates how reflecting on one's life can prompt significant personal growth and ultimately shape one's destiny. This exploration of time serves as a reminder that it is never too late to change one's path, advocating for mindfulness in one's actions and their implications.
    
    ### Conclusion
    
    In summary, "A Christmas Carol" is rich with themes of redemption, the spirit of Christmas, compassion, the effects of isolation, and the significance of time. Together, these themes contribute to a timeless narrative that not only entertains but also imparts profound moral lessons about the nature of humanity and the transformative power of kindness and generosity. Through Scrooge’s journey, Dickens encourages readers to embrace the festive spirit and recognize their roles as members of a compassionate community.

