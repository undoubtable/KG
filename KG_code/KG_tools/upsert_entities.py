# 写入实体
def upsert_entities(tx, entities):
    """
    把大模型返回的 entities 写进 Neo4j。
    每个实体对应一个 :KGNode 节点，uid 作为唯一标识。
    结构假定为：
    {
      "uid": "Law:著作权法",
      "node_type": "Law",
      "name": "中华人民共和国著作权法",
      "extra": {...}
    }
    """
    query = """
    UNWIND $entities AS ent
    MERGE (n:KGNode {uid: ent.uid})
    SET n.node_type = ent.node_type,
        n.name      = ent.name
    SET n += ent.extra
    """
    tx.run(query, entities=entities)