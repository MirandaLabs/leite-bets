"""
Gerenciador de Proxies para Scrapers
Implementa rotação aleatória de IPs da Webshare
"""
import os
import random
from typing import Optional, Dict
from dotenv import load_dotenv
from scrapers.shared.logger import logger

load_dotenv()


class ProxyManager:
    """
    Gerencia pool de proxies e rotação aleatória
    """
    
    def __init__(self):
        self.proxies = self._load_proxies()
        self.used_proxies = {}  # Track which proxy was used by which scraper
        
    def _load_proxies(self) -> list[str]:
        """
        Carrega lista de IPs do .env
        """
        proxies = []
        
        # Carregar IPs do .env (IP_1 até IP_10)
        for i in range(1, 11):
            ip = os.getenv(f"IP_{i}")
            if ip:
                proxies.append(ip)
        
        if not proxies:
            logger.warning("⚠️  Nenhum proxy encontrado no .env - scrapers rodarão sem proxy")
            return []
        
        logger.info(f"✅ {len(proxies)} proxies carregados: {', '.join(proxies[:3])}{'...' if len(proxies) > 3 else ''}")
        return proxies
    
    def get_random_proxy(self, scraper_name: str = None) -> Optional[str]:
        """
        Retorna um proxy aleatório do pool
        
        Args:
            scraper_name: Nome do scraper (para tracking/logs)
            
        Returns:
            IP do proxy ou None se não houver proxies disponíveis
        """
        if not self.proxies:
            logger.warning("⚠️  Nenhum proxy disponível - scraper rodará sem proxy")
            return None
        
        # Selecionar proxy aleatório
        proxy_ip = random.choice(self.proxies)
        
        # Track qual proxy está sendo usado
        if scraper_name:
            self.used_proxies[scraper_name] = proxy_ip
            logger.info(f"🔄 [{scraper_name.upper()}] Usando proxy: {proxy_ip}")
        else:
            logger.info(f"🔄 Proxy selecionado: {proxy_ip}")
        
        return proxy_ip
    
    def get_proxy_config(self, scraper_name: str = None) -> Optional[Dict[str, str]]:
        """
        Retorna configuração de proxy formatada para Playwright
        
        Args:
            scraper_name: Nome do scraper
            
        Returns:
            Dict com configuração do proxy ou None
        """
        proxy_ip = self.get_random_proxy(scraper_name)
        
        if not proxy_ip:
            return None
        
        # Formato esperado pela Webshare
        # Ajustar porta e credenciais conforme seu plano
        return {
            "server": f"http://{proxy_ip}:80",  # Ajustar porta se necessário
            # Se seus proxies precisam autenticação, adicionar:
            # "username": os.getenv("PROXY_USERNAME"),
            # "password": os.getenv("PROXY_PASSWORD")
        }
    
    def get_used_proxy(self, scraper_name: str) -> Optional[str]:
        """
        Retorna o proxy que está sendo usado por um scraper específico
        """
        return self.used_proxies.get(scraper_name)
    
    def reset_tracking(self):
        """
        Limpa tracking de proxies usados
        """
        self.used_proxies = {}
    
    @property
    def available_proxies_count(self) -> int:
        """
        Retorna quantidade de proxies disponíveis
        """
        return len(self.proxies)
    
    def test_proxy(self, proxy_ip: str) -> bool:
        """
        Testa se um proxy está funcionando
        
        Args:
            proxy_ip: IP do proxy para testar
            
        Returns:
            True se proxy está funcionando, False caso contrário
        """
        # TODO: Implementar teste real de conectividade
        # Pode usar requests com timeout para testar
        return True


# Instância global do gerenciador de proxies
proxy_manager = ProxyManager()


# Helper functions para uso direto
def get_random_proxy(scraper_name: str = None) -> Optional[str]:
    """
    Atalho para obter proxy aleatório
    """
    return proxy_manager.get_random_proxy(scraper_name)


def get_proxy_config(scraper_name: str = None) -> Optional[Dict[str, str]]:
    """
    Atalho para obter configuração de proxy
    """
    return proxy_manager.get_proxy_config(scraper_name)
