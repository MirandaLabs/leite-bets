import os
import asyncio
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode
from dotenv import load_dotenv
from models import SessionLocal
from arbitrage import buscar_oportunidades_automaticas

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Configurações
CHECK_INTERVAL = 60  # Verifica a cada 60 segundos
MIN_PROFIT_PERCENT = 1.0  # Lucro mínimo de 1%
VALORES_TESTE = [10, 20, 50, 100]  # Valores fixos para V1

# Armazena oportunidades já enviadas para não repetir
oportunidades_enviadas = set()


def formatar_mensagem_oportunidade(oportunidade: dict, valor: float) -> str:
    """
    Formata uma oportunidade em mensagem bonita para o Telegram.
    """
    event = oportunidade['event']
    bet1 = oportunidade['bet1']
    bet2 = oportunidade['bet2']
    
    # Recalcula para o valor específico
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
    """
    Envia mensagem para o grupo do Telegram.
    """
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=mensagem,
            parse_mode=ParseMode.HTML
        )
        print(f"✅ Mensagem enviada para o chat {chat_id}")
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")


async def monitorar_oportunidades(chat_id: str):
    """
    Monitora o banco de dados e envia oportunidades encontradas.
    """
    print("🤖 Bot iniciado! Monitorando oportunidades...")
    print(f"📊 Configurações:")
    print(f"   • Intervalo: {CHECK_INTERVAL}s")
    print(f"   • Lucro mínimo: {MIN_PROFIT_PERCENT}%")
    print(f"   • Chat ID: {chat_id}")
    print(f"   • Valores: {VALORES_TESTE}\n")
    
    while True:
        try:
            db = SessionLocal()
            
            # Busca oportunidades
            oportunidades = buscar_oportunidades_automaticas(
                db,
                valor_base=100.0,  # Base para comparação
                min_profit_percent=MIN_PROFIT_PERCENT
            )
            
            if oportunidades:
                print(f"🔍 Encontradas {len(oportunidades)} oportunidade(s)!")
                
                for oportunidade in oportunidades:
                    # Cria ID único para a oportunidade
                    opp_id = f"{oportunidade['event']['home_team']}-{oportunidade['bet1']['bookmaker']}-{oportunidade['bet2']['bookmaker']}"
                    
                    # Verifica se já enviou essa oportunidade
                    if opp_id not in oportunidades_enviadas:
                        # Envia para cada valor de teste
                        for valor in VALORES_TESTE:
                            mensagem = formatar_mensagem_oportunidade(oportunidade, valor)
                            await enviar_para_grupo(chat_id, mensagem)
                            await asyncio.sleep(1)  # Delay para não spammar
                        
                        oportunidades_enviadas.add(opp_id)
                        print(f"✅ Oportunidade {opp_id} enviada!\n")
            else:
                print(f"⏳ [{datetime.now().strftime('%H:%M:%S')}] Nenhuma oportunidade no momento...")
            
            db.close()
            
        except Exception as e:
            print(f"❌ Erro no monitoramento: {e}")
        
        # Aguarda antes da próxima verificação
        await asyncio.sleep(CHECK_INTERVAL)


async def testar_conexao():
    """
    Testa se o bot está funcionando.
    """
    try:
        me = await bot.get_me()
        print(f"✅ Bot conectado com sucesso!")
        print(f"   • Nome: {me.first_name}")
        print(f"   • Username: @{me.username}")
        print(f"   • ID: {me.id}\n")
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar bot: {e}")
        return False


def main():
    """
    Função principal - inicia o bot.
    """
    print("=" * 50)
    print("🥛 LeiteBets - Bot de Arbitragem V1")
    print("=" * 50)
    
    # IMPORTANTE: Adicione o ID do seu grupo aqui!
    # Para descobrir o ID:
    # 1. Adicione o bot no grupo
    # 2. Mande uma mensagem no grupo
    # 3. Acesse: https://api.telegram.org/bot<SEU_TOKEN>/getUpdates
    # 4. Procure por "chat":{"id": -1234567890}
    
    CHAT_ID = input("\n📱 Digite o ID do grupo do Telegram (ex: -1234567890): ")
    
    if not CHAT_ID:
        print("❌ ID do grupo não fornecido!")
        return
    
    # Executa o bot
    asyncio.run(main_async(CHAT_ID))


async def main_async(chat_id: str):
    """
    Função async principal.
    """
    # Testa conexão
    if not await testar_conexao():
        return
    
    # Envia mensagem de teste
    mensagem_inicio = """
🥛 <b>LeiteBets iniciado!</b>

O bot está monitorando oportunidades de arbitragem.
Você receberá notificações automaticamente quando encontrarmos boas oportunidades! 🎯
"""
    await enviar_para_grupo(chat_id, mensagem_inicio)
    
    # Inicia monitoramento
    await monitorar_oportunidades(chat_id)


if __name__ == "__main__":
    main()