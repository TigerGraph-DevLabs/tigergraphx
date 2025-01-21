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
   G = Graph(graph_schema)
   ```

!!! warning
    Avoid setting the environment variables if you intend to configure the connection by directly assigning the `tigergraph_connection_config` parameter; otherwise, conflicts will occur.

::: tigergraphx.core.graph.Graph.from_db

**Examples:**

If a graph is already created in TigerGraph, you can easily retrieve it using the `from_db` class method. By simply providing the `graph_name`, the schema is automatically fetched, making this the most straightforward way to obtain an existing graph instance.

Retrieve a graph named "Social" from the database:
```python
G = Graph.from_db("Social")
```

For details on setting the TigerGraph connection configuration, please refer to [\_\_init\_\_](#tigergraphx.core.graph.Graph.__init__).

## NodeView
::: tigergraphx.core.graph.Graph.nodes

**Examples:**

`nodes` is a property of the `Graph` class. Using it allows you to get the total number of nodes, retrieve data for a specific node, and check if a node exists.

If your graph contains only one node type, you don’t need to specify the type when accessing nodes:
```python
>>> G = Graph.from_db("Social")
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
>>> G = Graph.from_db("Social")
>>> G.add_nodes_from(["Alice", "Mike"], "Person")
>>> len(G.nodes)
2
>>> G.nodes[("Person", "Alice")]
{'name': 'Alice', 'age': 0, 'gender': ''}
>>> ("Person", "Alice") in G.nodes
True
```

## Schema Operations

The following methods handle schema operations:

::: tigergraphx.core.Graph.get_schema

**Examples:**

The default schema format retrieved from the database is a Python dictionary. 
```python
>>> G = Graph.from_db("Social")
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
>>> G = Graph.from_db("Social")
>>> G.get_schema("json")
'{"graph_name":"Social","nodes":{"Person":{"primary_key":"name","attributes":{"name":{"data_type":"STRING","default_value":null},"age":{"data_type":"UINT","default_value":null},"gender":{"data_type":"STRING","default_value":null}},"vector_attributes":{}}},"edges":{"Friendship":{"is_directed_edge":false,"from_node_type":"Person","to_node_type":"Person","discriminator":[],"attributes":{"closeness":{"data_type":"DOUBLE","default_value":null}}}}}'
```

::: tigergraphx.core.Graph.create_schema

**Examples:**

This method is rarely used because it is already called in the constructor.

If you do not need to drop the existing graph before creating the schema, you can use:
```python
>>> G = Graph.from_db("Social")
>>> G.create_schema()
2025-01-21 16:27:34,021 - tigergraphx.core.managers.schema_manager - INFO - Graph existence check for Social: exists
2025-01-21 16:27:34,022 - tigergraphx.core.managers.schema_manager - INFO - Graph 'Social' already exists. Skipping graph creation.
False
```

If you need to drop the existing graph, you can call:
```python
>>> G = Graph.from_db("Social")
>>> G.create_schema(True)
2025-01-21 16:27:52,323 - tigergraphx.core.managers.schema_manager - INFO - Graph existence check for Social: exists
2025-01-21 16:27:52,323 - tigergraphx.core.managers.schema_manager - INFO - Dropping graph: Social...
2025-01-21 16:27:55,618 - tigergraphx.core.managers.schema_manager - INFO - Graph dropped successfully.
2025-01-21 16:27:55,619 - tigergraphx.core.managers.schema_manager - INFO - Creating schema for graph: Social...
2025-01-21 16:27:58,573 - tigergraphx.core.managers.schema_manager - INFO - Graph schema created successfully.
True
```

::: tigergraphx.core.Graph.drop_graph

**Examples:**

```python
>>> G = Graph.from_db("Social")
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
>>> G = Graph.from_db("Social")
>>> G.load_data(loading_job_config)
2025-01-21 16:31:41,444 - tigergraphx.core.managers.data_manager - INFO - Initiating data load for job: loading_job_Social...
2025-01-21 16:31:49,010 - tigergraphx.core.managers.data_manager - INFO - Data load completed successfully.
```

## Node Operations

The following methods manage nodes:

::: tigergraphx.core.Graph.add_node

!!! warning
    This method is intended for adding individual nodes, and is best suited for tiny datasets.

    For larger datasets, consider using `add_nodes_from` for small batches or `load_data` for handling large amounts of data efficiently.

**Examples:**

Single Node Type Example:
```python
>>> G = Graph.from_db("Social")
>>> G.add_node("Alice", age=30, gender="Female")
>>> G.add_node("Mike", age=29)
>>> len(G.nodes)
2
```

Multiple Node Types Example:
```python
>>> G = Graph.from_db("Social")
>>> G.add_node("Alice", "Person", age=30, gender="Female")
>>> G.add_node("Mike", "Person", age=29)
>>> len(G.nodes)
2
```

::: tigergraphx.core.Graph.add_nodes_from

!!! warning
    This method is best suited for adding small batches of nodes. For larger datasets, consider using `load_data` to improve efficiency.

**Examples:**

Single Node Type Example:
```python
>>> G = Graph.from_db("Social")
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
```

Multiple Node Types Example:
```python
>>> G = Graph.from_db("Social")
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29}),
... ]
>>> G.add_nodes_from(nodes_for_adding, "Person")
2
```

::: tigergraphx.core.Graph.remove_node

**Examples:**

Single Node Type Example:
```python
>>> G = Graph.from_db("Social")
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
>>> G = Graph.from_db("Social")
>>> G.add_node("Alice", "Person", age=30, gender="Female")
>>> len(G.nodes)
1
>>> G.remove_node("Alice", "Person")
True
>>> len(G.nodes)
0
```

::: tigergraphx.core.Graph.has_node

**Examples:**

Single Node Type Example:
```python
>>> G = Graph.from_db("Social")
>>> G.add_node("Alice", age=30, gender="Female")
>>> G.has_node("Alice")
True
```

Multiple Node Types Example:
```python
>>> G = Graph.from_db("Social")
>>> G.add_node("Alice", "Person", age=30, gender="Female")
>>> G.has_node("Alice", "Person")
True
```

::: tigergraphx.core.Graph.get_node_data

**See also:**

- [NodeView.\_\_getitem\_\_](../nodeview/#tigergraphx.core.view.NodeView.__getitem__)

**Examples:**

Single Node Type Example:
```python
>>> G = Graph.from_db("Social")
>>> G.add_node("Alice", age=30, gender="Female")
>>> G.get_node_data("Alice")
{'name': 'Alice', 'age': 30, 'gender': 'Female'}
```

Multiple Node Types Example:
```python
>>> G = Graph.from_db("Social")
>>> G.add_node("Alice", "Person", age=30, gender="Female")
>>> G.get_node_data("Alice", "Person")
{'name': 'Alice', 'age': 30, 'gender': 'Female'}
```


::: tigergraphx.core.Graph.get_node_edges

**Examples:**

Single Node Type Example:
```python
>>> G = Graph.from_db("Social")
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
```

Multiple Node Types Example:
```python
>>> G = Graph.from_db("Social")
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
>>> # Assumes that both "Friendship" and "Follows" are edge types in the Social graph.
>>> G.get_node_edges("Alice", "Person", ["Friendship", "Follows"]) 
[('Alice', 'Mike')]
```

::: tigergraphx.core.Graph.clear

**Examples:**

```python
>>> G = Graph.from_db("Social")
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

!!! warning
    This method is intended for adding individual edges, and is best suited for tiny datasets.

    For larger datasets, consider using `add_edges_from` for small batches or `load_data` for handling large amounts of data efficiently.

**Examples:**

Single Node Type Example:
```python
>>> G = Graph.from_db("Social")
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29}),
... ]
>>> G.add_nodes_from(nodes_for_adding)
2
>>> G.add_edge("Alice", "Mike", closeness=2.5)
>>> G.has_edge("Alice", "Mike")
True
```

Multiple Node Types Example:
```python
>>> G = Graph.from_db("Social")
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29}),
... ]
>>> G.add_nodes_from(nodes_for_adding, "Person")
2
>>> G.add_edge("Alice", "Mike", "Person", "Friendship", "Person", closeness=2.5)
>>> G.has_edge("Alice", "Mike", "Person", "Friendship", "Person")
True
```

::: tigergraphx.core.Graph.add_edges_from

!!! warning
    This method is best suited for adding small batches of edges. For larger datasets, consider using `load_data` to improve efficiency.

**Examples:**

Single Node Type Example:
```python
>>> G = Graph.from_db("Social")
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
```

Multiple Node Types Example:
```python
>>> G = Graph.from_db("Social")
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29}),
... ]
>>> G.add_nodes_from(nodes_for_adding, "Person")
2
>>> G.add_edges_from([("Alice", "Mike")], "Person", "Friendship", "Person")
1
```

::: tigergraphx.core.Graph.has_edge

**Examples:**

Single Node Type Example:
```python
>>> G = Graph.from_db("Social")
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29}),
... ]
>>> G.add_nodes_from(nodes_for_adding)
2
>>> G.add_edge("Alice", "Mike")
>>> G.has_edge("Alice", "Mike")
True
```

Multiple Node Types Example:
```python
>>> G = Graph.from_db("Social")
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29}),
... ]
>>> G.add_nodes_from(nodes_for_adding, "Person")
2
>>> G.add_edge("Alice", "Mike", "Person", "Friendship", "Person")
>>> G.has_edge("Alice", "Mike", "Person", "Friendship", "Person")
True
```

::: tigergraphx.core.Graph.get_edge_data

**Examples:**

Single Node Type Example:
```python
>>> G = Graph.from_db("Social")
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29}),
... ]
>>> G.add_nodes_from(nodes_for_adding)
2
>>> G.add_edge("Alice", "Mike", closeness=2.5)
>>> G.get_edge_data("Alice", "Mike")
{'closeness': 2.5}
```

Multiple Node Types Example:
```python
>>> G = Graph.from_db("Social")
>>> nodes_for_adding = [
...    ("Alice", {"age": 30, "gender": "Female"}),
...    ("Mike", {"age": 29}),
... ]
>>> G.add_nodes_from(nodes_for_adding, "Person")
2
>>> G.add_edge("Alice", "Mike", "Person", "Friendship", "Person")
>>> G.get_edge_data("Alice", "Mike", "Person", "Friendship", "Person")
{'closeness': 2.5}
```

## Statistics Operations

The following methods handle statistics operations:

::: tigergraphx.core.Graph.degree

**Examples:**

Single Node Type Example:
```python
>>> G = Graph.from_db("Social")
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
```

Multiple Node Types Example:
```python
>>> G = Graph.from_db("Social")
>>> G.add_edges_from([("Alice", "Mike")], "Person", "Friendship", "Person")
1
>>> # Get the degree of node Alice for all edge types
>>> G.degree("Alice", "Person")
1
>>> # Get the degree of node Alice for a single edge type
>>> G.degree("Alice", "Person", "Friendship")
1
>>> # Get the degree of node Alice for multiple specified edge types.
>>> # Assumes that both "Friendship" and "Follows" are edge types in the Social graph.
>>> G.degree("Alice", "Person", ["Friendship", "Follows"])
1
```

::: tigergraphx.core.Graph.number_of_nodes

**Examples:**

```python
>>> G = Graph.from_db("Social")
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
```

::: tigergraphx.core.Graph.number_of_edges

**Examples:**

```python
>>> G = Graph.from_db("Social")
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
```

## Query Operations

The following methods perform query operations:

::: tigergraphx.core.Graph.run_query

**Examples:**

```python
>>> G = Graph.from_db("Social")
>>> 
```

::: tigergraphx.core.Graph.get_nodes

**Examples:**

```python
>>> G = Graph.from_db("Social")
>>> 
```

::: tigergraphx.core.Graph.get_nodes_from_spec

**Examples:**

```python
>>> G = Graph.from_db("Social")
>>> 
```

::: tigergraphx.core.Graph.get_neighbors

**Examples:**

```python
>>> G = Graph.from_db("Social")
>>> 
```

::: tigergraphx.core.Graph.get_neighbors_from_spec

**Examples:**

```python
>>> G = Graph.from_db("Social")
>>> 
```


## Vector Operations

The following methods handle vector operations:

::: tigergraphx.core.Graph.upsert

**Examples:**

```python
>>> G = Graph.from_db("Social")
>>> 
```

::: tigergraphx.core.Graph.fetch_node

**Examples:**

```python
>>> G = Graph.from_db("Social")
>>> 
```

::: tigergraphx.core.Graph.fetch_nodes

**Examples:**

```python
>>> G = Graph.from_db("Social")
>>> 
```

::: tigergraphx.core.Graph.search

**Examples:**

```python
>>> G = Graph.from_db("Social")
>>> 
```

::: tigergraphx.core.Graph.search_multi_vector_attributes

**Examples:**

```python
>>> G = Graph.from_db("Social")
>>> 
```

::: tigergraphx.core.Graph.search_top_k_similar_nodes

**Examples:**

```python
>>> G = Graph.from_db("Social")
>>> 
```

