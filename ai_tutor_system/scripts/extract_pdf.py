"""
PDF页面提取脚本
根据用户输入的PDF阅读器显示的页码范围提取特定页面

说明：
- 用户输入的是PDF阅读器显示的页码（1-based，从1开始）
- Python内部使用0-based索引
- 第10章: PDF第419页到第438页（阅读器显示）
"""

import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("请先安装PyMuPDF: pip install PyMuPDF")
    sys.exit(1)


def extract_pdf_pages(input_path: str, output_path: str, start_page: int, end_page: int):
    """
    提取PDF的指定页面范围
    
    Args:
        input_path: 输入PDF文件路径
        output_path: 输出PDF文件路径
        start_page: 起始页码（PDF阅读器显示的页码，1-based）
        end_page: 结束页码（PDF阅读器显示的页码，1-based）
    
    页码转换：
        - 用户输入 start_page=419 → 内部索引 start_idx=418
        - 用户输入 end_page=438 → 内部索引 end_idx=437
        - fitz.insert_pdf() 的 from_page 和 to_page 都是包含的（inclusive）
    """
    # 转换为0-based索引
    start_idx = start_page - 1  # 419 → 418
    end_idx = end_page - 1      # 438 → 437
    
    print(f"\n📖 PDF页面提取")
    print(f"   输入文件: {input_path}")
    print(f"   输出文件: {output_path}")
    print(f"   页码范围: 第{start_page}页 - 第{end_page}页 (共{end_page - start_page + 1}页)")
    print(f"   索引范围: {start_idx} - {end_idx} (0-based)")
    
    try:
        # 打开源PDF
        src_doc = fitz.open(input_path)
        total_pages = len(src_doc)
        print(f"   源文件共: {total_pages}页")
        
        # 验证页码范围
        if start_idx < 0:
            print(f"❌ 起始页码无效！最小为1")
            src_doc.close()
            return False
            
        if end_idx >= total_pages:
            print(f"❌ 结束页码无效！PDF只有{total_pages}页")
            src_doc.close()
            return False
        
        if start_idx > end_idx:
            print(f"❌ 起始页码不能大于结束页码！")
            src_doc.close()
            return False
        
        # 创建新PDF
        dst_doc = fitz.open()
        
        # 复制指定页面（from_page和to_page都是inclusive的）
        dst_doc.insert_pdf(src_doc, from_page=start_idx, to_page=end_idx)
        
        # 确保输出目录存在
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存
        dst_doc.save(output_path)
        dst_doc.close()
        src_doc.close()
        
        print(f"\n✅ 提取成功！")
        print(f"   已保存到: {output_path}")
        print(f"   提取页数: {end_page - start_page + 1}页")
        return True
        
    except Exception as e:
        print(f"❌ 提取失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def extract_text_from_pages(input_path: str, start_page: int, end_page: int) -> str:
    """
    提取PDF指定页面的文本内容
    
    Args:
        input_path: 输入PDF文件路径
        start_page: 起始页码（1-based）
        end_page: 结束页码（1-based）
    
    Returns:
        提取的文本内容
    """
    start_idx = start_page - 1
    end_idx = end_page - 1
    
    try:
        doc = fitz.open(input_path)
        all_text = []
        
        for page_idx in range(start_idx, end_idx + 1):
            page = doc[page_idx]
            text = page.get_text()
            if text.strip():
                all_text.append(f"[第{page_idx + 1}页]\n{text}")
        
        doc.close()
        return "\n\n".join(all_text)
        
    except Exception as e:
        print(f"❌ 提取文本失败: {e}")
        return ""


def main():
    """主函数 - 交互式输入"""
    # 默认路径配置
    base_dir = Path(__file__).parent.parent
    default_input = base_dir.parent / "考试要求与说明" / "0 数据挖掘导论  完整版.pdf"
    default_output = base_dir / "data" / "chapter_10.pdf"
    
    print("=" * 60)
    print("   📚 PDF页面提取工具")
    print("=" * 60)
    print("\n说明：请输入PDF阅读器底部显示的页码（如 419、438）")
    print("      程序会自动处理索引转换\n")
    
    # 确认输入文件
    print(f"输入文件: {default_input}")
    if not default_input.exists():
        print("❌ 默认输入文件不存在！")
        input_path = input("请输入PDF文件路径: ").strip()
        if not Path(input_path).exists():
            print("❌ 文件不存在！")
            return
    else:
        print("✅ 文件存在")
        input_path = str(default_input)
    
    # 获取页码范围
    print("\n请输入PDF阅读器显示的页码（底部显示的页数）:")
    print("（第10章推荐：起始419，结束438）")
    
    try:
        start_input = input("起始页码 [默认419]: ").strip()
        start_page = int(start_input) if start_input else 419
        
        end_input = input("结束页码 [默认438]: ").strip()
        end_page = int(end_input) if end_input else 438
    except ValueError:
        print("❌ 请输入有效的数字！")
        return
    
    # 确认输出路径
    output_path = str(default_output)
    custom_output = input(f"\n输出路径 [{output_path}] (直接回车使用默认): ").strip()
    if custom_output:
        output_path = custom_output
    
    # 执行提取
    success = extract_pdf_pages(input_path, output_path, start_page, end_page)
    
    if success:
        # 询问是否也提取文本
        extract_text = input("\n是否同时提取文本内容？[y/N]: ").strip().lower()
        if extract_text == 'y':
            text = extract_text_from_pages(input_path, start_page, end_page)
            text_output = Path(output_path).with_suffix('.txt')
            with open(text_output, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"✅ 文本已保存到: {text_output}")
            print(f"   文本长度: {len(text)} 字符")


if __name__ == "__main__":
    main()
