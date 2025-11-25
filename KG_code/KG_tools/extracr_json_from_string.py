import re
import json
# 从一大串字符串中“抠出”最外层 JSON
def extract_json_from_string(s: str) -> str:
    """
    在字符串中找到第一个 { 到 最后一个 } 之间的内容，
    认为这是 JSON 对象，返回这段子串。
    """
    s = s.strip()
    # 用正则搜索最外层的大括号
    m = re.search(r'\{.*\}', s, re.S)
    if not m:
        raise ValueError("在模型输出中没有找到 JSON 对象，原始内容为：\n" + s)
    return m.group(0)