import logging
from typing import Optional, List, Dict, Tuple
import pandas as pd

from pyTigerGraph import TigerGraphConnection

from .gsql import CREATE_QUERY_API_DEGREE, CREATE_QUERY_API_GET_NODE_EDGES
from tigergraphx.config import (
    TigerGraphConnectionConfig,
    NodeSchema,
    EdgeSchema,
    GraphSchema,
    LoadingJobConfig,
    NeighborSpec,
    NodeSpec,
)

logger = logging.getLogger(__name__)


class BaseGraph:
    def __init__(
        self,
        graph_schema: GraphSchema,
        tigergraph_connection_config: Optional[TigerGraphConnectionConfig] = None,
        drop_existing_graph: bool = False,
    ):
        # Set class attributes
        self.name = graph_schema.graph_name
        self.schema_config = graph_schema

        # Set the default node type if there's only one node type
        nodes: Dict[str, NodeSchema] = graph_schema.nodes
        self.node_type = next(iter(nodes)) if len(nodes) == 1 else ""

        # Set the default edge type if there's only one edge type
        edges: Dict[str, EdgeSchema] = graph_schema.edges
        self.edge_type = next(iter(edges)) if len(edges) == 1 else ""

        # Set the log level to WARNING to suppress INFO messages
        logging.getLogger("pyTigerGraph").setLevel(logging.WARNING)

        # Create a TigerGraph connection
        if tigergraph_connection_config is None:  # Set default options
            tigergraph_connection_config = TigerGraphConnectionConfig()
        self._connection = TigerGraphConnection(
            host=tigergraph_connection_config.host,
            graphname=self.name,
            username=tigergraph_connection_config.user_name,
            password=tigergraph_connection_config.password,
            restppPort=tigergraph_connection_config.restpp_port,
            gsPort=tigergraph_connection_config.graph_studio_port,
        )

        # Drop graph if drop_existing_graph is True
        is_graph_existing = self._check_graph_exists()
        if drop_existing_graph and is_graph_existing:
            gsql_script = self._create_gsql_drop_graph(self.name)
            result = self._connection.gsql(gsql_script)

        # Create the schema and install queries
        if not is_graph_existing or drop_existing_graph:
            # Create schema
            gsql_script = self._create_gsql_graph_schema(self.schema_config)
            result = self._connection.gsql(gsql_script)
            if "Failed to create schema change jobs" in result:
                error_msg = (
                    f"Schema change job creation failed. GSQL response: {result}"
                )
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            # Install queries
            gsql_script = self._create_gsql_install_queries(self.name)
            result = self._connection.gsql(gsql_script)
            if "Saved as draft query with type/semantic error" in result:
                error_msg = f"Query type/semantic error. GSQL response: {result}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

    def load_data(self, loading_job_config: LoadingJobConfig):
        gsql_script = self._create_gsql_load_data(loading_job_config)
        result = self._connection.gsql(gsql_script)
        if "LOAD SUCCESSFUL for loading jobid" not in result:
            error_msg = f"Data loading failed. GSQL response: {result}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def run_query(self, query_name: str, params: Dict = {}):
        try:
            return self._connection.runInstalledQuery(
                queryName=query_name, params=params
            )
        except Exception as e:
            logger.error(f"Error running query {query_name}: {e}")
            return None

    def _add_node(self, node_id: str, node_type: str, **attr):
        try:
            self._connection.upsertVertex(node_type, node_id, attr)
        except Exception as e:
            logger.error(f"Error adding node {node_id}: {e}")
            return None

    def _add_edge(
        self,
        src_node_id: str,
        tgt_node_id: str,
        src_node_type: str,
        edge_type: str,
        tgt_node_type: str,
        **attr,
    ):
        try:
            result = self._connection.upsertEdge(
                src_node_type, src_node_id, edge_type, tgt_node_type, tgt_node_id, attr
            )
        except Exception as e:
            logger.error(f"Error adding from {src_node_id} to {tgt_node_id}: {e}")
            return None

    def _has_node(self, node_id: str, node_type: str) -> bool:
        try:
            result = self._connection.getVerticesById(node_type, node_id)
            return bool(result)
        except Exception as e:
            logger.error(f"Error checking existence of node {node_id}: {e}")
            return False

    def _has_edge(
        self,
        src_node_id: str | int,
        tgt_node_id: str | int,
        src_node_type: str,
        edge_type: str,
        tgt_node_type: str,
    ) -> bool:
        try:
            result = self._connection.getEdgeCountFrom(
                src_node_type, src_node_id, edge_type, tgt_node_type, tgt_node_id
            )
            return bool(result)
        except Exception as e:
            logger.error(
                f"Error checking existence of edge from {src_node_id} to {tgt_node_type}: {e}"
            )
            return False

    def _get_node_data(self, node_id: str, node_type: str) -> Dict:
        """Retrieve node attributes by type and ID."""
        try:
            result = self._connection.getVerticesById(
                vertexType=node_type,
                vertexIds=node_id,
            )
            if isinstance(result, List) and result:
                return result[0].get("attributes", {})
            else:
                raise TypeError(f"Unsupported type for result: {type(result)}")
        except (TypeError, Exception) as e:
            logger.error(f"Error retrieving node {node_id}: {e}")
            return {}

    def _get_edge_data(
        self,
        src_node_id: str,
        tgt_node_id: str,
        src_node_type: str,
        edge_type: str,
        tgt_node_type: str,
    ) -> Dict:
        try:
            result = self._connection.getEdges(
                src_node_type, src_node_id, edge_type, tgt_node_type, tgt_node_id
            )
            if isinstance(result, List) and result:
                return result[0].get("attributes", {})
            else:
                raise TypeError(f"Unsupported type for result: {type(result)}")
        except Exception as e:
            logger.error(
                f"Error retrieving edge from {src_node_id} to {tgt_node_id}: {e}"
            )
            return {}

    def _degree(self, node_id: str, node_type: str, edge_types: List | str) -> int:
        try:
            params = {
                "input": (node_id, node_type),
                "edge_types": edge_types,
            }
            result = self._connection.runInstalledQuery("api_degree", params)
            if result:
                return result[0].get("degree", 0)
        except Exception as e:
            logger.error(f"Error retrieving degree of node {node_id}: {e}")
        return 0

    def _get_node_edges(
        self,
        node_id: str,
        node_type: str,
        edge_types: List | str,
        num_edge_samples: int = 1000,
    ) -> List:
        try:
            params = {
                "input": (node_id, node_type),
                "edge_types": edge_types,
                "num_edge_samples": num_edge_samples,
            }
            result = self._connection.runInstalledQuery("api_get_node_edges", params)
            if result:
                return result[0].get("edges")
        except Exception as e:
            logger.error(f"Error retrieving edges for node {node_id}: {e}")
        return []

    def _get_nodes(
        self,
        node_type: str,
        filter_expression: Optional[str] = None,
        return_attributes: Optional[str | List[str]] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame | None:
        """
        High-level function to retrieve nodes with multiple parameters.
        Converts parameters into a NodeSpec and delegates to `_get_nodes_from_spec`.
        """
        spec = NodeSpec(
            node_type=node_type,
            filter_expression=filter_expression,
            return_attributes=return_attributes,
            limit=limit,
        )
        return self._get_nodes_from_spec(spec)

    def _get_nodes_from_spec(self, spec: NodeSpec) -> pd.DataFrame | None:
        """
        Core function to retrieve nodes based on a NodeSpec object.
        """
        gsql_script = self._create_gsql_get_nodes(self.name, spec)
        try:
            result = self._connection.runInterpretedQuery(gsql_script)
            if not result or not isinstance(result, list):
                return None
            nodes = result[0].get("Nodes")
            if not nodes or not isinstance(nodes, list):
                return None
            df = pd.DataFrame(pd.json_normalize(nodes))
            if df.empty:
                return None
            attribute_columns = [
                col for col in df.columns if col.startswith("attributes.")
            ]
            if spec.return_attributes is None:
                rename_map = {
                    col: col.replace("attributes.", "") for col in attribute_columns
                }
                reordered_columns = df.columns
            else:
                rename_map = {
                    f"attributes.{attr}": attr for attr in spec.return_attributes
                }
                reordered_columns = [
                    attr
                    for attr in spec.return_attributes
                    if attr in rename_map.values()
                ]
            df.rename(columns=rename_map, inplace=True)
            drop_columns = [col for col in ["v_id", "v_type"] if col in df.columns]
            df.drop(columns=drop_columns, inplace=True)
            remaining_columns = [
                col for col in df.columns if col not in reordered_columns
            ]
            return pd.DataFrame(df[reordered_columns + remaining_columns])
        except Exception as e:
            logger.error(f"Error retrieving nodes for type {spec.node_type}: {e}")
        return None

    def _get_neighbors(
        self,
        start_nodes: str | List[str],
        start_node_type: str,
        edge_types: Optional[str | List[str]] = None,
        target_node_types: Optional[str | List[str]] = None,
        filter_expression: Optional[str] = None,
        return_attributes: Optional[str | List[str]] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame | None:
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
        return self._get_neighbors_from_spec(spec)

    def _get_neighbors_from_spec(self, spec: NeighborSpec) -> pd.DataFrame | None:
        """
        Core function to retrieve neighbors based on a NeighborSpec object.
        """
        gsql_script, params = self._create_gsql_get_neighbors(self.name, spec)
        try:
            result = self._connection.runInterpretedQuery(gsql_script, params)
            if not result or not isinstance(result, list):
                return None
            neighbors = result[0].get("Neighbors")
            if not neighbors or not isinstance(neighbors, list):
                return None
            df = pd.DataFrame(pd.json_normalize(neighbors))
            if df.empty:
                return None
            attribute_columns = [
                col for col in df.columns if col.startswith("attributes.")
            ]
            if spec.return_attributes is None:
                rename_map = {
                    col: col.replace("attributes.", "") for col in attribute_columns
                }
                reordered_columns = df.columns
            else:
                rename_map = {
                    f"attributes.{attr}": attr for attr in spec.return_attributes
                }
                reordered_columns = [
                    attr
                    for attr in spec.return_attributes
                    if attr in rename_map.values()
                ]
            df.rename(columns=rename_map, inplace=True)
            drop_columns = [col for col in ["v_id", "v_type"] if col in df.columns]
            df.drop(columns=drop_columns, inplace=True)
            remaining_columns = [
                col for col in df.columns if col not in reordered_columns
            ]
            return pd.DataFrame(df[reordered_columns + remaining_columns])
        except Exception as e:
            logger.error(
                f"Error retrieving neighbors for node(s) {spec.start_nodes}: {e}"
            )
        return None

    def _check_graph_exists(self) -> bool:
        """Check if the specified graph name exists in the gsql_script."""
        result = self._connection.gsql(f"USE Graph {self.name}")
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
    def _create_gsql_graph_schema(schema_config: GraphSchema) -> str:
        # Extracting node attributes
        node_definitions = []
        for node_name, node_schema in schema_config.nodes.items():
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
        for edge_name, edge_schema in schema_config.edges.items():
            edge_attr_str = ", ".join(
                [
                    f"{attribute_name} {attribute_schema.data_type.value}"
                    for attribute_name, attribute_schema in edge_schema.attributes.items()
                ]
            )

            # Construct the edge definition, with conditional attribute string and direction
            edge_type_str = "DIRECTED" if edge_schema.is_directed_edge else "UNDIRECTED"
            reverse_edge_clause = (
                f' WITH REVERSE_EDGE="reverse_{edge_name}"'
                if edge_schema.is_directed_edge
                else ""
            )

            edge_definitions.append(
                f"ADD {edge_type_str} EDGE {edge_name}(FROM {edge_schema.from_node_type}, TO {edge_schema.to_node_type}"
                + (f", {edge_attr_str}" if edge_attr_str else "")
                + f"){reverse_edge_clause};"
            )

        # Generating the full schema string
        graph_name = schema_config.graph_name
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
"""
        return gsql_script.strip()

    def _create_gsql_load_data(self, loading_job_config: LoadingJobConfig) -> str:
        # Define file paths for each file in config with numbered file names
        files = loading_job_config.files
        define_files = [
            f'DEFINE FILENAME {file.file_alias}{" = " + f"\"{file.file_path}\"" if file.file_path else ""};'
            for file in files
        ]

        # Build LOAD statements for each file
        load_statements = []
        for file in files:
            file_alias = file.file_alias
            csv_options = file.csv_parsing_options
            quote = csv_options.quote

            # Construct the USING clause
            using_clause = (
                f'USING SEPARATOR="{csv_options.separator}", HEADER="{csv_options.header}", EOL="{csv_options.EOL}"'
                + (f', QUOTE="{quote.value}"' if quote else "")
                + ";"
            )

            mapping_statements = []
            # Generate LOAD statements for each node mapping
            for mapping in file.node_mappings or []:
                # Find the corresponding NodeSchema by matching the target name with node_type keys
                node_type = mapping.target_name
                node_schema = self.schema_config.nodes.get(node_type)

                if not node_schema:
                    raise ValueError(
                        f"Node type '{node_type}' does not exist in the graph."
                    )

                # Construct attribute mappings in the order defined in NodeSchema
                attributes_ordered = []
                for attr_name in node_schema.attributes:
                    # Get the column name if it exists in mapping; otherwise, check for a default
                    column_name = mapping.attribute_column_mappings.get(attr_name)
                    if column_name is not None:
                        # Format and add the mapped column name
                        attributes_ordered.append(self._format_column_name(column_name))
                    else:
                        # Add a placeholder for missing attribute
                        attributes_ordered.append("_")

                # Join the ordered attributes for the LOAD statement
                attr_mappings = ", ".join(attributes_ordered)

                # Add the vertex LOAD statement
                mapping_statements.append(
                    f"TO VERTEX {node_type} VALUES({attr_mappings})"
                )

            # Generate LOAD statements for each edge mapping
            for mapping in file.edge_mappings or []:
                # Find the corresponding NodeSchema by matching the target name with node_type keys
                edge_type = mapping.target_name
                edge_schema = self.schema_config.edges.get(edge_type)
                if not edge_schema:
                    raise ValueError(
                        f"Edge type '{edge_type}' does not exist in the graph."
                    )

                # Format source and target node columns
                source_node = self._format_column_name(mapping.source_node_column)
                target_node = self._format_column_name(mapping.target_node_column)

                # Construct attribute mappings in the order defined in EdgeSchema
                attributes_ordered = []
                for attr_name in edge_schema.attributes:
                    # Get the column name if it exists in mapping; otherwise, check for a default
                    column_name = mapping.attribute_column_mappings.get(attr_name)
                    if column_name is not None:
                        # Format and add the mapped column name
                        attributes_ordered.append(self._format_column_name(column_name))
                    else:
                        # Add a placeholder for missing attribute
                        attributes_ordered.append("_")

                # Join the ordered attributes for the LOAD statement
                attr_mappings = ", ".join(
                    [source_node, target_node] + attributes_ordered
                )

                # Add the edge LOAD statement
                mapping_statements.append(
                    f"TO EDGE {edge_type} VALUES({attr_mappings})"
                )

            # Combine file-specific LOAD statements and the USING clause
            load_statements.append(
                f"LOAD {file_alias}\n    "
                + ",\n    ".join(mapping_statements)
                + f"\n    {using_clause}"
            )

        # Combine DEFINE FILENAME statements and LOAD statements into the loading job definition
        define_files_section = "  # Define files\n  " + "\n  ".join(define_files)
        load_section = "  # Load vertices and edges\n  " + "\n  ".join(load_statements)

        # Create the final GSQL script with each section layered
        loading_job_name = loading_job_config.loading_job_name
        gsql_script = f"""
# 1. Use graph
USE GRAPH {self.name}

# 2. Create loading job
CREATE LOADING JOB {loading_job_name} FOR GRAPH {self.name} {{
{define_files_section}

{load_section}
}}

# 3. Run loading job
RUN LOADING JOB {loading_job_name}

# 4. Drop loading job
DROP JOB {loading_job_name}
"""
        return gsql_script.strip()

    @staticmethod
    def _create_gsql_install_queries(graph_name: str):
        gsql_script = f"""
USE GRAPH {graph_name}
{CREATE_QUERY_API_DEGREE}
{CREATE_QUERY_API_GET_NODE_EDGES}
INSTALL QUERY *
"""
        return gsql_script.strip()

    @staticmethod
    def _create_gsql_get_nodes(graph_name: str, spec: NodeSpec) -> str:
        """
        Core function to generate a GSQL query based on a NodeSpec object.
        """
        node_type = spec.node_type
        filter_expression_str = (
            f"WHERE {spec.filter_expression}" if spec.filter_expression else ""
        )
        limit_clause = f"LIMIT {spec.limit}" if spec.limit else ""
        return_attributes = spec.return_attributes or []

        # Generate the base query
        query = f"""
INTERPRET QUERY() FOR GRAPH {graph_name} {{
  Nodes = {{{node_type}.*}};
"""
        # Add SELECT block only if filter or limit is specified
        if filter_expression_str or limit_clause:
            query += """  Nodes =
    SELECT s
    FROM Nodes:s
"""
            if filter_expression_str:
                query += f"    {filter_expression_str}\n"
            if limit_clause:
                query += f"    {limit_clause}\n"
            query += "  ;\n"

        # Add PRINT statement
        if return_attributes:
            prefixed_attributes = ",\n    ".join(
                [f"Nodes.{attr} AS {attr}" for attr in return_attributes]
            )
            query += f"  PRINT Nodes[\n    {prefixed_attributes}\n  ];"
        else:
            query += "  PRINT Nodes;"

        query += "\n}"
        return query.strip()

    @staticmethod
    def _create_gsql_get_neighbors(
        graph_name: str, spec: NeighborSpec
    ) -> Tuple[str, str]:
        """
        Core function to generate a GSQL query based on a NeighborSpec object.
        """
        # Normalize fields to lists
        params = "&".join(
            [
                f"start_nodes={node}"
                for node in (
                    [spec.start_nodes]
                    if isinstance(spec.start_nodes, str)
                    else spec.start_nodes
                )
            ]
        )
        edge_types = (
            [spec.edge_types] if isinstance(spec.edge_types, str) else spec.edge_types
        )
        target_node_types = (
            [spec.target_node_types]
            if isinstance(spec.target_node_types, str)
            else spec.target_node_types
        )
        return_attributes = (
            [spec.return_attributes]
            if isinstance(spec.return_attributes, str)
            else spec.return_attributes
        )

        # Handle filter expression
        filter_expression = spec.filter_expression
        filter_expression_str = (
            filter_expression if isinstance(filter_expression, str) else None
        )

        # Prepare components
        start_node_type = spec.start_node_type
        edge_types_str = (
            f"(({ '|'.join(edge_types or []) }):e)"
            if edge_types and len(edge_types) > 1
            else f"({ '|'.join(edge_types or []) }:e)"
            if edge_types
            else "(:e)"
        )
        target_node_types_str = (
            f"(({ '|'.join(target_node_types or []) }))"
            if target_node_types and len(target_node_types) > 1
            else f"{ '|'.join(target_node_types or []) }"
        )

        where_clause = (
            f"    WHERE {filter_expression_str}" if filter_expression_str else ""
        )
        limit_clause = f"    LIMIT {spec.limit}" if spec.limit else ""

        # Generate the query
        query = f"""
INTERPRET QUERY(
  SET<VERTEX<{start_node_type}>> start_nodes
) FOR GRAPH {graph_name} {{
  Nodes = {{start_nodes}};
  Neighbors =
    SELECT t
    FROM Nodes:s -{edge_types_str}- {target_node_types_str}:t
"""
        if where_clause:
            query += f"{where_clause}\n"
        if limit_clause:
            query += f"{limit_clause}\n"

        query += "  ;\n"

        # Add PRINT statement
        if return_attributes:
            prefixed_attributes = ",\n    ".join(
                [f"Neighbors.{attr} AS {attr}" for attr in return_attributes]
            )
            query += f"  PRINT Neighbors[\n    {prefixed_attributes}\n  ];"
        else:
            query += "  PRINT Neighbors;"

        query += "\n}"
        return (query.strip(), params)

    @staticmethod
    def _format_column_name(column_name: str | int | None) -> str:
        """Format column names as $number, $"variable", or _ for empty names."""
        if column_name is None:
            return "_"
        if isinstance(column_name, int):
            return f"${column_name}"
        if isinstance(column_name, str) and column_name.isidentifier():
            return f'$"{column_name}"'
        # Return the original name as string if it doesn't match any of the specified formats
        return str(column_name)
