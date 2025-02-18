from tigergraphx import Graph

graphs_to_drop = [
    "LightRAG",
    "Vector_chunks",
    "Vector_entities",
    "Vector_relationships",
]
for graph_name in graphs_to_drop:
    try:
        G = Graph.from_db(graph_name)
        G.drop_graph()
    except Exception as e:
        print(f"Error message: {str(e)}")
