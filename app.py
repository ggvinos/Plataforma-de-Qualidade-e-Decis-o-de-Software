"""
================================================================================
JIRA DASHBOARD v8.82 - NINA TECNOLOGIA - VERSÃO COMPLETA E ENRIQUECIDA
================================================================================
📊 NinaDash — Dashboard de Inteligência e Métricas de QA

🎯 Propósito: Transformar o QA de um processo sem visibilidade em um sistema 
   de inteligência operacional baseado em dados.

MELHORIAS v8.82:
- 🔧 FIX: Corrigido Meu Dashboard que não mostrava filtros corretamente
- 👤 PESSOAS: Lista de pessoas agora carrega corretamente
- ➕ ADICIONAR: Botão de adicionar widget agora funciona
- 📊 DEBUG: Mostra quantidade de dados e pessoas encontradas
- 🧹 SIMPLIFICADO: Interface mais limpa e direta

MELHORIAS v8.81:
- 🎨 MEU DASHBOARD: Tela totalmente nova para construir dashboards personalizados
- ➕ ADICIONAR WIDGETS: Construtor no topo para adicionar métricas  
- ⬆️⬇️ REORDENAR: Mova widgets para cima ou para baixo
- 🗑️ REMOVER: Exclua widgets que não precisa mais
- 📊 TEMPLATES: Visão Executiva, Foco DEV, Foco QA
- 💾 PERSISTÊNCIA: Dashboard salvo em cookie
- 🧹 SIDEBAR LIMPA: Apenas logo e botão voltar na tela do dashboard

MELHORIAS v8.80:
- 🎯 CONSULTA PERSONALIZADA: Tela separada para consultas avançadas
- 🔍 FILTROS DINÂMICOS: Pessoa, status, período, produto personalizados
- 📋 TIPOS DE CONSULTA: Cards, métricas, comparativos, tendências, bugs
- 💾 CONSULTAS SALVAS: Salve suas consultas favoritas
- 📅 PERÍODOS FLEXÍVEIS: Predefinidos ou datas personalizadas
- ⬅️ BOTÃO NA SIDEBAR: Acesso rápido à ferramenta avançada

MELHORIAS v8.78:
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
import extra_streamlit_components as stx

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
    page_title="NinaDash - Qualidade e Decisão de Software",
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
    # Campos para análise de Produto (Ellen)
    "temas": "customfield_10520",  # Temas/Clientes (multi-value)
    "importancia": "customfield_10522",  # Importância: Alto/Médio/Baixo
    "sla_status": "customfield_11124",  # SLA: Atrasado
}

# Temas que NÃO devem ser considerados como clientes
# Usados para demandas internas que beneficiam todos os clientes
TEMAS_NAO_CLIENTES = [
    "nina",
    "interna",
    "interno",
    "internal",
    "nina tecnologia",
    "nina - interno",
    "plataforma",  # Se aplicável
]

# URL base do NinaDash - CENTRALIZADA para facilitar alterações futuras
NINADASH_URL = "https://ninadash.streamlit.app/"

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
    # Status específicos do PB (Product Backlog)
    "pb_revisao_produto": ["Aguardando Revisão de Produto", "Revisão de Produto", "Análise de Produto"],
    "pb_roteiro": ["Em Roteiro", "Roteiro", "Definição de Roteiro"],
    "pb_ux": ["UX/Design", "UX Design", "Análise UX", "UX/UI"],
    "pb_esforco": ["Aguardando Esforço", "Estimativa de Esforço", "Aguarda Esforço"],
    "pb_aguarda_dev": ["Aguardando Desenvolvimento", "Aguarda Desenvolvimento", "Fila de Desenvolvimento"],
    "pb_aguardando_resposta": ["Aguardando Resposta", "Aguardando Cliente", "Aguarda Retorno"],
    # Status específicos do VALPROD (Validação em Produção)
    "valprod_pendente": ["Pendente", "Aguardando Validação", "Para Validar"],
    "valprod_validando": ["Em Validação", "Validando"],
    "valprod_aprovado": ["Aprovado", "Validado", "Concluído"],
    "valprod_rejeitado": ["Rejeitado", "Reprovado", "Com Problemas"],
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
    "unknown": "❓ Desconhecido",
    # PB
    "pb_revisao_produto": "📝 Revisão Produto",
    "pb_roteiro": "📋 Em Roteiro",
    "pb_ux": "🎨 UX/Design",
    "pb_esforco": "⏱️ Aguarda Esforço",
    "pb_aguarda_dev": "💻 Aguarda Dev",
    "pb_aguardando_resposta": "💬 Aguardando Resposta",
    # VALPROD
    "valprod_pendente": "⏳ Pendente Val Prod",
    "valprod_validando": "🔍 Validando",
    "valprod_aprovado": "✅ Aprovado",
    "valprod_rejeitado": "❌ Rejeitado",
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
    "unknown": "#9ca3af",
    # PB
    "pb_revisao_produto": "#6366f1",
    "pb_roteiro": "#8b5cf6",
    "pb_ux": "#ec4899",
    "pb_esforco": "#f97316",
    "pb_aguarda_dev": "#14b8a6",
    "pb_aguardando_resposta": "#f59e0b",
    # VALPROD
    "valprod_pendente": "#f59e0b",
    "valprod_validando": "#3b82f6",
    "valprod_aprovado": "#22c55e",
    "valprod_rejeitado": "#ef4444",
}

# Tradução dos tipos de link do Jira (inglês → português)
TRADUCAO_LINK_TYPES = {
    # Tipos de link
    "Relates": "Relacionado",
    "Blocks": "Bloqueia",
    "Clones": "Clone",
    "Duplicate": "Duplicado",
    "Parent": "Pai",
    "Subtask": "Subtarefa",
    "Epic Link": "Épico",
    "Polaris work item link": "Implementação",
    "Issue split": "Divisão",
    
    # Direções de link (inward/outward)
    "relates to": "relacionado a",
    "is related to": "relacionado a",
    "blocks": "bloqueia",
    "is blocked by": "bloqueado por",
    "clones": "clona",
    "is cloned by": "clonado por",
    "duplicates": "duplica",
    "is duplicated by": "duplicado por",
    "implements": "implementa",
    "is implemented by": "implementado por",
    "is split by": "dividido por",
    "split to": "dividido para",
    "is parent of": "é pai de",
    "is child of": "é filho de",
    "depends on": "depende de",
    "is depended on by": "dependência de",
}

def traduzir_link(texto: str) -> str:
    """Traduz texto de link do inglês para português."""
    if not texto:
        return texto
    # Busca tradução exata ou parcial (case-insensitive)
    texto_lower = texto.lower().strip()
    for en, pt in TRADUCAO_LINK_TYPES.items():
        if en.lower() == texto_lower:
            return pt
    return texto  # Retorna original se não encontrar

# Etapas do funil PB (ordem do processo)
PB_FUNIL_ETAPAS = [
    ("pb_revisao_produto", "📝 Revisão Produto"),
    ("pb_roteiro", "📋 Em Roteiro"),
    ("pb_ux", "🎨 UX/Design"),
    ("pb_esforco", "⏱️ Aguarda Esforço"),
    ("pb_aguarda_dev", "💻 Aguarda Dev"),
]

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


def card_link_com_popup(ticket_id: str, projeto: str = None, inline: bool = True) -> str:
    """
    Gera HTML de um link para Jira com botão NinaDash que aparece no hover.
    Design: [TICKET-ID] [📊 NinaDash] - ID vai pro Jira, botão vai pro NinaDash.
    
    Args:
        ticket_id: ID do card (ex: PB-797, SD-1234)
        projeto: Projeto do card (PB, SD, QA). Se None, detecta automaticamente.
        inline: Se True, renderiza inline. Se False, bloco.
    
    Returns:
        HTML string com link e botão de ação.
    """
    # Detecta projeto automaticamente se não informado
    if not projeto:
        if ticket_id.startswith("PB-"):
            projeto = "PB"
        elif ticket_id.startswith("QA-"):
            projeto = "QA"
        else:
            projeto = "SD"
    
    # URLs
    url_jira = f"{JIRA_BASE_URL}/browse/{ticket_id}"
    url_dashboard = f"?card={ticket_id}&projeto={projeto}"
    
    # Cor por projeto
    cores = {"PB": "#8b5cf6", "SD": "#3b82f6", "QA": "#22c55e"}
    cor = cores.get(projeto, "#6b7280")
    
    # HTML: ID vai pro Jira, botão NinaDash aparece no hover do wrapper
    html = f'''<span class="card-link-wrapper">
        <a href="{url_jira}" target="_blank" class="card-link-id" style="color: {cor};">{ticket_id}</a>
        <a href="{url_dashboard}" target="_blank" class="card-action-btn card-action-nina">📊 NinaDash</a>
    </span>'''
    
    return html


# CSS global para o popup (deve ser inserido uma vez na página)
CARD_POPUP_CSS = """
<style>
    /* Wrapper do link com botão NinaDash */
    .card-link-wrapper {
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    
    /* ID do ticket (link para Jira) */
    .card-link-id {
        font-weight: 600;
        text-decoration: none;
        padding: 1px 3px;
        border-radius: 3px;
        transition: all 0.2s ease;
    }
    .card-link-id:hover {
        background: rgba(59, 130, 246, 0.1);
        text-decoration: underline;
    }
    
    /* Botão NinaDash - escondido por padrão, aparece no hover do wrapper */
    .card-action-btn {
        display: none;
        align-items: center;
        gap: 3px;
        padding: 3px 8px;
        font-size: 11px;
        font-weight: 500;
        text-decoration: none;
        border-radius: 4px;
        transition: all 0.15s ease;
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        color: #475569;
        white-space: nowrap;
    }
    
    /* Mostrar botão no hover do wrapper */
    .card-link-wrapper:hover .card-action-btn {
        display: inline-flex;
    }
    
    /* Hover NinaDash */
    .card-action-nina:hover {
        background: #AF0C37;
        border-color: #AF0C37;
        color: white;
    }
</style>
"""


def card_link_para_html(ticket_id: str, projeto: str = None) -> str:
    """
    Gera link de card com popup para uso em HTML puro (components.html).
    Inclui CSS e JavaScript inline para funcionar isoladamente.
    
    Args:
        ticket_id: ID do card (ex: PB-797, SD-1234)
        projeto: Projeto do card (PB, SD, QA, VALPROD). Se None, detecta automaticamente.
    
    Returns:
        HTML string com popup completo.
    """
    if not projeto:
        if ticket_id.startswith("PB-"):
            projeto = "PB"
        elif ticket_id.startswith("QA-"):
            projeto = "QA"
        elif ticket_id.startswith("VALPROD-"):
            projeto = "VALPROD"
        elif ticket_id.startswith("DVG-"):
            projeto = "DVG"
        else:
            projeto = "SD"
    
    url_jira = f"{JIRA_BASE_URL}/browse/{ticket_id}"
    # URL do NinaDash
    url_dashboard = f"{NINADASH_URL}?card={ticket_id}&projeto={projeto}"
    
    cores = {"PB": "#8b5cf6", "SD": "#3b82f6", "QA": "#22c55e", "VALPROD": "#f59e0b", "DVG": "#14b8a6"}
    cor = cores.get(projeto, "#6b7280")
    
    # Gera ID único para o popup
    popup_id = f"popup_{ticket_id.replace('-', '_')}"
    
    html = f'''<span class="card-popup-inline" style="position: relative; display: inline-block;">
        <span onclick="document.getElementById('{popup_id}').style.display = document.getElementById('{popup_id}').style.display === 'block' ? 'none' : 'block'" 
              style="color: {cor}; font-weight: 600; cursor: pointer; text-decoration: underline; text-decoration-style: dashed;">
            {ticket_id}
        </span>
        <span id="{popup_id}" style="display: none; position: absolute; bottom: 120%; left: 0; background: white; border: 1px solid #e5e7eb; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); padding: 6px; z-index: 9999; min-width: 150px;">
            <a href="{url_dashboard}" target="_blank" style="display: flex; align-items: center; gap: 8px; padding: 8px 12px; color: #374151; text-decoration: none; border-radius: 6px; font-size: 13px;"
               onmouseover="this.style.background='#AF0C37'; this.style.color='white';"
               onmouseout="this.style.background='transparent'; this.style.color='#374151';">
                📊 NinaDash
            </a>
            <a href="{url_jira}" target="_blank" style="display: flex; align-items: center; gap: 8px; padding: 8px 12px; color: #374151; text-decoration: none; border-radius: 6px; font-size: 13px;"
               onmouseover="this.style.background='#3b82f6'; this.style.color='white';"
               onmouseout="this.style.background='transparent'; this.style.color='#374151';">
                🔗 Jira
            </a>
        </span>
    </span>'''
    
    return html


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
# AUTENTICAÇÃO DE USUÁRIO (usando Cookies para persistência)
# ==============================================================================

# Nome do cookie para autenticação
COOKIE_AUTH_NAME = "ninadash_auth_v2"
COOKIE_EXPIRY_DAYS = 30

# CookieManager para persistência de login entre sessões
@st.cache_resource(show_spinner=False)
def get_cookie_manager():
    """Retorna instância única do CookieManager."""
    return stx.CookieManager(key="ninadash_cookie_manager")


def verificar_login() -> bool:
    """
    Verifica se o usuário está logado.
    Ordem de verificação:
    1. session_state (mais rápido, já autenticado nesta sessão)
    2. Cookie (persistência entre recarregamentos/abas)
    3. Query params (para links compartilhados)
    """
    # 1. Primeiro verifica session_state (mais rápido)
    if st.session_state.get("logged_in", False) and st.session_state.get("user_email"):
        return True
    
    # 2. Verifica cookie para restaurar sessão
    try:
        cookie_manager = get_cookie_manager()
        auth_cookie = cookie_manager.get(COOKIE_AUTH_NAME)
        
        if auth_cookie and validar_email_corporativo(auth_cookie):
            # Restaura sessão a partir do cookie
            st.session_state.logged_in = True
            st.session_state.user_email = auth_cookie
            st.session_state.user_nome = extrair_nome_usuario(auth_cookie)
            return True
    except Exception:
        # Se falhar ao ler cookie, continua para outras verificações
        pass
    
    # 3. Verifica query_params para auto-login (vindo de link compartilhado)
    auto_login_email = st.query_params.get("_auth", None)
    if auto_login_email and validar_email_corporativo(auto_login_email):
        st.session_state.logged_in = True
        st.session_state.user_email = auto_login_email
        st.session_state.user_nome = extrair_nome_usuario(auto_login_email)
        # Salva no cookie para persistir
        try:
            cookie_manager = get_cookie_manager()
            cookie_manager.set(COOKIE_AUTH_NAME, auto_login_email, expires_at=datetime.now() + timedelta(days=COOKIE_EXPIRY_DAYS))
        except Exception:
            pass
        # Limpa o param de auth para não ficar na URL visível
        if "_auth" in st.query_params:
            del st.query_params["_auth"]
        return True
    
    return False


def validar_email_corporativo(email: str) -> bool:
    """Valida se é um email corporativo autorizado."""
    if not email or "@" not in email:
        return False
    return email.lower().strip().endswith("@confirmationcall.com.br")


def extrair_nome_usuario(email: str) -> str:
    """Extrai o nome do usuário do e-mail corporativo (nome.sobrenome@...)."""
    if not email or "@" not in email:
        return "Usuário"
    
    nome_parte = email.split("@")[0]  # nome.sobrenome
    nome_formatado = nome_parte.replace(".", " ").title()  # Nome Sobrenome
    return nome_formatado


def fazer_login(email: str, lembrar: bool = True) -> bool:
    """
    Valida e realiza login do usuário.
    Apenas e-mails com domínio @confirmationcall.com.br são aceitos.
    Salva cookie para persistência entre sessões.
    """
    email_lower = email.lower().strip()
    
    # Valida se é e-mail corporativo
    if validar_email_corporativo(email_lower):
        st.session_state.logged_in = True
        st.session_state.user_email = email_lower
        st.session_state.user_nome = extrair_nome_usuario(email_lower)
        
        # Salva cookie para persistência
        if lembrar:
            try:
                cookie_manager = get_cookie_manager()
                cookie_manager.set(
                    COOKIE_AUTH_NAME, 
                    email_lower, 
                    expires_at=datetime.now() + timedelta(days=COOKIE_EXPIRY_DAYS)
                )
            except Exception:
                pass  # Se falhar ao salvar cookie, login ainda funciona na sessão
        
        return True
    
    return False


def fazer_logout():
    """Remove sessão do usuário e limpa cookie."""
    # Limpa session_state
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.user_nome = None
    
    # Remove cookie de autenticação
    try:
        cookie_manager = get_cookie_manager()
        cookie_manager.delete(COOKIE_AUTH_NAME)
    except Exception:
        pass  # Se falhar ao remover cookie, sessão já está limpa
    
    # Limpa dados carregados para forçar reload após novo login
    if 'dados_carregados' in st.session_state:
        del st.session_state.dados_carregados


def mostrar_tela_loading():
    """Tela de carregamento exibida enquanto verifica autenticação."""
    st.markdown("""
    <style>
    .stApp {
        background: #ffffff !important;
    }
    
    header[data-testid="stHeader"],
    [data-testid="stSidebar"],
    #MainMenu, footer {
        display: none !important;
    }
    
    .block-container {
        max-width: 100% !important;
        padding: 0 !important;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(0.95); }
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        padding: 20px;
        background: #ffffff;
    }
    
    .loading-logo {
        animation: pulse 2s ease-in-out infinite;
        margin-bottom: 30px;
    }
    
    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 4px solid rgba(175, 12, 55, 0.2);
        border-top: 4px solid #AF0C37;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 20px;
    }
    
    .loading-text {
        color: #AF0C37;
        font-size: 1.1em;
        font-weight: 500;
    }
    </style>
    
    <div class="loading-container">
        <div class="loading-logo">
            <svg width="100" height="100" viewBox="0 0 187 187" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M173.709 89.2107C172.209 86.6048 169.414 84.838 166.225 84.838C163.036 84.838 160.241 86.5649 158.741 89.1627H151.683C149.465 58.8237 124.495 35 94.0216 35C63.5489 35 38.5862 58.8237 36.3678 89.1627H29.1759C27.6759 86.5649 24.8734 84.798 21.6682 84.798C18.463 84.798 15.6605 86.5806 14.1605 89.2031C13.4184 90.4899 13 92.001 13 93.6C13 95.1987 13.4184 96.7017 14.1605 97.997C15.6605 100.619 18.463 102.306 21.6682 102.306C24.8734 102.306 27.6838 100.435 29.1759 97.8369H36.3678C38.5862 128.168 63.5489 152 94.0216 152C124.495 152 149.465 128.176 151.675 97.8369H158.686C160.178 100.435 162.996 102.354 166.217 102.354C169.438 102.354 172.256 100.611 173.749 97.9648C174.475 96.6856 174.885 95.2148 174.885 93.6319C174.885 92.049 174.451 90.5222 173.701 89.2188L173.709 89.2107ZM111.145 125.554C107.971 131.518 101.758 135.459 94.5981 135.459C87.4374 135.459 81.2248 131.566 78.0509 125.602C77.1666 123.947 78.3667 122.092 80.2219 122.092H108.982C110.837 122.092 112.029 123.891 111.153 125.554H111.145ZM140.528 94.1277C140.528 103.825 132.76 111.691 123.184 111.691H65.4432C55.8675 111.691 48.0991 103.825 48.0991 94.1277V93.7199C48.0991 84.0223 55.8675 76.1557 65.4432 76.1557H123.184C132.76 76.1557 140.528 84.0223 140.528 93.7199V94.1277Z" fill="#AF0C37"/>
            <path d="M76.5809 105.311C82.9686 105.311 88.1466 100.068 88.1466 93.5996C88.1466 87.1312 82.9686 81.8875 76.5809 81.8875C70.1936 81.8875 65.0156 87.1312 65.0156 93.5996C65.0156 100.068 70.1936 105.311 76.5809 105.311Z" fill="#AF0C37"/>
            <path d="M111.437 105.311C117.824 105.311 123.002 100.068 123.002 93.5996C123.002 87.1312 117.824 81.8875 111.437 81.8875C105.049 81.8875 99.8712 87.1312 99.8712 93.5996C99.8712 100.068 105.049 105.311 111.437 105.311Z" fill="#AF0C37"/>
            </svg>
        </div>
        <div class="loading-spinner"></div>
        <p class="loading-text">Carregando NinaDash...</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Força um rerun após um momento para tentar verificar login novamente
    import time
    time.sleep(0.3)
    st.rerun()


def mostrar_tela_login():
    """Tela de login simplificada e profissional."""
    
    # CSS para tela de login
    st.markdown("""
    <style>
    /* ===== ESCONDER WARNING DO COOKIEMANAGER ===== */
    .stException, [data-testid="stException"] {
        display: none !important;
    }
    
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
            
            # Checkbox para lembrar login
            lembrar = st.checkbox("🔒 Lembrar de mim neste navegador", value=True)
            
            st.markdown(
                '<p style="text-align: center; font-size: 12px; color: #9CA3AF; margin: 8px 0 8px;">'
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
                        if fazer_login(email, lembrar):
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
# CONSULTAS PERSONALIZADAS - SISTEMA DE MÉTRICAS AVANÇADAS
# ==============================================================================

# Tipos de consulta disponíveis
TIPOS_CONSULTA = {
    "cards_pessoa": {
        "nome": "📋 Cards de uma Pessoa",
        "descricao": "Lista de cards filtrados por pessoa (responsável, QA, relator)",
        "filtros": ["pessoa", "papel_pessoa", "status", "periodo"],
        "visualizacao": "lista_cards"
    },
    "metricas_pessoa": {
        "nome": "📊 Métricas de uma Pessoa", 
        "descricao": "KPIs e métricas agregadas para uma pessoa específica",
        "filtros": ["pessoa", "papel_pessoa", "periodo"],
        "visualizacao": "metricas"
    },
    "cards_status": {
        "nome": "🏷️ Cards por Status",
        "descricao": "Cards filtrados por status específico",
        "filtros": ["status", "pessoa", "periodo"],
        "visualizacao": "lista_cards"
    },
    "cards_produto": {
        "nome": "📦 Cards por Produto",
        "descricao": "Cards filtrados por produto",
        "filtros": ["produto", "status", "pessoa", "periodo"],
        "visualizacao": "lista_cards"
    },
    "comparativo_pessoas": {
        "nome": "⚖️ Comparativo entre Pessoas",
        "descricao": "Compare métricas entre várias pessoas",
        "filtros": ["pessoas_multiplas", "papel_pessoa", "periodo"],
        "visualizacao": "comparativo"
    },
    "tendencia_periodo": {
        "nome": "📈 Tendência por Período",
        "descricao": "Evolução de métricas ao longo do tempo",
        "filtros": ["metrica", "pessoa", "periodo_range"],
        "visualizacao": "grafico_linha"
    },
    "bugs_analise": {
        "nome": "🐛 Análise de Bugs",
        "descricao": "Bugs encontrados com filtros avançados",
        "filtros": ["pessoa", "papel_pessoa", "produto", "periodo"],
        "visualizacao": "lista_cards_bugs"
    },
    "fator_k_detalhado": {
        "nome": "🎯 Fator K Detalhado",
        "descricao": "Análise detalhada do Fator K por pessoa/produto",
        "filtros": ["pessoa", "produto", "periodo"],
        "visualizacao": "metricas_fk"
    },
}

# Status disponíveis para filtro
STATUS_FILTRO = {
    "todos": "Todos os status",
    "concluido": "✅ Concluído",
    "em_andamento": "🔄 Em Andamento",
    "em_validacao": "🧪 Em Validação/QA",
    "aguardando_qa": "⏳ Aguardando QA",
    "code_review": "👀 Code Review",
    "impedido": "🚫 Impedido/Bloqueado",
    "reprovado": "❌ Reprovado",
    "backlog": "📋 Backlog",
}

# Papéis de pessoa
PAPEIS_PESSOA = {
    "qualquer": "Qualquer papel",
    "responsavel": "👨‍💻 Responsável/Dev",
    "qa": "🔬 QA Responsável",
    "relator": "📝 Relator/Criador",
}

# Períodos predefinidos
PERIODOS_PREDEFINIDOS = {
    "sprint_atual": "Sprint Atual",
    "ultima_semana": "Última Semana",
    "ultimas_2_semanas": "Últimas 2 Semanas",
    "ultimo_mes": "Último Mês",
    "ultimos_3_meses": "Últimos 3 Meses",
    "todo_periodo": "Todo o Período",
    "personalizado": "📅 Período Personalizado",
}

# ===============================================================================
# CATÁLOGO DE WIDGETS PARA MEU DASHBOARD
# ===============================================================================

CATALOGO_WIDGETS = {
    # === KPIs SIMPLES ===
    "kpi_total_cards": {
        "nome": "📋 Total de Cards",
        "categoria": "📊 KPIs",
        "descricao": "Total de cards no período",
        "tipo": "kpi",
        "filtros": ["pessoa", "status", "periodo"],
    },
    "kpi_story_points": {
        "nome": "⭐ Story Points",
        "categoria": "📊 KPIs",
        "descricao": "Total de Story Points",
        "tipo": "kpi",
        "filtros": ["pessoa", "status", "periodo"],
    },
    "kpi_bugs": {
        "nome": "🐛 Total de Bugs",
        "categoria": "📊 KPIs",
        "descricao": "Quantidade de bugs encontrados",
        "tipo": "kpi",
        "filtros": ["pessoa", "periodo"],
    },
    "kpi_fator_k": {
        "nome": "🎯 Fator K",
        "categoria": "📊 KPIs",
        "descricao": "Razão SP/Bugs (qualidade)",
        "tipo": "kpi",
        "filtros": ["pessoa", "periodo"],
    },
    "kpi_fpy": {
        "nome": "✅ FPY",
        "categoria": "📊 KPIs",
        "descricao": "First Pass Yield - % aprovados de primeira",
        "tipo": "kpi",
        "filtros": ["pessoa", "periodo"],
    },
    "kpi_taxa_conclusao": {
        "nome": "🏁 Taxa de Conclusão",
        "categoria": "📊 KPIs",
        "descricao": "% de cards concluídos",
        "tipo": "kpi",
        "filtros": ["pessoa", "periodo"],
    },
    
    # === GRÁFICOS ===
    "grafico_status": {
        "nome": "📊 Gráfico por Status",
        "categoria": "📈 Gráficos",
        "descricao": "Distribuição de cards por status",
        "tipo": "grafico_barra",
        "filtros": ["pessoa", "periodo"],
    },
    "grafico_produto": {
        "nome": "📦 Gráfico por Produto",
        "categoria": "📈 Gráficos",
        "descricao": "Distribuição de cards por produto",
        "tipo": "grafico_barra",
        "filtros": ["pessoa", "periodo"],
    },
    "grafico_responsavel": {
        "nome": "👤 Gráfico por Responsável",
        "categoria": "📈 Gráficos",
        "descricao": "Cards por responsável",
        "tipo": "grafico_barra",
        "filtros": ["status", "periodo"],
    },
    "grafico_bugs_dev": {
        "nome": "🐛 Bugs por Dev",
        "categoria": "📈 Gráficos",
        "descricao": "Bugs encontrados por desenvolvedor",
        "tipo": "grafico_barra",
        "filtros": ["periodo"],
    },
    
    # === TABELAS ===
    "tabela_ranking_devs": {
        "nome": "🏆 Ranking Devs",
        "categoria": "📋 Tabelas",
        "descricao": "Ranking de desenvolvedores por Fator K",
        "tipo": "tabela",
        "filtros": ["periodo"],
    },
    "tabela_cards_recentes": {
        "nome": "🕐 Cards Recentes",
        "categoria": "📋 Tabelas",
        "descricao": "Últimos cards atualizados",
        "tipo": "tabela",
        "filtros": ["pessoa", "status"],
    },
    "tabela_aging": {
        "nome": "⏰ Aging",
        "categoria": "📋 Tabelas",
        "descricao": "Cards há muito tempo parados",
        "tipo": "tabela",
        "filtros": ["status"],
    },
    
    # === LISTAS ===
    "lista_cards_pessoa": {
        "nome": "📋 Cards de uma Pessoa",
        "categoria": "📝 Listas",
        "descricao": "Lista de cards de uma pessoa específica",
        "tipo": "lista",
        "filtros": ["pessoa", "papel_pessoa", "status", "periodo"],
    },
    "lista_bugs": {
        "nome": "🐛 Lista de Bugs",
        "categoria": "📝 Listas",
        "descricao": "Lista de bugs encontrados",
        "tipo": "lista",
        "filtros": ["pessoa", "periodo"],
    },
}

# Nome do cookie para consultas salvas
COOKIE_CONSULTAS_NAME = "ninadash_consultas_salvas"
COOKIE_DASHBOARD_NAME = "ninadash_meu_dashboard"


def inicializar_meu_dashboard():
    """Inicializa o sistema de Meu Dashboard."""
    if 'meu_dashboard_widgets' not in st.session_state:
        # Tenta carregar do cookie
        try:
            cookie_manager = get_cookie_manager()
            dashboard_cookie = cookie_manager.get(COOKIE_DASHBOARD_NAME)
            if dashboard_cookie:
                import json
                st.session_state.meu_dashboard_widgets = json.loads(dashboard_cookie)
            else:
                st.session_state.meu_dashboard_widgets = []
        except:
            st.session_state.meu_dashboard_widgets = []
    
    if 'modo_meu_dashboard' not in st.session_state:
        st.session_state.modo_meu_dashboard = False


def _salvar_dashboard_cookie():
    """Salva o dashboard no cookie para persistência."""
    try:
        import json
        cookie_manager = get_cookie_manager()
        
        # Serializa os widgets (remove datetime objects)
        widgets_serializaveis = []
        for widget in st.session_state.meu_dashboard_widgets:
            widget_copia = widget.copy()
            filtros_copia = widget_copia.get('filtros', {}).copy()
            for key in ['data_inicio', 'data_fim']:
                if key in filtros_copia:
                    if isinstance(filtros_copia[key], datetime):
                        filtros_copia[key] = filtros_copia[key].isoformat()
            widget_copia['filtros'] = filtros_copia
            widgets_serializaveis.append(widget_copia)
        
        cookie_manager.set(
            COOKIE_DASHBOARD_NAME,
            json.dumps(widgets_serializaveis),
            expires_at=datetime.now() + timedelta(days=365)
        )
    except:
        pass


def adicionar_widget(tipo_widget: str, filtros: Dict):
    """Adiciona um widget ao dashboard."""
    inicializar_meu_dashboard()
    
    widget_info = CATALOGO_WIDGETS.get(tipo_widget, {})
    novo_widget = {
        "id": f"widget_{datetime.now().timestamp()}",
        "tipo": tipo_widget,
        "nome": widget_info.get('nome', tipo_widget),
        "filtros": filtros.copy(),
        "criado_em": datetime.now().isoformat()
    }
    st.session_state.meu_dashboard_widgets.append(novo_widget)
    _salvar_dashboard_cookie()


def remover_widget(widget_id: str):
    """Remove um widget do dashboard."""
    st.session_state.meu_dashboard_widgets = [
        w for w in st.session_state.meu_dashboard_widgets if w['id'] != widget_id
    ]
    _salvar_dashboard_cookie()


def mover_widget_cima(widget_id: str):
    """Move um widget para cima na lista."""
    widgets = st.session_state.meu_dashboard_widgets
    for i, w in enumerate(widgets):
        if w['id'] == widget_id and i > 0:
            widgets[i], widgets[i-1] = widgets[i-1], widgets[i]
            break
    _salvar_dashboard_cookie()


def mover_widget_baixo(widget_id: str):
    """Move um widget para baixo na lista."""
    widgets = st.session_state.meu_dashboard_widgets
    for i, w in enumerate(widgets):
        if w['id'] == widget_id and i < len(widgets) - 1:
            widgets[i], widgets[i+1] = widgets[i+1], widgets[i]
            break
    _salvar_dashboard_cookie()


def renderizar_widget(widget: Dict, df: pd.DataFrame, idx: int, total: int):
    """Renderiza um widget individual com controles."""
    
    tipo = widget['tipo']
    filtros = widget.get('filtros', {})
    widget_info = CATALOGO_WIDGETS.get(tipo, {})
    
    # Aplica filtros ao DataFrame
    df_filtrado = aplicar_filtros_widget(df, filtros)
    
    # Container do widget com borda
    with st.container():
        # Header do widget com controles
        col_titulo, col_controles = st.columns([4, 1])
        
        with col_titulo:
            st.markdown(f"#### {widget_info.get('nome', tipo)}")
            # Mostra filtros ativos
            filtros_texto = []
            if filtros.get('pessoa') and filtros['pessoa'] != 'Todos':
                filtros_texto.append(f"👤 {filtros['pessoa']}")
            if filtros.get('status') and filtros['status'] != 'todos':
                filtros_texto.append(f"🏷️ {STATUS_FILTRO.get(filtros['status'], filtros['status'])}")
            if filtros.get('periodo'):
                filtros_texto.append(f"📅 {PERIODOS_PREDEFINIDOS.get(filtros['periodo'], filtros['periodo'])}")
            if filtros_texto:
                st.caption(" | ".join(filtros_texto))
        
        with col_controles:
            col_up, col_down, col_del = st.columns(3)
            with col_up:
                if idx > 0:
                    if st.button("⬆️", key=f"up_{widget['id']}", help="Mover para cima"):
                        mover_widget_cima(widget['id'])
                        st.rerun()
            with col_down:
                if idx < total - 1:
                    if st.button("⬇️", key=f"down_{widget['id']}", help="Mover para baixo"):
                        mover_widget_baixo(widget['id'])
                        st.rerun()
            with col_del:
                if st.button("🗑️", key=f"del_{widget['id']}", help="Remover"):
                    remover_widget(widget['id'])
                    st.rerun()
        
        # Conteúdo do widget
        tipo_viz = widget_info.get('tipo', 'kpi')
        
        if df_filtrado.empty:
            st.info("Nenhum dado para os filtros selecionados")
        elif tipo_viz == 'kpi':
            renderizar_kpi_widget(tipo, df_filtrado)
        elif tipo_viz == 'grafico_barra':
            renderizar_grafico_widget(tipo, df_filtrado)
        elif tipo_viz == 'tabela':
            renderizar_tabela_widget(tipo, df_filtrado)
        elif tipo_viz == 'lista':
            renderizar_lista_widget(tipo, df_filtrado, filtros)
        
        st.markdown("---")


def aplicar_filtros_widget(df: pd.DataFrame, filtros: Dict) -> pd.DataFrame:
    """Aplica filtros ao DataFrame para um widget."""
    df_filtrado = df.copy()
    
    # Filtro por período
    if filtros.get('periodo'):
        data_inicio, data_fim = calcular_periodo_datas(
            filtros['periodo'],
            filtros.get('data_inicio'),
            filtros.get('data_fim')
        )
        if 'data_criacao' in df_filtrado.columns:
            df_filtrado['data_criacao_dt'] = pd.to_datetime(df_filtrado['data_criacao'], errors='coerce')
            df_filtrado['data_criacao_dt'] = df_filtrado['data_criacao_dt'].dt.tz_localize(None)
            df_filtrado = df_filtrado[
                (df_filtrado['data_criacao_dt'] >= data_inicio) & 
                (df_filtrado['data_criacao_dt'] <= data_fim)
            ]
    
    # Filtro por pessoa
    if filtros.get('pessoa') and filtros['pessoa'] != 'Todos':
        pessoa = filtros['pessoa']
        papel = filtros.get('papel_pessoa', 'qualquer')
        
        if papel == 'responsavel':
            df_filtrado = df_filtrado[df_filtrado['responsavel'].str.contains(pessoa, case=False, na=False)]
        elif papel == 'qa':
            df_filtrado = df_filtrado[df_filtrado['qa_responsavel'].str.contains(pessoa, case=False, na=False)]
        elif papel == 'relator':
            df_filtrado = df_filtrado[df_filtrado['relator'].str.contains(pessoa, case=False, na=False)]
        else:
            df_filtrado = df_filtrado[
                df_filtrado['responsavel'].str.contains(pessoa, case=False, na=False) |
                df_filtrado['qa_responsavel'].str.contains(pessoa, case=False, na=False) |
                df_filtrado['relator'].str.contains(pessoa, case=False, na=False)
            ]
    
    # Filtro por status
    if filtros.get('status') and filtros['status'] != 'todos':
        status_map = {
            "concluido": ["done"],
            "em_andamento": ["development"],
            "em_validacao": ["testing"],
            "aguardando_qa": ["waiting_qa"],
            "code_review": ["code_review"],
            "impedido": ["blocked"],
            "reprovado": ["rejected"],
            "backlog": ["backlog"],
        }
        categorias = status_map.get(filtros['status'], [])
        if categorias:
            df_filtrado = df_filtrado[df_filtrado['status_categoria'].isin(categorias)]
    
    return df_filtrado


def renderizar_kpi_widget(tipo: str, df: pd.DataFrame):
    """Renderiza um widget KPI."""
    
    if tipo == "kpi_total_cards":
        valor = len(df)
        st.metric("Total de Cards", f"{valor:,}")
    
    elif tipo == "kpi_story_points":
        valor = int(df['story_points'].sum())
        st.metric("Story Points", f"{valor:,}")
    
    elif tipo == "kpi_bugs":
        valor = int(df['bugs_encontrados'].sum())
        st.metric("Bugs Encontrados", f"{valor:,}")
    
    elif tipo == "kpi_fator_k":
        sp = df['story_points'].sum()
        bugs = df['bugs_encontrados'].sum()
        fk = sp / (bugs + 1)
        cor = "normal" if fk >= 3 else "inverse"
        st.metric("Fator K", f"{fk:.2f}", help="SP / (Bugs + 1)")
    
    elif tipo == "kpi_fpy":
        total = len(df)
        sem_bugs = len(df[df['bugs_encontrados'] == 0])
        fpy = (sem_bugs / total * 100) if total > 0 else 0
        st.metric("FPY", f"{fpy:.1f}%", help="Cards sem bugs")
    
    elif tipo == "kpi_taxa_conclusao":
        total = len(df)
        concluidos = len(df[df['status_categoria'] == 'done'])
        taxa = (concluidos / total * 100) if total > 0 else 0
        st.metric("Taxa Conclusão", f"{taxa:.1f}%")


def renderizar_grafico_widget(tipo: str, df: pd.DataFrame):
    """Renderiza um widget de gráfico."""
    
    if tipo == "grafico_status":
        contagem = df['status'].value_counts().head(10)
        fig = px.bar(x=contagem.index, y=contagem.values, labels={'x': 'Status', 'y': 'Quantidade'})
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    elif tipo == "grafico_produto":
        contagem = df['produto'].value_counts().head(10)
        fig = px.bar(x=contagem.index, y=contagem.values, labels={'x': 'Produto', 'y': 'Quantidade'})
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    elif tipo == "grafico_responsavel":
        contagem = df['responsavel'].value_counts().head(10)
        fig = px.bar(x=contagem.index, y=contagem.values, labels={'x': 'Responsável', 'y': 'Quantidade'})
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    elif tipo == "grafico_bugs_dev":
        bugs_dev = df.groupby('responsavel')['bugs_encontrados'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(x=bugs_dev.index, y=bugs_dev.values, labels={'x': 'Desenvolvedor', 'y': 'Bugs'})
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)


def renderizar_tabela_widget(tipo: str, df: pd.DataFrame):
    """Renderiza um widget de tabela."""
    
    if tipo == "tabela_ranking_devs":
        ranking = df.groupby('responsavel').agg({
            'story_points': 'sum',
            'bugs_encontrados': 'sum',
            'key': 'count'
        }).reset_index()
        ranking.columns = ['Desenvolvedor', 'SP', 'Bugs', 'Cards']
        ranking['FK'] = (ranking['SP'] / (ranking['Bugs'] + 1)).round(2)
        ranking = ranking.sort_values('FK', ascending=False).head(10)
        st.dataframe(ranking, use_container_width=True, hide_index=True, height=300)
    
    elif tipo == "tabela_cards_recentes":
        colunas = ['key', 'resumo', 'responsavel', 'status', 'story_points']
        colunas_existentes = [c for c in colunas if c in df.columns]
        df_recentes = df[colunas_existentes].head(10)
        st.dataframe(df_recentes, use_container_width=True, hide_index=True, height=300)
    
    elif tipo == "tabela_aging":
        # Cards parados há mais de 7 dias
        if 'data_atualizacao' in df.columns:
            df['data_atualizacao_dt'] = pd.to_datetime(df['data_atualizacao'], errors='coerce')
            df['dias_parado'] = (datetime.now() - df['data_atualizacao_dt'].dt.tz_localize(None)).dt.days
            aging = df[df['dias_parado'] > 7][['key', 'resumo', 'status', 'dias_parado']].sort_values('dias_parado', ascending=False).head(10)
            st.dataframe(aging, use_container_width=True, hide_index=True, height=300)
        else:
            st.info("Dados de atualização não disponíveis")


def renderizar_lista_widget(tipo: str, df: pd.DataFrame, filtros: Dict):
    """Renderiza um widget de lista de cards."""
    
    if tipo in ["lista_cards_pessoa", "lista_bugs"]:
        for _, row in df.head(15).iterrows():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"**[{row['key']}]({link_jira(row['key'])})**")
            with col2:
                titulo = str(row.get('resumo', ''))[:60]
                st.markdown(f"{titulo}")
                st.caption(f"👤 {row.get('responsavel', 'N/A')} | 📌 {row.get('status', 'N/A')}")
        
        if len(df) > 15:
            st.caption(f"... e mais {len(df) - 15} cards")


def inicializar_consultas_personalizadas():
    """Inicializa o sistema de consultas personalizadas, carregando do cookie se existir."""
    if 'consultas_salvas' not in st.session_state:
        # Tenta carregar do cookie
        try:
            cookie_manager = get_cookie_manager()
            consultas_cookie = cookie_manager.get(COOKIE_CONSULTAS_NAME)
            if consultas_cookie:
                import json
                st.session_state.consultas_salvas = json.loads(consultas_cookie)
            else:
                st.session_state.consultas_salvas = {}
        except:
            st.session_state.consultas_salvas = {}
    
    if 'modo_consulta_personalizada' not in st.session_state:
        st.session_state.modo_consulta_personalizada = False
    if 'consulta_atual' not in st.session_state:
        st.session_state.consulta_atual = None
    if 'consulta_executar' not in st.session_state:
        st.session_state.consulta_executar = None


def entrar_modo_consulta():
    """Ativa o modo de consulta personalizada."""
    st.session_state.modo_consulta_personalizada = True


def sair_modo_consulta():
    """Desativa o modo de consulta personalizada."""
    st.session_state.modo_consulta_personalizada = False
    st.session_state.consulta_atual = None


def _salvar_consultas_cookie():
    """Salva as consultas no cookie para persistência."""
    try:
        import json
        cookie_manager = get_cookie_manager()
        # Converte filtros datetime para string antes de serializar
        consultas_serializaveis = {}
        for nome, consulta in st.session_state.consultas_salvas.items():
            consulta_copia = consulta.copy()
            filtros_copia = consulta_copia.get('filtros', {}).copy()
            # Remove datetime objects que não são serializáveis
            for key in ['data_inicio', 'data_fim']:
                if key in filtros_copia and isinstance(filtros_copia[key], datetime):
                    filtros_copia[key] = filtros_copia[key].isoformat()
            consulta_copia['filtros'] = filtros_copia
            consultas_serializaveis[nome] = consulta_copia
        
        cookie_manager.set(
            COOKIE_CONSULTAS_NAME,
            json.dumps(consultas_serializaveis),
            expires_at=datetime.now() + timedelta(days=365)  # 1 ano
        )
    except Exception as e:
        pass  # Silently fail cookie save


def salvar_consulta(nome: str, tipo: str, filtros: Dict):
    """Salva uma consulta personalizada no session_state e no cookie."""
    inicializar_consultas_personalizadas()
    st.session_state.consultas_salvas[nome] = {
        "nome": nome,
        "tipo": tipo,
        "filtros": filtros.copy(),
        "criado_em": datetime.now().isoformat()
    }
    _salvar_consultas_cookie()


def listar_consultas_salvas() -> Dict:
    """Lista todas as consultas salvas."""
    inicializar_consultas_personalizadas()
    return st.session_state.consultas_salvas


def excluir_consulta(nome: str):
    """Exclui uma consulta salva."""
    if nome in st.session_state.consultas_salvas:
        del st.session_state.consultas_salvas[nome]
        _salvar_consultas_cookie()


def calcular_periodo_datas(periodo: str, data_inicio_custom: datetime = None, data_fim_custom: datetime = None) -> Tuple[datetime, datetime]:
    """Calcula as datas de início e fim baseado no período selecionado."""
    hoje = datetime.now()
    
    if periodo == "sprint_atual":
        # Aproxima para 2 semanas
        return hoje - timedelta(days=14), hoje
    elif periodo == "ultima_semana":
        return hoje - timedelta(days=7), hoje
    elif periodo == "ultimas_2_semanas":
        return hoje - timedelta(days=14), hoje
    elif periodo == "ultimo_mes":
        return hoje - timedelta(days=30), hoje
    elif periodo == "ultimos_3_meses":
        return hoje - timedelta(days=90), hoje
    elif periodo == "todo_periodo":
        return hoje - timedelta(days=365*5), hoje  # 5 anos
    elif periodo == "personalizado" and data_inicio_custom and data_fim_custom:
        return data_inicio_custom, data_fim_custom
    else:
        return hoje - timedelta(days=30), hoje


def filtrar_df_por_consulta(df: pd.DataFrame, tipo: str, filtros: Dict) -> pd.DataFrame:
    """Filtra o DataFrame baseado nos filtros da consulta."""
    df_filtrado = df.copy()
    
    # Filtro por período
    if 'periodo' in filtros and filtros['periodo']:
        data_inicio, data_fim = calcular_periodo_datas(
            filtros['periodo'],
            filtros.get('data_inicio'),
            filtros.get('data_fim')
        )
        if 'data_criacao' in df_filtrado.columns:
            df_filtrado['data_criacao_dt'] = pd.to_datetime(df_filtrado['data_criacao'], errors='coerce')
            # Remove timezone info for comparison
            df_filtrado['data_criacao_dt'] = df_filtrado['data_criacao_dt'].dt.tz_localize(None)
            df_filtrado = df_filtrado[
                (df_filtrado['data_criacao_dt'] >= data_inicio) & 
                (df_filtrado['data_criacao_dt'] <= data_fim)
            ]
    
    # Filtro por pessoa
    if 'pessoa' in filtros and filtros['pessoa'] and filtros['pessoa'] != "Todos":
        papel = filtros.get('papel_pessoa', 'qualquer')
        pessoa = filtros['pessoa']
        
        if papel == 'responsavel':
            df_filtrado = df_filtrado[df_filtrado['responsavel'].str.contains(pessoa, case=False, na=False)]
        elif papel == 'qa':
            df_filtrado = df_filtrado[df_filtrado['qa_responsavel'].str.contains(pessoa, case=False, na=False)]
        elif papel == 'relator':
            df_filtrado = df_filtrado[df_filtrado['relator'].str.contains(pessoa, case=False, na=False)]
        else:  # qualquer
            df_filtrado = df_filtrado[
                df_filtrado['responsavel'].str.contains(pessoa, case=False, na=False) |
                df_filtrado['qa_responsavel'].str.contains(pessoa, case=False, na=False) |
                df_filtrado['relator'].str.contains(pessoa, case=False, na=False)
            ]
    
    # Filtro por status
    if 'status' in filtros and filtros['status'] and filtros['status'] != "todos":
        status_map = {
            "concluido": ["done"],
            "em_andamento": ["development"],
            "em_validacao": ["testing"],
            "aguardando_qa": ["waiting_qa"],
            "code_review": ["code_review"],
            "impedido": ["blocked"],
            "reprovado": ["rejected"],
            "backlog": ["backlog"],
        }
        categorias = status_map.get(filtros['status'], [])
        if categorias:
            df_filtrado = df_filtrado[df_filtrado['status_categoria'].isin(categorias)]
    
    # Filtro por produto
    if 'produto' in filtros and filtros['produto'] and filtros['produto'] != "Todos":
        df_filtrado = df_filtrado[df_filtrado['produto'] == filtros['produto']]
    
    return df_filtrado


def renderizar_resultado_consulta(df_filtrado: pd.DataFrame, tipo: str, filtros: Dict):
    """Renderiza o resultado da consulta."""
    
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum resultado encontrado para os filtros selecionados.")
        return
    
    consulta = TIPOS_CONSULTA.get(tipo, {})
    visualizacao = consulta.get('visualizacao', 'lista_cards')
    
    # === VISUALIZAÇÃO: LISTA DE CARDS ===
    if visualizacao in ['lista_cards', 'lista_cards_bugs']:
        st.markdown(f"### 📋 {len(df_filtrado)} Cards Encontrados")
        
        # Métricas resumo
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Cards", len(df_filtrado))
        with col2:
            sp_total = int(df_filtrado['story_points'].sum())
            st.metric("Story Points", sp_total)
        with col3:
            bugs_total = int(df_filtrado['bugs_encontrados'].sum())
            st.metric("Bugs", bugs_total)
        with col4:
            concluidos = len(df_filtrado[df_filtrado['status_categoria'] == 'done'])
            st.metric("Concluídos", concluidos)
        
        st.markdown("---")
        
        # Lista de cards
        for _, row in df_filtrado.head(50).iterrows():
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    st.markdown(f"**[{row['key']}]({link_jira(row['key'])})**")
                with col2:
                    titulo = str(row.get('resumo', ''))[:80]
                    st.markdown(f"{titulo}")
                    st.caption(f"📌 {row.get('status', 'N/A')} | 👤 {row.get('responsavel', 'N/A')}")
                with col3:
                    sp = row.get('story_points', 0)
                    bugs = row.get('bugs_encontrados', 0)
                    st.markdown(f"**{sp} SP** | 🐛 {bugs}")
            st.markdown("---")
        
        if len(df_filtrado) > 50:
            st.info(f"Mostrando 50 de {len(df_filtrado)} cards. Refine os filtros para ver menos resultados.")
    
    # === VISUALIZAÇÃO: MÉTRICAS ===
    elif visualizacao == 'metricas':
        st.markdown("### 📊 Métricas Calculadas")
        
        # KPIs principais
        col1, col2, col3, col4 = st.columns(4)
        
        total_cards = len(df_filtrado)
        sp_total = int(df_filtrado['story_points'].sum())
        bugs_total = int(df_filtrado['bugs_encontrados'].sum())
        concluidos = len(df_filtrado[df_filtrado['status_categoria'] == 'done'])
        
        with col1:
            st.metric("Total Cards", total_cards)
        with col2:
            st.metric("Story Points", sp_total)
        with col3:
            st.metric("Bugs Encontrados", bugs_total)
        with col4:
            taxa_conclusao = (concluidos / total_cards * 100) if total_cards > 0 else 0
            st.metric("Taxa Conclusão", f"{taxa_conclusao:.1f}%")
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Fator K
            fk = sp_total / (bugs_total + 1)
            st.metric("Fator K", f"{fk:.2f}", help="SP / (Bugs + 1)")
        
        with col2:
            # FPY
            sem_bugs = len(df_filtrado[df_filtrado['bugs_encontrados'] == 0])
            fpy = (sem_bugs / total_cards * 100) if total_cards > 0 else 0
            st.metric("FPY", f"{fpy:.1f}%", help="Cards sem bugs / Total")
        
        with col3:
            # Média SP
            media_sp = df_filtrado['story_points'].mean() if total_cards > 0 else 0
            st.metric("Média SP/Card", f"{media_sp:.1f}")
        
        # Gráfico de status
        st.markdown("---")
        st.markdown("#### 📈 Distribuição por Status")
        status_counts = df_filtrado['status'].value_counts()
        fig = px.bar(x=status_counts.index, y=status_counts.values, labels={'x': 'Status', 'y': 'Quantidade'})
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # === VISUALIZAÇÃO: COMPARATIVO ===
    elif visualizacao == 'comparativo':
        st.markdown("### ⚖️ Comparativo")
        
        pessoas = filtros.get('pessoas_multiplas', [])
        if not pessoas:
            st.warning("Selecione pessoas para comparar")
            return
        
        dados_comparativo = []
        for pessoa in pessoas:
            df_pessoa = df_filtrado[
                df_filtrado['responsavel'].str.contains(pessoa, case=False, na=False) |
                df_filtrado['qa_responsavel'].str.contains(pessoa, case=False, na=False)
            ]
            dados_comparativo.append({
                'Pessoa': pessoa,
                'Cards': len(df_pessoa),
                'SP': int(df_pessoa['story_points'].sum()),
                'Bugs': int(df_pessoa['bugs_encontrados'].sum()),
                'FK': round(df_pessoa['story_points'].sum() / (df_pessoa['bugs_encontrados'].sum() + 1), 2)
            })
        
        df_comp = pd.DataFrame(dados_comparativo)
        st.dataframe(df_comp, use_container_width=True, hide_index=True)
        
        # Gráfico comparativo
        fig = px.bar(df_comp, x='Pessoa', y=['Cards', 'SP', 'Bugs'], barmode='group')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # === VISUALIZAÇÃO: FATOR K DETALHADO ===
    elif visualizacao == 'metricas_fk':
        st.markdown("### 🎯 Análise Fator K Detalhado")
        
        # Por desenvolvedor
        fk_dev = df_filtrado.groupby('responsavel').agg({
            'story_points': 'sum',
            'bugs_encontrados': 'sum',
            'key': 'count'
        }).reset_index()
        fk_dev.columns = ['Desenvolvedor', 'SP', 'Bugs', 'Cards']
        fk_dev['Fator K'] = fk_dev['SP'] / (fk_dev['Bugs'] + 1)
        fk_dev = fk_dev.sort_values('Fator K', ascending=False)
        
        st.dataframe(fk_dev.head(15), use_container_width=True, hide_index=True)
        
        # Gráfico
        fig = px.bar(fk_dev.head(10), x='Desenvolvedor', y='Fator K', color='Fator K',
                    color_continuous_scale='RdYlGn')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)


def tela_consulta_personalizada(df_todos: pd.DataFrame):
    """Renderiza a tela de Meu Dashboard - Dashboard Builder personalizado."""
    
    inicializar_meu_dashboard()
    
    # ===============================================
    # HEADER
    # ===============================================
    st.markdown("""
    <div style="text-align: center; padding: 10px 0 20px;">
        <h1 style="color: #AF0C37; margin: 0; font-size: 2em;">🎨 Meu Dashboard</h1>
        <p style="color: #666; font-size: 1em; margin-top: 5px;">Monte seu dashboard personalizado</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ===============================================
    # DEBUG: Mostra dados carregados
    # ===============================================
    st.info(f"📊 Dados carregados: {len(df_todos)} cards de {df_todos['projeto'].nunique() if 'projeto' in df_todos.columns else 0} projetos")
    
    # ===============================================
    # SEÇÃO 1: CONSTRUTOR DE WIDGET (TOPO)
    # ===============================================
    st.markdown("### ➕ Adicionar Widget")
    
    # Coleta lista de pessoas ANTES de renderizar os filtros
    pessoas_lista = []
    if 'responsavel' in df_todos.columns:
        responsaveis = df_todos['responsavel'].dropna().unique().tolist()
        pessoas_lista.extend([p for p in responsaveis if p and p != 'Não atribuído' and len(str(p)) > 2])
    if 'qa_responsavel' in df_todos.columns:
        qas = df_todos['qa_responsavel'].dropna().unique().tolist()
        pessoas_lista.extend([p for p in qas if p and p not in pessoas_lista and len(str(p)) > 2])
    pessoas_lista = sorted(list(set(pessoas_lista)))
    
    # DEBUG: Mostra quantas pessoas encontrou
    st.caption(f"👥 {len(pessoas_lista)} pessoas encontradas nos dados")
    
    # Linha 1: Tipo de widget
    col_tipo = st.columns([1])[0]
    with col_tipo:
        # Lista todos os widgets disponíveis
        opcoes_widgets = list(CATALOGO_WIDGETS.keys())
        
        tipo_widget = st.selectbox(
            "📊 Selecione o tipo de visualização",
            options=opcoes_widgets,
            format_func=lambda x: f"{CATALOGO_WIDGETS[x]['nome']} - {CATALOGO_WIDGETS[x]['descricao']}",
            key="select_tipo_widget_novo"
        )
    
    # Linha 2: Filtros em colunas
    st.markdown("**Filtros (opcional):**")
    col_pessoa, col_status, col_periodo = st.columns(3)
    
    with col_pessoa:
        pessoa_selecionada = st.selectbox(
            "👤 Pessoa",
            options=["Todos"] + pessoas_lista,
            key="filtro_pessoa_novo",
            help="Filtra por responsável, QA ou relator"
        )
    
    with col_status:
        status_selecionado = st.selectbox(
            "🏷️ Status",
            options=list(STATUS_FILTRO.keys()),
            format_func=lambda x: STATUS_FILTRO[x],
            key="filtro_status_novo"
        )
    
    with col_periodo:
        periodo_selecionado = st.selectbox(
            "📅 Período",
            options=list(PERIODOS_PREDEFINIDOS.keys()),
            format_func=lambda x: PERIODOS_PREDEFINIDOS[x],
            key="filtro_periodo_novo",
            index=5  # Todo o Período
        )
    
    # Botão de adicionar
    if st.button("➕ ADICIONAR WIDGET AO DASHBOARD", type="primary", use_container_width=True, key="btn_add_widget_novo"):
        filtros_novos = {
            "pessoa": pessoa_selecionada,
            "status": status_selecionado,
            "periodo": periodo_selecionado
        }
        adicionar_widget(tipo_widget, filtros_novos)
        st.success(f"✅ Widget '{CATALOGO_WIDGETS[tipo_widget]['nome']}' adicionado!")
        st.rerun()
    
    st.markdown("---")
    
    # ===============================================
    # SEÇÃO 2: WIDGETS ADICIONADOS (ABAIXO)
    # ===============================================
    widgets = st.session_state.get('meu_dashboard_widgets', [])
    
    if not widgets:
        # Estado vazio
        st.markdown("""
        <div style="text-align: center; padding: 40px 20px; background: #f8f9fa; 
                    border-radius: 10px; border: 2px dashed #dee2e6;">
            <h3 style="color: #6c757d; margin: 0;">📭 Seu dashboard está vazio</h3>
            <p style="color: #adb5bd; margin-top: 10px;">Selecione um tipo de widget acima e clique em "Adicionar"</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 💡 Ou comece com um template pronto:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Visão Executiva", use_container_width=True, key="tpl_exec"):
                adicionar_widget("kpi_total_cards", {"periodo": "todo_periodo"})
                adicionar_widget("kpi_story_points", {"periodo": "todo_periodo"})
                adicionar_widget("kpi_fator_k", {"periodo": "todo_periodo"})
                adicionar_widget("grafico_status", {"periodo": "todo_periodo"})
                st.rerun()
        
        with col2:
            if st.button("👨‍💻 Foco DEV", use_container_width=True, key="tpl_dev"):
                adicionar_widget("tabela_ranking_devs", {"periodo": "todo_periodo"})
                adicionar_widget("grafico_bugs_dev", {"periodo": "todo_periodo"})
                st.rerun()
        
        with col3:
            if st.button("🔬 Foco QA", use_container_width=True, key="tpl_qa"):
                adicionar_widget("kpi_bugs", {"periodo": "todo_periodo"})
                adicionar_widget("tabela_aging", {"status": "todos"})
                st.rerun()
    
    else:
        # Mostra contagem e botão limpar
        col_info, col_limpar = st.columns([4, 1])
        with col_info:
            st.markdown(f"### 📊 Seus Widgets ({len(widgets)})")
        with col_limpar:
            if st.button("🗑️ Limpar Tudo", key="btn_limpar"):
                st.session_state.meu_dashboard_widgets = []
                _salvar_dashboard_cookie()
                st.rerun()
        
        # Renderiza cada widget
        for idx, widget in enumerate(widgets):
            with st.container():
                # Header do widget
                col_titulo, col_acoes = st.columns([5, 1])
                
                widget_info = CATALOGO_WIDGETS.get(widget.get('tipo', ''), {})
                
                with col_titulo:
                    st.markdown(f"#### {widget_info.get('nome', widget.get('tipo', 'Widget'))}")
                    
                    # Mostra filtros aplicados
                    filtros = widget.get('filtros', {})
                    filtros_txt = []
                    if filtros.get('pessoa') and filtros['pessoa'] != 'Todos':
                        filtros_txt.append(f"👤 {filtros['pessoa']}")
                    if filtros.get('status') and filtros['status'] != 'todos':
                        filtros_txt.append(f"🏷️ {STATUS_FILTRO.get(filtros['status'], '')}")
                    if filtros.get('periodo'):
                        filtros_txt.append(f"📅 {PERIODOS_PREDEFINIDOS.get(filtros['periodo'], '')}")
                    if filtros_txt:
                        st.caption(" | ".join(filtros_txt))
                
                with col_acoes:
                    col_up, col_down, col_del = st.columns(3)
                    with col_up:
                        if idx > 0 and st.button("⬆️", key=f"up_{idx}"):
                            mover_widget_cima(widget['id'])
                            st.rerun()
                    with col_down:
                        if idx < len(widgets) - 1 and st.button("⬇️", key=f"down_{idx}"):
                            mover_widget_baixo(widget['id'])
                            st.rerun()
                    with col_del:
                        if st.button("🗑️", key=f"del_{idx}"):
                            remover_widget(widget['id'])
                            st.rerun()
                
                # Renderiza conteúdo do widget
                filtros = widget.get('filtros', {})
                df_widget = aplicar_filtros_widget(df_todos.copy(), filtros)
                
                if df_widget.empty:
                    st.warning("Nenhum dado encontrado para os filtros aplicados")
                else:
                    tipo = widget.get('tipo', '')
                    tipo_viz = widget_info.get('tipo', 'kpi')
                    
                    if tipo_viz == 'kpi':
                        renderizar_kpi_widget(tipo, df_widget)
                    elif tipo_viz == 'grafico_barra':
                        renderizar_grafico_widget(tipo, df_widget)
                    elif tipo_viz == 'tabela':
                        renderizar_tabela_widget(tipo, df_widget)
                    elif tipo_viz == 'lista':
                        renderizar_lista_widget(tipo, df_widget, filtros)
                
                st.markdown("---")


# Mantém compatibilidade com a função antiga mas redireciona para nova
def aba_dashboard_personalizado(df: pd.DataFrame):
    """Aba para criar e visualizar dashboards personalizados - DEPRECADO."""
    tela_consulta_personalizada(df)


# ==============================================================================
# CATÁLOGO DE MÉTRICAS - LEGACY (mantido para compatibilidade)
# ==============================================================================

CATALOGO_METRICAS = {
    # === MÉTRICAS DE QUALIDADE ===
    "fator_k_geral": {
        "nome": "Fator K (Geral)",
        "categoria": "📊 Qualidade",
        "descricao": "Razão entre Story Points e Bugs do projeto inteiro",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_fator_k_geral"
    },
    "fator_k_dev": {
        "nome": "Fator K por Desenvolvedor",
        "categoria": "📊 Qualidade",
        "descricao": "Fator K individual de cada desenvolvedor",
        "tipo": "tabela",
        "parametros": ["desenvolvedor"],
        "funcao": "calcular_fator_k_dev"
    },
    "fpy": {
        "nome": "FPY - First Pass Yield",
        "categoria": "📊 Qualidade",
        "descricao": "% de cards aprovados na primeira validação",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_fpy"
    },
    "ddp": {
        "nome": "DDP - Defect Detection",
        "categoria": "📊 Qualidade",
        "descricao": "% de defeitos encontrados antes da produção",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_ddp"
    },
    "health_score": {
        "nome": "Health Score",
        "categoria": "📊 Qualidade",
        "descricao": "Pontuação de saúde da release (0-100)",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_health_score"
    },
    
    # === MÉTRICAS DE PRODUTIVIDADE ===
    "throughput_cards": {
        "nome": "Throughput (Cards)",
        "categoria": "🚀 Produtividade",
        "descricao": "Quantidade de cards concluídos",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_throughput_cards"
    },
    "throughput_sp": {
        "nome": "Throughput (Story Points)",
        "categoria": "🚀 Produtividade",
        "descricao": "Quantidade de SP entregues",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_throughput_sp"
    },
    "lead_time": {
        "nome": "Lead Time Médio",
        "categoria": "🚀 Produtividade",
        "descricao": "Tempo médio do card (criação → conclusão)",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_lead_time"
    },
    "wip": {
        "nome": "WIP - Work In Progress",
        "categoria": "🚀 Produtividade",
        "descricao": "Cards em andamento agora",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_wip"
    },
    "velocidade_media": {
        "nome": "Velocidade Média",
        "categoria": "🚀 Produtividade",
        "descricao": "SP médio por card concluído",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_velocidade_media"
    },
    
    # === MÉTRICAS DE BUGS ===
    "total_bugs": {
        "nome": "Total de Bugs",
        "categoria": "🐛 Bugs",
        "descricao": "Quantidade total de bugs encontrados",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_total_bugs"
    },
    "densidade_bugs": {
        "nome": "Densidade de Bugs",
        "categoria": "🐛 Bugs",
        "descricao": "Bugs por Story Point",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_densidade_bugs"
    },
    "bugs_por_dev": {
        "nome": "Bugs por Desenvolvedor",
        "categoria": "🐛 Bugs",
        "descricao": "Ranking de bugs por desenvolvedor",
        "tipo": "grafico_barra",
        "parametros": [],
        "funcao": "calcular_bugs_por_dev"
    },
    
    # === MÉTRICAS DE QA ===
    "carga_qa": {
        "nome": "Carga por QA",
        "categoria": "🔬 QA",
        "descricao": "Cards em validação por QA",
        "tipo": "grafico_barra",
        "parametros": ["qa"],
        "funcao": "calcular_carga_qa"
    },
    "funil_qa": {
        "nome": "Funil de QA",
        "categoria": "🔬 QA",
        "descricao": "Status do funil de validação",
        "tipo": "grafico_funil",
        "parametros": [],
        "funcao": "calcular_funil_qa"
    },
    "aging_qa": {
        "nome": "Aging QA",
        "categoria": "🔬 QA",
        "descricao": "Cards aguardando validação há muito tempo",
        "tipo": "tabela",
        "parametros": [],
        "funcao": "calcular_aging_qa"
    },
    "taxa_reprovacao": {
        "nome": "Taxa de Reprovação",
        "categoria": "🔬 QA",
        "descricao": "% de cards reprovados",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_taxa_reprovacao"
    },
    
    # === MÉTRICAS DE DESENVOLVIMENTO ===
    "ranking_devs": {
        "nome": "Ranking de Desenvolvedores",
        "categoria": "👨‍💻 Desenvolvimento",
        "descricao": "Ranking por Fator K, SP e bugs",
        "tipo": "tabela",
        "parametros": [],
        "funcao": "calcular_ranking_devs"
    },
    "code_review_fila": {
        "nome": "Fila de Code Review",
        "categoria": "👨‍💻 Desenvolvimento",
        "descricao": "Cards aguardando code review",
        "tipo": "lista_cards",
        "parametros": [],
        "funcao": "calcular_code_review_fila"
    },
    "cards_por_dev": {
        "nome": "Cards por Desenvolvedor",
        "categoria": "👨‍💻 Desenvolvimento",
        "descricao": "Distribuição de cards por desenvolvedor",
        "tipo": "grafico_pizza",
        "parametros": [],
        "funcao": "calcular_cards_por_dev"
    },
    
    # === MÉTRICAS DE STATUS ===
    "cards_por_status": {
        "nome": "Cards por Status",
        "categoria": "📋 Status",
        "descricao": "Distribuição de cards por status",
        "tipo": "grafico_barra",
        "parametros": [],
        "funcao": "calcular_cards_por_status"
    },
    "cards_aguardando_qa": {
        "nome": "Aguardando QA",
        "categoria": "📋 Status",
        "descricao": "Cards aguardando validação",
        "tipo": "lista_cards",
        "parametros": [],
        "funcao": "calcular_aguardando_qa"
    },
    "cards_impedidos": {
        "nome": "Cards Impedidos",
        "categoria": "📋 Status",
        "descricao": "Cards com impedimentos",
        "tipo": "lista_cards",
        "parametros": [],
        "funcao": "calcular_impedidos"
    },
    "cards_bloqueados": {
        "nome": "Cards Bloqueados",
        "categoria": "📋 Status",
        "descricao": "Cards bloqueados",
        "tipo": "lista_cards",
        "parametros": [],
        "funcao": "calcular_bloqueados"
    },
    
    # === MÉTRICAS DE PRODUTO ===
    "por_produto": {
        "nome": "Cards por Produto",
        "categoria": "📦 Produto",
        "descricao": "Distribuição por produto",
        "tipo": "grafico_pizza",
        "parametros": [],
        "funcao": "calcular_por_produto"
    },
    "hotfix_por_produto": {
        "nome": "Hotfixes por Produto",
        "categoria": "📦 Produto",
        "descricao": "Hotfixes agrupados por produto",
        "tipo": "grafico_barra",
        "parametros": [],
        "funcao": "calcular_hotfix_produto"
    },
    
    # === MÉTRICAS DE CONCENTRAÇÃO ===
    "concentracao_dev": {
        "nome": "Concentração DEV",
        "categoria": "🎯 Concentração",
        "descricao": "Concentração de conhecimento por DEV",
        "tipo": "heatmap",
        "parametros": [],
        "funcao": "calcular_concentracao_dev"
    },
    "concentracao_qa": {
        "nome": "Concentração QA",
        "categoria": "🎯 Concentração",
        "descricao": "Concentração de conhecimento por QA",
        "tipo": "heatmap",
        "parametros": [],
        "funcao": "calcular_concentracao_qa"
    },
    
    # === MÉTRICAS DE CLIENTE ===
    "top_clientes": {
        "nome": "Top Clientes",
        "categoria": "🏢 Clientes",
        "descricao": "Clientes com mais cards",
        "tipo": "grafico_barra",
        "parametros": [],
        "funcao": "calcular_top_clientes"
    },
    "clientes_bugs": {
        "nome": "Bugs por Cliente",
        "categoria": "🏢 Clientes",
        "descricao": "Clientes com mais bugs reportados",
        "tipo": "grafico_barra",
        "parametros": [],
        "funcao": "calcular_clientes_bugs"
    },
}

# Categorias disponíveis para filtro
CATEGORIAS_METRICAS = [
    "📊 Qualidade",
    "🚀 Produtividade", 
    "🐛 Bugs",
    "🔬 QA",
    "👨‍💻 Desenvolvimento",
    "📋 Status",
    "📦 Produto",
    "🎯 Concentração",
    "🏢 Clientes",
]


# ==============================================================================
# FUNÇÕES DO DASHBOARD PERSONALIZADO
# ==============================================================================

def inicializar_dashboards_personalizados():
    """Inicializa o armazenamento de dashboards personalizados no session_state."""
    if 'dashboards_personalizados' not in st.session_state:
        st.session_state.dashboards_personalizados = {}
    if 'dashboard_ativo' not in st.session_state:
        st.session_state.dashboard_ativo = None
    if 'modo_builder' not in st.session_state:
        st.session_state.modo_builder = False


def salvar_dashboard_personalizado(nome: str, metricas: List[str], config: Dict = None):
    """Salva um dashboard personalizado."""
    inicializar_dashboards_personalizados()
    
    st.session_state.dashboards_personalizados[nome] = {
        "nome": nome,
        "metricas": metricas,
        "config": config or {},
        "criado_em": datetime.now().isoformat(),
        "atualizado_em": datetime.now().isoformat()
    }


def carregar_dashboard_personalizado(nome: str) -> Optional[Dict]:
    """Carrega um dashboard personalizado."""
    inicializar_dashboards_personalizados()
    return st.session_state.dashboards_personalizados.get(nome)


def listar_dashboards_personalizados() -> List[str]:
    """Lista todos os dashboards personalizados."""
    inicializar_dashboards_personalizados()
    return list(st.session_state.dashboards_personalizados.keys())


def excluir_dashboard_personalizado(nome: str):
    """Exclui um dashboard personalizado."""
    inicializar_dashboards_personalizados()
    if nome in st.session_state.dashboards_personalizados:
        del st.session_state.dashboards_personalizados[nome]


def renderizar_metrica_personalizada(metrica_key: str, df: pd.DataFrame):
    """Renderiza uma métrica do catálogo no dashboard personalizado."""
    if metrica_key not in CATALOGO_METRICAS:
        st.warning(f"⚠️ Métrica '{metrica_key}' não encontrada")
        return
    
    metrica = CATALOGO_METRICAS[metrica_key]
    tipo = metrica["tipo"]
    
    # Header da métrica
    st.markdown(f"#### {metrica['nome']}")
    st.caption(metrica['descricao'])
    
    try:
        # === KPIs (números simples) ===
        if tipo == "kpi":
            valor = calcular_valor_metrica(metrica_key, df)
            if valor is not None:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.metric(label=metrica['nome'], value=valor)
        
        # === Gráficos de Barra ===
        elif tipo == "grafico_barra":
            dados = calcular_dados_grafico(metrica_key, df)
            if dados is not None and not dados.empty:
                fig = px.bar(dados, x=dados.index, y=dados.values, 
                           title=metrica['nome'],
                           labels={'x': '', 'y': 'Quantidade'})
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        # === Gráficos de Pizza ===
        elif tipo == "grafico_pizza":
            dados = calcular_dados_grafico(metrica_key, df)
            if dados is not None and not dados.empty:
                fig = px.pie(values=dados.values, names=dados.index,
                           title=metrica['nome'])
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        # === Tabelas ===
        elif tipo == "tabela":
            dados = calcular_dados_tabela(metrica_key, df)
            if dados is not None and not dados.empty:
                st.dataframe(dados, use_container_width=True, height=250)
        
        # === Listas de Cards ===
        elif tipo == "lista_cards":
            cards = calcular_lista_cards(metrica_key, df)
            if cards is not None and len(cards) > 0:
                for card in cards[:10]:  # Limita a 10 cards
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.markdown(f"**{card.get('key', 'N/A')}**")
                    with col2:
                        titulo = card.get('titulo', card.get('resumo', ''))[:60]
                        st.markdown(f"{titulo}")
            else:
                st.info("Nenhum card encontrado")
        
        # === Heatmaps ===
        elif tipo == "heatmap":
            dados = calcular_dados_heatmap(metrica_key, df)
            if dados is not None and not dados.empty:
                fig = px.imshow(dados, aspect='auto', color_continuous_scale='RdYlGn',
                              title=metrica['nome'])
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
        
        # === Funil ===
        elif tipo == "grafico_funil":
            dados = calcular_dados_funil(metrica_key, df)
            if dados:
                criar_grafico_funil_personalizado(dados, metrica['nome'])
        
        else:
            st.info(f"Tipo de visualização '{tipo}' em desenvolvimento")
            
    except Exception as e:
        st.error(f"Erro ao renderizar métrica: {str(e)}")


def calcular_valor_metrica(metrica_key: str, df: pd.DataFrame):
    """Calcula o valor de uma métrica KPI."""
    try:
        if metrica_key == "fator_k_geral":
            total_sp = df['story_points'].sum()
            total_bugs = df['bugs_encontrados'].sum()
            return f"{total_sp / (total_bugs + 1):.2f}"
        
        elif metrica_key == "fpy":
            metricas = calcular_fpy(df)
            return f"{metricas.get('fpy', 0):.1f}%"
        
        elif metrica_key == "ddp":
            metricas = calcular_ddp(df)
            return f"{metricas.get('ddp', 0):.1f}%"
        
        elif metrica_key == "health_score":
            metricas = calcular_health_score(df)
            return f"{metricas.get('score', 0):.0f}"
        
        elif metrica_key == "throughput_cards":
            concluidos = df[df['status_categoria'] == 'done']
            return str(len(concluidos))
        
        elif metrica_key == "throughput_sp":
            concluidos = df[df['status_categoria'] == 'done']
            return str(int(concluidos['story_points'].sum()))
        
        elif metrica_key == "lead_time":
            metricas = calcular_lead_time(df)
            return f"{metricas.get('media', 0):.1f} dias"
        
        elif metrica_key == "wip":
            em_andamento = df[~df['status_categoria'].isin(['done', 'backlog', 'deferred'])]
            return str(len(em_andamento))
        
        elif metrica_key == "velocidade_media":
            concluidos = df[df['status_categoria'] == 'done']
            if len(concluidos) > 0:
                return f"{concluidos['story_points'].mean():.1f} SP"
            return "0 SP"
        
        elif metrica_key == "total_bugs":
            return str(int(df['bugs_encontrados'].sum()))
        
        elif metrica_key == "densidade_bugs":
            total_sp = df['story_points'].sum()
            total_bugs = df['bugs_encontrados'].sum()
            if total_sp > 0:
                return f"{total_bugs / total_sp:.2f}"
            return "0.00"
        
        elif metrica_key == "taxa_reprovacao":
            reprovados = df[df['status_categoria'] == 'rejected']
            total = len(df)
            if total > 0:
                return f"{(len(reprovados) / total) * 100:.1f}%"
            return "0%"
        
        return None
    except Exception:
        return None


def calcular_dados_grafico(metrica_key: str, df: pd.DataFrame):
    """Calcula dados para gráficos de barra/pizza."""
    try:
        if metrica_key == "bugs_por_dev":
            bugs_dev = df.groupby('responsavel')['bugs_encontrados'].sum().sort_values(ascending=False)
            return bugs_dev.head(10)
        
        elif metrica_key == "carga_qa":
            em_qa = df[df['status_categoria'].isin(['waiting_qa', 'testing'])]
            return em_qa['qa_responsavel'].value_counts().head(10)
        
        elif metrica_key == "cards_por_status":
            return df['status'].value_counts()
        
        elif metrica_key == "cards_por_dev":
            return df['responsavel'].value_counts().head(10)
        
        elif metrica_key == "por_produto":
            return df['produto'].value_counts()
        
        elif metrica_key == "hotfix_produto":
            hotfixes = df[df['tipo'].str.lower().str.contains('hotfix', na=False)]
            return hotfixes['produto'].value_counts()
        
        elif metrica_key == "top_clientes":
            if 'temas' in df.columns:
                # Extrai clientes dos temas
                clientes = []
                for temas in df['temas'].dropna():
                    if isinstance(temas, list):
                        clientes.extend(temas)
                    elif isinstance(temas, str):
                        clientes.append(temas)
                return pd.Series(clientes).value_counts().head(10)
            return pd.Series()
        
        elif metrica_key == "clientes_bugs":
            if 'temas' in df.columns:
                df_com_bugs = df[df['bugs_encontrados'] > 0]
                clientes = []
                for _, row in df_com_bugs.iterrows():
                    temas = row.get('temas', [])
                    if isinstance(temas, list):
                        for tema in temas:
                            clientes.append(tema)
                return pd.Series(clientes).value_counts().head(10)
            return pd.Series()
        
        return None
    except Exception:
        return None


def calcular_dados_tabela(metrica_key: str, df: pd.DataFrame):
    """Calcula dados para tabelas."""
    try:
        if metrica_key == "ranking_devs":
            # Agrupa por desenvolvedor
            ranking = df.groupby('responsavel').agg({
                'story_points': 'sum',
                'bugs_encontrados': 'sum',
                'key': 'count'
            }).reset_index()
            ranking.columns = ['Desenvolvedor', 'SP', 'Bugs', 'Cards']
            ranking['Fator K'] = ranking['SP'] / (ranking['Bugs'] + 1)
            ranking = ranking.sort_values('Fator K', ascending=False)
            return ranking[['Desenvolvedor', 'Cards', 'SP', 'Bugs', 'Fator K']].head(15)
        
        elif metrica_key == "aging_qa":
            em_qa = df[df['status_categoria'].isin(['waiting_qa', 'testing'])].copy()
            if 'data_criacao' in em_qa.columns:
                em_qa['Dias'] = (datetime.now() - pd.to_datetime(em_qa['data_criacao'])).dt.days
                return em_qa[['key', 'resumo', 'qa_responsavel', 'Dias']].sort_values('Dias', ascending=False).head(10)
            return pd.DataFrame()
        
        elif metrica_key == "fator_k_dev":
            # Similar ao ranking_devs mas focado no FK
            ranking = df.groupby('responsavel').agg({
                'story_points': 'sum',
                'bugs_encontrados': 'sum'
            }).reset_index()
            ranking['Fator K'] = ranking['story_points'] / (ranking['bugs_encontrados'] + 1)
            ranking = ranking.sort_values('Fator K', ascending=False)
            ranking.columns = ['Desenvolvedor', 'SP', 'Bugs', 'Fator K']
            return ranking.head(15)
        
        return None
    except Exception:
        return None


def calcular_lista_cards(metrica_key: str, df: pd.DataFrame):
    """Calcula lista de cards para exibição."""
    try:
        if metrica_key == "code_review_fila":
            em_cr = df[df['status_categoria'] == 'code_review']
            return em_cr[['key', 'resumo', 'responsavel']].to_dict('records')
        
        elif metrica_key == "cards_aguardando_qa":
            aguardando = df[df['status_categoria'] == 'waiting_qa']
            return aguardando[['key', 'resumo', 'qa_responsavel']].to_dict('records')
        
        elif metrica_key == "cards_impedidos":
            impedidos = df[df['status_categoria'] == 'blocked']
            return impedidos[['key', 'resumo', 'responsavel']].to_dict('records')
        
        elif metrica_key == "cards_bloqueados":
            bloqueados = df[df['status'].str.lower().str.contains('bloque|block', na=False)]
            return bloqueados[['key', 'resumo', 'responsavel']].to_dict('records')
        
        return []
    except Exception:
        return []


def calcular_dados_heatmap(metrica_key: str, df: pd.DataFrame):
    """Calcula dados para heatmaps."""
    try:
        if metrica_key == "concentracao_dev":
            conc = calcular_concentracao_conhecimento(df)
            return conc.get('matriz_dev')
        
        elif metrica_key == "concentracao_qa":
            conc = calcular_concentracao_conhecimento(df)
            return conc.get('matriz_qa')
        
        return None
    except Exception:
        return None


def calcular_dados_funil(metrica_key: str, df: pd.DataFrame):
    """Calcula dados para gráficos de funil."""
    try:
        if metrica_key == "funil_qa":
            metricas = calcular_metricas_qa(df)
            return metricas
        return None
    except Exception:
        return None


def criar_grafico_funil_personalizado(dados: Dict, titulo: str):
    """Cria um gráfico de funil simplificado."""
    try:
        # Extrai valores do funil
        aguardando = dados.get('aguardando_qa', 0)
        em_validacao = dados.get('em_validacao', 0)
        concluidos = dados.get('validados', 0)
        reprovados = dados.get('reprovados', 0)
        
        labels = ['Aguardando QA', 'Em Validação', 'Concluídos', 'Reprovados']
        valores = [aguardando, em_validacao, concluidos, reprovados]
        
        fig = go.Figure(go.Funnel(
            y=labels,
            x=valores,
            textposition="inside",
            textinfo="value+percent initial",
            marker={"color": ["#f59e0b", "#3b82f6", "#22c55e", "#ef4444"]}
        ))
        fig.update_layout(height=300, title=titulo)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Erro no funil: {e}")


def aba_dashboard_personalizado(df: pd.DataFrame):
    """Aba para criar e visualizar dashboards personalizados."""
    
    inicializar_dashboards_personalizados()
    
    st.markdown("## 🎨 Dashboard Personalizado")
    st.markdown("Crie seu próprio dashboard selecionando as métricas que deseja acompanhar.")
    
    # Tabs para organizar a interface
    tab_visualizar, tab_criar, tab_gerenciar = st.tabs([
        "📊 Visualizar Dashboard",
        "➕ Criar Novo",
        "⚙️ Gerenciar"
    ])
    
    # === ABA VISUALIZAR ===
    with tab_visualizar:
        dashboards = listar_dashboards_personalizados()
        
        if not dashboards:
            st.info("🎯 Você ainda não tem dashboards personalizados. Crie um na aba 'Criar Novo'!")
            
            # Sugestões rápidas
            st.markdown("### 💡 Sugestões Rápidas")
            st.markdown("Clique para criar um dashboard pré-configurado:")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 Visão Executiva", use_container_width=True, key="btn_exec"):
                    salvar_dashboard_personalizado(
                        "Visão Executiva",
                        ["health_score", "throughput_cards", "fator_k_geral", "lead_time", "cards_por_status"]
                    )
                    st.success("Dashboard 'Visão Executiva' criado!")
                    st.rerun()
            
            with col2:
                if st.button("🔬 Foco em QA", use_container_width=True, key="btn_qa"):
                    salvar_dashboard_personalizado(
                        "Foco em QA",
                        ["fpy", "ddp", "funil_qa", "carga_qa", "aging_qa", "taxa_reprovacao"]
                    )
                    st.success("Dashboard 'Foco em QA' criado!")
                    st.rerun()
            
            with col3:
                if st.button("👨‍💻 Foco em Dev", use_container_width=True, key="btn_dev"):
                    salvar_dashboard_personalizado(
                        "Foco em Dev",
                        ["fator_k_geral", "ranking_devs", "bugs_por_dev", "code_review_fila", "wip"]
                    )
                    st.success("Dashboard 'Foco em Dev' criado!")
                    st.rerun()
        
        else:
            # Seletor de dashboard
            col1, col2 = st.columns([3, 1])
            with col1:
                dashboard_selecionado = st.selectbox(
                    "Selecione um dashboard",
                    options=dashboards,
                    key="select_dash_view"
                )
            with col2:
                if st.button("🔄 Atualizar", use_container_width=True, key="btn_atualizar"):
                    st.rerun()
            
            if dashboard_selecionado:
                dash = carregar_dashboard_personalizado(dashboard_selecionado)
                
                if dash:
                    st.markdown(f"### 📈 {dash['nome']}")
                    st.caption(f"Última atualização: {dash.get('atualizado_em', 'N/A')[:16]}")
                    
                    st.markdown("---")
                    
                    # Renderiza as métricas em grid
                    metricas = dash.get('metricas', [])
                    
                    if not metricas:
                        st.warning("Este dashboard não tem métricas configuradas.")
                    else:
                        # Organiza em colunas (2 métricas por linha)
                        for i in range(0, len(metricas), 2):
                            cols = st.columns(2)
                            
                            for j, col in enumerate(cols):
                                idx = i + j
                                if idx < len(metricas):
                                    with col:
                                        with st.container():
                                            renderizar_metrica_personalizada(metricas[idx], df)
                                            st.markdown("---")
    
    # === ABA CRIAR ===
    with tab_criar:
        st.markdown("### ➕ Criar Novo Dashboard")
        
        # Nome do dashboard
        nome_novo = st.text_input(
            "Nome do Dashboard",
            placeholder="Ex: Meu Dashboard de QA",
            key="input_nome_dash"
        )
        
        # Filtro por categoria
        categorias_selecionadas = st.multiselect(
            "Filtrar por categoria",
            options=CATEGORIAS_METRICAS,
            default=[],
            key="filtro_categorias"
        )
        
        # Lista de métricas disponíveis
        st.markdown("#### 📋 Métricas Disponíveis")
        st.caption("Selecione as métricas que deseja incluir no dashboard")
        
        metricas_selecionadas = []
        
        # Agrupa métricas por categoria
        metricas_por_categoria = {}
        for key, metrica in CATALOGO_METRICAS.items():
            cat = metrica['categoria']
            if cat not in metricas_por_categoria:
                metricas_por_categoria[cat] = []
            metricas_por_categoria[cat].append((key, metrica))
        
        # Exibe métricas agrupadas
        for categoria in CATEGORIAS_METRICAS:
            # Aplica filtro de categoria se houver
            if categorias_selecionadas and categoria not in categorias_selecionadas:
                continue
            
            if categoria in metricas_por_categoria:
                with st.expander(categoria, expanded=len(categorias_selecionadas) > 0):
                    for key, metrica in metricas_por_categoria[categoria]:
                        col1, col2, col3 = st.columns([0.5, 3, 1])
                        with col1:
                            selecionado = st.checkbox(
                                "",
                                key=f"check_{key}",
                                label_visibility="collapsed"
                            )
                            if selecionado:
                                metricas_selecionadas.append(key)
                        with col2:
                            st.markdown(f"**{metrica['nome']}**")
                            st.caption(metrica['descricao'])
                        with col3:
                            tipo_badge = {
                                "kpi": "🔢",
                                "grafico_barra": "📊",
                                "grafico_pizza": "🥧",
                                "tabela": "📋",
                                "lista_cards": "📝",
                                "heatmap": "🗺️",
                                "grafico_funil": "📈"
                            }
                            st.markdown(f"{tipo_badge.get(metrica['tipo'], '📊')} {metrica['tipo']}")
        
        # Preview das seleções
        if metricas_selecionadas:
            st.markdown("---")
            st.markdown(f"**{len(metricas_selecionadas)} métricas selecionadas:**")
            for m in metricas_selecionadas:
                st.markdown(f"- {CATALOGO_METRICAS[m]['nome']}")
        
        # Botão de salvar
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("💾 Salvar Dashboard", type="primary", use_container_width=True, key="btn_salvar_dash"):
                if not nome_novo:
                    st.error("Digite um nome para o dashboard")
                elif not metricas_selecionadas:
                    st.error("Selecione pelo menos uma métrica")
                else:
                    salvar_dashboard_personalizado(nome_novo, metricas_selecionadas)
                    st.success(f"Dashboard '{nome_novo}' salvo com sucesso!")
                    st.balloons()
                    st.rerun()
    
    # === ABA GERENCIAR ===
    with tab_gerenciar:
        st.markdown("### ⚙️ Gerenciar Dashboards")
        
        dashboards = listar_dashboards_personalizados()
        
        if not dashboards:
            st.info("Nenhum dashboard personalizado criado ainda.")
        else:
            for nome in dashboards:
                dash = carregar_dashboard_personalizado(nome)
                with st.expander(f"📊 {nome}", expanded=False):
                    st.markdown(f"**Métricas:** {len(dash.get('metricas', []))}")
                    st.caption(f"Criado em: {dash.get('criado_em', 'N/A')[:16]}")
                    
                    # Lista métricas
                    st.markdown("**Métricas incluídas:**")
                    for m in dash.get('metricas', []):
                        if m in CATALOGO_METRICAS:
                            st.markdown(f"- {CATALOGO_METRICAS[m]['nome']}")
                    
                    # Botão excluir
                    if st.button(f"🗑️ Excluir '{nome}'", key=f"btn_excluir_{nome}"):
                        excluir_dashboard_personalizado(nome)
                        st.success(f"Dashboard '{nome}' excluído!")
                        st.rerun()


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
        "resolutiondate", "priority", "project", "labels", "reporter", "resolution",
        "issuelinks",  # Links para rastrear origem do PB
        CUSTOM_FIELDS["story_points"],
        CUSTOM_FIELDS["story_points_alt"],
        CUSTOM_FIELDS["sprint"],
        CUSTOM_FIELDS["bugs_encontrados"],
        CUSTOM_FIELDS["complexidade_teste"],
        CUSTOM_FIELDS["qa_responsavel"],
        CUSTOM_FIELDS["produto"],
        CUSTOM_FIELDS["temas"],
        CUSTOM_FIELDS["importancia"],
        CUSTOM_FIELDS["sla_status"],
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
            # Para quando não há mais páginas (sem limite artificial)
            if not next_page_token:
                break
        
        return all_issues, datetime.now()
    
    except Exception as e:
        st.error(f"Erro ao conectar com Jira: {e}")
        return None, datetime.now()


@st.cache_data(ttl=300, show_spinner=False)
def buscar_card_especifico(ticket_id: str) -> Tuple[Optional[Dict], Optional[List[Dict]], Optional[List[Dict]], Optional[List[Dict]]]:
    """
    Busca um card específico pelo ID, sem filtros de período.
    Retorna: (issue, links, comentarios, historico_transicoes)
    """
    secrets = get_secrets()
    if not secrets["email"] or not secrets["token"]:
        return None, None, None, None
    
    try:
        # Busca o card específico com links e changelog
        base_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}"
        headers = {"Accept": "application/json"}
        
        fields = [
            "key", "summary", "status", "issuetype", "assignee", "created", "updated",
            "resolutiondate", "priority", "project", "labels", "issuelinks", "parent", "subtasks",
            "description", "reporter", "resolution",
            CUSTOM_FIELDS["story_points"],
            CUSTOM_FIELDS["story_points_alt"],
            CUSTOM_FIELDS["sprint"],
            CUSTOM_FIELDS["bugs_encontrados"],
            CUSTOM_FIELDS["complexidade_teste"],
            CUSTOM_FIELDS["qa_responsavel"],
            CUSTOM_FIELDS["produto"],
        ]
        
        # Adiciona changelog para histórico de transições
        params = {"fields": ",".join(fields), "expand": "renderedFields,changelog"}
        
        response = requests.get(
            base_url,
            headers=headers,
            params=params,
            auth=(secrets["email"], secrets["token"]),
            timeout=30
        )
        
        if response.status_code == 404:
            return None, None, None, None
        
        response.raise_for_status()
        issue = response.json()
        
        # Extrai os links do card
        links = []
        fields_data = issue.get('fields', {})
        
        # Links diretos (issuelinks)
        issue_links = fields_data.get('issuelinks', [])
        for link in issue_links:
            link_type = traduzir_link(link.get('type', {}).get('name', 'Relacionado'))
            
            # Link de saída (outwardIssue)
            if 'outwardIssue' in link:
                linked = link['outwardIssue']
                links.append({
                    'tipo': link_type,
                    'direcao': traduzir_link(link.get('type', {}).get('outward', 'relacionado a')),
                    'ticket_id': linked.get('key', ''),
                    'titulo': linked.get('fields', {}).get('summary', ''),
                    'status': linked.get('fields', {}).get('status', {}).get('name', ''),
                    'link': f"{JIRA_BASE_URL}/browse/{linked.get('key', '')}",
                    'nivel': 1  # Link direto (primeiro nível)
                })
            
            # Link de entrada (inwardIssue)
            if 'inwardIssue' in link:
                linked = link['inwardIssue']
                links.append({
                    'tipo': link_type,
                    'direcao': traduzir_link(link.get('type', {}).get('inward', 'relacionado a')),
                    'ticket_id': linked.get('key', ''),
                    'titulo': linked.get('fields', {}).get('summary', ''),
                    'status': linked.get('fields', {}).get('status', {}).get('name', ''),
                    'link': f"{JIRA_BASE_URL}/browse/{linked.get('key', '')}",
                    'nivel': 1  # Link direto (primeiro nível)
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
                'tipo': 'Subtarefa',
                'direcao': 'é pai de',
                'ticket_id': sub.get('key', ''),
                'titulo': sub.get('fields', {}).get('summary', ''),
                'status': sub.get('fields', {}).get('status', {}).get('name', ''),
                'link': f"{JIRA_BASE_URL}/browse/{sub.get('key', '')}",
                'nivel': 1
            })
        
        # ===== BUSCA LINKS TRANSITIVOS (SEGUNDO NÍVEL) =====
        # Para cada card vinculado, busca seus links também
        links_primeiro_nivel = [l['ticket_id'] for l in links]
        links_transitivos = []
        
        for link_info in links:
            try:
                linked_ticket = link_info['ticket_id']
                if not linked_ticket:
                    continue
                
                # Busca os links do card vinculado (sem recursão adicional)
                linked_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{linked_ticket}"
                linked_params = {"fields": "issuelinks,summary,status"}
                
                linked_response = requests.get(
                    linked_url,
                    headers=headers,
                    params=linked_params,
                    auth=(secrets["email"], secrets["token"]),
                    timeout=10
                )
                
                if linked_response.status_code == 200:
                    linked_data = linked_response.json()
                    linked_fields = linked_data.get('fields', {})
                    linked_issue_links = linked_fields.get('issuelinks', [])
                    
                    for sub_link in linked_issue_links:
                        sub_type = traduzir_link(sub_link.get('type', {}).get('name', 'Relacionado'))
                        
                        # Link de saída
                        if 'outwardIssue' in sub_link:
                            sub_linked = sub_link['outwardIssue']
                            sub_key = sub_linked.get('key', '')
                            # Não adiciona se já está nos links diretos ou é o card original
                            if sub_key and sub_key != ticket_id and sub_key not in links_primeiro_nivel:
                                links_transitivos.append({
                                    'tipo': sub_type,
                                    'direcao': traduzir_link(sub_link.get('type', {}).get('outward', 'relacionado a')),
                                    'ticket_id': sub_key,
                                    'titulo': sub_linked.get('fields', {}).get('summary', ''),
                                    'status': sub_linked.get('fields', {}).get('status', {}).get('name', ''),
                                    'link': f"{JIRA_BASE_URL}/browse/{sub_key}",
                                    'nivel': 2,  # Segundo nível (transitivo)
                                    'via': linked_ticket  # Indica por qual card chegou
                                })
                        
                        # Link de entrada
                        if 'inwardIssue' in sub_link:
                            sub_linked = sub_link['inwardIssue']
                            sub_key = sub_linked.get('key', '')
                            if sub_key and sub_key != ticket_id and sub_key not in links_primeiro_nivel:
                                links_transitivos.append({
                                    'tipo': sub_type,
                                    'direcao': traduzir_link(sub_link.get('type', {}).get('inward', 'relacionado a')),
                                    'ticket_id': sub_key,
                                    'titulo': sub_linked.get('fields', {}).get('summary', ''),
                                    'status': sub_linked.get('fields', {}).get('status', {}).get('name', ''),
                                    'link': f"{JIRA_BASE_URL}/browse/{sub_key}",
                                    'nivel': 2,
                                    'via': linked_ticket
                                })
            except Exception:
                continue  # Falha silenciosa para links transitivos
        
        # Remove duplicatas dos transitivos
        seen = set(l['ticket_id'] for l in links)
        for lt in links_transitivos:
            if lt['ticket_id'] not in seen:
                links.append(lt)
                seen.add(lt['ticket_id'])
        
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
        
        # ===== EXTRAI HISTÓRICO DE TRANSIÇÕES DO CHANGELOG =====
        historico_transicoes = extrair_historico_transicoes(issue, ticket_id)
        
        return issue, links, comentarios, historico_transicoes
    
    except Exception as e:
        st.error(f"Erro ao buscar card: {e}")
        return None, None, None, None


def extrair_historico_transicoes(issue: Dict, ticket_id: str) -> List[Dict]:
    """
    Extrai o histórico completo de transições de status do changelog do Jira.
    
    Retorna lista ordenada cronologicamente com:
    - data: datetime da transição
    - de: status anterior
    - para: novo status
    - autor: quem fez a mudança
    - tipo: 'criacao', 'transicao', 'campo'
    - campo: nome do campo alterado (se não for status)
    - tempo_no_status: dias que ficou no status anterior
    """
    historico = []
    
    try:
        fields = issue.get('fields', {})
        changelog = issue.get('changelog', {})
        
        # 1. Primeiro evento: Criação do card
        data_criacao_str = fields.get('created', '')
        reporter = fields.get('reporter', {})
        
        if data_criacao_str:
            try:
                data_criacao = datetime.fromisoformat(data_criacao_str.replace('Z', '+00:00')).replace(tzinfo=None)
            except:
                data_criacao = datetime.now()
            
            historico.append({
                'data': data_criacao,
                'de': None,
                'para': 'Criado',
                'autor': reporter.get('displayName', 'Sistema') if reporter else 'Sistema',
                'tipo': 'criacao',
                'campo': 'Card',
                'detalhes': f"Card {ticket_id} criado",
                'icone': gerar_icone_tabler('file', tamanho=32, cor='#22c55e'),
                'cor': '#22c55e'
            })
        
        # 2. Processa todas as entradas do changelog
        histories = changelog.get('histories', [])
        
        for entry in histories:
            entry_date_str = entry.get('created', '')
            author = entry.get('author', {})
            author_name = author.get('displayName', 'Sistema') if author else 'Sistema'
            
            try:
                entry_date = datetime.fromisoformat(entry_date_str.replace('Z', '+00:00')).replace(tzinfo=None)
            except:
                continue
            
            items = entry.get('items', [])
            
            for item in items:
                field = item.get('field', '')
                field_type = item.get('fieldtype', '')
                from_value = item.get('fromString', '') or ''
                to_value = item.get('toString', '') or ''
                
                # Transições de STATUS são as mais importantes
                if field.lower() == 'status':
                    # Determina ícone e cor baseado no status de destino
                    icone, cor = obter_icone_status(to_value)
                    
                    historico.append({
                        'data': entry_date,
                        'de': from_value if from_value else 'Sem status',
                        'para': to_value if to_value else 'Desconhecido',
                        'autor': author_name,
                        'tipo': 'transicao',
                        'campo': 'Status',
                        'detalhes': f"{from_value or 'Início'} → {to_value}",
                        'icone': icone,
                        'cor': cor
                    })
                
                # Também captura mudanças importantes de outros campos
                elif field.lower() in ['assignee', 'responsável']:
                    historico.append({
                        'data': entry_date,
                        'de': from_value if from_value else 'Não atribuído',
                        'para': to_value if to_value else 'Não atribuído',
                        'autor': author_name,
                        'tipo': 'atribuicao',
                        'campo': 'Responsável',
                        'detalhes': f"Atribuído: {from_value or 'Ninguém'} → {to_value or 'Ninguém'}",
                        'icone': gerar_icone_tabler('user-check', tamanho=32, cor='#6366f1'),
                        'cor': '#6366f1'
                    })
                
                elif 'qa' in field.lower() or field == CUSTOM_FIELDS.get('qa_responsavel', ''):
                    historico.append({
                        'data': entry_date,
                        'de': from_value if from_value else 'Não atribuído',
                        'para': to_value if to_value else 'Não atribuído',
                        'autor': author_name,
                        'tipo': 'qa_atribuicao',
                        'campo': 'QA Responsável',
                        'detalhes': f"QA: {from_value or 'Ninguém'} → {to_value or 'Ninguém'}",
                        'icone': gerar_icone_tabler('test-pipe', tamanho=32, cor='#8b5cf6'),
                        'cor': '#8b5cf6'
                    })
                
                elif field.lower() == 'sprint':
                    historico.append({
                        'data': entry_date,
                        'de': from_value if from_value else 'Sem sprint',
                        'para': to_value if to_value else 'Removido da sprint',
                        'autor': author_name,
                        'tipo': 'sprint',
                        'campo': 'Sprint',
                        'detalhes': f"Sprint: {from_value or 'Nenhuma'} → {to_value or 'Removido'}",
                        'icone': gerar_icone_tabler('target', tamanho=32, cor='#f59e0b'),
                        'cor': '#f59e0b'
                    })
                
                elif 'story point' in field.lower() or field == CUSTOM_FIELDS.get('story_points', ''):
                    historico.append({
                        'data': entry_date,
                        'de': from_value if from_value else '0',
                        'para': to_value if to_value else '0',
                        'autor': author_name,
                        'tipo': 'estimativa',
                        'campo': 'Story Points',
                        'detalhes': f"SP: {from_value or '0'} → {to_value or '0'}",
                        'icone': gerar_icone_tabler('chart-bar', tamanho=32, cor='#3b82f6'),
                        'cor': '#3b82f6'
                    })
                
                elif 'bug' in field.lower() or field == CUSTOM_FIELDS.get('bugs_encontrados', ''):
                    historico.append({
                        'data': entry_date,
                        'de': from_value if from_value else '0',
                        'para': to_value if to_value else '0',
                        'autor': author_name,
                        'tipo': 'bugs',
                        'campo': 'Bugs Encontrados',
                        'detalhes': f"Bugs: {from_value or '0'} → {to_value or '0'}",
                        'icone': gerar_icone_tabler('bug', tamanho=32, cor='#ef4444'),
                        'cor': '#ef4444'
                    })
                
                elif field.lower() == 'resolution':
                    cor_resolucao = '#22c55e' if to_value else '#f97316'
                    historico.append({
                        'data': entry_date,
                        'de': from_value if from_value else 'Sem resolução',
                        'para': to_value if to_value else 'Reaberto',
                        'autor': author_name,
                        'tipo': 'resolucao',
                        'campo': 'Resolução',
                        'detalhes': f"Resolução: {to_value or 'Reaberto'}",
                        'icone': gerar_icone_tabler('shield-check', tamanho=32, cor=cor_resolucao) if to_value else gerar_icone_tabler('loader', tamanho=32, cor=cor_resolucao),
                        'cor': cor_resolucao
                    })
        
        # 3. Ordena por data
        historico.sort(key=lambda x: x['data'])
        
        # 4. Calcula tempo em cada status
        for i, evento in enumerate(historico):
            if i < len(historico) - 1:
                proximo = historico[i + 1]
                delta = proximo['data'] - evento['data']
                evento['duracao_dias'] = delta.days
                evento['duracao_horas'] = int(delta.total_seconds() / 3600)
            else:
                # Último evento - calcula até agora
                delta = datetime.now() - evento['data']
                evento['duracao_dias'] = delta.days
                evento['duracao_horas'] = int(delta.total_seconds() / 3600)
        
        return historico
    
    except Exception as e:
        # Em caso de erro, retorna lista vazia
        return []


def gerar_icone_tabler(nome_icone: str, tamanho: int = 24, cor: str = "currentColor", stroke_width: float = 2) -> str:
    """
    Gera ícone Tabler Icons em formato SVG inline.
    
    Ícones disponíveis:
    - list, clipboard, code, check, x, loader, alert-circle, clock, search,
      user, users, settings, layout, grid, bar-chart, line-chart, trending-up,
      trending-down, inbox, archive, trash, edit, plus, minus, folder, file,
      database, server, wifi, wifi-off, eye, eye-off, lock, unlock, download,
      upload, share, link, bookmark, star, heart, message, send, phone, mail
    
    Args:
        nome_icone: Nome do ícone Tabler
        tamanho: Tamanho em pixels
        cor: Cor do ícone (hex ou CSS color)
        stroke_width: Largura do traço
    """
    
    # Biblioteca de ícones Tabler em SVG (simplificados)
    icones = {
        # Status e estados
        'list': '<path d="M9 6h11M9 12h11M9 18h11M5 6v.01M5 12v.01M5 18v.01"/>',
        'check': '<path d="M5 12l4 4l6 -6"/>',
        'x': '<path d="M18 6l-12 12M6 6l12 12"/>',
        'circle-check': '<circle cx="12" cy="12" r="9"/><path d="M9 12l2 2l4 -4"/>',
        'circle-x': '<circle cx="12" cy="12" r="9"/><path d="M15 9l-6 6M9 9l6 6"/>',
        'loader': '<path d="M12 3v6m4.22 -1.22l-4.24 4.24M21 12h-6m1.22 4.22l-4.24 -4.24M12 21v-6M4.22 16.22l4.24 -4.24M3 12h6M7.22 7.22l4.24 4.24"/>',
        'alert-circle': '<circle cx="12" cy="12" r="9"/><path d="M12 8v4M12 16v.01"/>',
        'clock': '<circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 16 14"/>',
        
        # Pessoas e atribuição
        'user': '<path d="M8 7a4 4 0 1 0 8 0a4 4 0 0 0 -8 0M6 21v-2a4 4 0 0 1 4 -4h4a4 4 0 0 1 4 4v2"/>',
        'users': '<path d="M9 7a4 4 0 1 0 8 0a4 4 0 0 0 -8 0M3 21v-2a4 4 0 0 1 4 -4h4a4 4 0 0 1 4 4v2M15 16a4 4 0 0 1 4 -4h2a4 4 0 0 1 4 4v2"/>',
        'user-check': '<path d="M8 7a4 4 0 1 0 8 0a4 4 0 0 0 -8 0M6 21v-2a4 4 0 0 1 4 -4h4a4 4 0 0 1 4 4v2m1 -8l4 4l4 -4"/>',
        
        # Desenvolvimento e técnico
        'code': '<polyline points="7 8 3 12 7 16M17 8 21 12 17 16M14 4 10 20"/>',
        'git-branch': '<line x1="12" y1="5" x2="12" y2="19M7 12a5 5 0 0 0 5 5 5 5 0 0 0 5 -5"/>',
        'database': '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14a8 3 0 0 0 8 3a8 3 0 0 0 8 -3V5M4 12a8 3 0 0 0 8 3 8 3 0 0 0 8 -3"/>',
        
        # Projeto e sprint
        'rocket': '<path d="M4 13c.755 -1.478 2.559 -2.427 4.5 -2.427c2.3 0 4.322 1.453 5.186 3.427c.863 -1.974 2.886 -3.427 5.314 -3.427c1.941 0 3.745 .949 4.5 2.427M7 19c-.577 .962 -1.607 1.6 -2.8 1.6c-1.8 0 -3.2 -1.2 -3.2 -2.8s1.4 -2.8 3.2 -2.8c1.193 0 2.223 .638 2.8 1.6M17 19c.577 .962 1.607 1.6 2.8 1.6c1.8 0 3.2 -1.2 3.2 -2.8s-1.4 -2.8 -3.2 -2.8c-1.193 0 -2.223 .638 -2.8 1.6"/>',
        'target': '<circle cx="12" cy="12" r="1"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="9"/>',
        'trending-up': '<polyline points="3 17 9 11 13 15 21 7M15 7h6v6"/>',
        'trending-down': '<polyline points="3 7 9 13 13 9 21 17M15 17h6v-6"/>',
        
        # Qualidade e testes
        'bug': '<path d="M9 9v-1a3 3 0 0 1 6 0v1M3 11a6 6 0 0 0 6 6h6a6 6 0 0 0 6 -6v-7a1 1 0 0 0 -1 -1h-16a1 1 0 0 0 -1 1v7M9 17v3M15 17v3"/>',
        'shield-check': '<path d="M12 3l8 4.5v5.5a9 9 0 0 1 -8 9a9 9 0 0 1 -8 -9v-5.5L12 3M9 12l2 2l4 -4"/>',
        'test-pipe': '<path d="M8 5h10M8 5v12a2 2 0 0 0 2 2h4a2 2 0 0 0 2 -2V5M9 9h6M9 13h6M7 18h10"/>',
        
        # Gráficos e dados
        'chart-bar': '<rect x="3" y="3" width="7" height="7M14 3v7M3 17h7M14 14v7M3 14h18"/>',
        'chart-line': '<path d="M3 13a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5 -.5v-3a.5.5 0 0 1 .5 -.5h2a.5.5 0 0 1 .5.5v5a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5 -.5v-4"/>',
        'graph': '<path d="M3 13a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5 -.5v-3a.5.5 0 0 1 .5 -.5h2a.5.5 0 0 1 .5.5v5a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5 -.5v-4"/>',
        
        # UI
        'settings': '<path d="M12 1v6m6 -3l-4.24 4.24M12 23v-6m6 3l-4.24 -4.24M1 12h6m-3 -6l4.24 4.24M23 12h-6m3 6l-4.24 -4.24M5.64 5.64l-4.24 -4.24M18.36 18.36l4.24 4.24"/>',
        'calendar': '<rect x="4" y="5" width="16" height="16" rx="2"/><line x1="16" y1="3" x2="16" y2="7M8 3v4M4 11h16"/>',
        'filter': '<polyline points="4 4 10 14 10 20 14 22 14 14 20 4"/>',
        'search': '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
        
        # Arquivo
        'file': '<path d="M14 2H6a2 2 0 0 0 -2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2 -2V8z"/><polyline points="14 2 14 8 20 8"/>',
        'folder': '<path d="M5 4a1 1 0 0 0 -1 1v14a1 1 0 0 0 1 1h14a1 1 0 0 0 1 -1V7a1 1 0 0 0 -1 -1h-10a1 1 0 0 1 -1 -1H5z"/>',
        'download': '<path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2 -2v-2M7 11l5 5l5 -5M12 3v13"/>',
        'upload': '<path d="M21 14v5a2 2 0 0 1 -2 2H5a2 2 0 0 1 -2 -2v-5M17 8l-5 -5l-5 5M12 3v13"/>',
        
        # Comunicação
        'message': '<path d="M3 20l1.3 -3.9c-1 -1.5 -1.3 -3.4 -1.3 -5.1 0 -5.5 4.5 -10 10 -10s10 4.5 10 10 -4.5 10 -10 10c-1.7 0 -3.6 -.3 -5.1 -1.3L3 20"/>',
        'send': '<line x1="10" y1="14" x2="21" y2="3M21 3l-6.5 18.75a.55.55 0 0 1 -1 0l-3.5 -7l-7 -3.5a.55.55 0 0 1 0 -1L21 3"/>',
        'bell': '<path d="M9 4H5a2 2 0 0 0 -2 2v12a2 2 0 0 0 2 2h14a2 2 0 0 0 2 -2V6a2 2 0 0 0 -2 -2h-4M9 9h6M9 13h6"/>',
        
        # Ações
        'edit': '<path d="M7 7H6a2 2 0 0 0 -2 2v9a2 2 0 0 0 2 2h9a2 2 0 0 0 2 -2v-1M20.385 6.585a2.1 2.1 0 0 0 -2.97 -2.97L9 12v3h3L20.385 6.585z"/><path d="M16 5l3 3"/>',
        'trash': '<polyline points="3 6 5 6 21 6M8 6v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2 -2V6m-4 0V4a2 2 0 0 0 -2 -2h-4a2 2 0 0 0 -2 2v2M10 11v6M14 11v6"/>',
        'plus': '<line x1="12" y1="5" x2="12" y2="19M5 12h14"/>',
        'minus': '<line x1="5" y1="12" x2="19" y2="12"/>',
        'eye': '<circle cx="12" cy="12" r="1"/><path d="M12 5C7 5 2.73 7.61 1 11.35C2.73 15.39 7 18 12 18s9.27 -2.61 11 -6.65C21.27 7.61 17 5 12 5"/>',
        'eye-off': '<path d="M1 12s4 -6 11 -6 11 6 11 6M3.6 3.6l16.8 16.8M21 12s-4 6 -11 6 -11 -6 -11 -6"/>',
    }
    
    svg_path = icones.get(nome_icone, icones['list'])  # Default para 'list' se não encontrado
    
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{tamanho}" height="{tamanho}" viewBox="0 0 24 24" fill="none" stroke="{cor}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" style="display:inline-block; vertical-align:middle;">{svg_path}</svg>'


def gerar_icone_tabler_html(nome_icone: str, tamanho: int = 20, cor: str = "#64748b", stroke_width: float = 2) -> str:
    """
    Versão otimizada de gerar_icone_tabler para usar em strings HTML (sem quebras de linha).
    Retorna SVG inline em uma única linha.
    """
    # Biblioteca de ícones Tabler em SVG (simplificados)
    icones = {
        'list': '<path d="M9 6h11M9 12h11M9 18h11M5 6v.01M5 12v.01M5 18v.01"/>',
        'check': '<path d="M5 12l4 4l6 -6"/>',
        'x': '<path d="M18 6l-12 12M6 6l12 12"/>',
        'circle-check': '<circle cx="12" cy="12" r="9"/><path d="M9 12l2 2l4 -4"/>',
        'circle-x': '<circle cx="12" cy="12" r="9"/><path d="M15 9l-6 6M9 9l6 6"/>',
        'bug': '<path d="M9 9v-1a3 3 0 0 1 6 0v1M3 11a6 6 0 0 0 6 6h6a6 6 0 0 0 6 -6v-7a1 1 0 0 0 -1 -1h-16a1 1 0 0 0 -1 1v7M9 17v3M15 17v3"/>',
        'shield-check': '<path d="M12 3l8 4.5v5.5a9 9 0 0 1 -8 9a9 9 0 0 1 -8 -9v-5.5L12 3M9 12l2 2l4 -4"/>',
        'alert-circle': '<circle cx="12" cy="12" r="9"/><path d="M12 8v4M12 16v.01"/>',
    }
    
    svg_path = icones.get(nome_icone, icones['list'])
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{tamanho}" height="{tamanho}" viewBox="0 0 24 24" fill="none" stroke="{cor}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" style="display:inline-block;vertical-align:middle;margin-right:5px;">{svg_path}</svg>'


def gerar_badge_status(status: str, icone_nome: str = None, tamanho_icone: int = 16) -> str:
    """
    Gera um badge HTML com status e ícone Tabler.
    
    Args:
        status: Texto do status
        icone_nome: Nome do ícone Tabler (se None, escolhe baseado no status)
        tamanho_icone: Tamanho do ícone em pixels
    
    Returns:
        String HTML do badge
    """
    # Mapeamento padrão de status para cores e ícones
    mapeamento = {
        'concluído': ('#22c55e', 'circle-check'),
        'done': ('#22c55e', 'circle-check'),
        'reprovado': ('#dc2626', 'circle-x'),
        'rejected': ('#dc2626', 'circle-x'),
        'desenvolvimento': ('#3b82f6', 'code'),
        'development': ('#3b82f6', 'code'),
        'validação': ('#06b6d4', 'shield-check'),
        'qa': ('#06b6d4', 'shield-check'),
        'backlog': ('#64748b', 'list'),
        'warning': ('#f59e0b', 'alert-circle'),
    }
    
    status_lower = status.lower()
    cor = '#64748b'
    icone = 'list'
    
    # Encontra mapeamento baseado no status
    for chave, (cor_encontrada, icone_encontrado) in mapeamento.items():
        if chave in status_lower:
            cor = cor_encontrada
            icone = icone_encontrado
            break
    
    # Sobrescreve se ícone foi especificado
    if icone_nome:
        icone = icone_nome
    
    icon_svg = gerar_icone_tabler_html(icone, tamanho=tamanho_icone, cor=cor)
    
    return f'<span style="display:inline-flex;align-items:center;background:{cor}20;color:{cor};padding:4px 10px;border-radius:8px;font-size:12px;font-weight:600;">{icon_svg}{status}</span>'


def obter_icone_evento(tipo_evento: str, status: str = "") -> Tuple[str, str]:
    """
    Retorna ícone Tabler Icons e cor baseado no tipo de evento.
    
    Args:
        tipo_evento: Type of event ('criacao', 'transicao', 'atribuicao', etc.)
        status: Status value para transições (usado para cores mais precisas)
    
    Returns:
        Tuple[str, str]: (SVG inline, cor_hex)
    """
    mapeamento = {
        'criacao': (gerar_icone_tabler('file', tamanho=32, cor='#22c55e'), '#22c55e'),
        'transicao': (gerar_icone_tabler('git-branch', tamanho=32, cor='#3b82f6'), '#3b82f6'),
        'atribuicao': (gerar_icone_tabler('user-check', tamanho=32, cor='#6366f1'), '#6366f1'),
        'qa_atribuicao': (gerar_icone_tabler('test-pipe', tamanho=32, cor='#8b5cf6'), '#8b5cf6'),
        'sprint': (gerar_icone_tabler('target', tamanho=32, cor='#f59e0b'), '#f59e0b'),
        'estimativa': (gerar_icone_tabler('chart-bar', tamanho=32, cor='#3b82f6'), '#3b82f6'),
        'bugs': (gerar_icone_tabler('bug', tamanho=32, cor='#ef4444'), '#ef4444'),
        'resolucao': (gerar_icone_tabler('shield-check', tamanho=32, cor='#22c55e'), '#22c55e'),
    }
    
    # Se houver status, usa obter_icone_status para transições
    if tipo_evento == 'transicao' and status:
        return obter_icone_status(status)
    
    # Retorna mapeamento padrão ou padrão
    return mapeamento.get(tipo_evento, (gerar_icone_tabler('list', tamanho=32, cor='#9ca3af'), '#9ca3af'))


def obter_icone_status(status: str) -> Tuple[str, str]:
    """Retorna ícone Tabler Icons e cor baseado no nome do status."""
    status_lower = status.lower() if status else ''
    
    # Mapeamento de status para ícones Tabler e cores
    if any(x in status_lower for x in ['backlog', 'to do', 'pendente', 'aberto']):
        return gerar_icone_tabler('list', tamanho=32, cor='#64748b'), '#64748b'
    elif any(x in status_lower for x in ['andamento', 'development', 'desenvolviment', 'em progresso']):
        return gerar_icone_tabler('code', tamanho=32, cor='#3b82f6'), '#3b82f6'
    elif any(x in status_lower for x in ['revisão', 'review', 'code review']):
        return gerar_icone_tabler('git-branch', tamanho=32, cor='#8b5cf6'), '#8b5cf6'
    elif any(x in status_lower for x in ['aguardando validação', 'waiting', 'aguardando qa']):
        return gerar_icone_tabler('clock', tamanho=32, cor='#f59e0b'), '#f59e0b'
    elif any(x in status_lower for x in ['validação', 'em validação', 'testing', 'qa']):
        return gerar_icone_tabler('test-pipe', tamanho=32, cor='#06b6d4'), '#06b6d4'
    elif any(x in status_lower for x in ['concluído', 'done', 'finalizado', 'resolvido']):
        return gerar_icone_tabler('circle-check', tamanho=32, cor='#22c55e'), '#22c55e'
    elif any(x in status_lower for x in ['bloqueado', 'blocked', 'impedido']):
        return gerar_icone_tabler('alert-circle', tamanho=32, cor='#ef4444'), '#ef4444'
    elif any(x in status_lower for x in ['reprovado', 'rejected', 'recusado']):
        return gerar_icone_tabler('circle-x', tamanho=32, cor='#dc2626'), '#dc2626'
    elif any(x in status_lower for x in ['adiado', 'deferred', 'descartado']):
        return gerar_icone_tabler('calendar', tamanho=32, cor='#6b7280'), '#6b7280'
    else:
        return gerar_icone_tabler('list', tamanho=32, cor='#9ca3af'), '#9ca3af'


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
    
    # Relator (reporter) - quem criou/solicitou o item
    relator = f.get('reporter', {}).get('displayName', 'Não informado') if f.get('reporter') else 'Não informado'
    
    # Resolução/Roteiro - indica decisão sobre o item (ex: "Vai ser feito", "Aguardando retorno")
    resolution = f.get('resolution', {})
    resolucao = resolution.get('name', '') if resolution else ''
    
    # Story Points
    sp = f.get(CUSTOM_FIELDS['story_points']) or f.get(CUSTOM_FIELDS['story_points_alt']) or 0
    sp_original = bool(f.get(CUSTOM_FIELDS['story_points']) or f.get(CUSTOM_FIELDS['story_points_alt']))
    sp_estimado = False  # Flag para indicar se SP foi estimado pela regra de Hotfix
    if sp == 0 and tipo == "HOTFIX":
        sp = REGRAS["hotfix_sp_default"]
        sp_estimado = True  # SP calculado automaticamente
    
    # Sprint - CORRIGIDO: pegar sprint ATIVA, não a última da lista
    sprint_f = f.get(CUSTOM_FIELDS['sprint'], [])
    
    # Encontra a sprint ativa (state == 'active') ou a mais recente
    sprint_atual = None
    if sprint_f:
        # Primeiro tenta encontrar a sprint ativa
        for s in sprint_f:
            if s.get('state') == 'active':
                sprint_atual = s
                break
        # Se não encontrou ativa, pega a mais recente por endDate
        if not sprint_atual:
            sprint_atual = sprint_f[-1]
    
    sprint = sprint_atual.get('name', 'Sem Sprint') if sprint_atual else 'Sem Sprint'
    sprint_end = None
    sprint_state = sprint_atual.get('state', '') if sprint_atual else ''
    if sprint_atual:
        sprint_end_str = sprint_atual.get('endDate')
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
    
    # ===== CAMPOS EXTRAS PARA PRODUTO (PB) =====
    # Descrição
    descricao = f.get('description', '') or ''
    if isinstance(descricao, dict):
        # Jira Cloud pode retornar ADF (Atlassian Document Format)
        try:
            # Tenta extrair texto do ADF
            content = descricao.get('content', [])
            partes = []
            for item in content:
                if item.get('type') == 'paragraph':
                    for text_item in item.get('content', []):
                        if text_item.get('type') == 'text':
                            partes.append(text_item.get('text', ''))
            descricao = ' '.join(partes)
        except:
            descricao = ''
    
    # Labels
    labels = f.get('labels', []) or []
    
    # Componentes
    componentes_raw = f.get('components', []) or []
    componentes = [c.get('name', '') for c in componentes_raw] if componentes_raw else []
    
    # Epic Link / Parent
    epic_link = ''
    parent = f.get('parent', {})
    if parent:
        epic_link = parent.get('key', '')
    
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
        'relator': relator,
        'resolucao': resolucao,
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
        # Campos extras para Produto (PB)
        'descricao': descricao,
        'labels': labels,
        'componentes': componentes,
        'epic_link': epic_link,
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
        
        # Relator (reporter) - quem criou o card
        relator = f.get('reporter', {}).get('displayName', 'Não informado') if f.get('reporter') else 'Não informado'
        
        # Story Points - com regra de Hotfix
        sp = f.get(CUSTOM_FIELDS['story_points']) or f.get(CUSTOM_FIELDS['story_points_alt']) or 0
        sp_original = bool(f.get(CUSTOM_FIELDS['story_points']) or f.get(CUSTOM_FIELDS['story_points_alt']))
        if sp == 0 and tipo == "HOTFIX":
            sp = REGRAS["hotfix_sp_default"]
        
        # Sprint - CORRIGIDO: pegar sprint ATIVA, não a última da lista
        sprint_f = f.get(CUSTOM_FIELDS['sprint'], [])
        
        # Encontra a sprint ativa (state == 'active') ou a mais recente
        sprint_atual = None
        if sprint_f:
            # Primeiro tenta encontrar a sprint ativa
            for s in sprint_f:
                if s.get('state') == 'active':
                    sprint_atual = s
                    break
            # Se não encontrou ativa, pega a mais recente por endDate
            if not sprint_atual:
                sprint_atual = sprint_f[-1]
        
        sprint = sprint_atual.get('name', 'Sem Sprint') if sprint_atual else 'Sem Sprint'
        sprint_id = sprint_atual.get('id') if sprint_atual else None
        sprint_state = sprint_atual.get('state', '') if sprint_atual else ''
        sprint_start = None
        sprint_end = None
        if sprint_atual:
            sprint_start_str = sprint_atual.get('startDate')
            sprint_end_str = sprint_atual.get('endDate')
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
        
        # ===== NOVOS CAMPOS ELLEN =====
        # Temas/Clientes (multi-value)
        temas_f = f.get(CUSTOM_FIELDS['temas'], [])
        temas = temas_f if isinstance(temas_f, list) else []
        tema_principal = temas[0] if temas else 'Sem tema'
        
        # Importância (Alto/Médio/Baixo)
        importancia_f = f.get(CUSTOM_FIELDS['importancia'])
        importancia = importancia_f.get('value', 'Não definido') if isinstance(importancia_f, dict) else 'Não definido'
        
        # SLA Status (Atrasado ou null)
        sla_f = f.get(CUSTOM_FIELDS['sla_status'])
        sla_status = sla_f.get('value', '') if isinstance(sla_f, dict) else ''
        sla_atrasado = sla_status == 'Atrasado'
        
        # Issue Links - detectar origem do PB
        issuelinks = f.get('issuelinks', [])
        origem_pb = None
        tem_link_pb = False
        for link in issuelinks:
            # Link para card do PB (outward = implements)
            outward = link.get('outwardIssue', {})
            if outward.get('key', '').startswith('PB-'):
                origem_pb = outward.get('key')
                tem_link_pb = True
                break
            # Link reverso (inward = is implemented by)
            inward = link.get('inwardIssue', {})
            if inward.get('key', '').startswith('PB-'):
                origem_pb = inward.get('key')
                tem_link_pb = True
                break
        
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
            'relator': relator,
            'qa': qa,
            'sp': int(sp) if sp else 0,
            'sp_original': sp_original,
            'bugs': int(bugs) if bugs else 0,
            'sprint': sprint,
            'sprint_id': sprint_id,
            'sprint_state': sprint_state,  # 'active', 'closed', 'future'
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
            # Campos Ellen - Análise de Sprint e PB
            'temas': temas,
            'tema_principal': tema_principal,
            'importancia': importancia,
            'sla_status': sla_status,
            'sla_atrasado': sla_atrasado,
            'origem_pb': origem_pb,
            'tem_link_pb': tem_link_pb,
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


# ==============================================================================
# ANÁLISE DE CONCENTRAÇÃO DE CONHECIMENTO (RODÍZIO)
# ==============================================================================

def filtrar_qas_principais(df: pd.DataFrame, min_cards: int = 5) -> List[str]:
    """
    Retorna lista dos QAs principais (que mais validaram cards).
    Filtra pessoas que eventualmente validam mas não são QAs do time.
    
    Args:
        df: DataFrame com os cards
        min_cards: Mínimo de cards para ser considerado QA principal
    
    Returns:
        Lista de nomes dos QAs principais
    """
    if df.empty:
        return []
    
    # Conta cards por QA
    qa_counts = df[df['qa'] != 'Não atribuído'].groupby('qa').size().reset_index(name='total_cards')
    
    # Filtra apenas QAs com quantidade significativa de cards
    qas_principais = qa_counts[qa_counts['total_cards'] >= min_cards]['qa'].tolist()
    
    return qas_principais


def calcular_concentracao_conhecimento(df: pd.DataFrame) -> Dict:
    """
    Calcula métricas de concentração de conhecimento por DEV e QA,
    segmentado por Produto e Cliente.
    
    Retorna:
        Dict com matrizes de concentração, índices e alertas
    """
    if df.empty:
        return {
            "dev_produto": pd.DataFrame(),
            "qa_produto": pd.DataFrame(),
            "dev_cliente": pd.DataFrame(),
            "qa_cliente": pd.DataFrame(),
            "alertas_dev": [],
            "alertas_qa": [],
            "recomendacoes": [],
            "indices": {},
            "qas_principais": [],
        }
    
    # Filtra QAs principais
    qas_principais = filtrar_qas_principais(df)
    
    # Cria cópia para manipulação
    df_analise = df.copy()
    
    # Extrai cliente do campo tema_principal (filtra temas internos)
    def extrair_cliente(tema):
        if not tema or tema == 'Sem tema':
            return 'Sem cliente'
        tema_lower = tema.lower().strip()
        for interno in TEMAS_NAO_CLIENTES:
            if interno.lower() in tema_lower:
                return 'Interno/Plataforma'
        return tema
    
    df_analise['cliente'] = df_analise['tema_principal'].apply(extrair_cliente)
    
    # ==================== MATRIZ DEV x PRODUTO ====================
    dev_produto = df_analise[df_analise['desenvolvedor'] != 'Não atribuído'].groupby(
        ['desenvolvedor', 'produto']
    ).agg({
        'ticket_id': 'count',
        'sp': 'sum',
        'bugs': 'sum'
    }).reset_index()
    dev_produto.columns = ['DEV', 'Produto', 'Cards', 'SP', 'Bugs']
    
    # Pivot para matriz
    matriz_dev_produto = dev_produto.pivot_table(
        index='DEV', 
        columns='Produto', 
        values='Cards', 
        fill_value=0,
        aggfunc='sum'
    )
    
    # ==================== MATRIZ QA x PRODUTO ====================
    # Filtra apenas QAs principais
    df_qa = df_analise[(df_analise['qa'].isin(qas_principais)) & (df_analise['qa'] != 'Não atribuído')]
    
    qa_produto = df_qa.groupby(['qa', 'produto']).agg({
        'ticket_id': 'count',
        'sp': 'sum',
        'bugs': 'sum'
    }).reset_index()
    qa_produto.columns = ['QA', 'Produto', 'Cards', 'SP', 'Bugs']
    
    matriz_qa_produto = qa_produto.pivot_table(
        index='QA', 
        columns='Produto', 
        values='Cards', 
        fill_value=0,
        aggfunc='sum'
    ) if not qa_produto.empty else pd.DataFrame()
    
    # ==================== MATRIZ DEV x CLIENTE ====================
    dev_cliente = df_analise[df_analise['desenvolvedor'] != 'Não atribuído'].groupby(
        ['desenvolvedor', 'cliente']
    ).agg({
        'ticket_id': 'count',
        'sp': 'sum',
        'bugs': 'sum'
    }).reset_index()
    dev_cliente.columns = ['DEV', 'Cliente', 'Cards', 'SP', 'Bugs']
    
    matriz_dev_cliente = dev_cliente.pivot_table(
        index='DEV', 
        columns='Cliente', 
        values='Cards', 
        fill_value=0,
        aggfunc='sum'
    )
    
    # ==================== MATRIZ QA x CLIENTE ====================
    qa_cliente = df_qa.groupby(['qa', 'cliente']).agg({
        'ticket_id': 'count',
        'sp': 'sum',
        'bugs': 'sum'
    }).reset_index()
    qa_cliente.columns = ['QA', 'Cliente', 'Cards', 'SP', 'Bugs']
    
    matriz_qa_cliente = qa_cliente.pivot_table(
        index='QA', 
        columns='Cliente', 
        values='Cards', 
        fill_value=0,
        aggfunc='sum'
    ) if not qa_cliente.empty else pd.DataFrame()
    
    # ==================== CÁLCULO DE ÍNDICES ====================
    alertas_dev = []
    alertas_qa = []
    indices = {
        "dev_produto": {},
        "qa_produto": {},
        "dev_cliente": {},
        "qa_cliente": {},
    }
    
    # Análise de concentração DEV x Produto
    for produto in matriz_dev_produto.columns:
        col = matriz_dev_produto[produto]
        total = col.sum()
        if total > 0:
            max_val = col.max()
            max_dev = col.idxmax()
            concentracao = (max_val / total) * 100
            
            indices["dev_produto"][produto] = {
                "top_pessoa": max_dev,
                "top_cards": int(max_val),
                "total_cards": int(total),
                "concentracao_pct": round(concentracao, 1),
                "pessoas_atuando": int((col > 0).sum()),
            }
            
            # Alertas
            if concentracao >= 80:
                alertas_dev.append({
                    "tipo": "critico",
                    "contexto": "produto",
                    "nome": produto,
                    "pessoa": max_dev,
                    "pct": round(concentracao, 1),
                    "msg": f"🔴 CRÍTICO: {max_dev} desenvolveu {concentracao:.0f}% dos cards do produto '{produto}'"
                })
            elif concentracao >= 60:
                alertas_dev.append({
                    "tipo": "atencao",
                    "contexto": "produto",
                    "nome": produto,
                    "pessoa": max_dev,
                    "pct": round(concentracao, 1),
                    "msg": f"🟡 ATENÇÃO: {max_dev} desenvolveu {concentracao:.0f}% dos cards do produto '{produto}'"
                })
    
    # Análise de concentração QA x Produto
    if not matriz_qa_produto.empty:
        for produto in matriz_qa_produto.columns:
            col = matriz_qa_produto[produto]
            total = col.sum()
            if total > 0:
                max_val = col.max()
                max_qa = col.idxmax()
                concentracao = (max_val / total) * 100
                
                indices["qa_produto"][produto] = {
                    "top_pessoa": max_qa,
                    "top_cards": int(max_val),
                    "total_cards": int(total),
                    "concentracao_pct": round(concentracao, 1),
                    "pessoas_atuando": int((col > 0).sum()),
                }
                
                if concentracao >= 80:
                    alertas_qa.append({
                        "tipo": "critico",
                        "contexto": "produto",
                        "nome": produto,
                        "pessoa": max_qa,
                        "pct": round(concentracao, 1),
                        "msg": f"🔴 CRÍTICO: {max_qa} validou {concentracao:.0f}% dos cards do produto '{produto}'"
                    })
                elif concentracao >= 60:
                    alertas_qa.append({
                        "tipo": "atencao",
                        "contexto": "produto",
                        "nome": produto,
                        "pessoa": max_qa,
                        "pct": round(concentracao, 1),
                        "msg": f"🟡 ATENÇÃO: {max_qa} validou {concentracao:.0f}% dos cards do produto '{produto}'"
                    })
    
    # Análise de concentração DEV x Cliente
    for cliente in matriz_dev_cliente.columns:
        if cliente in ['Sem cliente', 'Interno/Plataforma']:
            continue
        col = matriz_dev_cliente[cliente]
        total = col.sum()
        if total >= 3:  # Só analisa clientes com pelo menos 3 cards
            max_val = col.max()
            max_dev = col.idxmax()
            concentracao = (max_val / total) * 100
            
            indices["dev_cliente"][cliente] = {
                "top_pessoa": max_dev,
                "top_cards": int(max_val),
                "total_cards": int(total),
                "concentracao_pct": round(concentracao, 1),
                "pessoas_atuando": int((col > 0).sum()),
            }
            
            if concentracao >= 80:
                alertas_dev.append({
                    "tipo": "critico",
                    "contexto": "cliente",
                    "nome": cliente,
                    "pessoa": max_dev,
                    "pct": round(concentracao, 1),
                    "msg": f"🔴 CRÍTICO: {max_dev} desenvolveu {concentracao:.0f}% dos cards do cliente '{cliente}'"
                })
            elif concentracao >= 60:
                alertas_dev.append({
                    "tipo": "atencao",
                    "contexto": "cliente",
                    "nome": cliente,
                    "pessoa": max_dev,
                    "pct": round(concentracao, 1),
                    "msg": f"🟡 ATENÇÃO: {max_dev} desenvolveu {concentracao:.0f}% dos cards do cliente '{cliente}'"
                })
    
    # Análise de concentração QA x Cliente
    if not matriz_qa_cliente.empty:
        for cliente in matriz_qa_cliente.columns:
            if cliente in ['Sem cliente', 'Interno/Plataforma']:
                continue
            col = matriz_qa_cliente[cliente]
            total = col.sum()
            if total >= 3:
                max_val = col.max()
                max_qa = col.idxmax()
                concentracao = (max_val / total) * 100
                
                indices["qa_cliente"][cliente] = {
                    "top_pessoa": max_qa,
                    "top_cards": int(max_val),
                    "total_cards": int(total),
                    "concentracao_pct": round(concentracao, 1),
                    "pessoas_atuando": int((col > 0).sum()),
                }
                
                if concentracao >= 80:
                    alertas_qa.append({
                        "tipo": "critico",
                        "contexto": "cliente",
                        "nome": cliente,
                        "pessoa": max_qa,
                        "pct": round(concentracao, 1),
                        "msg": f"🔴 CRÍTICO: {max_qa} validou {concentracao:.0f}% dos cards do cliente '{cliente}'"
                    })
                elif concentracao >= 60:
                    alertas_qa.append({
                        "tipo": "atencao",
                        "contexto": "cliente",
                        "nome": cliente,
                        "pessoa": max_qa,
                        "pct": round(concentracao, 1),
                        "msg": f"🟡 ATENÇÃO: {max_qa} validou {concentracao:.0f}% dos cards do cliente '{cliente}'"
                    })
    
    # ==================== RECOMENDAÇÕES DE RODÍZIO ====================
    recomendacoes = gerar_recomendacoes_rodizio(
        matriz_dev_produto, matriz_qa_produto,
        matriz_dev_cliente, matriz_qa_cliente,
        alertas_dev, alertas_qa
    )
    
    return {
        "dev_produto": dev_produto,
        "qa_produto": qa_produto,
        "dev_cliente": dev_cliente,
        "qa_cliente": qa_cliente,
        "matriz_dev_produto": matriz_dev_produto,
        "matriz_qa_produto": matriz_qa_produto,
        "matriz_dev_cliente": matriz_dev_cliente,
        "matriz_qa_cliente": matriz_qa_cliente,
        "alertas_dev": alertas_dev,
        "alertas_qa": alertas_qa,
        "recomendacoes": recomendacoes,
        "indices": indices,
        "qas_principais": qas_principais,
    }


def gerar_recomendacoes_rodizio(
    matriz_dev_produto: pd.DataFrame,
    matriz_qa_produto: pd.DataFrame,
    matriz_dev_cliente: pd.DataFrame,
    matriz_qa_cliente: pd.DataFrame,
    alertas_dev: List[Dict],
    alertas_qa: List[Dict]
) -> List[Dict]:
    """
    Gera recomendações automáticas de rodízio baseado nas concentrações detectadas.
    """
    recomendacoes = []
    
    # Para cada alerta crítico de DEV, sugere outros DEVs que poderiam assumir
    for alerta in alertas_dev:
        if alerta["tipo"] == "critico":
            contexto = alerta["contexto"]
            nome = alerta["nome"]
            pessoa_dominante = alerta["pessoa"]
            
            # Encontra outros DEVs que NÃO trabalharam nesse contexto
            if contexto == "produto" and not matriz_dev_produto.empty and nome in matriz_dev_produto.columns:
                col = matriz_dev_produto[nome]
                devs_sem_experiencia = col[col == 0].index.tolist()
                devs_pouca_experiencia = col[(col > 0) & (col < col.max() * 0.3)].index.tolist()
                
                sugestoes = devs_pouca_experiencia[:3] if devs_pouca_experiencia else devs_sem_experiencia[:3]
                
                if sugestoes:
                    recomendacoes.append({
                        "tipo": "rodizio_dev",
                        "contexto": contexto,
                        "nome": nome,
                        "pessoa_atual": pessoa_dominante,
                        "sugestoes": sugestoes,
                        "msg": f"🔄 **Rodízio sugerido para '{nome}':** Considere atribuir próximos cards a {', '.join(sugestoes)} para distribuir conhecimento"
                    })
            
            elif contexto == "cliente" and not matriz_dev_cliente.empty and nome in matriz_dev_cliente.columns:
                col = matriz_dev_cliente[nome]
                devs_sem_experiencia = col[col == 0].index.tolist()
                devs_pouca_experiencia = col[(col > 0) & (col < col.max() * 0.3)].index.tolist()
                
                sugestoes = devs_pouca_experiencia[:3] if devs_pouca_experiencia else devs_sem_experiencia[:3]
                
                if sugestoes:
                    recomendacoes.append({
                        "tipo": "rodizio_dev",
                        "contexto": contexto,
                        "nome": nome,
                        "pessoa_atual": pessoa_dominante,
                        "sugestoes": sugestoes,
                        "msg": f"🔄 **Rodízio sugerido para cliente '{nome}':** Considere atribuir próximos cards a {', '.join(sugestoes)}"
                    })
    
    # Para cada alerta crítico de QA, sugere outros QAs
    for alerta in alertas_qa:
        if alerta["tipo"] == "critico":
            contexto = alerta["contexto"]
            nome = alerta["nome"]
            pessoa_dominante = alerta["pessoa"]
            
            if contexto == "produto" and not matriz_qa_produto.empty and nome in matriz_qa_produto.columns:
                col = matriz_qa_produto[nome]
                qas_sem_experiencia = col[col == 0].index.tolist()
                qas_pouca_experiencia = col[(col > 0) & (col < col.max() * 0.3)].index.tolist()
                
                sugestoes = qas_pouca_experiencia[:2] if qas_pouca_experiencia else qas_sem_experiencia[:2]
                
                if sugestoes:
                    recomendacoes.append({
                        "tipo": "rodizio_qa",
                        "contexto": contexto,
                        "nome": nome,
                        "pessoa_atual": pessoa_dominante,
                        "sugestoes": sugestoes,
                        "msg": f"🔄 **Rodízio de QA para '{nome}':** Considere atribuir validações a {', '.join(sugestoes)}"
                    })
    
    # Recomendação geral se houver muitos alertas
    total_alertas = len([a for a in alertas_dev + alertas_qa if a["tipo"] == "critico"])
    if total_alertas >= 3:
        recomendacoes.insert(0, {
            "tipo": "geral",
            "msg": f"⚠️ **{total_alertas} áreas com concentração crítica detectadas.** Recomenda-se revisar a distribuição de trabalho na próxima sprint planning."
        })
    
    return recomendacoes


def criar_grafico_concentracao(matriz: pd.DataFrame, titulo: str, tipo: str = "dev") -> go.Figure:
    """Cria heatmap de concentração para visualização."""
    if matriz.empty:
        fig = go.Figure()
        fig.add_annotation(text="Sem dados suficientes", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    # Calcula percentuais
    matriz_pct = matriz.div(matriz.sum(axis=0), axis=1) * 100
    matriz_pct = matriz_pct.fillna(0)
    
    # Define escala de cores baseado no tipo
    colorscale = 'Blues' if tipo == "dev" else 'Purples'
    
    fig = go.Figure(data=go.Heatmap(
        z=matriz_pct.values,
        x=matriz_pct.columns.tolist(),
        y=matriz_pct.index.tolist(),
        colorscale=colorscale,
        text=matriz.values,  # Mostra valores absolutos
        texttemplate="%{text}",
        textfont={"size": 11},
        hovertemplate="<b>%{y}</b><br>%{x}: %{text} cards (%{z:.0f}%)<extra></extra>",
        colorbar=dict(title="%", ticksuffix="%")
    ))
    
    fig.update_layout(
        title=titulo,
        xaxis_title="",
        yaxis_title="",
        height=max(300, len(matriz) * 35 + 100),
        margin=dict(l=20, r=20, t=50, b=20),
    )
    
    return fig


def calcular_concentracao_pessoa(df: pd.DataFrame, pessoa: str, tipo: str = "dev") -> Dict:
    """
    Calcula a concentração de conhecimento de uma pessoa específica (DEV ou QA).
    Retorna um resumo simples com produtos e clientes onde a pessoa mais atua.
    
    Args:
        df: DataFrame com os cards
        pessoa: Nome da pessoa
        tipo: "dev" ou "qa"
    
    Returns:
        Dict com resumo de concentração da pessoa
    """
    if df.empty:
        return {"produtos": [], "clientes": [], "alertas": [], "total_cards": 0}
    
    # Filtra cards da pessoa
    coluna = 'desenvolvedor' if tipo == "dev" else 'qa'
    df_pessoa = df[df[coluna] == pessoa].copy()
    
    if df_pessoa.empty:
        return {"produtos": [], "clientes": [], "alertas": [], "total_cards": 0}
    
    total_cards = len(df_pessoa)
    
    # Extrai cliente do campo tema_principal
    def extrair_cliente(tema):
        if not tema or tema == 'Sem tema':
            return 'Sem cliente'
        tema_lower = tema.lower().strip()
        for interno in TEMAS_NAO_CLIENTES:
            if interno.lower() in tema_lower:
                return 'Interno/Plataforma'
        return tema
    
    df_pessoa['cliente'] = df_pessoa['tema_principal'].apply(extrair_cliente)
    
    # Agrupa por produto
    por_produto = df_pessoa.groupby('produto').agg({
        'ticket_id': 'count',
        'sp': 'sum'
    }).reset_index()
    por_produto.columns = ['nome', 'cards', 'sp']
    por_produto['pct'] = (por_produto['cards'] / total_cards * 100).round(1)
    por_produto = por_produto.sort_values('cards', ascending=False)
    
    # Agrupa por cliente
    por_cliente = df_pessoa.groupby('cliente').agg({
        'ticket_id': 'count',
        'sp': 'sum'
    }).reset_index()
    por_cliente.columns = ['nome', 'cards', 'sp']
    por_cliente['pct'] = (por_cliente['cards'] / total_cards * 100).round(1)
    por_cliente = por_cliente.sort_values('cards', ascending=False)
    
    # Identifica alertas (onde a pessoa é muito concentrada)
    alertas = []
    for _, row in por_produto.iterrows():
        if row['pct'] >= 60 and row['nome'] != 'Não definido':
            alertas.append({
                "tipo": "produto",
                "nome": row['nome'],
                "pct": row['pct'],
                "cards": row['cards']
            })
    
    for _, row in por_cliente.iterrows():
        if row['pct'] >= 60 and row['nome'] not in ['Sem cliente', 'Interno/Plataforma']:
            alertas.append({
                "tipo": "cliente",
                "nome": row['nome'],
                "pct": row['pct'],
                "cards": row['cards']
            })
    
    return {
        "produtos": por_produto.to_dict('records'),
        "clientes": por_cliente.to_dict('records'),
        "alertas": alertas,
        "total_cards": total_cards
    }


def exibir_concentracao_simplificada(df: pd.DataFrame, pessoa: str, tipo: str = "dev", expanded: bool = False):
    """
    Exibe um card simplificado com a concentração de conhecimento de uma pessoa.
    Para uso nas abas DEV e QA.
    
    Args:
        df: DataFrame com os cards
        pessoa: Nome da pessoa
        tipo: "dev" ou "qa"
        expanded: Se o expander deve estar aberto por padrão
    """
    concentracao = calcular_concentracao_pessoa(df, pessoa, tipo)
    
    if concentracao['total_cards'] == 0:
        return
    
    titulo_emoji = "📦" if tipo == "dev" else "🔬"
    titulo_tipo = "Desenvolvedor" if tipo == "dev" else "QA"
    
    with st.expander(f"{titulo_emoji} Áreas de Atuação", expanded=expanded):
        # Produtos
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📦 Por Produto:**")
            produtos = concentracao['produtos'][:5]  # Top 5
            if produtos:
                for p in produtos:
                    cor = '🔴' if p['pct'] >= 80 else '🟡' if p['pct'] >= 60 else '🟢'
                    st.markdown(f"{cor} **{p['nome']}**: {p['cards']} cards ({p['pct']}%)")
            else:
                st.info("Sem dados de produto")
        
        with col2:
            st.markdown("**🏢 Por Cliente:**")
            clientes = [c for c in concentracao['clientes'][:5] if c['nome'] not in ['Sem cliente', 'Interno/Plataforma']]
            if clientes:
                for c in clientes:
                    cor = '🔴' if c['pct'] >= 80 else '🟡' if c['pct'] >= 60 else '🟢'
                    st.markdown(f"{cor} **{c['nome']}**: {c['cards']} cards ({c['pct']}%)")
            else:
                st.info("Sem dados de cliente específico")
        
        # Alertas de concentração
        if concentracao['alertas']:
            st.markdown("---")
            st.markdown("**⚠️ Pontos de atenção (concentração ≥60%):**")
            for alerta in concentracao['alertas']:
                icone = "📦" if alerta['tipo'] == 'produto' else "🏢"
                st.warning(f"{icone} Alta concentração em **{alerta['nome']}** ({alerta['pct']}% dos cards)")


def exibir_concentracao_time(df: pd.DataFrame, tipo: str = "dev"):
    """
    Exibe um resumo da concentração de conhecimento do time todo.
    Para uso na visão geral das abas DEV e QA.
    
    Args:
        df: DataFrame com os cards
        tipo: "dev" ou "qa"
    """
    concentracao = calcular_concentracao_conhecimento(df)
    
    # Filtra alertas pelo tipo
    if tipo == "dev":
        alertas = concentracao['alertas_dev']
        indices_produto = concentracao['indices'].get('dev_produto', {})
        indices_cliente = concentracao['indices'].get('dev_cliente', {})
    else:
        alertas = concentracao['alertas_qa']
        indices_produto = concentracao['indices'].get('qa_produto', {})
        indices_cliente = concentracao['indices'].get('qa_cliente', {})
    
    alertas_criticos = [a for a in alertas if a['tipo'] == 'critico']
    alertas_atencao = [a for a in alertas if a['tipo'] == 'atencao']
    
    titulo_tipo = "DEV" if tipo == "dev" else "QA"
    
    with st.expander(f"🔄 Concentração de Conhecimento ({titulo_tipo})", expanded=False):
        st.caption("Identifique riscos de conhecimento centralizado no time")
        
        # Cards resumo
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cor = 'red' if len(alertas_criticos) > 0 else 'green'
            criar_card_metrica(str(len(alertas_criticos)), "Críticos", cor, "≥80% concentração")
        
        with col2:
            cor = 'yellow' if len(alertas_atencao) > 0 else 'green'
            criar_card_metrica(str(len(alertas_atencao)), "Atenção", cor, "60-79% concentração")
        
        with col3:
            total_areas = len(indices_produto) + len(indices_cliente)
            areas_ok = sum(1 for d in indices_produto.values() if d['concentracao_pct'] < 60)
            areas_ok += sum(1 for d in indices_cliente.values() if d['concentracao_pct'] < 60)
            pct_ok = (areas_ok / total_areas * 100) if total_areas > 0 else 100
            cor = 'green' if pct_ok >= 70 else 'yellow' if pct_ok >= 40 else 'red'
            criar_card_metrica(f"{pct_ok:.0f}%", "Bem Distribuído", cor)
        
        # Lista de alertas se houver
        if alertas_criticos or alertas_atencao:
            st.markdown("---")
            
            if alertas_criticos:
                st.markdown("**🚨 Concentração Crítica:**")
                for a in alertas_criticos[:3]:  # Mostra top 3
                    icone = "📦" if a['contexto'] == 'produto' else "🏢"
                    st.error(f"{icone} **{a['pessoa']}** domina {a['pct']}% de '{a['nome']}'")
                if len(alertas_criticos) > 3:
                    st.caption(f"... e mais {len(alertas_criticos) - 3} alertas críticos")
            
            if alertas_atencao:
                st.markdown("**⚠️ Pontos de Atenção:**")
                for a in alertas_atencao[:3]:
                    icone = "📦" if a['contexto'] == 'produto' else "🏢"
                    st.warning(f"{icone} **{a['pessoa']}** tem {a['pct']}% de '{a['nome']}'")
                if len(alertas_atencao) > 3:
                    st.caption(f"... e mais {len(alertas_atencao) - 3} pontos de atenção")
        else:
            st.success("✅ Conhecimento bem distribuído no time!")
        
        st.markdown("---")
        st.caption("💡 Veja análise completa na aba **Liderança** → seção 'Análise de Concentração'")


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

def exibir_card_detalhado_v2(card: Dict, links: List[Dict], comentarios: List[Dict], historico: List[Dict] = None, projeto: str = "SD") -> bool:
    """
    Exibe painel detalhado com informações de um card específico.
    Adapta o conteúdo conforme o projeto:
    - SD: Completo (bugs, FK, qualidade, janela, comentários)
    - QA: Foco em aging, automação, tempo parado
    - PB: Backlog - sem bugs, foco em prioridade e estimativa
    """
    if not card:
        return False
    
    # Garante que historico seja uma lista
    if historico is None:
        historico = []
    
    # Gera URL de compartilhamento
    base_url = NINADASH_URL
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
        <style>
            html, body {{
                margin: 0 !important;
                padding: 0 !important;
                overflow: hidden;
            }}
        </style>
        <button id="copyBtn" style="
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            border: none;
            padding: 0 16px;
            border-radius: 8px;
            cursor: pointer;
            width: 100%;
            height: 36px;
            font-size: 14px;
            font-weight: 500;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
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
        """, height=36)
    
    with col3:
        st.caption(f"Sprint: **{card['sprint']}** | Produto: **{card['produto']}**")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========================================================================
    # CONTEÚDO ESPECÍFICO POR PROJETO
    # ========================================================================
    
    if projeto == "SD":
        exibir_detalhes_sd(card, links, comentarios, historico)
    elif projeto == "QA":
        exibir_detalhes_qa(card, links, comentarios, historico)
    elif projeto == "PB":
        exibir_detalhes_pb(card, links, comentarios, historico)
    else:
        exibir_detalhes_sd(card, links, comentarios, historico)  # Fallback
    
    return True


def exibir_detalhes_sd(card: Dict, links: List[Dict], comentarios: List[Dict], historico: List[Dict] = None):
    """Exibe detalhes para projeto SD (Service Desk) - Completo com qualidade."""
    
    # Garante que historico seja uma lista
    if historico is None:
        historico = []
    
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
    
    # ===== DESCRIÇÃO DO CARD =====
    descricao = card.get('descricao', '')
    if descricao and descricao.strip():
        with st.expander("📝 **Descrição**", expanded=False):
            st.markdown(f"""
<div style='background: #f8fafc; padding: 16px; border-radius: 8px; border-left: 3px solid #3b82f6;'>
    <div style='color: #374151; line-height: 1.6; white-space: pre-wrap;'>{descricao}</div>
</div>
            """, unsafe_allow_html=True)
    
    # ===== TIMELINE DE TRANSIÇÕES =====
    if historico:
        exibir_timeline_transicoes(historico, "📜 Timeline Completa do Card")
    
    # ===== CARDS VINCULADOS =====
    exibir_cards_vinculados(links)
    
    # ===== COMENTÁRIOS =====
    exibir_comentarios(comentarios, projeto="SD")


def exibir_detalhes_qa(card: Dict, links: List[Dict], comentarios: List[Dict], historico: List[Dict] = None):
    """Exibe detalhes para projeto QA - Foco em automação e tempo parado."""
    
    # Garante que historico seja uma lista
    if historico is None:
        historico = []
    
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
    
    # ===== TIMELINE DE TRANSIÇÕES =====
    if historico:
        exibir_timeline_transicoes(historico, "📜 Timeline Completa do Card")
    
    # ===== CARDS VINCULADOS =====
    exibir_cards_vinculados(links)
    
    # ===== COMENTÁRIOS =====
    exibir_comentarios(comentarios, projeto="QA")


def exibir_detalhes_pb(card: Dict, links: List[Dict], comentarios: List[Dict], historico: List[Dict] = None):
    """Exibe detalhes para projeto PB (Backlog) - Sem bugs, foco em prioridade."""
    
    # Garante que historico seja uma lista
    if historico is None:
        historico = []
    
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
            epic_texto = f"[{card.get('epic_link', '')}]({link_jira(card.get('epic_link', ''))})" if card.get('epic_link') else 'Sem Epic'
            st.markdown(f"""
| Campo | Valor |
|-------|-------|
| **Projeto** | {card['projeto']} |
| **Produto** | {card['produto']} |
| **Tipo** | {card['tipo_original']} |
| **Estimativa** | {card['sp']} SP |
| **Epic/Parent** | {epic_texto} |
            """)
        
        with col2:
            responsavel = card.get('desenvolvedor', 'Não atribuído')
            if responsavel == 'Não atribuído':
                responsavel = card.get('relator', 'Não informado')
            st.markdown(f"""
| Campo | Valor |
|-------|-------|
| **Relator** | {card.get('relator', 'Não informado')} |
| **Responsável** | {responsavel} |
| **Data Criação** | {card['criado'].strftime('%d/%m/%Y') if pd.notna(card['criado']) else 'N/A'} |
| **Última Atualização** | {card['atualizado'].strftime('%d/%m/%Y') if pd.notna(card['atualizado']) else 'N/A'} |
| **Status** | {card['status']} |
            """)
        
        # Componentes se houver
        componentes = card.get('componentes', [])
        if componentes:
            comp_texto = ', '.join(componentes)
            st.markdown(f"""
            <div style='background: #6366f115; padding: 10px 15px; border-radius: 8px; 
                        border-left: 3px solid #6366f1; margin-top: 10px;'>
                <strong style='color: #6366f1;'>🧩 Componentes:</strong> {comp_texto}
            </div>
            """, unsafe_allow_html=True)
        
        # Labels se houver
        labels = card.get('labels', [])
        if labels:
            labels_html = ' '.join([f"<span style='background: #8b5cf620; color: #8b5cf6; padding: 3px 8px; border-radius: 12px; font-size: 0.85em; margin-right: 5px;'>{l}</span>" for l in labels])
            st.markdown(f"""
            <div style='background: #8b5cf610; padding: 10px 15px; border-radius: 8px; 
                        border-left: 3px solid #8b5cf6; margin-top: 10px;'>
                <strong style='color: #8b5cf6;'>🏷️ Labels:</strong><br>
                <div style='margin-top: 8px;'>{labels_html}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Resolução/Roteiro em destaque se estiver preenchido
        resolucao = card.get('resolucao', '')
        if resolucao:
            cor_resolucao = "#22c55e" if resolucao.lower() in ['done', 'concluído', 'vai ser feito', 'aprovado'] else "#f59e0b"
            st.markdown(f"""
            <div style='background: {cor_resolucao}15; padding: 12px 15px; border-radius: 8px; 
                        border-left: 3px solid {cor_resolucao}; margin-top: 10px;'>
                <strong style='color: {cor_resolucao};'>📋 Resolução/Roteiro:</strong> {resolucao}
            </div>
            """, unsafe_allow_html=True)
    
    # ===== DESCRIÇÃO DO ITEM =====
    descricao = card.get('descricao', '')
    if descricao and len(descricao.strip()) > 0:
        with st.expander("📝 **Descrição**", expanded=True):
            # Limita a descrição se for muito longa
            desc_display = descricao[:2000] + '...' if len(descricao) > 2000 else descricao
            st.markdown(f"""
            <div style='background: #f8fafc; padding: 15px; border-radius: 8px; 
                        border: 1px solid #e2e8f0; line-height: 1.6;'>
                {desc_display}
            </div>
            """, unsafe_allow_html=True)
    
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
    
    # ===== TIMELINE DE TRANSIÇÕES =====
    if historico:
        exibir_timeline_transicoes(historico, "📜 Timeline Completa do Card")
    
    # ===== CARDS VINCULADOS =====
    exibir_cards_vinculados(links)
    
    # ===== COMENTÁRIOS =====
    exibir_comentarios(comentarios, projeto="PB")


def exibir_timeline_transicoes(historico: List[Dict], titulo: str = "📜 Timeline Completa do Card"):
    """
    Exibe uma timeline visual completa com todas as transições do card.
    Usa components.html para scroll horizontal real.
    Scroll posicionado automaticamente no status atual.
    """
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not historico or len(historico) == 0:
        with st.expander(f"{titulo} (0 eventos)", expanded=False):
            st.info("Histórico não disponível")
        return
    
    # Filtra transições de status para métricas
    transicoes_status = [h for h in historico if h['tipo'] in ['criacao', 'transicao', 'resolucao']]
    
    # Calcula métricas gerais
    total_eventos = len(historico)
    total_dias = sum(e.get('duracao_dias', 0) for e in historico)
    qtd_retrabalhos = len([h for h in historico if h['tipo'] == 'transicao' and any(x in str(h.get('para', '')).lower() for x in ['desenvolviment', 'development', 'andamento'])])
    qtd_rejeicoes = len([h for h in historico if any(x in str(h.get('para', '')).lower() for x in ['reprovado', 'rejected', 'recusado'])])
    
    with st.expander(f"{titulo} ({len(historico)} eventos)", expanded=True):
        
        if historico:
            # Monta os cards da timeline com todos eventos
            cards_html = ""
            for i, evento in enumerate(historico):
                # Data completa com ano
                data_fmt = evento['data'].strftime('%d/%m/%Y') if evento['data'] else 'N/A'
                hora_fmt = evento['data'].strftime('%H:%M') if evento['data'] else ''
                
                # Dia da semana
                dias_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
                dia_semana = dias_semana[evento['data'].weekday()] if evento['data'] else ''
                
                # Duração formatada
                duracao_dias = evento.get('duracao_dias', 0)
                duracao_horas = evento.get('duracao_horas', 0)
                if duracao_dias > 0:
                    duracao = f"{duracao_dias} dia{'s' if duracao_dias > 1 else ''}"
                elif duracao_horas > 0:
                    duracao = f"{duracao_horas}h"
                else:
                    duracao = "< 1h"
                
                # Indicador de tempo (se ficou muito tempo)
                alerta_tempo = ""
                if duracao_dias >= 5:
                    alerta_tempo = "<div style='font-size:10px; color:#ef4444; margin-top:4px;'>⚠️ Tempo elevado</div>"
                elif duracao_dias >= 3:
                    alerta_tempo = "<div style='font-size:10px; color:#f59e0b; margin-top:4px;'>⏰ Atenção ao tempo</div>"
                
                is_current = (i == len(historico) - 1)
                current_id = "current-status" if is_current else ""
                badge = "<div style='background:linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color:white; font-size:11px; padding:6px 12px; border-radius:12px; margin-top:10px; display:inline-block; font-weight:600; box-shadow:0 2px 4px rgba(34,197,94,0.3);'>📍 STATUS ATUAL</div>" if is_current else ""
                arrow = "" if is_current else "<div style='display:flex; align-items:center; padding:0 8px; color:#94a3b8; font-size:28px; font-weight:300;'>→</div>"
                
                # Número do passo
                passo_num = f"<div style='position:absolute; top:-10px; left:-10px; background:{evento['cor']}; color:white; font-size:10px; font-weight:700; width:22px; height:22px; border-radius:50%; display:flex; align-items:center; justify-content:center; box-shadow:0 2px 4px rgba(0,0,0,0.2);'>{i+1}</div>"
                
                # Campo modificado
                campo = evento.get('campo', 'Status')
                tipo = evento.get('tipo', 'transicao')
                
                # Ícone baseado no tipo
                tipo_icone = {
                    'criacao': '🎫 Criação',
                    'transicao': '🔄 Status',
                    'atribuicao': '👤 Atribuição',
                    'qa_atribuicao': '🧪 QA',
                    'sprint': '🏃 Sprint',
                    'estimativa': '📊 Estimativa',
                    'bugs': '🐛 Bugs',
                    'resolucao': '✅ Resolução'
                }.get(tipo, f'📋 {campo}')
                
                campo_display = f"<div style='font-size:11px; color:#64748b; margin-bottom:6px; background:#f1f5f9; padding:4px 8px; border-radius:6px; display:inline-block;'>{tipo_icone}</div>"
                
                # Valor anterior (de) se existir
                de_valor = evento.get('de', '')
                de_display = f"<div style='font-size:12px; color:#94a3b8; margin-bottom:4px;'><span style='text-decoration:line-through; color:#ef4444;'>{str(de_valor)[:25]}</span></div>" if de_valor else ""
                
                # Valor novo (para) - destaque principal
                para_valor = evento.get('para', 'N/A')
                
                # Autor
                autor = evento.get('autor', 'Sistema')
                
                # Detalhes extras se disponível
                detalhes = evento.get('detalhes', '')
                
                cards_html += f'''
                <div id="{current_id}" style="position:relative; flex:0 0 auto; width:220px; background:white; border-radius:14px; padding:18px; border-top:5px solid {evento['cor']}; box-shadow:0 4px 16px rgba(0,0,0,0.08); font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; {'border:2px solid #22c55e; box-shadow:0 4px 20px rgba(34,197,94,0.2);' if is_current else ''}">
                    {passo_num}
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
                        <div style="font-size:32px;">{evento['icone']}</div>
                        <div style="text-align:right;">
                            <div style="font-size:13px; color:#1e293b; font-weight:700;">{data_fmt}</div>
                            <div style="font-size:11px; color:#64748b;">{dia_semana}, {hora_fmt}</div>
                        </div>
                    </div>
                    {campo_display}
                    {de_display}
                    <div style="font-weight:700; font-size:14px; color:{evento['cor']}; margin-bottom:10px; word-wrap:break-word; line-height:1.4; padding:10px; background:{evento['cor']}15; border-radius:10px; border-left:3px solid {evento['cor']};">{str(para_valor)[:35]}</div>
                    <div style="display:flex; justify-content:space-between; align-items:center; padding-top:10px; border-top:1px solid #f1f5f9;">
                        <div style="font-size:11px; color:#64748b; max-width:110px; overflow:hidden; text-overflow:ellipsis;">👤 {str(autor)[:20]}</div>
                        <div style="font-size:11px; background:linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%); color:#475569; padding:5px 10px; border-radius:10px; font-weight:600;">⏱️ {duracao}</div>
                    </div>
                    {alerta_tempo}
                    {badge}
                </div>
                {arrow}
                '''
            
            altura = 380
            
            # HTML completo com scroll posicionado no final (status atual)
            html_completo = f'''
            <style>
                .timeline-container {{
                    overflow-x: auto;
                    overflow-y: hidden !important;
                    padding: 20px 15px;
                    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                    border-radius: 14px;
                    border: 1px solid #e2e8f0;
                    max-height: 320px;
                }}
                .timeline-container::-webkit-scrollbar {{
                    height: 10px;
                }}
                .timeline-container::-webkit-scrollbar-track {{
                    background: #e2e8f0;
                    border-radius: 4px;
                    margin-right: 5px;
                }}
                .timeline-container::-webkit-scrollbar-thumb {{
                    background: #94a3b8;
                    border-radius: 6px;
                    cursor: grab;
                }}
                .timeline-container::-webkit-scrollbar-thumb:hover {{
                    background: #64748b;
                    cursor: grabbing;
                }}
            </style>
            <div class="timeline-container" id="timeline-scroll">
                <div style="display:flex; flex-direction:row; align-items:stretch; gap:10px; width:max-content; height:fit-content;">
                    {cards_html}
                </div>
            </div>
            <p style="font-size:12px; color:#94a3b8; text-align:center; margin:12px 0 0 0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
                ⬅️ Arraste para ver histórico completo | 📍 Posicionado no status atual ➡️
            </p>
            <script>
                // Auto-scroll para o status atual (final)
                setTimeout(function() {{
                    var container = document.getElementById('timeline-scroll');
                    if (container) {{
                        container.scrollLeft = container.scrollWidth;
                    }}
                }}, 100);
            </script>
            '''
            
            components.html(html_completo, height=altura, scrolling=False)
        else:
            st.info("Nenhum evento registrado.")
        
        # ===== MÉTRICAS DE TEMPO =====
        st.markdown("---")
        st.markdown("##### ⏱️ Métricas de Tempo por Status")
        
        # Agrupa tempo por status
        tempo_por_status = {}
        for evento in transicoes_status:
            if evento['tipo'] == 'transicao' and evento.get('de'):
                status_anterior = evento['de']
                if status_anterior not in tempo_por_status:
                    tempo_por_status[status_anterior] = 0
                # Procura o tempo que ficou nesse status (olhando o evento anterior)
                idx = transicoes_status.index(evento)
                if idx > 0:
                    evento_anterior = transicoes_status[idx - 1]
                    tempo_por_status[status_anterior] += evento_anterior.get('duracao_dias', 0)
        
        # Adiciona tempo no status atual
        if transicoes_status:
            ultimo = transicoes_status[-1]
            status_atual = ultimo.get('para', 'Desconhecido')
            tempo_por_status[status_atual] = ultimo.get('duracao_dias', 0)
        
        if tempo_por_status:
            cols = st.columns(min(len(tempo_por_status), 5))
            for i, (status, dias) in enumerate(tempo_por_status.items()):
                with cols[i % len(cols)]:
                    icone, cor = obter_icone_status(status)
                    st.markdown(f"""
<div style='background:{cor}15; padding:10px; border-radius:8px; text-align:center; border-left:3px solid {cor};'>
    <div style='font-size:18px;'>{icone}</div>
    <div style='font-size:11px; color:#666;'>{status[:15]}{'...' if len(status) > 15 else ''}</div>
    <div style='font-size:16px; font-weight:600; color:{cor};'>{dias}d</div>
</div>
                    """, unsafe_allow_html=True)
        
        # ===== QUANTIDADE DE REPROVAÇÕES =====
        reprovacoes = len([h for h in historico if h['tipo'] == 'transicao' and h.get('para') and
                          any(x in h['para'].lower() for x in ['reprovado', 'rejected', 'recusado'])])
        retornos_dev = len([h for h in historico if h['tipo'] == 'transicao' and h.get('de') and h.get('para') and
                           any(x in h['de'].lower() for x in ['validação', 'qa', 'testing']) and
                           any(x in h['para'].lower() for x in ['desenvolvimento', 'andamento', 'development'])])
        
        if reprovacoes > 0 or retornos_dev > 0:
            st.markdown("---")
            st.markdown("##### 🔄 Análise de Retrabalho")
            col1, col2 = st.columns(2)
            
            with col1:
                cor_rep = "#ef4444" if reprovacoes > 0 else "#22c55e"
                st.markdown(f"""
<div style='background:{cor_rep}15; padding:12px; border-radius:8px; text-align:center; border-left:3px solid {cor_rep};'>
    <div style='font-size:22px;'>❌</div>
    <div style='font-size:24px; font-weight:700; color:{cor_rep};'>{reprovacoes}</div>
    <div style='font-size:12px; color:#666;'>Reprovações</div>
</div>
                """, unsafe_allow_html=True)
            
            with col2:
                cor_ret = "#f97316" if retornos_dev > 0 else "#22c55e"
                st.markdown(f"""
<div style='background:{cor_ret}15; padding:12px; border-radius:8px; text-align:center; border-left:3px solid {cor_ret};'>
    <div style='font-size:22px;'>🔄</div>
    <div style='font-size:24px; font-weight:700; color:{cor_ret};'>{retornos_dev}</div>
    <div style='font-size:12px; color:#666;'>Retornos p/ Dev</div>
</div>
                """, unsafe_allow_html=True)


def exibir_cards_vinculados(links: List[Dict]):
    """Exibe seção de cards vinculados com popup para navegar. Inclui links transitivos (2º nível)."""
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not links or len(links) == 0:
        # Mostra mensagem quando não há vínculos
        with st.expander("🔗 **Cards Vinculados (0)**", expanded=False):
            st.markdown("""
<div style='background: #f8fafc; padding: 15px; border-radius: 8px; text-align: center; color: #64748b;'>
    <span style='font-size: 1.5em;'>🔗</span><br>
    <span style='font-size: 0.9em;'>Nenhum card vinculado</span><br>
    <span style='font-size: 0.8em; color: #94a3b8;'>Este card não possui links com outros cards no Jira</span>
</div>
            """, unsafe_allow_html=True)
        return
    
    # Separa links de primeiro e segundo nível
    links_nivel_1 = [l for l in links if l.get('nivel', 1) == 1]
    links_nivel_2 = [l for l in links if l.get('nivel', 1) == 2]
    
    with st.expander(f"🔗 **Cards Vinculados ({len(links)})**", expanded=True):
        # Links de primeiro nível (diretos)
        if links_nivel_1:
            st.markdown("**🔵 Links Diretos:**")
            for link in links_nivel_1:
                tipo_cor = "#6366f1" if link['tipo'] == 'Pai' else "#22c55e" if link['tipo'] == 'Subtarefa' else "#f59e0b"
                card_popup_html = card_link_com_popup(link['ticket_id'])
                st.markdown(f"""
<div style='background: {tipo_cor}10; padding: 10px 15px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid {tipo_cor};'>
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <div>
            <span style='color: {tipo_cor}; font-weight: bold; font-size: 0.85em;'>{link['tipo']}</span>
            <span style='color: #666; font-size: 0.8em;'> • {link['direcao']}</span>
            <br>
            {card_popup_html}
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
            
            # Links de segundo nível (transitivos)
            if links_nivel_2:
                st.markdown("---")
                st.markdown("**🔗 Outros Cards Relacionados** *(via cards vinculados)*:")
                st.caption("Cards conectados através dos links diretos acima")
                for link in links_nivel_2:
                    card_popup_html = card_link_com_popup(link['ticket_id'])
                    via_text = f" (via {link.get('via', '')})" if link.get('via') else ""
                    st.markdown(f"""
<div style='background: #f1f5f9; padding: 8px 12px; border-radius: 6px; margin-bottom: 6px; border-left: 3px dashed #94a3b8;'>
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <div>
            <span style='color: #64748b; font-size: 0.8em;'>{link['tipo']} • {link['direcao']}</span>
            <span style='color: #94a3b8; font-size: 0.75em;'>{via_text}</span>
            <br>
            {card_popup_html}
            <span style='color: #64748b; font-size: 0.8em;'> - {link['titulo'][:50]}{'...' if len(link['titulo']) > 50 else ''}</span>
        </div>
        <div>
            <span style='background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-size: 0.7em; color: #64748b;'>
                {link['status']}
            </span>
        </div>
    </div>
</div>
                    """, unsafe_allow_html=True)


def filtrar_e_classificar_comentarios(comentarios: List[Dict]) -> List[Dict]:
    """
    Filtra comentários de automação e classifica os relevantes.
    Adiciona contexto temporal (antes/depois de eventos importantes).
    
    Classificações:
    - bug: Comentário relacionado a bug/defeito
    - reprovacao: Comentário de reprovação
    - impedido: Comentário de impedimento
    - retorno_dev: Resposta do desenvolvedor a bug/reprovação
    - normal: Comentário comum (com contexto temporal)
    """
    if not comentarios:
        return []
    
    # Padrões de automação a serem filtrados (case insensitive)
    padroes_automacao = [
        "mentioned this issue in a commit",
        "mentioned this issue in a branch",
        "merge branch",
        "pushed a commit",
        "created a branch",
        "deleted branch",
        "opened a pull request",
        "closed a pull request",
        "merged a pull request",
        "mentioned this issue in a pull request",
        "linked a pull request",
        "connected this issue",
        "disconnected this issue",
        "moved this issue",
        "added a commit",
        "referenced this issue",
        "mentioned this page",
        "/confirmationcall on branch",
        "Elintondm /",
        "on branch sd-",
        "on branch SD-",
        "into homolog",
        "into master",
        "into main",
        "into develop",
    ]
    
    # Padrões para identificar comentários de bugs (AMPLIADO)
    padroes_bug = [
        # HASHTAG BUG (padrão usado pelo QA)
        "#bug",
        "# bug",
        "#Bug",
        "# Bug",
        # Padrões diretos de bug
        "bug encontrado",
        "bug identificado", 
        "bug registrado",
        "bugs identificados",
        "bugs encontrados",
        "alguns bugs",
        "bug:",
        "bug 1",
        "bug 2", 
        "bug 3",
        "bug 4",
        "bug 5",
        "bug#",
        "bug #",
        # Foram identificados
        "foram identificados",
        "foi identificado",
        "foram encontrados",
        "foi encontrado",
        # Defeitos/erros
        "defeito encontrado",
        "defeito identificado",
        "defeito:",
        "erro encontrado",
        "erro identificado",
        "erro:",
        "erro interno",
        "erro genérico",
        "falha encontrada",
        "falha identificada",
        "falha:",
        # Problemas de comportamento
        "problema encontrado",
        "problema identificado",
        "problema:",
        "inconsistência",
        "inconsistência encontrada",
        "falta de feedback",
        "não dá retorno",
        "sem retorno ao",
        "não dá feedback",
        # Interface/UX com problemas
        "funciona apenas como",
        "impedindo que o usuário",
        "obrigando-o",
        "obrigando o usuário",
        "não é possível realizar",
        "não estão traduzidas",
        "informação em inglês",
        "informações não estão",
        "deve impedir",
        "deveria impedir",
        "não impede",
        # Sistema retornando erros
        "sistema retornou",
        "sistema permitiu",
        "sistema não",
        "api retorna",
        "api retornou",
        "backend retornar",
        "retornar invalid",
        "retorna a informação",
        # Comportamento
        "não está funcionando",
        "não funciona",
        "não funcionou",
        "parou de funcionar",
        "comportamento incorreto",
        "comportamento inesperado",
        "comportamento errado",
        # Erros técnicos
        "retornou erro",
        "retorna erro",
        "apresentou erro",
        "apresenta erro",
        "deu erro",
        "está com erro",
        "erro ao",
        "falhou ao",
        "não consegue",
        "não carrega",
        "não abre",
        "não salva",
        "não exibe",
        "não mostra",
        "não aparece",
        "trava",
        "travou",
        "congelou",
        "quebrou",
        "crashou",
        # Porém/mas com problemas
        "porem",  # usuário usa sem acento
        "porém",
        "ainda não é possível",
        "ainda não",
        "mas não",
        "mas as informações",
        # Cenários de teste
        "cenário de bug",
        "cenário:",
        "cenário 1",
        "cenário 2",
        "cenário 3",
        "cenário 4",
        "cenário 5",
        "caso de bug",
        # Evidências
        "evidência de bug",
        "evidência do bug",
        "evidência:",
        "print do bug",
        "screenshot do erro",
        "anexo do bug",
        "devtools",
        "devTools",
        "DevTools",
        # Registro
        "registrando bug",
        "registrar bug",
        "abrir bug",
        "aberto bug",
        "abrindo bug",
        "novo bug",
        # QA reportando
        "encontrei um",
        "encontrei o",
        "identifiquei um",
        "identifiquei o",
        "verifiquei que",
        "percebi que",
        "notei que",
        "observei que",
        "ao testar",
        "durante o teste",
        "na validação",
        "validando",
        "ao tentar",
        "ao clicar",
        "ao acessar",
        "ao editar",
        "ao criar",
        "ao salvar",
    ]
    
    # Padrões para identificar comentários de reprovação
    padroes_reprovacao = [
        "reprovado",
        "reprovação",
        "reprovei",
        "reprovando",
        "não aprovado",
        "reprovar",
        "card reprovado",
        "tarefa reprovada",
        "retornando para",
        "devolvendo para",
        "devolvido para",
        "voltando para desenvolvimento",
        "retornar para desenvolvimento",
        "retornado para desenvolvimento",
        "ajustes necessários",
        "necessita de ajustes",
        "correções necessárias",
        "necessita correção",
        "não passou na validação",
        "não passou no teste",
        "falhou na validação",
        "não atende",
        "não atendeu",
        "favor corrigir",
        "por favor corrigir",
        "correção necessária",
        "precisa de correção",
        "precisa corrigir",
        "precisa ajustar",
        "não está conforme",
        "fora do esperado",
        "diferente do esperado",
    ]
    
    # Padrões para identificar comentários de impedimento
    padroes_impedido = [
        "impedido",
        "impedimento",
        "bloqueado",
        "bloqueio",
        "dependência",
        "aguardando",
        "aguardar",
        "esperar",
        "esperando",
        "não pode prosseguir",
        "não consigo continuar",
        "não é possível continuar",
        "parado",
        "pausado",
        "travado",
        "bloqueando",
        "depende de",
        "dependendo de",
        "precisa de",
        "necessita de ambiente",
        "ambiente indisponível",
        "sem acesso",
        "não tenho acesso",
        "aguardando retorno",
        "aguardando resposta",
    ]
    
    # Padrões para identificar retorno do DEV
    padroes_retorno_dev = [
        "corrigido",
        "correção feita",
        "correção realizada",
        "ajustado",
        "ajuste feito",
        "ajuste realizado",
        "pronto para",
        "disponível para",
        "liberado para",
        "pode testar",
        "pode validar",
        "favor validar",
        "por favor validar",
        "validar novamente",
        "retestando",
        "para revalidação",
        "para retestar",
        "já corrigi",
        "já ajustei",
        "feito o ajuste",
        "feita a correção",
        "resolvido",
        "solucionado",
        "implementado",
        "alterado conforme",
        "atualizado conforme",
    ]
    
    # Primeira passagem: filtrar automações e classificar
    comentarios_pre = []
    for com in comentarios:
        texto_lower = com.get('texto', '').lower()
        autor = com.get('autor', '').lower()
        
        # Verifica se é automação (pula se for)
        eh_automacao = False
        for padrao in padroes_automacao:
            if padrao.lower() in texto_lower:
                eh_automacao = True
                break
        
        if any(bot in autor for bot in ['automation', 'bot', 'github', 'bitbucket', 'gitlab', 'jira']):
            eh_automacao = True
        
        if eh_automacao:
            continue
        
        # Classifica o comentário (ordem de prioridade)
        classificacao = 'normal'
        
        # 1. Verifica bug (maior prioridade para QA)
        for padrao in padroes_bug:
            if padrao in texto_lower:
                classificacao = 'bug'
                break
        
        # 2. Verifica reprovação
        if classificacao == 'normal':
            for padrao in padroes_reprovacao:
                if padrao in texto_lower:
                    classificacao = 'reprovacao'
                    break
        
        # 3. Verifica impedimento
        if classificacao == 'normal':
            for padrao in padroes_impedido:
                if padrao in texto_lower:
                    classificacao = 'impedido'
                    break
        
        # 4. Verifica retorno do DEV
        if classificacao == 'normal':
            for padrao in padroes_retorno_dev:
                if padrao in texto_lower:
                    classificacao = 'retorno_dev'
                    break
        
        # Parse da data
        try:
            data_parsed = datetime.fromisoformat(com['data'].replace('Z', '+00:00')).replace(tzinfo=None)
        except:
            data_parsed = datetime.now()
        
        comentarios_pre.append({
            **com,
            'classificacao': classificacao,
            'data_parsed': data_parsed,
            'contexto': None
        })
    
    # Ordena por data
    comentarios_pre.sort(key=lambda x: x['data_parsed'])
    
    # Segunda passagem: adicionar contexto temporal
    eventos = []
    for i, com in enumerate(comentarios_pre):
        if com['classificacao'] in ['bug', 'reprovacao', 'impedido']:
            eventos.append({
                'indice': i,
                'tipo': com['classificacao'],
                'data': com['data_parsed'],
                'numero': len([e for e in eventos if e['tipo'] == com['classificacao']]) + 1
            })
    
    # Atribui contexto aos comentários normais e retorno_dev
    for i, com in enumerate(comentarios_pre):
        if com['classificacao'] in ['normal', 'retorno_dev']:
            evento_anterior = None
            evento_posterior = None
            
            for ev in eventos:
                if ev['indice'] < i:
                    evento_anterior = ev
                elif ev['indice'] > i and evento_posterior is None:
                    evento_posterior = ev
            
            if evento_anterior and evento_posterior:
                dist_ant = i - evento_anterior['indice']
                dist_pos = evento_posterior['indice'] - i
                
                if dist_ant <= dist_pos:
                    tipo_nome = {'bug': 'Bug', 'reprovacao': 'Reprovação', 'impedido': 'Impedimento'}[evento_anterior['tipo']]
                    com['contexto'] = f"Após {tipo_nome} #{evento_anterior['numero']}"
                else:
                    tipo_nome = {'bug': 'Bug', 'reprovacao': 'Reprovação', 'impedido': 'Impedimento'}[evento_posterior['tipo']]
                    com['contexto'] = f"Antes {tipo_nome} #{evento_posterior['numero']}"
            elif evento_anterior:
                tipo_nome = {'bug': 'Bug', 'reprovacao': 'Reprovação', 'impedido': 'Impedimento'}[evento_anterior['tipo']]
                com['contexto'] = f"Após {tipo_nome} #{evento_anterior['numero']}"
            elif evento_posterior:
                tipo_nome = {'bug': 'Bug', 'reprovacao': 'Reprovação', 'impedido': 'Impedimento'}[evento_posterior['tipo']]
                com['contexto'] = f"Antes {tipo_nome} #{evento_posterior['numero']}"
    
    # Numera os eventos no resultado final
    contadores = {'bug': 0, 'reprovacao': 0, 'impedido': 0, 'retorno_dev': 0}
    for com in comentarios_pre:
        if com['classificacao'] in contadores:
            contadores[com['classificacao']] += 1
            com['numero_evento'] = contadores[com['classificacao']]
    
    return comentarios_pre


def exibir_comentarios(comentarios: List[Dict], projeto: str = "SD"):
    """Exibe seção de comentários do card (filtrados e classificados) com filtros interativos."""
    
    # Usa classificação diferente para PB (Product Backlog)
    if projeto == "PB":
        exibir_comentarios_pb(comentarios)
        return
    
    # Para SD e QA: classificação com tags de QA
    comentarios_filtrados = filtrar_e_classificar_comentarios(comentarios)
    
    total_original = len(comentarios) if comentarios else 0
    total_filtrado = len(comentarios_filtrados)
    filtrados = total_original - total_filtrado
    
    # Conta por classificação
    bugs = sum(1 for c in comentarios_filtrados if c.get('classificacao') == 'bug')
    reprovacoes = sum(1 for c in comentarios_filtrados if c.get('classificacao') == 'reprovacao')
    impedidos = sum(1 for c in comentarios_filtrados if c.get('classificacao') == 'impedido')
    retornos = sum(1 for c in comentarios_filtrados if c.get('classificacao') == 'retorno_dev')
    normais = sum(1 for c in comentarios_filtrados if c.get('classificacao') == 'normal')
    
    if comentarios_filtrados and len(comentarios_filtrados) > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Monta título com contagens
        titulo_extra = []
        if bugs > 0:
            titulo_extra.append(f"🐛 {bugs}")
        if reprovacoes > 0:
            titulo_extra.append(f"❌ {reprovacoes}")
        if impedidos > 0:
            titulo_extra.append(f"🚫 {impedidos}")
        if retornos > 0:
            titulo_extra.append(f"🔄 {retornos}")
        titulo_sufixo = f" | {' '.join(titulo_extra)}" if titulo_extra else ""
        
        with st.expander(f"💬 **Comentários ({total_filtrado})**{titulo_sufixo}", expanded=True):
            # Aviso sobre comentários filtrados
            if filtrados > 0:
                st.caption(f"ℹ️ {filtrados} comentário(s) de automação foram ocultados")
            
            # FILTROS INTERATIVOS
            st.markdown("##### 🔍 Filtrar comentários:")
            
            # Filtro de busca por texto
            col_busca, col_autor = st.columns([2, 1])
            with col_busca:
                busca_texto = st.text_input("🔎 Buscar no texto:", placeholder="Digite para filtrar...", key="busca_comentario_texto")
            
            # Filtro por autor
            autores = list(set([c.get('autor', 'Desconhecido') for c in comentarios_filtrados]))
            autores.sort()
            with col_autor:
                autor_selecionado = st.selectbox("👤 Filtrar por autor:", ["Todos"] + autores, key="filtro_autor_comentario")
            
            # Filtros por tipo
            st.markdown("**Por tipo:**")
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                filtro_todos = st.checkbox("Todos", value=True, key="filtro_com_todos")
            with col2:
                filtro_bug = st.checkbox(f"🐛 Bug ({bugs})", value=False, key="filtro_com_bug", disabled=bugs==0)
            with col3:
                filtro_reprov = st.checkbox(f"❌ Reprov ({reprovacoes})", value=False, key="filtro_com_reprov", disabled=reprovacoes==0)
            with col4:
                filtro_imped = st.checkbox(f"🚫 Imped ({impedidos})", value=False, key="filtro_com_imped", disabled=impedidos==0)
            with col5:
                filtro_retorno = st.checkbox(f"🔄 Retorno ({retornos})", value=False, key="filtro_com_retorno", disabled=retornos==0)
            with col6:
                filtro_normal = st.checkbox(f"💬 Outros ({normais})", value=False, key="filtro_com_normal", disabled=normais==0)
            
            # Determina quais tipos exibir
            tipos_exibir = []
            if filtro_todos and not (filtro_bug or filtro_reprov or filtro_imped or filtro_retorno or filtro_normal):
                tipos_exibir = ['bug', 'reprovacao', 'impedido', 'retorno_dev', 'normal']
            else:
                if filtro_bug:
                    tipos_exibir.append('bug')
                if filtro_reprov:
                    tipos_exibir.append('reprovacao')
                if filtro_imped:
                    tipos_exibir.append('impedido')
                if filtro_retorno:
                    tipos_exibir.append('retorno_dev')
                if filtro_normal:
                    tipos_exibir.append('normal')
            
            # Se nenhum selecionado, mostra todos
            if not tipos_exibir:
                tipos_exibir = ['bug', 'reprovacao', 'impedido', 'retorno_dev', 'normal']
            
            # Filtra comentários por tipo
            comentarios_exibir = [c for c in comentarios_filtrados if c.get('classificacao') in tipos_exibir]
            
            # Aplica filtro de busca por texto
            if busca_texto:
                busca_lower = busca_texto.lower()
                comentarios_exibir = [c for c in comentarios_exibir if busca_lower in c.get('texto', '').lower()]
            
            # Aplica filtro por autor
            if autor_selecionado and autor_selecionado != "Todos":
                comentarios_exibir = [c for c in comentarios_exibir if c.get('autor') == autor_selecionado]
            
            st.markdown("---")
            
            # Legenda
            st.markdown("""
            <div style='display: flex; gap: 12px; margin-bottom: 15px; flex-wrap: wrap; font-size: 0.85em;'>
                <span>🐛 <b style='color: #dc2626;'>Bug</b></span>
                <span>❌ <b style='color: #ea580c;'>Reprovação</b></span>
                <span>🚫 <b style='color: #9333ea;'>Impedimento</b></span>
                <span>🔄 <b style='color: #0891b2;'>Retorno DEV</b></span>
                <span>💬 <b style='color: #64748b;'>Contexto</b></span>
            </div>
            """, unsafe_allow_html=True)
            
            if not comentarios_exibir:
                st.info("Nenhum comentário encontrado para os filtros selecionados.")
            else:
                st.caption(f"Exibindo {len(comentarios_exibir)} de {total_filtrado} comentários")
            
            for i, com in enumerate(comentarios_exibir):
                # Formata a data
                try:
                    data_com = datetime.fromisoformat(com['data'].replace('Z', '+00:00'))
                    data_formatada = data_com.strftime('%d/%m/%Y %H:%M')
                except:
                    data_formatada = com['data'][:10] if com['data'] else 'Data desconhecida'
                
                # Define cores e badges baseado na classificação
                classificacao = com.get('classificacao', 'normal')
                numero_evento = com.get('numero_evento', '')
                contexto = com.get('contexto', '')
                
                if classificacao == 'bug':
                    cor_borda = '#dc2626'
                    cor_fundo = '#fef2f2'
                    cor_avatar = '#dc2626'
                    badge = f'<span style="background: #dc2626; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; font-weight: bold;">🐛 Bug #{numero_evento}</span>'
                elif classificacao == 'reprovacao':
                    cor_borda = '#ea580c'
                    cor_fundo = '#fff7ed'
                    cor_avatar = '#ea580c'
                    badge = f'<span style="background: #ea580c; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; font-weight: bold;">❌ Reprovação #{numero_evento}</span>'
                elif classificacao == 'impedido':
                    cor_borda = '#9333ea'
                    cor_fundo = '#faf5ff'
                    cor_avatar = '#9333ea'
                    badge = f'<span style="background: #9333ea; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; font-weight: bold;">🚫 Impedimento #{numero_evento}</span>'
                elif classificacao == 'retorno_dev':
                    cor_borda = '#0891b2'
                    cor_fundo = '#ecfeff'
                    cor_avatar = '#0891b2'
                    contexto_badge = f' <span style="background: #e2e8f0; color: #475569; padding: 2px 6px; border-radius: 8px; font-size: 0.7em; margin-left: 5px;">{contexto}</span>' if contexto else ''
                    badge = f'<span style="background: #0891b2; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; font-weight: bold;">🔄 Retorno #{numero_evento}</span>{contexto_badge}'
                else:
                    cor_borda = '#94a3b8'
                    cor_fundo = '#f8fafc'
                    cor_avatar = '#64748b'
                    if contexto:
                        badge = f'<span style="background: #e2e8f0; color: #475569; padding: 3px 10px; border-radius: 12px; font-size: 0.75em;">{contexto}</span>'
                    else:
                        badge = ''
                
                st.markdown(f"""
<div style='background: {cor_fundo}; padding: 14px 16px; border-radius: 10px; margin-bottom: 12px; border-left: 4px solid {cor_borda}; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'>
    <div style='display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-bottom: 10px;'>
        <div style='display: flex; align-items: center; gap: 10px;'>
            <div style='width: 36px; height: 36px; border-radius: 50%; background: {cor_avatar}; 
                        display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 0.9em;'>
                {com['autor'][0].upper() if com['autor'] else '?'}
            </div>
            <div>
                <strong style='color: #1e293b; font-size: 0.95em;'>{com['autor']}</strong>
                <div style='color: #64748b; font-size: 0.8em;'>{data_formatada}</div>
            </div>
        </div>
        <div>{badge}</div>
    </div>
    <div style='color: #334155; font-size: 0.9em; line-height: 1.6; padding-left: 46px; white-space: pre-wrap;'>{com['texto'][:1000]}{'...' if len(com['texto']) > 1000 else ''}</div>
</div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        filtrados_msg = f" ({filtrados} de automação ocultados)" if filtrados > 0 else ""
        with st.expander(f"💬 **Comentários (0)**{filtrados_msg}", expanded=False):
            if filtrados > 0:
                st.caption(f"ℹ️ Este card tem {filtrados} comentário(s) de automação que foram ocultados.")
            else:
                st.caption("Nenhum comentário de usuário neste card.")


def filtrar_comentarios_pb(comentarios: List[Dict]) -> List[Dict]:
    """
    Filtra e classifica comentários para Product Backlog (PB).
    Tags específicas para contexto de produto, não de QA.
    
    Classificações PB:
    - decisao: Aprovações, decisões, definições
    - duvida: Perguntas, questionamentos
    - requisito: Detalhamento, escopo, critérios
    - alinhamento: Reuniões, alinhamentos
    - normal: Comentários gerais
    """
    if not comentarios:
        return []
    
    # Padrões de automação a serem filtrados
    padroes_automacao = [
        "mentioned this issue in a commit",
        "mentioned this issue in a branch",
        "merge branch",
        "pushed a commit",
        "created a branch",
        "deleted branch",
        "opened a pull request",
        "closed a pull request",
        "merged a pull request",
        "mentioned this issue in a pull request",
        "linked a pull request",
        "connected this issue",
        "referenced this issue",
        "/confirmationcall on branch",
        "on branch sd-",
        "on branch SD-",
        "on branch pb-",
        "on branch PB-",
    ]
    
    # Padrões para DECISÃO/APROVAÇÃO
    padroes_decisao = [
        "aprovado",
        "aprovação",
        "aprovei",
        "aprovar",
        "decidido",
        "decisão",
        "definido",
        "definição",
        "definimos",
        "ficou definido",
        "ficou decidido",
        "vamos fazer",
        "vamos seguir",
        "seguir com",
        "ok para",
        "pode seguir",
        "pode prosseguir",
        "liberado",
        "confirmado",
        "confirmação",
        "validado pelo",
        "validado por",
        "alinhado com",
        "combinado",
        "acordado",
    ]
    
    # Padrões para DÚVIDA/PERGUNTA
    padroes_duvida = [
        "dúvida",
        "duvida",
        "pergunta",
        "questão",
        "questao",
        "?",  # comentários com interrogação
        "não entendi",
        "não ficou claro",
        "poderia esclarecer",
        "pode explicar",
        "como funciona",
        "como seria",
        "qual seria",
        "qual é",
        "o que seria",
        "o que significa",
        "faz sentido",
        "seria possível",
        "é possível",
        "tem como",
        "precisamos entender",
        "preciso entender",
        "precisamos definir",
        "aguardando esclarecimento",
        "aguardando retorno",
        "favor esclarecer",
        "por favor esclarecer",
    ]
    
    # Padrões para REQUISITO/ESCOPO
    padroes_requisito = [
        "requisito",
        "critério de aceite",
        "critérios de aceite",
        "criterio de aceite",
        "ac:",
        "escopo",
        "funcionalidade",
        "deve permitir",
        "deve ser possível",
        "o sistema deve",
        "o usuário deve",
        "o usuário poderá",
        "será necessário",
        "deverá",
        "regra de negócio",
        "regra:",
        "detalhamento",
        "especificação",
        "fluxo:",
        "comportamento esperado",
        "cenário de uso",
        "caso de uso",
        "user story",
        "história de usuário",
        "como um",
        "eu quero",
        "para que",
    ]
    
    # Padrões para ALINHAMENTO
    padroes_alinhamento = [
        "alinhamento",
        "alinhado",
        "alinhei",
        "reunião",
        "conversei",
        "conversamos",
        "falei com",
        "falamos com",
        "discutimos",
        "discutido",
        "apresentamos",
        "apresentado",
        "feedback do",
        "retorno do",
        "segundo o",
        "conforme",
        "de acordo com",
        "stakeholder",
        "product owner",
        "po disse",
        "cliente disse",
        "cliente solicitou",
        "solicitação do",
        "pedido do",
    ]
    
    comentarios_filtrados = []
    
    for com in comentarios:
        texto_lower = com.get('texto', '').lower()
        autor = com.get('autor', '').lower()
        
        # Verifica se é automação
        eh_automacao = False
        for padrao in padroes_automacao:
            if padrao.lower() in texto_lower:
                eh_automacao = True
                break
        
        if any(bot in autor for bot in ['automation', 'bot', 'github', 'bitbucket', 'gitlab', 'jira']):
            eh_automacao = True
        
        if eh_automacao:
            continue
        
        # Classifica (ordem de prioridade)
        classificacao = 'normal'
        
        # 1. Decisão
        for padrao in padroes_decisao:
            if padrao in texto_lower:
                classificacao = 'decisao'
                break
        
        # 2. Dúvida (se não foi decisão)
        if classificacao == 'normal':
            for padrao in padroes_duvida:
                if padrao in texto_lower:
                    classificacao = 'duvida'
                    break
        
        # 3. Requisito
        if classificacao == 'normal':
            for padrao in padroes_requisito:
                if padrao in texto_lower:
                    classificacao = 'requisito'
                    break
        
        # 4. Alinhamento
        if classificacao == 'normal':
            for padrao in padroes_alinhamento:
                if padrao in texto_lower:
                    classificacao = 'alinhamento'
                    break
        
        # Parse da data
        try:
            data_parsed = datetime.fromisoformat(com['data'].replace('Z', '+00:00')).replace(tzinfo=None)
        except:
            data_parsed = datetime.now()
        
        comentarios_filtrados.append({
            **com,
            'classificacao': classificacao,
            'data_parsed': data_parsed,
        })
    
    # Ordena por data
    comentarios_filtrados.sort(key=lambda x: x['data_parsed'])
    
    # Numera os eventos
    contadores = {'decisao': 0, 'duvida': 0, 'requisito': 0, 'alinhamento': 0}
    for com in comentarios_filtrados:
        if com['classificacao'] in contadores:
            contadores[com['classificacao']] += 1
            com['numero_evento'] = contadores[com['classificacao']]
    
    return comentarios_filtrados


def exibir_comentarios_pb(comentarios: List[Dict]):
    """Exibe comentários para cards de Product Backlog (PB) com tags de produto."""
    
    comentarios_filtrados = filtrar_comentarios_pb(comentarios)
    
    total_original = len(comentarios) if comentarios else 0
    total_filtrado = len(comentarios_filtrados)
    filtrados = total_original - total_filtrado
    
    # Conta por classificação
    decisoes = sum(1 for c in comentarios_filtrados if c.get('classificacao') == 'decisao')
    duvidas = sum(1 for c in comentarios_filtrados if c.get('classificacao') == 'duvida')
    requisitos = sum(1 for c in comentarios_filtrados if c.get('classificacao') == 'requisito')
    alinhamentos = sum(1 for c in comentarios_filtrados if c.get('classificacao') == 'alinhamento')
    normais = sum(1 for c in comentarios_filtrados if c.get('classificacao') == 'normal')
    
    if comentarios_filtrados and len(comentarios_filtrados) > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Monta título com contagens
        titulo_extra = []
        if decisoes > 0:
            titulo_extra.append(f"✅ {decisoes}")
        if duvidas > 0:
            titulo_extra.append(f"❓ {duvidas}")
        if requisitos > 0:
            titulo_extra.append(f"📋 {requisitos}")
        if alinhamentos > 0:
            titulo_extra.append(f"🤝 {alinhamentos}")
        titulo_sufixo = f" | {' '.join(titulo_extra)}" if titulo_extra else ""
        
        with st.expander(f"💬 **Comentários ({total_filtrado})**{titulo_sufixo}", expanded=True):
            if filtrados > 0:
                st.caption(f"ℹ️ {filtrados} comentário(s) de automação foram ocultados")
            
            # FILTROS INTERATIVOS para PB
            st.markdown("##### 🔍 Filtrar comentários:")
            
            # Filtro de busca por texto e autor
            col_busca, col_autor = st.columns([2, 1])
            with col_busca:
                busca_texto_pb = st.text_input("🔎 Buscar no texto:", placeholder="Digite para filtrar...", key="busca_comentario_texto_pb")
            
            autores_pb = list(set([c.get('autor', 'Desconhecido') for c in comentarios_filtrados]))
            autores_pb.sort()
            with col_autor:
                autor_selecionado_pb = st.selectbox("👤 Filtrar por autor:", ["Todos"] + autores_pb, key="filtro_autor_comentario_pb")
            
            # Filtros por tipo
            st.markdown("**Por tipo:**")
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                filtro_todos = st.checkbox("Todos", value=True, key="filtro_pb_todos")
            with col2:
                filtro_decisao = st.checkbox(f"✅ Decisão ({decisoes})", value=False, key="filtro_pb_decisao", disabled=decisoes==0)
            with col3:
                filtro_duvida = st.checkbox(f"❓ Dúvida ({duvidas})", value=False, key="filtro_pb_duvida", disabled=duvidas==0)
            with col4:
                filtro_requisito = st.checkbox(f"📋 Requisito ({requisitos})", value=False, key="filtro_pb_requisito", disabled=requisitos==0)
            with col5:
                filtro_alinhamento = st.checkbox(f"🤝 Alinhamento ({alinhamentos})", value=False, key="filtro_pb_alinhamento", disabled=alinhamentos==0)
            with col6:
                filtro_normal = st.checkbox(f"💬 Outros ({normais})", value=False, key="filtro_pb_normal", disabled=normais==0)
            
            # Determina quais tipos exibir
            tipos_exibir = []
            if filtro_todos and not (filtro_decisao or filtro_duvida or filtro_requisito or filtro_alinhamento or filtro_normal):
                tipos_exibir = ['decisao', 'duvida', 'requisito', 'alinhamento', 'normal']
            else:
                if filtro_decisao:
                    tipos_exibir.append('decisao')
                if filtro_duvida:
                    tipos_exibir.append('duvida')
                if filtro_requisito:
                    tipos_exibir.append('requisito')
                if filtro_alinhamento:
                    tipos_exibir.append('alinhamento')
                if filtro_normal:
                    tipos_exibir.append('normal')
            
            if not tipos_exibir:
                tipos_exibir = ['decisao', 'duvida', 'requisito', 'alinhamento', 'normal']
            
            comentarios_exibir = [c for c in comentarios_filtrados if c.get('classificacao') in tipos_exibir]
            
            # Aplica filtro de busca por texto
            if busca_texto_pb:
                busca_lower = busca_texto_pb.lower()
                comentarios_exibir = [c for c in comentarios_exibir if busca_lower in c.get('texto', '').lower()]
            
            # Aplica filtro por autor
            if autor_selecionado_pb and autor_selecionado_pb != "Todos":
                comentarios_exibir = [c for c in comentarios_exibir if c.get('autor') == autor_selecionado_pb]
            
            st.markdown("---")
            
            # Legenda para PB
            st.markdown("""
            <div style='display: flex; gap: 12px; margin-bottom: 15px; flex-wrap: wrap; font-size: 0.85em;'>
                <span>✅ <b style='color: #16a34a;'>Decisão</b></span>
                <span>❓ <b style='color: #ca8a04;'>Dúvida</b></span>
                <span>📋 <b style='color: #2563eb;'>Requisito</b></span>
                <span>🤝 <b style='color: #7c3aed;'>Alinhamento</b></span>
                <span>💬 <b style='color: #64748b;'>Geral</b></span>
            </div>
            """, unsafe_allow_html=True)
            
            if not comentarios_exibir:
                st.info("Nenhum comentário encontrado para os filtros selecionados.")
            else:
                st.caption(f"Exibindo {len(comentarios_exibir)} de {total_filtrado} comentários")
            
            for i, com in enumerate(comentarios_exibir):
                try:
                    data_com = datetime.fromisoformat(com['data'].replace('Z', '+00:00'))
                    data_formatada = data_com.strftime('%d/%m/%Y %H:%M')
                except:
                    data_formatada = com['data'][:10] if com['data'] else 'Data desconhecida'
                
                classificacao = com.get('classificacao', 'normal')
                numero_evento = com.get('numero_evento', '')
                
                if classificacao == 'decisao':
                    cor_borda = '#16a34a'  # Verde
                    cor_fundo = '#f0fdf4'
                    cor_avatar = '#16a34a'
                    badge = f'<span style="background: #16a34a; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; font-weight: bold;">✅ Decisão #{numero_evento}</span>'
                elif classificacao == 'duvida':
                    cor_borda = '#ca8a04'  # Amarelo escuro
                    cor_fundo = '#fefce8'
                    cor_avatar = '#ca8a04'
                    badge = f'<span style="background: #ca8a04; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; font-weight: bold;">❓ Dúvida #{numero_evento}</span>'
                elif classificacao == 'requisito':
                    cor_borda = '#2563eb'  # Azul
                    cor_fundo = '#eff6ff'
                    cor_avatar = '#2563eb'
                    badge = f'<span style="background: #2563eb; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; font-weight: bold;">📋 Requisito #{numero_evento}</span>'
                elif classificacao == 'alinhamento':
                    cor_borda = '#7c3aed'  # Roxo
                    cor_fundo = '#f5f3ff'
                    cor_avatar = '#7c3aed'
                    badge = f'<span style="background: #7c3aed; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; font-weight: bold;">🤝 Alinhamento #{numero_evento}</span>'
                else:
                    cor_borda = '#94a3b8'
                    cor_fundo = '#f8fafc'
                    cor_avatar = '#64748b'
                    badge = ''
                
                st.markdown(f"""
<div style='background: {cor_fundo}; padding: 14px 16px; border-radius: 10px; margin-bottom: 12px; border-left: 4px solid {cor_borda}; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'>
    <div style='display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-bottom: 10px;'>
        <div style='display: flex; align-items: center; gap: 10px;'>
            <div style='width: 36px; height: 36px; border-radius: 50%; background: {cor_avatar}; 
                        display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 0.9em;'>
                {com['autor'][0].upper() if com['autor'] else '?'}
            </div>
            <div>
                <strong style='color: #1e293b; font-size: 0.95em;'>{com['autor']}</strong>
                <div style='color: #64748b; font-size: 0.8em;'>{data_formatada}</div>
            </div>
        </div>
        <div>{badge}</div>
    </div>
    <div style='color: #334155; font-size: 0.9em; line-height: 1.6; padding-left: 46px; white-space: pre-wrap;'>{com['texto'][:1000]}{'...' if len(com['texto']) > 1000 else ''}</div>
</div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        filtrados_msg = f" ({filtrados} de automação ocultados)" if filtrados > 0 else ""
        with st.expander(f"💬 **Comentários (0)**{filtrados_msg}", expanded=False):
            if filtrados > 0:
                st.caption(f"ℹ️ Este card tem {filtrados} comentário(s) de automação que foram ocultados.")
            else:
                st.caption("Nenhum comentário neste card.")


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
        min-height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: center;
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
    .card-sublabel { font-size: 12px; opacity: 0.6; margin-top: 3px; min-height: 16px; }
    
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
    
    /* Scroll container para listagens */
    .scroll-container {
        max-height: 450px;
        overflow-y: auto;
        padding-right: 8px;
        margin: 10px 0;
        scrollbar-width: thin;
        scrollbar-color: #cbd5e1 #f1f5f9;
    }
    .scroll-container::-webkit-scrollbar {
        width: 6px;
    }
    .scroll-container::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 3px;
    }
    .scroll-container::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 3px;
    }
    .scroll-container::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    
    /* Card de listagem padrão */
    .card-lista {
        background: rgba(100, 100, 100, 0.05);
        padding: 12px 15px;
        margin: 8px 0;
        border-radius: 8px;
        border-left: 4px solid #64748b;
        transition: all 0.2s ease;
    }
    .card-lista:hover {
        transform: translateX(3px);
        background: rgba(100, 100, 100, 0.1);
    }
    /* Variantes coloridas - herdam estilos base */
    .card-lista-amarelo, .card-lista-verde, .card-lista-azul, .card-lista-roxo, .card-lista-vermelho, .card-lista-laranja {
        padding: 12px 15px;
        margin: 8px 0;
        border-radius: 8px;
        border-left: 4px solid;
        transition: all 0.2s ease;
    }
    .card-lista-amarelo:hover, .card-lista-verde:hover, .card-lista-azul:hover, .card-lista-roxo:hover, .card-lista-vermelho:hover, .card-lista-laranja:hover {
        transform: translateX(3px);
        filter: brightness(0.95);
    }
    .card-lista-amarelo { border-left-color: #f59e0b; background: rgba(245, 158, 11, 0.08); }
    .card-lista-verde { border-left-color: #22c55e; background: rgba(34, 197, 94, 0.08); }
    .card-lista-azul { border-left-color: #3b82f6; background: rgba(59, 130, 246, 0.08); }
    .card-lista-roxo { border-left-color: #8b5cf6; background: rgba(139, 92, 246, 0.08); }
    .card-lista-vermelho { border-left-color: #ef4444; background: rgba(239, 68, 68, 0.08); }
    .card-lista-laranja { border-left-color: #f97316; background: rgba(249, 115, 22, 0.08); }
    
    /* Hide Streamlit elements */
    #MainMenu, .stDeployButton { display: none !important; }
    </style>
    """, unsafe_allow_html=True)


def get_tooltip_help(tooltip_key: str) -> str:
    """Retorna texto de ajuda para st.metric (aparece no ícone ?)."""
    if tooltip_key not in TOOLTIPS:
        return ""
    
    tip = TOOLTIPS[tooltip_key]
    help_text = f"{tip['titulo']}: {tip['descricao']}"
    if tip.get('formula'):
        help_text += f" | Fórmula: {tip['formula']}"
    return help_text


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
            <p class="nina-title"><span class="nina-highlight">NinaDash</span> — Dashboard de Qualidade e Decisão de Software</p>
            <p class="nina-subtitle">📊 Visibilidade, métricas e decisões inteligentes para todo o time</p>
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


def formatar_tempo_relativo(dt: datetime) -> str:
    """
    Formata uma datetime como tempo relativo (ex: "há 5 min", "há 2h", "há 3 dias").
    
    Args:
        dt: datetime a ser formatada
        
    Returns:
        String formatada com tempo relativo
    """
    if dt is None or pd.isna(dt):
        return ""
    
    agora = datetime.now()
    
    # Garante que dt seja datetime
    if isinstance(dt, str):
        try:
            dt = pd.to_datetime(dt)
        except:
            return ""
    
    # Se dt tem timezone, remove para comparação
    if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    
    diff = agora - dt
    segundos = diff.total_seconds()
    
    if segundos < 0:
        return "agora"
    elif segundos < 60:
        return "agora"
    elif segundos < 3600:  # menos de 1 hora
        minutos = int(segundos / 60)
        return f"há {minutos} min"
    elif segundos < 86400:  # menos de 1 dia
        horas = int(segundos / 3600)
        return f"há {horas}h"
    elif segundos < 604800:  # menos de 1 semana
        dias = int(segundos / 86400)
        return f"há {dias}d"
    elif segundos < 2592000:  # menos de 30 dias
        semanas = int(segundos / 604800)
        return f"há {semanas} sem"
    else:
        meses = int(segundos / 2592000)
        return f"há {meses} mês" if meses == 1 else f"há {meses} meses"


def criar_card_metrica(valor: str, titulo: str, cor: str = "blue", subtitulo: str = "", tooltip_key: str = ""):
    """Cria card de métrica visual. tooltip_key é ignorado (usar st.metric com help para tooltips)."""
    # Sempre mostra sublabel para manter altura uniforme
    sublabel_content = subtitulo if subtitulo else "&nbsp;"
    st.markdown(f"""
    <div class="status-card status-{cor}">
        <p class="big-number">{valor}</p>
        <p class="card-label">{titulo}</p>
        <p class="card-sublabel">{sublabel_content}</p>
    </div>
    """, unsafe_allow_html=True)


def gerar_html_card_ticket(row: dict, compacto: bool = False) -> str:
    """Gera HTML de um card de ticket (retorna string, não renderiza)."""
    bugs = row.get('bugs', 0)
    risco = 'high' if bugs >= 3 else 'medium' if bugs >= 1 else 'low'
    card_link = card_link_com_popup(row.get('ticket_id', ''))
    titulo = str(row.get('titulo', ''))[:60] + ('...' if len(str(row.get('titulo', ''))) > 60 else '')
    cor_bug = '#ef4444' if bugs >= 3 else '#f97316' if bugs >= 1 else '#22c55e'
    
    # Ícone de bugs com Tabler
    bug_icon = gerar_icone_tabler_html('bug', tamanho=16, cor=cor_bug)
    
    if compacto:
        return f'<div class="ticket-card ticket-risk-{risco}"><div style="display: flex; justify-content: space-between; align-items: center;">{card_link}<span style="opacity: 0.7;">{row.get("sp", 0)} SP | {bug_icon}{bugs}</span></div><p style="margin: 5px 0 0 0; font-size: 13px; opacity: 0.9;">{titulo}</p></div>'
    else:
        status_badge = gerar_badge_status(row.get("status", "N/A"))
        return f'<div class="ticket-card ticket-risk-{risco}"><div style="display: flex; justify-content: space-between;">{card_link}<span style="color: {cor_bug}; font-weight: bold;">{bug_icon}{bugs} bugs</span></div><p style="margin: 8px 0;">{row.get("titulo", "")}</p><p style="font-size: 12px; opacity: 0.8;"><b>Dev:</b> {row.get("desenvolvedor", "N/A")} | <b>QA:</b> {row.get("qa", "N/A")} | <b>SP:</b> {row.get("sp", 0)} | {status_badge}</p></div>'


def mostrar_card_ticket(row: dict, compacto: bool = False):
    """Mostra card de ticket COM LINK para Jira."""
    html = gerar_html_card_ticket(row, compacto)
    st.markdown(html, unsafe_allow_html=True)


def mostrar_lista_tickets_completa(items: list, titulo: str, mostrar_todos: bool = False, max_height: int = 450):
    """
    Mostra lista de tickets com scroll individual e opção de ver TODOS.
    
    Args:
        items: Lista de dicionários com dados dos cards
        titulo: Título da seção
        mostrar_todos: Se True, mostra todos os cards (sem limite inicial)
        max_height: Altura máxima do container de scroll (default 450px)
    """
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
        
        # Construir HTML completo em string única (necessário para scroll funcionar)
        html_lista = f'<div class="scroll-container" style="max-height: {max_height}px;">'
        
        for i, item in enumerate(items[:limite]):
            if isinstance(item, dict):
                html_lista += gerar_html_card_ticket(item, compacto=True)
            elif isinstance(item, pd.Series):
                html_lista += gerar_html_card_ticket(item.to_dict(), compacto=True)
        
        html_lista += '</div>'
        st.markdown(html_lista, unsafe_allow_html=True)
        
        if not mostrar_todos and total > 5:
            st.caption(f"📌 Mais {total - 5} cards ocultos. Marque acima para ver todos.")


def mostrar_lista_df_completa(df: pd.DataFrame, titulo: str):
    """Mostra lista de tickets de um DataFrame com opção de ver todos."""
    if df.empty:
        st.info(f"Nenhum card em: {titulo}")
        return
    
    items = df.to_dict('records')
    mostrar_lista_tickets_completa(items, titulo)


def renderizar_lista_com_scroll(df: pd.DataFrame, titulo: str = None, max_height: int = 400, 
                                 cor_classe: str = "", mostrar_checkbox: bool = True,
                                 limite_inicial: int = 20, key_prefix: str = "lista",
                                 campos_customizados: dict = None):
    """
    Renderiza uma lista de cards com scroll individual usando design padronizado.
    
    Args:
        df: DataFrame com os cards
        titulo: Título opcional da seção (se None, não mostra título)
        max_height: Altura máxima do container de scroll
        cor_classe: Classe CSS de cor (amarelo, verde, azul, roxo, vermelho, laranja)
        mostrar_checkbox: Se True, mostra checkbox "Ver todos"
        limite_inicial: Limite inicial de cards (se checkbox ativo)
        key_prefix: Prefixo para keys do Streamlit (evitar duplicatas)
        campos_customizados: Dict com campos customizados a exibir {campo: label}
    
    Returns:
        None (renderiza diretamente no Streamlit)
    """
    if df.empty:
        st.info("Nenhum card encontrado.")
        return
    
    total = len(df)
    
    # Checkbox para ver todos
    mostrar_todos = False
    if mostrar_checkbox and total > limite_inicial:
        mostrar_todos = st.checkbox(
            f"📋 Ver todos os {total} cards", 
            key=f"{key_prefix}_ver_todos_{titulo or 'lista'}",
            value=False
        )
    else:
        mostrar_todos = True
    
    limite = total if mostrar_todos else min(limite_inicial, total)
    
    # Título se especificado
    if titulo:
        st.markdown(f"##### {titulo} ({total})")
    
    # Container com scroll
    cards_html = f'<div class="scroll-container" style="max-height: {max_height}px;">'
    
    for _, card in df.head(limite).iterrows():
        projeto = card.get('projeto', 'SD')
        tipo = card.get('tipo', 'TAREFA')
        tipo_cor = "#ef4444" if tipo == "HOTFIX" else "#f97316" if tipo == "BUG" else "#6366f1" if tipo == "SUGESTÃO" else "#64748b"
        
        # Responsável (prioridade: responsavel > desenvolvedor > qa > relator)
        responsavel = card.get('responsavel') or card.get('desenvolvedor') or card.get('qa') or card.get('relator', 'N/A')
        if not responsavel or responsavel == 'Não atribuído':
            responsavel = card.get('relator', 'N/A')
        
        titulo_card = str(card.get('titulo', card.get('resumo', '')))[:80]
        ticket_id = card.get('ticket_id', '')
        status = card.get('status', '')
        
        # Classe de cor
        classe_cor = f"card-lista-{cor_classe}" if cor_classe else "card-lista"
        
        # Popup do card
        popup_html = card_link_com_popup(ticket_id, projeto)
        
        # Campos customizados
        info_extra = ""
        if campos_customizados:
            extras = []
            for campo, label in campos_customizados.items():
                valor = card.get(campo, '')
                if valor and valor != 'N/A' and valor != 'Não atribuído':
                    extras.append(f"<b>{label}:</b> {valor}")
            if extras:
                info_extra = f'<div style="font-size: 11px; color: #64748b; margin-top: 4px;">{" | ".join(extras)}</div>'
        
        cards_html += f'''
        <div class="{classe_cor}">
            <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-bottom: 4px;">
                <span style="background: #64748b; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">{projeto}</span>
                <span style="background: {tipo_cor}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">{tipo}</span>
                {popup_html}
                <span style="background: #e5e7eb; color: #374151; padding: 2px 6px; border-radius: 3px; font-size: 10px; margin-left: auto;">{status[:20]}</span>
            </div>
            <div style="font-size: 13px; color: #374151; line-height: 1.4;">{titulo_card}{"..." if len(str(card.get("titulo", ""))) > 80 else ""}</div>
            <div style="font-size: 11px; color: #64748b; margin-top: 4px;">👤 {responsavel}</div>
            {info_extra}
        </div>'''
    
    cards_html += '</div>'
    
    st.markdown(cards_html, unsafe_allow_html=True)
    
    if not mostrar_todos and total > limite_inicial:
        st.caption(f"📌 Mais {total - limite_inicial} cards ocultos. Marque acima para ver todos.")


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

def aba_clientes(df_todos: pd.DataFrame):
    """Aba de análise por Clientes/Temas (usa todos os projetos, ignora filtro de projeto)."""
    st.markdown("### 🏢 Análise por Cliente/Tema")
    st.caption("Visualize métricas, responsáveis e histórico de cards por cliente")
    
    # ===== AVISO SOBRE OS DADOS =====
    st.info("📊 **Esta aba mostra dados de TODOS os projetos** (SD, QA, PB, VALPROD) independentemente do filtro da barra lateral.")
    
    # Verifica se há cliente na URL para compartilhamento (link compartilhado)
    cliente_url = st.query_params.get("cliente", None)
    
    # Verifica se a coluna temas existe
    if 'temas' not in df_todos.columns:
        st.warning("⚠️ Dados de clientes/temas não disponíveis")
        return
    
    # Explode temas para análise
    df_temas_todos = df_todos.explode('temas')
    df_temas_todos = df_temas_todos[df_temas_todos['temas'].notna() & (df_temas_todos['temas'] != '') & (df_temas_todos['temas'] != 'Sem tema')]
    
    # Conta cards internos (nina, interna) ANTES de filtrar
    cards_internos = df_temas_todos[df_temas_todos['temas'].str.lower().str.strip().isin([t.lower() for t in TEMAS_NAO_CLIENTES])]
    total_cards_internos = len(cards_internos)
    
    # Remove temas internos que não são clientes (ex: "nina", "interna")
    # Esses são mantidos no sistema mas não aparecem na análise de clientes
    df_temas = df_temas_todos[~df_temas_todos['temas'].str.lower().str.strip().isin([t.lower() for t in TEMAS_NAO_CLIENTES])]
    
    # Informa sobre cards internos excluídos
    if total_cards_internos > 0:
        st.info(f"ℹ️ **{total_cards_internos} cards internos** (nina, interna) não são exibidos aqui pois beneficiam todos os clientes.")
    
    if df_temas.empty:
        st.info("ℹ️ Nenhum card com cliente/tema definido no período")
        return
    
    # ===== DETECTAR DESENVOLVIMENTO PAGO (baseado no tipo ORIGINAL do ticket do Jira) =====
    def is_desenvolvimento_pago(tipo_original):
        """Verifica se o card é desenvolvimento pago com base no tipo original do Jira."""
        if not tipo_original or (isinstance(tipo_original, float) and pd.isna(tipo_original)):
            return False
        tipo_lower = str(tipo_original).lower().strip()
        # O tipo exato é "Desenvolvimento Pago" 
        return 'desenvolvimento pago' in tipo_lower
    
    # Adiciona coluna de desenvolvimento pago (baseado no tipo ORIGINAL do Jira, não o simplificado)
    if 'tipo_original' in df_temas.columns:
        df_temas['dev_pago'] = df_temas['tipo_original'].apply(is_desenvolvimento_pago)
    else:
        df_temas['dev_pago'] = False
    
    # Lista de clientes únicos ordenados por frequência
    clientes_count = df_temas['temas'].value_counts()
    clientes_unicos = clientes_count.index.tolist()
    
    # Determinar índice inicial baseado na URL (se veio de link compartilhado)
    opcoes_cliente = ["👀 Visão Geral do Time"] + clientes_unicos
    indice_inicial = 0
    if cliente_url and cliente_url in clientes_unicos:
        indice_inicial = opcoes_cliente.index(cliente_url)
    
    # ===== SELETOR DE CLIENTE (igual QA/Dev) =====
    cliente_selecionado = st.selectbox(
        "🔍 Selecione ou pesquise um cliente",
        options=opcoes_cliente,
        index=indice_inicial,
        key="select_cliente_aba"
    )
    
    st.markdown("---")
    
    if cliente_selecionado == "👀 Visão Geral do Time":
        # ===== VISÃO GERAL - KPIs GLOBAIS =====
        with st.expander("📊 Indicadores Gerais de Clientes", expanded=True):
            col1, col2, col3, col4, col5 = st.columns(5)
            
            total_cards = len(df_temas)
            total_clientes = len(clientes_unicos)
            total_dev_pago = df_temas['dev_pago'].sum() if 'dev_pago' in df_temas.columns else 0
            total_sp = int(df_temas['sp'].sum()) if 'sp' in df_temas.columns else 0
            total_concluidos = len(df_temas[df_temas['status_cat'] == 'done']) if 'status_cat' in df_temas.columns else 0
            
            with col1:
                criar_card_metrica(str(total_clientes), "Clientes Ativos", "blue")
            with col2:
                criar_card_metrica(str(total_cards), "Total de Cards", "blue")
            with col3:
                pct_pago = int(total_dev_pago / total_cards * 100) if total_cards > 0 else 0
                cor = 'green' if pct_pago >= 30 else 'yellow' if pct_pago >= 15 else 'red'
                criar_card_metrica(f"{total_dev_pago} ({pct_pago}%)", "💰 Dev. Pago", cor)
            with col4:
                criar_card_metrica(str(total_sp), "Story Points", "blue")
            with col5:
                pct_concluido = int(total_concluidos / total_cards * 100) if total_cards > 0 else 0
                cor = 'green' if pct_concluido >= 70 else 'yellow' if pct_concluido >= 40 else 'red'
                criar_card_metrica(f"{pct_concluido}%", "Conclusão", cor)
        
        # ===== TOP CLIENTES =====
        st.markdown("#### 📊 Top 15 Clientes por Volume de Cards")
        
        # Ranking de clientes com desenvolvimento pago
        # Constrói dicionário de agregação dinamicamente com colunas existentes
        agg_dict = {'ticket_id': 'count'}
        if 'sp' in df_temas.columns:
            agg_dict['sp'] = 'sum'
        if 'bugs' in df_temas.columns:
            agg_dict['bugs'] = 'sum'
        if 'status_cat' in df_temas.columns:
            agg_dict['status_cat'] = lambda x: (x == 'done').sum()
        if 'dev_pago' in df_temas.columns:
            agg_dict['dev_pago'] = 'sum'
        if 'projeto' in df_temas.columns:
            agg_dict['projeto'] = lambda x: ', '.join(sorted(x.unique()))
        
        ranking_clientes = df_temas.groupby('temas').agg(agg_dict).reset_index()
        
        # Renomeia colunas baseado nas que existem
        col_names = ['Cliente', 'Cards']
        if 'sp' in df_temas.columns:
            col_names.append('SP Total')
        if 'bugs' in df_temas.columns:
            col_names.append('Bugs')
        if 'status_cat' in df_temas.columns:
            col_names.append('Concluídos')
        if 'dev_pago' in df_temas.columns:
            col_names.append('Dev Pago')
        if 'projeto' in df_temas.columns:
            col_names.append('Projetos')
        ranking_clientes.columns = col_names
        
        if 'Concluídos' in ranking_clientes.columns:
            ranking_clientes['% Concluído'] = (ranking_clientes['Concluídos'] / ranking_clientes['Cards'] * 100).round(0).astype(int)
        else:
            ranking_clientes['% Concluído'] = 0
        ranking_clientes = ranking_clientes.sort_values('Cards', ascending=False).head(15)
        
        # Layout com gráfico e tabela
        col_graf, col_tab = st.columns([1.2, 1])
        
        with col_graf:
            # Gráfico de barras horizontais
            fig = px.bar(
                ranking_clientes.sort_values('Cards', ascending=True),
                x='Cards', y='Cliente', orientation='h',
                color='% Concluído', color_continuous_scale='RdYlGn',
                title='Top 15 Clientes por Volume'
            )
            fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col_tab:
            # Tabela resumida - usa colunas disponíveis
            colunas_tabela = ['Cliente', 'Cards']
            if 'Dev Pago' in ranking_clientes.columns:
                colunas_tabela.append('Dev Pago')
            if 'SP Total' in ranking_clientes.columns:
                colunas_tabela.append('SP Total')
            colunas_tabela.append('% Concluído')
            if 'Projetos' in ranking_clientes.columns:
                colunas_tabela.append('Projetos')
            
            st.dataframe(
                ranking_clientes[colunas_tabela],
                hide_index=True, use_container_width=True, height=450
            )
        
        # ===== DESENVOLVIMENTO PAGO VS OUTROS =====
        if 'dev_pago' in df_temas.columns:
            st.markdown("---")
            st.markdown("#### 💰 Análise de Desenvolvimento Pago")
            st.caption("Cards com label indicando desenvolvimento pago")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de pizza: Pago vs Não Pago
                pago_count = df_temas.groupby('dev_pago').size().reset_index(name='Cards')
                pago_count['Categoria'] = pago_count['dev_pago'].apply(lambda x: '💰 Desenvolvimento Pago' if x else '🔧 Outros')
                
                fig_pago = px.pie(pago_count, values='Cards', names='Categoria',
                                  title='Distribuição: Pago vs Outros',
                                  color='Categoria',
                                  color_discrete_map={'💰 Desenvolvimento Pago': '#22c55e', '🔧 Outros': '#6b7280'})
                fig_pago.update_layout(height=350)
                st.plotly_chart(fig_pago, use_container_width=True)
            
            with col2:
                # Top clientes com mais desenvolvimento pago
                clientes_pago = df_temas[df_temas['dev_pago'] == True].groupby('temas').size().reset_index(name='Cards Pagos')
                clientes_pago = clientes_pago.sort_values('Cards Pagos', ascending=False).head(10)
                
                if not clientes_pago.empty:
                    fig_top_pago = px.bar(
                        clientes_pago,
                        x='temas', y='Cards Pagos',
                        title='Top 10 Clientes com Dev. Pago',
                        color='Cards Pagos', color_continuous_scale='Greens'
                    )
                    fig_top_pago.update_layout(height=350, xaxis_title="Cliente", xaxis_tickangle=45)
                    st.plotly_chart(fig_top_pago, use_container_width=True)
                else:
                    st.info("ℹ️ Nenhum card com label de desenvolvimento pago encontrado")
        
        # ===== CLIENTES COM MAIS BUGS =====
        st.markdown("---")
        st.markdown("#### 🐛 Clientes com Mais Bugs Encontrados")
        
        if 'bugs' in df_temas.columns:
            clientes_bugs = df_temas.groupby('temas')['bugs'].sum().reset_index()
            clientes_bugs = clientes_bugs[clientes_bugs['bugs'] > 0].sort_values('bugs', ascending=False).head(10)
            
            if not clientes_bugs.empty:
                fig_bugs = px.bar(
                    clientes_bugs,
                    x='temas', y='bugs',
                    title='Top 10 Clientes por Bugs Encontrados',
                    color='bugs', color_continuous_scale='Reds'
                )
                fig_bugs.update_layout(height=350, xaxis_title="Cliente", yaxis_title="Bugs")
                st.plotly_chart(fig_bugs, use_container_width=True)
            else:
                st.info("ℹ️ Nenhum bug registrado para clientes no período")
        else:
            st.info("ℹ️ Dados de bugs não disponíveis")
    
    else:
        # ===== ANÁLISE DO CLIENTE SELECIONADO =====
        df_cliente = df_temas[df_temas['temas'] == cliente_selecionado]
        
        if df_cliente.empty:
            st.warning(f"Nenhum card encontrado para o cliente {cliente_selecionado}")
            return
        
        # Header com título e botão de compartilhamento (igual QA/Dev)
        import urllib.parse
        share_url = f"{NINADASH_URL}?cliente={urllib.parse.quote(cliente_selecionado)}"
        
        col_titulo, col_share = st.columns([3, 1])
        with col_titulo:
            st.markdown(f"### 🏢 {cliente_selecionado}")
        with col_share:
            # Botão Copiar Link usando components.html (mesmo padrão do QA/Dev)
            components.html(f"""
            <button id="copyBtnCliente" style="
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
                document.getElementById('copyBtnCliente').addEventListener('click', function() {{
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
        
        # ===== MÉTRICAS PRINCIPAIS =====
        total_cards = len(df_cliente)
        total_concluidos = len(df_cliente[df_cliente['status_cat'] == 'done']) if 'status_cat' in df_cliente.columns else 0
        total_em_andamento = len(df_cliente[df_cliente['status_cat'] == 'progress']) if 'status_cat' in df_cliente.columns else 0
        total_sp = int(df_cliente['sp'].sum()) if 'sp' in df_cliente.columns else 0
        total_bugs = int(df_cliente['bugs'].sum()) if 'bugs' in df_cliente.columns else 0
        total_dev_pago = df_cliente['dev_pago'].sum() if 'dev_pago' in df_cliente.columns else 0
        
        with st.expander("📊 Métricas do Cliente", expanded=True):
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                criar_card_metrica(str(total_cards), "📋 Total Cards", "blue")
            with col2:
                pct = int(total_concluidos / total_cards * 100) if total_cards > 0 else 0
                cor = 'green' if pct >= 70 else 'yellow' if pct >= 40 else 'red'
                criar_card_metrica(f"{total_concluidos} ({pct}%)", "✅ Concluídos", cor)
            with col3:
                criar_card_metrica(str(total_em_andamento), "🔄 Em Andamento", "yellow")
            with col4:
                criar_card_metrica(str(total_sp), "📐 Story Points", "blue")
            with col5:
                cor = 'red' if total_bugs > 5 else 'yellow' if total_bugs > 0 else 'green'
                criar_card_metrica(str(total_bugs), "🐛 Bugs", cor)
            with col6:
                pct_pago = int(total_dev_pago / total_cards * 100) if total_cards > 0 else 0
                cor = 'green' if total_dev_pago > 0 else 'gray'
                criar_card_metrica(f"{total_dev_pago} ({pct_pago}%)", "💰 Dev. Pago", cor)
        
        # ===== PROJETOS DO CLIENTE =====
        if 'projeto' in df_cliente.columns:
            projetos_cliente = df_cliente['projeto'].value_counts()
            st.markdown(f"**📂 Presença em Projetos:** {', '.join([f'{proj} ({qtd})' for proj, qtd in projetos_cliente.items()])}")
        
        st.markdown("---")
        
        # ===== STATUS E TIPO DOS CARDS =====
        col_status, col_tipo = st.columns(2)
        
        with col_status:
            st.markdown("##### 📊 Distribuição por Status")
            if 'status_cat' in df_cliente.columns:
                status_count = df_cliente.groupby('status_cat').size().reset_index(name='Cards')
                status_count['Status'] = status_count['status_cat'].map(STATUS_NOMES)
                
                fig_status = px.pie(status_count, values='Cards', names='Status',
                                    color_discrete_sequence=px.colors.qualitative.Set2)
                fig_status.update_layout(height=300)
                st.plotly_chart(fig_status, use_container_width=True)
            else:
                st.caption("Dados de status não disponíveis")
        
        with col_tipo:
            st.markdown("##### 📋 Distribuição por Tipo")
            if 'tipo' in df_cliente.columns:
                tipo_count = df_cliente.groupby('tipo').size().reset_index(name='Cards')
                
                fig_tipo = px.pie(tipo_count, values='Cards', names='tipo',
                                  color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_tipo.update_layout(height=300)
                st.plotly_chart(fig_tipo, use_container_width=True)
            else:
                st.caption("Dados de tipo não disponíveis")
        
        st.markdown("---")
        
        # ===== QUEM MAIS TRATA ESSE CLIENTE =====
        st.markdown("##### 👥 Pessoas que mais tratam este cliente")
        
        col_relator, col_dev, col_qa = st.columns(3)
        
        with col_relator:
            st.markdown("**📝 Relatores (criadores)**")
            if 'relator' in df_cliente.columns:
                relatores = df_cliente['relator'].value_counts().head(5)
                for nome, qtd in relatores.items():
                    pct = int(qtd / total_cards * 100)
                    st.markdown(f"- **{nome}**: {qtd} cards ({pct}%)")
            else:
                st.caption("Dados não disponíveis")
        
        with col_dev:
            st.markdown("**👨‍💻 Desenvolvedores**")
            if 'desenvolvedor' in df_cliente.columns:
                devs = df_cliente['desenvolvedor'].value_counts().head(5)
                for nome, qtd in devs.items():
                    if nome != 'Não atribuído':
                        pct = int(qtd / total_cards * 100)
                        st.markdown(f"- **{nome}**: {qtd} cards ({pct}%)")
            else:
                st.caption("Dados não disponíveis")
        
        with col_qa:
            st.markdown("**🔬 QAs responsáveis**")
            if 'qa' in df_cliente.columns:
                qas = df_cliente['qa'].value_counts().head(5)
                for nome, qtd in qas.items():
                    if nome != 'Não atribuído':
                        pct = int(qtd / total_cards * 100)
                        st.markdown(f"- **{nome}**: {qtd} cards ({pct}%)")
            else:
                st.caption("Dados não disponíveis")
        
        st.markdown("---")
        
        # ===== DESENVOLVIMENTO PAGO =====
        st.markdown("##### 💰 Análise de Desenvolvimento Pago")
        
        col_pago1, col_pago2 = st.columns(2)
        
        with col_pago1:
            # Cards de desenvolvimento pago
            cards_pagos = df_cliente[df_cliente['dev_pago'] == True]
            cards_outros = df_cliente[df_cliente['dev_pago'] == False]
            
            sp_pagos = int(cards_pagos['sp'].sum()) if 'sp' in cards_pagos.columns else 0
            sp_outros = int(cards_outros['sp'].sum()) if 'sp' in cards_outros.columns else 0
            
            st.markdown(f"""
            <div style="background: #f0fdf4; border: 1px solid #22c55e; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
                <div style="font-size: 24px; font-weight: bold; color: #22c55e;">💰 {len(cards_pagos)}</div>
                <div style="color: #166534;">Cards de Desenvolvimento Pago</div>
                <div style="color: #6b7280; font-size: 12px; margin-top: 5px;">
                    {int(len(cards_pagos)/total_cards*100) if total_cards > 0 else 0}% do total | {sp_pagos} SP
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px;">
                <div style="font-size: 24px; font-weight: bold; color: #6b7280;">🔧 {len(cards_outros)}</div>
                <div style="color: #475569;">Outros (Manutenção/Suporte)</div>
                <div style="color: #6b7280; font-size: 12px; margin-top: 5px;">
                    {int(len(cards_outros)/total_cards*100) if total_cards > 0 else 0}% do total | {sp_outros} SP
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_pago2:
            # Lista de cards pagos
            if not cards_pagos.empty:
                st.markdown("**Últimos Cards Pagos:**")
                for _, card in cards_pagos.head(5).iterrows():
                    ticket_id = card['ticket_id']
                    url_jira = f"{JIRA_BASE_URL}/browse/{ticket_id}"
                    titulo = str(card.get('titulo', card.get('summary', 'Sem título')))[:40]
                    st.markdown(f"- [{ticket_id}]({url_jira}): {titulo}...")
            else:
                st.info("Nenhum card de desenvolvimento pago para este cliente")
        
        st.markdown("---")
        
        # ===== TIMELINE DE CARDS =====
        st.markdown("##### 📅 Timeline de Cards")
        
        # Agrupa por mês
        if 'criado' in df_cliente.columns:
            df_cliente_copy = df_cliente.copy()
            df_cliente_copy['mes'] = df_cliente_copy['criado'].dt.to_period('M').astype(str)
            agg_dict = {'ticket_id': 'count'}
            if 'sp' in df_cliente_copy.columns:
                agg_dict['sp'] = 'sum'
            timeline = df_cliente_copy.groupby('mes').agg(agg_dict).reset_index()
            timeline.columns = ['Mês', 'Cards'] + (['SP'] if 'sp' in agg_dict else [])
            
            if len(timeline) > 1:
                fig_timeline = px.line(timeline, x='Mês', y='Cards', markers=True,
                                       title='Evolução de Cards por Mês')
                fig_timeline.update_layout(height=300)
                st.plotly_chart(fig_timeline, use_container_width=True)
            else:
                st.caption("Timeline não disponível (período muito curto)")
        else:
            st.caption("Dados de data não disponíveis")
        
        st.markdown("---")
        
        # ===== ÚLTIMOS CARDS DO CLIENTE =====
        st.markdown("##### 📄 Últimos 10 Cards")
        
        # Ordena por data de atualização
        if 'atualizado' in df_cliente.columns:
            ultimos_cards = df_cliente.sort_values('atualizado', ascending=False).head(10)
        else:
            ultimos_cards = df_cliente.head(10)
        
        import html as html_lib
        
        for _, card in ultimos_cards.iterrows():
            status_cor = STATUS_CORES.get(card.get('status_cat', ''), '#6b7280')
            status_nome = STATUS_NOMES.get(card.get('status_cat', ''), card.get('status', 'N/A'))
            
            # Link simples para o Jira
            ticket_id = str(card['ticket_id'])
            url_jira = f"{JIRA_BASE_URL}/browse/{ticket_id}"
            projeto = str(card.get('projeto', 'N/A'))
            
            # Cor por projeto
            cores_projeto = {"PB": "#8b5cf6", "SD": "#3b82f6", "QA": "#22c55e", "VALPROD": "#f59e0b"}
            cor_projeto = cores_projeto.get(projeto, "#6b7280")
            
            # Tempo relativo
            tempo = formatar_tempo_relativo(card['atualizado']) if 'atualizado' in card else 'N/A'
            
            # Tag de desenvolvimento pago
            is_pago = card.get('dev_pago', False)
            tag_pago = '<span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px; margin-left: 5px;">💰 PAGO</span>' if is_pago else ''
            
            # Escapa caracteres especiais HTML
            titulo = html_lib.escape(str(card.get('titulo', card.get('summary', 'Sem título'))))
            titulo_truncado = titulo[:50] + ('...' if len(titulo) > 50 else '')
            relator = html_lib.escape(str(card.get('relator', 'N/A')))
            dev = html_lib.escape(str(card.get('desenvolvedor', 'N/A')))
            qa = html_lib.escape(str(card.get('qa', 'N/A')))
            status_nome = html_lib.escape(str(status_nome))
            
            html_card = f'''<div style="background: #f8fafc; border-left: 4px solid {status_cor}; padding: 10px 15px; margin: 5px 0; border-radius: 4px;">
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
<div style="display: flex; align-items: center; flex-wrap: wrap; gap: 5px;">
<a href="{url_jira}" target="_blank" style="color: {cor_projeto}; font-weight: 600; text-decoration: none;">{ticket_id}</a>
<span style="color: #64748b;">- {titulo_truncado}</span>
<span style="color: #9ca3af; font-size: 11px;">({projeto})</span>
{tag_pago}
</div>
<span style="background: {status_cor}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; white-space: nowrap;">{status_nome}</span>
</div>
<div style="margin-top: 5px; font-size: 12px; color: #94a3b8;">
👤 {relator} → 👨‍💻 {dev} → 🔬 {qa} | {tempo}
</div>
</div>'''
            st.markdown(html_card, unsafe_allow_html=True)


def aba_visao_geral(df: pd.DataFrame, ultima_atualizacao: datetime):
    """Aba principal com visão geral da sprint."""
    
    # Header integrado: Título + Botão de atualizar com indicador
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 📊 Visão Geral da Sprint")
    with col2:
        # Botão integrado com última atualização
        agora = datetime.now()
        diff = (agora - ultima_atualizacao).total_seconds() / 60
        if diff < 1:
            tempo_texto = "agora"
        elif diff < 60:
            tempo_texto = f"há {int(diff)} min"
        else:
            tempo_texto = f"há {int(diff/60)}h"
        
        if st.button(f"🔄 Atualizar ({tempo_texto})", type="secondary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Sprint info - MELHORADO: pega sprint ATIVA, não a mais frequente
    # Primeiro tenta filtrar por sprint ativa
    sprint_atual = "Sem Sprint"
    sprint_end = None
    
    if 'sprint_state' in df.columns:
        df_sprint_ativa = df[df['sprint_state'] == 'active']
        if not df_sprint_ativa.empty:
            # Tem cards com sprint ativa - usa ela
            sprint_atual = df_sprint_ativa['sprint'].iloc[0]
            if 'sprint_end' in df_sprint_ativa.columns:
                sprint_end = df_sprint_ativa['sprint_end'].dropna().iloc[0] if not df_sprint_ativa['sprint_end'].isna().all() else None
        else:
            # Fallback: pega a sprint mais frequente
            sprint_atual = df['sprint'].mode().iloc[0] if not df.empty else "Sem Sprint"
            if 'sprint_end' in df.columns and not df['sprint_end'].isna().all():
                sprint_end = df['sprint_end'].dropna().iloc[0] if not df['sprint_end'].dropna().empty else None
    else:
        # Fallback se não tiver a coluna
        sprint_atual = df['sprint'].mode().iloc[0] if not df.empty else "Sem Sprint"
        if 'sprint_end' in df.columns and not df['sprint_end'].isna().all():
            sprint_end = df['sprint_end'].dropna().iloc[0] if not df['sprint_end'].dropna().empty else None
    
    hoje = datetime.now()
    dias_diff = None
    release_bold = "normal"
    
    if sprint_end:
        dias_diff = (sprint_end - hoje).days
        
        if dias_diff < 0:
            # Release ATRASADA
            dias_atraso = abs(dias_diff)
            release_info = f"🚨 Release ATRASADA ({dias_atraso}d)"
            cor_barra = "#ef4444"  # Vermelho
            release_bold = "bold"
        elif dias_diff == 0:
            # Release é HOJE
            release_info = "⚡ Release HOJE!"
            cor_barra = "#f59e0b"  # Amarelo/Laranja
            release_bold = "bold"
        else:
            # Dias restantes
            release_info = f"📅 {dias_diff} dias até a release"
            cor_barra = "#AF0C37"  # Cor padrão
    else:
        release_info = "📅 Data não definida"
        cor_barra = "#64748b"  # Cinza
    
    st.markdown(f"""
    <div style="background: {cor_barra}; color: white; padding: 15px 20px; border-radius: 10px; margin-bottom: 20px;">
        <span style="font-size: 18px; font-weight: bold;">🚀 {sprint_atual}</span>
        <span style="float: right; font-weight: {release_bold};">{release_info}</span>
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
    
    # ===== MÉTRICAS PRINCIPAIS (SIMPLIFICADAS) =====
    # 5 KPIs essenciais: Total, SP, Concluído, Bugs, Dias até Release
    concluidos = len(df[df['status_cat'] == 'done'])
    pct_concluido = concluidos / len(df) * 100 if len(df) > 0 else 0
    sp_total = int(df['sp'].sum())
    bugs_total = int(df['bugs'].sum())
    
    st.markdown("#### 📈 Resumo da Sprint")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        criar_card_metrica(str(len(df)), "Total Cards", "blue")
    
    with col2:
        criar_card_metrica(str(sp_total), "Story Points", "purple")
    
    with col3:
        cor = 'green' if pct_concluido >= 70 else 'yellow' if pct_concluido >= 40 else 'red'
        criar_card_metrica(f"{pct_concluido:.0f}%", "Concluído", cor, f"{concluidos}/{len(df)}")
    
    with col4:
        cor = 'green' if bugs_total < 10 else 'yellow' if bugs_total < 20 else 'red'
        criar_card_metrica(str(bugs_total), "Bugs", cor, "encontrados")
    
    with col5:
        if dias_diff is not None:
            cor = 'green' if dias_diff > 5 else 'yellow' if dias_diff > 2 else 'red'
            criar_card_metrica(str(max(0, dias_diff)), "Dias p/ Release", cor)
        else:
            criar_card_metrica("—", "Dias p/ Release", "blue", "não definido")
    
    # ===== BARRA DE PROGRESSO VISUAL DA SPRINT =====
    st.markdown("#### 📊 Progresso da Sprint")
    
    # Calcular métricas por status
    em_dev = len(df[df['status_cat'] == 'development'])
    em_review = len(df[df['status_cat'] == 'code_review'])
    em_fila_qa = len(df[df['status_cat'] == 'waiting_qa'])
    em_teste = len(df[df['status_cat'] == 'testing'])
    em_andamento = em_dev + em_review + em_fila_qa + em_teste
    total = len(df)
    
    # Barra de progresso estilizada
    pct_done = (concluidos / total * 100) if total > 0 else 0
    pct_progress = (em_andamento / total * 100) if total > 0 else 0
    
    st.markdown(f"""
    <div style="margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 14px;">
            <span>✅ Concluído: <b>{concluidos}</b></span>
            <span>🔄 Em Andamento: <b>{em_andamento}</b></span>
            <span>📋 Total: <b>{total}</b></span>
        </div>
        <div style="background: #e5e7eb; border-radius: 10px; height: 30px; overflow: hidden; position: relative;">
            <div style="background: linear-gradient(90deg, #22c55e, #16a34a); width: {pct_done}%; height: 100%; display: inline-block; transition: width 0.5s;"></div>
            <div style="background: linear-gradient(90deg, #3b82f6, #2563eb); width: {pct_progress}%; height: 100%; display: inline-block; transition: width 0.5s;"></div>
            <span style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); font-weight: bold; color: #374151;">{pct_done:.0f}% concluído</span>
        </div>
        <div style="display: flex; gap: 20px; margin-top: 8px; font-size: 12px; color: #6b7280;">
            <span>🟢 Concluído ({concluidos})</span>
            <span>🔵 Em Andamento ({em_andamento})</span>
            <span>⬜ Pendente ({total - concluidos - em_andamento})</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== MÉTRICAS TÉCNICAS (PARA QUEM QUISER VER) =====
    with st.expander("🔬 Métricas Técnicas de Qualidade", expanded=False):
        st.caption("Indicadores avançados para análise detalhada de qualidade")
        
        fpy = calcular_fpy(df)
        ddp = calcular_ddp(df)
        lead = calcular_lead_time(df)
        health = calcular_health_score(df)
        fk = calcular_fator_k(sp_total, bugs_total)
        mat = classificar_maturidade(fk)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            cor = 'green' if fpy['valor'] >= 80 else 'yellow' if fpy['valor'] >= 60 else 'red'
            criar_card_metrica(f"{fpy['valor']:.0f}%", "FPY", cor, f"{fpy['sem_bugs']}/{fpy['total']} sem bugs", "fpy")
        
        with col2:
            cor = 'green' if ddp['valor'] >= 85 else 'yellow' if ddp['valor'] >= 70 else 'red'
            criar_card_metrica(f"{ddp['valor']:.0f}%", "DDP", cor, f"{ddp['bugs_qa']} detectados", "ddp")
        
        with col3:
            cor = 'green' if lead['medio'] <= 7 else 'yellow' if lead['medio'] <= 14 else 'red'
            criar_card_metrica(f"{lead['medio']:.1f}d", "Lead Time", cor, f"P85: {lead['p85']}d", "lead_time")
        
        with col4:
            cor = 'green' if health['score'] >= 75 else 'yellow' if health['score'] >= 50 else 'red'
            criar_card_metrica(f"{health['score']:.0f}", "Health Score", cor, health['status'], "health_score")
        
        with col5:
            cor_map = {'#22c55e': 'green', '#eab308': 'yellow', '#f97316': 'orange', '#ef4444': 'red'}
            criar_card_metrica(f"{fk:.1f}", f"Fator K {mat['emoji']}", cor_map.get(mat['cor'], 'blue'), mat['selo'], "fator_k")
        
        # Tooltips das métricas
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            mostrar_tooltip("fpy")
        with col2:
            mostrar_tooltip("ddp")
        with col3:
            mostrar_tooltip("lead_time")
        with col4:
            mostrar_tooltip("health_score")
        with col5:
            mostrar_tooltip("fator_k")
    
    # ===== CARDS POR STATUS (2 COLUNAS - MAIS ESPAÇO) =====
    with st.expander("📋 Cards por Status", expanded=True):
        status_counts = df.groupby('status_cat').size().to_dict()
        
        # Agrupamento em 2 colunas para melhor legibilidade
        status_grupos = [
            ['development', 'code_review'],  # Coluna 1: Desenvolvimento
            ['waiting_qa', 'testing']        # Coluna 2: QA
        ]
        
        col_esq, col_dir = st.columns(2)
        
        for col_idx, (coluna, grupo) in enumerate([(col_esq, status_grupos[0]), (col_dir, status_grupos[1])]):
            with coluna:
                for status in grupo:
                    count = status_counts.get(status, 0)
                    nome = STATUS_NOMES.get(status, status)
                    cor = STATUS_CORES.get(status, '#6b7280')
                    
                    st.markdown(f"""
                    <div style="background: {cor}20; border-left: 4px solid {cor}; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 24px; font-weight: bold;">{count}</span>
                            <span style="font-size: 14px; color: {cor}; font-weight: 500;">{nome}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Listagem COMPLETA com mais espaço
                    df_status = df[df['status_cat'] == status]
                    if not df_status.empty:
                        mostrar_lista_df_completa(df_status, nome)
    
    # ===== NOVA SEÇÃO ELLEN: ANÁLISE DE SPRINT =====
    projeto_atual = df['projeto'].iloc[0] if not df.empty else 'SD'
    if projeto_atual in ['SD', 'QA']:
        with st.expander("🎯 Análise de Sprint - Planejamento vs Entrega", expanded=False):
            st.markdown("#### Planejamento vs Entrega da Sprint")
            
            # Separar cards por categoria
            df_sprint = df[df['sprint'] != 'Sem Sprint'].copy()
            
            if not df_sprint.empty:
                # Métricas de sprint
                total_sprint = len(df_sprint)
                planejados = df_sprint[df_sprint['criado_na_sprint'] == False]
                adicionados_depois = df_sprint[df_sprint['adicionado_fora_periodo'] == True]
                concluidos = df_sprint[df_sprint['status_cat'] == 'done']
                
                # Categorização por tipo de entrada
                hotfixes = df_sprint[df_sprint['tipo'] == 'HOTFIX']
                com_link_pb = df_sprint[df_sprint['tem_link_pb'] == True]
                sem_link_pb = df_sprint[(df_sprint['tem_link_pb'] == False) & (df_sprint['tipo'] != 'HOTFIX')]
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    pct_entrega = len(concluidos) / total_sprint * 100 if total_sprint > 0 else 0
                    cor = 'green' if pct_entrega >= 80 else 'yellow' if pct_entrega >= 60 else 'red'
                    criar_card_metrica(f"{pct_entrega:.0f}%", "Taxa de Entrega", cor, f"{len(concluidos)}/{total_sprint} cards")
                
                with col2:
                    cor = 'green' if len(adicionados_depois) <= 3 else 'yellow' if len(adicionados_depois) <= 6 else 'red'
                    criar_card_metrica(str(len(adicionados_depois)), "Fora do Planejamento", cor, "Adicionados após início")
                
                with col3:
                    criar_card_metrica(str(len(hotfixes)), "Hotfix/Hotfeature", "orange", "Urgências da sprint")
                
                with col4:
                    pct_pb = len(com_link_pb) / total_sprint * 100 if total_sprint > 0 else 0
                    criar_card_metrica(f"{pct_pb:.0f}%", "Originados do PB", "blue", f"{len(com_link_pb)} cards")
            
                # Tabela de cards fora do planejamento
                if not adicionados_depois.empty:
                    st.markdown("---")
                    st.markdown("##### 🚨 Cards Fora do Planejamento Original")
                    st.caption("Cards adicionados após o início da sprint comprometem a previsibilidade")
                    
                    # Construir HTML completo em string única
                    html_cards = '<div class="scroll-container" style="max-height: 400px;">'
                    for _, card in adicionados_depois.iterrows():
                        if card['tipo'] == 'HOTFIX':
                            categoria = "🔥 Hotfix/Hotfeature"
                            cor_tag = "#f97316"
                        elif card['tem_link_pb']:
                            categoria = "📋 Puxado do PB"
                            cor_tag = "#3b82f6"
                        else:
                            categoria = "➕ Criação Direta"
                            cor_tag = "#8b5cf6"
                        
                        card_link = card_link_com_popup(card['ticket_id'])
                        titulo_card = str(card['titulo'])[:60]
                        status_card = str(card['status'])
                        html_cards += '<div class="card-lista" style="border-left-color: ' + cor_tag + ';">'
                        html_cards += '<span style="background: ' + cor_tag + '; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">' + categoria + '</span>'
                        html_cards += '<span style="margin-left: 10px;">' + card_link + '</span>'
                        html_cards += '<span style="color: #64748b;"> - ' + titulo_card + '...</span>'
                        html_cards += '<span style="float: right; color: #94a3b8; font-size: 12px;">' + status_card + '</span>'
                        html_cards += '</div>'
                    html_cards += '</div>'
                    st.markdown(html_cards, unsafe_allow_html=True)
                    
                # Cards por origem do PB
                if not com_link_pb.empty:
                    st.markdown("---")
                    st.markdown("##### 📋 Cards Originados do Product Backlog")
                    
                    # Agrupar por produto
                    por_produto = com_link_pb.groupby('produto').agg({
                        'ticket_id': 'count',
                        'sp': 'sum',
                        'status_cat': lambda x: (x == 'done').sum()
                    }).reset_index()
                    por_produto.columns = ['Produto', 'Cards', 'SP Total', 'Concluídos']
                    por_produto = por_produto.sort_values('Cards', ascending=False)
                    
                    st.dataframe(por_produto, hide_index=True, use_container_width=True)
            else:
                st.info("Nenhum card com sprint definida no período")
    
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
    
    # Verificar se há QA na URL para compartilhamento (link compartilhado)
    qa_url = st.query_params.get("qa", None)
    opcoes_qa = ["👀 Visão Geral do Time"] + sorted(qas)
    
    # Determinar índice inicial baseado na URL (se veio de link compartilhado)
    indice_inicial = 0
    if qa_url and qa_url in qas:
        indice_inicial = opcoes_qa.index(qa_url)
    
    # SELETOR DE QA (NÃO atualiza query_params - apenas o botão Copiar Link faz isso)
    qa_sel = st.selectbox("🔍 Selecione o QA", opcoes_qa, index=indice_inicial, key="select_qa")
    
    st.markdown("---")
    
    if qa_sel == "👀 Visão Geral do Time":
        # ====== VISÃO GERAL DO TIME DE QA ======
        
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
                ddp = calcular_ddp(df)
                cor = 'green' if ddp['valor'] >= 85 else 'yellow' if ddp['valor'] >= 70 else 'red'
                criar_card_metrica(f"{ddp['valor']:.0f}%", "DDP", cor, "Detecção de Defeitos", "ddp")
            
            # Linha adicional para Impedidos e Reprovados
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            # Cards impedidos
            cards_impedidos = df[df['status_cat'] == 'blocked']
            with col1:
                cor = 'green' if len(cards_impedidos) == 0 else 'yellow' if len(cards_impedidos) < 3 else 'red'
                criar_card_metrica(str(len(cards_impedidos)), "🚫 Impedidos", cor, "Bloqueados")
            
            # Cards reprovados
            cards_reprovados = df[df['status_cat'] == 'rejected']
            with col2:
                cor = 'green' if len(cards_reprovados) == 0 else 'yellow' if len(cards_reprovados) < 3 else 'red'
                criar_card_metrica(str(len(cards_reprovados)), "❌ Reprovados", cor, "Falha na validação")
            
            # Bug rate geral
            with col3:
                total_validados = len(df[df['status_cat'] == 'done'])
                total_com_bugs = len(df[(df['status_cat'] == 'done') & (df['bugs'] > 0)])
                bug_rate = total_com_bugs / total_validados * 100 if total_validados > 0 else 0
                cor = 'green' if bug_rate < 20 else 'yellow' if bug_rate < 40 else 'red'
                criar_card_metrica(f"{bug_rate:.0f}%", "Bug Rate", cor, f"{total_com_bugs} com bugs")
            
            # SP impedidos/reprovados
            with col4:
                sp_bloqueado = int(cards_impedidos['sp'].sum()) + int(cards_reprovados['sp'].sum())
                cor = 'green' if sp_bloqueado == 0 else 'yellow' if sp_bloqueado < 10 else 'red'
                criar_card_metrica(str(sp_bloqueado), "SP Travados", cor, "Impedidos + Reprovados")
        
        # Cards Impedidos/Reprovados detalhados
        if len(cards_impedidos) > 0 or len(cards_reprovados) > 0:
            with st.expander("🚨 Cards Impedidos e Reprovados", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 🚫 Impedidos")
                    if not cards_impedidos.empty:
                        html_impedidos = '<div class="scroll-container" style="max-height: 350px;">'
                        for _, row in cards_impedidos.iterrows():
                            card_link = card_link_com_popup(row['ticket_id'])
                            titulo = str(row['titulo'])
                            dev = str(row['desenvolvedor'])
                            qa = str(row['qa'])
                            sp = int(row['sp'])
                            html_impedidos += '<div class="card-lista-vermelho">'
                            html_impedidos += '<strong>' + card_link + '</strong>'
                            html_impedidos += '<span style="color: #64748b;"> - ' + titulo + '</span><br>'
                            html_impedidos += '<small style="color: #94a3b8;">👤 DEV: ' + dev + ' | 🧑‍🔬 QA: ' + qa + ' | ' + str(sp) + ' SP</small>'
                            html_impedidos += '</div>'
                        html_impedidos += '</div>'
                        st.markdown(html_impedidos, unsafe_allow_html=True)
                    else:
                        st.success("✅ Nenhum card impedido")
                
                with col2:
                    st.markdown("#### ❌ Reprovados")
                    if not cards_reprovados.empty:
                        html_reprovados = '<div class="scroll-container" style="max-height: 350px;">'
                        for _, row in cards_reprovados.iterrows():
                            card_link = card_link_com_popup(row['ticket_id'])
                            titulo = str(row['titulo'])
                            dev = str(row['desenvolvedor'])
                            qa = str(row['qa'])
                            sp = int(row['sp'])
                            bugs = int(row['bugs'])
                            html_reprovados += '<div class="card-lista-vermelho">'
                            html_reprovados += '<strong>' + card_link + '</strong>'
                            html_reprovados += '<span style="color: #64748b;"> - ' + titulo + '</span><br>'
                            html_reprovados += '<small style="color: #94a3b8;">👤 DEV: ' + dev + ' | 🧑‍🔬 QA: ' + qa + ' | ' + str(sp) + ' SP | 🐛 ' + str(bugs) + ' bugs</small>'
                            html_reprovados += '</div>'
                        html_reprovados += '</div>'
                        st.markdown(html_reprovados, unsafe_allow_html=True)
                    else:
                        st.success("✅ Nenhum card reprovado")
        
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
        
        # Concentração de Conhecimento do Time QA
        exibir_concentracao_time(df, "qa")
        
        # Comparativo entre QAs
        with st.expander("📊 Comparativo de Performance entre QAs", expanded=True):
            if qas:
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
        
        # ===== NOVA SEÇÃO: INTERAÇÃO QA x DEV =====
        with st.expander("🤝 Interação QA x DEV", expanded=True):
            st.caption("Visualize a relação de trabalho entre QAs e Desenvolvedores")
            
            # Filtra apenas cards com QA e DEV atribuídos
            df_interacao = df[(df['qa'] != 'Não atribuído') & (df['desenvolvedor'] != 'Não atribuído')].copy()
            
            if not df_interacao.empty:
                # Matriz de interação QA x DEV
                matriz_interacao = df_interacao.groupby(['qa', 'desenvolvedor']).agg({
                    'ticket_id': 'count',
                    'bugs': 'sum',
                    'sp': 'sum'
                }).reset_index()
                matriz_interacao.columns = ['QA', 'DEV', 'Cards', 'Bugs', 'SP']
                
                # Calcula FPY por dupla QA-DEV
                for idx, row in matriz_interacao.iterrows():
                    cards_dupla = df_interacao[(df_interacao['qa'] == row['QA']) & (df_interacao['desenvolvedor'] == row['DEV'])]
                    cards_sem_bugs = len(cards_dupla[cards_dupla['bugs'] == 0])
                    matriz_interacao.loc[idx, 'FPY'] = round(cards_sem_bugs / row['Cards'] * 100, 0) if row['Cards'] > 0 else 0
                
                matriz_interacao['FPY'] = matriz_interacao['FPY'].astype(int).astype(str) + '%'
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📊 Ranking de Duplas QA-DEV (Mais Cards)**")
                    top_duplas = matriz_interacao.sort_values('Cards', ascending=False).head(10)
                    st.dataframe(top_duplas, hide_index=True, use_container_width=True)
                
                with col2:
                    st.markdown("**🌟 Heatmap de Interações**")
                    # Criar pivot para heatmap
                    pivot_cards = df_interacao.groupby(['qa', 'desenvolvedor'])['ticket_id'].count().unstack(fill_value=0)
                    
                    if not pivot_cards.empty:
                        fig = px.imshow(
                            pivot_cards,
                            labels=dict(x="Desenvolvedor", y="QA", color="Cards"),
                            color_continuous_scale='Blues',
                            aspect='auto'
                        )
                        fig.update_layout(height=350)
                        st.plotly_chart(fig, use_container_width=True)
                
                # Métricas resumidas
                st.markdown("---")
                st.markdown("**📈 Métricas de Colaboração**")
                
                col1, col2, col3, col4 = st.columns(4)
                
                # Total de duplas únicas
                with col1:
                    total_duplas = len(matriz_interacao)
                    criar_card_metrica(str(total_duplas), "Duplas QA-DEV", "blue", "Combinações ativas")
                
                # Dupla mais produtiva
                with col2:
                    melhor_dupla = matriz_interacao.loc[matriz_interacao['Cards'].idxmax()]
                    criar_card_metrica(str(int(melhor_dupla['Cards'])), "Maior Parceria", "green", f"{melhor_dupla['QA'][:10]} + {melhor_dupla['DEV'][:10]}")
                
                # Melhor FPY
                with col3:
                    matriz_interacao['FPY_num'] = matriz_interacao['FPY'].str.replace('%', '').astype(float)
                    matriz_filtrada = matriz_interacao[matriz_interacao['Cards'] >= 3]  # Pelo menos 3 cards para ser significativo
                    if not matriz_filtrada.empty:
                        melhor_fpy = matriz_filtrada.loc[matriz_filtrada['FPY_num'].idxmax()]
                        criar_card_metrica(melhor_fpy['FPY'], "Melhor FPY", "green", f"{melhor_fpy['QA'][:10]} + {melhor_fpy['DEV'][:10]}")
                    else:
                        criar_card_metrica("N/A", "Melhor FPY", "gray", "Min. 3 cards")
                
                # Pior FPY (atenção)
                with col4:
                    if not matriz_filtrada.empty:
                        pior_fpy = matriz_filtrada.loc[matriz_filtrada['FPY_num'].idxmin()]
                        cor = 'red' if pior_fpy['FPY_num'] < 50 else 'yellow' if pior_fpy['FPY_num'] < 70 else 'green'
                        criar_card_metrica(pior_fpy['FPY'], "Menor FPY", cor, f"{pior_fpy['QA'][:10]} + {pior_fpy['DEV'][:10]}")
                    else:
                        criar_card_metrica("N/A", "Menor FPY", "gray", "Min. 3 cards")
            else:
                st.info("💡 Sem dados de interação QA-DEV disponíveis. Verifique se os cards têm QA e Desenvolvedor atribuídos.")
        
        # Análise de Bugs
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
                    fpy = calcular_fpy(df)
                    st.metric("FPY (First Pass Yield)", f"{fpy['valor']}%", help=get_tooltip_help("fpy"))
                    
                    cards_com_bugs = len(concluidos[concluidos['bugs'] > 0])
                    taxa_retrabalho = cards_com_bugs / len(concluidos) * 100 if len(concluidos) > 0 else 0
                    st.metric("Taxa de Retrabalho", f"{taxa_retrabalho:.1f}%", help="Percentual de cards que voltaram para correção após QA encontrar bugs")
                    
                    lead = calcular_lead_time(df)
                    st.metric("Lead Time Médio", f"{lead['medio']:.1f} dias", help=get_tooltip_help("lead_time"))
                else:
                    st.info("Sem cards concluídos")
            
            st.markdown("---")
            st.markdown("**⚠️ Desenvolvedores com mais bugs (requer atenção do QA)**")
            
            dev_bugs = df[df['desenvolvedor'] != 'Não atribuído'].groupby('desenvolvedor').agg({
                'bugs': 'sum', 'sp': 'sum', 'ticket_id': 'count'
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
        
        # Janela de Validação
        with st.expander("🕐 Janela de Validação (Análise de Risco)", expanded=True):
            st.markdown("""
            <div class="alert-info">
                <b>📋 Regras de Janela de Validação</b>
                <p>A janela considera a <b>complexidade de teste</b> do card para determinar se há tempo suficiente:</p>
                <ul style="margin: 5px 0 0 20px;">
                    <li><b>Alta:</b> 3+ dias necessários</li>
                    <li><b>Média:</b> 2 dias necessários</li>
                    <li><b>Baixa:</b> 1 dia é suficiente</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            cards_qa = df[df['status_cat'].isin(['waiting_qa', 'testing'])]
            
            if not cards_qa.empty:
                fora_janela = cards_qa[cards_qa['janela_status'] == 'fora']
                em_risco = cards_qa[cards_qa['janela_status'] == 'risco']
                dentro_janela = cards_qa[cards_qa['janela_status'] == 'ok']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    cor = 'red' if len(fora_janela) > 0 else 'green'
                    criar_card_metrica(str(len(fora_janela)), "🚨 Fora da Janela", cor)
                with col2:
                    cor = 'yellow' if len(em_risco) > 0 else 'green'
                    criar_card_metrica(str(len(em_risco)), "⚠️ Em Risco", cor)
                with col3:
                    criar_card_metrica(str(len(dentro_janela)), "✅ Dentro da Janela", "green")
                
                if not fora_janela.empty:
                    st.markdown("### 🚨 Cards FORA da Janela")
                    df_fora = fora_janela[['ticket_id', 'titulo', 'complexidade', 'dias_ate_release', 'desenvolvedor', 'sp']].copy()
                    df_fora.columns = ['Ticket', 'Título', 'Complexidade', 'Dias Disponíveis', 'Dev', 'SP']
                    st.dataframe(df_fora, hide_index=True, use_container_width=True)
            else:
                st.success("✅ Nenhum card aguardando validação!")
        
        # Cards Aging
        with st.expander("⏰ Cards Envelhecidos (Aging)", expanded=False):
            aging_waiting = metricas_qa['aging']['waiting']
            aging_testing = metricas_qa['aging']['testing']
            
            if not aging_waiting.empty or not aging_testing.empty:
                st.markdown(f"""
                <div class="alert-warning">
                    <b>⚠️ {metricas_qa['aging']['total']} card(s) há mais de {REGRAS['dias_aging_alerta']} dias no mesmo status!</b>
                </div>
                """, unsafe_allow_html=True)
                if not aging_waiting.empty:
                    mostrar_lista_df_completa(aging_waiting, "Aging - Aguardando QA")
                if not aging_testing.empty:
                    mostrar_lista_df_completa(aging_testing, "Aging - Em Validação")
            else:
                st.success("✅ Nenhum card envelhecido!")
        
        # Filas
        with st.expander("📋 Fila - Aguardando Validação", expanded=False):
            fila_qa = df[df['status_cat'] == 'waiting_qa'].sort_values('dias_em_status', ascending=False)
            mostrar_lista_df_completa(fila_qa, "Aguardando QA")
        
        with st.expander("🧪 Em Validação", expanded=False):
            em_teste = df[df['status_cat'] == 'testing'].sort_values('dias_em_status', ascending=False)
            mostrar_lista_df_completa(em_teste, "Em Validação")
    
    else:
        # ====== VISÃO INDIVIDUAL DO QA SELECIONADO ======
        df_qa = df[df['qa'] == qa_sel]
        
        if df_qa.empty:
            st.warning(f"Nenhum card atribuído para {qa_sel}")
            return
        
        # Header com título e botão de compartilhamento
        import urllib.parse
        base_url = NINADASH_URL
        share_url = f"{base_url}?aba=qa&qa={urllib.parse.quote(qa_sel)}"
        
        col_titulo, col_share = st.columns([3, 1])
        with col_titulo:
            st.markdown(f"### 👤 Métricas de {qa_sel}")
        with col_share:
            # Botão Copiar Link usando components.html (mesmo padrão do card individual)
            components.html(f"""
            <button id="copyBtnQA" style="
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
                document.getElementById('copyBtnQA').addEventListener('click', function() {{
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
        
        # KPIs individuais
        with st.expander("📊 Indicadores Individuais", expanded=True):
            validados = len(df_qa[df_qa['status_cat'] == 'done'])
            em_fila = len(df_qa[df_qa['status_cat'].isin(['waiting_qa', 'testing'])])
            bugs_encontrados = int(df_qa['bugs'].sum())
            cards_sem_bugs = len(df_qa[(df_qa['status_cat'] == 'done') & (df_qa['bugs'] == 0)])
            fpy_val = cards_sem_bugs / validados * 100 if validados > 0 else 0
            sp_total = int(df_qa['sp'].sum())
            lead_time_medio = df_qa['lead_time'].mean() if not df_qa.empty else 0
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                criar_card_metrica(str(len(df_qa)), "Total Cards", "blue")
            with col2:
                criar_card_metrica(str(validados), "Validados", "green")
            with col3:
                criar_card_metrica(str(em_fila), "Em Fila", "yellow", "", "wip")
            with col4:
                criar_card_metrica(str(bugs_encontrados), "Bugs Encontrados", "purple")
            with col5:
                cor = 'green' if fpy_val >= 80 else 'yellow' if fpy_val >= 60 else 'red'
                criar_card_metrica(f"{fpy_val:.0f}%", "FPY", cor, "", "fpy")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Story Points Total", sp_total, help="Soma de todos os Story Points dos cards atribuídos a este QA")
            with col2:
                st.metric("Lead Time Médio", f"{lead_time_medio:.1f} dias", help=get_tooltip_help("lead_time"))
            with col3:
                aging_qa = len(df_qa[df_qa['dias_em_status'] > REGRAS['dias_aging_alerta']])
                st.metric("Cards Aging", aging_qa, help="Cards parados há mais de 3 dias no mesmo status - requer atenção")
            
            # Linha de impedidos/reprovados do QA
            st.markdown("---")
            cards_impedidos_qa = df_qa[df_qa['status_cat'] == 'blocked']
            cards_reprovados_qa = df_qa[df_qa['status_cat'] == 'rejected']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                cor = 'green' if len(cards_impedidos_qa) == 0 else 'yellow' if len(cards_impedidos_qa) < 2 else 'red'
                criar_card_metrica(str(len(cards_impedidos_qa)), "🚫 Impedidos", cor)
            with col2:
                cor = 'green' if len(cards_reprovados_qa) == 0 else 'yellow' if len(cards_reprovados_qa) < 2 else 'red'
                criar_card_metrica(str(len(cards_reprovados_qa)), "❌ Reprovados", cor)
            with col3:
                sp_travado = int(cards_impedidos_qa['sp'].sum()) + int(cards_reprovados_qa['sp'].sum())
                cor = 'green' if sp_travado == 0 else 'yellow' if sp_travado < 5 else 'red'
                criar_card_metrica(str(sp_travado), "SP Travados", cor)
            with col4:
                em_validacao = len(df_qa[df_qa['status_cat'] == 'testing'])
                criar_card_metrica(str(em_validacao), "🧪 Validando", "blue")
            
            # Lista cards impedidos/reprovados se existirem
            if len(cards_impedidos_qa) > 0 or len(cards_reprovados_qa) > 0:
                st.markdown("---")
                st.markdown("**🚨 Seus cards com problemas:**")
                all_problemas = pd.concat([cards_impedidos_qa, cards_reprovados_qa]) if not cards_reprovados_qa.empty else cards_impedidos_qa
                for _, row in all_problemas.iterrows():
                    status_icon = "🚫" if row['status_cat'] == 'blocked' else "❌"
                    status_name = "Impedido" if row['status_cat'] == 'blocked' else "Reprovado"
                    card_link = card_link_com_popup(row['ticket_id'])
                    st.markdown(f"""
                    <div style="padding: 8px; margin: 4px 0; border-left: 3px solid #ef4444; background: rgba(239, 68, 68, 0.1); border-radius: 4px;">
                        <strong>{status_icon}</strong> {card_link} - {row['titulo']}<br>
                        <small style="color: #94a3b8;">👤 DEV: {row['desenvolvedor']} | {status_name} | {int(row['sp'])} SP</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        # ===== ÁREAS DE ATUAÇÃO (CONCENTRAÇÃO) =====
        exibir_concentracao_simplificada(df, qa_sel, "qa", expanded=False)
        
        # ===== NOVA SEÇÃO: RESUMO DA SEMANA =====
        with st.expander("📅 Resumo da Semana", expanded=True):
            st.caption("📊 Sua atividade semanal - ideal para apresentar ao time!")
            
            hoje = datetime.now()
            
            # Seletor de semana
            semanas_opcoes = {
                "Semana Atual": 0,
                "Semana Passada": 1,
                "2 Semanas Atrás": 2,
                "3 Semanas Atrás": 3,
                "4 Semanas Atrás": 4
            }
            
            semana_selecionada = st.selectbox(
                "📆 Selecione a semana:",
                list(semanas_opcoes.keys()),
                index=0,
                key=f"semana_qa_{qa_sel}"
            )
            
            semanas_atras = semanas_opcoes[semana_selecionada]
            
            # Calcula início e fim da semana selecionada (segunda a sexta)
            dias_desde_segunda = hoje.weekday()
            segunda_atual = hoje - timedelta(days=dias_desde_segunda)
            segunda_semana = segunda_atual - timedelta(weeks=semanas_atras)
            sexta_semana = segunda_semana + timedelta(days=4)
            # Inclui até 23:59:59 da sexta
            fim_sexta = sexta_semana + timedelta(days=1) - timedelta(seconds=1)
            # Para resolutiondate, precisa ir até o final do dia
            inicio_semana = segunda_semana.replace(hour=0, minute=0, second=0)
            
            # Exibe período selecionado
            st.markdown(f"""
            <div style="background: #f1f5f9; padding: 8px 15px; border-radius: 6px; margin-bottom: 15px; text-align: center;">
                <span style="color: #64748b;">📅 Período: <strong>{segunda_semana.strftime('%d/%m')} (Seg)</strong> a <strong>{sexta_semana.strftime('%d/%m')} (Sex)</strong></span>
            </div>
            """, unsafe_allow_html=True)
            
            # Filtra cards CONCLUÍDOS na semana usando resolutiondate (mais preciso)
            df_validados_semana = df_qa[
                (df_qa['status_cat'] == 'done') & 
                (df_qa['resolutiondate'].notna()) &
                (df_qa['resolutiondate'] >= inicio_semana) & 
                (df_qa['resolutiondate'] <= fim_sexta)
            ].copy()
            
            # Se não houver resolutiondate, usa atualizado como fallback
            if df_validados_semana.empty:
                df_validados_semana = df_qa[
                    (df_qa['status_cat'] == 'done') & 
                    (df_qa['atualizado'] >= inicio_semana) & 
                    (df_qa['atualizado'] <= fim_sexta)
                ].copy()
            
            # Cards que tiveram atividade na semana (todos os status)
            df_semana = df_qa[
                (df_qa['atualizado'] >= inicio_semana) & 
                (df_qa['atualizado'] <= fim_sexta)
            ].copy()
            
            # KPIs da Semana
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                criar_card_metrica(str(len(df_semana)), "Cards Trabalhados", "blue", f"{semana_selecionada}")
            with col2:
                criar_card_metrica(str(len(df_validados_semana)), "Validações", "green", "Concluídos")
            with col3:
                bugs_semana = int(df_validados_semana['bugs'].sum()) if not df_validados_semana.empty else 0
                criar_card_metrica(str(bugs_semana), "Bugs Encontrados", "purple")
            with col4:
                sp_semana = int(df_validados_semana['sp'].sum()) if not df_validados_semana.empty else 0
                criar_card_metrica(str(sp_semana), "SP Entregues", "green")
            
            st.markdown("---")
            
            # Evolução da Semana (gráfico de linhas - fila diminuindo, concluídos aumentando)
            st.markdown("**📈 Evolução da Semana**")
            st.caption("💡 Mostra a fila diminuindo e os concluídos aumentando ao longo da semana")
            
            # Calcula a evolução dia a dia
            # Total de cards que entraram em fila durante a semana (waiting_qa ou testing)
            cards_fila_semana = df_qa[
                (df_qa['status_cat'].isin(['waiting_qa', 'testing', 'done'])) &
                (df_qa['atualizado'] >= inicio_semana) & 
                (df_qa['atualizado'] <= fim_sexta)
            ].copy()
            
            total_fila_inicial = len(cards_fila_semana)
            
            dias_evolucao = []
            concluidos_acumulado = 0
            
            for i in range(5):  # 0=seg, 4=sex
                dia = segunda_semana + timedelta(days=i)
                dia_str = dia.strftime("%d/%m")
                dia_nome = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex'][i]
                
                # Cards concluídos até este dia (acumulado)
                # Converte dia para pd.Timestamp para comparação segura
                dia_fim = pd.Timestamp(dia.date()) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
                
                if 'resolutiondate' in df_qa.columns:
                    # Remove timezone se existir para comparação segura
                    col_resolution = df_qa['resolutiondate']
                    if hasattr(col_resolution.dtype, 'tz') and col_resolution.dtype.tz is not None:
                        col_resolution = col_resolution.dt.tz_localize(None)
                    
                    concluidos_ate_dia = len(df_qa[
                        (df_qa['status_cat'] == 'done') &
                        (col_resolution.notna()) &
                        (col_resolution >= inicio_semana) &
                        (col_resolution <= dia_fim)
                    ])
                    
                    # Fallback com atualizado
                    if concluidos_ate_dia == 0:
                        col_atualizado = df_qa['atualizado']
                        if hasattr(col_atualizado.dtype, 'tz') and col_atualizado.dtype.tz is not None:
                            col_atualizado = col_atualizado.dt.tz_localize(None)
                        
                        concluidos_ate_dia = len(df_qa[
                            (df_qa['status_cat'] == 'done') &
                            (col_atualizado >= inicio_semana) &
                            (col_atualizado <= dia_fim)
                        ])
                else:
                    concluidos_ate_dia = 0
                
                # Fila = total inicial - concluídos até o dia
                fila_dia = max(0, total_fila_inicial - concluidos_ate_dia)
                
                dias_evolucao.append({
                    'Dia': f"{dia_nome}\n{dia_str}",
                    'Em Fila': fila_dia,
                    'Concluídos': concluidos_ate_dia
                })
            
            df_evolucao = pd.DataFrame(dias_evolucao)
            
            # Gráfico de linhas com duas séries
            if total_fila_inicial > 0:
                fig = go.Figure()
                
                # Linha de Fila (laranja, diminuindo)
                fig.add_trace(go.Scatter(
                    x=df_evolucao['Dia'],
                    y=df_evolucao['Em Fila'],
                    mode='lines+markers+text',
                    name='Em Fila',
                    line=dict(color='#f59e0b', width=3),
                    marker=dict(size=10),
                    text=df_evolucao['Em Fila'],
                    textposition='top center',
                    textfont=dict(size=12, color='#f59e0b')
                ))
                
                # Linha de Concluídos (verde, aumentando)
                fig.add_trace(go.Scatter(
                    x=df_evolucao['Dia'],
                    y=df_evolucao['Concluídos'],
                    mode='lines+markers+text',
                    name='Concluídos',
                    line=dict(color='#22c55e', width=3),
                    marker=dict(size=10),
                    text=df_evolucao['Concluídos'],
                    textposition='bottom center',
                    textfont=dict(size=12, color='#22c55e')
                ))
                
                fig.update_layout(
                    height=280,
                    margin=dict(l=20, r=20, t=30, b=20),
                    xaxis_title="",
                    yaxis_title="Cards",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("💡 Nenhum card na fila de validação esta semana.")
            
            st.markdown("---")
            
            # ===== CARDS EM TRABALHO (Aguardando + Em Validação) =====
            df_em_trabalho = df_qa[df_qa['status_cat'].isin(['waiting_qa', 'testing'])].copy()
            
            st.markdown("**🔄 Cards em Trabalho**")
            st.caption("Cards que você está trabalhando agora (aguardando validação + em validação)")
            
            if not df_em_trabalho.empty:
                df_em_trabalho_sorted = df_em_trabalho.sort_values('atualizado', ascending=False)
                
                # Scroll container
                st.markdown('<div class="scroll-container" style="max-height: 400px;">', unsafe_allow_html=True)
                for _, row in df_em_trabalho_sorted.iterrows():
                    status_icon = "⏳" if row['status_cat'] == 'waiting_qa' else "🧪"
                    status_nome = "Aguardando" if row['status_cat'] == 'waiting_qa' else "Validando"
                    status_cor = "#f59e0b" if row['status_cat'] == 'waiting_qa' else "#3b82f6"
                    dias_status = row['dias_em_status']
                    urgencia_cor = '#ef4444' if dias_status > 3 else '#eab308' if dias_status > 1 else '#22c55e'
                    card_link = card_link_com_popup(row['ticket_id'])
                    tempo_atualizacao = formatar_tempo_relativo(row.get('atualizado'))
                    
                    st.markdown(f"""
                    <div class="card-lista" style="border-left-color: {status_cor}; background: {status_cor}10;">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                            <div style="flex: 1; min-width: 200px;">
                                <strong>{status_icon} {card_link}</strong>
                                <span style="color: #64748b;"> - {row['titulo']}</span>
                            </div>
                            <div style="display: flex; gap: 8px; align-items: center;">
                                <span style="background: {status_cor}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px;">{status_nome}</span>
                                <span style="background: {urgencia_cor}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px;">📅 {dias_status}d</span>
                                <span style="background: #6366f1; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px;">{int(row['sp'])} SP</span>
                            </div>
                        </div>
                        <div style="margin-top: 6px; font-size: 12px; color: #94a3b8;">
                            👤 DEV: {row['desenvolvedor']} | 🏷️ {row.get('complexidade', 'N/A')} | 🕐 Atualizado: {tempo_atualizacao}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.success("✅ Nenhum card em trabalho no momento - fila limpa!")
            
            st.markdown("---")
            
            # ===== CARDS REPROVADOS =====
            df_reprovados_qa = df_qa[df_qa['status_cat'] == 'rejected'].copy()
            
            st.markdown("**❌ Cards Reprovados**")
            st.caption("Cards que você reprovou e voltaram para correção")
            
            if not df_reprovados_qa.empty:
                df_reprovados_sorted = df_reprovados_qa.sort_values('atualizado', ascending=False)
                
                st.markdown('<div class="scroll-container" style="max-height: 350px;">', unsafe_allow_html=True)
                for _, row in df_reprovados_sorted.iterrows():
                    data_ref = row.get('atualizado')
                    data_reprovacao = data_ref.strftime("%d/%m %H:%M") if pd.notna(data_ref) else "N/A"
                    card_link = card_link_com_popup(row['ticket_id'])
                    
                    st.markdown(f"""
                    <div class="card-lista-vermelho">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                            <div style="flex: 1; min-width: 200px;">
                                <strong>❌ {card_link}</strong>
                                <span style="color: #64748b;"> - {row['titulo']}</span>
                            </div>
                            <div style="display: flex; gap: 8px; align-items: center;">
                                <span style="background: #dc2626; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px;">Reprovado</span>
                                <span style="background: #ef4444; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px;">🐛 {int(row['bugs'])}</span>
                                <span style="background: #6366f1; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px;">{int(row['sp'])} SP</span>
                            </div>
                        </div>
                        <div style="margin-top: 6px; font-size: 12px; color: #94a3b8;">
                            📅 {data_reprovacao} | 👤 DEV: {row['desenvolvedor']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("💡 Nenhum card reprovado no momento")
            
            st.markdown("---")
            
            # ===== CARDS IMPEDIDOS =====
            df_impedidos_qa = df_qa[df_qa['status_cat'] == 'blocked'].copy()
            
            if not df_impedidos_qa.empty:
                st.markdown("**🚫 Cards Impedidos**")
                st.caption("Cards bloqueados que precisam de atenção")
                
                st.markdown('<div class="scroll-container" style="max-height: 300px;">', unsafe_allow_html=True)
                for _, row in df_impedidos_qa.iterrows():
                    card_link = card_link_com_popup(row['ticket_id'])
                    st.markdown(f"""
                    <div class="card-lista-vermelho">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                            <div style="flex: 1; min-width: 200px;">
                                <strong>🚫 {card_link}</strong>
                                <span style="color: #64748b;"> - {row['titulo']}</span>
                            </div>
                            <div style="display: flex; gap: 8px; align-items: center;">
                                <span style="background: #ef4444; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px;">Impedido</span>
                                <span style="background: #6366f1; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px;">{int(row['sp'])} SP</span>
                            </div>
                        </div>
                        <div style="margin-top: 6px; font-size: 12px; color: #94a3b8;">
                            👤 DEV: {row['desenvolvedor']} | ⏱️ {row['dias_em_status']}d bloqueado
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("---")
            
            # Cards Validados na Semana (Timeline detalhada)
            st.markdown("**✅ Cards Validados na Semana**")
            st.caption("Cards que você concluiu a validação")
            
            if not df_validados_semana.empty:
                # Ordena por resolutiondate (mais preciso) ou atualizado
                sort_col = 'resolutiondate' if 'resolutiondate' in df_validados_semana.columns and df_validados_semana['resolutiondate'].notna().any() else 'atualizado'
                df_validados_semana_sorted = df_validados_semana.sort_values(sort_col, ascending=False)
                
                st.markdown('<div class="scroll-container" style="max-height: 400px;">', unsafe_allow_html=True)
                for _, row in df_validados_semana_sorted.iterrows():
                    # Usa resolutiondate se disponível
                    data_ref = row.get('resolutiondate') if pd.notna(row.get('resolutiondate')) else row.get('atualizado')
                    data_validacao = data_ref.strftime("%d/%m %H:%M") if pd.notna(data_ref) else "N/A"
                    bugs_cor = '#22c55e' if row['bugs'] == 0 else '#f97316' if row['bugs'] == 1 else '#ef4444'
                    badge_bugs = f'<span style="background: {bugs_cor}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px;">🐛 {int(row["bugs"])}</span>' if row['bugs'] > 0 else '<span style="background: #22c55e; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px;">✅ Clean</span>'
                    card_link = card_link_com_popup(row['ticket_id'])
                    
                    st.markdown(f"""
                    <div class="card-lista-verde">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                            <div style="flex: 1; min-width: 200px;">
                                <strong>{card_link}</strong>
                                <span style="color: #64748b;"> - {row['titulo']}</span>
                            </div>
                            <div style="display: flex; gap: 8px; align-items: center;">
                                {badge_bugs}
                                <span style="background: #3b82f6; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px;">{int(row['sp'])} SP</span>
                            </div>
                        </div>
                        <div style="margin-top: 6px; font-size: 12px; color: #94a3b8;">
                            📅 {data_validacao} | 👤 DEV: {row['desenvolvedor']} | ⏱️ Lead Time: {row['lead_time']:.1f}d
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Resumo textual completo para copiar
                st.markdown("---")
                st.markdown("**📝 Resumo Completo (copie para a daily/retro):**")
                
                total_validados = len(df_validados_semana)
                total_sp_validados = int(df_validados_semana['sp'].sum())
                total_bugs = int(df_validados_semana['bugs'].sum())
                clean_rate = len(df_validados_semana[df_validados_semana['bugs'] == 0]) / total_validados * 100 if total_validados > 0 else 0
                
                # Monta resumo completo
                resumo_em_trabalho = ""
                if not df_em_trabalho.empty:
                    resumo_em_trabalho = "\n🔄 Em trabalho:\n" + "\n".join([f"  • {row['ticket_id']}: {row['titulo']} ({'Aguardando' if row['status_cat'] == 'waiting_qa' else 'Validando'})" for _, row in df_em_trabalho_sorted.iterrows()])
                
                resumo_reprovados = ""
                if not df_reprovados_qa.empty:
                    resumo_reprovados = "\n❌ Reprovados:\n" + "\n".join([f"  • {row['ticket_id']}: {row['titulo']} ({int(row['bugs'])} bugs)" for _, row in df_reprovados_sorted.iterrows()])
                
                resumo_impedidos = ""
                if not df_impedidos_qa.empty:
                    resumo_impedidos = "\n🚫 Impedidos:\n" + "\n".join([f"  • {row['ticket_id']}: {row['titulo']}" for _, row in df_impedidos_qa.iterrows()])
                
                resumo_validados = ""
                if not df_validados_semana.empty:
                    resumo_validados = "\n✅ Validados:\n" + "\n".join([f"  • {row['ticket_id']}: {row['titulo']}" for _, row in df_validados_semana_sorted.iterrows()])
                
                resumo_texto = f"""📊 Resumo Semanal - {qa_sel}
📅 Período: {segunda_semana.strftime('%d/%m')} a {sexta_semana.strftime('%d/%m')}

📈 MÉTRICAS:
• {len(df_em_trabalho)} cards em trabalho
• {len(df_reprovados_qa)} cards reprovados
• {len(df_impedidos_qa)} cards impedidos
• {total_validados} cards validados
• {total_sp_validados} SP entregues
• {total_bugs} bugs encontrados
• {clean_rate:.0f}% FPY (taxa validação limpa)
{resumo_em_trabalho}{resumo_reprovados}{resumo_impedidos}{resumo_validados}"""
                
                st.code(resumo_texto, language=None)
            else:
                st.info("💡 Nenhum card foi validado nesta semana.")
            
            # Tempo de Ciclo por Card (se houver dados)
            if not df_validados_semana.empty:
                st.markdown("---")
                st.markdown("**⏱️ Tempo de Ciclo dos Cards da Semana**")
                
                df_tempo = df_validados_semana[['ticket_id', 'titulo', 'lead_time', 'sp']].copy()
                df_tempo.columns = ['Ticket', 'Título', 'Lead Time (dias)', 'SP']
                df_tempo = df_tempo.sort_values('Lead Time (dias)', ascending=False)
                
                st.dataframe(df_tempo, hide_index=True, use_container_width=True)
                
                media_lead = df_validados_semana['lead_time'].mean()
                cor_media = 'green' if media_lead <= 5 else 'yellow' if media_lead <= 10 else 'red'
                st.markdown(f"""
                <p style="text-align: center; margin-top: 10px;">
                    <span style="background: {cor_media}20; color: {cor_media}; padding: 5px 15px; border-radius: 20px; font-weight: bold;">
                        ⏱️ Média de Lead Time: {media_lead:.1f} dias
                    </span>
                </p>
                """, unsafe_allow_html=True)
        
        # Distribuição por Status
        with st.expander("📊 Distribuição por Status", expanded=True):
            status_count = df_qa['status_cat'].value_counts().reset_index()
            status_count.columns = ['Status', 'Cards']
            status_count['Status'] = status_count['Status'].map(lambda x: STATUS_NOMES.get(x, x))
            
            fig = px.pie(status_count, values='Cards', names='Status', hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        # Bugs por Desenvolvedor (que esse QA validou)
        with st.expander("🐛 Bugs por Desenvolvedor", expanded=True):
            bugs_dev = df_qa.groupby('desenvolvedor').agg({
                'bugs': 'sum', 'sp': 'sum', 'ticket_id': 'count'
            }).reset_index()
            bugs_dev.columns = ['Desenvolvedor', 'Bugs', 'SP', 'Cards']
            bugs_dev = bugs_dev.sort_values('Bugs', ascending=False)
            
            if not bugs_dev.empty:
                st.dataframe(bugs_dev, hide_index=True, use_container_width=True)
                
                fig = px.bar(bugs_dev.head(8), x='Desenvolvedor', y='Bugs', color='Bugs',
                             color_continuous_scale=['#22c55e', '#f97316', '#ef4444'])
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados de bugs por desenvolvedor")
        
        # Cards em Fila do QA
        with st.expander("📋 Cards em Fila (Aguardando/Validando)", expanded=True):
            cards_fila = df_qa[df_qa['status_cat'].isin(['waiting_qa', 'testing'])].sort_values('dias_em_status', ascending=False)
            
            if not cards_fila.empty:
                for _, row in cards_fila.iterrows():
                    dias = row['dias_em_status']
                    cor = '#ef4444' if dias > 3 else '#eab308' if dias > 1 else '#22c55e'
                    card_link = card_link_com_popup(row['ticket_id'])
                    st.markdown(f"""
                    <div style="padding: 10px; margin: 5px 0; border-left: 3px solid {cor}; background: rgba(100,100,100,0.05); border-radius: 4px;">
                        <strong>{card_link}</strong> - {row['titulo'][:50]}...<br>
                        <small style="color: #94a3b8;">📅 {dias} dia(s) | 👤 {row['desenvolvedor']} | {row['sp']} SP | {row['status']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ Nenhum card na fila!")
        
        # NOVAS MÉTRICAS INDIVIDUAIS
        with st.expander("📈 Throughput e Eficiência", expanded=True):
            st.caption("💡 **Throughput**: Quantidade de cards/SP entregues por período. Indica capacidade de entrega.")
            col1, col2 = st.columns(2)
            
            with col1:
                # Throughput semanal
                df_done_qa = df_qa[df_qa['status_cat'] == 'done'].copy()
                if not df_done_qa.empty and 'updated_at' in df_done_qa.columns:
                    df_done_qa['semana'] = pd.to_datetime(df_done_qa['updated_at']).dt.isocalendar().week
                    throughput_sem = df_done_qa.groupby('semana').size().reset_index(name='Cards')
                    
                    if len(throughput_sem) > 1:
                        fig = px.line(throughput_sem, x='semana', y='Cards', markers=True,
                                      title=f'📊 Throughput Semanal - {qa_sel}')
                        fig.update_layout(height=250, xaxis_title="Semana", yaxis_title="Cards Validados")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Dados insuficientes para gráfico de throughput")
                else:
                    st.info("Sem histórico de validações")
            
            with col2:
                # Eficiência: SP por card
                sp_medio = df_qa['sp'].mean() if not df_qa.empty else 0
                bugs_por_card = df_qa['bugs'].mean() if not df_qa.empty else 0
                
                # Taxa de retrabalho
                cards_com_bugs = len(df_qa[df_qa['bugs'] > 0])
                total_validados = len(df_qa[df_qa['status_cat'] == 'done'])
                taxa_retrabalho = (cards_com_bugs / total_validados * 100) if total_validados > 0 else 0
                
                st.markdown(f"""
                <div style="padding: 15px; background: rgba(100,100,100,0.1); border-radius: 8px; margin-bottom: 10px;">
                    <h4 style="margin-top: 0;">📊 Indicadores de Eficiência</h4>
                    <p><strong>SP Médio por Card:</strong> {sp_medio:.1f}</p>
                    <p><strong>Bugs Médio por Card:</strong> {bugs_por_card:.2f}</p>
                    <p><strong>Taxa de Retrabalho:</strong> {taxa_retrabalho:.1f}%</p>
                    <p><strong>Validações Limpas (FPY):</strong> {fpy_val:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Comparativo com a Média do Time
        with st.expander("📊 Comparativo com o Time", expanded=True):
            # Métricas do time
            todos_qas = df[df['status_cat'] == 'done']
            media_time_bugs = todos_qas.groupby('qa')['bugs'].sum().mean() if not todos_qas.empty else 0
            media_time_sp = todos_qas.groupby('qa')['sp'].sum().mean() if not todos_qas.empty else 0
            media_time_validados = len(todos_qas) / len(todos_qas['qa'].unique()) if not todos_qas.empty else 0
            
            # Métricas individuais
            meus_bugs = int(df_qa['bugs'].sum())
            meu_sp = int(df_qa['sp'].sum())
            meus_validados = validados
            
            col1, col2, col3 = st.columns(3)
            with col1:
                diff_validados = meus_validados - media_time_validados
                cor = "green" if diff_validados >= 0 else "red"
                st.metric("Cards Validados", meus_validados, f"{diff_validados:+.0f} vs média", delta_color="normal")
            with col2:
                diff_sp = meu_sp - media_time_sp
                st.metric("Story Points", meu_sp, f"{diff_sp:+.0f} vs média", delta_color="normal")
            with col3:
                diff_bugs = meus_bugs - media_time_bugs
                st.metric("Bugs Encontrados", meus_bugs, f"{diff_bugs:+.0f} vs média", delta_color="inverse")
        
        # Distribuição de Complexidade
        with st.expander("🎯 Distribuição de Complexidade (SP)", expanded=False):
            sp_dist = df_qa.groupby('sp').size().reset_index(name='Cards')
            if not sp_dist.empty:
                fig = px.bar(sp_dist, x='sp', y='Cards', title="Cards por Story Points",
                             color='sp', color_continuous_scale='Blues')
                fig.update_layout(height=300, xaxis_title="Story Points", yaxis_title="Quantidade")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados de SP")
        
        # Cards Validados
        with st.expander("✅ Cards Validados (Histórico)", expanded=False):
            cards_done = df_qa[df_qa['status_cat'] == 'done'].sort_values('lead_time', ascending=False)
            
            if not cards_done.empty:
                for _, row in cards_done.iterrows():
                    bugs_cor = '#ef4444' if row['bugs'] >= 2 else '#eab308' if row['bugs'] == 1 else '#22c55e'
                    card_link = card_link_com_popup(row['ticket_id'])
                    st.markdown(f"""
                    <div style="padding: 10px; margin: 5px 0; border-left: 3px solid {bugs_cor}; background: rgba(100,100,100,0.05); border-radius: 4px;">
                        <strong>{card_link}</strong> - {row['titulo'][:50]}...<br>
                        <small style="color: #94a3b8;">🐛 {row['bugs']} bugs | 👤 {row['desenvolvedor']} | {row['sp']} SP | ⏱️ {row['lead_time']:.1f}d</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum card validado ainda")


def aba_dev(df: pd.DataFrame):
    """Aba de Dev - Performance, Ranking e Análise por Desenvolvedor."""
    st.markdown("### 👨‍💻 Painel de Desenvolvimento")
    st.caption("Performance individual, ranking e métricas de maturidade do time de desenvolvimento")
    
    devs = [d for d in df['desenvolvedor'].unique() if d != 'Não atribuído']
    
    # Suporte a query params para compartilhamento (link compartilhado)
    dev_url = st.query_params.get("dev", None)
    opcoes_dev = ["🏆 Ranking Geral"] + sorted(devs)
    indice_inicial = 0
    if dev_url and dev_url in devs:
        indice_inicial = opcoes_dev.index(dev_url)
    
    # SELETOR DE DEV (NÃO atualiza query_params - apenas o botão Copiar Link faz isso)
    dev_sel = st.selectbox("👤 Selecione o Desenvolvedor", opcoes_dev, index=indice_inicial, key="select_dev")
    
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
                                st.markdown(f"- [{row['ticket_id']}]({row['link']}) - {row['bugs']} bugs - {row['titulo']}")
            else:
                st.success("✅ Todos os desenvolvedores estão com FK adequado!")
        
        # Concentração de Conhecimento do Time DEV
        exibir_concentracao_time(df, "dev")
        
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
                st.metric("Cards sem Bugs", f"{cards_zero_bugs} ({pct_zero_bugs:.0f}%)", help=get_tooltip_help("fpy"))
                lead_medio = df['lead_time'].mean() if not df.empty else 0
                st.metric("Lead Time Médio", f"{lead_medio:.1f} dias", help=get_tooltip_help("lead_time"))
        
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
                        card_link = card_link_com_popup(row['ticket_id'])
                        st.markdown(f"""
                        <div style="padding: 8px; margin: 4px 0; border-left: 3px solid {cor}; background: rgba(99, 102, 241, 0.1); border-radius: 4px;">
                            <strong>{card_link}</strong> - {row['titulo']}<br>
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
                        card_link = card_link_com_popup(row['ticket_id'])
                        st.markdown(f"""
                        <div style="padding: 8px; margin: 4px 0; border-left: 3px solid #ef4444; background: rgba(239, 68, 68, 0.1); border-radius: 4px;">
                            <strong>{card_link}</strong> - {row['titulo']}<br>
                            <small style="color: #fca5a5;">⚠️ {row['prioridade']} | 👤 {row['desenvolvedor']} | {row['sp']} SP</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if len(criticos_dev) > 5:
                        st.warning(f"⚠️ {len(criticos_dev)} cards de alta prioridade ainda em desenvolvimento!")
                else:
                    st.success("✅ Nenhum card crítico pendente")
        
        # Cards Impedidos e Reprovados
        cards_impedidos_dev = df[df['status_cat'] == 'blocked']
        cards_reprovados_dev = df[df['status_cat'] == 'rejected']
        
        if len(cards_impedidos_dev) > 0 or len(cards_reprovados_dev) > 0:
            with st.expander("🚨 Cards Impedidos e Reprovados", expanded=True):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    cor = 'green' if len(cards_impedidos_dev) == 0 else 'yellow' if len(cards_impedidos_dev) < 3 else 'red'
                    criar_card_metrica(str(len(cards_impedidos_dev)), "🚫 Impedidos", cor, "Bloqueados")
                
                with col2:
                    cor = 'green' if len(cards_reprovados_dev) == 0 else 'yellow' if len(cards_reprovados_dev) < 3 else 'red'
                    criar_card_metrica(str(len(cards_reprovados_dev)), "❌ Reprovados", cor, "Falha validação")
                
                with col3:
                    sp_impedido = int(cards_impedidos_dev['sp'].sum())
                    cor = 'green' if sp_impedido == 0 else 'yellow' if sp_impedido < 10 else 'red'
                    criar_card_metrica(str(sp_impedido), "SP Impedidos", cor)
                
                with col4:
                    sp_reprovado = int(cards_reprovados_dev['sp'].sum())
                    cor = 'green' if sp_reprovado == 0 else 'yellow' if sp_reprovado < 10 else 'red'
                    criar_card_metrica(str(sp_reprovado), "SP Reprovados", cor)
                
                st.markdown("---")
                col_imp, col_rep = st.columns(2)
                
                with col_imp:
                    st.markdown("#### 🚫 Impedidos")
                    if not cards_impedidos_dev.empty:
                        html_imp_dev = '<div class="scroll-container" style="max-height: 350px;">'
                        for _, row in cards_impedidos_dev.iterrows():
                            card_link = card_link_com_popup(row['ticket_id'])
                            titulo = str(row['titulo'])
                            dev = str(row['desenvolvedor'])
                            qa = str(row['qa'])
                            sp = int(row['sp'])
                            html_imp_dev += '<div class="card-lista-vermelho">'
                            html_imp_dev += '<strong>' + card_link + '</strong>'
                            html_imp_dev += '<span style="color: #64748b;"> - ' + titulo + '</span><br>'
                            html_imp_dev += '<small style="color: #94a3b8;">👤 ' + dev + ' | 🧑‍🔬 ' + qa + ' | ' + str(sp) + ' SP</small>'
                            html_imp_dev += '</div>'
                        html_imp_dev += '</div>'
                        st.markdown(html_imp_dev, unsafe_allow_html=True)
                    else:
                        st.success("✅ Nenhum card impedido")
                
                with col_rep:
                    st.markdown("#### ❌ Reprovados")
                    if not cards_reprovados_dev.empty:
                        html_rep_dev = '<div class="scroll-container" style="max-height: 350px;">'
                        for _, row in cards_reprovados_dev.iterrows():
                            card_link = card_link_com_popup(row['ticket_id'])
                            titulo = str(row['titulo'])
                            dev = str(row['desenvolvedor'])
                            qa = str(row['qa'])
                            sp = int(row['sp'])
                            bugs = int(row['bugs'])
                            html_rep_dev += '<div class="card-lista-vermelho">'
                            html_rep_dev += '<strong>' + card_link + '</strong>'
                            html_rep_dev += '<span style="color: #64748b;"> - ' + titulo + '</span><br>'
                            html_rep_dev += '<small style="color: #94a3b8;">👤 ' + dev + ' | 🧑‍🔬 ' + qa + ' | ' + str(sp) + ' SP | 🐛 ' + str(bugs) + ' bugs</small>'
                            html_rep_dev += '</div>'
                        html_rep_dev += '</div>'
                        st.markdown(html_rep_dev, unsafe_allow_html=True)
                    else:
                        st.success("✅ Nenhum card reprovado")
    
    else:
        # ====== Métricas Individuais ======
        analise = analisar_dev_detalhado(df, dev_sel)
        
        if analise:
            # Header com título e botão de compartilhamento
            import urllib.parse
            base_url = NINADASH_URL
            share_url = f"{base_url}?aba=dev&dev={urllib.parse.quote(dev_sel)}"
            
            col_titulo, col_share = st.columns([3, 1])
            with col_titulo:
                st.markdown(f"### 👤 Métricas de {dev_sel}")
            with col_share:
                # Botão Copiar Link usando components.html (mesmo padrão do card individual)
                components.html(f"""
                <button id="copyBtnDev" style="
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
                    document.getElementById('copyBtnDev').addEventListener('click', function() {{
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
                        st.metric("Cards Desenvolvidos", analise['cards'], help="Total de cards atribuídos a este desenvolvedor no período")
                    with c2:
                        st.metric("Story Points", analise['sp_total'], help="Soma de Story Points de todos os cards do desenvolvedor")
                    with c3:
                        st.metric("Bugs Encontrados", analise['bugs_total'], help="Total de bugs encontrados pelo QA nos cards deste desenvolvedor")
                    with c4:
                        st.metric("Taxa Zero Bugs", f"{analise['zero_bugs']}%", help=get_tooltip_help("fpy"))
                    
                    # Cards impedidos/reprovados do DEV
                    df_dev_individual = analise['df']
                    cards_impedidos_dev_ind = df_dev_individual[df_dev_individual['status_cat'] == 'blocked']
                    cards_reprovados_dev_ind = df_dev_individual[df_dev_individual['status_cat'] == 'rejected']
                    
                    st.markdown("---")
                    ci1, ci2, ci3, ci4 = st.columns(4)
                    with ci1:
                        cor = 'green' if len(cards_impedidos_dev_ind) == 0 else 'yellow' if len(cards_impedidos_dev_ind) < 2 else 'red'
                        criar_card_metrica(str(len(cards_impedidos_dev_ind)), "🚫 Impedidos", cor)
                    with ci2:
                        cor = 'green' if len(cards_reprovados_dev_ind) == 0 else 'yellow' if len(cards_reprovados_dev_ind) < 2 else 'red'
                        criar_card_metrica(str(len(cards_reprovados_dev_ind)), "❌ Reprovados", cor)
                    with ci3:
                        em_dev = len(df_dev_individual[df_dev_individual['status_cat'] == 'development'])
                        criar_card_metrica(str(em_dev), "🔧 Em Dev", "blue")
                    with ci4:
                        em_cr = len(df_dev_individual[df_dev_individual['status_cat'] == 'code_review'])
                        criar_card_metrica(str(em_cr), "👀 Code Review", "purple")
                    
                    # Lista cards impedidos/reprovados se existirem
                    if len(cards_impedidos_dev_ind) > 0 or len(cards_reprovados_dev_ind) > 0:
                        st.markdown("---")
                        st.markdown("**🚨 Seus cards com problemas:**")
                        all_problemas_dev = pd.concat([cards_impedidos_dev_ind, cards_reprovados_dev_ind]) if not cards_reprovados_dev_ind.empty and not cards_impedidos_dev_ind.empty else (cards_impedidos_dev_ind if not cards_impedidos_dev_ind.empty else cards_reprovados_dev_ind)
                        html_problemas = '<div class="scroll-container" style="max-height: 300px;">'
                        for _, row in all_problemas_dev.iterrows():
                            status_icon = "🚫" if row['status_cat'] == 'blocked' else "❌"
                            status_name = "Impedido" if row['status_cat'] == 'blocked' else "Reprovado"
                            card_link = card_link_com_popup(row['ticket_id'])
                            titulo = str(row['titulo'])
                            qa = str(row['qa'])
                            sp = int(row['sp'])
                            html_problemas += '<div class="card-lista-vermelho">'
                            html_problemas += '<strong>' + status_icon + '</strong> ' + card_link + ' - ' + titulo + '<br>'
                            html_problemas += '<small style="color: #94a3b8;">🧑‍🔬 QA: ' + qa + ' | ' + status_name + ' | ' + str(sp) + ' SP</small>'
                            html_problemas += '</div>'
                        html_problemas += '</div>'
                        st.markdown(html_problemas, unsafe_allow_html=True)
            
            # ===== ÁREAS DE ATUAÇÃO (CONCENTRAÇÃO) =====
            exibir_concentracao_simplificada(df, dev_sel, "dev", expanded=False)
            
            # ===== NOVA SEÇÃO: RESUMO DA SEMANA - DEV =====
            with st.expander("📅 Resumo da Semana", expanded=True):
                st.caption("📊 Sua atividade semanal - ideal para daily/retro!")
                
                hoje = datetime.now()
                
                # Seletor de semana
                semanas_opcoes = {
                    "Semana Atual": 0,
                    "Semana Passada": 1,
                    "2 Semanas Atrás": 2,
                    "3 Semanas Atrás": 3,
                    "4 Semanas Atrás": 4
                }
                
                semana_selecionada = st.selectbox(
                    "📆 Selecione a semana:",
                    list(semanas_opcoes.keys()),
                    index=0,
                    key=f"semana_dev_{dev_sel}"
                )
                
                semanas_atras = semanas_opcoes[semana_selecionada]
                
                # Calcula início e fim da semana selecionada (segunda a sexta)
                dias_desde_segunda = hoje.weekday()
                segunda_atual = hoje - timedelta(days=dias_desde_segunda)
                segunda_semana = segunda_atual - timedelta(weeks=semanas_atras)
                sexta_semana = segunda_semana + timedelta(days=4)
                fim_sexta = sexta_semana + timedelta(days=1) - timedelta(seconds=1)
                inicio_semana = segunda_semana.replace(hour=0, minute=0, second=0)
                
                # Exibe período selecionado
                st.markdown(f"""
                <div style="background: #f1f5f9; padding: 8px 15px; border-radius: 6px; margin-bottom: 15px; text-align: center;">
                    <span style="color: #64748b;">📅 Período: <strong>{segunda_semana.strftime('%d/%m')} (Seg)</strong> a <strong>{sexta_semana.strftime('%d/%m')} (Sex)</strong></span>
                </div>
                """, unsafe_allow_html=True)
                
                df_dev = analise['df'].copy()
                
                # Filtra cards CONCLUÍDOS na semana usando resolutiondate (mais preciso)
                df_done_semana = df_dev[
                    (df_dev['status_cat'] == 'done') & 
                    (df_dev['resolutiondate'].notna()) &
                    (df_dev['resolutiondate'] >= inicio_semana) & 
                    (df_dev['resolutiondate'] <= fim_sexta)
                ].copy() if 'resolutiondate' in df_dev.columns else pd.DataFrame()
                
                # Fallback para atualizado se não houver resultados com resolutiondate
                if df_done_semana.empty:
                    df_done_semana = df_dev[
                        (df_dev['status_cat'] == 'done') & 
                        (df_dev['atualizado'] >= inicio_semana) & 
                        (df_dev['atualizado'] <= fim_sexta)
                    ].copy() if 'atualizado' in df_dev.columns else pd.DataFrame()
                
                # Cards que tiveram atividade na semana (todos os status)
                df_semana = df_dev[
                    (df_dev['atualizado'] >= inicio_semana) & 
                    (df_dev['atualizado'] <= fim_sexta)
                ].copy() if 'atualizado' in df_dev.columns else pd.DataFrame()
                
                # KPIs da Semana
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    criar_card_metrica(str(len(df_semana)), "Cards Trabalhados", "blue", f"{semana_selecionada}")
                with col2:
                    criar_card_metrica(str(len(df_done_semana)), "Concluídos", "green", "Entregues")
                with col3:
                    bugs_semana = int(df_done_semana['bugs'].sum()) if not df_done_semana.empty else 0
                    cor_bugs = 'green' if bugs_semana == 0 else 'yellow' if bugs_semana < 3 else 'red'
                    criar_card_metrica(str(bugs_semana), "Bugs Recebidos", cor_bugs, "Pelo QA")
                with col4:
                    sp_semana = int(df_done_semana['sp'].sum()) if not df_done_semana.empty else 0
                    criar_card_metrica(str(sp_semana), "SP Entregues", "green")
                
                st.markdown("---")
                
                # Evolução da Semana (gráfico de linhas - fila diminuindo, concluídos aumentando)
                st.markdown("**📈 Evolução da Semana**")
                st.caption("💡 Mostra trabalho em progresso diminuindo e entregas aumentando")
                
                # Calcula a evolução dia a dia
                cards_trabalho_semana = df_dev[
                    (df_dev['status_cat'].isin(['development', 'code_review', 'done'])) &
                    (df_dev['atualizado'] >= inicio_semana) & 
                    (df_dev['atualizado'] <= fim_sexta)
                ].copy()
                
                total_trabalho_inicial = len(cards_trabalho_semana)
                
                dias_evolucao = []
                
                for i in range(5):  # 0=seg, 4=sex
                    dia = segunda_semana + timedelta(days=i)
                    dia_str = dia.strftime("%d/%m")
                    dia_nome = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex'][i]
                    
                    # Converte dia para pd.Timestamp para comparação segura
                    dia_fim = pd.Timestamp(dia.date()) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
                    
                    # Cards concluídos até este dia (acumulado)
                    if 'resolutiondate' in df_dev.columns:
                        # Remove timezone se existir para comparação segura
                        col_resolution = df_dev['resolutiondate']
                        if hasattr(col_resolution.dtype, 'tz') and col_resolution.dtype.tz is not None:
                            col_resolution = col_resolution.dt.tz_localize(None)
                        
                        concluidos_ate_dia = len(df_dev[
                            (df_dev['status_cat'] == 'done') &
                            (col_resolution.notna()) &
                            (col_resolution >= inicio_semana) &
                            (col_resolution <= dia_fim)
                        ])
                        
                        if concluidos_ate_dia == 0:
                            col_atualizado = df_dev['atualizado']
                            if hasattr(col_atualizado.dtype, 'tz') and col_atualizado.dtype.tz is not None:
                                col_atualizado = col_atualizado.dt.tz_localize(None)
                            
                            concluidos_ate_dia = len(df_dev[
                                (df_dev['status_cat'] == 'done') &
                                (col_atualizado >= inicio_semana) &
                                (col_atualizado <= dia_fim)
                            ])
                    else:
                        concluidos_ate_dia = 0
                    
                    # Em trabalho = total inicial - concluídos até o dia
                    em_trabalho_dia = max(0, total_trabalho_inicial - concluidos_ate_dia)
                    
                    dias_evolucao.append({
                        'Dia': f"{dia_nome}\n{dia_str}",
                        'Em Trabalho': em_trabalho_dia,
                        'Entregues': concluidos_ate_dia
                    })
                
                df_evolucao = pd.DataFrame(dias_evolucao)
                
                # Gráfico de linhas com duas séries
                if total_trabalho_inicial > 0:
                    fig = go.Figure()
                    
                    # Linha de Em Trabalho (roxo, diminuindo)
                    fig.add_trace(go.Scatter(
                        x=df_evolucao['Dia'],
                        y=df_evolucao['Em Trabalho'],
                        mode='lines+markers+text',
                        name='Em Trabalho',
                        line=dict(color='#8b5cf6', width=3),
                        marker=dict(size=10),
                        text=df_evolucao['Em Trabalho'],
                        textposition='top center',
                        textfont=dict(size=12, color='#8b5cf6')
                    ))
                    
                    # Linha de Entregues (verde, aumentando)
                    fig.add_trace(go.Scatter(
                        x=df_evolucao['Dia'],
                        y=df_evolucao['Entregues'],
                        mode='lines+markers+text',
                        name='Entregues',
                        line=dict(color='#22c55e', width=3),
                        marker=dict(size=10),
                        text=df_evolucao['Entregues'],
                        textposition='bottom center',
                        textfont=dict(size=12, color='#22c55e')
                    ))
                    
                    fig.update_layout(
                        height=280,
                        margin=dict(l=20, r=20, t=30, b=20),
                        xaxis_title="",
                        yaxis_title="Cards",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("💡 Nenhum card em trabalho esta semana.")
                
                st.markdown("---")
                
                # Cards Concluídos na Semana (Timeline detalhada)
                st.markdown("**✅ Cards Concluídos na Semana**")
                
                if not df_done_semana.empty:
                    df_done_semana_sorted = df_done_semana.sort_values('resolutiondate' if 'resolutiondate' in df_done_semana.columns else 'atualizado', ascending=False)
                    
                    st.markdown('<div class="scroll-container" style="max-height: 400px;">', unsafe_allow_html=True)
                    for _, row in df_done_semana_sorted.iterrows():
                        # Usa resolutiondate se disponível
                        data_ref = row.get('resolutiondate') if pd.notna(row.get('resolutiondate')) else row.get('atualizado')
                        data_conclusao = data_ref.strftime("%d/%m %H:%M") if pd.notna(data_ref) else "N/A"
                        bugs_cor = '#22c55e' if row['bugs'] == 0 else '#f97316' if row['bugs'] == 1 else '#ef4444'
                        badge_bugs = f'<span style="background: {bugs_cor}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px;">🐛 {int(row["bugs"])}</span>' if row['bugs'] > 0 else '<span style="background: #22c55e; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px;">✅ Clean</span>'
                        card_link = card_link_com_popup(row['ticket_id'])
                        
                        st.markdown(f"""
                        <div class="card-lista-roxo">
                            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                                <div>
                                    <strong>{card_link}</strong>
                                    <span style="color: #64748b;"> - {row['titulo']}</span>
                                </div>
                                <div style="display: flex; gap: 8px; align-items: center;">
                                    {badge_bugs}
                                    <span style="background: #8b5cf6; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px;">{int(row['sp'])} SP</span>
                                </div>
                            </div>
                            <div style="margin-top: 6px; font-size: 12px; color: #94a3b8;">
                                📅 {data_conclusao} | 👤 QA: {row['qa']} | ⏱️ Lead Time: {row['lead_time']:.1f}d
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Resumo textual
                    st.markdown("---")
                    st.markdown("**📝 Resumo:**")
                    
                    total_done = len(df_done_semana)
                    total_sp = int(df_done_semana['sp'].sum())
                    total_bugs = int(df_done_semana['bugs'].sum())
                    clean_rate = len(df_done_semana[df_done_semana['bugs'] == 0]) / total_done * 100 if total_done > 0 else 0
                    
                    resumo_texto = f"""📊 Resumo Semanal - {dev_sel}
📅 Período: {segunda_semana.strftime('%d/%m')} a {sexta_semana.strftime('%d/%m')}

• {total_done} cards entregues
• {total_sp} Story Points
• {total_bugs} bugs encontrados pelo QA
• {clean_rate:.0f}% taxa de entrega limpa

Cards concluídos:
""" + "\n".join([f"- {row['ticket_id']}: {row['titulo']}" for _, row in df_done_semana_sorted.iterrows()])
                    
                    st.code(resumo_texto, language=None)
                else:
                    st.info("💡 Nenhum card foi concluído nesta semana.")
                
                # Tempo de Ciclo por Card (se houver dados)
                if not df_done_semana.empty:
                    st.markdown("---")
                    st.markdown("**⏱️ Tempo de Ciclo dos Cards da Semana**")
                    
                    df_tempo = df_done_semana[['ticket_id', 'titulo', 'lead_time', 'sp', 'bugs']].copy()
                    df_tempo.columns = ['Ticket', 'Título', 'Lead Time (dias)', 'SP', 'Bugs']
                    df_tempo = df_tempo.sort_values('Lead Time (dias)', ascending=False)
                    
                    st.dataframe(df_tempo, hide_index=True, use_container_width=True)
                    
                    media_lead = df_done_semana['lead_time'].mean()
                    cor_media = 'green' if media_lead <= 5 else 'yellow' if media_lead <= 10 else 'red'
                    st.markdown(f"""
                    <p style="text-align: center; margin-top: 10px;">
                        <span style="background: {cor_media}20; color: {cor_media}; padding: 5px 15px; border-radius: 20px; font-weight: bold;">
                            ⏱️ Média de Lead Time: {media_lead:.1f} dias
                        </span>
                    </p>
                    """, unsafe_allow_html=True)
            
            # Cards do dev
            with st.expander(f"📋 Cards de {dev_sel}", expanded=True):
                for _, row in analise['df'].iterrows():
                    bugs_cor = '#ef4444' if row['bugs'] >= 2 else '#eab308' if row['bugs'] == 1 else '#22c55e'
                    card_link = card_link_com_popup(row['ticket_id'])
                    st.markdown(f"""
                    <div style="padding: 10px; margin: 5px 0; border-left: 3px solid {bugs_cor}; background: rgba(100,100,100,0.05); border-radius: 4px;">
                        <strong>{card_link}</strong> - {row['titulo'][:50]}...<br>
                        <small style="color: #94a3b8;">🐛 {row['bugs']} bugs | 📊 {row['sp']} SP | 📍 {row['status']} | ⏱️ {row['lead_time']:.1f}d</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            # NOVAS MÉTRICAS INDIVIDUAIS DEV
            with st.expander("📈 Throughput e Produtividade", expanded=True):
                st.caption("💡 **Throughput**: Vazão de entregas por período. **Fator K**: Qualidade = SP / (Bugs + 1)")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Throughput semanal
                    df_dev = analise['df'].copy()
                    if not df_dev.empty and 'updated_at' in df_dev.columns:
                        df_done_dev = df_dev[df_dev['status_cat'] == 'done']
                        if not df_done_dev.empty:
                            df_done_dev = df_done_dev.copy()
                            df_done_dev['semana'] = pd.to_datetime(df_done_dev['updated_at']).dt.isocalendar().week
                            throughput_sem = df_done_dev.groupby('semana').agg({
                                'ticket_id': 'count',
                                'sp': 'sum'
                            }).reset_index()
                            throughput_sem.columns = ['Semana', 'Cards', 'SP']
                            
                            if len(throughput_sem) > 1:
                                fig = px.line(throughput_sem, x='Semana', y='SP', markers=True,
                                              title=f'📊 SP Entregues por Semana')
                                fig.update_layout(height=250, xaxis_title="Semana", yaxis_title="Story Points")
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("Dados insuficientes para gráfico de throughput")
                        else:
                            st.info("Sem cards finalizados")
                    else:
                        st.info("Sem histórico disponível")
                
                with col2:
                    # Métricas de eficiência
                    sp_medio = analise['df']['sp'].mean() if not analise['df'].empty else 0
                    bugs_por_sp = analise['bugs_total'] / analise['sp_total'] if analise['sp_total'] > 0 else 0
                    lead_time_medio = analise['df']['lead_time'].mean() if 'lead_time' in analise['df'].columns else 0
                    
                    st.markdown(f"""
                    <div style="padding: 15px; background: rgba(100,100,100,0.1); border-radius: 8px; margin-bottom: 10px;">
                        <h4 style="margin-top: 0;">📊 Indicadores de Eficiência</h4>
                        <p><strong>SP Médio por Card:</strong> {sp_medio:.1f}</p>
                        <p><strong>Bugs por SP:</strong> {bugs_por_sp:.2f}</p>
                        <p><strong>Lead Time Médio:</strong> {lead_time_medio:.1f} dias</p>
                        <p><strong>Fator K:</strong> {analise['fk_medio']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Comparativo com a Média do Time
            with st.expander("📊 Comparativo com o Time", expanded=True):
                # Métricas do time
                todos_devs = df[df['status_cat'] == 'done']
                devs_list = [d for d in todos_devs['desenvolvedor'].unique() if d != 'Não atribuído']
                
                if devs_list:
                    media_time_bugs = todos_devs.groupby('desenvolvedor')['bugs'].sum().mean()
                    media_time_sp = todos_devs.groupby('desenvolvedor')['sp'].sum().mean()
                    media_time_cards = len(todos_devs) / len(devs_list) if devs_list else 0
                    media_time_fk = (todos_devs.groupby('desenvolvedor')['sp'].sum() / (todos_devs.groupby('desenvolvedor')['bugs'].sum() + 1)).mean()
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        diff_cards = analise['cards'] - media_time_cards
                        st.metric("Cards", analise['cards'], f"{diff_cards:+.0f} vs média", delta_color="normal")
                    with col2:
                        diff_sp = analise['sp_total'] - media_time_sp
                        st.metric("Story Points", analise['sp_total'], f"{diff_sp:+.0f} vs média", delta_color="normal")
                    with col3:
                        diff_bugs = analise['bugs_total'] - media_time_bugs
                        st.metric("Bugs", analise['bugs_total'], f"{diff_bugs:+.0f} vs média", delta_color="inverse")
                    with col4:
                        diff_fk = analise['fk_medio'] - media_time_fk
                        st.metric("Fator K", f"{analise['fk_medio']:.1f}", f"{diff_fk:+.1f} vs média", delta_color="normal")
                else:
                    st.info("Dados insuficientes para comparativo")
            
            # Distribuição por Status
            with st.expander("📊 Distribuição por Status", expanded=False):
                status_count = analise['df']['status_cat'].value_counts().reset_index()
                status_count.columns = ['Status', 'Cards']
                status_count['Status'] = status_count['Status'].map(lambda x: STATUS_NOMES.get(x, x))
                
                if not status_count.empty:
                    fig = px.pie(status_count, values='Cards', names='Status', hole=0.4,
                                 color_discrete_sequence=px.colors.qualitative.Set2)
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
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
    
    # REMOVER HOTFIX - não passa por produto, vai direto pra dev
    df_backlog = df_backlog[df_backlog['tipo'] != 'HOTFIX']
    
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
                st.dataframe(df_estag.head(15), hide_index=True, use_container_width=True)
            else:
                st.success("✅ Nenhum card estagnado!")
    
    # ===== NOVAS SEÇÕES ELLEN - PRODUTO =====
    
    # 1. Cards "Aguarda Revisão de Produto" com SLA Atrasado
    status_aguarda_revisao = "AGUARDA REVISÃO DE PRODUTO"
    df_aguarda_revisao = df[df['status'].str.upper() == status_aguarda_revisao.upper()].copy()
    
    if not df_aguarda_revisao.empty:
        with st.expander(f"⏰ Aguarda Revisão de Produto ({len(df_aguarda_revisao)} cards)", expanded=True):
            # Separar os atrasados
            df_atrasados = df_aguarda_revisao[df_aguarda_revisao['sla_atrasado'] == True] if 'sla_atrasado' in df_aguarda_revisao.columns else pd.DataFrame()
            df_no_prazo = df_aguarda_revisao[df_aguarda_revisao['sla_atrasado'] != True] if 'sla_atrasado' in df_aguarda_revisao.columns else df_aguarda_revisao
            
            col1, col2, col3 = st.columns(3)
            with col1:
                criar_card_metrica(str(len(df_aguarda_revisao)), "Total Aguardando", "blue", "Cards para revisar")
            with col2:
                cor = 'red' if len(df_atrasados) > 0 else 'green'
                criar_card_metrica(str(len(df_atrasados)), "SLA Atrasado", cor, "Precisam atenção urgente!")
            with col3:
                criar_card_metrica(str(len(df_no_prazo)), "No Prazo", "green", "Dentro do SLA")
            
            # Listar atrasados primeiro
            if not df_atrasados.empty:
                st.markdown("##### 🚨 Cards com SLA Atrasado")
                for _, card in df_atrasados.iterrows():
                    dias_esperando = (datetime.now() - card['atualizado']).days if pd.notna(card['atualizado']) else 0
                    card_link = card_link_com_popup(card['ticket_id'])
                    st.markdown(f"""
                    <div style="background: #fee2e2; border-left: 4px solid #ef4444; padding: 10px 15px; margin: 5px 0; border-radius: 4px;">
                        <span style="background: #ef4444; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">🚨 ATRASADO</span>
                        <span style="margin-left: 10px;">{card_link}</span>
                        <span style="color: #64748b;"> - {card['titulo'][:50]}...</span>
                        <span style="float: right; color: #dc2626; font-size: 12px;">{dias_esperando}d sem atualização</span>
                    </div>
                    """, unsafe_allow_html=True)
    
    # 2. Cards sem atuação há X dias (análise de tempo parado)
    dias_alerta = st.slider("⏳ Alertar cards sem atuação há mais de (dias):", 7, 60, 15, key="slider_dias_sem_atuacao")
    df['dias_sem_atuacao'] = (datetime.now() - pd.to_datetime(df['atualizado'])).dt.days
    df_sem_atuacao = df[df['dias_sem_atuacao'] >= dias_alerta].copy()
    
    if not df_sem_atuacao.empty:
        with st.expander(f"😴 Cards sem Atuação há {dias_alerta}+ dias ({len(df_sem_atuacao)} cards)", expanded=True):
            # Ordenar por dias sem atuação
            df_sem_atuacao = df_sem_atuacao.sort_values('dias_sem_atuacao', ascending=False)
            
            col1, col2 = st.columns(2)
            with col1:
                criar_card_metrica(str(len(df_sem_atuacao)), "Cards Parados", "orange", f"Sem atuação há {dias_alerta}+ dias")
            with col2:
                media_dias = df_sem_atuacao['dias_sem_atuacao'].mean()
                criar_card_metrica(f"{media_dias:.0f}d", "Média Parado", "red" if media_dias > 30 else "yellow", "Tempo médio sem atuação")
            
            # Tabela
            df_display = df_sem_atuacao[['ticket_id', 'titulo', 'dias_sem_atuacao', 'status', 'prioridade', 'produto']].head(15).copy()
            df_display.columns = ['Ticket', 'Título', 'Dias Parado', 'Status', 'Prioridade', 'Produto']
            st.dataframe(df_display, hide_index=True, use_container_width=True)
    
    # 3. Total de cards por Temas e por Produto
    if 'temas' in df.columns:
        with st.expander("🏷️ Análise por Temas e Produto", expanded=False):
            st.markdown("#### Cards por Tema/Cliente")
            st.caption("💡 *Demandas internas (nina, interna) não são exibidas aqui pois beneficiam todos os clientes*")
            
            # Expandir temas (multi-value)
            df_temas = df.explode('temas')
            df_temas = df_temas[df_temas['temas'].notna() & (df_temas['temas'] != '')]
            # Remove temas internos que não são clientes
            df_temas = df_temas[~df_temas['temas'].str.lower().str.strip().isin([t.lower() for t in TEMAS_NAO_CLIENTES])]
            
            if not df_temas.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Por Tema
                    tema_counts = df_temas.groupby('temas').agg({
                        'ticket_id': 'count',
                        'sp': 'sum'
                    }).reset_index()
                    tema_counts.columns = ['Tema', 'Cards', 'SP Total']
                    tema_counts = tema_counts.sort_values('Cards', ascending=False)
                    
                    fig = px.bar(tema_counts.head(10), x='Tema', y='Cards', 
                                 title='📊 Top 10 Temas/Clientes',
                                 color='Cards', color_continuous_scale='Blues')
                    fig.update_layout(height=350, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Por Produto E Tema (cruzamento)
                    produto_tema = df_temas.groupby(['produto', 'temas']).size().reset_index(name='Cards')
                    produto_tema = produto_tema.sort_values('Cards', ascending=False).head(15)
                    
                    st.markdown("##### 📦 Cruzamento Produto x Tema")
                    st.dataframe(produto_tema, hide_index=True, use_container_width=True)
            else:
                st.info("Nenhum card com tema definido")
    
    # 4. Tempo de Vida por Importância
    if 'importancia' in df.columns:
        with st.expander("⏱️ Tempo de Vida por Importância", expanded=True):
            st.markdown("##### Quanto tempo cada prioridade fica no backlog?")
            
            df['idade_dias'] = (datetime.now() - pd.to_datetime(df['criado'])).dt.days
            
            importancia_stats = df.groupby('importancia').agg({
                'ticket_id': 'count',
                'idade_dias': ['mean', 'median', 'max'],
                'sp': 'sum'
            }).reset_index()
            importancia_stats.columns = ['Importância', 'Cards', 'Idade Média', 'Idade Mediana', 'Mais Antigo', 'SP Total']
            
            # Ordenar por importância
            ordem_importancia = {'Alto': 1, 'Médio': 2, 'Baixo': 3, 'Não definido': 4}
            importancia_stats['ordem'] = importancia_stats['Importância'].map(ordem_importancia).fillna(5)
            importancia_stats = importancia_stats.sort_values('ordem').drop('ordem', axis=1)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de barras
                fig = px.bar(importancia_stats, x='Importância', y='Idade Média',
                             title='📊 Idade Média por Importância (dias)',
                             color='Importância',
                             color_discrete_map={'Alto': '#ef4444', 'Médio': '#f59e0b', 'Baixo': '#22c55e', 'Não definido': '#94a3b8'})
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Tabela
                importancia_stats['Idade Média'] = importancia_stats['Idade Média'].round(1).astype(str) + 'd'
                importancia_stats['Idade Mediana'] = importancia_stats['Idade Mediana'].round(1).astype(str) + 'd'
                importancia_stats['Mais Antigo'] = importancia_stats['Mais Antigo'].astype(str) + 'd'
                st.dataframe(importancia_stats, hide_index=True, use_container_width=True)
            
            # Alerta se itens de alta prioridade estão velhos
            df_alta = df[df['importancia'] == 'Alto']
            if not df_alta.empty:
                alta_velhos = df_alta[df_alta['idade_dias'] > 30]
                if not alta_velhos.empty:
                    st.warning(f"⚠️ {len(alta_velhos)} cards de **Alta Importância** estão há mais de 30 dias no backlog!")
    
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


# ==============================================================================
# ABA SUPORTE/IMPLANTAÇÃO
# ==============================================================================

def aba_suporte_implantacao(df_todos: pd.DataFrame):
    """
    Aba de Suporte e Implantação - Visão consolidada para times de suporte/implantação.
    
    Similar às abas QA e Dev:
    - Seletor de pessoa (relator): inclui "Ver Todos" para visão geral
    - Visão de cards em TODOS os projetos
    - Foco: "Onde estão meus cards?" + "O que precisa de validação/resposta?"
    
    Args:
        df_todos: DataFrame com cards de TODOS os projetos (SD, QA, PB, VALPROD)
    """
    st.markdown("### 🎯 Suporte e Implantação")
    st.caption("Acompanhe seus cards em todos os projetos: SD, QA, PB e VALPROD • *Os filtros de Projeto/Período da sidebar afetam outras abas*")
    
    if df_todos is None or df_todos.empty:
        st.warning("⚠️ Nenhum card encontrado nos projetos.")
        return
    
    # Verifica se a coluna 'relator' existe
    if 'relator' not in df_todos.columns:
        st.warning("⚠️ Coluna 'relator' não encontrada nos dados.")
        return
    
    # ========== SELETOR DE PESSOA (igual QA/Dev) ==========
    # Coleta relatores de todos os projetos
    relatores = sorted([r for r in df_todos['relator'].dropna().unique() 
                       if r and r != 'Não informado'])
    
    # Verifica se tem pessoa na URL (link compartilhado)
    pessoa_url = st.query_params.get("pessoa", None)
    pessoa_index = 0  # "👥 Ver Todos" é sempre index 0
    if pessoa_url and pessoa_url in relatores:
        pessoa_index = relatores.index(pessoa_url) + 1  # +1 porque "👥 Ver Todos" é index 0
    
    # SELETOR DE PESSOA (NÃO atualiza query_params - apenas o botão Copiar Link faz isso)
    pessoa_selecionada = st.selectbox(
        "👤 Selecione a pessoa",
        options=["👥 Ver Todos"] + relatores,
        index=pessoa_index,
        key="pessoa_suporte"
    )
    
    # ========== VISÃO GERAL (quando seleciona "Ver Todos") ==========
    if pessoa_selecionada == "👥 Ver Todos":
        
        st.markdown("---")
        
        # ===== MÉTRICAS GERAIS DO TIME =====
        st.markdown("#### 📊 Métricas Gerais do Time")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_cards = len(df_todos)
        projetos = df_todos['projeto'].unique() if 'projeto' in df_todos.columns else []
        
        with col1:
            total_sd = len(df_todos[df_todos['projeto'] == 'SD']) if 'projeto' in df_todos.columns else 0
            st.metric("📋 SD", total_sd, delta=f"{(total_sd/total_cards*100):.0f}%" if total_cards > 0 else None)
        
        with col2:
            total_qa = len(df_todos[df_todos['projeto'] == 'QA']) if 'projeto' in df_todos.columns else 0
            st.metric("🔬 QA", total_qa, delta=f"{(total_qa/total_cards*100):.0f}%" if total_cards > 0 else None)
        
        with col3:
            total_pb = len(df_todos[df_todos['projeto'] == 'PB']) if 'projeto' in df_todos.columns else 0
            st.metric("📦 PB", total_pb, delta=f"{(total_pb/total_cards*100):.0f}%" if total_cards > 0 else None)
        
        with col4:
            total_valprod = len(df_todos[df_todos['projeto'] == 'VALPROD']) if 'projeto' in df_todos.columns else 0
            st.metric("✅ VALPROD", total_valprod, delta=f"{(total_valprod/total_cards*100):.0f}%" if total_cards > 0 else None)
        
        with col5:
            pessoas_unicas = df_todos['relator'].nunique()
            st.metric("👥 Pessoas", pessoas_unicas)
        
        # ===== GRÁFICO: CARDS POR PROJETO E STATUS - EM EXPANDER =====
        with st.expander("📊 Distribuição de Cards", expanded=True):
            st.caption("Gráficos mostrando como os cards estão distribuídos entre projetos e status")
            
            col_graf1, col_graf2 = st.columns(2)
            
            with col_graf1:
                # Gráfico de Pizza por Projeto
                if 'projeto' in df_todos.columns:
                    projeto_counts = df_todos['projeto'].value_counts().reset_index()
                    projeto_counts.columns = ['projeto', 'count']
                    
                    cores_projeto = {'SD': '#3b82f6', 'QA': '#22c55e', 'PB': '#f59e0b', 'VALPROD': '#8b5cf6'}
                    
                    fig_pizza = px.pie(projeto_counts, values='count', names='projeto',
                                       title='📊 Cards por Projeto',
                                       color='projeto',
                                       color_discrete_map=cores_projeto)
                    fig_pizza.update_layout(height=350)
                    st.plotly_chart(fig_pizza, use_container_width=True)
            
            with col_graf2:
                # Gráfico de Barras por Status (top 10)
                if 'status' in df_todos.columns:
                    status_counts = df_todos['status'].value_counts().head(10).reset_index()
                    status_counts.columns = ['status', 'count']
                    
                    fig_bar = px.bar(status_counts, x='count', y='status', orientation='h',
                                     title='📋 Top 10 Status',
                                     color='count',
                                     color_continuous_scale='Blues')
                    fig_bar.update_layout(height=350, showlegend=False)
                    st.plotly_chart(fig_bar, use_container_width=True)
            
            # ===== GRÁFICO: CARDS POR PROJETO E STATUS (Stacked) =====
            col_graf3, col_graf4 = st.columns(2)
            
            with col_graf3:
                # Gráfico de Barras Empilhadas
                if 'projeto' in df_todos.columns and 'status' in df_todos.columns:
                    status_por_projeto = df_todos.groupby(['projeto', 'status']).size().reset_index(name='count')
                    
                    if not status_por_projeto.empty:
                        fig_stacked = px.bar(status_por_projeto, x='projeto', y='count', color='status',
                                             title='📊 Cards por Projeto e Status',
                                             labels={'projeto': 'Projeto', 'count': 'Cards', 'status': 'Status'})
                        fig_stacked.update_layout(height=400, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.3))
                        st.plotly_chart(fig_stacked, use_container_width=True)
            
            with col_graf4:
                # Top Relatores (filtra bots e automações)
                st.markdown("##### 👥 Top 15 Pessoas com Mais Cards")
                if 'relator' in df_todos.columns:
                    # Lista de nomes a filtrar (bots, automações, etc)
                    bots_filter = ['automation for jira', 'jira automation', 'system', 'admin', 
                                   'automação', 'bot', 'script', 'integration', 'webhook']
                    
                    # Filtra e conta
                    relatores_filtrados = df_todos[~df_todos['relator'].str.lower().str.contains(
                        '|'.join(bots_filter), na=True)]['relator']
                    top_relatores = relatores_filtrados.value_counts().head(15)
                    
                    contador = 0
                    for relator, count in top_relatores.items():
                        if relator and relator != 'Não informado' and contador < 15:
                            # Calcula proporção para barra visual
                            pct = count / top_relatores.max() * 100
                            contador += 1
                            st.markdown(f"""
                            <div style="margin: 4px 0;">
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="min-width: 25px; font-weight: bold; color: #64748b;">{contador}.</span>
                                    <span style="flex: 1; font-size: 0.9em;">{relator}</span>
                                    <span style="font-weight: bold; color: #AF0C37;">{count}</span>
                                </div>
                                <div style="background: #e5e7eb; height: 4px; border-radius: 2px; margin-top: 2px;">
                                    <div style="background: linear-gradient(90deg, #AF0C37, #f59e0b); height: 100%; width: {pct}%; border-radius: 2px;"></div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
        
        # ===== CARDS AGUARDANDO AÇÃO (VISÃO GERAL) - EM EXPANDER =====
        
        # Conta totais para exibir no título do expander
        df_aguard_resp = df_todos[df_todos['status'].str.lower().str.contains('aguardando', na=False)]
        df_valprod_pend = df_todos[(df_todos['projeto'] == 'VALPROD') & 
                                   (~df_todos['status'].str.lower().str.contains('aprovado|validado|concluído', na=False))]
        df_pb_aguard = df_todos[(df_todos['projeto'] == 'PB') & 
                                (df_todos['status'].str.lower().str.contains('aguardando|roteiro|ux', na=False))]
        total_aguardando = len(df_aguard_resp) + len(df_valprod_pend) + len(df_pb_aguard)
        
        with st.expander(f"⏳ Cards Aguardando Ação ({total_aguardando})", expanded=True):
            st.caption("Cards que precisam de ação. O **responsável** mostrado é quem deve agir no card.")
            
            # Checkbox para ver todos os cards
            ver_todos_cards = st.checkbox("📋 Ver todos os cards (sem limite)", key="ver_todos_cards_aguardando", value=False)
            limite_cards = 999 if ver_todos_cards else 20
            
            col_aguard1, col_aguard2, col_aguard3 = st.columns(3)
            
            with col_aguard1:
                st.markdown(f"##### 💬 Aguardando Resposta ({len(df_aguard_resp)})")
                
                # Gera HTML com scroll usando classe padrão
                cards_html = '<div class="scroll-container" style="max-height: 400px;">'
                for _, card in df_aguard_resp.head(limite_cards).iterrows():
                    projeto = card.get('projeto', 'SD')
                    tipo = card.get('tipo', 'TAREFA')
                    tipo_cor = "#ef4444" if tipo == "HOTFIX" else "#f97316" if tipo == "BUG" else "#64748b"
                    responsavel = card.get('responsavel') or card.get('desenvolvedor') or card.get('qa') or card.get('relator', 'N/A')
                    if not responsavel or responsavel == 'Não atribuído':
                        responsavel = card.get('relator', 'N/A')
                    titulo = str(card.get('titulo', card.get('resumo', '')))[:80]
                    ticket_id = card.get('ticket_id', '')
                    popup_html = card_link_com_popup(ticket_id, projeto)
                    
                    cards_html += f'''
                    <div class="card-lista-amarelo">
                        <div style="display: flex; align-items: center; gap: 4px; flex-wrap: wrap; margin-bottom: 4px;">
                            <span style="background: #64748b; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">{projeto}</span>
                            <span style="background: {tipo_cor}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">{tipo}</span>
                            {popup_html}
                        </div>
                        <div style="font-size: 13px; color: #78350f; line-height: 1.4;">{titulo}{"..." if len(str(card.get("titulo", ""))) > 80 else ""}</div>
                        <div style="font-size: 11px; color: #92400e; margin-top: 4px;">👤 {responsavel}</div>
                    </div>'''
                cards_html += '</div>'
                if len(df_aguard_resp) > limite_cards:
                    cards_html += f'<p style="color: #64748b; font-size: 12px; margin-top: 8px; text-align: center;">... e mais {len(df_aguard_resp) - limite_cards} cards</p>'
                
                st.markdown(cards_html, unsafe_allow_html=True)
            
            with col_aguard2:
                st.markdown(f"##### 🔍 Validação Produção ({len(df_valprod_pend)})")
                
                cards_html2 = '<div class="scroll-container" style="max-height: 400px;">'
                for _, card in df_valprod_pend.head(limite_cards).iterrows():
                    tipo = card.get('tipo', 'TAREFA')
                    tipo_cor = "#ef4444" if tipo == "HOTFIX" else "#f97316" if tipo == "BUG" else "#64748b"
                    responsavel = card.get('responsavel') or card.get('desenvolvedor') or card.get('relator', 'N/A')
                    if not responsavel or responsavel == 'Não atribuído':
                        responsavel = card.get('relator', 'N/A')
                    titulo = str(card.get('titulo', card.get('resumo', '')))[:80]
                    ticket_id = card.get('ticket_id', '')
                    popup_html = card_link_com_popup(ticket_id, 'VALPROD')
                    
                    cards_html2 += f'''
                    <div class="card-lista-laranja">
                        <div style="display: flex; align-items: center; gap: 4px; flex-wrap: wrap; margin-bottom: 4px;">
                            <span style="background: {tipo_cor}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">{tipo}</span>
                            {popup_html}
                        </div>
                        <div style="font-size: 13px; color: #713f12; line-height: 1.4;">{titulo}{"..." if len(str(card.get("titulo", ""))) > 80 else ""}</div>
                        <div style="font-size: 11px; color: #854d0e; margin-top: 4px;">👤 {responsavel}</div>
                    </div>'''
                cards_html2 += '</div>'
                if len(df_valprod_pend) > limite_cards:
                    cards_html2 += f'<p style="color: #64748b; font-size: 12px; margin-top: 8px; text-align: center;">... e mais {len(df_valprod_pend) - limite_cards} cards</p>'
                
                st.markdown(cards_html2, unsafe_allow_html=True)
            
            with col_aguard3:
                st.markdown(f"##### 📦 Backlog ({len(df_pb_aguard)})")
                
                cards_html3 = '<div class="scroll-container" style="max-height: 400px;">'
                for _, card in df_pb_aguard.head(limite_cards).iterrows():
                    tipo = card.get('tipo', 'TAREFA')
                    tipo_cor = "#ef4444" if tipo == "HOTFIX" else "#f97316" if tipo == "BUG" else "#64748b"
                    responsavel = card.get('responsavel') or card.get('desenvolvedor') or card.get('relator', 'N/A')
                    if not responsavel or responsavel == 'Não atribuído':
                        responsavel = card.get('relator', 'N/A')
                    titulo = str(card.get('titulo', card.get('resumo', '')))[:80]
                    ticket_id = card.get('ticket_id', '')
                    popup_html = card_link_com_popup(ticket_id, 'PB')
                    
                    cards_html3 += f'''
                    <div class="card-lista-azul">
                        <div style="display: flex; align-items: center; gap: 4px; flex-wrap: wrap; margin-bottom: 4px;">
                            <span style="background: {tipo_cor}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">{tipo}</span>
                            {popup_html}
                        </div>
                        <div style="font-size: 13px; color: #075985; line-height: 1.4;">{titulo}{"..." if len(str(card.get("titulo", ""))) > 80 else ""}</div>
                        <div style="font-size: 11px; color: #0369a1; margin-top: 4px;">👤 {responsavel}</div>
                    </div>'''
                cards_html3 += '</div>'
                if len(df_pb_aguard) > limite_cards:
                    cards_html3 += f'<p style="color: #64748b; font-size: 12px; margin-top: 8px; text-align: center;">... e mais {len(df_pb_aguard) - limite_cards} cards</p>'
                
                st.markdown(cards_html3, unsafe_allow_html=True)
        
        # ===== GRÁFICOS: TIPOS E IDADE - EM EXPANDER =====
        with st.expander("📊 Análise de Distribuição", expanded=False):
            st.caption("Visualize a distribuição dos cards por **tipo** (Bug, Hotfix, Tarefa) e por **idade** (quanto tempo desde a criação)")
            
            col_tipo1, col_tipo2 = st.columns(2)
            
            with col_tipo1:
                st.markdown("##### 🏷️ Distribuição por Tipo")
                st.caption("Mostra a proporção de cada tipo de card (Hotfix, Bug, Tarefa, etc)")
                if 'tipo' in df_todos.columns:
                    tipo_counts = df_todos['tipo'].value_counts().reset_index()
                    tipo_counts.columns = ['tipo', 'count']
                    
                    cores_tipo = {'HOTFIX': '#ef4444', 'BUG': '#f97316', 'TAREFA': '#64748b', 'SUGESTÃO': '#6366f1', 'HISTÓRIA': '#22c55e'}
                    
                    fig_tipo = px.pie(tipo_counts, values='count', names='tipo',
                                      color='tipo',
                                      color_discrete_map=cores_tipo)
                    fig_tipo.update_layout(height=300)
                    st.plotly_chart(fig_tipo, use_container_width=True)
            
            with col_tipo2:
                st.markdown("##### 📅 Cards por Idade")
                st.caption("Quanto tempo os cards estão abertos. Cards antigos (> 3 meses) precisam de atenção!")
                if 'criado' in df_todos.columns:
                    df_com_idade = df_todos.copy()
                    df_com_idade['idade_dias'] = (datetime.now() - pd.to_datetime(df_com_idade['criado'])).dt.days
                    
                    faixas = pd.cut(df_com_idade['idade_dias'], 
                                   bins=[0, 7, 14, 30, 90, float('inf')],
                                   labels=['< 1 sem', '1-2 sem', '2-4 sem', '1-3 meses', '> 3 meses'])
                    faixa_counts = faixas.value_counts().reset_index()
                    faixa_counts.columns = ['faixa', 'count']
                    
                    fig_idade = px.bar(faixa_counts, x='faixa', y='count',
                                       color='count', color_continuous_scale='Reds')
                    fig_idade.update_layout(height=300, showlegend=False)
                    st.plotly_chart(fig_idade, use_container_width=True)
        
        return
    
    st.markdown("---")
    
    # ========== FILTRAR CARDS DA PESSOA ==========
    df_pessoa = df_todos[df_todos['relator'] == pessoa_selecionada].copy()
    
    if df_pessoa.empty:
        st.warning(f"⚠️ Nenhum card encontrado para **{pessoa_selecionada}** no período selecionado.")
        return
    
    # ========== RESUMO: ONDE ESTÃO MEUS CARDS ==========
    # Linha com nome da pessoa + botão copiar link (IGUAL AO QA/DEV)
    import urllib.parse
    base_url = NINADASH_URL
    share_url = f"{base_url}?aba=suporte&pessoa={urllib.parse.quote(pessoa_selecionada)}"
    
    col_titulo, col_copiar = st.columns([3, 1])
    
    with col_titulo:
        st.markdown(f"### 👤 Métricas de {pessoa_selecionada}")
    
    with col_copiar:
        # Botão Copiar Link (IGUAL QA - mesmo estilo e altura)
        components.html(f"""
        <button id="copyBtnSuporteIndividual" style="
            background: linear-gradient(135deg, #AF0C37 0%, #8B0A2C 100%);
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
            document.getElementById('copyBtnSuporteIndividual').addEventListener('click', function() {{
                var url = '{share_url}';
                var btn = this;
                navigator.clipboard.writeText(url).then(function() {{
                    btn.innerHTML = '✅ Copiado!';
                    btn.style.background = 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)';
                    setTimeout(function() {{
                        btn.innerHTML = '📋 Copiar Link';
                        btn.style.background = 'linear-gradient(135deg, #AF0C37 0%, #8B0A2C 100%)';
                    }}, 2000);
                }}).catch(function() {{
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
                        btn.style.background = 'linear-gradient(135deg, #AF0C37 0%, #8B0A2C 100%)';
                    }}, 2000);
                }});
            }});
        </script>
        """, height=45)
    
    # Métricas por projeto
    col1, col2, col3, col4, col5 = st.columns(5)
    
    df_sd = df_pessoa[df_pessoa['projeto'] == 'SD'] if 'projeto' in df_pessoa.columns else pd.DataFrame()
    df_qa = df_pessoa[df_pessoa['projeto'] == 'QA'] if 'projeto' in df_pessoa.columns else pd.DataFrame()
    df_pb = df_pessoa[df_pessoa['projeto'] == 'PB'] if 'projeto' in df_pessoa.columns else pd.DataFrame()
    df_valprod = df_pessoa[df_pessoa['projeto'] == 'VALPROD'] if 'projeto' in df_pessoa.columns else pd.DataFrame()
    
    # Calcula total de concluídos em todos os projetos
    df_concluidos = df_pessoa[df_pessoa['status'].str.lower().str.contains(
        'concluído|finalizado|done|aprovado|validado|resolvido|closed|encerrado', na=False)]
    total_concluidos = len(df_concluidos)
    
    with col1:
        total_sd = len(df_sd)
        em_andamento_sd = len(df_sd[df_sd['status'].str.lower().str.contains('andamento|desenvolvimento|revisão|validação', na=False)]) if not df_sd.empty else 0
        st.metric("📋 SD", total_sd, delta=f"{em_andamento_sd} em andamento" if em_andamento_sd > 0 else None)
    
    with col2:
        total_qa = len(df_qa)
        st.metric("🔬 QA", total_qa)
    
    with col3:
        total_pb = len(df_pb)
        aguardando_pb = len(df_pb[df_pb['status'].str.lower().str.contains('aguardando', na=False)]) if not df_pb.empty else 0
        st.metric("📦 PB", total_pb, delta=f"{aguardando_pb} aguardando" if aguardando_pb > 0 else None)
    
    with col4:
        # Pendentes de validação (não concluídos) no VALPROD
        pendentes_valprod = len(df_valprod[~df_valprod['status'].str.lower().str.contains('aprovado|validado|concluído', na=False)]) if not df_valprod.empty else 0
        st.metric("🔍 Val. Prod", pendentes_valprod, delta="pendentes" if pendentes_valprod > 0 else None, delta_color="off")
    
    with col5:
        st.metric("✅ Concluídos", total_concluidos)
    
    # ========== 1. CARDS AGUARDANDO MINHA VALIDAÇÃO/AÇÃO - MAIS IMPORTANTE ==========
    # Cards onde a pessoa precisa agir: como QA, representante do cliente, ou responsável
    df_minha_acao = pd.DataFrame()
    
    # QA responsável
    if 'qa' in df_todos.columns:
        df_qa_resp = df_todos[
            (df_todos['qa'] == pessoa_selecionada) & 
            (df_todos['status'].str.lower().str.contains('aguardando validação|validação|testing|em teste|em qa', na=False, regex=True))
        ]
        df_minha_acao = pd.concat([df_minha_acao, df_qa_resp])
    
    # Representante do cliente
    if 'representante_cliente' in df_todos.columns:
        df_rep_cliente = df_todos[
            (df_todos['representante_cliente'] == pessoa_selecionada) & 
            (df_todos['status'].str.lower().str.contains('aguardando|validação|teste|cliente', na=False, regex=True))
        ]
        df_minha_acao = pd.concat([df_minha_acao, df_rep_cliente])
    
    # Responsável pelo card
    if 'responsavel' in df_todos.columns:
        df_responsavel = df_todos[
            (df_todos['responsavel'] == pessoa_selecionada) & 
            (df_todos['status'].str.lower().str.contains('aguardando|validação|pendente', na=False, regex=True))
        ]
        df_minha_acao = pd.concat([df_minha_acao, df_responsavel])
    
    # Remove duplicados
    if not df_minha_acao.empty:
        df_minha_acao = df_minha_acao.drop_duplicates(subset=['ticket_id'])
    
    if not df_minha_acao.empty:
        with st.expander(f"🔬 Cards Aguardando Minha Ação ({len(df_minha_acao)})", expanded=True):
            st.markdown(f"##### 🔬 {len(df_minha_acao)} cards para você validar/agir")
            st.caption("Cards onde você é QA, Representante do Cliente ou Responsável")
            
            # Construir HTML completo em string única
            html_minha_acao = '<div class="scroll-container" style="max-height: 450px;">'
            
            for _, card in df_minha_acao.iterrows():
                projeto = str(card.get('projeto', 'SD'))
                tipo = str(card.get('tipo', 'TAREFA'))
                tipo_cor = "#ef4444" if tipo == "HOTFIX" else "#f97316" if tipo == "BUG" else "#6366f1" if tipo == "SUGESTÃO" else "#64748b"
                titulo = str(card.get('titulo', card.get('resumo', '')))[:70]
                tempo_atualizacao = formatar_tempo_relativo(card.get('atualizado')) if 'atualizado' in card else ""
                relator = str(card.get('relator', 'N/A'))
                status_card = str(card.get('status', ''))
                
                # Identificar papel da pessoa
                papeis = []
                if card.get('qa') == pessoa_selecionada:
                    papeis.append("QA")
                if card.get('representante_cliente') == pessoa_selecionada:
                    papeis.append("Rep. Cliente")
                if card.get('responsavel') == pessoa_selecionada:
                    papeis.append("Responsável")
                papel_texto = " • ".join(papeis) if papeis else "Validador"
                
                card_link = card_link_com_popup(card['ticket_id'], projeto)
                sufixo = '...' if len(str(card.get('titulo', ''))) > 70 else ''
                
                html_minha_acao += '<div class="card-lista-roxo">'
                html_minha_acao += '<div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px; flex-wrap: wrap;">'
                html_minha_acao += '<span style="background: #64748b; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">' + projeto + '</span>'
                html_minha_acao += '<span style="background: ' + tipo_cor + '; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">' + tipo + '</span>'
                html_minha_acao += '<span style="background: #8b5cf6; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">' + papel_texto + '</span>'
                html_minha_acao += card_link
                html_minha_acao += '<span style="color: #7c3aed; font-size: 0.75em; margin-left: auto;">🕐 ' + tempo_atualizacao + '</span>'
                html_minha_acao += '</div>'
                html_minha_acao += '<div style="color: #5b21b6; font-size: 0.9em; line-height: 1.4;">' + titulo + sufixo + '</div>'
                html_minha_acao += '<div style="color: #64748b; font-size: 0.8em; margin-top: 4px;">Aberto por: ' + relator + ' • Status: ' + status_card + '</div>'
                html_minha_acao += '</div>'
            
            html_minha_acao += '</div>'
            st.markdown(html_minha_acao, unsafe_allow_html=True)
    
    # ========== 2. CARDS PARA VALIDAR EM PRODUÇÃO ==========
    with st.expander("🔍 Cards para Validar em Produção", expanded=True):
        if not df_valprod.empty:
            df_pendentes = df_valprod[~df_valprod['status'].str.lower().str.contains('aprovado|validado|concluído', na=False)]
            
            if not df_pendentes.empty:
                st.markdown(f"##### 🔍 {len(df_pendentes)} cards pendentes de validação")
                
                html_valprod = '<div class="scroll-container" style="max-height: 400px;">'
                for _, card in df_pendentes.iterrows():
                    dias = (datetime.now() - pd.to_datetime(card['criado'])).days if pd.notna(card.get('criado')) else 0
                    cor = "#ef4444" if dias > 7 else "#f59e0b" if dias > 3 else "#22c55e"
                    tipo = str(card.get('tipo', 'TAREFA'))
                    tipo_cor = "#ef4444" if tipo == "HOTFIX" else "#f97316" if tipo == "BUG" else "#6366f1" if tipo == "SUGESTÃO" else "#64748b"
                    titulo = str(card.get('titulo', card.get('resumo', '')))[:70]
                    tempo_atualizacao = formatar_tempo_relativo(card.get('atualizado')) if 'atualizado' in card else ""
                    status_card = str(card.get('status', 'N/A'))
                    sufixo = '...' if len(str(card.get('titulo', ''))) > 70 else ''
                    card_link = card_link_com_popup(card['ticket_id'], 'VALPROD')
                    
                    html_valprod += '<div class="card-lista" style="border-left-color: ' + cor + ';">'
                    html_valprod += '<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">'
                    html_valprod += '<span style="background: ' + tipo_cor + '; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: bold;">' + tipo + '</span>'
                    html_valprod += card_link
                    html_valprod += '<span style="color: #64748b; font-size: 0.75em; margin-left: auto;">🕐 ' + tempo_atualizacao + '</span>'
                    html_valprod += '</div>'
                    html_valprod += '<div style="color: #374151; font-size: 0.9em; line-height: 1.4;">' + titulo + sufixo + '</div>'
                    html_valprod += '<div style="color: #64748b; font-size: 0.8em; margin-top: 4px;">Status: ' + status_card + ' • Criado: ' + str(dias) + 'd atrás</div>'
                    html_valprod += '</div>'
                html_valprod += '</div>'
                st.markdown(html_valprod, unsafe_allow_html=True)
            else:
                st.success("✅ Nenhum card pendente de validação em produção!")
        else:
            st.info("ℹ️ Nenhum card encontrado no projeto VALPROD.")
    
    # ========== 3. CARDS CONCLUÍDOS ==========
    with st.expander("✅ Cards Concluídos", expanded=True):
        # Filtra cards concluídos/aprovados/validados em todos os projetos
        df_concluidos_lista = df_pessoa[df_pessoa['status'].str.lower().str.contains(
            'concluído|finalizado|done|aprovado|validado|resolvido|closed|encerrado', na=False)]
        
        if not df_concluidos_lista.empty:
            st.markdown(f"##### ✅ {len(df_concluidos_lista)} cards concluídos")
            
            # Ordena por data de criação (mais recente primeiro)
            df_concluidos_sorted = df_concluidos_lista.sort_values('criado', ascending=False) if 'criado' in df_concluidos_lista.columns else df_concluidos_lista
            
            html_concluidos = '<div class="scroll-container" style="max-height: 400px;">'
            for _, card in df_concluidos_sorted.head(30).iterrows():
                projeto = str(card.get('projeto', 'SD'))
                tipo = str(card.get('tipo', 'TAREFA'))
                tipo_cor = "#ef4444" if tipo == "HOTFIX" else "#f97316" if tipo == "BUG" else "#6366f1" if tipo == "SUGESTÃO" else "#64748b"
                titulo = str(card.get('titulo', card.get('resumo', '')))[:70]
                status = str(card.get('status', ''))
                sufixo = '...' if len(str(card.get('titulo', ''))) > 70 else ''
                
                # Cor do projeto
                projeto_cor = "#3b82f6" if projeto == "SD" else "#22c55e" if projeto == "QA" else "#f59e0b" if projeto == "PB" else "#8b5cf6"
                
                card_link = card_link_com_popup(card['ticket_id'], projeto)
                
                html_concluidos += '<div class="card-lista-verde">'
                html_concluidos += '<div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">'
                html_concluidos += '<span style="background: ' + projeto_cor + '; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">' + projeto + '</span>'
                html_concluidos += '<span style="background: ' + tipo_cor + '; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">' + tipo + '</span>'
                html_concluidos += card_link
                html_concluidos += '<span style="background: #22c55e; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; margin-left: auto;">✓ Concluído</span>'
                html_concluidos += '</div>'
                html_concluidos += '<div style="color: #166534; font-size: 0.9em; line-height: 1.4;">' + titulo + sufixo + '</div>'
                html_concluidos += '<div style="color: #64748b; font-size: 0.8em; margin-top: 4px;">Status: ' + status + '</div>'
                html_concluidos += '</div>'
            html_concluidos += '</div>'
            st.markdown(html_concluidos, unsafe_allow_html=True)
            
            if len(df_concluidos_lista) > 30:
                st.caption(f"... e mais {len(df_concluidos_lista) - 30} cards concluídos")
        else:
            st.info("ℹ️ Nenhum card concluído encontrado no período selecionado.")
    
    # ========== 4. GRÁFICO: CARDS POR PROJETO E STATUS ==========
    with st.expander("📊 Onde estão meus cards?", expanded=False):
        if 'projeto' in df_pessoa.columns:
            col_graf, col_lista = st.columns([1, 1])
            
            with col_graf:
                # Gráfico de barras empilhadas por projeto e status
                status_por_projeto = df_pessoa.groupby(['projeto', 'status']).size().reset_index(name='count')
                
                if not status_por_projeto.empty:
                    fig = px.bar(status_por_projeto, x='projeto', y='count', color='status',
                                 title='📊 Cards por Projeto e Status',
                                 labels={'projeto': 'Projeto', 'count': 'Cards', 'status': 'Status'})
                    fig.update_layout(height=350, showlegend=True)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col_lista:
                st.markdown("##### 📋 Detalhamento por Status")
                
                for projeto in ['SD', 'QA', 'PB', 'VALPROD']:
                    df_proj = df_pessoa[df_pessoa['projeto'] == projeto]
                    if not df_proj.empty:
                        st.markdown(f"**{projeto}** ({len(df_proj)} cards):")
                        status_counts = df_proj['status'].value_counts()
                        for status, count in status_counts.items():
                            # Cor baseada no status
                            cor = "#22c55e" if 'concluído' in status.lower() or 'validado' in status.lower() or 'aprovado' in status.lower() else \
                                  "#ef4444" if 'reprovado' in status.lower() or 'impedido' in status.lower() else \
                                  "#f59e0b" if 'aguardando' in status.lower() else \
                                  "#3b82f6"
                            st.markdown(f"<span style='color: {cor};'>●</span> {status}: **{count}**", unsafe_allow_html=True)
                        st.markdown("")
    
    # ========== 5. CARDS AGUARDANDO RESPOSTA (fechado por padrão - muitos cards) ==========
    with st.expander("💬 Cards Aguardando Resposta", expanded=False):
        # Cards com status "aguardando" em qualquer projeto (várias variações)
        filtro_aguardando = 'aguardando|waiting|pendente resposta|aguarda |em espera'
        df_aguardando = df_pessoa[df_pessoa['status'].str.lower().str.contains(filtro_aguardando, na=False, regex=True)]
        
        if not df_aguardando.empty:
            st.markdown(f"##### 💬 {len(df_aguardando)} cards aguardando algum retorno")
            
            for _, card in df_aguardando.iterrows():
                dias = (datetime.now() - pd.to_datetime(card['criado'])).days if pd.notna(card.get('criado')) else 0
                projeto = card.get('projeto', 'SD')
                tipo = card.get('tipo', 'TAREFA')
                # Tempo desde última atualização
                tempo_atualizacao = formatar_tempo_relativo(card.get('atualizado')) if 'atualizado' in card else ""
                tipo_cor = "#ef4444" if tipo == "HOTFIX" else "#f97316" if tipo == "BUG" else "#6366f1" if tipo == "SUGESTÃO" else "#64748b"
                titulo = card.get('titulo', card.get('resumo', ''))[:70]
                
                st.markdown(f"""
                <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 12px; margin: 8px 0; border-radius: 0 8px 8px 0;">
                    <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
                        <span style="background: #64748b; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">{projeto}</span>
                        <span style="background: {tipo_cor}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">{tipo}</span>
                        {card_link_com_popup(card['ticket_id'], projeto)}
                        <span style="color: #64748b; font-size: 0.75em; margin-left: auto;">🕐 {tempo_atualizacao}</span>
                    </div>
                    <div style="color: #92400e; font-size: 0.9em; line-height: 1.4;">{titulo}{'...' if len(card.get('titulo', '')) > 70 else ''}</div>
                    <div style="color: #64748b; font-size: 0.8em; margin-top: 4px;">Status: {card.get('status', '')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ Nenhum card aguardando resposta!")
    
    # ========== 6. FUNIL DO PB ==========
    with st.expander("📋 Meus Cards no Product Backlog", expanded=False):
        if not df_pb.empty:
            st.markdown(f"##### 📦 {len(df_pb)} cards no PB")
            
            # Agrupar por status
            status_counts = df_pb['status'].value_counts()
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("**Por Status:**")
                for status, count in status_counts.items():
                    st.markdown(f"- {status}: **{count}**")
            
            with col2:
                st.markdown("**Cards:**")
                for _, card in df_pb.head(10).iterrows():
                    dias = (datetime.now() - pd.to_datetime(card['criado'])).days if pd.notna(card.get('criado')) else 0
                    tipo = card.get('tipo', 'TAREFA')
                    tipo_cor = "#ef4444" if tipo == "HOTFIX" else "#f97316" if tipo == "BUG" else "#6366f1" if tipo == "SUGESTÃO" else "#64748b"
                    titulo = card.get('titulo', '')[:60]
                    
                    st.markdown(f"""
                    <div style="background: #f1f5f9; padding: 10px; margin: 6px 0; border-radius: 6px;">
                        <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                            <span style="background: {tipo_cor}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">{tipo}</span>
                            {card_link_com_popup(card['ticket_id'], 'PB')}
                            <span style="background: #cbd5e1; padding: 2px 6px; border-radius: 3px; font-size: 0.75em; margin-left: auto;">{card.get('status', '')}</span>
                        </div>
                        <div style="color: #374151; font-size: 0.85em;">{titulo}{'...' if len(card.get('titulo', '')) > 60 else ''}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                if len(df_pb) > 10:
                    st.caption(f"... e mais {len(df_pb) - 10} cards")
        else:
            st.info("ℹ️ Nenhum card no PB.")
    
    # ========== 7. TODOS OS CARDS SD/QA ==========
    with st.expander("📋 Meus Cards em Desenvolvimento (SD/QA)", expanded=False):
        df_dev = pd.concat([df_sd, df_qa]) if not df_sd.empty or not df_qa.empty else pd.DataFrame()
        
        if not df_dev.empty:
            st.markdown(f"##### 💻 {len(df_dev)} cards em SD/QA")
            
            # Agrupar por status
            status_counts = df_dev['status'].value_counts()
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("**Por Status:**")
                for status, count in status_counts.items():
                    st.markdown(f"- {status}: **{count}**")
            
            with col2:
                st.markdown("**Cards:**")
                for _, card in df_dev.head(10).iterrows():
                    projeto = card.get('projeto', 'SD')
                    tipo = card.get('tipo', 'TAREFA')
                    tipo_cor = "#ef4444" if tipo == "HOTFIX" else "#f97316" if tipo == "BUG" else "#6366f1" if tipo == "SUGESTÃO" else "#64748b"
                    titulo = card.get('titulo', '')[:55]
                    
                    st.markdown(f"""
                    <div style="background: #f1f5f9; padding: 10px; margin: 6px 0; border-radius: 6px;">
                        <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                            <span style="background: #374151; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">{projeto}</span>
                            <span style="background: {tipo_cor}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">{tipo}</span>
                            {card_link_com_popup(card['ticket_id'], projeto)}
                            <span style="background: #cbd5e1; padding: 2px 6px; border-radius: 3px; font-size: 0.75em; margin-left: auto;">{card.get('status', '')}</span>
                        </div>
                        <div style="color: #374151; font-size: 0.85em;">{titulo}{'...' if len(card.get('titulo', '')) > 55 else ''}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                if len(df_dev) > 10:
                    st.caption(f"... e mais {len(df_dev) - 10} cards")
        else:
            st.info("ℹ️ Nenhum card em SD/QA.")
    
    # ========== 8. TOOLTIP EXPLICATIVO ==========
    with st.expander("ℹ️ Sobre esta Aba", expanded=False):
        st.markdown("""
        ### 🎯 Suporte e Implantação — O que analisamos?
        
        Esta aba foi criada para você acompanhar **seus cards em todos os projetos**:
        
        | Seção | O que mostra |
        |-------|--------------|
        | **� Cards Aguardando Minha Validação** | Cards para você validar como QA |
        | **🔍 Cards para Validar em Produção** | Cards do VALPROD pendentes |
        | **✅ Cards Concluídos** | Cards finalizados |
        | **📊 Onde estão meus cards?** | Visão geral por projeto e status |
        | **💬 Cards Aguardando Resposta** | Cards que precisam de retorno |
        | **📋 PB** | Seus cards no Product Backlog |
        | **💻 SD/QA** | Seus cards em desenvolvimento |
        
        ### 🎯 Dicas:
        - Selecione sua pessoa para filtrar seus cards
        - Use o filtro de período na sidebar (Sprint Ativa, Todo período, etc)
        - Cards com mais de 7 dias pendentes aparecem em **vermelho**
        - Copie o link para compartilhar sua visão com outros
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
    
    # ===== NOVA SEÇÃO: ESFORÇO DO TIME =====
    with st.expander("💪 Esforço do Time (DEV + QA)", expanded=True):
        st.caption("Visualize a carga de trabalho e produtividade geral do time")
        
        # Métricas gerais do time
        col1, col2, col3, col4 = st.columns(4)
        
        # Total de devs ativos
        devs_ativos = df[df['desenvolvedor'] != 'Não atribuído']['desenvolvedor'].nunique()
        qas_ativos = df[df['qa'] != 'Não atribuído']['qa'].nunique()
        
        with col1:
            criar_card_metrica(str(devs_ativos), "DEVs Ativos", "blue", "Desenvolvendo")
        
        with col2:
            criar_card_metrica(str(qas_ativos), "QAs Ativos", "purple", "Validando")
        
        with col3:
            media_cards_dev = len(df) / devs_ativos if devs_ativos > 0 else 0
            criar_card_metrica(f"{media_cards_dev:.1f}", "Cards/DEV", "blue", "Média por dev")
        
        with col4:
            media_cards_qa = len(df) / qas_ativos if qas_ativos > 0 else 0
            criar_card_metrica(f"{media_cards_qa:.1f}", "Cards/QA", "purple", "Média por QA")
        
        st.markdown("---")
        
        # Distribuição de esforço DEV vs QA
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Carga por Desenvolvedor**")
            dev_carga = df[df['desenvolvedor'] != 'Não atribuído'].groupby('desenvolvedor').agg({
                'ticket_id': 'count',
                'sp': 'sum',
                'bugs': 'sum'
            }).reset_index()
            dev_carga.columns = ['DEV', 'Cards', 'SP', 'Bugs']
            dev_carga = dev_carga.sort_values('Cards', ascending=True)
            
            if not dev_carga.empty:
                fig = px.bar(dev_carga, x='Cards', y='DEV', orientation='h', color='SP',
                             color_continuous_scale='Blues', title='')
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados de desenvolvedores")
        
        with col2:
            st.markdown("**📊 Carga por QA**")
            qa_carga = df[df['qa'] != 'Não atribuído'].groupby('qa').agg({
                'ticket_id': 'count',
                'sp': 'sum',
                'bugs': 'sum'
            }).reset_index()
            qa_carga.columns = ['QA', 'Cards', 'SP', 'Bugs']
            qa_carga = qa_carga.sort_values('Cards', ascending=True)
            
            if not qa_carga.empty:
                fig = px.bar(qa_carga, x='Cards', y='QA', orientation='h', color='Bugs',
                             color_continuous_scale='Reds', title='')
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados de QAs")
        
        # Produtividade e Throughput
        st.markdown("---")
        st.markdown("**📈 Produtividade do Time**")
        
        col1, col2, col3 = st.columns(3)
        
        # Throughput (cards concluídos)
        with col1:
            throughput = len(df[df['status_cat'] == 'done'])
            criar_card_metrica(str(throughput), "Throughput", "green", "Cards concluídos")
        
        # Story Points entregues
        with col2:
            sp_entregues = int(df[df['status_cat'] == 'done']['sp'].sum())
            criar_card_metrica(str(sp_entregues), "SP Entregues", "green", "Story Points done")
        
        # Velocidade (SP/Dev)
        with col3:
            velocidade = sp_entregues / devs_ativos if devs_ativos > 0 else 0
            criar_card_metrica(f"{velocidade:.1f}", "Velocidade", "blue", "SP/DEV entregue")
    
    # ===== NOVA SEÇÃO: INTERAÇÃO QA x DEV (LIDERANÇA) =====
    with st.expander("🤝 Interação QA x DEV (Visão Liderança)", expanded=True):
        st.caption("Acompanhe a colaboração entre QAs e Desenvolvedores")
        
        # Filtra apenas cards com QA e DEV atribuídos
        df_interacao = df[(df['qa'] != 'Não atribuído') & (df['desenvolvedor'] != 'Não atribuído')].copy()
        
        if not df_interacao.empty:
            # Matriz de interação
            matriz = df_interacao.groupby(['qa', 'desenvolvedor']).agg({
                'ticket_id': 'count',
                'bugs': 'sum',
                'sp': 'sum'
            }).reset_index()
            matriz.columns = ['QA', 'DEV', 'Cards', 'Bugs', 'SP']
            matriz['FK'] = matriz.apply(lambda x: round(x['SP'] / (x['Bugs'] + 1), 2), axis=1)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📋 Top 10 Parcerias QA-DEV**")
                st.dataframe(matriz.sort_values('Cards', ascending=False).head(10), hide_index=True, use_container_width=True)
            
            with col2:
                st.markdown("**⚠️ Parcerias com Maior Retrabalho**")
                # Ordena por bugs (mais bugs = mais retrabalho)
                matriz_bugs = matriz[matriz['Bugs'] > 0].sort_values('Bugs', ascending=False).head(10)
                if not matriz_bugs.empty:
                    st.dataframe(matriz_bugs, hide_index=True, use_container_width=True)
                else:
                    st.success("✅ Nenhuma parceria com bugs significativos!")
            
            # Resumo de colaboração
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_parcerias = len(matriz)
                criar_card_metrica(str(total_parcerias), "Total Parcerias", "blue", "Combinações QA-DEV")
            
            with col2:
                media_cards_parceria = matriz['Cards'].mean()
                criar_card_metrica(f"{media_cards_parceria:.1f}", "Média Cards/Parceria", "green")
            
            with col3:
                parcerias_sem_bugs = len(matriz[matriz['Bugs'] == 0])
                pct_sem_bugs = parcerias_sem_bugs / total_parcerias * 100 if total_parcerias > 0 else 0
                criar_card_metrica(f"{pct_sem_bugs:.0f}%", "Parcerias Sem Bugs", "green")
            
            with col4:
                fk_medio = matriz['FK'].mean()
                cor = 'green' if fk_medio >= 3 else 'yellow' if fk_medio >= 2 else 'red'
                criar_card_metrica(f"{fk_medio:.1f}", "FK Médio Parcerias", cor)
        else:
            st.info("💡 Sem dados de interação QA-DEV. Verifique se os cards têm QA e Desenvolvedor atribuídos.")
    
    # ===== NOVA SEÇÃO: ANÁLISE DE CONCENTRAÇÃO DE CONHECIMENTO =====
    with st.expander("🔄 Análise de Concentração de Conhecimento (Rodízio)", expanded=True):
        st.caption("Identifique riscos de conhecimento centralizado e planeje rodízios para distribuir expertise no time")
        
        # Calcula métricas de concentração
        concentracao = calcular_concentracao_conhecimento(df)
        
        # ===== CARDS RESUMO NO TOPO =====
        alertas_criticos_dev = [a for a in concentracao['alertas_dev'] if a['tipo'] == 'critico']
        alertas_criticos_qa = [a for a in concentracao['alertas_qa'] if a['tipo'] == 'critico']
        alertas_atencao_dev = [a for a in concentracao['alertas_dev'] if a['tipo'] == 'atencao']
        alertas_atencao_qa = [a for a in concentracao['alertas_qa'] if a['tipo'] == 'atencao']
        
        total_criticos = len(alertas_criticos_dev) + len(alertas_criticos_qa)
        total_atencao = len(alertas_atencao_dev) + len(alertas_atencao_qa)
        total_recomendacoes = len(concentracao['recomendacoes'])
        
        # Cards de resumo
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            cor = 'red' if total_criticos > 0 else 'green'
            criar_card_metrica(str(total_criticos), "Alertas Críticos", cor, "≥80% concentração")
        with col2:
            cor = 'yellow' if total_atencao > 0 else 'green'
            criar_card_metrica(str(total_atencao), "Pontos de Atenção", cor, "60-79% concentração")
        with col3:
            criar_card_metrica(str(total_recomendacoes), "Recomendações", "blue", "Sugestões de rodízio")
        with col4:
            # Calcula score geral de distribuição
            total_indices = len(concentracao['indices'].get('dev_produto', {})) + len(concentracao['indices'].get('qa_produto', {}))
            indices_saudaveis = sum(1 for d in concentracao['indices'].get('dev_produto', {}).values() if d['concentracao_pct'] < 60)
            indices_saudaveis += sum(1 for d in concentracao['indices'].get('qa_produto', {}).values() if d['concentracao_pct'] < 60)
            score_distribuicao = (indices_saudaveis / total_indices * 100) if total_indices > 0 else 100
            cor = 'green' if score_distribuicao >= 70 else 'yellow' if score_distribuicao >= 40 else 'red'
            criar_card_metrica(f"{score_distribuicao:.0f}%", "Score Distribuição", cor, "Áreas bem distribuídas")
        
        # Status geral
        if total_criticos == 0 and total_atencao == 0:
            st.success("✅ **Excelente!** Conhecimento bem distribuído no time. Nenhuma concentração crítica detectada.")
        elif total_criticos > 0:
            st.error(f"🚨 **Atenção necessária:** {total_criticos} área(s) com concentração crítica de conhecimento.")
        
        st.markdown("---")
        
        # ===== FILTROS =====
        col_filtro1, col_filtro2, col_filtro3 = st.columns([2, 3, 2])
        
        # Lista de pessoas únicas
        devs_lista = sorted(list(set([a['pessoa'] for a in concentracao['alertas_dev']])))
        qas_lista = sorted(list(set([a['pessoa'] for a in concentracao['alertas_qa']])))
        todas_pessoas = sorted(list(set(devs_lista + qas_lista)))
        
        with col_filtro1:
            filtro_tipo = st.selectbox(
                "📋 Filtrar por tipo:",
                ["Todos", "Apenas DEV", "Apenas QA"],
                key="filtro_tipo_concentracao"
            )
        
        with col_filtro2:
            filtro_pessoas = st.multiselect(
                "👤 Filtrar por pessoa(s):",
                options=todas_pessoas,
                default=[],
                placeholder="Todas as pessoas",
                key="filtro_pessoa_concentracao"
            )
        
        with col_filtro3:
            filtro_contexto = st.selectbox(
                "🏷️ Filtrar por contexto:",
                ["Todos", "Apenas Produto", "Apenas Cliente"],
                key="filtro_contexto_concentracao"
            )
        
        # Aplica filtros
        def filtrar_alertas(alertas, tipo_role, filtro_tipo, filtro_pessoas, filtro_contexto):
            resultado = alertas.copy()
            
            # Filtro por tipo (DEV/QA)
            if filtro_tipo == "Apenas DEV" and tipo_role != "dev":
                return []
            if filtro_tipo == "Apenas QA" and tipo_role != "qa":
                return []
            
            # Filtro por pessoa(s) - se lista não vazia, filtra
            if filtro_pessoas:
                resultado = [a for a in resultado if a['pessoa'] in filtro_pessoas]
            
            # Filtro por contexto
            if filtro_contexto == "Apenas Produto":
                resultado = [a for a in resultado if a['contexto'] == 'produto']
            elif filtro_contexto == "Apenas Cliente":
                resultado = [a for a in resultado if a['contexto'] == 'cliente']
            
            return resultado
        
        alertas_criticos_dev_filtrados = filtrar_alertas(alertas_criticos_dev, "dev", filtro_tipo, filtro_pessoas, filtro_contexto)
        alertas_criticos_qa_filtrados = filtrar_alertas(alertas_criticos_qa, "qa", filtro_tipo, filtro_pessoas, filtro_contexto)
        alertas_atencao_dev_filtrados = filtrar_alertas(alertas_atencao_dev, "dev", filtro_tipo, filtro_pessoas, filtro_contexto)
        alertas_atencao_qa_filtrados = filtrar_alertas(alertas_atencao_qa, "qa", filtro_tipo, filtro_pessoas, filtro_contexto)
        
        # ===== FILTRA MATRIZES E ÍNDICES BASEADO NOS FILTROS =====
        def filtrar_matriz(matriz, pessoas_filtro):
            """Filtra matriz para mostrar apenas pessoas selecionadas."""
            if matriz.empty or not pessoas_filtro:
                return matriz
            # Filtra apenas linhas (pessoas) que estão na lista
            pessoas_na_matriz = [p for p in pessoas_filtro if p in matriz.index]
            if not pessoas_na_matriz:
                return matriz  # Se nenhuma pessoa do filtro está na matriz, mostra tudo
            return matriz.loc[pessoas_na_matriz]
        
        def filtrar_dataframe_pessoa(df_dados, coluna_pessoa, pessoas_filtro):
            """Filtra dataframe por pessoa."""
            if df_dados.empty or not pessoas_filtro:
                return df_dados
            return df_dados[df_dados[coluna_pessoa].isin(pessoas_filtro)]
        
        def filtrar_indices(indices_dict, pessoas_filtro):
            """Filtra índices para mostrar apenas onde a pessoa é o top."""
            if not pessoas_filtro:
                return indices_dict
            return {k: v for k, v in indices_dict.items() if v['top_pessoa'] in pessoas_filtro}
        
        # Aplica filtros às matrizes
        matriz_dev_produto_filtrada = filtrar_matriz(concentracao['matriz_dev_produto'], filtro_pessoas if filtro_tipo != "Apenas QA" else [])
        matriz_dev_cliente_filtrada = filtrar_matriz(concentracao['matriz_dev_cliente'], filtro_pessoas if filtro_tipo != "Apenas QA" else [])
        matriz_qa_produto_filtrada = filtrar_matriz(concentracao['matriz_qa_produto'], filtro_pessoas if filtro_tipo != "Apenas DEV" else [])
        matriz_qa_cliente_filtrada = filtrar_matriz(concentracao['matriz_qa_cliente'], filtro_pessoas if filtro_tipo != "Apenas DEV" else [])
        
        # Aplica filtros aos dataframes detalhados
        dev_produto_filtrado = filtrar_dataframe_pessoa(concentracao['dev_produto'], 'DEV', filtro_pessoas if filtro_tipo != "Apenas QA" else [])
        dev_cliente_filtrado = filtrar_dataframe_pessoa(concentracao['dev_cliente'], 'DEV', filtro_pessoas if filtro_tipo != "Apenas QA" else [])
        qa_produto_filtrado = filtrar_dataframe_pessoa(concentracao['qa_produto'], 'QA', filtro_pessoas if filtro_tipo != "Apenas DEV" else [])
        qa_cliente_filtrado = filtrar_dataframe_pessoa(concentracao['qa_cliente'], 'QA', filtro_pessoas if filtro_tipo != "Apenas DEV" else [])
        
        # Aplica filtros aos índices
        indices_dev_produto_filtrado = filtrar_indices(concentracao['indices'].get('dev_produto', {}), filtro_pessoas if filtro_tipo != "Apenas QA" else [])
        indices_dev_cliente_filtrado = filtrar_indices(concentracao['indices'].get('dev_cliente', {}), filtro_pessoas if filtro_tipo != "Apenas QA" else [])
        indices_qa_produto_filtrado = filtrar_indices(concentracao['indices'].get('qa_produto', {}), filtro_pessoas if filtro_tipo != "Apenas DEV" else [])
        indices_qa_cliente_filtrado = filtrar_indices(concentracao['indices'].get('qa_cliente', {}), filtro_pessoas if filtro_tipo != "Apenas DEV" else [])
        
        # ===== ALERTAS AGRUPADOS POR PESSOA (EM EXPANDERS) =====
        todos_alertas_criticos = alertas_criticos_dev_filtrados + alertas_criticos_qa_filtrados
        todos_alertas_atencao = alertas_atencao_dev_filtrados + alertas_atencao_qa_filtrados
        
        # Agrupa por pessoa
        def agrupar_por_pessoa(alertas):
            agrupado = {}
            for a in alertas:
                pessoa = a['pessoa']
                if pessoa not in agrupado:
                    agrupado[pessoa] = []
                agrupado[pessoa].append(a)
            return agrupado
        
        criticos_por_pessoa = agrupar_por_pessoa(todos_alertas_criticos)
        atencao_por_pessoa = agrupar_por_pessoa(todos_alertas_atencao)
        
        # Exibe alertas críticos
        if todos_alertas_criticos:
            with st.expander(f"🚨 Alertas Críticos ({len(todos_alertas_criticos)})", expanded=False):
                for pessoa, alertas in sorted(criticos_por_pessoa.items()):
                    st.markdown(f"**👤 {pessoa}** ({len(alertas)} alerta(s)):")
                    for alerta in alertas:
                        icone = "📦" if alerta['contexto'] == 'produto' else "🏢"
                        st.markdown(f"""
                        <div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 8px 12px; margin: 4px 0; border-radius: 4px;">
                            {icone} <b>{alerta['nome']}</b>: {alerta['pct']}% de concentração
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown("---")
        
        # Exibe alertas de atenção
        if todos_alertas_atencao:
            with st.expander(f"⚠️ Pontos de Atenção ({len(todos_alertas_atencao)})", expanded=False):
                for pessoa, alertas in sorted(atencao_por_pessoa.items()):
                    st.markdown(f"**👤 {pessoa}** ({len(alertas)} ponto(s)):")
                    for alerta in alertas:
                        icone = "📦" if alerta['contexto'] == 'produto' else "🏢"
                        st.markdown(f"""
                        <div style="background: #fffbeb; border-left: 4px solid #f59e0b; padding: 8px 12px; margin: 4px 0; border-radius: 4px;">
                            {icone} <b>{alerta['nome']}</b>: {alerta['pct']}% de concentração
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown("---")
        
        # ===== RECOMENDAÇÕES DE RODÍZIO (EM EXPANDER) =====
        if concentracao['recomendacoes']:
            with st.expander(f"💡 Recomendações de Rodízio ({len(concentracao['recomendacoes'])})", expanded=False):
                for rec in concentracao['recomendacoes']:
                    if rec['tipo'] == 'geral':
                        st.warning(rec['msg'])
                    else:
                        st.markdown(f"""
                        <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 10px 14px; margin: 6px 0; border-radius: 4px;">
                            {rec['msg']}
                        </div>
                        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ===== TABS PARA MATRIZES =====
        tab_dev, tab_qa = st.tabs(["👨‍💻 Concentração DEV", "🔬 Concentração QA"])
        
        with tab_dev:
            # Verifica se filtro de tipo permite mostrar DEV
            if filtro_tipo == "Apenas QA":
                st.info("🔍 Filtro 'Apenas QA' selecionado. Mude para 'Todos' ou 'Apenas DEV' para ver dados de desenvolvedores.")
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📦 DEV x Produto")
                    if not matriz_dev_produto_filtrada.empty:
                        fig = criar_grafico_concentracao(
                            matriz_dev_produto_filtrada, 
                            "Cards por DEV em cada Produto",
                            "dev"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Tabela resumo
                        with st.expander("📊 Ver dados detalhados", expanded=False):
                            st.dataframe(dev_produto_filtrado, hide_index=True, use_container_width=True)
                    else:
                        st.info("Sem dados de DEV x Produto para os filtros selecionados")
                
                with col2:
                    st.markdown("#### 🏢 DEV x Cliente")
                    if not matriz_dev_cliente_filtrada.empty:
                        fig = criar_grafico_concentracao(
                            matriz_dev_cliente_filtrada, 
                            "Cards por DEV em cada Cliente",
                            "dev"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        with st.expander("📊 Ver dados detalhados", expanded=False):
                            st.dataframe(dev_cliente_filtrado, hide_index=True, use_container_width=True)
                    else:
                        st.info("Sem dados de DEV x Cliente para os filtros selecionados")
                
                # Índices de concentração DEV (em expander)
                with st.expander("📈 Índices de Concentração (DEV)", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Por Produto:**")
                        if indices_dev_produto_filtrado:
                            for produto, dados in indices_dev_produto_filtrado.items():
                                cor = '🔴' if dados['concentracao_pct'] >= 80 else '🟡' if dados['concentracao_pct'] >= 60 else '🟢'
                                st.markdown(f"{cor} **{produto}**: {dados['top_pessoa']} ({dados['top_cards']}/{dados['total_cards']} = {dados['concentracao_pct']}%)")
                        else:
                            st.info("Nenhum índice para os filtros selecionados")
                    
                    with col2:
                        st.markdown("**Por Cliente:**")
                        if indices_dev_cliente_filtrado:
                            for cliente, dados in indices_dev_cliente_filtrado.items():
                                cor = '🔴' if dados['concentracao_pct'] >= 80 else '🟡' if dados['concentracao_pct'] >= 60 else '🟢'
                                st.markdown(f"{cor} **{cliente}**: {dados['top_pessoa']} ({dados['top_cards']}/{dados['total_cards']} = {dados['concentracao_pct']}%)")
                        else:
                            st.info("Nenhum índice para os filtros selecionados")
        
        with tab_qa:
            # Verifica se filtro de tipo permite mostrar QA
            if filtro_tipo == "Apenas DEV":
                st.info("🔍 Filtro 'Apenas DEV' selecionado. Mude para 'Todos' ou 'Apenas QA' para ver dados de QAs.")
            else:
                # Info sobre QAs principais
                if concentracao['qas_principais']:
                    st.info(f"📋 **QAs considerados:** {', '.join(concentracao['qas_principais'])} (baseado no volume de validações)")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📦 QA x Produto")
                    if not matriz_qa_produto_filtrada.empty:
                        fig = criar_grafico_concentracao(
                            matriz_qa_produto_filtrada, 
                            "Validações por QA em cada Produto",
                            "qa"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        with st.expander("📊 Ver dados detalhados", expanded=False):
                            st.dataframe(qa_produto_filtrado, hide_index=True, use_container_width=True)
                    else:
                        st.info("Sem dados de QA x Produto para os filtros selecionados")
                
                with col2:
                    st.markdown("#### 🏢 QA x Cliente")
                    if not matriz_qa_cliente_filtrada.empty:
                        fig = criar_grafico_concentracao(
                            matriz_qa_cliente_filtrada, 
                            "Validações por QA em cada Cliente",
                            "qa"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        with st.expander("📊 Ver dados detalhados", expanded=False):
                            st.dataframe(qa_cliente_filtrado, hide_index=True, use_container_width=True)
                    else:
                        st.info("Sem dados de QA x Cliente para os filtros selecionados")
                
                # Índices de concentração QA (em expander)
                with st.expander("📈 Índices de Concentração (QA)", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Por Produto:**")
                        if indices_qa_produto_filtrado:
                            for produto, dados in indices_qa_produto_filtrado.items():
                                cor = '🔴' if dados['concentracao_pct'] >= 80 else '🟡' if dados['concentracao_pct'] >= 60 else '🟢'
                                st.markdown(f"{cor} **{produto}**: {dados['top_pessoa']} ({dados['top_cards']}/{dados['total_cards']} = {dados['concentracao_pct']}%)")
                        else:
                            st.info("Nenhum índice para os filtros selecionados")
                    
                    with col2:
                        st.markdown("**Por Cliente:**")
                        if indices_qa_cliente_filtrado:
                            for cliente, dados in indices_qa_cliente_filtrado.items():
                                cor = '🔴' if dados['concentracao_pct'] >= 80 else '🟡' if dados['concentracao_pct'] >= 60 else '🟢'
                                st.markdown(f"{cor} **{cliente}**: {dados['top_pessoa']} ({dados['top_cards']}/{dados['total_cards']} = {dados['concentracao_pct']}%)")
                        else:
                            st.info("Nenhum índice para os filtros selecionados")
        
        # ===== LEGENDA (COLAPSADA) =====
        with st.expander("📖 Legenda e Conceitos", expanded=False):
            st.markdown("""
            **Níveis de Concentração:**
            - 🔴 **Crítico (≥80%)**: Conhecimento muito centralizado - risco alto de Bus Factor
            - 🟡 **Atenção (60-79%)**: Concentração moderada - planejar rodízio
            - 🟢 **Saudável (<60%)**: Conhecimento bem distribuído
            
            **💡 O que é Bus Factor?** 
            É o número mínimo de pessoas que precisam "sair" para o projeto/área ficar parado. 
            Quanto mais distribuído o conhecimento, maior o Bus Factor e menor o risco.
            
            **Como usar estas informações:**
            1. Identifique áreas com concentração crítica (🔴)
            2. Planeje rodízios nas próximas sprints
            3. Considere pair programming para transferência de conhecimento
            4. Documente processos específicos de áreas concentradas
            """)
    
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
        | **Mantido por** |9Vinícios Ferreira |
        | **Versão** | v8.78 |
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
        | **🎯 Suporte** | Visão pessoal: onde estão meus cards? Cards aguardando ação | Suporte, Implantação |
        | **🏢 Clientes** | Análise por cliente, desenvolvimento pago, bugs por cliente | Comercial, Liderança |
        | **📋 Governança** | Qualidade dos dados, campos obrigatórios, compliance | PO, Liderança |
        | **📦 Produto** | Métricas por produto, Health Score, tendências | PO, Stakeholders |
        | **📋 Backlog** | Saúde do backlog, aging, gargalos, cards problemáticos, recomendações | PO, Liderança |
        | **📈 Histórico** | Evolução de métricas entre releases, tendências | Liderança |
        | **🎯 Liderança** | Decisão Go/No-Go, riscos, simulações | Gerentes, Diretores |
        | **ℹ️ Sobre** | Esta documentação | Todos |
        
        ---
        
        ### � Meu Dashboard (NOVO!)
        
        Acesse pelo botão **"🎨 Meu Dashboard"** na sidebar!
        
        **Uma tela totalmente separada** para construir seu dashboard personalizado:
        
        **Como funciona:**
        1. ➕ **Adicionar Widget**: Escolha o tipo de widget no topo da tela
        2. 🎛️ **Configurar Filtros**: Selecione pessoa, status, período conforme necessário
        3. 📊 **Visualizar**: O widget aparece na área abaixo
        4. ⬆️⬇️ **Reordenar**: Mova widgets para cima ou para baixo
        5. 🗑️ **Remover**: Exclua widgets que não precisa mais
        
        **Tipos de Widgets:**
        - 📋 **Total de Cards** - Contador de cards
        - ⭐ **Story Points** - Total de SP
        - 🐛 **Total de Bugs** - Contador de bugs
        - 🎯 **Fator K** - Métrica de qualidade
        - ✅ **FPY** - First Pass Yield
        - 🏁 **Taxa de Conclusão** - % concluídos
        - 📊 **Gráfico por Status** - Distribuição visual
        - 📦 **Gráfico por Produto** - Distribuição visual
        - 👤 **Gráfico por Responsável** - Cards por pessoa
        - 🐛 **Bugs por Dev** - Análise de bugs
        - 🏆 **Ranking Devs** - Tabela de ranking
        - 🕐 **Cards Recentes** - Últimas atualizações
        - ⏰ **Aging** - Cards parados
        - 📋 **Lista de Cards** - Cards de uma pessoa
        - 🐛 **Lista de Bugs** - Bugs filtrados
        
        **Templates prontos:**
        - 📊 **Visão Executiva**: KPIs principais + gráfico de status
        - 👨‍💻 **Foco DEV**: Ranking + bugs por dev + FPY
        - 🔬 **Foco QA**: Bugs + taxa conclusão + aging
        
        **💾 Persistência**: Seu dashboard fica salvo mesmo depois de fechar o navegador!
        
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
    
    # ========== CSS GLOBAL PARA ESCONDER WARNINGS ==========
    # Injeta CSS imediatamente para esconder qualquer warning do CookieManager
    st.markdown("""
    <style>
    /* Esconde warnings/exceptions do Streamlit (CookieManager) */
    .stException, [data-testid="stException"], 
    .stWarning, [data-testid="stWarning"],
    div[data-testid="stNotification"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        overflow: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ========== VERIFICAR LOGIN (via session_state ou cookie) ==========
    if not verificar_login():
        # Mostra tela de login
        mostrar_tela_login()
        return
    
    # ========== USUÁRIO LOGADO - DASHBOARD ==========
    aplicar_estilos()
    
    # CSS global para popup de cards (permite escolher NinaDash ou Jira)
    st.markdown(CARD_POPUP_CSS, unsafe_allow_html=True)
    
    # Header principal com logo Nina
    mostrar_header_nina()
    
    # ========== GERENCIAMENTO DE QUERY PARAMS ==========
    # Captura query params para compartilhamento de busca
    query_params = st.query_params
    card_compartilhado = query_params.get("card", None)
    projeto_param = query_params.get("projeto", None)
    qa_compartilhado = query_params.get("qa", None)
    dev_compartilhado = query_params.get("dev", None)
    pessoa_compartilhada = query_params.get("pessoa", None)
    cliente_compartilhado = query_params.get("cliente", None)
    
    # Verifica se é um link compartilhado válido
    eh_link_compartilhado = any([card_compartilhado, qa_compartilhado, dev_compartilhado, pessoa_compartilhada, cliente_compartilhado])
    
    # Se NÃO é link compartilhado mas tem query_params de aba, limpa tudo
    # Isso evita "poluição" de URL quando o usuário navega normalmente
    if not eh_link_compartilhado and query_params.get("aba", None):
        # Limpa todos os query params para URL limpa
        st.query_params.clear()
    
    # Inicializa session_state para controle de busca
    if 'busca_ativa' not in st.session_state:
        st.session_state.busca_ativa = False
    if 'card_buscado' not in st.session_state:
        st.session_state.card_buscado = ""
    if 'projeto_buscado' not in st.session_state:
        st.session_state.projeto_buscado = "SD"
    
    # Inicializa modo Meu Dashboard
    if 'modo_consulta_personalizada' not in st.session_state:
        st.session_state.modo_consulta_personalizada = False
    
    # Verifica se veio via query param para Meu Dashboard
    if query_params.get("tela", None) == "meu_dashboard":
        st.session_state.modo_consulta_personalizada = True
    
    # ===============================================================
    # MODO MEU DASHBOARD - TELA SEPARADA COM SIDEBAR LIMPA
    # ===============================================================
    if st.session_state.modo_consulta_personalizada:
        # SIDEBAR MINIMALISTA - apenas logo, usuário e voltar
        with st.sidebar:
            # Logo
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
                    Meu Dashboard
                </p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Usuário logado
            user_nome = st.session_state.get("user_nome", "Usuário")
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #AF0C37 0%, #8F0A2E 100%); 
                        padding: 10px; border-radius: 8px; margin: 10px 0; text-align: center;">
                <p style="margin: 0; color: white; font-size: 13px;">👤 {user_nome}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Botão voltar (grande e em destaque)
            if st.button("⬅️ Voltar ao Dashboard", type="primary", use_container_width=True, key="btn_voltar_meu_dashboard"):
                st.session_state.modo_consulta_personalizada = False
                st.query_params.clear()
                st.rerun()
            
            st.markdown("---")
            
            # Rodapé minimalista
            st.markdown("""
            <div style="text-align: center; padding: 10px 0; color: #999; font-size: 0.75em;">
                📌 N9 • Qualidade e Decisão
            </div>
            """, unsafe_allow_html=True)
        
        # CARREGA DADOS DE TODOS OS PROJETOS
        with st.spinner("🔄 Carregando dados de todos os projetos..."):
            todos_dfs = []
            
            for proj in ["SD", "QA", "PB"]:
                try:
                    jql_proj = f'project = {proj} ORDER BY created DESC'
                    issues_proj, _ = buscar_dados_jira_cached(proj, jql_proj)
                    if issues_proj:
                        df_proj = processar_issues(issues_proj)
                        df_proj['projeto'] = proj
                        todos_dfs.append(df_proj)
                except:
                    pass
            
            if todos_dfs:
                df_todos = pd.concat(todos_dfs, ignore_index=True)
            else:
                st.error("❌ Não foi possível carregar dados")
                st.stop()
        
        # RENDERIZA A TELA MEU DASHBOARD
        tela_consulta_personalizada(df_todos)
        return  # Sai da função main() - não renderiza mais nada
    
    # ===============================================================
    # MODO NORMAL - SIDEBAR COMPLETA COM FILTROS
    # ===============================================================
    
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
        projetos_lista = ["SD", "QA", "PB", "VALPROD"]
        projeto_busca_index = 0
        if st.session_state.busca_ativa and st.session_state.projeto_buscado in projetos_lista:
            projeto_busca_index = projetos_lista.index(st.session_state.projeto_buscado)
        
        # Extrai número inicial se estiver buscando
        numero_inicial = ""
        if st.session_state.busca_ativa and st.session_state.card_buscado:
            numero_inicial = st.session_state.card_buscado.upper()
            for prefix in ["SD-", "QA-", "PB-", "VALPROD-"]:
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
                    help="SD, QA, PB ou VALPROD"
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
            
            # Índice padrão do filtro baseado no projeto E na aba
            # PB, VALPROD e aba Suporte usam "Todo o período" (index=0)
            # SD/QA usam "Sprint Ativa" (index=1)
            aba_suporte = st.query_params.get("aba", None) == "suporte"
            indice_filtro_padrao = 0 if projeto in ["PB", "VALPROD"] or aba_suporte else 1
            
            filtro_sprint = st.selectbox(
                "🗓️ Período",
                ["Todo o período", "Sprint Ativa", "Últimos 30 dias", "Últimos 90 dias"],
                index=indice_filtro_padrao
            )
            
            # Nota: Filtro de Produto será adicionado após carregar os dados
            # Ferramentas Avançadas também será adicionado após Produto
            
        else:
            # Quando pesquisando, usa o projeto da busca
            projeto = st.session_state.projeto_buscado
            filtro_sprint = "Sprint Ativa"  # Não usado na busca específica
    
    # ===== MODO BUSCA DE CARD ESPECÍFICO =====
    if st.session_state.busca_ativa and st.session_state.card_buscado:
        busca_card = st.session_state.card_buscado
        projeto_busca = st.session_state.projeto_buscado
        
        # Atualiza a URL com os parâmetros de compartilhamento
        st.query_params["card"] = busca_card
        st.query_params["projeto"] = projeto_busca
        
        # Busca o card específico (sem filtros de período)
        with st.spinner(f"🔍 Buscando {busca_card}..."):
            issue, links, comentarios, historico_transicoes = buscar_card_especifico(busca_card)
        
        if issue:
            # Processa o card encontrado
            card_data = processar_issue_unica(issue)
            exibir_card_detalhado_v2(card_data, links, comentarios, historico_transicoes, projeto_busca)
        else:
            st.warning(f"⚠️ Card **{busca_card}** não encontrado.")
            st.info("💡 Verifique se o ID está correto. O card será buscado em todo o histórico do projeto.")
    
    # ===== MODO DASHBOARD NORMAL =====
    else:
        # JQL
        if filtro_sprint == "Todo o período":
            jql = f'project = {projeto} ORDER BY created DESC'
        elif filtro_sprint == "Sprint Ativa":
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
        
        # Adiciona coluna de projeto ao df principal
        df['projeto'] = projeto
        
        # ===== BUSCA TODOS OS PROJETOS PARA ABA SUPORTE/IMPLANTAÇÃO =====
        # Essa aba precisa de dados de todos os projetos para mostrar "onde estão meus cards"
        todos_dfs = [df]  # Começa com o df do projeto selecionado
        
        # Busca SD (se não for o projeto atual)
        if projeto != "SD":
            try:
                if filtro_sprint == "Todo o período":
                    jql_sd = 'project = SD ORDER BY created DESC'
                elif filtro_sprint == "Sprint Ativa":
                    jql_sd = 'project = SD AND sprint in openSprints() ORDER BY created DESC'
                elif filtro_sprint == "Últimos 30 dias":
                    jql_sd = 'project = SD AND created >= -30d ORDER BY created DESC'
                else:
                    jql_sd = 'project = SD AND created >= -90d ORDER BY created DESC'
                
                issues_sd, _ = buscar_dados_jira_cached("SD", jql_sd)
                if issues_sd:
                    df_sd = processar_issues(issues_sd)
                    df_sd['projeto'] = 'SD'
                    todos_dfs.append(df_sd)
            except:
                pass
        
        # Busca QA (se não for o projeto atual)
        if projeto != "QA":
            try:
                if filtro_sprint == "Todo o período":
                    jql_qa = 'project = QA ORDER BY created DESC'
                elif filtro_sprint == "Sprint Ativa":
                    jql_qa = 'project = QA AND sprint in openSprints() ORDER BY created DESC'
                elif filtro_sprint == "Últimos 30 dias":
                    jql_qa = 'project = QA AND created >= -30d ORDER BY created DESC'
                else:
                    jql_qa = 'project = QA AND created >= -90d ORDER BY created DESC'
                
                issues_qa, _ = buscar_dados_jira_cached("QA", jql_qa)
                if issues_qa:
                    df_qa = processar_issues(issues_qa)
                    df_qa['projeto'] = 'QA'
                    todos_dfs.append(df_qa)
            except:
                pass
        
        # Busca PB (sempre todo período, não tem sprint)
        if projeto != "PB":
            try:
                jql_pb = 'project = PB ORDER BY created DESC'
                issues_pb, _ = buscar_dados_jira_cached("PB", jql_pb)
                if issues_pb:
                    df_pb = processar_issues(issues_pb)
                    df_pb['projeto'] = 'PB'
                    todos_dfs.append(df_pb)
            except:
                pass
        
        # Busca VALPROD (sempre todo período)
        if projeto != "VALPROD":
            try:
                jql_valprod = 'project = VALPROD ORDER BY created DESC'
                issues_valprod, _ = buscar_dados_jira_cached("VALPROD", jql_valprod)
                if issues_valprod:
                    df_valprod = processar_issues(issues_valprod)
                    df_valprod['projeto'] = 'VALPROD'
                    todos_dfs.append(df_valprod)
            except:
                pass
        
        # Combina todos os DataFrames
        df_todos = pd.concat(todos_dfs, ignore_index=True) if len(todos_dfs) > 0 else df.copy()
        
        # Garante que df_todos tenha a coluna 'projeto'
        if 'projeto' not in df_todos.columns:
            df_todos['projeto'] = projeto
        
        # Filtro por produto (dentro da sidebar, junto aos outros filtros)
        with st.sidebar:
            # Adiciona Produto aos filtros principais
            produtos_disponiveis = ['Todos'] + sorted(df['produto'].unique().tolist())
            filtro_produto = st.selectbox("📦 Produto", produtos_disponiveis, index=0, key="filtro_produto_main")
            
            if filtro_produto != 'Todos':
                df = df[df['produto'] == filtro_produto]
            
            # ===== SEÇÃO DE FERRAMENTAS AVANÇADAS (após todos os filtros) =====
            st.markdown("---")
            st.markdown("##### 🔍 Ferramentas Avançadas")
            
            if st.button("🎨 Meu Dashboard", use_container_width=True, key="btn_meu_dashboard", 
                        help="Monte seu dashboard personalizado com widgets"):
                st.session_state.modo_consulta_personalizada = True
                st.query_params["tela"] = "meu_dashboard"
                st.rerun()
            
            # ===== RODAPÉ DA SIDEBAR (sempre no final) =====
            st.markdown("---")
            st.markdown("""
            <div style="text-align: center; padding: 5px 0;">
                <p style="color: #AF0C37; font-weight: bold; margin: 0; font-size: 0.85em;">
                    📌 N9 • Qualidade e Decisão de Software
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Changelog em expander
            with st.expander("📋 Histórico de Versões", expanded=False):
                st.markdown("""
                <div style="margin-bottom: 10px; display: flex; flex-wrap: wrap; gap: 5px;">
                    <span style="background: #ef4444; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; white-space: nowrap;">🔥 HOTFIX</span>
                    <span style="background: #22c55e; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; white-space: nowrap;">✨ MELHORIA</span>
                    <span style="background: #f97316; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; white-space: nowrap;">🐛 BUG&nbsp;FIX</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                **v8.81** *(20/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎨 **Meu Dashboard**: Tela totalmente nova para construir dashboards personalizados
                - ➕ **Adicionar Widgets**: Construtor no topo para adicionar métricas
                - ⬆️⬇️ **Reordenar**: Mova widgets para cima ou para baixo
                - 🗑️ **Remover**: Exclua widgets que não precisa mais
                - 📊 **Templates**: Visão Executiva, Foco DEV, Foco QA
                - 💾 **Persistência**: Dashboard salvo em cookie
                - 🧹 **Sidebar Limpa**: Apenas logo e botão voltar na tela do dashboard
                
                **v8.80** *(20/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                
                **v8.79** *(20/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎯 **Consulta Personalizada**: Tela separada acessível pela sidebar
                - 🔍 **Filtros Avançados**: Pessoa, papel (DEV/QA/Relator), status, período
                - 📅 **Períodos Flexíveis**: Sprint atual, últimas semanas, mês, ou datas customizadas
                - 📊 **Tipos de Consulta**: Cards de pessoa, métricas, comparativos, bugs
                - 💾 **Salvar Consultas**: Guarde suas consultas favoritas para reusar
                - ⬅️ **Botão na Sidebar**: Acesso rápido abaixo dos filtros
                
                **v8.78** *(20/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎨 **Nova Aba: Meu Dashboard**: Crie dashboards personalizados!
                - 📊 **Catálogo de Métricas**: 30+ métricas disponíveis para escolher
                - 💾 **Persistência**: Dashboards salvos na sessão
                - 🎯 **Templates Rápidos**: Visão Executiva, Foco QA, Foco Dev
                - 📈 **Tipos de Visualização**: KPIs, gráficos, tabelas, heatmaps
                - 🔧 **Gerenciamento**: Criar, visualizar e excluir dashboards
                
                **v8.77** *(17/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🏢 **Aba Clientes Reposicionada**: Agora entre Suporte e Governança
                - 💰 **Desenvolvimento Pago**: Detecta cards pagos via label
                - 📊 **KPIs de Clientes**: Cards pagos, % conclusão, SP total
                - 👀 **Visão Geral do Time**: Padrão igual às abas QA/Dev/Suporte
                - 🎨 **Cards com Tag Pago**: Indicador visual 💰 PAGO nos cards
                - 📈 **Top Clientes Dev Pago**: Ranking de clientes com mais desenvolvimento pago
                
                **v8.76** *(17/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🏢 **Nova Aba Clientes**: Análise completa de clientes em aba dedicada
                - 📊 **Dados de Todos Projetos**: Aba Clientes ignora filtro de projeto (mostra tudo)
                - 🔗 **Link Compartilhável**: Copiar link direto para cliente específico
                - 💰 **Categorização**: Indicadores de desenvolvimento pago vs manutenção
                - 📅 **Timeline**: Gráfico de evolução de cards por mês para cada cliente
                - 🐛 **Top Bugs**: Ranking de clientes com mais bugs
                - 🔐 **Login via Cookie**: Método mais robusto usando CookieManager
                
                **v8.75** *(17/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🏢 **Análise por Cliente**: Nova seção em Visão Geral para pesquisar clientes
                - 📊 **Top Clientes**: Ranking dos clientes com mais cards
                - 👥 **Responsáveis**: Ver quem mais trata cada cliente (Relator, Dev, QA)
                - 📄 **Últimos Cards**: Histórico recente por cliente
                - 🔐 **Fix Login**: Corrigido localStorage usando parent.window
                
                **v8.74** *(17/04/2026)* <span style="background: #ef4444; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🔥</span>
                - 🔐 **Login via localStorage**: Substitui cookies por localStorage (mais confiável)
                - ⚡ **Auto-login**: JavaScript detecta email salvo e faz login automático
                - 🔄 **Persiste entre Refreshes**: Atualizar página mantém o login
                
                **v8.73** *(17/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔗 **URL Limpa**: Remove params da URL ao navegar (não polui mais)
                - 🚫 **Selectbox sem Params**: QA/Dev/Suporte não alteram mais a URL
                
                **v8.72** *(17/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔗 **URL Centralizada**: Constante `NINADASH_URL` para facilitar alterações
                - 🐛 **Fix TypeError**: Corrigido erro de comparação de datas com timezone
                - 🔄 **Cookies**: Novo domínio requer login na primeira vez (normal)
                
                **v8.71** *(17/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎨 **Novo Nome**: Dashboard de Qualidade e Decisão de Software
                - 🔗 **Nova URL**: ninadash.streamlit.app (mais curta e fácil)
                - 📊 **Barra de Progresso**: Visual da sprint com % concluído
                - 📈 **KPIs Simplificados**: 5 métricas essenciais (Cards, SP, Concluído, Bugs, Dias)
                - 🔬 **Métricas Técnicas**: FPY/DDP/Lead Time/Health/Fator K em expander separado
                - 📋 **Cards por Status**: Layout 2 colunas (mais espaço para leitura)
                - 🔄 **Botão Atualizar**: Integrado com indicador de última atualização
                - 📝 **Subtítulo Atualizado**: Foco em todo o time, não só QA
                
                **v8.70** *(17/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📦 **Expanders Padronizados**: Todas as seções agora podem ser ocultadas
                - 👤 **Fix Responsável**: Prioriza campo `responsavel` corretamente (não QA)
                - 📝 **Título Completo**: Aumentado de 50 para 80 caracteres
                - ✅ **Checkbox Ver Todos**: Voltou! Remove limite de 20 cards
                - 🎨 **Fonte Padronizada**: Cards com fonte consistente e legível
                - 📊 **Gráficos com Explicação**: Captions descritivos nos gráficos
                - 🔧 **Cards Aguardando Aberto**: Agora inicia expandido por padrão
                
                **v8.69** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📋 **Botão Copiar Link Padronizado**: Mesmo estilo do QA/Dev (height=45px)
                - 📜 **Cards Aguardando Ação em Expander**: Agora pode ocultar/expandir
                - 🔄 **Scroll Interno Funcional**: Usa components.html com scrolling=True
                - 🚫 **Removido Checkbox Ver Todos**: Substituído por scroll interno
                
                **v8.68** *(16/04/2026)* <span style="background: #ef4444; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🔥</span>
                - 🔧 **Fix Redirecionamento**: Corrigido bug que redirecionava para aba Dev
                - 📌 **Isolamento de Abas**: QA/Dev/Suporte não interferem mais entre si
                - 🔗 **Query Params**: Só atualiza URL quando a própria aba está ativa
                - ✅ Checkbox "Ver todos" não muda mais a aba ativa
                
                **v8.67** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📋 **Botão Copiar Link**: Movido para linha do título (não corta mais)
                - 📝 **Título nos Cards**: Cards Aguardando Ação agora mostram título
                - 📜 **Scroll em Ver Todos**: Scroll automático em listas longas (max 400px)
                - 👤 **Representante Cliente**: Cards onde você é Rep. Cliente ou Responsável
                - 🏷️ **Badge de Papel**: Mostra se você é QA, Rep. Cliente ou Responsável
                
                **v8.66** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📋 **Reordenação Expanders**: Prioriza cards de validação
                - 🔬 "Cards Aguardando Minha Validação" agora é o primeiro
                - ✅ "Cards Concluídos" movido para cima (mais visível)
                - 💬 "Cards Aguardando Resposta" fechado por padrão
                - 📊 "Onde estão meus cards?" fechado por padrão
                - 🔘 **Fix Botão Copiar**: Ajustado padding interno
                
                **v8.65** *(16/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔗 **Fix Copiar Link Suporte**: Botão funciona igual QA/Dev
                - ✅ Feedback visual: muda cor e mostra "Copiado!"
                - 📋 Usa mesmo padrão components.html
                
                **v8.64** *(16/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 👤 **Responsável nos Cards**: Mostra quem precisa agir
                - 📏 **Fix Copiar Link**: Botão alinhado com selectbox
                - 📝 Legenda explicativa em "Cards Aguardando Ação"
                
                **v8.63** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🕐 **Tempo de Atualização**: Mostra "há X min/h/d" nos cards
                - 🔬 **Cards Aguardando Minha Validação**: Nova seção para QA
                - 📏 **Fix Copiar Link**: Alinhado com seletor de pessoa
                - 🔍 **Filtro Aguardando**: Inclui mais variações de status
                - 📊 **QA Cards em Trabalho**: Ordenado por atualização
                
                **v8.62** *(16/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔧 **Fix UI Visão Geral**: Removido card desalinhado
                - 🤖 **Filtro Bots**: Automation for Jira removido do Top 15
                - 🔗 **Popup Links**: Cards Aguardando agora têm popup
                - ☑️ **Ver Todos**: Checkbox para expandir listas de cards
                - 📏 **Fix Botão Copiar**: Aumentado height do botão
                - ✅ **Métrica Concluídos**: Adicionada no resumo por pessoa
                - 📝 **Renomeado**: "Entregues" → "Concluídos"
                - 🔍 **Emoji Fix**: Validação Produção usa 🔍 (pendente)
                
                **v8.61** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 👥 **Ver Todos**: Opção no seletor para visão geral do time
                - 📊 **Gráficos na Visão Geral**: Pizza por projeto, barras por status, tipos
                - 🏆 **Cards Entregues**: Nova seção mostrando entregas por pessoa
                - 📅 **Filtro Padrão**: "Todo o período" para aba Suporte
                - 📋 **Top 15 Pessoas**: Ranking com barras visuais
                - ⏳ **Cards Aguardando**: Visão rápida de pendências por categoria
                
                **v8.60** *(16/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔗 **Fix Copiar Link**: Aba Suporte copia para clipboard
                - 📋 Mesmo padrão das abas QA e Dev
                - ✅ Feedback visual "Copiado!" após clicar
                
                **v8.59** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🏷️ **Cards com Título Completo**: Mostra nome do card
                - 🔖 **Tipo do Card**: Badge colorido (HOTFIX/BUG/TAREFA)
                - 🎨 Layout melhorado nas listagens
                - 📋 Mais informações visíveis em cada card
                
                **v8.58** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎯 **Aba Suporte Refatorada**: Igual QA/Dev
                - 👤 Seletor de pessoa (qualquer um pode ver qualquer pessoa)
                - 🔄 Busca TODOS os projetos (SD, QA, PB, VALPROD)
                - 📊 Gráfico "Onde estão meus cards?" por projeto/status
                - 🔗 Link compartilhável: ?aba=suporte&pessoa=Nome
                
                **v8.57** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎯 Nova ABA: Suporte/Implantação (v1)
                - 🆕 Projeto VALPROD adicionado ao sistema
                - 📊 Status específicos do PB mapeados
                
                **v8.56** *(16/04/2026)* <span style="background: #ef4444; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🔥</span>
                - 📊 **Sem Limite de Cards**: Removido limite de 500 cards
                - 🔄 Busca TODOS os cards do período selecionado
                - 🚀 Histórico completo disponível
                
                **v8.55** *(16/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🎨 **Fix Hover Popup**: CSS puro (funciona em todos locais)
                - 🔴 NinaDash: hover vermelho (#AF0C37) + texto branco
                - 🔵 Jira: hover azul (#3b82f6) + texto branco
                - ⬜ **Tela Loading**: Fundo branco + texto vermelho
                
                **v8.54** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎨 **Popup UX**: Hover vermelho no "Ver no NinaDash"
                - ⏳ **Tela de Loading**: Substituiu flash de login ao abrir
                - 🔄 Loading animado com logo NINA durante verificação
                
                **v8.53** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🚀 **Popup em TODAS aparições de cards**
                - 📊 QA: Em Trabalho, Reprovados, Impedidos, Validados
                - 👨‍💻 DEV: Code Review, Críticos, Resumo Semanal
                - 📋 Listagens, Filas e Cards do desenvolvedor
                - 🔗 18 locais atualizados com navegação NinaDash/Jira
                
                **v8.52** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🆕 **Popup de Navegação**: Clique em qualquer card exibe menu
                - 📊 Opção "Ver no NinaDash" (abre em nova aba)
                - 🔗 Opção "Abrir no Jira" (abre em nova aba)
                - 🎯 Aplicado em Cards Vinculados, Listagens e Resumos
                
                **v8.51** *(16/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔧 **Fix:** Botão "Copiar Link" alinhamento corrigido
                - 📝 **Novo:** Seção Descrição adicionada nos cards SD
                
                **v8.50** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🔄 **Novo:** Cards em Trabalho no resumo QA individual
                - ❌ **Novo:** Cards Reprovados listados no resumo
                - 🚫 **Novo:** Cards Impedidos listados no resumo
                - 📝 Resumo completo copiável (ideal para daily/retro)
                - 📊 Todas as categorias: em trabalho, reprovados, impedidos, validados
                
                **v8.49** *(15/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🚫 Cards Impedidos/Reprovados em QA e DEV
                - 🐛 Fix navegação entre QA/DEV
                
                **v8.48** *(15/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📈 Gráfico "Evolução da Semana"
                - 📝 Títulos completos em toda ferramenta
                
                **v8.47** *(15/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🐛 Dados históricos usam `resolutiondate`
                
                **v8.46** *(15/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📆 Seletor de semanas (2-4 semanas atrás)
                
                **v8.45** *(15/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📅 "Resumo da Semana" QA/DEV
                
                **v8.44** *(15/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🤝 **Novo:** Seção "Interação QA x DEV" na aba QA
                - 💪 **Novo:** Seção "Esforço do Time" na aba Liderança
                - 🤝 **Novo:** "Interação QA x DEV" visão Liderança
                - 🗓️ **UX:** Filtro padrão: PB=Todo período, SD/QA=Sprint Ativa
                - 🌟 Heatmap de interações, ranking de duplas, FPY por parceria
                - 📊 Carga por DEV e QA, throughput, velocidade do time
                
                **v8.43** *(15/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 📏 **Fix:** Cards de métricas agora com altura uniforme
                - 📏 **Fix:** Legenda de tags não quebra mais linha
                
                **v8.42** *(15/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎨 **UX:** Barra de release com cor sólida (remov. gradiente)
                - 📏 **UX:** Cards de métricas com tamanho uniforme
                - 📏 **UX:** Espaçamento corrigido em "Cards por Status"
                - 🏷️ **UX:** Tags visuais no histórico de versões
                
                **v8.41** <span style="background: #ef4444; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🔥</span>
                - 🔧 **Fix crítico:** Sprint agora pega a ATIVA, não a mais frequente
                - 📊 Filtra por `sprint_state == 'active'` antes de exibir
                - 🚨 **Release atrasada:** Barra vermelha + alerta visual
                - ⚡ **Release hoje:** Barra amarela com destaque
                - 📅 Cálculo correto de dias até release
                
                **v8.40** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎯 **Análise de Sprint (SD)** - Planejado vs Entregue!
                - 📊 Taxa de entrega da sprint com métricas visuais
                - 🚨 Cards fora do planejamento (Hotfix, PB, Criação direta)
                - 📋 Cards originados do PB por produto
                - ⏰ **PB: Aguarda Revisão** com alerta de SLA atrasado
                - 😴 **PB: Cards parados** - slider para definir dias sem atuação
                - 🏷️ **PB: Análise por Temas** - total por tema/cliente + cruzamento
                - ⏱️ **PB: Tempo de Vida por Importância** - Alto/Médio/Baixo
                - 🔎 **Filtros de comentários**: busca por texto + filtro por autor
                - 📦 Novos campos: Temas, Importância, SLA, Issue Links
                
                **v8.39** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📦 **Tags específicas por projeto** - PB tem tags de Produto!
                - ✅ PB: Decisão (verde) - aprovações e definições
                - ❓ PB: Dúvida (amarelo) - perguntas e questionamentos
                - 📋 PB: Requisito (azul) - escopo e critérios de aceite
                - 🤝 PB: Alinhamento (roxo) - reuniões e conversas
                - 🎨 SD/QA mantém tags de QA (Bug, Reprovação, etc.)
                
                **v8.38** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🐛 Detecção de #bug (hashtag) - padrão do QA
                - 🔍 +50 novos padrões de bugs adicionados
                - 🌐 Detecta problemas de tradução, UX, interface
                - ⚠️ Detecta "sistema retornou", "api retornou", "devTools"
                - 📝 Detecta "ao tentar", "ao clicar", "ao criar", etc.
                
                **v8.37** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🔍 Filtros interativos para tipos de comentários
                - 🐛 Detecção de bugs ampliada (80+ padrões)
                - 🔄 Nova categoria: Retorno DEV (ciano)
                - 📊 Checkboxes para filtrar: Bug, Reprovação, Impedimento, Retorno, Outros
                - 🎨 Visual ainda mais distinto por categoria
                - 📈 Contador de comentários exibidos vs total
                
                **v8.36** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎨 Visual de comentários completamente reformulado
                - 🐛 Bug: fundo vermelho claro + borda vermelha + badge numerado
                - ❌ Reprovação: fundo laranja claro + borda laranja + badge numerado  
                - 🚫 Impedimento: fundo roxo claro + borda roxa + badge numerado
                - 📍 Contexto temporal: "Antes Reprovação #1", "Após Bug #2"
                - 📊 Legenda visual no topo dos comentários
                
                **v8.35** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🧠 Comentários inteligentes: filtra automações do GitHub
                - 🐛 Destaca comentários de bugs (borda vermelha)
                - ❌ Destaca comentários de reprovação (borda laranja)
                - 📊 Mostra contagem de bugs/reprovações no título
                - ℹ️ Informa quantos comentários de automação foram ocultados
                
                **v8.34** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📦 Refatoração da aba Produto (PB) a pedido da Ellen
                - 🚫 PB: Hotfix removido (não passa por produto)
                - 📅 Filtro: "Todo o período" agora é padrão
                - 📝 PB: Descrição, Labels, Componentes e Epic nos cards
                - 👤 PB: Mostra Responsável no card pesquisado
                
                **v8.33** <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔧 Fix: Login persistente restaurado corretamente
                - 🍪 Usa get_all() para aguardar cookies carregarem
                - ⚡ Corrigido timing assíncrono do CookieManager
                
                **v8.32** <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔧 Fix: CachedWidgetWarning no CookieManager
                - 🍪 Removido @st.cache_resource (widgets não podem ser cacheados)
                - 🛡️ Tratamento de erros em todas operações com cookies
                
                **v8.31** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🔒 Login persistente agora usa cookies (mais confiável)
                - 🍪 Biblioteca extra-streamlit-components para gerenciar cookies
                - ⏰ Cookie expira em 30 dias
                
                **v8.30** <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔧 Fix: Login persistente agora funciona corretamente
                - 🔒 Mantém sessão entre atualizações e novas abas
                
                **v8.29** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🔒 "Lembrar de mim" - login persistente no navegador
                - 🔓 Não precisa mais fazer login toda vez que atualiza
                - 🧹 Logout limpa o login salvo
                
                **v8.28** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📋 PB: Mostra "Relator" em vez de "Criado por"
                - 📋 PB: Adiciona campo "Resolução/Roteiro" em destaque
                - 🔍 Melhoria na visão de produto para itens de backlog
                
                **v8.27** <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔧 Fix: Removido tooltips customizados que quebravam layout
                - ℹ️ Mantido help nativo do Streamlit (ícone ?) nos st.metric
                
                **v8.26** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 💡 Tooltips em todas as métricas (hover para explicação)
                - ℹ️ FPY, DDP, Fator K, Lead Time, Health Score explicados
                - 📊 Captions explicativos em Throughput e Produtividade
                
                **v8.25** <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🧹 Fix: URL limpa - remove params cruzados QA/Dev
                - 🧹 Clear total ao voltar para visão geral
                
                **v8.24** <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🧹 Fix: Limpa parâmetros da URL ao voltar para visão geral
                
                **v8.23** *(14/04/2026)*
                - 🚀 Navegação direta via link compartilhado
                - ⬅️ Botão "Ver Dashboard Completo" para voltar
                
                **v8.22** *(14/04/2026)*
                - 🔗 Fix: Botão "Copiar Link" para QA/Dev (igual ao card individual)
                - ✅ URL correta do Streamlit Cloud
                
                **v8.21** *(14/04/2026)*
                - 🔗 Links compartilháveis para QA e Dev individuais
                - 📊 Novas métricas: throughput, eficiência, comparativo
                - 📈 Gráficos de tendência individual
                - 🎯 URL params: ?aba=qa&qa=Nome ou ?aba=dev&dev=Nome
                
                **v8.20** *(14/04/2026)*
                - 📦 Filtro Produto acima do rodapé
                
                **v8.19** *(13/04/2026)*
                - 📋 Changelog na sidebar
                
                **v8.18** *(13/04/2026)*
                - ✅ Botão "Copiar Link" funcionando
                
                **v8.17** *(13/04/2026)*
                - 🔧 Fix erro React #231
                
                **v8.16** *(13/04/2026)*
                - 🔧 Fix busca (colunas iguais)
                
                **v8.15** *(13/04/2026)*
                - 🔔 Toast ao copiar link
                
                **v8.14** *(13/04/2026)*
                - 🎨 KPIs em cards estilizados
                
                **v8.13** *(13/04/2026)*
                - ⌨️ Busca funciona com Enter
                
                **v8.12** *(13/04/2026)*
                - ⚠️ Indicador SP estimado
                
                **v8.11** *(12/04/2026)*
                - 🔍 Botão "Buscar" explícito
                
                **v8.10** *(12/04/2026)*
                - 🏠 Logo centralizada, UX
                
                **v8.9** *(12/04/2026)*
                - 💬 Comentários do Jira
                - 📦 Conteúdo por projeto
                
                **v8.8** *(11/04/2026)*
                - 🔗 Card linkages
                - 🔍 Busca simplificada
                
                **v8.7** *(10/04/2026)*
                - ⬅️ Botão voltar sidebar
                - 🎨 Design refinado
                
                **v8.6** *(09/04/2026)*
                - 📱 Sidebar refatorada
                - 📤 Link compartilhável
                
                **v8.5** *(08/04/2026)*
                - 🔍 Busca de card individual
                - 📊 Painel completo do card
                """, unsafe_allow_html=True)
        
        # Captura query params para navegação direta (QA/Dev/Suporte individual)
        aba_param = st.query_params.get("aba", None)
        qa_param = st.query_params.get("qa", None)
        dev_param = st.query_params.get("dev", None)
        pessoa_param = st.query_params.get("pessoa", None)
        
        # NAVEGAÇÃO DIRETA via link compartilhado
        if aba_param == "suporte" and pessoa_param:
            # Mostra diretamente a aba Suporte com a pessoa selecionada
            col_header, col_voltar = st.columns([4, 1])
            with col_header:
                st.markdown(f"### 🔗 Link Compartilhado: Suporte/Implantação")
            with col_voltar:
                if st.button("⬅️ Ver Dashboard Completo", use_container_width=True, key="btn_voltar_suporte"):
                    st.query_params.clear()
                    st.rerun()
            st.markdown("---")
            aba_suporte_implantacao(df_todos)
            return
        
        if aba_param == "qa" and qa_param:
            # Mostra diretamente a aba QA com o colaborador selecionado
            col_header, col_voltar = st.columns([4, 1])
            with col_header:
                st.markdown(f"### 🔗 Link Compartilhado: Métricas de QA")
            with col_voltar:
                if st.button("⬅️ Ver Dashboard Completo", use_container_width=True, key="btn_voltar_qa"):
                    st.query_params.clear()
                    st.rerun()
            st.markdown("---")
            aba_qa(df)
            return
        
        if aba_param == "dev" and dev_param:
            # Mostra diretamente a aba Dev com o colaborador selecionado
            col_header, col_voltar = st.columns([4, 1])
            with col_header:
                st.markdown(f"### 🔗 Link Compartilhado: Métricas de Dev")
            with col_voltar:
                if st.button("⬅️ Ver Dashboard Completo", use_container_width=True, key="btn_voltar_dev"):
                    st.query_params.clear()
                    st.rerun()
            st.markdown("---")
            aba_dev(df)
            return
        
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
        
        elif projeto == "VALPROD":
            # Projeto VALPROD: Foco em Validação em Produção + Suporte
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🎯 Suporte/Implantação",
                "📊 Visão Geral",
                "📋 Governança",
                "📈 Histórico",
                "ℹ️ Sobre"
            ])
            
            with tab1:
                aba_suporte_implantacao(df_todos)
            
            with tab2:
                aba_visao_geral(df, ultima_atualizacao)
            
            with tab3:
                aba_governanca(df)
            
            with tab4:
                aba_historico(df)
            
            with tab5:
                aba_sobre()
        
        else:
            # Projetos SD e QA: Abas completas com QA/Dev + Clientes + Suporte
            tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
                "📊 Visão Geral",
                "🔬 QA",
                "👨‍💻 Dev",
                "🎯 Suporte/Implantação",
                "🏢 Clientes",
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
                aba_suporte_implantacao(df_todos)
            
            with tab5:
                aba_clientes(df_todos)
            
            with tab6:
                aba_governanca(df)
            
            with tab7:
                aba_produto(df)
            
            with tab8:
                aba_historico(df)
            
            with tab9:
                aba_lideranca(df)
            
            with tab10:
                aba_sobre()


if __name__ == "__main__":
    main()
