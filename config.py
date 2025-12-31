"""
AI助教系统配置文件
第10章：异常检测
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ============== 加载.env文件 ==============
BASE_DIR = Path(__file__).parent
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
    print(f"✅ 已加载配置文件: {ENV_FILE}")

# ============== 路径配置 ==============
# 本地开发路径
LOCAL_PDF_PATH = BASE_DIR.parent / "考试要求与说明" / "0 数据挖掘导论  完整版.pdf"
# 部署路径（PDF放在data文件夹中）
DEPLOY_PDF_PATH = BASE_DIR / "data" / "chapter_10.pdf"

# 自动选择存在的路径
if DEPLOY_PDF_PATH.exists():
    PDF_PATH = DEPLOY_PDF_PATH
else:
    PDF_PATH = LOCAL_PDF_PATH

CHROMA_DB_PATH = BASE_DIR / "chroma_db"

# ============== 章节配置 ==============
CHAPTER_NUMBER = 10
CHAPTER_TITLE = "异常检测"
CHAPTER_KEYWORDS = ["异常检测", "第10章", "第十章", "outlier", "anomaly"]

# 第10章在PDF中的真实页码范围（1-based，PDF文件中的实际页码）
# 注意：书中印刷页码P403对应PDF第419页，P422对应PDF第438页
CHAPTER_10_START_PAGE = 419  # 第10章起始页（PDF第419页 = 书中P403）
CHAPTER_10_END_PAGE = 438    # 第10章结束页（PDF第438页 = 书中P422）

# ============== 智谱AI配置 ==============
# 方式1: 在.env文件中设置 ZHIPUAI_API_KEY=你的key
# 方式2: 在Streamlit Cloud的Secrets中设置
# 方式3: 直接在下面填入API Key

# 优先从Streamlit secrets获取（用于Streamlit Cloud部署）
try:
    import streamlit as st
    ZHIPUAI_API_KEY = st.secrets.get("ZHIPUAI_API_KEY", os.getenv("ZHIPUAI_API_KEY", ""))
except:
    ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY", "")

# 模型配置
LLM_MODEL = "glm-4.6v"  # 问答模型（视觉模型也支持纯文本问答）
EMBEDDING_MODEL = "embedding-3"  # 向量化模型

# ============== RAG配置 ==============
CHUNK_SIZE = 500  # 文本分块大小
CHUNK_OVERLAP = 100  # 分块重叠大小
TOP_K = 5  # 检索返回的文档数量

# ============== 系统提示词 ==============
SYSTEM_PROMPT = """你是一个专业的数据挖掘课程AI助教，专门负责《数据挖掘导论》第10章"异常检测"的教学辅导工作。

你的职责包括：
1. 准确回答学生关于异常检测的问题，包括但不限于：
   - 异常检测的基本概念和定义
   - 统计方法（参数方法、非参数方法）
   - 基于邻近度的方法（基于距离、基于密度）
   - 基于聚类的方法
   - 异常检测的评估方法

2. 回答问题时必须：
   - 基于提供的参考资料进行回答
   - 明确标注引用来源
   - 使用通俗易懂的语言解释复杂概念
   - 适当举例说明

3. 如果问题超出第10章范围或参考资料中没有相关内容，请诚实告知学生。

请始终保持专业、耐心、友好的教学态度。"""

QUIZ_PROMPT = """基于以下关于异常检测的知识内容，请生成一道测试题。

要求：
1. 题目类型可以是：选择题、判断题或简答题
2. 题目难度适中，考察核心概念理解
3. 如果是选择题，提供4个选项，其中只有一个正确答案
4. 必须提供正确答案和解析

请按以下JSON格式输出：
{
    "type": "选择题/判断题/简答题",
    "question": "题目内容",
    "options": ["A. xxx", "B. xxx", "C. xxx", "D. xxx"],  // 选择题必填
    "answer": "正确答案",
    "explanation": "答案解析"
}

知识内容：
"""

KNOWLEDGE_MAP_PROMPT = """基于以下关于异常检测的内容，请生成一个结构化的知识提纲。

要求：
1. 提取主要知识点和子知识点
2. 按照逻辑层次组织
3. 标注重点和难点

请按以下格式输出：
# 第10章 异常检测

## 1. [一级知识点]
### 1.1 [二级知识点]
- 要点1
- 要点2
### 1.2 [二级知识点]
...

## 2. [一级知识点]
...

内容：
"""

