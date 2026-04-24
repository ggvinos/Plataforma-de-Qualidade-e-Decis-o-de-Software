"""
================================================================================
📦 NinaDash Módulos - Arquitetura Modular
================================================================================

Estrutura de módulos organizada por responsabilidade:

CONFIGURAÇÃO:
    config.py           - Constantes, configurações visuais, campos Jira

AUTENTICAÇÃO:
    auth.py            - Sistema de autenticação legado (cookies)
    confirmation_call_auth.py - Autenticação JWT via ConfirmationCall API

INTEGRAÇÃO:
    jira_api.py        - Cliente API do Jira, cache, busca de dados

LÓGICA DE NEGÓCIO:
    calculos.py        - Métricas: Fator K, DDP, FPY, Lead Time, Health Score
    processamento.py   - Filtros, processamento de DataFrames

INTERFACE:
    abas.py            - Componentes das abas do dashboard
    cards.py           - Visualização detalhada de tickets
    widgets.py         - Componentes visuais reutilizáveis
    graficos.py        - Gráficos Plotly (funil, tendências, heatmaps)

FUNCIONALIDADES:
    consultas.py       - Sistema de consultas personalizadas

UTILITÁRIOS:
    utils.py           - Funções auxiliares gerais
    helpers.py         - Helpers para cálculos e formatação
    changelog.py       - Histórico de versões

================================================================================
"""

__version__ = "8.82"
__author__ = "Nina Tecnologia"
