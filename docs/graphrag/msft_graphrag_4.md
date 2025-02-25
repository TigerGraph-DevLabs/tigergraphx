# Supporting Microsoft’s GraphRAG: Part 4 - Hybrid Retrieval and Integration with LLM

To run this Jupyter Notebook, you can download the original `.ipynb` file from [msft_graphrag_4.ipynb](https://github.com/tigergraph/tigergraphx/tree/main/docs/graphrag/msft_graphrag_4.ipynb).

---

## Get the Graph from TigerGraph


```python
from tigergraphx import Graph
connection = {
    "host": "http://127.0.0.1",
    "username": "tigergraph",
    "password": "tigergraph",
}
G = Graph.from_db("GraphRAG", connection)
```

    2025-01-05 23:51:06,143 - tigergraphx.core.graph.base_graph - INFO - Creating schema for graph GraphRAG...
    2025-01-05 23:51:06,152 - tigergraphx.core.graph.base_graph - INFO - Schema created successfully.


---

## Hybrid Retrieval
TigerGraph offers two flexible ways to perform hybrid retrieval, allowing you to extract relevant graph and vector data efficiently for GraphRAG workflows.
### Using TigerGraphX
TigerGraphX offers an intuitive, Python-native interface for hybrid retrieval, ideal for developers seeking simplicity and ease of use. 

**Key Advantage**: Minimal learning curve with high-level Python APIs, seamlessly integrated with existing workflows.

Below are some illustrative examples.

#### Retrieve Nodes with Specific Attributes
You can use the following code to fetch up to two nodes of type "Entity" and display their "id," "entity_type," and "description" attributes.


```python
G.get_nodes(
    node_type="Entity",
    return_attributes=["id", "name", "entity_type", "description"],
    limit=2,
)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>name</th>
      <th>entity_type</th>
      <th>description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>473502492d0a419981fed4fbc1493832</td>
      <td>THE THREE MISS FEZZIWIGS</td>
      <td>PERSON</td>
      <td>Daughters of Mr. and Mrs. Fezziwig, described ...</td>
    </tr>
    <tr>
      <th>1</th>
      <td>6fb90dc954fe40d5969f7532a66376e9</td>
      <td>WANT</td>
      <td>PERSON</td>
      <td>Want is depicted as a girl, symbolizing povert...</td>
    </tr>
  </tbody>
</table>
</div>



#### Retrieve Neighbors with Specific Attributes

The following code demonstrates how to fetch neighbors of specific nodes. In this example, the query retrieves neighbors connected to the given `start_nodes` of type `"Entity"` through the edge type `"community_contains_entity"`. The attributes `"id"`, `"title"`, and `"full_content"` of the neighbors are returned.


```python
start_nodes = ["473502492d0a419981fed4fbc1493832", "6fb90dc954fe40d5969f7532a66376e9"]
G.get_neighbors(
    start_nodes=start_nodes,
    start_node_type="Entity",
    edge_types="community_contains_entity",
    return_attributes=["id", "title", "full_content"],
)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>title</th>
      <th>full_content</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>9</td>
      <td>Community 9</td>
      <td># The Transformation of Ebenezer Scrooge: A St...</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0</td>
      <td>Community 0</td>
      <td># The Transformation Journey of Ebenezer Scroo...</td>
    </tr>
    <tr>
      <th>2</th>
      <td>19</td>
      <td>Community 19</td>
      <td># The Transformation of Ebenezer Scrooge: A Ch...</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1</td>
      <td>Community 1</td>
      <td># Fezziwig's Christmas Celebration Community\n...</td>
    </tr>
  </tbody>
</table>
</div>



#### Retrieve Top-K Using TigerVector's Vector Search Capability
The following code generates a random query vector of 1536 float values and uses it to perform a vector search on a TigerGraph instance. The search finds the most similar "Entity" nodes based on the "emb_description" vector attribute and returns the top result.


```python
import random
random_floats: list[float] = [random.random() for _ in range(1536)]
results = G.search(
    data=random_floats,
    vector_attribute_name="emb_description",
    node_type="Entity",
    limit=1,
)
print(results)
```

    [{'id': '9b24fbfeb0e94dd889c10700718b048f', 'distance': 0.9512004, 'human_readable_id': 83, 'name': 'GROCER', 'entity_type': '', 'description': ''}]


---

### Using GSQL
For developers seeking fine-grained control or complex retrieval logic, GSQL offers unmatched flexibility. As TigerGraph's built-in query language, GSQL empowers you to perform advanced graph data analysis. For more details, see the [official documentation](https://docs.tigergraph.com/gsql-ref/4.1/intro).

**Key Advantage:** Supports complex logic, customization, and direct interaction with TigerGraph’s powerful query engine.

1. Use an LLM to convert the query into an embedding.  
2. Write a GSQL query to retrieve the top-K similar objects and their neighbors, combining structured and vector-based retrieval:

```SQL
CREATE OR REPLACE QUERY my_query (
    LIST<float> query_vector,
    int k
) SYNTAX v3 {
  Nodes = vectorSearch({Entity.emb_description}, query_vector, k);
  PRINT Nodes;

  Neighbors =
    SELECT t
    FROM (s:Nodes)-[e:community_contains_entity]->(t:Community);

  print Neighbors[Neighbors.id, Neighbors.title, Neighbors.full_content];
}
```

---
## Context Building: Writing Custom Context Builders

Context builders play a vital role in graph-powered RAG workflows. They transform retrieved graph data into structured, meaningful contexts for tasks such as interactions with LLMs)\.

TigerGraphX simplifies this process by offering the flexible `BaseContextBuilder` class, which allows developers to define custom logic for context building.

### Key Features of `BaseContextBuilder`

The `BaseContextBuilder` class in TigerGraphX provides a strong foundation for creating custom context builders, offering:

- **Core Abstraction**: A reusable framework for building context logic.
- **Customizable Design**: Extensibility for implementing both global and query-specific context generation.

---

### Key Components

1. **Abstract Method - `build_context`**:  
   Subclasses must implement this method to define the logic for constructing context.

   ```python
   @abstractmethod
   async def build_context(self, *args, **kwargs) -> str | List[str]:
       """Abstract method to build context."""
       pass
   ```

2. **Batching and Retrieval Methods**:
   - **`batch_and_convert_to_text`**: Formats graph data into token-aware text.
   - **`retrieve_top_k_objects`**: Efficiently retrieves top-K objects for query-based context.

---

### Example: Global Context Builder


```python
import tiktoken
from typing import Optional, List
from tigergraphx.graphrag import BaseContextBuilder
from tigergraphx.core import Graph
class GlobalContextBuilder(BaseContextBuilder):
    def __init__(
        self,
        graph: Graph,
        token_encoder: Optional[tiktoken.Encoding] = None,
    ):
        """Initialize LocalContextBuilder with graph config and token encoder."""
        super().__init__(
            graph=graph,
            single_batch=False,
            token_encoder=token_encoder,
        )
    async def build_context(self) -> str | List[str]:
        """Build local context."""
        context: List[str] = []
        config = {
            "max_tokens": 12000,
            "section_name": "Communities",
            "return_attributes": ["id", "rank", "title", "full_content"],
            "limit": 1000,
        }
        df = self.graph.get_nodes(
            node_type="Community",
            return_attributes=config["return_attributes"],
            limit=config["limit"],
        )
        if df is not None:
            text_context = self.batch_and_convert_to_text(
                graph_data=df,
                max_tokens=config["max_tokens"],
                single_batch=self.single_batch,
                section_name=config["section_name"],
            )
            context.extend(
                text_context if isinstance(text_context, list) else [text_context]
            )
        return context
```

Here’s how you can utilize the custom global context builder:


```python
global_context_builder = GlobalContextBuilder(G)
context_list = await global_context_builder.build_context()
# Print the first 1000 characters for easier visualization of long text
print(context_list[0][:1000])
```

    -----Communities-----
    id|rank|title|full_content
    18|8.5|Community 18|# Project Gutenberg Ecosystem\n\nThe Project Gutenberg ecosystem is a collaborative network focused on the free distribution of electronic literature. Central to this community are the Project Gutenberg Literary Archive Foundation, Project Gutenberg™, and its electronic works, supported by a structure of copyright management, royalty fees, and the pioneering efforts of Michael S. Hart. This network facilitates the global dissemination of literature in digital formats, ensuring accessibility and promoting literary heritage.\n\n## The foundational role of the Project Gutenberg Literary Archive Foundation\n\nThe Project Gutenberg Literary Archive Foundation is pivotal in the Project Gutenberg ecosystem, managing copyrights and the Project Gutenberg trademark. It receives donations and royalties, supporting the mission to preserve and provide free access to electronic works. This foundation ensures the sustainability of P


---

### Example: Local Context Builder

To understand the functionality of the `LocalContextBuilder` class, let's review the key code from its `build_context` method.

![](https://github.com/tigergraph/tigergraphx/blob/main/docs/images/graphrag/local_context_builder.png?raw=true)

```
# Retrieve top-k objects
top_k_objects: List[str] = await self.retrieve_top_k_objects(query, k=k)
...
# Iterate over different neighbor types
for neighbor in neighbor_types:
    df = self.graph.get_neighbors(...)
    if df is not None:
        text_context = self.batch_and_convert_to_text(...)
        context.extend(
            text_context if isinstance(text_context, list) else [text_context]
        )
return "\n\n".join(context)
```

For full implementations of different context builders, refer to the following links:
- [LocalContextBuilder Code](https://github.com/tigergraph/tigergraphx/blob/main/applications/msft_graphrag/query/context_builder/local_context_builder.py)


Here’s how you can utilize the custom local context builder:

```python
local_builder = LocalContextBuilder(graph=graph, search_engine=search_engine)
local_context = await local_builder.build_context(query="What are the main topics discussed in the article?")
```

---

## Integrate with LLM

After successfully building context from TigerGraph, the final step is integrating it with LLMs, including chat models and embedding models.

We have provided an example implementation, which you can find here: [Example Code](https://github.com/tigergraph/tigergraphx/blob/main/applications/msft_graphrag/query/graphrag.py).

### Workflow Overview

The integration process follows the workflow illustrated below:

![](https://github.com/tigergraph/tigergraphx/blob/main/docs/images/graphrag/querying.png?raw=true)

---

## What’s Next?

- [API Reference](../../reference/features_overview): Dive deeper into TigerGraphX APIs.

---

Start transforming your GraphRAG workflows with the power of **TigerGraphX** today!
