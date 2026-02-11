import os
import random
import logging
import requests
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ProxyManager:
    """Gerenciador Otimizado para Proxies Residenciais Rotativos (Pool gigante)"""
    
    def __init__(self):
        # Carrega as variáveis uma única vez quando o sistema inicia
        self.user = os.getenv("WEBSHARE_USER")  # Alterado para USER
        self.password = os.getenv("WEBSHARE_PASSWORD")
        self.host = os.getenv("WEBSHARE_HOST", "p.webshare.io")
        
        # Verifica qual porta usar baseado no protocolo
        self.use_https = os.getenv("WEBSHARE_USE_HTTPS", "false").lower() == "true"
        self.port = os.getenv("WEBSHARE_PORT", "443" if self.use_https else "80")
        
        try:
            # Em qual número começa? (Geralmente 1)
            self.start_index = int(os.getenv("WEBSHARE_START_INDEX", "1"))
            # Até qual número vai? (Ex: 10000)
            self.proxy_count = int(os.getenv("WEBSHARE_PROXY_COUNT", "10000"))
        except ValueError:
            self.start_index = 1
            self.proxy_count = 10000

        if not all([self.user, self.password]):
            logger.warning("⚠️ Variáveis do Webshare ausentes. Rodando sem proxy!")
            self.proxy_count = 0
        else:
            logger.info(f"✅ Gerenciador Residencial pronto! Range: {self.user}-{self.start_index} a {self.user}-{self.proxy_count}")
    
    def _test_proxy(self, proxy_url: str) -> bool:
        """Testa se o proxy está funcionando"""
        try:
            test_url = "https://httpbin.org/ip"
            proxies = {
                "http": proxy_url,
                "https": proxy_url
            }
            response = requests.get(test_url, proxies=proxies, timeout=10)
            if response.status_code == 200:
                logger.debug(f"✅ Proxy testado com sucesso: {response.json()}")
                return True
        except Exception as e:
            logger.debug(f"❌ Proxy falhou no teste: {str(e)}")
        return False
    
    def get_random_proxy(self, max_attempts: int = 5) -> str:
        """Sorteia um proxy funcional"""
        if not all([self.user, self.password]) or self.proxy_count <= 0:
            return None
        
        for attempt in range(max_attempts):
            # Sorteia um número entre o start_index e o proxy_count
            random_session_id = random.randint(self.start_index, self.proxy_count)
            
            # Monta o usuário no formato correto: usuario-sessao
            username = f"{self.user}-{random_session_id}"
            
            # Escolhe protocolo baseado na configuração
            protocol = "https" if self.use_https else "http"
            
            # Monta a URL final no formato correto
            proxy_url = f"{protocol}://{username}:{self.password}@{self.host}:{self.port}"
            
            safe_log = proxy_url.replace(self.password, "***")
            logger.info(f"🕵️ Tentando proxy: {safe_log}")
            
            # Testa o proxy antes de retornar
            if self._test_proxy(proxy_url):
                logger.info(f"✅ Proxy funcionando: {safe_log}")
                return proxy_url
            else:
                logger.warning(f"❌ Proxy não respondeu, tentando outro...")
        
        logger.error("🚨 Não foi possível encontrar um proxy funcional")
        return None