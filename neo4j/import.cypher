CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (n:Entity) REQUIRE n.id IS UNIQUE;

LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS row
MERGE (n:Entity {id: row.id})
SET n.type = row.type,
    n.canonical = row.canonical,
    n.normalized = row.normalized,
    n.status = row.status;

LOAD CSV WITH HEADERS FROM 'file:///edges.csv' AS row
MATCH (a:Entity {id: row.source})
MATCH (b:Entity {id: row.target})
MERGE (a)-[r:RELATED {id: row.id}]->(b)
SET r.type = row.type,
    r.confidence = toFloat(row.confidence),
    r.source_file = row.source_file,
    r.source_row = toInteger(row.source_row);
