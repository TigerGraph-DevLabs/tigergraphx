# TigerGraphX Quick Start: Using TigerGraph as Vector Database

TigerGraph has supported vector storage since version 4.2. In this guide, we will demonstrate how to use TigerGraph as a pure vector database, without storing edges. This setup can be useful when you want to leverage TigerGraph solely as a vector database. However, to fully unlock the potential of TigerGraph, you can also use it as both a graph and vector storage solution. For more details, refer to the [next guide](quick_start_both.md).

This guide assumes that you have already installed TigerGraphX and its dependencies, as outlined in the [Installation Guide](installation.md).

To run this Jupyter Notebook, download the original `.ipynb` file from [quick_start_vector.ipynb](https://github.com/tigergraph/tigergraphx/tree/main/docs/getting_started/quick_start_vector.ipynb).

---

## Create a Graph
### Define the TigerGraph Connection Configuration
Since our data is stored in a TigerGraph instance—whether on-premise or in the cloud—we need to configure the connection settings. The recommended approach is to use environment variables, such as setting them with the `export` command in the shell. Here, to illustrate the demo, we configure them within Python using the `os.environ` method. You can find more methods for configuring connection settings in [Graph.\_\_init\_\_](../reference/01_core/graph.md#tigergraphx.core.graph.Graph.__init__).


```python
>>> import os
>>> os.environ["TG_HOST"] = "http://127.0.0.1"
>>> os.environ["TG_USERNAME"] = "tigergraph"
>>> os.environ["TG_PASSWORD"] = "tigergraph"
```

### Define a Graph Schema

TigerGraph is a schema-based database, which requires defining a schema to structure your graph. A typical schema includes the graph name, nodes (vertices), edges (relationships), and their respective attributes. However, when using TigerGraph as a pure vector database, you only need to define the graph name, the node (vertex) type, and its attributes, including vector attributes.

In this example, we create a graph called "FinancialGraph" with one node type: "Account." This node type has a primary key `name`, attributes `name` (string) and `isBlocked` (boolean), and a vector attribute `emb1` (3-dimensional).


```python
>>> graph_schema = {
...     "graph_name": "FinancialGraph",
...     "nodes": {
...         "Account": {
...             "primary_key": "name",
...             "attributes": {
...                 "name": "STRING",
...                 "isBlocked": "BOOL",
...             },
...             "vector_attributes": {"emb1": 3},
...         },
...     },
...     "edges": {}
... }
```

TigerGraphX offers several methods to define the schema, including a Python dictionary, YAML file, or JSON file. Above is an example using a Python dictionary. For other methods, please refer to [Graph.\_\_init\_\_](../reference/01_core/graph.md#tigergraphx.core.graph.Graph.__init__) for more details.

### Create a Graph
Running the following command will create a graph using the user-defined schema if it does not already exist. If the graph exists, the command will return the existing graph. To overwrite the existing graph, set the drop_existing_graph parameter to True. Note that creating the graph may take several seconds.


```python
>>> from tigergraphx import Graph
>>> G = Graph(graph_schema)
```

    2025-02-27 17:35:49,124 - tigergraphx.core.managers.schema_manager - INFO - Creating schema for graph: FinancialGraph...
    2025-02-27 17:35:52,641 - tigergraphx.core.managers.schema_manager - INFO - Graph schema created successfully.
    2025-02-27 17:35:52,642 - tigergraphx.core.managers.schema_manager - INFO - Adding vector attribute(s) for graph: FinancialGraph...
    2025-02-27 17:36:52,825 - tigergraphx.core.managers.schema_manager - INFO - Vector attribute(s) added successfully.


### Retrieve a Graph and Print Its Schema
Once a graph has been created in TigerGraph, you can retrieve it without manually defining the schema using the `Graph.from_db` method, which requires only the graph name:


```python
>>> G = Graph.from_db("FinancialGraph")
```

Now, let's print the schema of the graph in a well-formatted manner:


```python
>>> import json
>>> schema = G.get_schema()
>>> print(json.dumps(schema, indent=4, default=str))
```

    {
        "graph_name": "FinancialGraph",
        "nodes": {
            "Account": {
                "primary_key": "name",
                "attributes": {
                    "name": {
                        "data_type": "DataType.STRING",
                        "default_value": null
                    },
                    "isBlocked": {
                        "data_type": "DataType.BOOL",
                        "default_value": null
                    }
                },
                "vector_attributes": {
                    "emb1": {
                        "dimension": 3,
                        "index_type": "HNSW",
                        "data_type": "FLOAT",
                        "metric": "COSINE"
                    }
                }
            }
        },
        "edges": {}
    }


## Add Nodes
In this example, we add multiple nodes representing accounts to the graph. Each node is uniquely identified by a name and comes with two attributes:

- **isBlocked:** A Boolean indicating whether the account is blocked.
- **emb1:** A three-dimensional embedding vector.


```python
>>> nodes_for_adding = [
...     ("Scott", {"isBlocked": False, "emb1": [-0.017733968794345856, -0.01019224338233471, -0.016571875661611557]}),
...     ("Jenny", {"isBlocked": False, "emb1": [-0.019265105947852135, 0.0004929182468913496, 0.006711316294968128]}),
...     ("Steven", {"isBlocked": True, "emb1": [-0.01505514420568943, -0.016819344833493233, -0.0221870020031929]}),
...     ("Paul", {"isBlocked": False, "emb1": [0.0011193430982530117, -0.001038988004438579, -0.017158523201942444]}),
...     ("Ed", {"isBlocked": False, "emb1": [-0.003692442551255226, 0.010494389571249485, -0.004631792660802603]}),
... ]
>>> print("Number of Account Nodes Inserted:", G.add_nodes_from(nodes_for_adding, node_type="Account"))
```

    Number of Account Nodes Inserted: 5


For larger datasets, consider using [load_data](../reference/01_core/graph.md#tigergraphx.core.Graph.load_data) for efficient handling of large-scale data.

## Exploring Nodes in the Graph
### Display the Number of Nodes
Next, let's verify that the data has been inserted into the graph by using the following command. As expected, the number of nodes is 5.


```python
>>> print(G.number_of_nodes())
```

    5


### Check if Nodes Exist
Use the following commands to check whether specific nodes are present in the graph:


```python
>>> print(G.has_node("Scott"))
```

    True



```python
>>> print(G.has_node("Jenny"))
```

    True


### Display Node Attributes
To display all attributes of a given node, use the following command:


```python
>>> print(G.nodes["Scott"])
```

    {'name': 'Scott', 'isBlocked': False}


To display a specific attribute, use the command below:


```python
>>> print(G.nodes["Scott"]["isBlocked"])
```

    False


### Filter the Nodes
Retrieve "Account" nodes that match a specific filter expression, request only selected attributes, and limit the results:


```python
>>> df = G.get_nodes(
...     node_type="Account",
...     node_alias="s", # "s" is the default value, so you can remove this line
...     filter_expression="s.isBlocked == False",
...     return_attributes=["name", "isBlocked"],
...     limit=2
... )
>>> print(df)
```

        name  isBlocked
    0   Paul      False
    1  Scott      False


### Display Node's Vector Attributes
Retrieve the vector attribute of a specific node:


```python
>>> vector = G.fetch_node(
...     node_id="Scott",
...     vector_attribute_name="emb1",
... )
>>> print(vector)
```

    [-0.01773397, -0.01019224, -0.01657188]


Retrieve vector attributes for multiple nodes:


```python
>>> vectors = G.fetch_nodes(
...     node_ids=["Scott", "Jenny"],
...     vector_attribute_name="emb1",
... )
>>> for vector in vectors.items():
...     print(vector)
```

    ('Scott', [-0.01773397, -0.01019224, -0.01657188])
    ('Jenny', [-0.01926511, 0.0004929182, 0.006711317])


## Perform Vector Search
### Top-k Vector Search on a Given Vertex Type's Vector Attribute
To find the top 2 most similar accounts to "Scott" based on the embedding, we use the following code. As expected, "Scott" will appear in the list with a distance of 0.


```python
>>> results = G.search(
...    data=[-0.017733968794345856, -0.01019224338233471, -0.016571875661611557],
...    vector_attribute_name="emb1",
...    node_type="Account",
...    limit=2
... )
>>> for result in results:
...     print(result)
```

    {'id': 'Scott', 'distance': 0, 'name': 'Scott', 'isBlocked': False}
    {'id': 'Steven', 'distance': 0.0325563, 'name': 'Steven', 'isBlocked': True}


### Top-k Vector Search Using a Vertex Embedding as the Query Vector
This code performs a top-k vector search for similar nodes to a specified node "Scott". It searches within the "Account" node type using the "emb1" embedding attribute and retrieves the top 2 similar node.


```python
>>> results = G.search_top_k_similar_nodes(
...     node_id="Scott",
...     vector_attribute_name="emb1",
...     node_type="Account",
...     limit=2
... )
>>> for result in results:
...     print(result)
```

    {'id': 'Paul', 'distance': 0.3933879, 'name': 'Paul', 'isBlocked': False}
    {'id': 'Steven', 'distance': 0.0325563, 'name': 'Steven', 'isBlocked': True}


### Top-k Vector Search with Specified Candidates
This code performs a top-2 vector search on the "Account" node type using the "emb1" embedding attribute. It limits the search to the specified candidate nodes: "Jenny", "Steven", and "Ed".


```python
>>> results = G.search(
...     data=[-0.017733968794345856, -0.01019224338233471, -0.016571875661611557],
...     vector_attribute_name="emb1",
...     node_type="Account",
...     limit=2,
...     candidate_ids=["Jenny", "Steven", "Ed"]
... )
>>> for result in results:
...     print(result)
```

    {'id': 'Steven', 'distance': 0.0325563, 'name': 'Steven', 'isBlocked': True}
    {'id': 'Jenny', 'distance': 0.5804119, 'name': 'Jenny', 'isBlocked': False}


## Filtered Vector Search
Let's first retrieves all "Account" nodes where the isBlocked attribute is False and returns their name attributes in a Pandas DataFrame.


```python
>>> nodes_df = G.get_nodes(
...     node_type="Account",
...     node_alias="s", # The alias "s" is used in filter_expression. You can remove this line since the default node alias is "s"
...     filter_expression='s.isBlocked == False AND s.name != "Ed"',
...     return_attributes=["name"],
... )
>>> print(nodes_df)
```

        name
    0   Paul
    1  Scott
    2  Jenny


Then convert the name column of the retrieved DataFrame into a set of candidate IDs and performs a top-2 vector search on the "Account" node type using the "emb1" embedding attribute, restricted to the specified candidate IDs.


```python
>>> candidate_ids = set(nodes_df['name'])
... results = G.search(
...     data=[-0.017733968794345856, -0.01019224338233471, -0.016571875661611557],
...     vector_attribute_name="emb1",
...     node_type="Account",
...     limit=2,
...     candidate_ids=candidate_ids
... )
>>> for result in results:
...     print(result)
```

    {'id': 'Paul', 'distance': 0.393388, 'name': 'Paul', 'isBlocked': False}
    {'id': 'Scott', 'distance': 0, 'name': 'Scott', 'isBlocked': False}


## Clear and Drop a Graph

### Clear the Graph
To clear the data in the graph without dropping it, use the following code:


```python
>>> print(G.clear())
```

    True


Afterwards, you can confirm that there are no nodes in the graph by checking:


```python
>>> print(G.number_of_nodes())
```

    0


### Drop the Graph
To clear the data and completely remove the graph—including schema, loading jobs, and queries—use the following code:


```python
>>> G.drop_graph()
```

    2025-02-27 17:38:44,545 - tigergraphx.core.managers.schema_manager - INFO - Dropping graph: FinancialGraph...
    2025-02-27 17:38:47,882 - tigergraphx.core.managers.schema_manager - INFO - Graph dropped successfully.


---

## What’s Next?

Now that you've learned how to use TigerGraph for storing both graph data and vectors, you can dive into more advanced features of TigerGraphX:

- [TigerGraph Quick Start Guide for Graph and Vector Storage](quick_start_both.md): Quickly get started with TigerGraph for storing both graph and vector data.
- [API Reference](../reference/introduction.md): Dive deeper into TigerGraphX APIs.

---

Start unlocking the power of graphs with **TigerGraphX** today!
