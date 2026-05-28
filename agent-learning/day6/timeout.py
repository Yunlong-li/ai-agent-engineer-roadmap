import asyncio


async def slow_tool() -> str:
    await asyncio.sleep(3)
    return "done"


# async def main() -> None:
#     try:
#         result = await asyncio.wait_for(slow_tool(), timeout=1)
#         print(result)
#     except asyncio.TimeoutError:
#         print("tool timeout")

# asyncio.run(main())

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    answer: str


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    try:
        # result = await asyncio.wait_for(slow_tool(), timeout=1)
        result = await asyncio.wait_for(slow_tool(), timeout=3.1)
        return ChatResponse(answer=f"收到：{req.message}，结果为：{result}")
    except asyncio.TimeoutError:
        return ChatResponse(answer="连接超时，请检查网络")
    




# python -m uvicorn timeout:app --reload