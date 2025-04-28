# Graph

## Overview

::: tigergraphx.core.graph.Graph
    options:
        members: false

## Constructor

::: tigergraphx.core.graph.Graph.__init__

**Examples:**

Since our data is stored in a TigerGraph instance—whether on-premise or in the cloud—we need to configure the connection settings. Here are three methods for connecting:

- User/password authentication
- Secret-based authentication
- Token-based authentication

Though you set up the connection by directly assigning the `tigergraph_connection_config` parameter, it is highly recommended to use environment variables for security reasons. Environment variables can be set by running the following **shell** commands:

=== "User/password authentication"
    ```bash
    export TG_HOST=http://127.0.0.1
    export TG_USERNAME=tigergraph
    export TG_PASSWORD=tigergraph
    # The ports below are optional unless yours are different.
    export TG_RESTPP_PORT=14240
    export TG_GSQL_PORT=14240
    ```

=== "Secret-based authentication"
    ```bash
    export TG_HOST=http://127.0.0.1
    export TG_SECRET=<Your Secret>
    # The ports below are optional unless yours are different.
    export TG_RESTPP_PORT=14240
    export TG_GSQL_PORT=14240
    ```

=== "Token-based authentication"
    ```bash
    export TG_HOST=http://127.0.0.1
    export TG_TOKEN=<Your Token>
    # The ports below are optional unless yours are different.
    export TG_RESTPP_PORT=14240
    export TG_GSQL_PORT=14240
    ```

!!! note
    Both the default RESTPP and GSQL ports for TigerGraph 4 are 14240, which is consistent with TigerGraphX's default setting.

    In TigerGraph 3, the default RESTPP port is 9000 and the default GSQL port is 14240.

    If you are using TigerGraph 3 or have changed your server's port number, please set the environment variables TG_RESTPP_PORT and TG_GSQL_PORT accordingly.

TigerGraph is a schema-based database, which requires defining a schema to structure your graph. This schema specifies the graph name, nodes (vertices), edges (relationships), and their respective attributes.

We offer several methods to define the schema, including using a Python dictionary, YAML file, or JSON file. Below is an example of defining the same homogeneous graph—with one node type and one edge type—using all three approaches.


=== "Python Dictionary"
    ```python
    graph_schema = {
        "graph_name": "Social",
        "nodes": {
            "Person": {
                "primary_key": "name",
                "attributes": {
                    "name": "STRING",
                    "age": "UINT",
                    "gender": "STRING",
                },
            },
        },
        "edges": {
            "Friendship": {
                "is_directed_edge": False,
                "from_node_type": "Person",
                "to_node_type": "Person",
                "attributes": {
                    "closeness": "DOUBLE",
                },
            },
        },
    }
    ```

=== "YAML"
    ```python
    graph_schema = "/path/to/your/schema.yaml"
    ```
    The contents of the file "/path/to/your/schema.yaml" is as follows:
    ```yaml
    graph_name: Social
    nodes:
      Person:
        primary_key: name
        attributes:
          name: STRING
          age: UINT
          gender: STRING
    edges:
      Friendship:
        is_directed_edge: false
        from_node_type: Person
        to_node_type: Person
        attributes:
          closeness: DOUBLE
    ```

=== "JSON"
    ```python
    graph_schema = "/path/to/your/schema.json"
    ```
    The contents of the file "/path/to/your/schema.json" is as follows:
    ```json
    {
      "graph_name": "Social",
      "nodes": {
        "Person": {
          "primary_key": "name",
          "attributes": {
            "name": "STRING",
            "age": "UINT",
            "gender": "STRING"
          }
        }
      },
      "edges": {
        "Friendship": {
          "is_directed_edge": false,
          "from_node_type": "Person",
          "to_node_type": "Person",
          "attributes": {
            "closeness": "DOUBLE"
          }
        }
      }
    }
    ```

This schema defines a simple social graph where each person is represented as a node with attributes like `name`, `age`, and `gender`. Relationships between people are modeled as undirected "Friendship" edges, which include an attribute `closeness` to represent the strength of the connection. We will use this schema for the examples in most of the following methods.

Once the connection configuration and schema are set up, you can create a graph using the following code.

   ```python
   from tigergraphx import Graph
   G = Graph(graph_schema)
   ```

Running the command will create a graph using the user-defined schema if it does not already exist. If the graph exists, the command will return the existing graph. To overwrite an existing graph, set the `drop_existing_graph` parameter to `True`.

!!! Note
    Creating the graph may take several seconds.

---

**Alternative Connection Setup Methods**

An alternative way to set up the connection is by directly assigning the `tigergraph_connection_config` parameter. Suppose we have already defined the same `graph_schema` as before. Now let's define the connection. Like the schema, the connection can be defined using a Python dictionary, YAML file, or JSON file. Below are examples of defining the same connection using all three approaches:

=== "User/password authentication"
    ```python
    tigergraph_connection_config = {
        "host": "http://localhost",
        "username": "tigergraph",
        "password": "tigergraph",
    }
    ```

=== "Secret-based authentication"
    ```python
    tigergraph_connection_config = {
        "host": "http://localhost",
        "secret": "<Your Secret>",
    }
    ```

=== "Token-based authentication"
    ```python
    tigergraph_connection_config = {
        "host": "http://localhost",
        "token": "<Your Token>",
    }
    ```

Once the connection configuration and schema are set up, you can create a graph using the following code.

   ```python
   from tigergraphx import Graph
   G = Graph(graph_schema)
   ```

!!! warning
    Avoid setting the environment variables if you intend to configure the connection by directly assigning the `tigergraph_connection_config` parameter; otherwise, conflicts will occur.

::: tigergraphx.core.graph.Graph.from_db

**Examples:**

If a graph is already created in TigerGraph, you can easily retrieve it using the `from_db` class method. By simply providing the `graph_name`, the schema is automatically fetched, making this the most straightforward way to obtain an existing graph instance.

Retrieve a graph named "Social" from the database:
```python
from tigergraphx import Graph
G = Graph.from_db("Social")
```

For details on setting the TigerGraph connection configuration, please refer to [\_\_init\_\_](#tigergraphx.core.graph.Graph.__init__).

## NodeView
::: tigergraphx.core.graph.Graph.nodes

**Examples:**

`nodes` is a property of the `Graph` class. Using it allows you to get the total number of nodes, retrieve data for a specific node, and check if a node exists.

If your graph contains only one node type, you don’t need to specify the type when accessing nodes:
```python
>>> G = Graph(graph_schema)
>>> G.add_nodes_from(["Alice", "Mike"])
>>> len(G.nodes)
2
>>> G.nodes["Alice"]
{'name': 'Alice', 'age': 0, 'gender': ''}
>>> "Alice" in G.nodes
True
```

For graphs with multiple node types, you must include the node type when accessing nodes:
```python
>>> G = Graph(graph_schema)
>>> G.add_nodes_from(["Alice", "Mike"], "Person")
>>> len(G.nodes)
2
>>> G.nodes[("Person", "Alice")]
{'name': 'Alice', 'age': 0, 'gender': ''}
>>> ("Person", "Alice") in G.nodes
True
>>> G.clear()
True
```

## Schema Operations

The following methods handle schema operations:

::: tigergraphx.core.Graph.get_schema

**Examples:**

The default schema format retrieved from the database is a Python dictionary. 
```python
>>> G = Graph(graph_schema)
>>> G.get_schema()
{'graph_name': 'Social',
 'nodes': {'Person': {'primary_key': 'name',
   'attributes': {'name': {'data_type': <DataType.STRING: 'STRING'>,
     'default_value': None},
    'age': {'data_type': <DataType.UINT: 'UINT'>, 'default_value': None},
    'gender': {'data_type': <DataType.STRING: 'STRING'>,
     'default_value': None}},
   'vector_attributes': {}}},
 'edges': {'Friendship': {'is_directed_edge': False,
   'from_node_type': 'Person',
   'to_node_type': 'Person',
   'discriminator': set(),
   'attributes': {'closeness': {'data_type': <DataType.DOUBLE: 'DOUBLE'>,
     'default_value': None}}}}}
```

To retrieve the schema in JSON format, you can use:
```python
>>> G = Graph(graph_schema)
>>> G.get_schema("json")
'{"graph_name":"Social","nodes":{"Person":{"primary_key":"name","attributes":{"name":{"data_type":"STRING","default_value":null},"age":{"data_type":"UINT","default_value":null},"gender":{"data_type":"STRING","default_value":null}},"vector_attributes":{}}},"edges":{"Friendship":{"is_directed_edge":false,"from_node_type":"Person","to_node_type":"Person","discriminator":[],"attributes":{"closeness":{"data_type":"DOUBLE","default_value":null}}}}}'
```

::: tigergraphx.core.Graph.create_schema

**Examples:**

This method is rarely used because it is already called in the constructor.

If you do not need to drop the existing graph before creating the schema, you can use:
```python
>>> G = Graph(graph_schema)
>>> G.create_schema()
False
```

If you need to drop the existing graph, you can call:
```python
>>> G = Graph(graph_schema)
>>> G.create_schema(True)
2025-01-21 16:27:52,323 - tigergraphx.core.managers.schema_manager - INFO - Dropping graph: Social...
2025-01-21 16:27:55,618 - tigergraphx.core.managers.schema_manager - INFO - Graph dropped successfully.
2025-01-21 16:27:55,619 - tigergraphx.core.managers.schema_manager - INFO - Creating schema for graph: Social...
2025-01-21 16:27:58,573 - tigergraphx.core.managers.schema_manager - INFO - Graph schema created successfully.
True
```

::: tigergraphx.core.Graph.drop_graph

**Examples:**

```python
>>> G = Graph(graph_schema)
>>> G.drop_graph()
2025-01-20 16:45:04,544 - tigergraphx.core.managers.schema_manager - INFO - Dropping graph: Social...
2025-01-20 16:45:07,645 - tigergraphx.core.managers.schema_manager - INFO - Graph dropped successfully.
```

## Data Loading Operations
The following methods handle data loading operations:

::: tigergraphx.core.Graph.load_data

**Examples:**

The loading job can be defined using a Python dictionary, YAML file, or JSON file. Below are examples of defining the same loading job using each format:

=== "Python Dictionary"
    ```python
    loading_job_config = {
        "loading_job_name": "loading_job_Social",
        "files": [
            {
                "file_alias": "f_person",
                "file_path": "/path/to/person_data.csv",
                "csv_parsing_options": {
                    "separator": ",",
                    "header": True,
                    "EOL": "\\n",
                    "quote": "DOUBLE",
                },
                "node_mappings": [
                    {
                        "target_name": "Person",
                        "attribute_column_mappings": {
                            "name": "name",
                            "age": "age",
                        },
                    }
                ],
            },
            {
                "file_alias": "f_friendship",
                "file_path": "/path/to/friendship_data.csv",
                "edge_mappings": [
                    {
                        "target_name": "Friendship",
                        "source_node_column": "source",
                        "target_node_column": "target",
                        "attribute_column_mappings": {
                            "closeness": "closeness",
                        },
                    }
                ],
            },
        ],
    }
    ```

=== "YAML"
    ```python
    loading_job_config = "/path/to/your/loading_job_config.yaml"
    ```
    The contents of the file "/path/to/your/loading_job_config.yaml" is as follows:
    ```yaml
    loading_job_name: loading_job_Social
    files:
      - file_alias: f_person
        file_path: /path/to/person_data.csv
        csv_parsing_options:
          separator: ","
          header: true
          EOL: "\n"
          quote: DOUBLE
        node_mappings:
          - target_name: Person
            attribute_column_mappings:
              name: name
              age: age
      - file_alias: f_friendship
        file_path: /path/to/friendship_data.csv
        edge_mappings:
          - target_name: Friendship
            source_node_column: source
            target_node_column: target
            attribute_column_mappings:
              closeness: closeness
    ```

=== "JSON"
    ```python
    loading_job_config = "/path/to/your/loading_job_config.json"
    ```
    The contents of the file "/path/to/your/loading_job_config.json" is as follows:
    ```json
    {
      "loading_job_name": "loading_job_Social",
      "files": [
        {
          "file_alias": "f_person",
          "file_path": "/path/to/person_data.csv",
          "csv_parsing_options": {
            "separator": ",",
            "header": true,
            "EOL": "\\n",
            "quote": "DOUBLE"
          },
          "node_mappings": [
            {
              "target_name": "Person",
              "attribute_column_mappings": {
                "name": "name",
                "age": "age"
              }
            }
          ]
        },
        {
          "file_alias": "f_friendship",
          "file_path": "/path/to/friendship_data.csv",
          "edge_mappings": [
            {
              "target_name": "Friendship",
              "source_node_column": "source",
              "target_node_column": "target",
              "attribute_column_mappings": {
                "closeness": "closeness"
              }
            }
          ]
        }
      ]
    }
    ```

The code above defines the configuration for a loading job into the graph. It specifies the loading job name, the files to be imported, and how the data in those files maps to graph nodes and edges.

- **loading_job_name**: The name of the loading job.
- **files**: A list of file configurations.

    - **file_alias**: A unique identifier for the file within this loading job.
    - **file_path**: The path to the CSV file containing data to be loaded.
    - **csv_parsing_options**: Parsing options for the CSV file. The default value is:
    ```python
    {
        "separator": ",",
        "header": True,
        "EOL": "\\n",
        "quote": "DOUBLE",
    }
    ```
    This section is optional if the user’s configuration matches these defaults.
    - **node_mappings**: For files containing node data, this maps columns in the CSV to the corresponding node attributes in the graph.
    - **edge_mappings**: For files containing edge data, this maps columns in the CSV to the corresponding edge attributes and source/target nodes in the graph.


After the loading job is defined, we can load data by running the command below:
```python
>>> G = Graph(graph_schema)
>>> G.load_data(loading_job_config)
2025-02-27 17:06:48,941 - tigergraphx.core.managers.schema_manager - INFO - Creating schema for graph: Social...
2025-02-27 17:06:52,332 - tigergraphx.core.managers.schema_manager - INFO - Graph schema created successfully.
2025-02-27 17:06:52,353 - tigergraphx.core.managers.data_manager - INFO - Initiating data load for job: loading_job_Social...
2025-02-27 17:06:59,944 - tigergraphx.core.managers.data_manager - INFO - Data load completed successfully.
>>> print(G.number_of_nodes())
1
>>> print(G.number_of_edges())
1
>>> G.clear()
True
```

## Node Operations

The following methods manage nodes:

::: tigergraphx.core.Graph.add_node

!!! note
    This method follows a similar interface to NetworkX's `add_node()`.

!!! warning
    This method is intended for adding individual nodes, and is best suited for tiny datasets.

    For larger datasets, consider using `add_nodes_from` for small batches or `load_data` for handling large amounts of data efficiently.

**Examples:**

Single Node Type Example:
```python
>>> G = Graph(graph_schema)
>>> G.add_node("Alice", age=30, gender="Female")
>>> G.add_node("Mike", age=29)
>>> len(G.nodes)
2
>>> G.clear()
True
```

Multiple Node Types Example:
```python
>>> G = Graph(graph_schema)
>>> G.add_node("Alice", "Person", age=30, gender="Female")
>>> G.add_node("Mike", "Person", age=29)
>>> len(G.nodes)
2
>>> G.clear()
True
```

::: tigergraphx.core.Graph.add_nodes_from

!!! note
    This method follows a similar interface to NetworkX's `add_node()`.

!!! warning
    This method is best suited for adding small batches of nodes. For larger datasets, consider using `load_data` to improve efficiency.

**Examples:**

Single Node Type Example:
```python
>>> G = Graph(graph_schema)
>>> # Add nodes using a list of node IDs only, without additional attributes
>>> G.add_nodes_from(["Alice", "Mike"])
2
>>> # Add nodes with individual attributes using a list of (ID, attribute_dict) tuples
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29}),
... ]
>>> G.add_nodes_from(nodes_for_adding)
2
>>> # Add nodes with shared attributes applied to all listed node IDs
>>> G.add_nodes_from(["Alice", "Mike"], age=30)
2
>>> G.clear()
True
```

Multiple Node Types Example:
```python
>>> G = Graph(graph_schema)
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29}),
... ]
>>> G.add_nodes_from(nodes_for_adding, "Person")
2
>>> G.clear()
True

```

::: tigergraphx.core.Graph.remove_node

!!! note
    This method follows a similar interface to NetworkX's `remove_node()`.

**Examples:**

Single Node Type Example:
```python
>>> G = Graph(graph_schema)
>>> G.add_node("Alice", age=30, gender="Female")
>>> len(G.nodes)
1
>>> G.remove_node("Alice")
True
>>> len(G.nodes)
0
```

Multiple Node Types Example:
```python
>>> G = Graph(graph_schema)
>>> G.add_node("Alice", "Person", age=30, gender="Female")
>>> len(G.nodes)
1
>>> G.remove_node("Alice", "Person")
True
>>> len(G.nodes)
0
```

::: tigergraphx.core.Graph.has_node

!!! note
    This method follows a similar interface to NetworkX's `has_node()`.

**Examples:**

Single Node Type Example:
```python
>>> G = Graph(graph_schema)
>>> G.add_node("Alice", age=30, gender="Female")
>>> G.has_node("Alice")
True
>>> G.clear()
True
```

Multiple Node Types Example:
```python
>>> G = Graph(graph_schema)
>>> G.add_node("Alice", "Person", age=30, gender="Female")
>>> G.has_node("Alice", "Person")
True
>>> G.clear()
True
```

::: tigergraphx.core.Graph.get_node_data

**See also:**

- [NodeView.\_\_getitem\_\_](nodeview.md/#tigergraphx.core.view.NodeView.__getitem__)

**Examples:**

Single Node Type Example:
```python
>>> G = Graph(graph_schema)
>>> G.add_node("Alice", age=30, gender="Female")
>>> G.get_node_data("Alice")
{'name': 'Alice', 'age': 30, 'gender': 'Female'}
>>> G.clear()
True
```

Multiple Node Types Example:
```python
>>> G = Graph(graph_schema)
>>> G.add_node("Alice", "Person", age=30, gender="Female")
>>> G.get_node_data("Alice", "Person")
{'name': 'Alice', 'age': 30, 'gender': 'Female'}
>>> G.clear()
True
```

::: tigergraphx.core.Graph.get_node_edges

**Examples:**

Single Node Type Example:
```python
>>> G = Graph(graph_schema)
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29}),
... ]
>>> G.add_nodes_from(nodes_for_adding)
2
>>> G.add_edges_from([("Alice", "Mike")])
1
>>> G.get_node_edges("Alice")
[('Alice', 'Mike')]
>>> G.clear()
True
```

Multiple Node Types Example:
```python
>>> G = Graph(graph_schema)
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29}),
... ]
>>> G.add_nodes_from(nodes_for_adding, "Person")
2
>>> G.add_edges_from([("Alice", "Mike")], "Person", "Friendship", "Person")
1
>>> # Retrieve all edges connected to Alice, regardless of type
>>> G.get_node_edges("Alice", "Person")
[('Alice', 'Mike')]
>>> # Retrieve only edges of type "Friendship"
>>> G.get_node_edges("Alice", "Person", "Friendship")
[('Alice', 'Mike')]
>>> # Retrieve edges of multiple specified types.
>>> G.get_node_edges("Alice", "Person", ["Friendship", "Friendship"]) 
[('Alice', 'Mike')]
>>> G.clear()
True
```

::: tigergraphx.core.Graph.clear

!!! note
    This method follows a similar interface to NetworkX's `clear()`.

**Examples:**

```python
>>> G = Graph(graph_schema)
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29}),
... ]
>>> G.add_nodes_from(nodes_for_adding, "Person")
2
>>> len(G.nodes)
2
>>> G.clear()
True
>>> len(G.nodes)
0
```

## Edge Operations

The following methods manage edges:

::: tigergraphx.core.Graph.add_edge

!!! note
    This method follows a similar interface to NetworkX's `add_nodes_from()`.

!!! warning
    This method is intended for adding individual edges, and is best suited for tiny datasets.

    For larger datasets, consider using `add_edges_from` for small batches or `load_data` for handling large amounts of data efficiently.

**Examples:**

Single Node Type Example:
```python
>>> G = Graph(graph_schema)
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29}),
... ]
>>> G.add_nodes_from(nodes_for_adding)
2
>>> G.add_edge("Alice", "Mike", closeness=2.5)
>>> G.has_edge("Alice", "Mike")
True
>>> G.clear()
True
```

Multiple Node Types Example:
```python
>>> G = Graph(graph_schema)
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29}),
... ]
>>> G.add_nodes_from(nodes_for_adding, "Person")
2
>>> G.add_edge("Alice", "Mike", "Person", "Friendship", "Person", closeness=2.5)
>>> G.has_edge("Alice", "Mike", "Person", "Friendship", "Person")
True
>>> G.clear()
True
```

::: tigergraphx.core.Graph.add_edges_from

!!! note
    This method follows a similar interface to NetworkX's `add_edges_from()`.

!!! warning
    This method is best suited for adding small batches of edges. For larger datasets, consider using `load_data` to improve efficiency.

**Examples:**

Single Node Type Example:
```python
>>> G = Graph(graph_schema)
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29}),
... ]
>>> G.add_nodes_from(nodes_for_adding)
2
>>> # Add edges using a list of (source ID, target ID) tuples, without attributes
>>> G.add_edges_from([("Alice", "Mike"), ("Alice", "John")])
2
>>> # Add edges with individual attributes using (source ID, target ID, attribute_dict) tuples
>>> ebunch_to_add = [
...    ("Alice", "Mike"),
...    ("Alice", "John", {"closeness": 2.5}),
... ]
>>> G.add_edges_from(ebunch_to_add)
2
>>> # Add edges with shared attributes applied to all listed edges
>>> G.add_edges_from([("Alice", "Mike"), ("Alice", "John")], closeness=2.5)
2
>>> G.clear()
True
```

Multiple Node Types Example:
```python
>>> G = Graph(graph_schema)
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29}),
... ]
>>> G.add_nodes_from(nodes_for_adding, "Person")
2
>>> G.add_edges_from([("Alice", "Mike")], "Person", "Friendship", "Person")
1
>>> G.clear()
True
```

::: tigergraphx.core.Graph.has_edge

!!! note
    This method follows a similar interface to NetworkX's `has_edge()`.

**Examples:**

Single Node Type Example:
```python
>>> G = Graph(graph_schema)
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29}),
... ]
>>> G.add_nodes_from(nodes_for_adding)
2
>>> G.add_edge("Alice", "Mike")
>>> G.has_edge("Alice", "Mike")
True
>>> G.clear()
True
```

Multiple Node Types Example:
```python
>>> G = Graph(graph_schema)
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29}),
... ]
>>> G.add_nodes_from(nodes_for_adding, "Person")
2
>>> G.add_edge("Alice", "Mike", "Person", "Friendship", "Person")
>>> G.has_edge("Alice", "Mike", "Person", "Friendship", "Person")
True
>>> G.clear()
True
```

::: tigergraphx.core.Graph.get_edge_data

!!! note
    This method follows a similar interface to NetworkX's `get_edge_data()`.

**Examples:**

Single Node Type Example:
```python
>>> G = Graph(graph_schema)
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29}),
... ]
>>> G.add_nodes_from(nodes_for_adding)
2
>>> G.add_edge("Alice", "Mike", closeness=2.5)
>>> G.get_edge_data("Alice", "Mike")
{'closeness': 2.5}
>>> G.clear()
True
```

Multiple Node Types Example:
```python
>>> G = Graph(graph_schema)
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29}),
... ]
>>> G.add_nodes_from(nodes_for_adding, "Person")
2
>>> G.add_edge("Alice", "Mike", "Person", "Friendship", "Person", closeness=2.5)
>>> G.get_edge_data("Alice", "Mike", "Person", "Friendship", "Person")
{'closeness': 2.5}
>>> G.clear()
True
```

## Statistics Operations

The following methods handle statistics operations:

::: tigergraphx.core.Graph.degree

**Examples:**

Single Node Type Example:
```python
>>> G = Graph(graph_schema)
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29}),
... ]
>>> G.add_nodes_from(nodes_for_adding)
2
>>> G.add_edges_from([("Alice", "Mike")])
1
>>> G.degree("Alice")
1
>>> G.clear()
True
```

Multiple Node Types Example:
```python
>>> G = Graph(graph_schema)
>>> G.add_edges_from([("Alice", "Mike")], "Person", "Friendship", "Person")
1
>>> # Get the degree of node Alice for all edge types
>>> G.degree("Alice", "Person")
1
>>> # Get the degree of node Alice for a single edge type
>>> G.degree("Alice", "Person", "Friendship")
1
>>> # Get the degree of node Alice for multiple specified edge types.
>>> G.degree("Alice", "Person", ["Friendship", "Friendship"])
1
>>> G.clear()
True
```

::: tigergraphx.core.Graph.number_of_nodes

!!! note
    This method follows a similar interface to NetworkX's `number_of_nodes()`.

**Examples:**

```python
>>> G = Graph(graph_schema)
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29}),
... ]
>>> G.add_nodes_from(nodes_for_adding, "Person")
2
>>> # Get the total number of edges in the graph
>>> G.number_of_nodes()
2
>>> # Get the number of edges of type "Friendship"
>>> G.number_of_nodes("Person")
2
>>> G.clear()
True
```

::: tigergraphx.core.Graph.number_of_edges

!!! note
    This method follows a similar interface to NetworkX's `number_of_edges()`.

**Examples:**

```python
>>> G = Graph(graph_schema)
>>> ebunch_to_add = [
...    ("Alice", "Mike"),
...    ("Alice", "John", {"closeness": 2.5}),
... ]
>>> G.add_edges_from(ebunch_to_add)
2
>>> # Get the total number of edges in the graph
>>> G.number_of_edges()
2
>>> # Get the number of edges of type "Friendship"
>>> G.number_of_edges("Friendship")
2
>>> G.clear()
True
```

## Query Operations

The following methods perform query operations:

::: tigergraphx.core.Graph.get_nodes

**Examples:**

```python
>>> G = Graph(graph_schema)
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29, "gender": "Male"}),
...    ("Emily", {"age": 28, "gender": "Female"}),
... ]
>>> G.add_nodes_from(nodes_for_adding, "Person")
3
>>> # Get all nodes of type "Person"
>>> df = G.get_nodes("Person")
>>> print(df)
    v_id  v_type  gender   name  age
0   Mike  Person    Male   Mike   29
1  Emily  Person  Female  Emily   28
2  Alice  Person  Female  Alice   30
>>> # Get all nodes of all types
>>> df = G.get_nodes(all_node_types=True)
>>> print(df)
    v_id  v_type  gender   name  age
0   Mike  Person    Male   Mike   29
1  Alice  Person  Female  Alice   30
2  Emily  Person  Female  Emily   28
>>> # Retrieve nodes with a filter expression
>>> df = G.get_nodes(
...     node_type="Person",
...     node_alias="s", # "s" is the default value, so you can remove this line
...     filter_expression="s.age >= 29",
... )
>>> # Retrieve women aged 29 or older
>>> df = G.get_nodes(node_type="Person", filter_expression='s.age >= 29 and s.gender == "Female"')
>>> print(df)
    v_id  v_type  gender   name  age
0   Mike  Person    Male   Mike   29
1  Alice  Person  Female  Alice   30
>>> # Retrieve women aged 29 or older
>>> df = G.get_nodes(node_type="Person", filter_expression='s.age >= 29 and s.gender == "Female"')
>>> print(df)
    v_id  v_type  gender   name  age
0  Alice  Person  Female  Alice   30
>>> # Retrieve only specific attributes
>>> df = G.get_nodes(
...     node_type="Person",
...     return_attributes=["name", "gender"],
... )
>>> print(df)
    name  gender
0   Mike    Male
1  Emily  Female
2  Alice  Female
>>> # Limit the number of nodes returned
>>> df = G.get_nodes(
...     node_type="Person",
...     limit=1,
... )
>>> print(df)
    v_id  v_type  gender   name  age
0  Emily  Person  Female  Emily   28
>>> # Retrieve "Person" nodes with a specific filter expression,
>>> # use a custom alias, request only selected attributes, and limit the results.
>>> df = G.get_nodes(
...     node_type="Person",
...     filter_expression="s.age >= 29",
...     return_attributes=["name", "age"],
...     limit=1
... )
>>> print(df)
   name  age
0  Mike   29
>>> G.clear()
True
```

::: tigergraphx.core.Graph.get_neighbors

**Examples:**

```python
>>> G = Graph(graph_schema)
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29, "gender": "Male"}),
...    ("Emily", {"age": 28, "gender": "Female"}),
...    ("John", {"age": 27, "gender": "Male"}),
...    ("Mary", {"age": 28, "gender": "Female"}),
... ]
>>> G.add_nodes_from(nodes_for_adding, "Person")
5
>>> ebunch_to_add = [
...    ("Alice", "Mike", {"closeness": 1.5}),
...    ("Alice", "John", {"closeness": 2.5}),
...    ("John", "Emily", {"closeness": 3.5}),
...    ("Emily", "Mary", {"closeness": 3.5}),
... ]
>>> G.add_edges_from(ebunch_to_add)
4
>>> # Get neighbors of Alice
>>> df = G.get_neighbors(start_nodes="Alice", start_node_type="Person")
>>> print(df)
  gender  name  age
0   Male  Mike   29
1   Male  John   27
>>> # Get neighbors of Alice with a specific edge type
>>> df = G.get_neighbors(
...     start_nodes="Alice",
...     start_node_type="Person",
...     edge_types="Friendship",
... )
>>> print(df)
  gender  name  age
0   Male  Mike   29
1   Male  John   27
>>> # Get neighbors of Alice with a filter expression
>>> df = G.get_neighbors(
...     start_nodes="Alice",
...     start_node_type="Person",
...     start_node_alias="s", # "s" is the default value, so you can remove this line
...     edge_alias="e", # "e" is the default value, so you can remove this line
...     target_node_alias="t", # "t" is the default value, so you can remove this line
...     filter_expression="e.closeness > 1.5",
... )
>>> print(df)
  gender  name  age
0   Male  John   27
>>> # Retrieve only specific attributes for neighbors
>>> df = G.get_neighbors(
...     start_nodes="Alice",
...     start_node_type="Person",
...     return_attributes=["name", "gender"],
... )
>>> print(df)
   name gender
0  Mike   Male
1  John   Male
>>> # Limit the number of neighbors returned
>>> df = G.get_neighbors(
...     start_nodes="Alice",
...     start_node_type="Person",
...     limit=1,
... )
>>> print(df)
  gender  name  age
0   Male  Mike   29
>>> # Retrieve the first target node of type "Person" that is a friend of Alice (a "Person"),
>>> # filtering edges by "closeness > 1" and returning the target node's "name" and "gender".
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
   name gender
0  Mike   Male
>>> G.clear()
True
```

::: tigergraphx.core.Graph.bfs

**Examples:**

```python
>>> G = Graph(graph_schema)
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29, "gender": "Male"}),
...    ("Emily", {"age": 28, "gender": "Female"}),
...    ("John", {"age": 27, "gender": "Male"}),
...    ("Mary", {"age": 28, "gender": "Female"}),
... ]
>>> G.add_nodes_from(nodes_for_adding, "Person")
5
>>> ebunch_to_add = [
...    ("Alice", "Mike", {"closeness": 1.5}),
...    ("Alice", "John", {"closeness": 2.5}),
...    ("John", "Emily", {"closeness": 3.5}),
...    ("Emily", "Mary", {"closeness": 3.5}),
... ]
>>> G.add_edges_from(ebunch_to_add)
4
>>> # Breadth First Search example
>>> # First hop: Retrieve neighbors of "Alice" of type "Person"
>>> visited = set(["Alice"])  # Track visited nodes
>>> df = G.get_neighbors(start_nodes="Alice", start_node_type="Person")
>>> primary_ids = set(df['name']) - visited  # Exclude already visited nodes
>>> print(primary_ids)
{'Mike', 'John'}
>>> # Second hop: Retrieve neighbors of the nodes identified in the first hop
>>> visited.update(primary_ids)  # Mark these nodes as visited
>>> df = G.get_neighbors(start_nodes=primary_ids, start_node_type="Person")
>>> primary_ids = set(df['name']) - visited  # Exclude visited nodes
>>> print(primary_ids)
{'Emily'}
>>> # Third hop: Retrieve neighbors of the nodes identified in the second hop
>>> visited.update(primary_ids)  # Mark these nodes as visited
>>> df = G.get_neighbors(start_nodes=primary_ids, start_node_type="Person")
>>> df = df[~df['name'].isin(visited)]  # Remove visited nodes from the final result
>>> print(df)
   gender  name  age
0  Female  Mary   28
>>>
>>> # Alternatively, you can also use the built-in `bfs` method.
>>> df = G.bfs(start_nodes=["Alice"], node_type="Person", max_hops=3)
>>> print(df)
   gender  name  age  _bfs_level
0  Female  Mary   28           2
>>> G.clear()
True
```

## Vector Operations

The following methods handle vector operations:

!!! note
    Vector operations are supported only on TigerGraph 4.2 and later versions, which include the TigerVector feature.

The previous `Social` graph did not include vector attributes, which are essential for vector operations. Here, we define a new graph, `SocialWithVector`, that incorporates vector attributes, enabling tasks such as machine learning, similarity searches, and more.

Vector attributes go beyond standard node properties by storing numerical embeddings directly in the graph schema. In most cases, specifying the attribute dimension is sufficient—such as `"emb_1": 3` to define a 3-dimensional vector attribute. If additional customization is required, you can define properties like `index_type`, `data_type`, and `metric` using a dictionary format. For example, `"emb_2"` specifies these details explicitly, allowing you to tailor the vector attribute’s behavior.

Below are examples of how you can define the same graph schema—with one node type, one edge type, and vector attributes—using three different formats: a Python dictionary, YAML, and JSON.

=== "Python Dictionary"
    ```python
    graph_schema = {
        "graph_name": "SocialWithVector",
        "nodes": {
            "Person": {
                "primary_key": "name",
                "attributes": {
                    "name": "STRING",
                    "age": "UINT",
                    "gender": "STRING",
                },
                "vector_attributes": {
                    "emb_1": 3,
                    "emb_2": {
                        "dimension": 3,
                        "index_type": "HNSW",
                        "data_type": "FLOAT",
                        "metric": "COSINE",
                    },
                },
            },
        },
        "edges": {
            "Friendship": {
                "is_directed_edge": False,
                "from_node_type": "Person",
                "to_node_type": "Person",
                "attributes": {
                    "closeness": "DOUBLE",
                },
            },
        },
    }
    ```

=== "YAML"
    ```python
    graph_schema = "/path/to/your/schema_with_vector.yaml"
    ```
    The contents of the file "/path/to/your/schema_with_vector.yaml" are as follows:
    ```yaml
    graph_name: SocialWithVector
    nodes:
      Person:
        primary_key: name
        attributes:
          name: STRING
          age: UINT
          gender: STRING
        vector_attributes:
          emb_1: 3
          emb_2:
            dimension: 3
            index_type: HNSW
            data_type: FLOAT
            metric: COSINE
    edges:
      Friendship:
        is_directed_edge: false
        from_node_type: Person
        to_node_type: Person
        attributes:
          closeness: DOUBLE
    ```

=== "JSON"
    ```python
    graph_schema = "/path/to/your/schema_with_vector.json"
    ```
    The contents of the file "/path/to/your/schema_with_vector.json" are as follows:
    ```json
    {
      "graph_name": "SocialWithVector",
      "nodes": {
        "Person": {
          "primary_key": "name",
          "attributes": {
            "name": "STRING",
            "age": "UINT",
            "gender": "STRING"
          },
          "vector_attributes": {
            "emb_1": 3,
            "emb_2": {
              "dimension": 3,
              "index_type": "HNSW",
              "data_type": "FLOAT",
              "metric": "COSINE"
            }
          }
        }
      },
      "edges": {
        "Friendship": {
          "is_directed_edge": false,
          "from_node_type": "Person",
          "to_node_type": "Person",
          "attributes": {
            "closeness": "DOUBLE"
          }
        }
      }
    }
    ```

This schema represents a social graph where each person is a node with attributes like `name`, `age`, and `gender`. The addition of vector attributes—`emb_1` and `emb_2`—enables complex operations such as similarity-based queries. Relationships between people are defined as undirected "Friendship" edges, each with an attribute `closeness` that measures the strength of the connection.

You can create a graph using this schema by running:

```python
G = Graph(graph_schema)
```

This command will create a new graph using the schema if it doesn’t already exist. If the graph exists, it will simply return the existing graph instance. To overwrite an existing graph, set the `drop_existing_graph` parameter to `True`.

For details on setting the TigerGraph connection configuration, please refer to [\_\_init\_\_](#tigergraphx.core.graph.Graph.__init__).

!!! Note
    Creating the graph may take several seconds.

::: tigergraphx.core.Graph.upsert

**Examples:**

Single Node Type Example:
```python
>>> G = Graph(graph_schema)
>>> # Upsert a single node with vector data
>>> G.upsert(
...     data={"name": "Alice", "age": 30, "gender": "Female", "emb_1": [0.1, 0.2, 0.3]},
... )
1
>>> # Upsert multiple nodes with vector data
>>> G.upsert(
...     data=[
...         {"name": "Mike", "age": 29, "gender": "Male", "emb_1": [0.4, 0.5, 0.6]},
...         {"name": "Emily", "age": 28, "gender": "Female", "emb_1": [0.7, 0.8, 0.9]},
...     ],
... )
2
>>> # Get the total number of nodes in the graph
>>> G.number_of_nodes()
3
>>> G.clear()
True
```

Multiple Node Types Example:
```python
>>> G = Graph(graph_schema)
>>> # Upsert a single node with vector data
>>> G.upsert(
...     data={"name": "Alice", "age": 30, "gender": "Female", "emb_1": [0.1, 0.2, 0.3]},
...     node_type="Person",
... )
1
>>> # Upsert multiple nodes with vector data
>>> G.upsert(
...     data=[
...         {"name": "Mike", "age": 29, "gender": "Male", "emb_1": [0.4, 0.5, 0.6]},
...         {"name": "Emily", "age": 28, "gender": "Female", "emb_1": [0.7, 0.8, 0.9]},
...     ],
...     node_type="Person",
... )
2
>>> # Get the total number of nodes in the graph
>>> G.number_of_nodes()
3
>>> G.clear()
True
```

::: tigergraphx.core.Graph.fetch_node

**Examples:**

Single Node Type Example:
```python
>>> G = Graph(graph_schema)
>>> # Upsert a single node with vector data
>>> G.upsert(
...     data={"name": "Alice", "age": 30, "gender": "Female", "emb_1": [0.1, 0.2, 0.3]},
... )
1
>>> # Fetch vector data for a single node
>>> vector = G.fetch_node(
...     node_id="Alice",
...     vector_attribute_name="emb_1",
... )
>>> print(vector)
[0.1, 0.2, 0.3]
>>> G.clear()
True
```

Multiple Node Types Example:
```python
>>> G = Graph(graph_schema)
>>> # Upsert a single node with vector data, specifying node type
>>> G.upsert(
...     data={"name": "Alice", "age": 30, "gender": "Female", "emb_1": [0.1, 0.2, 0.3]},
...     node_type="Person",
... )
1
>>> # Fetch vector data for a single node, specifying node type
>>> vector = G.fetch_node(
...     node_id="Alice",
...     vector_attribute_name="emb_1",
...     node_type="Person",
... )
>>> print(vector)
[0.1, 0.2, 0.3]
>>> G.clear()
True
```

::: tigergraphx.core.Graph.fetch_nodes

**Examples:**

Single Node Type Example:
```python
>>> G = Graph(graph_schema)
>>> # Upsert multiple nodes with vector data
>>> G.upsert(
...     data=[
...         {"name": "Alice", "age": 30, "gender": "Female", "emb_1": [0.1, 0.2, 0.3]},
...         {"name": "Bob", "age": 32, "gender": "Male", "emb_1": [0.4, 0.5, 0.6]},
...     ]
... )
2
>>> # Fetch vector data for multiple nodes
>>> vectors = G.fetch_nodes(
...     node_ids=["Alice", "Bob"],
...     vector_attribute_name="emb_1",
... )
>>> print(vectors)
{'Alice': [0.1, 0.2, 0.3], 'Bob': [0.4, 0.5, 0.6]}
>>> G.clear()
True
```

Multiple Node Types Example:
```python
>>> G = Graph(graph_schema)
>>> # Upsert multiple nodes with vector data, specifying node type
>>> G.upsert(
...     data=[
...         {"name": "Alice", "age": 30, "gender": "Female", "emb_1": [0.1, 0.2, 0.3]},
...         {"name": "Bob", "age": 32, "gender": "Male", "emb_1": [0.4, 0.5, 0.6]},
...     ],
...     node_type="Person",
... )
2
>>> # Fetch vector data for multiple nodes, specifying node type
>>> vectors = G.fetch_nodes(
...     node_ids=["Alice", "Bob"],
...     vector_attribute_name="emb_1",
...     node_type="Person",
... )
>>> print(vectors)
{'Alice': [0.1, 0.2, 0.3], 'Bob': [0.4, 0.5, 0.6]}
>>> G.clear()
True
```

::: tigergraphx.core.Graph.search

**Examples:**

Single Node Type Example:
```python
>>> G = Graph(graph_schema)
>>> # Upsert multiple nodes with vector data
>>> G.upsert(
...     data=[
...         {"name": "Alice", "age": 30, "gender": "Female", "emb_1": [0.1, 0.2, 0.3]},
...         {"name": "Bob", "age": 32, "gender": "Male", "emb_1": [0.4, 0.5, 0.6]},
...         {"name": "Eve", "age": 29, "gender": "Female", "emb_1": [0.3, 0.2, 0.1]},
...     ]
... )
3
>>> # Search for nodes most similar to a query vector
>>> results = G.search(
...     data=[0.2, 0.2, 0.2],
...     vector_attribute_name="emb_1",
...     limit=2,
...     return_attributes=["name", "gender"],
... )
>>> for result in results:
...     print(result)
{'id': 'Bob', 'distance': 0.01307237, 'name': 'Bob', 'gender': 'Male'}
{'id': 'Eve', 'distance': 0.07417983, 'name': 'Eve', 'gender': 'Female'}
```

Multiple Node Types Example:
```python
>>> G = Graph(graph_schema)
>>> # Upsert multiple nodes with vector data, specifying node type
>>> G.upsert(
...     data=[
...         {"name": "Alice", "age": 30, "gender": "Female", "emb_1": [0.1, 0.2, 0.3]},
...         {"name": "Bob", "age": 32, "gender": "Male", "emb_1": [0.4, 0.5, 0.6]},
...         {"name": "Eve", "age": 29, "gender": "Female", "emb_1": [0.3, 0.2, 0.1]},
...     ],
...     node_type="Person",
... )
3
>>> # Search for nodes most similar to a query vector, specifying node type
>>> results = G.search(
...     data=[0.2, 0.2, 0.2],
...     vector_attribute_name="emb_1",
...     node_type="Person",
...     limit=2,
...     return_attributes=["name", "gender"],
... )
>>> for result in results:
...     print(result)
{'id': 'Bob', 'distance': 0.01307237, 'name': 'Bob', 'gender': 'Male'}
{'id': 'Eve', 'distance': 0.07417983, 'name': 'Eve', 'gender': 'Female'}
```

::: tigergraphx.core.Graph.search_multi_vector_attributes

**Examples:**

Single Node Type Example:
```python
>>> G = Graph(graph_schema)
>>> # Upsert multiple nodes with different vector attributes
>>> G.upsert(
...     data=[
...         {"name": "Alice", "age": 30, "gender": "Female", "emb_1": [0.1, 0.2, 0.3], "emb_2": [0.2, 0.4, 0.6]},
...         {"name": "Bob", "age": 32, "gender": "Male", "emb_1": [0.4, 0.5, 0.6], "emb_2": [0.5, 0.6, 0.7]},
...         {"name": "Eve", "age": 29, "gender": "Female", "emb_1": [0.3, 0.2, 0.1], "emb_2": [0.1, 0.2, 0.3]},
...     ]
... )
3
>>> # Search for nodes most similar to a query vector using multiple vector attributes
>>> results = G.search_multi_vector_attributes(
...     data=[0.1, 0.2, 0.3],
...     vector_attribute_names=["emb_1", "emb_2"],
...     limit=2,
...     return_attributes_list=[["name", "gender"], ["name"]],
... )
>>> for result in results:
...     print(result)
{'id': 'Alice', 'distance': 1.192093e-07, 'name': 'Alice', 'gender': 'Female'}
{'id': 'Eve', 'distance': 1.192093e-07, 'name': 'Eve'}
```

Multiple Node Types Example:
```python
>>> G = Graph(graph_schema)
>>> # Upsert multiple nodes with vector attributes
>>> G.upsert(
...     data=[
...         {"name": "Alice", "age": 30, "gender": "Female", "emb_1": [0.1, 0.2, 0.3], "emb_2": [0.2, 0.4, 0.6]},
...         {"name": "Bob", "age": 32, "gender": "Male", "emb_1": [0.4, 0.5, 0.6], "emb_2": [0.5, 0.6, 0.7]},
...         {"name": "Eve", "age": 29, "gender": "Female", "emb_1": [0.3, 0.2, 0.1], "emb_2": [0.1, 0.2, 0.3]},
...     ],
...     node_type="Person",
... )
3
>>> # Search for nodes most similar to a query vector using multiple vector attributes
>>> results = G.search_multi_vector_attributes(
...     data=[0.1, 0.2, 0.3],
...     vector_attribute_names=["emb_1", "emb_2"],
...     node_types=["Person", "Person"],
...     limit=2,
...     return_attributes_list=[["name", "gender"], ["name"]],
... )
>>> for result in results:
...     print(result)
{'id': 'Alice', 'distance': 1.192093e-07, 'name': 'Alice', 'gender': 'Female'}
{'id': 'Bob', 'distance': 0.02536821, 'name': 'Bob', 'gender': 'Male'}
>>> G.clear()
True
```

::: tigergraphx.core.Graph.search_top_k_similar_nodes

**Examples:**

Single Node Type Example:
```python
>>> G = Graph(graph_schema)
>>> # Upsert a node with vector data
>>> G.upsert(
...     data=[
...         {"name": "Alice", "age": 30, "gender": "Female", "emb_1": [0.1, 0.2, 0.3]},
...         {"name": "Bob", "age": 32, "gender": "Male", "emb_1": [0.1, 0.2, 0.4]},
...         {"name": "Eve", "age": 29, "gender": "Female", "emb_1": [0.5, 0.6, 0.7]},
...     ]
... )
3
>>> # Retrieve the top-1 nodes similar to "Alice" based on the emb_1 vector
>>> similar_nodes = G.search_top_k_similar_nodes(
...     node_id="Alice",
...     vector_attribute_name="emb_1",
...     limit=1,
...     return_attributes=["name", "age", "gender"]
... )
>>> for node in similar_nodes:
...     print(node)
{'id': 'Bob', 'distance': 0.008539915, 'name': 'Bob', 'age': 32, 'gender': 'Male'}
>>> G.clear()
True
```

Multiple Node Types Example:
```python
>>> G = Graph(graph_schema)
>>> # Upsert nodes with vector data
>>> G.upsert(
...     data=[
...         {"name": "Alice", "age": 30, "gender": "Female", "emb_1": [0.1, 0.2, 0.3]},
...         {"name": "Bob", "age": 32, "gender": "Male", "emb_1": [0.1, 0.2, 0.4]},
...         {"name": "Eve", "age": 29, "gender": "Female", "emb_1": [0.5, 0.6, 0.7]},
...     ],
...     node_type="Person"
... )
3
>>> # Retrieve the top-5 nodes similar to "Alice" based on the emb_1 vector
>>> similar_nodes = G.search_top_k_similar_nodes(
...     node_id="Alice",
...     vector_attribute_name="emb_1",
...     node_type="Person",
...     limit=5,
...     return_attributes=["name", "age", "gender"]
... )
>>> for node in similar_nodes:
...     print(node)
{'id': 'Bob', 'distance': 0.008539915, 'name': 'Bob', 'age': 32, 'gender': 'Male'}
{'id': 'Eve', 'distance': 0.03167039, 'name': 'Eve', 'age': 29, 'gender': 'Female'}
>>> G.clear()
True
```
