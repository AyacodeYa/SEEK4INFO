"""
Streamlit Web UI
"""
import streamlit as st
import asyncio
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.scrapers.company_scraper import CompanyScraper
from src.parsers.resume_parser import ResumeParser
from src.ai.matcher import OfferMatcher


# 页面配置
st.set_page_config(
    page_title="Offer匹配器",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """主函数"""
    
    # 标题
    st.markdown('<h1 class="main-header">🎯 Offer匹配器</h1>', unsafe_allow_html=True)
    st.markdown("### 智能求职决策助手 - 基于本地AI的匹配分析")
    
    # 侧边栏
    with st.sidebar:
        st.header("⚙️ 配置")
        
        # Ollama配置
        st.subheader("Ollama设置")
        ollama_url = st.text_input(
            "Ollama URL",
            value="http://localhost:11434"
        )
        ollama_model = st.text_input(
            "模型名称",
            value="llama3.2:3b"
        )
        
        # 用户偏好
        st.subheader("个人偏好")
        expected_salary = st.text_input("期望薪资", value="15-25K")
        location = st.text_input("期望地点", value="北京")
        overtime_acceptable = st.checkbox("接受加班", value=False)
        
        st.divider()
        
        # 关于
        st.subheader("关于")
        st.info("""
        **Offer匹配器** v0.1.0
        
        基于MCP协议和本地Ollama模型的智能Offer分析工具。
        
        功能：
        - 公司信息采集
        - 简历智能解析
        - AI匹配分析
        - 岗位推荐
        """)
    
    # 主界面 - 分步骤表单
    tab1, tab2, tab3 = st.tabs(["📝 输入信息", "🔍 分析结果", "📊 报告"])
    
    with tab1:
        st.markdown('<div class="step-header">步骤1: 公司信息</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            company_name = st.text_input("公司名称*", placeholder="例如：腾讯")
        with col2:
            company_url = st.text_input("公司官网（可选）", placeholder="https://...")
        
        st.markdown('<div class="step-header">步骤2: 简历上传</div>', unsafe_allow_html=True)
        
        upload_method = st.radio(
            "选择输入方式",
            ["上传文件", "粘贴文本"],
            horizontal=True
        )
        
        resume_data = None
        if upload_method == "上传文件":
            uploaded_file = st.file_uploader(
                "上传简历",
                type=["pdf", "docx", "txt"],
                help="支持PDF、Word和TXT格式"
            )
            if uploaded_file:
                # 保存临时文件
                temp_path = Path("cache") / uploaded_file.name
                temp_path.parent.mkdir(exist_ok=True)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                resume_data = {"type": "file", "path": str(temp_path)}
        else:
            resume_text = st.text_area(
                "粘贴简历内容",
                height=200,
                placeholder="请粘贴您的简历..."
            )
            if resume_text:
                resume_data = {"type": "text", "content": resume_text}
        
        st.markdown('<div class="step-header">步骤3: 目标岗位</div>', unsafe_allow_html=True)
        
        job_description = st.text_area(
            "岗位描述*",
            height=150,
            placeholder="请粘贴岗位描述，包括岗位职责、任职要求等..."
        )
        
        st.divider()
        
        # 分析按钮
        if st.button("🚀 开始分析", type="primary", use_container_width=True):
            if not company_name:
                st.error("请输入公司名称")
            elif not resume_data:
                st.error("请上传简历或粘贴简历内容")
            elif not job_description:
                st.error("请输入岗位描述")
            else:
                # 执行分析
                with st.spinner("分析中，请稍候..."):
                    result = asyncio.run(run_analysis(
                        company_name=company_name,
                        company_url=company_url,
                        resume_data=resume_data,
                        job_description=job_description,
                        user_preferences={
                            "expected_salary": expected_salary,
                            "location": location,
                            "overtime_acceptable": overtime_acceptable
                        }
                    ))
                    
                    # 保存到session state
                    st.session_state["analysis_result"] = result
                    
                    st.success("✅ 分析完成！请查看【分析结果】和【报告】标签页")
    
    with tab2:
        st.markdown('<div class="step-header">匹配分析结果</div>', unsafe_allow_html=True)
        
        if "analysis_result" in st.session_state:
            result = st.session_state["analysis_result"]
            
            # 显示匹配度
            match_score = result.get("match_result", {}).get("overall_score", 0)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("综合匹配度", f"{match_score}/100")
            with col2:
                status = "推荐" if match_score >= 70 else "谨慎" if match_score >= 50 else "不推荐"
                st.metric("决策建议", status)
            with col3:
                st.metric("推荐岗位", len(result.get("recommendations", {}).get("recommendations", [])))
            
            st.divider()
            
            # 详细分析
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("✅ 优势项")
                strengths = result.get("match_result", {}).get("strengths", [])
                if strengths:
                    for strength in strengths:
                        st.success(strength)
                else:
                    st.info("暂无数据")
            
            with col2:
                st.subheader("⚠️ 风险项")
                weaknesses = result.get("match_result", {}).get("weaknesses", [])
                if weaknesses:
                    for weakness in weaknesses:
                        st.warning(weakness)
                else:
                    st.info("暂无数据")
            
            st.divider()
            
            # 推荐岗位
            st.subheader("🎯 推荐其他岗位")
            recommendations = result.get("recommendations", {}).get("recommendations", [])
            
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    with st.expander(f"{i}. {rec['title']} - 匹配度: {rec['match_score']}/100"):
                        st.write(f"**推荐理由：** {rec['reason']}")
            else:
                st.info("该公司暂无其他合适岗位")
        else:
            st.info("请先在【输入信息】标签页完成分析")
    
    with tab3:
        st.markdown('<div class="step-header">完整分析报告</div>', unsafe_allow_html=True)
        
        if "analysis_result" in st.session_state:
            result = st.session_state["analysis_result"]
            report = result.get("report", {}).get("content", "")
            
            if report:
                st.markdown(report)
                
                # 下载按钮
                st.download_button(
                    label="📥 下载Markdown报告",
                    data=report,
                    file_name="offer_analysis_report.md",
                    mime="text/markdown"
                )
            else:
                st.info("报告生成中...")
        else:
            st.info("请先在【输入信息】标签页完成分析")


async def run_analysis(
    company_name: str,
    company_url: str,
    resume_data: dict,
    job_description: str,
    user_preferences: dict
) -> dict:
    """执行完整分析流程"""
    
    result = {}
    
    # 1. 爬取公司信息
    scraper = CompanyScraper()
    company_info = await scraper.scrape(
        company_name=company_name,
        url=company_url,
        include_recruitment=True
    )
    result["company_info"] = company_info
    
    # 2. 解析简历
    parser = ResumeParser()
    if resume_data["type"] == "file":
        parsed_resume = await parser.parse_file(resume_data["path"])
    else:
        parsed_resume = await parser.parse_text(resume_data["content"])
    result["resume_data"] = parsed_resume
    
    # 3. 匹配分析
    matcher = OfferMatcher()
    match_result = await matcher.analyze_match(
        resume_data=parsed_resume,
        job_description=job_description,
        company_info=company_info,
        user_preferences=user_preferences
    )
    result["match_result"] = match_result
    
    # 4. 岗位推荐
    recommendations = await matcher.recommend_positions(
        resume_data=parsed_resume,
        company_info=company_info,
        top_k=3
    )
    result["recommendations"] = recommendations
    
    # 5. 生成报告
    report = await matcher.generate_report(
        match_result=match_result,
        format_type="markdown"
    )
    result["report"] = report
    
    return result


if __name__ == "__main__":
    main()
