[LightRAG](https://github.com/HKUDS/LightRAG) is an open-source RAG system that enhances LLMs by integrating graph-based structures into text indexing and retrieval. It overcomes the limitations of traditional RAG systems, such as fragmented answers and weak contextual awareness, by enabling dual-level retrieval for more comprehensive knowledge discovery. With support for incremental data updates, LightRAG ensures timely integration of new information while delivering improved retrieval accuracy and efficiency.

To run this Jupyter Notebook, you can download the original `.ipynb` file from [lightrag.ipynb](https://github.com/tigergraph/tigergraphx/tree/main/docs/graphrag/lightrag.ipynb).

---

## Prerequisites

- Before proceeding, complete the installation and setup steps outlined in the [Installation Guide](../getting_started/installation.md), including:

- Setting up Python and TigerGraph. See the [Requirements](../getting_started/installation.md#requirements) section for details.
- Installing TigerGraphX and its development dependencies. See the [Development Installation](../getting_started/installation.md#development-installation) section.
- Setting the required environment variables:  
  

   ```bash
   export TG_HOST=https://127.0.0.1
   export TG_USERNAME=tigergraph
   export TG_PASSWORD=tigergraph
   export OPENAI_API_KEY=<Your OpenAI API Key>
   ```

   These variables configure the connection to the TigerGraph server and OpenAI.

---

## Implementing Graph and Vector Storage with TigerGraph

LightRAG abstracts storage into components such as graph storage, key-value storage, and vector storage. You can explore the base classes **BaseGraphStorage**, **BaseVectorStorage**, and **BaseKVStorage** in the [source code](https://github.com/HKUDS/LightRAG/blob/main/lightrag/base.py).

This section demonstrates how to use **TigerGraphX** to implement:
1. **`BaseGraphStorage`** for storing and retrieving graph data in TigerGraph.
2. **`BaseVectorStorage`** for storing vector data and performing vector searches using TigerGraph's **TigerVector** feature.

### Implementing Graph Storage with TigerGraph

The following code defines the `TigerGraphStorage` class, which interfaces with **TigerGraphX** to manage graph data in TigerGraph.


```python
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

            # Initialize the graph
            self._graph = Graph(graph_schema)
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
```

#### Key Features:

1. **Graph Schema**  
   - Defines a node type `"Entity"` with attributes: `id`, `entity_type`, `description`, and `source_id`.
   - Defines an edge type `"relationship"` with attributes: `weight`, `description`, and `source_id`.

2. **Graph Initialization**  
   - Initializes the graph schema using **TigerGraphX**.

3. **Node and Edge Operations**  
   - **Node Operations**:
     - `has_node`: Checks if a node exists.
     - `get_node`: Retrieves node data.
     - `upsert_node`: Adds or updates a node.
     - `delete_node`: Removes a node.
   - **Edge Operations**:
     - `has_edge`: Checks if an edge exists.
     - `get_edge`: Retrieves edge data.
     - `upsert_edge`: Adds or updates an edge.

4. **Graph Metrics**  
   - `node_degree`: Returns a node’s connection count.
   - `edge_degree`: Computes the combined degrees of two nodes.

5. **Utility Functions**  
   - **`clean_quotes`**: Removes surrounding quotes from strings.
   - **`drop_graph`**: Deletes the entire graph.

#### Conclusion:
The `TigerGraphStorage` class provides an efficient way to manage graph data in TigerGraph, offering straightforward methods for storing, retrieving, and handling nodes, edges, and graph metrics.

### Implement Vector Storage with TigerGraph
The following code defines the `TigerVectorStorage` class, which enables storing and querying vector data (such as embeddings) in a TigerGraph database using **TigerGraphX**.


```python
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

            # Initialize the graph
            self._graph = Graph(graph_schema)
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

#### Key Features:

1. **Graph Schema**  
   - Defines a node type `"Table"` with attributes including an `id` and a vector field for storing embeddings.  
   - The vector attribute's dimension is determined by the `embedding_func`.

2. **Upsert Method**  
   - Inserts or updates vector data in the TigerGraph database.  
   - Batches the data and asynchronously generates embeddings using `embedding_func`, then stores them in the graph.

3. **Query Method**  
   - Performs vector search in the TigerGraph database to find the most similar nodes based on a query vector.  
   - Uses `embedding_func` to generate the query vector and retrieves the closest nodes.

#### Conclusion:
`TigerVectorStorage` facilitates efficient storage and retrieval of vector embeddings in TigerGraph, enabling seamless integration of vector search capabilities.

## Integrating Custom Graph and Vector Storage with LightRAG

Once the `TigerGraphStorage` and `TigerVectorStorage` classes are defined, they can be integrated into LightRAG. By subclassing LightRAG and extending its storage mapping, you can seamlessly replace or enhance the default storage backends with custom implementations.

Although modifying the LightRAG source code is an option, this example demonstrates how to achieve integration without altering the original code.

Below is the implementation of `CustomLightRAG`, which incorporates `TigerGraphStorage` and `TigerVectorStorage` into its storage mapping:


```python
from lightrag import LightRAG
from lightrag.lightrag import lazy_external_import


class CustomLightRAG(LightRAG):
    def _get_storage_class(self, storage_name: str) -> dict:
        """Override storage retrieval to use a custom storage mapping."""

        custom_storages = {
            "TigerGraphStorage": "__main__",
            "TigerVectorStorage": "__main__",
        }

        if storage_name in custom_storages:
            import_path = custom_storages[storage_name]
            return lazy_external_import(import_path, storage_name

        # Call the parent class's method to prevent infinite recursion
        return super()._get_storage_class(storage_name)
```

---

## Indexing
### Data Preparation
For this demo, we will use `applications/lightrag/data` as the working directory.

The input dataset, `input/clapnq_dev_answerable_orig.jsonl.10.txt`, is located in the working directory. It consists of the first ten records from the [original dataset](https://github.com/primeqa/clapnq/blob/main/original_documents/dev/clapnq_dev_answerable_orig.jsonl).

Additionally, we have another dataset, `clapnq_dev_answerable.jsonl.10`, for evaluation, stored in `applications/resources`. This dataset contains ten questions from the [annotated dataset](https://github.com/primeqa/clapnq/blob/main/annotated_data/dev/clapnq_dev_answerable.jsonl), each with corresponding context from the original dataset.

---

### Indexing
The following code sets up the working directory and demonstrates how to index a document using LightRAG:


```python
import logging
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed

import nest_asyncio
# Allow nested event loops in Jupyter Notebook without conflicts
nest_asyncio.apply()


working_dir = "../../applications/lightrag/data"

custom_rag = CustomLightRAG(
    working_dir=working_dir,
    embedding_func=openai_embed,
    llm_model_func=gpt_4o_mini_complete,
    graph_storage="TigerGraphStorage",
    vector_storage="TigerVectorStorage",
    kv_storage="JsonKVStorage",
)

with open(working_dir + "/input/clapnq_dev_answerable_orig.jsonl.10.txt") as f:
    custom_rag.insert(f.read())
```

**Note:** The output has been cleared due to its length, as most of it consists of logs.

Additionally, **TigerVector** is supported only in TigerGraph **v4.2.0 and later**.

## Querying
The following code demonstrates how to perform a query in LightRAG using the TigerGraph graph storage implementation.


```python
from lightrag import QueryParam

query = "where is the world's largest man made lake"

result = custom_rag.query(query=query, param=QueryParam(mode="hybrid"))

print("------------------- Query Result:  -------------------")
print(result)
```

    2025-02-28 20:21:58,215 - lightrag - INFO - Using hybrid mode for query processing
    2025-02-28 20:23:21,681 - lightrag - INFO - Global query uses 70 entites, 60 relations, 3 text units
    2025-02-28 20:23:21,683 - lightrag - INFO - Local query uses 60 entites, 32 relations, 3 text units
    ------------------- Query Result:  -------------------
    ### World's Largest Man-Made Lake
    
    The world's largest man-made lake is **Lake Kariba**, which is located on the Zambezi River, straddling the border between **Zambia** and **Zimbabwe**. The lake was created by the construction of the **Kariba Dam**, which significantly impacted the surrounding environment and local communities when it was completed between 1958 and 1963. 
    
    ### Key Features
    
    - **Size**: Lake Kariba has a surface area of approximately **5,580 square kilometers** and is known for its rich biodiversity, supporting various fish species and wildlife.
    - **Biodiversity**: The lake is home to numerous species, including **kapenta**, a fish introduced to enhance its ecological dynamics and commercial value.
    - **Economical Importance**: The lake plays a critical role in supporting the **tourism industry** for both Zambia and Zimbabwe, attracting visitors with its natural beauty and wildlife.
    
    Lake Kariba not only serves as a significant geographical landmark but also as a crucial resource for the economies of the surrounding nations.


## Evaluation
To evaluate the performance of LightRAG, we use TigerGraphX's `RagasEvaluator` class, which leverages Ragas for evaluation.

In the code below, we define the `prepare_evaluation_data` function to construct the evaluation dataset. This function processes `ragas_data` by extracting questions and ground-truth answers, then queries `custom_rag` to retrieve both context passages and generated responses. The extracted data is then structured into evaluation samples, where each sample includes the question, retrieved contexts, generated answer, and ground-truth answers from the `clapnq_dev_answerable.jsonl.10` dataset stored in `applications/resources`.


```python
from typing import Literal, cast

from tigergraphx.graphrag import RagasEvaluator

def query_light_rag(
    custom_rag,
    query,
    mode: Literal["naive", "hybrid"] = "hybrid",
    only_context=False,
):
    """Query LightRAG to retrieve context or generated responses."""
    param = QueryParam(mode=mode, only_need_context=only_context)
    result = custom_rag.query(query=query, param=param)
    return result


def prepare_evaluation_data(
    custom_rag,
    ragas_data,
    mode: Literal["naive", "hybrid"] = "hybrid",
):
    """Prepare evaluation dataset using queries from ragas_data."""
    eval_samples = []

    for row in ragas_data:
        question = row["input"]  # Adjust to match dataset structure
        ground_truths = [
            ans["answer"] for ans in row["output"]
        ]  # Extract ground truth answers

        # Extract passages from the dataset (context retrieval)
        retrieved_contexts = query_light_rag(
            custom_rag, question, mode, only_context=True
        )

        # Extract generated response from LightRAG
        response = query_light_rag(custom_rag, question, mode, only_context=False)

        eval_samples.append(
            {
                "question": question,
                "contexts": retrieved_contexts
                if isinstance(retrieved_contexts, list)
                else [retrieved_contexts],
                "answer": response,
                "ground_truth": ground_truths,
            }
        )
    return eval_samples
```

Next, we load the evaluation dataset from `clapnq_dev_answerable.jsonl.10`, which contains queries and ground-truth answers. We then use the `prepare_evaluation_data` function to generate evaluation samples by retrieving context passages and responses from `custom_rag`.

Once the evaluation dataset is prepared, we initialize the `RagasEvaluator` with the `gpt-4o` model and run the evaluation to assess LightRAG's performance.


```python
from datasets import Dataset, load_dataset
# Load datasets
dataset = load_dataset(
    "json",
    data_files="../../applications/resources/clapnq_dev_answerable.jsonl.10",
    split="train",
)
dataset = cast(Dataset, dataset)

# Prepare evaluation dataset
eval_samples = prepare_evaluation_data(custom_rag, dataset, "hybrid")

# Evaluate LightRAG
evaluator = RagasEvaluator(model="gpt-4o")

# Run evaluation
results = evaluator.evaluate_dataset(eval_samples)
```

    2025-02-28 20:31:01,776 - lightrag - INFO - Using hybrid mode for query processing
    2025-02-28 20:32:24,563 - lightrag - INFO - Global query uses 53 entites, 60 relations, 3 text units
    2025-02-28 20:32:24,565 - lightrag - INFO - Local query uses 60 entites, 24 relations, 3 text units
    2025-02-28 20:32:24,647 - lightrag - INFO - Using hybrid mode for query processing
    2025-02-28 20:32:34,144 - lightrag - INFO - Global query uses 53 entites, 60 relations, 3 text units
    2025-02-28 20:32:34,146 - lightrag - INFO - Local query uses 60 entites, 24 relations, 3 text units
    2025-02-28 20:32:41,812 - lightrag - INFO - Using hybrid mode for query processing
    2025-02-28 20:33:44,706 - lightrag - INFO - Global query uses 76 entites, 60 relations, 3 text units
    2025-02-28 20:33:47,394 - lightrag - INFO - Local query uses 60 entites, 40 relations, 3 text units
    2025-02-28 20:33:47,425 - lightrag - INFO - Using hybrid mode for query processing
    2025-02-28 20:33:55,750 - lightrag - INFO - Global query uses 76 entites, 60 relations, 3 text units
    2025-02-28 20:33:57,289 - lightrag - INFO - Local query uses 60 entites, 40 relations, 3 text units
    2025-02-28 20:34:03,817 - lightrag - INFO - Using hybrid mode for query processing
    2025-02-28 20:35:07,504 - lightrag - INFO - Global query uses 59 entites, 60 relations, 3 text units
    2025-02-28 20:35:10,693 - lightrag - INFO - Local query uses 60 entites, 39 relations, 3 text units
    2025-02-28 20:35:10,724 - lightrag - INFO - Using hybrid mode for query processing
    2025-02-28 20:35:19,992 - lightrag - INFO - Global query uses 59 entites, 60 relations, 3 text units
    2025-02-28 20:35:21,489 - lightrag - INFO - Local query uses 60 entites, 39 relations, 3 text units
    2025-02-28 20:35:26,577 - lightrag - INFO - Using hybrid mode for query processing
    2025-02-28 20:35:47,741 - lightrag - WARNING - Some nodes are missing, maybe the storage is damaged
    2025-02-28 20:36:22,940 - lightrag - INFO - Global query uses 71 entites, 60 relations, 3 text units
    2025-02-28 20:36:22,943 - lightrag - INFO - Local query uses 58 entites, 37 relations, 3 text units
    2025-02-28 20:36:22,982 - lightrag - INFO - Using hybrid mode for query processing
    2025-02-28 20:36:28,583 - lightrag - WARNING - Some nodes are missing, maybe the storage is damaged
    2025-02-28 20:36:30,848 - lightrag - INFO - Global query uses 71 entites, 60 relations, 3 text units
    2025-02-28 20:36:32,222 - lightrag - INFO - Local query uses 58 entites, 37 relations, 3 text units
    2025-02-28 20:36:36,151 - lightrag - INFO - Using hybrid mode for query processing
    2025-02-28 20:37:35,089 - lightrag - INFO - Global query uses 59 entites, 60 relations, 3 text units
    2025-02-28 20:38:01,468 - lightrag - INFO - Local query uses 60 entites, 125 relations, 3 text units
    2025-02-28 20:38:01,517 - lightrag - INFO - Using hybrid mode for query processing
    2025-02-28 20:38:10,021 - lightrag - INFO - Global query uses 59 entites, 60 relations, 3 text units
    2025-02-28 20:38:16,022 - lightrag - INFO - Local query uses 60 entites, 125 relations, 3 text units
    2025-02-28 20:38:21,065 - lightrag - INFO - Using hybrid mode for query processing
    2025-02-28 20:39:28,932 - lightrag - INFO - Global query uses 61 entites, 60 relations, 3 text units
    2025-02-28 20:39:28,935 - lightrag - INFO - Local query uses 60 entites, 95 relations, 3 text units
    2025-02-28 20:39:28,977 - lightrag - INFO - Using hybrid mode for query processing
    2025-02-28 20:39:40,160 - lightrag - INFO - Global query uses 61 entites, 60 relations, 3 text units
    2025-02-28 20:39:40,162 - lightrag - INFO - Local query uses 60 entites, 95 relations, 3 text units
    2025-02-28 20:39:51,972 - lightrag - INFO - Using hybrid mode for query processing
    2025-02-28 20:39:52,129 - openai._base_client - INFO - Retrying request to /embeddings in 0.436530 seconds
    2025-02-28 20:40:52,287 - lightrag - INFO - Global query uses 68 entites, 60 relations, 3 text units
    2025-02-28 20:40:52,290 - lightrag - INFO - Local query uses 60 entites, 36 relations, 3 text units
    2025-02-28 20:40:52,339 - lightrag - INFO - Using hybrid mode for query processing
    2025-02-28 20:41:01,041 - lightrag - INFO - Global query uses 68 entites, 60 relations, 3 text units
    2025-02-28 20:41:02,383 - lightrag - INFO - Local query uses 60 entites, 36 relations, 3 text units
    2025-02-28 20:41:10,024 - lightrag - INFO - Using hybrid mode for query processing
    2025-02-28 20:41:31,041 - lightrag - WARNING - Some nodes are missing, maybe the storage is damaged
    2025-02-28 20:42:11,316 - lightrag - INFO - Global query uses 81 entites, 60 relations, 3 text units
    2025-02-28 20:42:11,319 - lightrag - INFO - Local query uses 57 entites, 43 relations, 3 text units
    2025-02-28 20:42:11,351 - lightrag - INFO - Using hybrid mode for query processing
    2025-02-28 20:42:17,018 - lightrag - WARNING - Some nodes are missing, maybe the storage is damaged
    2025-02-28 20:42:19,114 - lightrag - INFO - Global query uses 81 entites, 60 relations, 3 text units
    2025-02-28 20:42:20,809 - lightrag - INFO - Local query uses 57 entites, 43 relations, 3 text units
    2025-02-28 20:42:30,206 - lightrag - INFO - Using hybrid mode for query processing
    2025-02-28 20:42:30,375 - openai._base_client - INFO - Retrying request to /embeddings in 0.428693 seconds
    2025-02-28 20:43:28,485 - lightrag - INFO - Global query uses 56 entites, 60 relations, 3 text units
    2025-02-28 20:43:43,044 - lightrag - INFO - Local query uses 60 entites, 109 relations, 3 text units
    2025-02-28 20:43:43,080 - lightrag - INFO - Using hybrid mode for query processing
    2025-02-28 20:43:47,577 - lightrag - INFO - Global query uses 56 entites, 60 relations, 3 text units
    2025-02-28 20:43:48,136 - openai._base_client - INFO - Retrying request to /embeddings in 0.396963 seconds
    2025-02-28 20:43:58,277 - lightrag - INFO - Local query uses 60 entites, 109 relations, 3 text units



    Evaluating:   0%|          | 0/40 [00:00<?, ?it/s]


    2025-02-28 20:44:08,812 - openai._base_client - INFO - Retrying request to /chat/completions in 0.480058 seconds
    2025-02-28 20:44:08,814 - openai._base_client - INFO - Retrying request to /chat/completions in 0.397422 seconds
    2025-02-28 20:47:02,781 - ragas.executor - ERROR - Exception raised in Job[3]: TimeoutError()
    2025-02-28 20:47:02,788 - ragas.executor - ERROR - Exception raised in Job[2]: TimeoutError()
    2025-02-28 20:47:03,337 - tigergraphx.graphrag.evaluation.ragas_evaluator - INFO - Evaluation results: {'answer_relevancy': 0.8976, 'faithfulness': 0.6659, 'llm_context_precision_with_reference': 0.5556, 'context_recall': 0.4444}


The final line displays the evaluation results:

`Evaluation results: {'answer_relevancy': 0.8976, 'faithfulness': 0.6659, 'llm_context_precision_with_reference': 0.5556, 'context_recall': 0.4444}`

---
## Reset

After completing the evaluation, it is recommended to clean up the environment by removing the previously created graphs. The following code iterates through a list of graph names and attempts to drop each graph from the TigerGraph database. If a graph does not exist or an error occurs during deletion, the error message is printed.


```python
from tigergraphx import Graph

graphs_to_drop = [
    "LightRAG",
    "Vector_chunks",
    "Vector_entities",
    "Vector_relationships",
]
for graph_name in graphs_to_drop:
    try:
        G = Graph.from_db(graph_name)
        G.drop_graph()
    except Exception as e:
        print(f"Error message: {str(e)}")
```

    2025-02-28 20:50:07,250 - tigergraphx.core.managers.schema_manager - INFO - Dropping graph: LightRAG...
    2025-02-28 20:50:10,802 - tigergraphx.core.managers.schema_manager - INFO - Graph dropped successfully.
    2025-02-28 20:50:10,840 - tigergraphx.core.managers.schema_manager - INFO - Dropping graph: Vector_chunks...
    2025-02-28 20:50:14,019 - tigergraphx.core.managers.schema_manager - INFO - Graph dropped successfully.
    2025-02-28 20:50:14,050 - tigergraphx.core.managers.schema_manager - INFO - Dropping graph: Vector_entities...
    2025-02-28 20:50:17,205 - tigergraphx.core.managers.schema_manager - INFO - Graph dropped successfully.
    2025-02-28 20:50:17,268 - tigergraphx.core.managers.schema_manager - INFO - Dropping graph: Vector_relationships...
    2025-02-28 20:50:20,638 - tigergraphx.core.managers.schema_manager - INFO - Graph dropped successfully.


---

## Next Steps

- [Supporting Microsoft’s GraphRAG: Part 1](msft_graphrag_1.md): Demonstrates how to integrate TigerGraph with Microsoft's GraphRAG.

---

Start transforming your GraphRAG workflows with the power of **TigerGraphX** today!
