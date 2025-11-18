# Offer匹配器 - 启动脚本

Write-Host "🎯 Offer匹配器 - 启动向导" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# 检查Python
Write-Host "检查Python环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python未安装或未添加到PATH" -ForegroundColor Red
    Write-Host "请访问 https://www.python.org/downloads/ 安装Python 3.9+" -ForegroundColor Red
    exit 1
}

# 检查Ollama
Write-Host "`n检查Ollama..." -ForegroundColor Yellow
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "✅ Ollama已安装" -ForegroundColor Green
    
    # 检查模型
    Write-Host "检查模型..." -ForegroundColor Yellow
    $models = ollama list 2>&1
    if ($models -match "llama3.2") {
        Write-Host "✅ llama3.2模型已安装" -ForegroundColor Green
    } else {
        Write-Host "⚠️  llama3.2模型未安装" -ForegroundColor Yellow
        Write-Host "正在下载模型（这可能需要几分钟）..." -ForegroundColor Yellow
        ollama pull llama3.2:3b
    }
} catch {
    Write-Host "❌ Ollama未安装" -ForegroundColor Red
    Write-Host "请访问 https://ollama.com/download 安装Ollama" -ForegroundColor Red
    exit 1
}

# 检查依赖
Write-Host "`n检查依赖..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    Write-Host "创建虚拟环境..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "激活虚拟环境..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

Write-Host "安装依赖..." -ForegroundColor Yellow
pip install -r requirements.txt -q

# 检查.env文件
if (-not (Test-Path ".env")) {
    Write-Host "`n创建.env配置文件..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✅ 配置文件已创建" -ForegroundColor Green
}

# 菜单
Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "选择启动方式：" -ForegroundColor Cyan
Write-Host "1. Web界面（推荐）" -ForegroundColor White
Write-Host "2. 命令行测试" -ForegroundColor White
Write-Host "3. 完整分析示例" -ForegroundColor White
Write-Host "4. MCP服务器" -ForegroundColor White
Write-Host "5. 退出" -ForegroundColor White
Write-Host "================================`n" -ForegroundColor Cyan

$choice = Read-Host "请输入选项 (1-5)"

switch ($choice) {
    "1" {
        Write-Host "`n🚀 启动Web界面..." -ForegroundColor Green
        Write-Host "浏览器将自动打开 http://localhost:8501" -ForegroundColor Yellow
        streamlit run app.py
    }
    "2" {
        Write-Host "`n🔧 运行快速测试..." -ForegroundColor Green
        python cli.py --mode test
    }
    "3" {
        Write-Host "`n📊 运行完整分析示例..." -ForegroundColor Green
        python cli.py --mode analyze `
            --company "示例公司" `
            --resume "examples/sample_resume.txt" `
            --job "examples/sample_job.txt"
    }
    "4" {
        Write-Host "`n🔌 启动MCP服务器..." -ForegroundColor Green
        python -m src.mcp_server
    }
    "5" {
        Write-Host "`n👋 再见！" -ForegroundColor Cyan
        exit 0
    }
    default {
        Write-Host "`n❌ 无效选项" -ForegroundColor Red
    }
}

Write-Host "`n按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
