# scrapers/base/bet365/parser.py

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

def parse_odd_value(raw_value: str) -> Optional[float]:
    """Converte string '1.50' para float 1.50."""
    try:
        if not raw_value:
            return None
        return float(raw_value.strip())
    except ValueError:
        logger.warning(f"Falha ao converter odd: {raw_value}")
        return None

def normalize_selection_name(raw_name: str, home_team: str, away_team: str) -> str:
    """
    Tenta padronizar o nome da seleção para chaves universais (1, X, 2, 1X, etc).
    Isso é crucial para a arbitragem depois.
    """
    clean_name = raw_name.strip().lower()
    home = home_team.strip().lower()
    away = away_team.strip().lower()

    # Lógica para Dupla Hipótese
    if f"{home} ou empate" in clean_name:
        return "1X"
    if f"{away} ou empate" in clean_name:
        return "X2"
    if f"{home} ou {away}" in clean_name or "empate anula" not in clean_name and " ou " in clean_name: 
        return "12"
    
    # Lógica para 1X2 Simples
    if clean_name == home:
        return "1"
    if clean_name == away:
        return "2"
    if "empate" in clean_name:
        return "X"

    return raw_name 