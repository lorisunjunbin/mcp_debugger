"""FastAPI-based MCP proxy router.
Forwards all /mcp traffic from :8000 to upstream :3000 while logging request/response details.
"""
import json
import logging
from typing import Dict, Iterable

import httpx
from fastapi import FastAPI, Request, Response
import uvicorn

# Simple stdout logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("mcp_router")

UPSTREAM_BASE = "http://localhost:8000"
LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 3000

app = FastAPI()


@app.api_route("/mcp", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def proxy_mcp(request: Request) -> Response:
    # Capture incoming request details
    body_bytes = await request.body()
    body_text = body_bytes.decode(errors="ignore") if body_bytes else ""
    as_json = _safe_json(body_text)
    logger.info("Incoming %s %s", request.method, request.url)
    logger.info("Incoming headers: %s", dict(request.headers))
    if as_json is not None:
        logger.info("Incoming JSON body: %s", as_json)
    elif body_text:
        logger.info("Incoming raw body: %s", body_text)

    # Forward to upstream
    async with httpx.AsyncClient(timeout=30.0) as client:
        upstream_url = f"{UPSTREAM_BASE}/mcp"
        # Remove host header to let httpx set it; keep others
        forward_headers = _filter_headers(request.headers)
        upstream_response = await client.request(
            request.method,
            upstream_url,
            content=body_bytes,
            headers=forward_headers,
        )

    # Log upstream response
    logger.info("Upstream response status: %s", upstream_response.status_code)
    logger.info("Upstream response headers: %s", dict(upstream_response.headers))
    resp_json = _safe_json(upstream_response.text)
    if resp_json is not None:
        logger.info("Upstream response JSON body: %s", resp_json)
    else:
        logger.info("Upstream response raw body:\n---------------------------\n %s \n---------------------------", upstream_response.text)

    # Return upstream response to caller
    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=_filter_response_headers(upstream_response.headers),
        media_type=upstream_response.headers.get("content-type"),
    )


def _safe_json(text: str):
    try:
        return json.loads(text)
    except Exception:
        return None


def _filter_headers(headers: Iterable[tuple[str, str]] | Dict[str, str]) -> Dict[str, str]:
    # Remove hop-by-hop headers and host to avoid conflicts
    hop_by_hop = {"host", "content-length", "transfer-encoding", "connection"}
    return {k: v for k, v in dict(headers).items() if k.lower() not in hop_by_hop}


def _filter_response_headers(headers: httpx.Headers) -> Dict[str, str]:
    hop_by_hop = {"content-length", "transfer-encoding", "connection"}
    return {k: v for k, v in headers.items() if k.lower() not in hop_by_hop}


if __name__ == "__main__":
    logger.info("Starting MCP proxy router on %s:%s -> %s/mcp", LISTEN_HOST, LISTEN_PORT, UPSTREAM_BASE)
    uvicorn.run("mcp_router:app", host=LISTEN_HOST, port=LISTEN_PORT, reload=False)

