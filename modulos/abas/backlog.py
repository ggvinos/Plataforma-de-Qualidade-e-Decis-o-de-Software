"""
================================================================================
ABA BACKLOG - NinaDash v8.82
================================================================================
Análise do Product Backlog (PB) - 100% FOCADO EM PRODUTO

Funcionalidades:
- Funil de Produto Visual (5 etapas)
- KPIs de Produto para PO
- Score de saúde do backlog
- Análise de aging (envelhecimento)
- Visão por Cliente/Tema
- Projeção de capacidade
- Cards por etapa do funil

Author: GitHub Copilot
Version: 2.0 (Redesign Produto)
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

from modulos.config import TEMAS_NAO_CLIENTES, PB_FUNIL_ETAPAS, STATUS_NOMES, STATUS_CORES
from modulos.calculos import calcular_metricas_backlog
from modulos.helpers import obter_contexto_periodo
from modulos.utils import link_jira, card_link_com_popup
from modulos.widgets import mostrar_lista_df_completa, mostrar_lista_tickets_completa
from modulos.graficos import (
    criar_grafico_aging_backlog,
    criar_grafico_prioridade_backlog,
)


def _mini_card(valor, titulo, subtitulo, cor="#6b7280"):
    """Helper para criar mini-cards harmonizados."""
    bg = f"{cor}10" if cor != "#6b7280" else "white"
    border = f"{cor}40" if cor != "#6b7280" else "#e5e7eb"
    return f'<div style="background: {bg}; border: 2px solid {border}; border-radius: 12px; padding: 16px 12px; text-align: center; height: 95px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);"><div style="font-size: 28px; font-weight: 700; color: {cor}; line-height: 1.1;">{valor}</div><div style="font-size: 12px; font-weight: 600; color: #374151; margin-top: 4px;">{titulo}</div><div style="font-size: 10px; color: #6b7280;">{subtitulo}</div></div>'


def _cor_status(valor, verde, amarelo):
    """Retorna cor baseado em thresholds (verde se < verde, amarelo se < amarelo, vermelho se >=)"""
    if valor < verde:
        return "#22c55e"
    elif valor < amarelo:
        return "#f59e0b"
    return "#ef4444"


def _cor_status_inv(valor, verde, amarelo):
    """Inverso - verde se >= verde, amarelo se >= amarelo"""
    if valor >= verde:
        return "#22c55e"
    elif valor >= amarelo:
        return "#f59e0b"
    return "#ef4444"


def aba_backlog(df: pd.DataFrame, projeto: str = "PB"):
    """Aba de análise do Product Backlog (PB) - Visão de Produto."""
    ctx = obter_contexto_periodo()
    
    st.markdown("### 📋 Product Backlog - Visão de Produto")
    st.caption(f"Funil de produto, saúde do backlog e análise de demandas • **{ctx['emoji']} {ctx['titulo']}**")
    
    # Calcular métricas de backlog
    metricas = calcular_metricas_backlog(df)
    df_backlog = metricas.get('df_backlog', df)
    
    # ===== SEÇÃO 1: FUNIL DE PRODUTO =====
    _renderizar_funil_produto(df)
    
    # ===== SEÇÃO 2: KPIs DE PRODUTO =====
    _renderizar_kpis_produto(df, metricas)
    
    # ===== SEÇÃO 3: SAÚDE DO BACKLOG =====
    _renderizar_saude_backlog(metricas)
    
    # ===== SEÇÃO 4: ANÁLISE DE AGING =====
    _renderizar_aging(df, metricas)
    
    # ===== SEÇÃO 5: VISÃO POR CLIENTE/TEMA =====
    _renderizar_visao_clientes(df)
    
    # ===== SEÇÃO 6: PROJEÇÃO DE CAPACIDADE =====
    _renderizar_projecao_capacidade(df, metricas)
    
    # ===== SEÇÃO 7: CARDS POR ETAPA DO FUNIL =====
    _renderizar_cards_por_etapa(df)
    
    # ===== SEÇÃO 8: CARDS PROBLEMÁTICOS =====
    _renderizar_cards_problematicos(metricas)
    
    # ===== SEÇÃO 9: SOBRE ESTA ABA =====
    _renderizar_sobre()


def _renderizar_funil_produto(df: pd.DataFrame):
    """Renderiza o funil de produto visual com as 5 etapas."""
    st.markdown("##### 🎯 Funil de Produto")
    
    # Cores do funil
    cores_funil = {
        "pb_revisao_produto": "#6366f1",
        "pb_roteiro": "#8b5cf6", 
        "pb_ux": "#ec4899",
        "pb_esforco": "#f97316",
        "pb_aguarda_dev": "#22c55e",
    }
    
    # Contar cards em cada etapa
    contagens = {}
    sp_por_etapa = {}
    for cat, nome in PB_FUNIL_ETAPAS:
        cards_etapa = df[df['status_cat'] == cat]
        contagens[cat] = len(cards_etapa)
        sp_por_etapa[cat] = int(cards_etapa['sp'].sum())
    
    total_funil = sum(contagens.values())
    
    # Criar visualização do funil
    cols = st.columns(5)
    
    for i, (cat, nome) in enumerate(PB_FUNIL_ETAPAS):
        with cols[i]:
            cor = cores_funil.get(cat, "#6b7280")
            qtd = contagens[cat]
            sp = sp_por_etapa[cat]
            pct = (qtd / total_funil * 100) if total_funil > 0 else 0
            
            st.markdown(f'''
            <div style="background: {cor}15; border: 2px solid {cor}; border-radius: 12px; 
                        padding: 16px 8px; text-align: center; min-height: 120px;">
                <div style="font-size: 32px; font-weight: 700; color: {cor};">{qtd}</div>
                <div style="font-size: 11px; font-weight: 600; color: #374151; margin-top: 4px;">{nome}</div>
                <div style="font-size: 10px; color: #6b7280; margin-top: 4px;">{sp} SP · {pct:.0f}%</div>
            </div>
            ''', unsafe_allow_html=True)
    
    # Setas entre as etapas (indicador de fluxo)
    st.markdown(f'''
    <div style="text-align: center; margin: 8px 0 16px 0; color: #9ca3af; font-size: 12px;">
        📝 → 📋 → 🎨 → ⏱️ → 💻 → 🚀 <span style="color: #22c55e; font-weight: 600;">Desenvolvimento</span>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)


def _renderizar_kpis_produto(df: pd.DataFrame, metricas: dict):
    """Renderiza os KPIs principais de Produto."""
    st.markdown("##### 📊 Indicadores de Produto")
    
    # Calcular métricas
    total_backlog = metricas['total_itens']
    sp_pendentes = metricas['sp_pendentes']
    idade_media = metricas['idade_media']
    pct_sem_sp = metricas['pct_sem_sp']
    
    # Cards aguardando (status PB)
    status_pb = ['pb_revisao_produto', 'pb_roteiro', 'pb_ux', 'pb_esforco', 'pb_aguarda_dev']
    cards_aguardando = len(df[df['status_cat'].isin(status_pb)])
    
    # Cards alta prioridade
    prioridades_altas = ['Highest', 'High', 'Alta', 'Muito Alta', 'Crítica']
    cards_alta_prio = len(df[df['prioridade'].isin(prioridades_altas) & df['status_cat'].isin(status_pb + ['backlog', 'unknown'])])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(_mini_card(str(total_backlog), "📋 No Backlog", "itens pendentes", "#3b82f6"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(_mini_card(str(sp_pendentes), "📊 SP Pendentes", "story points", "#8b5cf6"), unsafe_allow_html=True)
    
    with col3:
        cor = _cor_status(idade_media, 30, 60)
        st.markdown(_mini_card(f"{idade_media:.0f}d", "⏱️ Idade Média", "dias no backlog", cor), unsafe_allow_html=True)
    
    with col4:
        cor = _cor_status(cards_alta_prio, 5, 10)
        st.markdown(_mini_card(str(cards_alta_prio), "🔴 Alta Prioridade", "urgentes", cor), unsafe_allow_html=True)
    
    with col5:
        cor = _cor_status(pct_sem_sp, 20, 40)
        st.markdown(_mini_card(f"{pct_sem_sp:.0f}%", "❓ Sem Estimativa", "a refinar", cor), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)


def _renderizar_saude_backlog(metricas: dict):
    """Renderiza o score de saúde do backlog."""
    with st.expander("🏥 Saúde do Backlog", expanded=True):
        score = metricas['score_saude']
        status = metricas['status_saude']
        
        # Determinar cor e emoji baseado no score
        if score >= 75:
            cor_score = "#22c55e"
            emoji_score = "🟢"
            msg = "Backlog saudável! Continue monitorando."
        elif score >= 50:
            cor_score = "#f59e0b"
            emoji_score = "🟡"
            msg = "Backlog precisa de atenção. Revise a priorização."
        elif score >= 25:
            cor_score = "#f97316"
            emoji_score = "🟠"
            msg = "Backlog com problemas. Agende grooming urgente!"
        else:
            cor_score = "#ef4444"
            emoji_score = "🔴"
            msg = "Backlog crítico! Reavaliação completa necessária."
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f'''
            <div style="background: {cor_score}15; border: 3px solid {cor_score}; border-radius: 16px; 
                        padding: 24px; text-align: center;">
                <div style="font-size: 48px; font-weight: 700; color: {cor_score};">{score:.0f}</div>
                <div style="font-size: 14px; font-weight: 600; color: #374151; margin-top: 8px;">Health Score</div>
                <div style="font-size: 20px; margin-top: 8px;">{emoji_score} {status}</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'''
            <div style="background: #f8fafc; border-radius: 12px; padding: 16px; height: 100%;">
                <h4 style="margin: 0 0 12px 0; color: #374151;">📋 O que compõe o score?</h4>
                <ul style="margin: 0; padding-left: 20px; color: #4b5563; font-size: 14px; line-height: 1.8;">
                    <li><strong>Idade média</strong> - Penaliza se > 30 dias</li>
                    <li><strong>Cards sem estimativa</strong> - Penaliza se > 20%</li>
                    <li><strong>Cards aging (> 60 dias)</strong> - Penaliza acúmulo</li>
                    <li><strong>Distribuição de prioridade</strong> - Penaliza desequilíbrio</li>
                </ul>
                <div style="background: {cor_score}20; border-left: 4px solid {cor_score}; padding: 10px 12px; 
                            margin-top: 12px; border-radius: 0 8px 8px 0;">
                    <span style="font-size: 13px; color: #374151;"><strong>💡 Recomendação:</strong> {msg}</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Recomendações automáticas
        if metricas.get('recomendacoes'):
            st.markdown("##### 💡 Ações Recomendadas")
            for rec in metricas['recomendacoes'][:3]:  # Top 3
                classe_cor = "#ef4444" if rec['criticidade'] == 'alta' else "#f59e0b"
                st.markdown(f'''
                <div style="background: {classe_cor}10; border-left: 4px solid {classe_cor}; 
                            padding: 10px 15px; margin: 8px 0; border-radius: 0 8px 8px 0;">
                    <strong style="color: {classe_cor};">{rec['tipo']}</strong>
                    <p style="margin: 4px 0 0 0; color: #4b5563; font-size: 13px;">{rec['msg']}</p>
                </div>
                ''', unsafe_allow_html=True)


def _renderizar_aging(df: pd.DataFrame, metricas: dict):
    """Renderiza análise de aging (envelhecimento)."""
    with st.expander("📊 Análise de Envelhecimento (Aging)", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de faixas de idade
            faixas = metricas['faixas_idade']
            fig = criar_grafico_aging_backlog(faixas)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("##### 📈 Métricas de Aging")
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric("📅 Mais Antigo", f"{metricas['mais_antigo']} dias")
                st.metric("⏰ Cards > 60 dias", f"{faixas['61-90'] + faixas['90+']}")
            with c2:
                st.metric("🗑️ Cards > 90 dias", f"{faixas['90+']}")
                st.metric("📊 Idade Mediana", f"{metricas['idade_mediana']:.0f} dias")
            
            if faixas['90+'] > 0:
                st.warning(f"⚠️ **{faixas['90+']} cards** estão há mais de 90 dias no backlog - candidatos a descarte!")
        
        # Cards aging detalhados
        if not metricas['cards_aging'].empty:
            st.markdown("##### 📋 Cards Mais Antigos (> 60 dias)")
            cards_aging = metricas['cards_aging'].head(10)
            mostrar_lista_tickets_completa(cards_aging.to_dict('records'), "Cards Aging")


def _renderizar_visao_clientes(df: pd.DataFrame):
    """Renderiza visão de demandas por cliente/tema."""
    with st.expander("👥 Demandas por Cliente/Tema", expanded=False):
        st.markdown("##### 📊 Distribuição por Cliente")
        st.caption("*Demandas internas (nina, interna) não são exibidas pois beneficiam todos os clientes*")
        
        if 'temas' not in df.columns:
            st.info("Campo 'Temas' não disponível nos dados")
            return
        
        # Expandir temas (multi-value)
        df_temas = df.explode('temas').copy()
        df_temas = df_temas[df_temas['temas'].notna() & (df_temas['temas'] != '')]
        
        # Remove temas internos
        df_temas = df_temas[~df_temas['temas'].str.lower().str.strip().isin([t.lower() for t in TEMAS_NAO_CLIENTES])]
        
        if df_temas.empty:
            st.info("Nenhum card com tema de cliente definido")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top clientes por quantidade
            tema_counts = df_temas.groupby('temas').agg({
                'ticket_id': 'count',
                'sp': 'sum'
            }).reset_index()
            tema_counts.columns = ['Cliente', 'Cards', 'SP Total']
            tema_counts = tema_counts.sort_values('Cards', ascending=False)
            
            fig = px.bar(tema_counts.head(10), x='Cliente', y='Cards',
                         title='📊 Top 10 Clientes (por Cards)',
                         color='SP Total', color_continuous_scale='Blues')
            fig.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Tabela resumo
            st.markdown("##### 📋 Resumo por Cliente")
            df_display = tema_counts.head(15).copy()
            df_display['SP Total'] = df_display['SP Total'].astype(int)
            st.dataframe(df_display, hide_index=True, use_container_width=True)
        
        # Alerta de concentração
        if not tema_counts.empty:
            top_cliente = tema_counts.iloc[0]
            total_cards = tema_counts['Cards'].sum()
            pct_top = (top_cliente['Cards'] / total_cards * 100) if total_cards > 0 else 0
            
            if pct_top > 30:
                st.warning(f"⚠️ **{top_cliente['Cliente']}** representa {pct_top:.0f}% do backlog ({top_cliente['Cards']} cards)")


def _renderizar_projecao_capacidade(df: pd.DataFrame, metricas: dict):
    """Renderiza projeção de capacidade para zerar o backlog."""
    with st.expander("📈 Projeção de Capacidade", expanded=False):
        st.markdown("##### 🎯 Quanto tempo para entregar o backlog?")
        
        sp_pendentes = metricas['sp_pendentes']
        total_cards = metricas['total_itens']
        
        # Calcular velocidade baseada nos cards concluídos
        df_done = df[df['status_cat'] == 'done']
        
        if df_done.empty:
            st.info("Sem dados de cards concluídos para calcular velocidade")
            return
        
        # Estimar velocidade (SP/sprint, assumindo sprint de 2 semanas)
        sp_done = int(df_done['sp'].sum())
        cards_done = len(df_done)
        
        # Assumir que os dados são de uma sprint
        velocidade_sp = sp_done if sp_done > 0 else 20  # Default 20 SP/sprint
        throughput = cards_done if cards_done > 0 else 10  # Default 10 cards/sprint
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sprints_sp = sp_pendentes / velocidade_sp if velocidade_sp > 0 else 0
            cor = _cor_status(sprints_sp, 3, 6)
            st.markdown(_mini_card(f"{sprints_sp:.1f}", "📊 Sprints (SP)", f"{sp_pendentes} SP / {velocidade_sp} vel", cor), unsafe_allow_html=True)
        
        with col2:
            sprints_cards = total_cards / throughput if throughput > 0 else 0
            cor = _cor_status(sprints_cards, 3, 6)
            st.markdown(_mini_card(f"{sprints_cards:.1f}", "📋 Sprints (Cards)", f"{total_cards} / {throughput} throughput", cor), unsafe_allow_html=True)
        
        with col3:
            semanas = max(sprints_sp, sprints_cards) * 2  # Sprints de 2 semanas
            cor = _cor_status(semanas, 6, 12)
            st.markdown(_mini_card(f"{semanas:.0f}", "📅 Semanas", "estimativa total", cor), unsafe_allow_html=True)
        
        st.caption(f"💡 *Baseado na velocidade atual: {velocidade_sp} SP/sprint, {throughput} cards/sprint*")
        
        # Alerta se backlog muito grande
        if sprints_sp > 6:
            st.warning(f"⚠️ Backlog levará **{sprints_sp:.0f} sprints** (~{semanas:.0f} semanas) para ser entregue. Considere repriorizar!")


def _renderizar_cards_por_etapa(df: pd.DataFrame):
    """Renderiza cards agrupados por etapa do funil."""
    with st.expander("📦 Cards por Etapa do Funil", expanded=False):
        # Criar tabs para cada etapa
        tab_names = [nome for _, nome in PB_FUNIL_ETAPAS]
        tabs = st.tabs(tab_names)
        
        for i, (cat, nome) in enumerate(PB_FUNIL_ETAPAS):
            with tabs[i]:
                cards_etapa = df[df['status_cat'] == cat]
                
                if cards_etapa.empty:
                    st.info(f"Nenhum card em {nome}")
                else:
                    # KPIs da etapa
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📋 Cards", len(cards_etapa))
                    with col2:
                        st.metric("📊 SP Total", int(cards_etapa['sp'].sum()))
                    with col3:
                        idade_media = (datetime.now() - pd.to_datetime(cards_etapa['criado'])).dt.days.mean()
                        st.metric("⏱️ Idade Média", f"{idade_media:.0f}d")
                    
                    # Lista de cards
                    mostrar_lista_tickets_completa(cards_etapa.to_dict('records'), f"Cards em {nome}")


def _renderizar_cards_problematicos(metricas: dict):
    """Renderiza cards que precisam de atenção."""
    with st.expander("⚠️ Cards que Precisam de Atenção", expanded=False):
        tab_sem_sp, tab_sem_resp, tab_estagnados = st.tabs([
            f"📝 Sem Estimativa ({len(metricas['cards_sem_sp'])})",
            f"👤 Sem Responsável ({len(metricas['cards_sem_responsavel'])})",
            f"⏸️ Estagnados ({len(metricas['cards_estagnados'])})"
        ])
        
        with tab_sem_sp:
            if not metricas['cards_sem_sp'].empty:
                st.markdown("**Cards que precisam de estimativa (Story Points):**")
                st.caption("Estes cards não podem ser planejados corretamente sem estimativa")
                mostrar_lista_tickets_completa(metricas['cards_sem_sp'].to_dict('records'), "Sem Estimativa")
            else:
                st.success("✅ Todos os cards têm estimativa!")
        
        with tab_sem_resp:
            if not metricas['cards_sem_responsavel'].empty:
                st.markdown("**Cards sem responsável atribuído:**")
                st.caption("Estes cards estão 'órfãos' - ninguém é dono deles")
                mostrar_lista_tickets_completa(metricas['cards_sem_responsavel'].to_dict('records'), "Sem Responsável")
            else:
                st.success("✅ Todos os cards têm responsável!")
        
        with tab_estagnados:
            if not metricas['cards_estagnados'].empty:
                st.markdown("**Cards sem movimentação há mais de 30 dias:**")
                st.caption("Podem estar esquecidos ou bloqueados")
                mostrar_lista_tickets_completa(metricas['cards_estagnados'].to_dict('records'), "Estagnados")
            else:
                st.success("✅ Nenhum card estagnado!")


def _renderizar_sobre():
    """Renderiza informações sobre esta aba."""
    with st.expander("ℹ️ Sobre esta Aba", expanded=False):
        st.markdown("""
        ### 📋 Product Backlog - Visão de Produto
        
        Esta aba foi criada para ajudar o **Product Owner** e o **Time de Produto** na gestão do backlog:
        
        | Seção | O que mostra |
        |-------|--------------|
        | **🎯 Funil de Produto** | Cards em cada etapa do fluxo de produto |
        | **📊 Indicadores** | KPIs principais: total, SP, idade, prioridade |
        | **🏥 Saúde** | Score de 0-100 baseado em múltiplos fatores |
        | **📊 Aging** | Cards antigos que precisam de decisão |
        | **👥 Clientes** | Demandas por cliente/tema |
        | **📈 Projeção** | Quantas sprints para entregar o backlog |
        | **📦 Por Etapa** | Lista de cards em cada fase do funil |
        | **⚠️ Problemáticos** | Cards sem SP, sem responsável, estagnados |
        
        ### 🎯 Decisões suportadas:
        - **O que priorizar?** → Ver cards por prioridade e idade
        - **O que descartar?** → Cards > 90 dias, baixa prioridade
        - **Backlog saudável?** → Health Score
        - **Qual cliente atender?** → Visão por tema
        - **Capacidade de entrega?** → Projeção de sprints
        """)


# ==============================================================================
# ABAS ESPECÍFICAS PARA PROJETO PB
# ==============================================================================

def aba_produto_pb(df: pd.DataFrame, projeto: str = "PB"):
    """
    Aba de Análise de Demandas específica para Product Backlog.
    Foca em: tipos, origem, reprovações, refinamento pendente.
    """
    ctx = obter_contexto_periodo()
    
    st.markdown("### 📦 Análise de Demandas")
    st.caption(f"Entenda a composição e origem das demandas do backlog • **{ctx['emoji']} {ctx['titulo']}**")
    
    # ===== SEÇÃO 1: DISTRIBUIÇÃO POR TIPO =====
    st.markdown("##### 📊 Distribuição por Tipo de Demanda")
    
    # Contar por tipo
    tipos = df['tipo'].value_counts().reset_index()
    tipos.columns = ['Tipo', 'Quantidade']
    
    if len(tipos) > 0:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Gráfico de pizza
            cores_tipo = {
                'Story': '#3b82f6', 'Tarefa': '#8b5cf6', 'Bug': '#ef4444',
                'HOTFIX': '#f97316', 'Improvement': '#22c55e', 'Epic': '#ec4899',
                'Sub-task': '#6b7280', 'Technical Debt': '#f59e0b'
            }
            fig = px.pie(tipos, values='Quantidade', names='Tipo', 
                        color='Tipo', color_discrete_map=cores_tipo,
                        hole=0.4)
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=280,
                            showlegend=True, legend=dict(orientation="h", y=-0.1))
            fig.update_traces(textposition='inside', textinfo='value+percent')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Mini cards por tipo
            for _, row in tipos.head(5).iterrows():
                tipo = row['Tipo']
                qtd = row['Quantidade']
                cor = cores_tipo.get(tipo, '#6b7280')
                pct = (qtd / len(df) * 100) if len(df) > 0 else 0
                st.markdown(f'''
                <div style="display: flex; align-items: center; padding: 8px 12px; 
                            background: {cor}10; border-left: 4px solid {cor}; 
                            border-radius: 0 8px 8px 0; margin-bottom: 8px;">
                    <div style="flex: 1;">
                        <div style="font-weight: 600; color: #374151;">{tipo}</div>
                        <div style="font-size: 12px; color: #6b7280;">{pct:.1f}% do backlog</div>
                    </div>
                    <div style="font-size: 24px; font-weight: 700; color: {cor};">{qtd}</div>
                </div>
                ''', unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    # ===== SEÇÃO 2: DEMANDAS POR PRIORIDADE =====
    st.markdown("##### 🎯 Priorização do Backlog")
    
    # Mapa de prioridades
    mapa_prio = {
        'Highest': ('🔴', '#ef4444', 1), 'High': ('🟠', '#f97316', 2),
        'Crítica': ('🔴', '#ef4444', 1), 'Muito Alta': ('🟠', '#f97316', 2),
        'Alta': ('🟠', '#f97316', 2), 'Medium': ('🟡', '#f59e0b', 3),
        'Média': ('🟡', '#f59e0b', 3), 'Low': ('🟢', '#22c55e', 4),
        'Baixa': ('🟢', '#22c55e', 4), 'Lowest': ('⚪', '#9ca3af', 5)
    }
    
    # Status que estão no backlog (não finalizados)
    status_backlog = ['pb_revisao_produto', 'pb_roteiro', 'pb_ux', 'pb_esforco', 
                      'pb_aguarda_dev', 'backlog', 'unknown', 'in_progress']
    df_pendentes = df[df['status_cat'].isin(status_backlog)]
    
    prioridades = df_pendentes['prioridade'].value_counts().reset_index()
    prioridades.columns = ['Prioridade', 'Quantidade']
    
    cols = st.columns(min(5, len(prioridades)))
    for i, (_, row) in enumerate(prioridades.head(5).iterrows()):
        prio = row['Prioridade']
        qtd = row['Quantidade']
        emoji, cor, _ = mapa_prio.get(prio, ('⚪', '#9ca3af', 5))
        
        with cols[i]:
            st.markdown(_mini_card(str(qtd), f"{emoji} {prio}", "pendentes", cor), unsafe_allow_html=True)
    
    # Alertas de priorização
    altas = len(df_pendentes[df_pendentes['prioridade'].isin(['Highest', 'High', 'Crítica', 'Muito Alta', 'Alta'])])
    if altas > 10:
        st.warning(f"⚠️ **{altas} demandas** de alta prioridade pendentes. Considere revisar priorização!")
    
    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    # ===== SEÇÃO 3: REPROVAÇÕES E CANCELAMENTOS =====
    with st.expander("❌ Demandas Reprovadas/Canceladas", expanded=False):
        df_reprovados = df[df['status_cat'].isin(['reprovado', 'cancelado', 'descartado'])]
        
        if len(df_reprovados) > 0:
            st.markdown(f"**{len(df_reprovados)}** demandas foram reprovadas/canceladas")
            
            # Motivos (se disponível no resumo)
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📋 Total Reprovados", len(df_reprovados))
                if 'criado' in df_reprovados.columns:
                    ultimos_30d = len(df_reprovados[pd.to_datetime(df_reprovados['criado']) >= 
                                                    datetime.now() - timedelta(days=30)])
                    st.metric("📅 Últimos 30 dias", ultimos_30d)
            
            with col2:
                # Por tipo
                rep_por_tipo = df_reprovados['tipo'].value_counts().head(3)
                for tipo, qtd in rep_por_tipo.items():
                    st.markdown(f"• **{tipo}**: {qtd}")
            
            mostrar_lista_df_completa(df_reprovados, "Demandas Reprovadas")
        else:
            st.success("✅ Nenhuma demanda reprovada/cancelada registrada")
    
    # ===== SEÇÃO 4: PENDENTE DE REFINAMENTO =====
    with st.expander("📝 Pendente de Refinamento", expanded=True):
        # Cards sem SP ou em revisão de produto
        cards_refinamento = df_pendentes[
            (df_pendentes['sp'] == 0) | 
            (df_pendentes['status_cat'] == 'pb_revisao_produto')
        ]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            sem_sp = len(df_pendentes[df_pendentes['sp'] == 0])
            cor = _cor_status(sem_sp, 5, 10)
            st.markdown(_mini_card(str(sem_sp), "❓ Sem Estimativa", "precisa refinar", cor), unsafe_allow_html=True)
        
        with col2:
            em_revisao = len(df_pendentes[df_pendentes['status_cat'] == 'pb_revisao_produto'])
            st.markdown(_mini_card(str(em_revisao), "📝 Em Revisão", "aguarda produto", "#6366f1"), unsafe_allow_html=True)
        
        with col3:
            aguarda_ux = len(df_pendentes[df_pendentes['status_cat'] == 'pb_ux'])
            st.markdown(_mini_card(str(aguarda_ux), "🎨 Aguarda UX", "precisa design", "#ec4899"), unsafe_allow_html=True)
        
        if not cards_refinamento.empty:
            st.markdown("##### 📋 Cards que Precisam de Refinamento")
            mostrar_lista_df_completa(cards_refinamento.head(20), "Pendentes de Refinamento")
    
    # ===== SEÇÃO 5: POR QUEM CRIOU =====
    with st.expander("👤 Demandas por Solicitante", expanded=False):
        if 'relator' in df.columns:
            por_criador = df_pendentes['relator'].value_counts().head(10).reset_index()
            por_criador.columns = ['Solicitante', 'Demandas']
            
            fig = px.bar(por_criador, x='Demandas', y='Solicitante', orientation='h',
                        color='Demandas', color_continuous_scale='Blues')
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300,
                            showlegend=False, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Campo 'relator' não disponível")


def aba_historico_pb(df: pd.DataFrame, projeto: str = "PB"):
    """
    Aba de Evolução do Backlog - específica para Product Backlog.
    Foca em: evolução por período (meses), throughput do funil, tempo médio por etapa.
    NÃO usa sprints - o backlog de produto é avaliado ao longo do tempo.
    """
    ctx = obter_contexto_periodo()
    
    st.markdown("### 📈 Evolução do Backlog de Produto")
    st.caption(f"Acompanhe a evolução do time de produto ao longo do tempo • **{ctx['emoji']} {ctx['titulo']}**")
    
    # Preparar dados
    df = df.copy()
    
    if 'criado' in df.columns:
        df['criado_dt'] = pd.to_datetime(df['criado'], errors='coerce')
    else:
        df['criado_dt'] = pd.NaT
    
    if 'atualizado' in df.columns:
        df['atualizado_dt'] = pd.to_datetime(df['atualizado'], errors='coerce')
    else:
        df['atualizado_dt'] = pd.NaT
    
    hoje = datetime.now()
    
    # Etapas do funil PB
    etapas_funil = [
        ('pb_revisao_produto', '📝 Revisão', '#6366f1'),
        ('pb_roteiro', '📋 Roteiro', '#8b5cf6'),
        ('pb_ux', '🎨 UX', '#ec4899'),
        ('pb_esforco', '⏱️ Esforço', '#f97316'),
        ('pb_aguarda_dev', '💻 Aguarda Dev', '#22c55e'),
    ]
    
    # ===== SEÇÃO 1: KPIs GERAIS DO BACKLOG =====
    st.markdown("##### 📊 Visão Geral do Backlog")
    
    total_geral = len(df)
    total_funil = sum(len(df[df['status_cat'] == s]) for s, _, _ in etapas_funil)
    total_convertido = len(df[df['status_cat'].isin(['pb_aguarda_dev'])])  # Prontos para dev
    sp_total = int(df['sp'].sum()) if 'sp' in df.columns else 0
    
    # Calcular idade média do backlog
    if df['criado_dt'].notna().any():
        idade_media = (hoje - df['criado_dt']).dt.days.mean()
    else:
        idade_media = 0
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(_mini_card(str(total_geral), "📋 Total Cards", "no backlog", "#3b82f6"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(_mini_card(str(sp_total), "📊 Story Points", "total", "#8b5cf6"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(_mini_card(str(total_funil), "🔄 No Funil", "em processo", "#f97316"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(_mini_card(str(total_convertido), "✅ Prontos", "aguardando dev", "#22c55e"), unsafe_allow_html=True)
    
    with col5:
        cor_idade = "#22c55e" if idade_media < 60 else "#f59e0b" if idade_media < 120 else "#ef4444"
        st.markdown(_mini_card(f"{idade_media:.0f}d", "📅 Idade Média", "do backlog", cor_idade), unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)
    
    # ===== SEÇÃO 2: EVOLUÇÃO POR MÊS =====
    with st.expander("📈 Evolução Mensal do Backlog", expanded=True):
        st.markdown("""
        **Como o backlog evoluiu nos últimos meses?**
        
        Criação de novas demandas vs. demandas que avançaram para desenvolvimento.
        """)
        
        if df['criado_dt'].notna().any():
            # Criar dados por mês - últimos 6 meses
            df['mes_criacao'] = df['criado_dt'].dt.to_period('M')
            
            # Gerar range de meses
            meses = pd.period_range(end=pd.Period(hoje, 'M'), periods=6, freq='M')
            
            dados_evolucao = []
            for mes in meses:
                mes_str = mes.strftime('%b/%Y')
                mes_inicio = mes.start_time
                mes_fim = mes.end_time
                
                # Cards criados no mês
                criados = len(df[df['mes_criacao'] == mes])
                
                # Cards que chegaram em "Aguarda Dev" no mês (baseado em atualizado)
                df_atualizado_mes = df[
                    (df['atualizado_dt'] >= mes_inicio) & 
                    (df['atualizado_dt'] <= mes_fim) & 
                    (df['status_cat'] == 'pb_aguarda_dev')
                ]
                convertidos = len(df_atualizado_mes)
                
                # SP criados
                sp_criados = int(df[df['mes_criacao'] == mes]['sp'].sum()) if 'sp' in df.columns else 0
                
                dados_evolucao.append({
                    'Mês': mes_str,
                    'Criados': criados,
                    'Convertidos': convertidos,
                    'SP Criados': sp_criados,
                    'Saldo': convertidos - criados
                })
            
            df_evolucao = pd.DataFrame(dados_evolucao)
            
            # Gráfico de barras agrupadas
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='📥 Criados',
                x=df_evolucao['Mês'],
                y=df_evolucao['Criados'],
                marker_color='#3b82f6'
            ))
            fig.add_trace(go.Bar(
                name='✅ Convertidos (→ Dev)',
                x=df_evolucao['Mês'],
                y=df_evolucao['Convertidos'],
                marker_color='#22c55e'
            ))
            
            fig.update_layout(
                barmode='group',
                margin=dict(t=30, b=30, l=30, r=30),
                height=300,
                legend=dict(orientation="h", y=1.1),
                xaxis_title="Mês",
                yaxis_title="Cards"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabela resumo
            st.dataframe(df_evolucao, use_container_width=True, hide_index=True)
            
            # Análise de tendência
            if len(dados_evolucao) >= 2:
                media_criados = sum(d['Criados'] for d in dados_evolucao) / len(dados_evolucao)
                media_convertidos = sum(d['Convertidos'] for d in dados_evolucao) / len(dados_evolucao)
                
                if media_criados > media_convertidos * 1.2:
                    st.warning(f"⚠️ **Backlog crescendo**: Média de {media_criados:.0f} criados/mês vs {media_convertidos:.0f} convertidos/mês")
                elif media_convertidos > media_criados * 1.2:
                    st.success(f"✅ **Backlog diminuindo**: Média de {media_convertidos:.0f} convertidos/mês vs {media_criados:.0f} criados/mês")
                else:
                    st.info(f"➡️ **Backlog estável**: ~{media_criados:.0f} criados e ~{media_convertidos:.0f} convertidos/mês")
        else:
            st.info("Sem dados de criação para análise mensal")
    
    # ===== SEÇÃO 3: THROUGHPUT DO FUNIL =====
    with st.expander("🎯 Distribuição no Funil de Produto", expanded=True):
        st.markdown("""
        **Quantos cards estão em cada etapa do funil?**
        """)
        
        cols = st.columns(5)
        for i, (status_cat, nome, cor) in enumerate(etapas_funil):
            with cols[i]:
                qtd = len(df[df['status_cat'] == status_cat])
                sp = int(df[df['status_cat'] == status_cat]['sp'].sum()) if 'sp' in df.columns else 0
                st.markdown(f'''
                <div style="background: {cor}15; border: 2px solid {cor}; border-radius: 12px; 
                            padding: 12px 8px; text-align: center;">
                    <div style="font-size: 28px; font-weight: 700; color: {cor};">{qtd}</div>
                    <div style="font-size: 11px; font-weight: 600; color: #374151;">{nome}</div>
                    <div style="font-size: 10px; color: #6b7280;">{sp} SP</div>
                </div>
                ''', unsafe_allow_html=True)
        
        st.markdown("<div style='margin: 16px 0;'></div>", unsafe_allow_html=True)
        
        # Gráfico de funil
        valores_funil = [len(df[df['status_cat'] == s]) for s, _, _ in etapas_funil]
        nomes_funil = [n for _, n, _ in etapas_funil]
        
        if sum(valores_funil) > 0:
            fig = go.Figure(go.Funnel(
                y=nomes_funil,
                x=valores_funil,
                textinfo="value+percent initial",
                marker=dict(color=['#6366f1', '#8b5cf6', '#ec4899', '#f97316', '#22c55e'])
            ))
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    # ===== SEÇÃO 4: TEMPO MÉDIO POR ETAPA =====
    with st.expander("⏱️ Tempo Médio por Etapa", expanded=False):
        st.markdown("""
        **Quanto tempo os cards ficam em cada etapa?**
        
        *Baseado no campo `dias_em_status` - tempo desde última movimentação*
        """)
        
        tempos = []
        for status_cat, nome, cor in etapas_funil:
            df_etapa = df[df['status_cat'] == status_cat]
            if not df_etapa.empty and 'dias_em_status' in df_etapa.columns:
                media_dias = df_etapa['dias_em_status'].mean()
                max_dias = df_etapa['dias_em_status'].max()
                qtd = len(df_etapa)
                tempos.append({
                    'Etapa': nome,
                    'Cards': qtd,
                    'Média (dias)': round(media_dias, 1),
                    'Máximo (dias)': int(max_dias),
                    'cor': cor
                })
        
        if tempos:
            df_tempos = pd.DataFrame(tempos)
            
            # Gráfico de barras horizontais
            fig = px.bar(df_tempos, x='Média (dias)', y='Etapa', orientation='h',
                        color='Etapa', color_discrete_sequence=['#6366f1', '#8b5cf6', '#ec4899', '#f97316', '#22c55e'])
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=250,
                            showlegend=False, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabela
            st.dataframe(df_tempos[['Etapa', 'Cards', 'Média (dias)', 'Máximo (dias)']], 
                        use_container_width=True, hide_index=True)
            
            # Alertas
            for t in tempos:
                if t['Média (dias)'] > 30:
                    st.warning(f"⚠️ **{t['Etapa']}**: {t['Cards']} cards há mais de {t['Média (dias)']:.0f} dias em média!")
        else:
            st.info("Sem dados de tempo por etapa disponíveis")
    
    # ===== SEÇÃO 5: CARDS MAIS ANTIGOS =====
    with st.expander("🗓️ Cards Mais Antigos no Backlog", expanded=False):
        df_funil = df[df['status_cat'].isin([s for s, _, _ in etapas_funil])]
        
        if not df_funil.empty and 'dias_em_status' in df_funil.columns:
            df_antigos = df_funil.nlargest(15, 'dias_em_status')
            
            st.markdown("**Top 15 cards há mais tempo parados (potenciais bloqueios):**")
            
            for _, card in df_antigos.iterrows():
                dias = int(card['dias_em_status'])
                cor = "#ef4444" if dias > 60 else "#f59e0b" if dias > 30 else "#6b7280"
                status_nome = next((n for s, n, _ in etapas_funil if s == card['status_cat']), card['status_cat'])
                titulo = str(card['titulo'])[:55] if pd.notna(card['titulo']) else "Sem título"
                
                st.markdown(f'''
                <div style="display: flex; align-items: center; padding: 8px 12px; 
                            background: #f8fafc; border-left: 4px solid {cor}; 
                            border-radius: 0 8px 8px 0; margin-bottom: 8px;">
                    <div style="flex: 1;">
                        <a href="https://ninatecnologia.atlassian.net/browse/{card['ticket_id']}" target="_blank" 
                           style="color: #3b82f6; text-decoration: none; font-weight: 600;">
                            {card['ticket_id']}
                        </a>
                        <span style="color: #374151; margin-left: 8px;">{titulo}...</span>
                        <span style="color: #9ca3af; font-size: 11px; margin-left: 8px;">({status_nome})</span>
                    </div>
                    <div style="font-size: 14px; font-weight: 700; color: {cor};">{dias}d</div>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("Nenhum card no funil ou sem dados de tempo")
    
    # ===== SEÇÃO 6: DISTRIBUIÇÃO POR TIPO E PRIORIDADE =====
    with st.expander("📊 Composição do Backlog", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Por Tipo de Demanda**")
            if 'tipo' in df.columns:
                tipo_counts = df['tipo'].value_counts()
                fig = px.pie(values=tipo_counts.values, names=tipo_counts.index,
                            color_discrete_sequence=px.colors.qualitative.Set2)
                fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=250)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados de tipo")
        
        with col2:
            st.markdown("**Por Prioridade**")
            if 'prioridade' in df.columns:
                prio_counts = df['prioridade'].value_counts()
                cores_prio = {'Highest': '#ef4444', 'High': '#f97316', 'Medium': '#f59e0b', 
                             'Low': '#22c55e', 'Lowest': '#6b7280'}
                fig = px.pie(values=prio_counts.values, names=prio_counts.index,
                            color=prio_counts.index, 
                            color_discrete_map=cores_prio)
                fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=250)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados de prioridade")
