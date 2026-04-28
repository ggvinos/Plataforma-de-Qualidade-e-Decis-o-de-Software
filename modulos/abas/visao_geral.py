"""
================================================================================
ABA: VISÃO GERAL - NinaDash v8.82
================================================================================
Aba principal com visão geral da sprint.

Mostra:
- Header com sprint ativa e dias até release
- Alertas de governança (SP preenchido)
- KPIs principais: Total, SP, Concluído, Bugs, Dias até Release
- Barra de progresso visual da sprint
- Métricas técnicas de qualidade (FPY, DDP, Lead Time, Health Score, FK)
- Cards por status agrupados
- Análise de sprint (planejamento vs entrega)
- Gráficos de distribuição

Dependências:
- modulos.config: STATUS_NOMES, STATUS_CORES
- modulos.calculos: várias funções de cálculo
- modulos.helpers: criar_card_metrica
- modulos.utils: card_link_com_popup
- modulos.widgets: mostrar_tooltip, mostrar_lista_df_completa
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

from modulos.config import STATUS_NOMES, STATUS_CORES
from modulos.calculos import (
    calcular_metricas_governanca,
    calcular_fpy,
    calcular_ddp,
    calcular_lead_time,
    calcular_health_score,
    calcular_fator_k,
    classificar_maturidade,
)
from modulos.helpers import criar_card_metrica
from modulos.utils import card_link_com_popup
from modulos.widgets import mostrar_tooltip, mostrar_lista_df_completa


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
            # Verifica se precisa virar sprint no Jira
            precisa_virar_sprint = False
            if 'sprint_state' in df.columns:
                df_future = df[df['sprint_state'] == 'future']
                if not df_future.empty and 'sprint_start' in df_future.columns:
                    for _, row in df_future.iterrows():
                        future_start = row.get('sprint_start')
                        if future_start is not None:
                            try:
                                if isinstance(future_start, str):
                                    future_start = datetime.fromisoformat(future_start.replace('Z', '+00:00')).replace(tzinfo=None)
                                if future_start <= hoje:
                                    precisa_virar_sprint = True
                                    break
                            except:
                                pass
            
            if precisa_virar_sprint:
                release_info = "⚠️ VIRAR SPRINT NO JIRA"
            else:
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
    with st.expander("📋 Cards por Status", expanded=False):
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
                        
                        ambiente = card.get('ambiente', '')
                        card_link = card_link_com_popup(card['ticket_id'], ambiente=ambiente)
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
