# 🗝️ 如何获取阿里云百炼 (DashScope) API Key

为了体验 SilverCompanion 的“完全体”能力（更快的响应速度、更精准的中文理解），建议您配置阿里云 API Key。

## ⏩ 快速步骤

1. **访问控制台**:
    打开 [阿里云百炼控制台](https://bailian.console.aliyun.com/) 并登录您的阿里云账号。
2. **开通服务**:
    如果是首次已使用，点击“立即开通”（百炼提供一定的免费额度给新用户）。
3. **创建 API Key**:
    * 在左侧菜单栏找到 **“API-KEY管理”**。
    * 点击 **“创建新的 API-KEY”**。
    * 复制生成的 `sk-` 开头的字符串。
4. **配置项目**:
    * 打开本地文件: `d:\MyData\projects\xuexiaokecheng\人工智能基础与实践\期末汇报\project_code\backend\.env`
    * 将 Key 填入第一行: `DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx`
    * 保存文件。
5. **重启服务**:
    * 关闭正在运行的后端窗口。
    * 重新双击 `运行后端服务.bat`。

---

## ❓ 常见问题

* **必须配置吗？**
  * 不是。如果您只有 OpenRouter Key，项目会自动降级使用 Route B (Llama 3.3)，依然可以正常演示。
* **为什么要配置？**
  * Route A (Qwen-Max) 在处理“上海话发音模拟”和“长文本政策阅读”时效果更好。
