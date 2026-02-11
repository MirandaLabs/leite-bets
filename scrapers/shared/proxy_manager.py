import os
import logging

logger = logging.getLogger(__name__)

class ProxyManager:
    """Gerenciador de Proxy Oficial (Webshare Residential / Backbone)"""
    
    def __init__(self):
        self.user = os.getenv("WEBSHARE_USERNAME") 
        self.password = os.getenv("WEBSHARE_PASSWORD")
        # Por padrão, a Webshare usa proxy.webshare.io ou p.webshare.io
        self.host = os.getenv("WEBSHARE_HOST", "p.webshare.io")
        self.port = os.getenv("WEBSHARE_PORT", "80")

    def get_random_proxy(self):
        """Retorna o endpoint da Webshare sem injetar sufixos dinâmicos."""
        if not all([self.user, self.password]):
            logger.warning("⚠️ Variáveis de proxy ausentes! Rodando sem proxy.")
            return None
        
        # Usa estritamente o usuário configurado na nuvem
        proxy_url = f"http://{self.user}:{self.password}@{self.host}:{self.port}"
        
        safe_log = proxy_url.replace(self.password, "***")
        logger.info(f"🕵️ Usando Proxy Residencial (Webshare Endpoint): {safe_log}")
        
        return proxy_url