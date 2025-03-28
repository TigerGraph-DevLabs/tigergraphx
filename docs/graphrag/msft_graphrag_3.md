# Supporting Microsoft’s GraphRAG: Part 3 - Graph Analysis

In the [previous section](msft_graphrag_2.md), we have created a graph in TigerGraph, and loaded the CSV data into it.

Now, let’s use Jupyter Notebook to explore the graph data and perform graph analysis.

To run this Jupyter Notebook, you can download the original `.ipynb` file from [msft_graphrag_3.ipynb](https://github.com/tigergraph/tigergraphx/tree/main/docs/graphrag/msft_graphrag_3.ipynb).

---

## Retrieving the Graph from TigerGraph
Since the graph has already been created in TigerGraph, redefining its schema is unnecessary. Instead, you can provide the graph name to retrieve it. TigerGraphX will verify if the graph exists in TigerGraph and, if it does, will return the corresponding graph.

### Define the TigerGraph Connection Configuration
Before retrieving the graph schema, you need to configure the **TigerGraph connection settings**.  

The recommended approach is to use environment variables, such as setting them with the `export` command in the shell. Here, to illustrate the demo, we configure them within Python using the `os.environ` method. You can find more methods for configuring connection settings in [Graph.\_\_init\_\_](../reference/01_core/graph.md#tigergraphx.core.graph.Graph.__init__).


```python
>>> import os
>>> os.environ["TG_HOST"] = "http://127.0.0.1"
>>> os.environ["TG_USERNAME"] = "tigergraph"
>>> os.environ["TG_PASSWORD"] = "tigergraph"
```

### Retrieve a Graph and Print Its Schema
Once the graph has been created in TigerGraph, you can retrieve it without manually defining the schema using the `Graph.from_db` method, which requires only the graph name:


```python
>>> from tigergraphx import Graph
>>> G = Graph.from_db("GraphRAG")
```

## Display the Graph Schema
Now, let's print the schema of the graph in a well-formatted manner:


```python
>>> import json
>>> schema = G.get_schema()
>>> print(json.dumps(schema, indent=4, default=str))
```

    {
        "graph_name": "GraphRAG",
        "nodes": {
            "Document": {
                "primary_key": "id",
                "attributes": {
                    "id": {
                        "data_type": "DataType.STRING",
                        "default_value": null
                    },
                    "title": {
                        "data_type": "DataType.STRING",
                        "default_value": null
                    }
                },
                "vector_attributes": {}
            },
            "TextUnit": {
                "primary_key": "id",
                "attributes": {
                    "id": {
                        "data_type": "DataType.STRING",
                        "default_value": null
                    },
                    "text": {
                        "data_type": "DataType.STRING",
                        "default_value": null
                    },
                    "n_tokens": {
                        "data_type": "DataType.UINT",
                        "default_value": null
                    }
                },
                "vector_attributes": {}
            },
            "Entity": {
                "primary_key": "id",
                "attributes": {
                    "id": {
                        "data_type": "DataType.STRING",
                        "default_value": null
                    },
                    "human_readable_id": {
                        "data_type": "DataType.UINT",
                        "default_value": null
                    },
                    "name": {
                        "data_type": "DataType.STRING",
                        "default_value": null
                    },
                    "entity_type": {
                        "data_type": "DataType.STRING",
                        "default_value": null
                    },
                    "description": {
                        "data_type": "DataType.STRING",
                        "default_value": null
                    }
                },
                "vector_attributes": {
                    "emb_description": {
                        "dimension": 1536,
                        "index_type": "HNSW",
                        "data_type": "FLOAT",
                        "metric": "COSINE"
                    }
                }
            },
            "Relationship": {
                "primary_key": "id",
                "attributes": {
                    "id": {
                        "data_type": "DataType.STRING",
                        "default_value": null
                    },
                    "human_readable_id": {
                        "data_type": "DataType.UINT",
                        "default_value": null
                    },
                    "rank": {
                        "data_type": "DataType.UINT",
                        "default_value": null
                    },
                    "weight": {
                        "data_type": "DataType.DOUBLE",
                        "default_value": null
                    },
                    "description": {
                        "data_type": "DataType.STRING",
                        "default_value": null
                    }
                },
                "vector_attributes": {}
            },
            "Community": {
                "primary_key": "id",
                "attributes": {
                    "id": {
                        "data_type": "DataType.STRING",
                        "default_value": null
                    },
                    "level": {
                        "data_type": "DataType.UINT",
                        "default_value": null
                    },
                    "rank": {
                        "data_type": "DataType.DOUBLE",
                        "default_value": null
                    },
                    "rank_explanation": {
                        "data_type": "DataType.STRING",
                        "default_value": null
                    },
                    "title": {
                        "data_type": "DataType.STRING",
                        "default_value": null
                    },
                    "full_content": {
                        "data_type": "DataType.STRING",
                        "default_value": null
                    },
                    "summary": {
                        "data_type": "DataType.STRING",
                        "default_value": null
                    }
                },
                "vector_attributes": {}
            }
        },
        "edges": {
            "document_contains_text_unit": {
                "is_directed_edge": false,
                "from_node_type": "Document",
                "to_node_type": "TextUnit",
                "discriminator": "set()",
                "attributes": {}
            },
            "text_unit_contains_entity": {
                "is_directed_edge": false,
                "from_node_type": "TextUnit",
                "to_node_type": "Entity",
                "discriminator": "set()",
                "attributes": {}
            },
            "text_unit_contains_relationship": {
                "is_directed_edge": false,
                "from_node_type": "TextUnit",
                "to_node_type": "Relationship",
                "discriminator": "set()",
                "attributes": {}
            },
            "relationship_source": {
                "is_directed_edge": false,
                "from_node_type": "Relationship",
                "to_node_type": "Entity",
                "discriminator": "set()",
                "attributes": {}
            },
            "relationship_target": {
                "is_directed_edge": false,
                "from_node_type": "Relationship",
                "to_node_type": "Entity",
                "discriminator": "set()",
                "attributes": {}
            },
            "community_contains_entity": {
                "is_directed_edge": false,
                "from_node_type": "Community",
                "to_node_type": "Entity",
                "discriminator": "set()",
                "attributes": {}
            },
            "community_contains_relationship": {
                "is_directed_edge": false,
                "from_node_type": "Community",
                "to_node_type": "Relationship",
                "discriminator": "set()",
                "attributes": {}
            }
        }
    }


## Display Node and Edge Counts

Gain deeper insights into the graph by exploring details such as the total number of nodes and the count of nodes for each node type.

### Display the Total Number of Nodes


```python
>>> G.number_of_nodes()
```




    2883



### Display the Count of Nodes for Each Node Type


```python
>>> for node_type in schema["nodes"]:
...     print(f"{node_type}: {G.number_of_nodes(node_type)}")
```

    Document: 1
    TextUnit: 104
    Entity: 1577
    Relationship: 1092
    Community: 109


### Display the Total Number of Edges


```python
>>> G.number_of_edges()
```




    10313



### Display the Count of Edges for Each Edge Type


```python
>>> for edge_type in schema["edges"]:
...     print(f"{edge_type}: {G.number_of_edges(edge_type)}")
```

    document_contains_text_unit: 104
    text_unit_contains_entity: 2095
    text_unit_contains_relationship: 1282
    relationship_source: 1092
    relationship_target: 1092
    community_contains_entity: 1956
    community_contains_relationship: 2692


## Retrieving Sample Nodes
Retrieve Sample `Entity` Nodes.


```python
>>> print(G.get_nodes(node_type="Entity", limit=2))
```

                                   v_id  v_type  human_readable_id entity_type  \
    0  c0803923646246c5a203810faa4e4464  Entity                825         GEO   
    1  6069e8895f924b659534f74d6736e69d  Entity                830         GEO   
    
                name                                        description  \
    0  VALLEY STREAM  Valley Stream is a location in New York where ...   
    1          CHINA  China is a country in East Asia where Walmart ...   
    
                                     id  
    0  c0803923646246c5a203810faa4e4464  
    1  6069e8895f924b659534f74d6736e69d  


Retrieve Sample `Relationship` Nodes


```python
>>> print(G.get_nodes(node_type="Relationship", limit=2))
```

                                   v_id        v_type  human_readable_id  rank  \
    0  5e7864d8153f4aa8936b253792f0b636  Relationship               1066    32   
    1  1db19aed7ed54b44b4e8f71b7588e0dd  Relationship               1058    16   
    
       weight                                        description  \
    0       8  Animax is a channel owned by Sony Pictures Tel...   
    1       7  Guerrilla Cambridge developed games for the Pl...   
    
                                     id  
    0  5e7864d8153f4aa8936b253792f0b636  
    1  1db19aed7ed54b44b4e8f71b7588e0dd  


Retrieve Sample `Community` Nodes


```python
>>> print(G.get_nodes(node_type="Community", limit=2))
```

      v_id     v_type                                            summary  level  \
    0   49  Community  This community encompasses various command-lin...      1   
    1   61  Community  The community centers around the Battles of Ma...      1   
    
                                            full_content  rank  id  \
    0  # DOS and Command-Line Operating Systems Commu...   7.5  49   
    1  # Battles of Manassas and Civil War Historians...   6.5  61   
    
                                        rank_explanation         title  
    0  The impact severity rating is high due to the ...  Community 49  
    1  The impact severity rating is moderate to high...  Community 61  


---

## What’s Next?

- [Supporting Microsoft’s GraphRAG: Part 4](msft_graphrag_4.md): Perform queries using GSQL and Python-native TigerGraphX, with global and local context builders.

---

Start transforming your GraphRAG workflows with the power of **TigerGraphX** today!
