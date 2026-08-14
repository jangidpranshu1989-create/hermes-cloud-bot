import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

def setup_hermes():
    # 1. Local hidden profile directory generate karna
    os.makedirs(os.path.expanduser("~/.hermes"), exist_ok=True)
    
    # 2. Saari local environment keys aur security structures load karna
    with open(os.path.expanduser("~/.hermes/.env"), "w") as f:
        f.write(f"NVIDIA_API_KEY={os.getenv('NVIDIA_API_KEY')}\n")
        f.write(f"TELEGRAM_BOT_TOKEN={os.getenv('TELEGRAM_BOT_TOKEN')}\n")
        f.write(f"TELEGRAM_ALLOWED_USERS={os.getenv('TELEGRAM_ALLOWED_USERS')}\n")
        f.write(f"SUPABASE_URL={os.getenv('SUPABASE_URL')}\n")
        f.write(f"SUPABASE_KEY={os.getenv('SUPABASE_KEY')}\n")
    
    # 3. Memory structure ko file disk se hatakar Supabase par map karna
    with open(os.path.expanduser("~/.hermes/config.yaml"), "w") as f:
        f.write("provider: nvidia\n")
        f.write("model: minimaxai/minimax-m2.7\n")
        f.write("memory:\n")
        f.write("  backend: postgresql\n")
        f.write(f"  url: \"{os.getenv('SUPABASE_URL')}\"\n")
        f.write(f"  key: \"{os.getenv('SUPABASE_KEY')}\"\n")

    print("Launching Hermes Agent Engine in Database Offloading Mode...")
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Foreground background gateway trigger logic bind karenge
    subprocess.Popen(f"hermes gateway --provider nvidia --gateway telegram --token '{bot_token}'", shell=True)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Render check ping logs capture response
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Hermes Secure Database Agent is Online!")

if __name__ == "__main__":
    setup_hermes()
    # Port parameters binding for Render runtime interface
    server_address = ('', int(os.getenv("PORT", 8080)))
    HTTPServer(server_address, SimpleHTTPRequestHandler).serve_forever()
