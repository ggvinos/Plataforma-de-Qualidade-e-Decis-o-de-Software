"""
================================================================================
JIRA DASHBOARD v8.7 - NINA TECNOLOGIA - VERSÃO COMPLETA E ENRIQUECIDA
================================================================================
📊 NinaDash — Dashboard de Inteligência e Métricas de QA

🎯 Propósito: Transformar o QA de um processo sem visibilidade em um sistema 
   de inteligência operacional baseado em dados.

MELHORIAS v8.7:
- 🎨 DESIGN REFINADO: Melhor espaçamento entre elementos
- ⬅️ BOTÃO VOLTAR NA SIDEBAR: Indica card ativo + volta fácil
- Link de compartilhamento mais compacto e funcional
- Visual mais limpo nas métricas do card
- Expanders fechados por padrão para menos poluição visual

MELHORIAS v8.6:
- 📱 SIDEBAR REFATORADA: Busca de card em destaque no topo
- 📤 COMPARTILHAMENTO FUNCIONAL: Link direto via query params
- Layout reorganizado: Logo → Busca → Filtros → Rodapé NINA
- URL persistente: ?card=SD-1234&projeto=SD

MELHORIAS v8.5:
- 🔍 BUSCA DE CARD INDIVIDUAL: Pesquise qualquer card pelo ID
- Painel completo com todas as métricas do card
- Fator K individual, janela de validação, aging, lead time
- Flags de fluxo (criado/finalizado na sprint, fora período)
- Timeline completa, resumo executivo automático

MELHORIAS v8.4:
- Aba Backlog exclusiva para projeto PB (Product Backlog)
- Health Score do backlog, análise de aging, cards estagnados
- Recomendações automáticas de ação

MELHORIAS v8.0:
- Header com logo Nina + subtítulo explicativo do objetivo
- Tooltips/explicações em TODAS as métricas (FPY, DDP, Fator K, etc)
- Seções colapsáveis em todas as abas (toggle open/close)
- Listagens COMPLETAS (opção de ver todos os cards)
- Aba Histórico enriquecida com múltiplos gráficos
- Mais métricas em cada aba
- Aba QA (sem "Gargalos" no nome)
- Auto-load + Cache inteligente
- Cards clicáveis com links Jira
- Métricas Ellen: iniciado/finalizado sprint, fora período, hotfix/produto

CAMPOS MAPEADOS JIRA NINA:
- customfield_11257: Story Points (principal)
- customfield_10016: Story Points (alternativo)
- customfield_11157: Bugs Encontrados  
- customfield_10020: Sprint
- customfield_11290: Complexidade de Teste
- customfield_10487: QA Responsável
- customfield_10102: Produto
================================================================================
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from typing import Optional, Dict, List, Any, Tuple
import json
import os
import io
import base64
import random

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA (DEVE SER PRIMEIRO)
# ==============================================================================

# Logo SVG da Nina em base64 para favicon
NINA_LOGO_SVG = '''<svg width="187" height="187" viewBox="0 0 187 187" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M173.709 89.2107C172.209 86.6048 169.414 84.838 166.225 84.838C163.036 84.838 160.241 86.5649 158.741 89.1627H151.683C149.465 58.8237 124.495 35 94.0216 35C63.5489 35 38.5862 58.8237 36.3678 89.1627H29.1759C27.6759 86.5649 24.8734 84.798 21.6682 84.798C18.463 84.798 15.6605 86.5806 14.1605 89.2031C13.4184 90.4899 13 92.001 13 93.6C13 95.1987 13.4184 96.7017 14.1605 97.997C15.6605 100.619 18.463 102.306 21.6682 102.306C24.8734 102.306 27.6838 100.435 29.1759 97.8369H36.3678C38.5862 128.168 63.5489 152 94.0216 152C124.495 152 149.465 128.176 151.675 97.8369H158.686C160.178 100.435 162.996 102.354 166.217 102.354C169.438 102.354 172.256 100.611 173.749 97.9648C174.475 96.6856 174.885 95.2148 174.885 93.6319C174.885 92.049 174.451 90.5222 173.701 89.2188L173.709 89.2107ZM111.145 125.554C107.971 131.518 101.758 135.459 94.5981 135.459C87.4374 135.459 81.2248 131.566 78.0509 125.602C77.1666 123.947 78.3667 122.092 80.2219 122.092H108.982C110.837 122.092 112.029 123.891 111.153 125.554H111.145ZM140.528 94.1277C140.528 103.825 132.76 111.691 123.184 111.691H65.4432C55.8675 111.691 48.0991 103.825 48.0991 94.1277V93.7199C48.0991 84.0223 55.8675 76.1557 65.4432 76.1557H123.184C132.76 76.1557 140.528 84.0223 140.528 93.7199V94.1277Z" fill="#AF0C37"/>
<path d="M76.5809 105.311C82.9686 105.311 88.1466 100.068 88.1466 93.5996C88.1466 87.1312 82.9686 81.8875 76.5809 81.8875C70.1936 81.8875 65.0156 87.1312 65.0156 93.5996C65.0156 100.068 70.1936 105.311 76.5809 105.311Z" fill="#AF0C37"/>
<path d="M111.437 105.311C117.824 105.311 123.002 100.068 123.002 93.5996C123.002 87.1312 117.824 81.8875 111.437 81.8875C105.049 81.8875 99.8712 87.1312 99.8712 93.5996C99.8712 100.068 105.049 105.311 111.437 105.311Z" fill="#AF0C37"/>
</svg>'''

# Favicon como Data URI (funciona em navegadores modernos)
NINA_FAVICON = "data:image/svg+xml," + NINA_LOGO_SVG.replace("#", "%23").replace("\n", "").replace(" ", "%20")

st.set_page_config(
    page_title="NinaDash - Métricas de Qualidade",
    page_icon="favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        "descricao": "Percentual de defeitos encontrados pelo QA antes da produção. Mede a eficácia do time de testes em filtrar bugs.",
        "formula": "DDP = (Bugs encontrados em QA / Total de Bugs estimados) × 100",
        "interpretacao": {
            "≥85%": "Excelente - QA muito eficaz",
            "70-84%": "Bom - Processo funcionando",
            "50-69%": "Regular - Precisa melhorar",
            "<50%": "Crítico - Muitos bugs escapando para produção"
        },
        "fonte": "ISTQB Foundation Level - Test Metrics"
    },
    "fpy": {
        "titulo": "FPY - First Pass Yield (Rendimento de Primeira Passagem)",
        "descricao": "Percentual de cards aprovados na PRIMEIRA validação, sem nenhum bug. Indica a qualidade do código entregue pelo desenvolvimento.",
        "formula": "FPY = (Cards sem bugs / Total de cards) × 100",
        "interpretacao": {
            "≥80%": "Excelente - Código de alta qualidade",
            "60-79%": "Bom - Dentro do esperado",
            "40-59%": "Regular - Revisar práticas de desenvolvimento",
            "<40%": "Crítico - Alto retrabalho, código instável"
        },
        "fonte": "Six Sigma / Lean Manufacturing adaptado para software"
    },
    "lead_time": {
        "titulo": "Lead Time (Tempo de Ciclo Total)",
        "descricao": "Tempo total desde a criação do card até sua conclusão. Inclui desenvolvimento, code review e validação QA.",
        "formula": "Lead Time = Data de Conclusão - Data de Criação",
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
        "descricao": "Pontuação composta (0-100) que avalia a saúde geral da release considerando múltiplos fatores de qualidade.",
        "formula": "HS = (Conclusão×30 + DDP×25 + FPY×20 + Gargalos×15 + LeadTime×10) / 100",
        "interpretacao": {
            "≥75": "🟢 Saudável - Release pode seguir",
            "50-74": "🟡 Atenção - Monitorar riscos",
            "25-49": "🟠 Alerta - Ação necessária",
            "<25": "🔴 Crítico - Avaliar adiamento"
        },
        "fonte": "Composite Score baseado em ISTQB Test Process Improvement"
    },
    "throughput": {
        "titulo": "Throughput (Vazão)",
        "descricao": "Quantidade de cards ou Story Points concluídos por período (sprint). Indica a capacidade de entrega do time.",
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
        "descricao": "Quantidade de cards em andamento simultaneamente. WIP alto pode indicar gargalos e sobrecarga.",
        "formula": "WIP = Cards não concluídos e não no backlog",
        "interpretacao": {
            "≤ Capacidade": "Fluxo saudável",
            "> Capacidade": "Sobrecarga - Risco de atrasos"
        },
        "fonte": "Kanban / Little's Law"
    },
    "defect_density": {
        "titulo": "Densidade de Defeitos",
        "descricao": "Quantidade de bugs por Story Point. Indica a taxa de defeitos relativa ao tamanho da entrega.",
        "formula": "DD = Total de Bugs / Total de SP",
        "interpretacao": {
            "≤0.2": "Baixa densidade - Excelente",
            "0.21-0.5": "Densidade aceitável",
            "0.51-1.0": "Densidade alta - Atenção",
            ">1.0": "Crítico - Muitos bugs por SP"
        },
        "fonte": "IEEE 982.1 - Software Quality Metrics"
    },
}

# ==============================================================================
# CONFIGURAÇÕES GLOBAIS
# ==============================================================================

JIRA_BASE_URL = "https://ninatecnologia.atlassian.net"

CUSTOM_FIELDS = {
    "story_points": "customfield_11257",
    "story_points_alt": "customfield_10016", 
    "sprint": "customfield_10020",
    "bugs_encontrados": "customfield_11157",
    "complexidade_teste": "customfield_11290",
    "qa_responsavel": "customfield_10487",
    "produto": "customfield_10102",
}

STATUS_FLOW = {
    "backlog": ["Backlog", "To Do", "Tarefas pendentes"],
    "development": ["Em andamento"],
    "code_review": ["EM REVISÃO"],
    "waiting_qa": ["AGUARDANDO VALIDAÇÃO"],
    "testing": ["EM VALIDAÇÃO"],
    "done": ["Concluído"],
    "blocked": ["IMPEDIDO"],
    "rejected": ["REPROVADO"],
    "deferred": ["Validado - Adiado", "DESCARTADO"],
}

STATUS_NOMES = {
    "backlog": "📋 Backlog",
    "development": "💻 Desenvolvimento",
    "code_review": "👀 Code Review",
    "waiting_qa": "⏳ Aguardando QA",
    "testing": "🧪 Em Validação",
    "done": "✅ Concluído",
    "blocked": "🚫 Bloqueado",
    "rejected": "❌ Reprovado",
    "deferred": "📅 Adiado",
    "unknown": "❓ Desconhecido"
}

STATUS_CORES = {
    "backlog": "#64748b",
    "development": "#3b82f6",
    "code_review": "#8b5cf6",
    "waiting_qa": "#f59e0b",
    "testing": "#06b6d4",
    "done": "#22c55e",
    "blocked": "#ef4444",
    "rejected": "#dc2626",
    "deferred": "#6b7280",
    "unknown": "#9ca3af"
}

REGRAS = {
    "hotfix_sp_default": 2,
    "cache_ttl_minutos": 5,
    "dias_aging_alerta": 3,
    # Janela de validação por complexidade de teste (dias úteis necessários)
    "janela_complexidade": {
        "Alta": 3,      # Complexidade alta: precisa de 3+ dias
        "Média": 2,     # Complexidade média: precisa de 2 dias  
        "Baixa": 1,     # Complexidade baixa: pode validar em 1 dia
        "default": 3,   # Sem complexidade definida: assume 3 dias (conservador)
    },
}

# ==============================================================================
# UTILITÁRIOS
# ==============================================================================

def link_jira(ticket_id: str) -> str:
    """Gera link para o Jira."""
    return f"{JIRA_BASE_URL}/browse/{ticket_id}"


def calcular_dias_necessarios_validacao(complexidade: str) -> int:
    """
    Calcula quantos dias úteis são necessários para validação baseado na complexidade de teste.
    
    - Alta: 3 dias (testes extensivos, múltiplos cenários)
    - Média: 2 dias (validação padrão)
    - Baixa: 1 dia (validação simples/rápida)
    - Sem definição: 3 dias (conservador)
    """
    janela = REGRAS["janela_complexidade"]
    return janela.get(complexidade, janela["default"])


def avaliar_janela_validacao(dias_ate_release: int, complexidade: str) -> Dict:
    """
    Avalia se um card está dentro ou fora da janela de validação.
    
    Retorna:
        - dentro_janela: bool
        - dias_necessarios: int
        - dias_disponiveis: int
        - status: str ('ok', 'risco', 'fora')
        - mensagem: str
    """
    dias_necessarios = calcular_dias_necessarios_validacao(complexidade)
    dias_disponiveis = dias_ate_release
    
    if dias_disponiveis >= dias_necessarios:
        status = "ok"
        mensagem = f"✅ Dentro da janela ({dias_disponiveis}d disponíveis, {dias_necessarios}d necessários)"
    elif dias_disponiveis >= dias_necessarios - 1:
        status = "risco"
        mensagem = f"⚠️ Em risco ({dias_disponiveis}d disponíveis, {dias_necessarios}d necessários)"
    else:
        status = "fora"
        mensagem = f"🚨 Fora da janela ({dias_disponiveis}d disponíveis, {dias_necessarios}d necessários)"
    
    return {
        "dentro_janela": status == "ok",
        "dias_necessarios": dias_necessarios,
        "dias_disponiveis": dias_disponiveis,
        "status": status,
        "mensagem": mensagem,
        "complexidade_usada": complexidade if complexidade else "Não definida (assumindo 3d)"
    }


def get_secrets():
    """Carrega credenciais de forma segura."""
    try:
        if "jira" in st.secrets:
            return {
                "email": st.secrets["jira"]["email"],
                "token": st.secrets["jira"]["token"],
            }
    except:
        pass
    return {
        "email": os.getenv("JIRA_API_EMAIL", ""),
        "token": os.getenv("JIRA_API_TOKEN", ""),
    }


def verificar_credenciais() -> bool:
    """Verifica se as credenciais estão configuradas."""
    secrets = get_secrets()
    return bool(secrets["email"] and secrets["token"])


# ==============================================================================
# AUTENTICAÇÃO DE USUÁRIO
# ==============================================================================

def verificar_login() -> bool:
    """Verifica se o usuário está logado."""
    return st.session_state.get("logged_in", False) and st.session_state.get("user_email")


def extrair_nome_usuario(email: str) -> str:
    """Extrai o nome do usuário do e-mail corporativo (nome.sobrenome@...)."""
    if not email or "@" not in email:
        return "Usuário"
    
    nome_parte = email.split("@")[0]  # nome.sobrenome
    nome_formatado = nome_parte.replace(".", " ").title()  # Nome Sobrenome
    return nome_formatado


def fazer_login(email: str) -> bool:
    """
    Valida e realiza login do usuário.
    Apenas e-mails com domínio @confirmationcall.com.br são aceitos.
    """
    email_lower = email.lower().strip()
    
    # Valida se é e-mail corporativo (domínio @confirmationcall.com.br)
    if email_lower.endswith("@confirmationcall.com.br"):
        st.session_state.logged_in = True
        st.session_state.user_email = email_lower
        st.session_state.user_nome = extrair_nome_usuario(email_lower)
        return True
    
    return False


def fazer_logout():
    """Remove sessão do usuário."""
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.user_nome = None
    # Limpa dados carregados para forçar reload após novo login
    if 'dados_carregados' in st.session_state:
        del st.session_state.dados_carregados


def mostrar_tela_login():
    """Tela de login simplificada e profissional."""
    
    # CSS para tela de login
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
        padding-top: 80px !important;
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
        line-height: 48px !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #9CA3AF !important;
        line-height: 48px !important;
    }
    
    .stTextInput label {
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #374151 !important;
        margin-bottom: 6px !important;
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
    
    /* ===== ALERTAS ===== */
    .stAlert {
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Layout com 3 colunas (central é o card)
    col1, col2, col3 = st.columns([1, 1.4, 1])
    
    with col2:
        # Logo NINA (robô) - centralizada
        st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 20px;">
            <svg width="80" height="80" viewBox="0 0 187 187" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M173.709 89.2107C172.209 86.6048 169.414 84.838 166.225 84.838C163.036 84.838 160.241 86.5649 158.741 89.1627H151.683C149.465 58.8237 124.495 35 94.0216 35C63.5489 35 38.5862 58.8237 36.3678 89.1627H29.1759C27.6759 86.5649 24.8734 84.798 21.6682 84.798C18.463 84.798 15.6605 86.5806 14.1605 89.2031C13.4184 90.4899 13 92.001 13 93.6C13 95.1987 13.4184 96.7017 14.1605 97.997C15.6605 100.619 18.463 102.306 21.6682 102.306C24.8734 102.306 27.6838 100.435 29.1759 97.8369H36.3678C38.5862 128.168 63.5489 152 94.0216 152C124.495 152 149.465 128.176 151.675 97.8369H158.686C160.178 100.435 162.996 102.354 166.217 102.354C169.438 102.354 172.256 100.611 173.749 97.9648C174.475 96.6856 174.885 95.2148 174.885 93.6319C174.885 92.049 174.451 90.5222 173.701 89.2188L173.709 89.2107ZM111.145 125.554C107.971 131.518 101.758 135.459 94.5981 135.459C87.4374 135.459 81.2248 131.566 78.0509 125.602C77.1666 123.947 78.3667 122.092 80.2219 122.092H108.982C110.837 122.092 112.029 123.891 111.153 125.554H111.145ZM140.528 94.1277C140.528 103.825 132.76 111.691 123.184 111.691H65.4432C55.8675 111.691 48.0991 103.825 48.0991 94.1277V93.7199C48.0991 84.0223 55.8675 76.1557 65.4432 76.1557H123.184C132.76 76.1557 140.528 84.0223 140.528 93.7199V94.1277Z" fill="#AF0C37"/>
            <path d="M76.5809 105.311C82.9686 105.311 88.1466 100.068 88.1466 93.5996C88.1466 87.1312 82.9686 81.8875 76.5809 81.8875C70.1936 81.8875 65.0156 87.1312 65.0156 93.5996C65.0156 100.068 70.1936 105.311 76.5809 105.311Z" fill="#AF0C37"/>
            <path d="M111.437 105.311C117.824 105.311 123.002 100.068 123.002 93.5996C123.002 87.1312 117.824 81.8875 111.437 81.8875C105.049 81.8875 99.8712 87.1312 99.8712 93.5996C99.8712 100.068 105.049 105.311 111.437 105.311Z" fill="#AF0C37"/>
            </svg>
        </div>
        """, unsafe_allow_html=True)
        
        # Título e subtítulo - centralizados com NinaDash em vermelho
        st.markdown("""
        <div style="text-align: center; margin-bottom: 28px;">
            <h1 style="font-size: 24px; font-weight: 600; color: #1F2937; margin: 0 0 4px; line-height: 1.3;">
                Bem-vindo ao <span style="color: #AF0C37;">NinaDash</span>
            </h1>
            <p style="font-size: 14px; color: #6B7280; margin: 0; line-height: 1.4;">
                Plataforma de Qualidade e Decisão de Software
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Formulário de login
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input(
                "E-mail corporativo",
                placeholder="seu.nome@empresa.com.br",
                help="Utilize seu e-mail corporativo para acessar"
            )
            
            st.markdown(
                '<p style="text-align: center; font-size: 12px; color: #9CA3AF; margin: 16px 0 8px;">'
                '🔐 Acesso restrito a colaboradores</p>',
                unsafe_allow_html=True
            )
            
            submitted = st.form_submit_button("Entrar", use_container_width=True)
            
            if submitted:
                if not email:
                    st.error("Por favor, informe seu e-mail corporativo")
                elif "@" not in email:
                    st.error("E-mail inválido")
                else:
                    with st.spinner("Verificando..."):
                        if fazer_login(email):
                            st.success(f"Bem-vindo(a), {st.session_state.user_nome}!")
                            st.rerun()
                        else:
                            st.error("E-mail não autorizado. Utilize seu e-mail corporativo.")
        
        # Rodapé
        st.markdown("""
        <div style="text-align: center; margin-top: 24px; padding: 12px; background: #F8F9FA; border-radius: 8px; font-size: 12px; color: #6B7280;">
            🔒 Acesso restrito – dados protegidos
        </div>
        
        <p style="text-align: center; font-size: 11px; color: #9CA3AF; margin-top: 16px;">
            © 2026 NINA Tecnologia
        </p>
        """, unsafe_allow_html=True)


def mostrar_tooltip(metrica_key: str):
    """Mostra tooltip explicativo de uma métrica."""
    if metrica_key not in TOOLTIPS:
        return
    
    tooltip = TOOLTIPS[metrica_key]
    with st.expander(f"ℹ️ O que é {tooltip['titulo']}?", expanded=False):
        st.markdown(f"**{tooltip['descricao']}**")
        st.code(tooltip['formula'], language="text")
        st.markdown("**Interpretação:**")
        for nivel, desc in tooltip['interpretacao'].items():
            st.markdown(f"- {nivel}: {desc}")
        st.caption(f"📚 Fonte: {tooltip['fonte']}")


# ==============================================================================
# CACHE E AUTO-LOAD
# ==============================================================================

@st.cache_data(ttl=300, show_spinner=False)
def buscar_dados_jira_cached(projeto: str, jql: str) -> Tuple[Optional[List[Dict]], datetime]:
    """Busca dados do Jira com cache."""
    secrets = get_secrets()
    if not secrets["email"] or not secrets["token"]:
        return None, datetime.now()
    
    base_url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
    headers = {"Accept": "application/json"}
    
    fields = [
        "key", "summary", "status", "issuetype", "assignee", "created", "updated",
        "resolutiondate", "priority", "project", "labels",
        CUSTOM_FIELDS["story_points"],
        CUSTOM_FIELDS["story_points_alt"],
        CUSTOM_FIELDS["sprint"],
        CUSTOM_FIELDS["bugs_encontrados"],
        CUSTOM_FIELDS["complexidade_teste"],
        CUSTOM_FIELDS["qa_responsavel"],
        CUSTOM_FIELDS["produto"],
    ]
    
    all_issues = []
    next_page_token = None
    
    try:
        while True:
            params = {
                "jql": jql,
                "maxResults": 100,
                "fields": ",".join(fields)
            }
            if next_page_token:
                params["nextPageToken"] = next_page_token
            
            response = requests.get(
                base_url, 
                headers=headers, 
                params=params, 
                auth=(secrets["email"], secrets["token"]),
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            all_issues.extend(data.get("issues", []))
            
            next_page_token = data.get("nextPageToken")
            if not next_page_token or len(all_issues) >= 500:
                break
        
        return all_issues, datetime.now()
    
    except Exception as e:
        st.error(f"Erro ao conectar com Jira: {e}")
        return None, datetime.now()


@st.cache_data(ttl=300, show_spinner=False)
def buscar_card_especifico(ticket_id: str) -> Tuple[Optional[Dict], Optional[List[Dict]], Optional[List[Dict]]]:
    """
    Busca um card específico pelo ID, sem filtros de período.
    Retorna: (issue, links, comentarios)
    """
    secrets = get_secrets()
    if not secrets["email"] or not secrets["token"]:
        return None, None, None
    
    try:
        # Busca o card específico com links
        base_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}"
        headers = {"Accept": "application/json"}
        
        fields = [
            "key", "summary", "status", "issuetype", "assignee", "created", "updated",
            "resolutiondate", "priority", "project", "labels", "issuelinks", "parent", "subtasks",
            "description",
            CUSTOM_FIELDS["story_points"],
            CUSTOM_FIELDS["story_points_alt"],
            CUSTOM_FIELDS["sprint"],
            CUSTOM_FIELDS["bugs_encontrados"],
            CUSTOM_FIELDS["complexidade_teste"],
            CUSTOM_FIELDS["qa_responsavel"],
            CUSTOM_FIELDS["produto"],
        ]
        
        params = {"fields": ",".join(fields), "expand": "renderedFields"}
        
        response = requests.get(
            base_url,
            headers=headers,
            params=params,
            auth=(secrets["email"], secrets["token"]),
            timeout=30
        )
        
        if response.status_code == 404:
            return None, None, None
        
        response.raise_for_status()
        issue = response.json()
        
        # Extrai os links do card
        links = []
        fields_data = issue.get('fields', {})
        
        # Links diretos (issuelinks)
        issue_links = fields_data.get('issuelinks', [])
        for link in issue_links:
            link_type = link.get('type', {}).get('name', 'Relacionado')
            
            # Link de saída (outwardIssue)
            if 'outwardIssue' in link:
                linked = link['outwardIssue']
                links.append({
                    'tipo': link_type,
                    'direcao': link.get('type', {}).get('outward', 'relacionado a'),
                    'ticket_id': linked.get('key', ''),
                    'titulo': linked.get('fields', {}).get('summary', ''),
                    'status': linked.get('fields', {}).get('status', {}).get('name', ''),
                    'link': f"{JIRA_BASE_URL}/browse/{linked.get('key', '')}"
                })
            
            # Link de entrada (inwardIssue)
            if 'inwardIssue' in link:
                linked = link['inwardIssue']
                links.append({
                    'tipo': link_type,
                    'direcao': link.get('type', {}).get('inward', 'relacionado a'),
                    'ticket_id': linked.get('key', ''),
                    'titulo': linked.get('fields', {}).get('summary', ''),
                    'status': linked.get('fields', {}).get('status', {}).get('name', ''),
                    'link': f"{JIRA_BASE_URL}/browse/{linked.get('key', '')}"
                })
        
        # Parent (Epic/Story pai)
        parent = fields_data.get('parent')
        if parent:
            links.append({
                'tipo': 'Parent',
                'direcao': 'é filho de',
                'ticket_id': parent.get('key', ''),
                'titulo': parent.get('fields', {}).get('summary', ''),
                'status': parent.get('fields', {}).get('status', {}).get('name', ''),
                'link': f"{JIRA_BASE_URL}/browse/{parent.get('key', '')}"
            })
        
        # Subtasks (tarefas filhas)
        subtasks = fields_data.get('subtasks', [])
        for sub in subtasks:
            links.append({
                'tipo': 'Subtask',
                'direcao': 'é pai de',
                'ticket_id': sub.get('key', ''),
                'titulo': sub.get('fields', {}).get('summary', ''),
                'status': sub.get('fields', {}).get('status', {}).get('name', ''),
                'link': f"{JIRA_BASE_URL}/browse/{sub.get('key', '')}"
            })
        
        # Busca comentários do card
        comentarios = []
        try:
            comments_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}/comment"
            comments_response = requests.get(
                comments_url,
                headers=headers,
                auth=(secrets["email"], secrets["token"]),
                timeout=15
            )
            if comments_response.status_code == 200:
                comments_data = comments_response.json()
                for comment in comments_data.get('comments', []):
                    author = comment.get('author', {})
                    author_type = author.get('accountType', 'user')
                    
                    # Filtra comentários de automações (bots, apps)
                    # accountType: 'atlassian' = usuário, 'app' = automação
                    if author_type == 'app':
                        continue
                    
                    # Também ignora se o displayName contém patterns de automação
                    display_name = author.get('displayName', '')
                    bot_patterns = ['bot', 'automation', 'jira', 'webhook', 'integration', 'service']
                    is_bot = any(pattern.lower() in display_name.lower() for pattern in bot_patterns)
                    if is_bot:
                        continue
                    
                    # Extrai texto do corpo do comentário (formato ADF)
                    body = comment.get('body', {})
                    body_text = extrair_texto_adf(body)
                    
                    if body_text.strip():
                        comentarios.append({
                            'autor': display_name,
                            'avatar': author.get('avatarUrls', {}).get('24x24', ''),
                            'data': comment.get('created', ''),
                            'texto': body_text
                        })
        except Exception:
            pass  # Comentários são opcionais
        
        return issue, links, comentarios
    
    except Exception as e:
        st.error(f"Erro ao buscar card: {e}")
        return None, None, None


def extrair_texto_adf(adf_content: Dict) -> str:
    """Extrai texto plano de conteúdo ADF (Atlassian Document Format)."""
    if not adf_content:
        return ""
    
    texto = []
    
    def extrair_recursivo(node):
        if isinstance(node, dict):
            if node.get('type') == 'text':
                texto.append(node.get('text', ''))
            elif node.get('type') == 'hardBreak':
                texto.append('\n')
            elif node.get('type') == 'mention':
                texto.append(f"@{node.get('attrs', {}).get('text', '')}")
            
            for child in node.get('content', []):
                extrair_recursivo(child)
        elif isinstance(node, list):
            for item in node:
                extrair_recursivo(item)
    
    extrair_recursivo(adf_content)
    return ' '.join(texto).strip()


def processar_issue_unica(issue: Dict) -> Dict:
    """Processa uma issue única do Jira para dicionário de dados."""
    hoje = datetime.now()
    f = issue.get('fields', {})
    
    # Tipo do ticket
    tipo_original = f.get('issuetype', {}).get('name', 'Desconhecido')
    tipo = "TAREFA"
    if any(t in tipo_original for t in ["Hotfix", "Hotfeature"]):
        tipo = "HOTFIX"
    elif any(t in tipo_original for t in ["Bug", "Impeditivo"]):
        tipo = "BUG"
    elif "Sugestão" in tipo_original:
        tipo = "SUGESTÃO"
    
    # Projeto
    projeto = f.get('project', {}).get('key', 'N/A')
    
    # Desenvolvedor
    dev = f.get('assignee', {}).get('displayName', 'Não atribuído') if f.get('assignee') else 'Não atribuído'
    
    # Story Points
    sp = f.get(CUSTOM_FIELDS['story_points']) or f.get(CUSTOM_FIELDS['story_points_alt']) or 0
    sp_original = bool(f.get(CUSTOM_FIELDS['story_points']) or f.get(CUSTOM_FIELDS['story_points_alt']))
    sp_estimado = False  # Flag para indicar se SP foi estimado pela regra de Hotfix
    if sp == 0 and tipo == "HOTFIX":
        sp = REGRAS["hotfix_sp_default"]
        sp_estimado = True  # SP calculado automaticamente
    
    # Sprint
    sprint_f = f.get(CUSTOM_FIELDS['sprint'], [])
    sprint = sprint_f[-1].get('name', 'Sem Sprint') if sprint_f else 'Sem Sprint'
    sprint_end = None
    if sprint_f:
        sprint_end_str = sprint_f[-1].get('endDate')
        if sprint_end_str:
            try:
                sprint_end = datetime.fromisoformat(sprint_end_str.replace('Z', '+00:00')).replace(tzinfo=None)
            except:
                pass
    
    # Status
    status = f.get('status', {}).get('name', 'Desconhecido')
    status_cat = 'unknown'
    for cat, statuses in STATUS_FLOW.items():
        if any(s.lower() == status.lower() for s in statuses):
            status_cat = cat
            break
    
    # Bugs
    bugs = f.get(CUSTOM_FIELDS['bugs_encontrados']) or 0
    
    # Complexidade
    comp = f.get(CUSTOM_FIELDS['complexidade_teste'])
    complexidade = comp.get('value', '') if isinstance(comp, dict) else ''
    
    # QA
    qa_f = f.get(CUSTOM_FIELDS['qa_responsavel'])
    qa = 'Não atribuído'
    if qa_f:
        if isinstance(qa_f, dict):
            qa = qa_f.get('displayName', 'Não atribuído')
        elif isinstance(qa_f, list) and qa_f:
            qa = qa_f[0].get('displayName', 'Não atribuído')
    
    # Produto
    produto_f = f.get(CUSTOM_FIELDS['produto'], [])
    produtos = [p.get('value', '') for p in produto_f] if produto_f else []
    produto = produtos[0] if produtos else 'Não definido'
    
    # Datas
    try:
        criado = datetime.fromisoformat(f.get('created', '').replace('Z', '+00:00')).replace(tzinfo=None)
    except:
        criado = hoje
    
    try:
        atualizado = datetime.fromisoformat(f.get('updated', '').replace('Z', '+00:00')).replace(tzinfo=None)
    except:
        atualizado = hoje
    
    resolutiondate = None
    if f.get('resolutiondate'):
        try:
            resolutiondate = datetime.fromisoformat(f.get('resolutiondate').replace('Z', '+00:00')).replace(tzinfo=None)
        except:
            pass
    
    # Métricas calculadas
    dias_em_status = (hoje - atualizado).days
    lead_time = (resolutiondate - criado).days if resolutiondate else (hoje - criado).days
    
    # Dias até release
    dias_ate_release = 0
    if sprint_end:
        dias_ate_release = max(0, (sprint_end - hoje).days)
    
    # Janela de validação
    janela_info = avaliar_janela_validacao(dias_ate_release, complexidade)
    
    ticket_id = issue.get('key', '')
    
    return {
        'ticket_id': ticket_id,
        'link': link_jira(ticket_id),
        'titulo': f.get('summary', ''),
        'tipo': tipo,
        'tipo_original': tipo_original,
        'status': status,
        'status_cat': status_cat,
        'projeto': projeto,
        'desenvolvedor': dev,
        'qa': qa,
        'sp': int(sp) if sp else 0,
        'sp_original': sp_original,
        'sp_estimado': sp_estimado,  # True quando SP foi calculado pela regra de Hotfix
        'bugs': int(bugs) if bugs else 0,
        'sprint': sprint,
        'prioridade': f.get('priority', {}).get('name', 'Média') if f.get('priority') else 'Média',
        'complexidade': complexidade,
        'produto': produto,
        'criado': criado,
        'atualizado': atualizado,
        'resolutiondate': resolutiondate,
        'dias_em_status': dias_em_status,
        'lead_time': lead_time,
        'dias_ate_release': dias_ate_release,
        'dentro_janela': janela_info["dentro_janela"],
        'janela_status': janela_info["status"],
        'janela_dias_necessarios': janela_info["dias_necessarios"],
        'sp_preenchido': sp_original,
        'bugs_preenchido': f.get(CUSTOM_FIELDS['bugs_encontrados']) is not None,
        'complexidade_preenchida': bool(complexidade),
        'qa_preenchido': qa != 'Não atribuído',
        'criado_na_sprint': False,  # Simplificado para card individual
        'finalizado_mesma_sprint': False,
        'adicionado_fora_periodo': False,
    }


def processar_issues(issues: List[Dict]) -> pd.DataFrame:
    """Processa issues do Jira para DataFrame."""
    dados = []
    hoje = datetime.now()
    
    for issue in issues:
        f = issue.get('fields', {})
        
        # Tipo do ticket
        tipo_original = f.get('issuetype', {}).get('name', 'Desconhecido')
        tipo = "TAREFA"
        if any(t in tipo_original for t in ["Hotfix", "Hotfeature"]):
            tipo = "HOTFIX"
        elif any(t in tipo_original for t in ["Bug", "Impeditivo"]):
            tipo = "BUG"
        elif "Sugestão" in tipo_original:
            tipo = "SUGESTÃO"
        
        # Projeto
        projeto = f.get('project', {}).get('key', 'N/A')
        
        # Desenvolvedor
        dev = f.get('assignee', {}).get('displayName', 'Não atribuído') if f.get('assignee') else 'Não atribuído'
        
        # Story Points - com regra de Hotfix
        sp = f.get(CUSTOM_FIELDS['story_points']) or f.get(CUSTOM_FIELDS['story_points_alt']) or 0
        sp_original = bool(f.get(CUSTOM_FIELDS['story_points']) or f.get(CUSTOM_FIELDS['story_points_alt']))
        if sp == 0 and tipo == "HOTFIX":
            sp = REGRAS["hotfix_sp_default"]
        
        # Sprint
        sprint_f = f.get(CUSTOM_FIELDS['sprint'], [])
        sprint = sprint_f[-1].get('name', 'Sem Sprint') if sprint_f else 'Sem Sprint'
        sprint_id = sprint_f[-1].get('id') if sprint_f else None
        sprint_start = None
        sprint_end = None
        if sprint_f:
            sprint_start_str = sprint_f[-1].get('startDate')
            sprint_end_str = sprint_f[-1].get('endDate')
            if sprint_start_str:
                try:
                    sprint_start = datetime.fromisoformat(sprint_start_str.replace('Z', '+00:00')).replace(tzinfo=None)
                except:
                    pass
            if sprint_end_str:
                try:
                    sprint_end = datetime.fromisoformat(sprint_end_str.replace('Z', '+00:00')).replace(tzinfo=None)
                except:
                    pass
        
        # Status
        status = f.get('status', {}).get('name', 'Desconhecido')
        status_cat = 'unknown'
        for cat, statuses in STATUS_FLOW.items():
            if any(s.lower() == status.lower() for s in statuses):
                status_cat = cat
                break
        
        # Bugs
        bugs = f.get(CUSTOM_FIELDS['bugs_encontrados']) or 0
        
        # Complexidade
        comp = f.get(CUSTOM_FIELDS['complexidade_teste'])
        complexidade = comp.get('value', '') if isinstance(comp, dict) else ''
        
        # QA
        qa_f = f.get(CUSTOM_FIELDS['qa_responsavel'])
        qa = 'Não atribuído'
        if qa_f:
            if isinstance(qa_f, dict):
                qa = qa_f.get('displayName', 'Não atribuído')
            elif isinstance(qa_f, list) and qa_f:
                qa = qa_f[0].get('displayName', 'Não atribuído')
        
        # Produto
        produto_f = f.get(CUSTOM_FIELDS['produto'], [])
        produtos = [p.get('value', '') for p in produto_f] if produto_f else []
        produto = produtos[0] if produtos else 'Não definido'
        
        # Datas
        try:
            criado = datetime.fromisoformat(f.get('created', '').replace('Z', '+00:00')).replace(tzinfo=None)
        except:
            criado = hoje
        
        try:
            atualizado = datetime.fromisoformat(f.get('updated', '').replace('Z', '+00:00')).replace(tzinfo=None)
        except:
            atualizado = hoje
        
        resolutiondate = None
        if f.get('resolutiondate'):
            try:
                resolutiondate = datetime.fromisoformat(f.get('resolutiondate').replace('Z', '+00:00')).replace(tzinfo=None)
            except:
                pass
        
        # Métricas calculadas
        dias_em_status = (hoje - atualizado).days
        lead_time = (resolutiondate - criado).days if resolutiondate else (hoje - criado).days
        
        # Dias até release
        dias_ate_release = 0
        if sprint_end:
            dias_ate_release = max(0, (sprint_end - hoje).days)
        
        # MÉTRICAS Ellen/Produto
        criado_na_sprint = False
        if sprint_start and sprint_end:
            criado_na_sprint = sprint_start <= criado <= sprint_end
        
        finalizado_mesma_sprint = False
        if status_cat == 'done' and criado_na_sprint:
            finalizado_mesma_sprint = True
        
        adicionado_fora_periodo = False
        if sprint_start and criado > sprint_start + timedelta(days=2):
            adicionado_fora_periodo = True
        
        # Janela de validação inteligente (considera complexidade de teste)
        janela_info = avaliar_janela_validacao(dias_ate_release, complexidade)
        dentro_janela = janela_info["dentro_janela"]
        janela_status = janela_info["status"]  # 'ok', 'risco', 'fora'
        janela_dias_necessarios = janela_info["dias_necessarios"]
        
        # Flags de preenchimento
        sp_preenchido = sp_original
        bugs_preenchido = f.get(CUSTOM_FIELDS['bugs_encontrados']) is not None
        complexidade_preenchida = bool(complexidade)
        qa_preenchido = qa != 'Não atribuído'
        
        ticket_id = issue.get('key', '')
        
        dados.append({
            'ticket_id': ticket_id,
            'link': link_jira(ticket_id),
            'titulo': f.get('summary', ''),
            'tipo': tipo,
            'tipo_original': tipo_original,
            'status': status,
            'status_cat': status_cat,
            'projeto': projeto,
            'desenvolvedor': dev,
            'qa': qa,
            'sp': int(sp) if sp else 0,
            'sp_original': sp_original,
            'bugs': int(bugs) if bugs else 0,
            'sprint': sprint,
            'sprint_id': sprint_id,
            'sprint_start': sprint_start,
            'sprint_end': sprint_end,
            'prioridade': f.get('priority', {}).get('name', 'Média') if f.get('priority') else 'Média',
            'complexidade': complexidade,
            'produto': produto,
            'produtos': produtos,
            'criado': criado,
            'atualizado': atualizado,
            'resolutiondate': resolutiondate,
            'dias_em_status': dias_em_status,
            'lead_time': lead_time,
            'dias_ate_release': dias_ate_release,
            'dentro_janela': dentro_janela,
            'janela_status': janela_status,
            'janela_dias_necessarios': janela_dias_necessarios,
            # Flags de preenchimento
            'sp_preenchido': sp_preenchido,
            'bugs_preenchido': bugs_preenchido,
            'complexidade_preenchida': complexidade_preenchida,
            'qa_preenchido': qa_preenchido,
            # Novas métricas Ellen
            'criado_na_sprint': criado_na_sprint,
            'finalizado_mesma_sprint': finalizado_mesma_sprint,
            'adicionado_fora_periodo': adicionado_fora_periodo,
        })
    
    return pd.DataFrame(dados)


# ==============================================================================
# FUNÇÕES DE MÉTRICAS
# ==============================================================================

def calcular_fator_k(sp: int, bugs: int) -> float:
    """Calcula Fator K = SP / (Bugs + 1)"""
    if sp == 0:
        return 0
    return round(sp / (bugs + 1), 2)


def classificar_maturidade(fk: float) -> Dict:
    """Classifica maturidade baseado no Fator K."""
    if fk >= 3.0:
        return {"selo": "Gold", "emoji": "🥇", "cor": "#22c55e", "desc": "Excelente"}
    elif fk >= 2.0:
        return {"selo": "Silver", "emoji": "🥈", "cor": "#eab308", "desc": "Bom"}
    elif fk >= 1.0:
        return {"selo": "Bronze", "emoji": "🥉", "cor": "#f97316", "desc": "Regular"}
    else:
        return {"selo": "Risco", "emoji": "⚠️", "cor": "#ef4444", "desc": "Crítico"}


def calcular_ddp(df: pd.DataFrame) -> Dict:
    """Defect Detection Percentage."""
    bugs_qa = df['bugs'].sum()
    bugs_estimados_prod = max(1, len(df) * 0.05)
    total_bugs = bugs_qa + bugs_estimados_prod
    ddp = (bugs_qa / total_bugs * 100) if total_bugs > 0 else 100
    return {"valor": round(ddp, 1), "bugs_qa": int(bugs_qa)}


def calcular_fpy(df: pd.DataFrame) -> Dict:
    """First Pass Yield."""
    total = len(df)
    if total == 0:
        return {"valor": 0, "sem_bugs": 0, "total": 0}
    sem_bugs = len(df[df['bugs'] == 0])
    fpy = sem_bugs / total * 100
    return {"valor": round(fpy, 1), "sem_bugs": sem_bugs, "total": total}


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


def analisar_dev_detalhado(df: pd.DataFrame, dev_nome: str) -> Optional[Dict]:
    """Análise completa de um desenvolvedor."""
    df_dev = df[df['desenvolvedor'] == dev_nome]
    if df_dev.empty:
        return None
    
    sp_total = int(df_dev['sp'].sum())
    bugs_total = int(df_dev['bugs'].sum())
    
    fk_medio = calcular_fator_k(sp_total, bugs_total)
    maturidade = classificar_maturidade(fk_medio)
    
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


def calcular_metricas_governanca(df: pd.DataFrame) -> Dict:
    """Calcula métricas de governança de dados."""
    total = len(df)
    if total == 0:
        return {
            "sp": {"preenchido": 0, "total": 0, "pct": 0, "faltando": []},
            "bugs": {"preenchido": 0, "total": 0, "pct": 0, "faltando": []},
            "complexidade": {"preenchido": 0, "total": 0, "pct": 0, "faltando": []},
            "qa": {"preenchido": 0, "total": 0, "pct": 0, "faltando": []},
        }
    
    df_sem_hotfix = df[df['tipo'] != 'HOTFIX']
    total_sem_hotfix = len(df_sem_hotfix)
    
    return {
        "sp": {
            "preenchido": int(df_sem_hotfix['sp_preenchido'].sum()) if total_sem_hotfix > 0 else 0,
            "total": total_sem_hotfix,
            "pct": round(df_sem_hotfix['sp_preenchido'].sum() / total_sem_hotfix * 100, 1) if total_sem_hotfix > 0 else 0,
            "faltando": df_sem_hotfix[~df_sem_hotfix['sp_preenchido']][['ticket_id', 'titulo', 'desenvolvedor', 'link']].to_dict('records') if total_sem_hotfix > 0 else []
        },
        "bugs": {
            "preenchido": int(df['bugs_preenchido'].sum()),
            "total": total,
            "pct": round(df['bugs_preenchido'].sum() / total * 100, 1),
            "faltando": df[~df['bugs_preenchido']][['ticket_id', 'titulo', 'desenvolvedor', 'link']].to_dict('records')
        },
        "complexidade": {
            "preenchido": int(df['complexidade_preenchida'].sum()),
            "total": total,
            "pct": round(df['complexidade_preenchida'].sum() / total * 100, 1),
            "faltando": df[~df['complexidade_preenchida']][['ticket_id', 'titulo', 'desenvolvedor', 'link']].to_dict('records')
        },
        "qa": {
            "preenchido": int(df['qa_preenchido'].sum()),
            "total": total,
            "pct": round(df['qa_preenchido'].sum() / total * 100, 1),
            "faltando": df[~df['qa_preenchido']][['ticket_id', 'titulo', 'desenvolvedor', 'link']].to_dict('records')
        },
    }


def calcular_metricas_qa(df: pd.DataFrame) -> Dict:
    """Calcula métricas específicas de QA."""
    waiting_qa = df[df['status_cat'] == 'waiting_qa']
    testing = df[df['status_cat'] == 'testing']
    done = df[df['status_cat'] == 'done']
    blocked = df[df['status_cat'] == 'blocked']
    rejected = df[df['status_cat'] == 'rejected']
    
    tempo_waiting = waiting_qa['dias_em_status'].mean() if not waiting_qa.empty else 0
    tempo_testing = testing['dias_em_status'].mean() if not testing.empty else 0
    
    aging_waiting = waiting_qa[waiting_qa['dias_em_status'] >= REGRAS['dias_aging_alerta']]
    aging_testing = testing[testing['dias_em_status'] >= REGRAS['dias_aging_alerta']]
    
    carga_qa = df[df['status_cat'].isin(['waiting_qa', 'testing'])].groupby('qa').agg({
        'ticket_id': 'count',
        'sp': 'sum'
    }).reset_index()
    carga_qa.columns = ['QA', 'Cards', 'SP']
    
    total_validados = len(done) + len(rejected)
    taxa_reprovacao = len(rejected) / total_validados * 100 if total_validados > 0 else 0
    
    return {
        "funil": {
            "waiting_qa": len(waiting_qa),
            "testing": len(testing),
            "done": len(done),
            "blocked": len(blocked),
            "rejected": len(rejected),
        },
        "tempo": {
            "waiting": round(tempo_waiting, 1),
            "testing": round(tempo_testing, 1),
        },
        "aging": {
            "waiting": aging_waiting,
            "testing": aging_testing,
            "total": len(aging_waiting) + len(aging_testing),
        },
        "carga_qa": carga_qa,
        "taxa_reprovacao": round(taxa_reprovacao, 1),
        "fila_completa": waiting_qa,
        "em_teste": testing,
    }


def calcular_metricas_produto(df: pd.DataFrame) -> Dict:
    """Calcula métricas específicas por produto (métricas Ellen)."""
    hotfix_por_produto = df[df['tipo'] == 'HOTFIX'].groupby('produto').size().reset_index(name='hotfixes')
    finalizados_mesma_sprint = df[df['finalizado_mesma_sprint'] == True]
    adicionados_fora = df[df['adicionado_fora_periodo'] == True]
    
    return {
        "hotfix_por_produto": hotfix_por_produto,
        "finalizados_mesma_sprint": finalizados_mesma_sprint,
        "adicionados_fora": adicionados_fora,
        "total_finalizados_mesma_sprint": len(finalizados_mesma_sprint),
        "total_adicionados_fora": len(adicionados_fora),
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
    fpy = calcular_fpy(df)
    score_fpy = min(20, fpy['valor'] * 0.2)
    detalhes['fpy'] = {'peso': 20, 'score': round(score_fpy, 1), 'valor': f"{fpy['valor']}%"}
    
    # 4. Gargalos (peso 15)
    metricas_qa = calcular_metricas_qa(df)
    penalidade = metricas_qa['aging']['total'] * 3
    score_gargalos = max(0, 15 - penalidade)
    detalhes['gargalos'] = {'peso': 15, 'score': score_gargalos, 'valor': f"{metricas_qa['aging']['total']} aging"}
    
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


def calcular_metricas_dev(df: pd.DataFrame) -> Dict:
    """Calcula métricas por desenvolvedor."""
    dev_stats = df.groupby('desenvolvedor').agg({
        'ticket_id': 'count',
        'sp': 'sum',
        'bugs': 'sum',
    }).reset_index()
    dev_stats.columns = ['Desenvolvedor', 'Cards', 'SP', 'Bugs']
    dev_stats['FK'] = dev_stats.apply(lambda x: calcular_fator_k(x['SP'], x['Bugs']), axis=1)
    dev_stats['Maturidade'] = dev_stats['FK'].apply(lambda x: classificar_maturidade(x)['selo'])
    
    return {"stats": dev_stats.sort_values('Cards', ascending=False)}


# ==============================================================================
# BUSCA E DETALHES DO CARD
# ==============================================================================

def exibir_card_detalhado_v2(card: Dict, links: List[Dict], comentarios: List[Dict], projeto: str = "SD") -> bool:
    """
    Exibe painel detalhado com informações de um card específico.
    Adapta o conteúdo conforme o projeto:
    - SD: Completo (bugs, FK, qualidade, janela, comentários)
    - QA: Foco em aging, automação, tempo parado
    - PB: Backlog - sem bugs, foco em prioridade e estimativa
    """
    if not card:
        return False
    
    # Gera URL de compartilhamento
    base_url = "https://plataforma-de-qualidade-e-decis-o-de-software-8ze3ycurhvmdahdv.streamlit.app/"
    share_url = f"{base_url}?card={card['ticket_id']}&projeto={projeto}"
    
    # ===== HEADER DO CARD =====
    # Cor do header varia por projeto
    header_colors = {
        "SD": ("linear-gradient(135deg, #AF0C37 0%, #8a0a2c 100%)", "🔍"),
        "QA": ("linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)", "🤖"),
        "PB": ("linear-gradient(135deg, #059669 0%, #047857 100%)", "📋")
    }
    header_bg, header_icon = header_colors.get(projeto, header_colors["SD"])
    
    st.markdown(f"""
    <div style='background: {header_bg}; 
                color: white; padding: 20px; border-radius: 12px; margin-bottom: 15px;'>
        <h2 style='margin: 0; color: white; font-size: 1.5em;'>
            {header_icon} {card['ticket_id']}
        </h2>
        <p style='margin: 8px 0 0 0; opacity: 0.9; font-size: 0.95em;'>
            {card['titulo'][:120]}{'...' if len(card['titulo']) > 120 else ''}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== BOTÕES DE AÇÃO =====
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        st.link_button("🔗 Abrir no Jira", card['link'], use_container_width=True)
    
    with col2:
        # Usar components.html para JavaScript funcionar (iframe isolado)
        components.html(f"""
        <button id="copyBtn" style="
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            border: none;
            padding: 10px 16px;
            border-radius: 6px;
            cursor: pointer;
            width: 100%;
            font-size: 14px;
            font-weight: 500;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            transition: all 0.2s ease;
        ">📋 Copiar Link</button>
        <script>
            document.getElementById('copyBtn').addEventListener('click', function() {{
                var url = '{share_url}';
                var btn = this;
                navigator.clipboard.writeText(url).then(function() {{
                    btn.innerHTML = '✅ Copiado!';
                    btn.style.background = 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)';
                    setTimeout(function() {{
                        btn.innerHTML = '📋 Copiar Link';
                        btn.style.background = 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)';
                    }}, 2000);
                }}).catch(function() {{
                    // Fallback
                    var temp = document.createElement('textarea');
                    temp.value = url;
                    document.body.appendChild(temp);
                    temp.select();
                    document.execCommand('copy');
                    document.body.removeChild(temp);
                    btn.innerHTML = '✅ Copiado!';
                    btn.style.background = 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)';
                    setTimeout(function() {{
                        btn.innerHTML = '📋 Copiar Link';
                        btn.style.background = 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)';
                    }}, 2000);
                }});
            }});
        </script>
        """, height=45)
    
    with col3:
        st.caption(f"Sprint: **{card['sprint']}** | Produto: **{card['produto']}**")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========================================================================
    # CONTEÚDO ESPECÍFICO POR PROJETO
    # ========================================================================
    
    if projeto == "SD":
        exibir_detalhes_sd(card, links, comentarios)
    elif projeto == "QA":
        exibir_detalhes_qa(card, links, comentarios)
    elif projeto == "PB":
        exibir_detalhes_pb(card, links, comentarios)
    else:
        exibir_detalhes_sd(card, links, comentarios)  # Fallback
    
    return True


def exibir_detalhes_sd(card: Dict, links: List[Dict], comentarios: List[Dict]):
    """Exibe detalhes para projeto SD (Service Desk) - Completo com qualidade."""
    
    # ===== KPIs PRINCIPAIS (CARDS ESTILIZADOS) =====
    fk = calcular_fator_k(card['sp'], card['bugs'])
    mat = classificar_maturidade(fk)
    
    # Cores por status
    status_cores = {
        "Done": "#22c55e", "Concluído": "#22c55e",
        "Em Validação": "#3b82f6", "Aguardando Validação": "#f59e0b",
        "Desenvolvimento": "#8b5cf6", "Code Review": "#ec4899",
        "Blocked": "#ef4444", "Reprovado": "#ef4444"
    }
    status_cor = status_cores.get(card['status'], "#6b7280")
    
    st.markdown(f"""
    <div style='display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;'>
        <div style='background: linear-gradient(135deg, {status_cor}15, {status_cor}05); border: 1px solid {status_cor}40; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>📌</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Status</div>
            <div style='font-size: 14px; font-weight: 600; color: {status_cor}; margin-top: 4px; word-wrap: break-word;'>{card['status']}</div>
        </div>
        <div style='background: linear-gradient(135deg, #6366f115, #6366f105); border: 1px solid #6366f140; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>🎯</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Tipo</div>
            <div style='font-size: 14px; font-weight: 600; color: #6366f1; margin-top: 4px;'>{card['tipo']}</div>
        </div>
        <div style='background: linear-gradient(135deg, #f9731615, #f9731605); border: 1px solid #f9731640; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>⚡</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Prioridade</div>
            <div style='font-size: 14px; font-weight: 600; color: #f97316; margin-top: 4px;'>{card['prioridade']}</div>
        </div>
        <div style='background: linear-gradient(135deg, {mat['cor']}15, {mat['cor']}05); border: 1px solid {mat['cor']}40; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>🎖️</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Fator K</div>
            <div style='font-size: 14px; font-weight: 600; color: {mat['cor']}; margin-top: 4px;'>{fk:.2f} {mat['emoji']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== INFORMAÇÕES BÁSICAS =====
    with st.expander("📋 **Informações Básicas**", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
| Campo | Valor |
|-------|-------|
| **Projeto** | {card['projeto']} |
| **Sprint** | {card['sprint']} |
| **Produto** | {card['produto']} |
| **Tipo Original** | {card['tipo_original']} |
            """)
        
        with col2:
            # Indicador visual se SP foi estimado pela regra de Hotfix
            sp_display = f"{card['sp']} ⚠️ *estimado*" if card.get('sp_estimado', False) else str(card['sp'])
            st.markdown(f"""
| Campo | Valor |
|-------|-------|
| **Desenvolvedor** | {card['desenvolvedor']} |
| **QA Responsável** | {card['qa']} |
| **Story Points** | {sp_display} |
| **Complexidade** | {card['complexidade'] if card['complexidade'] else 'Não definida'} |
            """)
    
    # ===== MÉTRICAS DE QUALIDADE =====
    with st.expander("📊 **Métricas de Qualidade**", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        fk = calcular_fator_k(card['sp'], card['bugs'])
        mat = classificar_maturidade(fk)
        
        with col1:
            st.markdown(f"""
<div style='background: {mat['cor']}15; padding: 12px; border-radius: 8px; text-align: center; border-left: 3px solid {mat['cor']}; margin-bottom: 8px;'>
    <h3 style='margin:0; color: {mat['cor']}; font-size: 1.4em;'>{fk:.2f}</h3>
    <small style='color: #666;'>Fator K</small><br>
    <span style='font-size: 18px;'>{mat['emoji']}</span>
    <small style='color: {mat['cor']};'>{mat['desc']}</small>
</div>
            """, unsafe_allow_html=True)
        
        with col2:
            bugs_cor = "#22c55e" if card['bugs'] == 0 else "#f97316" if card['bugs'] <= 2 else "#ef4444"
            st.markdown(f"""
<div style='background: {bugs_cor}15; padding: 12px; border-radius: 8px; text-align: center; border-left: 3px solid {bugs_cor}; margin-bottom: 8px;'>
    <h3 style='margin:0; color: {bugs_cor}; font-size: 1.4em;'>{card['bugs']}</h3>
    <small style='color: #666;'>Bugs</small><br>
    <span style='font-size: 18px;'>{'✅' if card['bugs'] == 0 else '⚠️' if card['bugs'] <= 2 else '🐛'}</span>
</div>
            """, unsafe_allow_html=True)
        
        with col3:
            sp_estimado_aviso = "<br><small style='color: #f59e0b;'>⚠️ Estimado</small>" if card.get('sp_estimado', False) else ""
            st.markdown(f"""
<div style='background: #3b82f615; padding: 12px; border-radius: 8px; text-align: center; border-left: 3px solid #3b82f6; margin-bottom: 8px;'>
    <h3 style='margin:0; color: #3b82f6; font-size: 1.4em;'>{card['sp']}</h3>
    <small style='color: #666;'>Story Points</small>{sp_estimado_aviso}<br>
    <span style='font-size: 18px;'>{'🎯' if card['sp'] > 0 else '❓'}</span>
</div>
            """, unsafe_allow_html=True)
        
        with col4:
            fpy_individual = 100 if card['bugs'] == 0 else 0
            fpy_cor = "#22c55e" if fpy_individual == 100 else "#ef4444"
            st.markdown(f"""
<div style='background: {fpy_cor}15; padding: 12px; border-radius: 8px; text-align: center; border-left: 3px solid {fpy_cor}; margin-bottom: 8px;'>
    <h3 style='margin:0; color: {fpy_cor}; font-size: 1.4em;'>{fpy_individual}%</h3>
    <small style='color: #666;'>FPY</small><br>
    <span style='font-size: 18px;'>{'✅' if fpy_individual == 100 else '🔄'}</span>
</div>
            """, unsafe_allow_html=True)
    
    # ===== ANÁLISE DE TEMPO =====
    with st.expander("⏱️ **Análise de Tempo**", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            lead_cor = "#22c55e" if card['lead_time'] <= 7 else "#f97316" if card['lead_time'] <= 14 else "#ef4444"
            st.markdown(f"""
<div style='background: {lead_cor}15; padding: 12px; border-radius: 8px; text-align: center; border-left: 3px solid {lead_cor}; margin-bottom: 8px;'>
    <h3 style='margin:0; color: {lead_cor}; font-size: 1.3em;'>{card['lead_time']} dias</h3>
    <small style='color: #666;'>Lead Time</small><br>
    <span style='font-size: 16px;'>{'🚀' if card['lead_time'] <= 7 else '⏳' if card['lead_time'] <= 14 else '🐢'}</span>
    <small style='color: {lead_cor};'>{'Rápido' if card['lead_time'] <= 7 else 'Normal' if card['lead_time'] <= 14 else 'Lento'}</small>
</div>
            """, unsafe_allow_html=True)
        
        with col2:
            aging_cor = "#22c55e" if card['dias_em_status'] <= 3 else "#f97316" if card['dias_em_status'] <= 7 else "#ef4444"
            st.markdown(f"""
<div style='background: {aging_cor}15; padding: 12px; border-radius: 8px; text-align: center; border-left: 3px solid {aging_cor}; margin-bottom: 8px;'>
    <h3 style='margin:0; color: {aging_cor}; font-size: 1.3em;'>{card['dias_em_status']} dias</h3>
    <small style='color: #666;'>No Status Atual</small><br>
    <span style='font-size: 16px;'>{'✅' if card['dias_em_status'] <= 3 else '⚠️' if card['dias_em_status'] <= 7 else '🚨'}</span>
    <small style='color: {aging_cor};'>{'OK' if card['dias_em_status'] <= 3 else 'Atenção' if card['dias_em_status'] <= 7 else 'Aging'}</small>
</div>
            """, unsafe_allow_html=True)
        
        with col3:
            release_cor = "#22c55e" if card['dias_ate_release'] >= 3 else "#f97316" if card['dias_ate_release'] >= 1 else "#ef4444"
            st.markdown(f"""
<div style='background: {release_cor}15; padding: 12px; border-radius: 8px; text-align: center; border-left: 3px solid {release_cor}; margin-bottom: 8px;'>
    <h3 style='margin:0; color: {release_cor}; font-size: 1.3em;'>{card['dias_ate_release']} dias</h3>
    <small style='color: #666;'>Até Release</small><br>
    <span style='font-size: 16px;'>{'✅' if card['dias_ate_release'] >= 3 else '⚠️' if card['dias_ate_release'] >= 1 else '🚨'}</span>
</div>
            """, unsafe_allow_html=True)
        
        # Timeline
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**📅 Timeline**")
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            st.caption(f"**Criação:** {card['criado'].strftime('%d/%m/%Y') if pd.notna(card['criado']) else 'N/A'}")
        with col_t2:
            st.caption(f"**Atualização:** {card['atualizado'].strftime('%d/%m/%Y') if pd.notna(card['atualizado']) else 'N/A'}")
        with col_t3:
            st.caption(f"**Resolução:** {card['resolutiondate'].strftime('%d/%m/%Y') if pd.notna(card['resolutiondate']) else 'Pendente'}")
    
    # ===== JANELA DE VALIDAÇÃO =====
    with st.expander("🕐 **Janela de Validação**", expanded=False):
        janela_cor = "#22c55e" if card['janela_status'] == 'ok' else "#f97316" if card['janela_status'] == 'risco' else "#ef4444"
        janela_emoji = "✅" if card['janela_status'] == 'ok' else "⚠️" if card['janela_status'] == 'risco' else "🚨"
        janela_texto = "Dentro da Janela" if card['janela_status'] == 'ok' else "Janela em Risco" if card['janela_status'] == 'risco' else "Fora da Janela"
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
<div style='background: {janela_cor}15; padding: 12px; border-radius: 8px; text-align: center; border-left: 3px solid {janela_cor};'>
    <span style='font-size: 24px;'>{janela_emoji}</span>
    <h4 style='margin: 5px 0; color: {janela_cor}; font-size: 1em;'>{janela_texto}</h4>
</div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
<div style='background: #6366f115; padding: 12px; border-radius: 8px; text-align: center; border-left: 3px solid #6366f1;'>
    <h3 style='margin:0; color: #6366f1; font-size: 1.2em;'>{card['janela_dias_necessarios']}d</h3>
    <small style='color: #666;'>Necessários</small>
</div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
<div style='background: #8b5cf615; padding: 12px; border-radius: 8px; text-align: center; border-left: 3px solid #8b5cf6;'>
    <h3 style='margin:0; color: #8b5cf6; font-size: 1.2em;'>{card['dias_ate_release']}d</h3>
    <small style='color: #666;'>Disponíveis</small>
</div>
            """, unsafe_allow_html=True)
    
    # ===== RESUMO EXECUTIVO =====
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📝 Resumo Executivo")
    
    insights = []
    
    if card['bugs'] == 0:
        insights.append("✅ **Qualidade**: Zero bugs")
    elif card['bugs'] <= 2:
        insights.append(f"⚠️ **Qualidade**: {card['bugs']} bug(s)")
    else:
        insights.append(f"🚨 **Qualidade**: {card['bugs']} bugs")
    
    if card['lead_time'] <= 7:
        insights.append(f"✅ **Velocidade**: {card['lead_time']}d")
    elif card['lead_time'] <= 14:
        insights.append(f"⚠️ **Velocidade**: {card['lead_time']}d")
    else:
        insights.append(f"🚨 **Velocidade**: {card['lead_time']}d")
    
    if card['janela_status'] == 'ok':
        insights.append("✅ **Janela**: OK")
    elif card['janela_status'] == 'risco':
        insights.append("⚠️ **Janela**: Risco")
    else:
        insights.append("🚨 **Janela**: FORA")
    
    if card['dias_em_status'] > 7:
        insights.append(f"🚨 **Aging**: {card['dias_em_status']}d")
    
    cols = st.columns(len(insights)) if insights else [st]
    for i, insight in enumerate(insights):
        with cols[i]:
            st.markdown(insight)
    
    # ===== CARDS VINCULADOS =====
    exibir_cards_vinculados(links)
    
    # ===== COMENTÁRIOS =====
    exibir_comentarios(comentarios)


def exibir_detalhes_qa(card: Dict, links: List[Dict], comentarios: List[Dict]):
    """Exibe detalhes para projeto QA - Foco em automação e tempo parado."""
    
    # ===== KPIs PRINCIPAIS (CARDS ESTILIZADOS - QA) =====
    # Cores por status
    status_cores = {
        "Done": "#22c55e", "Concluído": "#22c55e",
        "Em Validação": "#3b82f6", "Aguardando Validação": "#f59e0b",
        "Desenvolvimento": "#8b5cf6", "Code Review": "#ec4899",
        "Blocked": "#ef4444", "Reprovado": "#ef4444"
    }
    status_cor = status_cores.get(card['status'], "#6b7280")
    sp_estimado_badge = "<span style='background:#f59e0b; color:white; font-size:9px; padding:2px 6px; border-radius:4px; margin-left:4px;'>estimado</span>" if card.get('sp_estimado', False) else ""
    
    st.markdown(f"""
    <div style='display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;'>
        <div style='background: linear-gradient(135deg, {status_cor}15, {status_cor}05); border: 1px solid {status_cor}40; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>📌</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Status</div>
            <div style='font-size: 14px; font-weight: 600; color: {status_cor}; margin-top: 4px; word-wrap: break-word;'>{card['status']}</div>
        </div>
        <div style='background: linear-gradient(135deg, #6366f115, #6366f105); border: 1px solid #6366f140; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>🎯</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Tipo</div>
            <div style='font-size: 14px; font-weight: 600; color: #6366f1; margin-top: 4px;'>{card['tipo']}</div>
        </div>
        <div style='background: linear-gradient(135deg, #f9731615, #f9731605); border: 1px solid #f9731640; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>⚡</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Prioridade</div>
            <div style='font-size: 14px; font-weight: 600; color: #f97316; margin-top: 4px;'>{card['prioridade']}</div>
        </div>
        <div style='background: linear-gradient(135deg, #3b82f615, #3b82f605); border: 1px solid #3b82f640; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>📊</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Story Points</div>
            <div style='font-size: 14px; font-weight: 600; color: #3b82f6; margin-top: 4px;'>{card['sp']}{sp_estimado_badge}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== ALERTA DE AGING (DESTAQUE PARA QA) =====
    aging_cor = "#22c55e" if card['dias_em_status'] <= 7 else "#f97316" if card['dias_em_status'] <= 30 else "#ef4444"
    aging_emoji = "✅" if card['dias_em_status'] <= 7 else "⚠️" if card['dias_em_status'] <= 30 else "🚨"
    
    st.markdown(f"""
    <div style='background: {aging_cor}15; padding: 20px; border-radius: 12px; 
                border-left: 4px solid {aging_cor}; margin-bottom: 20px;'>
        <div style='display: flex; align-items: center; gap: 15px;'>
            <span style='font-size: 40px;'>{aging_emoji}</span>
            <div>
                <h3 style='margin: 0; color: {aging_cor}; font-size: 1.3em;'>
                    {card['dias_em_status']} dias no status atual
                </h3>
                <p style='margin: 5px 0 0 0; color: #666; font-size: 0.9em;'>
                    Status: <b>{card['status']}</b> | 
                    {'Atividade recente' if card['dias_em_status'] <= 7 else 'Possível bloqueio - verificar impedimentos' if card['dias_em_status'] <= 30 else 'Card parado há muito tempo - ação necessária'}
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== INFORMAÇÕES DO CARD =====
    with st.expander("📋 **Informações do Card de Automação**", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
| Campo | Valor |
|-------|-------|
| **Projeto** | {card['projeto']} |
| **Sprint** | {card['sprint']} |
| **Produto** | {card['produto']} |
| **Tipo** | {card['tipo_original']} |
            """)
        
        with col2:
            sp_display_pb = f"{card['sp']} ⚠️ *estimado*" if card.get('sp_estimado', False) else str(card['sp'])
            st.markdown(f"""
| Campo | Valor |
|-------|-------|
| **Responsável** | {card['desenvolvedor']} |
| **Story Points** | {sp_display_pb} |
| **Criado** | {card['criado'].strftime('%d/%m/%Y') if pd.notna(card['criado']) else 'N/A'} |
| **Atualizado** | {card['atualizado'].strftime('%d/%m/%Y') if pd.notna(card['atualizado']) else 'N/A'} |
            """)
    
    # ===== ANÁLISE DE TEMPO =====
    with st.expander("⏱️ **Análise de Tempo**", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            lead_cor = "#22c55e" if card['lead_time'] <= 14 else "#f97316" if card['lead_time'] <= 30 else "#ef4444"
            st.markdown(f"""
<div style='background: {lead_cor}15; padding: 15px; border-radius: 8px; text-align: center; border-left: 3px solid {lead_cor};'>
    <h3 style='margin:0; color: {lead_cor}; font-size: 1.4em;'>{card['lead_time']} dias</h3>
    <small style='color: #666;'>Lead Time Total</small>
</div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
<div style='background: {aging_cor}15; padding: 15px; border-radius: 8px; text-align: center; border-left: 3px solid {aging_cor};'>
    <h3 style='margin:0; color: {aging_cor}; font-size: 1.4em;'>{card['dias_em_status']} dias</h3>
    <small style='color: #666;'>Parado no Status</small>
</div>
            """, unsafe_allow_html=True)
        
        with col3:
            criado_ha = (datetime.now() - card['criado']).days if pd.notna(card['criado']) else 0
            st.markdown(f"""
<div style='background: #6366f115; padding: 15px; border-radius: 8px; text-align: center; border-left: 3px solid #6366f1;'>
    <h3 style='margin:0; color: #6366f1; font-size: 1.4em;'>{criado_ha} dias</h3>
    <small style='color: #666;'>Desde Criação</small>
</div>
            """, unsafe_allow_html=True)
    
    # ===== RESUMO =====
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📝 Situação do Card de Automação")
    
    if card['dias_em_status'] <= 7:
        st.success("✅ Card com atividade recente. Desenvolvimento em andamento normal.")
    elif card['dias_em_status'] <= 30:
        st.warning("⚠️ Card parado há mais de uma semana. Verificar se há impedimentos ou necessidade de repriorização.")
    else:
        st.error("🚨 Card parado há muito tempo. Recomenda-se revisar a necessidade ou arquivar se não for mais relevante.")
    
    # ===== CARDS VINCULADOS =====
    exibir_cards_vinculados(links)
    
    # ===== COMENTÁRIOS =====
    exibir_comentarios(comentarios)


def exibir_detalhes_pb(card: Dict, links: List[Dict], comentarios: List[Dict]):
    """Exibe detalhes para projeto PB (Backlog) - Sem bugs, foco em prioridade."""
    
    # ===== KPIs PRINCIPAIS (CARDS ESTILIZADOS - PB) =====
    # Cores por status
    status_cores = {
        "Done": "#22c55e", "Concluído": "#22c55e",
        "Em Validação": "#3b82f6", "Aguardando Validação": "#f59e0b",
        "Desenvolvimento": "#8b5cf6", "Code Review": "#ec4899",
        "Blocked": "#ef4444", "Reprovado": "#ef4444",
        "Backlog": "#6b7280", "To Do": "#6b7280"
    }
    status_cor = status_cores.get(card['status'], "#6b7280")
    sp_valor = card['sp'] if card['sp'] > 0 else "N/A"
    
    st.markdown(f"""
    <div style='display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;'>
        <div style='background: linear-gradient(135deg, {status_cor}15, {status_cor}05); border: 1px solid {status_cor}40; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>📌</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Status</div>
            <div style='font-size: 14px; font-weight: 600; color: {status_cor}; margin-top: 4px; word-wrap: break-word;'>{card['status']}</div>
        </div>
        <div style='background: linear-gradient(135deg, #6366f115, #6366f105); border: 1px solid #6366f140; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>🎯</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Tipo</div>
            <div style='font-size: 14px; font-weight: 600; color: #6366f1; margin-top: 4px;'>{card['tipo']}</div>
        </div>
        <div style='background: linear-gradient(135deg, #f9731615, #f9731605); border: 1px solid #f9731640; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>⚡</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Prioridade</div>
            <div style='font-size: 14px; font-weight: 600; color: #f97316; margin-top: 4px;'>{card['prioridade']}</div>
        </div>
        <div style='background: linear-gradient(135deg, #3b82f615, #3b82f605); border: 1px solid #3b82f640; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>📊</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Estimativa</div>
            <div style='font-size: 14px; font-weight: 600; color: #3b82f6; margin-top: 4px;'>{sp_valor} SP</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== INDICADOR DE PRIORIZAÇÃO =====
    prioridade_map = {
        "Highest": ("#ef4444", "🔴", "Crítica"),
        "High": ("#f97316", "🟠", "Alta"),
        "Medium": ("#eab308", "🟡", "Média"),
        "Low": ("#22c55e", "🟢", "Baixa"),
        "Lowest": ("#6b7280", "⚪", "Muito Baixa")
    }
    prio_info = prioridade_map.get(card['prioridade'], ("#6b7280", "⚪", card['prioridade']))
    
    st.markdown(f"""
    <div style='background: {prio_info[0]}15; padding: 20px; border-radius: 12px; 
                border-left: 4px solid {prio_info[0]}; margin-bottom: 20px;'>
        <div style='display: flex; align-items: center; gap: 15px;'>
            <span style='font-size: 40px;'>{prio_info[1]}</span>
            <div>
                <h3 style='margin: 0; color: {prio_info[0]}; font-size: 1.3em;'>
                    Prioridade: {prio_info[2]}
                </h3>
                <p style='margin: 5px 0 0 0; color: #666; font-size: 0.9em;'>
                    Item de backlog aguardando priorização para desenvolvimento
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== INFORMAÇÕES DO ITEM =====
    with st.expander("📋 **Informações do Item de Backlog**", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
| Campo | Valor |
|-------|-------|
| **Projeto** | {card['projeto']} |
| **Produto** | {card['produto']} |
| **Tipo** | {card['tipo_original']} |
| **Estimativa** | {card['sp']} SP |
            """)
        
        with col2:
            st.markdown(f"""
| Campo | Valor |
|-------|-------|
| **Criado por** | {card['desenvolvedor']} |
| **Data Criação** | {card['criado'].strftime('%d/%m/%Y') if pd.notna(card['criado']) else 'N/A'} |
| **Última Atualização** | {card['atualizado'].strftime('%d/%m/%Y') if pd.notna(card['atualizado']) else 'N/A'} |
| **Status** | {card['status']} |
            """)
    
    # ===== TEMPO NO BACKLOG =====
    with st.expander("⏱️ **Tempo no Backlog**", expanded=True):
        dias_no_backlog = (datetime.now() - card['criado']).days if pd.notna(card['criado']) else 0
        
        col1, col2 = st.columns(2)
        
        with col1:
            backlog_cor = "#22c55e" if dias_no_backlog <= 30 else "#f97316" if dias_no_backlog <= 90 else "#ef4444"
            st.markdown(f"""
<div style='background: {backlog_cor}15; padding: 15px; border-radius: 8px; text-align: center; border-left: 3px solid {backlog_cor};'>
    <h3 style='margin:0; color: {backlog_cor}; font-size: 1.4em;'>{dias_no_backlog} dias</h3>
    <small style='color: #666;'>No Backlog</small><br>
    <small style='color: {backlog_cor};'>{'Recente' if dias_no_backlog <= 30 else 'Aguardando há algum tempo' if dias_no_backlog <= 90 else 'Revisar relevância'}</small>
</div>
            """, unsafe_allow_html=True)
        
        with col2:
            estimado = card['sp'] > 0
            est_cor = "#22c55e" if estimado else "#f97316"
            st.markdown(f"""
<div style='background: {est_cor}15; padding: 15px; border-radius: 8px; text-align: center; border-left: 3px solid {est_cor};'>
    <h3 style='margin:0; color: {est_cor}; font-size: 1.4em;'>{'✅' if estimado else '❓'}</h3>
    <small style='color: #666;'>Estimativa</small><br>
    <small style='color: {est_cor};'>{f'{card["sp"]} Story Points' if estimado else 'Não estimado'}</small>
</div>
            """, unsafe_allow_html=True)
    
    # ===== RESUMO =====
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📝 Situação do Item")
    
    insights = []
    
    if dias_no_backlog <= 30:
        insights.append("✅ Item recente no backlog")
    elif dias_no_backlog <= 90:
        insights.append("⚠️ Item aguardando há algum tempo")
    else:
        insights.append("🚨 Revisar relevância do item")
    
    if card['sp'] > 0:
        insights.append(f"✅ Estimado: {card['sp']} SP")
    else:
        insights.append("⚠️ Sem estimativa")
    
    if card['prioridade'] in ["Highest", "High"]:
        insights.append("🔴 Alta prioridade")
    
    cols = st.columns(len(insights)) if insights else [st]
    for i, insight in enumerate(insights):
        with cols[i]:
            st.markdown(insight)
    
    # ===== CARDS VINCULADOS =====
    exibir_cards_vinculados(links)
    
    # ===== COMENTÁRIOS =====
    exibir_comentarios(comentarios)


def exibir_cards_vinculados(links: List[Dict]):
    """Exibe seção de cards vinculados."""
    if links and len(links) > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander(f"🔗 **Cards Vinculados ({len(links)})**", expanded=True):
            for link in links:
                tipo_cor = "#6366f1" if link['tipo'] == 'Parent' else "#22c55e" if link['tipo'] == 'Subtask' else "#f59e0b"
                st.markdown(f"""
<div style='background: {tipo_cor}10; padding: 10px 15px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid {tipo_cor};'>
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <div>
            <span style='color: {tipo_cor}; font-weight: bold; font-size: 0.85em;'>{link['tipo']}</span>
            <span style='color: #666; font-size: 0.8em;'> • {link['direcao']}</span>
            <br>
            <a href="{link['link']}" target="_blank" style='color: #333; font-weight: bold; text-decoration: none;'>
                {link['ticket_id']}
            </a>
            <span style='color: #666; font-size: 0.85em;'> - {link['titulo'][:60]}{'...' if len(link['titulo']) > 60 else ''}</span>
        </div>
        <div style='text-align: right;'>
            <span style='background: #e5e7eb; padding: 3px 8px; border-radius: 4px; font-size: 0.75em;'>
                {link['status']}
            </span>
        </div>
    </div>
</div>
                """, unsafe_allow_html=True)


def exibir_comentarios(comentarios: List[Dict]):
    """Exibe seção de comentários do card."""
    if comentarios and len(comentarios) > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander(f"💬 **Comentários ({len(comentarios)})**", expanded=True):
            for i, com in enumerate(comentarios):
                # Formata a data
                try:
                    data_com = datetime.fromisoformat(com['data'].replace('Z', '+00:00'))
                    data_formatada = data_com.strftime('%d/%m/%Y às %H:%M')
                except:
                    data_formatada = com['data'][:10] if com['data'] else 'Data desconhecida'
                
                st.markdown(f"""
<div style='background: #f8fafc; padding: 12px 15px; border-radius: 8px; margin-bottom: 10px; border-left: 3px solid #6366f1;'>
    <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 8px;'>
        <div style='width: 32px; height: 32px; border-radius: 50%; background: #6366f1; 
                    display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;'>
            {com['autor'][0].upper() if com['autor'] else '?'}
        </div>
        <div>
            <strong style='color: #333;'>{com['autor']}</strong>
            <span style='color: #888; font-size: 0.8em; margin-left: 8px;'>{data_formatada}</span>
        </div>
    </div>
    <div style='color: #444; font-size: 0.9em; line-height: 1.5; padding-left: 42px;'>
        {com['texto'][:500]}{'...' if len(com['texto']) > 500 else ''}
    </div>
</div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("💬 **Comentários (0)**", expanded=False):
            st.caption("Nenhum comentário de usuário neste card.")


# ==============================================================================
# DADOS DE TENDÊNCIA (HISTÓRICO)
# ==============================================================================

def gerar_dados_tendencia() -> pd.DataFrame:
    """Gera dados históricos para demonstração de tendências."""
    sprints = [f"Release {i}" for i in range(230, 239)]
    
    dados = []
    for i, sprint in enumerate(sprints):
        # Progressão gradual com alguma variação
        base_fk = 1.2 + (i * 0.22) + random.uniform(-0.2, 0.2)
        base_fpy = 40 + (i * 5) + random.uniform(-4, 4)
        base_ddp = 65 + (i * 3.5) + random.uniform(-4, 4)
        base_health = 45 + (i * 5.5) + random.uniform(-6, 6)
        
        dados.append({
            'sprint': sprint,
            'fator_k': round(min(4, max(0.5, base_fk)), 2),
            'fpy': round(min(95, max(25, base_fpy)), 1),
            'ddp': round(min(98, max(45, base_ddp)), 1),
            'health_score': round(min(95, max(20, base_health)), 0),
            'bugs_total': max(3, 35 - (i * 3) + random.randint(-4, 4)),
            'cards_total': random.randint(35, 55),
            'sp_total': random.randint(80, 150),
            'lead_time_medio': round(max(3, 14 - (i * 0.9) + random.uniform(-1, 1)), 1),
            'throughput': random.randint(25, 45),
            'taxa_reprovacao': round(max(2, 25 - (i * 2) + random.uniform(-3, 3)), 1),
        })
    
    return pd.DataFrame(dados)


# ==============================================================================
# EXPORTAÇÃO
# ==============================================================================

def exportar_para_csv(df: pd.DataFrame) -> str:
    """Exporta dados para CSV."""
    df_export = df[['ticket_id', 'titulo', 'tipo', 'status', 'desenvolvedor', 'qa', 
                    'sp', 'bugs', 'sprint', 'produto', 'prioridade', 'lead_time']].copy()
    return df_export.to_csv(index=False)


def exportar_para_excel(df: pd.DataFrame, metricas: Dict) -> bytes:
    """Exporta dados para Excel com múltiplas abas."""
    output = io.BytesIO()
    
    try:
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export = df[['ticket_id', 'titulo', 'tipo', 'status', 'desenvolvedor', 'qa', 
                            'sp', 'bugs', 'sprint', 'produto', 'lead_time']].copy()
            df_export.to_excel(writer, sheet_name='Cards', index=False)
            
            metricas_df = pd.DataFrame([
                {'Métrica': 'Total de Cards', 'Valor': len(df)},
                {'Métrica': 'Story Points Total', 'Valor': int(df['sp'].sum())},
                {'Métrica': 'Bugs Encontrados', 'Valor': int(df['bugs'].sum())},
                {'Métrica': 'Cards Concluídos', 'Valor': len(df[df['status_cat'] == 'done'])},
                {'Métrica': 'Health Score', 'Valor': metricas.get('health_score', 'N/A')},
            ])
            metricas_df.to_excel(writer, sheet_name='Métricas', index=False)
            
            dev_stats = df.groupby('desenvolvedor').agg({
                'ticket_id': 'count', 'sp': 'sum', 'bugs': 'sum'
            }).reset_index()
            dev_stats.columns = ['Desenvolvedor', 'Cards', 'SP', 'Bugs']
            dev_stats.to_excel(writer, sheet_name='Por Desenvolvedor', index=False)
        
        return output.getvalue()
    except:
        return None


# ==============================================================================
# ESTILOS CSS
# ==============================================================================

def aplicar_estilos():
    st.markdown("""
    <style>
    /* Header Nina - Fundo branco para melhor contraste */
    .nina-header {
        background: #ffffff;
        color: #1e293b;
        padding: 20px 25px;
        border-radius: 12px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .nina-logo {
        width: 60px;
        height: 60px;
        flex-shrink: 0;
    }
    .nina-logo svg {
        width: 100%;
        height: 100%;
    }
    .nina-title {
        font-size: 24px;
        font-weight: bold;
        margin: 0;
        color: #1e293b;
    }
    .nina-subtitle {
        font-size: 14px;
        opacity: 0.75;
        margin: 5px 0 0 0;
        color: #64748b;
    }
    .nina-highlight {
        color: #AF0C37;
        font-weight: bold;
    }
    
    /* Cards de status */
    .status-card {
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 2px solid;
        margin-bottom: 10px;
        transition: transform 0.2s;
    }
    .status-card:hover { transform: translateY(-3px); }
    .status-green { background: rgba(34, 197, 94, 0.1); border-color: #22c55e; }
    .status-yellow { background: rgba(234, 179, 8, 0.1); border-color: #eab308; }
    .status-orange { background: rgba(249, 115, 22, 0.1); border-color: #f97316; }
    .status-red { background: rgba(239, 68, 68, 0.1); border-color: #ef4444; }
    .status-blue { background: rgba(59, 130, 246, 0.1); border-color: #3b82f6; }
    .status-purple { background: rgba(139, 92, 246, 0.1); border-color: #8b5cf6; }
    .status-gray { background: rgba(107, 114, 128, 0.1); border-color: #6b7280; }
    
    .big-number { font-size: 36px; font-weight: bold; margin: 0; }
    .card-label { font-size: 14px; opacity: 0.8; margin-top: 5px; }
    .card-sublabel { font-size: 12px; opacity: 0.6; margin-top: 3px; }
    
    /* Alertas */
    .alert-critical {
        background: rgba(239, 68, 68, 0.15);
        border-left: 4px solid #ef4444;
        padding: 15px; border-radius: 8px; margin: 10px 0;
    }
    .alert-warning {
        background: rgba(234, 179, 8, 0.15);
        border-left: 4px solid #eab308;
        padding: 15px; border-radius: 8px; margin: 10px 0;
    }
    .alert-info {
        background: rgba(59, 130, 246, 0.15);
        border-left: 4px solid #3b82f6;
        padding: 15px; border-radius: 8px; margin: 10px 0;
    }
    .alert-success {
        background: rgba(34, 197, 94, 0.15);
        border-left: 4px solid #22c55e;
        padding: 15px; border-radius: 8px; margin: 10px 0;
    }
    
    /* Ticket cards clicáveis */
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
    
    /* Barra de progresso */
    .progress-bar {
        background: #e5e7eb;
        border-radius: 10px;
        height: 24px;
        overflow: hidden;
        margin: 5px 0;
    }
    .progress-fill {
        height: 100%;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 12px;
    }
    
    /* Última atualização */
    .update-badge {
        background: rgba(34, 197, 94, 0.2);
        color: #166534;
        padding: 5px 12px;
        border-radius: 15px;
        font-size: 12px;
        display: inline-block;
    }
    .update-badge-stale {
        background: rgba(234, 179, 8, 0.2);
        color: #854d0e;
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, rgba(99, 102, 241, 0.1), transparent);
        padding: 10px 15px;
        border-radius: 8px;
        margin: 20px 0 10px 0;
        border-left: 4px solid #6366f1;
    }
    
    /* Hide Streamlit elements */
    #MainMenu, .stDeployButton { display: none !important; }
    </style>
    """, unsafe_allow_html=True)


# ==============================================================================
# COMPONENTES UI
# ==============================================================================

def mostrar_header_nina():
    """Mostra header principal com logo SVG da Nina."""
    # Logo SVG da Nina (vermelho #AF0C37)
    logo_svg = '''<svg width="60" height="60" viewBox="0 0 187 187" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M173.709 89.2107C172.209 86.6048 169.414 84.838 166.225 84.838C163.036 84.838 160.241 86.5649 158.741 89.1627H151.683C149.465 58.8237 124.495 35 94.0216 35C63.5489 35 38.5862 58.8237 36.3678 89.1627H29.1759C27.6759 86.5649 24.8734 84.798 21.6682 84.798C18.463 84.798 15.6605 86.5806 14.1605 89.2031C13.4184 90.4899 13 92.001 13 93.6C13 95.1987 13.4184 96.7017 14.1605 97.997C15.6605 100.619 18.463 102.306 21.6682 102.306C24.8734 102.306 27.6838 100.435 29.1759 97.8369H36.3678C38.5862 128.168 63.5489 152 94.0216 152C124.495 152 149.465 128.176 151.675 97.8369H158.686C160.178 100.435 162.996 102.354 166.217 102.354C169.438 102.354 172.256 100.611 173.749 97.9648C174.475 96.6856 174.885 95.2148 174.885 93.6319C174.885 92.049 174.451 90.5222 173.701 89.2188L173.709 89.2107ZM111.145 125.554C107.971 131.518 101.758 135.459 94.5981 135.459C87.4374 135.459 81.2248 131.566 78.0509 125.602C77.1666 123.947 78.3667 122.092 80.2219 122.092H108.982C110.837 122.092 112.029 123.891 111.153 125.554H111.145ZM140.528 94.1277C140.528 103.825 132.76 111.691 123.184 111.691H65.4432C55.8675 111.691 48.0991 103.825 48.0991 94.1277V93.7199C48.0991 84.0223 55.8675 76.1557 65.4432 76.1557H123.184C132.76 76.1557 140.528 84.0223 140.528 93.7199V94.1277Z" fill="#AF0C37"/>
    <path d="M76.5809 105.311C82.9686 105.311 88.1466 100.068 88.1466 93.5996C88.1466 87.1312 82.9686 81.8875 76.5809 81.8875C70.1936 81.8875 65.0156 87.1312 65.0156 93.5996C65.0156 100.068 70.1936 105.311 76.5809 105.311Z" fill="#AF0C37"/>
    <path d="M111.437 105.311C117.824 105.311 123.002 100.068 123.002 93.5996C123.002 87.1312 117.824 81.8875 111.437 81.8875C105.049 81.8875 99.8712 87.1312 99.8712 93.5996C99.8712 100.068 105.049 105.311 111.437 105.311Z" fill="#AF0C37"/>
    </svg>'''
    
    st.markdown(f"""
    <div class="nina-header">
        <div class="nina-logo">{logo_svg}</div>
        <div>
            <p class="nina-title"><span class="nina-highlight">NinaDash</span> — Dashboard de Inteligência e Métricas de QA</p>
            <p class="nina-subtitle">📊 Transformando dados em decisões: visibilidade de qualidade, gargalos e maturidade do time</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def mostrar_indicador_atualizacao(ultima_atualizacao: datetime):
    """Mostra indicador de última atualização."""
    agora = datetime.now()
    diff = (agora - ultima_atualizacao).total_seconds() / 60
    
    if diff < 1:
        texto = "Atualizado agora"
        classe = "update-badge"
    elif diff < REGRAS['cache_ttl_minutos']:
        texto = f"Atualizado há {int(diff)} min"
        classe = "update-badge"
    else:
        texto = f"Dados de {int(diff)} min atrás"
        classe = "update-badge update-badge-stale"
    
    st.markdown(f'<span class="{classe}">🕐 {texto}</span>', unsafe_allow_html=True)


def criar_card_metrica(valor: str, titulo: str, cor: str = "blue", subtitulo: str = ""):
    """Cria card de métrica visual."""
    st.markdown(f"""
    <div class="status-card status-{cor}">
        <p class="big-number">{valor}</p>
        <p class="card-label">{titulo}</p>
        {f'<p class="card-sublabel">{subtitulo}</p>' if subtitulo else ''}
    </div>
    """, unsafe_allow_html=True)


def mostrar_card_ticket(row: dict, compacto: bool = False):
    """Mostra card de ticket COM LINK para Jira."""
    bugs = row.get('bugs', 0)
    risco = 'high' if bugs >= 3 else 'medium' if bugs >= 1 else 'low'
    link = row.get('link', link_jira(row.get('ticket_id', '')))
    
    titulo = str(row.get('titulo', ''))[:60] + ('...' if len(str(row.get('titulo', ''))) > 60 else '')
    
    if compacto:
        st.markdown(f"""
        <div class="ticket-card ticket-risk-{risco}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <a href="{link}" target="_blank" style="color: #6366f1; font-weight: bold; text-decoration: none;">🔗 {row.get('ticket_id', '')}</a>
                <span style="opacity: 0.7;">{row.get('sp', 0)} SP | 🐛 {bugs}</span>
            </div>
            <p style="margin: 5px 0 0 0; font-size: 13px; opacity: 0.9;">{titulo}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="ticket-card ticket-risk-{risco}">
            <div style="display: flex; justify-content: space-between;">
                <a href="{link}" target="_blank" style="color: #6366f1; font-weight: bold; text-decoration: none;">🔗 {row.get('ticket_id', '')}</a>
                <span style="color: {'#ef4444' if bugs >= 3 else '#f97316' if bugs >= 1 else '#22c55e'}; font-weight: bold;">🐛 {bugs} bugs</span>
            </div>
            <p style="margin: 8px 0;">{row.get('titulo', '')}</p>
            <p style="font-size: 12px; opacity: 0.8;">
                <b>Dev:</b> {row.get('desenvolvedor', 'N/A')} | 
                <b>QA:</b> {row.get('qa', 'N/A')} | 
                <b>SP:</b> {row.get('sp', 0)} | 
                <b>{row.get('status', 'N/A')}</b>
            </p>
        </div>
        """, unsafe_allow_html=True)


def mostrar_lista_tickets_completa(items: list, titulo: str, mostrar_todos: bool = False):
    """Mostra lista de tickets com opção de ver TODOS."""
    if not items:
        st.info(f"Nenhum card em: {titulo}")
        return
    
    total = len(items)
    
    with st.expander(f"📋 {titulo} ({total} cards)", expanded=False):
        # Checkbox para mostrar todos
        if total > 5:
            mostrar_todos = st.checkbox(f"Mostrar todos os {total} cards", key=f"mostrar_todos_{titulo}", value=mostrar_todos)
        else:
            mostrar_todos = True
        
        limite = total if mostrar_todos else min(5, total)
        
        for i, item in enumerate(items[:limite]):
            if isinstance(item, dict):
                mostrar_card_ticket(item, compacto=True)
            elif isinstance(item, pd.Series):
                mostrar_card_ticket(item.to_dict(), compacto=True)
        
        if not mostrar_todos and total > 5:
            st.caption(f"📌 Mais {total - 5} cards ocultos. Marque acima para ver todos.")


def mostrar_lista_df_completa(df: pd.DataFrame, titulo: str):
    """Mostra lista de tickets de um DataFrame com opção de ver todos."""
    if df.empty:
        st.info(f"Nenhum card em: {titulo}")
        return
    
    items = df.to_dict('records')
    mostrar_lista_tickets_completa(items, titulo)


# ==============================================================================
# GRÁFICOS
# ==============================================================================

def criar_grafico_funil_qa(metricas_qa: Dict) -> go.Figure:
    """Cria gráfico de funil de validação QA."""
    funil = metricas_qa['funil']
    
    labels = ['⏳ Aguardando QA', '🧪 Em Validação', '✅ Concluído']
    values = [funil['waiting_qa'], funil['testing'], funil['done']]
    colors = ['#f59e0b', '#06b6d4', '#22c55e']
    
    if funil['blocked'] > 0:
        labels.append('🚫 Bloqueado')
        values.append(funil['blocked'])
        colors.append('#ef4444')
    
    if funil['rejected'] > 0:
        labels.append('❌ Reprovado')
        values.append(funil['rejected'])
        colors.append('#dc2626')
    
    fig = go.Figure(go.Funnel(
        y=labels, x=values,
        textinfo="value+percent total",
        marker=dict(color=colors),
        connector=dict(line=dict(color="royalblue", dash="dot", width=2))
    ))
    
    fig.update_layout(title="Funil de Validação QA", height=350, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def criar_grafico_tendencia_fator_k(df_tendencia: pd.DataFrame) -> go.Figure:
    """Cria gráfico de tendência do Fator K."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_tendencia['sprint'], y=df_tendencia['fator_k'],
        mode='lines+markers', name='Fator K',
        line=dict(color='#6366f1', width=3),
        marker=dict(size=10),
        hovertemplate='<b>%{x}</b><br>Fator K: %{y:.2f}<extra></extra>'
    ))
    
    # Faixas de maturidade
    fig.add_hline(y=3.0, line_dash="dash", line_color="#22c55e", annotation_text="Gold (≥3.0)")
    fig.add_hline(y=2.0, line_dash="dash", line_color="#eab308", annotation_text="Silver (≥2.0)")
    fig.add_hline(y=1.0, line_dash="dash", line_color="#f97316", annotation_text="Bronze (≥1.0)")
    
    fig.update_layout(
        title="📈 Evolução do Fator K (Maturidade)",
        xaxis_title="Sprint", yaxis_title="Fator K",
        hovermode='x unified', template='plotly_white', height=350
    )
    return fig


def criar_grafico_tendencia_qualidade(df_tendencia: pd.DataFrame) -> go.Figure:
    """Cria gráfico de tendência FPY e DDP."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_tendencia['sprint'], y=df_tendencia['fpy'],
        mode='lines+markers', name='FPY (%)',
        line=dict(color='#22c55e', width=2), marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=df_tendencia['sprint'], y=df_tendencia['ddp'],
        mode='lines+markers', name='DDP (%)',
        line=dict(color='#3b82f6', width=2), marker=dict(size=8)
    ))
    
    fig.add_hline(y=80, line_dash="dot", line_color="#22c55e", annotation_text="Meta FPY (80%)")
    fig.add_hline(y=85, line_dash="dot", line_color="#3b82f6", annotation_text="Meta DDP (85%)")
    
    fig.update_layout(
        title="📊 Evolução de Qualidade (FPY e DDP)",
        xaxis_title="Sprint", yaxis_title="Percentual (%)",
        hovermode='x unified', template='plotly_white', height=350,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def criar_grafico_tendencia_bugs(df_tendencia: pd.DataFrame) -> go.Figure:
    """Cria gráfico de tendência de bugs."""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_tendencia['sprint'], y=df_tendencia['bugs_total'],
        name='Bugs Encontrados', marker_color='#ef4444',
        text=df_tendencia['bugs_total'], textposition='outside'
    ))
    
    fig.add_trace(go.Scatter(
        x=df_tendencia['sprint'],
        y=df_tendencia['bugs_total'].rolling(3, min_periods=1).mean(),
        mode='lines', name='Média Móvel (3 sprints)',
        line=dict(color='#6366f1', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title="🐛 Bugs por Sprint",
        xaxis_title="Sprint", yaxis_title="Quantidade de Bugs",
        template='plotly_white', height=350, showlegend=True
    )
    return fig


def criar_grafico_tendencia_health(df_tendencia: pd.DataFrame) -> go.Figure:
    """Cria gráfico de tendência do Health Score."""
    fig = go.Figure()
    
    colors = ['#22c55e' if h >= 75 else '#eab308' if h >= 50 else '#f97316' if h >= 25 else '#ef4444' 
              for h in df_tendencia['health_score']]
    
    fig.add_trace(go.Bar(
        x=df_tendencia['sprint'], y=df_tendencia['health_score'],
        marker_color=colors,
        text=df_tendencia['health_score'].astype(int), textposition='outside'
    ))
    
    fig.add_hline(y=75, line_dash="dash", line_color="#22c55e", annotation_text="Saudável (≥75)")
    fig.add_hline(y=50, line_dash="dash", line_color="#eab308", annotation_text="Atenção (≥50)")
    
    fig.update_layout(
        title="🏥 Evolução do Health Score",
        xaxis_title="Sprint", yaxis_title="Health Score",
        template='plotly_white', height=350
    )
    return fig


def criar_grafico_throughput(df_tendencia: pd.DataFrame) -> go.Figure:
    """Cria gráfico de throughput."""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_tendencia['sprint'], y=df_tendencia['throughput'],
        name='Cards Entregues', marker_color='#3b82f6',
        text=df_tendencia['throughput'], textposition='outside'
    ))
    
    fig.add_trace(go.Scatter(
        x=df_tendencia['sprint'], y=df_tendencia['sp_total'],
        mode='lines+markers', name='SP Total',
        line=dict(color='#8b5cf6', width=2), yaxis='y2'
    ))
    
    fig.update_layout(
        title="📦 Throughput por Sprint",
        xaxis_title="Sprint",
        yaxis=dict(title="Cards", side='left'),
        yaxis2=dict(title="Story Points", side='right', overlaying='y'),
        template='plotly_white', height=350,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def criar_grafico_lead_time(df_tendencia: pd.DataFrame) -> go.Figure:
    """Cria gráfico de lead time."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_tendencia['sprint'], y=df_tendencia['lead_time_medio'],
        mode='lines+markers+text', name='Lead Time Médio',
        line=dict(color='#f59e0b', width=3), marker=dict(size=10),
        text=df_tendencia['lead_time_medio'].apply(lambda x: f"{x:.1f}d"),
        textposition='top center'
    ))
    
    fig.add_hline(y=7, line_dash="dash", line_color="#22c55e", annotation_text="Meta (≤7 dias)")
    
    fig.update_layout(
        title="⏱️ Lead Time Médio por Sprint",
        xaxis_title="Sprint", yaxis_title="Dias",
        template='plotly_white', height=350
    )
    return fig


def criar_grafico_reprovacao(df_tendencia: pd.DataFrame) -> go.Figure:
    """Cria gráfico de taxa de reprovação."""
    fig = go.Figure()
    
    colors = ['#ef4444' if r > 15 else '#f97316' if r > 10 else '#22c55e' 
              for r in df_tendencia['taxa_reprovacao']]
    
    fig.add_trace(go.Bar(
        x=df_tendencia['sprint'], y=df_tendencia['taxa_reprovacao'],
        marker_color=colors,
        text=df_tendencia['taxa_reprovacao'].apply(lambda x: f"{x:.0f}%"), textposition='outside'
    ))
    
    fig.add_hline(y=10, line_dash="dash", line_color="#22c55e", annotation_text="Meta (≤10%)")
    
    fig.update_layout(
        title="❌ Taxa de Reprovação por Sprint",
        xaxis_title="Sprint", yaxis_title="% Reprovados",
        template='plotly_white', height=350
    )
    return fig


def criar_grafico_estagio_por_produto(df: pd.DataFrame) -> go.Figure:
    """Cria gráfico de estágio por produto."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Sem dados", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    data = df.groupby(['produto', 'status_cat']).size().reset_index(name='count')
    
    fig = px.bar(
        data, x='produto', y='count', color='status_cat',
        color_discrete_map=STATUS_CORES,
        title='Estágio de Cards por Produto',
        labels={'count': 'Cards', 'produto': 'Produto', 'status_cat': 'Status'}
    )
    
    fig.update_layout(height=400, barmode='stack')
    return fig


def criar_grafico_hotfix_por_produto(df: pd.DataFrame) -> go.Figure:
    """Cria gráfico de hotfix por produto."""
    hotfix_df = df[df['tipo'] == 'HOTFIX']
    
    if hotfix_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Nenhum Hotfix encontrado", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    data = hotfix_df.groupby('produto').size().reset_index(name='count')
    
    fig = px.pie(
        data, values='count', names='produto',
        title='🔥 Hotfixes por Produto',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(height=350)
    return fig


# ==============================================================================
# ABAS DO DASHBOARD
# ==============================================================================

def aba_visao_geral(df: pd.DataFrame, ultima_atualizacao: datetime):
    """Aba principal com visão geral da sprint."""
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("### 📊 Visão Geral da Sprint")
    with col2:
        mostrar_indicador_atualizacao(ultima_atualizacao)
    with col3:
        if st.button("🔄 Atualizar Dados", type="secondary"):
            st.cache_data.clear()
            st.rerun()
    
    # Sprint info
    sprint_atual = df['sprint'].mode().iloc[0] if not df.empty else "Sem Sprint"
    dias_release = df['dias_ate_release'].max() if 'dias_ate_release' in df.columns else 0
    
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #AF0C37, #8B0A2C); color: white; padding: 15px 20px; border-radius: 10px; margin-bottom: 20px;">
        <span style="font-size: 18px; font-weight: bold;">🚀 {sprint_atual}</span>
        <span style="float: right;">📅 {dias_release} dias até a release</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Alertas de governança
    gov = calcular_metricas_governanca(df)
    if gov['sp']['pct'] < 50:
        st.markdown(f"""
        <div class="alert-critical">
            <b>⚠️ ALERTA: Apenas {gov['sp']['pct']:.0f}% dos cards têm Story Points preenchidos!</b>
            <p>Isso impacta diretamente nas métricas de capacidade, qualidade e decisões de release.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # KPIs principais COM TOOLTIPS
    with st.expander("📈 KPIs Principais da Sprint", expanded=True):
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            criar_card_metrica(str(len(df)), "Total Cards", "blue")
        
        with col2:
            sp_total = int(df['sp'].sum())
            criar_card_metrica(str(sp_total), "Story Points", "purple")
        
        with col3:
            concluidos = len(df[df['status_cat'] == 'done'])
            pct = concluidos / len(df) * 100 if len(df) > 0 else 0
            cor = 'green' if pct >= 70 else 'yellow' if pct >= 40 else 'red'
            criar_card_metrica(f"{pct:.0f}%", "Concluído", cor, f"{concluidos}/{len(df)}")
        
        with col4:
            bugs_total = int(df['bugs'].sum())
            cor = 'green' if bugs_total < 10 else 'yellow' if bugs_total < 20 else 'red'
            criar_card_metrica(str(bugs_total), "Bugs Encontrados", cor)
        
        with col5:
            fk = calcular_fator_k(sp_total, bugs_total)
            mat = classificar_maturidade(fk)
            cor_map = {'#22c55e': 'green', '#eab308': 'yellow', '#f97316': 'orange', '#ef4444': 'red'}
            criar_card_metrica(f"{fk:.1f}", f"Fator K {mat['emoji']}", cor_map.get(mat['cor'], 'blue'), mat['selo'])
        
        # Tooltip do Fator K
        mostrar_tooltip("fator_k")
    
    # Métricas de Qualidade COM TOOLTIPS
    with st.expander("🎯 Métricas de Qualidade", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        fpy = calcular_fpy(df)
        ddp = calcular_ddp(df)
        lead = calcular_lead_time(df)
        health = calcular_health_score(df)
        
        with col1:
            cor = 'green' if fpy['valor'] >= 80 else 'yellow' if fpy['valor'] >= 60 else 'red'
            criar_card_metrica(f"{fpy['valor']:.0f}%", "FPY", cor, f"{fpy['sem_bugs']}/{fpy['total']} sem bugs")
        
        with col2:
            cor = 'green' if ddp['valor'] >= 85 else 'yellow' if ddp['valor'] >= 70 else 'red'
            criar_card_metrica(f"{ddp['valor']:.0f}%", "DDP", cor, f"{ddp['bugs_qa']} bugs detectados")
        
        with col3:
            cor = 'green' if lead['medio'] <= 7 else 'yellow' if lead['medio'] <= 14 else 'red'
            criar_card_metrica(f"{lead['medio']:.1f}d", "Lead Time", cor, f"P85: {lead['p85']}d")
        
        with col4:
            cor = 'green' if health['score'] >= 75 else 'yellow' if health['score'] >= 50 else 'red'
            criar_card_metrica(f"{health['score']:.0f}", "Health Score", cor, health['status'])
        
        # Tooltips das métricas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            mostrar_tooltip("fpy")
        with col2:
            mostrar_tooltip("ddp")
        with col3:
            mostrar_tooltip("lead_time")
        with col4:
            mostrar_tooltip("health_score")
    
    # Distribuição por status COM LISTAGEM COMPLETA
    with st.expander("📋 Cards por Status", expanded=True):
        status_counts = df.groupby('status_cat').size().to_dict()
        
        cols = st.columns(4)
        status_order = ['development', 'code_review', 'waiting_qa', 'testing']
        
        for i, status in enumerate(status_order):
            with cols[i]:
                count = status_counts.get(status, 0)
                nome = STATUS_NOMES.get(status, status)
                cor = STATUS_CORES.get(status, '#6b7280')
                
                st.markdown(f"""
                <div style="background: {cor}20; border-left: 4px solid {cor}; padding: 15px; border-radius: 8px;">
                    <p style="font-size: 28px; font-weight: bold; margin: 0;">{count}</p>
                    <p style="font-size: 13px; margin: 5px 0 0 0;">{nome}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Listagem COMPLETA
                df_status = df[df['status_cat'] == status]
                if not df_status.empty:
                    mostrar_lista_df_completa(df_status, nome)
    
    # Gráficos
    with st.expander("📊 Gráficos de Distribuição", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            tipo_count = df['tipo'].value_counts().reset_index()
            tipo_count.columns = ['tipo', 'count']
            
            fig = px.pie(tipo_count, values='count', names='tipo', title='Distribuição por Tipo',
                         color='tipo', color_discrete_map={'TAREFA': '#3b82f6', 'BUG': '#ef4444', 'HOTFIX': '#f59e0b', 'SUGESTÃO': '#8b5cf6'},
                         hole=0.4)
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            prod_count = df['produto'].value_counts().reset_index()
            prod_count.columns = ['produto', 'count']
            
            fig = px.bar(prod_count.head(6), x='produto', y='count', title='Cards por Produto',
                         color='count', color_continuous_scale='Blues')
            fig.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)


def aba_qa(df: pd.DataFrame):
    """Aba de QA (análise de validação, gargalos e comparativo entre QAs)."""
    st.markdown("### 🔬 Análise de QA")
    st.caption("Monitore o funil de validação, identifique gargalos e compare a performance dos QAs")
    
    metricas_qa = calcular_metricas_qa(df)
    qas = [q for q in df['qa'].unique() if q != 'Não atribuído']
    
    # KPIs de QA
    with st.expander("📊 Indicadores de QA", expanded=True):
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total_fila = metricas_qa['funil']['waiting_qa'] + metricas_qa['funil']['testing']
            cor = 'green' if total_fila < 5 else 'yellow' if total_fila < 10 else 'red'
            criar_card_metrica(str(total_fila), "Fila de QA", cor, f"({metricas_qa['funil']['waiting_qa']} aguardando)")
        
        with col2:
            tempo = metricas_qa['tempo']['waiting']
            cor = 'green' if tempo < 2 else 'yellow' if tempo < 5 else 'red'
            criar_card_metrica(f"{tempo:.1f}d", "Tempo Médio Fila", cor)
        
        with col3:
            aging = metricas_qa['aging']['total']
            cor = 'green' if aging == 0 else 'yellow' if aging < 3 else 'red'
            criar_card_metrica(str(aging), f"Cards Aging (>{REGRAS['dias_aging_alerta']}d)", cor)
        
        with col4:
            taxa = metricas_qa['taxa_reprovacao']
            cor = 'green' if taxa < 10 else 'yellow' if taxa < 20 else 'red'
            criar_card_metrica(f"{taxa:.0f}%", "Taxa Reprovação", cor)
        
        with col5:
            # DDP
            ddp = calcular_ddp(df)
            cor = 'green' if ddp['valor'] >= 85 else 'yellow' if ddp['valor'] >= 70 else 'red'
            criar_card_metrica(f"{ddp['valor']:.0f}%", "DDP", cor, "Detecção de Defeitos")
        
        mostrar_tooltip("ddp")
    
    # Funil e Carga
    with st.expander("📈 Funil de Validação e Carga por QA", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            fig = criar_grafico_funil_qa(metricas_qa)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if not metricas_qa['carga_qa'].empty:
                fig = px.bar(
                    metricas_qa['carga_qa'].sort_values('Cards', ascending=True),
                    x='Cards', y='QA', orientation='h', color='SP',
                    color_continuous_scale='Blues', title='Carga por QA'
                )
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Nenhum card em validação no momento.")
    
    # ========== NOVO: Comparativo entre QAs ==========
    with st.expander("📊 Comparativo de Performance entre QAs", expanded=True):
        if qas:
            # Tabela comparativa
            dados_qa = []
            for qa in qas:
                df_qa = df[df['qa'] == qa]
                validados = len(df_qa[df_qa['status_cat'] == 'done'])
                em_fila = len(df_qa[df_qa['status_cat'].isin(['waiting_qa', 'testing'])])
                bugs_encontrados = int(df_qa['bugs'].sum())
                cards_sem_bugs = len(df_qa[(df_qa['status_cat'] == 'done') & (df_qa['bugs'] == 0)])
                fpy_val = cards_sem_bugs / validados * 100 if validados > 0 else 0
                sp_total = int(df_qa['sp'].sum())
                lead_time_medio = df_qa['lead_time'].mean() if not df_qa.empty else 0
                
                dados_qa.append({
                    'QA': qa,
                    'Cards': len(df_qa),
                    'Validados': validados,
                    'Em Fila': em_fila,
                    'Bugs Encontrados': bugs_encontrados,
                    'FPY': f"{fpy_val:.0f}%",
                    'SP Total': sp_total,
                    'Lead Time': f"{lead_time_medio:.1f}d",
                })
            
            df_comparativo = pd.DataFrame(dados_qa)
            st.dataframe(df_comparativo.sort_values('Cards', ascending=False), hide_index=True, use_container_width=True)
            
            # Gráficos comparativos
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🐛 Bugs Encontrados por QA**")
                bugs_por_qa = df[df['qa'] != 'Não atribuído'].groupby('qa')['bugs'].sum().reset_index()
                bugs_por_qa.columns = ['QA', 'Bugs']
                if not bugs_por_qa.empty and bugs_por_qa['Bugs'].sum() > 0:
                    fig = px.bar(bugs_por_qa.sort_values('Bugs', ascending=False), 
                                 x='QA', y='Bugs', color='Bugs',
                                 color_continuous_scale=['#22c55e', '#f97316', '#ef4444'],
                                 title='')
                    fig.update_layout(height=350, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Sem dados de bugs por QA")
            
            with col2:
                st.markdown("**✅ Cards Validados por QA**")
                validados_por_qa = df[(df['qa'] != 'Não atribuído') & (df['status_cat'] == 'done')].groupby('qa').size().reset_index(name='Validados')
                if not validados_por_qa.empty:
                    fig = px.pie(validados_por_qa, values='Validados', names='qa', 
                                 hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Nenhum card validado ainda")
        else:
            st.info("Nenhum QA atribuído aos cards.")
    
    # ========== NOVO: Bugs por Tipo e Impacto ==========
    with st.expander("🐛 Análise de Bugs e Retrabalho", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🎯 Bugs por Tipo de Card**")
            bugs_por_tipo = df.groupby('tipo')['bugs'].sum().reset_index()
            if not bugs_por_tipo.empty and bugs_por_tipo['bugs'].sum() > 0:
                fig = px.pie(bugs_por_tipo, values='bugs', names='tipo', hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Set2)
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem bugs registrados")
        
        with col2:
            st.markdown("**📊 Métricas de Eficiência**")
            concluidos = df[df['status_cat'] == 'done']
            if not concluidos.empty:
                # FPY geral
                fpy = calcular_fpy(df)
                st.metric("FPY (First Pass Yield)", f"{fpy['valor']}%", 
                         help="Cards aprovados sem bugs na primeira validação")
                
                # Taxa de retrabalho
                cards_com_bugs = len(concluidos[concluidos['bugs'] > 0])
                taxa_retrabalho = cards_com_bugs / len(concluidos) * 100 if len(concluidos) > 0 else 0
                st.metric("Taxa de Retrabalho", f"{taxa_retrabalho:.1f}%",
                         help="Cards que precisaram de correção")
                
                # Lead time médio
                lead = calcular_lead_time(df)
                st.metric("Lead Time Médio", f"{lead['medio']:.1f} dias")
            else:
                st.info("Sem cards concluídos")
        
        # Devs que mais geraram bugs
        st.markdown("---")
        st.markdown("**⚠️ Desenvolvedores com mais bugs (requer atenção do QA)**")
        
        dev_bugs = df[df['desenvolvedor'] != 'Não atribuído'].groupby('desenvolvedor').agg({
            'bugs': 'sum',
            'sp': 'sum',
            'ticket_id': 'count'
        }).reset_index()
        dev_bugs.columns = ['Desenvolvedor', 'Bugs', 'SP', 'Cards']
        dev_bugs['FK'] = dev_bugs.apply(lambda x: round(x['SP'] / (x['Bugs'] + 1), 2), axis=1)
        dev_bugs = dev_bugs[dev_bugs['Bugs'] > 0].sort_values('Bugs', ascending=False)
        
        if not dev_bugs.empty:
            for _, row in dev_bugs.head(5).iterrows():
                cor = '#ef4444' if row['FK'] < 1.5 else '#f97316' if row['FK'] < 2.5 else '#22c55e'
                st.markdown(f"""
                <div style="background: rgba(100,100,100,0.05); padding: 10px; border-radius: 8px; margin: 5px 0; border-left: 3px solid {cor};">
                    <b>{row['Desenvolvedor']}</b><br>
                    <span style="font-size: 12px;">🐛 {row['Bugs']} bugs | FK: {row['FK']} | {row['Cards']} cards</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ Nenhum desenvolvedor com bugs significativos!")
    
    # ========== NOVO: JANELA DE VALIDAÇÃO (considera complexidade) ==========
    with st.expander("🕐 Janela de Validação (Análise de Risco)", expanded=True):
        st.markdown("""
        <div class="alert-info">
            <b>📋 Regras de Janela de Validação</b>
            <p>A janela considera a <b>complexidade de teste</b> do card para determinar se há tempo suficiente:</p>
            <ul style="margin: 5px 0 0 20px;">
                <li><b>Alta:</b> 3+ dias necessários</li>
                <li><b>Média:</b> 2 dias necessários</li>
                <li><b>Baixa:</b> 1 dia é suficiente</li>
                <li><b>Não definida:</b> Assume 3 dias (conservador)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Filtrar cards em fila de QA ou validação
        cards_qa = df[df['status_cat'].isin(['waiting_qa', 'testing'])]
        
        if not cards_qa.empty:
            # Contagem por status de janela
            fora_janela = cards_qa[cards_qa['janela_status'] == 'fora']
            em_risco = cards_qa[cards_qa['janela_status'] == 'risco']
            dentro_janela = cards_qa[cards_qa['janela_status'] == 'ok']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                cor = 'red' if len(fora_janela) > 0 else 'green'
                criar_card_metrica(str(len(fora_janela)), "🚨 Fora da Janela", cor, "Validar próxima sprint")
            
            with col2:
                cor = 'yellow' if len(em_risco) > 0 else 'green'
                criar_card_metrica(str(len(em_risco)), "⚠️ Em Risco", cor, "Priorizar imediatamente")
            
            with col3:
                criar_card_metrica(str(len(dentro_janela)), "✅ Dentro da Janela", "green", "Tempo adequado")
            
            # Lista de cards FORA da janela
            if not fora_janela.empty:
                st.markdown("### 🚨 Cards FORA da Janela de Validação")
                st.markdown("""
                <div class="alert-critical">
                    <b>Estes cards não têm tempo suficiente para validação completa nesta sprint.</b>
                    <p>Recomendação: Considerar para a próxima sprint ou priorizar validação simplificada.</p>
                </div>
                """, unsafe_allow_html=True)
                
                df_fora = fora_janela[['ticket_id', 'titulo', 'complexidade', 'dias_ate_release', 'janela_dias_necessarios', 'desenvolvedor', 'qa', 'sp']].copy()
                df_fora.columns = ['Ticket', 'Título', 'Complexidade', 'Dias Disponíveis', 'Dias Necessários', 'Dev', 'QA', 'SP']
                df_fora['Título'] = df_fora['Título'].str[:40] + '...'
                df_fora['Complexidade'] = df_fora['Complexidade'].replace('', 'Não definida')
                df_fora['Déficit'] = df_fora['Dias Necessários'] - df_fora['Dias Disponíveis']
                
                st.dataframe(df_fora.sort_values('Déficit', ascending=False), hide_index=True, use_container_width=True)
                
                # Análise por desenvolvedor
                st.markdown("#### 📊 Cards fora da janela por Desenvolvedor")
                dev_fora = fora_janela.groupby('desenvolvedor').size().reset_index(name='Cards Fora')
                dev_fora = dev_fora.sort_values('Cards Fora', ascending=False)
                
                fig = px.bar(dev_fora, x='desenvolvedor', y='Cards Fora', 
                            color='Cards Fora', color_continuous_scale='Reds',
                            title='Quem mais encaminhou cards sem tempo adequado?')
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            # Lista de cards EM RISCO
            if not em_risco.empty:
                st.markdown("### ⚠️ Cards EM RISCO")
                st.markdown("""
                <div class="alert-warning">
                    <b>Estes cards estão no limite do tempo - priorizar validação!</b>
                </div>
                """, unsafe_allow_html=True)
                
                df_risco = em_risco[['ticket_id', 'titulo', 'complexidade', 'dias_ate_release', 'janela_dias_necessarios', 'qa', 'sp']].copy()
                df_risco.columns = ['Ticket', 'Título', 'Complexidade', 'Dias Disponíveis', 'Dias Necessários', 'QA', 'SP']
                df_risco['Título'] = df_risco['Título'].str[:40] + '...'
                df_risco['Complexidade'] = df_risco['Complexidade'].replace('', 'Não definida')
                
                st.dataframe(df_risco, hide_index=True, use_container_width=True)
            
            # Análise por complexidade
            st.markdown("#### 📈 Análise de Complexidade vs Tempo Disponível")
            
            col1, col2 = st.columns(2)
            with col1:
                # Distribuição de complexidade
                complex_dist = cards_qa['complexidade'].replace('', 'Não definida').value_counts().reset_index()
                complex_dist.columns = ['Complexidade', 'Quantidade']
                
                cores_complex = {'Alta': '#ef4444', 'Média': '#f59e0b', 'Baixa': '#22c55e', 'Não definida': '#6b7280'}
                fig = px.pie(complex_dist, names='Complexidade', values='Quantidade',
                            title='Distribuição por Complexidade',
                            color='Complexidade', color_discrete_map=cores_complex)
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Status da janela
                status_dist = cards_qa['janela_status'].value_counts().reset_index()
                status_dist.columns = ['Status', 'Quantidade']
                status_dist['Status'] = status_dist['Status'].map({'ok': '✅ OK', 'risco': '⚠️ Risco', 'fora': '🚨 Fora'})
                
                cores_status = {'✅ OK': '#22c55e', '⚠️ Risco': '#f59e0b', '🚨 Fora': '#ef4444'}
                fig = px.pie(status_dist, names='Status', values='Quantidade',
                            title='Status da Janela de Validação',
                            color='Status', color_discrete_map=cores_status)
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.success("✅ Nenhum card aguardando validação no momento!")
    
    # Cards com aging - COM LISTAGEM COMPLETA
    with st.expander("⏰ Cards Envelhecidos (Aging)", expanded=False):
        aging_waiting = metricas_qa['aging']['waiting']
        aging_testing = metricas_qa['aging']['testing']
        
        if not aging_waiting.empty or not aging_testing.empty:
            st.markdown(f"""
            <div class="alert-warning">
                <b>⚠️ {metricas_qa['aging']['total']} card(s) estão há mais de {REGRAS['dias_aging_alerta']} dias no mesmo status!</b>
            </div>
            """, unsafe_allow_html=True)
            
            if not aging_waiting.empty:
                mostrar_lista_df_completa(aging_waiting, "Aging - Aguardando QA")
            
            if not aging_testing.empty:
                mostrar_lista_df_completa(aging_testing, "Aging - Em Validação")
        else:
            st.success("✅ Nenhum card envelhecido! Fluxo de QA saudável.")
    
    # Fila completa COM LISTAGEM COMPLETA
    with st.expander("📋 Fila Completa - Aguardando Validação", expanded=False):
        fila_qa = df[df['status_cat'] == 'waiting_qa'].sort_values('dias_em_status', ascending=False)
        mostrar_lista_df_completa(fila_qa, "Aguardando QA")
    
    # Em validação COM LISTAGEM COMPLETA
    with st.expander("🧪 Em Validação", expanded=False):
        em_teste = df[df['status_cat'] == 'testing'].sort_values('dias_em_status', ascending=False)
        mostrar_lista_df_completa(em_teste, "Em Validação")


def aba_dev(df: pd.DataFrame):
    """Aba de Dev - Performance, Ranking e Análise por Desenvolvedor."""
    st.markdown("### 👨‍💻 Painel de Desenvolvimento")
    st.caption("Performance individual, ranking e métricas de maturidade do time de desenvolvimento")
    
    devs = [d for d in df['desenvolvedor'].unique() if d != 'Não atribuído']
    
    dev_sel = st.selectbox("👤 Selecione o Desenvolvedor", ["🏆 Ranking Geral"] + sorted(devs))
    st.markdown("---")
    
    if dev_sel == "🏆 Ranking Geral":
        # Card explicativo sobre Fator K
        with st.expander("📐 Como é calculada a Maturidade de Entrega (Fator K)?", expanded=False):
            st.markdown("""
            O **Fator K** mede a qualidade da entrega do desenvolvedor, considerando o esforço planejado (Story Points) 
            e os bugs encontrados pelo QA.
            
            **Fórmula:** `FK = SP / (Bugs + 1)`
            
            **Exemplo:** Um dev com 13 SP e 2 bugs terá FK = (13 / 3) = **4.33** (Excelente!)
            
            | Selo | Fator K | Classificação |
            |------|---------|---------------|
            | 🥇 Gold | ≥ 3.0 | Excelente |
            | 🥈 Silver | 2.0 - 2.9 | Bom |
            | 🥉 Bronze | 1.0 - 1.9 | Regular |
            | ⚠️ Risco | < 1.0 | Crítico |
            """)
            mostrar_tooltip("fator_k")
        
        # Ranking
        with st.expander("🏆 Ranking de Performance", expanded=True):
            dados_dev = []
            for dev in devs:
                analise = analisar_dev_detalhado(df, dev)
                if analise:
                    dados_dev.append({
                        'Desenvolvedor': dev,
                        'Cards': analise['cards'],
                        'SP': analise['sp_total'],
                        'Bugs': analise['bugs_total'],
                        'Fator K': analise['fk_medio'],
                        'FPY': f"{analise['zero_bugs']}%",
                        'Tempo Médio': f"{analise['tempo_medio']} dias",
                        'Selo': f"{analise['maturidade']['emoji']} {analise['maturidade']['selo']}"
                    })
            
            if dados_dev:
                df_rank = pd.DataFrame(dados_dev)
                df_rank = df_rank.sort_values('Fator K', ascending=False)
                
                st.dataframe(df_rank, hide_index=True, use_container_width=True)
                
                # Gráfico Fator K
                fig = px.bar(df_rank, x='Desenvolvedor', y='Fator K',
                             color='Fator K',
                             color_continuous_scale=['#ef4444', '#f97316', '#eab308', '#22c55e'],
                             text='Selo')
                fig.add_hline(y=2, line_dash="dash", annotation_text="Meta (FK ≥ 2)")
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Nenhum desenvolvedor com dados suficientes.")
        
        # Devs que precisam de atenção
        with st.expander("⚠️ Desenvolvedores que Precisam de Atenção", expanded=False):
            devs_atencao = [d for d in dados_dev if d['Fator K'] >= 0 and d['Fator K'] < 2 and d['Bugs'] > 0]
            
            if devs_atencao:
                st.caption("Fator K abaixo de 2 com bugs encontrados - podem se beneficiar de code review mais rigoroso")
                
                for d in devs_atencao:
                    df_dev_filter = df[df['desenvolvedor'] == d['Desenvolvedor']]
                    cards_problematicos = df_dev_filter[df_dev_filter['bugs'] >= 2].head(3)
                    
                    with st.expander(f"⚠️ {d['Desenvolvedor']} - FK: {d['Fator K']} | {d['Bugs']} bugs em {d['Cards']} cards"):
                        if not cards_problematicos.empty:
                            st.markdown("**Cards com mais bugs:**")
                            for _, row in cards_problematicos.iterrows():
                                st.markdown(f"- [{row['ticket_id']}]({row['link']}) - {row['bugs']} bugs - {row['titulo'][:40]}...")
            else:
                st.success("✅ Todos os desenvolvedores estão com FK adequado!")
        
        # Análise do Time
        with st.expander("📊 Análise do Time de Desenvolvimento", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📋 Cards por Desenvolvedor**")
                cards_por_dev = df[df['desenvolvedor'] != 'Não atribuído'].groupby('desenvolvedor').size().reset_index(name='cards')
                if not cards_por_dev.empty:
                    cards_por_dev = cards_por_dev.nlargest(8, 'cards')
                    fig_cards = px.bar(cards_por_dev, x='desenvolvedor', y='cards', 
                                       color='cards', color_continuous_scale='Blues')
                    fig_cards.update_layout(height=350, showlegend=False, xaxis_title="", yaxis_title="Cards")
                    st.plotly_chart(fig_cards, use_container_width=True)
                else:
                    st.info("Sem dados de cards por desenvolvedor")
            
            with col2:
                st.markdown("**🐛 Taxa de Bugs por Card**")
                taxa_bugs = df[df['desenvolvedor'] != 'Não atribuído'].groupby('desenvolvedor').agg({
                    'bugs': 'sum', 'ticket_id': 'count'
                }).reset_index()
                taxa_bugs['taxa'] = (taxa_bugs['bugs'] / taxa_bugs['ticket_id']).round(2)
                taxa_bugs = taxa_bugs.nlargest(8, 'taxa')
                
                if not taxa_bugs.empty and taxa_bugs['taxa'].sum() > 0:
                    fig_taxa = px.bar(taxa_bugs, x='desenvolvedor', y='taxa', 
                                      color='taxa', color_continuous_scale=['#22c55e', '#eab308', '#ef4444'])
                    fig_taxa.update_layout(height=350, showlegend=False, xaxis_title="", yaxis_title="Bugs/Card")
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
                cards_zero_bugs = len(df[df['bugs'] == 0])
                pct_zero_bugs = cards_zero_bugs / len(df) * 100 if len(df) > 0 else 0
                st.metric("Cards sem Bugs", f"{cards_zero_bugs} ({pct_zero_bugs:.0f}%)")
                lead_medio = df['lead_time'].mean() if not df.empty else 0
                st.metric("Lead Time Médio", f"{lead_medio:.1f} dias")
        
        # Análise para Tech Lead
        with st.expander("🎯 Análise para Tech Lead", expanded=False):
            col_tl1, col_tl2 = st.columns(2)
            
            with col_tl1:
                st.markdown("**📊 Distribuição de Story Points por Dev**")
                st.caption("Quem está assumindo mais complexidade")
                sp_por_dev = df[df['desenvolvedor'] != 'Não atribuído'].groupby('desenvolvedor')['sp'].sum().reset_index()
                sp_por_dev = sp_por_dev.sort_values('sp', ascending=False).head(8)
                
                if not sp_por_dev.empty and sp_por_dev['sp'].sum() > 0:
                    fig_sp = px.pie(sp_por_dev, names='desenvolvedor', values='sp', 
                                   color_discrete_sequence=px.colors.sequential.RdBu)
                    fig_sp.update_layout(height=350)
                    fig_sp.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_sp, use_container_width=True)
                else:
                    st.info("Sem dados de SP")
            
            with col_tl2:
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
                    fig_status.update_layout(height=350, xaxis_title="", legend=dict(orientation="h", y=1.1))
                    st.plotly_chart(fig_status, use_container_width=True)
            
            # WIP e Code Review
            col_tl3, col_tl4 = st.columns(2)
            
            with col_tl3:
                st.markdown("**⏳ Work-In-Progress (WIP) por Dev**")
                st.caption("Quantos cards cada dev está trabalhando agora")
                
                wip_devs = df[(df['desenvolvedor'] != 'Não atribuído') & 
                              (df['status_cat'].isin(['development', 'code_review']))].groupby('desenvolvedor').size().reset_index(name='WIP')
                wip_devs = wip_devs.sort_values('WIP', ascending=False)
                
                if not wip_devs.empty:
                    fig_wip = px.bar(wip_devs, x='desenvolvedor', y='WIP', 
                                     color='WIP', color_continuous_scale=['#22c55e', '#eab308', '#ef4444'],
                                     text='WIP')
                    fig_wip.add_hline(y=3, line_dash="dash", annotation_text="WIP Ideal ≤ 3", line_color="#eab308")
                    fig_wip.update_layout(height=350, showlegend=False, xaxis_title="")
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
            
            # Velocidade e Cards Críticos
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
                    fig_vel.update_layout(height=350, showlegend=False, xaxis_title="")
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
        # ====== Métricas Individuais ======
        analise = analisar_dev_detalhado(df, dev_sel)
        
        if analise:
            st.markdown(f"### 👤 Métricas de {dev_sel}")
            
            mat = analise['maturidade']
            
            with st.expander(f"{mat['emoji']} Selo de Maturidade: {mat['selo']}", expanded=True):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.markdown(f"""
                    <div style="background: {mat['cor']}20; border: 2px solid {mat['cor']}; padding: 20px; border-radius: 12px; text-align: center;">
                        <p style="font-size: 48px; margin: 0;">{mat['emoji']}</p>
                        <p style="font-size: 20px; font-weight: bold; margin: 5px 0; color: {mat['cor']};">{mat['selo']}</p>
                        <p style="font-size: 14px; opacity: 0.8;">{mat['desc']}</p>
                        <p style="font-size: 24px; font-weight: bold; margin-top: 10px; color: {mat['cor']};">FK: {analise['fk_medio']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
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
            
            # Cards do dev
            with st.expander(f"📋 Cards de {dev_sel}", expanded=True):
                for _, row in analise['df'].iterrows():
                    bugs_cor = '#ef4444' if row['bugs'] >= 2 else '#eab308' if row['bugs'] == 1 else '#22c55e'
                    st.markdown(f"""
                    <div style="padding: 10px; margin: 5px 0; border-left: 3px solid {bugs_cor}; background: rgba(100,100,100,0.05); border-radius: 4px;">
                        <strong><a href="{row['link']}" style="color: #60a5fa;">{row['ticket_id']}</a></strong> - {row['titulo'][:50]}...<br>
                        <small style="color: #94a3b8;">🐛 {row['bugs']} bugs | 📊 {row['sp']} SP | 📍 {row['status']} | ⏱️ {row['lead_time']:.1f}d</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning(f"Nenhum card encontrado para {dev_sel}")


def aba_governanca(df: pd.DataFrame):
    """Aba de Governança de Dados."""
    st.markdown("### 📋 Governança de Dados")
    st.caption("Monitore o preenchimento dos campos obrigatórios para garantir métricas confiáveis")
    
    gov = calcular_metricas_governanca(df)
    
    media_preenchimento = (gov['sp']['pct'] + gov['bugs']['pct'] + gov['complexidade']['pct'] + gov['qa']['pct']) / 4
    
    # Alerta geral
    with st.expander("📊 Status Geral da Governança", expanded=True):
        if media_preenchimento < 50:
            st.markdown("""
            <div class="alert-critical">
                <b>🚨 ATENÇÃO: Qualidade dos dados comprometida!</b>
                <p>Muitos campos obrigatórios não estão preenchidos. Isso impacta diretamente nas métricas e decisões.</p>
            </div>
            """, unsafe_allow_html=True)
        elif media_preenchimento < 80:
            st.markdown("""
            <div class="alert-warning">
                <b>⚠️ Oportunidade de melhoria nos dados</b>
                <p>Alguns campos precisam de atenção para melhorar a qualidade das métricas.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-success">
                <b>✅ Dados em boa qualidade!</b>
                <p>Os campos obrigatórios estão bem preenchidos.</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.metric("Média de Preenchimento", f"{media_preenchimento:.0f}%")
    
    # Campos obrigatórios - COM LISTAGEM COMPLETA
    campos = [
        ("Story Points", gov['sp'], "Obrigatório para todos os cards (exceto Hotfix que assume 2 SP por padrão)"),
        ("Bugs Encontrados", gov['bugs'], "Preencher após validação - essencial para métricas de qualidade"),
        ("Complexidade de Teste", gov['complexidade'], "Meta futura - ajuda a balancear carga de QA"),
        ("QA Responsável", gov['qa'], "Obrigatório - indica quem está validando"),
    ]
    
    for nome, dados, obs in campos:
        with st.expander(f"📌 {nome} - {dados['pct']:.0f}% preenchido ({dados['preenchido']}/{dados['total']})", expanded=False):
            cor = '#22c55e' if dados['pct'] >= 80 else '#f59e0b' if dados['pct'] >= 50 else '#ef4444'
            
            st.markdown(f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width: {dados['pct']}%; background: {cor};">
                    {dados['pct']:.0f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.caption(obs)
            
            # Listagem COMPLETA dos faltando
            if dados['faltando']:
                mostrar_lista_tickets_completa(dados['faltando'], f"Cards sem {nome}")
            else:
                st.success(f"✅ Todos os cards têm {nome} preenchido!")
    
    # Exportar lista para cobrança
    with st.expander("📥 Exportar Listas para Cobrança", expanded=False):
        if gov['sp']['faltando']:
            df_export = pd.DataFrame(gov['sp']['faltando'])
            csv = df_export.to_csv(index=False)
            st.download_button("📥 Baixar cards sem Story Points", csv, "cards_sem_sp.csv", "text/csv")
        
        if gov['bugs']['faltando']:
            df_export = pd.DataFrame(gov['bugs']['faltando'])
            csv = df_export.to_csv(index=False)
            st.download_button("📥 Baixar cards sem Bugs preenchido", csv, "cards_sem_bugs.csv", "text/csv")


def aba_produto(df: pd.DataFrame):
    """Aba de métricas por Produto (métricas Ellen)."""
    st.markdown("### 📦 Métricas por Produto")
    st.caption("Visualize métricas segmentadas por produto - inclui métricas de fluxo da sprint")
    
    metricas_prod = calcular_metricas_produto(df)
    
    # KPIs novas métricas Ellen
    with st.expander("🎯 Indicadores de Fluxo da Sprint", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_finalizados = metricas_prod['total_finalizados_mesma_sprint']
            total_done = len(df[df['status_cat'] == 'done'])
            pct = total_finalizados / total_done * 100 if total_done > 0 else 0
            cor = 'green' if pct >= 70 else 'yellow' if pct >= 40 else 'red'
            criar_card_metrica(f"{total_finalizados}", "Iniciados e Finalizados na Sprint", cor, f"{pct:.0f}% dos concluídos")
        
        with col2:
            total_fora = metricas_prod['total_adicionados_fora']
            cor = 'green' if total_fora < 3 else 'yellow' if total_fora < 6 else 'red'
            criar_card_metrica(str(total_fora), "Cards Adicionados Fora do Período", cor, "Adicionados após início da sprint")
        
        with col3:
            total_hotfix = len(df[df['tipo'] == 'HOTFIX'])
            cor = 'green' if total_hotfix < 5 else 'yellow' if total_hotfix < 10 else 'red'
            criar_card_metrica(str(total_hotfix), "Total de Hotfixes", cor)
        
        st.caption("💡 **Dica:** Cards adicionados fora do período comprometem o planejamento da sprint")
    
    # Cards adicionados fora do período - COM LISTAGEM COMPLETA
    with st.expander("⚠️ Cards Adicionados Fora do Período", expanded=False):
        if not metricas_prod['adicionados_fora'].empty:
            st.markdown("""
            <div class="alert-warning">
                <b>Estes cards foram adicionados após o início da sprint</b>
                <p>Isso pode indicar escopo não planejado ou emergências.</p>
            </div>
            """, unsafe_allow_html=True)
            mostrar_lista_df_completa(metricas_prod['adicionados_fora'], "Cards Fora do Período")
        else:
            st.success("✅ Nenhum card foi adicionado fora do período!")
    
    # Gráficos
    with st.expander("📊 Visualizações por Produto", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            fig = criar_grafico_hotfix_por_produto(df)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = criar_grafico_estagio_por_produto(df)
            st.plotly_chart(fig, use_container_width=True)
    
    # Tabela resumo por produto
    with st.expander("📋 Resumo por Produto", expanded=True):
        produto_stats = df.groupby('produto').agg({
            'ticket_id': 'count',
            'sp': 'sum',
            'bugs': 'sum',
        }).reset_index()
        produto_stats.columns = ['produto', 'Cards', 'SP', 'Bugs']
        produto_stats['FK'] = produto_stats.apply(lambda x: calcular_fator_k(x['SP'], x['Bugs']), axis=1)
        
        hotfix_count = df[df['tipo'] == 'HOTFIX'].groupby('produto').size().reset_index(name='Hotfixes')
        produto_stats = produto_stats.merge(hotfix_count, on='produto', how='left').fillna(0)
        produto_stats['Hotfixes'] = produto_stats['Hotfixes'].astype(int)
        produto_stats = produto_stats.rename(columns={'produto': 'Produto'})
        
        st.dataframe(produto_stats.sort_values('Cards', ascending=False), hide_index=True, use_container_width=True)


def calcular_metricas_backlog(df: pd.DataFrame) -> Dict:
    """Calcula métricas específicas para análise do Product Backlog."""
    hoje = datetime.now()
    
    # Filtrar apenas itens no backlog (não concluídos e não em progresso avançado)
    df_backlog = df[df['status_cat'].isin(['backlog'])]
    
    # Se não houver itens no backlog "puro", considerar todos não concluídos
    if df_backlog.empty:
        df_backlog = df[~df['status_cat'].isin(['done', 'deferred'])]
    
    total_backlog = len(df_backlog)
    
    if total_backlog == 0:
        return {
            "total_itens": 0,
            "sp_pendentes": 0,
            "idade_media": 0,
            "idade_mediana": 0,
            "pct_sem_sp": 0,
            "pct_sem_responsavel": 0,
            "cards_aging": pd.DataFrame(),
            "por_prioridade": {},
            "por_tipo": {},
            "por_produto": pd.DataFrame(),
            "score_saude": 100,
            "status_saude": "🟢 Saudável",
            "faixas_idade": {"0-15": 0, "16-30": 0, "31-60": 0, "61-90": 0, "90+": 0},
            "cards_sem_sprint": pd.DataFrame(),
            "cards_sem_responsavel": pd.DataFrame(),
            "cards_sem_sp": pd.DataFrame(),
            "cards_estagnados": pd.DataFrame(),
            "mais_antigo": 0,
            "df_backlog": df_backlog,
            "recomendacoes": [],
        }
    
    # Calcular idade em dias
    df_backlog = df_backlog.copy()
    df_backlog['idade_dias'] = df_backlog['criado'].apply(lambda x: (hoje - x).days if pd.notna(x) else 0)
    df_backlog['dias_sem_update'] = df_backlog['atualizado'].apply(lambda x: (hoje - x).days if pd.notna(x) else 0)
    
    # Métricas básicas
    sp_pendentes = int(df_backlog['sp'].sum())
    idade_media = df_backlog['idade_dias'].mean()
    idade_mediana = df_backlog['idade_dias'].median()
    mais_antigo = df_backlog['idade_dias'].max()
    
    # Cards sem estimativa
    sem_sp = df_backlog[df_backlog['sp'] == 0]
    pct_sem_sp = len(sem_sp) / total_backlog * 100 if total_backlog > 0 else 0
    
    # Cards sem responsável
    sem_responsavel = df_backlog[df_backlog['desenvolvedor'] == 'Não atribuído']
    pct_sem_responsavel = len(sem_responsavel) / total_backlog * 100 if total_backlog > 0 else 0
    
    # Faixas de idade
    faixas_idade = {
        "0-15": len(df_backlog[df_backlog['idade_dias'] <= 15]),
        "16-30": len(df_backlog[(df_backlog['idade_dias'] > 15) & (df_backlog['idade_dias'] <= 30)]),
        "31-60": len(df_backlog[(df_backlog['idade_dias'] > 30) & (df_backlog['idade_dias'] <= 60)]),
        "61-90": len(df_backlog[(df_backlog['idade_dias'] > 60) & (df_backlog['idade_dias'] <= 90)]),
        "90+": len(df_backlog[df_backlog['idade_dias'] > 90]),
    }
    
    # Cards aging (> 60 dias)
    cards_aging = df_backlog[df_backlog['idade_dias'] > 60].sort_values('idade_dias', ascending=False)
    
    # Cards estagnados (sem update há mais de 30 dias)
    cards_estagnados = df_backlog[df_backlog['dias_sem_update'] > 30].sort_values('dias_sem_update', ascending=False)
    
    # Cards sem sprint
    cards_sem_sprint = df_backlog[df_backlog['sprint'] == 'Sem Sprint']
    
    # Distribuição por prioridade
    por_prioridade = df_backlog['prioridade'].value_counts().to_dict()
    
    # Distribuição por tipo
    por_tipo = df_backlog['tipo'].value_counts().to_dict()
    
    # Por produto
    por_produto = df_backlog.groupby('produto').agg({
        'ticket_id': 'count',
        'sp': 'sum',
        'idade_dias': 'mean'
    }).reset_index()
    por_produto.columns = ['Produto', 'Cards', 'SP', 'Idade Média']
    por_produto['Idade Média'] = por_produto['Idade Média'].round(1)
    
    # Calcular score de saúde do backlog (0-100)
    # Componentes:
    # - Idade média (30%) - penaliza se > 30 dias
    # - % sem SP (25%) - penaliza itens sem estimativa
    # - Taxa de crescimento aprox (25%) - baseado em aging
    # - Priorização (20%) - penaliza se muitos críticos
    
    score_idade = max(0, 30 - (idade_media / 3)) if idade_media <= 90 else 0
    score_sp = max(0, 25 - (pct_sem_sp / 2))
    score_aging = max(0, 25 - (faixas_idade["90+"] * 2))
    
    pct_criticos = por_prioridade.get('Highest', 0) + por_prioridade.get('High', 0) + por_prioridade.get('Alta', 0)
    pct_criticos = (pct_criticos / total_backlog * 100) if total_backlog > 0 else 0
    score_priorizacao = max(0, 20 - (pct_criticos / 2))
    
    score_saude = round(score_idade + score_sp + score_aging + score_priorizacao, 0)
    
    if score_saude >= 75:
        status_saude = "🟢 Saudável"
    elif score_saude >= 50:
        status_saude = "🟡 Atenção"
    elif score_saude >= 25:
        status_saude = "🟠 Alerta"
    else:
        status_saude = "🔴 Crítico"
    
    # Gerar recomendações
    recomendacoes = []
    
    if faixas_idade["90+"] > 0:
        recomendacoes.append({
            "tipo": "🗑️ Candidatos a Descarte",
            "msg": f"{faixas_idade['90+']} itens estão há mais de 90 dias no backlog. Considere descartá-los.",
            "criticidade": "alta"
        })
    
    if pct_sem_sp > 30:
        recomendacoes.append({
            "tipo": "📝 Refinamento Necessário",
            "msg": f"{pct_sem_sp:.0f}% do backlog não tem estimativa. Agende um grooming.",
            "criticidade": "media"
        })
    
    if pct_sem_responsavel > 40:
        recomendacoes.append({
            "tipo": "👤 Atribuir Responsáveis",
            "msg": f"{pct_sem_responsavel:.0f}% dos itens não têm responsável definido.",
            "criticidade": "media"
        })
    
    if len(cards_estagnados) > 5:
        recomendacoes.append({
            "tipo": "⏸️ Cards Estagnados",
            "msg": f"{len(cards_estagnados)} cards não são atualizados há mais de 30 dias.",
            "criticidade": "media"
        })
    
    if idade_media > 60:
        recomendacoes.append({
            "tipo": "⚠️ Backlog Envelhecido",
            "msg": f"Idade média de {idade_media:.0f} dias. Revise a priorização.",
            "criticidade": "alta"
        })
    
    return {
        "total_itens": total_backlog,
        "sp_pendentes": sp_pendentes,
        "idade_media": round(idade_media, 1),
        "idade_mediana": round(idade_mediana, 1),
        "pct_sem_sp": round(pct_sem_sp, 1),
        "pct_sem_responsavel": round(pct_sem_responsavel, 1),
        "cards_aging": cards_aging,
        "por_prioridade": por_prioridade,
        "por_tipo": por_tipo,
        "por_produto": por_produto,
        "score_saude": score_saude,
        "status_saude": status_saude,
        "faixas_idade": faixas_idade,
        "cards_sem_sprint": cards_sem_sprint,
        "cards_sem_responsavel": sem_responsavel,
        "cards_sem_sp": sem_sp,
        "cards_estagnados": cards_estagnados,
        "mais_antigo": mais_antigo,
        "df_backlog": df_backlog,
        "recomendacoes": recomendacoes,
    }


def criar_grafico_aging_backlog(faixas: Dict) -> go.Figure:
    """Cria gráfico de barras para faixas de aging do backlog."""
    labels = ['0-15 dias', '16-30 dias', '31-60 dias', '61-90 dias', '90+ dias']
    values = [faixas['0-15'], faixas['16-30'], faixas['31-60'], faixas['61-90'], faixas['90+']]
    colors = ['#22c55e', '#eab308', '#f97316', '#ef4444', '#7f1d1d']
    
    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker_color=colors,
        text=values,
        textposition='auto',
    ))
    
    fig.update_layout(
        title="📊 Distribuição por Idade no Backlog",
        xaxis_title="Faixa de Idade",
        yaxis_title="Quantidade de Cards",
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=False
    )
    
    return fig


def criar_grafico_prioridade_backlog(por_prioridade: Dict) -> go.Figure:
    """Cria gráfico de pizza para distribuição por prioridade."""
    labels = list(por_prioridade.keys())
    values = list(por_prioridade.values())
    
    # Cores por prioridade
    cores_prioridade = {
        'Highest': '#7f1d1d',
        'High': '#ef4444',
        'Alta': '#ef4444',
        'Medium': '#f59e0b',
        'Média': '#f59e0b',
        'Low': '#22c55e',
        'Baixa': '#22c55e',
        'Lowest': '#64748b',
    }
    colors = [cores_prioridade.get(l, '#6b7280') for l in labels]
    
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        marker_colors=colors,
        textinfo='label+percent',
        hole=0.4
    ))
    
    fig.update_layout(
        title="🎯 Distribuição por Prioridade",
        height=350,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


def criar_grafico_tipo_backlog(por_tipo: Dict) -> go.Figure:
    """Cria gráfico de barras horizontais para distribuição por tipo."""
    labels = list(por_tipo.keys())
    values = list(por_tipo.values())
    
    cores_tipo = {
        'TAREFA': '#3b82f6',
        'BUG': '#ef4444',
        'HOTFIX': '#f97316',
        'SUGESTÃO': '#8b5cf6',
    }
    colors = [cores_tipo.get(l, '#6b7280') for l in labels]
    
    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation='h',
        marker_color=colors,
        text=values,
        textposition='auto',
    ))
    
    fig.update_layout(
        title="📋 Distribuição por Tipo",
        xaxis_title="Quantidade",
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


def criar_grafico_backlog_por_produto(df_produto: pd.DataFrame) -> go.Figure:
    """Cria gráfico de barras para backlog por produto."""
    if df_produto.empty:
        fig = go.Figure()
        fig.add_annotation(text="Sem dados por produto", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_produto['Produto'],
        y=df_produto['Cards'],
        name='Cards',
        marker_color='#3b82f6',
        text=df_produto['Cards'],
        textposition='auto',
    ))
    
    fig.update_layout(
        title="📦 Backlog por Produto",
        xaxis_title="Produto",
        yaxis_title="Quantidade de Cards",
        height=350,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


def aba_backlog(df: pd.DataFrame):
    """Aba de análise do Product Backlog (PB)."""
    st.markdown("### 📋 Product Backlog - Análise de Gargalos")
    st.caption("Visualize a saúde do backlog, identifique itens estagnados e tome decisões de priorização")
    
    metricas = calcular_metricas_backlog(df)
    
    # Score de Saúde do Backlog
    with st.expander("🏥 Saúde do Backlog", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            score = metricas['score_saude']
            cor = 'green' if score >= 75 else 'yellow' if score >= 50 else 'orange' if score >= 25 else 'red'
            criar_card_metrica(f"{score:.0f}", "Health Score", cor, metricas['status_saude'])
        
        with col2:
            criar_card_metrica(str(metricas['total_itens']), "Total no Backlog", "blue", f"{metricas['sp_pendentes']} SP pendentes")
        
        with col3:
            cor = 'green' if metricas['idade_media'] <= 30 else 'yellow' if metricas['idade_media'] <= 60 else 'red'
            criar_card_metrica(f"{metricas['idade_media']:.0f}d", "Idade Média", cor, f"Mediana: {metricas['idade_mediana']:.0f}d")
        
        with col4:
            cor = 'green' if metricas['pct_sem_sp'] <= 20 else 'yellow' if metricas['pct_sem_sp'] <= 40 else 'red'
            criar_card_metrica(f"{metricas['pct_sem_sp']:.0f}%", "Sem Estimativa", cor, f"{len(metricas['cards_sem_sp'])} cards")
        
        st.caption("💡 **Health Score:** Pontuação composta (0-100) baseada em idade, estimativas, aging e priorização")
    
    # Recomendações automáticas
    if metricas['recomendacoes']:
        with st.expander("💡 Recomendações Automáticas", expanded=True):
            for rec in metricas['recomendacoes']:
                classe = 'alert-critical' if rec['criticidade'] == 'alta' else 'alert-warning'
                st.markdown(f"""
                <div class="{classe}">
                    <b>{rec['tipo']}</b>
                    <p>{rec['msg']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Análise de Aging
    with st.expander("📊 Análise de Envelhecimento (Aging)", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            fig = criar_grafico_aging_backlog(metricas['faixas_idade'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 📈 Métricas de Aging")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Item Mais Antigo", f"{metricas['mais_antigo']} dias")
                st.metric("Cards > 60 dias", f"{metricas['faixas_idade']['61-90'] + metricas['faixas_idade']['90+']}")
            with col_b:
                st.metric("Cards > 90 dias", f"{metricas['faixas_idade']['90+']}")
                st.metric("Idade Mediana", f"{metricas['idade_mediana']:.0f} dias")
            
            if metricas['faixas_idade']['90+'] > 0:
                st.warning(f"⚠️ {metricas['faixas_idade']['90+']} cards estão há mais de 90 dias no backlog - candidatos a descarte!")
    
    # Cards Aging (> 60 dias)
    if not metricas['cards_aging'].empty:
        with st.expander(f"⏰ Cards Aging - Mais de 60 dias ({len(metricas['cards_aging'])} cards)", expanded=False):
            df_display = metricas['cards_aging'][['ticket_id', 'titulo', 'idade_dias', 'prioridade', 'produto', 'sp', 'desenvolvedor']].copy()
            df_display.columns = ['Ticket', 'Título', 'Dias', 'Prioridade', 'Produto', 'SP', 'Responsável']
            df_display['Título'] = df_display['Título'].str[:50] + '...'
            
            # Adicionar link
            df_display['Ticket'] = df_display['Ticket'].apply(lambda x: f"[{x}]({link_jira(x)})")
            
            st.dataframe(df_display.head(20), hide_index=True, use_container_width=True)
            
            if len(metricas['cards_aging']) > 20:
                st.caption(f"Mostrando 20 de {len(metricas['cards_aging'])} cards")
    
    # Distribuição
    with st.expander("📊 Distribuição do Backlog", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            if metricas['por_prioridade']:
                fig = criar_grafico_prioridade_backlog(metricas['por_prioridade'])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados de prioridade disponíveis")
        
        with col2:
            if metricas['por_tipo']:
                fig = criar_grafico_tipo_backlog(metricas['por_tipo'])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados de tipo disponíveis")
    
    # Por Produto
    with st.expander("📦 Backlog por Produto", expanded=True):
        if not metricas['por_produto'].empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = criar_grafico_backlog_por_produto(metricas['por_produto'])
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 📋 Resumo por Produto")
                st.dataframe(metricas['por_produto'].sort_values('Cards', ascending=False), hide_index=True, use_container_width=True)
        else:
            st.info("Sem dados por produto disponíveis")
    
    # Cards Problemáticos
    with st.expander("⚠️ Cards que Precisam de Atenção", expanded=False):
        tab_sem_sp, tab_sem_resp, tab_estagnados = st.tabs([
            f"📝 Sem Estimativa ({len(metricas['cards_sem_sp'])})",
            f"👤 Sem Responsável ({len(metricas['cards_sem_responsavel'])})",
            f"⏸️ Estagnados ({len(metricas['cards_estagnados'])})"
        ])
        
        with tab_sem_sp:
            if not metricas['cards_sem_sp'].empty:
                st.markdown("Cards que precisam de estimativa (Story Points):")
                mostrar_lista_df_completa(metricas['cards_sem_sp'], "Sem Estimativa")
            else:
                st.success("✅ Todos os cards têm estimativa!")
        
        with tab_sem_resp:
            if not metricas['cards_sem_responsavel'].empty:
                st.markdown("Cards sem responsável atribuído:")
                mostrar_lista_df_completa(metricas['cards_sem_responsavel'], "Sem Responsável")
            else:
                st.success("✅ Todos os cards têm responsável!")
        
        with tab_estagnados:
            if not metricas['cards_estagnados'].empty:
                st.markdown("Cards sem movimentação há mais de 30 dias:")
                df_estag = metricas['cards_estagnados'][['ticket_id', 'titulo', 'dias_sem_update', 'prioridade', 'desenvolvedor']].copy()
                df_estag.columns = ['Ticket', 'Título', 'Dias sem Update', 'Prioridade', 'Responsável']
                df_estag['Título'] = df_estag['Título'].str[:40] + '...'
                st.dataframe(df_estag.head(15), hide_index=True, use_container_width=True)
            else:
                st.success("✅ Nenhum card estagnado!")
    
    # Tooltip explicativo
    with st.expander("ℹ️ Sobre esta Aba", expanded=False):
        st.markdown("""
        ### 📋 Product Backlog - O que analisamos?
        
        Esta aba foi criada para ajudar na **gestão saudável do backlog**, identificando:
        
        | Métrica | O que significa |
        |---------|-----------------|
        | **Health Score** | Pontuação geral da saúde do backlog (0-100) |
        | **Idade Média** | Quanto tempo os itens ficam parados |
        | **Aging** | Cards que estão há muito tempo esperando |
        | **Sem Estimativa** | Cards sem Story Points definidos |
        | **Estagnados** | Cards sem movimentação recente |
        
        ### 🎯 Recomendações:
        - Cards **> 90 dias** são candidatos a descarte
        - **Idade média > 60 dias** indica backlog represado
        - **> 30% sem estimativa** requer grooming urgente
        """)


def aba_historico(df: pd.DataFrame):
    """Aba de Histórico/Tendências - ENRIQUECIDA."""
    st.markdown("### 📈 Histórico e Tendências")
    st.caption("Visualize a evolução das métricas ao longo das sprints. *Dados demonstrativos para visualização do potencial da ferramenta.*")
    
    df_tendencia = gerar_dados_tendencia()
    
    # Insights automáticos
    with st.expander("💡 Insights Automáticos", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        ultimo_fk = df_tendencia['fator_k'].iloc[-1]
        primeiro_fk = df_tendencia['fator_k'].iloc[0]
        variacao_fk = ((ultimo_fk - primeiro_fk) / primeiro_fk) * 100 if primeiro_fk > 0 else 0
        
        with col1:
            if variacao_fk > 0:
                st.markdown(f"""
                <div class="alert-success">
                    <b>📈 Fator K em crescimento</b>
                    <p>+{variacao_fk:.1f}% nas últimas sprints</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="alert-warning">
                    <b>📉 Fator K em queda</b>
                    <p>{variacao_fk:.1f}% nas últimas sprints</p>
                </div>
                """, unsafe_allow_html=True)
        
        ultimo_fpy = df_tendencia['fpy'].iloc[-1]
        with col2:
            if ultimo_fpy >= 80:
                st.markdown(f"""
                <div class="alert-success">
                    <b>✅ FPY acima da meta</b>
                    <p>{ultimo_fpy:.1f}% (meta: 80%)</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="alert-info">
                    <b>ℹ️ FPY abaixo da meta</b>
                    <p>{ultimo_fpy:.1f}% ({80 - ultimo_fpy:.1f}% abaixo)</p>
                </div>
                """, unsafe_allow_html=True)
        
        ultimo_lead = df_tendencia['lead_time_medio'].iloc[-1]
        with col3:
            if ultimo_lead <= 7:
                st.markdown(f"""
                <div class="alert-success">
                    <b>⚡ Lead Time saudável</b>
                    <p>{ultimo_lead:.1f} dias (meta: ≤7)</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="alert-warning">
                    <b>⏱️ Lead Time alto</b>
                    <p>{ultimo_lead:.1f} dias (meta: ≤7)</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Gráficos de evolução
    with st.expander("🏆 Evolução do Fator K (Maturidade)", expanded=True):
        fig = criar_grafico_tendencia_fator_k(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
        mostrar_tooltip("fator_k")
    
    with st.expander("📊 Evolução de Qualidade (FPY e DDP)", expanded=True):
        fig = criar_grafico_tendencia_qualidade(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            mostrar_tooltip("fpy")
        with col2:
            mostrar_tooltip("ddp")
    
    with st.expander("🐛 Evolução de Bugs", expanded=False):
        fig = criar_grafico_tendencia_bugs(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("🏥 Evolução do Health Score", expanded=False):
        fig = criar_grafico_tendencia_health(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
        mostrar_tooltip("health_score")
    
    with st.expander("📦 Throughput (Vazão de Entrega)", expanded=False):
        fig = criar_grafico_throughput(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
        mostrar_tooltip("throughput")
    
    with st.expander("⏱️ Lead Time Médio", expanded=False):
        fig = criar_grafico_lead_time(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
        mostrar_tooltip("lead_time")
    
    with st.expander("❌ Taxa de Reprovação", expanded=False):
        fig = criar_grafico_reprovacao(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabela de dados históricos
    with st.expander("📋 Dados Históricos Completos", expanded=False):
        st.dataframe(df_tendencia, hide_index=True, use_container_width=True)


def aba_lideranca(df: pd.DataFrame):
    """Aba de Liderança com decisões estratégicas."""
    st.markdown("### 🎯 Painel de Liderança")
    st.caption("Visão executiva para tomada de decisão - Go/No-Go de release")
    
    # Health Score
    health = calcular_health_score(df)
    
    # Métricas globais
    total_cards = len(df)
    sp_total = int(df['sp'].sum())
    bugs_total = int(df['bugs'].sum())
    concluidos = len(df[df['status_cat'] == 'done'])
    pct_conclusao = concluidos / total_cards * 100 if total_cards > 0 else 0
    fk = calcular_fator_k(sp_total, bugs_total)
    mat = classificar_maturidade(fk)
    
    # Card de decisão
    dias_release = df['dias_ate_release'].max() if 'dias_ate_release' in df.columns else 10
    bloqueados = len(df[df['status_cat'].isin(['blocked', 'rejected'])])
    
    if bloqueados > 0 or pct_conclusao < 30:
        decisao = "🛑 ATENÇÃO NECESSÁRIA"
        decisao_cor = "red"
        decisao_msg = "Cards bloqueados ou taxa de conclusão muito baixa - avaliar riscos"
    elif pct_conclusao < 50 and dias_release < 3:
        decisao = "⚠️ REVISAR ESCOPO"
        decisao_cor = "yellow"
        decisao_msg = "Pouco tempo e muitos cards pendentes - considerar redução de escopo"
    else:
        decisao = "✅ NO CAMINHO"
        decisao_cor = "green"
        decisao_msg = "Sprint progredindo conforme esperado"
    
    # Layout
    with st.expander("🚦 Decisão de Release (Go/No-Go)", expanded=True):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"""
            <div class="status-card status-{decisao_cor}" style="padding: 25px;">
                <p style="font-size: 24px; margin: 0;">{decisao}</p>
                <p class="card-label" style="margin-top: 10px;">{decisao_msg}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            cor_health = 'green' if health['score'] >= 75 else 'yellow' if health['score'] >= 50 else 'red'
            criar_card_metrica(f"{health['score']:.0f}", "Health Score", cor_health, health['status'])
        
        with col2:
            col_a, col_b, col_c, col_d = st.columns(4)
            
            with col_a:
                st.metric("Cards", total_cards)
            with col_b:
                st.metric("Concluídos", f"{pct_conclusao:.0f}%")
            with col_c:
                st.metric("Fator K", f"{fk:.1f}", mat['selo'])
            with col_d:
                st.metric("Dias até Release", dias_release)
            
            st.markdown("---")
            
            # Composição do Health Score
            st.markdown("**📊 Composição do Health Score:**")
            cols = st.columns(5)
            nomes = {'conclusao': 'Conclusão', 'ddp': 'DDP', 'fpy': 'FPY', 'gargalos': 'Gargalos', 'lead_time': 'Lead Time'}
            
            for i, (key, det) in enumerate(health['detalhes'].items()):
                with cols[i]:
                    cor = '#22c55e' if det['score'] >= det['peso'] * 0.7 else '#f59e0b' if det['score'] >= det['peso'] * 0.4 else '#ef4444'
                    st.markdown(f"""
                    <div style="text-align: center; padding: 10px; background: {cor}20; border-radius: 8px;">
                        <p style="font-size: 18px; font-weight: bold; margin: 0;">{det['score']:.0f}/{det['peso']}</p>
                        <p style="font-size: 11px; margin: 3px 0 0 0;">{nomes.get(key, key)}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        mostrar_tooltip("health_score")
    
    # Pontos de atenção COM LISTAGEM COMPLETA
    with st.expander("🚨 Pontos de Atenção", expanded=True):
        # Cards bloqueados
        bloqueados_df = df[df['status_cat'].isin(['blocked', 'rejected'])]
        if not bloqueados_df.empty:
            st.markdown(f"""
            <div class="alert-critical">
                <b>🚫 {len(bloqueados_df)} card(s) bloqueado(s)/reprovado(s)</b>
            </div>
            """, unsafe_allow_html=True)
            mostrar_lista_df_completa(bloqueados_df, "Cards Bloqueados/Reprovados")
        
        # Alta prioridade não concluídos
        alta_prio = df[(df['prioridade'].isin(['Alta', 'Muito Alta', 'Muito alto', 'Alto', 'Highest', 'High'])) & (df['status_cat'] != 'done')]
        if not alta_prio.empty:
            st.markdown(f"""
            <div class="alert-warning">
                <b>⚠️ {len(alta_prio)} card(s) de alta prioridade em andamento</b>
            </div>
            """, unsafe_allow_html=True)
            mostrar_lista_df_completa(alta_prio, "Alta Prioridade Pendentes")
        
        # Fora da janela de validação (considera complexidade)
        cards_pendentes = df[df['status_cat'].isin(['waiting_qa', 'testing'])]
        fora_janela = cards_pendentes[cards_pendentes['janela_status'] == 'fora'] if not cards_pendentes.empty else pd.DataFrame()
        em_risco = cards_pendentes[cards_pendentes['janela_status'] == 'risco'] if not cards_pendentes.empty else pd.DataFrame()
        
        if not fora_janela.empty:
            st.markdown(f"""
            <div class="alert-critical">
                <b>🚨 {len(fora_janela)} card(s) SEM TEMPO para validação nesta sprint!</b>
                <p style="font-size: 12px; margin-top: 5px;">Considerar para próxima sprint baseado na complexidade de teste.</p>
            </div>
            """, unsafe_allow_html=True)
            # Mostrar tabela com detalhes
            df_fora = fora_janela[['ticket_id', 'titulo', 'complexidade', 'dias_ate_release', 'janela_dias_necessarios', 'qa']].copy()
            df_fora.columns = ['Ticket', 'Título', 'Complexidade', 'Dias Disponíveis', 'Dias Necessários', 'QA']
            df_fora['Título'] = df_fora['Título'].str[:35] + '...'
            df_fora['Complexidade'] = df_fora['Complexidade'].replace('', 'Não definida')
            st.dataframe(df_fora, hide_index=True, use_container_width=True)
        
        if not em_risco.empty:
            st.markdown(f"""
            <div class="alert-warning">
                <b>⚠️ {len(em_risco)} card(s) EM RISCO - no limite de tempo!</b>
            </div>
            """, unsafe_allow_html=True)
        
        if bloqueados_df.empty and alta_prio.empty and fora_janela.empty and em_risco.empty:
            st.success("✅ Nenhum ponto crítico identificado!")
    
    # Performance por Desenvolvedor
    with st.expander("👨‍💻 Performance por Desenvolvedor", expanded=False):
        dev_metricas = calcular_metricas_dev(df)
        st.dataframe(dev_metricas['stats'], hide_index=True, use_container_width=True)
    
    # Exportação
    with st.expander("📥 Exportar Dados", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            csv = exportar_para_csv(df)
            st.download_button("📄 Baixar CSV", csv, f"nina_dashboard_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
        
        with col2:
            try:
                excel = exportar_para_excel(df, {'health_score': health['score']})
                if excel:
                    st.download_button("📊 Baixar Excel", excel, f"nina_dashboard_{datetime.now().strftime('%Y%m%d')}.xlsx", 
                                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except:
                st.info("Instale openpyxl para exportar Excel: pip install openpyxl")


def aba_sobre():
    """Aba Sobre - Objetivo do Dashboard e Fontes das Métricas."""
    st.markdown("### ℹ️ Sobre o NinaDash")
    st.caption("Objetivo, métricas utilizadas e referências teóricas")
    
    # Sobre a NINA
    with st.expander("🤖 NINA Tecnologia", expanded=True):
        st.markdown("""
        <div style="background: linear-gradient(135deg, #AF0C37 0%, #8B0A2C 100%); padding: 24px; border-radius: 12px; margin-bottom: 16px;">
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
    
    # Objetivo do Dashboard
    with st.expander("🎯 Objetivo do Dashboard", expanded=True):
        st.markdown("""
        ### 📊 NinaDash — Dashboard de Inteligência e Métricas de QA
        
        **Propósito central:** Transformar o QA de um processo sem visibilidade em um **sistema de inteligência operacional baseado em dados**.
        
        ---
        
        #### 🚨 Problema que resolve
        
        | Antes do NinaDash | Depois do NinaDash |
        |---|---|
        | ❌ Falta de mensuração real do tempo de validação | ✅ Coleta automatizada de métricas |
        | ❌ Zero previsibilidade de entregas | ✅ Cálculo em tempo real de SLAs |
        | ❌ Uso do Notion como controle manual | ✅ Integração direta com Jira |
        | ❌ Falta de segurança na validação de cards | ✅ Monitoramento da janela de release (3 dias úteis) |
        | ❌ Decisões baseadas em "feeling" | ✅ Decisão orientada por dados |
        
        ---
        
        #### ⚡ Diferencial
        
        | Dashboards Comuns | NinaDash |
        |---|---|
        | Métricas genéricas | Métricas baseadas em QA (ISTQB) |
        | Dados estáticos | Integração em tempo real |
        | Foco em volume | Foco em **qualidade e maturidade** |
        | Sem contexto de QA | Janela de release com dias úteis |
        | Métricas isoladas | Health Score para decisão Go/No-Go |
        """)
    
    # Métricas implementadas
    with st.expander("📊 Métricas Implementadas (ISTQB-Aligned)", expanded=True):
        st.markdown("""
        O dashboard implementa métricas fundamentais do **ISTQB Foundation Level**, fornecendo uma visão completa do ciclo de qualidade:
        
        | Métrica | Descrição | Impacto |
        |---------|-----------|---------|
        | **FPY (First Pass Yield)** | Cards aprovados de primeira sem bugs | Mede eficiência do desenvolvimento |
        | **DDP (Defect Detection Percentage)** | Eficácia do QA em encontrar bugs | Indica maturidade do processo de testes |
        | **Fator K** | Relação SP/Bugs (SP/(Bugs+1)) | Classifica maturidade individual |
        | **Lead Time** | Tempo do início ao fim do card | Identifica gargalos no fluxo |
        | **Health Score** | Score composto de saúde da release | Suporta decisão Go/No-Go |
        | **WIP (Work In Progress)** | Cards simultâneos por pessoa | Controla sobrecarga |
        | **Throughput** | Vazão de entrega por sprint | Indica capacidade do time |
        """)
    
    # Fórmulas
    with st.expander("🧮 Fórmulas Principais", expanded=False):
        st.markdown("""
        ### Fator K (Maturidade)
        ```
        FK = SP / (Bugs + 1)
        ```
        - **🥇 Gold (≥3.0):** Excelente qualidade
        - **🥈 Silver (2.0-2.9):** Boa qualidade
        - **🥉 Bronze (1.0-1.9):** Regular
        - **⚠️ Risco (<1.0):** Crítico
        
        ---
        
        ### Health Score (Saúde da Release)
        ```
        HS = (Conclusão×30 + DDP×25 + FPY×20 + Gargalos×15 + LeadTime×10) / 100
        ```
        - **🟢 ≥75:** Saudável - Release pode seguir
        - **🟡 50-74:** Atenção - Monitorar riscos
        - **🟠 25-49:** Alerta - Ação necessária
        - **🔴 <25:** Crítico - Avaliar adiamento
        
        ---
        
        ### First Pass Yield (FPY)
        ```
        FPY = (Cards sem bugs / Total de cards) × 100
        ```
        
        ### Defect Detection Percentage (DDP)
        ```
        DDP = (Bugs encontrados em QA / Total estimado de bugs) × 100
        ```
        
        ### Janela de Release
        ```
        ≥ 3 dias úteis antes da release = Dentro da janela ✅
        ```
        """)
    
    # Fundamentos Teóricos
    with st.expander("📚 Fundamentos Teóricos", expanded=False):
        st.markdown("""
        ### 🎓 ISTQB/CTFL - International Software Testing Qualifications Board
        
        O **ISTQB Foundation Level (CTFL)** define padrões globais para métricas de teste:
        
        **Métricas de Processo** (implementadas no dashboard):
        - *Defect Detection Percentage (DDP)*: Eficácia do QA
        - *First Pass Yield (FPY)*: Qualidade na primeira entrega
        - *Rework Effort Ratio*: Esforço gasto em correções
        
        **Métricas de Produto**:
        - *Defect Density*: Bugs por unidade de tamanho (SP)
        - *Test Coverage*: Cobertura de testes automatizados
        
        > *"We cannot improve what we cannot measure"* - ISTQB Syllabus
        
        **Referência**: [ISTQB CTFL Syllabus v4.0](https://www.istqb.org/certifications/certified-tester-foundation-level)
        
        ---
        
        ### 🔄 TDD - Test-Driven Development (Kent Beck)
        
        O **TDD** segue o ciclo **Red-Green-Refactor**:
        1. 🔴 **Red**: Escrever um teste que falha
        2. 🟢 **Green**: Escrever código mínimo para passar
        3. 🔵 **Refactor**: Melhorar o código mantendo testes passando
        
        **Como o Fator K se relaciona com TDD**:
        - Devs que praticam TDD tendem a ter **FK mais alto**
        - Menos bugs = maior proporção SP/Bugs
        - Selo Gold incentiva a prática
        
        **Referência**: [Martin Fowler - TDD](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
        
        ---
        
        ### 📈 Shift-Left Testing
        
        O conceito move as atividades de teste para o início do ciclo:
        
        ```
        Tradicional:  Requisitos → Desenvolvimento → [TESTES] → Deploy
        Shift-Left:   [TESTES] → Requisitos → [TESTES] → Dev → [TESTES] → Deploy
        ```
        
        **Estatísticas da indústria**:
        - Bug encontrado em dev: **$100** para corrigir
        - Bug encontrado em QA: **$1.500** para corrigir  
        - Bug encontrado em produção: **$10.000+** para corrigir
        
        > O dashboard ajuda a NINA a encontrar bugs mais cedo, economizando recursos.
        """)
    
    # Tomada de Decisão
    with st.expander("🧠 Tomada de Decisão por Perfil", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 👥 Para QA
            - Priorização de cards
            - Gestão de carga
            - Avaliação de risco de release
            - Identificação de aging
            """)
        
        with col2:
            st.markdown("""
            ### 🧑‍💼 Para Liderança
            - Go / No-Go de release
            - Performance do time
            - Identificação de gargalos
            - Health Score da sprint
            """)
        
        with col3:
            st.markdown("""
            ### 👨‍💻 Para Devs
            - Feedback de qualidade (Fator K)
            - Taxa de retrabalho
            - Tempo de ciclo
            - Cards pendentes
            """)
    
    # Governança
    with st.expander("🏢 Governança", expanded=False):
        st.markdown("""
        | Informação | Valor |
        |------------|-------|
        | **Desenvolvido por** | QA NINA |
        | **Mantido por** | Vinícios Ferreira |
        | **Versão** | v8.7 |
        | **Última atualização** | Abril 2026 |
        | **Stack** | Python, Streamlit, Plotly, Pandas |
        | **Integração** | Jira API REST |
        """)
    
    # Abas Disponíveis
    with st.expander("📑 Abas Disponíveis", expanded=True):
        st.markdown("""
        ### Visão Geral das Abas
        
        | Aba | Descrição | Público-Alvo |
        |-----|-----------|---------------|
        | **📊 Visão Geral** | KPIs principais, Health Score, alertas e progresso da release | Todos |
        | **🔬 QA** | Funil de validação, carga por QA, aging, comparativo entre QAs, bugs | QA, Liderança |
        | **👨‍💻 Dev** | Ranking Fator K, performance individual, WIP, code review, análise Tech Lead | Devs, Tech Lead |
        | **📋 Governança** | Qualidade dos dados, campos obrigatórios, compliance | PO, Liderança |
        | **📦 Produto** | Métricas por produto, Health Score, tendências | PO, Stakeholders |
        | **� Backlog** | Saúde do backlog, aging, gargalos, cards problemáticos, recomendações | PO, Liderança |
        | **�📈 Histórico** | Evolução de métricas entre releases, tendências | Liderança |
        | **🎯 Liderança** | Decisão Go/No-Go, riscos, simulações | Gerentes, Diretores |
        | **ℹ️ Sobre** | Esta documentação | Todos |
        
        ---
        
        ### 👨‍💻 Aba de Dev em Detalhe
        
        **Ranking Geral:**
        - 🏆 Tabela de ranking com Fator K, FPY, SP, Bugs
        - 📊 Gráfico de Fator K com meta (FK ≥ 2)
        - ⚠️ Lista de devs que precisam de atenção
        
        **Análise do Time:**
        - Cards por desenvolvedor
        - Taxa de bugs por card
        - Métricas gerais (total cards, bugs, lead time)
        
        **Análise para Tech Lead:**
        - Distribuição de SP por dev
        - Status de entrega (Concluído vs Em andamento)
        - Work-In-Progress (WIP)
        - Fila de Code Review
        - Velocidade (SP/Card)
        - Cards críticos de alta prioridade
        
        **Visão Individual:**
        - Selo de maturidade (Gold/Silver/Bronze/Risco)
        - Métricas detalhadas
        - Lista de cards com status
        """)


# ==============================================================================
# FUNÇÃO PRINCIPAL
# ==============================================================================

def main():
    """Função principal do dashboard."""
    
    # ========== VERIFICAR LOGIN ==========
    if not verificar_login():
        mostrar_tela_login()
        return
    
    # ========== USUÁRIO LOGADO - DASHBOARD ==========
    aplicar_estilos()
    
    # Header principal com logo Nina
    mostrar_header_nina()
    
    # Captura query params para compartilhamento de busca
    query_params = st.query_params
    card_compartilhado = query_params.get("card", None)
    projeto_param = query_params.get("projeto", None)
    
    # Inicializa session_state para controle de busca
    if 'busca_ativa' not in st.session_state:
        st.session_state.busca_ativa = False
    if 'card_buscado' not in st.session_state:
        st.session_state.card_buscado = ""
    if 'projeto_buscado' not in st.session_state:
        st.session_state.projeto_buscado = "SD"
    
    # Se veio via URL, ativa a busca automaticamente
    if card_compartilhado and not st.session_state.busca_ativa:
        st.session_state.busca_ativa = True
        st.session_state.card_buscado = card_compartilhado
        st.session_state.projeto_buscado = projeto_param if projeto_param else "SD"
    
    # Sidebar reorganizada
    with st.sidebar:
        # ===== HEADER: Logo centralizada + Nome + Descrição =====
        st.markdown('''
        <div style="text-align: center; padding: 10px 0 5px 0;">
            <svg width="70" height="70" viewBox="0 0 187 187" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M173.709 89.2107C172.209 86.6048 169.414 84.838 166.225 84.838C163.036 84.838 160.241 86.5649 158.741 89.1627H151.683C149.465 58.8237 124.495 35 94.0216 35C63.5489 35 38.5862 58.8237 36.3678 89.1627H29.1759C27.6759 86.5649 24.8734 84.798 21.6682 84.798C18.463 84.798 15.6605 86.5806 14.1605 89.2031C13.4184 90.4899 13 92.001 13 93.6C13 95.1987 13.4184 96.7017 14.1605 97.997C15.6605 100.619 18.463 102.306 21.6682 102.306C24.8734 102.306 27.6838 100.435 29.1759 97.8369H36.3678C38.5862 128.168 63.5489 152 94.0216 152C124.495 152 149.465 128.176 151.675 97.8369H158.686C160.178 100.435 162.996 102.354 166.217 102.354C169.438 102.354 172.256 100.611 173.749 97.9648C174.475 96.6856 174.885 95.2148 174.885 93.6319C174.885 92.049 174.451 90.5222 173.701 89.2188L173.709 89.2107ZM111.145 125.554C107.971 131.518 101.758 135.459 94.5981 135.459C87.4374 135.459 81.2248 131.566 78.0509 125.602C77.1666 123.947 78.3667 122.092 80.2219 122.092H108.982C110.837 122.092 112.029 123.891 111.153 125.554H111.145ZM140.528 94.1277C140.528 103.825 132.76 111.691 123.184 111.691H65.4432C55.8675 111.691 48.0991 103.825 48.0991 94.1277V93.7199C48.0991 84.0223 55.8675 76.1557 65.4432 76.1557H123.184C132.76 76.1557 140.528 84.0223 140.528 93.7199V94.1277Z" fill="#AF0C37"/>
            <path d="M76.5809 105.311C82.9686 105.311 88.1466 100.068 88.1466 93.5996C88.1466 87.1312 82.9686 81.8875 76.5809 81.8875C70.1936 81.8875 65.0156 87.1312 65.0156 93.5996C65.0156 100.068 70.1936 105.311 76.5809 105.311Z" fill="#AF0C37"/>
            <path d="M111.437 105.311C117.824 105.311 123.002 100.068 123.002 93.5996C123.002 87.1312 117.824 81.8875 111.437 81.8875C105.049 81.8875 99.8712 87.1312 99.8712 93.5996C99.8712 100.068 105.049 105.311 111.437 105.311Z" fill="#AF0C37"/>
            </svg>
        </div>
        <div style="text-align: center; margin-bottom: 5px;">
            <h2 style="color: #AF0C37; margin: 0; font-size: 1.8em;">NinaDash</h2>
            <p style="color: #666; font-size: 0.85em; margin: 2px 0 0 0; font-style: italic;">
                Transformando dados em decisões
            </p>
        </div>
        ''', unsafe_allow_html=True)
        
        # ===== USUÁRIO LOGADO =====
        user_nome = st.session_state.get("user_nome", "Usuário")
        user_email = st.session_state.get("user_email", "")
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #AF0C37 0%, #8F0A2E 100%); 
                    padding: 12px; border-radius: 8px; margin: 10px 0; text-align: center;">
            <p style="margin: 0; color: white; font-size: 14px; font-weight: 500;">👤 {user_nome}</p>
            <p style="margin: 4px 0 0 0; color: #fecdd3; font-size: 11px;">{user_email}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botão de Logout
        if st.button("🚪 Sair", use_container_width=True, key="btn_logout"):
            fazer_logout()
            st.rerun()
        
        if not verificar_credenciais():
            st.error("⚠️ Credenciais não configuradas!")
            st.markdown("""
            Configure em `.streamlit/secrets.toml`:
            ```toml
            [jira]
            email = "seu-email"
            token = "seu-token"
            ```
            """)
            st.stop()
        
        st.markdown("---")
        
        # ===== SEÇÃO 1: BUSCA DE CARD =====
        st.markdown("##### 🔍 Busca Rápida de Card")
        
        # Projeto para busca
        projetos_lista = ["SD", "QA", "PB"]
        projeto_busca_index = 0
        if st.session_state.busca_ativa and st.session_state.projeto_buscado in projetos_lista:
            projeto_busca_index = projetos_lista.index(st.session_state.projeto_buscado)
        
        # Extrai número inicial se estiver buscando
        numero_inicial = ""
        if st.session_state.busca_ativa and st.session_state.card_buscado:
            numero_inicial = st.session_state.card_buscado.upper()
            for prefix in ["SD-", "QA-", "PB-"]:
                if numero_inicial.startswith(prefix):
                    numero_inicial = numero_inicial[len(prefix):]
                    break
        
        # Formulário permite Enter para buscar
        with st.form(key="form_busca_card", clear_on_submit=False):
            col_proj, col_num = st.columns([1.5, 1.5])
            with col_proj:
                projeto_busca = st.selectbox(
                    "Projeto",
                    projetos_lista,
                    index=projeto_busca_index,
                    label_visibility="collapsed",
                    help="SD, QA ou PB"
                )
            
            with col_num:
                numero_card_input = st.text_input(
                    "Número",
                    value=numero_inicial,
                    placeholder="1234",
                    label_visibility="collapsed",
                    max_chars=10
                )
            
            # Botão de buscar (submete com Enter também)
            buscar_clicado = st.form_submit_button("🔍 Buscar", use_container_width=True)
            
            if buscar_clicado:
                if numero_card_input:
                    st.session_state.busca_ativa = True
                    st.session_state.card_buscado = f"{projeto_busca}-{numero_card_input}"
                    st.session_state.projeto_buscado = projeto_busca
                    st.rerun()
                else:
                    st.warning("Digite o número do card")
        
        # Mostra indicador de pesquisa ativa
        if st.session_state.busca_ativa and st.session_state.card_buscado:
            st.markdown(f"""
            <div style="background: #fef3c7; border: 1px solid #f59e0b; border-radius: 6px; 
                        padding: 8px; margin: 8px 0; text-align: center;">
                <p style="margin: 0; color: #92400e; font-size: 0.85em;">
                    📍 <b>Visualizando:</b> {st.session_state.card_buscado.upper()}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Botão para voltar ao dashboard
            if st.button("⬅️ Voltar ao Dashboard", type="primary", use_container_width=True, key="btn_voltar"):
                st.session_state.busca_ativa = False
                st.session_state.card_buscado = ""
                st.session_state.projeto_buscado = "SD"
                st.query_params.clear()
                st.rerun()
        
        st.markdown("---")
        
        # ===== SEÇÃO 2: FILTROS (só mostra quando NÃO está pesquisando) =====
        if not st.session_state.busca_ativa:
            st.markdown("##### ⚙️ Filtros do Dashboard")
            
            projeto = st.selectbox("📁 Projeto", projetos_lista, index=0, key="projeto_dash")
            
            filtro_sprint = st.selectbox(
                "🗓️ Período",
                ["Sprint Ativa", "Últimos 30 dias", "Últimos 90 dias"],
                index=0
            )
        else:
            # Quando pesquisando, usa o projeto da busca
            projeto = st.session_state.projeto_buscado
            filtro_sprint = "Sprint Ativa"  # Não usado na busca específica
        
        # ===== SEÇÃO 3: RODAPÉ =====
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 5px 0;">
            <p style="color: #AF0C37; font-weight: bold; margin: 0; font-size: 0.85em;">
                📌 NINA Tecnologia
            </p>
            <p style="color: #888; font-size: 0.7em; margin: 2px 0 0 0;">
                v8.11 • Dashboard de Inteligência QA
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # ===== MODO BUSCA DE CARD ESPECÍFICO =====
    if st.session_state.busca_ativa and st.session_state.card_buscado:
        busca_card = st.session_state.card_buscado
        projeto_busca = st.session_state.projeto_buscado
        
        # Atualiza a URL com os parâmetros de compartilhamento
        st.query_params["card"] = busca_card
        st.query_params["projeto"] = projeto_busca
        
        # Busca o card específico (sem filtros de período)
        with st.spinner(f"🔍 Buscando {busca_card}..."):
            issue, links, comentarios = buscar_card_especifico(busca_card)
        
        if issue:
            # Processa o card encontrado
            card_data = processar_issue_unica(issue)
            exibir_card_detalhado_v2(card_data, links, comentarios, projeto_busca)
        else:
            st.warning(f"⚠️ Card **{busca_card}** não encontrado.")
            st.info("💡 Verifique se o ID está correto. O card será buscado em todo o histórico do projeto.")
    
    # ===== MODO DASHBOARD NORMAL =====
    else:
        # JQL
        if filtro_sprint == "Sprint Ativa":
            jql = f'project = {projeto} AND sprint in openSprints() ORDER BY created DESC'
        elif filtro_sprint == "Últimos 30 dias":
            jql = f'project = {projeto} AND created >= -30d ORDER BY created DESC'
        else:
            jql = f'project = {projeto} AND created >= -90d ORDER BY created DESC'
        
        # AUTO-LOAD
        with st.spinner("🔄 Carregando dados do Jira..."):
            issues, ultima_atualizacao = buscar_dados_jira_cached(projeto, jql)
        
        if issues is None:
            st.error("❌ Não foi possível carregar dados do Jira")
            st.stop()
        
        if len(issues) == 0:
            st.warning("⚠️ Nenhum card encontrado para os filtros selecionados")
            st.stop()
        
        df = processar_issues(issues)
        
        # Filtro por produto (dentro da sidebar)
        with st.sidebar:
            produtos_disponiveis = ['Todos'] + sorted(df['produto'].unique().tolist())
            filtro_produto = st.selectbox("📦 Produto", produtos_disponiveis, index=0, key="filtro_produto_main")
            
            if filtro_produto != 'Todos':
                df = df[df['produto'] == filtro_produto]
        
        # Abas condicionais por projeto (fluxo normal)
        if projeto == "PB":
            # Projeto PB: Aba de Backlog como foco principal
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📋 Backlog",
                "📊 Visão Geral",
                "📦 Produto",
                "📈 Histórico",
                "ℹ️ Sobre"
            ])
            
            with tab1:
                aba_backlog(df)
            
            with tab2:
                aba_visao_geral(df, ultima_atualizacao)
            
            with tab3:
                aba_produto(df)
            
            with tab4:
                aba_historico(df)
            
            with tab5:
                aba_sobre()
        
        else:
            # Projetos SD e QA: Abas completas com QA/Dev
            tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
                "📊 Visão Geral",
                "🔬 QA",
                "👨‍💻 Dev",
                "📋 Governança",
                "📦 Produto",
                "📈 Histórico",
                "🎯 Liderança",
                "ℹ️ Sobre"
            ])
            
            with tab1:
                aba_visao_geral(df, ultima_atualizacao)
            
            with tab2:
                aba_qa(df)
            
            with tab3:
                aba_dev(df)
            
            with tab4:
                aba_governanca(df)
            
            with tab5:
                aba_produto(df)
            
            with tab6:
                aba_historico(df)
            
            with tab7:
                aba_lideranca(df)
            
            with tab8:
                aba_sobre()


if __name__ == "__main__":
    main()
