"""API main entry point - works on both local/Docker and Vercel."""
import os
import sys

# Detect Vercel environment
if os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"):
    # On Vercel, redirect to vercel_app
    from api.vercel_app import app  # noqa: F401
else:
    # Local / Docker - import full app
    from api._main import app  # noqa: F401

__all__ = ["app"]
