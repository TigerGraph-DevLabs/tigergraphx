CREATE_QUERY_API_DEGREE = """
CREATE OR REPLACE QUERY api_degree(
  VERTEX input,
  SET<STRING> edge_types
) SYNTAX V1 {
  SumAccum<INT> @@sum_degree;
  Nodes = {input};
  IF edge_types.size() == 0 THEN
    Nodes =
        SELECT s
        FROM Nodes:s -(ANY)- :t
        ACCUM  @@sum_degree += 1
    ;
  ELSE
    Nodes =
        SELECT s
        FROM Nodes:s -(edge_types)- :t
        ACCUM  @@sum_degree += 1
    ;
  END;
  PRINT @@sum_degree AS degree;
}
"""
CREATE_QUERY_API_GET_NODE_EDGES = """
CREATE OR REPLACE QUERY api_get_node_edges(
  VERTEX input,
  SET<STRING> edge_types,
  UINT num_edge_samples = 1000
) SYNTAX V1 {
  SetAccum<EDGE> @@set_edge;
  Nodes = {input};
  IF edge_types.size() == 0 THEN
    Nodes =
        SELECT t
        FROM Nodes:s -(ANY:e)- :t
        SAMPLE num_edge_samples EDGE WHEN s.outdegree(edge_types) > num_edge_samples
        ACCUM @@set_edge += e
    ;
  ELSE
    Nodes =
        SELECT t
        FROM Nodes:s -(edge_types:e)- :t
        SAMPLE num_edge_samples EDGE WHEN s.outdegree(edge_types) > num_edge_samples
        ACCUM @@set_edge += e
    ;
  END;
  PRINT @@set_edge AS edges;
}
"""

