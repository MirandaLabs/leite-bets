import os
import random
import logging

logger = logging.getLogger(__name__)

class ProxyManager:
    """Gerenciador Otimizado para Proxies Residenciais Rotativos (Pool gigante)"""
    
    def __init__(self):
        # Carrega as variáveis uma única vez quando o sistema inicia
        self.user_prefix = os.getenv("WEBSHARE_USER_PREFIX")
        self.password = os.getenv("WEBSHARE_PASSWORD")
        self.host = os.getenv("WEBSHARE_HOST", "p.webshare.io")
        self.port = os.getenv("WEBSHARE_PORT", "80")
        
        try:
            # Em qual número começa? (Geralmente 1 ou 11)
            self.start_index = int(os.getenv("WEBSHARE_START_INDEX", "1"))
            # Até qual número vai? (Ex: 10000)
            self.proxy_count = int(os.getenv("WEBSHARE_PROXY_COUNT", "0"))
        except ValueError:
            self.start_index = 1
            self.proxy_count = 0

        if not all([self.user_prefix, self.password]) or self.proxy_count <= 0:
            logger.warning("⚠️ Variáveis do Webshare ausentes ou COUNT é zero. Rodando sem proxy!")
        else:
            logger.info(f"✅ Gerenciador Residencial pronto! Range: {self.user_prefix}{self.start_index} a {self.user_prefix}{self.proxy_count}")

    def get_random_proxy(self):
        """Sorteia um ID de sessão na hora e retorna a URL do proxy."""
        if not all([self.user_prefix, self.password]) or self.proxy_count <= 0:
            return None
        
        # Sorteia um número entre o start_index e o proxy_count
        random_session_id = random.randint(1, 100000)
        
        # Monta o usuário (ex: zecdovnb-8452)
        user = f"{self.user_prefix}BR-{random_session_id}"
        
        # Monta a URL final
        proxy_url = f"http://{user}:{self.password}@{self.host}:{self.port}"
        
        safe_log = proxy_url.replace(self.password, "***")
        logger.info(f"🕵️ Usando proxy residencial: {safe_log}")
        
        return proxy_url