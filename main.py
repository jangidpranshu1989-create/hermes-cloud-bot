import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import json
import urllib.request  # बिना किसी एक्स्ट्रा पैकेज (जैसे requests) के वेबहुक भेजने के लिए

def send_to_make_webhook(message_text, user_id):
    """Make.com Webhook पर डेटा भेजने का फंक्शन"""
    webhook_url = os.getenv('WEBHOOK_URL')
    if not webhook_url:
        print("DEBUG: WEBHOOK_URL Environment Variable missing!", flush=True)
        return
    
    data = {
        "message": message_text,
        "user_id": user_id,
        "agent": "Hermes Agent"
    }
    
    try:
        req = urllib.request.Request(
            webhook_url, 
            data=json.dumps(data).encode('utf-8'), 
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            print(f"DEBUG: Data sent to Make.com! Status code: {response.getcode()}", flush=True)
    except Exception as e:
        print(f"DEBUG: Error sending to Make.com: {e}", flush=True)

def setup_hermes():
    os.makedirs(os.path.expanduser("~/.hermes"), exist_ok=True)

    # Environment profile update logic
    with open(os.path.expanduser("~/.hermes/.env"), "w") as f:
        f.write(f"GITHUB_TOKEN={os.getenv('GITHUB_TOKEN')}\n")
        f.write(f"KILOCODE_API_KEY={os.getenv('KILOCODE_API_KEY')}\n")
        f.write(f"TELEGRAM_BOT_TOKEN={os.getenv('TELEGRAM_BOT_TOKEN')}\n")
        f.write(f"TELEGRAM_ALLOWED_USERS={os.getenv('TELEGRAM_ALLOWED_USERS')}\n")

    # Exact configurations building (Composio Block Removed to fix error)
    with open(os.path.expanduser("~/.hermes/config.yaml"), "w") as f:
        f.write("model:\n")
        f.write("  default: gpt-4.1\n")
        f.write("  provider: copilot\n")
        f.write("  base_url: https://api.githubcopilot.com\n")
        f.write("  api_mode: chat_completions\n")
        f.write("fallback_model:\n")
        f.write("  provider: kilocode\n")
        f.write("  model: \"nvidia/nemotron-3-ultra-550b-a55b:free\"\n")
        f.write("  base_url: https://api.kilo.ai/api/gateway\n")
        f.write("memory:\n")
        f.write("  backend: postgresql\n")
        f.write(f"  url: \"{os.getenv('SUPABASE_URL')}\"\n")
        f.write(f"  key: \"{os.getenv('SUPABASE_KEY')}\"\n")
        f.write("messaging:\n")
        f.write("  gateway: telegram\n")
        f.write("telegram:\n")
        f.write(f"  token: \"{os.getenv('TELEGRAM_BOT_TOKEN')}\"\n")
        f.write(f"  allowed_users: [\"{os.getenv('TELEGRAM_ALLOWED_USERS')}\"]\n")

    with open(os.path.expanduser("~/.hermes/config.yaml")) as _f:
        print("DEBUG CONFIG:\n" + _f.read(), flush=True)
    print("Launching Correct Hermes Gateway Bridge...")

    # पुराना एरर टेस्ट कमांड हटा दिया गया है
    subprocess.Popen("hermes gateway run --replace", shell=True)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Hermes Secure Database Agent is Fully Synchronized!")

        # जैसे ही Render का हेल्थ चेक पिंग (GET) आएगा या कोई बोट एक्टिविटी होगी, टेस्ट के लिए मेक को डेटा ट्रिगर करेगा
        allowed_user = os.getenv('TELEGRAM_ALLOWED_USERS', 'Unknown')
        threading.Thread(target=send_to_make_webhook, args=("Bot Active & Running on Render", allowed_user)).start()

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

if __name__ == "__main__":
    threading.Thread(target=setup_hermes, daemon=True).start()

    port = int(os.getenv("PORT", 10000))
    server_address = ('', port)
    print(f"Web server active parameters locked on port: {port}")
    HTTPServer(server_address, SimpleHTTPRequestHandler).serve_forever()
