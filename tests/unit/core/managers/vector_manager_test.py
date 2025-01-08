import pytest
from unittest.mock import MagicMock

from tigergraphx.config import (
    GraphSchema,
    NodeSchema,
    AttributeSchema,
    VectorAttributeSchema,
    DataType,
)
from tigergraphx.core.managers.vector_manager import VectorManager


class TestVectorManager:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_connection = MagicMock()
        self.mock_connection.gsql = MagicMock()

        mock_context = MagicMock()
        mock_context.connection = self.mock_connection  # Use the mocked connection
        mock_context.graph_schema = GraphSchema(
            graph_name="MyGraph",
            nodes={
                "Account": NodeSchema(
                    primary_key="name",
                    attributes={
                        "name": AttributeSchema(data_type=DataType.STRING),
                        "value": AttributeSchema(data_type=DataType.BOOL),
                    },
                    vector_attributes={"emb1": VectorAttributeSchema(dimension=3)},
                ),
                "Phone": NodeSchema(
                    primary_key="number",
                    attributes={
                        "number": AttributeSchema(data_type=DataType.STRING),
                        "isBlocked": AttributeSchema(data_type=DataType.BOOL),
                    },
                    vector_attributes={"emb2": VectorAttributeSchema(dimension=3)},
                ),
            },
            edges={},
        )
        self.vector_manager = VectorManager(mock_context)

    def test_upsert_single_record(self):
        # Test case for single record upsert
        data = {
            "name": "Scott",
            "emb1": [
                -0.017733968794345856,
                -0.01019224338233471,
                -0.016571875661611557,
            ],
        }
        node_type = "Account"

        # Mock the upsertVertices call
        self.mock_connection.upsertVertices.return_value = 1

        result = self.vector_manager.upsert(data, node_type)

        # Assert that the result is as expected
        assert result == 1
        self.mock_connection.upsertVertices.assert_called_once_with(
            vertexType=node_type,
            vertices=[
                (
                    "Scott",
                    {
                        "emb1": [
                            -0.017733968794345856,
                            -0.01019224338233471,
                            -0.016571875661611557,
                        ]
                    },
                )
            ],
        )

    def test_upsert_multiple_records(self):
        # Test case for multiple records upsert
        data = [
            {
                "name": "Scott",
                "emb1": [
                    -0.017733968794345856,
                    -0.01019224338233471,
                    -0.016571875661611557,
                ],
            },
            {
                "name": "Jenny",
                "emb1": [
                    -0.019265105947852135,
                    0.0004929182468913496,
                    0.006711316294968128,
                ],
            },
        ]
        node_type = "Account"

        # Mock the upsertVertices call
        self.mock_connection.upsertVertices.return_value = {"status": "success"}

        result = self.vector_manager.upsert(data, node_type)

        # Assert that the result is as expected
        assert result == {"status": "success"}
        self.mock_connection.upsertVertices.assert_called_once_with(
            vertexType=node_type,
            vertices=[
                (
                    "Scott",
                    {
                        "emb1": [
                            -0.017733968794345856,
                            -0.01019224338233471,
                            -0.016571875661611557,
                        ]
                    },
                ),
                (
                    "Jenny",
                    {
                        "emb1": [
                            -0.019265105947852135,
                            0.0004929182468913496,
                            0.006711316294968128,
                        ]
                    },
                ),
            ],
        )

    def test_upsert_node_type_not_found(self):
        # Test case when node type is not found in the graph schema
        data = {
            "name": "Scott",
            "emb1": [
                -0.017733968794345856,
                -0.01019224338233471,
                -0.016571875661611557,
            ],
        }
        node_type = "NonExistingType"

        # Mock Graph Schema to return None for the node type
        self.vector_manager._graph_schema.nodes = {}

        result = self.vector_manager.upsert(data, node_type)

        # Assert that the result is None, because the node type doesn't exist
        assert result is None

    # -------------------------
    # Test Cases for fetch Method
    # -------------------------

    def test_fetch_successful(self):
        """
        Test case where the fetch method successfully retrieves embeddings.
        """
        node_id = "Ed"
        node_type = "Account"
        mock_result = [
            {
                "Nodes": [
                    {
                        "Embeddings": {
                            "emb1": [-0.003692443, 0.01049439, -0.004631793]
                        },
                        "attributes": {"isBlocked": False, "name": "Ed"},
                        "v_id": "Ed",
                        "v_type": "Account",
                    }
                ]
            }
        ]
        self.mock_connection.runInstalledQuery.return_value = mock_result

        expected_embeddings = {"emb1": [-0.003692443, 0.01049439, -0.004631793]}

        result = self.vector_manager.fetch(node_id, node_type)
        assert result == expected_embeddings

    def test_fetch_no_result(self):
        """
        Test case where the query returns no results.
        """
        node_id = "Ed"
        node_type = "Account"
        self.mock_connection.runInstalledQuery.return_value = []

        result = self.vector_manager.fetch(node_id, node_type)
        assert result is None

    def test_fetch_missing_nodes_key(self):
        """
        Test case where the 'Nodes' key is missing in the query result.
        """
        node_id = "Ed"
        node_type = "Account"
        mock_result = [{}]
        self.mock_connection.runInstalledQuery.return_value = mock_result

        result = self.vector_manager.fetch(node_id, node_type)
        assert result is None

    def test_fetch_empty_nodes_list(self):
        """
        Test case where the 'Nodes' list is empty.
        """
        node_id = "Ed"
        node_type = "Account"
        mock_result = [{"Nodes": []}]
        self.mock_connection.runInstalledQuery.return_value = mock_result

        result = self.vector_manager.fetch(node_id, node_type)
        assert result is None

    def test_fetch_missing_embeddings_key(self):
        """
        Test case where the 'Embeddings' key is missing in the node.
        """
        node_id = "Ed"
        node_type = "Account"
        mock_result = [
            {
                "Nodes": [
                    {
                        "attributes": {"isBlocked": False, "name": "Ed"},
                        "v_id": "Ed",
                        "v_type": "Account",
                    }
                ]
            }
        ]
        self.mock_connection.runInstalledQuery.return_value = mock_result

        result = self.vector_manager.fetch(node_id, node_type)
        assert result is None

    def test_fetch_embeddings_not_dict(self):
        """
        Test case where 'Embeddings' is not a dictionary.
        """
        node_id = "Ed"
        node_type = "Account"
        mock_result = [
            {
                "Nodes": [
                    {
                        "Embeddings": ["invalid_embedding_format"],
                        "attributes": {"isBlocked": False, "name": "Ed"},
                        "v_id": "Ed",
                        "v_type": "Account",
                    }
                ]
            }
        ]
        self.mock_connection.runInstalledQuery.return_value = mock_result

        result = self.vector_manager.fetch(node_id, node_type)
        assert result is None

    def test_fetch_embedding_name_not_string(self):
        """
        Test case where an embedding name is not a string.
        """
        node_id = "Ed"
        node_type = "Account"
        mock_result = [
            {
                "Nodes": [
                    {
                        "Embeddings": {123: [-0.003692443, 0.01049439, -0.004631793]},
                        "attributes": {"isBlocked": False, "name": "Ed"},
                        "v_id": "Ed",
                        "v_type": "Account",
                    }
                ]
            }
        ]
        self.mock_connection.runInstalledQuery.return_value = mock_result

        result = self.vector_manager.fetch(node_id, node_type)
        assert result is None

    def test_fetch_embedding_vector_not_list_of_floats(self):
        """
        Test case where an embedding vector is not a list of floats.
        """
        node_id = "Ed"
        node_type = "Account"
        mock_result = [
            {
                "Nodes": [
                    {
                        "Embeddings": {"emb1": "invalid_vector_format"},
                        "attributes": {"isBlocked": False, "name": "Ed"},
                        "v_id": "Ed",
                        "v_type": "Account",
                    }
                ]
            }
        ]
        self.mock_connection.runInstalledQuery.return_value = mock_result

        result = self.vector_manager.fetch(node_id, node_type)
        assert result is None

    def test_fetch_multiple_embeddings(self):
        """
        Test case where multiple embeddings are present and correctly returned.
        """
        node_id = "Ed"
        node_type = "Account"
        mock_result = [
            {
                "Nodes": [
                    {
                        "Embeddings": {
                            "emb1": [-0.003692443, 0.01049439, -0.004631793],
                            "emb2": [0.002345678, -0.00987654, 0.0054321],
                        },
                        "attributes": {"isBlocked": False, "name": "Ed"},
                        "v_id": "Ed",
                        "v_type": "Account",
                    }
                ]
            }
        ]
        self.mock_connection.runInstalledQuery.return_value = mock_result

        expected_embeddings = {
            "emb1": [-0.003692443, 0.01049439, -0.004631793],
            "emb2": [0.002345678, -0.00987654, 0.0054321],
        }

        result = self.vector_manager.fetch(node_id, node_type)
        assert result == expected_embeddings

    def test_fetch_no_embeddings_found(self):
        """
        Test case where no embeddings are found for the node.
        """
        node_id = "Ed"
        node_type = "Account"
        mock_result = [
            {
                "Nodes": [
                    {
                        "Embeddings": {},
                        "attributes": {"isBlocked": False, "name": "Ed"},
                        "v_id": "Ed",
                        "v_type": "Account",
                    }
                ]
            }
        ]
        self.mock_connection.runInstalledQuery.return_value = mock_result

        result = self.vector_manager.fetch(node_id, node_type)
        # Since 'Embeddings' exists but is empty, it should return the empty dict
        assert result == {}

    def test_fetch_exception_handling(self):
        """
        Test case where an exception occurs during the fetch operation.
        """
        node_id = "Ed"
        node_type = "Account"
        self.mock_connection.runInstalledQuery.side_effect = Exception("Database error")

        result = self.vector_manager.fetch(node_id, node_type)
        assert result is None

    def test_fetch_non_float_embedding_vector_elements(self):
        """
        Test case where embedding vectors contain non-float elements.
        """
        node_id = "Ed"
        node_type = "Account"
        mock_result = [
            {
                "Nodes": [
                    {
                        "Embeddings": {
                            "emb1": [-0.003692443, "invalid_float", -0.004631793]
                        },
                        "attributes": {"isBlocked": False, "name": "Ed"},
                        "v_id": "Ed",
                        "v_type": "Account",
                    }
                ]
            }
        ]
        self.mock_connection.runInstalledQuery.return_value = mock_result

        result = self.vector_manager.fetch(node_id, node_type)
        assert result is None

    def test_fetch_additional_unexpected_keys(self):
        """
        Test case where the node contains additional unexpected keys.
        """
        node_id = "Ed"
        node_type = "Account"
        mock_result = [
            {
                "Nodes": [
                    {
                        "Embeddings": {
                            "emb1": [-0.003692443, 0.01049439, -0.004631793]
                        },
                        "attributes": {
                            "isBlocked": False,
                            "name": "Ed",
                            "extra_attribute": "extra_value",
                        },
                        "v_id": "Ed",
                        "v_type": "Account",
                        "unexpected_key": "unexpected_value",
                    }
                ]
            }
        ]
        self.mock_connection.runInstalledQuery.return_value = mock_result

        expected_embeddings = {"emb1": [-0.003692443, 0.01049439, -0.004631793]}

        result = self.vector_manager.fetch(node_id, node_type)
        assert result == expected_embeddings

    def test_fetch_multiple_nodes_returned(self):
        """
        Test case where multiple nodes are returned for a single node_id.
        Assumes that only the first node is processed.
        """
        node_id = "Ed"
        node_type = "Account"
        mock_result = [
            {
                "Nodes": [
                    {
                        "Embeddings": {
                            "emb1": [-0.003692443, 0.01049439, -0.004631793]
                        },
                        "attributes": {"isBlocked": False, "name": "Ed"},
                        "v_id": "Ed",
                        "v_type": "Account",
                    },
                    {
                        "Embeddings": {
                            "emb1": [-0.002345678, 0.00987654, -0.003210987]
                        },
                        "attributes": {"isBlocked": True, "name": "EdDuplicate"},
                        "v_id": "EdDuplicate",
                        "v_type": "Account",
                    },
                ]
            }
        ]
        self.mock_connection.runInstalledQuery.return_value = mock_result

        expected_embeddings = {"emb1": [-0.003692443, 0.01049439, -0.004631793]}

        result = self.vector_manager.fetch(node_id, node_type)
        # Only the first node's embeddings should be returned
        assert result == expected_embeddings

    def test_fetch_embeddings_with_different_dimensions(self):
        """
        Test case where embeddings have different dimensions.
        Assumes that the method does not enforce consistent dimensions.
        """
        node_id = "Ed"
        node_type = "Account"
        mock_result = [
            {
                "Nodes": [
                    {
                        "Embeddings": {
                            "emb1": [
                                -0.003692443,
                                0.01049439,
                            ]  # Only 2 dimensions instead of expected 3
                        },
                        "attributes": {"isBlocked": False, "name": "Ed"},
                        "v_id": "Ed",
                        "v_type": "Account",
                    }
                ]
            }
        ]
        self.mock_connection.runInstalledQuery.return_value = mock_result

        # The method does not check for specific dimension sizes, only that elements are floats
        expected_embeddings = {"emb1": [-0.003692443, 0.01049439]}

        result = self.vector_manager.fetch(node_id, node_type)
        assert result == expected_embeddings

    def test_fetch_embeddings_with_nested_embeddings(self):
        """
        Test case where embeddings contain nested structures (invalid format).
        """
        node_id = "Ed"
        node_type = "Account"
        mock_result = [
            {
                "Nodes": [
                    {
                        "Embeddings": {
                            "emb1": [
                                -0.003692443,
                                [0.01049439],  # Nested list instead of float
                                -0.004631793,
                            ]
                        },
                        "attributes": {"isBlocked": False, "name": "Ed"},
                        "v_id": "Ed",
                        "v_type": "Account",
                    }
                ]
            }
        ]
        self.mock_connection.runInstalledQuery.return_value = mock_result

        result = self.vector_manager.fetch(node_id, node_type)
        # Should return None due to invalid embedding vector format
        assert result is None

    # -------------------------
    # Tests for search_multi_vector_attributes
    # -------------------------

    def test_search_multi_vector_attributes_single_return_attributes(self):
        """
        Test case where only one attribute is returned for each node.
        """
        data = [-0.0177, -0.0101, -0.0165]
        vector_attribute_names = ["emb1", "emb2"]
        node_types = ["Account", "Phone"]
        return_attributes = [["name"], ["number"]]
        limit = 2

        def mock_run_installed_query(query_name, params, usePost=True):
            if "emb1" in query_name:
                return [
                    {"map_node_distance": {"Account1": 0.1, "Account2": 0.2}},
                    {
                        "Nodes": [
                            {
                                "v_id": "Account1",
                                "attributes": {"name": "Scott", "value": True},
                            },
                            {
                                "v_id": "Account2",
                                "attributes": {"name": "Jenny", "value": False},
                            },
                        ]
                    },
                ]
            elif "emb2" in query_name:
                return [
                    {"map_node_distance": {"Phone1": 0.15, "Phone2": 0.25}},
                    {
                        "Nodes": [
                            {
                                "v_id": "Phone1",
                                "attributes": {
                                    "number": "718-245-5888",
                                    "isBlocked": False,
                                },
                            },
                            {
                                "v_id": "Phone2",
                                "attributes": {
                                    "number": "650-658-9867",
                                    "isBlocked": True,
                                },
                            },
                        ]
                    },
                ]
            return []

        self.mock_connection.runInstalledQuery.side_effect = mock_run_installed_query

        result = self.vector_manager.search_multi_vector_attributes(
            data,
            vector_attribute_names,
            node_types,
            limit,
            return_attributes_list=return_attributes,
        )

        # Assert the results are correctly filtered by attributes and sorted by distance
        assert len(result) == 2
        assert result[0]["id"] == "Account1"
        assert result[1]["id"] == "Phone1"
        assert result[0]["distance"] == 0.1
        assert result[1]["distance"] == 0.15
        assert "name" in result[0]
        assert "number" in result[1]
        assert "value" not in result[0]
        assert "isBlocked" not in result[1]

    def test_search_multi_vector_attributes_all_attributes(self):
        """
        Test case where all attributes are returned for each node.
        """
        data = [-0.0177, -0.0101, -0.0165]
        vector_attribute_names = ["emb1", "emb2"]
        node_types = ["Account", "Phone"]
        return_attributes = None  # All attributes will be returned
        limit = 2

        def mock_run_installed_query(query_name, params, usePost=True):
            if "emb1" in query_name:
                return [
                    {"map_node_distance": {"Account1": 0.1, "Account2": 0.2}},
                    {
                        "Nodes": [
                            {
                                "v_id": "Account1",
                                "attributes": {"name": "Scott", "value": True},
                            },
                            {
                                "v_id": "Account2",
                                "attributes": {"name": "Jenny", "value": False},
                            },
                        ]
                    },
                ]
            elif "emb2" in query_name:
                return [
                    {"map_node_distance": {"Phone1": 0.15, "Phone2": 0.25}},
                    {
                        "Nodes": [
                            {
                                "v_id": "Phone1",
                                "attributes": {
                                    "number": "718-245-5888",
                                    "isBlocked": False,
                                },
                            },
                            {
                                "v_id": "Phone2",
                                "attributes": {
                                    "number": "650-658-9867",
                                    "isBlocked": True,
                                },
                            },
                        ]
                    },
                ]
            return []

        self.mock_connection.runInstalledQuery.side_effect = mock_run_installed_query

        result = self.vector_manager.search_multi_vector_attributes(
            data,
            vector_attribute_names,
            node_types,
            limit,
            return_attributes_list=return_attributes,
        )

        # Assert the results are correctly filtered by attributes and sorted by distance
        assert len(result) == 2
        assert result[0]["id"] == "Account1"
        assert result[1]["id"] == "Phone1"
        assert result[0]["distance"] == 0.1
        assert result[1]["distance"] == 0.15
        assert "name" in result[0]
        assert "value" in result[0]
        assert "number" in result[1]
        assert "isBlocked" in result[1]

    def test_search_multi_vector_attributes_invalid_return_attributes_length(self):
        """
        Test case where the return_attributes_list length does not match vector_attribute_names length.
        """
        data = [-0.0177, -0.0101, -0.0165]
        vector_attribute_names = ["emb1", "emb2"]
        node_types = ["Account", "Phone"]
        return_attributes = [["name"], ["number"], ["isBlocked"]]  # Invalid size
        limit = 2

        result = self.vector_manager.search_multi_vector_attributes(
            data,
            vector_attribute_names,
            node_types,
            limit,
            return_attributes_list=return_attributes,
        )

        # Assert the result is empty due to mismatched lengths of return_attributes
        assert result == []

    def test_search_multi_vector_attributes_node_types_length_mismatch(self):
        """
        Test case for mismatch in node_types and vector_attribute_names lengths.
        """
        data = [-0.0177, -0.0101, -0.0165]
        vector_attribute_names = ["emb1", "emb2"]
        node_types = ["Account"]  # Only one node type, but two vector attributes
        limit = 2

        result = self.vector_manager.search_multi_vector_attributes(
            data, vector_attribute_names, node_types, limit
        )

        # Assert the result is empty due to mismatched lengths of node_types and vector_attribute_names
        assert result == []

    def test_search_multi_vector_attributes_no_results(self):
        """
        Test case where no results are found.
        """
        data = [-0.0177, -0.0101, -0.0165]
        vector_attribute_names = ["emb1", "emb2"]
        node_types = ["Account", "Phone"]
        return_attributes = None  # Return all attributes
        limit = 2

        # Mock the search result for both attributes to return no results
        self.mock_connection.runInstalledQuery.return_value = [
            {"map_node_distance": {}},  # No matching nodes found
            {"Nodes": []},
        ]

        result = self.vector_manager.search_multi_vector_attributes(
            data,
            vector_attribute_names,
            node_types,
            limit,
            return_attributes_list=return_attributes,
        )

        # Assert the result is empty since no nodes were found
        assert result == []

    def test_search_multi_vector_attributes_run_installed_query_returns_none(self):
        """
        Test case where run_installed_query returns None.
        """
        data = [-0.0177, -0.0101, -0.0165]
        vector_attribute_names = ["emb1"]
        node_types = ["Account"]
        return_attributes = [["name"]]
        limit = 2

        # Mock run_installed_query to return None
        self.mock_connection.runInstalledQuery.return_value = None

        result = self.vector_manager.search_multi_vector_attributes(
            data,
            vector_attribute_names,
            node_types,
            limit,
            return_attributes_list=return_attributes,
        )

        # Assert the result is empty due to None return
        assert result == []

    def test_search_multi_vector_attributes_run_installed_query_invalid_structure(self):
        """
        Test case where run_installed_query returns an invalid structure.
        """
        data = [-0.0177, -0.0101, -0.0165]
        vector_attribute_names = ["emb1"]
        node_types = ["Account"]
        return_attributes = [["name"]]
        limit = 2

        # Mock run_installed_query to return a list with missing keys
        self.mock_connection.runInstalledQuery.return_value = [
            {"invalid_key": {}},
            {"Nodes": []},
        ]

        result = self.vector_manager.search_multi_vector_attributes(
            data,
            vector_attribute_names,
            node_types,
            limit,
            return_attributes_list=return_attributes,
        )

        # Assert the result is empty due to missing 'map_node_distance'
        assert result == []

    # -------------------------
    # Tests for search
    # -------------------------

    def test_search_with_single_return_attribute(self):
        """
        Test case for search with a single return attribute.
        """
        data = [-0.0177, -0.0101, -0.0165]
        vector_attribute_name = "emb1"
        node_type = "Account"
        limit = 5
        return_attributes = ["name"]

        self.mock_connection.runInstalledQuery.return_value = [
            {"map_node_distance": {"Account1": 0.1, "Account2": 0.2}},
            {
                "Nodes": [
                    {
                        "v_id": "Account1",
                        "attributes": {"name": "Scott", "value": True},
                    },
                    {
                        "v_id": "Account2",
                        "attributes": {"name": "Jenny", "value": False},
                    },
                ]
            },
        ]

        result = self.vector_manager.search(
            data, vector_attribute_name, node_type, limit, return_attributes
        )

        # Assert the search results are combined correctly
        assert len(result) == 2
        assert result[0]["id"] == "Account1"
        assert result[1]["id"] == "Account2"
        assert result[0]["distance"] == 0.1
        assert result[1]["distance"] == 0.2
        assert "name" in result[0]
        assert "name" in result[1]
        assert "value" not in result[0]
        assert "value" not in result[1]

    def test_search_with_all_attributes(self):
        """
        Test case for search where all attributes are returned.
        """
        data = [-0.0177, -0.0101, -0.0165]
        vector_attribute_name = "emb2"
        node_type = "Phone"
        limit = 3
        return_attributes = None  # All attributes will be returned

        self.mock_connection.runInstalledQuery.return_value = [
            {"map_node_distance": {"Phone1": 0.05, "Phone2": 0.15, "Phone3": 0.25}},
            {
                "Nodes": [
                    {
                        "v_id": "Phone1",
                        "attributes": {"number": "123-456-7890", "isBlocked": False},
                    },
                    {
                        "v_id": "Phone2",
                        "attributes": {"number": "098-765-4321", "isBlocked": True},
                    },
                    {
                        "v_id": "Phone3",
                        "attributes": {"number": "555-555-5555", "isBlocked": False},
                    },
                ]
            },
        ]

        result = self.vector_manager.search(
            data, vector_attribute_name, node_type, limit, return_attributes
        )

        # Assert the search results are combined correctly
        assert len(result) == 3
        assert result[0]["id"] == "Phone1"
        assert result[1]["id"] == "Phone2"
        assert result[2]["id"] == "Phone3"
        assert result[0]["distance"] == 0.05
        assert result[1]["distance"] == 0.15
        assert result[2]["distance"] == 0.25
        assert "number" in result[0]
        assert "isBlocked" in result[0]
        assert "number" in result[1]
        assert "isBlocked" in result[1]
        assert "number" in result[2]
        assert "isBlocked" in result[2]

    def test_search_with_no_matching_nodes(self):
        """
        Test case where no matching nodes are found.
        """
        data = [-0.0177, -0.0101, -0.0165]
        vector_attribute_name = "emb1"
        node_type = "Account"
        limit = 2
        return_attributes = ["name"]

        self.mock_connection.runInstalledQuery.return_value = [
            {"map_node_distance": {}},
            {"Nodes": []},
        ]

        result = self.vector_manager.search(
            data, vector_attribute_name, node_type, limit, return_attributes
        )

        # Assert the result is empty since no nodes were found
        assert result == []

    def test_search_run_installed_query_returns_none(self):
        """
        Test case where run_installed_query returns None.
        """
        data = [-0.0177, -0.0101, -0.0165]
        vector_attribute_name = "emb2"
        node_type = "Phone"
        limit = 3
        return_attributes = ["number"]

        # Mock run_installed_query to return None
        self.mock_connection.runInstalledQuery.return_value = None

        result = self.vector_manager.search(
            data, vector_attribute_name, node_type, limit, return_attributes
        )

        # Assert the result is empty due to None return
        assert result == []

    def test_search_run_installed_query_invalid_structure(self):
        """
        Test case where run_installed_query returns an invalid structure.
        """
        data = [-0.0177, -0.0101, -0.0165]
        vector_attribute_name = "emb1"
        node_type = "Account"
        limit = 2
        return_attributes = ["name"]

        # Mock run_installed_query to return a list with missing keys
        self.mock_connection.runInstalledQuery.return_value = [
            {"invalid_key": {}},
            {"Nodes": []},
        ]

        result = self.vector_manager.search(
            data, vector_attribute_name, node_type, limit, return_attributes
        )

        # Assert the result is empty due to missing 'map_node_distance'
        assert result == []

    def test_search_with_candidate_ids(self):
        """
        Test case for search with candidate_ids provided.
        """
        data = [-0.0177, -0.0101, -0.0165]
        vector_attribute_name = "emb1"
        node_type = "Account"
        limit = 3
        return_attributes = ["name"]
        candidate_ids = {"Account1", "Account3"}

        self.mock_connection.runInstalledQuery.return_value = [
            {"map_node_distance": {"Account1": 0.1}},
            {
                "Nodes": [
                    {
                        "v_id": "Account1",
                        "attributes": {"name": "Scott", "value": True},
                    },
                ]
            },
        ]

        result = self.vector_manager.search(
            data,
            vector_attribute_name,
            node_type,
            limit,
            return_attributes,
            candidate_ids=candidate_ids,
        )

        # Assert that only candidate_ids are considered
        assert len(result) == 1
        assert result[0]["id"] == "Account1"
        assert result[0]["distance"] == 0.1
        assert "name" in result[0]
        assert "value" not in result[0]

    def test_search_with_empty_return_attributes(self):
        """
        Test case where return_attributes is an empty list.
        """
        data = [-0.0177, -0.0101, -0.0165]
        vector_attribute_name = "emb2"
        node_type = "Phone"
        limit = 2
        return_attributes = []  # Should return no attributes

        self.mock_connection.runInstalledQuery.return_value = [
            {"map_node_distance": {"Phone1": 0.05, "Phone2": 0.15}},
            {
                "Nodes": [
                    {
                        "v_id": "Phone1",
                        "attributes": {"number": "123-456-7890", "isBlocked": False},
                    },
                    {
                        "v_id": "Phone2",
                        "attributes": {"number": "098-765-4321", "isBlocked": True},
                    },
                ]
            },
        ]

        result = self.vector_manager.search(
            data, vector_attribute_name, node_type, limit, return_attributes
        )

        # Assert that no attributes are returned
        assert len(result) == 2
        assert "number" not in result[0]
        assert "isBlocked" not in result[0]
        assert "number" not in result[1]
        assert "isBlocked" not in result[1]
        assert "id" in result[0]
        assert "distance" in result[0]
        assert "id" in result[1]
        assert "distance" in result[1]

    def test_search_with_non_string_return_attributes(self):
        """
        Test case where return_attributes contain non-string types.
        """
        data = [-0.0177, -0.0101, -0.0165]
        vector_attribute_name = "emb1"
        node_type = "Account"
        limit = 2
        return_attributes = [["name", 123]]  # Invalid attribute type

        # Assuming the method handles non-string attributes gracefully
        self.mock_connection.runInstalledQuery.return_value = [
            {"map_node_distance": {"Account1": 0.1}},
            {
                "Nodes": [
                    {
                        "v_id": "Account1",
                        "attributes": {"name": "Scott", "value": True},
                    }
                ]
            },
        ]

        result = self.vector_manager.search_multi_vector_attributes(
            data,
            [vector_attribute_name],
            [node_type],
            limit,
            return_attributes_list=return_attributes,
        )

        # Assert that only valid string attributes are returned
        assert len(result) == 1
        assert result[0]["id"] == "Account1"
        assert result[0]["distance"] == 0.1
        assert "name" in result[0]
        # The invalid attribute should be ignored or cause an error based on implementation
        # Here, we assume it's ignored
        assert len(result[0]) == 3  # id, distance, name

    def test_search_with_missing_node_id(self):
        """
        Test case where one of the nodes is missing the 'v_id'.
        """
        data = [-0.0177, -0.0101, -0.0165]
        vector_attribute_name = "emb2"
        node_type = "Phone"
        limit = 2
        return_attributes = ["number"]

        self.mock_connection.runInstalledQuery.return_value = [
            {"map_node_distance": {"Phone1": 0.05, "Phone2": 0.15}},
            {
                "Nodes": [
                    {
                        "attributes": {"number": "123-456-7890", "isBlocked": False},
                    },  # Missing 'v_id'
                    {
                        "v_id": "Phone2",
                        "attributes": {"number": "098-765-4321", "isBlocked": True},
                    },
                ]
            },
        ]

        result = self.vector_manager.search_multi_vector_attributes(
            data,
            [vector_attribute_name],
            [node_type],
            limit,
            return_attributes_list=[return_attributes],
        )

        # Assert that the node without 'v_id' is skipped
        assert len(result) == 1
        assert result[0]["id"] == "Phone2"
        assert result[0]["distance"] == 0.15
        assert "number" in result[0]
        assert "isBlocked" not in result[0]

    def test_search_with_distance_missing(self):
        """
        Test case where the distance for a node is missing in 'map_node_distance'.
        """
        data = [-0.0177, -0.0101, -0.0165]
        vector_attribute_name = "emb1"
        node_type = "Account"
        limit = 2
        return_attributes = ["name"]

        self.mock_connection.runInstalledQuery.return_value = [
            {"map_node_distance": {"Account1": 0.1}},
            {
                "Nodes": [
                    {
                        "v_id": "Account1",
                        "attributes": {"name": "Scott", "value": True},
                    },
                    {
                        "v_id": "Account2",
                        "attributes": {"name": "Jenny", "value": False},
                    },
                ]
            },
        ]

        result = self.vector_manager.search(
            data,
            vector_attribute_name,
            node_type,
            limit,
            return_attributes,
        )

        # Assert that Account2 is included with distance as None or skipped based on implementation
        # Assuming it's included with distance as None
        assert len(result) == 2
        assert result[0]["id"] == "Account1"
        assert result[0]["distance"] == 0.1
        assert "name" in result[0]
        assert result[1]["id"] == "Account2"
        assert result[1]["distance"] is None
        assert "name" in result[1]

    def test_search_with_exception_handling(self):
        """
        Test case where an exception is raised during search.
        """
        data = [-0.0177, -0.0101, -0.0165]
        vector_attribute_name = "emb1"
        node_type = "Account"
        limit = 2
        return_attributes = ["name"]

        # Mock run_installed_query to raise an exception
        self.mock_connection.runInstalledQuery.side_effect = Exception("Database error")

        result = self.vector_manager.search(
            data,
            vector_attribute_name,
            node_type,
            limit,
            return_attributes,
        )

        # Assert that the result is empty due to exception
        assert result == []

    # -------------------------
    # Additional Tests for Robustness
    # -------------------------

    def test_search_with_large_limit(self):
        """
        Test case where the limit exceeds the number of available results.
        """
        data = [-0.0177, -0.0101, -0.0165]
        vector_attribute_name = "emb1"
        node_type = "Account"
        limit = 10
        return_attributes = ["name"]

        self.mock_connection.runInstalledQuery.return_value = [
            {"map_node_distance": {"Account1": 0.1, "Account2": 0.2}},
            {
                "Nodes": [
                    {
                        "v_id": "Account1",
                        "attributes": {"name": "Scott", "value": True},
                    },
                    {
                        "v_id": "Account2",
                        "attributes": {"name": "Jenny", "value": False},
                    },
                ]
            },
        ]

        result = self.vector_manager.search(
            data,
            vector_attribute_name,
            node_type,
            limit,
            return_attributes,
        )

        # Assert that all available results are returned
        assert len(result) == 2
        assert result[0]["id"] == "Account1"
        assert result[1]["id"] == "Account2"

    def test_search_with_zero_limit(self):
        """
        Test case where the limit is set to zero.
        """
        data = [-0.0177, -0.0101, -0.0165]
        vector_attribute_name = "emb2"
        node_type = "Phone"
        limit = 0
        return_attributes = ["number"]

        self.mock_connection.runInstalledQuery.return_value = [
            {"map_node_distance": {}},
            {"Nodes": []},
        ]

        result = self.vector_manager.search(
            data, vector_attribute_name, node_type, limit, return_attributes
        )

        # Assert that no results are returned when limit is zero
        assert result == []

    def test_search_multi_vector_attributes_with_empty_vector_attribute_names(self):
        """
        Test case where vector_attribute_names is empty.
        """
        data = [-0.0177, -0.0101, -0.0165]
        vector_attribute_names = []
        node_types = []
        return_attributes = []
        limit = 5

        result = self.vector_manager.search_multi_vector_attributes(
            data,
            vector_attribute_names,
            node_types,
            limit,
            return_attributes_list=return_attributes,
        )

        # Assert that the result is empty since no vector attributes are provided
        assert result == []

    def test_search_with_non_existent_vector_attribute(self):
        """
        Test case where the vector_attribute_name does not exist in the schema.
        """
        data = [-0.0177, -0.0101, -0.0165]
        vector_attribute_name = "non_existent_emb"
        node_type = "Account"
        limit = 2
        return_attributes = ["name"]

        # Mock run_installed_query to return empty results as the vector attribute doesn't exist
        self.mock_connection.runInstalledQuery.return_value = [
            {"map_node_distance": {}},
            {"Nodes": []},
        ]

        result = self.vector_manager.search(
            data,
            vector_attribute_name,
            node_type,
            limit,
            return_attributes,
        )

        # Assert that the result is empty
        assert result == []
