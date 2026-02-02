# 🔒 Sistema de Rotação de Proxies

## 📋 Visão Geral

Sistema implementado para **rotação automática e aleatória de proxies** em todos os scrapers, evitando banimentos e rate limiting das casas de apostas.

## 🎯 Funcionalidades

- ✅ Pool de 10 IPs estáticos da Webshare
- ✅ Rotação aleatória por execução
- ✅ Tracking de qual proxy cada scraper está usando
- ✅ Logs detalhados de uso de proxy
- ✅ Fallback automático caso não haja proxies configurados

## 🏗️ Arquitetura

```
┌─────────────────┐
│  .env           │
│  IP_1 a IP_10   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ProxyManager    │ ← Gerencia pool e rotação
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  browser.py     │ ← Configura proxy no Playwright
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Scrapers       │ ← Betano, Superbet, EsportesDaSorte
│  (collectors)   │
└─────────────────┘
```

## ⚙️ Configuração

### 1. Adicionar IPs no `.env`

```env
# Proxies Webshare (10 IPs estáticos)
IP_1=***
IP_2=***
IP_3=***
IP_4=***
IP_5=***
IP_6=***
IP_7=***
IP_8=***
IP_9=***
IP_10=***

# Se seus proxies precisam autenticação:
# PROXY_USERNAME=seu_usuario
# PROXY_PASSWORD=sua_senha
```

### 2. Configurar Porta/Autenticação (se necessário)

Edite [`scrapers/shared/proxy_manager.py`](scrapers/shared/proxy_manager.py):

```python
return {
    "server": f"http://{proxy_ip}:80",  # ← Ajustar porta
    # Descomentar se precisar autenticação:
    # "username": os.getenv("PROXY_USERNAME"),
    # "password": os.getenv("PROXY_PASSWORD")
}
```

## 🚀 Como Funciona

### Exemplo de Execução

**1º Momento:**
```
[BETANO] Usando proxy: ***
[SUPERBET] Usando proxy: ***
[ESPORTESDASORTE] Usando proxy: ***
```

**2º Momento (nova execução):**
```
[BETANO] Usando proxy:***
[SUPERBET] Usando proxy: ***
[ESPORTESDASORTE] Usando proxy: ***
```

**A rotação é aleatória e automática!** 🔄

### Fluxo de Dados

```python
# 1. Scraper é iniciado
collect()

# 2. Browser é criado com proxy
with sync_playwright() as p:
    browser, context = get_browser_context(p, scraper_name="betano")
    # ↑ Proxy aleatório é selecionado aqui

# 3. ProxyManager escolhe IP aleatório
proxy_ip = random.choice([IP_1, IP_2, ..., IP_10])

# 4. Playwright usa o proxy para todas as requisições
page.goto("https://betano.bet.br")  # ← Via proxy
```

## 📁 Arquivos Principais

| Arquivo | Função |
|---------|--------|
| [`scrapers/shared/proxy_manager.py`](scrapers/shared/proxy_manager.py) | Gerenciador central de proxies |
| [`scrapers/shared/browser.py`](scrapers/shared/browser.py) | Configuração de browser com proxy |
| [`scrapers/base/browser.py`](scrapers/base/browser.py) | Mesma função (duplicado) |
| [`scrapers/base/betano/collector.py`](scrapers/base/betano/collector.py) | Scraper usando proxy |
| [`scrapers/base/superbet/collector.py`](scrapers/base/superbet/collector.py) | Scraper usando proxy |
| [`scrapers/base/esportesdasorte/collector.py`](scrapers/base/esportesdasorte/collector.py) | Scraper usando proxy |

## 🔍 Verificar Proxies em Uso

### Via Logs

```bash
docker-compose logs scraper | grep "proxy"
```

Saída esperada:
```
✅ 10 proxies carregados: ***, ***, ***...
🔄 [BETANO] Usando proxy: ***
🔄 [SUPERBET] Usando proxy: ***
```

### Via Código

```python
from scrapers.shared.proxy_manager import proxy_manager

# Ver quantos proxies estão carregados
print(f"Proxies disponíveis: {proxy_manager.available_proxies_count}")

# Ver qual proxy um scraper está usando
proxy = proxy_manager.get_used_proxy("betano")
print(f"Betano está usando: {proxy}")

# Ver todos os proxies em uso
print(proxy_manager.used_proxies)
# {'betano': '***', 'superbet': '***'}
```

## 🧪 Testar Funcionamento

### Teste 1: Verificar se Proxies Estão Carregados

```python
from scrapers.shared.proxy_manager import proxy_manager

print(f"Proxies: {proxy_manager.proxies}")
print(f"Total: {proxy_manager.available_proxies_count}")
```

### Teste 2: Simular Rotação

```python
from scrapers.shared.proxy_manager import get_random_proxy

# Simular 5 execuções
for i in range(5):
    betano_proxy = get_random_proxy("betano")
    superbet_proxy = get_random_proxy("superbet")
    print(f"Execução {i+1}:")
    print(f"  Betano: {betano_proxy}")
    print(f"  Superbet: {superbet_proxy}")
    print()
```

### Teste 3: Rodar Scraper Completo

```bash
# Via Docker
docker-compose up scraper

# Ou localmente
python scrapers/workflows/run_betano.py
```

## ⚠️ Troubleshooting

### Problema: Nenhum proxy carregado

**Sintoma:**
```
⚠️  Nenhum proxy encontrado no .env - scrapers rodarão sem proxy
```

**Solução:**
1. Verificar se `.env` tem os IPs configurados
2. Verificar se está carregando o `.env` coreto (no Docker, adicionar ao docker-compose.yml)

### Problema: Proxies não funcionam

**Sintoma:** Timeout ou erro de conexão

**Soluções:**
1. **Verificar porta:** Ajustar em `proxy_manager.py` (linha ~66)
   ```python
   "server": f"http://{proxy_ip}:80"  # Trocar 80 pela porta correta
   ```

2. **Adicionar autenticação:** Se seus proxies precisam user/pass
   ```python
   "username": os.getenv("PROXY_USERNAME"),
   "password": os.getenv("PROXY_PASSWORD")
   ```

3. **Testar proxy manualmente:**
   ```bash
   curl -x http://***:80 https://api.ipify.org
   ```

### Problema: Sempre usa o mesmo proxy

**Causa:** Seed do random pode estar fixo

**Solução:** Já está implementado com `random.choice()` - cada execução deve ser diferente

## 📊 Estatísticas de Uso

Para adicionar métricas de uso dos proxies:

```python
# Em proxy_manager.py, adicionar:
class ProxyManager:
    def __init__(self):
        self.proxies = self._load_proxies()
        self.used_proxies = {}
        self.usage_stats = {}  # Novo
    
    def get_random_proxy(self, scraper_name: str = None):
        proxy_ip = random.choice(self.proxies)
        
        # Incrementar contador
        self.usage_stats[proxy_ip] = self.usage_stats.get(proxy_ip, 0) + 1
        
        return proxy_ip
    
    def get_stats(self):
        """Retorna estatísticas de uso"""
        return self.usage_stats
```

## 🔐 Segurança

### Boas Práticas

✅ **Não commitar** o `.env` com IPs reais  
✅ **Rotacionar** IPs regularmente (mensalmente)  
✅ **Monitorar** se algum IP está bloqueado  
✅ **Ter backup** de IPs extras caso algum falhe  

### Adicionar ao `.gitignore`

```gitignore
.env
.env.local
*.env.backup
```

## 🚀 Próximos Passos (Melhorias Futuras)

- [ ] Sistema de health check para testar proxies periodicamente
- [ ] Remover automaticamente proxies que falharem
- [ ] Load balancing inteligente (menos uso em proxies mais usados)
- [ ] Métricas de performance por proxy
- [ ] Rotação baseada em tempo (trocar proxy a cada X minutos)
- [ ] Suporte a diferentes tipos de proxy (SOCKS5, HTTPS)

## 📝 Changelog

**v1.0.0** - Sistema de Proxies
- ✨ Implementação inicial do ProxyManager
- ✨ Rotação aleatória de 10 IPs
- ✨ Integração com todos os scrapers
- ✨ Logs detalhados de uso
- ✨ Fallback automático sem proxies

---

💡 **Dica:** Configure mais IPs no `.env` (IP_11, IP_12, etc.) para aumentar o pool. O sistema detecta automaticamente!
