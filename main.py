import os
import subprocess
import sys
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

MAX_STARTUP_WAIT = 300  # seconds to wait for gateway to become healthy


def _write_env() -> None:
    os.makedirs(os.path.expanduser("~/.hermes"), exist_ok=True)
    env_path = os.path.expanduser("~/.hermes/.env")
    lines = []
    for key in ("GITHUB_TOKEN", "KILOCODE_API_KEY", "TELEGRAM_BOT_TOKEN"):
        val = os.getenv(key)
        if not val:
            raise RuntimeError(f"Missing required environment variable: {key}")
        lines.append(f"{key}={val}")
    lines.append(f"TELEGRAM_ALLOWED_USERS={os.getenv('TELEGRAM_ALLOWED_USERS', '')}")
    lines.append("HERMES_LOG_LEVEL=DEBUG")
    with open(env_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def _write_config() -> None:
    config_path = os.path.expanduser("~/.hermes/config.yaml")
    allowed = os.getenv("TELEGRAM_ALLOWED_USERS", "")
    config = f"""model:
  default: gpt-4.1
  provider: copilot
  base_url: https://api.githubcopilot.com
  api_mode: chat_completions
  agent:
    tool_use_enforcement: true
fallback_model:
  provider: kilocode
  model: "nvidia/nemotron-3-ultra-550b-a55b:free"
  base_url: https://api.kilo.ai/api/gateway
system_prompt: "You are an advanced AI Agent. You have access to tools for Gmail, Google Drive, Notion, web search, browser automation, terminal, files, memory, skills, task planning, delegation, cron, and messaging. You MUST use these tools to execute requests directly whenever a user asks you to do a task."
messaging:
  gateway: telegram
telegram:
  token: "{os.getenv('TELEGRAM_BOT_TOKEN')}"
  allowed_users: ["{allowed}"]
timezone: Asia/Kolkata
"""
    with open(config_path, "w") as f:
        f.write(config)


def _wait_for_gateway() -> None:
    deadline = time.time() + MAX_STARTUP_WAIT
    while time.time() < deadline:
        try:
            import urllib.request
            req = urllib.request.Request(
                "http://localhost:10000/",
                headers={"User-Agent": "Hermes-HealthCheck/1.0"},
            )
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    print("Gateway is healthy.", flush=True)
                    return
        except Exception:
            pass
        time.sleep(2)
    print("WARNING: Gateway did not become healthy within timeout.", flush=True)


def setup_hermes() -> None:
    print("Initializing Hermes Agent...", flush=True)
    _write_env()
    _write_config()

    print("Launching Hermes Autonomous Gateway...", flush=True)
    gateway_proc = subprocess.Popen(
        ["hermes", "gateway", "run", "--replace"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    threading.Thread(target=_wait_for_gateway, daemon=True).start()

    # Forward gateway logs to stdout so Render captures them.
    assert gateway_proc.stdout is not None
    for line in gateway_proc.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()

    gateway_proc.wait()
    print(f"Gateway exited with code {gateway_proc.returncode}", flush=True)


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Hermes Agent Connected")

    def do_HEAD(self) -> None:
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def log_message(self, format: str, *args) -> None:  # type: ignore[override]
        # Suppress default HTTP request logging to keep Render logs clean.
        pass


if __name__ == "__main__":
    threading.Thread(target=setup_hermes, daemon=True).start()
    port = int(os.getenv("PORT", 10000))
    HTTPServer(("", port), SimpleHTTPRequestHandler).serve_forever()
