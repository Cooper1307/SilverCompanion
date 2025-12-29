import os
import sys
import httpx
import asyncio
from dotenv import load_dotenv

# 加载环境变量
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

dash_key = os.getenv("DASHSCOPE_API_KEY")
or_key = os.getenv("OPENROUTER_API_KEY")

async def test_connectivity():
    print("="*40)
    print("🚀 SilverCompanion 连通性自检程序")
    print("="*40)

    # 1. 检查 API Key 配置
    print(f"[配置] 阿里云 Key (Route A): {'✅ 已配置' if dash_key else '⬜ 未配置 (将降级)'}")
    print(f"[配置] OpenRouter Key (Route B): {'✅ 已配置' if or_key else '❌ 未配置'}")

    # 2. 检查后端服务状态
    url = "http://localhost:8001"
    print(f"\n[网络] 正在尝试连接后端服务 {url}...")
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=3.0)
            if resp.status_code == 200:
                data = resp.json()
                print(f"[状态] 服务在线! ✅")
                print(f"[信息] 激活路由: {data.get('active_routes')}")
            else:
                print(f"[状态] 服务异常 (状态码: {resp.status_code}) ❌")
    except httpx.ConnectError:
        print("[错误] 无法连接到服务器。请确认您已运行 '运行后端服务.bat'。 ❌")
        return
    except Exception as e:
        print(f"[错误] 发生异常: {e} ❌")
        return

    # 3. 模拟对话测试 (UAT)
    print("\n[测试] 正在发送测试指令: '你好'...")
    try:
        async with httpx.AsyncClient() as client:
            payload = {"message": "你好", "user_id": "test_bot"}
            resp = await client.post(f"{url}/chat", json=payload, timeout=30.0)
            if resp.status_code == 200:
                res_data = resp.json()
                print(f"[响应] AI 回复: {res_data['response'][:50]}...")
                print("[结论] 全链路测试通过! 🚀")
            else:
                print(f"[响应] 请求失败: {resp.text}")
    except Exception as e:
        print(f"[错误] 对话测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_connectivity())
    input("\n按回车键退出...")
