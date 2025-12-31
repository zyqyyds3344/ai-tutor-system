"""
知识库初始化脚本
运行此脚本来初始化向量数据库
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from pdf_processor import PDFProcessor
from rag_engine import RAGEngine


def main():
    """初始化知识库"""
    print("=" * 60)
    print("   📚 AI助教系统 - 知识库初始化")
    print("   第10章：异常检测")
    print("=" * 60)
    
    # 检查API Key
    api_key = os.getenv("ZHIPUAI_API_KEY")
    if not api_key:
        print("\n❌ 错误：未设置 ZHIPUAI_API_KEY 环境变量")
        print("   请执行以下步骤：")
        print("   1. 复制 .env.example 为 .env")
        print("   2. 在 .env 文件中填入您的智谱AI API Key")
        print("   3. 重新运行此脚本")
        return
    
    print(f"\n✅ API Key 已配置: {api_key[:10]}...")
    
    # 步骤1: 处理PDF
    print("\n" + "-" * 40)
    print("步骤 1/3: 处理PDF文档")
    print("-" * 40)
    
    processor = PDFProcessor()
    
    if not processor.open_pdf():
        print("❌ 无法打开PDF文件，请检查文件路径")
        return
    
    # 提取第10章内容
    text = processor.extract_chapter_text()
    
    if not text:
        print("❌ 无法提取章节内容")
        processor.close()
        return
    
    print(f"\n📄 提取的文本长度: {len(text)} 字符")
    print(f"   预览: {text[:200]}...")
    
    # 步骤2: 创建文本块
    print("\n" + "-" * 40)
    print("步骤 2/3: 创建文本分块")
    print("-" * 40)
    
    chunks = processor.create_chunks()
    processor.close()
    
    if not chunks:
        print("❌ 没有生成任何文本块")
        return
    
    print(f"\n📦 生成的文本块数量: {len(chunks)}")
    
    # 步骤3: 向量化并存入数据库
    print("\n" + "-" * 40)
    print("步骤 3/3: 向量化并存入数据库")
    print("-" * 40)
    
    engine = RAGEngine()
    
    # 清空现有数据
    print("\n🗑️ 清空现有数据...")
    engine.clear_database()
    
    # 添加新文档
    print("\n📥 添加文档到向量库...")
    engine.add_documents(chunks)
    
    # 验证
    stats = engine.get_stats()
    print(f"\n✅ 知识库初始化完成！")
    print(f"   文档数量: {stats['document_count']}")
    
    # 测试查询
    print("\n" + "-" * 40)
    print("测试查询")
    print("-" * 40)
    
    test_question = "什么是异常检测？"
    print(f"\n🔍 测试问题: {test_question}")
    
    result = engine.ask(test_question)
    print(f"\n🤖 回答:\n{result['answer']}")
    
    print("\n" + "=" * 60)
    print("   ✅ 初始化完成！现在可以运行 streamlit run app.py")
    print("=" * 60)


if __name__ == "__main__":
    main()

