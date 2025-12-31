"""
交互式测试生成模块
负责生成测试题并进行互动问答
"""

import json
import random
from typing import List, Dict, Optional

from zhipuai import ZhipuAI

from config import ZHIPUAI_API_KEY, LLM_MODEL, QUIZ_PROMPT


class QuizGenerator:
    """测试题生成器"""
    
    def __init__(self, rag_engine=None):
        self.rag_engine = rag_engine
        self.zhipu_client = None
        self.quiz_history = []  # 记录已生成的题目
        self._init_zhipu()
    
    def _init_zhipu(self):
        """初始化智谱AI客户端"""
        if ZHIPUAI_API_KEY:
            self.zhipu_client = ZhipuAI(api_key=ZHIPUAI_API_KEY)
    
    def generate_quiz(self, topic: Optional[str] = None, quiz_type: str = "随机") -> Dict:
        """
        生成一道测试题
        topic: 指定知识点主题，None则随机选择
        quiz_type: "选择题" / "判断题" / "简答题" / "随机"
        """
        if not self.zhipu_client:
            return {"error": "智谱AI客户端未初始化"}
        
        # 从知识库获取相关内容
        if self.rag_engine and topic:
            docs = self.rag_engine.search(topic, top_k=3)
            if docs:
                knowledge_content = "\n\n".join([doc["text"] for doc in docs])
            else:
                knowledge_content = self._get_default_content()
        else:
            knowledge_content = self._get_default_content()
        
        # 确定题目类型
        if quiz_type == "随机":
            quiz_type = random.choice(["选择题", "判断题", "简答题"])
        
        prompt = QUIZ_PROMPT + knowledge_content + f"\n\n请生成一道{quiz_type}。"
        
        try:
            response = self.zhipu_client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的数据挖掘课程出题专家，擅长设计有针对性的测试题目。请严格按照JSON格式输出。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # 尝试解析JSON
            quiz = self._parse_quiz_response(content)
            
            if quiz:
                self.quiz_history.append(quiz)
                return quiz
            else:
                return {"error": "无法解析生成的题目", "raw": content}
        
        except Exception as e:
            return {"error": f"生成题目失败: {e}"}
    
    def _parse_quiz_response(self, content: str) -> Optional[Dict]:
        """解析AI返回的题目JSON"""
        try:
            # 尝试直接解析
            return json.loads(content)
        except json.JSONDecodeError:
            # 尝试提取JSON部分
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
        return None
    
    def _get_default_content(self) -> str:
        """获取默认的异常检测知识内容"""
        return """
异常检测（Anomaly Detection）是数据挖掘中的重要任务，用于识别数据集中不符合预期模式的数据点。

主要内容包括：
1. 异常的类型：
   - 全局异常：与整个数据集明显不同的数据点
   - 上下文异常：在特定上下文中异常的数据点
   - 集体异常：一组数据点作为整体表现异常

2. 异常检测方法：
   - 统计方法：基于数据分布建模，假设正常数据符合某种分布
   - 基于邻近度的方法：基于距离或密度判断异常
   - 基于聚类的方法：将不属于任何簇的点视为异常

3. 评估指标：
   - 准确率、召回率、F1分数
   - ROC曲线和AUC值
"""
    
    def check_answer(self, quiz: Dict, user_answer: str) -> Dict:
        """
        检查用户答案
        返回: {"correct": bool, "feedback": str}
        """
        correct_answer = quiz.get("answer", "")
        quiz_type = quiz.get("type", "")
        
        # 标准化答案比较
        user_answer_clean = user_answer.strip().upper()
        correct_answer_clean = correct_answer.strip().upper()
        
        if quiz_type == "选择题":
            # 提取选项字母
            user_letter = user_answer_clean[0] if user_answer_clean else ""
            correct_letter = correct_answer_clean[0] if correct_answer_clean else ""
            is_correct = user_letter == correct_letter
        elif quiz_type == "判断题":
            # 判断对错
            user_bool = user_answer_clean in ["对", "正确", "TRUE", "T", "是", "Y", "YES"]
            correct_bool = correct_answer_clean in ["对", "正确", "TRUE", "T", "是", "Y", "YES"]
            is_correct = user_bool == correct_bool
        else:
            # 简答题需要AI评判
            is_correct = self._evaluate_open_answer(quiz, user_answer)
        
        feedback = quiz.get("explanation", "暂无解析")
        
        return {
            "correct": is_correct,
            "correct_answer": correct_answer,
            "explanation": feedback,
            "feedback": "✅ 回答正确！" if is_correct else f"❌ 回答错误。正确答案是：{correct_answer}"
        }
    
    def _evaluate_open_answer(self, quiz: Dict, user_answer: str) -> bool:
        """使用AI评估简答题答案"""
        if not self.zhipu_client:
            return False
        
        prompt = f"""请评估学生的简答题回答是否正确。

题目：{quiz.get('question', '')}
标准答案：{quiz.get('answer', '')}
学生回答：{user_answer}

请只回复"正确"或"错误"。"""

        try:
            response = self.zhipu_client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=10
            )
            result = response.choices[0].message.content.strip()
            return "正确" in result
        except:
            return False
    
    def get_quiz_statistics(self) -> Dict:
        """获取测试统计信息"""
        return {
            "total_quizzes": len(self.quiz_history),
            "quiz_types": {
                "选择题": sum(1 for q in self.quiz_history if q.get("type") == "选择题"),
                "判断题": sum(1 for q in self.quiz_history if q.get("type") == "判断题"),
                "简答题": sum(1 for q in self.quiz_history if q.get("type") == "简答题")
            }
        }


def test_quiz_generator():
    """测试题目生成器"""
    generator = QuizGenerator()
    
    print("生成一道选择题：")
    quiz = generator.generate_quiz(topic="异常检测方法", quiz_type="选择题")
    
    if "error" not in quiz:
        print(f"\n题目类型: {quiz.get('type')}")
        print(f"题目: {quiz.get('question')}")
        if quiz.get('options'):
            for opt in quiz['options']:
                print(f"  {opt}")
        print(f"\n正确答案: {quiz.get('answer')}")
        print(f"解析: {quiz.get('explanation')}")
    else:
        print(f"错误: {quiz}")


if __name__ == "__main__":
    test_quiz_generator()

