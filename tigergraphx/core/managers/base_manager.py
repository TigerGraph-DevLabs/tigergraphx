from tigergraphx.core.graph_context import GraphContext


class BaseManager:
    def __init__(self, context: GraphContext):
        self._connection = context.connection
        self._graph_schema = context.graph_schema
