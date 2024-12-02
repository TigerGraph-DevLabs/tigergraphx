import logging

from .base_manager import BaseManager

from tigergraphx.core.graph_context import GraphContext
from tigergraphx.config import (
    LoadingJobConfig,
    GraphSchema,
)


logger = logging.getLogger(__name__)


class DataManager(BaseManager):
    def __init__(self, context: GraphContext):
        super().__init__(context)

    def load_data(self, loading_job_config: LoadingJobConfig):
        logger.info(
            "Starting data loading for job: %s", loading_job_config.loading_job_name
        )
        gsql_script = self._create_gsql_load_data(
            loading_job_config, self._graph_schema
        )

        result = self._connection.gsql(gsql_script)
        if "LOAD SUCCESSFUL for loading jobid" not in result:
            error_msg = f"Data loading failed. GSQL response: {result}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def _create_gsql_load_data(
        self,
        loading_job_config: LoadingJobConfig,
        graph_schema: GraphSchema,
    ) -> str:
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
                node_schema = graph_schema.nodes.get(node_type)

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
                edge_schema = graph_schema.edges.get(edge_type)
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
USE GRAPH {graph_schema.graph_name}

# 2. Create loading job
CREATE LOADING JOB {loading_job_name} FOR GRAPH {graph_schema.graph_name} {{
{define_files_section}

{load_section}
}}

# 3. Run loading job
RUN LOADING JOB {loading_job_name}

# 4. Drop loading job
DROP JOB {loading_job_name}
"""
        logger.debug("Generated GSQL script: %s", gsql_script)
        return gsql_script.strip()

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
