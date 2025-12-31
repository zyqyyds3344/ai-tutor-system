"""
PDF处理模块
负责从PDF中提取第10章（异常检测）的内容
使用智谱GLM-4V视觉模型识别扫描件PDF
"""

import re
import io
import base64
import time
from pathlib import Path
from typing import List, Tuple, Optional
import fitz  # PyMuPDF
from PIL import Image
from zhipuai import ZhipuAI

from config import (
    PDF_PATH, 
    CHAPTER_NUMBER, 
    CHUNK_SIZE, 
    CHUNK_OVERLAP,
    CHAPTER_10_START_PAGE,
    CHAPTER_10_END_PAGE,
    ZHIPUAI_API_KEY
)


class PDFProcessor:
    """PDF文档处理器（使用GLM-4V视觉模型识别扫描件）"""
    
    def __init__(self, pdf_path: Path = PDF_PATH):
        self.pdf_path = pdf_path
        self.doc = None
        self.chapter_text = ""
        self.chapter_pages = []
        self.zhipu_client = None
        
        # 使用配置文件中的固定页码（转换为0-based索引）
        self.start_page = CHAPTER_10_START_PAGE - 1  # 419 -> 418
        self.end_page = CHAPTER_10_END_PAGE - 1      # 438 -> 437
        
        # 初始化智谱AI客户端
        self._init_zhipu()
    
    def _init_zhipu(self):
        """初始化智谱AI客户端"""
        if ZHIPUAI_API_KEY:
            self.zhipu_client = ZhipuAI(api_key=ZHIPUAI_API_KEY)
            print("✅ 智谱AI视觉模型已就绪")
        else:
            print("⚠️ 未设置ZHIPUAI_API_KEY，无法使用视觉模型")
        
    def open_pdf(self) -> bool:
        """打开PDF文件"""
        try:
            self.doc = fitz.open(str(self.pdf_path))
            print(f"✅ 成功打开PDF，共 {len(self.doc)} 页")
            return True
        except Exception as e:
            print(f"❌ 打开PDF失败: {e}")
            return False
    
    def get_chapter_pages(self) -> Tuple[int, int]:
        """获取第10章的页码范围"""
        if self.doc:
            total_pages = len(self.doc)
            if self.end_page >= total_pages:
                print(f"⚠️ 结束页码超出范围，调整为最后一页: {total_pages}")
                self.end_page = total_pages - 1
        
        print(f"📖 第10章页码范围:")
        print(f"   起始页: 第{self.start_page + 1}页 (索引: {self.start_page})")
        print(f"   结束页: 第{self.end_page + 1}页 (索引: {self.end_page})")
        print(f"   共计: {self.end_page - self.start_page + 1}页")
        
        self.chapter_pages = list(range(self.start_page, self.end_page + 1))
        return self.start_page, self.end_page
    
    def page_to_base64(self, page_num: int, dpi: int = 150) -> str:
        """将PDF页面转换为base64编码的图片"""
        page = self.doc[page_num]
        
        # 渲染页面为图片
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        
        # 转换为PNG格式的bytes
        img_bytes = pix.tobytes("png")
        
        # 转换为base64
        base64_str = base64.b64encode(img_bytes).decode('utf-8')
        
        return base64_str
    
    def extract_text_from_page_glm4v(self, page_num: int) -> str:
        """使用GLM-4V视觉模型从页面提取文字"""
        if not self.zhipu_client:
            print("❌ 智谱AI客户端未初始化")
            return ""
        
        try:
            # 将页面转换为base64图片
            img_base64 = self.page_to_base64(page_num)
            
            # 调用GLM-4V模型
            response = self.zhipu_client.chat.completions.create(
                model="glm-4.6v",  # 使用glm-4.6v视觉模型
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                }
                            },
                            {
                                "type": "text",
                                "text": """请识别这个PDF页面中的所有文字内容，包括：
1. 正文文字
2. 标题
3. 公式（用文字描述）
4. 图表说明

要求：
- 保持原文的段落结构
- 准确识别中英文混合内容
- 公式尽量用文字或符号表示
- 只输出识别到的文字内容，不要添加任何解释"""
                            }
                        ]
                    }
                ],
                max_tokens=4000
            )
            
            text = response.choices[0].message.content
            return text.strip()
            
        except Exception as e:
            print(f"⚠️ GLM-4V识别失败: {e}")
            return ""
    
    def extract_chapter_text(self) -> str:
        """提取第10章的全部文本（使用GLM-4V视觉模型）"""
        if not self.doc:
            self.open_pdf()
        
        if not self.zhipu_client:
            print("❌ 请先设置ZHIPUAI_API_KEY")
            return ""
        
        start_page, end_page = self.get_chapter_pages()
        
        print(f"\n📖 正在使用GLM-4V识别第10章内容...")
        print(f"   页面范围: 第{start_page + 1}页 - 第{end_page + 1}页")
        print(f"   预计耗时: {(end_page - start_page + 1) * 3}秒左右\n")
        
        chapter_text_parts = []
        total_pages = end_page - start_page + 1
        
        for i, page_num in enumerate(range(start_page, end_page + 1)):
            print(f"   [{i+1}/{total_pages}] 识别第{page_num + 1}页...", end=" ", flush=True)
            
            # 调用GLM-4V识别
            text = self.extract_text_from_page_glm4v(page_num)
            
            if text:
                # 清理文本
                text = self._clean_text(text)
                chapter_text_parts.append(f"[第{page_num + 1}页]\n{text}")
                print(f"✅ {len(text)}字符")
            else:
                print(f"⚠️ 识别失败")
            
            # 添加短暂延迟避免API限流
            if i < total_pages - 1:
                time.sleep(1)
        
        self.chapter_text = "\n\n".join(chapter_text_parts)
        print(f"\n✅ 提取完成，共 {len(self.chapter_text)} 字符")
        
        if self.chapter_text:
            preview = self.chapter_text[:500].replace('\n', ' ')
            print(f"   内容预览: {preview}...")
        
        return self.chapter_text
    
    def _clean_text(self, text: str) -> str:
        """清理提取的文本"""
        if not text:
            return ""
        
        # 移除多余空白
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        return text.strip()
    
    def create_chunks(self, text: Optional[str] = None) -> List[dict]:
        """将文本分割成小块用于向量化"""
        if text is None:
            text = self.chapter_text
        
        if not text:
            text = self.extract_chapter_text()
        
        if not text:
            print("❌ 没有文本可以分块")
            return []
        
        chunks = []
        
        # 按段落分割
        paragraphs = text.split('\n\n')
        current_chunk = ""
        current_page = self.start_page + 1
        chunk_id = 0
        
        for para in paragraphs:
            # 检查是否有页码标记
            page_match = re.search(r'\[第(\d+)页\]', para)
            if page_match:
                current_page = int(page_match.group(1))
                para = re.sub(r'\[第\d+页\]\n?', '', para)
            
            if not para.strip():
                continue
            
            if len(current_chunk) + len(para) < CHUNK_SIZE:
                current_chunk += para + "\n\n"
            else:
                if current_chunk.strip():
                    chunks.append({
                        "text": current_chunk.strip(),
                        "metadata": {
                            "page": current_page,
                            "chunk_id": chunk_id,
                            "chapter": CHAPTER_NUMBER,
                            "source": "数据挖掘导论第10章-异常检测"
                        }
                    })
                    chunk_id += 1
                
                if len(current_chunk) > CHUNK_OVERLAP:
                    overlap_text = current_chunk[-CHUNK_OVERLAP:]
                    current_chunk = overlap_text + para + "\n\n"
                else:
                    current_chunk = para + "\n\n"
        
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "metadata": {
                    "page": current_page,
                    "chunk_id": chunk_id,
                    "chapter": CHAPTER_NUMBER,
                    "source": "数据挖掘导论第10章-异常检测"
                }
            })
        
        print(f"✅ 文本分块完成，共 {len(chunks)} 个块")
        return chunks
    
    def save_text_to_file(self, output_path: Optional[str] = None) -> bool:
        """将提取的文本保存到文件"""
        if not self.chapter_text:
            print("❌ 没有文本可保存，请先运行extract_chapter_text()")
            return False
        
        if output_path is None:
            output_path = Path(__file__).parent / "data" / "chapter_10_text.txt"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.chapter_text)
        
        print(f"💾 文本已保存到: {output_path}")
        return True
    
    def close(self):
        """关闭PDF文档"""
        if self.doc:
            self.doc.close()
            self.doc = None


def test_pdf_processor():
    """测试PDF处理器"""
    print("=" * 60)
    print("   📚 PDF处理器测试 (GLM-4V视觉模型)")
    print("=" * 60)
    
    processor = PDFProcessor()
    
    if not processor.zhipu_client:
        print("\n❌ 请先设置ZHIPUAI_API_KEY环境变量")
        return
    
    processor.open_pdf()
    
    # 只测试第一页
    print("\n测试识别第一页...")
    text = processor.extract_text_from_page_glm4v(processor.start_page)
    
    if text:
        print(f"\n识别结果（前1000字符）:")
        print("=" * 60)
        print(text[:1000])
        print("=" * 60)
        print(f"\n✅ 测试成功！总计 {len(text)} 字符")
    else:
        print("\n❌ 识别失败")
    
    processor.close()


if __name__ == "__main__":
    test_pdf_processor()
