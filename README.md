# Paper Tracker

每日自动追踪 arXiv 论文，使用 AI 进行分析和分类，生成静态网站展示。

**在线演示**: [https://gitgurugu.github.io/Paper_Tracker/](https://gitgurugu.github.io/Paper_Tracker/)

## 界面预览

| 首页 | 论文详情 |
|:---:|:---:|
| 高相关度论文 + 最新论文列表 | AI 摘要 + 主要贡献 + 方法论 |

**主要页面:**
- **首页**: 高相关度论文卡片、最新论文列表、分类导航
- **分类页**: 论文筛选（按日期/相关度排序，按分数过滤）
- **详情页**: AI 生成的中文摘要、主要贡献、方法论分析、原文摘要

## 特性

### 核心功能
- **多领域支持**: 通过 `config.json` 自定义追踪任意研究领域
- **多 LLM 支持**: Claude / OpenAI / Gemini / Ollama / MiniMax
- **自动化部署**: GitHub Actions 每日自动更新 + GitHub Pages 托管
- **AI 分析**: 自动生成中文摘要、主要贡献、方法论、相关度评分

### 前端界面
- **深色主题**: Research Observatory 风格，类似 GitHub Dark
- **精选字体**: JetBrains Mono (代码) + Instrument Sans (标题) + Source Serif 4 (正文)
- **客户端搜索**: 实时搜索论文标题、摘要、标签，支持键盘导航
- **响应式设计**: 完美适配桌面和移动端
- **流畅动画**: 页面加载渐入效果、悬停交互动画
- **论文卡片**: 相关度评分高亮、标签展示、一键访问 PDF

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt

# 根据使用的 LLM 安装额外依赖
pip install google-generativeai  # Gemini
```

### 2. 配置

复制并编辑配置文件：

```bash
cp .env.example .env
# 编辑 .env 设置 API Key
```

编辑 `data/config.json` 自定义追踪领域和 LLM 提供商。

### 3. 运行

```bash
# 获取并分析论文
python -m src.main fetch-and-analyze

# 生成静态网站
python -m src.main generate-site

# 本地预览
python -m src.main serve
```

## 支持的 LLM 提供商

| 提供商 | provider | 模型示例 | 环境变量 |
|--------|----------|----------|----------|
| Claude | `claude` | `claude-sonnet-4-20250514` | `ANTHROPIC_API_KEY` |
| OpenAI | `openai` | `gpt-4o-mini` | `OPENAI_API_KEY` |
| Gemini | `gemini` | `gemini-2.0-flash` | `GOOGLE_API_KEY` |
| Ollama | `ollama` | `llama3.2` | - |
| MiniMax | `minimax` | `abab6.5s-chat` | `MINIMAX_API_KEY` |
| 第三方 / 中转 | `openai` | 视厂商而定 | 自定义（配合 `base_url_env`） |

> 第三方 OpenAI 兼容接口（DeepSeek、Kimi、硅基流动、OpenRouter 等）请用 `provider: openai` 并设置 `base_url_env`，详见下方 [配置说明](#配置说明)。

## CLI 命令

| 命令 | 说明 |
|------|------|
| `show-config` | 显示当前配置 |
| `fetch-and-analyze` | 获取并分析论文 |
| `generate-site` | 生成静态网站 |
| `run` | 执行完整流程 |
| `serve` | 启动本地预览服务器 |

### 选项

| 选项 | 适用命令 | 说明 |
|------|---------|------|
| `--config, -c` | 全局 | 指定配置文件路径 |
| `--days, -d` | `fetch-and-analyze` | 回溯天数（默认 1） |
| `--dry-run` | `fetch-and-analyze` | 仅获取不分析 |
| `--output, -o` | `generate-site`, `serve` | 输出目录（默认 `docs`） |
| `--port, -p` | `serve` | 服务器端口（默认 8000） |

## 配置说明

`data/config.json` 示例：

```json
{
  "site": {
    "title": "My Paper Tracker",
    "description": "Tracking papers in my research areas",
    "base_url": "/Paper_Tracker"
  },
  "llm": {
    "provider": "gemini",
    "model": "gemini-2.0-flash",
    "api_key_env": "GOOGLE_API_KEY"
  },
  "domains": [
    {
      "name": "LLM Memory",
      "categories": ["cs.CL", "cs.AI"],
      "keywords": ["memory", "RAG", "retrieval"],
      "output_category": "memory"
    }
  ],
  "fetch": {
    "days_back": 1,
    "max_papers_per_domain": 50,
    "min_relevance_score": 5
  }
}
```

> **注意**: `base_url` 用于 GitHub Pages 部署，**必须与仓库名一致**，格式为 `/<repo-name>`（例如仓库叫 `Paper_Tracker` 就填 `/Paper_Tracker`）。本地开发时可设为空字符串 `""`。

### LLM 字段说明

| 字段 | 说明 |
|------|------|
| `provider` | 提供商类型：`claude` / `openai` / `gemini` / `ollama` / `minimax` |
| `model` | 模型名（兜底默认值，被 `model_env` 覆盖） |
| `model_env` | _(可选)_ 模型名所在的**环境变量名**，设置后优先于 `model` |
| `api_key_env` | API Key 所在的环境变量名 |
| `base_url_env` | _(可选)_ API 地址所在的**环境变量名**，用于第三方/中转接口 |

> 配置文件里只写**变量名**，真实的 Key / URL / 模型名通过环境变量或 GitHub Secrets 注入，不进代码库。

### 使用第三方 / 中转模型

绝大多数第三方模型（DeepSeek、Kimi/Moonshot、硅基流动、OpenRouter、各类中转站等）都提供 **OpenAI 兼容接口**。只要 `provider` 用 `openai` 并指定 `base_url_env` 即可接入，**Key、地址、模型名全部用环境变量管理**：

```json
"llm": {
  "provider": "openai",
  "model": "deepseek-chat",
  "model_env": "LLM_MODEL",
  "api_key_env": "LLM_API_KEY",
  "base_url_env": "LLM_BASE_URL"
}
```

对应需要设置 3 个环境变量 / GitHub Secrets：

| 变量名 | 示例值 |
|--------|--------|
| `LLM_API_KEY` | `sk-xxxxxxxx` |
| `LLM_BASE_URL` | `https://api.deepseek.com/v1` |
| `LLM_MODEL` | `deepseek-chat` |

本地运行时写进 `.env` 即可；GitHub Actions 部署时写进 Repository Secrets（见下文）。

## GitHub Actions 部署

Fork 本仓库后，按以下步骤配置即可实现每日自动更新 + 自动部署到 GitHub Pages。

### 1. 启用 Actions

Fork 来的仓库默认禁用工作流：进入 **Actions** 标签 → 点击 **"I understand my workflows, enable them"**。

### 2. 配置 Repository Secrets

进入 **Settings → Secrets and variables → Actions → New repository secret**，按你选择的模型添加密钥。

**使用第三方 / 中转模型（推荐，对应当前 `config.json`）:**

| Secret 名称 | 示例值 | 说明 |
|------------|--------|------|
| `LLM_API_KEY` | `sk-xxxxxxxx` | API Key |
| `LLM_BASE_URL` | `https://api.deepseek.com/v1` | 接口地址 |
| `LLM_MODEL` | `deepseek-chat` | 模型名 |

> `LLM_BASE_URL` 和 `LLM_MODEL` 并非敏感信息，也可放在 **Variables** 标签并在工作流中用 `${{ vars.XXX }}` 引用。

**使用官方模型（Claude / OpenAI / Gemini）:** 改回对应的 `config.json` 字段，并设置 `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `GOOGLE_API_KEY`，同时在 `.github/workflows/daily_update.yml` 的 `env` 中注入对应变量。

### 3. 授予写入权限

工作流需要把每日抓取的论文数据提交回仓库：
**Settings → Actions → General → Workflow permissions** → 选 **Read and write permissions** → 保存。

### 4. 启用 GitHub Pages

**Settings → Pages → Source** 选择 **GitHub Actions**（不是 "Deploy from a branch"）。

> ⚠️ 确认 `data/config.json` 里 `site.base_url` 与仓库名一致（如 `/Paper_Tracker`），否则部署后页面样式会 404。

### 5. 触发运行

- **手动**: Actions → 选 `Daily Paper Update` → **Run workflow**
- **自动**: 工作流每日 UTC 6:00（北京 14:00）自动运行

### 部署地址

项目站点部署在 `https://<用户名>.github.io/<仓库名>/`，例如 `https://yourname.github.io/Paper_Tracker/`。

> 它是**项目站点**，挂在仓库名子路径下，**不会覆盖**你 `https://<用户名>.github.io/` 根域名的个人主页（用户站点），两者互相独立。

## 项目结构

```
Paper_Tracker/
├── .github/workflows/
│   └── daily_update.yml     # GitHub Actions 自动化
├── src/
│   ├── main.py              # CLI 入口
│   ├── config.py            # 配置管理 (Pydantic)
│   ├── models.py            # 数据模型
│   ├── arxiv_fetcher.py     # arXiv API 封装
│   ├── site_generator.py    # 静态网站生成器
│   └── llm/                 # 多 LLM 支持
│       ├── base.py          # 抽象基类
│       ├── claude_analyzer.py
│       ├── openai_analyzer.py
│       ├── gemini_analyzer.py
│       ├── ollama_analyzer.py
│       └── minimax_analyzer.py
├── templates/               # Jinja2 模板
│   ├── base.html           # 基础布局
│   ├── index.html          # 首页
│   ├── paper_list.html     # 分类列表页
│   └── paper_detail.html   # 论文详情页
├── static/
│   ├── css/style.css       # 深色主题样式
│   └── js/main.js          # 客户端搜索
├── data/
│   ├── config.json         # 用户配置
│   └── papers/             # 论文 JSON 数据
└── docs/                    # 生成的静态网站
```

## License

MIT

