from openai import OpenAI
import re
import json
import os
from neo4j import GraphDatabase

client = OpenAI(
    base_url="https://ai.gitee.com/v1",
    api_key="DUQFR61KA8QLDVEQPGJKBXYSL2DXMPST1FM98Y1L",
    default_headers={"X-Failover-Enabled":"true"},
)

# Load prompt from text file
def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

SYSTEM_PROMPT = load_text("law_prompt.txt")  # 这里用你的prompt .txt

# 抽取知识图谱
# -------- 1. 从整串字符串中抠出最外层 JSON --------
def extract_json_from_string(s: str) -> str:
    """
    用大括号配平的方式，从字符串中提取第一个完整 JSON 对象。
    """
    s = s.strip()
    start = s.find("{")
    if start == -1:
        raise ValueError("未找到 '{'，模型输出为：\n" + s)

    depth = 0
    end = None
    for i, ch in enumerate(s[start:], start=start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break

    if end is None:
        raise ValueError("大括号未配平，模型输出：\n" + s)

    return s[start:end+1]


# -------- 2. 用流式的方式调用 DeepSeek-R1，抽取知识图谱 --------
def extract_kg_stream(text: str):
    response = client.chat.completions.create(
        model="DeepSeek-R1",
        stream=True,                      # 保留流式
        response_format={"type": "json_object"},
        max_tokens=1500,
        temperature=0.2,
        top_p=0.7,
        extra_body={
            "top_k": 50,
            "enable_reasoning": False,
        },
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT    # law_prompt.txt
            },
            {
                "role": "user",
                "content": f"请从以下文本中抽取知识图谱实体和关系，并按提示返回 JSON：\n\n{text}"
            }
        ],
    )

    full_json_str = ""
    print("Response:")

    # 流式逐块接收
    for chunk in response:
        if not chunk.choices:
            continue

        delta = chunk.choices[0].delta

        # 推理内容（思考过程），只打印
        if hasattr(delta, "reasoning_content") and delta.reasoning_content:
            print(f"\033[90m{delta.reasoning_content}\033[0m", end="", flush=True)

        # 真正的 JSON 内容
        elif delta.content:
            full_json_str += delta.content
            print(delta.content, end="", flush=True)

    print("\n\n=== Raw streamed content ===")
    print(full_json_str)

    # 1）抠出 JSON 子串
    json_str = extract_json_from_string(full_json_str)
    print("\n=== Extracted JSON string ===")
    print(json_str)

    # 2）解析 JSON
    kg_raw = json.loads(json_str)
    print("\n➡️ 解析后的原始 JSON：")
    print(kg_raw)

    # -------- 3. 统一整理成 { "entities": [...], "relations": [...] } --------

    entities = []
    relations = []

    # 情况 A：根上就是 entities / relations（完全符合 law_prompt.txt）
    if isinstance(kg_raw, dict) and "entities" in kg_raw and "relations" in kg_raw:
        entities = kg_raw["entities"]
        relations = kg_raw["relations"]

    # 情况 B：有 content 且 content 是 dict（例如 {"content": {"entities": [...], "relations": [...]}})
    elif isinstance(kg_raw, dict) and "content" in kg_raw and isinstance(kg_raw["content"], dict):
        content = kg_raw["content"]
        entities = content.get("entities", []) or []
        relations = content.get("relations", []) or []

    # 情况 C：content 是字符串（例如 {"content": "保护发明创造的专利权..." }）
    elif isinstance(kg_raw, dict) and "content" in kg_raw and isinstance(kg_raw["content"], str):
        print("⚠️ 模型输出 content 为原文字符串，未识别出实体/关系，返回空 KG。")
        entities = []
        relations = []

    # 情况 D：模型只吐了一个实体（uid/node_type/name/...）
    elif isinstance(kg_raw, dict) and all(k in kg_raw for k in ("uid", "node_type")):
        entities = [kg_raw]
        relations = []

    # 情况 E：其它完全不符合结构的情况 → 不再 raise，而是给个空 KG
    else:
        print("⚠️ 模型输出不含任何 KG 结构，返回空 KG。")
        entities = []
        relations = []

    # 保证这两个一定是列表
    if entities is None:
        entities = []
    if relations is None:
        relations = []

    kg_data = {
        "entities": entities,
        "relations": relations,
    }

    print("\n✅ 最终标准化后的 KG JSON：")
    print(json.dumps(kg_data, ensure_ascii=False, indent=2))

    return kg_data

test_text = """
第十条 著作权包括下列权利：
（一）发表权，即决定作品是否公之于众的权利；
（二）署名权，即表明作者身份，在作品上署名的权利；
（三）修改权，即修改或者授权他人修改作品的权利；
（四）保护作品完整权。
"""

kg = extract_kg_stream(test_text)
print("=== KG JSON 预览 ===")
print(json.dumps(kg, ensure_ascii=False, indent=2))

OUTPUT_DIR = "D:\\Desktop\\现代软件工程\\作业\\实践营\\KG\\KG_files\\KG_json_test"
# 如果目录不存在就创建
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_kg_json(kg: dict, output_dir: str, filename: str):
    """把 kg（Python 字典）保存为一个 .json 文件"""
    path = os.path.join(output_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(kg, f, ensure_ascii=False, indent=2)
    print(f"已保存到: {path}")

# 从 kg 里取出条文 uid 或 name，当作文件名一部分
article_uid = None
for ent in kg["entities"]:
    if ent["node_type"] == "Article":
        article_uid = ent["uid"]  # 比如 "Article:第10条"
        break

if article_uid is None:
    filename = "unknown_article.json"
else:
    # 简单处理下文件名里的冒号
    safe_uid = article_uid.replace(":", "_")
    filename = f"{safe_uid}.json"   # Article_第10条.json

save_kg_json(kg, OUTPUT_DIR, filename)   
print("✅ KG 保存完成！")

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "20011127"  # 换成你 Neo4j Desktop 里设置的

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
print("Neo4j driver initialized.")

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "20011127"))
with driver.session() as session:
    result = session.run("RETURN 1 AS test")
    print(result.single())

# 确保每个 KGNode 的 uid 唯一（只需要跑一次）
with driver.session() as session:
    session.run("""
    CREATE CONSTRAINT kgnode_uid_unique IF NOT EXISTS
    FOR (n:KGNode)
    REQUIRE n.uid IS UNIQUE
    """)
print("Constraint created (if it didn't exist).")

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

# 写入关系
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

print("upsert_entities & upsert_relations 已定义。")

entities = kg["entities"]
relations = kg["relations"]

with driver.session() as session:
    session.execute_write(upsert_entities, entities)
    session.execute_write(upsert_relations, relations)

print("当前这条法条已写入 Neo4j。")

JSON_DIR = "D:\\Desktop\\现代软件工程\\作业\\实践营\\KG\\KG_files\\KG_json_test"  # ← 你的目录

def import_json_to_neo4j(json_dir):
    files = [f for f in os.listdir(json_dir) if f.endswith(".json")]
    print("检测到 JSON 文件：", files)

    for filename in files:
        path = os.path.join(json_dir, filename)
        print(f"\n>>> 处理文件：{path}")

        with open(path, "r", encoding="utf-8") as f:
            kg = json.load(f)

        entities = kg["entities"]
        relations = kg["relations"]

        with driver.session() as session:
            session.execute_write(upsert_entities, entities)
            session.execute_write(upsert_relations, relations)

    print("\n🎉 所有 JSON 文件已成功写入 Neo4j！")

import_json_to_neo4j(JSON_DIR)