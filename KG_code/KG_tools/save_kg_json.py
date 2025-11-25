import os
import json

def save_kg_json(kg: dict, output_dir: str, filename: str):
    """把 kg（Python 字典）保存为一个 .json 文件"""
    path = os.path.join(output_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(kg, f, ensure_ascii=False, indent=2)
    print(f"已保存到: {path}")