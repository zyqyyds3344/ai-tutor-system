"""
PDF调试脚本 - 测试能否正确读取指定页面
"""

import fitz
from pathlib import Path

# PDF路径
PDF_PATH = Path(__file__).parent.parent / "考试要求与说明" / "0 数据挖掘导论  完整版.pdf"

# 第10章页码范围（PDF阅读器显示的页码，1-based）
START_PAGE = 419  # PDF第419页 = 书中P403
END_PAGE = 438    # PDF第438页 = 书中P422

def test_pdf():
    print(f"📄 PDF路径: {PDF_PATH}")
    print(f"📄 文件存在: {PDF_PATH.exists()}")
    
    if not PDF_PATH.exists():
        print("❌ PDF文件不存在！")
        return
    
    # 打开PDF
    doc = fitz.open(str(PDF_PATH))
    print(f"✅ 成功打开PDF，共 {len(doc)} 页")
    
    # 测试读取第419页（0-based索引为418）
    test_pages = [START_PAGE - 1, START_PAGE, END_PAGE - 1]  # 测试几个页面
    
    for page_idx in test_pages:
        if page_idx >= len(doc):
            print(f"⚠️ 页面 {page_idx} 超出范围")
            continue
            
        page = doc[page_idx]
        text = page.get_text()
        
        print(f"\n{'='*60}")
        print(f"📖 页面索引: {page_idx} (PDF显示为第{page_idx + 1}页)")
        print(f"   原始文本长度: {len(text)} 字符")
        print(f"   前500字符预览:")
        print("-" * 40)
        print(text[:500] if text else "[空白页]")
        print("-" * 40)
    
    # 提取完整的第10章
    print(f"\n{'='*60}")
    print(f"📚 提取第10章完整内容 (索引 {START_PAGE-1} 到 {END_PAGE-1})")
    print("=" * 60)
    
    all_text = []
    for page_idx in range(START_PAGE - 1, END_PAGE):  # 0-based: 418 到 437
        page = doc[page_idx]
        text = page.get_text()
        if text.strip():
            all_text.append(f"[第{page_idx + 1}页]\n{text}")
            print(f"✅ 第{page_idx + 1}页: {len(text)} 字符")
        else:
            print(f"⚠️ 第{page_idx + 1}页: 空白")
    
    full_text = "\n\n".join(all_text)
    print(f"\n📊 总计提取: {len(full_text)} 字符")
    
    # 保存到文件以便检查
    output_file = Path(__file__).parent / "debug_chapter10_text.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_text)
    print(f"💾 已保存到: {output_file}")
    
    doc.close()


if __name__ == "__main__":
    test_pdf()

