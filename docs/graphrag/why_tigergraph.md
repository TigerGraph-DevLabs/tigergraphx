# Why TigerGraph for GraphRAG?

## Unlocking the Full Potential of GraphRAG

TigerGraph is the ideal platform for **GraphRAG (Graph-Retrieval Augmented Generation)** workflows, offering unmatched scalability, performance, and flexibility. Its robust support for hybrid retrieval, real-time graph queries, and seamless integration with vector data makes it the foundation for building advanced applications powered by graph databases and large language models (LLMs).

---

## Key Advantages of TigerGraph for GraphRAG

### **1. Scalability and Performance**
TigerGraph is designed for handling massive datasets with ease. Its high-speed query engine enables:
- **Efficient Multi-Hop Traversals**: Execute queries across multiple hops in milliseconds.
- **Real-Time Performance**: Support real-time decision-making in GraphRAG workflows, even at scale.

Whether you're working with large knowledge graphs or complex hybrid retrieval tasks, TigerGraph delivers reliable, high-performance solutions.

---

### **2. Unified Support for Graph and Vector Data**
TigerGraph integrates structured graph data and vector embeddings, allowing you to:
- Store and query vectors alongside traditional graph attributes.
- Perform hybrid retrieval that combines graph traversal with vector similarity search.

This unified approach ensures compatibility with GraphRAG workflows, enabling semantic and contextual retrieval for LLMs.

---

### **3. Cost-Effective Solutions**
TigerGraph optimizes both storage and query execution, reducing computational overhead. Key cost-saving features include:
- **Optimized Storage**: Efficiently manage graph and vector data.
- **Query Efficiency**: Minimize infrastructure costs through high-speed query execution.

These advantages make TigerGraph a cost-effective option for building scalable GraphRAG applications.

---

### **4. Hybrid Retrieval Made Easy**
TigerGraph simplifies hybrid retrieval by combining:
- **Structured Queries**: Use graph traversal to fetch specific relationships and nodes.
- **Semantic Search**: Retrieve context based on semantic relevance.
- **Vector Similarity**: Leverage vector embeddings for nearest-neighbor searches.

#### Example Hybrid Retrieval Workflow
```gsql
CREATE OR REPLACE QUERY hybrid_retrieval (List<float> embedding, int k) {
  Nodes = TopKVectorSearch({Entity.embedding}, embedding, k);

  Results =
    SELECT t
    FROM Nodes:s -(relationship:e)- :t;

  PRINT Results;
}
```

---

### **5. Flexibility and Integration**
TigerGraph supports hybrid retrieval strategies across various workflows:
- **Structured Data Queries**: Define schemas and perform CRUD operations on nodes and edges.
- **Vector Search**: Retrieve top-K similar objects based on vector embeddings.
- **LLM Integration**: Build token-aware contexts for seamless interaction with large language models.

Whether you’re using GSQL for fine-grained control or TigerGraphX for Python-native workflows, TigerGraph adapts to your needs.

---

## How TigerGraph Supports GraphRAG Workflows

TigerGraph is built to enable advanced GraphRAG workflows, including:

1. **Schema Design**: Define graph schemas with nodes, edges, and attributes tailored to your application.
2. **Data Preparation and Loading**: Use TigerGraphX to load data from formats like Parquet for scalable processing.
3. **Real-Time Hybrid Retrieval**: Combine structured queries, semantic search, and vector similarity.
4. **Context Building for LLMs**: Retrieve relevant graph data and format it for token-aware LLM workflows.
5. **LLM Integration**: Pass rich, structured context to LLMs for improved response generation.

---

## Why Choose TigerGraph for GraphRAG?

### **Comprehensive Capabilities**
TigerGraph bridges multiple technological domains:
- **Graph Databases**: Efficiently manage schemas, relationships, and attributes.
- **Vector Search**: Retrieve top-K entities using vector similarity.
- **LLM Integration**: Build contextual applications powered by graph and vector data.

### **Developer-Friendly Tools**
TigerGraph provides flexibility for both GSQL experts and Python developers:
- **GSQL**: Write powerful graph queries with complete control.
- **TigerGraphX**: Use intuitive Python APIs for hybrid retrieval and schema management.

### **Seamless Ecosystem Integration**
TigerGraph integrates with:
- **Vector Databases**: Store and query embeddings alongside graph data.
- **LLMs**: Build advanced GraphRAG workflows with context-aware query processing.

---

## Next Steps

1. Learn about GraphRAG in the [GraphRAG Overview](overview.md).
2. Explore a practical example in [Microsoft GraphRAG](msft_graphrag.md).
3. Dive into advanced [API Reference](../reference/api.md) features.

---

TigerGraph’s robust capabilities make it the ultimate platform for scalable, efficient, and intelligent GraphRAG workflows. Start building with TigerGraph today!
