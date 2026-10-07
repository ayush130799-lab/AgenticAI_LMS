"""Launch the API: `python serve.py [--port 8000] [--reload]`.

Equivalent to `uvicorn app.main:app`, but forces the selector event loop on
Windows, where uvicorn's default (Proactor) loop is incompatible with
psycopg's async driver. On Linux/macOS/Docker plain uvicorn works too.
"""
import argparse
import sys

import uvicorn

from app.core.runtime import run_async


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true", help="auto-reload on code changes (dev only)")
    args = parser.parse_args()

    if args.reload:
        # uvicorn's reloader runs the server in a subprocess, which already uses the selector loop on Windows.
        uvicorn.run("app.main:app", host=args.host, port=args.port, reload=True)
        return

    server = uvicorn.Server(uvicorn.Config("app.main:app", host=args.host, port=args.port))
    if sys.platform == "win32":
        run_async(server.serve())
    else:
        server.run()


if __name__ == "__main__":
    main()
