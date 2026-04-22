"""
================================================================================
MÓDULO DASHBOARDS_PERSONALIZADOS - NinaDash v8.82
================================================================================
Dashboards Personalizados - Configuração de dashboards por usuário

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




