Documentação de Tentativas e Falhas: Rotação de Proxy Residencial Webshare x Cloudflare no Railway
📌 O Problema Principal (Root Cause)
O problema central da aplicação reside na incompatibilidade entre as restrições de segurança estritas da arquitetura de nuvem (Railway) e as políticas de autenticação e Anti-Fraude dos Proxies Residenciais da Webshare e do Cloudflare.

Em ambientes locais (teste no Python no terminal local), a conexão residencial da Webshare é validada imediatamente, quer usemos Sticky Sessions (sufixos) ou não. No entanto, quando as mesmas credenciais e lógica partem de um IP de Datacenter (AWS/Railway), ocorre um conflito em três frentes:

O WAF do Cloudflare: Bloqueia IPs de datacenter (falha original) e bloqueia "salada de IPs" simultâneos na mesma requisição.

O Gateway da Webshare: Rejeita a autenticação básica (HTTP 407) a partir da nuvem quando o formato do utilizador sofre alterações (sufixos dinâmicos) que não constam explicitamente na whitelist interna do painel residencial deles para aquela conta.

Timeouts de Rede (Blackholing): Quando o tráfego é barrado pelo gateway do proxy, em vez de um erro claro, a porta fica aberta mas não responde, causando Timeouts absurdos (90s a 120s) no Playwright, camuflando a causa real.

🛠️ Workarounds Tentados e Motivos de Falha
Abaixo está o histórico detalhado das nossas tentativas de contornar o bloqueio imposto pelo Cloudflare na Betano, Superbet e Esportes da Sorte:

Tentativa 1: Lista Estática de Proxies (Datacenter/ISP)
O que tentámos: Utilizar os proxies originais (plano Free ou ISP) da Webshare, iterando sequencialmente sobre uma lista baseada no sufixo (zecdovnb-1 a zecdovnb-20).

Por que falhou: Os IPs do Webshare estavam na "lista negra" do Cloudflare/Akamai da Betano e Superbet.

Sintoma: Bloqueio imediato (HTTP 403 Forbidden na Betano e "Página em branco/HTML muito pequeno" de 1378 bytes na Superbet).

Tentativa 2: Implementação do pacote playwright-stealth
O que tentámos: Injetar o playwright-stealth na página do Playwright para mascarar as assinaturas do navegador headless (ex: ocultar a propriedade webdriver = true) e passar pelo WAF.

Por que falhou: Embora o stealth evite a deteção no lado do cliente (Javascript), a conexão WAF ocorre a nível de rede (TCP/IP). Como o IP ainda era de Datacenter, a proteção atuou antes mesmo do navegador renderizar a página.

Conclusão desta fase: Migrar obrigatoriamente para Proxies Residenciais Rotativos.

Tentativa 3: Rotação Residencial com Sorteio de Número Elevado (random.randint)
O que tentámos: No plano Residencial, assumimos que tínhamos acesso a milhares de Sticky Sessions. Atualizámos o ProxyManager para sortear um sufixo elevado (ex: zecdovnb-37717) de 1 a 100.000 para forçar IPs sempre novos.

Por que falhou: A Webshare parece limitar (ou ignorar) números de sessão muito elevados para contas base, ou o roteamento a partir da nuvem considerou o utilizador inválido.

Sintoma: O proxy rejeitou a ligação, resultando em HTTP 407 (Proxy Authentication Required) na Betano e Timeouts esgotados na Superbet/Esportes.

Tentativa 4: O "Country Targeting" Embutido (-BR-)
O que tentámos: Para garantir apenas IPs brasileiros, formatámos o utilizador como zecdovnb-BR-14824, que é um padrão comum de filtragem geográfica em várias provedoras.

Por que falhou: Na Webshare, o Country Targeting (filtro específico por string na URL) costuma requerer um Add-on pago. Como a conta não o tinha ativado para chamadas dinâmicas, a credencial tornou-se inválida.

Sintoma: Novamente, HTTP 407 e bloqueios de rede.

Tentativa 5: O Endpoint Oficial Rotativo (-rotate)
O que tentámos: Remover a lógica de sessão no código Python e usar o método da própria provedora, adicionando o sufixo -rotate ao utilizador para que a Webshare trocasse o IP automaticamente (delegação completa).

Por que falhou (O Perigo Mortal): O -rotate altera o IP a cada requisição. Como o Playwright abre dezenas de conexões simultâneas para carregar uma única página (HTML, CSS, imagens, JS), a Webshare entregou IPs de diferentes residências para a mesma visita. O Cloudflare interpretou isso como um ataque distribuído (botnet) e engoliu o tráfego ("Blackhole").

Sintoma: Timeouts catastróficos (60s, 90s, 120s) na navegação do Playwright (Page.goto: Timeout).

Tentativa 6: Voltar à "Sticky Session" com Sorteio Limitado (Limite de 1000 e 100)
O que tentámos: Após o utilizador confirmar no terminal local que o sufixo 1000 funcionava (zecdovnb-1000), reduzimos drasticamente o teto do randint para sortear números seguros (até 1000, e depois até 100), usando apenas a formatação mais pura de utilizador: zecdovnb-667.

Por que falhou: Apesar da prova matemática de que o código funciona no ambiente local, o ambiente Railway continuou a receber bloqueios. A arquitetura da conta Webshare em vigor não autorizou o uso das Sticky Sessions (sufixos dinâmicos) vindas do IP Cloud do Railway, exigindo a autenticação estrita no Backbone.

Sintoma: Persistência inquebrável do Erro 407 e do Timeout 120000ms.

Tentativa 7: Endpoint "Root" Base sem Sufixos
O que tentámos: Enviar o utilizador puro (zecdovnb) sem nenhum sufixo para o host p.webshare.io, utilizando a Autenticação Básica (HTTP Basic Auth).

Por que falhou: Contas residenciais rotativas recentes da Webshare não permitem, frequentemente, a ligação no endpoint root sem declaração de estado (sufixo) quando originadas de Datacenters, resultando em falha de autenticação.

Sintoma: Erro 407.

🏁 Conclusão Final
A aplicação encontra-se atualmente num impasse onde a infraestrutura (Código e Railway) executa as instruções corretamente, mas a ponte de ligação com o provedor de rede (Webshare) atua como um muro intransponível.

Para resolver o Problema Principal, o sistema de scraping precisará de uma destas abordagens:

Migração de Provedor de Proxy: Testar uma provedora de Proxies Residenciais diferente (como ScraperAPI, BrightData ou Oxylabs), que possua APIs nativas ou WAF Bypasses desenhados especificamente para a nuvem.

Validação de Plano: Contactar o suporte da Webshare para autorizar expressamente os Egress IPs do Railway e ativar as "Sessões Fixas" para a conta.
