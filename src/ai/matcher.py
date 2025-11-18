"""
Offer匹配分析模块 - 使用Ollama本地模型
"""
import json
from typing import Dict, Any, List
from loguru import logger

from .ollama_client import OllamaClient
from .prompts import (
    MATCH_ANALYSIS_PROMPT,
    POSITION_RECOMMENDATION_PROMPT,
    REPORT_GENERATION_PROMPT
)
from config import settings


class OfferMatcher:
    """Offer匹配分析器"""
    
    def __init__(self):
        self.ollama = OllamaClient()
    
    async def analyze_match(
        self,
        resume_data: Dict[str, Any],
        job_description: str,
        company_info: Dict[str, Any],
        user_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        分析岗位匹配度
        
        Args:
            resume_data: 简历数据
            job_description: 岗位描述
            company_info: 公司信息
            user_preferences: 用户偏好
        
        Returns:
            匹配分析结果
        """
        try:
            # 检查模型是否可用
            if not await self.ollama.check_model():
                return {
                    "error": "Ollama模型不可用，请确保Ollama服务正在运行并已下载模型"
                }
            
            # 构建提示词
            prompt = MATCH_ANALYSIS_PROMPT.format(
                resume_skills=", ".join(resume_data.get("skills", [])),
                resume_experience=self._format_experience(resume_data.get("work_experience", [])),
                resume_education=self._format_education(resume_data.get("education", [])),
                job_description=job_description,
                company_name=company_info.get("company_name", "未知公司"),
                company_description=company_info.get("basic_info", {}).get("description", ""),
                expected_salary=user_preferences.get("expected_salary", ""),
                location=user_preferences.get("location", ""),
                overtime_acceptable="接受" if user_preferences.get("overtime_acceptable") else "不接受"
            )
            
            # 调用Ollama生成分析
            logger.info("开始AI匹配分析...")
            response = await self.ollama.generate(
                prompt=prompt,
                temperature=settings.OLLAMA_TEMPERATURE,
                max_tokens=settings.OLLAMA_MAX_TOKENS
            )
            
            # 解析响应
            result = self._parse_analysis_response(response)
            
            logger.info("匹配分析完成")
            return result
            
        except Exception as e:
            logger.error(f"匹配分析失败: {e}")
            return {"error": str(e)}
    
    async def recommend_positions(
        self,
        resume_data: Dict[str, Any],
        company_info: Dict[str, Any],
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        推荐更适合的岗位
        
        Args:
            resume_data: 简历数据
            company_info: 公司信息
            top_k: 返回top K个推荐
        
        Returns:
            推荐结果
        """
        try:
            positions = company_info.get("positions", [])
            
            if not positions:
                return {
                    "recommendations": [],
                    "message": "该公司暂无招聘岗位信息"
                }
            
            # 构建提示词
            prompt = POSITION_RECOMMENDATION_PROMPT.format(
                resume_skills=", ".join(resume_data.get("skills", [])),
                resume_experience=self._format_experience(resume_data.get("work_experience", [])),
                positions=self._format_positions(positions),
                top_k=top_k
            )
            
            logger.info(f"开始推荐岗位 (top {top_k})...")
            response = await self.ollama.generate(
                prompt=prompt,
                temperature=0.5,  # 降低温度，使推荐更稳定
                max_tokens=1024
            )
            
            result = self._parse_recommendation_response(response, positions)
            
            logger.info("岗位推荐完成")
            return result
            
        except Exception as e:
            logger.error(f"岗位推荐失败: {e}")
            return {"error": str(e)}
    
    async def generate_report(
        self,
        match_result: Dict[str, Any],
        format_type: str = "markdown"
    ) -> Dict[str, Any]:
        """
        生成匹配分析报告
        
        Args:
            match_result: 匹配分析结果
            format_type: 报告格式（markdown/pdf/html）
        
        Returns:
            报告内容
        """
        try:
            if format_type == "markdown":
                report = self._generate_markdown_report(match_result)
            elif format_type == "pdf":
                # TODO: 实现PDF生成
                report = "PDF格式暂未实现"
            elif format_type == "html":
                # TODO: 实现HTML生成
                report = "HTML格式暂未实现"
            else:
                report = f"不支持的格式: {format_type}"
            
            return {
                "format": format_type,
                "content": report
            }
            
        except Exception as e:
            logger.error(f"生成报告失败: {e}")
            return {"error": str(e)}
    
    def _format_experience(self, experiences: List[Dict]) -> str:
        """格式化工作经验"""
        if not experiences:
            return "无工作经验"
        
        formatted = []
        for exp in experiences:
            company = exp.get("company", "")
            position = exp.get("position", "")
            duration = exp.get("duration", "")
            formatted.append(f"{company} - {position} ({duration})")
        
        return "\n".join(formatted)
    
    def _format_education(self, education: List[Dict]) -> str:
        """格式化教育背景"""
        if not education:
            return "未提供教育背景"
        
        formatted = []
        for edu in education:
            school = edu.get("school", "")
            degree = edu.get("degree", "")
            major = edu.get("major", "")
            formatted.append(f"{school} - {degree} - {major}")
        
        return "\n".join(formatted)
    
    def _format_positions(self, positions: List[Dict]) -> str:
        """格式化岗位列表"""
        formatted = []
        for i, pos in enumerate(positions, 1):
            title = pos.get("title", "")
            requirements = pos.get("requirements", [])
            salary = pos.get("salary", "")
            
            formatted.append(f"{i}. {title}")
            formatted.append(f"   薪资: {salary}")
            formatted.append(f"   要求: {', '.join(requirements[:3])}")
            formatted.append("")
        
        return "\n".join(formatted)
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """解析匹配分析响应"""
        # 尝试从响应中提取结构化信息
        result = {
            "overall_score": 0,
            "detailed_scores": {},
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "decision": "",
            "raw_analysis": response
        }
        
        # 简单的模式匹配提取分数
        import re
        
        # 提取总分
        score_match = re.search(r'总分[：:]\s*(\d+)', response)
        if score_match:
            result["overall_score"] = int(score_match.group(1))
        
        # 提取优势
        strengths_match = re.search(r'优势[：:](.+?)(?=劣势|风险|建议|$)', response, re.DOTALL)
        if strengths_match:
            strengths_text = strengths_match.group(1)
            result["strengths"] = [s.strip() for s in strengths_text.split('\n') if s.strip() and not s.strip().startswith('-')]
        
        # 提取建议
        recommendations_match = re.search(r'建议[：:](.+?)(?=决策|$)', response, re.DOTALL)
        if recommendations_match:
            rec_text = recommendations_match.group(1)
            result["recommendations"] = [r.strip() for r in rec_text.split('\n') if r.strip() and not r.strip().startswith('-')]
        
        return result
    
    def _parse_recommendation_response(
        self,
        response: str,
        positions: List[Dict]
    ) -> Dict[str, Any]:
        """解析推荐响应"""
        result = {
            "recommendations": [],
            "raw_response": response
        }
        
        # TODO: 更智能的解析逻辑
        # 现在简单返回前3个岗位
        for pos in positions[:3]:
            result["recommendations"].append({
                "title": pos.get("title", ""),
                "match_score": 80,  # 默认分数
                "reason": "基于技能匹配"
            })
        
        return result
    
    def _generate_markdown_report(self, match_result: Dict[str, Any]) -> str:
        """生成Markdown格式报告"""
        score = match_result.get("overall_score", 0)
        strengths = match_result.get("strengths", [])
        weaknesses = match_result.get("weaknesses", [])
        recommendations = match_result.get("recommendations", [])
        
        report = f"""# Offer匹配分析报告

## 📊 综合匹配度：{score}/100

---

## ✅ 优势项

"""
        for strength in strengths:
            report += f"- {strength}\n"
        
        report += "\n## ⚠️ 风险项\n\n"
        for weakness in weaknesses:
            report += f"- {weakness}\n"
        
        report += "\n## 💡 建议\n\n"
        for rec in recommendations:
            report += f"- {rec}\n"
        
        report += "\n---\n\n"
        report += match_result.get("raw_analysis", "")
        
        return report
