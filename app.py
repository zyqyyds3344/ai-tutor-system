"""
AI助教系统 - 现代化 Streamlit 前端应用
基于《数据挖掘导论》第10章：异常检测
设计风格：科技蓝 + 教育绿，现代化UI，响应式设计
"""

import streamlit as st
import os
import json
import time
from pathlib import Path
from datetime import datetime

# 设置页面配置（必须在最前面）
st.set_page_config(
    page_title="📚 AI助教 - 异常检测",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 导入模块
from config import CHAPTER_NUMBER, CHAPTER_TITLE, ZHIPUAI_API_KEY
from pdf_processor import PDFProcessor
from rag_engine import RAGEngine
from quiz_generator import QuizGenerator
from knowledge_map import KnowledgeMapGenerator


# ============== 固定登录凭据 ==============
VALID_CREDENTIALS = {
    "10001": "123456",
    "admin": "admin123",
    "test": "test123"
}


# ============== 支持的大模型配置 ==============
LLM_PROVIDERS = {
    "智谱AI (ZhipuAI)": {
        "models": ["GLM-4", "GLM-4-Plus", "GLM-4V", "GLM-4-Long"],
        "env_key": "ZHIPUAI_API_KEY",
        "placeholder": "请输入智谱AI API Key (sk-...)"
    },
    "OpenAI": {
        "models": ["GPT-4o", "GPT-4-Turbo", "GPT-4", "GPT-3.5-Turbo"],
        "env_key": "OPENAI_API_KEY",
        "placeholder": "请输入OpenAI API Key (sk-...)"
    },
    "百度文心 (Wenxin)": {
        "models": ["ERNIE-4.0", "ERNIE-3.5-Turbo", "ERNIE-Bot"],
        "env_key": "WENXIN_API_KEY",
        "placeholder": "请输入百度文心 API Key"
    },
    "阿里通义 (Tongyi)": {
        "models": ["Qwen-Max", "Qwen-Plus", "Qwen-Turbo"],
        "env_key": "DASHSCOPE_API_KEY",
        "placeholder": "请输入阿里通义 API Key"
    },
    "讯飞星火 (Spark)": {
        "models": ["Spark-4.0", "Spark-3.5", "Spark-3.0"],
        "env_key": "SPARK_API_KEY",
        "placeholder": "请输入讯飞星火 API Key"
    },
    "Anthropic Claude": {
        "models": ["Claude-3-Opus", "Claude-3-Sonnet", "Claude-3-Haiku"],
        "env_key": "ANTHROPIC_API_KEY",
        "placeholder": "请输入Anthropic API Key (sk-ant-...)"
    }
}


# ============== 现代化CSS样式 ==============
def load_modern_css():
    """加载现代化CSS样式 - 根据主题动态生成"""
    is_light = st.session_state.get("theme", "dark") == "light"
    
    if is_light:
        # 明亮主题色彩
        css_vars = """
        :root {
            --primary-blue: #2563eb;
            --primary-blue-light: #3b82f6;
            --primary-blue-dark: #1d4ed8;
            --accent-green: #10b981;
            --accent-green-light: #34d399;
            --accent-green-dark: #059669;
            --bg-gradient-start: #f8fafc;
            --bg-gradient-end: #e2e8f0;
            --card-bg: rgba(255, 255, 255, 0.9);
            --card-border: rgba(0, 0, 0, 0.1);
            --text-primary: #1e293b;
            --text-secondary: #475569;
            --text-muted: #64748b;
            --success: #22c55e;
            --warning: #f59e0b;
            --error: #ef4444;
            --info: #06b6d4;
            --sidebar-bg: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%);
            --input-bg: rgba(0, 0, 0, 0.03);
            --input-border: rgba(0, 0, 0, 0.15);
        }
        """
        app_bg = "background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);"
        sidebar_text = "color: #1e293b;"
        card_shadow = "box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);"
    else:
        # 暗色主题色彩
        css_vars = """
        :root {
            --primary-blue: #2563eb;
            --primary-blue-light: #3b82f6;
            --primary-blue-dark: #1d4ed8;
            --accent-green: #10b981;
            --accent-green-light: #34d399;
            --accent-green-dark: #059669;
            --bg-gradient-start: #0f172a;
            --bg-gradient-end: #1e293b;
            --card-bg: rgba(255, 255, 255, 0.05);
            --card-border: rgba(255, 255, 255, 0.1);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --success: #22c55e;
            --warning: #f59e0b;
            --error: #ef4444;
            --info: #06b6d4;
            --sidebar-bg: linear-gradient(180deg, rgba(15, 23, 42, 0.98) 0%, rgba(30, 41, 59, 0.98) 100%);
            --input-bg: rgba(255, 255, 255, 0.05);
            --input-border: rgba(255, 255, 255, 0.1);
        }
        """
        app_bg = "background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);"
        sidebar_text = "color: #f8fafc;"
        card_shadow = "box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);"
    
    st.markdown(f"""
    <style>
    {css_vars}
    
    /* ============== 字体设置 - 优化中文显示 ============== */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');
    
    * {{
        font-family: 'Noto Sans SC', 'Microsoft YaHei', '微软雅黑', 'PingFang SC', 'Hiragino Sans GB', 'WenQuanYi Micro Hei', sans-serif !important;
    }}
    
    /* ============== 全局样式 ============== */
    .stApp {{
        {app_bg}
    }}
    
    /* 确保所有文本清晰显示 */
    body, p, span, div, h1, h2, h3, h4, h5, h6, label, button {{
        font-family: 'Noto Sans SC', 'Microsoft YaHei', '微软雅黑', 'PingFang SC', sans-serif !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-rendering: optimizeLegibility;
    }}
    
    /* ============== 隐藏默认元素 ============== */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* ============== 加载动画 ============== */
    @keyframes shimmer {{
        0% {{ background-position: -1000px 0; }}
        100% {{ background-position: 1000px 0; }}
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}
    
    @keyframes float {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-10px); }}
    }}
    
    .skeleton {{
        background: linear-gradient(90deg, #1e293b 25%, #334155 50%, #1e293b 75%);
        background-size: 1000px 100%;
        animation: shimmer 2s infinite linear;
        border-radius: 8px;
    }}
    
    .fade-in {{
        animation: fadeIn 0.6s ease-out forwards;
    }}
    
    /* ============== 页面标题 ============== */
    .page-header {{
        text-align: center;
        padding: 2rem 0;
        animation: fadeIn 0.6s ease-out;
    }}
    
    .main-title {{
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary-blue-light) 0%, var(--accent-green) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }}
    
    .subtitle {{
        color: var(--text-secondary);
        font-size: 1.1rem;
        font-weight: 400;
    }}
    
    /* ============== 卡片样式 ============== */
    .modern-card {{
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        {card_shadow}
    }}
    
    .modern-card:hover {{
        transform: translateY(-4px);
        border-color: var(--primary-blue);
    }}
    
    .glass-card {{
        background: var(--card-bg);
        backdrop-filter: blur(30px);
        border: 1px solid var(--card-border);
        border-radius: 20px;
        padding: 2rem;
        {card_shadow}
    }}
    
    /* ============== 统计卡片 ============== */
    .stat-card {{
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.15) 0%, rgba(16, 185, 129, 0.15) 100%);
        border: 1px solid rgba(37, 99, 235, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }}
    
    .stat-card:hover {{
        transform: scale(1.02);
        border-color: var(--accent-green);
    }}
    
    .stat-icon {{
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }}
    
    .stat-number {{
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary-blue-light) 0%, var(--accent-green) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    .stat-label {{
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-top: 0.25rem;
    }}
    
    /* ============== 按钮样式 ============== */
    .stButton > button {{
        background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-blue-dark) 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.39);
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 25px -5px rgba(37, 99, 235, 0.5);
        background: linear-gradient(135deg, var(--primary-blue-light) 0%, var(--primary-blue) 100%);
    }}
    
    .stButton > button:active {{
        transform: translateY(0);
    }}
    
    /* ============== 输入框样式 ============== */
    .stTextInput > div > div > input {{
        background: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 12px !important;
        color: #000000 !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: var(--primary-blue) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2) !important;
        background: #ffffff !important;
        color: #000000 !important;
    }}
    
    .stTextInput > div > div > input::placeholder {{
        color: #64748b !important;
    }}
    
    /* 密码输入框 */
    .stTextInput input[type="password"] {{
        background: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        color: #000000 !important;
    }}
    
    /* 选择框样式 */
    .stSelectbox > div > div {{
        background: var(--input-bg) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
    }}
    
    /* ============== 聊天消息样式 ============== */
    .chat-container {{
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
        scrollbar-width: thin;
        scrollbar-color: var(--primary-blue) transparent;
    }}
    
    .chat-message {{
        display: flex;
        gap: 12px;
        margin: 1rem 0;
        animation: fadeIn 0.4s ease-out;
    }}
    
    .chat-avatar {{
        width: 40px;
        height: 40px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        flex-shrink: 0;
    }}
    
    .user-avatar-chat {{
        background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-blue-dark) 100%);
    }}
    
    .ai-avatar-chat {{
        background: linear-gradient(135deg, var(--accent-green) 0%, var(--accent-green-dark) 100%);
    }}
    
    .chat-bubble {{
        max-width: 80%;
        padding: 1rem 1.25rem;
        border-radius: 16px;
        line-height: 1.6;
        color: var(--text-primary);
    }}
    
    .user-bubble {{
        background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-blue-dark) 100%);
        color: white !important;
        border-bottom-left-radius: 4px;
    }}
    
    .ai-bubble {{
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        color: var(--text-primary);
        border-bottom-left-radius: 4px;
    }}
    
    /* ============== 引用来源样式 ============== */
    .source-card {{
        background: rgba(37, 99, 235, 0.1);
        border: 1px solid rgba(37, 99, 235, 0.3);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }}
    
    .source-card-header {{
        display: flex;
        align-items: center;
        gap: 8px;
        color: var(--primary-blue-light);
        font-weight: 600;
        margin-bottom: 0.5rem;
    }}
    
    /* ============== 测试题卡片 ============== */
    .quiz-card {{
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%);
        border: 1px solid rgba(37, 99, 235, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
    }}
    
    .quiz-question {{
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }}
    
    .quiz-option {{
        background: var(--input-bg);
        border: 1px solid var(--input-border);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        color: var(--text-primary);
    }}
    
    .quiz-option:hover {{
        background: rgba(37, 99, 235, 0.2);
        border-color: var(--primary-blue);
    }}
    
    /* ============== 进度条 ============== */
    .progress-container {{
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        height: 10px;
        overflow: hidden;
        margin: 1rem 0;
    }}
    
    .progress-bar {{
        height: 100%;
        background: linear-gradient(90deg, var(--primary-blue) 0%, var(--accent-green) 100%);
        border-radius: 10px;
        transition: width 0.5s ease;
    }}
    
    /* ============== 标签页样式 ============== */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: var(--input-bg);
        border-radius: 16px;
        padding: 8px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: 12px;
        color: var(--text-secondary);
        padding: 12px 24px;
        font-weight: 500;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-blue-dark) 100%);
        color: white !important;
    }}
    
    /* ============== 侧边栏样式 ============== */
    [data-testid="stSidebar"] {{
        background: var(--sidebar-bg);
        border-right: 1px solid var(--card-border);
    }}
    
    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 2rem;
    }}
    
    [data-testid="stSidebar"] .stMarkdown {{
        {sidebar_text}
    }}
    
    /* ============== 登录页面样式 ============== */
    .login-container {{
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
    }}
    
    .login-card {{
        background: var(--card-bg);
        backdrop-filter: blur(30px);
        border: 1px solid var(--card-border);
        border-radius: 24px;
        padding: 3rem;
        width: 100%;
        max-width: 420px;
        animation: fadeIn 0.8s ease-out;
        {card_shadow}
    }}
    
    .login-header {{
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    .login-logo {{
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, var(--primary-blue) 0%, var(--accent-green) 100%);
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        margin: 0 auto 1.5rem;
        animation: float 3s ease-in-out infinite;
    }}
    
    .login-title {{
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }}
    
    .login-subtitle {{
        color: var(--text-secondary);
        font-size: 0.95rem;
    }}
    
    /* ============== 仪表板样式 ============== */
    .dashboard-welcome {{
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.15) 0%, rgba(16, 185, 129, 0.15) 100%);
        border: 1px solid rgba(37, 99, 235, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
    }}
    
    .welcome-text {{
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
    }}
    
    .welcome-subtitle {{
        color: var(--text-secondary);
        margin-top: 0.5rem;
    }}
    
    /* 快捷入口卡片 */
    .quick-action {{
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
    }}
    
    .quick-action:hover {{
        transform: translateY(-4px);
        border-color: var(--primary-blue);
    }}
    
    .quick-action-icon {{
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }}
    
    .quick-action-title {{
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }}
    
    .quick-action-desc {{
        font-size: 0.85rem;
        color: var(--text-secondary);
    }}
    
    /* ============== 学习历史样式 ============== */
    .history-item {{
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.3s ease;
    }}
    
    .history-item:hover {{
        background: rgba(37, 99, 235, 0.1);
        border-color: rgba(37, 99, 235, 0.3);
    }}
    
    .history-content {{
        flex: 1;
    }}
    
    .history-title {{
        font-weight: 500;
        color: var(--text-primary);
        margin-bottom: 0.25rem;
    }}
    
    .history-meta {{
        font-size: 0.85rem;
        color: var(--text-muted);
    }}
    
    /* ============== 思维导图容器 ============== */
    .mindmap-container {{
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        min-height: 400px;
    }}
    
    .mindmap-image {{
        width: 100%;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }}
    
    /* ============== 响应式设计 ============== */
    @media (max-width: 768px) {{
        .main-title {{
            font-size: 2rem;
        }}
        
        .login-card {{
            padding: 2rem;
        }}
        
        .stat-card {{
            padding: 1rem;
        }}
        
        .stat-number {{
            font-size: 1.75rem;
        }}
    }}
    
    /* ============== 滚动条样式 ============== */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: rgba(255, 255, 255, 0.05);
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: var(--primary-blue);
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--primary-blue-light);
    }}
    
    /* ============== 状态徽章 ============== */
    .badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }}
    
    .badge-success {{
        background: rgba(34, 197, 94, 0.2);
        color: var(--success);
    }}
    
    .badge-warning {{
        background: rgba(245, 158, 11, 0.2);
        color: var(--warning);
    }}
    
    .badge-error {{
        background: rgba(239, 68, 68, 0.2);
        color: var(--error);
    }}
    
    .badge-info {{
        background: rgba(6, 182, 212, 0.2);
        color: var(--info);
    }}
    
    /* ============== 错误和成功提示 ============== */
    .stAlert {{
        border-radius: 12px !important;
    }}
    
    /* ============== 标签文字颜色 ============== */
    label {{
        color: var(--text-primary) !important;
    }}
    
    .stMarkdown p, .stMarkdown li {{
        color: var(--text-primary);
    }}
    </style>
    """, unsafe_allow_html=True)


# ============== 初始化Session State ==============
def init_session_state():
    """初始化会话状态"""
    defaults = {
        "rag_engine": None,
        "quiz_generator": None,
        "knowledge_map": None,
        "chat_history": [],
        "current_quiz": None,
        "quiz_results": {"correct": 0, "total": 0},
        "db_initialized": False,
        "logged_in": False,
        "username": "",
        "current_page": "dashboard",
        "theme": "dark",
        "language": "zh",
        "learning_history": [],
        "quiz_history": [],
        "outline_history": [],
        "show_sources": True,
        "api_key_set": bool(ZHIPUAI_API_KEY),
        "selected_provider": "智谱AI (ZhipuAI)",
        "selected_model": "GLM-4",
        "api_keys": {}
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def initialize_system():
    """初始化系统组件"""
    try:
        st.session_state.rag_engine = RAGEngine()
        st.session_state.quiz_generator = QuizGenerator(st.session_state.rag_engine)
        st.session_state.knowledge_map = KnowledgeMapGenerator(st.session_state.rag_engine)
        
        stats = st.session_state.rag_engine.get_stats()
        st.session_state.db_initialized = stats["document_count"] > 0
        
        return True
    except Exception as e:
        st.error(f"系统初始化失败: {e}")
        return False


# ============== 登录验证函数 ==============
def verify_login(username, password):
    """验证登录凭据"""
    if username in VALID_CREDENTIALS:
        return VALID_CREDENTIALS[username] == password
    return False


# ============== 登录/注册页面 ==============
def render_login_page():
    """渲染登录页面"""
    st.markdown("""
    <div class="page-header fade-in">
        <div class="login-logo">🎓</div>
        <h1 class="login-title">AI助教系统</h1>
        <p class="login-subtitle">基于《数据挖掘导论》第10章 - 异常检测</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="glass-card fade-in">
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 登录", "📝 注册"])
        
        with tab1:
            st.markdown("### 欢迎回来")
            st.markdown("""
            <div style="background: #e0f2fe; border: 2px solid #0284c7; border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
                <p style="margin: 0; font-size: 0.95rem; color: #000000;">
                    <strong style="color: #0369a1;">📋 默认账户：</strong><br>
                    <span style="color: #000000;">用户名:</span> 
                    <code style="background: #0369a1; color: #ffffff; padding: 3px 8px; border-radius: 4px; font-weight: 600;">10001</code><br>
                    <span style="color: #000000;">密码:</span> 
                    <code style="background: #0369a1; color: #ffffff; padding: 3px 8px; border-radius: 4px; font-weight: 600;">123456</code>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            username = st.text_input("用户名 / 学号", placeholder="请输入用户名或学号", key="login_username")
            password = st.text_input("密码", type="password", placeholder="请输入密码", key="login_password")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                remember = st.checkbox("记住我", value=True)
            
            if st.button("登 录", use_container_width=True, key="login_btn"):
                if username and password:
                    if verify_login(username, password):
                        with st.spinner("正在登录..."):
                            time.sleep(0.5)
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.success("✅ 登录成功！")
                            time.sleep(0.3)
                            st.rerun()
                    else:
                        st.error("❌ 用户名或密码错误！")
                else:
                    st.warning("请输入用户名和密码")
        
        with tab2:
            st.markdown("### 创建新账户")
            st.info("💡 注册功能仅供演示，注册后可直接登录")
            
            new_username = st.text_input("用户名", placeholder="请设置用户名", key="reg_username")
            student_id = st.text_input("学号", placeholder="请输入学号", key="reg_student_id")
            new_email = st.text_input("邮箱", placeholder="请输入邮箱", key="reg_email")
            new_password = st.text_input("密码", type="password", placeholder="请设置密码", key="reg_password")
            confirm_password = st.text_input("确认密码", type="password", placeholder="请再次输入密码", key="reg_confirm")
            
            chapter = st.selectbox(
                "选择学习章节",
                ["第10章 - 异常检测", "第9章 - 聚类分析", "第8章 - 关联分析"],
                index=0
            )
            
            agree = st.checkbox("我已阅读并同意服务条款", value=False)
            
            if st.button("注 册", use_container_width=True, key="register_btn"):
                if new_username and new_password and agree:
                    if new_password == confirm_password:
                        # 将新用户添加到有效凭据中
                        VALID_CREDENTIALS[new_username] = new_password
                        with st.spinner("正在创建账户..."):
                            time.sleep(0.5)
                            st.success("✅ 注册成功！请使用新账户登录")
                    else:
                        st.error("两次密码输入不一致")
                elif not agree:
                    st.warning("请先同意服务条款")
                else:
                    st.error("请填写完整信息")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-top: 3rem; color: var(--text-muted);">
        <p>© 2025 AI助教系统 | AI编程与Python数据科学实践</p>
    </div>
    """, unsafe_allow_html=True)


# ============== 侧边栏导航 ==============
def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        # Logo和标题
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0 2rem;">
            <div style="
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, #2563eb 0%, #10b981 100%);
                border-radius: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.75rem;
                margin: 0 auto 1rem;
            ">🎓</div>
            <h2 style="
                font-size: 1.25rem;
                font-weight: 700;
                background: linear-gradient(135deg, #3b82f6 0%, #10b981 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0;
            ">AI助教系统</h2>
            <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 0.25rem;">第10章 · 异常检测</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 用户信息
        st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 0.75rem;
            background: rgba(37, 99, 235, 0.1);
            border-radius: 12px;
            margin-bottom: 1.5rem;
        ">
            <div style="
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, #2563eb 0%, #10b981 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: 600;
            ">{st.session_state.username[0].upper() if st.session_state.username else 'U'}</div>
            <div>
                <div style="font-weight: 600; color: var(--text-primary);">{st.session_state.username or '用户'}</div>
                <div style="font-size: 0.75rem; color: var(--text-muted);">学习中...</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 导航菜单
        st.markdown("#### 📚 功能导航")
        
        nav_items = [
            ("dashboard", "📊", "学习仪表板"),
            ("qa", "💬", "智能问答"),
            ("knowledge_map", "🗺️", "知识导图"),
            ("quiz", "📝", "交互测试"),
            ("history", "📜", "学习历史"),
            ("settings", "⚙️", "系统设置"),
        ]
        
        for page_id, icon, label in nav_items:
            is_active = st.session_state.current_page == page_id
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{page_id}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_page = page_id
                st.rerun()
        
        st.markdown("---")
        
        # 知识库状态
        st.markdown("#### 📚 知识库状态")
        
        if st.session_state.rag_engine:
            stats = st.session_state.rag_engine.get_stats()
            doc_count = stats.get("document_count", 0)
            
            if doc_count > 0:
                st.markdown(f"""
                <div style="
                    background: rgba(34, 197, 94, 0.1);
                    border: 1px solid rgba(34, 197, 94, 0.3);
                    border-radius: 8px;
                    padding: 0.75rem;
                    text-align: center;
                ">
                    <span style="color: #22c55e;">✅ 已就绪</span>
                    <br>
                    <span style="color: var(--text-muted); font-size: 0.85rem;">{doc_count} 个文档块</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="
                    background: rgba(245, 158, 11, 0.1);
                    border: 1px solid rgba(245, 158, 11, 0.3);
                    border-radius: 8px;
                    padding: 0.75rem;
                    text-align: center;
                ">
                    <span style="color: #f59e0b;">⚠️ 未初始化</span>
                </div>
                """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 初始化", use_container_width=True, key="sidebar_init"):
                    init_knowledge_base()
            with col2:
                if st.button("🗑️ 清空", use_container_width=True, key="sidebar_clear"):
                    if st.session_state.rag_engine:
                        st.session_state.rag_engine.clear_database()
                        st.session_state.db_initialized = False
                        st.success("已清空")
                        st.rerun()
        
        st.markdown("---")
        
        # 主题切换
        st.markdown("#### 🎨 主题设置")
        theme_options = ["暗色模式", "明亮模式"]
        current_theme_idx = 0 if st.session_state.theme == "dark" else 1
        new_theme = st.selectbox(
            "选择主题",
            theme_options,
            index=current_theme_idx,
            key="theme_selector",
            label_visibility="collapsed"
        )
        
        if (new_theme == "暗色模式" and st.session_state.theme != "dark") or \
           (new_theme == "明亮模式" and st.session_state.theme != "light"):
            st.session_state.theme = "dark" if new_theme == "暗色模式" else "light"
            st.rerun()
        
        st.markdown("---")
        
        # 学习统计
        st.markdown("#### 📊 今日学习")
        results = st.session_state.quiz_results
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("答题数", results["total"])
        with col2:
            if results["total"] > 0:
                accuracy = results["correct"] / results["total"] * 100
                st.metric("正确率", f"{accuracy:.0f}%")
            else:
                st.metric("正确率", "-")
        
        # 退出登录
        st.markdown("---")
        if st.button("🚪 退出登录", use_container_width=True, key="logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()


def init_knowledge_base():
    """初始化知识库"""
    with st.spinner("📖 正在处理PDF并构建知识库..."):
        try:
            processor = PDFProcessor()
            if not processor.open_pdf():
                st.error("无法打开PDF文件")
                return
            
            text = processor.extract_chapter_text()
            if not text:
                st.error("无法提取章节内容")
                return
            
            chunks = processor.create_chunks()
            processor.close()
            
            if not chunks:
                st.error("没有生成任何文本块")
                return
            
            st.session_state.rag_engine.clear_database()
            st.session_state.rag_engine.add_documents(chunks)
            st.session_state.db_initialized = True
            
            st.success(f"✅ 知识库初始化完成！共添加 {len(chunks)} 个文档块")
            st.rerun()
            
        except Exception as e:
            st.error(f"初始化失败: {e}")


# ============== 仪表板页面 ==============
def render_dashboard():
    """渲染仪表板页面"""
    st.markdown("""
    <div class="page-header fade-in">
        <h1 class="main-title">📊 学习仪表板</h1>
        <p class="subtitle">欢迎回来，开始今天的学习之旅</p>
    </div>
    """, unsafe_allow_html=True)
    
    current_time = datetime.now()
    greeting = "早上好" if current_time.hour < 12 else ("下午好" if current_time.hour < 18 else "晚上好")
    
    st.markdown(f"""
    <div class="dashboard-welcome fade-in">
        <div class="welcome-text">👋 {greeting}，{st.session_state.username or '同学'}！</div>
        <div class="welcome-subtitle">今天是 {current_time.strftime('%Y年%m月%d日')}，让我们一起学习《异常检测》吧！</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 统计卡片
    col1, col2, col3, col4 = st.columns(4)
    
    results = st.session_state.quiz_results
    chat_count = len(st.session_state.chat_history) // 2
    
    with col1:
        st.markdown(f"""
        <div class="stat-card fade-in">
            <div class="stat-icon">💬</div>
            <div class="stat-number">{chat_count}</div>
            <div class="stat-label">问答次数</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card fade-in">
            <div class="stat-icon">📝</div>
            <div class="stat-number">{results["total"]}</div>
            <div class="stat-label">答题数量</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        accuracy = results["correct"] / results["total"] * 100 if results["total"] > 0 else 0
        st.markdown(f"""
        <div class="stat-card fade-in">
            <div class="stat-icon">🎯</div>
            <div class="stat-number">{accuracy:.0f}%</div>
            <div class="stat-label">正确率</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        doc_count = 0
        if st.session_state.rag_engine:
            stats = st.session_state.rag_engine.get_stats()
            doc_count = stats.get("document_count", 0)
        st.markdown(f"""
        <div class="stat-card fade-in">
            <div class="stat-icon">📚</div>
            <div class="stat-number">{doc_count}</div>
            <div class="stat-label">知识块</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 快捷入口
    st.markdown("### 🚀 快捷入口")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="quick-action fade-in">
            <div class="quick-action-icon">💬</div>
            <div class="quick-action-title">智能问答</div>
            <div class="quick-action-desc">基于RAG的精准知识问答</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("开始提问", key="quick_qa", use_container_width=True):
            st.session_state.current_page = "qa"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="quick-action fade-in">
            <div class="quick-action-icon">🗺️</div>
            <div class="quick-action-title">知识导图</div>
            <div class="quick-action-desc">章节知识结构可视化</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("查看导图", key="quick_map", use_container_width=True):
            st.session_state.current_page = "knowledge_map"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="quick-action fade-in">
            <div class="quick-action-icon">📝</div>
            <div class="quick-action-title">交互测试</div>
            <div class="quick-action-desc">检验学习效果</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("开始测试", key="quick_quiz", use_container_width=True):
            st.session_state.current_page = "quiz"
            st.rerun()
    
    # 学习进度
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📈 学习进度")
    
    progress = min(results["total"] * 10, 100) if results["total"] > 0 else 5
    st.markdown(f"""
    <div class="modern-card fade-in">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="color: var(--text-primary); font-weight: 500;">第10章 · 异常检测</span>
            <span style="color: #10b981; font-weight: 600;">{progress}%</span>
        </div>
        <div class="progress-container">
            <div class="progress-bar" style="width: {progress}%;"></div>
        </div>
        <div style="color: var(--text-muted); font-size: 0.85rem; margin-top: 0.5rem;">
            {'继续保持学习热情！' if progress < 50 else '太棒了，已完成大部分内容！' if progress < 100 else '恭喜完成本章学习！'}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============== 问答页面 ==============
def render_qa_page():
    """渲染问答页面"""
    st.markdown("""
    <div class="page-header fade-in">
        <h1 class="main-title">💬 智能问答</h1>
        <p class="subtitle">基于RAG技术的异常检测知识问答</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.db_initialized:
        st.warning("⚠️ 知识库尚未初始化，请先在侧边栏点击「初始化」按钮")
        return
    
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🗑️ 清空对话", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()
    with col2:
        st.session_state.show_sources = st.checkbox("📖 显示引用", value=st.session_state.show_sources)
    
    st.markdown("---")
    
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
                <div style="font-size: 4rem; margin-bottom: 1rem;">💭</div>
                <h3 style="color: var(--text-secondary);">开始你的学习之旅</h3>
                <p>问问关于异常检测的任何问题吧！</p>
                <div style="margin-top: 2rem;">
                    <p style="font-size: 0.9rem;">试试这些问题：</p>
                    <p style="color: #3b82f6;">• 什么是异常检测？</p>
                    <p style="color: #3b82f6;">• LOF算法的原理是什么？</p>
                    <p style="color: #3b82f6;">• 异常检测有哪些应用场景？</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message fade-in" style="justify-content: flex-end;">
                        <div class="chat-bubble user-bubble">
                            {msg["content"]}
                        </div>
                        <div class="chat-avatar user-avatar-chat">🧑‍🎓</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message fade-in">
                        <div class="chat-avatar ai-avatar-chat">🤖</div>
                        <div class="chat-bubble ai-bubble">
                            {msg["content"]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.session_state.show_sources and msg.get("sources"):
                        with st.expander("📖 查看引用来源", expanded=False):
                            for i, source in enumerate(msg["sources"]):
                                if "pdf_page" in source:
                                    page_info = f"PDF第{source['pdf_page']}页，书中P{source['book_page']}页"
                                else:
                                    page_info = f"第{source.get('page', '未知')}页"
                                
                                st.markdown(f"""
                                <div class="source-card">
                                    <div class="source-card-header">
                                        📄 来源 {i+1} · {page_info}
                                    </div>
                                    <div style="color: var(--text-secondary); font-size: 0.9rem;">
                                        {source['preview'][:200]}...
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns([6, 1])
    
    with col1:
        question = st.text_input(
            "输入问题",
            placeholder="请输入关于异常检测的问题...",
            label_visibility="collapsed",
            key="qa_input"
        )
    
    with col2:
        send_btn = st.button("发送 📤", use_container_width=True, key="send_qa")
    
    if send_btn and question:
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })
        
        with st.spinner("🤔 AI助教思考中..."):
            result = st.session_state.rag_engine.ask(question)
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result.get("sources", [])
        })
        
        st.session_state.learning_history.append({
            "type": "qa",
            "question": question,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        
        st.rerun()


# ============== 知识导图页面 ==============
def render_knowledge_map_page():
    """渲染知识导图页面"""
    st.markdown("""
    <div class="page-header fade-in">
        <h1 class="main-title">🗺️ 知识导图</h1>
        <p class="subtitle">第10章异常检测知识结构与学习路径</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not ZHIPUAI_API_KEY:
        st.warning("⚠️ 请先在系统设置中配置智谱AI API Key")
        return
    
    # 功能按钮
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("📋 生成提纲", use_container_width=True, key="gen_outline"):
            with st.spinner("正在生成知识提纲..."):
                outline = st.session_state.knowledge_map.generate_outline()
                st.session_state.current_outline = outline
                st.session_state.outline_history.append({
                    "type": "outline",
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
    
    with col2:
        if st.button("💡 核心概念", use_container_width=True, key="gen_concepts"):
            with st.spinner("正在生成核心概念..."):
                concepts = st.session_state.knowledge_map.generate_key_concepts()
                st.session_state.current_concepts = concepts
    
    with col3:
        if st.button("🛤️ 学习路径", use_container_width=True, key="gen_path"):
            with st.spinner("正在生成学习路径..."):
                path = st.session_state.knowledge_map.generate_learning_path()
                st.session_state.current_path = path
    
    with col4:
        if st.button("🧠 思维导图", use_container_width=True, key="show_mindmap"):
            st.session_state.show_mindmap = True
    
    with col5:
        if st.button("📥 导出PDF", use_container_width=True, key="export_map"):
            st.info("📥 导出功能开发中...")
    
    st.markdown("---")
    
    # 显示内容
    tabs = st.tabs(["📋 知识提纲", "💡 核心概念", "🛤️ 学习路径", "🧠 思维导图"])
    
    with tabs[0]:
        if hasattr(st.session_state, "current_outline") and st.session_state.current_outline:
            st.markdown("""
            <div class="modern-card fade-in">
            """, unsafe_allow_html=True)
            st.markdown(st.session_state.current_outline)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📋</div>
                <p>点击上方「生成提纲」按钮</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tabs[1]:
        if hasattr(st.session_state, "current_concepts") and st.session_state.current_concepts:
            st.markdown("""
            <div class="modern-card fade-in">
            """, unsafe_allow_html=True)
            st.markdown(st.session_state.current_concepts)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
                <div style="font-size: 3rem; margin-bottom: 1rem;">💡</div>
                <p>点击上方「核心概念」按钮</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tabs[2]:
        if hasattr(st.session_state, "current_path") and st.session_state.current_path:
            st.markdown("""
            <div class="modern-card fade-in">
            """, unsafe_allow_html=True)
            st.markdown(st.session_state.current_path)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🛤️</div>
                <p>点击上方「学习路径」按钮</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tabs[3]:
        st.markdown("### 🧠 第10章 异常检测 思维导图")
        
        # 选择导图来源
        mindmap_source = st.radio(
            "选择思维导图来源",
            ["📷 上传图片", "🤖 AI生成 (Mermaid)"],
            horizontal=True,
            key="mindmap_source"
        )
        
        if mindmap_source == "📷 上传图片":
            uploaded_file = st.file_uploader(
                "上传思维导图图片",
                type=["png", "jpg", "jpeg", "gif", "webp"],
                key="mindmap_upload"
            )
            
            if uploaded_file is not None:
                st.markdown("""
                <div class="mindmap-container fade-in">
                """, unsafe_allow_html=True)
                st.image(uploaded_file, caption="第10章 异常检测 思维导图", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # 保存上传的图片路径
                st.session_state.uploaded_mindmap = uploaded_file
            else:
                st.info("💡 请上传第10章异常检测的思维导图图片")
                
        else:  # AI生成
            st.markdown("""
            <div class="modern-card">
                <h4 style="color: var(--text-primary);">📊 异常检测知识结构图 (Mermaid)</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # 使用Mermaid语法生成思维导图
            mermaid_code = """
```mermaid
mindmap
  root((第10章<br>异常检测))
    概述
      定义与应用
      异常类型
        点异常
        上下文异常
        集体异常
      挑战与问题
    统计方法
      参数方法
        基于高斯分布
        混合模型
      非参数方法
        直方图
        核密度估计
    基于邻近度
      基于距离
        k近邻距离
      基于密度
        LOF算法
        局部离群因子
    基于聚类
      基于原型的聚类
      基于密度的聚类
      基于图的方法
    分类方法
      一类分类
      半监督方法
      过采样/欠采样
    评估
      评价指标
        精确率/召回率
        ROC曲线
        AUC
      交叉验证
```
            """
            st.markdown(mermaid_code)
            
            st.markdown("---")
            st.markdown("#### 📝 详细知识点结构")
            
            # 以树状结构展示
            st.markdown("""
            <div class="modern-card">
            
**🔹 10.1 异常检测概述**
- 什么是异常/离群点
- 异常的成因
- 异常检测的应用领域
- 异常检测的主要挑战

**🔹 10.2 异常类型**
- 点异常 (Point Anomalies)
- 上下文异常 (Contextual Anomalies)  
- 集体异常 (Collective Anomalies)

**🔹 10.3 统计学方法**
- 参数方法：基于正态分布
- 非参数方法：直方图、核密度估计
- 优缺点分析

**🔹 10.4 基于邻近度的方法**
- 基于距离的异常检测
- 基于密度的异常检测
- **LOF (Local Outlier Factor) 算法** ⭐
- k-距离与可达距离

**🔹 10.5 基于聚类的方法**
- 簇分析中的异常
- DBSCAN与噪声点
- 基于原型的方法

**🔹 10.6 分类方法**
- 一类分类器 (One-Class SVM)
- 半监督异常检测
- 类别不平衡处理

**🔹 10.7 评估方法**
- 混淆矩阵
- 精确率、召回率、F1分数
- ROC曲线与AUC值
            
            </div>
            """, unsafe_allow_html=True)


# ============== 交互测试页面 ==============
def render_quiz_page():
    """渲染测试页面"""
    st.markdown("""
    <div class="page-header fade-in">
        <h1 class="main-title">📝 交互测试</h1>
        <p class="subtitle">检验你对异常检测的理解</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not ZHIPUAI_API_KEY:
        st.warning("⚠️ 请先在系统设置中配置智谱AI API Key")
        return
    
    st.markdown("### 🎯 测试设置")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        quiz_mode = st.selectbox(
            "测试模式",
            ["章节测试", "随机测试", "错题重做"],
            key="quiz_mode"
        )
    
    with col2:
        quiz_type = st.selectbox(
            "题目类型",
            ["随机", "选择题", "判断题", "简答题"],
            key="quiz_type"
        )
    
    with col3:
        topic = st.text_input(
            "知识点(可选)",
            placeholder="如：LOF算法",
            key="quiz_topic"
        )
    
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        generate_btn = st.button("🎲 生成题目", use_container_width=True, key="gen_quiz")
    
    st.markdown("---")
    
    if generate_btn:
        with st.spinner("🎲 正在生成题目..."):
            quiz = st.session_state.quiz_generator.generate_quiz(
                topic=topic if topic else None,
                quiz_type=quiz_type
            )
            if "error" not in quiz:
                st.session_state.current_quiz = quiz
                st.session_state.quiz_answered = False
            else:
                st.error(f"生成失败: {quiz.get('error', '未知错误')}")
    
    if st.session_state.current_quiz:
        quiz = st.session_state.current_quiz
        
        results = st.session_state.quiz_results
        col1, col2 = st.columns([3, 1])
        with col1:
            progress = (results["total"] % 10 + 1) / 10 * 100
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <span style="color: var(--text-secondary);">进度</span>
                <div class="progress-container" style="flex: 1;">
                    <div class="progress-bar" style="width: {progress}%;"></div>
                </div>
                <span style="color: #10b981; font-weight: 600;">{results['total'] % 10 + 1}/10</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="text-align: right;">
                <span class="badge badge-info">正确: {results['correct']}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="quiz-card fade-in">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                <span class="badge badge-info">{quiz.get('type', '题目')}</span>
            </div>
            <div class="quiz-question">{quiz.get('question', '')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if quiz.get("options"):
            st.markdown("#### 选项")
            for opt in quiz["options"]:
                st.markdown(f"""
                <div class="quiz-option">
                    {opt}
                </div>
                """, unsafe_allow_html=True)
        
        if not st.session_state.get("quiz_answered", False):
            st.markdown("#### ✍️ 你的答案")
            answer = st.text_input("", placeholder="请输入你的答案...", key="quiz_answer", label_visibility="collapsed")
            
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("✅ 提交答案", use_container_width=True, key="submit_quiz"):
                    if answer:
                        result = st.session_state.quiz_generator.check_answer(quiz, answer)
                        st.session_state.quiz_result = result
                        st.session_state.quiz_answered = True
                        
                        st.session_state.quiz_results["total"] += 1
                        if result["correct"]:
                            st.session_state.quiz_results["correct"] += 1
                        
                        st.session_state.quiz_history.append({
                            "question": quiz.get('question', ''),
                            "answer": answer,
                            "correct": result["correct"],
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        
                        st.rerun()
                    else:
                        st.warning("请输入答案")
        
        if st.session_state.get("quiz_answered", False):
            result = st.session_state.quiz_result
            
            if result["correct"]:
                st.markdown("""
                <div style="
                    background: rgba(34, 197, 94, 0.1);
                    border: 1px solid rgba(34, 197, 94, 0.3);
                    border-radius: 12px;
                    padding: 1rem;
                    text-align: center;
                    margin: 1rem 0;
                ">
                    <span style="font-size: 2rem;">🎉</span>
                    <h3 style="color: #22c55e; margin: 0.5rem 0;">回答正确！</h3>
                    <p style="color: var(--text-secondary);">太棒了，继续保持！</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    background: rgba(239, 68, 68, 0.1);
                    border: 1px solid rgba(239, 68, 68, 0.3);
                    border-radius: 12px;
                    padding: 1rem;
                    text-align: center;
                    margin: 1rem 0;
                ">
                    <span style="font-size: 2rem;">😅</span>
                    <h3 style="color: #ef4444; margin: 0.5rem 0;">回答错误</h3>
                    <p style="color: var(--text-secondary);">正确答案是：<strong>{result['correct_answer']}</strong></p>
                </div>
                """, unsafe_allow_html=True)
            
            with st.expander("📖 查看解析", expanded=True):
                st.markdown(f"""
                <div class="modern-card">
                    {result["explanation"]}
                </div>
                """, unsafe_allow_html=True)
            
            if st.button("➡️ 下一题", use_container_width=False, key="next_quiz"):
                st.session_state.current_quiz = None
                st.session_state.quiz_answered = False
                st.rerun()
    else:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📝</div>
            <h3 style="color: var(--text-secondary);">准备好测试了吗？</h3>
            <p>点击上方「生成题目」开始答题</p>
        </div>
        """, unsafe_allow_html=True)


# ============== 学习历史页面 ==============
def render_history_page():
    """渲染学习历史页面"""
    st.markdown("""
    <div class="page-header fade-in">
        <h1 class="main-title">📜 学习历史</h1>
        <p class="subtitle">回顾你的学习足迹</p>
    </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs(["💬 问答历史", "📝 测试记录", "🗺️ 导图记录"])
    
    with tabs[0]:
        if st.session_state.learning_history:
            for item in reversed(st.session_state.learning_history[-20:]):
                st.markdown(f"""
                <div class="history-item fade-in">
                    <div class="history-content">
                        <div class="history-title">💬 {item.get('question', '未知问题')[:50]}...</div>
                        <div class="history-meta">{item.get('time', '')}</div>
                    </div>
                    <span class="badge badge-success">已完成</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
                <div style="font-size: 3rem; margin-bottom: 1rem;">💬</div>
                <p>暂无问答记录</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tabs[1]:
        if st.session_state.quiz_history:
            for item in reversed(st.session_state.quiz_history[-20:]):
                badge_class = "badge-success" if item.get('correct') else "badge-error"
                badge_text = "正确" if item.get('correct') else "错误"
                st.markdown(f"""
                <div class="history-item fade-in">
                    <div class="history-content">
                        <div class="history-title">📝 {item.get('question', '未知题目')[:50]}...</div>
                        <div class="history-meta">{item.get('time', '')}</div>
                    </div>
                    <span class="badge {badge_class}">{badge_text}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📝</div>
                <p>暂无测试记录</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tabs[2]:
        if st.session_state.outline_history:
            for item in reversed(st.session_state.outline_history[-10:]):
                st.markdown(f"""
                <div class="history-item fade-in">
                    <div class="history-content">
                        <div class="history-title">🗺️ 知识{item.get('type', '导图')}</div>
                        <div class="history-meta">{item.get('time', '')}</div>
                    </div>
                    <span class="badge badge-info">已生成</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🗺️</div>
                <p>暂无导图记录</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("🗑️ 清空所有历史", key="clear_history"):
        st.session_state.learning_history = []
        st.session_state.quiz_history = []
        st.session_state.outline_history = []
        st.success("已清空所有历史记录")
        st.rerun()


# ============== 系统设置页面 ==============
def render_settings_page():
    """渲染系统设置页面"""
    st.markdown("""
    <div class="page-header fade-in">
        <h1 class="main-title">⚙️ 系统设置</h1>
        <p class="subtitle">个性化你的学习体验</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API设置
    st.markdown("### 🔑 大模型 API 设置")
    st.markdown("""
    <div class="modern-card">
    """, unsafe_allow_html=True)
    
    # 选择大模型提供商
    col1, col2 = st.columns(2)
    
    with col1:
        provider = st.selectbox(
            "选择大模型提供商",
            list(LLM_PROVIDERS.keys()),
            index=list(LLM_PROVIDERS.keys()).index(st.session_state.selected_provider),
            key="llm_provider"
        )
        st.session_state.selected_provider = provider
    
    with col2:
        models = LLM_PROVIDERS[provider]["models"]
        model = st.selectbox(
            "选择模型",
            models,
            index=0,
            key="llm_model"
        )
        st.session_state.selected_model = model
    
    st.markdown("---")
    
    # API Key 输入
    provider_config = LLM_PROVIDERS[provider]
    current_key = st.session_state.api_keys.get(provider, "") or os.environ.get(provider_config["env_key"], "")
    
    api_key = st.text_input(
        f"{provider} API Key",
        value=current_key,
        type="password",
        placeholder=provider_config["placeholder"],
        key="api_key_input"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("💾 保存 API Key", use_container_width=True, key="save_api"):
            if api_key:
                st.session_state.api_keys[provider] = api_key
                os.environ[provider_config["env_key"]] = api_key
                st.success(f"✅ {provider} API Key 已保存！")
            else:
                st.warning("请输入 API Key")
    
    # 显示已配置的API状态
    st.markdown("#### 📊 API 配置状态")
    for prov, config in LLM_PROVIDERS.items():
        key_exists = bool(st.session_state.api_keys.get(prov) or os.environ.get(config["env_key"]))
        status_icon = "✅" if key_exists else "❌"
        status_text = "已配置" if key_exists else "未配置"
        st.markdown(f"- {prov}: {status_icon} {status_text}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 界面设置
    st.markdown("### 🎨 界面设置")
    st.markdown("""
    <div class="modern-card">
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        theme_options = ["暗色模式", "明亮模式"]
        current_theme_idx = 0 if st.session_state.theme == "dark" else 1
        theme = st.selectbox(
            "主题模式",
            theme_options,
            index=current_theme_idx,
            key="settings_theme"
        )
        
        if st.button("应用主题", key="apply_theme"):
            st.session_state.theme = "dark" if theme == "暗色模式" else "light"
            st.success(f"已切换到{theme}")
            st.rerun()
    
    with col2:
        language = st.selectbox(
            "界面语言",
            ["中文", "English"],
            index=0,
            key="settings_language"
        )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 学习提醒
    st.markdown("### 🔔 学习提醒")
    st.markdown("""
    <div class="modern-card">
    """, unsafe_allow_html=True)
    
    reminder_enabled = st.checkbox("开启每日学习提醒", value=False)
    if reminder_enabled:
        reminder_time = st.time_input("提醒时间", value=None)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 关于系统
    st.markdown("### ℹ️ 关于系统")
    st.markdown("""
    <div class="modern-card">
        <h4 style="color: var(--text-primary);">AI助教系统 v2.0</h4>
        <p style="color: var(--text-secondary);">基于《数据挖掘导论》第10章 - 异常检测</p>
        <br>
        <p style="color: var(--text-muted); font-size: 0.9rem;">
            <strong>技术栈：</strong><br>
            • 大模型：智谱AI GLM-4 / OpenAI GPT-4 / 百度文心 / 阿里通义<br>
            • 向量化：智谱AI Embedding-3<br>
            • 向量库：ChromaDB<br>
            • 前端框架：Streamlit<br>
            • PDF解析：PyMuPDF
        </p>
        <br>
        <p style="color: var(--text-muted); font-size: 0.9rem;">
            <strong>登录凭据：</strong><br>
            • 用户名: 10001 / 密码: 123456<br>
            • 用户名: admin / 密码: admin123
        </p>
        <br>
        <p style="color: var(--text-muted); font-size: 0.85rem;">
            © 2025 AI编程与Python数据科学实践
        </p>
    </div>
    """, unsafe_allow_html=True)


# ============== 主函数 ==============
def main():
    """主函数"""
    init_session_state()
    load_modern_css()
    
    # 未登录显示登录页面
    if not st.session_state.logged_in:
        render_login_page()
        return
    
    # 初始化系统组件
    if st.session_state.rag_engine is None:
        with st.spinner("🔄 正在初始化系统..."):
            initialize_system()
    
    # 渲染侧边栏
    render_sidebar()
    
    # 根据当前页面渲染内容
    page = st.session_state.current_page
    
    if page == "dashboard":
        render_dashboard()
    elif page == "qa":
        render_qa_page()
    elif page == "knowledge_map":
        render_knowledge_map_page()
    elif page == "quiz":
        render_quiz_page()
    elif page == "history":
        render_history_page()
    elif page == "settings":
        render_settings_page()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
