# SilverCompanion 快速在线部署指南

本项目采用 **FastAPI (后端) + Vanilla JS (前端)** 架构。借助现代 AI 友好型部署平台，您可以实现“代码提交即部署”。

## 方案 A：Zeabur (推荐，最快最稳)

Zeabur 是最适合此类 Small-Scale Full-stack 项目的平台，支持自动识别 GitHub 仓库并部署。

### 1. 准备工作

- 确保代码已推送到 [GitHub 仓库](https://github.com/Cooper1307/SilverCompanion)。
- 确保 `project_code/backend/requirements.txt` 包含所有依赖。

### 2. 部署后端 (FastAPI)

1. 访问 [Zeabur 控制台](https://zeabur.com/)。
2. 点击 **Create Project** -> **Deploy Service** -> **GitHub**。
3. 选择 `SilverCompanion` 仓库。
4. **关键配置**：
   - **Root Directory**: `project_code/backend`
   - **Environment Variables**: 点击 "Variables"，添加您的 API Key：
     - `DASH_API_KEY`: 您的阿里云 Key
     - `TAVILY_API_KEY`: 您的联网搜索 Key
     - `OR_API_KEY`: 您的 OpenRouter Key

### 3. 部署前端 (HTML)

1. 在同一个 Zeabur Project 中再添加一个 Service。
2. 同样选择 GitHub 仓库，但 **Root Directory** 设置为 `project_code/frontend`。
3. Zeabur 会自动将其识别为静态网站并生成域名。

---

## 方案 B：Hugging Face Spaces (学术/展示首选)

如果您想获得更具“AI 感”的展示链接，推荐使用 Hugging Face。

1. [新建 Space](https://huggingface.co/new-space)。
2. SDK 选择 **Docker** (最灵活) 或 **Static**。
3. 如果选择 Docker，只需在根目录放一个简单 `Dockerfile` (我可以为您生成)。
4. 如果选择 Static，直接上传前端文件。

---

## 🛠️ AI 助力的自动化秘籍

### 1. 域名自动化

Zeabur 会自动为您分配一个 `xxx.zeabur.app` 的子域名。您只需在前端 `index.html` 中将：

```javascript
const API_BASE_URL = "http://localhost:8001";
```

改为您的后端实际域名。

### 2. CI/CD 自动同步

由于您已经关联了 GitHub，以后只要在本地 Git Commit 并 Push，在线网页就会在 1 分钟内自动完成更新。

---

**如果您现在决定使用 Zeabur，只需告诉我有报错的地方，我会协助您调整代码架构以适应云端环境！**
