# Workflows n8n - Scrapers Locais

Este diretório contém workflows do n8n para automação dos scrapers locais.

## 📋 Workflows Disponíveis

### 1. Scraper Local Automation.json
**Tipo:** Automático (Cron)  
**Execução:** A cada 2 horas entre 10h e 21h  
**Descrição:** Workflow automatizado que executa os scrapers locais periodicamente

**Recursos:**
- ⏰ Cron: `0 10-21/2 * * *` (2h, 4h, 6h, 8h até 21h)
- 🤖 Executa `run_all_local.py` automaticamente
- 📊 Processa resultados e formata mensagem
- ✅ Distingue entre sucesso, aviso e erro
- 📝 Gera relatório detalhado

**Como usar:**
1. Importe o workflow no n8n local
2. Ative o workflow
3. Aguarde a próxima execução agendada
4. Monitore os logs

### 2. Scraper Local Manual.json
**Tipo:** Manual  
**Execução:** Sob demanda (clique para executar)  
**Descrição:** Workflow para testes manuais dos scrapers

**Recursos:**
- 🖱️ Execução manual via botão
- 🔍 Ideal para testes e debug
- 📊 Exibe resultados detalhados
- 🚀 Resposta rápida

**Como usar:**
1. Importe o workflow no n8n local
2. Abra o workflow
3. Clique em "Execute Workflow"
4. Visualize os resultados

### 3. Scraper Automation - Leite Bets.json
**Tipo:** Produção (Railway)  
**Execução:** A cada 2 horas entre 10h e 21h  
**Descrição:** Workflow original que chama a API remota no Railway

**Recursos:**
- 🌐 Chama API remota (com proxy)
- ☁️ Roda na nuvem
- 📡 Usa proxy residencial
- 🔄 Produção

## 🔧 Configuração do n8n Local

### 1. Acesse o n8n local
```bash
# O n8n local está rodando em:
http://localhost:5679
```

### 2. Importe os workflows

1. Acesse: http://localhost:5679
2. Menu lateral → **Workflows**
3. Clique em **Import from File**
4. Selecione o arquivo JSON desejado:
   - `Scraper Local Automation.json` (automático)
   - `Scraper Local Manual.json` (manual)

### 3. Configure o comando Python

Se necessário, ajuste o caminho do Python no node **Run Local Scrapers**:

```json
{
  "command": "python scrapers/local/run_all_local.py"
}
```

No Windows, pode precisar de:
```json
{
  "command": "python.exe scrapers\\local\\run_all_local.py"
}
```

## ⏰ Expressões Cron

| Expressão | Descrição |
|-----------|-----------|
| `0 10-21/2 * * *` | A cada 2 horas entre 10h-21h |
| `0 */4 * * *` | A cada 4 horas |
| `0 8-20/3 * * *` | A cada 3 horas entre 8h-20h |
| `0 10,14,18,22 * * *` | Às 10h, 14h, 18h e 22h |
| `0 12 * * *` | Todo dia ao meio-dia |

### Modificar o horário:

1. Abra o workflow no n8n
2. Clique no node **Schedule Trigger Local**
3. Em **Cron Expression**, altere:
   ```
   0 10-21/2 * * *
   ```
4. Salve o workflow

## 🔍 Debug e Logs

### Visualizar logs do workflow:

1. No n8n, vá em **Executions**
2. Clique na execução desejada
3. Visualize cada node e seus dados

### Logs do Python:

Os logs do script Python aparecem no node **Run Local Scrapers** → **Output Data** → `stdout`

Exemplo de saída:
```
🏠 INICIANDO COLETA LOCAL (SEM PROXY)
================================================================================
📊 [1/4] BETANO
✅ Betano: 8 jogos coletados e enviados
📊 [2/4] SUPERBET
⚠️ Superbet: Sem dados
...
```

## 📊 Estrutura dos Dados

### Output do Process Results:

```json
{
  "timestamp": "11/02/2026, 14:30:00",
  "exitCode": 0,
  "totalJogos": 13,
  "casas": [
    {
      "nome": "Betano",
      "jogos": 8,
      "status": "✅"
    },
    {
      "nome": "Esportes da Sorte",
      "jogos": 5,
      "status": "✅"
    },
    {
      "nome": "Superbet",
      "jogos": 0,
      "status": "⚠️"
    }
  ],
  "success": true,
  "stdout": "...logs completos...",
  "stderr": ""
}
```

## 🚨 Troubleshooting

### ❌ "Command not found: python"

**Solução:** Ajuste o comando para:
- Windows: `python.exe` ou `py`
- Linux/Mac: `python3`

### ❌ "Cannot find module 'scrapers'"

**Solução:** Verifique o working directory no node:
```json
{
  "options": {
    "cwd": "/app"
  }
}
```

Ou use o caminho absoluto do projeto.

### ❌ "API_URL não configurada"

**Solução:** Configure `API_URL` no `.env.local`:
```env
API_URL=https://seu-projeto.up.railway.app/api/odds/scraper
```

### ⚠️ Workflow não executa no horário

**Verificações:**
1. Workflow está ativo? (toggle no canto superior direito)
2. Timezone do n8n está correto?
3. Container n8n está rodando?

```bash
# Verifique containers
docker ps | grep n8n

# Veja logs do n8n
docker logs leite-bets-local-n8n
```

## 🔄 Integração com Telegram (Opcional)

Para receber notificações no Telegram, adicione um node **Telegram** após o **Format Message**:

1. No workflow, clique em **+** após Format Message
2. Adicione node **Telegram**
3. Configure:
   - **Chat ID**: Seu ID do Telegram
   - **Token**: Token do bot
   - **Text**: `{{ $json.mensagemFormatada }}`

## 📈 Monitoramento

### Ver histórico de execuções:

```bash
# Acesse o n8n
http://localhost:5679

# Menu: Executions
# Filtre por:
# - Workflow: Scraper Local Automation
# - Status: Success / Error / Warning
```

### Estatísticas úteis:

- **Taxa de sucesso**: Quantas execuções tiveram `totalJogos > 0`
- **Média de jogos**: Soma de `totalJogos` / número de execuções
- **Tempo de execução**: Duração média de cada workflow

## 🎯 Próximos Passos

1. ✅ Importe os workflows no n8n local
2. ✅ Teste a versão manual primeiro
3. ✅ Ative a versão automática
4. ✅ Configure notificações (Telegram/Email)
5. ✅ Monitore as primeiras execuções
6. ✅ Ajuste o cron se necessário

## 💡 Dicas

1. **Teste sempre a versão manual** antes de ativar o automático
2. **Configure alertas** para quando `totalJogos = 0`
3. **Monitore o stderr** para detectar erros Python
4. **Ajuste o timeout** se os scrapers demorarem muito
5. **Use tags** para organizar workflows (local, prod, test)

## 📚 Documentação

- [n8n Documentation](https://docs.n8n.io/)
- [Cron Expression Generator](https://crontab.guru/)
- [Scrapers Locais](../scrapers/local/README.md)
