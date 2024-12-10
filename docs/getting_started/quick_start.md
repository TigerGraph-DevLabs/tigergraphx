# Quick Start Guide

Follow this guide to quickly set up **TigerGraphX** and build your first graph. This guide assumes that you have already installed TigerGraphX and its dependencies as described in the [Installation Guide](installation.md).

---

## Step 1: Import TigerGraphX

Start by importing TigerGraphX into your Python script or Jupyter Notebook:

```python
from tigergraphx import Graph
```

---

## Step 2: Define a Schema

Create a schema to define the structure of your graph, including vertices (nodes), edges (relationships), and their attributes:

```python
# Define a graph schema
schema = {
    "vertices": {
        "Entity": {
            "primary_key": "id",
            "attributes": {
                "id": "string",
                "name": "string",
                "type": "string",
                "description": "string"
            }
        }
    },
    "edges": {
        "Relationship": {
            "from_node_type": "Entity",
            "to_node_type": "Entity",
            "attributes": {
                "type": "string",
                "weight": "float"
            }
        }
    }
}
```

---

## Step 3: Initialize a Graph

Use the schema to initialize a graph in TigerGraphX:

```python
# Initialize a graph with the schema
graph = Graph(schema=schema)
print("Graph initialized successfully!")
```

---

## Step 4: Load Data into the Graph

Load data into your graph from a Parquet file or Python dictionary. For this example, we’ll use a Python dictionary:

```python
# Sample data for vertices
entities = [
    {"id": "1", "name": "Entity 1", "type": "Type A", "description": "This is entity 1."},
    {"id": "2", "name": "Entity 2", "type": "Type B", "description": "This is entity 2."}
]

# Sample data for edges
relationships = [
    {"from_id": "1", "to_id": "2", "type": "Connected", "weight": 1.0}
]

# Load data into the graph
graph.add_vertices("Entity", entities)
graph.add_edges("Relationship", relationships)

print("Data loaded successfully!")
```

---

## Step 5: Query the Graph

Query the graph to retrieve data, such as neighbors or specific attributes:

```python
# Retrieve neighbors of a vertex
neighbors = graph.get_neighbors(vertex_id="1", edge_type="Relationship")
print("Neighbors of Entity 1:", neighbors)

# Run a custom query
results = graph.query("MATCH (e:Entity)-[r:Relationship]->(n:Entity) RETURN e, r, n")
print("Query results:", results)
```

---

## Step 6: Perform Hybrid Retrieval (Optional)

For advanced workflows like GraphRAG, you can combine graph traversal with vector search:

```python
# Retrieve top-k similar entities based on vector embeddings
query_embedding = [0.1, 0.2, 0.3]  # Example embedding vector
top_k = graph.retrieve_top_k_objects(query_embedding, k=5)

print("Top-K similar entities:", top_k)
```

---

## Step 7: Build Context for LLMs (Optional)

TigerGraphX can be used to build token-aware context for large language models (LLMs):

```python
# Build token-aware context from graph data
context = graph.build_context(vertex_id="1", depth=2)
print("Generated context for LLMs:")
print(context)
```

---

## What’s Next?

Now that you’ve set up your graph and performed basic operations, you can explore more advanced features of TigerGraphX:
- [GraphRAG Overview](../graphrag/overview.md): Learn about integrating graphs with LLMs.
- [API Reference](../reference/api.md): Dive deeper into TigerGraphX APIs.
- [Advanced Topics](../advanced/graph_vector_data.md): Explore hybrid retrieval and vector search.

---

Start building powerful graph applications with **TigerGraphX** today!
