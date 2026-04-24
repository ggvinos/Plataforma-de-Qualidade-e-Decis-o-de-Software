"""
================================================================================
ABA BACKLOG - NinaDash v8.82
================================================================================
Análise do Product Backlog (PB).

Funcionalidades:
- Score de saúde do backlog
- Análise de aging (envelhecimento)
- Cards problemáticos (sem SP, sem responsável, estagnados)
- Análise por temas e produto
- Tempo de vida por importância

Author: GitHub Copilot
Version: 1.0 (Phase 6)
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

from modulos.config import TEMAS_NAO_CLIENTES
from modulos.calculos import calcular_metricas_backlog
from modulos.helpers import criar_card_metrica
from modulos.utils import link_jira, card_link_com_popup
from modulos.widgets import mostrar_lista_df_completa
from modulos.graficos import (
    criar_grafico_aging_backlog,
    criar_grafico_prioridade_backlog,
    criar_grafico_tipo_backlog,
    criar_grafico_backlog_por_produto,
)


def aba_backlog(df: pd.DataFrame):
    """Aba de análise do Product Backlog (PB)."""
    st.markdown("### 📋 Product Backlog - Análise de Gargalos")
    st.caption("Visualize a saúde do backlog, identifique itens estagnados e tome decisões de priorização")
    
    metricas = calcular_metricas_backlog(df)
    
    # Score de Saúde do Backlog
    with st.expander("🏥 Saúde do Backlog", expanded=False):
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
        with st.expander("💡 Recomendações Automáticas", expanded=False):
            for rec in metricas['recomendacoes']:
                classe = 'alert-critical' if rec['criticidade'] == 'alta' else 'alert-warning'
                st.markdown(f"""
                <div class="{classe}">
                    <b>{rec['tipo']}</b>
                    <p>{rec['msg']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Análise de Aging
    with st.expander("📊 Análise de Envelhecimento (Aging)", expanded=False):
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
    with st.expander("📊 Distribuição do Backlog", expanded=False):
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
    with st.expander("📦 Backlog por Produto", expanded=False):
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
        with st.expander(f"⏰ Aguarda Revisão de Produto ({len(df_aguarda_revisao)} cards)", expanded=False):
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
        with st.expander(f"😴 Cards sem Atuação há {dias_alerta}+ dias ({len(df_sem_atuacao)} cards)", expanded=False):
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
        with st.expander("⏱️ Tempo de Vida por Importância", expanded=False):
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
