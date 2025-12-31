"""
知识导图/提纲生成模块
负责生成章节的知识结构和学习重点
"""

from typing import Dict, Optional

from zhipuai import ZhipuAI

from config import ZHIPUAI_API_KEY, LLM_MODEL, KNOWLEDGE_MAP_PROMPT


class KnowledgeMapGenerator:
    """知识导图生成器"""
    
    def __init__(self, rag_engine=None):
        self.rag_engine = rag_engine
        self.zhipu_client = None
        self.cached_map = None
        self._init_zhipu()
    
    def _init_zhipu(self):
        """初始化智谱AI客户端"""
        if ZHIPUAI_API_KEY:
            self.zhipu_client = ZhipuAI(api_key=ZHIPUAI_API_KEY)
    
    def generate_outline(self, content: Optional[str] = None) -> str:
        """
        生成知识提纲
        content: 章节内容，如果为None则从知识库获取
        """
        if not self.zhipu_client:
            return "❌ 智谱AI客户端未初始化，请设置API Key"
        
        # 获取内容
        if content is None:
            if self.rag_engine:
                # 从知识库获取所有文档的摘要
                docs = self.rag_engine.search("异常检测的主要内容和方法", top_k=10)
                if docs:
                    content = "\n\n".join([doc["text"] for doc in docs])
                else:
                    content = self._get_default_content()
            else:
                content = self._get_default_content()
        
        prompt = KNOWLEDGE_MAP_PROMPT + content
        
        try:
            response = self.zhipu_client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的数据挖掘教学专家，擅长整理和组织知识点。请生成清晰、结构化的知识提纲。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2000
            )
            
            outline = response.choices[0].message.content
            self.cached_map = outline
            return outline
        
        except Exception as e:
            return f"❌ 生成知识提纲失败: {e}"
    
    def generate_key_concepts(self) -> str:
        """生成核心概念列表"""
        if not self.zhipu_client:
            return "❌ 智谱AI客户端未初始化"
        
        prompt = """请列出《数据挖掘导论》第10章"异常检测"中的核心概念。

要求：
1. 每个概念用一句话简要解释
2. 标注难度级别（基础/中等/高级）
3. 按重要程度排序

格式：
🔹 **概念名称** [难度] - 简要解释
"""
        
        try:
            response = self.zhipu_client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"❌ 生成概念列表失败: {e}"
    
    def generate_learning_path(self) -> str:
        """生成学习路径建议"""
        if not self.zhipu_client:
            return "❌ 智谱AI客户端未初始化"
        
        prompt = """为学习《数据挖掘导论》第10章"异常检测"设计一个学习路径。

要求：
1. 分为若干学习阶段
2. 每个阶段标注预计学习时间
3. 包含学习目标和检验方法
4. 提供学习建议

格式：
## 📚 异常检测学习路径

### 阶段1: xxx (预计xx分钟)
- **目标**: ...
- **内容**: ...
- **检验**: ...
- **建议**: ...
"""
        
        try:
            response = self.zhipu_client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"❌ 生成学习路径失败: {e}"
    
    def _get_default_content(self) -> str:
        """获取默认的异常检测知识内容"""
        return """
第10章 异常检测 (Anomaly Detection)

10.1 异常检测概述
- 异常的定义：与大多数数据显著不同的数据对象
- 异常的别名：离群点(outlier)、异常值(anomaly)、例外(exception)
- 应用场景：欺诈检测、入侵检测、医学诊断、故障检测

10.2 异常的类型
- 全局异常(Global Outlier)：相对于整个数据集的异常
- 情境异常(Contextual Outlier)：在特定情境中的异常
- 集体异常(Collective Outlier)：一组数据点共同表现异常

10.3 异常检测方法
10.3.1 统计方法
- 参数方法：假设数据服从某种分布
- 非参数方法：不假设特定分布

10.3.2 基于邻近度的方法
- 基于距离：k近邻距离
- 基于密度：局部离群因子(LOF)

10.3.3 基于聚类的方法
- 将不属于任何簇的点视为异常
- 与簇中心距离过大的点视为异常

10.4 评估方法
- 准确率、召回率、F1分数
- ROC曲线、AUC
"""
    
    def generate_summary(self, topic: str = "异常检测") -> str:
        """生成指定主题的摘要"""
        if not self.zhipu_client:
            return "❌ 智谱AI客户端未初始化"
        
        # 从知识库检索相关内容
        if self.rag_engine:
            docs = self.rag_engine.search(topic, top_k=5)
            if docs:
                content = "\n\n".join([doc["text"] for doc in docs])
            else:
                content = self._get_default_content()
        else:
            content = self._get_default_content()
        
        prompt = f"""基于以下内容，生成关于"{topic}"的简明摘要。

要求：
1. 概括核心要点
2. 语言简洁清晰
3. 控制在200字以内

内容：
{content}
"""
        
        try:
            response = self.zhipu_client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"❌ 生成摘要失败: {e}"


def test_knowledge_map():
    """测试知识导图生成"""
    generator = KnowledgeMapGenerator()
    
    print("=" * 50)
    print("生成知识提纲...")
    print("=" * 50)
    outline = generator.generate_outline()
    print(outline)
    
    print("\n" + "=" * 50)
    print("生成核心概念...")
    print("=" * 50)
    concepts = generator.generate_key_concepts()
    print(concepts)


if __name__ == "__main__":
    test_knowledge_map()

