import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

def setup_hermes():
    print("Initializing Hermes Agent with Autonomous Tools Access...", flush=True)
    os.makedirs(os.path.expanduser("~/.hermes"), exist_ok=True)

    # 1. Environment profile setup
    with open(os.path.expanduser("~/.hermes/.env"), "w") as f:
        f.write(f"GITHUB_TOKEN={os.getenv('GITHUB_TOKEN')}\n")
        f.write(f"KILOCODE_API_KEY={os.getenv('KILOCODE_API_KEY')}\n")
        f.write(f"COMPOSIO_API_KEY={os.getenv('COMPOSIO_API_KEY')}\n")
        f.write(f"TELEGRAM_BOT_TOKEN={os.getenv('TELEGRAM_BOT_TOKEN')}\n")
        f.write(f"TELEGRAM_ALLOWED_USERS={os.getenv('TELEGRAM_ALLOWED_USERS')}\n")

    # 2. Creating config.yaml with STRICT system instructions for tool usage
    with open(os.path.expanduser("~/.hermes/config.yaml"), "w") as f:
        f.write("model:\n")
        f.write("  default: gpt-4.1\n")
        f.write("  provider: copilot\n")
        f.write("  base_url: https://githubcopilot.com\n")
        f.write("  api_mode: chat_completions\n")
        f.write("fallback_model:\n")
        f.write("  provider: kilocode\n")
        f.write("  model: \"nvidia/nemotron-3-ultra-550b-a55b:free\"\n")
        f.write("  base_url: https://kilo.ai\n")
        
        # This forces the LLM to use Composio actions instead of text guides
        f.write("system_prompt: \"You are a powerful autonomous AI executive. You have direct backend tool access via Composio MCP. When a user asks you to create a folder, list files, write emails, or manage spreadsheets, you MUST call the appropriate composio tool immediately. Never guide the user to do it manually. Execute it yourself.\"\n")
        
        f.write("memory:\n")
        f.write("  backend: postgresql\n")
        f.write(f"  url: \"{os.getenv('SUPABASE_URL')}\"\n")
        f.write(f"  key: \"{os.getenv('SUPABASE_KEY')}\"\n")
        f.write("messaging:\n")
        f.write("  gateway: telegram\n")
        f.write("telegram:\n")
        f.write(f"  token: \"{os.getenv('TELEGRAM_BOT_TOKEN')}\"\n")
        f.write(f"  allowed_users: [\"{os.getenv('TELEGRAM_ALLOWED_USERS')}\"]\n")
        
        # Composio Native HTTP Connection Block
        f.write("mcp_servers:\n")
        f.write("  composio:\n")
        f.write("    url: \"https://composio.dev\"\n")
        f.write("    headers:\n")
        f.write(f"      x-consumer-api-key: \"{os.getenv('COMPOSIO_API_KEY')}\"\n")

    with open(os.path.expanduser("~/.hermes/config.yaml")) as _f:
        print("DEBUG INSTALLED CONFIG:\n" + _f.read(), flush=True)

    print("Launching Hermes Autonomous Gateway...", flush=True)
    subprocess.Popen("hermes gateway run --replace", shell=True)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Hermes Secure Database Agent is Fully Synchronized with Composio!")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

if __name__ == "__main__":
    threading.Thread(target=setup_hermes, daemon=True).start()
    port = int(os.getenv("PORT", 10000))
    HTTPServer(('', port), SimpleHTTPRequestHandler).serve_forever()
