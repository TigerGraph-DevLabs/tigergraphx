import logging
from typing import Dict, Literal, Optional
from pathlib import Path

from .base_manager import BaseManager

from tigergraphx.core.graph_context import GraphContext
from tigergraphx.config import GraphSchema, TigerGraphConnectionConfig


logger = logging.getLogger(__name__)


class SchemaManager(BaseManager):
    def __init__(self, context: GraphContext):
        super().__init__(context)

    def get_schema(self, format: Literal["json", "dict"] = "dict") -> str | Dict:
        if format == "json":
            return self._graph_schema.model_dump_json()
        return self._graph_schema.model_dump()

    def create_schema(self, drop_existing_graph=False) -> bool:
        logger.info(
            "Starting schema creation for graph: %s", self._graph_schema.graph_name
        )

        # Drop graph if drop_existing_graph is True
        logger.info("Checking if graph exists: %s", self._graph_schema.graph_name)
        is_graph_existing = self._check_graph_exists()
        if drop_existing_graph and is_graph_existing:
            self.drop_graph()

        # Create the schema
        if not is_graph_existing or drop_existing_graph:
            gsql_script = self._create_gsql_graph_schema(
                self._graph_schema
            ) + self._create_gsql_add_vector_attr(self._graph_schema)
            result = self._connection.gsql(gsql_script)
            if "Failed to create schema change jobs" in result:
                error_msg = (
                    f"Schema change job creation failed. GSQL response: {result}"
                )
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            return True
        return False

    def drop_graph(self) -> None:
        gsql_script = self._create_gsql_drop_graph(self._graph_schema.graph_name)
        self._connection.gsql(gsql_script)

    @staticmethod
    def get_schema_from_db(
        graph_name: str,
        tigergraph_connection_config: Optional[
            TigerGraphConnectionConfig | Dict | str | Path
        ] = None,
    ) -> Dict:
        # Create a minimal GraphSchema to initialize the context
        initial_graph_schema = GraphSchema(graph_name=graph_name, nodes={}, edges={})
        context = GraphContext(
            graph_schema=initial_graph_schema,
            tigergraph_connection_config=tigergraph_connection_config,
        )
        # Retrieve the schema from TigerGraph DB
        raw_schema = context.connection.getSchema()
        # Construct nodes dictionary
        nodes = {}
        for vertex in raw_schema["VertexTypes"]:
            # Collect attributes
            attributes = {
                attr["AttributeName"]: {
                    "data_type": attr["AttributeType"]["Name"],
                    "default_value": attr.get("DefaultValue"),
                }
                for attr in vertex["Attributes"]
            }
            # Include primary key as an attribute if PrimaryIdAsAttribute is True
            primary_id = vertex["PrimaryId"]
            if primary_id["PrimaryIdAsAttribute"]:
                attributes[primary_id["AttributeName"]] = {
                    "data_type": primary_id["AttributeType"]["Name"],
                    "default_value": None,  # Primary keys typically do not have default values
                }
            nodes[vertex["Name"]] = {
                "primary_key": primary_id["AttributeName"],
                "attributes": attributes,
            }
        # Construct edges dictionary
        edges = {
            edge["Name"]: {
                "is_directed_edge": edge["IsDirected"],
                "from_node_type": edge["FromVertexTypeName"],
                "to_node_type": edge["ToVertexTypeName"],
                "attributes": {
                    attr["AttributeName"]: {
                        "data_type": attr["AttributeType"]["Name"],
                        "default_value": attr.get("DefaultValue"),
                    }
                    for attr in edge["Attributes"]
                },
            }
            for edge in raw_schema["EdgeTypes"]
        }
        # Combine into a dictionary format
        graph_schema = {
            "graph_name": graph_name,
            "nodes": nodes,
            "edges": edges,
        }
        return graph_schema

    def _check_graph_exists(self) -> bool:
        """Check if the specified graph name exists in the gsql_script."""
        result = self._connection.gsql(f"USE Graph {self._graph_schema.graph_name}")
        logger.info(
            "Graph existence check for %s: %s",
            self._graph_schema.graph_name,
            "exists" if "Using graph" in result else "does not exist",
        )
        return "Using graph" in result

    @staticmethod
    def _create_gsql_drop_graph(graph_name: str) -> str:
        # Generating the gsql script to drop graph
        gsql_script = f"""
USE GRAPH {graph_name}
DROP QUERY *
DROP JOB *
DROP GRAPH {graph_name}
"""
        return gsql_script.strip()

    @staticmethod
    def _create_gsql_graph_schema(graph_schema: GraphSchema) -> str:
        # Extracting node attributes
        node_definitions = []
        for node_name, node_schema in graph_schema.nodes.items():
            primary_key_name = node_schema.primary_key

            # Extract the primary ID type
            primary_key_type = node_schema.attributes[primary_key_name].data_type.value

            # Build attribute string excluding the primary ID, since it’s declared separately
            node_attr_str = ", ".join(
                [
                    f"{attribute_name} {attribute_schema.data_type.value}"
                    for attribute_name, attribute_schema in node_schema.attributes.items()
                    if attribute_name != primary_key_name
                ]
            )

            # Append the vertex definition with the dynamic primary ID
            node_definitions.append(
                f"ADD VERTEX {node_name}(PRIMARY_ID {primary_key_name} {primary_key_type}"
                + (f", {node_attr_str}" if node_attr_str else "")
                + ') WITH PRIMARY_ID_AS_ATTRIBUTE="true";'
            )

        # Extracting edge attributes
        edge_definitions = []
        for edge_name, edge_schema in graph_schema.edges.items():
            edge_attr_str = []

            # Separate out the regular attributes and discriminator attributes
            regular_attrs = []
            discriminator_attrs = []
            for attribute_name, attribute_schema in edge_schema.attributes.items():
                if attribute_name in edge_schema.discriminator:
                    # This attribute is part of the edge identifier
                    discriminator_attrs.append(
                        f"{attribute_name} {attribute_schema.data_type.value}"
                    )
                else:
                    # This attribute is a regular edge attribute
                    regular_attrs.append(
                        f"{attribute_name} {attribute_schema.data_type.value}"
                    )

            # Combine regular and discriminator attributes
            if discriminator_attrs:
                discriminator_str = f"DISCRIMINATOR({', '.join(discriminator_attrs)})"
                edge_attr_str.append(discriminator_str)

            # Adding regular attributes to edge definition string
            if regular_attrs:
                edge_attr_str.append(", ".join(regular_attrs))

            # Construct the edge definition, with conditional attribute string and direction
            edge_type_str = "DIRECTED" if edge_schema.is_directed_edge else "UNDIRECTED"
            reverse_edge_clause = (
                f' WITH REVERSE_EDGE="reverse_{edge_name}"'
                if edge_schema.is_directed_edge
                else ""
            )

            edge_definitions.append(
                f"ADD {edge_type_str} EDGE {edge_name}(FROM {edge_schema.from_node_type}, TO {edge_schema.to_node_type}"
                + (f", {', '.join(edge_attr_str)}" if edge_attr_str else "")
                + f"){reverse_edge_clause};"
            )

        # Generating the full schema string
        graph_name = graph_schema.graph_name
        if len(node_definitions) + len(edge_definitions) == 0:
            gsql_script = f"""
# 1. Create graph
CREATE GRAPH {graph_name} ()
"""
        else:
            gsql_script = f"""
# 1. Create graph
CREATE GRAPH {graph_name} ()

# 2. Create schema_change job
CREATE SCHEMA_CHANGE JOB schema_change_job_for_graph_{graph_name} FOR GRAPH {graph_name} {{
  # 2.1 Create vertices
  {'\n  '.join(node_definitions)}

  # 2.2 Create edges
  {'\n  '.join(edge_definitions)}
}}

# 3. Run schema_change job
RUN SCHEMA_CHANGE JOB schema_change_job_for_graph_{graph_name}

# 4. Drop schema_change job
DROP JOB schema_change_job_for_graph_{graph_name}

# 5. Install functions in the package gds
USE GLOBAL
IMPORT PACKAGE GDS
INSTALL FUNCTION GDS.*
"""
        logger.debug("GSQL script for creating graph: %s", gsql_script)
        return gsql_script.strip()

    @staticmethod
    def _create_gsql_add_vector_attr(graph_schema: "GraphSchema") -> str:
        """
        Generate the GSQL script to add vector attributes to vertices.

        Args:
            graph_schema (GraphSchema): The graph schema configuration.

        Returns:
            str: The generated GSQL script.
        """
        # List to hold GSQL commands for adding vector attributes
        vector_attribute_statements = []

        # List to hold GSQL commands for creating vector search query
        query_statements = []

        # Iterate over all nodes and their vector attributes
        for node_type, node_schema in graph_schema.nodes.items():
            if node_schema.vector_attributes:
                for (
                    vector_attribute_name,
                    vector_attr,
                ) in node_schema.vector_attributes.items():
                    # Extract the fields from VectorAttributeSchema
                    dimension = vector_attr.dimension
                    index_type = vector_attr.index_type
                    data_type = vector_attr.data_type
                    metric = vector_attr.metric

                    # Generate GSQL for each vector attribute in the node schema
                    vector_attribute_statements.append(
                        f"ALTER VERTEX {node_type} ADD VECTOR ATTRIBUTE {vector_attribute_name}"
                        f'(DIMENSION={dimension}, INDEXTYPE="{index_type}", '
                        f'DATATYPE="{data_type}", METRIC="{metric}");'
                    )
                    query_statements.append(
                        f"""
CREATE OR REPLACE QUERY api_vector_search_{node_type}_{vector_attribute_name} (
  UINT k=10,
  LIST<float> query_vector
) SYNTAX v3 {{
  MapAccum<Vertex, Float> @@map_node_distance;

  Nodes = vectorSearch(
    {{{node_type}.{vector_attribute_name}}},
    query_vector,
    k,
    {{ distance_map: @@map_node_distance}}
  );

  PRINT @@map_node_distance AS map_node_distance;
  PRINT Nodes;
}}
""".strip()
                    )

        # Combine all statements and wrap them into the full GSQL script
        if len(vector_attribute_statements) == 0:
            gsql_script = ""
        else:
            gsql_script = f"""
# 1. Use graph
USE GRAPH {graph_schema.graph_name}

# 2. Create schema_change job
CREATE SCHEMA_CHANGE JOB change_schema_of_{graph_schema.graph_name} FOR GRAPH {graph_schema.graph_name} {{
  # 2.1 Add vector attributes
  {'\n  '.join(vector_attribute_statements)}
}}

# 3. Run schema_change job
RUN SCHEMA_CHANGE JOB change_schema_of_{graph_schema.graph_name}

# 4. Drop schema_change job
DROP JOB change_schema_of_{graph_schema.graph_name}
"""
            if len(query_statements) > 0:
                gsql_script = f"""
{gsql_script}
{'\n'.join(query_statements)}
INSTALL QUERY *
"""
        logger.debug("GSQL script for adding vector attributes: %s", gsql_script)
        return gsql_script.rstrip()
