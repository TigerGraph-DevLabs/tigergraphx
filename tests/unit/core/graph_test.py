import pytest
from typing import Optional, List

from tigergraphx import Graph
from tigergraphx import GraphSchema
from .base_graph_test import TestBaseGraph
from tigergraphx.config import (
    NodeSpec,
    NeighborSpec,
)


class TestGraph(TestBaseGraph):
    def set_up(self):
        # Define the schema configuration as a dictionary
        schema_config = {
            "graph_name": "HeteGraph",
            "nodes": {
                "User": {
                    "primary_key": "id",
                    "attributes": {
                        "id": "STRING",
                        "name": "STRING",
                        "age": "UINT",
                    },
                },
                "Product": {
                    "primary_key": "id",
                    "attributes": {
                        "id": "STRING",
                        "name": "STRING",
                        "price": "DOUBLE",
                    },
                },
            },
            "edges": {
                "purchased": {
                    "is_directed_edge": True,
                    "from_node_type": "User",
                    "to_node_type": "Product",
                    "attributes": {
                        "purchase_date": "DATETIME",
                        "quantity": "DOUBLE",
                    },
                },
                "similar_to": {
                    "is_directed_edge": False,
                    "from_node_type": "Product",
                    "to_node_type": "Product",
                    "attributes": {
                        "purchase_date": "DATETIME",
                        "quantity": "DOUBLE",
                    },
                },
            },
        }
        # Use GraphSchema.ensure_config to create the schema
        graph_schema = GraphSchema.ensure_config(schema_config)
        # Initialize the graph with the schema
        self.G = Graph(graph_schema=graph_schema)

    def test_graph(self):
        # Set up
        self.set_up()
        # Adding and removing nodes and edges
        self.G.add_node("User_A", "User")
        self.G.add_node("User_B", "User", name="B")
        self.G.add_node("User_C", "User", name="C", age=30)
        self.G.add_node("Product_1", "Product")
        self.G.add_node("Product_2", "Product", name="2")
        self.G.add_node("Product_3", "Product", name="3", price=50)
        self.G.add_edge("User_A", "Product_1", "User", "purchased", "Product")
        self.G.add_edge(
            "User_B",
            "Product_2",
            "User",
            "purchased",
            "Product",
            purchase_date="2024-01-12",
        )
        self.G.add_edge(
            "User_C",
            "Product_1",
            "User",
            "purchased",
            "Product",
            purchase_date="2024-01-12",
            quantity=5.5,
        )
        self.G.add_edge(
            "User_C",
            "Product_2",
            "User",
            "purchased",
            "Product",
            purchase_date="2024-01-12",
            quantity=15.5,
        )
        self.G.add_edge(
            "User_C",
            "Product_3",
            "User",
            "purchased",
            "Product",
            purchase_date="2024-01-12",
            quantity=25.5,
        )
        self.G.add_edge(
            "Product_1",
            "Product_3",
            "Product",
            "similar_to",
            "Product",
        )

        # Reporting nodes, edges and neighbors
        ## has node/edge
        assert self.G.has_node("User_A", "User")
        assert self.G.has_node("User_B", "User")
        assert self.G.has_node("User_C", "User")
        assert self.G.has_node("Product_1", "Product")
        assert self.G.has_node("Product_2", "Product")
        assert self.G.has_node("Product_3", "Product")
        assert not self.G.has_node("User_D", "User")
        assert not self.G.has_edge(
            "User_A", "Product_2", "User", "purchased", "Product"
        )
        assert not self.G.has_edge(
            "User_A", "Product_3", "User", "purchased", "Product"
        )
        assert self.G.has_edge("User_C", "Product_1", "User", "purchased", "Product")
        assert self.G.has_edge("User_C", "Product_2", "User", "purchased", "Product")
        assert self.G.has_edge("User_C", "Product_3", "User", "purchased", "Product")

        ## get node/edge data
        print()
        node_data = self.time_execution(
            lambda: self.G.get_node_data("User_C", "User"), "get_node_data"
        )
        assert node_data["id"] == "User_C"
        assert node_data["name"] == "C"
        assert node_data["age"] == 30
        edge_data = self.time_execution(
            lambda: self.G.get_edge_data(
                "User_C", "Product_2", "User", "purchased", "Product"
            ),
            "get_edge_data",
        )
        assert edge_data["purchase_date"] == "2024-01-12 00:00:00"
        assert edge_data["quantity"] == 15.5

        ## get node edges
        node_edges = self.time_execution(
            lambda: self.G.get_node_edges("User_C", "User", "purchased"),
            "get_node_edges",
        )
        assert len(node_edges) == 3

        # Counting nodes edges and neighbors
        degree = self.time_execution(
            lambda: self.G.degree("Product_1", "Product", ["reverse_purchased"]),
            "degree",
        )
        assert degree == 2
        degree = self.time_execution(
            lambda: self.G.degree("Product_1", "Product", ["similar_to"]), "degree"
        )
        assert degree == 1
        degree = self.time_execution(
            lambda: self.G.degree(
                "Product_1", "Product", ["reverse_purchased", "similar_to"]
            ),
            "degree",
        )
        assert degree == 3
        degree = self.time_execution(
            lambda: self.G.degree("Product_1", "Product", []), "degree"
        )
        assert degree == 3

        # Exceptions
        with pytest.raises(
            ValueError,
            match="Please specify a node type, as the graph has multiple node types.",
        ):
            self.G.add_node("D", "")
        with pytest.raises(
            ValueError,
            match="Please specify a node type for the target node, as the graph has multiple node types.",
        ):
            self.G.add_edge("User_A", "Product_2", "User", "purchased", "")
        with pytest.raises(
            ValueError,
            match="Please specify a node type for the source node, as the graph has multiple node types.",
        ):
            self.G.add_edge("User_A", "Product_2", "", "purchased", "Product")
        with pytest.raises(
            ValueError,
            match="Please specify an edge type, as the graph has multiple edge types.",
        ):
            self.G.add_edge("User_A", "Product_2", "User", "", "Product")

        with pytest.raises(
            ValueError,
            match="Please specify a node type, as the graph has multiple node types.",
        ):
            self.G.has_node("D", "")

    def set_up_2(self):
        # Define the schema configuration as a dictionary
        schema_config = {
            "graph_name": "HeteGraph2",
            "nodes": {
                "Product": {
                    "primary_key": "id",
                    "attributes": {
                        "id": "STRING",
                        "name": "STRING",
                        "price": "DOUBLE",
                    },
                },
            },
            "edges": {
                "similar_to": {
                    "is_directed_edge": False,
                    "from_node_type": "Product",
                    "to_node_type": "Product",
                    "attributes": {
                        "similarity_score": "DOUBLE",
                    },
                },
            },
        }
        # Use GraphSchema.ensure_config to create the schema
        graph_schema = GraphSchema.ensure_config(schema_config)
        # Initialize the graph with the schema
        self.G = Graph(graph_schema=graph_schema)

    def test_graph_2(self):
        # Set up
        self.set_up_2()
        # Adding and removing nodes and edges
        self.G.add_node("Product_1", "Product")
        self.G.add_node("Product_2", "Product", name="2")
        self.G.add_node("Product_3", "Product", name="3", price=50)
        self.G.add_edge(
            "Product_1",
            "Product_3",
            "Product",
            "similar_to",
            "Product",
        )

        # Exceptions
        assert self.G.has_node("Product_1")
        assert self.G.has_node("Product_2")
        assert self.G.has_node("Product_3")
        assert self.G.has_edge("Product_1", "Product_3")

    def set_up_3(self):
        # Define the schema configuration as a dictionary
        schema_config = {
            "graph_name": "HeteGraph3",
            "nodes": {
                "Entity": {
                    "primary_key": "id",
                    "attributes": {
                        "id": "STRING",
                        "entity_type": "STRING",
                        "description": "STRING",
                        "source_id": "STRING",
                    },
                },
            },
            "edges": {
                "relationship": {
                    "is_directed_edge": True,
                    "from_node_type": "Entity",
                    "to_node_type": "Entity",
                    "attributes": {
                        "weight": "DOUBLE",
                        "description": "STRING",
                        "keywords": "STRING",
                        "source_id": "STRING",
                    },
                },
            },
        }
        # Use GraphSchema.ensure_config to create the schema
        graph_schema = GraphSchema.ensure_config(schema_config)
        # Initialize the graph with the schema
        self.G = Graph(graph_schema=graph_schema)

    # def create_loading_job_config(self) -> LoadingJobConfig:
    #     """
    #     Generate the LoadingJobConfig using a dictionary.
    #     """
    #     config_dict = {
    #         "loading_job_name": "loading_job_HeteGraph3",
    #         "files": [
    #             {
    #                 "file_alias": "f_entity",
    #                 "file_path": "/home/tigergraph/data/lightrag/ultradomain_fin/entity.csv",
    #                 "csv_parsing_options": {
    #                     "separator": ",",
    #                     "header": True,
    #                     "EOL": "\\n",
    #                     "quote": "DOUBLE",
    #                 },
    #                 "node_mappings": [
    #                     {
    #                         "target_name": "Entity",
    #                         "attribute_column_mappings": {
    #                             "id": "id",
    #                             "entity_type": "entity_type",
    #                             "description": "description",
    #                             "source_id": "source_id",
    #                         },
    #                     }
    #                 ],
    #             },
    #             {
    #                 "file_alias": "f_relationship",
    #                 "file_path": "/home/tigergraph/data/lightrag/ultradomain_fin/relationship.csv",
    #                 "csv_parsing_options": {
    #                     "separator": ",",
    #                     "header": True,
    #                     "EOL": "\\n",
    #                     "quote": "DOUBLE",
    #                 },
    #                 "edge_mappings": [
    #                     {
    #                         "target_name": "relationship",
    #                         "source_node_column": "source",
    #                         "target_node_column": "target",
    #                         "attribute_column_mappings": {
    #                             "weight": "weight",
    #                             "description": "description",
    #                             "keywords": "keywords",
    #                             "source_id": "source_id",
    #                         },
    #                     }
    #                 ],
    #             },
    #         ],
    #     }
    #
    #     # Generate the LoadingJobConfig from the dictionary
    #     return LoadingJobConfig.ensure_config(config_dict)

    # def test_graph_3(self):
    #     # Set up
    #     self.set_up_3()
    #     # Load data
    #     loading_job_config = self.create_loading_job_config()
    #     self.G.load_data(loading_job_config)

    def create_gsql_get_nodes(
        self,
        node_type: str,
        filter_expression: Optional[str] = None,
        return_attributes: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> str:
        """
        High-level function to generate a GSQL query for node selection.
        Converts parameters into a NodeSpec and delegates to `_create_gsql_get_nodes`.
        """
        spec = NodeSpec(
            node_type=node_type,
            filter_expression=filter_expression,
            return_attributes=return_attributes,
            limit=limit,
        )
        return self.G._query_manager._create_gsql_get_nodes(self.G.name, spec)

    def test_create_gsql_get_nodes(self):
        # Set up
        self.set_up_3()
        # Test case 1: Simple query without filters, limits, or return attributes
        actual_gsql_script = self.create_gsql_get_nodes(node_type="Community")
        expected_gsql_script = """
INTERPRET QUERY() FOR GRAPH HeteGraph3 {
  Nodes = {Community.*};
  PRINT Nodes;
}
""".strip()
        assert actual_gsql_script == expected_gsql_script

        # Test case 2: Query with limit
        actual_gsql_script = self.create_gsql_get_nodes(node_type="Community", limit=10)
        expected_gsql_script = """
INTERPRET QUERY() FOR GRAPH HeteGraph3 {
  Nodes = {Community.*};
  Nodes =
    SELECT s
    FROM Nodes:s
    LIMIT 10
  ;
  PRINT Nodes;
}
""".strip()
        assert actual_gsql_script == expected_gsql_script

        # Test case 3: Query with return attributes
        actual_gsql_script = self.create_gsql_get_nodes(
            node_type="Community",
            return_attributes=["id", "rank"],
        )
        expected_gsql_script = """
INTERPRET QUERY() FOR GRAPH HeteGraph3 {
  Nodes = {Community.*};
  PRINT Nodes[
    Nodes.id AS id,
    Nodes.rank AS rank
  ];
}
""".strip()
        assert actual_gsql_script == expected_gsql_script

        # Test case 4: Query with filter expression
        actual_gsql_script = self.create_gsql_get_nodes(
            node_type="Community",
            filter_expression="s.rank > 0",
        )
        expected_gsql_script = """
INTERPRET QUERY() FOR GRAPH HeteGraph3 {
  Nodes = {Community.*};
  Nodes =
    SELECT s
    FROM Nodes:s
    WHERE s.rank > 0
  ;
  PRINT Nodes;
}
""".strip()
        assert actual_gsql_script == expected_gsql_script

        # Test case 5: Query with all options
        actual_gsql_script = self.create_gsql_get_nodes(
            node_type="Community",
            filter_expression="s.rank > 0",
            return_attributes=["id", "rank"],
            limit=10,
        )
        expected_gsql_script = """
INTERPRET QUERY() FOR GRAPH HeteGraph3 {
  Nodes = {Community.*};
  Nodes =
    SELECT s
    FROM Nodes:s
    WHERE s.rank > 0
    LIMIT 10
  ;
  PRINT Nodes[
    Nodes.id AS id,
    Nodes.rank AS rank
  ];
}
""".strip()
        assert actual_gsql_script == expected_gsql_script

    def create_gsql_get_neighbors(
        self,
        start_nodes: str | List[str],
        start_node_type: str,
        edge_types: Optional[str | List[str]] = None,
        target_node_types: Optional[str | List[str]] = None,
        filter_expression: Optional[str] = None,
        return_attributes: Optional[str | List[str]] = None,
        limit: Optional[int] = None,
    ) -> str:
        """
        High-level function to retrieve neighbors with multiple parameters.
        Converts parameters into a NeighborSpec and delegates to `_get_neighbors_from_spec`.
        """
        spec = NeighborSpec(
            start_nodes=start_nodes,
            start_node_type=start_node_type,
            edge_types=edge_types,
            target_node_types=target_node_types,
            filter_expression=filter_expression,
            return_attributes=return_attributes,
            limit=limit,
        )
        gsql_script, _ = self.G._query_manager._create_gsql_get_neighbors(
            self.G.name, spec
        )
        return gsql_script

    def test_create_gsql_get_neighbors(self):
        # Set up
        self.set_up_3()
        # Get neighbors
        actual_gsql_script = self.create_gsql_get_neighbors(
            start_nodes=["CYTOSORB"],
            start_node_type="Entity",
        )
        expected_gsql_script = """
INTERPRET QUERY(
  SET<VERTEX<Entity>> start_nodes
) FOR GRAPH HeteGraph3 {
  Nodes = {start_nodes};
  Neighbors =
    SELECT t
    FROM Nodes:s -(:e)- :t
  ;
  PRINT Neighbors;
}
""".strip()
        assert actual_gsql_script == expected_gsql_script

        actual_gsql_script = self.create_gsql_get_neighbors(
            start_nodes=["CYTOSORB"],
            start_node_type="Entity",
            edge_types=["relationship", "reverse_relationship"],
            target_node_types=["Entity"],
            limit=10,
        )
        expected_gsql_script = """
INTERPRET QUERY(
  SET<VERTEX<Entity>> start_nodes
) FOR GRAPH HeteGraph3 {
  Nodes = {start_nodes};
  Neighbors =
    SELECT t
    FROM Nodes:s -((relationship|reverse_relationship):e)- Entity:t
    LIMIT 10
  ;
  PRINT Neighbors;
}
""".strip()
        assert actual_gsql_script == expected_gsql_script

        actual_gsql_script = self.create_gsql_get_neighbors(
            start_nodes="CYTOSORB",
            start_node_type="Entity",
            edge_types=["relationship", "reverse_relationship"],
            target_node_types="Entity",
            return_attributes="id",
            limit=10,
        )
        expected_gsql_script = """
INTERPRET QUERY(
  SET<VERTEX<Entity>> start_nodes
) FOR GRAPH HeteGraph3 {
  Nodes = {start_nodes};
  Neighbors =
    SELECT t
    FROM Nodes:s -((relationship|reverse_relationship):e)- Entity:t
    LIMIT 10
  ;
  PRINT Neighbors[
    Neighbors.id AS id
  ];
}
""".strip()
        assert actual_gsql_script == expected_gsql_script

        actual_gsql_script = self.create_gsql_get_neighbors(
            start_nodes="CYTOSORB",
            start_node_type="Entity",
            edge_types=["relationship", "reverse_relationship"],
            target_node_types="Entity",
            return_attributes=["id", "entity_type"],
            limit=10,
        )
        expected_gsql_script = """
INTERPRET QUERY(
  SET<VERTEX<Entity>> start_nodes
) FOR GRAPH HeteGraph3 {
  Nodes = {start_nodes};
  Neighbors =
    SELECT t
    FROM Nodes:s -((relationship|reverse_relationship):e)- Entity:t
    LIMIT 10
  ;
  PRINT Neighbors[
    Neighbors.id AS id,
    Neighbors.entity_type AS entity_type
  ];
}
""".strip()
        assert actual_gsql_script == expected_gsql_script

        actual_gsql_script = self.create_gsql_get_neighbors(
            start_nodes=["CYTOSORB", "ITALY"],
            start_node_type="Entity",
            edge_types=["relationship", "reverse_relationship"],
            target_node_types="Entity",
            filter_expression="s.id != t.id",
            return_attributes=["id", "entity_type"],
            limit=10,
        )
        expected_gsql_script = """
INTERPRET QUERY(
  SET<VERTEX<Entity>> start_nodes
) FOR GRAPH HeteGraph3 {
  Nodes = {start_nodes};
  Neighbors =
    SELECT t
    FROM Nodes:s -((relationship|reverse_relationship):e)- Entity:t
    WHERE s.id != t.id
    LIMIT 10
  ;
  PRINT Neighbors[
    Neighbors.id AS id,
    Neighbors.entity_type AS entity_type
  ];
}
""".strip()
        assert actual_gsql_script == expected_gsql_script

    def test_get_nodes(self):
        # Set up the graph (assuming `set_up_graph` initializes a test graph)
        self.set_up_3()

        # Define the return attributes and test parameters
        return_attributes = ["id", "entity_type"]
        nodes = self.time_execution(
            lambda: self.G.get_nodes(
                node_type="Entity",
                filter_expression='s.entity_type != ""',
                return_attributes=return_attributes,
                limit=10,
            ),
            "get_nodes",
        )

        # Assertions to verify the test output
        assert nodes is not None, "No nodes returned."
        assert len(nodes) == 10, "Expected 10 nodes, but got a different count."
        assert set(nodes.columns) == set(
            return_attributes
        ), f"Expected columns {return_attributes}, but got {list(nodes.columns)}."

    def test_get_neighbors(self):
        # Set up
        self.set_up_3()
        # Get neighbors
        return_attributes = ["id", "entity_type"]
        neighbors = self.time_execution(
            lambda: self.G.get_neighbors(
                start_nodes=["CYTOSORB", "ITALY"],
                start_node_type="Entity",
                edge_types=["relationship", "reverse_relationship"],
                target_node_types="Entity",
                filter_expression="s.id != t.id",
                return_attributes=return_attributes,
                limit=10,
            ),
            "get_neighbors",
        )
        assert len(neighbors) == 10
        assert set(neighbors.columns) == set(return_attributes)
