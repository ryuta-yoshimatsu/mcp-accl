# server.py
import os
from contextlib import asynccontextmanager
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.responses import PlainTextResponse
import uvicorn

try:
    # Newer releases ship FastMCP as a separate package.
    from fastmcp import FastMCP  # type: ignore
except ImportError:  # pragma: no cover
    # Older releases expose FastMCP under the mcp package.
    from mcp.server.fastmcp import FastMCP  # type: ignore

if load_dotenv:
    load_dotenv()
APP_PORT = int(os.getenv("APP_PORT", 8000))  # default port

# --- FastMCP setup ---
mcp_app = FastMCP(name="healthcare-mcp-server", stateless_http=True)

# -----------------------
# Perplexity API config
# -----------------------
# NOTE: User requested a hard-coded API key. Replace this with your real key.
# You can optionally override via env var PERPLEXITY_API_KEY.
PERPLEXITY_API_KEY = "pplx-REPLACE_WITH_REAL_KEY"
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

# -----------------------
# External API stubs
# -----------------------
async def call_risk_api(patient_data: dict) -> dict:
    score = 0.2 * patient_data.get("age", 50) + 5
    return {
        "risk_score": round(score, 2),
        "explanation": "Mock risk score based on age * 0.2 + 5",
        "raw_response": {"calculation_basis": "age"}
    }

async def call_labs_api(patient_id: str) -> dict:
    return {
        "labs": [
            {"test": "HbA1c", "value": 6.2, "unit": "%", "date": "2025-08-01"},
            {"test": "Cholesterol", "value": 190, "unit": "mg/dL", "date": "2025-07-15"}
        ]
    }

async def call_scheduler_api(patient_id: str, preferred_window: str) -> dict:
    return {
        "appointment_id": f"APT-{patient_id}-001",
        "scheduled_time": f"{preferred_window}T10:00:00",
        "confirmation": "Appointment scheduled successfully"
    }

async def call_perplexity_api(
    prompt: str,
    *,
    model: str = "sonar",
    system_prompt: Optional[str] = None,
    max_tokens: int = 512,
    temperature: float = 0.2,
) -> dict:
    """
    Call Perplexity Chat Completions API (OpenAI-compatible).
    Returns a normalized object containing: text, citations, raw_response.
    """
    import httpx

    api_key = os.getenv("PERPLEXITY_API_KEY") or PERPLEXITY_API_KEY
    if not api_key or "REPLACE_WITH_REAL_KEY" in api_key:
        raise ValueError(
            "Perplexity API key not configured. Set PERPLEXITY_API_KEY env var or "
            "replace PERPLEXITY_API_KEY in server.py with a real key."
        )

    messages: list[dict] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        resp = await client.post(PERPLEXITY_API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    # OpenAI-compatible: choices[0].message.content; Perplexity may also include citations.
    text = (
        (((data.get("choices") or [{}])[0]).get("message") or {}).get("content")
        or ""
    )
    citations = data.get("citations") or []
    return {"text": text, "citations": citations, "raw_response": data}

# -----------------------
# MCP Tools
# -----------------------
@mcp_app.tool()
async def calculate_risk_score_tool(patient_data: dict):
    """
    Calculate a risk score for a patient using an external risk-scoring API.

    :param patient_data: Required: patient identifiers and relevant features
    """
    return await call_risk_api(patient_data)

@mcp_app.tool()
async def fetch_lab_results_tool(patient_id: str):
    """
    Fetch recent lab results for a patient from an external lab API.

    :param patient_id: Required: patient ID
    """
    return await call_labs_api(patient_id)

@mcp_app.tool()
async def schedule_follow_up_tool(patient_id: str, preferred_window: str):
    """
    Schedule a follow-up appointment for a patient via scheduling API.

    :param patient_id: Required: patient ID
    :param preferred_window: Required: preferred date/time window for the appointment
    """
    return await call_scheduler_api(patient_id, preferred_window)

@mcp_app.tool()
async def perplexity_chat_tool(
    prompt: str,
    model: str = "sonar",
    system_prompt: Optional[str] = None,
    max_tokens: int = 512,
    temperature: float = 0.2,
):
    """
    Ask Perplexity a question and return answer text + citations.

    :param prompt: Required: user prompt/question
    :param model: Optional: Perplexity model name (default: sonar)
    :param system_prompt: Optional: system prompt for instructions/behavior
    :param max_tokens: Optional: response token limit
    :param temperature: Optional: sampling temperature
    """
    try:
        return await call_perplexity_api(
            prompt,
            model=model,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )
    except Exception as e:
        # Avoid crashing the stateless session TaskGroup; return structured error.
        return {"error": str(e), "error_type": type(e).__name__}

# -----------------------
# Mount FastMCP under /
# -----------------------
async def homepage(request):
    return PlainTextResponse("Healthcare MCP Server running")

def _streamable_mcp_asgi_app():
    """
    Compatibility shim across FastMCP versions.
    """
    # Preferred name in current MCP Python SDK.
    if hasattr(mcp_app, "streamable_http_app"):
        return mcp_app.streamable_http_app()
    # Fallbacks for other variants.
    if hasattr(mcp_app, "http_app"):
        return mcp_app.http_app()
    raise RuntimeError("FastMCP does not expose a streamable/http ASGI app on this version.")

@asynccontextmanager
async def lifespan(app):
    """
    Starlette lifespan wrapper that works across MCP SDK versions.
    """
    sm = getattr(mcp_app, "session_manager", None)
    if sm is None or not hasattr(sm, "run"):
        yield
        return

    maybe_cm = sm.run()
    # Newer versions: async context manager
    if hasattr(maybe_cm, "__aenter__") and hasattr(maybe_cm, "__aexit__"):
        async with maybe_cm:
            yield
        return

    # Fallback: if it's an awaitable setup, just await it.
    await maybe_cm
    yield

starlette_app = Starlette(
    debug=True,
    routes=[
        Route("/", homepage),
        Mount("/", app=_streamable_mcp_asgi_app()),
    ],
    lifespan=lifespan,
)

if __name__ == "__main__":
    uvicorn.run(starlette_app, host="0.0.0.0", port=APP_PORT)