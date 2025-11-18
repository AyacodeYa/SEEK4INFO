"""
简历解析模块
"""
import re
import asyncio
from pathlib import Path
from typing import Optional, Union
from loguru import logger

# PDF解析
import PyPDF2
import pdfplumber

# Word解析
from docx import Document

from config import settings


class ResumeParser:
    """简历解析器"""
    
    def __init__(self):
        self.allowed_formats = settings.RESUME_ALLOWED_FORMATS
        self.max_size_mb = settings.RESUME_MAX_SIZE_MB
    
    async def parse_file(self, file_path: str) -> dict:
        """
        解析简历文件
        
        Args:
            file_path: 简历文件路径
        
        Returns:
            解析后的简历数据
        """
        try:
            path = Path(file_path)
            
            # 检查文件是否存在
            if not path.exists():
                return {"error": f"文件不存在: {file_path}"}
            
            # 检查文件大小
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb > self.max_size_mb:
                return {"error": f"文件过大: {size_mb:.2f}MB (最大{self.max_size_mb}MB)"}
            
            # 检查文件格式
            suffix = path.suffix.lower().replace('.', '')
            if suffix not in self.allowed_formats:
                return {"error": f"不支持的文件格式: {suffix}"}
            
            # 根据格式解析
            if suffix == 'pdf':
                text = await self._parse_pdf(path)
            elif suffix in ['docx', 'doc']:
                text = await self._parse_word(path)
            elif suffix == 'txt':
                text = await self._parse_txt(path)
            else:
                return {"error": f"未实现的解析器: {suffix}"}
            
            # 提取结构化信息
            result = await self.parse_text(text)
            result["file_path"] = str(path)
            result["file_format"] = suffix
            
            logger.info(f"成功解析简历: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"解析简历失败: {file_path}, 错误: {e}")
            return {"error": str(e)}
    
    async def parse_text(self, text: str) -> dict:
        """
        解析简历文本
        
        Args:
            text: 简历文本内容
        
        Returns:
            结构化的简历数据
        """
        try:
            result = {
                "raw_text": text,
                "personal_info": self._extract_personal_info(text),
                "education": self._extract_education(text),
                "work_experience": self._extract_work_experience(text),
                "project_experience": self._extract_project_experience(text),
                "skills": self._extract_skills(text),
                "certificates": self._extract_certificates(text),
                "summary": self._extract_summary(text)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"解析简历文本失败: {e}")
            return {"error": str(e), "raw_text": text}
    
    async def _parse_pdf(self, path: Path) -> str:
        """解析PDF文件"""
        try:
            text = ""
            
            # 方法1: 使用pdfplumber（推荐）
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            # 如果pdfplumber失败，尝试PyPDF2
            if not text.strip():
                with open(path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"解析PDF失败: {path}, 错误: {e}")
            return ""
    
    async def _parse_word(self, path: Path) -> str:
        """解析Word文件"""
        try:
            doc = Document(path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            logger.error(f"解析Word失败: {path}, 错误: {e}")
            return ""
    
    async def _parse_txt(self, path: Path) -> str:
        """解析TXT文件"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except UnicodeDecodeError:
            # 尝试其他编码
            with open(path, 'r', encoding='gbk') as f:
                return f.read().strip()
    
    def _extract_personal_info(self, text: str) -> dict:
        """提取个人信息"""
        info = {}
        
        # 提取姓名（通常在开头）
        name_match = re.search(r'姓\s*名[:：]\s*([^\n]+)', text)
        if name_match:
            info["name"] = name_match.group(1).strip()
        
        # 提取电话
        phone_match = re.search(r'1[3-9]\d{9}', text)
        if phone_match:
            info["phone"] = phone_match.group(0)
        
        # 提取邮箱
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            info["email"] = email_match.group(0)
        
        # 提取年龄
        age_match = re.search(r'年\s*龄[:：]\s*(\d+)', text)
        if age_match:
            info["age"] = int(age_match.group(1))
        
        return info
    
    def _extract_education(self, text: str) -> list:
        """提取教育背景"""
        education = []
        
        # 简单的教育信息提取
        # TODO: 改进提取逻辑
        patterns = [
            r'(本科|硕士|博士|大专).*?([^\n]+大学[^\n]*)',
            r'([^\n]+大学[^\n]*).*?(本科|硕士|博士|大专)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                education.append({
                    "degree": match.group(1) if match.group(1) in ['本科', '硕士', '博士', '大专'] else match.group(2),
                    "school": match.group(2) if match.group(1) in ['本科', '硕士', '博士', '大专'] else match.group(1),
                    "major": "",
                    "duration": ""
                })
        
        return education
    
    def _extract_work_experience(self, text: str) -> list:
        """提取工作经验"""
        experiences = []
        
        # TODO: 实现更复杂的工作经验提取逻辑
        # 这里只是示例
        work_section = re.search(r'(工作经[历验]|工作经历)(.+?)(?=教育|项目|技能|$)', text, re.DOTALL)
        if work_section:
            section_text = work_section.group(2)
            # 进一步解析...
        
        return experiences
    
    def _extract_project_experience(self, text: str) -> list:
        """提取项目经验"""
        projects = []
        
        # TODO: 实现项目经验提取
        project_section = re.search(r'(项目经[历验])(.+?)(?=工作|教育|技能|$)', text, re.DOTALL)
        if project_section:
            section_text = project_section.group(2)
            # 进一步解析...
        
        return projects
    
    def _extract_skills(self, text: str) -> list:
        """提取技能列表"""
        skills = []
        
        # 常见技能关键词
        skill_keywords = [
            'Python', 'Java', 'JavaScript', 'C++', 'Go', 'Rust',
            'Django', 'Flask', 'Spring', 'React', 'Vue', 'Angular',
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis',
            'Docker', 'Kubernetes', 'AWS', 'Azure',
            'Git', 'Linux', 'Nginx', 'Kafka'
        ]
        
        for keyword in skill_keywords:
            if re.search(rf'\b{keyword}\b', text, re.IGNORECASE):
                skills.append(keyword)
        
        return skills
    
    def _extract_certificates(self, text: str) -> list:
        """提取证书"""
        certificates = []
        
        # TODO: 实现证书提取
        
        return certificates
    
    def _extract_summary(self, text: str) -> str:
        """提取个人简介"""
        # 提取自我评价或个人简介部分
        summary_match = re.search(
            r'(个人简介|自我评价|个人总结)[:：]\s*([^\n]+(?:\n(?![\u4e00-\u9fa5]+[:：])[^\n]+)*)',
            text,
            re.IGNORECASE
        )
        
        if summary_match:
            return summary_match.group(2).strip()
        
        return ""
