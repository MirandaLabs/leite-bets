import os
import random
import logging

logger = logging.getLogger(__name__)

class ProxyManager:
    """Gerenciador de Proxy Residencial com Sessão Fixa Segura (Max 100)"""
    
    def __init__(self):
        # Usuário limpo (Apenas zecdovnb) configurado no Railway
        self.user = os.getenv("WEBSHARE_USERNAME") 
        self.password = os.getenv("WEBSHARE_PASSWORD")
        self.host = os.getenv("WEBSHARE_HOST", "p.webshare.io")
        self.port = os.getenv("WEBSHARE_PORT", "80")

    def get_random_proxy(self):
        """Sorteia um ID baixo e anexa ao usuário para Rotação Garantida."""
        if not all([self.user, self.password]):
            logger.warning("⚠️ Variáveis de proxy ausentes! Rodando sem proxy.")
            return None
        
        # Sorteia apenas até 100 (Extremamente seguro, impossível dar 407)
        session_id = random.randint(1, 100)
        
        # Injeta o sufixo (ex: zecdovnb-42)
        user_with_session = f"{self.user}-{session_id}"
        
        proxy_url = f"http://{user_with_session}:{self.password}@{self.host}:{self.port}"
        
        safe_log = proxy_url.replace(self.password, "***")
        logger.info(f"🕵️ Usando IP Residencial Fixo (Sessão {session_id}): {safe_log}")
        
        return proxy_url