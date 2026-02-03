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
import time

class HealthCheckHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silenciar logs do servidor HTTP para não poluir
        pass
    
    def do_GET(self):
        """Responde a requisições GET"""
        if self.path == "/" or self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            response = {
                "status": "healthy",
                "service": "telegram-bot",
                "timestamp": datetime.utcnow().isoformat(),
                "uptime": time.time()
            }
            
            self.wfile.write(json.dumps(response).encode())
            print(f"✅ Health check respondido: 200 OK")
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not Found"}).encode())

def run_health_server(port=8080):
    """Inicia o servidor de health check"""
    try:
        server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
        print(f"🏥 Health check server ATIVO na porta {port}")
        print(f"🌐 Teste: curl http://localhost:{port}/health")
        server.serve_forever()
    except Exception as e:
        print(f"❌ Erro ao iniciar health server: {e}")
        raise

def start_health_server_thread(port=8080):
    """Inicia o servidor em uma thread separada"""
    print(f"🚀 Iniciando health check server na porta {port}...")
    thread = threading.Thread(
        target=run_health_server, 
        args=(port,), 
        daemon=True,
        name="HealthCheckServer"
    )
    thread.start()
    
    # Aguarda um pouco para garantir que o servidor iniciou
    time.sleep(0.5)
    
    if thread.is_alive():
        print(f"✅ Health check server iniciado com sucesso (thread: {thread.name})")
    else:
        print(f"❌ Health check server FALHOU ao iniciar")
        raise RuntimeError("Health check server não iniciou corretamente")

if __name__ == "__main__":
    # Se executado diretamente, apenas roda o servidor
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print(f"🏥 Iniciando health server standalone na porta {port}...")
    run_health_server(port)
