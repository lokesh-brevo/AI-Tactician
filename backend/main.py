"""FastAPI backend for the AI Tactician prototype."""
from __future__ import annotations

import json
import os
import uuid
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

load_dotenv()

from agent import run_agent_stream
from mock_api import get_account_context

app = FastAPI(title="AI Tactician API", version="0.1.0")

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory conversation store ─────────────────────────────────────────────
# Maps conversation_id → list of messages
_conversations: dict[str, list[dict]] = {}


# ── Vercel AI SDK compatible streaming ───────────────────────────────────────
# The AI SDK Data Stream Protocol expects newline-delimited events with
# specific prefixes. We map our agent events to this format.
# See: https://sdk.vercel.ai/docs/ai-sdk-ui/stream-protocol#data-stream-protocol

async def _stream_response(messages: list[dict]):
    """Stream agent response in Vercel AI SDK Data Stream Protocol format.

    Event format (newline-delimited):
      0:"text chunk"         — text delta
      9:{...}                — tool call start
      a:{...}                — tool result
      e:{...}                — finish reason
      d:{...}                — done signal
    """
    full_text = ""
    try:
        async for event in run_agent_stream(messages):
            if event["type"] == "text_delta":
                content = event["content"]
                full_text += content
                # Text delta: prefix 0
                escaped = json.dumps(content)
                yield f"0:{escaped}\n"

            elif event["type"] == "tool_call_start":
                # Tool call: prefix 9
                tool_data = {
                    "toolCallId": str(uuid.uuid4()),
                    "toolName": event["tool"],
                    "args": event["input"],
                }
                yield f"9:{json.dumps(tool_data)}\n"

            elif event["type"] == "tool_result":
                # Tool result: prefix a
                result_data = {
                    "toolCallId": str(uuid.uuid4()),
                    "toolName": event["tool"],
                    "result": event["result"],
                }
                yield f"a:{json.dumps(result_data)}\n"

            elif event["type"] == "message_done":
                # Finish: prefix e, then done: prefix d
                yield f'e:{json.dumps({"finishReason": "stop", "usage": {"promptTokens": 0, "completionTokens": 0}})}\n'
                yield f'd:{json.dumps({"finishReason": "stop"})}\n'

    except Exception as exc:
        # Stream error as text
        error_msg = f"\n\n⚠️ Error: {str(exc)}"
        yield f"0:{json.dumps(error_msg)}\n"
        yield f'e:{json.dumps({"finishReason": "error"})}\n'
        yield f'd:{json.dumps({"finishReason": "error"})}\n'


# ── Routes ───────────────────────────────────────────────────────────────────

@app.post("/api/chat")
async def chat(request: Request):
    """Streaming chat endpoint compatible with Vercel AI SDK useChat hook.

    Expects: { "messages": [{"role": "user"|"assistant", "content": "..."}] }
    Returns: SSE stream in AI SDK Data Stream Protocol format.
    """
    body = await request.json()
    messages = body.get("messages", [])

    # Convert from AI SDK format to Anthropic format
    anthropic_messages = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role in ("user", "assistant"):
            anthropic_messages.append({"role": role, "content": content})

    return StreamingResponse(
        _stream_response(anthropic_messages),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Vercel-AI-Data-Stream": "v1",
        },
    )


@app.get("/api/account/context")
async def account_context():
    """Returns the account context for the right panel."""
    return get_account_context()


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
