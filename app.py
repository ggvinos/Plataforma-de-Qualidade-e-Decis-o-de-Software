"""
================================================================================
JIRA DASHBOARD v5.0 - MÉTRICAS ISTQB/CTFL PARA TOMADA DE DECISÃO
================================================================================
- Totalmente em português brasileiro
- Tooltips explicativos em todas as métricas
- Aba de Liderança expandida para decisões estratégicas
- Compartilhamento via link externo
- Textos em terceira pessoa

CAMPOS MAPEADOS DO JIRA NINA:
- customfield_10487: QA (user)
- customfield_11157: Bugs Encontrados
- customfield_10016: Story Points
- customfield_10020: Sprint
- customfield_11358: Janela de Testes
- customfield_11357: Dias até a Release
- customfield_11290: Complexidade de Teste
================================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import requests
from typing import Optional, Dict, List, Any, Tuple
import json
import os
import urllib.parse

# Carregar .env se existir
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ==============================================================================
# TOOLTIPS E EXPLICAÇÕES DAS MÉTRICAS
# ==============================================================================

TOOLTIPS = {
    "fator_k": {
        "titulo": "Fator K (Maturidade)",
        "descricao": "Razão entre Story Points entregues e bugs encontrados. Quanto maior, melhor a qualidade do código.",
        "formula": "FK = SP / (Bugs + 1)",
        "interpretacao": {
            "🥇 Gold (≥3.0)": "Excelente qualidade, código maduro",
            "🥈 Silver (2.0-2.9)": "Boa qualidade, dentro do esperado",
            "🥉 Bronze (1.0-1.9)": "Regular, precisa de atenção",
            "⚠️ Risco (<1.0)": "Crítico, requer intervenção imediata"
        },
        "fonte": "Métrica interna NINA baseada em práticas ISTQB"
    },
    "ddp": {
        "titulo": "DDP - Defect Detection Percentage",
        "descricao": "Percentual de defeitos encontrados pelo QA antes da produção. Mede a eficácia do time de testes.",
        "formula": "DDP = (Bugs em QA / Total de Bugs) × 100",
        "interpretacao": {
            "≥85%": "Excelente - QA muito eficaz",
            "70-84%": "Bom - Processo funcionando",
            "50-69%": "Regular - Precisa melhorar",
            "<50%": "Crítico - Muitos bugs escapando"
        },
        "fonte": "ISTQB Foundation Level - Test Metrics"
    },
    "fpy": {
        "titulo": "FPY - First Pass Yield",
        "descricao": "Percentual de cards aprovados na primeira validação, sem bugs. Indica qualidade do desenvolvimento.",
        "formula": "FPY = (Cards sem bugs / Total de cards) × 100",
        "interpretacao": {
            "≥80%": "Excelente - Código de alta qualidade",
            "60-79%": "Bom - Dentro do esperado",
            "40-59%": "Regular - Revisar práticas",
            "<40%": "Crítico - Alto retrabalho"
        },
        "fonte": "Six Sigma / Lean Manufacturing adaptado para software"
    },
    "mttr": {
        "titulo": "MTTR - Mean Time To Repair",
        "descricao": "Tempo médio para corrigir um bug após identificado. Quanto menor, mais ágil o time.",
        "formula": "MTTR = Σ(Tempo de correção) / Nº de bugs",
        "interpretacao": {
            "≤1 dia": "Excelente resposta",
            "2-3 dias": "Tempo aceitável",
            "4-7 dias": "Precisa melhorar",
            ">7 dias": "Gargalo crítico"
        },
        "fonte": "ITIL / DevOps Metrics"
    },
    "lead_time": {
        "titulo": "Lead Time",
        "descricao": "Tempo total desde a criação do card até sua conclusão. Inclui desenvolvimento, code review e QA.",
        "formula": "Lead Time = Data Conclusão - Data Criação",
        "interpretacao": {
            "≤5 dias": "Fluxo muito ágil",
            "6-10 dias": "Tempo saudável",
            "11-15 dias": "Atenção ao processo",
            ">15 dias": "Investigar gargalos"
        },
        "fonte": "Kanban / Lean Metrics"
    },
    "health_score": {
        "titulo": "Health Score (Saúde da Release)",
        "descricao": "Pontuação composta que avalia a saúde geral da release considerando múltiplos fatores.",
        "formula": "HS = (Conclusão×30 + DDP×25 + FPY×20 + Gargalos×15 + LeadTime×10) / 100",
        "interpretacao": {
            "≥75": "🟢 Saudável - Release pode seguir",
            "50-74": "🟡 Atenção - Monitorar riscos",
            "25-49": "🟠 Alerta - Ação necessária",
            "<25": "🔴 Crítico - Avaliar adiamento"
        },
        "fonte": "Composite Score baseado em ISTQB Test Process Improvement"
    },
    "defect_density": {
        "titulo": "Densidade de Defeitos",
        "descricao": "Quantidade de bugs por Story Point. Indica a taxa de defeitos relativa ao tamanho.",
        "formula": "DD = Total de Bugs / Total de SP",
        "interpretacao": {
            "≤0.2": "Baixa densidade - Excelente",
            "0.21-0.5": "Densidade aceitável",
            "0.51-1.0": "Densidade alta - Atenção",
            ">1.0": "Crítico - Muitos bugs/SP"
        },
        "fonte": "IEEE 982.1 - Software Quality Metrics"
    },
    "throughput": {
        "titulo": "Throughput (Vazão)",
        "descricao": "Quantidade de cards/SP concluídos por período. Indica a capacidade de entrega do time.",
        "formula": "Throughput = Cards concluídos / Período",
        "interpretacao": {
            "Crescente": "Time ganhando velocidade",
            "Estável": "Capacidade previsível",
            "Decrescente": "Investigar impedimentos"
        },
        "fonte": "Kanban Metrics / Flow Efficiency"
    },
    "wip": {
        "titulo": "WIP - Work In Progress",
        "descricao": "Quantidade de cards em andamento simultaneamente. WIP alto pode indicar gargalos.",
        "formula": "WIP = Cards não concluídos e não no backlog",
        "interpretacao": {
            "≤ Capacidade": "Fluxo saudável",
            "> Capacidade": "Sobrecarga - Risco de atrasos"
        },
        "fonte": "Kanban / Little's Law"
    }
}

# ==============================================================================
# CONFIGURAÇÕES
# ==============================================================================

# ==============================================================================
# CREDENCIAIS SEGURAS (via st.secrets ou variáveis de ambiente)
# ==============================================================================
# Para desenvolvimento local: .streamlit/secrets.toml
# Para Streamlit Cloud: App Settings > Secrets
# ==============================================================================

def get_secrets():
    """Carrega credenciais de forma segura."""
    try:
        # Primeiro tenta st.secrets (Streamlit Cloud e .streamlit/secrets.toml)
        if "jira" in st.secrets:
            return {
                "base_url": st.secrets["jira"]["base_url"],
                "email": st.secrets["jira"]["email"],
                "token": st.secrets["jira"]["token"],
                "emails_autorizados": st.secrets["auth"]["emails_autorizados"].split(",")
            }
        else:
            raise KeyError("Secrets não encontrados")
    except Exception as e:
        # Fallback para variáveis de ambiente
        email = os.getenv("JIRA_API_EMAIL", "")
        token = os.getenv("JIRA_API_TOKEN", "")
        
        # Se nem secrets nem env vars estão configurados, mostrar aviso
        if not email or not token:
            st.error("""
            ⚠️ **Credenciais não configuradas!**
            
            Configure os Secrets no Streamlit Cloud:
            1. Vá em Settings > Secrets
            2. Cole:
            ```
            [jira]
            base_url = "https://ninatecnologia.atlassian.net"
            email = "seu-email@empresa.com"
            token = "seu-token-jira"
            
            [auth]
            emails_autorizados = "email1@empresa.com"
            ```
            """)
        
        return {
            "base_url": os.getenv("JIRA_BASE_URL", "https://ninatecnologia.atlassian.net"),
            "email": email,
            "token": token,
            "emails_autorizados": os.getenv("EMAILS_AUTORIZADOS", "").split(",")
        }

# Carregar credenciais
_secrets = get_secrets()
JIRA_BASE_URL = _secrets["base_url"]
JIRA_API_EMAIL = _secrets["email"]
JIRA_API_TOKEN = _secrets["token"]
EMAILS_AUTORIZADOS = [e.strip() for e in _secrets["emails_autorizados"] if e.strip()]

PROJETOS = {
    "SD": {"nome": "Desenvolvimento", "principal": True},
    "QA": {"nome": "QA", "principal": False},
    "PB": {"nome": "Backlog de Produto", "principal": False},
    "VALPROD": {"nome": "Validação em Produção", "principal": False},
}

CUSTOM_FIELDS = {
    "story_points": "customfield_11257",  # Campo correto de Story Points
    "story_points_alt": "customfield_10016",  # Campo alternativo
    "sprint": "customfield_10020",
    "bugs_encontrados": "customfield_11157",
    "dias_ate_release": "customfield_11357",
    "janela_testes": "customfield_11358",
    "complexidade_teste": "customfield_11290",
    "qa_responsavel": "customfield_10487",
    "qa_array": "customfield_10784",
    "desenvolvedor": "customfield_10455",
    "desenvolvedor_array": "customfield_10785",
}

STATUS_FLOW = {
    "backlog": ["Backlog", "To Do"],
    "development": ["Em andamento"],
    "code_review": ["EM REVISÃO"],
    "waiting_qa": ["AGUARDANDO VALIDAÇÃO", "Tarefas pendentes"],
    "testing": ["EM VALIDAÇÃO"],
    "done": ["Concluído"],
    "blocked": ["IMPEDIDO", "REPROVADO"],
    "deferred": ["Validado - Adiado", "DESCARTADO"],
}

MATURIDADE = {
    "Gold": {"min_fk": 3.0, "cor": "#22c55e", "emoji": "🥇", "desc": "Excelente"},
    "Silver": {"min_fk": 2.0, "cor": "#eab308", "emoji": "🥈", "desc": "Bom"},
    "Bronze": {"min_fk": 1.0, "cor": "#f97316", "emoji": "🥉", "desc": "Regular"},
    "Risco": {"min_fk": 0.01, "cor": "#ef4444", "emoji": "⚠️", "desc": "Atenção"},
    "Sem SP": {"min_fk": -1, "cor": "#9ca3af", "emoji": "📊", "desc": "Sem dados de SP"},
}

# Nomes traduzidos para status
STATUS_NOMES = {
    "backlog": "Backlog",
    "development": "Desenvolvimento",
    "code_review": "Revisão de Código",
    "waiting_qa": "Aguardando QA",
    "testing": "Em Validação",
    "done": "Concluído",
    "blocked": "Bloqueado",
    "deferred": "Adiado",
    "unknown": "Desconhecido"
}

# ==============================================================================
# UTILIDADES
# ==============================================================================

def link_jira(ticket_id: str) -> str:
    return f"{JIRA_BASE_URL}/browse/{ticket_id}"


def link_html(ticket_id: str, texto: str = None) -> str:
    url = link_jira(ticket_id)
    display = texto or ticket_id
    return f'<a href="{url}" target="_blank" style="color: #6366f1; text-decoration: none; font-weight: 600;">🔗 {display}</a>'


def formatar_duracao(dias: float) -> str:
    if dias < 1:
        return f"{int(dias * 24)}h"
    elif dias < 7:
        return f"{dias:.1f} dias"
    else:
        return f"{dias/7:.1f} semanas"


def calcular_dias_uteis(data_inicio: datetime, data_fim: datetime) -> int:
    """
    Calcula o número de dias úteis restantes até a data fim.
    Não inclui o dia atual, apenas os dias futuros.
    Exclui sábados e domingos.
    """
    # Usar apenas a parte da data (sem horário)
    inicio = data_inicio.date() if hasattr(data_inicio, 'date') else data_inicio
    fim = data_fim.date() if hasattr(data_fim, 'date') else data_fim
    
    if fim <= inicio:
        return 0
    
    dias_uteis = 0
    # Começar do dia seguinte (não conta hoje)
    data_atual = inicio + timedelta(days=1)
    
    while data_atual <= fim:
        # 0 = segunda, 6 = domingo
        if data_atual.weekday() < 5:  # Segunda a Sexta
            dias_uteis += 1
        data_atual += timedelta(days=1)
    
    return dias_uteis


def mostrar_tooltip(metrica_key: str, inline: bool = False):
    """
    Mostra ícone de info com tooltip explicativo para a métrica.
    Usa help nativo do Streamlit para tooltip hover (não precisa clicar).
    """
    if metrica_key not in TOOLTIPS:
        return
    
    t = TOOLTIPS[metrica_key]
    
    # Monta texto do tooltip de forma compacta
    texto = f"**{t['titulo']}**\n\n{t['descricao']}\n\n"
    texto += f"📐 Fórmula: {t['formula']}\n\n"
    texto += "📊 Interpretação:\n"
    for nivel, desc in t['interpretacao'].items():
        texto += f"• {nivel}: {desc}\n"
    texto += f"\n📚 {t['fonte']}"
    
    if inline:
        # Retorna apenas o texto para usar em help=
        return texto
    else:
        # Mostra ícone pequeno com tooltip
        st.caption(f"ℹ️ {t['titulo']}", help=texto)


def gerar_link_compartilhamento() -> str:
    """Gera URL para compartilhamento do dashboard com parâmetros atuais."""
    params = {}
    if 'projeto' in st.session_state:
        params['projeto'] = st.session_state.projeto
    if 'filtro_qa' in st.session_state:
        params['qa'] = st.session_state.filtro_qa
    if 'filtro_dev' in st.session_state:
        params['dev'] = st.session_state.filtro_dev
    
    base_url = "http://localhost:8501"  # Mudar para URL real quando deployado
    if params:
        return f"{base_url}?{urllib.parse.urlencode(params)}"
    return base_url


# ==============================================================================
# ESTILOS CSS
# ==============================================================================

def aplicar_estilos():
    st.markdown("""
    <style>
    /* ==== ANIMAÇÕES DE ENTRADA ==== */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    
    /* Classes de animação */
    .animate-fadeInUp {
        animation: fadeInUp 0.5s ease-out forwards;
    }
    
    .animate-fadeIn {
        animation: fadeIn 0.4s ease-out forwards;
    }
    
    .animate-slideInLeft {
        animation: slideInLeft 0.4s ease-out forwards;
    }
    
    .animate-slideInRight {
        animation: slideInRight 0.4s ease-out forwards;
    }
    
    /* Aplicar animações a elementos Streamlit */
    .stMetric {
        animation: fadeInUp 0.4s ease-out;
    }
    
    .element-container:has(.status-card) {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Animação de hover nos cards */
    .status-card {
        transition: all 0.3s ease;
    }
    .status-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .metric-card, .alert-card, .insight-card { color: inherit; }
    
    .status-card {
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 2px solid;
        animation: fadeInUp 0.4s ease-out;
    }
    .status-green { background: rgba(34, 197, 94, 0.1); border-color: #22c55e; }
    .status-yellow { background: rgba(234, 179, 8, 0.1); border-color: #eab308; }
    .status-orange { background: rgba(249, 115, 22, 0.1); border-color: #f97316; }
    .status-red { background: rgba(239, 68, 68, 0.1); border-color: #ef4444; }
    .status-blue { background: rgba(59, 130, 246, 0.1); border-color: #3b82f6; }
    .status-purple { background: rgba(139, 92, 246, 0.1); border-color: #8b5cf6; }
    
    .big-number { font-size: 36px; font-weight: bold; margin: 0; }
    .card-label { font-size: 13px; opacity: 0.8; margin-top: 5px; }
    
    .alert-critical {
        background: rgba(239, 68, 68, 0.15);
        border-left: 4px solid #ef4444;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        animation: slideInLeft 0.4s ease-out;
    }
    .alert-warning {
        background: rgba(234, 179, 8, 0.15);
        border-left: 4px solid #eab308;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        animation: slideInLeft 0.4s ease-out;
    }
    .alert-info {
        background: rgba(59, 130, 246, 0.15);
        border-left: 4px solid #3b82f6;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        animation: slideInLeft 0.4s ease-out;
    }
    .alert-success {
        background: rgba(34, 197, 94, 0.15);
        border-left: 4px solid #22c55e;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        animation: slideInLeft 0.4s ease-out;
    }
    
    .ticket-card {
        border-radius: 10px;
        padding: 12px 15px;
        margin: 8px 0;
        border-left: 4px solid;
        background: rgba(100, 100, 100, 0.05);
        transition: all 0.2s ease;
    }
    .ticket-card:hover {
        transform: translateX(5px);
        background: rgba(100, 100, 100, 0.1);
    }
    .ticket-risk-high { border-left-color: #ef4444; }
    .ticket-risk-medium { border-left-color: #f97316; }
    .ticket-risk-low { border-left-color: #22c55e; }
    
    .section-header {
        background: linear-gradient(90deg, rgba(99, 102, 241, 0.15), transparent);
        padding: 12px 20px;
        border-radius: 8px;
        margin: 25px 0 15px 0;
        border-left: 4px solid #6366f1;
        animation: slideInLeft 0.5s ease-out;
    }
    
    .go-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
        animation: fadeIn 0.6s ease-out;
    }
    .go-approved { background: #22c55e; color: white; }
    .go-warning { background: #eab308; color: black; }
    .go-blocked { background: #ef4444; color: white; }
    
    .impact-card {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(16, 185, 129, 0.05));
        border: 1px solid rgba(34, 197, 94, 0.3);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        animation: fadeInUp 0.5s ease-out;
        transition: all 0.3s ease;
    }
    .impact-card:hover {
        transform: scale(1.01);
        box-shadow: 0 5px 20px rgba(34, 197, 94, 0.2);
    }
    
    .problematic-card {
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        animation: fadeIn 0.4s ease-out;
    }
    
    .comment-card {
        background: rgba(100, 100, 100, 0.05);
        border-radius: 8px;
        padding: 12px;
        margin: 5px 0;
        font-size: 13px;
    }
    
    .stTabs [data-baseweb="tab-list"] { 
        gap: 4px; 
        animation: fadeIn 0.3s ease-out;
    }
    .stTabs [data-baseweb="tab"] { 
        padding: 12px 24px; 
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(99, 102, 241, 0.1);
    }
    
    .metric-info {
        font-size: 11px;
        opacity: 0.7;
        margin-top: 4px;
    }
    
    .decisao-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.05));
        border: 2px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        animation: fadeInUp 0.5s ease-out;
    }
    
    .previsao-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(14, 165, 233, 0.05));
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        animation: fadeInUp 0.5s ease-out;
    }
    
    .share-button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        text-decoration: none;
        display: inline-block;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .share-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(99, 102, 241, 0.4);
    }
    
    /* Header com logo NINA */
    .nina-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px 0 15px 0;
        border-bottom: 2px solid #AF0C37;
        margin-bottom: 10px;
        animation: fadeIn 0.5s ease-out;
    }
    
    .nina-header svg {
        fill: #AF0C37;
    }
    
    .nina-header-title {
        font-size: 24px;
        font-weight: 700;
        color: #1f2937;
        margin-top: 10px;
    }
    
    .nina-header-subtitle {
        font-size: 13px;
        color: #6b7280;
        margin-top: 2px;
    }
    
    /* Barra de Release com animação */
    .release-bar {
        background: linear-gradient(90deg, #AF0C37, #8B0A2C);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        margin: 10px 0 20px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 14px;
        animation: slideInLeft 0.5s ease-out;
        box-shadow: 0 4px 15px rgba(175, 12, 55, 0.3);
    }
    
    .release-bar .release-name {
        font-weight: bold;
        font-size: 16px;
    }
    
    .release-bar .release-info {
        opacity: 0.9;
    }
    
    /* Card de métrica explicativa */
    .metric-explain-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(139, 92, 246, 0.05));
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        font-size: 13px;
    }
    .metric-explain-card h4 {
        margin: 0 0 8px 0;
        color: #6366f1;
        font-size: 14px;
    }
    .metric-explain-card .formula {
        background: rgba(0,0,0,0.05);
        padding: 8px 12px;
        border-radius: 6px;
        font-family: monospace;
        margin: 8px 0;
    }
    
    /* Expander customizado */
    .streamlit-expanderHeader {
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.2s ease;
    }
    .streamlit-expanderHeader:hover {
        color: #6366f1 !important;
    }
    
    /* Ocultar elementos desnecessários */
    .stDeployButton, #MainMenu {
        display: none !important;
    }
    
    /* Animação de loading shimmer */
    .shimmer-loading {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
    }
    </style>
    """, unsafe_allow_html=True)


# ==============================================================================
# AUTENTICAÇÃO E CONEXÃO JIRA
# ==============================================================================

def verificar_login() -> bool:
    """Verifica se o usuário está logado."""
    return st.session_state.get("logged_in", False) and st.session_state.get("user_email")


def fazer_login(email: str, senha: str) -> bool:
    """Valida login: email deve estar na lista e senha = email."""
    email_lower = email.lower().strip()
    
    # Verifica se email está autorizado (domínio @confirmationcall.com.br)
    autorizado = (
        email_lower in [e.lower() for e in EMAILS_AUTORIZADOS] or
        "@confirmationcall.com.br" in email_lower
    )
    
    # Senha = email (validação simples para uso interno)
    senha_correta = senha.strip().lower() == email_lower
    
    if autorizado and senha_correta:
        st.session_state.logged_in = True
        st.session_state.user_email = email_lower
        return True
    return False


def fazer_logout():
    """Remove sessão do usuário."""
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.dados = None
    st.session_state.modo_demo = True
    st.session_state.sprint_info = None


def get_credenciais() -> Tuple[str, str]:
    """Retorna email e token fixos para autenticação na API do Jira."""
    return JIRA_API_EMAIL, JIRA_API_TOKEN


def verificar_credenciais() -> bool:
    """Verifica se está logado (usa token fixo)."""
    return verificar_login()


def buscar_sprint_ativo(projeto: str = "SD") -> Optional[Dict]:
    """Busca informações da sprint ativa do projeto."""
    if not verificar_login():
        return None
    
    email, token = get_credenciais()
    
    # Buscar board do projeto
    url_boards = f"{JIRA_BASE_URL}/rest/agile/1.0/board?projectKeyOrId={projeto}"
    headers = {"Accept": "application/json"}
    
    try:
        response = requests.get(url_boards, headers=headers, auth=(email, token))
        response.raise_for_status()
        boards = response.json().get("values", [])
        
        if not boards:
            return None
        
        board_id = boards[0].get("id")
        
        # Buscar sprints ativos
        url_sprints = f"{JIRA_BASE_URL}/rest/agile/1.0/board/{board_id}/sprint?state=active"
        response = requests.get(url_sprints, headers=headers, auth=(email, token))
        response.raise_for_status()
        sprints = response.json().get("values", [])
        
        if sprints:
            sprint = sprints[0]
            return {
                "id": sprint.get("id"),
                "name": sprint.get("name"),
                "startDate": sprint.get("startDate"),
                "endDate": sprint.get("endDate"),
                "state": sprint.get("state")
            }
        
        return None
    except Exception as e:
        st.error(f"Erro ao buscar sprint: {e}")
        return None


def buscar_jira(jql: str, expand: str = "", max_results: int = 500) -> Optional[List[Dict]]:
    """Busca issues do Jira com suporte a paginação (nova API com nextPageToken)."""
    if not verificar_login():
        return None
    
    email, token = get_credenciais()
    base_url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
    headers = {"Accept": "application/json"}
    
    fields = ["key", "summary", "status", "issuetype", "assignee", "created", "updated",
              "resolutiondate", "priority", "project", "labels", "components",
              "comment"] + list(CUSTOM_FIELDS.values())
    
    all_issues = []
    next_page_token = None
    page_size = 100
    
    try:
        while True:
            # Construir query params
            params = {
                "jql": jql,
                "maxResults": page_size,
                "fields": ",".join(fields)
            }
            if expand:
                params["expand"] = expand
            if next_page_token:
                params["nextPageToken"] = next_page_token
            
            response = requests.get(base_url, headers=headers, params=params, auth=(email, token))
            response.raise_for_status()
            data = response.json()
            
            issues = data.get("issues", [])
            all_issues.extend(issues)
            
            # Verificar se há próxima página
            next_page_token = data.get("nextPageToken")
            if not next_page_token or len(all_issues) >= max_results:
                break
        
        return all_issues
    except Exception as e:
        st.error(f"Erro ao conectar com Jira: {e}")
        return None


def buscar_comentarios(ticket_id: str) -> List[Dict]:
    if not verificar_login():
        return []
    
    email, token = get_credenciais()
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}/comment"
    headers = {"Accept": "application/json"}
    
    try:
        response = requests.get(url, headers=headers, auth=(email, token))
        response.raise_for_status()
        return response.json().get("comments", [])
    except:
        return []


def processar_issues(issues: List[Dict], data_release: datetime) -> pd.DataFrame:
    dados = []
    
    for issue in issues:
        f = issue.get('fields', {})
        
        tipo_original = f.get('issuetype', {}).get('name', 'Desconhecido')
        tipo = "TAREFA"
        for t, nomes in [("HOTFIX", ["Hotfix", "Hotfeature"]), ("BUG", ["Bug", "Impeditivo"]),
                         ("TAREFA", ["Tarefa", "Task", "Subtarefa"]), ("SUGESTÃO", ["Sugestão"])]:
            if any(n in tipo_original for n in nomes):
                tipo = t
                break
        
        projeto = f.get('project', {}).get('key', 'N/A')
        
        dev = 'Não atribuído'
        if f.get('assignee'):
            dev = f['assignee'].get('displayName', dev)
        
        # Tentar ler SP de ambos os campos (principal e alternativo)
        sp = f.get(CUSTOM_FIELDS['story_points']) or f.get(CUSTOM_FIELDS.get('story_points_alt', '')) or 0
        
        sprint_f = f.get(CUSTOM_FIELDS['sprint'], [])
        sprint = sprint_f[-1].get('name', 'Sem Sprint') if sprint_f else 'Sem Sprint'
        
        status = f.get('status', {}).get('name', 'Desconhecido')
        
        status_cat = 'unknown'
        for cat, statuses in STATUS_FLOW.items():
            if any(s.lower() in status.lower() for s in statuses):
                status_cat = cat
                break
        
        bugs = f.get(CUSTOM_FIELDS['bugs_encontrados'], 0) or 0
        
        comp = f.get(CUSTOM_FIELDS['complexidade_teste'])
        complexidade = comp.get('value', 'N/A') if isinstance(comp, dict) else 'N/A'
        
        qa = 'Não atribuído'
        qa_f = f.get(CUSTOM_FIELDS['qa_responsavel'])
        if qa_f:
            if isinstance(qa_f, dict):
                qa = qa_f.get('displayName', qa)
            elif isinstance(qa_f, list) and qa_f:
                qa = qa_f[0].get('displayName', qa)
        
        janela = f.get(CUSTOM_FIELDS['janela_testes'], '')
        
        try:
            criado = datetime.fromisoformat(f.get('created', '').replace('Z', '+00:00')).replace(tzinfo=None)
        except:
            criado = datetime.now()
        
        try:
            atualizado = datetime.fromisoformat(f.get('updated', '').replace('Z', '+00:00')).replace(tzinfo=None)
        except:
            atualizado = datetime.now()
        
        comentarios = f.get('comment', {}).get('comments', [])
        num_comentarios = len(comentarios)
        ultimos_comentarios = []
        for c in comentarios[-3:]:
            autor = c.get('author', {}).get('displayName', 'Anônimo')
            corpo = c.get('body', {})
            if isinstance(corpo, dict):
                texto = ""
                for content in corpo.get('content', []):
                    for item in content.get('content', []):
                        if item.get('type') == 'text':
                            texto += item.get('text', '')
            else:
                texto = str(corpo)
            ultimos_comentarios.append({'autor': autor, 'texto': texto[:200]})
        
        ticket_id = issue.get('key', f"ID-{issue.get('id', '?')}")
        
        # Calcular dias até release e tempo em QA
        dias_ate_release = calcular_dias_uteis(datetime.now(), data_release)
        
        # Tempo em QA: se está em waiting_qa/testing, calcular desde que chegou lá
        # Aproximação: usar dias desde última atualização para cards em QA
        tempo_em_qa = 0
        if status_cat in ['waiting_qa', 'testing']:
            tempo_em_qa = (datetime.now() - atualizado).days
        elif status_cat == 'done':
            # Para cards concluídos, estimar com base no ciclo
            tempo_em_qa = min(5, (atualizado - criado).days // 3)
        
        # Cards dentro da janela crítica (≤3 dias até release)
        dentro_janela = dias_ate_release <= 3 and status_cat in ['waiting_qa', 'testing']
        
        dados.append({
            'ticket_id': ticket_id,
            'link': link_jira(ticket_id),
            'titulo': f.get('summary', 'Sem título'),
            'tipo': tipo,
            'tipo_original': tipo_original,
            'status': status,
            'status_cat': status_cat,
            'projeto': projeto,
            'desenvolvedor': dev,
            'qa': qa,
            'sp': sp,
            'bugs': bugs,
            'sprint': sprint,
            'prioridade': f.get('priority', {}).get('name', 'Média'),
            'complexidade': complexidade,
            'janela_testes': janela,
            'criado': criado,
            'atualizado': atualizado,
            'data_release': data_release,
            'dias_em_status': (datetime.now() - atualizado).days,
            'lead_time': (atualizado - criado).days,
            'num_comentarios': num_comentarios,
            'comentarios': ultimos_comentarios,
            'dias_ate_release': dias_ate_release,
            'tempo_em_qa': tempo_em_qa,
            'dentro_janela': dentro_janela,
        })
    
    return pd.DataFrame(dados)


def gerar_dados_mock(projeto: str = "SD") -> pd.DataFrame:
    """Gera dados realistas para demonstração."""
    
    devs = ["Augusto Oliveira", "Christopher Krauss de Carvalho", "Suyan Moriel", 
            "Daniel Marques", "Elinton Dozol Machado", "Carlos Daniel de Souza Cordeiro",
            "Cristian Yamamoto", "João Pedro Menegali"]
    
    qas = ["Vinicios Ferreira", "Vinicius Alves da Silva Neto", 
           "João Pedro Greif de Souza", "Eduardo Barbosa da Silva"]
    
    tipos = ["TAREFA", "BUG", "HOTFIX"]
    complexidades = ["Baixa", "Média", "Alta", "Muito Alta"]
    prioridades = ["Baixa", "Média", "Alta", "Muito Alta"]
    
    statuses = [
        ("Backlog", "backlog"),
        ("Em andamento", "development"),
        ("EM REVISÃO", "code_review"),
        ("AGUARDANDO VALIDAÇÃO", "waiting_qa"),
        ("EM VALIDAÇÃO", "testing"),
        ("Concluído", "done"),
        ("IMPEDIDO", "blocked"),
    ]
    
    comentarios_mock = [
        "Validado com sucesso, sem bugs encontrados.",
        "Encontrado bug crítico na integração com API.",
        "Card retornou do QA com 2 bugs.",
        "Aprovado após correção dos bugs relatados.",
        "Necessário revisão dos critérios de aceite.",
        "Teste de regressão realizado, OK.",
        "Fluxo alternativo identificado e documentado.",
        "Dev confirma correção aplicada.",
    ]
    
    sprint = "Release 238 (Atual)"
    
    dados = []
    hoje = datetime.now()
    data_release = hoje + timedelta(days=random.randint(7, 14))
    
    for i in range(55):
        tipo = random.choices(tipos, weights=[60, 25, 15])[0]
        sp = random.choice([3, 5, 8, 13]) if tipo == "TAREFA" else random.choice([1, 2, 3])
        
        comp = random.choice(complexidades)
        if comp in ["Alta", "Muito Alta"]:
            bugs = random.choices([0, 1, 2, 3, 4, 5], weights=[15, 20, 25, 20, 15, 5])[0]
        else:
            bugs = random.choices([0, 1, 2, 3], weights=[45, 30, 20, 5])[0]
        
        status, status_cat = random.choice(statuses)
        
        criado = hoje - timedelta(days=random.randint(3, 35))
        lead_time = random.randint(2, 15)
        atualizado = criado + timedelta(days=lead_time)
        if atualizado > hoje:
            atualizado = hoje
        
        janela = str(random.randint(2, 12)) if status_cat in ['waiting_qa', 'done'] else ''
        
        ticket_id = f"{projeto}-{1000 + i}"
        
        # Calcular datas relacionadas ao QA
        dias_ate_release = calcular_dias_uteis(hoje, data_release)
        if status_cat in ['waiting_qa', 'testing', 'done']:
            # Simular quando foi enviado para QA (alguns dias antes do atual)
            data_enviado_qa = atualizado - timedelta(days=random.randint(1, 5))
            tempo_em_qa = (hoje - data_enviado_qa).days if status_cat != 'done' else random.randint(1, 5)
        else:
            data_enviado_qa = None
            tempo_em_qa = 0
        
        # Calcular se está "dentro da janela" (3 dias úteis antes da release)
        dentro_janela = dias_ate_release <= 3 and status_cat in ['waiting_qa', 'testing']
        
        num_comentarios = random.randint(0, 8)
        coments = []
        for _ in range(min(3, num_comentarios)):
            coments.append({
                'autor': random.choice(qas + devs),
                'texto': random.choice(comentarios_mock)
            })
        
        dados.append({
            'ticket_id': ticket_id,
            'link': link_jira(ticket_id),
            'titulo': f"{tipo} - Implementação de funcionalidade #{i+1}",
            'tipo': tipo,
            'tipo_original': tipo,
            'status': status,
            'status_cat': status_cat,
            'projeto': projeto,
            'desenvolvedor': random.choice(devs),
            'qa': random.choice(qas),
            'sp': sp,
            'bugs': bugs,
            'sprint': sprint,
            'prioridade': random.choices(prioridades, weights=[10, 50, 30, 10])[0],
            'complexidade': comp,
            'janela_testes': janela,
            'criado': criado,
            'atualizado': atualizado,
            'data_release': data_release,
            'dias_ate_release': dias_ate_release,
            'data_enviado_qa': data_enviado_qa,
            'tempo_em_qa': tempo_em_qa,
            'dentro_janela': dentro_janela,
            'dias_em_status': (hoje - atualizado).days,
            'lead_time': lead_time,
            'num_comentarios': num_comentarios,
            'comentarios': coments,
        })
    
    return pd.DataFrame(dados)


# ==============================================================================
# MÉTRICAS ISTQB/CTFL
# ==============================================================================

def calcular_fator_k(sp: int, bugs: int, rigor: float = 1.5) -> float:
    """Calcula Fator K. Retorna -1 se não há SP para indicar dados insuficientes."""
    if sp == 0:
        return -1  # Indica que não há dados de SP
    return round(sp / (bugs + 1) * rigor, 2)


def classificar_maturidade(fator_k: float, sp: int = 0, bugs: int = 0) -> Dict:
    """Classifica maturidade baseado no Fator K (FK).
    
    O Fator K é calculado como: FK = SP / (Bugs + 1)
    
    Gold: FK >= 3.0 (Excelente qualidade, código maduro)
    Silver: FK >= 2.0 (Boa qualidade, dentro do esperado)  
    Bronze: FK >= 1.0 (Regular, precisa de atenção)
    Risco: FK < 1.0 (Crítico, requer intervenção imediata)
    """
    # Caso especial: sem Story Points
    if sp == 0:
        if bugs == 0:
            return {"selo": "Sem SP", **MATURIDADE["Sem SP"]}
        return {"selo": "Risco", **MATURIDADE["Risco"]}
    
    # Classificação baseada no Fator K
    # GOLD: FK >= 3.0 (Excelente qualidade)
    if fator_k >= 3.0:
        return {"selo": "Gold", **MATURIDADE["Gold"]}
    
    # SILVER: FK >= 2.0 (Boa qualidade)
    if fator_k >= 2.0:
        return {"selo": "Silver", **MATURIDADE["Silver"]}
    
    # BRONZE: FK >= 1.0 (Regular)
    if fator_k >= 1.0:
        return {"selo": "Bronze", **MATURIDADE["Bronze"]}
    
    # RISCO: FK < 1.0 (Crítico)
    return {"selo": "Risco", **MATURIDADE["Risco"]}


def calcular_ddp(df: pd.DataFrame) -> Dict:
    """Defect Detection Percentage - eficácia do QA."""
    bugs_qa = df['bugs'].sum()
    bugs_estimados_prod = max(1, len(df) * 0.05)  # Estimativa: 5% escapa
    
    total_bugs = bugs_qa + bugs_estimados_prod
    ddp = (bugs_qa / total_bugs * 100) if total_bugs > 0 else 100
    
    status = 'excellent' if ddp >= 85 else 'good' if ddp >= 70 else 'regular' if ddp >= 50 else 'poor'
    return {"valor": round(ddp, 1), "status": status, "bugs_qa": bugs_qa}


def calcular_first_pass_yield(df: pd.DataFrame) -> Dict:
    """First Pass Yield - cards aprovados de primeira."""
    total = len(df)
    if total == 0:
        return {"valor": 0, "status": "poor", "sem_bugs": 0, "total": 0}
    
    sem_bugs = len(df[df['bugs'] == 0])
    fpy = sem_bugs / total * 100
    
    status = 'excellent' if fpy >= 80 else 'good' if fpy >= 60 else 'regular' if fpy >= 40 else 'poor'
    return {"valor": round(fpy, 1), "status": status, "sem_bugs": sem_bugs, "total": total}


def calcular_defect_density(df: pd.DataFrame) -> Dict:
    """Densidade de defeitos por SP."""
    sp_total = df['sp'].sum()
    bugs_total = int(df['bugs'].sum())
    
    dd = bugs_total / sp_total if sp_total > 0 else 0
    return {"valor": round(dd, 2), "bugs": bugs_total, "sp": int(sp_total)}


def calcular_mttr(df: pd.DataFrame) -> Dict:
    """Mean Time To Repair."""
    bugs_df = df[df['bugs'] > 0]
    if bugs_df.empty:
        return {"valor": 0, "cards_com_bugs": 0}
    
    tempo_medio = bugs_df['lead_time'].mean()
    return {"valor": round(tempo_medio, 1), "cards_com_bugs": len(bugs_df)}


def calcular_lead_time(df: pd.DataFrame) -> Dict:
    """Lead time médio e percentis."""
    if df.empty:
        return {"medio": 0, "p50": 0, "p85": 0, "p95": 0}
    
    lead_times = df['lead_time']
    return {
        "medio": round(lead_times.mean(), 1),
        "p50": round(lead_times.quantile(0.5), 1),
        "p85": round(lead_times.quantile(0.85), 1),
        "p95": round(lead_times.quantile(0.95), 1),
    }


def calcular_throughput(df: pd.DataFrame) -> Dict:
    """Vazão de cards concluídos."""
    concluidos = df[df['status_cat'] == 'done']
    return {
        "cards": len(concluidos),
        "sp": concluidos['sp'].sum(),
        "por_dia": round(len(concluidos) / 14, 1),  # Assumindo sprint de 2 semanas
    }


def calcular_wip(df: pd.DataFrame) -> Dict:
    """Work In Progress atual."""
    em_andamento = df[~df['status_cat'].isin(['backlog', 'done', 'deferred'])]
    return {
        "total": len(em_andamento),
        "development": len(df[df['status_cat'] == 'development']),
        "code_review": len(df[df['status_cat'] == 'code_review']),
        "waiting_qa": len(df[df['status_cat'] == 'waiting_qa']),
        "testing": len(df[df['status_cat'] == 'testing']),
        "blocked": len(df[df['status_cat'] == 'blocked']),
    }


def identificar_gargalos(df: pd.DataFrame) -> List[Dict]:
    """Identifica gargalos no fluxo."""
    gargalos = []
    
    limites = {
        'waiting_qa': {'esperado': 3, 'limite': 5},
        'code_review': {'esperado': 2, 'limite': 4},
        'development': {'esperado': 5, 'limite': 8},
    }
    
    for cat, lim in limites.items():
        cards_cat = df[df['status_cat'] == cat]
        if not cards_cat.empty:
            tempo_medio = cards_cat['dias_em_status'].mean()
            if tempo_medio > lim['limite'] or len(cards_cat) > 5:
                impacto = 'ALTO' if tempo_medio > lim['limite'] * 1.5 else 'MÉDIO'
                gargalos.append({
                    'categoria': cat,
                    'cards': len(cards_cat),
                    'atual': round(tempo_medio, 1),
                    'esperado': lim['esperado'],
                    'impacto': impacto,
                    'tickets': cards_cat['ticket_id'].tolist(),
                })
    
    return sorted(gargalos, key=lambda x: x['impacto'] == 'ALTO', reverse=True)


def avaliar_go_no_go(df: pd.DataFrame) -> Dict:
    """Avaliação Go/No-Go com base em métricas."""
    bloqueios = []
    alertas = []
    
    # 1. Verifica cards bloqueados
    bloqueados = df[df['status_cat'] == 'blocked']
    if not bloqueados.empty:
        cards_info = [{'id': row['ticket_id'], 'titulo': row.get('titulo', '')[:60], 'link': row.get('link', '')} 
                      for _, row in bloqueados.iterrows()]
        bloqueios.append({
            'tipo': 'blocked',
            'msg': f"{len(bloqueados)} card(s) bloqueado(s) - Resolver antes da release",
            'cards': cards_info
        })
    
    # 2. Fila de QA muito grande
    fila_qa = df[df['status_cat'] == 'waiting_qa']
    if len(fila_qa) > 10:
        cards_info = [{'id': row['ticket_id'], 'titulo': row.get('titulo', '')[:60], 'link': row.get('link', '')} 
                      for _, row in fila_qa.iterrows()]
        alertas.append({
            'tipo': 'queue',
            'msg': f"Fila de QA alta: {len(fila_qa)} cards aguardando validação",
            'cards': cards_info
        })
    
    # 3. Cards críticos não concluídos
    criticos = df[(df['prioridade'].isin(['Alta', 'Muito Alta', 'Muito alto', 'Alto'])) & 
                  (df['status_cat'] != 'done')]
    if not criticos.empty:
        cards_info = [{'id': row['ticket_id'], 'titulo': row.get('titulo', '')[:60], 'link': row.get('link', '')} 
                      for _, row in criticos.iterrows()]
        alertas.append({
            'tipo': 'priority',
            'msg': f"{len(criticos)} card(s) de alta prioridade ainda em andamento",
            'cards': cards_info
        })
    
    # 4. FPY muito baixo
    fpy = calcular_first_pass_yield(df)
    if fpy['valor'] < 40:
        alertas.append({
            'tipo': 'quality',
            'msg': f"FPY baixo ({fpy['valor']}%) - Muitos bugs encontrados",
            'cards': []
        })
    
    # Health Score
    health = calcular_health_score(df)
    
    # Decisão
    if bloqueios:
        decisao = "🛑 BLOQUEAR RELEASE"
        classe = "blocked"
    elif len(alertas) >= 3 or health['score'] < 50:
        decisao = "⚠️ REVISAR ANTES"
        classe = "warning"
    else:
        decisao = "✅ GO PARA RELEASE"
        classe = "approved"
    
    return {
        'decisao': decisao,
        'classe': classe,
        'bloqueios': bloqueios,
        'alertas': alertas,
        'health': health,
    }


def calcular_health_score(df: pd.DataFrame) -> Dict:
    """Calcula score de saúde da release (0-100)."""
    detalhes = {}
    
    # 1. Taxa de conclusão (peso 30)
    concluidos = len(df[df['status_cat'] == 'done'])
    taxa_conclusao = concluidos / len(df) * 100 if len(df) > 0 else 0
    score_conclusao = min(30, taxa_conclusao * 0.3)
    detalhes['conclusao'] = {'peso': 30, 'score': round(score_conclusao, 1), 'valor': f"{taxa_conclusao:.0f}%"}
    
    # 2. DDP (peso 25)
    ddp = calcular_ddp(df)
    score_ddp = min(25, ddp['valor'] * 0.25)
    detalhes['ddp'] = {'peso': 25, 'score': round(score_ddp, 1), 'valor': f"{ddp['valor']}%"}
    
    # 3. FPY (peso 20)
    fpy = calcular_first_pass_yield(df)
    score_fpy = min(20, fpy['valor'] * 0.2)
    detalhes['fpy'] = {'peso': 20, 'score': round(score_fpy, 1), 'valor': f"{fpy['valor']}%"}
    
    # 4. Gargalos (peso 15)
    gargalos = identificar_gargalos(df)
    penalidade_gargalos = len([g for g in gargalos if g['impacto'] == 'ALTO']) * 5
    score_gargalos = max(0, 15 - penalidade_gargalos)
    detalhes['gargalos'] = {'peso': 15, 'score': score_gargalos, 'valor': f"{len(gargalos)} encontrados"}
    
    # 5. Lead Time (peso 10)
    lead = calcular_lead_time(df)
    score_lead = 10 if lead['medio'] <= 7 else 7 if lead['medio'] <= 10 else 4 if lead['medio'] <= 14 else 0
    detalhes['lead_time'] = {'peso': 10, 'score': score_lead, 'valor': f"{lead['medio']} dias"}
    
    score_total = sum(d['score'] for d in detalhes.values())
    
    if score_total >= 75:
        status = "🟢 Saudável"
    elif score_total >= 50:
        status = "🟡 Atenção"
    elif score_total >= 25:
        status = "🟠 Alerta"
    else:
        status = "🔴 Crítico"
    
    return {'score': score_total, 'status': status, 'detalhes': detalhes}


# ==============================================================================
# ANÁLISES DETALHADAS
# ==============================================================================

def analisar_qa_detalhado(df: pd.DataFrame, qa_nome: str) -> Optional[Dict]:
    """Análise completa de um QA."""
    df_qa = df[df['qa'] == qa_nome]
    if df_qa.empty:
        return None
    
    validados = df_qa[df_qa['status_cat'] == 'done']
    em_fila = df_qa[df_qa['status_cat'] == 'waiting_qa']
    em_validacao = df_qa[df_qa['status_cat'] == 'testing']
    
    bugs_encontrados = int(df_qa['bugs'].sum())
    sp_protegidos = df_qa['sp'].sum()
    
    fpy = calcular_first_pass_yield(df_qa)
    ddp = calcular_ddp(df_qa)
    
    tempo_validacao = validados['lead_time'].mean() if not validados.empty else 0
    
    cards_problematicos = df_qa[df_qa['bugs'] >= 3].sort_values('bugs', ascending=False)
    
    mais_rapido = validados.nsmallest(3, 'lead_time') if not validados.empty else pd.DataFrame()
    mais_lento = validados.nlargest(3, 'lead_time') if not validados.empty else pd.DataFrame()
    
    por_complexidade = {}
    for comp in df_qa['complexidade'].unique():
        comp_df = df_qa[df_qa['complexidade'] == comp]
        por_complexidade[comp] = {
            'ticket_id': len(comp_df),
            'bugs': comp_df['bugs'].sum(),
            'lead_time': round(comp_df['lead_time'].mean(), 1) if not comp_df.empty else 0
        }
    
    return {
        'df': df_qa,
        'cards_total': len(df_qa),
        'validados': len(validados),
        'em_fila': len(em_fila),
        'em_validacao': len(em_validacao),
        'bugs_encontrados': bugs_encontrados,
        'bugs_evitados': bugs_encontrados,
        'sp_protegidos': sp_protegidos,
        'fpy': fpy,
        'ddp': ddp,
        'tempo_validacao': round(tempo_validacao, 1),
        'cards_problematicos': cards_problematicos,
        'mais_rapido': mais_rapido,
        'mais_lento': mais_lento,
        'por_complexidade': por_complexidade,
    }


def analisar_dev_detalhado(df: pd.DataFrame, dev_nome: str) -> Optional[Dict]:
    """Análise completa de um desenvolvedor."""
    df_dev = df[df['desenvolvedor'] == dev_nome]
    if df_dev.empty:
        return None
    
    sp_total = df_dev['sp'].sum()
    bugs_total = int(df_dev['bugs'].sum())
    
    fk_medio = calcular_fator_k(sp_total, bugs_total)
    maturidade = classificar_maturidade(fk_medio, sp_total, bugs_total)
    
    zero_bugs = len(df_dev[df_dev['bugs'] == 0]) / len(df_dev) * 100 if len(df_dev) > 0 else 0
    
    return {
        'df': df_dev,
        'cards': len(df_dev),
        'sp_total': sp_total,
        'bugs_total': bugs_total,
        'fk_medio': fk_medio,
        'maturidade': maturidade,
        'zero_bugs': round(zero_bugs, 1),
        'tempo_medio': round(df_dev['lead_time'].mean(), 1) if not df_dev.empty else 0,
    }


# ==============================================================================
# COMPONENTES UI
# ==============================================================================

def mostrar_metrica_com_tooltip(valor: str, titulo: str, metrica_key: str, cor: str = "blue", subtitulo: str = ""):
    """Mostra métrica com tooltip explicativo em layout responsivo."""
    # Card com a métrica
    st.markdown(f"""
    <div class="status-card status-{cor}" style="padding: 15px;">
        <p class="big-number">{valor}</p>
        <p class="card-label">{titulo}</p>
        {f'<p class="metric-info">{subtitulo}</p>' if subtitulo else ''}
    </div>
    """, unsafe_allow_html=True)
    
    # Tooltip como popover separado (não usa colunas para evitar sobreposição)
    mostrar_tooltip(metrica_key)


def mostrar_alerta_expandivel(tipo: str, titulo: str, msg: str, cards: List):
    """Mostra alerta com lista expandível de cards (com títulos)."""
    classe = f"alert-{tipo}" if tipo in ['critical', 'warning', 'info', 'success'] else 'alert-info'
    
    st.markdown(f"""
    <div class="{classe}">
        <b>{titulo}</b>
        <p style="margin: 5px 0;">{msg}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if cards:
        with st.expander(f"📋 Ver {len(cards)} card(s) afetado(s)"):
            for card in cards[:10]:
                # Suporta tanto string quanto dict com info do card
                if isinstance(card, dict):
                    ticket_id = card.get('id', '')
                    titulo_card = card.get('titulo', '')
                    link = card.get('link', link_jira(ticket_id))
                    st.markdown(f"""- **[{ticket_id}]({link})** - {titulo_card}""")
                else:
                    st.markdown(f"- [{card}]({link_jira(card)})")
            if len(cards) > 10:
                st.caption(f"... e mais {len(cards) - 10} cards")


def mostrar_card_ticket(row: Dict, compacto: bool = False, mostrar_qa: bool = True):
    """Mostra card de ticket com informações."""
    bugs = row.get('bugs', 0)
    risco = 'high' if bugs >= 3 else 'medium' if bugs >= 1 else 'low'
    
    if compacto:
        st.markdown(f"""
        <div class="ticket-card ticket-risk-{risco}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <a href="{row['link']}" target="_blank" style="color: #6366f1; font-weight: bold; text-decoration: none;">🔗 {row['ticket_id']}</a>
                <span style="opacity: 0.7;">{row.get('sp', 0)} SP | 🐛 {bugs}</span>
            </div>
            <p style="margin: 5px 0 0 0; font-size: 13px; opacity: 0.9;">{row.get('titulo', '')[:50]}...</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        qa_info = f"<br><b>QA:</b> {row.get('qa', 'N/A')}" if mostrar_qa else ""
        st.markdown(f"""
        <div class="ticket-card ticket-risk-{risco}">
            <div style="display: flex; justify-content: space-between;">
                <a href="{row['link']}" target="_blank" style="color: #6366f1; font-weight: bold; text-decoration: none;">🔗 {row['ticket_id']}</a>
                <span style="color: {'#ef4444' if bugs >= 3 else '#f97316' if bugs >= 1 else '#22c55e'}; font-weight: bold;">🐛 {bugs} bugs</span>
            </div>
            <p style="margin: 8px 0;">{row.get('titulo', '')}</p>
            <p style="font-size: 12px; opacity: 0.8;">
                <b>Dev:</b> {row.get('desenvolvedor', 'N/A')} | 
                <b>SP:</b> {row.get('sp', 0)} | 
                <b>Status:</b> {row.get('status', 'N/A')}{qa_info}
            </p>
        </div>
        """, unsafe_allow_html=True)


def mostrar_comentarios(comentarios: List[Dict]):
    """Mostra lista de comentários."""
    for c in comentarios:
        st.markdown(f"""
        <div class="comment-card">
            <b>{c.get('autor', 'Anônimo')}</b>
            <p style="margin: 5px 0 0 0;">{c.get('texto', '')}</p>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# ABA DE LIDERANÇA (EXPANDIDA)
# ==============================================================================

def aba_lideranca(df: pd.DataFrame):
    """Aba de Liderança - Visão executiva expandida com decisões."""
    
    # Pegar release atual
    release_atual = st.session_state.get('release_atual', 'Release 238')
    
    st.markdown('<div class="section-header"><h2>🎯 Painel de Liderança</h2></div>', unsafe_allow_html=True)
    st.caption(f"📦 Dados da **{release_atual}** | Métricas baseadas em ISTQB/CTFL e processos internos da NINA Tecnologia")
    
    go_no_go = avaliar_go_no_go(df)
    health = go_no_go['health']
    
    # ==== SEÇÃO 1: Status da Release ====
    with st.expander("🎯 **Status da Release** - Visão executiva para tomada de decisão", expanded=True):
        st.caption("""
        A pontuação de saúde é calculada com base em 5 indicadores: taxa de conclusão, DDP (detecção de defeitos), 
        FPY (aprovação de primeira), gargalos no fluxo e lead time médio. Cada indicador tem um peso na composição final.
        """)
        
        # Dias até release em destaque
        dias_release = df['dias_ate_release'].iloc[0] if 'dias_ate_release' in df.columns and len(df) > 0 else 10
        
        col_dias, col_health = st.columns([1, 3])
        
        with col_dias:
            dias_cor = 'green' if dias_release > 5 else 'yellow' if dias_release > 2 else 'red'
            st.markdown(f"""
            <div class="status-card status-{dias_cor}" style="padding: 20px;">
                <p style="font-size: 42px; font-weight: bold; margin: 0;">📅 {dias_release}</p>
                <p class="card-label">Dias até a Release</p>
                <p style="font-size: 11px; opacity: 0.7; margin-top: 5px;">
                    {'Prazo confortável' if dias_release > 5 else 'Atenção ao prazo' if dias_release > 2 else 'Prazo crítico!'}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_health:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                cor_class = 'green' if health['score'] >= 75 else 'yellow' if health['score'] >= 50 else 'orange' if health['score'] >= 25 else 'red'
                status_texto = {
                    'green': 'Release em excelente estado para produção',
                    'yellow': 'Release requer atenção em alguns pontos',
                    'orange': 'Release com riscos que precisam ser avaliados',
                    'red': 'Release com problemas críticos a resolver'
                }
                st.markdown(f"""
                <div class="status-card status-{cor_class}" style="padding: 30px;">
                    <p class="big-number">{health['score']:.0f}</p>
                    <p class="card-label">Pontuação de Saúde</p>
                    <p style="margin-top: 10px; font-size: 16px;"><b>{health['status']}</b></p>
                    <p style="font-size: 12px; opacity: 0.8; margin-top: 8px;">{status_texto.get(cor_class, '')}</p>
                </div>
                """, unsafe_allow_html=True)
        
            with col2:
                # Métricas executivas em linha
                c1, c2, c3, c4 = st.columns(4)
                
                with c1:
                    st.metric("Total de Cards", len(df), help="Número total de cards nesta release")
                with c2:
                    st.metric("Story Points", int(df['sp'].sum()), help="Soma dos story points estimados")
                with c3:
                    concluidos = len(df[df['status_cat'] == 'done'])
                    pct = concluidos/len(df)*100 if len(df) > 0 else 0
                    st.metric("Concluídos", f"{concluidos} ({pct:.0f}%)", help="Cards que já passaram por QA e estão prontos")
                with c4:
                    lead = calcular_lead_time(df)
                    st.metric("Lead Time Médio", f"{lead['medio']} dias", help="Tempo médio do card desde criação até conclusão")
        
        # Fator K Geral do Time
        st.markdown("---")
        st.markdown("#### 📊 Maturidade de Entrega do Time (Fator K)")
        st.caption("""
        **Fator K** = Story Points / (Bugs + 1) × Rigor (1.5). 
        Indica a qualidade da entrega: quanto maior o FK, menos bugs em relação ao esforço planejado.
        """)
        
        sp_total = df['sp'].sum()
        bugs_total = int(df['bugs'].sum())
        fk_geral = calcular_fator_k(sp_total, bugs_total)
        maturidade_geral = classificar_maturidade(fk_geral, sp_total, bugs_total)
        
        col_fk1, col_fk2, col_fk3 = st.columns([1, 1, 2])
        
        with col_fk1:
            fk_cor = 'green' if fk_geral >= 3 else 'yellow' if fk_geral >= 2 else 'orange' if fk_geral >= 1 else 'red'
            if fk_geral < 0:
                fk_cor = 'blue'
                fk_display = "N/A"
            else:
                fk_display = f"{fk_geral:.1f}"
            
            st.markdown(f"""
            <div class="status-card status-{fk_cor}" style="padding: 20px;">
                <p style="font-size: 36px; font-weight: bold; margin: 0;">{fk_display}</p>
                <p class="card-label">Fator K do Time</p>
                <p style="font-size: 14px; margin-top: 8px;">{maturidade_geral['emoji']} {maturidade_geral['selo']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_fk2:
            st.markdown(f"""
            | Componente | Valor |
            |------------|-------|
            | Story Points | **{int(sp_total)}** |
            | Bugs Encontrados | **{bugs_total}** |
            | Rigor Aplicado | **1.5** |
            """)
        
        with col_fk3:
            st.markdown("""
            **Interpretação do Fator K:**
            - 🥇 **FK ≥ 3.0** → Excelente (Gold) - Entrega madura
            - 🥈 **FK ≥ 2.0** → Bom (Silver) - Meta atingida
            - 🥉 **FK ≥ 1.0** → Regular (Bronze) - Melhorar
            - ⚠️ **FK < 1.0** → Atenção - Muitos bugs/SP
            """)
        
        st.markdown("---")
        
        # Alertas e pontos de atenção
        if go_no_go['bloqueios']:
            st.markdown("#### 🚨 Pontos Críticos")
            st.caption("Itens que precisam de resolução antes de prosseguir com a release")
            for b in go_no_go['bloqueios']:
                mostrar_alerta_expandivel('critical', '🚫 Crítico', b['msg'], b.get('cards', []))
        
        if go_no_go['alertas']:
            st.markdown("#### ⚠️ Pontos de Atenção")
            st.caption("Itens que merecem monitoramento mas não impedem a release")
            for a in go_no_go['alertas']:
                mostrar_alerta_expandivel('warning', '⚠️ Atenção', a['msg'], a.get('cards', []))
        
        if not go_no_go['bloqueios'] and not go_no_go['alertas']:
            st.markdown("""
            <div class="alert-success">
                <b>✅ Release Saudável</b>
                <p style="margin: 5px 0;">Todos os critérios de qualidade atendidos. A release pode seguir para produção.</p>
            </div>
            """, unsafe_allow_html=True)
    
    
    # ==== SEÇÃO 2: Composição do Health Score ====
    with st.expander("📊 **Composição da Pontuação** - Detalhamento dos 5 indicadores", expanded=True):
        st.caption("""
        Cada indicador contribui com um peso para a pontuação final. 
        **Verde**: atingiu meta | **Amarelo**: atenção | **Vermelho**: abaixo do esperado
        """)
        
        cols = st.columns(5)
        detalhes = health['detalhes']
        
        nomes = {
            'conclusao': ('Conclusão', 'Taxa de cards finalizados', None),
            'ddp': ('DDP', 'Detecção de Defeitos', 'ddp'),
            'fpy': ('FPY', 'Aprovação de Primeira', 'fpy'),
            'gargalos': ('Gargalos', 'Pontos de lentidão', None),
            'lead_time': ('Lead Time', 'Tempo de entrega', 'lead_time')
        }
        
        for i, (nome, d) in enumerate(detalhes.items()):
            with cols[i]:
                titulo, desc, tooltip_key = nomes.get(nome, (nome, '', None))
                cor = 'green' if d['score'] >= d['peso'] * 0.7 else 'yellow' if d['score'] >= d['peso'] * 0.4 else 'red'
                
                st.markdown(f"""
                <div class="status-card status-{cor}" style="padding: 10px;">
                    <p style="font-size: 20px; font-weight: bold; margin: 0;">{d['score']:.1f}/{d['peso']}</p>
                    <p class="card-label">{titulo}</p>
                    <p class="metric-info">{d['valor']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if tooltip_key:
                    mostrar_tooltip(tooltip_key)
    
    # ==== SEÇÃO 3: Métricas de Qualidade ISTQB ====
    with st.expander("🧪 **Métricas de Qualidade ISTQB** - Indicadores padronizados internacionais", expanded=True):
        st.markdown("""
        <div class="metric-explain-card">
        <h4>📚 O que são essas métricas?</h4>
        Métricas baseadas no <b>ISTQB (International Software Testing Qualifications Board)</b>, o padrão mundial para medir qualidade de software.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            ddp = calcular_ddp(df)
            fpy = calcular_first_pass_yield(df)
            
            # DDP - Detecção de Defeitos
            st.markdown("##### 🔍 DDP - Detecção de Defeitos Preventiva")
            st.caption("Porcentagem de bugs encontrados pelo QA **antes** de chegar ao usuário final.")
            ddp_cor = 'green' if ddp['valor'] >= 85 else 'yellow' if ddp['valor'] >= 70 else 'orange' if ddp['valor'] >= 50 else 'red'
            
            col_m1, col_m2 = st.columns([2, 3])
            with col_m1:
                st.markdown(f"""
                <div class="status-card status-{ddp_cor}" style="padding: 15px;">
                    <p class="big-number">{ddp['valor']}%</p>
                    <p class="card-label">DDP</p>
                </div>
                """, unsafe_allow_html=True)
            with col_m2:
                st.markdown(f"""
                | Meta | Atual | Status |
                |------|-------|--------|
                | ≥85% | {ddp['valor']}% | {'✅ Excelente' if ddp['valor'] >= 85 else '⚠️ Atenção' if ddp['valor'] >= 70 else '❌ Crítico'} |
                
                📐 **Fórmula**: Bugs_QA / (Bugs_QA + Bugs_Prod) × 100
                """)
            
            st.markdown("---")
            
            # FPY - First Pass Yield
            st.markdown("##### ✅ FPY - First Pass Yield (Aprovação de Primeira)")
            st.caption("Porcentagem de cards que passam na validação de **primeira**, sem precisar de correções.")
            fpy_cor = 'green' if fpy['valor'] >= 80 else 'yellow' if fpy['valor'] >= 60 else 'orange' if fpy['valor'] >= 40 else 'red'
            
            col_m1, col_m2 = st.columns([2, 3])
            with col_m1:
                st.markdown(f"""
                <div class="status-card status-{fpy_cor}" style="padding: 15px;">
                    <p class="big-number">{fpy['valor']}%</p>
                    <p class="card-label">FPY</p>
                </div>
                """, unsafe_allow_html=True)
            with col_m2:
                st.markdown(f"""
                | Meta | Atual | Status |
                |------|-------|--------|
                | ≥80% | {fpy['valor']}% | {'✅ Excelente' if fpy['valor'] >= 80 else '⚠️ Atenção' if fpy['valor'] >= 60 else '❌ Crítico'} |
                
                📐 **Fórmula**: Cards_Sem_Bug / Total_Cards × 100
                """)
            
            st.markdown("---")
            
            dd = calcular_defect_density(df)
            mttr = calcular_mttr(df)
            
            # Densidade de Defeitos e MTTR lado a lado
            col_dd, col_mttr = st.columns(2)
            
            with col_dd:
                st.markdown("##### 📊 Densidade de Defeitos")
                st.caption("Bugs por Story Point")
                dd_cor = 'green' if dd['valor'] <= 0.2 else 'yellow' if dd['valor'] <= 0.5 else 'red'
                st.markdown(f"""
                <div class="status-card status-{dd_cor}" style="padding: 12px;">
                    <p style="font-size: 24px; font-weight: bold; margin: 0;">{dd['valor']}</p>
                    <p class="card-label">{dd['bugs']} bugs / {dd['sp']} SP</p>
                </div>
                """, unsafe_allow_html=True)
                st.caption("Meta: ≤ 0.2 bugs/SP")
            
            with col_mttr:
                st.markdown("##### ⏱️ MTTR")
                st.caption("Tempo Médio de Correção")
                mttr_cor = 'green' if mttr['valor'] <= 2 else 'yellow' if mttr['valor'] <= 5 else 'red'
                st.markdown(f"""
                <div class="status-card status-{mttr_cor}" style="padding: 12px;">
                    <p style="font-size: 24px; font-weight: bold; margin: 0;">{mttr['valor']} dias</p>
                    <p class="card-label">Mean Time To Repair</p>
                </div>
                """, unsafe_allow_html=True)
                st.caption("Meta: ≤ 2 dias")
        
        with col2:
            st.markdown("#### 🔄 Gargalos Identificados")
            st.caption("Pontos do fluxo onde cards estão acumulando além do tempo esperado")
            
            gargalos = identificar_gargalos(df)
            if gargalos:
                for g in gargalos:
                    emoji = '🔴' if g['impacto'] == 'ALTO' else '🟡'
                    cat_nome = STATUS_NOMES.get(g['categoria'], g['categoria'])
                    
                    with st.expander(f"{emoji} **{cat_nome}**: {g['cards']} cards ({g['atual']} dias vs {g['esperado']} esperado)"):
                        st.caption(f"Impacto: **{g['impacto']}** - Cards parados mais tempo que o esperado")
                        st.markdown("**Cards afetados:**")
                        for ticket in g['tickets'][:5]:
                            st.markdown(f"- [{ticket}]({link_jira(ticket)})")
                        if len(g['tickets']) > 5:
                            st.caption(f"... e mais {len(g['tickets']) - 5} cards")
            else:
                st.success("✅ Nenhum gargalo identificado! O fluxo está saudável.")
            
            st.markdown("---")
            
            # Legenda das métricas
            st.markdown("#### 📖 Guia Rápido das Métricas")
            st.markdown("""
            | Métrica | O que mede | Meta |
            |---------|------------|------|
            | **DDP** | Bugs encontrados antes de produção | ≥ 85% |
            | **FPY** | Cards aprovados de primeira | ≥ 80% |
            | **Densidade** | Bugs por Story Point | ≤ 0.2 |
            | **MTTR** | Tempo para corrigir bugs | ≤ 2 dias |
            """)
    
    # ==== SEÇÃO 4: WIP e Throughput ====
    with st.expander("📈 **Fluxo de Trabalho** - WIP, Vazão e Lead Time", expanded=False):
        st.caption("""
        **WIP (Work In Progress)**: quantidade de trabalho em andamento simultaneamente. Idealmente controlado para evitar sobrecarga.
        **Throughput**: velocidade de entrega (cards/dia). **Lead Time**: tempo total desde a criação até entrega do card.
        """)
        
        wip = calcular_wip(df)
        throughput = calcular_throughput(df)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🔄 WIP (Em Andamento)")
            st.metric("Total em Andamento", wip['total'], help="Cards não finalizados")
            
            # Tabela clara de WIP por etapa
            st.markdown("""
            | Etapa | Cards |
            |-------|-------|
            | 👨‍💻 Desenvolvimento | {} |
            | 🔍 Revisão de Código | {} |
            | 📋 Aguardando QA | {} |
            | 🧪 Em Validação | {} |
            | 🚫 Bloqueado | {} |
            """.format(wip['development'], wip['code_review'], wip['waiting_qa'], wip['testing'], wip['blocked']))
        
        with col2:
            st.markdown("#### ⚡ Vazão (Throughput)")
            st.metric("Cards Concluídos", throughput['cards'], help="Total de cards que chegaram ao status Concluído")
            st.metric("Story Points Entregues", int(throughput['sp']), help="Soma dos SP dos cards concluídos")
            st.metric("Cards/Dia (média)", throughput['por_dia'], help="Velocidade média de conclusão por dia")
        
        with col3:
            st.markdown("#### ⏱️ Lead Time")
            lead = calcular_lead_time(df)
            st.metric("Médio", f"{lead['medio']} dias", help="Tempo médio de conclusão")
            st.metric("P50 (Mediana)", f"{lead['p50']} dias", help="50% dos cards são entregues neste tempo")
            st.metric("P85", f"{lead['p85']} dias", help="85% dos cards são entregues neste tempo")
            st.metric("P95", f"{lead['p95']} dias", help="95% dos cards são entregues neste tempo")
    
    # ==== SEÇÃO 5: Previsões e Tendências ====
    with st.expander("🔮 **Previsões e Recomendações** - Insights para tomada de decisão", expanded=False):
        st.caption("""
        Previsões baseadas na velocidade atual do time e recomendações automáticas para o Tech Lead.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="previsao-card">
                <h4>📅 Previsão de Entrega</h4>
            """, unsafe_allow_html=True)
            
            # Calcular previsão
            cards_restantes = len(df[~df['status_cat'].isin(['done', 'deferred'])])
            velocidade = throughput['por_dia'] if throughput['por_dia'] > 0 else 1
            dias_estimados = cards_restantes / velocidade
            
            data_prevista = datetime.now() + timedelta(days=dias_estimados)
            
            st.metric("Cards Restantes", cards_restantes)
            st.metric("Dias Estimados", f"{dias_estimados:.1f}")
            st.metric("Data Prevista", data_prevista.strftime('%d/%m/%Y'))
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="decisao-card">
                <h4>💡 Recomendações para o Tech Lead</h4>
            """, unsafe_allow_html=True)
            
            recomendacoes = []
            
            fpy = calcular_first_pass_yield(df)
            
            # Gera recomendações baseadas nos dados
            if wip['blocked'] > 0:
                recomendacoes.append(f"🚨 **Prioridade 1**: Resolver {wip['blocked']} card(s) bloqueado(s)")
            
            if wip['waiting_qa'] > 5:
                recomendacoes.append(f"⚠️ **Fila de QA**: {wip['waiting_qa']} cards aguardando - considerar realocar QAs")
            
            if fpy['valor'] < 60:
                recomendacoes.append("📋 **Qualidade**: FPY baixo - revisar critérios de aceite e code review")
            
            if lead['medio'] > 10:
                recomendacoes.append(f"⏱️ **Lead Time**: {lead['medio']} dias - analisar gargalos no fluxo")
            
            # Cards de alta prioridade
            alta_prioridade = df[(df['prioridade'].isin(['Alta', 'Muito Alta', 'Muito alto', 'Alto'])) & 
                                 (df['status_cat'] != 'done')]
            if not alta_prioridade.empty:
                recomendacoes.append(f"🔥 **Alta Prioridade**: {len(alta_prioridade)} card(s) críticos pendentes")
            
            # Verificar janela de validação (se disponível)
            if 'dias_ate_release' in df.columns:
                dias_release = df['dias_ate_release'].iloc[0] if len(df) > 0 else 10
                cards_qa = len(df[df['status_cat'].isin(['waiting_qa', 'testing'])])
                if dias_release <= 3 and cards_qa > 0:
                    recomendacoes.append(f"🕐 **Janela Crítica**: {cards_qa} cards em QA a {dias_release} dias da release")
            
            if not recomendacoes:
                recomendacoes.append("✅ Release em bom estado! Manter monitoramento.")
            
            for r in recomendacoes:
                st.markdown(f"- {r}")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # ==== SEÇÃO 6: Gráficos de Distribuição ====
    with st.expander("📊 **Visão Geral** - Distribuição de cards por status e tipo", expanded=False):
        st.caption("Visão rápida da composição da release atual.")
    
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Distribuição por Status**")
            status_count = df.groupby('status_cat').size().reset_index(name='count')
            status_count['status_nome'] = status_count['status_cat'].map(STATUS_NOMES)
            fig = px.pie(status_count, values='count', names='status_nome', hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**Cards por Tipo**")
            tipo_count = df.groupby('tipo').size().reset_index(name='count')
            fig2 = px.bar(tipo_count, x='tipo', y='count', color='tipo',
                          color_discrete_sequence=px.colors.qualitative.Set2)
            fig2.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20), showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
    
    # ==== SEÇÃO 7: Desenvolvedores - Fator K ====
    with st.expander("👨‍💻 **Performance dos Desenvolvedores** - Fator K e maturidade", expanded=False):
        st.caption("""
        **Fator K** = Story Points / Bugs. Quanto maior, melhor a entrega com qualidade.
        Meta: FK ≥ 2.0 indica entrega madura. Sem SP cadastrado, usa-se taxa de bugs por card.
        """)
    
        devs = [d for d in df['desenvolvedor'].unique() if d != 'Não atribuído']
        dados_dev = []
        
        for dev in devs:
            analise = analisar_dev_detalhado(df, dev)
            if analise:
                # Para o gráfico, usar 0 se FK=-1 (sem SP)
                fk_display = analise['fk_medio'] if analise['fk_medio'] >= 0 else 0
                dados_dev.append({
                    'Desenvolvedor': dev,
                    'Cards': analise['cards'],
                    'SP': analise['sp_total'],
                    'Bugs': int(analise['bugs_total']),
                    'Fator K': fk_display,
                    'FK Real': analise['fk_medio'],
                    'Selo': f"{analise['maturidade']['emoji']} {analise['maturidade']['selo']}"
                })
        
        if dados_dev:
            df_dev = pd.DataFrame(dados_dev).sort_values('Fator K', ascending=False)
            
            # Verificar se há dados de SP
            total_sp = df_dev['SP'].sum()
            
            if total_sp > 0:
                # Mostrar gráfico normal
                fig = px.bar(df_dev, x='Desenvolvedor', y='Fator K', color='Fator K',
                             color_continuous_scale=['#ef4444', '#f97316', '#eab308', '#22c55e'],
                             text='Selo')
                fig.add_hline(y=2, line_dash="dash", annotation_text="Meta FK ≥ 2")
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Mostrar gráfico alternativo por bugs
                st.info("📊 Story Points não cadastrados nos cards. Exibindo ranking por taxa de bugs encontrados.")
                
                df_dev['Taxa de Bugs'] = df_dev.apply(
                    lambda x: round(x['Bugs'] / x['Cards'], 2) if x['Cards'] > 0 else 0, axis=1)
                df_dev = df_dev.sort_values('Taxa de Bugs', ascending=True)
                
                fig = px.bar(df_dev, x='Desenvolvedor', y='Taxa de Bugs', color='Taxa de Bugs',
                             color_continuous_scale=['#22c55e', '#eab308', '#f97316', '#ef4444'],
                             text=df_dev['Bugs'].astype(str) + ' bugs')
                fig.update_layout(height=350, title="Taxa de Bugs por Card (menor = melhor)")
                st.plotly_chart(fig, use_container_width=True)
            
            # Tabela detalhada inline (sem sub-expander)
            st.markdown("**📋 Tabela detalhada:**")
            df_display = df_dev[['Desenvolvedor', 'Cards', 'SP', 'Bugs', 'Selo']].copy()
            if total_sp > 0:
                df_display['Fator K'] = df_dev['Fator K']
            st.dataframe(df_display, hide_index=True, use_container_width=True)
    
    # ==== SEÇÃO 8: Últimos Comentários ====
    with st.expander("💬 **Últimos Comentários** - Atualizações recentes nos cards", expanded=False):
        st.caption("""
        Comentários recentes dos cards podem conter informações importantes sobre bugs, bloqueios ou status de validação.
        """)
        
        # Buscar cards com comentários
        cards_com_comentarios = df[df['num_comentarios'] > 0].sort_values('atualizado', ascending=False)
        
        if not cards_com_comentarios.empty:
            for _, row in cards_com_comentarios.head(8).iterrows():
                comentarios = row.get('comentarios', [])
                if comentarios:
                    ultimo_comentario = comentarios[-1] if isinstance(comentarios, list) else None
                    
                    if ultimo_comentario:
                        # Determinar cor baseado no status
                        status_cor = {
                            'done': '#22c55e',
                            'blocked': '#ef4444',
                            'testing': '#3b82f6',
                            'waiting_qa': '#eab308',
                            'development': '#8b5cf6'
                        }.get(row['status_cat'], '#6b7280')
                        
                        st.markdown(f"""
                        <div class="comment-card" style="border-left: 3px solid {status_cor}; padding-left: 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <a href="{row['link']}" target="_blank" style="color: #6366f1; font-weight: bold; text-decoration: none;">
                                    🔗 {row['ticket_id']}
                                </a>
                                <span style="font-size: 11px; opacity: 0.7;">
                                    {row.get('desenvolvedor', 'N/A')} → {row.get('qa', 'N/A')}
                                </span>
                            </div>
                            <p style="margin: 5px 0; font-size: 13px;"><b>{ultimo_comentario.get('autor', 'Anônimo')}:</b></p>
                            <p style="margin: 0; font-size: 13px; opacity: 0.9;">{ultimo_comentario.get('texto', 'Sem comentário')}</p>
                            <div style="margin-top: 8px; font-size: 11px; opacity: 0.6;">
                                🐛 {int(row['bugs'])} bugs | {int(row['sp'])} SP | Status: {row['status']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown("")  # Espaço entre cards
        else:
            st.info("📝 Nenhum card com comentários encontrado nesta release.")


# ==============================================================================
# ABA DE QA (EXPANDIDA)
# ==============================================================================

def aba_qa(df: pd.DataFrame):
    """Aba de QA - Métricas detalhadas e impacto."""
    
    st.markdown('<div class="section-header"><h2>🧪 Painel de QA</h2></div>', unsafe_allow_html=True)
    
    qas = [q for q in df['qa'].unique() if q != 'Não atribuído']
    
    qa_sel = st.selectbox("👤 Selecione o QA", ["Visão Geral do Time"] + sorted(qas))
    st.session_state.filtro_qa = qa_sel
    
    st.markdown("---")
    
    if qa_sel == "Visão Geral do Time":
        # ==== Impacto do QA no Time ====
        st.markdown("### 🛡️ Impacto do Time de QA")
        
        bugs_total = int(df['bugs'].sum())
        sp_protegidos = df['sp'].sum()
        ddp = calcular_ddp(df)
        fpy = calcular_first_pass_yield(df)
        
        # Contar cards validados (concluídos + em validação)
        cards_validados = len(df[df['status_cat'].isin(['done', 'testing'])])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="impact-card">
                <p style="font-size: 32px; font-weight: bold; color: #22c55e; margin: 0;">🐛 {bugs_total}</p>
                <p style="margin: 5px 0;">Bugs Encontrados</p>
                <p style="font-size: 12px; opacity: 0.7;">Problemas identificados antes de produção</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="impact-card">
                <p style="font-size: 32px; font-weight: bold; color: #3b82f6; margin: 0;">✅ {cards_validados}</p>
                <p style="margin: 5px 0;">Cards Validados</p>
                <p style="font-size: 12px; opacity: 0.7;">Funcionalidades testadas pelo QA</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="impact-card">
                <p style="font-size: 32px; font-weight: bold; color: #8b5cf6; margin: 0;">🎯 {ddp['valor']}%</p>
                <p style="margin: 5px 0;">DDP</p>
                <p style="font-size: 12px; opacity: 0.7;">Taxa de Detecção de Defeitos</p>
            </div>
            """, unsafe_allow_html=True)
            mostrar_tooltip("ddp")
        
        with col4:
            st.markdown(f"""
            <div class="impact-card">
                <p style="font-size: 32px; font-weight: bold; color: #f97316; margin: 0;">⚡ {fpy['valor']}%</p>
                <p style="margin: 5px 0;">FPY</p>
                <p style="font-size: 12px; opacity: 0.7;">Aprovação de Primeira</p>
            </div>
            """, unsafe_allow_html=True)
            mostrar_tooltip("fpy")
        
        st.markdown("---")
        
        # ==== Comparativo entre QAs ====
        st.markdown("### 📊 Performance por QA")
        
        dados_qa = []
        for qa in qas:
            analise = analisar_qa_detalhado(df, qa)
            if analise:
                dados_qa.append({
                    'QA': qa,
                    'Cards': analise['cards_total'],
                    'Validados': analise['validados'],
                    'Em Fila': analise['em_fila'],
                    'Bugs Encontrados': analise['bugs_encontrados'],
                    'FPY': f"{analise['fpy']['valor']}%",
                    'Tempo Médio': f"{analise['tempo_validacao']} dias",
                })
        
        if dados_qa:
            df_qa = pd.DataFrame(dados_qa)
            st.dataframe(df_qa, hide_index=True, use_container_width=True)
        
        st.markdown("---")
        
        # ==== Estatísticas Adicionais do QA ====
        st.markdown("### 📈 Análise Detalhada")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bugs por Tipo de Card
            st.markdown("**🐛 Bugs por Tipo de Card**")
            bugs_por_tipo = df.groupby('tipo')['bugs'].sum().reset_index()
            if not bugs_por_tipo.empty and bugs_por_tipo['bugs'].sum() > 0:
                fig_bugs = px.pie(bugs_por_tipo, values='bugs', names='tipo', hole=0.4,
                                  color_discrete_sequence=px.colors.qualitative.Set2)
                fig_bugs.update_layout(height=250, margin=dict(t=20, b=20, l=20, r=20))
                st.plotly_chart(fig_bugs, use_container_width=True)
            else:
                st.info("Sem bugs registrados por tipo")
        
        with col2:
            # Distribuição de bugs por QA
            st.markdown("**🎯 Bugs Encontrados por QA**")
            bugs_por_qa = df[df['qa'] != 'Não atribuído'].groupby('qa')['bugs'].sum().reset_index()
            if not bugs_por_qa.empty and bugs_por_qa['bugs'].sum() > 0:
                fig_qa_bugs = px.bar(bugs_por_qa.nlargest(5, 'bugs'), x='qa', y='bugs', 
                                     color='bugs', color_continuous_scale=['#22c55e', '#ef4444'])
                fig_qa_bugs.update_layout(height=250, margin=dict(t=20, b=20, l=20, r=20), 
                                          showlegend=False, xaxis_title="", yaxis_title="Bugs")
                st.plotly_chart(fig_qa_bugs, use_container_width=True)
            else:
                st.info("Sem dados de bugs por QA")
        
        # Métricas de tempo
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("**⏱️ Tempo em Validação**")
            em_validacao = df[df['status_cat'].isin(['waiting_qa', 'testing'])]
            if not em_validacao.empty:
                tempo_medio_fila = em_validacao['dias_em_status'].mean()
                st.metric("Tempo Médio na Fila", f"{tempo_medio_fila:.1f} dias")
                st.metric("Máximo na Fila", f"{em_validacao['dias_em_status'].max()} dias")
            else:
                st.info("Sem cards em validação")
        
        with col4:
            st.markdown("**📊 Eficiência do Time**")
            concluidos = df[df['status_cat'] == 'done']
            if not concluidos.empty:
                lead_time_qa = concluidos['lead_time'].mean()
                st.metric("Lead Time Médio", f"{lead_time_qa:.1f} dias")
                # Taxa de retrabalho (cards que voltaram - aproximação por bugs > 0)
                cards_com_bugs = len(concluidos[concluidos['bugs'] > 0])
                taxa_retrabalho = cards_com_bugs / len(concluidos) * 100 if len(concluidos) > 0 else 0
                st.metric("Taxa de Retrabalho", f"{taxa_retrabalho:.1f}%", 
                         help="Cards que precisaram de correção antes de aprovar")
            else:
                st.info("Sem cards concluídos")
        
        st.markdown("---")
        
        # ==== Fila de QA ====
        fila_qa = df[df['status_cat'] == 'waiting_qa']
        
        if not fila_qa.empty:
            st.markdown("### ⏳ Fila de Validação")
            
            c1, c2 = st.columns([1, 2])
            with c1:
                st.metric("Cards na Fila", len(fila_qa))
                st.metric("SP na Fila", fila_qa['sp'].sum())
                
                capacidade = 5 * len(qas) if qas else 5
                dias_estim = fila_qa['sp'].sum() / capacidade
                st.metric("Dias Estimados para Limpar", f"{dias_estim:.1f}")
            
            with c2:
                for _, row in fila_qa.head(5).iterrows():
                    mostrar_card_ticket(row.to_dict(), compacto=True)
                
                if len(fila_qa) > 5:
                    with st.expander(f"Ver mais {len(fila_qa) - 5} cards"):
                        for _, row in fila_qa.iloc[5:].iterrows():
                            mostrar_card_ticket(row.to_dict(), compacto=True)
        else:
            st.success("✅ Fila de QA vazia! Todos os cards foram validados.")
        
        st.markdown("---")
        
        # ==== NOVA SEÇÃO: Janela de Validação vs Dias até Release ====
        st.markdown("### ⏱️ Análise de Janela de Validação")
        st.caption("""
        **Janela de Validação**: Tempo que os cards ficam esperando/em validação comparado aos dias restantes para a release.
        Segundo as métricas da NINA, cards devem ser testados **até 3 dias úteis antes da release** para garantir estabilidade.
        """)
        
        # Verificar se o campo existe no DataFrame
        if 'dias_ate_release' in df.columns and 'tempo_em_qa' in df.columns:
            col_jan1, col_jan2 = st.columns(2)
            
            with col_jan1:
                # Cards dentro e fora da janela
                cards_na_fila = df[df['status_cat'].isin(['waiting_qa', 'testing'])]
                
                if not cards_na_fila.empty and 'dentro_janela' in df.columns:
                    dentro = len(cards_na_fila[cards_na_fila['dentro_janela'] == True])
                    fora = len(cards_na_fila) - dentro
                    
                    st.markdown("**📊 Status da Janela de Validação**")
                    
                    if dentro > 0:
                        st.warning(f"⚠️ **{dentro} card(s)** estão dentro da janela crítica (≤3 dias até release)")
                    
                    # Métricas de tempo
                    dias_release = df['dias_ate_release'].iloc[0] if 'dias_ate_release' in df.columns else 10
                    tempo_medio_qa = cards_na_fila['tempo_em_qa'].mean() if 'tempo_em_qa' in df.columns else 0
                    
                    st.metric("Dias até a Release", f"{dias_release} dias", 
                             help="Dias restantes até a data planejada da release")
                    st.metric("Tempo Médio em QA", f"{tempo_medio_qa:.1f} dias",
                             help="Tempo médio que os cards ficam no fluxo de QA")
                    
                    # Capacidade vs Demanda
                    cards_pendentes = len(df[df['status_cat'].isin(['waiting_qa', 'testing'])])
                    capacidade_diaria = max(1, len(qas) * 2)  # ~2 cards/QA/dia
                    dias_necessarios = cards_pendentes / capacidade_diaria
                    
                    st.metric("Cards em Análise/Fila", cards_pendentes)
                    st.metric("Dias Necessários para Validar", f"{dias_necessarios:.1f}",
                             delta=f"{dias_release - dias_necessarios:.1f} dias de folga" if dias_release > dias_necessarios else f"{dias_necessarios - dias_release:.1f} dias de atraso",
                             delta_color="normal" if dias_release > dias_necessarios else "inverse")
                else:
                    st.info("Nenhum card aguardando validação")
            
            with col_jan2:
                st.markdown("**📈 Detalhamento por Desenvolvedor**")
                st.caption("Tempo desde que o Dev enviou para validação até agora")
                
                # Agrupar por desenvolvedor e calcular tempo médio em QA
                cards_qa = df[df['status_cat'].isin(['waiting_qa', 'testing', 'done'])]
                
                if not cards_qa.empty and 'tempo_em_qa' in df.columns:
                    tempo_por_dev = cards_qa.groupby('desenvolvedor').agg({
                        'tempo_em_qa': 'mean',
                        'ticket_id': 'count',
                        'bugs': 'sum'
                    }).reset_index()
                    tempo_por_dev.columns = ['Desenvolvedor', 'Tempo Médio QA', 'Cards', 'Bugs']
                    tempo_por_dev['Tempo Médio QA'] = tempo_por_dev['Tempo Médio QA'].round(1)
                    tempo_por_dev = tempo_por_dev.sort_values('Tempo Médio QA', ascending=False)
                    
                    # Gráfico horizontal
                    fig = px.bar(tempo_por_dev.head(6), 
                                 x='Tempo Médio QA', 
                                 y='Desenvolvedor', 
                                 orientation='h',
                                 color='Tempo Médio QA',
                                 color_continuous_scale=['#22c55e', '#eab308', '#ef4444'],
                                 text='Tempo Médio QA')
                    fig.update_layout(height=250, margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
                    fig.update_traces(texttemplate='%{text} dias', textposition='inside')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.caption("💡 Cards com tempo maior em QA podem indicar complexidade alta ou dependência de correções")
                else:
                    st.info("Dados de tempo em QA não disponíveis")
        else:
            st.info("📊 Dados de janela de validação serão carregados quando conectado ao Jira")
        
        st.markdown("---")
        
        # ==== NOVA SEÇÃO: Impacto do FK na Validação ====
        st.markdown("### 📊 Relação Fator K × Carga de Trabalho do QA")
        st.caption("""
        O **Fator K** dos desenvolvedores impacta diretamente o trabalho do QA. Devs com FK baixo tendem a gerar mais bugs,
        aumentando o tempo de validação e retrabalho.
        """)
        
        col_rel1, col_rel2 = st.columns(2)
        
        with col_rel1:
            st.markdown("**🎯 Devs que mais geraram retrabalho para o QA**")
            
            # Agrupar por dev e calcular FK + bugs
            dev_impacto = df[df['desenvolvedor'] != 'Não atribuído'].groupby('desenvolvedor').agg({
                'bugs': 'sum',
                'sp': 'sum',
                'ticket_id': 'count'
            }).reset_index()
            
            dev_impacto['FK'] = dev_impacto.apply(
                lambda x: round((x['sp'] / (x['bugs'] + 1)) * 1.5, 1) if x['sp'] > 0 else 0, axis=1)
            dev_impacto['Bugs'] = dev_impacto['bugs'].astype(int)
            dev_impacto = dev_impacto[dev_impacto['bugs'] > 0].sort_values('bugs', ascending=False)
            
            if not dev_impacto.empty:
                for _, row in dev_impacto.head(5).iterrows():
                    cor = '#ef4444' if row['FK'] < 2 else '#eab308' if row['FK'] < 3 else '#22c55e'
                    st.markdown(f"""
                    <div style="background: rgba(100,100,100,0.05); padding: 10px; border-radius: 8px; margin: 5px 0; border-left: 3px solid {cor};">
                        <b>{row['desenvolvedor']}</b><br>
                        <span style="font-size: 12px;">🐛 {row['Bugs']} bugs | FK: {row['FK']} | {row['ticket_id']} cards</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ Nenhum dev gerou bugs significativos nesta release!")
        
        with col_rel2:
            st.markdown("**💡 Recomendações para o QA**")
            
            # Gerar recomendações baseadas nos dados
            recomendacoes_qa = []
            
            fpy = calcular_first_pass_yield(df)
            if fpy['valor'] < 60:
                recomendacoes_qa.append("📋 FPY baixo indica que muitos cards voltam - considerar definir checklists de aceite mais claros")
            
            cards_alta_bugs = df[df['bugs'] >= 3]
            if not cards_alta_bugs.empty:
                devs_problematicos = cards_alta_bugs['desenvolvedor'].value_counts().head(2)
                for dev, count in devs_problematicos.items():
                    recomendacoes_qa.append(f"🔍 Atenção extra para cards de **{dev}** ({count} cards com 3+ bugs)")
            
            tipo_mais_bugs = df.groupby('tipo')['bugs'].sum().idxmax() if df['bugs'].sum() > 0 else None
            if tipo_mais_bugs:
                recomendacoes_qa.append(f"🎯 Foco em cards do tipo **{tipo_mais_bugs}** - maior incidência de bugs")
            
            if not recomendacoes_qa:
                recomendacoes_qa.append("✅ A qualidade das entregas está boa! Manter padrão de validação.")
            
            for rec in recomendacoes_qa:
                st.markdown(f"- {rec}")
    
    else:
        # ==== Métricas individuais do QA (TERCEIRA PESSOA) ====
        analise = analisar_qa_detalhado(df, qa_sel)
        
        if analise:
            st.markdown(f"### 👤 Métricas de {qa_sel}")
            
            # Métricas principais
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                st.metric("Cards Atribuídos", analise['cards_total'])
            with c2:
                st.metric("Cards Validados", analise['validados'])
            with c3:
                st.metric("Bugs Encontrados", analise['bugs_encontrados'])
            with c4:
                st.metric("FPY", f"{analise['fpy']['valor']}%")
            with c5:
                st.metric("Tempo Médio", f"{analise['tempo_validacao']} dias")
            
            st.markdown("---")
            
            # Impacto (TERCEIRA PESSOA)
            st.markdown(f"### 🛡️ Impacto de {qa_sel}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="impact-card">
                    <h4>Bugs Evitados em Produção</h4>
                    <p style="font-size: 28px; font-weight: bold; color: #22c55e;">{analise['bugs_evitados']} bugs</p>
                    <p>{qa_sel} protegeu <b>{analise['sp_protegidos']} Story Points</b> de funcionalidades</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                ddp_cor = 'green' if analise['ddp']['status'] in ['excellent', 'good'] else 'yellow'
                st.markdown(f"""
                <div class="status-card status-{ddp_cor}">
                    <p class="big-number">{analise['ddp']['valor']}%</p>
                    <p class="card-label">Taxa de Detecção (DDP)</p>
                    <p class="metric-info">Eficácia de {qa_sel.split()[0]} em encontrar bugs</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Cards problemáticos (TERCEIRA PESSOA)
            if not analise['cards_problematicos'].empty:
                st.markdown(f"### 🔴 Cards mais Problemáticos de {qa_sel}")
                st.caption("Cards com 3+ bugs - podem indicar problemas de especificação ou alta complexidade")
                
                for _, row in analise['cards_problematicos'].head(5).iterrows():
                    st.markdown(f"""
                    <div class="problematic-card">
                        <div style="display: flex; justify-content: space-between;">
                            <a href="{row['link']}" target="_blank" style="color: #6366f1; font-weight: bold; text-decoration: none;">🔗 {row['ticket_id']}</a>
                            <span style="color: #ef4444; font-weight: bold;">🐛 {row['bugs']} bugs</span>
                        </div>
                        <p style="margin: 6px 0; opacity: 0.85;">{row['titulo'][:60]}...</p>
                        <p style="font-size: 12px; opacity: 0.7;">Complexidade: {row['complexidade']} | Dev: {row['desenvolvedor']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Tempo de validação (TERCEIRA PESSOA)
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"### ⚡ Cards mais Rápidos de {qa_sel.split()[0]}")
                if not analise['mais_rapido'].empty:
                    for _, row in analise['mais_rapido'].iterrows():
                        st.markdown(f"- [{row['ticket_id']}]({row['link']}) - **{row['lead_time']} dias** ({row['bugs']} bugs)")
                else:
                    st.info("Ainda sem dados suficientes")
            
            with col2:
                st.markdown(f"### 🐢 Cards mais Demorados de {qa_sel.split()[0]}")
                if not analise['mais_lento'].empty:
                    for _, row in analise['mais_lento'].iterrows():
                        st.markdown(f"- [{row['ticket_id']}]({row['link']}) - **{row['lead_time']} dias** ({row['bugs']} bugs)")
                else:
                    st.info("Ainda sem dados suficientes")
            
            st.markdown("---")
            
            # Por complexidade
            if analise['por_complexidade']:
                st.markdown(f"### 📈 Performance por Complexidade de {qa_sel.split()[0]}")
                
                dados_comp = [{'Complexidade': k, 'Cards': v['ticket_id'], 'Bugs': v['bugs'], 'Tempo Médio': v['lead_time']} 
                              for k, v in analise['por_complexidade'].items() if k != 'N/A']
                
                if dados_comp:
                    df_comp = pd.DataFrame(dados_comp)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        fig = px.bar(df_comp, x='Complexidade', y=['Cards', 'Bugs'], barmode='group',
                                    title='Cards e Bugs por Complexidade')
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        fig2 = px.bar(df_comp, x='Complexidade', y='Tempo Médio', 
                                     title='Tempo Médio por Complexidade (dias)')
                        st.plotly_chart(fig2, use_container_width=True)
            
            st.markdown("---")
            
            # Todos os cards (TERCEIRA PESSOA)
            st.markdown(f"### 📋 Todos os Cards de {qa_sel}")
            
            for _, row in analise['df'].iterrows():
                with st.expander(f"🔗 {row['ticket_id']} - {row['titulo'][:40]}... ({row['bugs']} bugs)"):
                    mostrar_card_ticket(row.to_dict(), mostrar_qa=False)
                    
                    if row['comentarios']:
                        st.markdown("**💬 Últimos Comentários:**")
                        mostrar_comentarios(row['comentarios'])


# ==============================================================================
# ABA DE DEV
# ==============================================================================

def aba_dev(df: pd.DataFrame):
    """Aba de Dev - Performance e análise."""
    
    st.markdown('<div class="section-header"><h2>👨‍💻 Painel de Desenvolvimento</h2></div>', unsafe_allow_html=True)
    
    devs = [d for d in df['desenvolvedor'].unique() if d != 'Não atribuído']
    
    dev_sel = st.selectbox("👤 Selecione o Desenvolvedor", ["Ranking Geral"] + sorted(devs))
    st.session_state.filtro_dev = dev_sel
    
    st.markdown("---")
    
    if dev_sel == "Ranking Geral":
        # Card explicativo sobre Fator K
        st.markdown("""
        <div class="metric-explain-card">
        <h4>📐 Como é calculada a Maturidade de Entrega (Fator K)?</h4>
        <p>O <b>Fator K</b> mede a qualidade da entrega do desenvolvedor, considerando o esforço planejado (Story Points) 
        e os bugs encontrados pelo QA. É aplicado um <b>rigor de 1.5</b> para todas as releases.</p>
        <div class="formula">FK = (Story Points / (Bugs + 1)) × 1.5</div>
        <p><b>Exemplo:</b> Um dev com 13 SP e 2 bugs terá FK = (13 / 3) × 1.5 = <b>6.5</b> (Excelente!)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🏆 Ranking de Performance")
        
        col_fk, col_info = st.columns([10, 1])
        with col_info:
            mostrar_tooltip("fator_k")
        
        dados_dev = []
        for dev in devs:
            analise = analisar_dev_detalhado(df, dev)
            if analise:
                dados_dev.append({
                    'Desenvolvedor': dev,
                    'Cards': analise['cards'],
                    'SP': analise['sp_total'],
                    'Bugs': int(analise['bugs_total']),
                    'Fator K': analise['fk_medio'],
                    'FPY': f"{analise['zero_bugs']}%",
                    'Tempo Médio': f"{analise['tempo_medio']} dias",
                    'Selo': f"{analise['maturidade']['emoji']} {analise['maturidade']['selo']}"
                })
        
        df_rank = pd.DataFrame(dados_dev)
        df_rank = df_rank.sort_values('Fator K', ascending=False)
        
        st.dataframe(df_rank, hide_index=True, use_container_width=True)
        
        # Gráfico
        fig = px.bar(df_rank, x='Desenvolvedor', y='Fator K',
                     color='Fator K',
                     color_continuous_scale=['#ef4444', '#f97316', '#eab308', '#22c55e'],
                     text='Selo')
        fig.add_hline(y=2, line_dash="dash", annotation_text="Meta (FK ≥ 2)")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Devs que precisam de suporte (somente quem tem bugs E dados de SP)
        # Não incluir quem tem FK=-1 (sem SP) ou quem tem 0 bugs
        devs_atencao = [d for d in dados_dev 
                       if d['Fator K'] >= 0 and d['Fator K'] < 2 and d['Bugs'] > 0]
        if devs_atencao:
            st.markdown("### ⚠️ Desenvolvedores que Precisam de Atenção")
            st.caption("Fator K abaixo de 2 com bugs encontrados - podem se beneficiar de code review mais rigoroso")
            
            for d in devs_atencao:
                df_dev_filter = df[df['desenvolvedor'] == d['Desenvolvedor']]
                cards_problematicos = df_dev_filter[df_dev_filter['bugs'] >= 2].head(3)
                
                with st.expander(f"⚠️ {d['Desenvolvedor']} - FK: {d['Fator K']} | {d['Bugs']} bugs em {d['Cards']} cards"):
                    if not cards_problematicos.empty:
                        st.markdown("**Cards com mais bugs:**")
                        for _, row in cards_problematicos.iterrows():
                            st.markdown(f"- [{row['ticket_id']}]({row['link']}) - {row['bugs']} bugs - {row['titulo'][:40]}...")
        
        st.markdown("---")
        
        # ==== Estatísticas Adicionais de Desenvolvimento ====
        st.markdown("### 📊 Análise do Time de Desenvolvimento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribuição de cards por desenvolvedor
            st.markdown("**📋 Cards por Desenvolvedor**")
            cards_por_dev = df[df['desenvolvedor'] != 'Não atribuído'].groupby('desenvolvedor').size().reset_index(name='cards')
            if not cards_por_dev.empty:
                cards_por_dev = cards_por_dev.nlargest(8, 'cards')
                fig_cards = px.bar(cards_por_dev, x='desenvolvedor', y='cards', 
                                   color='cards', color_continuous_scale='Blues')
                fig_cards.update_layout(height=250, margin=dict(t=20, b=20, l=20, r=20), 
                                        showlegend=False, xaxis_title="", yaxis_title="Cards")
                st.plotly_chart(fig_cards, use_container_width=True)
            else:
                st.info("Sem dados de cards por desenvolvedor")
        
        with col2:
            # Taxa de bugs por desenvolvedor (bugs/card)
            st.markdown("**🐛 Taxa de Bugs por Card**")
            taxa_bugs = df[df['desenvolvedor'] != 'Não atribuído'].groupby('desenvolvedor').agg({
                'bugs': 'sum', 'ticket_id': 'count'
            }).reset_index()
            taxa_bugs['taxa'] = (taxa_bugs['bugs'] / taxa_bugs['ticket_id']).round(2)
            taxa_bugs = taxa_bugs.nlargest(8, 'taxa')
            
            if not taxa_bugs.empty and taxa_bugs['taxa'].sum() > 0:
                fig_taxa = px.bar(taxa_bugs, x='desenvolvedor', y='taxa', 
                                  color='taxa', color_continuous_scale=['#22c55e', '#eab308', '#ef4444'])
                fig_taxa.update_layout(height=250, margin=dict(t=20, b=20, l=20, r=20), 
                                       showlegend=False, xaxis_title="", yaxis_title="Bugs/Card")
                st.plotly_chart(fig_taxa, use_container_width=True)
            else:
                st.success("✅ Sem bugs registrados!")
        
        # Métricas gerais do time
        col3, col4, col5 = st.columns(3)
        
        with col3:
            st.metric("Total de Cards", len(df))
            em_andamento = len(df[df['status_cat'] == 'development'])
            st.metric("Em Desenvolvimento", em_andamento)
        
        with col4:
            total_bugs = df['bugs'].sum()
            st.metric("Total de Bugs", int(total_bugs))
            media_bugs = total_bugs / len(df) if len(df) > 0 else 0
            st.metric("Média de Bugs/Card", f"{media_bugs:.2f}")
        
        with col5:
            # Cards sem bugs (qualidade)
            cards_zero_bugs = len(df[df['bugs'] == 0])
            pct_zero_bugs = cards_zero_bugs / len(df) * 100 if len(df) > 0 else 0
            st.metric("Cards sem Bugs", f"{cards_zero_bugs} ({pct_zero_bugs:.0f}%)")
            # Tempo médio de desenvolvimento
            lead_medio = df['lead_time'].mean() if not df.empty else 0
            st.metric("Lead Time Médio", f"{lead_medio:.1f} dias")
        
        st.markdown("---")
        
        # ==== NOVOS CARDS PARA TECH LEAD ====
        st.markdown("### 🎯 Análise para Tech Lead")
        st.caption("Métricas avançadas para tomada de decisão")
        
        col_tl1, col_tl2 = st.columns(2)
        
        with col_tl1:
            # Distribuição de complexidade (SP) por Dev
            st.markdown("**📊 Distribuição de Story Points por Dev**")
            st.caption("Quem está assumindo mais complexidade")
            sp_por_dev = df[df['desenvolvedor'] != 'Não atribuído'].groupby('desenvolvedor')['sp'].sum().reset_index()
            sp_por_dev = sp_por_dev.sort_values('sp', ascending=False).head(8)
            
            if not sp_por_dev.empty and sp_por_dev['sp'].sum() > 0:
                fig_sp = px.pie(sp_por_dev, names='desenvolvedor', values='sp', 
                               color_discrete_sequence=px.colors.sequential.RdBu)
                fig_sp.update_layout(height=250, margin=dict(t=20, b=20, l=20, r=20))
                fig_sp.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_sp, use_container_width=True)
            else:
                st.info("Sem dados de SP")
        
        with col_tl2:
            # Throughput: Cards concluídos vs em andamento por dev
            st.markdown("**🚀 Status de Entrega por Dev**")
            st.caption("Progresso: Concluído vs Em andamento")
            
            status_dev = df[df['desenvolvedor'] != 'Não atribuído'].groupby('desenvolvedor').apply(
                lambda x: pd.Series({
                    'Concluídos': len(x[x['status_cat'] == 'done']),
                    'Em Andamento': len(x[x['status_cat'].isin(['development', 'code_review', 'testing', 'waiting_qa'])])
                })
            ).reset_index()
            
            if not status_dev.empty:
                status_dev = status_dev.head(8)
                fig_status = px.bar(status_dev, x='desenvolvedor', y=['Concluídos', 'Em Andamento'],
                                    barmode='stack', 
                                    color_discrete_map={'Concluídos': '#22c55e', 'Em Andamento': '#3b82f6'})
                fig_status.update_layout(height=250, margin=dict(t=20, b=20, l=20, r=20),
                                         xaxis_title="", legend=dict(orientation="h", y=1.1))
                st.plotly_chart(fig_status, use_container_width=True)
        
        # WIP Analysis e Code Review
        col_tl3, col_tl4 = st.columns(2)
        
        with col_tl3:
            st.markdown("**⏳ Work-In-Progress (WIP) por Dev**")
            st.caption("Quantos cards cada dev está trabalhando agora")
            
            wip_devs = df[(df['desenvolvedor'] != 'Não atribuído') & 
                          (df['status_cat'].isin(['development', 'code_review']))].groupby('desenvolvedor').size().reset_index(name='WIP')
            wip_devs = wip_devs.sort_values('WIP', ascending=False)
            
            if not wip_devs.empty:
                # Colorir por WIP (vermelho se > 3)
                wip_devs['Cor'] = wip_devs['WIP'].apply(lambda x: '#ef4444' if x > 3 else '#22c55e' if x <= 2 else '#eab308')
                
                fig_wip = px.bar(wip_devs, x='desenvolvedor', y='WIP', 
                                 color='WIP', color_continuous_scale=['#22c55e', '#eab308', '#ef4444'],
                                 text='WIP')
                fig_wip.add_hline(y=3, line_dash="dash", annotation_text="WIP Ideal ≤ 3", line_color="#eab308")
                fig_wip.update_layout(height=250, margin=dict(t=30, b=20, l=20, r=20), showlegend=False, xaxis_title="")
                fig_wip.update_traces(textposition='outside')
                st.plotly_chart(fig_wip, use_container_width=True)
            else:
                st.success("✅ Nenhum dev com WIP no momento")
        
        with col_tl4:
            st.markdown("**🔍 Fila de Code Review**")
            st.caption("Cards aguardando revisão de código")
            
            code_review = df[df['status_cat'] == 'code_review']
            
            if not code_review.empty:
                for _, row in code_review.head(5).iterrows():
                    dias = row['dias_em_status']
                    cor = '#ef4444' if dias > 3 else '#eab308' if dias > 1 else '#22c55e'
                    st.markdown(f"""
                    <div style="padding: 8px; margin: 4px 0; border-left: 3px solid {cor}; background: rgba(99, 102, 241, 0.1); border-radius: 4px;">
                        <strong><a href="{row['link']}" style="color: #60a5fa;">{row['ticket_id']}</a></strong> - {row['titulo'][:35]}...<br>
                        <small style="color: #94a3b8;">📅 {dias} dia(s) em CR | 👤 {row['desenvolvedor']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                if len(code_review) > 5:
                    st.caption(f"... e mais {len(code_review) - 5} cards em Code Review")
            else:
                st.success("✅ Nenhum card aguardando Code Review")
        
        # Velocidade e Tempo em Status
        col_tl5, col_tl6 = st.columns(2)
        
        with col_tl5:
            st.markdown("**📈 Velocidade do Time (SP/Card)**")
            st.caption("Eficiência: média de Story Points por card entregue")
            
            cards_done = df[df['status_cat'] == 'done']
            if not cards_done.empty:
                vel_dev = cards_done.groupby('desenvolvedor').agg({
                    'sp': ['sum', 'count']
                })
                vel_dev.columns = ['SP Total', 'Cards']
                vel_dev['SP/Card'] = (vel_dev['SP Total'] / vel_dev['Cards']).round(1)
                vel_dev = vel_dev.reset_index().sort_values('SP/Card', ascending=False).head(6)
                
                fig_vel = px.bar(vel_dev, x='desenvolvedor', y='SP/Card',
                                 color='SP/Card', color_continuous_scale=['#f97316', '#22c55e'],
                                 text='SP/Card')
                fig_vel.add_hline(y=vel_dev['SP/Card'].mean(), line_dash="dash", annotation_text=f"Média: {vel_dev['SP/Card'].mean():.1f}")
                fig_vel.update_layout(height=250, margin=dict(t=30, b=20, l=20, r=20), showlegend=False, xaxis_title="")
                fig_vel.update_traces(textposition='outside')
                st.plotly_chart(fig_vel, use_container_width=True)
            else:
                st.info("Sem cards concluídos para análise")
        
        with col_tl6:
            st.markdown("**🔴 Cards Críticos (Alta Prioridade em Dev)**")
            st.caption("Cards urgentes ainda em desenvolvimento")
            
            criticos_dev = df[(df['prioridade'].isin(['Alta', 'Muito Alta', 'Muito alto', 'Alto'])) & 
                              (df['status_cat'].isin(['development', 'code_review', 'backlog']))]
            
            if not criticos_dev.empty:
                for _, row in criticos_dev.head(5).iterrows():
                    st.markdown(f"""
                    <div style="padding: 8px; margin: 4px 0; border-left: 3px solid #ef4444; background: rgba(239, 68, 68, 0.1); border-radius: 4px;">
                        <strong><a href="{row['link']}" style="color: #f87171;">{row['ticket_id']}</a></strong> - {row['titulo'][:35]}...<br>
                        <small style="color: #fca5a5;">⚠️ {row['prioridade']} | 👤 {row['desenvolvedor']} | {row['sp']} SP</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                if len(criticos_dev) > 5:
                    st.warning(f"⚠️ {len(criticos_dev)} cards de alta prioridade ainda em desenvolvimento!")
            else:
                st.success("✅ Nenhum card crítico pendente")
    
    else:
        # Métricas individuais (TERCEIRA PESSOA)
        analise = analisar_dev_detalhado(df, dev_sel)
        
        if analise:
            st.markdown(f"### 👤 Métricas de {dev_sel}")
            
            # Selo de maturidade
            mat = analise['maturidade']
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown(f"""
                <div class="status-card" style="background: {mat['cor']}20; border-color: {mat['cor']}; padding: 20px;">
                    <p style="font-size: 48px; margin: 0;">{mat['emoji']}</p>
                    <p style="font-size: 20px; font-weight: bold; margin: 5px 0;">{mat['selo']}</p>
                    <p style="font-size: 14px; opacity: 0.8;">{mat['desc']}</p>
                    <p style="font-size: 24px; font-weight: bold; margin-top: 10px;">FK: {analise['fk_medio']}</p>
                </div>
                """, unsafe_allow_html=True)
                mostrar_tooltip("fator_k")
            
            with col2:
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("Cards Desenvolvidos", analise['cards'])
                with c2:
                    st.metric("Story Points", analise['sp_total'])
                with c3:
                    st.metric("Bugs Encontrados", analise['bugs_total'])
                with c4:
                    st.metric("Taxa Zero Bugs", f"{analise['zero_bugs']}%")
            
            st.markdown("---")
            
            # Cards do dev (TERCEIRA PESSOA)
            st.markdown(f"### 📋 Cards de {dev_sel}")
            
            for _, row in analise['df'].iterrows():
                with st.expander(f"🔗 {row['ticket_id']} - {row['titulo'][:40]}... ({row['bugs']} bugs)"):
                    mostrar_card_ticket(row.to_dict())
                    
                    if row['comentarios']:
                        st.markdown("**💬 Últimos Comentários:**")
                        mostrar_comentarios(row['comentarios'])


# ==============================================================================
# ABA DE HISTÓRICO
# ==============================================================================

def aba_historico():
    """Aba de Histórico - Tendências e Evolução de Qualidade Completa."""
    
    # Pegar release atual do session_state
    release_atual = st.session_state.get('release_atual', 'Release 238')
    
    st.markdown('<div class="section-header"><h2>📜 Histórico e Evolução de Qualidade</h2></div>', unsafe_allow_html=True)
    
    st.info(f"📊 Acompanhe a evolução das métricas de qualidade. **{release_atual}** (atual) em destaque.")
    
    # Dados mock de histórico (releases 233 a 238, sendo 238 a atual)
    releases = [f"Release {i}" for i in range(233, 239)]
    
    dados_hist = {
        'Release': releases,
        'Cards Concluídos': [45, 52, 48, 55, 51, 58],
        'Story Points': [180, 210, 195, 220, 205, 235],
        'Bugs Encontrados': [12, 15, 10, 18, 14, 11],
        'Bugs Produção': [2, 4, 1, 5, 3, 1],
        'Hotfixes': [3, 5, 2, 4, 3, 2],
        'Taxa Retrabalho (%)': [18, 22, 15, 25, 19, 14],
        'FPY (%)': [72, 68, 75, 65, 71, 78],
        'DDP (%)': [82, 78, 85, 75, 80, 88],
        'Lead Time (dias)': [9, 10, 8, 10, 8, 7],
        'MTTR (horas)': [24, 32, 18, 36, 22, 16],
        'Cobertura Testes (%)': [65, 62, 70, 58, 68, 75],
    }
    
    df_hist = pd.DataFrame(dados_hist)
    
    # ==== Seção 1: Métricas da Release Atual ====
    st.markdown(f"### 📦 {release_atual} (Atual)")
    
    release_idx = -1  # Última release
    
    col_m1, col_m2, col_m3, col_m4, col_m5, col_m6 = st.columns(6)
    
    with col_m1:
        val = df_hist['Cards Concluídos'].iloc[release_idx]
        delta = val - df_hist['Cards Concluídos'].iloc[release_idx - 1]
        st.metric("Cards", val, f"{delta:+d}")
    
    with col_m2:
        val = df_hist['Story Points'].iloc[release_idx]
        delta = val - df_hist['Story Points'].iloc[release_idx - 1]
        st.metric("Story Points", val, f"{delta:+d}")
    
    with col_m3:
        val = df_hist['Bugs Encontrados'].iloc[release_idx]
        delta = val - df_hist['Bugs Encontrados'].iloc[release_idx - 1]
        st.metric("Bugs QA", val, f"{delta:+d}", delta_color="inverse")
    
    with col_m4:
        val = df_hist['FPY (%)'].iloc[release_idx]
        delta = val - df_hist['FPY (%)'].iloc[release_idx - 1]
        st.metric("FPY", f"{val}%", f"{delta:+.0f}%")
    
    with col_m5:
        val = df_hist['DDP (%)'].iloc[release_idx]
        delta = val - df_hist['DDP (%)'].iloc[release_idx - 1]
        st.metric("DDP", f"{val}%", f"{delta:+.0f}%")
    
    with col_m6:
        val = df_hist['Lead Time (dias)'].iloc[release_idx]
        delta = val - df_hist['Lead Time (dias)'].iloc[release_idx - 1]
        st.metric("Lead Time", f"{val}d", f"{delta:+.0f}d", delta_color="inverse")
    
    st.markdown("---")
    
    # ==== Seção 2: Evolução de Qualidade (FPY, DDP, Cobertura) ====
    st.markdown("### 📈 Evolução da Qualidade")
    
    # AVISO: Dados históricos simulados
    st.warning("⚠️ **Dados Simulados**: As métricas de histórico abaixo são para demonstração. Para dados reais, integre com pipelines CI/CD ou colete manualmente ao final de cada release.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.line(df_hist, x='Release', y=['FPY (%)', 'DDP (%)'],
                       title='Qualidade: FPY e DDP por Release (Simulado)',
                       markers=True,
                       color_discrete_sequence=['#22c55e', '#3b82f6'])
        fig1.add_hline(y=70, line_dash="dash", annotation_text="Meta FPY ≥ 70%", line_color="#22c55e")
        fig1.add_hline(y=85, line_dash="dash", annotation_text="Meta DDP ≥ 85%", line_color="#3b82f6")
        fig1.update_layout(height=320, legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.caption("💡 *Cobertura de Testes*: Requer integração com CI/CD (SonarQube, Codecov, etc.)")
        fig2 = px.area(df_hist, x='Release', y='Cobertura Testes (%)',
                       title='Cobertura de Testes Automatizados (Simulado)',
                       color_discrete_sequence=['#8b5cf6'])
        fig2.add_hline(y=70, line_dash="dash", annotation_text="Meta ≥ 70%", line_color="#22c55e")
        fig2.update_layout(height=300)
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("---")
    
    # ==== Seção 3: Bugs e Defeitos ====
    st.markdown("### 🐛 Evolução de Bugs e Defeitos")
    
    col3, col4 = st.columns(2)
    
    with col3:
        fig3 = px.bar(df_hist, x='Release', y=['Bugs Encontrados', 'Bugs Produção', 'Hotfixes'],
                      title='Bugs por Release (QA vs Produção vs Hotfixes)',
                      barmode='group',
                      color_discrete_sequence=['#f97316', '#ef4444', '#dc2626'])
        fig3.update_layout(height=300, legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig3, use_container_width=True)
    
    with col4:
        # Densidade de bugs e taxa de escape
        df_hist['Densidade Bugs'] = (df_hist['Bugs Encontrados'] / df_hist['Cards Concluídos']).round(2)
        df_hist['Taxa Escape (%)'] = ((df_hist['Bugs Produção'] / (df_hist['Bugs Encontrados'] + df_hist['Bugs Produção'])) * 100).round(1)
        
        fig4 = px.line(df_hist, x='Release', y=['Densidade Bugs', 'Taxa Escape (%)'],
                       title='Densidade de Bugs e Taxa de Escape',
                       markers=True,
                       color_discrete_sequence=['#8b5cf6', '#ef4444'])
        fig4.add_hline(y=0.25, line_dash="dash", annotation_text="Meta Densidade ≤ 0.25", line_color="#22c55e")
        fig4.add_hline(y=10, line_dash="dash", annotation_text="Meta Escape ≤ 10%", line_color="#f97316")
        fig4.update_layout(height=300, legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig4, use_container_width=True)
    
    st.markdown("---")
    
    # ==== Seção 4: Produtividade e Lead Time ====
    st.markdown("### ⏱️ Produtividade e Tempo de Entrega")
    
    col5, col6 = st.columns(2)
    
    with col5:
        fig5 = px.bar(df_hist, x='Release', y=['Cards Concluídos', 'Story Points'],
                      title='Produtividade por Release',
                      barmode='group',
                      color_discrete_sequence=['#3b82f6', '#22c55e'])
        fig5.update_layout(height=300, legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig5, use_container_width=True)
    
    with col6:
        fig6 = px.line(df_hist, x='Release', y=['Lead Time (dias)', 'MTTR (horas)'],
                       title='Lead Time e MTTR por Release',
                       markers=True,
                       color_discrete_sequence=['#6366f1', '#f97316'])
        fig6.add_hline(y=7, line_dash="dash", annotation_text="Meta Lead Time ≤ 7d", line_color="#22c55e")
        fig6.update_layout(height=300, legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig6, use_container_width=True)
    
    st.markdown("---")
    
    # ==== Seção 5: Taxa de Retrabalho ====
    st.markdown("### 🔄 Taxa de Retrabalho")
    
    col7, col8 = st.columns(2)
    
    with col7:
        fig7 = px.line(df_hist, x='Release', y='Taxa Retrabalho (%)',
                       title='Evolução da Taxa de Retrabalho',
                       markers=True,
                       color_discrete_sequence=['#ef4444'])
        fig7.add_hline(y=15, line_dash="dash", annotation_text="Meta ≤ 15%", line_color="#22c55e")
        fig7.update_layout(height=280)
        st.plotly_chart(fig7, use_container_width=True)
    
    with col8:
        # Gráfico de velocidade (SP/Release)
        fig8 = px.bar(df_hist, x='Release', y='Story Points',
                      title='Velocidade do Time (Story Points/Release)',
                      color='Story Points',
                      color_continuous_scale='Greens')
        fig8.add_hline(y=df_hist['Story Points'].mean(), line_dash="dash", 
                       annotation_text=f"Média: {df_hist['Story Points'].mean():.0f} SP", line_color="#3b82f6")
        fig8.update_layout(height=280, showlegend=False)
        st.plotly_chart(fig8, use_container_width=True)
    
    st.markdown("---")
    
    # ==== Seção 6: Tabela Completa ====
    st.markdown("### 📊 Tabela de Histórico Completo")
    
    # Remover colunas calculadas para exibir tabela limpa
    df_display = df_hist[['Release', 'Cards Concluídos', 'Story Points', 'Bugs Encontrados', 
                          'Bugs Produção', 'Hotfixes', 'Taxa Retrabalho (%)', 'FPY (%)', 
                          'DDP (%)', 'Lead Time (dias)', 'MTTR (horas)', 'Cobertura Testes (%)']].copy()
    
    st.dataframe(df_display, hide_index=True, use_container_width=True)
    
    st.markdown("---")
    
    # ==== Seção 7: Análise de Tendências ====
    st.markdown("### 💡 Análise de Tendências")
    
    col_t1, col_t2, col_t3 = st.columns(3)
    
    with col_t1:
        fpy_trend = df_hist['FPY (%)'].iloc[-1] - df_hist['FPY (%)'].iloc[0]
        fpy_emoji = "📈" if fpy_trend > 0 else "📉" if fpy_trend < 0 else "➡️"
        fpy_status = "Melhorando" if fpy_trend > 0 else "Piorando" if fpy_trend < 0 else "Estável"
        
        st.markdown(f"""
        <div class="status-card status-{'green' if fpy_trend > 0 else 'yellow' if fpy_trend == 0 else 'red'}">
            <p style="font-size: 24px; margin: 0;">{fpy_emoji}</p>
            <p style="font-weight: bold; margin: 5px 0;">FPY</p>
            <p class="card-label">{fpy_status} ({fpy_trend:+.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_t2:
        retrabalho_trend = df_hist['Taxa Retrabalho (%)'].iloc[-1] - df_hist['Taxa Retrabalho (%)'].iloc[0]
        retrabalho_emoji = "📈" if retrabalho_trend < 0 else "📉" if retrabalho_trend > 0 else "➡️"
        retrabalho_status = "Melhorando" if retrabalho_trend < 0 else "Piorando" if retrabalho_trend > 0 else "Estável"
        
        st.markdown(f"""
        <div class="status-card status-{'green' if retrabalho_trend < 0 else 'yellow' if retrabalho_trend == 0 else 'red'}">
            <p style="font-size: 24px; margin: 0;">{retrabalho_emoji}</p>
            <p style="font-weight: bold; margin: 5px 0;">Retrabalho</p>
            <p class="card-label">{retrabalho_status} ({retrabalho_trend:+.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_t3:
        lead_trend = df_hist['Lead Time (dias)'].iloc[-1] - df_hist['Lead Time (dias)'].iloc[0]
        lead_emoji = "📈" if lead_trend < 0 else "📉" if lead_trend > 0 else "➡️"
        lead_status = "Melhorando" if lead_trend < 0 else "Piorando" if lead_trend > 0 else "Estável"
        
        st.markdown(f"""
        <div class="status-card status-{'green' if lead_trend < 0 else 'yellow' if lead_trend == 0 else 'red'}">
            <p style="font-size: 24px; margin: 0;">{lead_emoji}</p>
            <p style="font-weight: bold; margin: 5px 0;">Lead Time</p>
            <p class="card-label">{lead_status} ({lead_trend:+.1f}d)</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==== Seção 8: Resumo Estatístico ====
    st.markdown("### 📉 Resumo Estatístico do Período")
    
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        st.markdown(f"""
        **Médias do Período (últimas 6 releases):**
        
        | Métrica | Média | Mín | Máx |
        |---------|-------|-----|-----|
        | Cards/Release | {df_hist['Cards Concluídos'].mean():.0f} | {df_hist['Cards Concluídos'].min()} | {df_hist['Cards Concluídos'].max()} |
        | Story Points | {df_hist['Story Points'].mean():.0f} | {df_hist['Story Points'].min()} | {df_hist['Story Points'].max()} |
        | Bugs QA | {df_hist['Bugs Encontrados'].mean():.0f} | {df_hist['Bugs Encontrados'].min()} | {df_hist['Bugs Encontrados'].max()} |
        | Lead Time | {df_hist['Lead Time (dias)'].mean():.1f}d | {df_hist['Lead Time (dias)'].min()}d | {df_hist['Lead Time (dias)'].max()}d |
        """)
    
    with col_s2:
        st.markdown(f"""
        **Indicadores de Qualidade (Simulado):**
        
        | Métrica | Média | Meta | Status |
        |---------|-------|------|--------|
        | FPY | {df_hist['FPY (%)'].mean():.1f}% | ≥70% | {'✅' if df_hist['FPY (%)'].mean() >= 70 else '⚠️'} |
        | DDP | {df_hist['DDP (%)'].mean():.1f}% | ≥85% | {'✅' if df_hist['DDP (%)'].mean() >= 85 else '⚠️'} |
        | Retrabalho | {df_hist['Taxa Retrabalho (%)'].mean():.1f}% | ≤15% | {'✅' if df_hist['Taxa Retrabalho (%)'].mean() <= 15 else '⚠️'} |
        | Cobertura* | - | ≥70% | 🔧 |
        
        *Cobertura de testes: requer integração CI/CD
        """)
    
    st.markdown("---")
    st.caption("💡 **Dica**: Para dados históricos reais, configure a integração com o Jira. Os dados são coletados automaticamente ao final de cada release.")


# ==============================================================================
# ABA DE IMPACTO & ROADMAP
# ==============================================================================

def aba_impacto_roadmap():
    """Aba de Análise de Impacto e Roadmap - Estilo Notion."""
    
    st.markdown('<div class="section-header"><h2>🎯 Impacto & Roadmap</h2></div>', unsafe_allow_html=True)
    
    # ==== SEÇÃO 0: SOBRE A NINA ====
    st.markdown("""
    <div style="background: linear-gradient(135deg, #AF0C37 0%, #8B0A2C 100%); padding: 24px; border-radius: 12px; margin-bottom: 24px;">
        <h3 style="margin: 0 0 12px 0; color: #ffffff;">🤖 NINA Tecnologia</h3>
        <p style="margin: 0 0 16px 0; color: #fecdd3; font-size: 15px; line-height: 1.6;">
            A <b style="color: #fff;">NINA</b> é uma empresa de tecnologia especializada em <b style="color: #fff;">soluções digitais inovadoras</b>, 
            com foco em desenvolvimento de software de alta qualidade. Nossa missão é transformar ideias em produtos 
            digitais que geram valor real para nossos clientes.
        </p>
        <div style="display: flex; gap: 16px; flex-wrap: wrap;">
            <div style="background: rgba(255,255,255,0.15); padding: 12px 16px; border-radius: 8px; flex: 1; min-width: 200px;">
                <p style="margin: 0; color: #fecdd3; font-size: 12px;">🎯 MISSÃO</p>
                <p style="margin: 4px 0 0 0; color: #fff; font-size: 14px; font-weight: 500;">Entregar software de qualidade com excelência operacional</p>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 12px 16px; border-radius: 8px; flex: 1; min-width: 200px;">
                <p style="margin: 0; color: #fecdd3; font-size: 12px;">👁️ VISÃO</p>
                <p style="margin: 4px 0 0 0; color: #fff; font-size: 14px; font-weight: 500;">Ser referência em qualidade de software no Brasil</p>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 12px 16px; border-radius: 8px; flex: 1; min-width: 200px;">
                <p style="margin: 0; color: #fecdd3; font-size: 12px;">💎 VALORES</p>
                <p style="margin: 4px 0 0 0; color: #fff; font-size: 14px; font-weight: 500;">Qualidade, Transparência, Inovação</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 24px; border-radius: 12px; border-left: 4px solid #AF0C37; margin-bottom: 24px;">
        <h3 style="margin: 0 0 10px 0; color: #f8fafc;">📊 Análise Estratégica do Dashboard</h3>
        <p style="margin: 0; color: #e2e8f0; font-size: 14px;">
            Este dashboard foi desenvolvido para a <b style="color: #AF0C37;">NINA Tecnologia</b>, baseado em padrões 
            <b>ISTQB/CTFL</b>, práticas de <b>Test-Driven Development (TDD)</b> e métricas de qualidade de software 
            reconhecidas internacionalmente.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ==== SEÇÃO 1: IMPACTO ATUAL ====
    st.markdown("## 📈 Impacto Atual do Dashboard")
    
    st.markdown("""
    <div style="background: #1e293b; padding: 20px; border-radius: 8px; margin-bottom: 16px; color: #f1f5f9;">
    
    ### 🎯 Métricas Implementadas (ISTQB-Aligned)
    
    O dashboard implementa métricas fundamentais do **ISTQB Foundation Level**, fornecendo uma visão completa do ciclo de qualidade na **NINA**:
    
    | Métrica | Descrição | Impacto na NINA |
    |---------|-----------|-----------------|
    | **FPY (First Pass Yield)** | Cards aprovados de primeira sem bugs | Mede eficiência do desenvolvimento |
    | **DDP (Defect Detection Percentage)** | Eficácia do QA em encontrar bugs | Indica maturidade do processo de testes |
    | **Fator K** | Relação SP/Bugs com rigor | Classifica maturidade individual dos devs |
    | **Lead Time** | Tempo do início ao fim do card | Identifica gargalos no fluxo |
    | **MTTR** | Tempo médio para resolver bugs | Mede capacidade de resposta |
    | **WIP (Work In Progress)** | Cards simultâneos por pessoa | Controla sobrecarga e contexto |
    
    </div>
    """, unsafe_allow_html=True)
    
    col_imp1, col_imp2 = st.columns(2)
    
    with col_imp1:
        st.markdown("""
        <div style="background: #22c55e15; padding: 16px; border-radius: 8px; border-left: 3px solid #22c55e;">
        <h4 style="color: #22c55e; margin: 0 0 12px 0;">✅ O que já conseguimos</h4>
        
        - **Visibilidade Total**: Status de todas as releases em tempo real
        - **Rastreabilidade**: Cada card vinculado ao desenvolvedor e QA
        - **Métricas ISTQB**: FPY, DDP, MTTR padronizados internacionalmente
        - **Fator K Único**: Classificação de maturidade dos desenvolvedores
        - **Alertas Proativos**: Go/No-Go automático com cards rastreáveis
        - **Janela de Validação**: Análise de tempo vs prazo da release
        - **Análise para Tech Lead**: WIP, Code Review, Velocidade
        
        </div>
        """, unsafe_allow_html=True)
    
    with col_imp2:
        st.markdown("""
        <div style="background: #3b82f615; padding: 16px; border-radius: 8px; border-left: 3px solid #3b82f6;">
        <h4 style="color: #3b82f6; margin: 0 0 12px 0;">📊 Benefícios Mensuráveis</h4>
        
        - **Redução de retrabalho**: Identificação precoce de devs que precisam de suporte
        - **Decisões data-driven**: Liderança com métricas em vez de percepção
        - **Cultura de qualidade**: Selo Gold incentiva entregas sem bugs
        - **Previsibilidade**: Análise de tendências e histórico
        - **Transparência**: Time vê o mesmo dashboard que a liderança
        - **Shift-Left**: Problemas detectados antes da produção
        
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==== SEÇÃO 2: FUNDAMENTOS TEÓRICOS ====
    st.markdown("## 📚 Fundamentos Teóricos")
    
    with st.expander("🎓 ISTQB/CTFL - Métricas de Teste de Software", expanded=False):
        st.markdown("""
        ### International Software Testing Qualifications Board (ISTQB)
        
        O **ISTQB Foundation Level (CTFL)** define padrões globais para métricas de teste:
        
        **Métricas de Processo** (implementadas no dashboard):
        - *Defect Detection Percentage (DDP)*: Eficácia do QA
        - *First Pass Yield (FPY)*: Qualidade na primeira entrega
        - *Rework Effort Ratio*: Esforço gasto em correções
        
        **Métricas de Produto**:
        - *Defect Density*: Bugs por unidade de tamanho (SP)
        - *Test Coverage*: Cobertura de testes automatizados
        
        **Métricas de Projeto**:
        - *Schedule Variance*: Desvio do prazo planejado
        - *Resource Utilization*: Utilização da capacidade do time
        
        > *"We cannot improve what we cannot measure"* - ISTQB Syllabus
        
        **Referência**: [ISTQB CTFL Syllabus v4.0](https://www.istqb.org/certifications/certified-tester-foundation-level)
        """)
    
    with st.expander("🔄 TDD - Test-Driven Development", expanded=False):
        st.markdown("""
        ### Test-Driven Development (Kent Beck)
        
        O **TDD** segue o ciclo **Red-Green-Refactor**:
        
        1. 🔴 **Red**: Escrever um teste que falha
        2. 🟢 **Green**: Escrever código mínimo para passar
        3. 🔵 **Refactor**: Melhorar o código mantendo testes passando
        
        **Benefícios mensuráveis pelo dashboard**:
        
        | Prática TDD | Métrica no Dashboard |
        |-------------|---------------------|
        | Menos bugs em produção | FPY alto, DDP alto |
        | Código mais limpo | Lead Time menor |
        | Confiança para refatorar | Taxa de retrabalho baixa |
        | Documentação viva | Cobertura de testes |
        
        **Como o Fator K se relaciona com TDD**:
        - Devs que praticam TDD tendem a ter **FK mais alto**
        - Menos bugs = maior proporção SP/Bugs
        - Selo Gold incentiva a prática
        
        **Referência**: [Martin Fowler - TDD](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
        """)
    
    with st.expander("📈 Shift-Left Testing", expanded=False):
        st.markdown("""
        ### Shift-Left: Testar Mais Cedo
        
        O conceito de **Shift-Left** move as atividades de teste para o início do ciclo:
        
        ```
        Tradicional:  Requisitos → Desenvolvimento → [TESTES] → Deploy
        Shift-Left:   [TESTES] → Requisitos → [TESTES] → Desenvolvimento → [TESTES] → Deploy
        ```
        
        **Impacto do Dashboard na cultura Shift-Left**:
        
        - 🎯 **Visibilidade de bugs em tempo real** incentiva correção imediata
        - 📊 **Fator K visível** motiva devs a testar antes de entregar
        - ⚠️ **Alertas de Go/No-Go** impedem releases problemáticas
        - 🏆 **Selo Gold (SP≥6, 0 bugs)** recompensa qualidade antecipada
        
        **Estatísticas da indústria**:
        - Bug encontrado em dev: **$100** para corrigir
        - Bug encontrado em QA: **$1.500** para corrigir
        - Bug encontrado em produção: **$10.000+** para corrigir
        
        > O dashboard ajuda a NINA a encontrar bugs mais cedo, economizando recursos.
        """)
    
    st.markdown("---")
    
    # ==== SEÇÃO 3: ROADMAP DE EVOLUÇÃO ====
    st.markdown("## 🚀 Roadmap de Evolução")
    
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1e293b 0%, #334155 100%); padding: 20px; border-radius: 12px; margin-bottom: 16px;">
    <p style="color: #f1f5f9; margin: 0; font-weight: 500;">📋 Próximas melhorias priorizadas por impacto e viabilidade técnica para a <span style="color: #AF0C37;">NINA</span>:</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Fase 1
    st.markdown("### 🔵 Fase 1: Curto Prazo (1-2 sprints)")
    
    col_f1a, col_f1b = st.columns(2)
    
    with col_f1a:
        st.markdown("""
        <div style="background: #1e293b; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
        <h5 style="color: #60a5fa; margin: 0 0 8px 0;">📊 Integração com Testes Automatizados</h5>
        <p style="color: #e2e8f0; font-size: 13px; margin: 0 0 8px 0;">
        Conectar com pipelines CI/CD para mostrar cobertura de testes e resultados de execução.
        </p>
        <span style="background: #22c55e20; color: #22c55e; padding: 2px 8px; border-radius: 4px; font-size: 11px;">Alto Impacto</span>
        <span style="background: #3b82f620; color: #3b82f6; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-left: 4px;">Média Complexidade</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: #1e293b; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
        <h5 style="color: #60a5fa; margin: 0 0 8px 0;">🔔 Notificações Inteligentes</h5>
        <p style="color: #e2e8f0; font-size: 13px; margin: 0 0 8px 0;">
        Alertas via Slack/Teams quando métricas críticas ultrapassarem thresholds.
        </p>
        <span style="background: #eab30820; color: #eab308; padding: 2px 8px; border-radius: 4px; font-size: 11px;">Médio Impacto</span>
        <span style="background: #22c55e20; color: #22c55e; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-left: 4px;">Baixa Complexidade</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col_f1b:
        st.markdown("""
        <div style="background: #1e293b; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
        <h5 style="color: #60a5fa; margin: 0 0 8px 0;">📈 Predição de Bugs</h5>
        <p style="color: #e2e8f0; font-size: 13px; margin: 0 0 8px 0;">
        Machine Learning para prever cards com alta probabilidade de bugs baseado em padrões históricos.
        </p>
        <span style="background: #22c55e20; color: #22c55e; padding: 2px 8px; border-radius: 4px; font-size: 11px;">Alto Impacto</span>
        <span style="background: #ef444420; color: #ef4444; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-left: 4px;">Alta Complexidade</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: #1e293b; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
        <h5 style="color: #60a5fa; margin: 0 0 8px 0;">📱 Export de Relatórios</h5>
        <p style="color: #e2e8f0; font-size: 13px; margin: 0 0 8px 0;">
        Gerar PDFs executivos e planilhas para stakeholders externos.
        </p>
        <span style="background: #eab30820; color: #eab308; padding: 2px 8px; border-radius: 4px; font-size: 11px;">Médio Impacto</span>
        <span style="background: #22c55e20; color: #22c55e; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-left: 4px;">Baixa Complexidade</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Fase 2
    st.markdown("### 🟢 Fase 2: Médio Prazo (3-4 sprints)")
    
    col_f2a, col_f2b = st.columns(2)
    
    with col_f2a:
        st.markdown("""
        <div style="background: #1e293b; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
        <h5 style="color: #22c55e; margin: 0 0 8px 0;">🎮 Gamificação para Desenvolvedores</h5>
        <p style="color: #e2e8f0; font-size: 13px; margin: 0 0 8px 0;">
        Sistema de conquistas, rankings e recompensas baseados em métricas de qualidade.
        </p>
        <ul style="color: #cbd5e1; font-size: 12px; margin: 8px 0 0 0; padding-left: 16px;">
        <li>🏆 Troféus por sequência de cards sem bugs</li>
        <li>📈 Ranking mensal de FPY</li>
        <li>🎯 Metas personalizadas por dev</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: #1e293b; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
        <h5 style="color: #22c55e; margin: 0 0 8px 0;">🔍 Análise de Root Cause</h5>
        <p style="color: #e2e8f0; font-size: 13px; margin: 0 0 8px 0;">
        Categorização automática de bugs por tipo (lógica, UI, performance, etc) para análise de padrões.
        </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_f2b:
        st.markdown("""
        <div style="background: #1e293b; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
        <h5 style="color: #22c55e; margin: 0 0 8px 0;">📊 Dashboard de Squad</h5>
        <p style="color: #e2e8f0; font-size: 13px; margin: 0 0 8px 0;">
        Visão por squad/equipe para comparativos e métricas agregadas.
        </p>
        <ul style="color: #cbd5e1; font-size: 12px; margin: 8px 0 0 0; padding-left: 16px;">
        <li>📈 Velocidade comparativa entre squads</li>
        <li>🎯 Metas por equipe</li>
        <li>🔄 Análise de dependências</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: #1e293b; padding: 16px; border-radius: 8px; margin-bottom: 12px;">
        <h5 style="color: #22c55e; margin: 0 0 8px 0;">🤖 Integração com IA</h5>
        <p style="color: #e2e8f0; font-size: 13px; margin: 0 0 8px 0;">
        Sugestões automáticas de melhorias baseadas em análise de dados históricos.
        </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Fase 3
    st.markdown("### 🟣 Fase 3: Longo Prazo (5+ sprints)")
    
    st.markdown("""
    <div style="background: #1e293b; padding: 20px; border-radius: 8px; color: #f1f5f9;">
    
    | Feature | Descrição | Benefício |
    |---------|-----------|-----------|
    | **Benchmark Externo** | Comparar métricas com padrões da indústria | Posicionamento competitivo |
    | **Mobile App** | Dashboard em tempo real no celular | Acesso ubíquo para liderança |
    | **Integração Confluence** | Documentação automática de releases | Rastreabilidade completa |
    | **Analytics Avançado** | Correlações, regressões, forecasting | Tomada de decisão preditiva |
    | **Multi-projeto** | Suporte a múltiplos projetos Jira | Escalabilidade organizacional |
    
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==== SEÇÃO 4: MÉTRICAS DE SUCESSO ====
    st.markdown("## 🎯 Métricas de Sucesso do Dashboard")
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    with col_m1:
        st.markdown("""
        <div style="background: #22c55e15; padding: 16px; border-radius: 8px; text-align: center;">
        <p style="font-size: 32px; margin: 0;">📈</p>
        <p style="font-size: 24px; font-weight: bold; color: #22c55e; margin: 8px 0;">+15%</p>
        <p style="font-size: 12px; color: #e2e8f0; margin: 0;">Meta: FPY</p>
        <p style="font-size: 11px; color: #94a3b8; margin: 4px 0 0 0;">6 meses</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_m2:
        st.markdown("""
        <div style="background: #3b82f615; padding: 16px; border-radius: 8px; text-align: center;">
        <p style="font-size: 32px; margin: 0;">📉</p>
        <p style="font-size: 24px; font-weight: bold; color: #3b82f6; margin: 8px 0;">-30%</p>
        <p style="font-size: 12px; color: #e2e8f0; margin: 0;">Meta: Retrabalho</p>
        <p style="font-size: 11px; color: #94a3b8; margin: 4px 0 0 0;">6 meses</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_m3:
        st.markdown("""
        <div style="background: #eab30815; padding: 16px; border-radius: 8px; text-align: center;">
        <p style="font-size: 32px; margin: 0;">⏱️</p>
        <p style="font-size: 24px; font-weight: bold; color: #eab308; margin: 8px 0;">≤7d</p>
        <p style="font-size: 12px; color: #e2e8f0; margin: 0;">Meta: Lead Time</p>
        <p style="font-size: 11px; color: #94a3b8; margin: 4px 0 0 0;">Médio</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_m4:
        st.markdown("""
        <div style="background: #8b5cf615; padding: 16px; border-radius: 8px; text-align: center;">
        <p style="font-size: 32px; margin: 0;">🥇</p>
        <p style="font-size: 24px; font-weight: bold; color: #8b5cf6; margin: 8px 0;">50%</p>
        <p style="font-size: 12px; color: #e2e8f0; margin: 0;">Meta: Devs Gold</p>
        <p style="font-size: 11px; color: #94a3b8; margin: 4px 0 0 0;">12 meses</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==== SEÇÃO 5: REFERÊNCIAS ====
    st.markdown("## 📚 Referências e Leitura Recomendada")
    
    st.markdown("""
    <div style="background: #1e293b; padding: 20px; border-radius: 8px; color: #f1f5f9;">
    
    **Certificações e Padrões:**
    - 🎓 [ISTQB CTFL Syllabus v4.0](https://www.istqb.org/certifications/certified-tester-foundation-level) - Fundamentos de teste de software
    - 📖 [ISTQB Glossary](https://glossary.istqb.org/) - Termos padronizados de QA
    
    **Práticas de Desenvolvimento:**
    - 🔄 [Test-Driven Development - Martin Fowler](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
    - 📘 *Test-Driven Development by Example* - Kent Beck
    - 📗 *The Art of Agile Development* - James Shore
    
    **Métricas e Analytics:**
    - 📊 [Software Testing Metrics - Guru99](https://www.guru99.com/software-testing-metrics-complete-tutorial.html)
    - 📈 *Accelerate* - Nicole Forsgren (métricas DevOps)
    
    **Qualidade de Software:**
    - 🎯 [Shift-Left Testing - IBM](https://www.ibm.com/garage/method/practices/code/practice_test_driven_development/)
    - 🔍 IEEE 730 - Standard for Software Quality Assurance
    
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("📅 Última atualização da análise: Abril 2026 | Dashboard desenvolvido exclusivamente para NINA Tecnologia")


# ==============================================================================
# ABA DE PRODUTOS NINA
# ==============================================================================

# Configuração dos produtos reais da NINA
# Os produtos são identificados no Jira por componentes, labels ou palavras-chave no título
PRODUTOS_NINA = {
    "plataforma": {
        "id": "PROD-001",
        "nome": "Plataforma Nina",
        "nome_curto": "Plataforma",
        "descricao": "Confirmação de Agendamentos, gestão de agenda, integrações com ERPs/sistemas médicos, regras de template",
        "categoria": "Plataforma",
        "keywords": ["plataforma", "confirmationcall", "confirmação", "agendamento", "agenda", "erp", "template", "integração"],
        "components": ["Plataforma", "ConfirmationCall", "Agenda"],
        "emoji": "📞",
        "cor": "#AF0C37"
    },
    "ninachat": {
        "id": "PROD-002",
        "nome": "NinaChat",
        "nome_curto": "NinaChat",
        "descricao": "Chat omnichannel (WhatsApp, Instagram/Messenger, e-mail, etc.), Kanban, fila de conversas, campanhas, NPS no chat, dashboards",
        "categoria": "Módulo",
        "keywords": ["ninachat", "chat", "whatsapp", "instagram", "messenger", "kanban", "fila", "campanha", "nps", "omnichannel"],
        "components": ["NinaChat", "Chat", "Mensageria"],
        "emoji": "💬",
        "cor": "#25D366"
    },
    "ninaflow": {
        "id": "PROD-003",
        "nome": "Nina Flow",
        "nome_curto": "Flow",
        "descricao": "Orquestrador de fluxos/bots (URA, chatbot integrado, IA generativa, ferramentas de listagem, regras de preço)",
        "categoria": "Plataforma",
        "keywords": ["flow", "fluxo", "ura", "chatbot", "bot", "ia", "generativa", "orquestrador", "listagem", "preço"],
        "components": ["NinaFlow", "Flow", "URA", "Bot"],
        "emoji": "🔄",
        "cor": "#8B5CF6"
    },
    "hub": {
        "id": "PROD-004",
        "nome": "HUB",
        "nome_curto": "HUB",
        "descricao": "Agendamento centralizado (\"Uber de agendamentos\"), relatórios de agendamentos, cadência de ligação para prestadores",
        "categoria": "Módulo",
        "keywords": ["hub", "centralizado", "prestador", "cadência", "ligação", "relatório agendamento"],
        "components": ["HUB", "Hub"],
        "emoji": "🎯",
        "cor": "#F59E0B"
    },
    "checkin": {
        "id": "PROD-005",
        "nome": "Checkin",
        "nome_curto": "Checkin",
        "descricao": "Web check-in, totens, captura de foto/FaceMesh, emissão de senhas, concierge",
        "categoria": "App",
        "keywords": ["checkin", "check-in", "totem", "facemesh", "senha", "concierge", "recepção"],
        "components": ["Checkin", "Check-in", "Totem"],
        "emoji": "✅",
        "cor": "#10B981"
    },
    "nina_agenda": {
        "id": "PROD-006",
        "nome": "Nina Agenda",
        "nome_curto": "Agenda",
        "descricao": "Agenda do profissional (app/visualização própria), exibição de telefone e unidade no card do agendamento",
        "categoria": "App",
        "keywords": ["nina agenda", "agenda profissional", "agenda médico", "visualização agenda"],
        "components": ["NinaAgenda", "Agenda Profissional"],
        "emoji": "📅",
        "cor": "#3B82F6"
    },
    "app_paciente": {
        "id": "PROD-007",
        "nome": "APP Paciente",
        "nome_curto": "App Paciente",
        "descricao": "Aplicativo do paciente (Minha Saúde, histórico de vacinas, agendamentos, dados clínicos)",
        "categoria": "App",
        "keywords": ["app paciente", "minha saúde", "vacina", "histórico", "dados clínicos", "paciente app"],
        "components": ["APP Paciente", "App Paciente", "Minha Saúde"],
        "emoji": "📱",
        "cor": "#EC4899"
    }
}


def identificar_produto_card(titulo: str, componentes: List = None, labels: List = None) -> str:
    """Identifica a qual produto um card pertence baseado no título, componentes ou labels."""
    titulo_lower = titulo.lower() if titulo else ""
    
    for produto_key, produto_info in PRODUTOS_NINA.items():
        # Verificar keywords no título
        for keyword in produto_info["keywords"]:
            if keyword.lower() in titulo_lower:
                return produto_key
        
        # Verificar componentes
        if componentes:
            for comp in componentes:
                comp_name = comp.get("name", "") if isinstance(comp, dict) else str(comp)
                for prod_comp in produto_info["components"]:
                    if prod_comp.lower() in comp_name.lower():
                        return produto_key
    
    return "outros"  # Card não identificado


def calcular_metricas_produto(df: pd.DataFrame, produto_key: str) -> Dict:
    """Calcula métricas de um produto específico baseado nos cards do DataFrame."""
    
    # Filtrar cards do produto
    if produto_key == "todos":
        df_produto = df
    else:
        produto_info = PRODUTOS_NINA.get(produto_key, {})
        keywords = produto_info.get("keywords", [])
        
        # Filtrar por keywords no título
        mask = df["titulo"].str.lower().str.contains("|".join(keywords), case=False, na=False)
        df_produto = df[mask]
    
    if df_produto.empty:
        return {
            "total_cards": 0,
            "cards_concluidos": 0,
            "cards_em_andamento": 0,
            "cards_backlog": 0,
            "total_bugs": 0,
            "total_sp": 0,
            "fpy": 0,
            "ddp": 0,
            "fator_k": 0,
            "lead_time_medio": 0,
            "cards_por_status": {},
            "bugs_por_tipo": {},
            "desenvolvedores": [],
            "qas": [],
            "cards_detalhe": []
        }
    
    # Métricas básicas
    total_cards = len(df_produto)
    cards_concluidos = len(df_produto[df_produto["status_cat"] == "done"])
    cards_em_andamento = len(df_produto[df_produto["status_cat"].isin(["development", "code_review", "testing", "waiting_qa"])])
    cards_backlog = len(df_produto[df_produto["status_cat"] == "backlog"])
    cards_bloqueados = len(df_produto[df_produto["status_cat"] == "blocked"])
    
    total_bugs = int(df_produto["bugs"].sum())
    total_sp = int(df_produto["sp"].sum())
    
    # FPY - First Pass Yield
    cards_sem_bugs = len(df_produto[df_produto["bugs"] == 0])
    fpy = (cards_sem_bugs / total_cards * 100) if total_cards > 0 else 0
    
    # DDP
    bugs_estimados_prod = max(1, total_cards * 0.05)
    ddp = (total_bugs / (total_bugs + bugs_estimados_prod) * 100) if total_bugs > 0 else 100
    
    # Fator K
    fator_k = round((total_sp / (total_bugs + 1)) * 1.5, 2) if total_sp > 0 else 0
    
    # Lead time médio
    lead_time_medio = round(df_produto["lead_time"].mean(), 1) if not df_produto.empty else 0
    
    # Cards por status
    cards_por_status = df_produto.groupby("status_cat").size().to_dict()
    
    # Bugs por tipo de card
    bugs_por_tipo = df_produto.groupby("tipo")["bugs"].sum().to_dict()
    
    # Desenvolvedores únicos
    desenvolvedores = df_produto["desenvolvedor"].unique().tolist()
    desenvolvedores = [d for d in desenvolvedores if d != "Não atribuído"]
    
    # QAs únicos
    qas = df_produto["qa"].unique().tolist()
    qas = [q for q in qas if q != "Não atribuído"]
    
    # Cards com mais bugs
    cards_problematicos = df_produto[df_produto["bugs"] >= 2].sort_values("bugs", ascending=False).head(5)
    
    return {
        "total_cards": total_cards,
        "cards_concluidos": cards_concluidos,
        "cards_em_andamento": cards_em_andamento,
        "cards_backlog": cards_backlog,
        "cards_bloqueados": cards_bloqueados,
        "total_bugs": total_bugs,
        "total_sp": total_sp,
        "fpy": round(fpy, 1),
        "ddp": round(ddp, 1),
        "fator_k": fator_k,
        "lead_time_medio": lead_time_medio,
        "cards_por_status": cards_por_status,
        "bugs_por_tipo": bugs_por_tipo,
        "desenvolvedores": desenvolvedores,
        "qas": qas,
        "cards_problematicos": cards_problematicos,
        "df_produto": df_produto
    }


def aba_produtos(df: pd.DataFrame):
    """Aba de Produtos da NINA - Estatísticas de Liderança e Histórico."""
    
    st.markdown('<div class="section-header"><h2>📦 Produtos NINA</h2></div>', unsafe_allow_html=True)
    
    modo_demo = st.session_state.get('modo_demo', True)
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 20px; border-radius: 12px; border-left: 4px solid #AF0C37; margin-bottom: 24px;">
        <h4 style="margin: 0 0 8px 0; color: #f8fafc;">🎯 Visão de Produtos NINA</h4>
        <p style="margin: 0; color: #e2e8f0; font-size: 14px;">
            Métricas de qualidade, histórico e KPIs para cada produto da NINA.
            <br><small style="color: #94a3b8;">{'⚠️ Modo demonstração - Conecte ao Jira para dados reais' if modo_demo else '✅ Dados do Jira carregados'}</small>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ==== SEÇÃO 1: VISÃO GERAL DO PORTFÓLIO ====
    with st.expander("📊 **Visão Geral do Portfólio** - Todos os produtos em um olhar", expanded=True):
        
        st.markdown("#### 📱 Produtos da NINA Tecnologia")
        
        # Calcular métricas para cada produto
        metricas_produtos = {}
        for produto_key in PRODUTOS_NINA.keys():
            metricas_produtos[produto_key] = calcular_metricas_produto(df, produto_key)
        
        # Cards de produtos em grid
        cols = st.columns(4)
        for i, (produto_key, produto_info) in enumerate(PRODUTOS_NINA.items()):
            metricas = metricas_produtos[produto_key]
            
            with cols[i % 4]:
                # Calcular indicador de saúde
                score = 0
                if metricas["total_cards"] > 0:
                    if metricas["fpy"] >= 70: score += 30
                    elif metricas["fpy"] >= 50: score += 15
                    
                    if metricas["cards_bloqueados"] == 0: score += 25
                    elif metricas["cards_bloqueados"] <= 2: score += 10
                    
                    conclusao = metricas["cards_concluidos"] / metricas["total_cards"] * 100
                    if conclusao >= 70: score += 25
                    elif conclusao >= 50: score += 15
                    
                    if metricas["fator_k"] >= 3: score += 20
                    elif metricas["fator_k"] >= 2: score += 10
                
                saude_cor = "#22c55e" if score >= 70 else "#eab308" if score >= 40 else "#ef4444"
                saude_texto = "Saudável" if score >= 70 else "Atenção" if score >= 40 else "Crítico"
                
                st.markdown(f"""
                <div style="background: #1e293b; padding: 16px; border-radius: 12px; margin-bottom: 12px; border-left: 4px solid {produto_info['cor']}; min-height: 180px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 20px;">{produto_info['emoji']}</span>
                        <span style="background: {saude_cor}20; color: {saude_cor}; padding: 2px 8px; border-radius: 4px; font-size: 10px;">{saude_texto}</span>
                    </div>
                    <h5 style="color: #f8fafc; margin: 0 0 8px 0; font-size: 14px;">{produto_info['nome']}</h5>
                    <p style="color: #94a3b8; font-size: 11px; margin: 0 0 12px 0; line-height: 1.4;">{produto_info['descricao'][:80]}...</p>
                    <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                        <span style="background: #3b82f620; color: #60a5fa; padding: 2px 6px; border-radius: 4px; font-size: 10px;">📋 {metricas['total_cards']} cards</span>
                        <span style="background: #22c55e20; color: #22c55e; padding: 2px 6px; border-radius: 4px; font-size: 10px;">✅ {metricas['cards_concluidos']}</span>
                        <span style="background: #ef444420; color: #ef4444; padding: 2px 6px; border-radius: 4px; font-size: 10px;">🐛 {metricas['total_bugs']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Métricas agregadas
        total_cards = sum(m["total_cards"] for m in metricas_produtos.values())
        total_concluidos = sum(m["cards_concluidos"] for m in metricas_produtos.values())
        total_bugs = sum(m["total_bugs"] for m in metricas_produtos.values())
        total_sp = sum(m["total_sp"] for m in metricas_produtos.values())
        total_bloqueados = sum(m["cards_bloqueados"] for m in metricas_produtos.values())
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
            <div class="status-card status-blue" style="padding: 15px;">
                <p class="big-number">{len(PRODUTOS_NINA)}</p>
                <p class="card-label">Produtos</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="status-card status-purple" style="padding: 15px;">
                <p class="big-number">{total_cards}</p>
                <p class="card-label">Total Cards</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            pct_concluido = (total_concluidos / total_cards * 100) if total_cards > 0 else 0
            cor = "green" if pct_concluido >= 70 else "yellow" if pct_concluido >= 40 else "red"
            st.markdown(f"""
            <div class="status-card status-{cor}" style="padding: 15px;">
                <p class="big-number">{pct_concluido:.0f}%</p>
                <p class="card-label">Concluídos</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="status-card status-orange" style="padding: 15px;">
                <p class="big-number">{total_bugs}</p>
                <p class="card-label">Total Bugs</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            cor_bloq = "green" if total_bloqueados == 0 else "red"
            st.markdown(f"""
            <div class="status-card status-{cor_bloq}" style="padding: 15px;">
                <p class="big-number">{total_bloqueados}</p>
                <p class="card-label">Bloqueados</p>
            </div>
            """, unsafe_allow_html=True)
    
    # ==== SEÇÃO 2: SELEÇÃO DE PRODUTO ====
    st.markdown("---")
    
    nomes_produtos = [(k, v["nome"]) for k, v in PRODUTOS_NINA.items()]
    produto_options = ["📊 Visão Geral (Todos)"] + [f"{v['emoji']} {v['nome']}" for k, v in PRODUTOS_NINA.items()]
    
    produto_selecionado = st.selectbox("🔍 Selecione um produto para análise detalhada", produto_options)
    
    if produto_selecionado == "📊 Visão Geral (Todos)":
        # Mostrar comparativo entre produtos
        with st.expander("📊 **Comparativo entre Produtos**", expanded=True):
            st.caption("Métricas comparativas de todos os produtos da NINA")
            
            dados_comp = []
            for produto_key, produto_info in PRODUTOS_NINA.items():
                metricas = metricas_produtos[produto_key]
                dados_comp.append({
                    "Produto": produto_info["nome"],
                    "Cards": metricas["total_cards"],
                    "Concluídos": metricas["cards_concluidos"],
                    "Em Andamento": metricas["cards_em_andamento"],
                    "Bugs": metricas["total_bugs"],
                    "SP": metricas["total_sp"],
                    "FPY (%)": metricas["fpy"],
                    "Fator K": metricas["fator_k"],
                    "Lead Time (dias)": metricas["lead_time_medio"]
                })
            
            df_comp = pd.DataFrame(dados_comp)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Cards por Produto**")
                if not df_comp.empty and df_comp["Cards"].sum() > 0:
                    fig = px.bar(df_comp, x="Produto", y=["Concluídos", "Em Andamento", "Bugs"],
                                barmode="stack",
                                color_discrete_sequence=["#22c55e", "#3b82f6", "#ef4444"])
                    fig.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20),
                                     legend=dict(orientation="h", yanchor="bottom", y=1.02),
                                     xaxis_title="", yaxis_title="")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Sem dados para exibir")
            
            with col2:
                st.markdown("**🎯 FPY por Produto**")
                if not df_comp.empty and df_comp["Cards"].sum() > 0:
                    fig2 = px.bar(df_comp.sort_values("FPY (%)", ascending=True), 
                                 x="FPY (%)", y="Produto", orientation="h",
                                 color="FPY (%)",
                                 color_continuous_scale=["#ef4444", "#eab308", "#22c55e"])
                    fig2.add_vline(x=70, line_dash="dash", annotation_text="Meta: 70%", line_color="#3b82f6")
                    fig2.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20), showlegend=False)
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("Sem dados para exibir")
            
            st.markdown("**📋 Tabela Comparativa**")
            st.dataframe(df_comp, hide_index=True, use_container_width=True)
    
    else:
        # Encontrar produto selecionado
        produto_key = None
        for k, v in PRODUTOS_NINA.items():
            if v["nome"] in produto_selecionado:
                produto_key = k
                break
        
        if produto_key:
            produto_info = PRODUTOS_NINA[produto_key]
            metricas = metricas_produtos[produto_key]
            
            # ==== SEÇÃO 3: ESTATÍSTICAS DO PRODUTO ====
            with st.expander(f"🎯 **Estatísticas de Liderança** - {produto_info['nome']}", expanded=True):
                st.caption(f"KPIs e métricas de qualidade baseados nos cards do Jira")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # KPIs principais
                    st.markdown("#### 📊 Métricas de Qualidade")
                    
                    kpi_cols = st.columns(4)
                    
                    with kpi_cols[0]:
                        fpy_cor = "green" if metricas["fpy"] >= 70 else "yellow" if metricas["fpy"] >= 50 else "red"
                        st.markdown(f"""
                        <div class="status-card status-{fpy_cor}" style="padding: 12px;">
                            <p style="font-size: 28px; font-weight: bold; margin: 0;">{metricas['fpy']}%</p>
                            <p class="card-label">FPY</p>
                            <p style="font-size: 10px; opacity: 0.7;">Cards sem bugs</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with kpi_cols[1]:
                        ddp_cor = "green" if metricas["ddp"] >= 85 else "yellow" if metricas["ddp"] >= 70 else "red"
                        st.markdown(f"""
                        <div class="status-card status-{ddp_cor}" style="padding: 12px;">
                            <p style="font-size: 28px; font-weight: bold; margin: 0;">{metricas['ddp']}%</p>
                            <p class="card-label">DDP</p>
                            <p style="font-size: 10px; opacity: 0.7;">Detecção de Defeitos</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with kpi_cols[2]:
                        fk_cor = "green" if metricas["fator_k"] >= 3 else "yellow" if metricas["fator_k"] >= 2 else "red" if metricas["fator_k"] > 0 else "blue"
                        st.markdown(f"""
                        <div class="status-card status-{fk_cor}" style="padding: 12px;">
                            <p style="font-size: 28px; font-weight: bold; margin: 0;">{metricas['fator_k']}</p>
                            <p class="card-label">Fator K</p>
                            <p style="font-size: 10px; opacity: 0.7;">Maturidade</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with kpi_cols[3]:
                        lt_cor = "green" if metricas["lead_time_medio"] <= 7 else "yellow" if metricas["lead_time_medio"] <= 14 else "red"
                        st.markdown(f"""
                        <div class="status-card status-{lt_cor}" style="padding: 12px;">
                            <p style="font-size: 28px; font-weight: bold; margin: 0;">{metricas['lead_time_medio']}</p>
                            <p class="card-label">Lead Time</p>
                            <p style="font-size: 10px; opacity: 0.7;">Dias (média)</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Métricas de cards
                    st.markdown("#### 📋 Status dos Cards")
                    
                    card_cols = st.columns(5)
                    
                    with card_cols[0]:
                        st.metric("Total", metricas["total_cards"])
                    with card_cols[1]:
                        st.metric("Concluídos", metricas["cards_concluidos"], 
                                 delta=f"{metricas['cards_concluidos']/metricas['total_cards']*100:.0f}%" if metricas["total_cards"] > 0 else "0%")
                    with card_cols[2]:
                        st.metric("Em Andamento", metricas["cards_em_andamento"])
                    with card_cols[3]:
                        st.metric("Backlog", metricas["cards_backlog"])
                    with card_cols[4]:
                        st.metric("Bloqueados", metricas["cards_bloqueados"], 
                                 delta="Crítico!" if metricas["cards_bloqueados"] > 0 else None,
                                 delta_color="inverse")
                    
                    st.markdown("---")
                    
                    # Bugs
                    st.markdown("#### 🐛 Análise de Bugs")
                    
                    bug_cols = st.columns(3)
                    
                    with bug_cols[0]:
                        st.metric("Total de Bugs", metricas["total_bugs"])
                    with bug_cols[1]:
                        taxa = metricas["total_bugs"] / metricas["total_cards"] if metricas["total_cards"] > 0 else 0
                        st.metric("Taxa de Bugs/Card", f"{taxa:.2f}")
                    with bug_cols[2]:
                        st.metric("Story Points", metricas["total_sp"])
                
                with col2:
                    # Info do produto
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, {produto_info['cor']} 0%, {produto_info['cor']}CC 100%); padding: 20px; border-radius: 12px; color: white;">
                        <div style="font-size: 32px; text-align: center; margin-bottom: 12px;">{produto_info['emoji']}</div>
                        <h4 style="margin: 0 0 12px 0; color: white; text-align: center;">{produto_info['nome']}</h4>
                        <p style="font-size: 12px; opacity: 0.9; margin: 0 0 16px 0; text-align: center;">{produto_info['descricao']}</p>
                        
                        <div style="background: rgba(255,255,255,0.15); padding: 10px; border-radius: 8px; margin-bottom: 10px;">
                            <p style="margin: 0; font-size: 11px; opacity: 0.8;">📂 Categoria</p>
                            <p style="margin: 4px 0 0 0; font-size: 13px; font-weight: 600;">{produto_info['categoria']}</p>
                        </div>
                        
                        <div style="background: rgba(255,255,255,0.15); padding: 10px; border-radius: 8px; margin-bottom: 10px;">
                            <p style="margin: 0; font-size: 11px; opacity: 0.8;">👨‍💻 Desenvolvedores</p>
                            <p style="margin: 4px 0 0 0; font-size: 13px; font-weight: 600;">{len(metricas['desenvolvedores'])}</p>
                        </div>
                        
                        <div style="background: rgba(255,255,255,0.15); padding: 10px; border-radius: 8px;">
                            <p style="margin: 0; font-size: 11px; opacity: 0.8;">🧪 QAs</p>
                            <p style="margin: 4px 0 0 0; font-size: 13px; font-weight: 600;">{len(metricas['qas'])}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # ==== SEÇÃO 4: CARDS PROBLEMÁTICOS ====
            if metricas["total_bugs"] > 0:
                with st.expander(f"🐛 **Cards com mais Bugs** - {produto_info['nome']}", expanded=True):
                    st.caption("Cards que precisam de atenção especial")
                    
                    if "cards_problematicos" in metricas and not metricas["cards_problematicos"].empty:
                        for _, row in metricas["cards_problematicos"].iterrows():
                            bugs = row.get("bugs", 0)
                            risco = "high" if bugs >= 3 else "medium" if bugs >= 2 else "low"
                            
                            st.markdown(f"""
                            <div class="ticket-card ticket-risk-{risco}">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <a href="{row.get('link', '#')}" target="_blank" style="color: #6366f1; font-weight: bold; text-decoration: none;">🔗 {row.get('ticket_id', 'N/A')}</a>
                                    <span style="color: #ef4444; font-weight: bold;">🐛 {bugs} bugs</span>
                                </div>
                                <p style="margin: 8px 0;">{row.get('titulo', '')[:60]}...</p>
                                <p style="font-size: 12px; opacity: 0.8;">
                                    <b>Dev:</b> {row.get('desenvolvedor', 'N/A')} | 
                                    <b>QA:</b> {row.get('qa', 'N/A')} | 
                                    <b>SP:</b> {row.get('sp', 0)}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.success("✅ Nenhum card com múltiplos bugs!")
            
            # ==== SEÇÃO 5: LISTA DE CARDS ====
            with st.expander(f"📋 **Todos os Cards** - {produto_info['nome']}", expanded=False):
                st.caption(f"Lista completa dos cards identificados para este produto")
                
                if "df_produto" in metricas and not metricas["df_produto"].empty:
                    df_display = metricas["df_produto"][["ticket_id", "titulo", "status", "desenvolvedor", "qa", "sp", "bugs", "lead_time"]].copy()
                    df_display.columns = ["Ticket", "Título", "Status", "Dev", "QA", "SP", "Bugs", "Lead Time"]
                    df_display["Título"] = df_display["Título"].str[:50] + "..."
                    st.dataframe(df_display, hide_index=True, use_container_width=True)
                else:
                    st.info("Nenhum card encontrado para este produto")
    
    # ==== NOTA SOBRE IDENTIFICAÇÃO ====
    with st.expander("ℹ️ **Como os produtos são identificados?**", expanded=False):
        st.markdown("""
        Os cards são associados aos produtos através de:
        
        1. **Palavras-chave no título**: Cada produto tem uma lista de keywords que são buscadas no título do card
        2. **Componentes do Jira**: Se o card tiver um componente associado a um produto
        3. **Labels**: Tags específicas no card
        
        **Dica**: Para melhor identificação, use componentes ou prefixos consistentes nos títulos dos cards.
        """)
        
        st.markdown("**Keywords por produto:**")
        for k, v in PRODUTOS_NINA.items():
            st.markdown(f"- **{v['nome']}**: {', '.join(v['keywords'][:5])}...")
    
    # Footer
    st.markdown("---")
    st.caption("💡 **Nota**: Os cards são identificados automaticamente por keywords no título. Para maior precisão, configure componentes no Jira.")


# ==============================================================================
# MAIN
# ==============================================================================

# Favicon da NINA como data URI
NINA_FAVICON = "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 187 187'><path d='M173.709 89.2107C172.209 86.6048 169.414 84.838 166.225 84.838C163.036 84.838 160.241 86.5649 158.741 89.1627H151.683C149.465 58.8237 124.495 35 94.0216 35C63.5489 35 38.5862 58.8237 36.3678 89.1627H29.1759C27.6759 86.5649 24.8734 84.798 21.6682 84.798C18.463 84.798 15.6605 86.5806 14.1605 89.2031C13.4184 90.4899 13 92.001 13 93.6C13 95.1987 13.4184 96.7017 14.1605 97.997C15.6605 100.619 18.463 102.306 21.6682 102.306C24.8734 102.306 27.6838 100.435 29.1759 97.8369H36.3678C38.5862 128.168 63.5489 152 94.0216 152C124.495 152 149.465 128.176 151.675 97.8369H158.686C160.178 100.435 162.996 102.354 166.217 102.354C169.438 102.354 172.256 100.611 173.749 97.9648C174.475 96.6856 174.885 95.2148 174.885 93.6319C174.885 92.049 174.451 90.5222 173.701 89.2188L173.709 89.2107ZM111.145 125.554C107.971 131.518 101.758 135.459 94.5981 135.459C87.4374 135.459 81.2248 131.566 78.0509 125.602C77.1666 123.947 78.3667 122.092 80.2219 122.092H108.982C110.837 122.092 112.029 123.891 111.153 125.554H111.145ZM140.528 94.1277C140.528 103.825 132.76 111.691 123.184 111.691H65.4432C55.8675 111.691 48.0991 103.825 48.0991 94.1277V93.7199C48.0991 84.0223 55.8675 76.1557 65.4432 76.1557H123.184C132.76 76.1557 140.528 84.0223 140.528 93.7199V94.1277Z' fill='%23AF0C37'/><path d='M76.5809 105.311C82.9686 105.311 88.1466 100.068 88.1466 93.5996C88.1466 87.1312 82.9686 81.8875 76.5809 81.8875C70.1936 81.8875 65.0156 87.1312 65.0156 93.5996C65.0156 100.068 70.1936 105.311 76.5809 105.311Z' fill='%23AF0C37'/><path d='M111.437 105.311C117.824 105.311 123.002 100.068 123.002 93.5996C123.002 87.1312 117.824 81.8875 111.437 81.8875C105.049 81.8875 99.8712 87.1312 99.8712 93.5996C99.8712 100.068 105.049 105.311 111.437 105.311Z' fill='%23AF0C37'/></svg>"

# Logo NINA SVG para usar em várias partes
NINA_LOGO_SVG = '''<svg width="60" height="60" viewBox="0 0 187 187" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M173.709 89.2107C172.209 86.6048 169.414 84.838 166.225 84.838C163.036 84.838 160.241 86.5649 158.741 89.1627H151.683C149.465 58.8237 124.495 35 94.0216 35C63.5489 35 38.5862 58.8237 36.3678 89.1627H29.1759C27.6759 86.5649 24.8734 84.798 21.6682 84.798C18.463 84.798 15.6605 86.5806 14.1605 89.2031C13.4184 90.4899 13 92.001 13 93.6C13 95.1987 13.4184 96.7017 14.1605 97.997C15.6605 100.619 18.463 102.306 21.6682 102.306C24.8734 102.306 27.6838 100.435 29.1759 97.8369H36.3678C38.5862 128.168 63.5489 152 94.0216 152C124.495 152 149.465 128.176 151.675 97.8369H158.686C160.178 100.435 162.996 102.354 166.217 102.354C169.438 102.354 172.256 100.611 173.749 97.9648C174.475 96.6856 174.885 95.2148 174.885 93.6319C174.885 92.049 174.451 90.5222 173.701 89.2188L173.709 89.2107ZM111.145 125.554C107.971 131.518 101.758 135.459 94.5981 135.459C87.4374 135.459 81.2248 131.566 78.0509 125.602C77.1666 123.947 78.3667 122.092 80.2219 122.092H108.982C110.837 122.092 112.029 123.891 111.153 125.554H111.145ZM140.528 94.1277C140.528 103.825 132.76 111.691 123.184 111.691H65.4432C55.8675 111.691 48.0991 103.825 48.0991 94.1277V93.7199C48.0991 84.0223 55.8675 76.1557 65.4432 76.1557H123.184C132.76 76.1557 140.528 84.0223 140.528 93.7199V94.1277Z" fill="#AF0C37"/>
<path d="M76.5809 105.311C82.9686 105.311 88.1466 100.068 88.1466 93.5996C88.1466 87.1312 82.9686 81.8875 76.5809 81.8875C70.1936 81.8875 65.0156 87.1312 65.0156 93.5996C65.0156 100.068 70.1936 105.311 76.5809 105.311Z" fill="#AF0C37"/>
<path d="M111.437 105.311C117.824 105.311 123.002 100.068 123.002 93.5996C123.002 87.1312 117.824 81.8875 111.437 81.8875C105.049 81.8875 99.8712 87.1312 99.8712 93.5996C99.8712 100.068 105.049 105.311 111.437 105.311Z" fill="#AF0C37"/>
</svg>'''


def mostrar_tela_login():
    """Tela de login moderna e profissional."""
    
    # Inicializar estado do modal
    if "mostrar_modal_acesso" not in st.session_state:
        st.session_state.mostrar_modal_acesso = False
    
    # Se modal está aberto, mostrar tela do modal
    if st.session_state.mostrar_modal_acesso:
        mostrar_modal_solicitar_acesso()
        return
    
    # CSS completo para transformar a coluna central em card
    st.markdown("""
    <style>
    /* ===== FUNDO E RESET ===== */
    .stApp {
        background: #F7F7F8 !important;
    }
    
    header[data-testid="stHeader"],
    [data-testid="stSidebar"],
    #MainMenu, footer {
        display: none !important;
    }
    
    .block-container {
        padding-top: 100px !important;
        padding-bottom: 40px !important;
        max-width: 100% !important;
    }
    
    /* ===== COLUNA CENTRAL COMO CARD ===== */
    [data-testid="column"]:nth-child(2) > div {
        background: white !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 24px rgba(0,0,0,0.08) !important;
        padding: 40px 36px 32px !important;
        max-width: 420px !important;
        margin: 0 auto !important;
    }
    
    /* ===== INPUTS MODERNOS ===== */
    .stTextInput > div > div {
        background: #F9FAFB !important;
        border-radius: 10px !important;
        border: 1.5px solid #E5E7EB !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
    }
    
    .stTextInput > div > div:hover {
        border-color: #D1D5DB !important;
        background: #F3F4F6 !important;
    }
    
    .stTextInput > div > div:focus-within {
        border-color: #AF0C37 !important;
        background: #FFFFFF !important;
        box-shadow: 0 0 0 3px rgba(175, 12, 55, 0.08) !important;
    }
    
    .stTextInput > div > div > input {
        height: 48px !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0 14px !important;
        font-size: 15px !important;
        background: transparent !important;
        color: #1F2937 !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #9CA3AF !important;
        opacity: 1 !important;
    }
    
    .stTextInput label {
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #374151 !important;
        margin-bottom: 6px !important;
    }
    
    /* ===== BOTÃO DE OCULTAR SENHA COM CONTRASTE ===== */
    .stTextInput button {
        color: #6B7280 !important;
        background: transparent !important;
    }
    
    .stTextInput button:hover {
        color: #374151 !important;
        background: #E5E7EB !important;
    }
    
    .stTextInput svg {
        color: #6B7280 !important;
        fill: #6B7280 !important;
    }
    
    /* ===== FORMULÁRIO ===== */
    div[data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
        background: transparent !important;
    }
    
    /* ===== BOTÃO PRINCIPAL ===== */
    .stFormSubmitButton > button {
        width: 100% !important;
        height: 50px !important;
        background: linear-gradient(135deg, #AF0C37 0%, #8F0A2E 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        margin-top: 12px !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 2px 8px rgba(175, 12, 55, 0.25) !important;
    }
    
    .stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, #8F0A2E 0%, #700823 100%) !important;
        box-shadow: 0 4px 16px rgba(175, 12, 55, 0.35) !important;
        transform: translateY(-1px) !important;
    }
    
    .stFormSubmitButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* ===== ALERTAS ===== */
    .stAlert {
        border-radius: 10px !important;
    }
    
    /* ===== LINK SOLICITAR ACESSO ===== */
    .solicitar-acesso-link {
        color: #AF0C37 !important;
        text-decoration: none !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: color 0.2s ease !important;
    }
    
    .solicitar-acesso-link:hover {
        color: #8F0A2E !important;
        text-decoration: underline !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Layout com 3 colunas (central é o card)
    col1, col2, col3 = st.columns([1, 1.4, 1])
    
    with col2:
        # Logo NINA real no topo
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <svg width="130" height="30" viewBox="0 0 129 29" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M123.407 4.40351C112.719 -1.10001 102.104 9.63353 107.537 20.4563C109.291 23.9462 112.854 26.1025 116.719 26.1025H126.133C127.716 26.1025 129 24.8381 129 23.2368V13.7042C129 9.7901 126.851 6.17922 123.405 4.40549L123.407 4.40351ZM120.706 19.3623C119.798 19.9747 118.706 20.3314 117.534 20.3314C114.367 20.3314 111.8 17.7313 111.8 14.5247C111.8 11.3181 114.367 8.71793 117.534 8.71793C120.7 8.71793 123.268 11.3181 123.268 14.5247C123.268 15.7118 122.915 16.8157 122.311 17.7372L124.107 21.1816L120.706 19.3623Z" fill="#AF0C37"/>
                <path d="M77.4431 5.81865V23.2369C77.4431 24.8402 76.1632 26.1403 74.578 26.1403C72.9928 26.1403 71.7129 24.8402 71.7129 23.2369V5.81865C71.7129 4.21536 72.9713 2.91528 74.5565 2.91528C75.3471 2.91528 76.0732 3.2403 76.5918 3.76548C77.1104 4.29067 77.4411 5.01601 77.4411 5.81865H77.4431Z" fill="#AF0C37"/>
                <path d="M68.745 14.5268V23.2349C68.745 24.8382 67.4906 26.1383 65.9073 26.1383C64.7448 26.1383 63.733 25.4367 63.2829 24.4319C63.1205 24.0673 63.0168 23.663 63.0168 23.2369V14.5288C63.0168 11.3222 60.455 8.72202 57.2885 8.72202C54.122 8.72202 51.5603 11.3222 51.5603 14.5288V23.2369C51.5603 23.663 51.4898 24.0692 51.3274 24.4319C50.8773 25.4387 49.8694 26.1383 48.7069 26.1383C47.1237 26.1383 45.832 24.8382 45.832 23.2349V14.5268C45.832 8.1136 50.9575 2.91528 57.2885 2.91528C63.6195 2.91528 68.745 8.1136 68.745 14.5268Z" fill="#AF0C37"/>
                <path d="M103.116 14.5268V23.2349C103.116 24.8382 101.875 26.1383 100.292 26.1383C99.1296 26.1383 98.11 25.4367 97.6599 24.4319C97.4975 24.0673 97.3879 23.663 97.3879 23.2369V14.5288C97.3879 11.3222 94.8261 8.72202 91.6596 8.72202C88.4931 8.72202 85.9314 11.3222 85.9314 14.5288V23.2369C85.9314 23.663 85.8766 24.0692 85.7122 24.4319C85.2621 25.4387 84.2464 26.1383 83.0839 26.1383C81.5006 26.1383 80.2012 24.8382 80.2012 23.2349V14.5268C80.2012 8.1136 85.3267 2.91528 91.6577 2.91528C97.9887 2.91528 103.114 8.1136 103.114 14.5268H103.116Z" fill="#AF0C37"/>
                <path d="M39.8413 13.4387C39.4695 12.7927 38.7767 12.3547 37.9861 12.3547C37.1954 12.3547 36.5026 12.7828 36.1308 13.4268H34.3812C33.8313 5.90583 27.6412 0 20.087 0C12.5329 0 6.34471 5.90583 5.79478 13.4268H4.01192C3.64008 12.7828 2.94534 12.3448 2.15078 12.3448C1.35622 12.3448 0.661474 12.7867 0.289637 13.4368C0.105676 13.7558 0.00195312 14.1304 0.00195312 14.5268C0.00195312 14.9231 0.105676 15.2957 0.289637 15.6168C0.661474 16.2668 1.35622 16.685 2.15078 16.685C2.94534 16.685 3.64204 16.2212 4.01192 15.5771H5.79478C6.34471 23.0961 12.5329 29.004 20.087 29.004C27.6412 29.004 33.8313 23.0981 34.3792 15.5771H36.1171C36.487 16.2212 37.1856 16.6968 37.9841 16.6968C38.7826 16.6968 39.4812 16.2648 39.8511 15.6088C40.0312 15.2917 40.1329 14.9271 40.1329 14.5347C40.1329 14.1423 40.0253 13.7638 39.8394 13.4407L39.8413 13.4387ZM24.3318 22.4481C23.5451 23.9265 22.0049 24.9036 20.2299 24.9036C18.4548 24.9036 16.9147 23.9384 16.1279 22.46C15.9087 22.0497 16.2062 21.59 16.6661 21.59H23.7956C24.2555 21.59 24.551 22.0359 24.3338 22.4481H24.3318ZM31.6159 14.6576C31.6159 17.0615 29.6902 19.0116 27.3163 19.0116H13.0025C10.6287 19.0116 8.70294 17.0615 8.70294 14.6576V14.5565C8.70294 12.1525 10.6287 10.2024 13.0025 10.2024H27.3163C29.6902 10.2024 31.6159 12.1525 31.6159 14.5565V14.6576Z" fill="#AF0C37"/>
                <path d="M15.7635 17.43C17.347 17.43 18.6306 16.1301 18.6306 14.5267C18.6306 12.9232 17.347 11.6233 15.7635 11.6233C14.1801 11.6233 12.8965 12.9232 12.8965 14.5267C12.8965 16.1301 14.1801 17.43 15.7635 17.43Z" fill="#AF0C37"/>
                <path d="M24.4042 17.43C25.9876 17.43 27.2712 16.1301 27.2712 14.5267C27.2712 12.9232 25.9876 11.6233 24.4042 11.6233C22.8207 11.6233 21.5371 12.9232 21.5371 14.5267C21.5371 16.1301 22.8207 17.43 24.4042 17.43Z" fill="#AF0C37"/>
            </svg>
        </div>
        """, unsafe_allow_html=True)
        
        # Título e subtítulo
        st.markdown("""
        <h1 style="text-align: center; font-size: 22px; font-weight: 600; color: #1F2937; margin: 0 0 4px; line-height: 1.3;">
            Bem-vindo ao NinaDash
        </h1>
        <p style="text-align: center; font-size: 14px; color: #6B7280; margin: 0 0 24px; line-height: 1.4;">
            Plataforma de Qualidade e Decisão de Software
        </p>
        """, unsafe_allow_html=True)
        
        # Formulário
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("E-mail", placeholder="seuemail@empresa.com.br")
            senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            
            st.markdown('<p style="text-align: center; font-size: 12px; color: #9CA3AF; margin: 16px 0 8px;">💡 Use seu e-mail corporativo</p>', unsafe_allow_html=True)
            
            submitted = st.form_submit_button("Entrar", use_container_width=True)
            
            if submitted:
                if not email:
                    st.error("Por favor, informe seu e-mail")
                elif not senha:
                    st.error("Por favor, informe sua senha")
                elif "@" not in email:
                    st.error("E-mail inválido")
                else:
                    with st.spinner("Entrando..."):
                        if fazer_login(email, senha):
                            st.success("Login realizado!")
                            st.rerun()
                        else:
                            st.error("Credenciais inválidas")
        
        # Solicitar acesso
        st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
        
        if st.button("Solicitar acesso", key="btn_solicitar_acesso", use_container_width=True, type="secondary"):
            st.session_state.mostrar_modal_acesso = True
            st.rerun()
        
        # Rodapé
        st.markdown("""
        <div style="text-align: center; margin-top: 20px; padding: 12px; background: #F8F9FA; border-radius: 8px; font-size: 12px; color: #6B7280;">
            🔒 Acesso restrito – dados protegidos
        </div>
        
        <p style="text-align: center; font-size: 11px; color: #9CA3AF; margin-top: 16px;">
            © 2026 NINA Tecnologia
        </p>
        """, unsafe_allow_html=True)


def mostrar_modal_solicitar_acesso():
    """Tela de solicitar acesso (substitui o login temporariamente)."""
    
    # CSS para a tela de solicitar acesso
    st.markdown("""
    <style>
    .stApp {
        background: #F7F7F8 !important;
    }
    
    header[data-testid="stHeader"],
    [data-testid="stSidebar"],
    #MainMenu, footer {
        display: none !important;
    }
    
    .block-container {
        padding-top: 100px !important;
        padding-bottom: 40px !important;
        max-width: 100% !important;
    }
    
    /* Card central */
    [data-testid="column"]:nth-child(2) > div {
        background: white !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 24px rgba(0,0,0,0.08) !important;
        padding: 40px 36px 32px !important;
        max-width: 420px !important;
        margin: 0 auto !important;
    }
    
    /* Botão voltar */
    .stButton > button {
        width: 100% !important;
        height: 48px !important;
        background: linear-gradient(135deg, #AF0C37 0%, #8F0A2E 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 2px 8px rgba(175, 12, 55, 0.25) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #8F0A2E 0%, #700823 100%) !important;
        box-shadow: 0 4px 16px rgba(175, 12, 55, 0.35) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Layout com 3 colunas
    col1, col2, col3 = st.columns([1, 1.4, 1])
    
    with col2:
        # Ícone de email
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="
                width: 64px;
                height: 64px;
                background: linear-gradient(135deg, #AF0C37, #8F0A2E);
                border-radius: 50%;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 16px rgba(175, 12, 55, 0.3);
            ">
                <svg width="28" height="28" fill="white" viewBox="0 0 24 24">
                    <path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
                </svg>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Título e texto
        st.markdown("""
        <h1 style="text-align: center; font-size: 22px; font-weight: 600; color: #1F2937; margin: 0 0 12px;">
            Solicitar Acesso
        </h1>
        <p style="text-align: center; font-size: 14px; color: #6B7280; margin: 0 0 24px; line-height: 1.6;">
            Para solicitar acesso à plataforma NinaDash, entre em contato pelo e-mail abaixo:
        </p>
        """, unsafe_allow_html=True)
        
        # Email em destaque
        st.markdown("""
        <div style="text-align: center; margin-bottom: 24px;">
            <a href="mailto:vinicios.ferreira@confirmationcall.com.br" style="
                display: inline-block;
                background: #FEF2F2;
                color: #AF0C37;
                padding: 14px 24px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
                text-decoration: none;
                transition: background 0.2s;
            ">
                📧 vinicios.ferreira@confirmationcall.com.br
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        # Botão Voltar
        if st.button("← Voltar ao Login", key="btn_voltar_login", use_container_width=True):
            st.session_state.mostrar_modal_acesso = False
            st.rerun()
        
        # Rodapé
        st.markdown("""
        <p style="text-align: center; font-size: 11px; color: #9CA3AF; margin-top: 24px;">
            © 2026 NINA Tecnologia
        </p>
        """, unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="Dashboard QA - NINA",
        page_icon=NINA_FAVICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    aplicar_estilos()
    
    # ========== VERIFICAR LOGIN ==========
    if not verificar_login():
        mostrar_tela_login()
        return
    
    # ========== USUÁRIO LOGADO - DASHBOARD ==========
    
    # Logo NINA (robô vermelho) - SVG inline
    logo_svg = '''<svg width="50" height="50" viewBox="0 0 187 187" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M173.709 89.2107C172.209 86.6048 169.414 84.838 166.225 84.838C163.036 84.838 160.241 86.5649 158.741 89.1627H151.683C149.465 58.8237 124.495 35 94.0216 35C63.5489 35 38.5862 58.8237 36.3678 89.1627H29.1759C27.6759 86.5649 24.8734 84.798 21.6682 84.798C18.463 84.798 15.6605 86.5806 14.1605 89.2031C13.4184 90.4899 13 92.001 13 93.6C13 95.1987 13.4184 96.7017 14.1605 97.997C15.6605 100.619 18.463 102.306 21.6682 102.306C24.8734 102.306 27.6838 100.435 29.1759 97.8369H36.3678C38.5862 128.168 63.5489 152 94.0216 152C124.495 152 149.465 128.176 151.675 97.8369H158.686C160.178 100.435 162.996 102.354 166.217 102.354C169.438 102.354 172.256 100.611 173.749 97.9648C174.475 96.6856 174.885 95.2148 174.885 93.6319C174.885 92.049 174.451 90.5222 173.701 89.2188L173.709 89.2107ZM111.145 125.554C107.971 131.518 101.758 135.459 94.5981 135.459C87.4374 135.459 81.2248 131.566 78.0509 125.602C77.1666 123.947 78.3667 122.092 80.2219 122.092H108.982C110.837 122.092 112.029 123.891 111.153 125.554H111.145ZM140.528 94.1277C140.528 103.825 132.76 111.691 123.184 111.691H65.4432C55.8675 111.691 48.0991 103.825 48.0991 94.1277V93.7199C48.0991 84.0223 55.8675 76.1557 65.4432 76.1557H123.184C132.76 76.1557 140.528 84.0223 140.528 93.7199V94.1277Z" fill="#AF0C37"/>
    <path d="M76.5809 105.311C82.9686 105.311 88.1466 100.068 88.1466 93.5996C88.1466 87.1312 82.9686 81.8875 76.5809 81.8875C70.1936 81.8875 65.0156 87.1312 65.0156 93.5996C65.0156 100.068 70.1936 105.311 76.5809 105.311Z" fill="#AF0C37"/>
    <path d="M111.437 105.311C117.824 105.311 123.002 100.068 123.002 93.5996C123.002 87.1312 117.824 81.8875 111.437 81.8875C105.049 81.8875 99.8712 87.1312 99.8712 93.5996C99.8712 100.068 105.049 105.311 111.437 105.311Z" fill="#AF0C37"/>
    </svg>'''
    
    # ========== HEADER COM LOGO CENTRALIZADA ==========
    st.markdown(f'''
    <div class="nina-header">
        {logo_svg}
        <div class="nina-header-title">Dashboard de Qualidade</div>
        <div class="nina-header-subtitle">NINA Tecnologia | Métricas ISTQB/CTFL</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        # Usuário logado
        user_email = st.session_state.get("user_email", "")
        user_name = user_email.split("@")[0].replace(".", " ").title() if user_email else "Usuário"
        
        st.markdown(f"""
        <div style="background: #AF0C37; padding: 12px; border-radius: 8px; margin-bottom: 16px; text-align: center;">
            <p style="margin: 0; color: white; font-size: 14px;">👤 {user_name}</p>
            <p style="margin: 4px 0 0 0; color: #fecdd3; font-size: 11px;">{user_email}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botão de Logout
        if st.button("🚪 Sair", use_container_width=True):
            fazer_logout()
            st.rerun()
        
        st.markdown("---")
        
        st.title("⚙️ Configurações")
        
        # Projeto
        st.subheader("📁 Projeto")
        
        projetos_disponiveis = list(PROJETOS.keys())
        projeto = st.selectbox(
            "Projeto principal",
            projetos_disponiveis,
            index=0,
            format_func=lambda x: f"{x} - {PROJETOS[x]['nome']}"
        )
        
        st.caption("💡 SD = Desenvolvimento (foco principal)")
        
        st.markdown("---")
        
        # Informações da Sprint
        st.subheader("📅 Sprint Ativo")
        
        sprint_info = st.session_state.get("sprint_info")
        
        if sprint_info:
            data_fim = datetime.fromisoformat(sprint_info["endDate"].replace("Z", "+00:00")).replace(tzinfo=None)
            dias_restantes = (data_fim - datetime.now()).days
            
            st.success(f"🏃 **{sprint_info['name']}**")
            st.caption(f"📆 Fim: {data_fim.strftime('%d/%m/%Y')}")
            
            if dias_restantes <= 0:
                st.error(f"🚨 Sprint encerrada!")
            elif dias_restantes <= 3:
                st.warning(f"⚠️ {dias_restantes} dia(s) restante(s)")
            else:
                st.info(f"📊 {dias_restantes} dia(s) restante(s)")
        else:
            st.info("Clique em carregar para buscar a sprint")
        
        st.markdown("---")
        
        # Botão de carregar - DESTAQUE
        st.markdown("""
        <style>
        div[data-testid="stButton"] > button[kind="secondary"] {
            background: linear-gradient(135deg, #AF0C37 0%, #8F0A2E 100%) !important;
            color: white !important;
            font-weight: bold !important;
            font-size: 1.1rem !important;
            padding: 0.75rem 1rem !important;
            border: none !important;
            box-shadow: 0 4px 15px rgba(175, 12, 55, 0.4) !important;
            animation: pulse-btn 2s infinite !important;
        }
        div[data-testid="stButton"] > button[kind="secondary"]:hover {
            transform: scale(1.02) !important;
            box-shadow: 0 6px 20px rgba(175, 12, 55, 0.5) !important;
        }
        @keyframes pulse-btn {
            0%, 100% { box-shadow: 0 4px 15px rgba(175, 12, 55, 0.4); }
            50% { box-shadow: 0 4px 25px rgba(175, 12, 55, 0.7); }
        }
        </style>
        """, unsafe_allow_html=True)
        
        carregar_jira = st.button("🔄 CARREGAR DADOS DO JIRA", use_container_width=True, type="secondary")
        
        if carregar_jira:
            with st.spinner("Buscando dados do Jira..."):
                # Primeiro buscar informações da sprint
                sprint_info = buscar_sprint_ativo(projeto)
                
                if sprint_info:
                    st.session_state.sprint_info = sprint_info
                    data_fim_sprint = datetime.fromisoformat(sprint_info["endDate"].replace("Z", "+00:00")).replace(tzinfo=None)
                else:
                    # Fallback: usar data atual + 7 dias
                    data_fim_sprint = datetime.now() + timedelta(days=7)
                
                # Buscar issues
                jql = f'project = "{projeto}" AND sprint in openSprints() ORDER BY created DESC'
                issues = buscar_jira(jql)
                
                if issues:
                    st.session_state.dados = processar_issues(issues, data_fim_sprint)
                    st.session_state.projeto = projeto
                    st.session_state.modo_demo = False
                    st.session_state.ultima_atualizacao = datetime.now()
                    st.success(f"✅ {len(issues)} cards carregados!")
                    st.rerun()
                else:
                    # Tentar query alternativa
                    jql_alt = f'project = "{projeto}" AND updated >= -90d ORDER BY updated DESC'
                    issues = buscar_jira(jql_alt)
                    if issues:
                        st.session_state.dados = processar_issues(issues, data_fim_sprint)
                        st.session_state.projeto = projeto
                        st.session_state.modo_demo = False
                        st.session_state.ultima_atualizacao = datetime.now()
                        st.success(f"✅ {len(issues)} cards carregados (últimos 90 dias)!")
                        st.rerun()
                    else:
                        st.error("Nenhum card encontrado.")
        
        st.markdown("---")
        
        # Indicador de modo e última atualização - ALERTA DESTACADO
        if st.session_state.get('modo_demo', True):
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); 
                        padding: 16px; border-radius: 8px; margin: 8px 0;
                        border-left: 4px solid #92400e; animation: blink-warning 1.5s ease-in-out infinite;">
                <p style="color: white; font-weight: bold; margin: 0; font-size: 0.95rem;">
                    ⚠️ DADOS DE DEMONSTRAÇÃO
                </p>
                <p style="color: #fef3c7; margin: 5px 0 0 0; font-size: 0.85rem;">
                    Os dados exibidos são fictícios.<br>
                    Clique no botão acima para carregar dados reais do Jira.
                </p>
            </div>
            <style>
            @keyframes blink-warning {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.85; }
            }
            </style>
            """, unsafe_allow_html=True)
        else:
            ultima = st.session_state.get('ultima_atualizacao')
            if ultima:
                st.success(f"✅ **Dados do Jira**\n\nÚltima atualização:\n{ultima.strftime('%d/%m/%Y %H:%M')}")
        
        st.markdown("---")
        
        # Legenda das métricas
        st.markdown("**📚 Métricas ISTQB/CTFL:**")
        st.markdown("""
        - **DDP**: Detecção de Defeitos
        - **FPY**: Aprovação de Primeira
        - **MTTR**: Tempo Médio de Correção
        - **FK**: Fator K (Maturidade)
        """)
        
        st.caption("Dashboard v5.1 | NINA Tecnologia")
    
    # Inicializar dados (modo demo se não carregou do Jira)
    if 'dados' not in st.session_state or st.session_state.dados is None:
        st.session_state.dados = gerar_dados_mock("SD")
        st.session_state.projeto = "SD"
        st.session_state.modo_demo = True
    
    df = st.session_state.dados
    projeto_atual = st.session_state.get('projeto', 'SD')
    
    # Extrair Release atual do sprint
    sprint_info = st.session_state.get("sprint_info")
    if sprint_info:
        release_atual = sprint_info["name"].replace("Sprint", "Release")
    else:
        sprint_atual = df['sprint'].mode().iloc[0] if not df.empty else "N/A"
        release_atual = sprint_atual.replace('Sprint', 'Release') if 'Sprint' in str(sprint_atual) else f"Release {sprint_atual}"
    
    # Armazenar release no session_state para uso em outras abas
    st.session_state.release_atual = release_atual
    
    modo = "Jira" if not st.session_state.get('modo_demo', True) else "Demonstração"
    
    # Calcular dias até release
    if sprint_info and "endDate" in sprint_info:
        data_fim = datetime.fromisoformat(sprint_info["endDate"].replace("Z", "+00:00")).replace(tzinfo=None)
        dias_ate_release = calcular_dias_uteis(datetime.now(), data_fim)
    else:
        dias_ate_release = df['dias_ate_release'].iloc[0] if 'dias_ate_release' in df.columns and len(df) > 0 else "?"
    
    # Barra de Release (visível em toda a página)
    # Se modo demo, adicionar alerta no topo
    if st.session_state.get('modo_demo', True):
        st.markdown("""
        <div style="background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%); 
                    padding: 12px 20px; border-radius: 8px; margin-bottom: 16px;
                    display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 1.5rem;">⚠️</span>
                <div>
                    <p style="color: white; font-weight: bold; margin: 0; font-size: 1rem;">
                        MODO DEMONSTRAÇÃO ATIVO
                    </p>
                    <p style="color: #fef3c7; margin: 0; font-size: 0.85rem;">
                        Os dados exibidos são fictícios. Use o botão "Carregar Dados do Jira" na barra lateral para visualizar dados reais.
                    </p>
                </div>
            </div>
            <span style="background: white; color: #d97706; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 0.8rem;">
                DEMO
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f'''
    <div class="release-bar">
        <span class="release-name">📦 {release_atual}</span>
        <span class="release-info">{len(df)} cards | {df['sp'].sum():.0f} SP | 📆 {dias_ate_release} dias | Modo: {modo}</span>
    </div>
    ''', unsafe_allow_html=True)
    
    # Tabs
    tabs = st.tabs(["🎯 Liderança", "📦 Produtos NINA", "🧪 QA", "👨‍💻 Desenvolvimento", "📜 Histórico", "🚀 Impacto & Roadmap"])
    
    with tabs[0]:
        aba_lideranca(df)
    
    with tabs[1]:
        aba_produtos(df)
    
    with tabs[2]:
        aba_qa(df)
    
    with tabs[3]:
        aba_dev(df)
    
    with tabs[4]:
        aba_historico()
    
    with tabs[5]:
        aba_impacto_roadmap()
    
    # Footer
    st.markdown("---")
    st.caption(f"📅 Atualizado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')} | Dashboard v5.1 - NINA Tecnologia")


if __name__ == "__main__":
    main()
