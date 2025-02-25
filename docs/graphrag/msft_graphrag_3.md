# Supporting Microsoft’s GraphRAG: Part 3 - Graph Analysis

In the [previous section](../msft_graphrag_2), we have created a graph in TigerGraph, and loaded the CSV data into it.

Now, let’s use Jupyter Notebook to explore the graph data and perform graph analysis.

To run this Jupyter Notebook, you can download the original `.ipynb` file from [msft_graphrag_3.ipynb](https://github.com/tigergraph/tigergraphx/tree/main/docs/graphrag/msft_graphrag_3.ipynb).

---

## Get the Graph from TigerGraph
Since the graph has already been created in TigerGraph, redefining its schema is unnecessary. Instead, you can provide the graph name to retrieve it. TigerGraphX will verify if the graph exists in TigerGraph and, if it does, will return the corresponding graph.


```python
from tigergraphx import Graph
connection = {
    "host": "http://127.0.0.1",
    "username": "tigergraph",
    "password": "tigergraph",
}
G = Graph.from_db("GraphRAG", connection)
```

    2025-01-05 23:30:15,203 - tigergraphx.core.graph.base_graph - INFO - Creating schema for graph GraphRAG...
    2025-01-05 23:30:15,223 - tigergraphx.core.graph.base_graph - INFO - Schema created successfully.


## Display the Graph Schema

Let's retrieve the graph schema using the `get_schema` method. The output is a Python dictionary containing three keys: `"graph_name"`, `"nodes"`, and `"edges"`. We'll print each of them individually to explore the schema details.
### Retrieve the Graph Schema and Display the Graph Name


```python
schema = G.get_schema()
print(schema["graph_name"])
```

    GraphRAG


### Display the Node Tyeps


```python
for node in schema["nodes"].items():
    print(node)
```

    ('Document', {'primary_key': 'id', 'attributes': {'title': {'data_type': <DataType.STRING: 'STRING'>, 'default_value': None}, 'id': {'data_type': <DataType.STRING: 'STRING'>, 'default_value': None}}, 'vector_attributes': {}})
    ('TextUnit', {'primary_key': 'id', 'attributes': {'text': {'data_type': <DataType.STRING: 'STRING'>, 'default_value': None}, 'n_tokens': {'data_type': <DataType.UINT: 'UINT'>, 'default_value': None}, 'id': {'data_type': <DataType.STRING: 'STRING'>, 'default_value': None}}, 'vector_attributes': {}})
    ('Entity', {'primary_key': 'id', 'attributes': {'human_readable_id': {'data_type': <DataType.UINT: 'UINT'>, 'default_value': None}, 'name': {'data_type': <DataType.STRING: 'STRING'>, 'default_value': None}, 'entity_type': {'data_type': <DataType.STRING: 'STRING'>, 'default_value': None}, 'description': {'data_type': <DataType.STRING: 'STRING'>, 'default_value': None}, 'id': {'data_type': <DataType.STRING: 'STRING'>, 'default_value': None}}, 'vector_attributes': {}})
    ('Relationship', {'primary_key': 'id', 'attributes': {'human_readable_id': {'data_type': <DataType.UINT: 'UINT'>, 'default_value': None}, 'rank': {'data_type': <DataType.UINT: 'UINT'>, 'default_value': None}, 'weight': {'data_type': <DataType.DOUBLE: 'DOUBLE'>, 'default_value': None}, 'description': {'data_type': <DataType.STRING: 'STRING'>, 'default_value': None}, 'id': {'data_type': <DataType.STRING: 'STRING'>, 'default_value': None}}, 'vector_attributes': {}})
    ('Community', {'primary_key': 'id', 'attributes': {'level': {'data_type': <DataType.UINT: 'UINT'>, 'default_value': None}, 'rank': {'data_type': <DataType.DOUBLE: 'DOUBLE'>, 'default_value': None}, 'rank_explanation': {'data_type': <DataType.STRING: 'STRING'>, 'default_value': None}, 'title': {'data_type': <DataType.STRING: 'STRING'>, 'default_value': None}, 'full_content': {'data_type': <DataType.STRING: 'STRING'>, 'default_value': None}, 'summary': {'data_type': <DataType.STRING: 'STRING'>, 'default_value': None}, 'id': {'data_type': <DataType.STRING: 'STRING'>, 'default_value': None}}, 'vector_attributes': {}})


### Display the Edge Types


```python
for edge in schema["edges"].items():
    print(edge)
```

    ('document_contains_text_unit', {'is_directed_edge': False, 'from_node_type': 'Document', 'to_node_type': 'TextUnit', 'discriminator': set(), 'attributes': {}})
    ('text_unit_contains_entity', {'is_directed_edge': False, 'from_node_type': 'TextUnit', 'to_node_type': 'Entity', 'discriminator': set(), 'attributes': {}})
    ('text_unit_contains_relationship', {'is_directed_edge': False, 'from_node_type': 'TextUnit', 'to_node_type': 'Relationship', 'discriminator': set(), 'attributes': {}})
    ('relationship_source', {'is_directed_edge': False, 'from_node_type': 'Relationship', 'to_node_type': 'Entity', 'discriminator': set(), 'attributes': {}})
    ('relationship_target', {'is_directed_edge': False, 'from_node_type': 'Relationship', 'to_node_type': 'Entity', 'discriminator': set(), 'attributes': {}})
    ('community_contains_entity', {'is_directed_edge': False, 'from_node_type': 'Community', 'to_node_type': 'Entity', 'discriminator': set(), 'attributes': {}})
    ('community_contains_relationship', {'is_directed_edge': False, 'from_node_type': 'Community', 'to_node_type': 'Relationship', 'discriminator': set(), 'attributes': {}})


## Display Node and Edge Counts

Gain deeper insights into the graph by exploring details such as the total number of nodes and the count of nodes for each node type.

### Display the Total Number of Nodes


```python
G.number_of_nodes()
```




    371



### Display the Count of Nodes for Each Node Type


```python
for node_type in schema["nodes"]:
    print(f"{node_type}: {G.number_of_nodes(node_type)}")
```

    Document: 1
    TextUnit: 42
    Entity: 138
    Relationship: 168
    Community: 22


### Display the Total Number of Edges


```python
G.number_of_edges()
```




    1545



### Display the Count of Edges for Each Edge Type


```python
for edge_type in schema["edges"]:
    print(f"{edge_type}: {G.number_of_edges(edge_type)}")
```

    document_contains_text_unit: 42
    text_unit_contains_entity: 274
    text_unit_contains_relationship: 238
    relationship_source: 168
    relationship_target: 168
    community_contains_entity: 236
    community_contains_relationship: 419


## Retrieve Sample Nodes from the Graph


```python
G.get_nodes(node_type="Entity", limit=2)
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
      <th>v_id</th>
      <th>v_type</th>
      <th>human_readable_id</th>
      <th>entity_type</th>
      <th>name</th>
      <th>description</th>
      <th>id</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>473502492d0a419981fed4fbc1493832</td>
      <td>Entity</td>
      <td>69</td>
      <td>PERSON</td>
      <td>THE THREE MISS FEZZIWIGS</td>
      <td>Daughters of Mr. and Mrs. Fezziwig, described ...</td>
      <td>473502492d0a419981fed4fbc1493832</td>
    </tr>
    <tr>
      <th>1</th>
      <td>6fb90dc954fe40d5969f7532a66376e9</td>
      <td>Entity</td>
      <td>108</td>
      <td>PERSON</td>
      <td>WANT</td>
      <td>Want is depicted as a girl, symbolizing povert...</td>
      <td>6fb90dc954fe40d5969f7532a66376e9</td>
    </tr>
  </tbody>
</table>
</div>




```python
G.get_nodes(node_type="Relationship", limit=2)
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
      <th>v_id</th>
      <th>v_type</th>
      <th>human_readable_id</th>
      <th>rank</th>
      <th>weight</th>
      <th>description</th>
      <th>id</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>9953ed9db4c5418e8bf9fee18032c0da</td>
      <td>Relationship</td>
      <td>63</td>
      <td>9</td>
      <td>20</td>
      <td>Fezziwig and Mrs. Fezziwig share a close perso...</td>
      <td>9953ed9db4c5418e8bf9fee18032c0da</td>
    </tr>
    <tr>
      <th>1</th>
      <td>e9953a1648364e878d835bc6bcc0d3ef</td>
      <td>Relationship</td>
      <td>37</td>
      <td>5</td>
      <td>1</td>
      <td>The activities and cheer that the Ghost of Chr...</td>
      <td>e9953a1648364e878d835bc6bcc0d3ef</td>
    </tr>
  </tbody>
</table>
</div>




```python
G.get_nodes(node_type="Community", limit=2)
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
      <th>v_id</th>
      <th>v_type</th>
      <th>summary</th>
      <th>level</th>
      <th>full_content</th>
      <th>rank</th>
      <th>id</th>
      <th>rank_explanation</th>
      <th>title</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>12</td>
      <td>Community</td>
      <td>This report delves into the interconnected rel...</td>
      <td>1</td>
      <td># The Transformation of Ebenezer Scrooge: A Ch...</td>
      <td>8.5</td>
      <td>12</td>
      <td>The high impact severity rating reflects the p...</td>
      <td>Community 12</td>
    </tr>
    <tr>
      <th>1</th>
      <td>7</td>
      <td>Community</td>
      <td>This report explores the network surrounding P...</td>
      <td>0</td>
      <td># Project Gutenberg and the Digital Disseminat...</td>
      <td>8.5</td>
      <td>7</td>
      <td>The high impact severity rating reflects Proje...</td>
      <td>Community 7</td>
    </tr>
  </tbody>
</table>
</div>



---

## What’s Next?

- [Supporting Microsoft’s GraphRAG: Part 4](../msft_graphrag_4): Perform queries using GSQL and Python-native TigerGraphX, with global and local context builders.

---

Start transforming your GraphRAG workflows with the power of **TigerGraphX** today!
