"""
Health Check Server para Railway
Servidor HTTP simples que responde a requisições de health check
enquanto o bot do Telegram roda em background.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime
import threading
import sys

class HealthCheckHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silenciar logs do servidor HTTP
        pass
    
    def do_GET(self):
        """Responde a requisições GET"""
        if self.path == "/" or self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            response = {
                "status": "healthy",
                "service": "telegram-bot",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

def run_health_server(port=8080):
    """Inicia o servidor de health check"""
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"🏥 Health check server rodando na porta {port}")
    server.serve_forever()

def start_health_server_thread(port=8080):
    """Inicia o servidor em uma thread separada"""
    thread = threading.Thread(target=run_health_server, args=(port,), daemon=True)
    thread.start()
    print(f"✅ Health check server iniciado em background na porta {port}")

if __name__ == "__main__":
    # Se executado diretamente, apenas roda o servidor
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_health_server(port)
