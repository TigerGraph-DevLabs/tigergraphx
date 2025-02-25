# TigerGraphX Quick Start: Using TigerGraph as Vector Database

TigerGraph has supported vector storage since version 4.2. In this guide, we will demonstrate how to use TigerGraph as a pure vector database, without storing edges. This setup can be useful when you want to leverage TigerGraph solely as a vector database. However, to fully unlock the potential of TigerGraph, you can also use it as both a graph and vector storage solution. For more details, refer to the [next guide](../quick_start_both).

This guide assumes that you have already installed TigerGraphX and its dependencies, as outlined in the [Installation Guide](../installation).

To run this Jupyter Notebook, download the original `.ipynb` file from [quick_start_vector.ipynb](https://github.com/tigergraph/tigergraphx/tree/main/docs/getting_started/quick_start_vector.ipynb).

---

## Create a Graph
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

### Define the TigerGraph Connection Configuration
In addition to defining the schema, a connection configuration is necessary to establish communication with the TigerGraph server.


```python
>>> connection = {
...     "host": "http://127.0.0.1",
...     "username": "tigergraph",
...     "password": "tigergraph",
... }
```

### Create a Graph
Running the following command will create a graph using the user-defined schema if it does not already exist. If the graph exists, the command will return the existing graph. To overwrite the existing graph, set the drop_existing_graph parameter to True. Note that creating the graph may take several seconds.


```python
>>> from tigergraphx import Graph
>>> G = Graph(graph_schema, connection)
```

    2025-02-25 17:53:21,057 - tigergraphx.core.managers.schema_manager - INFO - Graph existence check for FinancialGraph: does not exist
    2025-02-25 17:53:21,058 - tigergraphx.core.managers.schema_manager - INFO - Creating schema for graph: FinancialGraph...
    2025-02-25 17:53:24,286 - tigergraphx.core.managers.schema_manager - INFO - Graph schema created successfully.
    2025-02-25 17:53:24,287 - tigergraphx.core.managers.schema_manager - INFO - Adding vector attribute(s) for graph: FinancialGraph...
    2025-02-25 17:54:19,747 - tigergraphx.core.managers.schema_manager - INFO - Vector attribute(s) added successfully.


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

    2025-02-25 17:52:38,777 - tigergraphx.core.managers.node_manager - ERROR - Error adding nodes: ("The query didn't finish because it exceeded the query timeout threshold (16 seconds). Please check GSE log for license expiration and RESTPP/GPE log with request id (16777217.RESTPP_1_1.1740477142564.N) for details. Try increase RESTPP.Factory.DefaultQueryTimeoutSec or add header GSQL-TIMEOUT to override default system timeout. ", 'REST-3002')
    Number of Account Nodes Inserted: None


## Display the Number of Nodes
Next, let's verify that the data has been inserted into the graph by using the following command. As expected, the number of nodes is 5.


```python
>>> print(G.number_of_nodes())
```

    5


## Perform Vector Search
To find the top 2 most similar accounts to "Scott" based on the embedding, we use the following code. As expected, "Scott" will appear in the list with a distance of 0.


```python
>>> results = G.search(
...    data=[-0.017733968794345856, -0.01019224338233471, -0.016571875661611557],
...    vector_attribute_name="emb1",
...    node_type="Account",
...    limit=2
...)
>>> for result in results:
...     print(result)
```

    {'id': 'Paul', 'distance': 0.393388, 'name': 'Paul', 'isBlocked': False}
    {'id': 'Ed', 'distance': 0.8887959, 'name': 'Ed', 'isBlocked': False}


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

    2025-02-25 17:53:05,613 - tigergraphx.core.managers.schema_manager - INFO - Dropping graph: FinancialGraph...
    2025-02-25 17:53:09,351 - tigergraphx.core.managers.schema_manager - INFO - Graph dropped successfully.


---

## What’s Next?

Now that you've learned how to use TigerGraph for storing both graph data and vectors, you can dive into more advanced features of TigerGraphX:
- [GraphRAG Overview](../../graphrag/graphrag_overview): Learn about integrating graphs with LLMs.
- [API Reference](../../reference/features_overview): Dive deeper into TigerGraphX APIs.

---

Start unlocking the power of graphs with **TigerGraphX** today!
