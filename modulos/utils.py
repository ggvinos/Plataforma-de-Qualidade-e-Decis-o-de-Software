"""
🔧 UTILS - Funções Utilitárias

Funções puras sem dependências de Streamlit ou estado.
Inclui helpers para links, tradução, cálculos simples, etc.
"""

import os
from typing import Dict
from modulos.config import (
    JIRA_BASE_URL,
    NINADASH_URL,
    TRADUCAO_LINK_TYPES,
    REGRAS,
)

# ==============================================================================
# JIRA LINKS
# ==============================================================================

def link_jira(ticket_id: str) -> str:
    """Gera URL para o Jira."""
    return f"{JIRA_BASE_URL}/browse/{ticket_id}"


def card_link_com_popup(ticket_id: str, projeto: str = None, inline: bool = True) -> str:
    """Gera HTML de link para Jira com botão NinaDash no hover."""
    if not projeto:
        if ticket_id.startswith("PB-"):
            projeto = "PB"
        elif ticket_id.startswith("QA-"):
            projeto = "QA"
        else:
            projeto = "SD"
    
    url_jira = f"{JIRA_BASE_URL}/browse/{ticket_id}"
    url_dashboard = f"?card={ticket_id}&projeto={projeto}"
    
    cores = {"PB": "#8b5cf6", "SD": "#3b82f6", "QA": "#22c55e"}
    cor = cores.get(projeto, "#6b7280")
    
    html = f'''<span class="card-link-wrapper">
        <a href="{url_jira}" target="_blank" class="card-link-id" style="color: {cor};">{ticket_id}</a>
        <a href="{url_dashboard}" target="_blank" class="card-action-btn card-action-nina">📊 NinaDash</a>
    </span>'''
    
    return html


def card_link_para_html(ticket_id: str, projeto: str = None) -> str:
    """Gera link de card com popup para uso em HTML puro."""
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
    url_dashboard = f"{NINADASH_URL}?card={ticket_id}&projeto={projeto}"
    
    cores = {"PB": "#8b5cf6", "SD": "#3b82f6", "QA": "#22c55e", "VALPROD": "#f59e0b", "DVG": "#14b8a6"}
    cor = cores.get(projeto, "#6b7280")
    
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


# ==============================================================================
# TRADUÇÃO
# ==============================================================================

def traduzir_link(texto: str) -> str:
    """Traduz tipo de link do inglês para português."""
    if not texto:
        return texto
    
    texto_lower = texto.lower().strip()
    for en, pt in TRADUCAO_LINK_TYPES.items():
        if en.lower() == texto_lower:
            return pt
    return texto


# ==============================================================================
# JANELA DE VALIDAÇÃO
# ==============================================================================

def calcular_dias_necessarios_validacao(complexidade: str) -> int:
    """Calcula dias necessários para validação por complexidade."""
    janela = REGRAS["janela_complexidade"]
    return janela.get(complexidade, janela["default"])


def avaliar_janela_validacao(dias_ate_release: int, complexidade: str) -> Dict:
    """Avalia se um card está dentro da janela de validação."""
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
        "complexidade_usada": complexidade if complexidade else "Não definida (3d)",
    }


# ==============================================================================
# CREDENCIAIS
# ==============================================================================

def get_secrets():
    """Carrega credenciais Jira com fallback para env vars."""
    try:
        import streamlit as st
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
    """Verifica se credenciais estão configuradas."""
    secrets = get_secrets()
    return bool(secrets["email"] and secrets["token"])
