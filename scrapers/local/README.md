# Scrapers Locais (Sem Proxy)

Versão alternativa dos scrapers que **não usa proxy**, ideal para execução local usando sua conexão de internet normal.

## 🎯 Objetivo

- Coletar odds das casas de apostas usando sua internet local (sem proxy)
- Enviar dados diretamente para a API no Railway
- Mais simples e rápido para desenvolvimento/teste

## 📋 Pré-requisitos

```bash
# Instalar dependências
pip install playwright requests python-dotenv

# Instalar browser do Playwright
playwright install chromium
```

## ⚙️ Configuração

1. **Configure o .env.local:**

```env
# URL da API no Railway (obrigatório)
API_URL=https://seu-projeto.up.railway.app/api/odds/scraper

# Database (apenas se precisar consultar dados localmente)
DATABASE_URL=postgresql+psycopg://...

# Log
LOG_LEVEL=INFO
```

2. **Verifique se a API Railway está acessível:**

```bash
curl https://seu-projeto.up.railway.app/health
```

## 🚀 Uso

### Rodar Todos os Scrapers

```bash
# Usando o script bash
chmod +x run_local_scraper.sh
./run_local_scraper.sh

# Ou diretamente com Python
python scrapers/local/run_all_local.py

# No Windows (PowerShell)
python scrapers\local\run_all_local.py
```

### Rodar Scraper Individual

```python
from scrapers.local.betano_local import collect_betano_local
from scrapers.shared.sender import send_odds_to_api

# Coleta dados
data = collect_betano_local()

# Envia para API
if data:
    send_odds_to_api(data)
```

## 📊 Scrapers Disponíveis

| Casa | Status | Obs |
|------|--------|-----|
| Betano | ✅ Funcional | Double Chance |
| Esportes da Sorte | ✅ Funcional | Double Chance |
| Superbet | ⚠️ Em desenvolvimento | Parser pendente |
| Bet365 | ⚠️ Em desenvolvimento | Parser pendente |

## 🔍 Como Funciona

1. **Browser Local**: Usa Playwright com configuração simples, sem proxy
2. **Coleta**: Cada scraper acessa o site e extrai as odds
3. **Formato**: Converte para o formato padrão da API
4. **Envio**: Posta os dados para `API_URL/api/odds/scraper`
5. **API**: Processa e salva no banco PostgreSQL no Railway

## 🆚 Diferenças vs Versão com Proxy

| Aspecto | Versão Local | Versão com Proxy |
|---------|-------------|------------------|
| Internet | Sua conexão | Proxy residencial |
| Velocidade | Mais rápida | Pode ser mais lenta |
| Bloqueios | Possível | Menos provável |
| Custo | Grátis | Pago (Webshare) |
| Uso | Desenvolvimento/teste | Produção |

## ⚠️ Limitações

- **Bloqueios**: Sites podem bloquear seu IP se fizer muitas requisições
- **Geolocalização**: Alguns sites podem exigir IP brasileiro
- **Rate Limiting**: Sem rotação de IP, pode atingir limites mais rápido

## 💡 Dicas

1. **Execute com moderação**: Não rode muito frequentemente para evitar bloqueios
2. **Use VPN brasileira**: Se estiver fora do Brasil
3. **Horários**: Rode em horários de menor tráfego (2h-6h AM)
4. **Monitore**: Acompanhe os logs para detectar bloqueios

## 🐛 Troubleshooting

### "Timeout" ao acessar sites

```python
# Aumente o timeout no collector
page.goto(URL, timeout=120000)  # 2 minutos
```

### "403 Forbidden"

Seu IP pode estar bloqueado. Soluções:
- Aguarde algumas horas
- Use VPN
- Mude para versão com proxy

### Dados não chegam na API

1. Verifique `API_URL` no `.env.local`
2. Teste manualmente:
```bash
curl -X POST $API_URL \
  -H "Content-Type: application/json" \
  -d '{"data": []}'
```

## 📝 Logs

Os logs mostram o progresso:

```
🏠 INICIANDO COLETA LOCAL (SEM PROXY)
📊 [1/4] BETANO
🇧🇷 Iniciando coleta BETANO (conexão local)
✅ Página carregada com sucesso
✅ Encontrados 8 jogos na Betano
✅ Betano: 8 jogos coletados e enviados
```

## 🔄 Automação com Cron

Para rodar automaticamente no Linux/Mac:

```bash
# Edite o crontab
crontab -e

# Execute a cada 6 horas
0 */6 * * * cd /caminho/leite-bets && ./run_local_scraper.sh >> /var/log/scraper.log 2>&1
```

### Automação no Windows com Task Scheduler

```powershell
# Crie um script .bat
@echo off
cd C:\caminho\leite-bets
python scrapers\local\run_all_local.py >> logs\scraper.log 2>&1
```

## 📦 Estrutura de Arquivos

```
scrapers/local/
├── README.md                    # Este arquivo
├── __init__.py                  # Módulo Python
├── browser_no_proxy.py          # Browser sem proxy
├── betano_local.py              # Scraper Betano
├── superbet_local.py            # Scraper Superbet
├── esportesdasorte_local.py     # Scraper Esportes
├── bet365_local.py              # Scraper Bet365
└── run_all_local.py             # Executa todos
```

## 🔐 Segurança

- Nunca commite o `.env.local` com credenciais reais
- Use variáveis de ambiente para dados sensíveis
- Não exponha logs com informações sensíveis

## 📊 Monitoramento

Para monitorar a execução:

```bash
# Ver logs em tempo real
tail -f logs/scraper.log

# Contar execuções bem-sucedidas
grep "✅" logs/scraper.log | wc -l
```

## 🚀 Próximos Passos

1. Implementar parsers completos para Superbet e Bet365
2. Adicionar retry automático em caso de falha
3. Implementar cache local para evitar requisições duplicadas
4. Adicionar notificações quando houver erros
5. Criar dashboard local para visualizar status

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique os logs detalhados
2. Revise a configuração do `.env.local`
3. Teste cada scraper individualmente
4. Abra uma issue no repositório
