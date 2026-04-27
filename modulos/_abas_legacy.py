"""
================================================================================
MÓDULO DE ABAS - NinaDash v8.82
================================================================================
Contém todas as abas de visualização do dashboard.

Responsabilidades:
- Renderização de dashboards por contexto (QA, Dev, Liderança, etc)
- Abas especializadas (Clientes, Produto, Backlog, Suporte/Implantação)
- Abas secundárias (Histórico, Sobre)
- Dashboard personalizado

Cada aba é uma função completa que renderiza a UI usando Streamlit.

Dependências:
- streamlit (para st.* commands)
- pandas, plotly, datetime
- modulos.config, modulos.utils, modulos.calculos, modulos.jira_api

Author: GitHub Copilot
Version: 1.0 (Phase 6)
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import random

from modulos.config import (
    JIRA_BASE_URL, CUSTOM_FIELDS, STATUS_FLOW, STATUS_NOMES, STATUS_CORES,
    TOOLTIPS, REGRAS, PB_FUNIL_ETAPAS, TEMAS_NAO_CLIENTES, NINA_LOGO_SVG,
    CATEGORIAS_METRICAS, CATALOGO_METRICAS, NINADASH_URL
)
from modulos.utils import (
    link_jira, card_link_com_popup, traduzir_link, 
    calcular_dias_necessarios_validacao, avaliar_janela_validacao, get_secrets
)
from modulos.calculos import (
    calcular_fator_k, calcular_ddp, calcular_fpy, calcular_lead_time,
    analisar_dev_detalhado, filtrar_qas_principais,
    calcular_concentracao_conhecimento, gerar_recomendacoes_rodizio,
    calcular_concentracao_pessoa, calcular_metricas_governanca,
    calcular_metricas_qa, calcular_metricas_produto, calcular_health_score,
    calcular_metricas_dev, calcular_metricas_backlog, processar_issues,
    classificar_maturidade
)
from modulos.helpers import (
    calcular_valor_metrica, calcular_dados_grafico, calcular_dados_tabela,
    criar_card_metrica, gerar_html_card_ticket, formatar_tempo_relativo,
    gerar_dados_tendencia, exportar_para_csv, exportar_para_excel, get_tooltip_help
)
from modulos.widgets import (
    mostrar_tooltip, mostrar_lista_tickets_completa, mostrar_lista_df_completa,
    renderizar_resultado_consulta, renderizar_widget, renderizar_lista_com_scroll,
    mostrar_card_ticket, exibir_concentracao_time, renderizar_metrica_personalizada,
    exibir_concentracao_simplificada
)
from modulos.graficos import (
    criar_grafico_funil_qa, criar_grafico_tendencia_fator_k,
    criar_grafico_tendencia_qualidade, criar_grafico_tendencia_bugs,
    criar_grafico_tendencia_health, criar_grafico_throughput,
    criar_grafico_lead_time, criar_grafico_reprovacao,
    criar_grafico_estagio_por_produto, criar_grafico_hotfix_por_produto,
    criar_grafico_funil_personalizado, criar_grafico_aging_backlog,
    criar_grafico_prioridade_backlog, criar_grafico_tipo_backlog,
    criar_grafico_backlog_por_produto, criar_grafico_concentracao
)
from modulos.jira_api import (
    gerar_icone_tabler, gerar_icone_tabler_html, gerar_badge_status,
    obter_icone_evento, obter_icone_status,
    buscar_dados_jira_cached, buscar_card_especifico,
    extrair_historico_transicoes, extrair_texto_adf
)

# aba_visao_geral foi movida para modulos/abas/visao_geral.py


# ==============================================================================
# ABAS DO DASHBOARD
# ==============================================================================

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


# ==============================================================================
# ==============================================================================
# FUNÇÕES DE MÉTRICAS
# ==============================================================================

# ==============================================================================
# ANÁLISE DE CONCENTRAÇÃO DE CONHECIMENTO (RODÍZIO)
# ==============================================================================

# ==============================================================================
# BUSCA E DETALHES DO CARD
# ==============================================================================


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
    
    
    # ===== HISTÓRICO DE CARDS VALIDADOS (com lógica corrigida - Sprint Atual mostra todos) =====
    with st.expander("✅ Histórico de Cards Validados", expanded=True):
        exibir_historico_validacoes(df, key_prefix="lideranca")
    
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
        
        # ===== HISTÓRICO DE CARDS VALIDADOS (com lógica corrigida - Sprint Atual mostra todos) =====
        with st.expander("✅ Histórico de Cards Validados", expanded=True):
            exibir_historico_validacoes(df, key_prefix="qa_geral")
    
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


# aba_visao_geral foi movida para modulos/abas/visao_geral.py


# ==============================================================================
# FUNÇÃO: HISTÓRICO DE CARDS VALIDADOS
# ==============================================================================

def exibir_historico_validacoes(df: pd.DataFrame, key_prefix: str = "qa"):
    """
    Exibe histórico de cards validados com filtros.
    
    Mostra:
    - Listagem clicável de cards
    - Filtros por período, QA, tipo, produto
    - Análise dos cards validados
    
    Args:
        df: DataFrame com dados dos cards
        key_prefix: Prefixo para chaves de widgets (evita conflitos)
    """
    st.markdown("### ✅ Histórico de Cards Validados")
    st.caption("Acompanhe todos os cards que passaram por validação")
    
    # Filtra apenas cards validados (status concluído)
    df_validados = df[df['status_cat'] == 'done'].copy()
    
    if df_validados.empty:
        st.info("📭 Nenhum card validado no período selecionado.")
        return
    
    # Lista de opções para filtros
    qas_disponiveis = ['Todos'] + sorted([q for q in df_validados['qa'].unique() if q and q != 'Não atribuído'])
    tipos_disponiveis = ['Todos'] + sorted([t for t in df_validados['tipo'].unique() if t])
    produtos_disponiveis = ['Todos'] + sorted([p for p in df_validados['produto'].unique() if p])
    ambientes_disponiveis = ['Todos', '🟢 Develop', '🟡 Homologação', '🔴 Produção', '⚪ Sem Ambiente']
    
    # ===== FILTROS =====
    st.markdown("#### 🔍 Filtros")
    col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
    
    with col_f1:
        # ATUALIZAÇÃO: Sprint Atual agora é "Sprint Atual (todos)" com valor 0
        # Isso mostra todos os cards validados da sprint sem filtro de data adicional
        periodo_opcoes = {
            "Sprint Atual (todos)": 0,  # Mostra todos os validados (df já filtrado pela sprint na sidebar)
            "Últimos 7 dias": 7,
            "Últimos 15 dias": 15,
            "Últimos 30 dias": 30,
            "Últimos 60 dias": 60,
            "Todo o período": 9999
        }
        periodo_sel = st.selectbox(
            "📅 Período",
            list(periodo_opcoes.keys()),
            index=0,
            key=f"{key_prefix}_periodo_validacao"
        )
    
    with col_f2:
        qa_sel = st.selectbox(
            "🧑‍🔬 QA",
            qas_disponiveis,
            index=0,
            key=f"{key_prefix}_qa_filtro_validacao"
        )
    
    with col_f3:
        tipo_sel = st.selectbox(
            "📋 Tipo",
            tipos_disponiveis,
            index=0,
            key=f"{key_prefix}_tipo_filtro_validacao"
        )
    
    with col_f4:
        produto_sel = st.selectbox(
            "📦 Produto",
            produtos_disponiveis,
            index=0,
            key=f"{key_prefix}_produto_filtro_validacao"
        )
    
    with col_f5:
        ambiente_sel = st.selectbox(
            "🌍 Ambiente",
            ambientes_disponiveis,
            index=0,
            key=f"{key_prefix}_ambiente_filtro_validacao"
        )
    
    # ===== APLICA FILTROS =====
    hoje = datetime.now()
    dias_filtro = periodo_opcoes[periodo_sel]
    
    # LÓGICA CORRIGIDA (conforme HOTFIX recente):
    # - dias_filtro = 0 significa "Sprint Atual (todos)" - SEM filtro de data (mostra todos)
    # - dias_filtro > 0 e < 9999 significa filtrar por resolutiondate
    # - dias_filtro = 9999 significa "Todo o período"
    if dias_filtro == 0:
        # Sprint Atual: mostra todos os validados (df já vem filtrado pela sprint na sidebar)
        df_filtrado = df_validados.copy()
    elif dias_filtro < 9999:
        data_corte = hoje - timedelta(days=dias_filtro)
        df_filtrado = df_validados[
            (df_validados['resolutiondate'].notna()) & 
            (df_validados['resolutiondate'] >= data_corte)
        ].copy()
    else:
        df_filtrado = df_validados.copy()
    
    # Aplica filtros adicionais
    if qa_sel != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['qa'] == qa_sel]
    
    if tipo_sel != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['tipo'] == tipo_sel]
    
    if produto_sel != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['produto'] == produto_sel]
    
    # Filtro por ambiente
    if ambiente_sel != 'Todos' and 'ambiente' in df_filtrado.columns:
        if ambiente_sel == '🟢 Develop':
            df_filtrado = df_filtrado[df_filtrado['ambiente'].str.lower().str.contains('develop', na=False)]
        elif ambiente_sel == '🟡 Homologação':
            df_filtrado = df_filtrado[df_filtrado['ambiente'].str.lower().str.contains('homolog', na=False)]
        elif ambiente_sel == '🔴 Produção':
            df_filtrado = df_filtrado[df_filtrado['ambiente'].str.lower().str.contains('produ', na=False)]
        elif ambiente_sel == '⚪ Sem Ambiente':
            df_filtrado = df_filtrado[df_filtrado['ambiente'].isna() | (df_filtrado['ambiente'] == '')]
    
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum card encontrado para os filtros selecionados.")
        return
    
    # ===== KPIs =====
    st.markdown("---")
    st.markdown("#### 📊 Resumo dos Cards Validados")
    
    # Helper para mini-cards harmonizados
    def mini_card(valor, titulo, subtitulo, cor="#6b7280"):
        bg = f"{cor}10" if cor != "#6b7280" else "white"
        border = f"{cor}40" if cor != "#6b7280" else "#e5e7eb"
        return f'<div style="background: {bg}; border: 2px solid {border}; border-radius: 12px; padding: 16px 12px; text-align: center; height: 95px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);"><div style="font-size: 28px; font-weight: 700; color: {cor}; line-height: 1.1;">{valor}</div><div style="font-size: 12px; font-weight: 600; color: #374151; margin-top: 4px;">{titulo}</div><div style="font-size: 10px; color: #6b7280;">{subtitulo}</div></div>'
    
    def cor_status_inv(valor, verde, amarelo):
        if valor >= verde:
            return "#22c55e"
        elif valor >= amarelo:
            return "#f59e0b"
        return "#ef4444"
    
    total_validados = len(df_filtrado)
    total_bugs = int(df_filtrado['bugs'].sum()) if 'bugs' in df_filtrado.columns else 0
    cards_sem_bugs = len(df_filtrado[df_filtrado['bugs'] == 0]) if 'bugs' in df_filtrado.columns else 0
    taxa_sem_bugs = cards_sem_bugs / total_validados * 100 if total_validados > 0 else 0
    dias_medio = (df_filtrado['atualizado'].max() - df_filtrado['criado'].min()).days if not df_filtrado.empty else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(mini_card(str(total_validados), "✅ Validados", "concluídos", "#22c55e"), unsafe_allow_html=True)
    
    with col2:
        cor = "#f59e0b" if total_bugs > 0 else "#22c55e"
        st.markdown(mini_card(str(total_bugs), "🐛 Bugs Total", "encontrados", cor), unsafe_allow_html=True)
    
    with col3:
        cor = cor_status_inv(taxa_sem_bugs, 80, 60)
        st.markdown(mini_card(f"{taxa_sem_bugs:.0f}%", "🟢 Sem Bugs", f"{cards_sem_bugs} cards", cor), unsafe_allow_html=True)
    
    with col4:
        st.markdown(mini_card(str(dias_medio), "📅 Dias", "span período", "#3b82f6"), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
    
    # ===== LISTAGEM DE CARDS =====
    st.markdown("---")
    st.markdown("#### 📋 Cards")
    
    df_filtrado_sorted = df_filtrado.sort_values('atualizado', ascending=False)
    
    # Container com scroll (classe global)
    cards_html = '<div class="scroll-container" style="max-height: 350px;">'
    
    for idx, (_, row) in enumerate(df_filtrado_sorted.head(50).iterrows()):
        bugs = int(row.get('bugs', 0))
        bugs_cor = '#ef4444' if bugs >= 2 else '#eab308' if bugs == 1 else '#22c55e'
        card_link = card_link_com_popup(row['ticket_id'])
        titulo = str(row.get('titulo', 'N/A'))[:60]
        dev = str(row.get('desenvolvedor', 'N/A'))
        sp = str(row.get('sp', '0'))
        qa = str(row.get('qa', ''))
        
        cards_html += '<div style="padding: 10px; margin: 5px 0; border-left: 3px solid ' + bugs_cor + '; background: rgba(100,100,100,0.05); border-radius: 4px;">'
        cards_html += '<div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">'
        cards_html += card_link
        cards_html += '<span style="color: #64748b;"> - ' + titulo + '...</span>'
        cards_html += '</div>'
        cards_html += '<small style="color: #94a3b8;">👤 ' + dev + ' | ' + sp + ' SP | 🐛 ' + str(bugs) + ' bugs'
        if qa and qa != 'Não atribuído':
            cards_html += ' | 🧑‍🔬 ' + qa
        cards_html += '</small></div>'
    
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)
    
    if len(df_filtrado_sorted) > 50:
        st.caption(f"📋 Mostrando 50 de {len(df_filtrado_sorted)} cards")



