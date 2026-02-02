"""
Módulo para determinar o status de eventos baseado no horário
"""
from datetime import datetime, timedelta
from scrapers.shared.models.odds import EventStatus


# Duração média de um jogo de futebol (em minutos)
MATCH_DURATION = 120  # 90 min + intervalo + acréscimos


def get_event_status(event_start_time: datetime) -> EventStatus:
    """
    Determina o status do evento baseado no horário de início
    
    Args:
        event_start_time: Horário de início do evento
        
    Returns:
        EventStatus: upcoming, live ou finished
    """
    if not event_start_time:
        # Se não tem horário, assume upcoming por padrão
        return EventStatus.UPCOMING
    
    now = datetime.now(event_start_time.tzinfo) if event_start_time.tzinfo else datetime.utcnow()
    
    # Se o jogo ainda não começou
    if now < event_start_time:
        return EventStatus.UPCOMING
    
    # Calcula o tempo desde o início do jogo
    elapsed_time = now - event_start_time
    
    # Se passou o tempo de duração do jogo, considera finalizado
    if elapsed_time > timedelta(minutes=MATCH_DURATION):
        return EventStatus.FINISHED
    
    # Se o jogo já começou mas ainda não acabou
    return EventStatus.LIVE


def should_keep_event(event_start_time: datetime) -> bool:
    """
    Verifica se o evento deve ser mantido no sistema
    
    Args:
        event_start_time: Horário de início do evento
        
    Returns:
        bool: True se deve manter, False se deve remover
    """
    status = get_event_status(event_start_time)
    return status != EventStatus.FINISHED
