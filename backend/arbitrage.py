from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from models import Event, Odd
from datetime import datetime, timedelta

def calcular_hedge(
    aposta_usuario: float,
    odd_usuario: float,
    odd_oposta: float
) -> Dict:
    """
    Calcula a aposta oposta (hedge) para garantir resultado.
    
    Args:
        aposta_usuario: Valor que o usuário quer apostar
        odd_usuario: Odd do time escolhido pelo usuário
        odd_oposta: Odd do Double Chance oposto
    
    Returns:
        Dict com cálculos da arbitragem
    """
    # Calcula quanto apostar no lado oposto
    aposta_oposta = (aposta_usuario * odd_usuario) / odd_oposta
    
    # Total investido
    total_investido = aposta_usuario + aposta_oposta
    
    # Retorno garantido (o menor dos dois cenários)
    retorno_se_usuario_ganha = aposta_usuario * odd_usuario
    retorno_se_oposto_ganha = aposta_oposta * odd_oposta
    retorno_garantido = min(retorno_se_usuario_ganha, retorno_se_oposto_ganha)
    
    # Lucro/Prejuízo
    lucro = retorno_garantido - total_investido
    lucro_percentual = (lucro / total_investido) * 100
    
    # Determinar tipo de oportunidade
    if lucro > 0:
        tipo = "profit"
    elif abs(lucro) < 0.01:  # Breakeven (margem de erro)
        tipo = "breakeven"
    else:
        tipo = "loss-minimize"
    
    return {
        "aposta_oposta": round(aposta_oposta, 2),
        "total_investido": round(total_investido, 2),
        "retorno_garantido": round(retorno_garantido, 2),
        "lucro": round(lucro, 2),
        "lucro_percentual": round(lucro_percentual, 2),
        "tipo": tipo
    }


def encontrar_melhor_odd_double_chance(
    db: Session,
    event_id: str,
    time_usuario: str,
    bookmaker_usuario: str
) -> Optional[Dict]:
    """
    Busca a melhor odd de Double Chance oposta.
    
    Args:
        db: Sessão do banco de dados
        event_id: ID do evento
        time_usuario: Time escolhido pelo usuário ('home' ou 'away')
        bookmaker_usuario: Casa de apostas escolhida pelo usuário
    
    Returns:
        Dict com a melhor odd Double Chance encontrada ou None
    """
    # Busca o evento
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return None
    
    # Busca todas as odds desse evento (exceto a casa do usuário)
    odds = db.query(Odd).filter(
        Odd.event_id == event_id,
        Odd.bookmaker != bookmaker_usuario
    ).all()
    
    if not odds:
        return None
    
    # Determina qual odd Double Chance procurar
    if time_usuario == "home":
        # Se usuário apostou no mandante, procura melhor odd de "Visitante ou Empate"
        odds_validas = [o for o in odds if o.away_or_draw_odd is not None]
        if not odds_validas:
            return None
        melhor_odd = max(odds_validas, key=lambda x: float(x.away_or_draw_odd))
        return {
            "bookmaker": melhor_odd.bookmaker,
            "market": "Double Chance",
            "description": f"{event.away_team} ou Empate",
            "odd": float(melhor_odd.away_or_draw_odd)
        }
    else:
        # Se usuário apostou no visitante, procura melhor odd de "Mandante ou Empate"
        odds_validas = [o for o in odds if o.home_or_draw_odd is not None]
        if not odds_validas:
            return None
        melhor_odd = max(odds_validas, key=lambda x: float(x.home_or_draw_odd))
        return {
            "bookmaker": melhor_odd.bookmaker,
            "market": "Double Chance",
            "description": f"{event.home_team} ou Empate",
            "odd": float(melhor_odd.home_or_draw_odd)
        }


def processar_arbitragem(
    db: Session,
    event_id: str,
    time_usuario: str,
    bookmaker_usuario: str,
    aposta_usuario: float
) -> Optional[Dict]:
    """
    Processa toda a lógica de arbitragem para uma aposta usando Double Chance.
    
    Args:
        db: Sessão do banco de dados
        event_id: ID do evento
        time_usuario: Time escolhido ('home' ou 'away')
        bookmaker_usuario: Casa de apostas escolhida
        aposta_usuario: Valor da aposta
    
    Returns:
        Dict completo com sugestão de arbitragem ou None se não encontrar
    """
    # Busca o evento
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return None
    
    # Busca a odd do usuário
    odd_usuario_db = db.query(Odd).filter(
        Odd.event_id == event_id,
        Odd.bookmaker == bookmaker_usuario
    ).first()
    
    if not odd_usuario_db:
        return None
    
    # Pega a odd correta baseada no time escolhido
    if time_usuario == "home":
        odd_usuario = float(odd_usuario_db.home_odd)
        time_usuario_nome = event.home_team
    else:
        odd_usuario = float(odd_usuario_db.away_odd)
        time_usuario_nome = event.away_team
    
    # Encontra a melhor odd Double Chance oposta
    melhor_oposta = encontrar_melhor_odd_double_chance(
        db, event_id, time_usuario, bookmaker_usuario
    )
    
    if not melhor_oposta:
        return None
    
    # Calcula o hedge
    resultado = calcular_hedge(
        aposta_usuario,
        odd_usuario,
        melhor_oposta["odd"]
    )
    
    return {
        "event": {
            "id": event.id,
            "home_team": event.home_team,
            "away_team": event.away_team,
            "league": event.league,
            "event_date": event.event_date.isoformat()
        },
        "user_bet": {
            "team": time_usuario_nome,
            "bookmaker": bookmaker_usuario,
            "market": "Resultado Final",
            "odd": odd_usuario,
            "amount": aposta_usuario
        },
        "hedge_bet": {
            "description": melhor_oposta["description"],
            "bookmaker": melhor_oposta["bookmaker"],
            "market": "Double Chance",
            "odd": melhor_oposta["odd"],
            "amount": resultado["aposta_oposta"]
        },
        "result": resultado
    }


def buscar_oportunidades_automaticas(
    db: Session,
    valor_base: float = 100.0,
    min_profit_percent: float = 1.0
) -> List[Dict]:
    """
    Busca oportunidades de arbitragem automaticamente usando Double Chance.
    Filtra apenas eventos ativos (upcoming ou live) e recentes.
    
    Args:
        db: Sessão do banco
        valor_base: Valor base para calcular (default: R$ 100)
        min_profit_percent: Lucro mínimo em % (default: 1%)
    
    Returns:
        Lista de oportunidades encontradas
    """
    oportunidades = []
    
    # NOVO: Busca eventos upcoming OU live que ainda não expiraram
    now = datetime.utcnow()
    cutoff_time = now - timedelta(hours=3)  # Ignora jogos de mais de 3h atrás
    
    events = db.query(Event).filter(
        Event.status.in_(["upcoming", "live"]),
        Event.event_date > cutoff_time
    ).all()
    
    for event in events:
        # Busca todas as odds desse evento
        odds = db.query(Odd).filter(Odd.event_id == event.id).all()
        
        if len(odds) < 2:
            continue
        
        # Testa combinações: Mandante vs Double Chance (Visitante ou Empate)
        for odd_mandante in odds:
            if odd_mandante.home_odd is None:
                continue
            
            for odd_dc in odds:
                if odd_dc.bookmaker == odd_mandante.bookmaker:
                    continue
                if odd_dc.away_or_draw_odd is None:
                    continue
                
                resultado = calcular_hedge(
                    valor_base,
                    float(odd_mandante.home_odd),
                    float(odd_dc.away_or_draw_odd)
                )
                
                if resultado["tipo"] == "profit" and resultado["lucro_percentual"] >= min_profit_percent:
                    oportunidades.append({
                        "event": {
                            "home_team": event.home_team,
                            "away_team": event.away_team,
                            "league": event.league
                        },
                        "bet1": {
                            "description": event.home_team,
                            "bookmaker": odd_mandante.bookmaker,
                            "market": "Resultado Final",
                            "odd": float(odd_mandante.home_odd),
                            "amount": valor_base
                        },
                        "bet2": {
                            "description": f"{event.away_team} ou Empate",
                            "bookmaker": odd_dc.bookmaker,
                            "market": "Double Chance",
                            "odd": float(odd_dc.away_or_draw_odd),
                            "amount": resultado["aposta_oposta"]
                        },
                        "profit": resultado["lucro"],
                        "profit_percent": resultado["lucro_percentual"]
                    })
        
        # Testa combinações: Visitante vs Double Chance (Mandante ou Empate)
        for odd_visitante in odds:
            if odd_visitante.away_odd is None:
                continue
            
            for odd_dc in odds:
                if odd_dc.bookmaker == odd_visitante.bookmaker:
                    continue
                if odd_dc.home_or_draw_odd is None:
                    continue
                
                resultado = calcular_hedge(
                    valor_base,
                    float(odd_visitante.away_odd),
                    float(odd_dc.home_or_draw_odd)
                )
                
                if resultado["tipo"] == "profit" and resultado["lucro_percentual"] >= min_profit_percent:
                    oportunidades.append({
                        "event": {
                            "home_team": event.home_team,
                            "away_team": event.away_team,
                            "league": event.league
                        },
                        "bet1": {
                            "description": event.away_team,
                            "bookmaker": odd_visitante.bookmaker,
                            "market": "Resultado Final",
                            "odd": float(odd_visitante.away_odd),
                            "amount": valor_base
                        },
                        "bet2": {
                            "description": f"{event.home_team} ou Empate",
                            "bookmaker": odd_dc.bookmaker,
                            "market": "Double Chance",
                            "odd": float(odd_dc.home_or_draw_odd),
                            "amount": resultado["aposta_oposta"]
                        },
                        "profit": resultado["lucro"],
                        "profit_percent": resultado["lucro_percentual"]
                    })
    
    # Ordena por lucro percentual (melhor primeiro)
    oportunidades.sort(key=lambda x: x["profit_percent"], reverse=True)
    
    return oportunidades


def limpar_eventos_antigos(db: Session):
    """
    Marca eventos antigos como 'finished' para não processar mais.
    Eventos são considerados antigos se passaram mais de 3h do horário do jogo.
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=3)
    
    # Atualiza status para finished
    updated = db.query(Event).filter(
        Event.event_date < cutoff_time,
        Event.status != "finished"
    ).update({"status": "finished"})
    
    if updated > 0:
        db.commit()
        print(f"✅ Marcados {updated} evento(s) como finalizados")