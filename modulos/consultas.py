"""
================================================================================
MÓDULO CONSULTAS - NinaDash v8.82
================================================================================
Consultas Personalizadas

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

from modulos.processamento import filtrar_df_por_consulta, aplicar_filtros_widget, calcular_periodo_datas


# ==============================================================================
# FUNÇÕES DO MÓDULO
# ==============================================================================

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


