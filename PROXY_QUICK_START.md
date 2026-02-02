# 🚀 Guia Rápido - Proxies

## ✅ O que foi implementado?

Sistema de **rotação automática de proxies** para todos os scrapers usando 10 IPs estáticos da Webshare.

## 🎯 Como usar?

### 1. Configurar IPs no `.env`

```env
IP_1=***
IP_2=***
IP_3=1***
# ... até IP_10
```

### 2. Pronto! 🎉

Os scrapers **já estão configurados** para usar proxies automaticamente.

## 📊 Como funciona?

**Cada execução usa IPs diferentes aleatoriamente:**

```
1ª Execução:
  Betano → IP: ***
  Superbet → IP: ***
  
2ª Execução:
  Betano → IP: ***
  Superbet → IP: ***
```

## 🔍 Ver proxies em uso

```bash
docker-compose logs scraper | grep "proxy"
```

## ⚙️ Configuração Webshare

Se seus proxies precisam de **porta diferente** ou **autenticação**, edite:

[`scrapers/shared/proxy_manager.py`](scrapers/shared/proxy_manager.py) linha 66:

```python
return {
    "server": f"http://{proxy_ip}:80",  # ← Mudar porta aqui
    # Descomentar se precisar user/pass:
    # "username": os.getenv("PROXY_USERNAME"),
    # "password": os.getenv("PROXY_PASSWORD")
}
```

## 📁 Arquivos Criados

- [`scrapers/shared/proxy_manager.py`](scrapers/shared/proxy_manager.py) - Gerenciador de proxies
- [`PROXY_ROTATION.md`](PROXY_ROTATION.md) - Documentação completa

## 📁 Arquivos Modificados

- [`scrapers/shared/browser.py`](scrapers/shared/browser.py) - Suporte a proxy
- [`scrapers/base/browser.py`](scrapers/base/browser.py) - Suporte a proxy
- Collectors: Betano, Superbet, EsportesDaSorte

## ⚠️ Importante

- ✅ Proxies são opcionais (funciona sem eles)
- ✅ Rotação é 100% automática
- ✅ Logs mostram qual IP está sendo usado
- ✅ Sem config manual nos scrapers

---

**Ver documentação completa:** [PROXY_ROTATION.md](PROXY_ROTATION.md)
