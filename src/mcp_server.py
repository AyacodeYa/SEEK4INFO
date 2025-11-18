"""
MCP服务器实现 - Offer匹配器的核心服务
"""
import asyncio
from typing import Any, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from loguru import logger

from src.scrapers.company_scraper import CompanyScraper
from src.parsers.resume_parser import ResumeParser
from src.ai.matcher import OfferMatcher
from config import settings


class OfferMatcherServer:
    """Offer匹配器MCP服务器"""
    
    def __init__(self):
        self.server = Server("offer-matcher")
        self.company_scraper = CompanyScraper()
        self.resume_parser = ResumeParser()
        self.matcher = OfferMatcher()
        
        # 注册工具
        self._register_tools()
        
    def _register_tools(self):
        """注册MCP工具"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """列出所有可用工具"""
            return [
                Tool(
                    name="scrape_company_info",
                    description="爬取指定公司的官网信息，包括公司介绍、招聘信息、员工待遇等",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "company_name": {
                                "type": "string",
                                "description": "公司名称，如'腾讯'、'阿里巴巴'"
                            },
                            "company_url": {
                                "type": "string",
                                "description": "公司官网URL（可选）"
                            },
                            "include_recruitment": {
                                "type": "boolean",
                                "description": "是否包含招聘信息",
                                "default": True
                            }
                        },
                        "required": ["company_name"]
                    }
                ),
                Tool(
                    name="parse_resume",
                    description="解析用户简历，提取关键信息如技能、经验、教育背景等",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "resume_path": {
                                "type": "string",
                                "description": "简历文件路径（支持PDF、Word）"
                            },
                            "resume_text": {
                                "type": "string",
                                "description": "简历文本内容（可选，与resume_path二选一）"
                            }
                        }
                    }
                ),
                Tool(
                    name="analyze_job_match",
                    description="分析岗位与个人的匹配度，提供详细的评分和建议",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "resume_data": {
                                "type": "object",
                                "description": "简历数据（由parse_resume返回）"
                            },
                            "job_description": {
                                "type": "string",
                                "description": "岗位描述"
                            },
                            "company_info": {
                                "type": "object",
                                "description": "公司信息（由scrape_company_info返回）"
                            },
                            "user_preferences": {
                                "type": "object",
                                "description": "用户偏好（期望薪资、工作地点、加班接受度等）",
                                "properties": {
                                    "expected_salary": {"type": "string"},
                                    "location": {"type": "string"},
                                    "overtime_acceptable": {"type": "boolean"}
                                }
                            }
                        },
                        "required": ["resume_data", "job_description"]
                    }
                ),
                Tool(
                    name="recommend_positions",
                    description="推荐公司内更适合的岗位",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "resume_data": {
                                "type": "object",
                                "description": "简历数据"
                            },
                            "company_info": {
                                "type": "object",
                                "description": "公司信息（包含所有招聘岗位）"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "返回top K个推荐岗位",
                                "default": 3
                            }
                        },
                        "required": ["resume_data", "company_info"]
                    }
                ),
                Tool(
                    name="generate_report",
                    description="生成完整的匹配分析报告",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "match_result": {
                                "type": "object",
                                "description": "匹配分析结果"
                            },
                            "format": {
                                "type": "string",
                                "enum": ["markdown", "pdf", "html"],
                                "description": "报告格式",
                                "default": "markdown"
                            }
                        },
                        "required": ["match_result"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
            """调用工具"""
            try:
                logger.info(f"调用工具: {name}, 参数: {arguments}")
                
                if name == "scrape_company_info":
                    result = await self._scrape_company_info(arguments)
                elif name == "parse_resume":
                    result = await self._parse_resume(arguments)
                elif name == "analyze_job_match":
                    result = await self._analyze_job_match(arguments)
                elif name == "recommend_positions":
                    result = await self._recommend_positions(arguments)
                elif name == "generate_report":
                    result = await self._generate_report(arguments)
                else:
                    result = {"error": f"未知工具: {name}"}
                
                return [TextContent(type="text", text=str(result))]
                
            except Exception as e:
                logger.error(f"工具调用失败: {name}, 错误: {e}")
                return [TextContent(type="text", text=f"错误: {str(e)}")]
    
    async def _scrape_company_info(self, args: dict) -> dict:
        """爬取公司信息"""
        company_name = args["company_name"]
        company_url = args.get("company_url")
        include_recruitment = args.get("include_recruitment", True)
        
        logger.info(f"开始爬取公司信息: {company_name}")
        
        result = await self.company_scraper.scrape(
            company_name=company_name,
            url=company_url,
            include_recruitment=include_recruitment
        )
        
        return result
    
    async def _parse_resume(self, args: dict) -> dict:
        """解析简历"""
        resume_path = args.get("resume_path")
        resume_text = args.get("resume_text")
        
        if not resume_path and not resume_text:
            return {"error": "必须提供resume_path或resume_text之一"}
        
        logger.info(f"开始解析简历: {resume_path or '文本输入'}")
        
        if resume_path:
            result = await self.resume_parser.parse_file(resume_path)
        else:
            result = await self.resume_parser.parse_text(resume_text)
        
        return result
    
    async def _analyze_job_match(self, args: dict) -> dict:
        """分析岗位匹配度"""
        resume_data = args["resume_data"]
        job_description = args["job_description"]
        company_info = args.get("company_info", {})
        user_preferences = args.get("user_preferences", {})
        
        logger.info("开始分析岗位匹配度")
        
        result = await self.matcher.analyze_match(
            resume_data=resume_data,
            job_description=job_description,
            company_info=company_info,
            user_preferences=user_preferences
        )
        
        return result
    
    async def _recommend_positions(self, args: dict) -> dict:
        """推荐岗位"""
        resume_data = args["resume_data"]
        company_info = args["company_info"]
        top_k = args.get("top_k", 3)
        
        logger.info(f"开始推荐岗位 (top {top_k})")
        
        result = await self.matcher.recommend_positions(
            resume_data=resume_data,
            company_info=company_info,
            top_k=top_k
        )
        
        return result
    
    async def _generate_report(self, args: dict) -> dict:
        """生成报告"""
        match_result = args["match_result"]
        format_type = args.get("format", "markdown")
        
        logger.info(f"生成报告，格式: {format_type}")
        
        result = await self.matcher.generate_report(
            match_result=match_result,
            format_type=format_type
        )
        
        return result
    
    async def run(self):
        """启动MCP服务器"""
        logger.info("启动Offer匹配器MCP服务器...")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """主函数"""
    server = OfferMatcherServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
