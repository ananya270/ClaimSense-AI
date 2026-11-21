"""Cross-platform production WSGI server launcher for ClaimSense AI.

Supports Waitress (multithreaded Windows/Linux WSGI server) and Gunicorn (pre-fork Linux WSGI server).
"""
import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import Config


def run_server(host: str, port: int, threads: int = 8, workers: int = 4, server_type: str = "auto"):
    """Starts the production WSGI server."""
    os_name = platform.system().lower()
    selected_server = server_type.lower()

    if selected_server == "auto":
        if os_name == "windows":
            selected_server = "waitress"
        else:
            selected_server = "gunicorn"

    print("=" * 72)
    print(" ClaimSense AI — Production WSGI Server")
    print(f" Environment:   {Config.FLASK_ENV.upper()}")
    print(f" Host & Port:   http://{host}:{port}")
    print(f" Architecture:  {selected_server.upper()} (Threads: {threads}, Workers: {workers})")
    print(f" Operating Sys: {platform.platform()}")
    print("=" * 72)

    # 1. Try Waitress
    if selected_server == "waitress":
        try:
            import waitress
            from wsgi import app
            print(f"[INFO] Serving on http://{host}:{port} using Waitress {waitress.__version__} with {threads} threads...")
            waitress.serve(app, host=host, port=port, threads=threads)
            return
        except ImportError:
            print("[WARN] Waitress is not installed. Attempting fallback...", file=sys.stderr)

    # 2. Try Gunicorn (Unix only)
    if selected_server == "gunicorn" and os_name != "windows":
        try:
            cmd = [
                sys.executable,
                "-m", "gunicorn",
                "--workers", str(workers),
                "--threads", str(threads),
                "--worker-class", "gthread",
                "--bind", f"{host}:{port}",
                "--timeout", "120",
                "wsgi:app",
            ]
            print(f"[INFO] Spawning Gunicorn with command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            return
        except Exception as exc:
            print(f"[WARN] Gunicorn failed to launch: {exc}. Attempting fallback...", file=sys.stderr)

    # 3. Graceful fallback to Werkzeug / standard WSGI
    print("[INFO] Launching via built-in application server fallback...")
    from wsgi import app
    app.run(host=host, port=port, debug=False, threaded=True)


def main():
    parser = argparse.ArgumentParser(description="ClaimSense AI Production WSGI Server Runner")
    parser.add_argument("--host", type=str, default=os.getenv("HOST", "127.0.0.1"), help="Binding host")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", 5001)), help="Binding port")
    parser.add_argument("--threads", type=int, default=8, help="Worker thread count (Waitress/Gunicorn)")
    parser.add_argument("--workers", type=int, default=4, help="Process worker count (Gunicorn)")
    parser.add_argument(
        "--server",
        type=str,
        default="auto",
        choices=["auto", "waitress", "gunicorn", "fallback"],
        help="WSGI server backend (default: auto)",
    )

    args = parser.parse_args()
    run_server(
        host=args.host,
        port=args.port,
        threads=args.threads,
        workers=args.workers,
        server_type=args.server,
    )


if __name__ == "__main__":
    main()
