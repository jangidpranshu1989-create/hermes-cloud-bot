import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

def setup_hermes():
    os.makedirs(os.path.expanduser("~/.hermes"), exist_ok=True)
    
    # Precise credentials write to configuration container env
    with open(os.path.expanduser("~/.hermes/.env"), "w") as f:
        f.write(f"NVIDIA_API_KEY={os.getenv('NVIDIA_API_KEY')}\n")
        f.write(f"TELEGRAM_BOT_TOKEN={os.getenv('TELEGRAM_BOT_TOKEN')}\n")
        f.write(f"TELEGRAM_ALLOWED_USERS={os.getenv('TELEGRAM_ALLOWED_USERS')}\n")
    
    with open(os.path.expanduser("~/.hermes/config.yaml"), "w") as f:
        f.write("provider: nvidia\n")
        f.write("model: minimaxai/minimax-m2.7\n")
        f.write("memory:\n")
        f.write("  backend: postgresql\n")
        f.write(f"  url: \"{os.getenv('SUPABASE_URL')}\"\n")
        f.write(f"  key: \"{os.getenv('SUPABASE_KEY')}\"\n")

    print("Launching Isolated Bot Bridge...")
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Active serve framework routing configuration parameters pass
    subprocess.Popen(f"hermes serve --gateway telegram --token '{bot_token}'", shell=True)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Hermes Secure Database Agent is Fully Synchronized!")

if __name__ == "__main__":
    # Isolated multithread execute to prevent port block crashes
    threading.Thread(target=setup_hermes, daemon=True).start()
    
    # Fix: Directly lock on port 10000 matching Render profile expectations
    port = int(os.getenv("PORT", 10000))
    server_address = ('', port)
    print(f"Server scaling up lock parameters on port: {port}")
    HTTPServer(server_address, SimpleHTTPRequestHandler).serve_forever()
