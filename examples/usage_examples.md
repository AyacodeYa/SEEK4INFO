# 示例：使用Python脚本调用

本示例展示如何在Python脚本中使用Offer匹配器的各个组件。

## 示例1: 基础使用

```python
import asyncio
from src.scrapers.company_scraper import CompanyScraper
from src.parsers.resume_parser import ResumeParser
from src.ai.matcher import OfferMatcher


async def main():
    """基础使用示例"""
    
    # 1. 爬取公司信息
    print("爬取公司信息...")
    scraper = CompanyScraper()
    company_info = await scraper.scrape(
        company_name="腾讯",
        url="https://www.tencent.com",
        include_recruitment=True
    )
    print(f"公司名称: {company_info['company_name']}")
    print(f"岗位数量: {len(company_info['positions'])}")
    
    # 2. 解析简历
    print("\n解析简历...")
    parser = ResumeParser()
    resume_data = await parser.parse_file("examples/sample_resume.pdf")
    print(f"提取技能: {', '.join(resume_data['skills'][:5])}")
    
    # 3. 匹配分析
    print("\n进行匹配分析...")
    matcher = OfferMatcher()
    
    job_description = """
    岗位：Python后端工程师
    
    职责：
    - 负责后端服务开发和维护
    - 参与系统架构设计
    
    要求：
    - 3年以上Python开发经验
    - 熟悉Django/Flask框架
    - 熟悉MySQL、Redis等数据库
    """
    
    match_result = await matcher.analyze_match(
        resume_data=resume_data,
        job_description=job_description,
        company_info=company_info,
        user_preferences={
            "expected_salary": "20-30K",
            "location": "北京",
            "overtime_acceptable": False
        }
    )
    
    print(f"匹配度: {match_result['overall_score']}/100")
    print(f"优势: {match_result['strengths']}")
    print(f"建议: {match_result['recommendations']}")
    
    # 4. 生成报告
    print("\n生成报告...")
    report = await matcher.generate_report(match_result, format_type="markdown")
    
    # 保存报告
    with open("report.md", "w", encoding="utf-8") as f:
        f.write(report["content"])
    print("报告已保存到 report.md")


if __name__ == "__main__":
    asyncio.run(main())
```

## 示例2: 批量分析多个岗位

```python
import asyncio
from src.ai.matcher import OfferMatcher
from src.parsers.resume_parser import ResumeParser


async def batch_analyze():
    """批量分析多个岗位"""
    
    # 解析简历（只需一次）
    parser = ResumeParser()
    resume_data = await parser.parse_file("examples/sample_resume.pdf")
    
    # 多个岗位
    jobs = [
        {
            "company": "腾讯",
            "position": "Python后端工程师",
            "description": "..."
        },
        {
            "company": "阿里巴巴",
            "position": "Java开发工程师",
            "description": "..."
        },
        {
            "company": "字节跳动",
            "position": "全栈工程师",
            "description": "..."
        }
    ]
    
    matcher = OfferMatcher()
    results = []
    
    # 分析每个岗位
    for job in jobs:
        print(f"\n分析: {job['company']} - {job['position']}")
        
        result = await matcher.analyze_match(
            resume_data=resume_data,
            job_description=job['description'],
            company_info={"company_name": job['company']},
            user_preferences={}
        )
        
        results.append({
            "company": job['company'],
            "position": job['position'],
            "score": result['overall_score'],
            "decision": result.get('decision', '')
        })
    
    # 按匹配度排序
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # 打印结果
    print("\n" + "="*60)
    print("匹配度排名:")
    print("="*60)
    
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['company']} - {r['position']}")
        print(f"   匹配度: {r['score']}/100")
        print(f"   建议: {r['decision']}\n")


if __name__ == "__main__":
    asyncio.run(batch_analyze())
```

## 示例3: 直接使用Ollama客户端

```python
import asyncio
from src.ai.ollama_client import OllamaClient


async def test_ollama():
    """测试Ollama客户端"""
    
    client = OllamaClient()
    
    # 检查模型
    if not await client.check_model():
        print("模型不可用")
        return
    
    # 生成文本
    prompt = "请简要介绍一下Python语言的特点。"
    response = await client.generate(prompt, temperature=0.7)
    print(f"问: {prompt}")
    print(f"答: {response}\n")
    
    # 对话模式
    messages = [
        {"role": "user", "content": "什么是机器学习？"},
        {"role": "assistant", "content": "机器学习是人工智能的一个分支..."},
        {"role": "user", "content": "它有哪些应用？"}
    ]
    
    response = await client.chat(messages)
    print(f"对话回复: {response}")


if __name__ == "__main__":
    asyncio.run(test_ollama())
```

## 示例4: 自定义Prompt

```python
import asyncio
from src.ai.ollama_client import OllamaClient


async def custom_analysis():
    """使用自定义Prompt进行分析"""
    
    client = OllamaClient()
    
    # 自定义系统提示
    system_prompt = """
    你是一位资深的职业规划专家和HR，拥有10年以上的招聘和人才评估经验。
    你擅长从求职者的背景中发现亮点，并给出专业的职业建议。
    """
    
    # 用户输入
    user_prompt = """
    求职者背景：
    - 教育：北京大学，计算机科学，本科
    - 技能：Python, Django, MySQL, Redis
    - 经验：3年Python后端开发经验
    
    目标岗位：
    某互联网大厂的高级Python工程师，要求5年以上经验
    
    问题：
    1. 这位求职者的竞争力如何？
    2. 是否应该投递这个岗位？
    3. 如何提升成功率？
    """
    
    # 生成分析
    response = await client.generate(
        prompt=user_prompt,
        system=system_prompt,
        temperature=0.6,
        max_tokens=1024
    )
    
    print("专家分析:")
    print(response)


if __name__ == "__main__":
    asyncio.run(custom_analysis())
```

## 示例5: 集成到现有项目

```python
# your_app.py
from fastapi import FastAPI, UploadFile, File
from src.parsers.resume_parser import ResumeParser
from src.ai.matcher import OfferMatcher
import asyncio

app = FastAPI()
parser = ResumeParser()
matcher = OfferMatcher()


@app.post("/analyze_offer")
async def analyze_offer(
    resume: UploadFile = File(...),
    job_description: str = None
):
    """API端点：分析Offer匹配度"""
    
    # 保存上传的文件
    temp_path = f"temp/{resume.filename}"
    with open(temp_path, "wb") as f:
        f.write(await resume.read())
    
    # 解析简历
    resume_data = await parser.parse_file(temp_path)
    
    # 匹配分析
    result = await matcher.analyze_match(
        resume_data=resume_data,
        job_description=job_description,
        company_info={},
        user_preferences={}
    )
    
    return {
        "status": "success",
        "match_score": result["overall_score"],
        "analysis": result
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 运行示例

将以上代码保存为 `.py` 文件，然后运行：

```powershell
# 示例1
python example1_basic.py

# 示例2
python example2_batch.py

# 示例3
python example3_ollama.py

# 示例4
python example4_custom_prompt.py

# 示例5（FastAPI）
python example5_api.py
# 访问 http://localhost:8000/docs
```
