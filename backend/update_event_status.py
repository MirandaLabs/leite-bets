"""
Script para atualizar status de eventos baseado no horário
Deve ser executado periodicamente (via cron job ou scheduler)
"""
from datetime import datetime, timedelta
from models import get_db, Event, Odd
from sqlalchemy.orm import Session


# Duração média de um jogo de futebol (em minutos)
MATCH_DURATION = 120  # 90 min + intervalo + acréscimos


def update_event_statuses():
    """
    Atualiza o status de todos os eventos baseado no horário atual
    """
    db = next(get_db())
    
    try:
        now = datetime.utcnow()
        updated_count = 0
        finished_count = 0
        
        # Busca todos os eventos que não estão finalizados
        events = db.query(Event).filter(
            Event.status.in_(["upcoming", "live"])
        ).all()
        
        for event in events:
            old_status = event.status
            new_status = determine_status(event.event_date, now)
            
            if old_status != new_status:
                event.status = new_status
                
                # Se o evento foi finalizado, marca o horário e desativa as odds
                if new_status == "finished":
                    event.finished_at = now
                    
                    # Desativa todas as odds deste evento
                    db.query(Odd).filter(
                        Odd.event_id == event.id
                    ).update({"is_active": False})
                    
                    finished_count += 1
                    print(f"✓ Evento finalizado: {event.home_team} vs {event.away_team}")
                
                elif new_status == "live":
                    print(f"⚽ Jogo iniciado: {event.home_team} vs {event.away_team}")
                
                updated_count += 1
        
        db.commit()
        
        print(f"\n📊 Resumo da atualização:")
        print(f"   - Eventos atualizados: {updated_count}")
        print(f"   - Eventos finalizados: {finished_count}")
        print(f"   - Timestamp: {now.isoformat()}")
        
        return {
            "success": True,
            "updated": updated_count,
            "finished": finished_count,
            "timestamp": now.isoformat()
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao atualizar status: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


def determine_status(event_date: datetime, now: datetime) -> str:
    """
    Determina o status do evento baseado no horário
    """
    # Se o jogo ainda não começou
    if now < event_date:
        return "upcoming"
    
    # Calcula o tempo desde o início do jogo
    elapsed_time = now - event_date
    
    # Se passou o tempo de duração do jogo, considera finalizado
    if elapsed_time > timedelta(minutes=MATCH_DURATION):
        return "finished"
    
    # Se o jogo já começou mas ainda não acabou
    return "live"


def cleanup_old_finished_events(days_old: int = 7):
    """
    Remove eventos finalizados há mais de X dias
    
    Args:
        days_old: Número de dias para considerar evento como antigo
    """
    db = next(get_db())
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Busca eventos finalizados há mais de X dias
        old_events = db.query(Event).filter(
            Event.status == "finished",
            Event.finished_at < cutoff_date
        ).all()
        
        deleted_count = len(old_events)
        
        for event in old_events:
            db.delete(event)
        
        db.commit()
        
        print(f"🗑️  Removidos {deleted_count} eventos antigos (> {days_old} dias)")
        
        return {
            "success": True,
            "deleted": deleted_count
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao limpar eventos antigos: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


if __name__ == "__main__":
    print("🔄 Iniciando atualização de status dos eventos...\n")
    
    # Atualiza status dos eventos
    result = update_event_statuses()
    
    # Limpa eventos antigos (opcional)
    if result.get("success"):
        print("\n🧹 Limpando eventos antigos...")
        cleanup_old_finished_events(days_old=7)
