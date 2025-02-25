# TigerGraphX Quick Start: Using TigerGraph as Graph Database
Follow this guide to quickly set up **TigerGraphX** and build your first graph. This guide assumes that you have already installed TigerGraphX and its dependencies as described in the [Installation Guide](../installation).

To run this Jupyter Notebook, you can download the original `.ipynb` file from [quick_start_graph.ipynb](https://github.com/tigergraph/tigergraphx/tree/main/docs/getting_started/quick_start_graph.ipynb).

---

## Create a Graph
### Define the TigerGraph Connection Configuration
Since our data is stored in a TigerGraph instance—whether on-premise or in the cloud—we need to configure the connection settings. The recommended approach is to use environment variables, such as setting them with the `export` command in the shell. Here, to illustrate the demo, we configure them within Python using the `os.environ` method. You can find more methods for configuring connection settings in [Graph.\_\_init\_\_](../../reference/01_core/graph/#tigergraphx.core.graph.Graph.__init__).


```python
import os
os.environ["TG_HOST"] = "http://127.0.0.1"
os.environ["TG_USERNAME"] = "tigergraph"
os.environ["TG_PASSWORD"] = "tigergraph"
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

    2025-02-25 19:39:35,846 - tigergraphx.core.managers.schema_manager - INFO - Graph existence check for Social: does not exist
    2025-02-25 19:39:35,847 - tigergraphx.core.managers.schema_manager - INFO - Creating schema for graph: Social...
    2025-02-25 19:39:39,769 - tigergraphx.core.managers.schema_manager - INFO - Graph schema created successfully.


Once the graph has been created inside TigerGraph, a simpler way to get the graph without defining graph schema is using `Graph.from_db` method, which only graph name is required to provide. 


```python
>>> G = Graph.from_db("Social")
```

## Nodes and Edges
### Add Nodes and Edges
*Note*: This example demonstrates how to easily add nodes and edges using the API. However, adding nodes and edges individually may not be efficient for large-scale operations. For better performance when loading data into TigerGraph, it is recommended to use a loading job. Nonetheless, these examples are ideal for quickly getting started.


```python
>>> G.add_node("Alice", "Person", age=25)
>>> G.add_node("Michael", "Person", age=28)
>>> G.add_edge("Alice", "Michael", closeness=0.98)
```

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
#### Using `get_node_data` and `get_edge_data` Functions


```python
>>> print(G.get_node_data("Alice"))
```

    {'name': 'Alice', 'age': 25}



```python
>>> print(G.get_edge_data("Alice", "Michael"))
```

    {'closeness': 0.98}


#### Using Node View


```python
>>> print(G.nodes["Alice"])
```

    {'name': 'Alice', 'age': 25}



```python
>>> print(G.nodes["Michael"]["age"])
```

    28


*Note:* The Edge View feature is planned for future releases.

### Display the Degree of Nodes


```python
>>> print(G.degree("Alice"))
```

    1


### Retrieve the Neighbors of a Node


```python
>>> neighbors = G.get_neighbors("Alice")
>>> print(neighbors)
```

          name  age
    0  Michael   28



```python
>>> print(type(neighbors))
```

    <class 'pandas.core.frame.DataFrame'>


## Graph Statistics
### Display the Number of Nodes


```python
>>> print(G.number_of_nodes())
```

    2


### Display the Number of Edges


```python
>>> print(G.number_of_edges())
```

    1


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

    2025-02-25 18:11:56,813 - tigergraphx.core.managers.schema_manager - INFO - Dropping graph: Social...
    2025-02-25 18:11:59,489 - tigergraphx.core.managers.schema_manager - INFO - Graph dropped successfully.


---

## What’s Next?

Now that you've set up your graph storage and performed basic operations, you can explore more advanced features of TigerGraphX:

- [TigerGraph Quick Start Guide for Vector Storage](../quick_start_vector): Quickly get started with TigerGraph for storing vector data.
- [API Reference](../../reference/features_overview): Dive deeper into TigerGraphX APIs to understand its full capabilities.

---

Start unlocking the power of graphs with **TigerGraphX** today!
