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
        Carrega lista de proxies das variáveis de ambiente
        Aceita formatos: IP_1=ip:porta OU IP_1=ip (usa porta padrão)
        """
        proxies = []
        default_port = os.getenv("PROXY_PORT", "80")
        
        logger.info("🔍 Tentando carregar proxies das variáveis de ambiente...")
        
        # Carregar apenas 3 proxies residenciais (IP_1, IP_2, IP_3)
        for i in range(1, 4):  # IP_1 até IP_3
            ip = os.getenv(f"IP_{i}")
            
            if not ip:
                logger.debug(f"❌ IP_{i} não encontrado")
                continue
            
            ip = ip.strip()
            
            # Se IP já contém porta (formato ip:porta)
            if ':' in ip:
                proxies.append(ip)
                logger.info(f"✅ IP_{i} carregado: {ip}")
            else:
                # Se não tem porta, usar porta padrão
                proxy = f"{ip}:{default_port}"
                proxies.append(proxy)
                logger.info(f"✅ IP_{i} carregado: {proxy} (porta padrão)")
        
        if not proxies:
            logger.warning("⚠️  Nenhum proxy encontrado - scrapers rodarão sem proxy")
            return []
        
        logger.info(f"✅ Total: {len(proxies)} proxies carregados")
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
        proxy = self.get_random_proxy(scraper_name)
        
        if not proxy:
            return None
        
        logger.info(f"🔀 Usando proxy residencial: {proxy}")
        
        # Proxies residenciais próprios - sem autenticação
        proxy_config = {
            "server": f"http://{proxy}"
        }
        
        # Autenticação opcional (caso configure PROXY_USERNAME/PASSWORD)
        proxy_user = os.getenv("PROXY_USERNAME")
        proxy_pass = os.getenv("PROXY_PASSWORD")
        if proxy_user and proxy_pass:
            proxy_config["username"] = proxy_user
            proxy_config["password"] = proxy_pass
            logger.info(f"🔐 Proxy com autenticação")
        
        return proxy_config
    
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
