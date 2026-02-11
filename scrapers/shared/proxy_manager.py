import os
import random
import logging
import ti

logger = logging.getLogger(__name__)

class ProxyManager:
    """Gerenciador de Proxy Residencial com Sticky Sessions (Sessão Fixa)"""
    
    def __init__(self):
        # O usuário limpo, sem -rotate e sem -BR-
        self.user = os.getenv("WEBSHARE_USERNAME") 
        self.password = os.getenv("WEBSHARE_PASSWORD")
        self.host = os.getenv("WEBSHARE_HOST", "p.webshare.io")
        self.port = os.getenv("WEBSHARE_PORT", "80")

    def get_random_proxy(self):
        """Sorteia um ID de Sessão para manter o mesmo IP durante o carregamento da página."""
        if not all([self.user, self.password]):
            logger.warning("⚠️ Variáveis de proxy ausentes! Rodando sem proxy.")
            return None
        
        # Sorteia um número de 1 a 100.000 para forçar a Webshare a dar um IP residencial novo
        session_id = random.randint(1, 100000)
        
        # Monta o usuário (Exemplo: zecdovnb-8452)
        user_with_session = f"{self.user}-{session_id}"
        
        proxy_url = f"http://{user_with_session}:{self.password}@{self.host}:{self.port}"
        
        safe_log = proxy_url.replace(self.password, "***")
        logger.info(f"🕵️ Usando IP Residencial Fixo (Sessão {session_id}): {safe_log}")
        
        return proxy_url