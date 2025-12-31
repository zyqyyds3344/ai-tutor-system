# 📚 AI助教系统 - 第10章：异常检测

> 基于《数据挖掘导论》第10章内容开发的智能AI助教系统

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 💬 **智能问答** | 基于RAG技术的精准知识问答，答案标注引用来源 |
| 🗺️ **知识导图** | 自动生成章节知识结构、核心概念和学习路径 |
| 📝 **交互测试** | AI生成选择题/判断题/简答题，实时检验学习效果 |
| 🎨 **现代UI** | 美观的渐变主题设计，流畅的交互体验 |

## 🛠️ 技术栈

- **大模型**: 智谱AI GLM-4-Flash
- **向量化**: 智谱AI Embedding-3
- **向量库**: ChromaDB (本地持久化)
- **前端框架**: Streamlit
- **PDF解析**: PyMuPDF

## 📦 安装步骤

### 1. 创建虚拟环境（推荐）

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置API Key

```bash
# 复制环境变量模板
copy .env.example .env

# 编辑 .env 文件，填入您的智谱AI API Key
# ZHIPUAI_API_KEY=your-api-key-here
```

> 💡 智谱AI API Key 获取地址: https://open.bigmodel.cn/

### 4. 初始化知识库

```bash
python init_db.py
```

这会：
- 从PDF中提取第10章"异常检测"的内容
- 将文本分块并向量化
- 存入ChromaDB向量数据库

### 5. 启动应用

```bash
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`

## 📁 项目结构

```
ai_tutor_system/
├── app.py              # Streamlit主应用
├── config.py           # 配置文件
├── pdf_processor.py    # PDF处理模块
├── rag_engine.py       # RAG引擎（向量化+检索+问答）
├── quiz_generator.py   # 测试题生成器
├── knowledge_map.py    # 知识导图生成器
├── init_db.py          # 知识库初始化脚本
├── requirements.txt    # 依赖文件
├── .env.example        # 环境变量模板
├── README.md           # 说明文档
└── chroma_db/          # ChromaDB数据目录（自动生成）
```

## 🚀 使用指南

### 智能问答

1. 在左侧侧边栏确认知识库已初始化（文档数量 > 0）
2. 在输入框输入关于异常检测的问题
3. 点击"发送"获取AI助教的回答
4. 可展开"查看引用来源"了解答案出处

### 知识导图

1. 点击"生成知识提纲"获取章节知识结构
2. 点击"核心概念"查看重要概念列表
3. 点击"学习路径"获取学习建议

### 交互测试

1. 选择题目类型（选择题/判断题/简答题/随机）
2. 可选填写特定知识点
3. 点击"生成题目"获取测试题
4. 输入答案后点击"提交答案"
5. 查看答题结果和解析

## 🌐 在线部署 (Streamlit Cloud)

### 快速部署步骤

1. **Fork本仓库** 到你的GitHub账号

2. **访问 [share.streamlit.io](https://share.streamlit.io)** 并用GitHub登录

3. **点击 "New app"**，选择：
   - Repository: `你的用户名/ai-tutor-system`
   - Branch: `main`
   - Main file path: `app.py`

4. **配置Secrets**（点击 Advanced settings → Secrets）：
   ```toml
   ZHIPUAI_API_KEY = "你的智谱AI_API_Key"
   ```

5. **点击 Deploy** 等待部署完成

部署成功后，你会获得一个公开链接，如：`https://ai-tutor-system.streamlit.app`

### 默认登录账户
- 用户名: `10001`
- 密码: `123456`

## ⚠️ 注意事项

1. **API Key安全**: 不要将API Key提交到代码仓库，使用Streamlit Secrets管理
2. **网络要求**: 需要网络连接访问智谱AI API
3. **PDF路径**: 确保PDF文件位于正确位置
4. **Streamlit Cloud**: 免费版需要仓库为Public

## 📊 第10章核心知识点

- **异常类型**: 全局异常、情境异常、集体异常
- **检测方法**: 
  - 统计方法（参数/非参数）
  - 基于邻近度（距离/密度）
  - 基于聚类
- **评估指标**: 准确率、召回率、F1、ROC/AUC

## 👨‍🎓 开发信息

- **学号**: 405
- **章节**: 第10章 - 异常检测
- **课程**: AI编程与Python数据科学实践
- **时间**: 2025年

---

*本项目在AI编程助手(Cursor)的辅助下完成开发*

