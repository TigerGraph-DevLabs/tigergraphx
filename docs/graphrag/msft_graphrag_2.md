# Supporting Microsoft’s GraphRAG: Part 2 - Graph Creation and Data Loading

In the [previous section](../msft_graphrag_1), we used Microsoft's GraphRAG to convert unstructured documents into Parquet files, and then used TigerGraphX to transform these files into CSV format.

Now, let’s use Jupyter Notebook to create the schema and load the CSV files into TigerGraph.

To run this Jupyter Notebook, you can download the original `.ipynb` file from [msft_graphrag_2.ipynb](https://github.com/tigergraph/tigergraphx/tree/main/docs/graphrag/msft_graphrag_2.ipynb).

## Create a Graph
TigerGraph is a schema-based database, which requires defining a schema to structure your graph. This schema specifies the graph name, nodes (vertices), edges (relationships), and their respective attributes.

### Define a Graph Schema

The graph schema can be defined using a YAML file, a JSON file, or a Python dictionary.
In this example, we will initialize a graph using a schema defined in [a YAML file](https://github.com/tigergraph/tigergraphx/blob/main/applications/msft_graphrag/query/resources/graph_schema.yaml). The schema structure is represented visually in the following image.

![image](https://github.com/tigergraph/tigergraphx/blob/main/docs/images/graphrag/schema.png?raw=true)


```python
from tigergraphx import Graph
resource_dir = "../../applications/msft_graphrag/query/resources/"
graph_schema = resource_dir + "graph_schema.yaml"
```

### Define the TigerGraph Connection Configuration

In addition to defining the schema, you also need a connection configuration to establish communication with the TigerGraph server. You can connect using either a username/password, a secret, or a token. Below is an example of connecting to TigerGraph using a username and password.


```python
connection = {
    "host": "http://127.0.0.1",
    "username": "tigergraph",
    "password": "tigergraph",
}
```

### Create a Graph
Running the following command will create a graph using the user-defined schema if it does not already exist. If the graph exists, the command will return the existing graph. To overwrite the existing graph, set the drop_existing_graph parameter to True. Note that creating the graph may take several seconds.


```python
G = Graph(
    graph_schema=graph_schema,
    tigergraph_connection_config=connection,
    drop_existing_graph=False,
)
```

    2025-01-05 23:22:37,193 - tigergraphx.core.graph.base_graph - INFO - Creating schema for graph GraphRAG...
    2025-01-05 23:23:30,577 - tigergraphx.core.graph.base_graph - INFO - Schema created successfully.


## Load Data
First, let's check the total number of nodes in the graph. As anticipated, the graph is currently empty.


```python
print(G.number_of_nodes())
```

    0


After that, we will load data into the graph using a pre-defined loading job configuration. The configuration is stored in [a YAML file](https://github.com/tigergraph/tigergraphx/blob/main/applications/msft_graphrag/query/resources/loading_job_config.yaml). Note that loading the data may take several seconds.


```python
loading_job_config = resource_dir + "loading_job_config.yaml"
G.load_data(loading_job_config)
```

Now, let's check the total number of nodes in the graph again. We should observe that some nodes have been successfully loaded into the graph.


```python
print(G.number_of_nodes())
```

    371


---

## Next Steps

- [Supporting Microsoft’s GraphRAG: Part 3](../msft_graphrag_3): Use Jupyter Notebook to explore graph data and perform Graph Analysis.

---

Start transforming your GraphRAG workflows with the power of **TigerGraphX** today!
