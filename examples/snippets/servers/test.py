import os
import asyncio
import json
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from mcp import ClientSession

# 🔥 핵심 변경 1: sse_client 대신 최신 streamablehttp_client를 사용합니다.
from mcp.client.streamable_http import streamable_http_client

load_dotenv()

ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
API_KEY = os.getenv("AZURE_OPENAI_KEY")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

llm_client = AsyncAzureOpenAI(
    azure_endpoint=ENDPOINT,
    api_key=API_KEY,
    api_version=API_VERSION
)

# 🔥 핵심 변경 2: streamable-http 서버의 기본 엔드포인트인 /mcp 로 변경합니다.
SERVER_URL = "http://127.0.0.1:8000/mcp"

LLM_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "두 숫자를 더합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"}
                },
                "required": ["a", "b"]
            }
        }
    }
]


# 2. 서버 연결 부분 변경 (약 50번째 줄 부근)
async def chat_with_agent(user_prompt: str):
    print(f"\n👤 사용자: {user_prompt}")
    
    # 함수 이름에 언더바 추가!
    async with streamable_http_client(SERVER_URL) as streams:
        async with ClientSession(streams[0], streams[1]) as mcp_session:
            
            await mcp_session.initialize()
            
            messages = [{"role": "user", "content": user_prompt}]
            
            response = await llm_client.chat.completions.create(
                model=DEPLOYMENT_NAME,
                messages=messages,
                tools=LLM_TOOLS,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            messages.append(response_message)
            
            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"🤖 에이전트: '{function_name}' 도구 호출 중... 인자: {function_args}")
                    
                    mcp_result = await mcp_session.call_tool(
                        function_name, 
                        arguments=function_args
                    )
                    
                    tool_output = mcp_result.content[0].text if isinstance(mcp_result.content, list) else str(mcp_result.content)
                    print(f"🛠️ MCP 서버 응답: {tool_output}")
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": tool_output
                    })
                
                final_response = await llm_client.chat.completions.create(
                    model=DEPLOYMENT_NAME,
                    messages=messages
                )
                print(f"🤖 최종 답변: {final_response.choices[0].message.content}")
            else:
                print(f"🤖 에이전트: {response_message.content}")

async def main():
    a = input("첫번째 값을 입력하세요!...")
    b = input("두번째 값을 입력하세요!...") 

    await chat_with_agent(f"{a}와 {b}를 더하면 얼마야?")

if __name__ == "__main__":
    asyncio.run(main())