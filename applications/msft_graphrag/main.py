from .graphrag import GraphRAG, QueryParam


if __name__ == "__main__":
    graphrag = GraphRAG()

    param = QueryParam(mode="global")
    result = graphrag.query(
        query="Which companies are mentioned in the article?",
        param=param,
    )

    param = QueryParam(mode="local")
    result = graphrag.query(
        query="Which companies are mentioned in the article?",
        param=param,
    )

    print(result)
