import os
import logging

logger = logging.getLogger(__name__)

class ProxyManager:
    """Gerenciador para Proxy Residencial Rotativo (Endpoint da Webshare)"""
    
    def __init__(self):
        # Aqui você vai colocar exatamente o usuário que a Webshare te deu
        self.user = os.getenv("WEBSHARE_USERNAME") 
        self.password = os.getenv("WEBSHARE_PASSWORD")
        self.host = os.getenv("WEBSHARE_HOST", "p.webshare.io")
        self.port = os.getenv("WEBSHARE_PORT", "80")

    def get_random_proxy(self):
        """Retorna sempre o mesmo endpoint rotativo. A mágica acontece na Webshare."""
        if not all([self.user, self.password]):
            logger.warning("⚠️ Variáveis de proxy ausentes! Rodando sem proxy.")
            return None
        
        proxy_url = f"http://{self.user}:{self.password}@{self.host}:{self.port}"
        
        safe_log = proxy_url.replace(self.password, "***")
        logger.info(f"🕵️ Conectando ao Rotating Endpoint: {safe_log}")
        
        return proxy_url