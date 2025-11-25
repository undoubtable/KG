import pdfplumber
from pathlib import Path

def extract_pdf_text(pdf_path: str) -> str:
    """从 PDF 文件中提取全部文本（不落地保存 .txt），直接返回字符串。"""
    pdf_path = Path(pdf_path)
    assert pdf_path.exists(), f"文件不存在: {pdf_path}"
    
    all_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            all_text.append(text)
    
    return "\n".join(all_text)

print("✅ extract_pdf_text 已定义，可以直接用于提取 PDF 文本。")
