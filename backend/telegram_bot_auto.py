import os
import asyncio
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode
from dotenv import load_dotenv
from models import SessionLocal
from arbitrage import buscar_oportunidades_automaticas, limpar_eventos_antigos

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN não encontrado no .env")
if not TELEGRAM_CHAT_ID:
    raise ValueError("TELEGRAM_CHAT_ID não encontrado no .env")

bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Configurações
CHECK_INTERVAL = 60
MIN_PROFIT_PERCENT = 1.0
VALORES_TESTE = [10, 20, 50, 100]

# Cache de oportunidades já enviadas
oportunidades_enviadas = set()
ultima_limpeza_cache = datetime.now()

def formatar_mensagem_oportunidade(oportunidade: dict, valor: float) -> str:
    event = oportunidade['event']
    bet1 = oportunidade['bet1']
    bet2 = oportunidade['bet2']
    
    from arbitrage import calcular_hedge
    resultado = calcular_hedge(valor, bet1['odd'], bet2['odd'])
    
    mensagem = f"""
🎯 <b>OPORTUNIDADE DE ARBITRAGEM!</b>

⚽ <b>Jogo:</b> {event['home_team']} x {event['away_team']}
🏆 <b>Campeonato:</b> {event['league']}

💰 <b>APOSTA 1:</b>
   • <b>{bet1['description']}</b> ({bet1['market']})
   • Casa: {bet1['bookmaker']}
   • Odd: {bet1['odd']}
   • Apostar: R$ {valor:.2f}

💰 <b>APOSTA 2:</b>
   • <b>{bet2['description']}</b> ({bet2['market']})
   • Casa: {bet2['bookmaker']}
   • Odd: {bet2['odd']}
   • Apostar: R$ {resultado['aposta_oposta']:.2f}

✅ <b>RESULTADO GARANTIDO:</b>
   • Total investido: R$ {resultado['total_investido']:.2f}
   • Retorno: R$ {resultado['retorno_garantido']:.2f}
   • <b>Lucro: R$ {resultado['lucro']:.2f} (+{resultado['lucro_percentual']:.1f}%)</b>

💡 <i>Com Double Chance você cobre TODOS os 3 resultados!</i>
⏰ <i>Válido até as odds mudarem</i>
"""
    return mensagem

async def enviar_para_grupo(chat_id: str, mensagem: str):
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=mensagem,
            parse_mode=ParseMode.HTML
        )
        print(f"✅ Mensagem enviada para o chat {chat_id}")
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")

async def monitorar_oportunidades():
    global oportunidades_enviadas, ultima_limpeza_cache
    
    print("🤖 Bot iniciado! Monitorando oportunidades...")
    print(f"📊 Configurações:")
    print(f"   • Intervalo: {CHECK_INTERVAL}s")
    print(f"   • Lucro mínimo: {MIN_PROFIT_PERCENT}%")
    print(f"   • Chat ID: {TELEGRAM_CHAT_ID}")
    print(f"   • Valores: {VALORES_TESTE}\n")
    
    # Envia mensagem de início
    mensagem_inicio = """
🥛 <b>LeiteBets iniciado!</b>

O bot está monitorando oportunidades de arbitragem.
Você receberá notificações automaticamente quando encontrarmos boas oportunidades! 🎯
"""
    await enviar_para_grupo(TELEGRAM_CHAT_ID, mensagem_inicio)
    
    ciclos_sem_oportunidades = 0
    
    while True:
        try:
            db = SessionLocal()
            
            # NOVO: Limpa eventos antigos a cada ciclo
            limpar_eventos_antigos(db)
            
            # Busca oportunidades
            oportunidades = buscar_oportunidades_automaticas(
                db,
                valor_base=100.0,
                min_profit_percent=MIN_PROFIT_PERCENT
            )
            
            if oportunidades:
                print(f"🔍 Encontradas {len(oportunidades)} oportunidade(s)!")
                ciclos_sem_oportunidades = 0
                
                for oportunidade in oportunidades:
                    # ID único da oportunidade baseado em evento + casas
                    opp_id = f"{oportunidade['event']['home_team']}-{oportunidade['event']['away_team']}-{oportunidade['bet1']['bookmaker']}-{oportunidade['bet2']['bookmaker']}"
                    
                    # Verifica se já enviou essa combinação
                    if opp_id not in oportunidades_enviadas:
                        print(f"📤 Enviando oportunidade: {opp_id}")
                        
                        # Envia para cada valor de teste
                        for valor in VALORES_TESTE:
                            mensagem = formatar_mensagem_oportunidade(oportunidade, valor)
                            await enviar_para_grupo(TELEGRAM_CHAT_ID, mensagem)
                            await asyncio.sleep(1)  # Delay para não spammar
                        
                        oportunidades_enviadas.add(opp_id)
                        print(f"✅ Oportunidade {opp_id} enviada!\n")
                    else:
                        print(f"⏭️  Oportunidade {opp_id} já foi enviada anteriormente")
            else:
                ciclos_sem_oportunidades += 1
                print(f"⏳ [{datetime.now().strftime('%H:%M:%S')}] Nenhuma oportunidade no momento... (ciclo {ciclos_sem_oportunidades})")
                
                # NOVO: Limpa cache se ficar muito tempo sem oportunidades (para reenviar quando voltarem)
                if ciclos_sem_oportunidades >= 10:  # 10 minutos sem oportunidades
                    if len(oportunidades_enviadas) > 0:
                        print(f"🧹 Limpando cache de {len(oportunidades_enviadas)} oportunidades antigas...")
                        oportunidades_enviadas.clear()
                    ciclos_sem_oportunidades = 0
            
            db.close()
            
        except Exception as e:
            print(f"❌ Erro no monitoramento: {e}")
            import traceback
            traceback.print_exc()
        
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    print("=" * 50)
    print("🥛 LeiteBets - Bot de Arbitragem (Auto)")
    print("=" * 50)
    asyncio.run(monitorar_oportunidades())