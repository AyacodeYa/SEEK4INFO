"""
命令行客户端 - 用于测试和快速使用
"""
import asyncio
import argparse
from pathlib import Path
from loguru import logger

from src.scrapers.company_scraper import CompanyScraper
from src.parsers.resume_parser import ResumeParser
from src.ai.matcher import OfferMatcher


async def analyze_offer(
    company_name: str,
    resume_path: str,
    job_description: str,
    company_url: str = None
):
    """完整的Offer分析流程"""
    
    print("\n" + "="*60)
    print("🎯 Offer匹配器 - 开始分析")
    print("="*60 + "\n")
    
    # 1. 爬取公司信息
    print("📡 步骤1: 爬取公司信息...")
    scraper = CompanyScraper()
    company_info = await scraper.scrape(
        company_name=company_name,
        url=company_url,
        include_recruitment=True
    )
    
    if "error" in company_info:
        print(f"❌ 爬取失败: {company_info['error']}")
        return
    
    print(f"✅ 公司信息爬取完成: {company_name}")
    print(f"   - 岗位数量: {len(company_info.get('positions', []))}")
    
    # 2. 解析简历
    print(f"\n📄 步骤2: 解析简历...")
    parser = ResumeParser()
    resume_data = await parser.parse_file(resume_path)
    
    if "error" in resume_data:
        print(f"❌ 解析失败: {resume_data['error']}")
        return
    
    print(f"✅ 简历解析完成")
    print(f"   - 技能: {', '.join(resume_data.get('skills', [])[:5])}")
    print(f"   - 工作经验: {len(resume_data.get('work_experience', []))} 条")
    
    # 3. AI匹配分析
    print(f"\n🤖 步骤3: AI匹配分析...")
    matcher = OfferMatcher()
    
    match_result = await matcher.analyze_match(
        resume_data=resume_data,
        job_description=job_description,
        company_info=company_info,
        user_preferences={
            "expected_salary": "15-25K",
            "location": "北京",
            "overtime_acceptable": False
        }
    )
    
    if "error" in match_result:
        print(f"❌ 分析失败: {match_result['error']}")
        return
    
    print(f"✅ 匹配分析完成")
    
    # 4. 生成报告
    print(f"\n📊 步骤4: 生成分析报告...\n")
    report = await matcher.generate_report(match_result, format_type="markdown")
    
    print(report.get("content", ""))
    
    # 5. 岗位推荐
    if company_info.get("positions"):
        print(f"\n🎯 步骤5: 推荐其他岗位...\n")
        recommendations = await matcher.recommend_positions(
            resume_data=resume_data,
            company_info=company_info,
            top_k=3
        )
        
        if recommendations.get("recommendations"):
            print("推荐岗位：")
            for i, rec in enumerate(recommendations["recommendations"], 1):
                print(f"{i}. {rec['title']} - 匹配度: {rec['match_score']}/100")
                print(f"   理由: {rec['reason']}\n")
    
    print("\n" + "="*60)
    print("✨ 分析完成！")
    print("="*60)


async def quick_test():
    """快速测试模式"""
    print("\n🚀 快速测试模式\n")
    
    # 测试Ollama连接
    from src.ai.ollama_client import OllamaClient
    
    client = OllamaClient()
    print("检查Ollama连接...")
    
    if await client.check_model():
        print("✅ Ollama服务正常\n")
        
        # 简单测试
        print("测试生成能力...")
        response = await client.generate(
            prompt="请用一句话介绍什么是Python。",
            temperature=0.7
        )
        print(f"回复: {response}\n")
    else:
        print("❌ Ollama服务不可用")
        print("请确保：")
        print("1. Ollama已安装并运行")
        print("2. 已下载模型（如 llama3.2:3b）")
        print("3. 检查配置文件中的 OLLAMA_BASE_URL 和 OLLAMA_MODEL")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Offer匹配器 - 智能求职决策助手"
    )
    
    parser.add_argument(
        "--mode",
        choices=["analyze", "test"],
        default="test",
        help="运行模式：analyze（完整分析）或 test（快速测试）"
    )
    
    parser.add_argument(
        "--company",
        help="公司名称"
    )
    
    parser.add_argument(
        "--resume",
        help="简历文件路径"
    )
    
    parser.add_argument(
        "--job",
        help="岗位描述（可以是文本或文件路径）"
    )
    
    parser.add_argument(
        "--url",
        help="公司官网URL（可选）"
    )
    
    args = parser.parse_args()
    
    if args.mode == "test":
        asyncio.run(quick_test())
    elif args.mode == "analyze":
        if not all([args.company, args.resume, args.job]):
            print("错误: analyze模式需要提供 --company, --resume 和 --job 参数")
            parser.print_help()
            return
        
        # 读取岗位描述
        job_desc = args.job
        if Path(job_desc).exists():
            with open(job_desc, 'r', encoding='utf-8') as f:
                job_desc = f.read()
        
        asyncio.run(analyze_offer(
            company_name=args.company,
            resume_path=args.resume,
            job_description=job_desc,
            company_url=args.url
        ))


if __name__ == "__main__":
    main()
