from neo4j import Transaction

def upsert_relations(tx: Transaction, relations):
    """
    把 relations 写成 Neo4j 里的关系。
    每条关系结构:
    {
      "from_uid": "Law:著作权法",
      "to_uid":   "Article:第10条",
      "rel_type": "HAS_ARTICLE"
    }

    根据 rel_type 动态创建关系类型：
    (a)-[:HAS_ARTICLE]->(b)
    (a)-[:REQUIRES_DOC]->(b)
    ...
    """
    for rel in relations:
        from_uid = rel["from_uid"]
        to_uid   = rel["to_uid"]
        rel_type = rel["rel_type"]  # 例如 "HAS_ARTICLE"

        # 用反引号包裹，避免 rel_type 中有特殊字符时报错
        cypher = f"""
        MATCH (a:KGNode {{uid: $from_uid}})
        MATCH (b:KGNode {{uid: $to_uid}})
        MERGE (a)-[r:`{rel_type}`]->(b)
        SET r.rel_type = $rel_type
        """

        tx.run(cypher, from_uid=from_uid, to_uid=to_uid, rel_type=rel_type)
