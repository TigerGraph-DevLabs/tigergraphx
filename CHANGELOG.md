# Changelog

---
## 0.2.3
- feat: add support for output_type="List" in get_nodes, get_neighbors, and bfs

## 0.2.2
- feat: run RESTful APIs directly within TigerGraphX instead of using pyTigerGraph

## 0.2.1
- feat: add simple GraphRAG
- fix: correct the image link
- docs: add documentation for Supporting Simple GraphRAG

## 0.2.0
- docs: add copywrie to all Python files; add document LICENSE
- perf: importing fewer classes in `tigergraphx/__init__.py`
- feat: add support for TigerGraph APIs (ping, gsql, get_schema)
- feat: add support for TigerGraph APIs (run_interpreted_query)
- test: add unit test cases to class TigerGraphConnectionConfig
- fix: get_schema_from_db should consider vector attributes
- fix: add multi-edge support in `get_edge_data`
- feat: add method `bfs`
- feat: integrate Ragas for GraphRAG evaluation
- feat: add Ragas-based evaluation for LightRAG
- feat: add Ragas-based evaluation for MSFT GraphRAG
- perf: replace mkdocs-jupyter with jupyter nbconvert for faster ipynb-to-md conversion
- docs: add more examples in "TigerGraphX Quick Start: Using TigerGraph as Graph Database"
- docs: add more examples in "TigerGraphX Quick Start: Using TigerGraph as Vector Database"
- docs: add more examples in "TigerGraphX Quick Start: Using TigerGraph for Graph and Vector Database"
- docs: add evaluation section to LightRAG
- docs: add evaluation content to MSFT GraphRAG
- docs: add examples for query operations APIs
- docs: add BFS example by using method get_neighbors
- docs: add examples for vector operations APIs

## 0.1.12
- docs: add CHANGELOG.md
- fix: improve error messages and logging for schema creation
- feat: add aliases to TigerGraphConnectionConfig for environment variables
- fix: correct the order of attributes when getting schema from TigerGraph
- fix: consider the discriminators in multi-edges when getting schema from TigerGraph
- fix: improve error messages and logging for data loading
- fix: support for integer node IDs
- fix: add alias to `get_nodes` and `get_neighbors` methods
- docs: add filtering on multiple attributes in the `get_nodes` example
- fix: return empty DataFrame when the result is empty for `get_nodes` and `get_neighbors` methods
- fix: check the existence of the edge types for the method `degree`, `get_node_edges` and `get_neighbors`
- fix: convert the types of `edge_types` and `target_node_types` to `Set` in the `get_neighbors` method
- fix: ensure undirected edges are counted once in `number_of_edges` method
- docs: rewrite API Reference Introduction
- docs: add examples for schema operation APIs
- docs: add examples for data loading operation APIs
- docs: add examples for node operations APIs
- docs: add examples for edge operations APIs
- docs: add examples for statistics operations APIs

---

## 0.1.11
- Initial release.
