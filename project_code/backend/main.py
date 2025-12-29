import os
import httpx
import json
from http import HTTPStatus
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import dashscope
import logging
import time  # v2.0: 用于响应耗时统计
from datetime import datetime, timedelta  # v2.1: 会话过期管理

# Load environment variables (API Keys)
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(ENV_PATH)
DASH_API_KEY = os.getenv("DASHSCOPE_API_KEY")
OR_API_KEY = os.getenv("OPENROUTER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")  # v3.0: 实时搜索 API

dashscope.api_key = DASH_API_KEY

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
POLICY_FILE = os.path.join(DATA_DIR, "shanghai_policy_snippet.txt")
LOG_FILE = os.path.join(os.path.dirname(__file__), "backend_running.log")

# --- 日志配置 (Logging Configuration) ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SilverCompanion")

# === v2.0 优化: 对话历史存储 (Context Memory) ===
# v2.1: 添加时间戳和 TTL 过期机制，防止内存泄漏
conversation_history = {}  # {user_id: {"messages": [...], "last_access": datetime}}
MAX_HISTORY_LENGTH = 10    # 每个用户最多保留 10 轮对话
SESSION_TTL_HOURS = 24     # 会话过期时间 (小时)

def cleanup_expired_sessions():
    """清理过期的会话历史，防止内存泄漏"""
    now = datetime.now()
    expired_users = [
        uid for uid, data in conversation_history.items()
        if now - data.get("last_access", now) > timedelta(hours=SESSION_TTL_HOURS)
    ]
    for uid in expired_users:
        del conversation_history[uid]
        logger.info(f"[TTL] 清理过期会话: {uid}")
    return len(expired_users)

# === v3.0 优化: 实时联网搜索 ===
REALTIME_KEYWORDS = ["天气", "今天", "新闻", "最新", "现在几点", "时间"]

async def search_realtime(query: str) -> str | None:
    """使用 Tavily API 进行实时搜索 (v3.0)"""
    if not TAVILY_API_KEY:
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": TAVILY_API_KEY,
                    "query": query,
                    "search_depth": "basic",
                    "max_results": 3
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("results"):
                # 提取前 3 个结果的摘要
                summaries = [r.get("content", "")[:200] for r in data["results"][:3]]
                return "\n".join(summaries)
    except Exception as e:
        logger.warning(f"[v3.0 Search] 搜索失败: {e}")
    
    return None

def needs_realtime_search(message: str) -> bool:
    """检测消息是否需要实时搜索"""
    return any(keyword in message for keyword in REALTIME_KEYWORDS)

# === v2.0 优化: 紧急关键词检测 ===
EMERGENCY_KEYWORDS = ["胸闷", "胸痛", "头晕", "呼吸困难", "晕倒", "晕过去", "心脏痛", "不省人事", "打120"]

def check_emergency(message: str) -> str | None:
    """检查消息中是否包含紧急关键词，返回紧急响应或 None"""
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in message:
            logger.warning(f"[紧急检测] 发现报警关键词: {keyword}")
            return f"老人家，您说的“{keyword}”让我很担心！这种情况千万不能拖，您现在就拨打 **120** 急救电话，或者让家里人送您去医院。我会一直在这里陪着您！"
    return None

def get_local_knowledge():
    """Reads local policy snippet for RAG-lite simulation."""
    try:
        if os.path.exists(POLICY_FILE):
            with open(POLICY_FILE, "r", encoding="utf-8") as f:
                return f.read()
    except Exception:
        pass
    return "暂时无法读取本地政策库。"

app = FastAPI(
    title="SilverCompanion API",
    description="Backend for the SilverCompanion Elderly Assistant",
    version="2.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dynamic Persona Configuration
knowledge_base = get_local_knowledge()
SYSTEM_PROMPT_DYNAMIC = f"""
你是一个在上海社区工作多年的“金牌社工小张”。你说话亲切自然，保持晚辈的谦卑与温度，像对待自己的长辈一样对待社区老人。

# 参考知识库 (当前真实上海政策摘要)
{knowledge_base}

# 语言规范
1. 称呼：始终使用“您”、“老人家”、“阿姨/叔叔”。
2. 措辞：严禁使用 AI 术语，要说“我想想看”、“我帮您打听了一下”。
3. 精简：一句话不超过 15 个字，多使用短句，避免长难句。

# 核心职责
1. 政策通：解答关于长护险、养老补贴、助餐点的问题。请务必优先查看参考知识库中的内容。
2. 健康哨兵：提供基础饮食建议，不涉及具体药量。
3. 情感安抚：先进行 30 字以内的共情安抚，再给建议。

# 安全红线
1. 严禁给出具体处方药量。
2. 识别到“胸闷”、“呼吸困难”等报警词，必须引导用户拨打 120。
"""

class ChatRequest(BaseModel):
    """聊天消息请求模型。"""
    message: str
    user_id: str

class ChatResponse(BaseModel):
    """包含 AI 回复和建议追问的响应模型。"""
    response: str
    suggestions: List[str]

@app.get("/")
async def root():
    """健康检查端点，显示活动路由。"""
    logger.info("收到健康检查请求 (/)")
    routes = []
    if DASH_API_KEY: routes.append("Aliyun (Route A)")
    if OR_API_KEY: routes.append("OpenRouter (Route B)")
    return {
        "status": "online",
        "active_routes": routes,
        "message": "SilverCompanion API ready."
    }

async def call_openrouter(user_message: str, history: list = None, realtime_ctx: str = ""):
    """使用 OpenRouter 免费模型的兜底逻辑。v2.1: 支持历史对话, v3.0: 支持实时搜索上下文"""
    async with httpx.AsyncClient() as client:
        try:
            # v2.1: 构建包含历史的消息列表
            # v3.0: 注入实时搜索上下文
            system_content = SYSTEM_PROMPT_DYNAMIC + realtime_ctx
            messages = [{"role": "system", "content": system_content}]
            if history:
                messages.extend(history[-MAX_HISTORY_LENGTH*2:])
            messages.append({"role": "user", "content": user_message})
            
            payload = {
                "model": "meta-llama/llama-3.3-70b-instruct:free",
                "messages": messages
            }
            logger.info(f"[Route B] 正在向 OpenRouter 发送请求...")
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OR_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://silvercompanion.demo",
                    "X-Title": "SilverCompanion-Elderly-Assistant",
                },
                data=json.dumps(payload),
                timeout=90.0
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"[Route B] 成功收到模型回复。")
            return data['choices'][0]['message']['content']
        except httpx.TimeoutException:
            logger.warning(f"[Route B] 请求超时。")
            return None
        except Exception as e:
            logger.error(f"[Route B] 发生错误: {type(e).__name__} - {e}")
            return None

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    start_time = time.time()  # v2.0: 开始计时
    logger.info(f"收到用户请求: {request.user_id} - '{request.message[:20]}...'")
    
    # === v2.0 优化: 紧急关键词前置检测 (最高优先级) ===
    emergency_response = check_emergency(request.message)
    if emergency_response:
        elapsed = time.time() - start_time
        logger.info(f"[耗时] {elapsed:.2f}s (紧急响应)")
        return ChatResponse(
            response=emergency_response,
            suggestions=["我已经拨打了120", "帮我联系家人", "我现在感觉好一点了"]
        )
    
    # === v2.1 优化: 定期清理过期会话 ===
    cleanup_expired_sessions()
    
    # === v3.0 优化: 实时联网搜索 ===
    realtime_context = ""
    if needs_realtime_search(request.message):
        logger.info(f"[v3.0] 检测到实时查询关键词，尝试联网搜索...")
        search_result = await search_realtime(request.message)
        if search_result:
            realtime_context = f"\n\n# 实时搜索结果 (供参考)\n{search_result}\n"
            logger.info(f"[v3.0] 联网搜索成功，已注入上下文。")
    
    # === v2.0 优化: 加载/初始化对话历史 ===
    if request.user_id not in conversation_history:
        conversation_history[request.user_id] = {"messages": [], "last_access": datetime.now()}
    else:
        conversation_history[request.user_id]["last_access"] = datetime.now()
    
    user_history = conversation_history[request.user_id]["messages"]
    
    # Route A: Aliyun (Priority)
    if DASH_API_KEY:
        try:
            # v2.1: 将历史对话传递给 LLM，实现真正的多轮对话
            # v3.0: 注入实时搜索结果到系统提示
            system_with_context = SYSTEM_PROMPT_DYNAMIC + realtime_context
            messages_for_llm = [{'role': 'system', 'content': system_with_context}]
            messages_for_llm.extend(user_history[-MAX_HISTORY_LENGTH*2:])  # 最近 N 轮历史
            messages_for_llm.append({'role': 'user', 'content': request.message})
            
            response = dashscope.Generation.call(
                model="qwen-max",
                messages=messages_for_llm,
                result_format='message',
            )
            if response.status_code == HTTPStatus.OK:
                elapsed = time.time() - start_time
                logger.info(f"[Route A] 成功收到模型回复 (Aliyun)。[耗时] {elapsed:.2f}s")
                ai_content = response.output.choices[0].message.content
                # v2.1: 保存对话历史 (使用新结构)
                user_history.append({"role": "user", "content": request.message})
                user_history.append({"role": "assistant", "content": ai_content})
                if len(user_history) > MAX_HISTORY_LENGTH * 2:
                    conversation_history[request.user_id]["messages"] = user_history[-MAX_HISTORY_LENGTH * 2:]
                return ChatResponse(
                    response=ai_content,
                    suggestions=["申请补贴要什么材料？", "帮我查查最近的助餐点", "老人家该多吃什么？"]
                )
        except Exception as e:
            logger.warning(f"[Route A] 失败，尝试切换。错误: {e}")
            pass # Fallback to Route B

    # Route B: OpenRouter
    if OR_API_KEY:
        content = await call_openrouter(request.message, user_history, realtime_context)  # v3.0: 传递搜索上下文
        if content:
            elapsed = time.time() - start_time
            logger.info(f"[Route B] 成功收到模型回复 (OpenRouter)。[耗时] {elapsed:.2f}s")
            # v2.1: 保存对话历史 (使用新结构)
            user_history.append({"role": "user", "content": request.message})
            user_history.append({"role": "assistant", "content": content})
            if len(user_history) > MAX_HISTORY_LENGTH * 2:
                conversation_history[request.user_id]["messages"] = user_history[-MAX_HISTORY_LENGTH * 2:]
            return ChatResponse(
                response=content,
                suggestions=["长护险怎么查？", "助餐点几点开？"]
            )

    # Final Fallback: Mock Presentation Mode (静态兜底)
    # 根据用户输入关键词，返回预设的“演示用”标准答案
    msg = request.message
    
    if "长护险" in msg:
        logger.info("[Mock] 匹配到关键词: 长护险")
        return ChatResponse(
            response="王阿姨，长护险可是个好政策！根据上海最新规定，60岁以上参保人员都能申请。您可以带上身份证和社保卡，去咱们街道的社区事务受理中心（就在居委会旁边）办理评估。评下来如果需要照护，每天有护理员上门，政府还给报销大头呢！",
            suggestions=["需要准备什么材料？", "评估通过难不难？", "我有退休工资能办吗？"]
        )
    
    if "助餐" in msg or "吃饭" in msg:
        logger.info("[Mock] 匹配到关键词: 助餐")
        return ChatResponse(
            response="吃饭确实是头等大事！咱们静安区的社区食堂每天中午10:30开饭。如果您办了敬老卡，每顿还能补贴1-2块钱。今天的菜单有红烧肉和清蒸鱼，就在小区北门出去左转那家，味道很清淡，适合咱们老年人。",
            suggestions=["能送餐上门吗？", "周末开门吗？", "今天的菜谱是什么？"]
        )
        
    if "健康" in msg or "高血压" in msg or "不舒服" in msg:
        logger.info("[Mock] 匹配到关键词: 健康/安全")
        return ChatResponse(
            response="老人家，天冷了要注意保暖。如果有高血压，记得按时吃药，饮食上少吃咸的。如果现在觉得胸闷或者头晕，千万别硬撑，赶紧按一下手边的紧急呼叫器，或者我帮您联系子女？",
            suggestions=["我不舒服，帮我打120", "高血压能吃红烧肉吗？", "最近天气怎么样？"]
        )

    # 默认兜底
    logger.info("[Mock] 未匹配关键词，执行默认兜底响应。")
    return ChatResponse(
        response="老人家，我收到您的消息啦！不过现在我的‘大脑’（API Key）还没连接好，等陈组长帮我接上线，我就能根据上海最新政策帮您解答更多问题了。您刚刚问的这个问题，我记在小本子上了。",
        suggestions=["如何申请长护险", "附近哪里有助餐点", "我不舒服怎么办"]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
