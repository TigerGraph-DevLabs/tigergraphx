class NodeView:
    def __init__(self, graph):
        self.graph = graph

    def __getitem__(self, key):
        """
        Retrieve data associated with a node.

        The interpretation of `key` depends on the graph's node type configuration:

        - **Single Node Type**: Pass the node's identifier as `node_id`.
        - **Multiple Node Types**: Pass a tuple in the form `(node_type, node_id)`.
        """
        if isinstance(key, str):
            # Homogeneous: Use the default node_type
            node_id = key
            return self.graph.get_node_data(node_id=node_id)
        elif isinstance(key, tuple) and len(key) == 2:
            # Heterogeneous: Expect (node_type, node_id)
            node_type, node_id = key
            return self.graph.get_node_data(node_type=node_type, node_id=node_id)
        else:
            raise ValueError(
                "Key must be node_id for the graphs with single node type"
                "or (node_type, node_id) for the graphs with multiple node type."
            )

    def __contains__(self, key):
        """Check if a node exists."""
        if isinstance(key, str):
            node_id = key
            return self.graph.has_node(node_id=node_id)
        elif isinstance(key, tuple) and len(key) == 2:
            node_type, node_id = key
            return self.graph.has_node(node_type=node_type, node_id=node_id)
        else:
            raise ValueError(
                "Key must be node_id for the graphs with single node type"
                "or (node_type, node_id) for the graphs with multiple node type."
            )

    def __iter__(self):
        """Iterate over all nodes.

        WARNING: Iterating over all nodes will retrieve all data from the database. 
        This method is intended for small datasets only. For large datasets, using this 
        method may lead to significant performance issues or excessive memory usage.

        - For homogeneous nodes: each iteration returns a node_id.
        - For heterogeneous nodes: each iteration returns a tuple (node_type, node_id).
        """
        # Get all nodes
        nodes = self.graph.get_nodes(all_node_types=True)
        # If the graph has only one node type, then only return IDs
        if len(self.graph.node_types) == 1:
            return iter(node["v_id"] for _, node in nodes.iterrows())
        # If the graph has multiple one node type, then only return (type, id)
        return iter((node["v_type"], node["v_id"]) for _, node in nodes.iterrows())

    def __len__(self):
        """Return the number of nodes."""
        return self.graph.number_of_nodes()

    # def __call__(self, node_type=None, data=False, default=None):
    #     """
    #     Retrieve all nodes, or nodes of a specific type, or with specific attributes.
    #     - For homogeneous graphs: `node_type` is ignored.
    #     """
    #     if self.graph.node_type:
    #         node_type = self.graph.node_type  # Default to the graph's node_type
    #     if node_type is None and not self.graph.node_type:
    #         raise ValueError("node_type must be specified for heterogeneous graphs.")
    #     return NodeDataView(self.graph, node_type=node_type, data=data, default=default)


# class NodeDataView:
#     def __init__(self, graph, node_type=None, data=False, default=None):
#         self.graph = graph
#         self.node_type = node_type
#         self.data = data
#         self.default = default
#
#     def __iter__(self):
#         """Iterate over nodes of a specific type and their attributes."""
#         if not self.node_type:
#             raise ValueError("node_type must be specified for heterogeneous graphs.")
#         query = f'SELECT id, {self.data} FROM NODES WHERE TYPE="{self.node_type}"'
#         nodes = self.graph._fetch_node_data(
#             node_type=self.node_type, attributes=self.data
#         )
#         for node in nodes:
#             yield (node["id"], node.get(self.data, self.default))
