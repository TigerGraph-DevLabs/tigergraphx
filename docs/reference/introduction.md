# Introduction

## Overview
The TigerGraphX project is organized into several top-level directories, each serving a distinct purpose within the codebase. The first-level package structure is as follows:

- **`core`**: Defines core components and the main graph-related functionality. This includes the `Graph` class, which provides a unified structure for handling both homogeneous and heterogeneous graphs. It offers a range of interfaces for performing various graph operations.
- **`vector_search`**: Implements vector-based search functionalities, including integration with vector databases and support for TigerGraph’s TigerVector feature. It also provides embedding utilities and search operations.
- **`llm`**: Focuses on large language model (LLM) integrations. This directory contains connectors for services like OpenAI as well as chat-related utilities.
- **`config`**: Contains configurations and settings used across the project. This includes database settings, query configurations, and settings for GraphRAG applications.
- **`graphrag`**: Houses logic related to the GraphRAG framework.
- **`pipelines`**: Provides components for processing data in a pipeline manner, such as handling Parquet files.
- **`utils`**: Offers various utilities and helper functions to streamline development tasks.

## Graph Class in TigerGraphX
The fundamental feature of TigerGraphX is a class named [Graph](01_core/graph.md). This class encapsulates the entire structure of a graph, including all nodes and edges defined by a set of node types and edge types. In other words, it supports heterogeneous graphs—allowing you to work with multiple types of nodes and multiple types of edges within the same graph.

You can create multiple instances of the `Graph` class, each identified by a unique graph name. The graph name serves as the identifier for that particular graph in TigerGraph. This design ensures isolation between graphs; when you create a new `Graph` instance with a different name, a completely separate graph is created within TigerGraph. No nodes or edges are shared between these graph instances, so each graph can be managed and queried independently.

The `Graph` class provides a rich interface that enables you to:

- **Define a Graph Schema and Create a Graph**:  
  Specify the schema—detailing the various node types, edge types, and their respective attributes—using flexible formats such as Python dictionaries, YAML, or JSON. The `Graph` class then uses this schema to create a new graph inside TigerGraph, ensuring that the structure adheres to your specified design.

- **Load Data into the Graph from Files**:  
  Once the graph schema is in place, import data into the graph from various file formats. This feature streamlines the data ingestion process and allows you to quickly populate your graph with nodes and edges.

- **Use the Graph Library Interface**:  
  Leverage a suite of functions and methods that are very similar to those provided by NetworkX, a popular Python library for graph processing, to perform common graph operations.

- **Use the Graph Query Interface**:  
  Execute complex graph queries with simplified Python-based methods. Query results are formatted as Pandas DataFrames, providing seamless integration with your analytics workflows.

- **Leverage Vector Search Capabilities**:  
  Enhance your graph analytics with integrated vector search functionality, enabling tasks like similarity searches and semantic queries directly within your graph.

To explore the extensive features of the Graph class, please refer to [Graph](01_core/graph.md).
