import os
import random
import logging
import requests
from urllib.parse import urlparse
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class ProxyManager:
    """
    Gerenciador de proxies residenciais rotativos da Webshare.
    
    Utiliza o pool de proxies residenciais com autenticação por sessão.
    Formato correto da URL: http://usuario-sessao:senha@host:porta
    """
    
    def __init__(self):
        # Carrega variáveis de ambiente uma única vez
        self.username = os.getenv("WEBSHARE_USERNAME")
        self.password = os.getenv("WEBSHARE_PASSWORD")
        self.host = os.getenv("WEBSHARE_HOST", "p.webshare.io")
        self.port = os.getenv("WEBSHARE_PORT", "80")
        self.use_https = os.getenv("WEBSHARE_USE_HTTPS", "false").lower() == "true"
        
        # Número total de proxies no pool (usado para sortear sessão)
        try:
            self.proxy_count = int(os.getenv("WEBSHARE_PROXY_COUNT", "10000"))
        except ValueError:
            self.proxy_count = 10000
        
        # Validação das credenciais
        if not self.username or not self.password:
            logger.error(
                "❌ WEBSHARE_USERNAME ou WEBSHARE_PASSWORD não definidos. "
                "Proxy será desativado."
            )
            self.proxy_count = 0
        else:
            logger.info(
                f"✅ ProxyManager inicializado. "
                f"Usuário base: {self.username}, "
                f"Pool: 1-{self.proxy_count}, "
                f"Host: {self.host}:{self.port} ({'HTTPS' if self.use_https else 'HTTP'})"
            )
    
    def _build_proxy_url(self, session_id: int) -> str:
        """
        Constrói a URL completa do proxy com o formato correto.
        Formato: {protocolo}://{username}-{session_id}:{password}@{host}:{port}
        """
        protocol = "https" if self.use_https else "http"
        username_with_session = f"{self.username}-{session_id}"
        return f"{protocol}://{username_with_session}:{self.password}@{self.host}:{self.port}"
    
    def _test_proxy(self, proxy_url: str, timeout: int = 10) -> bool:
        """
        Testa se o proxy está respondendo e é funcional.
        Usa httpbin.org/ip para verificar o IP de saída.
        """
        try:
            proxies = {
                "http": proxy_url,
                "https": proxy_url
            }
            response = requests.get(
                "https://httpbin.org/ip",
                proxies=proxies,
                timeout=timeout
            )
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"✅ Proxy OK - IP de saída: {data.get('origin', 'desconhecido')}")
                return True
            else:
                logger.debug(f"❌ Proxy retornou status {response.status_code}")
                return False
        except requests.exceptions.ProxyError as e:
            logger.debug(f"❌ Erro de proxy: {str(e)}")
        except requests.exceptions.ConnectTimeout:
            logger.debug("❌ Timeout na conexão do proxy")
        except Exception as e:
            logger.debug(f"❌ Falha no teste do proxy: {str(e)}")
        return False
    
    def get_random_proxy(self, max_attempts: int = 5) -> Optional[str]:
        """
        Retorna uma URL de proxy funcional, testada.
        Realiza até `max_attempts` tentativas com diferentes session_ids.
        """
        if not self.username or not self.password or self.proxy_count <= 0:
            logger.warning("⚠️ Proxy não disponível - rodando sem proxy")
            return None
        
        for attempt in range(max_attempts):
            # Sorteia um ID de sessão entre 1 e o total disponível
            session_id = random.randint(1, self.proxy_count)
            proxy_url = self._build_proxy_url(session_id)
            
            # Ofusca a senha para log seguro
            safe_url = proxy_url.replace(self.password, "***") if self.password else proxy_url
            logger.info(f"🔁 Tentativa {attempt+1}/{max_attempts} - {safe_url}")
            
            if self._test_proxy(proxy_url):
                logger.info(f"✅ Proxy funcional encontrado: {safe_url}")
                return proxy_url
            else:
                logger.debug(f"❌ Proxy falhou, tentando outro...")
        
        logger.error("🚨 Nenhum proxy funcional encontrado após várias tentativas")
        return None
    
    def get_proxy_config(self) -> Optional[Dict]:
        """
        Retorna a configuração de proxy no formato exigido pelo Playwright.
        Exemplo: {'server': 'http://p.webshare.io:80', 'username': 'user-12345', 'password': 'senha'}
        """
        proxy_url = self.get_random_proxy()
        if not proxy_url:
            return None
        
        try:
            parsed = urlparse(proxy_url)
            # Playwright espera 'server' no formato 'protocolo://host:porta'
            server = f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
            return {
                "server": server,
                "username": parsed.username,
                "password": parsed.password
            }
        except Exception as e:
            logger.error(f"❌ Erro ao interpretar URL do proxy: {e}")
            return None


# ---------------------------------------------------------------------
# Bloco de teste independente (executar com python proxy_manager.py)
# ---------------------------------------------------------------------
if __name__ == "__main__":
    # Configura logging para ver os detalhes
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Simula as variáveis de ambiente (descomente e preencha para testar localmente)
    # os.environ["WEBSHARE_USERNAME"] = "seu_usuario"
    # os.environ["WEBSHARE_PASSWORD"] = "sua_senha"
    # os.environ["WEBSHARE_PROXY_COUNT"] = "10000"
    
    pm = ProxyManager()
    config = pm.get_proxy_config()
    
    if config:
        print("\n🎯 Configuração de proxy obtida com sucesso:")
        print(f"   Server   : {config['server']}")
        print(f"   Username : {config['username']}")
        print(f"   Password : {'*' * len(config['password'])}")
    else:
        print("\n❌ Não foi possível obter um proxy funcional.")