# Introduction to TigerGraphX

## What is TigerGraphX?

**TigerGraphX** is a high-level Python library designed to make working with graph databases, graph analytics, and **GraphRAG (Graph-Retrieval Augmented Generation)** workflows simpler and more efficient. Inspired by the usability of **NetworkX** and the power of **TigerGraph**, TigerGraphX empowers Python developers to harness the power of graphs without the steep learning curve of graph query languages like GSQL or Cypher.

Whether you’re managing knowledge graphs, performing vector search, or integrating large language models (LLMs) for GraphRAG workflows, TigerGraphX provides a unified interface to streamline your development process.

---

## Key Features

TigerGraphX combines the best of Python and graph technologies with the following features:

### **1. Schema Management**
Define and modify graph schemas effortlessly using YAML, JSON, or Python dictionaries—no GSQL required. TigerGraphX allows you to:
- Add, remove, or modify vertices and edges.
- Specify attributes for schema elements.

### **2. Data Loading**
Load data efficiently into TigerGraph with built-in support for:
- **Parquet files** for high-efficiency workflows.
- Automatic loading jobs for seamless integration.

### **3. Graph Library Interface**
Simplify graph management with Python-native APIs for:
- **CRUD operations** on nodes and edges.
- Multi-hop traversals.
- Reporting and analytics.

### **4. Graph Query Interface**
Perform complex queries without worrying about query syntax:
- Query results are returned as **DataFrames** for easier integration into Python analytics workflows.

### **5. Vector Search**
Enable AI-powered applications with:
- Integration with vector databases like **LanceDB**.
- Top-K entity retrieval based on vector embeddings.

### **6. LLM Integration**
TigerGraphX is built for GraphRAG workflows:
- Supports **token-aware context building** for LLMs.
- Facilitates hybrid retrieval using graph, semantic, and vector-based methods.

---

## Why Use TigerGraphX?

TigerGraphX simplifies graph database complexity, making it easy to:
- **Build hybrid applications** with graph and vector data.
- **Leverage LLMs** for intelligent applications powered by contextual data.
- **Adopt GraphRAG workflows** for advanced use cases.

It bridges multiple technological domains:
- **Graph Databases**: Schema management, CRUD operations, and multi-hop queries.
- **Vector Databases**: Integration with LanceDB and other tools.
- **LLMs**: Token-aware workflows for enhanced AI applications.

---

## How TigerGraphX Powers GraphRAG Workflows

GraphRAG combines **retrieval-augmented generation (RAG)** with the power of graph databases. With TigerGraphX, you can:
1. **Prepare the Data**: Design graph schemas and load structured and vector data into TigerGraph.
2. **Retrieve Relevant Context**: Combine graph queries, vector embeddings, and semantic search for hybrid retrieval.
3. **Build Context**: Construct token-aware context for use with LLMs.
4. **Generate Outputs**: Query LLMs with enriched context for advanced applications.

---

## Next Steps

- [Getting Started](getting_started/installation.md): Learn how to install and set up TigerGraphX.
- [GraphRAG Overview](graphrag/overview.md): Explore how TigerGraphX integrates with GraphRAG workflows.
- [API Reference](reference/api.md): Dive into the TigerGraphX API.

Unlock the potential of graphs and vectors with **TigerGraphX** today!
