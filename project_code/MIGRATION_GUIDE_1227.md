# 🛸 SilverCompanion 项目迁移指令集 & 2026 开发蓝图

**当前时间上下文**: 2025年12月27日 20:30
**项目状态**: 结项冲刺/审计阶段 (Phase 8.5) - 已确立全量同步对齐协议 (SAP)。

---

## 📋 给新对话的“前情提要” (Copy & Paste)
>
> 你好！我是 SilverCompanion 项目的 AI 助手。目前项目已进入“期末结项”阶段。
>
> **核心技术栈**:
>
> - **后端**: FastAPI (Python), 运行于 8001 端口。
> - **模型**: 分布式路由 (Aliyun Bailian Qwen-Max + OpenRouter Llama 3.3 70B)。
> - **特色**: RAG-Lite 本地知识库 (`shanghai_policy_snippet.txt`)，注入“金牌社工小张”亲和力人设。
> - **核心规则**: **同步对齐协议 (Synchronized Alignment Protocol)** —— 改动必同步，逻辑必闭环。
> - **前端**: 旗舰版毛玻璃 UI (`index.html`)，适配 ASR 语音模拟与适老化大字。
>
> **已完成里程碑**:
>
> 1. [12.19] 通过“Happy Path”全链路演示，双路由自动 Fallback 逻辑验证成功。
> 2. [12.19] 知识库由 4 条扩充至 9 大板块 (含长护险、助餐点、适老化改造等)。
>
1. [12.27] 完成《实践报告》技术细节实时同步（含真实 Prompt 与难点记录）。
2. [12.27] 正式确立 **SAP 同步协议**，实现“库-码-文”三方垂直对齐。

**当前任务**: 保持 Consistent (Green) 状态，进行最终演示文稿打磨与环境兼容性增强。

---

## 📂 关键文件索引

- **后端核心**: `project_code/backend/main.py` (含 Fallback 逻辑)
- **本地政策库**: `project_code/data/shanghai_policy_snippet.txt` (RAG 核心)
- **前端页面**: `project_code/frontend/index.html` (旗舰版 UI)
- **正式报告**: `project_code/SilverCompanion_Practice_Report_vFinal.md`
- **额度手册**: `C:/Users/Lenovo/.gemini/antigravity/brain/.../Gemini_3_Selection_Playbook.md`

---

## 🔮 后续优化方向 (SilverCompanion v2.0)

为了让项目在汇报中更具“未来感”，以下是建议的后续迭代方向：

### 1. 实时联网搜索 (Real-time Search)

- **现状**: 仅依赖本地 TXT，无法回答“今天的天气”或“最新的实时活动”。
- **方案**: 引入 **Tavily API** 或 **Serper API**，让小张具备查阅上海实时新闻的能力。

### 2. 多模态视觉辅助 (Multimodal Vision)

- **现状**: 老人打字不便。
- **方案**: 利用 **Gemini 3 Pro 的视觉能力**，增加“拍照片识药盒”功能。老人只需拍照，小张即可念出用法用量（需严格遵循医学伦理）。

### 3. 硬件/IOT 深度整合

- **现状**: 运行于网页浏览器。
- **方案**: 预研智能盲杖/紧急手环的心率数据对接。识别到异常心率时，自动在 UI 上高亮显示报警入口。

### 4. 上海方言 ASR/TTS 插件

- **现状**: 普通话交互。
- **方案**: 探索特定街道的上海话微调模型，让“小张”更有里弄间的亲切感。

---

## 🛠️ 关于 IDE 额度的最后叮嘱

在新对话中，请继续遵循 **“换族轮换”** 策略：

- **Flash**: 用于所有 CSS/HTML 的视觉微调。
- **Claude Sonnet 4.5 / Pro**: 用于报告的学术措辞提升与逻辑对齐。

**陈组长，迁移准备已就绪。你可以随时开启 New Chat 并喂入上方“前情提要”！** 🚀🏆
