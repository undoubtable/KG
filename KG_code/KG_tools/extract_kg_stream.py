# 抽取知识图谱
import re
import json
# 从一大串字符串中“抠出”最外层 JSON
from openai import OpenAI
from KG_tools.load_prompt_text import load_prompt_text
from KG_tools.extracr_json_from_string import extract_json_from_string

client = OpenAI(
    base_url="https://ai.gitee.com/v1",
    api_key="DUQFR61KA8QLDVEQPGJKBXYSL2DXMPST1FM98Y1L",
    default_headers={"X-Failover-Enabled":"true"},
)

# Load prompt from text file

SYSTEM_PROMPT = load_prompt_text("law_prompt.txt")  # 这里用你的prompt .txt文件路径

def extract_kg_stream(text: str):
    response = client.chat.completions.create(
        model="DeepSeek-R1",
        stream=True,                      # ✅ 保留流式
        response_format={"type": "json_object"},  # ✅ 告诉服务端我们要 JSON
        max_tokens=10000, # 1500
        temperature=0.2,
        top_p=0.7,
        extra_body={
            "top_k": 50,
            "enable_reasoning": False,     # ✅ 关闭长时间推理，避免一直跑
        },
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"请从以下文本中抽取知识图谱实体和关系：\n\n{text}"
            }
        ],
    )

    full_json_str = ""
    print("Response:")

    # 5. 流式逐块接收
    for chunk in response:
        if len(chunk.choices) == 0:
            continue

        delta = chunk.choices[0].delta

        # 如果有推理内容（reasoning_content），只打印，不参与 JSON
        if hasattr(delta, "reasoning_content") and delta.reasoning_content:
            # 灰色输出思考过程，仅供你调试看
            print(f"\033[90m{delta.reasoning_content}\033[0m", end="", flush=True)

        # 真正的 JSON 字符串在 content 里
        elif delta.content:
            full_json_str += delta.content
            # 你也可以边打印边看模型在输出什么
            print(delta.content, end="", flush=True)

    print("\n\n=== Raw streamed content ===")
    print(full_json_str)

    # 6. 从整串内容里抠出 JSON 部分
    json_str = extract_json_from_string(full_json_str)
    print("\n=== Extracted JSON string ===")
    print(json_str)

    # 7. 解析为 Python dict
    kg_data = json.loads(json_str)
    print("\n✅ JSON 解析成功！")
    return kg_data