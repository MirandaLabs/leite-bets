# Sistema de Status de Eventos - Implementação Completa

## 📋 Resumo das Mudanças

Implementado sistema de gerenciamento de status de eventos com 3 estados:
- **upcoming**: Evento agendado para o futuro
- **live**: Evento em andamento
- **finished**: Evento finalizado

## 🎯 Objetivos Alcançados

✅ Criação de enum `EventStatus` no modelo de dados  
✅ Atualização do schema do banco de dados  
✅ Atualização de todos os parsers dos scrapers  
✅ Lógica automática de verificação de horários  
✅ Filtros no backend para eventos finalizados  
✅ Sistema de limpeza de dados antigos  

## 🔄 Arquivos Modificados

### 1. **Modelos de Dados**

#### [`scrapers/shared/models/odds.py`](scrapers/shared/models/odds.py)
```python
from enum import Enum

class EventStatus(str, Enum):
    UPCOMING = "upcoming"
    LIVE = "live"
    FINISHED = "finished"

class Event(BaseModel):
    id: str
    name: str
    start_time: Optional[datetime]
    status: EventStatus = EventStatus.UPCOMING  # ← MUDANÇA
```

### 2. **Schema do Banco de Dados**

#### [`backend/schema.sql`](backend/schema.sql)
- Adicionado enum `event_status`
- Campo `finished_at` na tabela `events`
- Campo `is_active` na tabela `odds`

#### [`backend/models.py`](backend/models.py)
- Atualizado modelo `Event` com campo `finished_at`
- Atualizado modelo `Odd` com campo `is_active`

### 3. **Parsers dos Scrapers**

Atualizados para usar o novo sistema:
- [`scrapers/base/superbet/parser.py`](scrapers/base/superbet/parser.py)
- [`scrapers/base/betano/parser.py`](scrapers/base/betano/parser.py)
- [`scrapers/base/esportesdasorte/parser.py`](scrapers/base/esportesdasorte/parser.py)

### 4. **Backend API**

#### [`backend/main.py`](backend/main.py)

**Novos endpoints:**

- `POST /api/events/update-status` - Atualiza status de todos os eventos
- `DELETE /api/events/cleanup?days_old=7` - Remove eventos antigos

**Alterações:**

- `GET /api/events` - Agora filtra apenas eventos `upcoming` e `live`
- Sistema de arbitragem filtra apenas odds ativas

## 📁 Novos Arquivos Criados

### [`scrapers/shared/status_checker.py`](scrapers/shared/status_checker.py)
Módulo auxiliar para determinar status baseado no horário:

```python
def get_event_status(event_start_time: datetime) -> EventStatus:
    """Determina: upcoming, live ou finished"""
    
def should_keep_event(event_start_time: datetime) -> bool:
    """Verifica se evento deve ser mantido"""
```

### [`backend/update_event_status.py`](backend/update_event_status.py)
Script standalone para atualizar status (pode ser executado via cron):

```bash
python backend/update_event_status.py
```

### [`backend/migration_event_status.sql`](backend/migration_event_status.sql)
Script de migração para atualizar banco existente.

## 🚀 Como Aplicar as Mudanças

### 1. Atualizar o Banco de Dados

```bash
# Execute o script de migração
psql -U seu_usuario -d seu_banco -f backend/migration_event_status.sql
```

Ou via Python:
```python
from models import engine
with open('backend/migration_event_status.sql') as f:
    engine.execute(f.read())
```

### 2. Instalar Dependências (se necessário)

```bash
pip install -r backend/requirements.txt
```

### 3. Reiniciar o Backend

```bash
cd backend
python main.py
```

## ⚙️ Configuração Automática

### Atualização Periódica via Cron

Adicione ao crontab para executar a cada 15 minutos:

```bash
*/15 * * * * cd /caminho/do/projeto && python backend/update_event_status.py
```

### Limpeza Semanal

Execute aos domingos à 3h da manhã:

```bash
0 3 * * 0 cd /caminho/do/projeto && python backend/update_event_status.py
```

### Via API (n8n, Airflow, etc.)

```bash
# Atualizar status
curl -X POST http://localhost:8000/api/events/update-status

# Limpar eventos antigos (mais de 7 dias)
curl -X DELETE "http://localhost:8000/api/events/cleanup?days_old=7"
```

## 🎮 Como Funciona

### 1. Determinação de Status

```
Horário do Jogo: 15:00

Agora < 15:00     → status = "upcoming"
15:00 ≤ Agora < 17:00 → status = "live" (2h de duração)
Agora ≥ 17:00     → status = "finished"
```

### 2. Fluxo de Dados

```
Scraper coleta odds
    ↓
status = "upcoming" (padrão)
    ↓
Evento salvo no banco
    ↓
Script/API verifica horário
    ↓
Atualiza status (upcoming → live → finished)
    ↓
Se finished: desativa odds (is_active = false)
    ↓
Backend filtra apenas eventos ativos
    ↓
Após 7 dias: remove evento do banco
```

### 3. Filtros Aplicados

**No Backend (`/api/events`):**
```python
events = db.query(Event).filter(
    Event.status.in_(["upcoming", "live"])
).all()
```

**No Sistema de Arbitragem:**
```python
event = db.query(Event).filter(
    Event.id == event_id,
    Event.status.in_(["upcoming", "live"])
).first()

odds = db.query(Odd).filter(
    Odd.event_id == event_id,
    Odd.is_active == True
).all()
```

## 📊 Monitoramento

### Ver Status dos Eventos

```sql
SELECT 
    status,
    COUNT(*) as total
FROM events
GROUP BY status;
```

### Ver Odds Ativas/Inativas

```sql
SELECT 
    is_active,
    COUNT(*) as total
FROM odds
GROUP BY is_active;
```

### Eventos Finalizados Hoje

```sql
SELECT 
    home_team, 
    away_team, 
    finished_at
FROM events
WHERE status = 'finished'
  AND finished_at >= CURRENT_DATE
ORDER BY finished_at DESC;
```

## ⚠️ Considerações Importantes

1. **Duração do Jogo**: Configurada como 120 minutos (pode ser ajustada)
2. **Timezone**: Sistema usa UTC - ajustar se necessário
3. **Odds Inativas**: Não são deletadas, apenas marcadas como `is_active=false`
4. **Limpeza**: Eventos finished são mantidos por 7 dias (configurável)

## 🧪 Testes

### Testar Manualmente

```bash
# 1. Criar evento de teste com horário passado
# 2. Executar atualização
python backend/update_event_status.py

# 3. Verificar mudança de status
# 4. Confirmar que odds foram desativadas
```

### Via API

```bash
# Criar evento
curl -X POST http://localhost:8000/api/odds/scraper \
  -H "Content-Type: application/json" \
  -d '{"data": [...]}'

# Atualizar status
curl -X POST http://localhost:8000/api/events/update-status

# Verificar eventos
curl http://localhost:8000/api/events
```

## 🐛 Troubleshooting

### Problema: Eventos não estão mudando de status

**Solução:** Executar manualmente o script de atualização:
```bash
python backend/update_event_status.py
```

### Problema: Odds ainda aparecem após finalizar

**Solução:** Verificar se `is_active` está sendo respeitado:
```python
odds = db.query(Odd).filter(Odd.is_active == True).all()
```

### Problema: Eventos antigos não são removidos

**Solução:** Executar limpeza manual:
```bash
curl -X DELETE "http://localhost:8000/api/events/cleanup?days_old=7"
```

## 📈 Próximos Passos (Opcional)

- [ ] Adicionar notificação quando evento finalizar
- [ ] Dashboard para visualizar status em tempo real
- [ ] Logs de mudanças de status
- [ ] Integração com API de resultados reais
- [ ] Sistema de validação de resultados

## 📝 Changelog

**v2.0.0** - Sistema de Status Completo
- ✨ Enum de 3 estados (upcoming, live, finished)
- ✨ Verificação automática de horários
- ✨ Desativação de odds finalizadas
- ✨ Limpeza automática de dados antigos
- ✨ Endpoints para gerenciamento
- ✨ Script standalone para cron jobs
