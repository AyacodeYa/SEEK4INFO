# Offer匹配器 - 智能求职决策助手

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-Protocol-green.svg)](https://modelcontextprotocol.io/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-orange.svg)](https://ollama.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 项目简介

**Offer匹配器**是一个基于MCP协议和本地Ollama大模型的智能求职决策助手，帮助求职者快速分析岗位匹配度，提供专业的决策建议。

### 核心特点
- 🤖 **本地AI**：使用Ollama运行本地大模型，数据隐私有保障
- 🔌 **MCP协议**：标准化接口，易于集成到其他工具
- 📊 **智能分析**：多维度评估岗位匹配度（硬技能、软实力、发展前景等）
- 🎨 **友好界面**：提供Web UI和命令行两种使用方式
- 🚀 **快速上手**：3分钟即可开始使用

## 项目背景
**痛点识别**：秋招期间，求职者面对大量offer和岗位，难以快速判断：
- 岗位要求与个人能力是否匹配？
- 公司文化和发展前景是否符合预期？
- 薪资待遇是否合理？
- 是否有更适合的岗位推荐？

**解决方案**：基于AI的智能Offer匹配器，自动化分析公司信息与个人简历的适配度，为求职者提供专业的决策建议。

## 项目概述
这是一个两阶段智能决策系统：
1. **信息采集阶段**：爬取目标公司官网的招聘信息、公司介绍、职员待遇等
2. **智能匹配阶段**：结合用户简历和目标岗位，进行适配度分析和岗位推荐

---

## 🚀 快速开始

### 前置要求
- Python 3.9+
- [Ollama](https://ollama.com/download)（本地AI运行环境）

### 安装步骤

1. **安装Ollama并下载模型**
```powershell
# 安装Ollama（访问官网下载）
# https://ollama.com/download

# 下载推荐模型（轻量级，3B参数）
ollama pull llama3.2:3b
```

2. **安装项目依赖**
```powershell
# 克隆/进入项目目录
cd Seek4Info

# 安装依赖
pip install -r requirements.txt

# 复制配置文件
Copy-Item .env.example .env
```

3. **启动服务**

**Web界面（推荐）：**
```powershell
streamlit run app.py
```
访问：http://localhost:8501

**命令行测试：**
```powershell
python cli.py --mode test
```

**完整分析：**
```powershell
python cli.py --mode analyze `
  --company "腾讯" `
  --resume "examples/sample_resume.txt" `
  --job "examples/sample_job.txt"
```

详细说明请查看 [快速开始指南](QUICKSTART.md)

---

## 📁 项目结构

```
Seek4Info/
├── src/                      # 源代码
│   ├── ai/                   # AI模块
│   │   ├── ollama_client.py  # Ollama客户端
│   │   ├── matcher.py        # 匹配分析器
│   │   └── prompts.py        # 提示词模板
│   ├── scrapers/             # 爬虫模块
│   │   └── company_scraper.py
│   ├── parsers/              # 解析模块
│   │   └── resume_parser.py
│   ├── utils/                # 工具模块
│   │   └── logger.py
│   └── mcp_server.py         # MCP服务器
├── examples/                 # 示例文件
│   ├── sample_resume.txt
│   ├── sample_job.txt
│   └── usage_examples.md
├── cli.py                    # 命令行客户端
├── app.py                    # Streamlit Web应用
├── config.py                 # 配置管理
├── requirements.txt          # 依赖列表
├── QUICKSTART.md             # 快速开始指南
└── README.md                 # 项目文档
```

#### 输出结果
1. **综合匹配报告**
   ```
   📊 匹配度总分：78/100
   
   ✅ 优势项：
   - 技术栈高度匹配（Java Spring Boot经验3年）
   - 薪资符合预期（15-20K，期望18K）
   
   ⚠️ 风险项：
   - 工作强度较大（可能996）
   - 职位要求5年经验，你有3年（可尝试）
   
   💡 建议：
   - 可以投递，通过概率60%
   - 面试时重点强调XX项目经验
   - 准备XX技术相关问题
   ```

2. **岗位推荐**（如匹配度<60）
   ```
   🎯 该公司更适合你的岗位：
   
   1. 【Java开发工程师 - 中级】- 匹配度 85/100
      理由：技术要求与你经验完全吻合，薪资15-18K
      
   2. 【后端开发实习生 - 转正】- 匹配度 72/100
      理由：可作为备选，压力较小，成长空间大
   ```

3. **决策建议**
   - 是否投递：推荐/谨慎/不推荐
   - 谈判建议：薪资谈判空间、福利关注点
   - 准备清单：需补充的技能、面试重点

## 成本估算

### 开发成本（MVP阶段）
| 项目 | 预估成本 | 说明 |
|------|---------|------|
| **开发人员** | ¥0（个人项目） | 或外包¥15,000-30,000 |
| **AI API** | ¥500-1,000/月 | GPT-4 API调用费用 |
| **云服务器** | ¥200-500/月 | 阿里云/腾讯云基础配置 |
| **数据存储** | ¥100/月 | PostgreSQL + Redis |
| **代理IP池** | ¥300/月 | 应对反爬虫（可选） |
| **域名+SSL** | ¥100/年 | 品牌域名 |
| **总计（月）** | **¥1,100-2,000** | 不含开发人力 |

### 现有解决方案对比

| 产品 | 核心功能 | 优势 | 劣势 | 差异化空间 |
|------|---------|------|------|-----------|
| **Boss直聘** | 职位推荐 | 平台大、岗位多 | 推荐算法简单，无深度分析 | ✅ 我们提供深度匹配分析 |
| **拉勾网** | 互联网招聘 | 垂直领域专业 | 缺少决策辅助 | ✅ AI驱动的决策建议 |
| **看准网** | 公司点评 | 真实员工评价 | 信息分散，需手动整合 | ✅ 自动整合多源信息 |
| **职徒简历** | 简历优化 | 简历诊断准确 | 不涉及岗位匹配 | ✅ 结合岗位做匹配分析 |
| **Offer格格** | Offer比较 | 多offer横向对比 | 需手动输入，无AI | ✅ 自动采集+AI分析 |

---

## 附录：参考资源

### 学习资源
- [Scrapy官方文档](https://docs.scrapy.org/)
- [LangChain实战教程](https://python.langchain.com/)
- [简历解析开源项目](https://github.com/topics/resume-parser)

### 数据源
- [Boss直聘开放平台](https://open.zhipin.com/)
- [看准网](https://www.kanzhun.com/)
- [Offer Collector](https://offershow.cn/)（薪资数据）

### 法律合规
- [《**爬取数据须遵规**》](https://www.spp.gov.cn/llyj/202202/t20220210_543998.shtml)

