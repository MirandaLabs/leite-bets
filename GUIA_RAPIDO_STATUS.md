# 🎯 Guia Rápido - Sistema de Status de Eventos

## 📝 O que foi implementado?

Sistema completo de gerenciamento de status para eventos esportivos com **3 estados**:

```
┌─────────────┐
│  UPCOMING   │ ← Antes do jogo começar
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    LIVE     │ ← Durante o jogo (2 horas)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  FINISHED   │ ← Jogo finalizado (odds desativadas)
└─────────────┘
```

## 🚀 Como Usar

### 1️⃣ Aplicar Migração no Banco

```bash
# PostgreSQL
psql -U usuario -d leite_bets -f backend/migration_event_status.sql

# Ou usar o script de atualização incremental
psql -U usuario -d leite_bets -f backend/update_schema.sql
```

### 2️⃣ Iniciar o Backend

```bash
cd backend
python main.py
```

### 3️⃣ Atualizar Status Automaticamente

**Opção A: Via API (recomendado para n8n/automação)**
```bash
curl -X POST http://localhost:8000/api/events/update-status
```

**Opção B: Script Standalone**
```bash
python backend/update_event_status.py
```

**Opção C: Cron Job (Linux/Mac)**
```bash
# Editar crontab
crontab -e

# Adicionar linha (executa a cada 15 minutos)
*/15 * * * * cd /caminho/projeto && python backend/update_event_status.py
```

**Opção D: Task Scheduler (Windows)**
- Abrir "Agendador de Tarefas"
- Criar tarefa básica
- Ação: `python C:\caminho\projeto\backend\update_event_status.py`
- Repetir: A cada 15 minutos

### 4️⃣ Limpar Eventos Antigos

```bash
# Remove eventos finalizados há mais de 7 dias
curl -X DELETE "http://localhost:8000/api/events/cleanup?days_old=7"
```

## 🔍 Verificar Funcionamento

### Ver Status dos Eventos
```sql
SELECT status, COUNT(*) as total
FROM events
GROUP BY status;
```

### Listar Eventos Ativos
```bash
curl http://localhost:8000/api/events
```

### Ver Último Evento Finalizado
```sql
SELECT home_team, away_team, finished_at
FROM events
WHERE status = 'finished'
ORDER BY finished_at DESC
LIMIT 1;
```

## 📋 Checklist de Implementação

- [ ] Executar migration SQL no banco
- [ ] Reiniciar backend
- [ ] Testar endpoint `/api/events/update-status`
- [ ] Configurar automação (cron/n8n)
- [ ] Verificar que eventos finished não aparecem na API
- [ ] Configurar limpeza semanal

## ⚡ Endpoints Novos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/events/update-status` | Atualiza status de todos eventos |
| `DELETE` | `/api/events/cleanup?days_old=7` | Remove eventos antigos |
| `GET` | `/api/events` | Lista eventos (só upcoming/live) |

## 🔧 Configurações

Ajustar duração do jogo em [`backend/main.py`](backend/main.py):

```python
# Linha ~311
MATCH_DURATION = 120  # minutos (padrão: 2 horas)
```

Ajustar dias para limpeza:

```bash
curl -X DELETE "http://localhost:8000/api/events/cleanup?days_old=14"
#                                                                 ↑
#                                                          alterar aqui
```

## 📊 Fluxo Completo

```
1. Scraper coleta odds
   ↓
2. Envia para /api/odds/scraper
   ↓
3. Backend cria evento com status="upcoming"
   ↓
4. Script/API verifica horário periodicamente
   ↓
5. Se passou horário → status="live"
   ↓
6. Se passou 2h do horário → status="finished"
   ↓
7. Odds marcadas como is_active=false
   ↓
8. GET /api/events não retorna mais o evento
   ↓
9. Após 7 dias → evento removido do banco
```

## ❓ Perguntas Frequentes

**Q: Os scrapers precisam ser modificados?**  
R: Não, os parsers já foram atualizados para usar `status="upcoming"`.

**Q: Preciso rodar atualização manualmente?**  
R: Não, configure automação via cron ou n8n.

**Q: Eventos são deletados imediatamente?**  
R: Não, são mantidos por 7 dias após finalizar (configurável).

**Q: Posso mudar o tempo de jogo?**  
R: Sim, altere `MATCH_DURATION` no backend/main.py.

## 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| Eventos não mudam status | Execute `python backend/update_event_status.py` |
| Odds ainda aparecem | Verifique se `is_active` está sendo filtrado |
| Erro no SQL | Use `backend/migration_event_status.sql` em vez de schema.sql |
| Timezone errado | Ajustar para seu fuso horário no código |

## 📚 Arquivos Importantes

| Arquivo | Descrição |
|---------|-----------|
| [`backend/main.py`](backend/main.py) | API com novos endpoints |
| [`backend/update_event_status.py`](backend/update_event_status.py) | Script standalone |
| [`backend/migration_event_status.sql`](backend/migration_event_status.sql) | Migração completa |
| [`backend/update_schema.sql`](backend/update_schema.sql) | Atualização incremental |
| [`scrapers/shared/status_checker.py`](scrapers/shared/status_checker.py) | Lógica de verificação |
| [`IMPLEMENTACAO_STATUS.md`](IMPLEMENTACAO_STATUS.md) | Documentação completa |

## ✅ Resultado Esperado

Antes:
```json
{
  "events": [
    {"eventId": "evt_jogo_finalizado", "status": "upcoming", ...},
    {"eventId": "evt_jogo_atual", "status": "upcoming", ...}
  ]
}
```

Depois:
```json
{
  "events": [
    {"eventId": "evt_jogo_atual", "status": "live", ...}
  ]
}
```
*(Evento finalizado não aparece mais)*

---

💡 **Dica**: Configure a atualização via n8n para rodar a cada 15 minutos!
