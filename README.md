
[![中关村学院 GitHub 组织](https://img.shields.io/badge/Linked%20to-bjzgcai%20Org-blue?logo=github)](https://github.com/bjzgcai)

**项目简介**
- **名称**:: `KG` — 交互式知识图谱（KG）构建与导入工具集合。
- **用途**:: 从法律类 PDF/文本中抽取实体与关系，生成知识图谱 JSON，并可导入 Neo4j 进行可视化与查询。

**目录结构**
- **`KG_code/`**:: 主演示脚本与 Jupyter Notebook（如 `lawtest_for_pdf.ipynb`）。
- **`KG_tools/`**:: KG 抽取、保存与导入的工具模块（如 `extract_kg_stream.py`、`upsert_entities.py`、`import_json_to_neo4j.py` 等）。
- **`KG_files/`**:: 存放示例输入（PDF）与输出 JSON 的目录（例如 `KG_json_test/`）。

**依赖环境**
- **Python 版本**:: 建议使用 Python 3.8+。
- **主要第三方包**:: `pdfplumber`, `neo4j`（还有 notebook 环境如 `jupyter`）。
- **安装示例** (PowerShell):
```
pip install pdfplumber neo4j jupyter
```

**快速上手（Notebook 演示）**
- 打开 Jupyter Notebook/Lab，在浏览器中打开并运行 `KG_code/lawtest_for_pdf.ipynb`。该 notebook 演示了：
  - 使用 `KG_tools/extract_pdf_text.py` 从 PDF 提取文本（内存中处理）。
  - 使用 `KG_tools/extract_kg_stream.py` 将文本解析为知识图谱结构（entities & relations）。
  - 将解析结果保存为 JSON（输出目录: `KG_files/KG_json_test`）。
  - 将解析后的实体与关系写入本地 Neo4j（示例代码在 notebook 中，需修改 Neo4j 凭据）。

**命令行运行（示例）**
- 运行 Notebook（无界面自动执行）：
```
jupyter nbconvert --to notebook --execute KG_code/lawtest_for_pdf.ipynb --inplace
```
- 仅执行导入 JSON 到 Neo4j（使用仓库中工具）：
```
python -c "from KG_tools.import_json_to_neo4j import import_json_to_neo4j; import_json_to_neo4j('KG_files/KG_json_test')"
```

**配置 Neo4j 凭据**
- Notebook 中示例（`KG_code/lawtest_for_pdf.ipynb`）使用：
```
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "<your_password>"
```
- 请替换为你本地 Neo4j Desktop / Aura 的实际账号密码，确保服务已启动并监听对应端口。

**关键文件说明**
- `KG_code/lawtest_for_pdf.ipynb`:: 演示从 PDF 提取文本、解析为 KG、增强（split/attach body/enrich）并保存/导入 Neo4j 的完整流程。
- `KG_tools/extract_kg_stream.py`:: 主解析器，负责将文本转为 KG JSON 结构。
- `KG_tools/save_kg_json.py`:: 将解析结果保存为 JSON。
- `KG_tools/import_json_to_neo4j.py`:: 批量读取 JSON 并写入 Neo4j（调用 `upsert_entities` / `upsert_relations`）。

**使用示例与注意事项**
- 将待解析的 PDF 放到 `KG_files/` 下（示例 notebook 使用 `KG_files/专利法2021.pdf`）。
- 运行 notebook 后，输出 JSON 会保存到 `KG_files/KG_json_test/`。文件名采用实体 UID 衍生（例如 `Article_第10条.json`）。
- 若要导入 Neo4j：先启动 Neo4j 服务并确认凭据正确，再在 notebook 中运行导入单元或使用 `import_json_to_neo4j`。导入前请检查 JSON 文件格式是否完整。

**扩展建议**
- 可把解析器改造为批量处理目录下所有 PDF 并并行化处理。
- 可以把 Neo4j 凭据抽到配置文件或环境变量里，避免在笔记本中明文存放密码。

**联系 / 许可**
- 若需我帮你：我可以：修改 notebook 以使用环境变量、添加 `requirements.txt`、或把导入脚本打包为 CLI。是否需要我继续做这些？

---
文件位置: `README.md`（仓库根目录）
