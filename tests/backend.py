from fastapi import FastAPI
from fastapi.responses import FileResponse
import aiohttp
from fastapi import Request
from fastapi.responses import StreamingResponse
import json

app = FastAPI()

@ app.get("/")
async def root():
    return FileResponse("static/index.html")

@ app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message")
    async with aiohttp.ClientSession() as session:
        url = "http://localhost:11434/api/chat"
        params = {
            "model": "mistral",
            "messages": [{"role": "user", "content": message}],
            "stream": True
        }
        async with session.post(url, json=params) as resp:
            reader = resp.content
            async def stream():
                buffer = ''
                while True:
                    chunk = await reader.read(1024)
                    if not chunk:
                        break
                    buffer += chunk.decode('utf-8')
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if line:
                            try:
                                data = json.loads(line)
                                yield f"data: {data['response']}\n\n"
                            except json.JSONDecodeError:
                                pass  # 处理不完整的 JSON
            return StreamingResponse(stream(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)