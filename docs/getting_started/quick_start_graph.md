# TigerGraphX Quick Start: Using TigerGraph as Graph Database
Follow this guide to quickly set up **TigerGraphX** and build your first graph. This guide assumes that you have already installed TigerGraphX and its dependencies as described in the [Installation Guide](../installation).

To run this Jupyter Notebook, you can download the original `.ipynb` file from [quick_start_graph.ipynb](https://github.com/tigergraph/tigergraphx/tree/main/docs/getting_started/quick_start_graph.ipynb).

---

## Create a Graph
### Define the TigerGraph Connection Configuration
Since our data is stored in a TigerGraph instance—whether on-premise or in the cloud—we need to configure the connection settings. The recommended approach is to use environment variables, such as setting them with the `export` command in the shell. Here, to illustrate the demo, we configure them within Python using the `os.environ` method. You can find more methods for configuring connection settings in [Graph.\_\_init\_\_](../../reference/01_core/graph/#tigergraphx.core.graph.Graph.__init__).


```python
>>> import os
>>> os.environ["TG_HOST"] = "http://127.0.0.1"
>>> os.environ["TG_USERNAME"] = "tigergraph"
>>> os.environ["TG_PASSWORD"] = "tigergraph"
```

### Define a Graph Schema
TigerGraph is a schema-based database, which requires defining a schema to structure your graph. This schema specifies the graph name, nodes (vertices), edges (relationships), and their respective attributes.

In this example, we will create a graph named "Social" that includes one node type, "Person," and one directed edge type, "Friendship." Note that you must define the primary key for each node type, indicate whether an edge type is directed or undirected, and specify the source and target node types for each edge type.


```python
>>> graph_schema = {
...     "graph_name": "Social",
...     "nodes": {
...         "Person": {
...             "primary_key": "name",
...             "attributes": {
...                 "name": "STRING",
...                 "age": "UINT",
...                 "gender": "STRING",
...             },
...         },
...     },
...     "edges": {
...         "Friendship": {
...             "is_directed_edge": False,
...             "from_node_type": "Person",
...             "to_node_type": "Person",
...             "attributes": {
...                 "closeness": "DOUBLE",
...             },
...         },
...     },
... }
```

TigerGraphX offers several methods to define the schema, including a Python dictionary, YAML file, or JSON file. Above is an example using a Python dictionary. For other methods, please refer to [Graph.\_\_init\_\_](../../reference/01_core/graph/#tigergraphx.core.graph.Graph.__init__) for more details.

### Create a Graph
Running the following command will create a graph using the user-defined schema if it does not already exist. If the graph exists, the command will return the existing graph. To overwrite the existing graph, set the drop_existing_graph parameter to True. Note that creating the graph may take several seconds.


```python
>>> from tigergraphx import Graph
>>> G = Graph(graph_schema)
```

    2025-02-26 15:22:48,539 - tigergraphx.core.managers.schema_manager - INFO - Graph existence check for Social: does not exist
    2025-02-26 15:22:48,540 - tigergraphx.core.managers.schema_manager - INFO - Creating schema for graph: Social...
    2025-02-26 15:22:51,758 - tigergraphx.core.managers.schema_manager - INFO - Graph schema created successfully.


### Retrieve a Graph and Print Its Schema
Once a graph has been created in TigerGraph, you can retrieve it without manually defining the schema using the `Graph.from_db` method, which requires only the graph name:


```python
>>> G = Graph.from_db("Social")
```

Now, let's print the schema of the graph in a well-formatted manner:


```python
>>> import json
>>> schema = G.get_schema()
>>> print(json.dumps(schema, indent=4, default=str))
```

    {
        "graph_name": "Social",
        "nodes": {
            "Person": {
                "primary_key": "name",
                "attributes": {
                    "name": {
                        "data_type": "DataType.STRING",
                        "default_value": null
                    },
                    "age": {
                        "data_type": "DataType.UINT",
                        "default_value": null
                    },
                    "gender": {
                        "data_type": "DataType.STRING",
                        "default_value": null
                    }
                },
                "vector_attributes": {}
            }
        },
        "edges": {
            "Friendship": {
                "is_directed_edge": false,
                "from_node_type": "Person",
                "to_node_type": "Person",
                "discriminator": "set()",
                "attributes": {
                    "closeness": {
                        "data_type": "DataType.DOUBLE",
                        "default_value": null
                    }
                }
            }
        }
    }


## Nodes and Edges
### Adding Nodes and Edges

TigerGraphX provides NetworkX-like methods for node operations, edge operations, and statistical analysis. You can find the full API reference in the [Graph class reference](../../reference/01_core/graph).

To add nodes or edges individually, use the following code:


```python
>>> G.add_node("Emily", age=25, gender="Female")
>>> G.add_node("John", age=28, gender="Male")
>>> G.add_edge("Emily", "John", closeness=0.98)
```

While this method is simple, it adds nodes and edges one by one. Alternatively, you can use `add_nodes_from` and `add_edges_from` to add them in small batches. The following example demonstrates how to add multiple nodes at once:


```python
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Michael", {"age": 29}),
...    ("Victor", {"age": 31, "gender": "Male"}),
... ]
>>> G.add_nodes_from(nodes_for_adding)
```




    3



Next, let's add edges with individual attributes using tuples in the format `(source ID, target ID, attribute_dict)`.


```python
>>> ebunch_to_add = [
...    ("Alice", "Michael"),
...    ("Alice", "John", {"closeness": 2.5}),
...    ("Emily", "Victor", {"closeness": 1.5}),
... ]
>>> G.add_edges_from(ebunch_to_add)
```




    3



For larger datasets, consider using [load_data](../../reference/01_core/graph/#tigergraphx.core.Graph.load_data) for efficient handling of large-scale data.

### Check if Nodes and Edges Exist


```python
>>> print(G.has_node("Alice"))
```

    True



```python
>>> print(G.has_node("Michael"))
```

    True


Since the 'Friendship' edge is undirected, both 'Alice -> Michael' and 'Michael -> Alice' are valid and accessible.


```python
>>> print(G.has_edge("Alice", "Michael"))
```

    True



```python
>>> print(G.has_edge("Michael", "Alice"))
```

    True


### Display Node and Edge Attributes

#### Display Node Attributes
To display all attributes of a given node, use the following command:


```python
>>> print(G.nodes["Alice"])
```

    {'name': 'Alice', 'age': 30, 'gender': 'Female'}


To display a specific attribute, use the command below:


```python
>>> print(G.nodes["Michael"]["age"])
```

    29


#### Display Edge Attributes


```python
>>> print(G.get_edge_data("Alice", "John"))
```

    {'closeness': 2.5}


### Display the Degree of Nodes
To display the degree of a given node, use the following command:


```python
>>> print(G.degree("Alice"))
```

    2


## Query Operations
### Retrieve Nodes
Retrieve "Person" nodes that match a specific filter expression, use a custom alias, request only selected attributes, and limit the results:


```python
>>> df = G.get_nodes(
...     node_type="Person",
...     node_alias="s", # "s" is the default value, so you can remove this line
...     filter_expression="s.age >= 29",
...     return_attributes=["name", "age"],
...     limit=1
... )
>>> print(df)
```

         name  age
    0  Victor   31


### Retrieve a Node's Neighbors
Retrieve the first "Person" node that is a friend of Alice, filtering edges where closeness > 1 and returning the target node's "name" and "gender" attributes:


```python
>>> df = G.get_neighbors(
...     start_nodes="Alice",
...     start_node_type="Person",
...     edge_types="Friendship",
...     target_node_types="Person",
...     filter_expression="e.closeness > 1",
...     return_attributes=["name", "gender"],
...     limit=1,
... )
>>> print(df)
```

       name gender
    0  John   Male


Note that the result of `get_neighbors` is a Pandas DataFrame.


```python
>>> print(type(df))
```

    <class 'pandas.core.frame.DataFrame'>


### Breadth First Search
Below is an example of multi-hop neighbor traversal:


```python
>>> # First hop: Retrieve neighbors of "Alice" of type "Person"
>>> visited = set(["Alice"])  # Track visited nodes
>>> df = G.get_neighbors(start_nodes="Alice", start_node_type="Person")
>>> primary_ids = set(df['name']) - visited  # Exclude already visited nodes
>>> print(primary_ids)
```

    {'Michael', 'John'}



```python
>>> # Second hop: Retrieve neighbors of the nodes identified in the first hop
>>> visited.update(primary_ids)  # Mark these nodes as visited
>>> df = G.get_neighbors(start_nodes=primary_ids, start_node_type="Person")
>>> primary_ids = set(df['name']) - visited  # Exclude visited nodes
>>> print(primary_ids)
```

    {'Emily'}



```python
>>> # Third hop: Retrieve neighbors of the nodes identified in the second hop
>>> visited.update(primary_ids)  # Mark these nodes as visited
>>> df = G.get_neighbors(start_nodes=primary_ids, start_node_type="Person")
>>> df = df[~df['name'].isin(visited)]  # Remove visited nodes from the final result
>>> print(df)
```

      gender    name  age
    0   Male  Victor   31


## Graph Statistics
### Display the Number of Nodes


```python
>>> print(G.number_of_nodes())
```

    5


### Display the Number of Edges


```python
>>> print(G.number_of_edges())
```

    4


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

    2025-02-26 15:23:17,281 - tigergraphx.core.managers.schema_manager - INFO - Dropping graph: Social...


---

## What’s Next?

Now that you've set up your graph storage and performed basic operations, you can explore more advanced features of TigerGraphX:

- [TigerGraph Quick Start Guide for Vector Storage](../quick_start_vector): Quickly get started with TigerGraph for storing vector data.
- [API Reference](../../reference/features_overview): Dive deeper into TigerGraphX APIs to understand its full capabilities.

---

Start unlocking the power of graphs with **TigerGraphX** today!
