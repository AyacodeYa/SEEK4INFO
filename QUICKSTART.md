# Offer匹配器 - 快速开始指南

## 📋 前置要求

### 1. 安装Python
确保已安装Python 3.9或更高版本。

### 2. 安装Ollama
Ollama是本项目使用的本地AI模型运行环境。

**Windows安装：**
1. 访问 [Ollama官网](https://ollama.com/download)
2. 下载Windows安装包
3. 运行安装程序

**验证安装：**
```powershell
ollama --version
```

### 3. 下载AI模型
推荐使用 `llama3.2:3b` 模型（轻量级，适合个人电脑）：

```powershell
ollama pull llama3.2:3b
```

或者使用更强大的模型（需要更多内存）：
```powershell
ollama pull llama3.2:8b
```

查看已安装的模型：
```powershell
ollama list
```

## 🚀 快速开始

### 步骤1: 克隆/下载项目

项目已在 `c:\Users\Ayaco\Desktop\Code\Seek4Info`

### 步骤2: 安装依赖

```powershell
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt
```

### 步骤3: 配置环境变量

复制 `.env.example` 为 `.env`：

```powershell
Copy-Item .env.example .env
```

编辑 `.env` 文件（可选，使用默认配置即可）：

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

### 步骤4: 启动Ollama服务

Ollama安装后通常会自动启动。如果没有，手动启动：

```powershell
ollama serve
```

### 步骤5: 测试连接

运行快速测试：

```powershell
python cli.py --mode test
```

如果看到 "✅ Ollama服务正常"，说明配置成功！

## 💻 使用方式

### 方式1: Web界面（推荐）

启动Streamlit应用：

```powershell
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`

**使用步骤：**
1. 输入公司名称
2. 上传简历（PDF/Word/TXT）
3. 粘贴岗位描述
4. 点击"开始分析"
5. 查看分析结果和报告

### 方式2: 命令行

```powershell
python cli.py --mode analyze `
  --company "腾讯" `
  --resume "path/to/your/resume.pdf" `
  --job "path/to/job_description.txt"
```

### 方式3: MCP服务器（高级）

启动MCP服务器（用于与其他工具集成）：

```powershell
python -m src.mcp_server
```

## 📝 示例

### 示例1: 分析腾讯的岗位

1. 准备简历文件 `resume.pdf`
2. 准备岗位描述 `job_desc.txt`：

```text
岗位：Python后端工程师

职责：
- 负责后端服务开发和维护
- 参与系统架构设计
- 优化系统性能

要求：
- 3年以上Python开发经验
- 熟悉Django/Flask框架
- 熟悉MySQL、Redis等数据库
- 有微服务架构经验优先
```

3. 运行分析：

```powershell
python cli.py --mode analyze `
  --company "腾讯" `
  --resume "resume.pdf" `
  --job "job_desc.txt"
```

### 示例2: 使用Web界面

```powershell
streamlit run app.py
```

在界面中：
1. 公司名称：输入"腾讯"
2. 简历：上传 `resume.pdf`
3. 岗位描述：粘贴岗位JD
4. 点击"开始分析"

## 🔧 配置说明

### config.py 配置项

```python
# Ollama配置
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:3b"
OLLAMA_TEMPERATURE = 0.7  # 生成随机性（0-1）
OLLAMA_MAX_TOKENS = 2048  # 最大生成长度

# 爬虫配置
CRAWLER_TIMEOUT = 30  # 请求超时（秒）
CRAWLER_DELAY = 1.0   # 请求延迟（秒）
```

### 更换模型

如果想使用其他模型（如 qwen、deepseek 等）：

1. 下载模型：
```powershell
ollama pull qwen2.5:7b
```

2. 修改 `.env`：
```env
OLLAMA_MODEL=qwen2.5:7b
```

## 📊 项目结构

```
Seek4Info/
├── src/
│   ├── ai/              # AI模块
│   │   ├── ollama_client.py  # Ollama客户端
│   │   ├── matcher.py        # 匹配分析器
│   │   └── prompts.py        # 提示词模板
│   ├── scrapers/        # 爬虫模块
│   │   └── company_scraper.py
│   ├── parsers/         # 解析模块
│   │   └── resume_parser.py
│   ├── utils/           # 工具模块
│   │   └── logger.py
│   └── mcp_server.py    # MCP服务器
├── cli.py               # 命令行客户端
├── app.py               # Streamlit Web应用
├── config.py            # 配置文件
├── requirements.txt     # 依赖列表
└── README.md            # 项目文档
```

## ❓ 常见问题

### Q1: Ollama连接失败
**A:** 
- 确保Ollama服务正在运行：`ollama serve`
- 检查端口是否被占用：默认11434
- 检查防火墙设置

### Q2: 模型响应很慢
**A:**
- 使用更小的模型（如 llama3.2:3b）
- 减少 `OLLAMA_MAX_TOKENS`
- 升级硬件（建议16GB+ 内存）

### Q3: 简历解析失败
**A:**
- 确保文件格式正确（PDF/DOCX/TXT）
- 文件不要加密
- 尝试转换为TXT格式

### Q4: 爬虫无法获取公司信息
**A:**
- 目前只支持部分知名公司
- 可以手动提供公司URL
- 未来版本会增加更多公司支持

## 🎯 下一步

1. **优化简历解析**：提高关键信息提取准确率
2. **扩展公司数据库**：支持更多公司官网
3. **集成招聘API**：接入Boss直聘、拉勾等平台
4. **历史记录**：保存分析历史，支持对比
5. **PDF报告生成**：生成专业的PDF分析报告

## 📞 支持

如有问题，请：
1. 查看日志文件：`logs/app_*.log`
2. 提交Issue
3. 查看文档：[项目Wiki]

## 📄 许可证

MIT License

---

**开始你的智能求职之旅！** 🚀
