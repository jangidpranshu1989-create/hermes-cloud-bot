import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

def setup_hermes():
    os.makedirs(os.path.expanduser("~/.hermes"), exist_ok=True)

    # Environment profile update logic
    with open(os.path.expanduser("~/.hermes/.env"), "w") as f:
        f.write(f"NVIDIA_API_KEY={os.getenv('NVIDIA_API_KEY')}\n")
        f.write(f"TELEGRAM_BOT_TOKEN={os.getenv('TELEGRAM_BOT_TOKEN')}\n")
        f.write(f"TELEGRAM_ALLOWED_USERS={os.getenv('TELEGRAM_ALLOWED_USERS')}\n")

    # Exact configurations building
    with open(os.path.expanduser("~/.hermes/config.yaml"), "w") as f:
        f.write("provider: nvidia\n")
        f.write("model: minimaxai/minimax-m2.7\n")
        f.write("memory:\n")
        f.write("  backend: postgresql\n")
        f.write(f"  url: \"{os.getenv('SUPABASE_URL')}\"\n")
        f.write(f"  key: \"{os.getenv('SUPABASE_KEY')}\"\n")
        f.write("messaging:\n")
        f.write("  gateway: telegram\n")
        f.write("telegram:\n")
        f.write(f"  token: \"{os.getenv('TELEGRAM_BOT_TOKEN')}\"\n")
        f.write(f"  allowed_users: [\"{os.getenv('TELEGRAM_ALLOWED_USERS')}\"]\n")

    print("Launching Correct Hermes Gateway Bridge...")

    # Fixed: 'gateway run' takes no platform/token args — reads from config.yaml
    subprocess.Popen("hermes gateway run --replace", shell=True)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Hermes Secure Database Agent is Fully Synchronized!")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

if __name__ == "__main__":
    # Multithreading configuration to isolate bot routing from port blocks
    threading.Thread(target=setup_hermes, daemon=True).start()

    port = int(os.getenv("PORT", 10000))
    server_address = ('', port)
    print(f"Web server active parameters locked on port: {port}")
    HTTPServer(server_address, SimpleHTTPRequestHandler).serve_forever()
