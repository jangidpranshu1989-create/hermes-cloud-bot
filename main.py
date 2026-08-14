import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

def setup_hermes():
    print("Initializing Hermes Agent with Composio Toolset...", flush=True)
    os.makedirs(os.path.expanduser("~/.hermes"), exist_ok=True)

    # 1. Environment profile setup
    with open(os.path.expanduser("~/.hermes/.env"), "w") as f:
        f.write(f"GITHUB_TOKEN={os.getenv('GITHUB_TOKEN')}\n")
        f.write(f"KILOCODE_API_KEY={os.getenv('KILOCODE_API_KEY')}\n")
        f.write(f"COMPOSIO_API_KEY={os.getenv('COMPOSIO_API_KEY')}\n")
        f.write(f"TELEGRAM_BOT_TOKEN={os.getenv('TELEGRAM_BOT_TOKEN')}\n")
        f.write(f"TELEGRAM_ALLOWED_USERS={os.getenv('TELEGRAM_ALLOWED_USERS')}\n")

    # 2. Creating config.yaml (Composio Local App Tools Integration)
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
        f.write("system_prompt: \"You are an advanced AI Agent. You have direct access to Composio tools for Gmail, Google Drive, and Notion. You MUST use these tools to execute requests directly whenever a user asks you to do a task.\"\n")
        f.write("memory:\n")
        f.write("  backend: postgresql\n")
        f.write(f"  url: \"{os.getenv('SUPABASE_URL')}\"\n")
        f.write(f"  key: \"{os.getenv('SUPABASE_KEY')}\"\n")
        f.write("messaging:\n")
        f.write("  gateway: telegram\n")
        f.write("telegram:\n")
        f.write(f"  token: \"{os.getenv('TELEGRAM_BOT_TOKEN')}\"\n")
        f.write(f"  allowed_users: [\"{os.getenv('TELEGRAM_ALLOWED_USERS')}\"]\n")

    print("Syncing Composio Apps Locally...", flush=True)
    # Composio CLI के जरिए ऐप्स को लोकल एनवायरनमेंट में सिंक करना
    subprocess.run(f"composio login {os.getenv('COMPOSIO_API_KEY')}", shell=True)
    subprocess.run("composio apps enable gmail googledrive notion", shell=True)

    print("Launching Hermes Autonomous Gateway...", flush=True)
    subprocess.Popen("hermes gateway run --replace", shell=True)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Hermes Agent Connected via Native Composio Tooling!")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

if __name__ == "__main__":
    threading.Thread(target=setup_hermes, daemon=True).start()
    port = int(os.getenv("PORT", 10000))
    HTTPServer(('', port), SimpleHTTPRequestHandler).serve_forever()
