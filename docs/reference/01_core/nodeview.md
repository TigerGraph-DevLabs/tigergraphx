# NodeView

::: tigergraphx.core.view.NodeView.__init__

**Examples:**

To obtain a `NodeView` instance, please use `Graph.nodes`. Refer to [Graph.nodes](../graph/#tigergraphx.core.graph.Graph.nodes):

```python
>>> G = Graph.from_db("Social")
>>> node_view = G.nodes
>>> len(G.nodes)
2
```

::: tigergraphx.core.view.NodeView.__getitem__

**Examples:**

Retrieve data for a node using its identifier.

Single Node Type Example:
```python
>>> G = Graph.from_db("Social")
>>> G.nodes["Alice"]
{'name': 'Alice', 'age': 25}
```

Multiple Node Types Example:
```python
>>> G = Graph.from_db("Social")
>>> G.nodes[("Person", "Alice")]
{'name': 'Alice', 'age': 25}
```

::: tigergraphx.core.view.NodeView.__contains__

**Examples:**

Check whether a node exists in the view.  

Single Node Type Example:
```python
>>> G = Graph.from_db("Social")
>>> "Alice" in G.nodes
True
```

Multiple Node Types Example:
```python
>>> G = Graph.from_db("Social")
>>> ("Person", "Alice") in G.nodes
True
```

::: tigergraphx.core.view.NodeView.__iter__

!!! warning
    Iterating over all nodes will retrieve all data from the database. 

    This method is intended for small datasets only. For large datasets, using this method may lead to significant performance issues or excessive memory usage.

**Examples:**

Iterate over all nodes in the view.

Single Node Type Example:
```python
>>> G = Graph.from_db("Social")
>>> for node_id in G.nodes:
>>>     print(node_id)
Michael
Alice
```

Multiple Node Types Example:
```python
>>> G = Graph.from_db("Social")
>>> for node_type, node_id in G.nodes:
>>>     print(f"{node_type}: {node_id}")
Person: Alice
Person: Michael
Community: Photography Enthusiasts
Community: Fitness and Wellness Group
```


::: tigergraphx.core.view.NodeView.__len__

**Examples:**

Get the number of nodes in the view:
```python
>>> len(G.nodes)
2
```
