class NodeView:
    def __init__(self, graph):
        self.graph = graph

    def __getitem__(self, key):
        """
        Retrieve specific node data.
        - For homogeneous graphs: key is `node_id`.
        - For heterogeneous graphs: key is `(node_type, node_id)`.
        """
        if self.graph.node_type:
            # Homogeneous: Use the default node_type
            node_id = key
            node_type = self.graph.node_type
        elif isinstance(key, tuple) and len(key) == 2:
            # Heterogeneous: Expect (node_type, node_id)
            node_type, node_id = key
        else:
            raise ValueError(
                "Key must be node_id for homogeneous graphs or (node_type, node_id) for heterogeneous graphs."
            )
        return self.graph._get_node_data(node_type=node_type, node_id=node_id)

    def __contains__(self, key):
        """Check if a node exists."""
        if self.graph.node_type:
            node_id = key
            node_type = self.graph.node_type
        elif isinstance(key, tuple) and len(key) == 2:
            node_type, node_id = key
        else:
            raise ValueError(
                "Key must be node_id for homogeneous graphs or (node_type, node_id) for heterogeneous graphs."
            )
        return self.graph._has_node(node_type=node_type, node_id=node_id)

    def __iter__(self):
        """Iterate over all nodes.
        For homogeneous: return node_id.
        For heterogeneous: return (node_type, node_id).
        """
        nodes = self.graph._get_nodes()
        if self.graph.node_type:
            return iter(
                node["v_id"] for _, node in nodes.iterrows()
            )  # Homogeneous: Only return IDs
        return iter(
            (node["v_type"], node["v_id"]) for _, node in nodes.iterrows()
        )  # Heterogeneous: Return (type, id)

    def __len__(self):
        """Return the number of nodes."""
        return self.graph._number_of_nodes()

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
