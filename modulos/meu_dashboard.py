"""
================================================================================
MÓDULO MEU_DASHBOARD - NinaDash v8.82
================================================================================
Meu Dashboard - Widgets personalizados por usuário

Dependências:
- streamlit, pandas, plotly, datetime
- modulos.config, modulos.utils, modulos.calculos, modulos.jira_api, modulos.processamento

Author: GitHub Copilot
Version: 1.0 (Phase 7)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

from modulos.config import (
    JIRA_BASE_URL, CUSTOM_FIELDS, STATUS_FLOW, STATUS_NOMES, STATUS_CORES,
    TOOLTIPS, REGRAS, PB_FUNIL_ETAPAS, TEMAS_NAO_CLIENTES
)
from modulos.utils import (
    link_jira, card_link_com_popup, traduzir_link,
    calcular_dias_necessarios_validacao, avaliar_janela_validacao, get_secrets
)
from modulos.calculos import (
    calcular_fator_k, calcular_ddp, calcular_fpy, calcular_lead_time,
    analisar_dev_detalhado, filtrar_qas_principais,
    calcular_concentracao_conhecimento, gerar_recomendacoes_rodizio,
    calcular_metricas_governanca, calcular_metricas_qa, calcular_metricas_produto,
    calcular_health_score, calcular_metricas_dev, calcular_metricas_backlog
)
from modulos.jira_api import (
    buscar_dados_jira_cached, buscar_card_especifico,
    gerar_icone_tabler, gerar_badge_status, obter_icone_status,
    extrair_historico_transicoes, extrair_texto_adf
)


# ==============================================================================
# FUNÇÕES DO MÓDULO
# ==============================================================================

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




