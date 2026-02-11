import os
import random
import logging
import requests
from urllib.parse import urlparse
import time

logger = logging.getLogger(__name__)

class ProxyManager:
    """Gerenciador Otimizado para Proxies Residenciais Rotativos da Webshare"""
    
    def __init__(self):
        # Carrega as variáveis de ambiente
        self.username = os.getenv("WEBSHARE_USERNAME")  # Nome de usuário SEM o sufixo
        self.password = os.getenv("WEBSHARE_PASSWORD")
        
        # Configurações da Webshare
        self.proxy_host = os.getenv("WEBSHARE_HOST", "p.webshare.io")
        self.proxy_port = os.getenv("WEBSHARE_PORT", "80")
        self.use_https = os.getenv("WEBSHARE_USE_HTTPS", "false").lower() == "true"
        
        # Configuração do pool de proxies
        self.proxy_count = int(os.getenv("WEBSHARE_PROXY_COUNT", "10000"))
        
        if not all([self.username, self.password]):
            logger.warning("⚠️ Variáveis do Webshare não configuradas. Rodando sem proxy!")
            self.proxy_count = 0
        else:
            logger.info(f"✅ Gerenciador Webshare configurado. Usuário: {self.username}")
    
    def get_random_proxy(self, max_attempts: int = 3) -> str:
        """Retorna uma URL de proxy funcional da Webshare"""
        if not all([self.username, self.password]) or self.proxy_count <= 0:
            logger.info("🚨 Rodando sem proxy (configuração ausente)")
            return None
        
        for attempt in range(max_attempts):
            try:
                # Gera um número de sessão aleatório
                session_id = random.randint(1, 100000)
                
                # **IMPORTANTE**: Formato CORRETO da Webshare
                # Formato 1: usuario-sessao (mais comum)
                # Formato 2: usuario-BR-sessao (com país)
                # Vamos tentar ambos
                
                # Primeiro tenta o formato simples
                proxy_username = f"{self.username}-{session_id}"
                
                # Monta a URL do proxy
                protocol = "https" if self.use_https else "http"
                proxy_url = f"{protocol}://{proxy_username}:{self.password}@{self.proxy_host}:{self.proxy_port}"
                
                safe_log = proxy_url.replace(self.password, "***")
                logger.info(f"🔧 Tentando proxy [{attempt+1}/{max_attempts}]: {safe_log}")
                
                # Testa rapidamente se o proxy funciona
                if self._test_proxy_quick(proxy_url):
                    logger.info(f"✅ Proxy testado e funcionando")
                    return proxy_url
                else:
                    logger.warning(f"❌ Proxy não respondeu, tentando próximo...")
                    
            except Exception as e:
                logger.error(f"❌ Erro ao configurar proxy: {str(e)}")
        
        logger.error("🚨 Todos os proxies testados falharam")
        return None
    
    def _test_proxy_quick(self, proxy_url: str) -> bool:
        """Teste rápido do proxy usando uma requisição simples"""
        try:
            # Usa um teste rápido com timeout baixo
            test_proxies = {
                "http": proxy_url,
                "https": proxy_url
            }
            
            # Testa com um site simples
            response = requests.get(
                "http://httpbin.org/ip",
                proxies=test_proxies,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.debug(f"✅ Proxy respondeu: {response.json()}")
                return True
                
        except requests.exceptions.ProxyError as e:
            logger.debug(f"❌ Erro de proxy: {str(e)}")
        except requests.exceptions.ConnectTimeout:
            logger.debug("❌ Timeout na conexão do proxy")
        except Exception as e:
            logger.debug(f"❌ Erro no teste do proxy: {str(e)}")
        
        return False
    
    def get_proxy_config(self):
        """Retorna a configuração do proxy para o Playwright"""
        proxy_url = self.get_random_proxy()
        
        if not proxy_url:
            return None
        
        try:
            parsed = urlparse(proxy_url)
            
            # Formato correto para o Playwright
            return {
                "server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}",
                "username": parsed.username,
                "password": parsed.password
            }
        except Exception as e:
            logger.error(f"❌ Erro ao parsear URL do proxy: {str(e)}")
            return None