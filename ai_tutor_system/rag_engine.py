"""
RAG引擎模块
负责向量化、检索和问答功能
"""

import json
from typing import List, Dict, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings
from zhipuai import ZhipuAI

from config import (
    ZHIPUAI_API_KEY, 
    LLM_MODEL, 
    EMBEDDING_MODEL,
    CHROMA_DB_PATH,
    TOP_K,
    SYSTEM_PROMPT,
    CHAPTER_NUMBER
)


class RAGEngine:
    """RAG检索增强生成引擎"""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self.zhipu_client = None
        self._init_zhipu()
        self._init_chromadb()
    
    def _init_zhipu(self):
        """初始化智谱AI客户端"""
        if not ZHIPUAI_API_KEY:
            print("⚠️ 未设置ZHIPUAI_API_KEY环境变量")
            print("   请设置: export ZHIPUAI_API_KEY='your-api-key'")
            print("   或在Windows: set ZHIPUAI_API_KEY=your-api-key")
            return
        
        try:
            self.zhipu_client = ZhipuAI(api_key=ZHIPUAI_API_KEY)
            print("✅ 智谱AI客户端初始化成功")
        except Exception as e:
            print(f"❌ 智谱AI客户端初始化失败: {e}")
    
    def _init_chromadb(self):
        """初始化ChromaDB向量数据库"""
        try:
            # 确保目录存在
            CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=str(CHROMA_DB_PATH),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # 获取或创建集合
            self.collection = self.client.get_or_create_collection(
                name=f"chapter_{CHAPTER_NUMBER}_anomaly_detection",
                metadata={"description": "第10章异常检测知识库"}
            )
            
            print(f"✅ ChromaDB初始化成功，当前文档数: {self.collection.count()}")
        except Exception as e:
            print(f"❌ ChromaDB初始化失败: {e}")
    
    def get_embedding(self, text: str) -> List[float]:
        """获取文本的向量表示"""
        if not self.zhipu_client:
            raise ValueError("智谱AI客户端未初始化，请设置API Key")
        
        try:
            response = self.zhipu_client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ 获取向量失败: {e}")
            raise
    
    def add_documents(self, chunks: List[Dict]):
        """
        将文档块添加到向量数据库
        chunks: [{"text": "...", "metadata": {...}}]
        """
        if not chunks:
            print("⚠️ 没有文档需要添加")
            return
        
        print(f"📥 正在添加 {len(chunks)} 个文档块到向量库...")
        
        ids = []
        documents = []
        metadatas = []
        embeddings = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"chunk_{CHAPTER_NUMBER}_{i}"
            ids.append(chunk_id)
            documents.append(chunk["text"])
            metadatas.append(chunk["metadata"])
            
            # 获取向量
            try:
                embedding = self.get_embedding(chunk["text"])
                embeddings.append(embedding)
                if (i + 1) % 10 == 0:
                    print(f"   已处理 {i + 1}/{len(chunks)} 个文档块")
            except Exception as e:
                print(f"⚠️ 跳过文档块 {i}: {e}")
                ids.pop()
                documents.pop()
                metadatas.pop()
                continue
        
        if ids:
            # 批量添加到ChromaDB
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
            print(f"✅ 成功添加 {len(ids)} 个文档块")
        else:
            print("❌ 没有成功处理任何文档块")
    
    def search(self, query: str, top_k: int = TOP_K) -> List[Dict]:
        """
        检索相关文档
        返回: [{"text": "...", "metadata": {...}, "distance": float}]
        """
        if self.collection.count() == 0:
            print("⚠️ 知识库为空，请先添加文档")
            return []
        
        try:
            # 获取查询向量
            query_embedding = self.get_embedding(query)
            
            # 在ChromaDB中检索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            # 格式化结果
            docs = []
            for i in range(len(results["ids"][0])):
                docs.append({
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                })
            
            return docs
        
        except Exception as e:
            print(f"❌ 检索失败: {e}")
            return []
    
    def generate_answer(self, query: str, context_docs: List[Dict]) -> Dict:
        """
        基于检索结果生成回答
        返回: {"answer": "...", "sources": [...]}
        """
        if not self.zhipu_client:
            return {"answer": "❌ 智谱AI客户端未初始化，请设置API Key", "sources": []}
        
        # 构建上下文
        context_parts = []
        sources = []
        
        # PDF页码与书中页码的偏移量（PDF页码 - 16 = 书中页码）
        PAGE_OFFSET = 16
        
        for i, doc in enumerate(context_docs):
            pdf_page = doc["metadata"].get("page", 0)
            book_page = pdf_page - PAGE_OFFSET if isinstance(pdf_page, int) else "未知"
            
            context_parts.append(f"[参考资料{i+1}，PDF第{pdf_page}页/书中P{book_page}]\n{doc['text']}")
            sources.append({
                "pdf_page": pdf_page,
                "book_page": book_page,
                "preview": doc["text"][:100] + "..."
            })
        
        context = "\n\n".join(context_parts)
        
        # 构建提示词
        user_message = f"""请基于以下参考资料回答问题。回答时请：
1. 准确引用资料内容
2. 在回答中标注引用来源（如"根据第X页..."）
3. 如果资料中没有相关信息，请诚实告知

参考资料：
{context}

问题：{query}

请给出详细、准确的回答："""

        try:
            response = self.zhipu_client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            answer = response.choices[0].message.content
            return {"answer": answer, "sources": sources}
        
        except Exception as e:
            return {"answer": f"❌ 生成回答失败: {e}", "sources": sources}
    
    def ask(self, question: str) -> Dict:
        """
        完整的RAG问答流程
        """
        print(f"\n🔍 问题: {question}")
        
        # 1. 检索相关文档
        print("📚 正在检索相关文档...")
        docs = self.search(question)
        
        if not docs:
            return {
                "answer": "抱歉，知识库中没有找到相关内容。请确保已经初始化知识库。",
                "sources": []
            }
        
        print(f"   找到 {len(docs)} 个相关文档")
        
        # 2. 生成回答
        print("🤖 正在生成回答...")
        result = self.generate_answer(question, docs)
        
        return result
    
    def clear_database(self):
        """清空向量数据库"""
        if self.collection:
            # 删除并重新创建集合
            self.client.delete_collection(f"chapter_{CHAPTER_NUMBER}_anomaly_detection")
            self.collection = self.client.create_collection(
                name=f"chapter_{CHAPTER_NUMBER}_anomaly_detection",
                metadata={"description": "第10章异常检测知识库"}
            )
            print("✅ 知识库已清空")
    
    def get_stats(self) -> Dict:
        """获取知识库统计信息"""
        if self.collection:
            return {
                "document_count": self.collection.count(),
                "collection_name": self.collection.name
            }
        return {"document_count": 0, "collection_name": "未初始化"}


def test_rag_engine():
    """测试RAG引擎"""
    engine = RAGEngine()
    
    # 测试问答（需要先初始化知识库）
    stats = engine.get_stats()
    print(f"\n知识库状态: {stats}")
    
    if stats["document_count"] > 0:
        result = engine.ask("什么是异常检测？")
        print(f"\n回答: {result['answer']}")
        print(f"\n引用来源: {result['sources']}")
    else:
        print("\n⚠️ 知识库为空，请先运行初始化脚本")


if __name__ == "__main__":
    test_rag_engine()

