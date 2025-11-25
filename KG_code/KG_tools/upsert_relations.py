def upsert_relations(tx, relations):
    """
    把 relations 写成 Neo4j 里的关系。
    关系结构假定为：
    {
      "from_uid": "Law:著作权法",
      "to_uid":   "Article:第10条",
      "rel_type": "HAS_ARTICLE"
    }
    这里统一用关系类型 :REL，具体类型存在 r.rel_type 属性里。
    """
    query = """
    UNWIND $relations AS rel
    MATCH (a:KGNode {uid: rel.from_uid})
    MATCH (b:KGNode {uid: rel.to_uid})
    MERGE (a)-[r:REL {rel_type: rel.rel_type}]->(b)
    """
    tx.run(query, relations=relations)
