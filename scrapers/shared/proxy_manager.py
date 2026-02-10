import os
import random
import logging

logger = logging.getLogger(__name__)

class ProxyManager:
    """Gerenciador de proxies inteligente para Webshare Backbone (p.webshare.io)"""
    
    def __init__(self):
        self.proxies = []
        self._load_proxies()

    def _load_proxies(self):
        """Constrói as URLs de proxy baseadas no prefixo e quantidade."""
        try:
            user_prefix = os.getenv("WEBSHARE_USER_PREFIX")
            password = os.getenv("WEBSHARE_PASSWORD")
            host = os.getenv("WEBSHARE_HOST", "p.webshare.io")
            port = os.getenv("WEBSHARE_PORT", "80")
            
            # Pega a quantidade de proxies (padrão é 0 se não for definido)
            try:
                proxy_count = int(os.getenv("WEBSHARE_PROXY_COUNT", "0"))
            except ValueError:
                proxy_count = 0

            # Validação de segurança
            if not all([user_prefix, password]) or proxy_count <= 0:
                logger.warning("Variáveis do Webshare ausentes ou COUNT é zero. Scraping rodará SEM proxy!")
                return

            # Gera a lista de URLs (ex: do 1 ao 20)
            for i in range(1, proxy_count + 1):
                user = f"{user_prefix}{i}"
                proxy_url = f"http://{user}:{password}@{host}:{port}"
                self.proxies.append(proxy_url)
                
            logger.info(f"{len(self.proxies)} proxies Webshare carregados com sucesso (Rota: {host}).")

        except Exception as e:
            logger.error(f"Erro ao construir lista de proxies: {e}")

    def get_random_proxy(self):
        """Sorteia um proxy para a requisição atual."""
        if not self.proxies:
            return None
        
        # Sorteia um proxy aleatório da lista construída
        chosen_proxy = random.choice(self.proxies)
        
        # Dica: Oculta a senha no log para não vazar no console do Railway
        safe_log = chosen_proxy.replace(os.getenv("WEBSHARE_PASSWORD", ""), "***")
        logger.info(f"Usando proxy: {safe_log}")
        
        return chosen_proxy