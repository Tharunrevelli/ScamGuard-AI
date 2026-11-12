"""
Vercel Serverless Entrypoint for ScamGuard AI FastAPI Backend.
Exposes the ASGI application with Vercel path-resolution middleware.
"""
import os
import sys
from urllib.parse import parse_qs, urlencode

# Ensure repository root is on sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.app.main import app as fastapi_app


class VercelPathMiddleware:
    """
    Vercel rewrites forward requests to /api/index.py?__path__=<original_path>.
    This ASGI middleware restores scope['path'] and cleans scope['query_string']
    so FastAPI routing and dependency injection work seamlessly.
    """
    def __init__(self, inner_app):
        self.inner_app = inner_app

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http":
            query_bytes = scope.get("query_string", b"")
            if query_bytes:
                query_str = query_bytes.decode("utf-8", "ignore")
                qs = parse_qs(query_str, keep_blank_values=True)
                if "__path__" in qs:
                    matched_path = qs.pop("__path__")[0]
                    scope["path"] = matched_path
                    scope["raw_path"] = matched_path.encode("utf-8")
                    scope["query_string"] = urlencode(qs, doseq=True).encode("utf-8")
        await self.inner_app(scope, receive, send)


app = VercelPathMiddleware(fastapi_app)
handler = app
