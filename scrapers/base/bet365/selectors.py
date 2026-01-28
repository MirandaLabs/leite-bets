# scrapers/base/bet365/selectors.py

"""
Seletores CSS para scraping visual da Bet365.
IMPORTANTE: As classes da Bet365 são ofuscadas e mudam frequentemente.
Mantenha este arquivo atualizado.
"""

# Seletor genérico para encontrar a lista de jogos na home/liga
MATCH_GRID_ITEM = "div.rcl-ParticipantFixtureDetails"

# Dentro da página do jogo
MARKET_GROUP_BUTTON = "div.gl-MarketGroupButton_Text"
MARKET_CONTAINER = "div.gl-MarketGroup"

# Estrutura interna das odds (dentro do MarketGroup)
# Isso varia por mercado, mas para Dupla Hipótese/Resultado Final costuma ser padrão
PARTICIPANT_GENERAL = "div.gl-Participant_General"
PARTICIPANT_NAME = "span.gl-Participant_Name"
PARTICIPANT_ODDS = "span.gl-Participant_Odds"

# Abas (caso precise navegar entre 'Populares', 'Criar Aposta', etc)
TAB_BAR = "div.sph-MarketGroupNavBar"
TAB_ITEM = "div.sph-MarketGroupNavBarButton"