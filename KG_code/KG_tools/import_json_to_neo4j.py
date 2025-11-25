import os
import json
from neo4j import GraphDatabase
from KG_tools.upsert_entities import upsert_entities
from KG_tools.upsert_relations import upsert_relations

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "20011127")) # 请根据实际情况修改

def import_json_to_neo4j(json_dir):
    files = [f for f in os.listdir(json_dir) if f.endswith(".json")]
    print("检测到 JSON 文件：", files)

    for filename in files:
        path = os.path.join(json_dir, filename)
        print(f"\n>>> 处理文件：{path}")

        with open(path, "r", encoding="utf-8") as f:
            kg = json.load(f)

        entities = kg["content"]["entities"]
        relations = kg["content"]["relations"]

        with driver.session() as session:
            session.execute_write(upsert_entities, entities)
            session.execute_write(upsert_relations, relations)

    print("\n🎉 所有 JSON 文件已成功写入 Neo4j！")