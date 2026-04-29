"""
================================================================================
ABA: DEV - NinaDash v8.82
================================================================================
Aba de Desenvolvimento - Performance, Ranking e Análise por Desenvolvedor.

Mostra:
- Ranking de performance (Fator K)
- Métricas individuais por desenvolvedor
- Concentração de conhecimento do time
- Análise para Tech Lead (WIP, Code Review, Velocidade)
- Cards impedidos/reprovados
- Resumo semanal por desenvolvedor

Dependências:
- modulos.config: STATUS_NOMES, STATUS_CORES, NINADASH_URL
- modulos.calculos: analisar_dev_detalhado, classificar_maturidade, etc
- modulos.helpers: criar_card_metrica, get_tooltip_help
- modulos.utils: card_link_com_popup
- modulos.widgets: mostrar_tooltip, exibir_concentracao_time, exibir_concentracao_simplificada
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import urllib.parse

from modulos.config import STATUS_NOMES, STATUS_CORES, NINADASH_URL
from modulos.calculos import (
    analisar_dev_detalhado,
    calcular_fator_k,
    classificar_maturidade,
)
from modulos.helpers import criar_card_metrica, get_tooltip_help, obter_contexto_periodo
from modulos.utils import card_link_com_popup
from modulos.widgets import (
    mostrar_tooltip,
    exibir_concentracao_time,
    exibir_concentracao_simplificada,
)


def aba_dev(df: pd.DataFrame):
    """Aba de Dev - Performance, Ranking e Análise por Desenvolvedor."""
    ctx = obter_contexto_periodo()
    
    st.markdown("### 👨‍💻 Painel de Desenvolvimento")
    st.caption(f"Performance individual, ranking e métricas de maturidade • **{ctx['emoji']} {ctx['titulo']}**")
    
    devs = [d for d in df['desenvolvedor'].unique() if d != 'Não atribuído']
    
    # Suporte a query params para compartilhamento (link compartilhado)
    dev_url = st.query_params.get("dev", None)
    opcoes_dev = ["🏆 Ranking Geral"] + sorted(devs)
    indice_inicial = 0
    if dev_url and dev_url in devs:
        indice_inicial = opcoes_dev.index(dev_url)
    
    # SELETOR DE DEV (NÃO atualiza query_params - apenas o botão Copiar Link faz isso)
    dev_sel = st.selectbox("👤 Selecione o Desenvolvedor", opcoes_dev, index=indice_inicial, key="select_dev")
    
    st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
    
    if dev_sel == "🏆 Ranking Geral":
        _renderizar_ranking_geral(df, devs)
    else:
        _renderizar_metricas_individuais(df, dev_sel)


def _renderizar_ranking_geral(df: pd.DataFrame, devs: list):
    """Renderiza a visão de ranking geral dos desenvolvedores."""
    
    # Helper para mini-cards compactos (para flexbox)
    def mini_card(valor, titulo, subtitulo, cor="#6b7280"):
        bg = f"{cor}10" if cor != "#6b7280" else "white"
        border = f"{cor}40" if cor != "#6b7280" else "#e5e7eb"
        return f'<div style="flex: 1; min-width: 0; background: {bg}; border: 1px solid {border}; border-radius: 8px; padding: 10px 8px; text-align: center; height: 72px; display: flex; flex-direction: column; justify-content: center;"><div style="font-size: 24px; font-weight: 700; color: {cor}; line-height: 1;">{valor}</div><div style="font-size: 11px; font-weight: 600; color: #374151; margin-top: 3px;">{titulo}</div><div style="font-size: 10px; color: #6b7280;">{subtitulo}</div></div>'
    
    def renderizar_linha(cards_html):
        return f'<div style="display: flex; gap: 8px; margin-bottom: 8px;">{"".join(cards_html)}</div>'
    
    def cor_status(valor, verde, amarelo):
        if valor < verde:
            return "#22c55e"
        elif valor < amarelo:
            return "#f59e0b"
        return "#ef4444"
    
    def cor_status_inv(valor, verde, amarelo):
        if valor >= verde:
            return "#22c55e"
        elif valor >= amarelo:
            return "#f59e0b"
        return "#ef4444"
    
    # ===== INDICADORES DE DESENVOLVIMENTO =====
    st.markdown("##### 📊 Indicadores de Desenvolvimento")
    
    # Métricas gerais
    total_cards = len(df[df['desenvolvedor'] != 'Não atribuído'])
    em_dev = len(df[df['status_cat'] == 'development'])
    em_cr = len(df[df['status_cat'] == 'code_review'])
    concluidos = len(df[df['status_cat'] == 'done'])
    bugs_total = int(df['bugs'].sum())
    sp_total = int(df['sp'].sum())
    fk_medio = sp_total / (bugs_total + 1) if bugs_total >= 0 else 0
    mat = classificar_maturidade(fk_medio)
    
    cards_linha1 = [
        mini_card(str(total_cards), "Total Cards", f"{sp_total} SP", "#3b82f6"),
        mini_card(str(em_dev), "🔧 Em Dev", "desenvolvimento", cor_status(em_dev, 10, 20)),
        mini_card(str(em_cr), "👀 Code Review", "aguardando CR", cor_status(em_cr, 5, 10)),
        mini_card(str(concluidos), "✅ Concluídos", "done", cor_status_inv(concluidos, 10, 5)),
        mini_card(f"{fk_medio:.1f}", f"Fator K {mat['emoji']}", mat['selo'], cor_status_inv(fk_medio, 3, 2)),
    ]
    st.markdown(renderizar_linha(cards_linha1), unsafe_allow_html=True)
    
    # Linha 2: Status de Cards
    cards_impedidos = df[df['status_cat'] == 'blocked']
    cards_reprovados = df[df['status_cat'] == 'rejected']
    sp_bloqueado = int(cards_impedidos['sp'].sum()) + int(cards_reprovados['sp'].sum())
    
    cards_linha2 = [
        mini_card(str(len(cards_impedidos)), "🚫 Impedidos", "bloqueados", cor_status(len(cards_impedidos), 1, 3)),
        mini_card(str(len(cards_reprovados)), "❌ Reprovados", "falha QA", cor_status(len(cards_reprovados), 1, 3)),
        mini_card(str(bugs_total), "🐛 Bugs", "total encontrados", cor_status(bugs_total, 10, 20)),
        mini_card(str(sp_bloqueado), "SP Travados", "imp. + repr.", cor_status(sp_bloqueado, 1, 10)),
    ]
    st.markdown(renderizar_linha(cards_linha2), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    
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
    with st.expander("🏆 Ranking de Performance", expanded=False):
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
    _renderizar_analise_time(df)
    
    # Code Reviews Pendentes
    _renderizar_code_reviews_pendentes(df)
    
    # Cards Impedidos e Reprovados
    _renderizar_cards_impedidos_reprovados(df)


def _renderizar_analise_time(df: pd.DataFrame):
    """Renderiza análise geral do time de desenvolvimento."""
    with st.expander("📊 Análise do Time de Desenvolvimento", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div style="font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 8px;">📋 Cards por Desenvolvedor</div>', unsafe_allow_html=True)
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
            st.markdown('<div style="font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 8px;">🐛 Taxa de Bugs por Card</div>', unsafe_allow_html=True)
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
                st.markdown('<div style="background: #F0FDF4; border-radius: 8px; padding: 16px; text-align: center;"><span style="font-size: 18px;">✅</span><div style="font-size: 13px; color: #166534; margin-top: 4px;">Sem bugs registrados!</div></div>', unsafe_allow_html=True)
        
        # Métricas gerais do time com novo design
        st.markdown('<div style="margin-top: 16px;"></div>', unsafe_allow_html=True)
        col3, col4, col5, col6 = st.columns(4)
        
        total_cards = len(df)
        em_andamento = len(df[df['status_cat'] == 'development'])
        total_bugs = int(df['bugs'].sum())
        media_bugs = total_bugs / len(df) if len(df) > 0 else 0
        cards_zero_bugs = len(df[df['bugs'] == 0])
        pct_zero_bugs = cards_zero_bugs / len(df) * 100 if len(df) > 0 else 0
        lead_medio = df['lead_time'].mean() if not df.empty else 0
        
        with col3:
            st.markdown(f'<div style="background: #3b82f610; border: 1px solid #3b82f640; border-radius: 8px; padding: 12px; text-align: center;"><div style="font-size: 22px; font-weight: 700; color: #3b82f6;">{total_cards}</div><div style="font-size: 12px; color: #374151; font-weight: 600;">Total Cards</div></div>', unsafe_allow_html=True)
        with col4:
            cor = "#f59e0b" if em_andamento > 15 else "#22c55e"
            st.markdown(f'<div style="background: {cor}10; border: 1px solid {cor}40; border-radius: 8px; padding: 12px; text-align: center;"><div style="font-size: 22px; font-weight: 700; color: {cor};">{em_andamento}</div><div style="font-size: 12px; color: #374151; font-weight: 600;">Em Desenvolvimento</div></div>', unsafe_allow_html=True)
        with col5:
            cor = "#22c55e" if pct_zero_bugs >= 70 else "#f59e0b" if pct_zero_bugs >= 50 else "#ef4444"
            st.markdown(f'<div style="background: {cor}10; border: 1px solid {cor}40; border-radius: 8px; padding: 12px; text-align: center;"><div style="font-size: 22px; font-weight: 700; color: {cor};">{pct_zero_bugs:.0f}%</div><div style="font-size: 12px; color: #374151; font-weight: 600;">Cards sem Bugs</div></div>', unsafe_allow_html=True)
        with col6:
            cor = "#22c55e" if lead_medio <= 7 else "#f59e0b" if lead_medio <= 14 else "#ef4444"
            st.markdown(f'<div style="background: {cor}10; border: 1px solid {cor}40; border-radius: 8px; padding: 12px; text-align: center;"><div style="font-size: 22px; font-weight: 700; color: {cor};">{lead_medio:.1f}d</div><div style="font-size: 12px; color: #374151; font-weight: 600;">Lead Time Médio</div></div>', unsafe_allow_html=True)


def _renderizar_code_reviews_pendentes(df: pd.DataFrame):
    """Renderiza seção de code reviews pendentes - relevante para devs."""
    code_review = df[df['status_cat'] == 'code_review']
    
    with st.expander(f"👀 Code Reviews Pendentes ({len(code_review)})", expanded=False):
        st.markdown('<div style="font-size: 13px; color: #6b7280; margin-bottom: 12px;">Cards aguardando revisão de código - ajude um colega!</div>', unsafe_allow_html=True)
        
        if not code_review.empty:
            # KPIs
            col1, col2, col3 = st.columns(3)
            cr_urgente = len(code_review[code_review['dias_em_status'] > 2])
            sp_em_cr = int(code_review['sp'].sum())
            
            with col1:
                cor = "#ef4444" if cr_urgente > 0 else "#22c55e"
                st.markdown(f'<div style="background: {cor}10; border: 1px solid {cor}40; border-radius: 8px; padding: 12px; text-align: center; margin-bottom: 12px;"><div style="font-size: 24px; font-weight: 700; color: {cor};">{len(code_review)}</div><div style="font-size: 13px; color: #374151; font-weight: 600;">Aguardando CR</div></div>', unsafe_allow_html=True)
            with col2:
                cor = "#ef4444" if cr_urgente > 2 else "#f59e0b" if cr_urgente > 0 else "#22c55e"
                st.markdown(f'<div style="background: {cor}10; border: 1px solid {cor}40; border-radius: 8px; padding: 12px; text-align: center; margin-bottom: 12px;"><div style="font-size: 24px; font-weight: 700; color: {cor};">{cr_urgente}</div><div style="font-size: 13px; color: #374151; font-weight: 600;">🔥 Urgentes (+2d)</div></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div style="background: #3b82f610; border: 1px solid #3b82f640; border-radius: 8px; padding: 12px; text-align: center; margin-bottom: 12px;"><div style="font-size: 24px; font-weight: 700; color: #3b82f6;">{sp_em_cr}</div><div style="font-size: 13px; color: #374151; font-weight: 600;">SP em Fila</div></div>', unsafe_allow_html=True)
            
            # Lista de cards
            st.markdown('<div style="font-size: 14px; font-weight: 600; color: #374151; margin: 12px 0 8px 0;">📋 Cards aguardando review:</div>', unsafe_allow_html=True)
            
            code_review_sorted = code_review.sort_values('dias_em_status', ascending=False)
            for _, row in code_review_sorted.head(8).iterrows():
                dias = row['dias_em_status']
                cor = '#ef4444' if dias > 2 else '#f59e0b' if dias > 1 else '#22c55e'
                urgente = "🔥 " if dias > 2 else ""
                ambiente = row.get('ambiente', '') if 'ambiente' in row.index else ''
                card_link = card_link_com_popup(row['ticket_id'], ambiente=ambiente)
                titulo = str(row['titulo'])[:50] + "..." if len(str(row['titulo'])) > 50 else str(row['titulo'])
                st.markdown(f'<div style="background: white; border-left: 3px solid {cor}; border-radius: 0 8px 8px 0; padding: 10px 12px; margin-bottom: 8px;"><div style="font-size: 13px; font-weight: 600; color: #374151;">{urgente}{card_link}</div><div style="font-size: 12px; color: #6b7280; margin-top: 4px;">{titulo}</div><div style="font-size: 11px; color: #9ca3af; margin-top: 6px;">👤 {row["desenvolvedor"]} · {row["sp"]} SP · <span style="color: {cor};">📅 {dias}d em CR</span></div></div>', unsafe_allow_html=True)
            
            if len(code_review) > 8:
                st.markdown(f'<div style="font-size: 12px; color: #9ca3af; margin-top: 8px;">... e mais {len(code_review) - 8} cards em Code Review</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background: #F0FDF4; border-radius: 8px; padding: 16px; text-align: center;"><span style="font-size: 18px;">✅</span><div style="font-size: 13px; color: #166534; margin-top: 4px;">Nenhum card aguardando Code Review!</div></div>', unsafe_allow_html=True)


def _renderizar_cards_impedidos_reprovados(df: pd.DataFrame):
    """Renderiza seção de cards impedidos e reprovados."""
    cards_impedidos_dev = df[df['status_cat'] == 'blocked']
    cards_reprovados_dev = df[df['status_cat'] == 'rejected']
    
    if len(cards_impedidos_dev) > 0 or len(cards_reprovados_dev) > 0:
        with st.expander("🚨 Cards Impedidos e Reprovados", expanded=False):
            # KPIs com novo design
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                cor = "#22c55e" if len(cards_impedidos_dev) == 0 else "#f59e0b" if len(cards_impedidos_dev) < 3 else "#ef4444"
                st.markdown(f'<div style="background: {cor}10; border: 1px solid {cor}40; border-radius: 8px; padding: 12px; text-align: center; margin-bottom: 12px;"><div style="font-size: 24px; font-weight: 700; color: {cor};">{len(cards_impedidos_dev)}</div><div style="font-size: 13px; color: #374151; font-weight: 600;">🚫 Impedidos</div></div>', unsafe_allow_html=True)
            
            with col2:
                cor = "#22c55e" if len(cards_reprovados_dev) == 0 else "#f59e0b" if len(cards_reprovados_dev) < 3 else "#ef4444"
                st.markdown(f'<div style="background: {cor}10; border: 1px solid {cor}40; border-radius: 8px; padding: 12px; text-align: center; margin-bottom: 12px;"><div style="font-size: 24px; font-weight: 700; color: {cor};">{len(cards_reprovados_dev)}</div><div style="font-size: 13px; color: #374151; font-weight: 600;">❌ Reprovados</div></div>', unsafe_allow_html=True)
            
            with col3:
                sp_impedido = int(cards_impedidos_dev['sp'].sum())
                cor = "#22c55e" if sp_impedido == 0 else "#f59e0b" if sp_impedido < 10 else "#ef4444"
                st.markdown(f'<div style="background: {cor}10; border: 1px solid {cor}40; border-radius: 8px; padding: 12px; text-align: center; margin-bottom: 12px;"><div style="font-size: 24px; font-weight: 700; color: {cor};">{sp_impedido}</div><div style="font-size: 13px; color: #374151; font-weight: 600;">SP Impedidos</div></div>', unsafe_allow_html=True)
            
            with col4:
                sp_reprovado = int(cards_reprovados_dev['sp'].sum())
                cor = "#22c55e" if sp_reprovado == 0 else "#f59e0b" if sp_reprovado < 10 else "#ef4444"
                st.markdown(f'<div style="background: {cor}10; border: 1px solid {cor}40; border-radius: 8px; padding: 12px; text-align: center; margin-bottom: 12px;"><div style="font-size: 24px; font-weight: 700; color: {cor};">{sp_reprovado}</div><div style="font-size: 13px; color: #374151; font-weight: 600;">SP Reprovados</div></div>', unsafe_allow_html=True)
            
            col_imp, col_rep = st.columns(2)
            
            with col_imp:
                st.markdown('<div style="font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 8px;">🚫 Cards Impedidos</div>', unsafe_allow_html=True)
                if not cards_impedidos_dev.empty:
                    html_imp_dev = '<div style="max-height: 350px; overflow-y: auto;">'
                    for _, row in cards_impedidos_dev.iterrows():
                        ambiente = row.get('ambiente', '') if 'ambiente' in row.index else ''
                        card_link = card_link_com_popup(row['ticket_id'], ambiente=ambiente)
                        titulo = str(row['titulo'])[:50] + "..." if len(str(row['titulo'])) > 50 else str(row['titulo'])
                        dev = str(row['desenvolvedor'])
                        qa = str(row['qa'])
                        sp = int(row['sp'])
                        html_imp_dev += f'<div style="background: #FEF2F2; border-left: 3px solid #EF4444; border-radius: 0 8px 8px 0; padding: 10px 12px; margin-bottom: 8px;">'
                        html_imp_dev += f'<div style="font-size: 13px; font-weight: 600; color: #374151;">{card_link}</div>'
                        html_imp_dev += f'<div style="font-size: 12px; color: #6b7280; margin-top: 4px;">{titulo}</div>'
                        html_imp_dev += f'<div style="font-size: 11px; color: #9ca3af; margin-top: 6px;">👤 {dev} · 🧑‍🔬 {qa} · {sp} SP</div>'
                        html_imp_dev += '</div>'
                    html_imp_dev += '</div>'
                    st.markdown(html_imp_dev, unsafe_allow_html=True)
                else:
                    st.markdown('<div style="background: #F0FDF4; border-radius: 8px; padding: 16px; text-align: center;"><span style="font-size: 18px;">✅</span><div style="font-size: 13px; color: #166534; margin-top: 4px;">Nenhum card impedido</div></div>', unsafe_allow_html=True)
            
            with col_rep:
                st.markdown('<div style="font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 8px;">❌ Cards Reprovados</div>', unsafe_allow_html=True)
                if not cards_reprovados_dev.empty:
                    html_rep_dev = '<div style="max-height: 350px; overflow-y: auto;">'
                    for _, row in cards_reprovados_dev.iterrows():
                        ambiente = row.get('ambiente', '') if 'ambiente' in row.index else ''
                        card_link = card_link_com_popup(row['ticket_id'], ambiente=ambiente)
                        titulo = str(row['titulo'])[:50] + "..." if len(str(row['titulo'])) > 50 else str(row['titulo'])
                        dev = str(row['desenvolvedor'])
                        qa = str(row['qa'])
                        sp = int(row['sp'])
                        bugs = int(row['bugs'])
                        html_rep_dev += f'<div style="background: #FEF2F2; border-left: 3px solid #DC2626; border-radius: 0 8px 8px 0; padding: 10px 12px; margin-bottom: 8px;">'
                        html_rep_dev += f'<div style="font-size: 13px; font-weight: 600; color: #374151;">{card_link}</div>'
                        html_rep_dev += f'<div style="font-size: 12px; color: #6b7280; margin-top: 4px;">{titulo}</div>'
                        html_rep_dev += f'<div style="font-size: 11px; color: #9ca3af; margin-top: 6px;">👤 {dev} · 🧑‍🔬 {qa} · {sp} SP · <span style="color: #EF4444;">🐛 {bugs}</span></div>'
                        html_rep_dev += '</div>'
                    html_rep_dev += '</div>'
                    st.markdown(html_rep_dev, unsafe_allow_html=True)
                else:
                    st.markdown('<div style="background: #F0FDF4; border-radius: 8px; padding: 16px; text-align: center;"><span style="font-size: 18px;">✅</span><div style="font-size: 13px; color: #166534; margin-top: 4px;">Nenhum card reprovado</div></div>', unsafe_allow_html=True)


def _renderizar_metricas_individuais(df: pd.DataFrame, dev_sel: str):
    """Renderiza métricas individuais de um desenvolvedor."""
    analise = analisar_dev_detalhado(df, dev_sel)
    
    if not analise:
        st.warning(f"Nenhum card encontrado para {dev_sel}")
        return
    
    # Header com título e botão de compartilhamento
    base_url = NINADASH_URL
    share_url = f"{base_url}?aba=dev&dev={urllib.parse.quote(dev_sel)}"
    
    col_titulo, col_share = st.columns([3, 1])
    with col_titulo:
        st.markdown(f"### 👤 Métricas de {dev_sel}")
    with col_share:
        # Botão Copiar Link usando components.html
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
    
    # Indicadores Individuais - Novo estilo harmonizado
    _renderizar_indicadores_individuais_dev(analise, mat)
    
    # Selo de Maturidade (agora em expander)
    _renderizar_selo_maturidade(analise, mat)
    
    # Áreas de Atuação
    exibir_concentracao_simplificada(df, dev_sel, "dev", expanded=False)
    
    # Resumo da Semana
    _renderizar_resumo_semana(analise, dev_sel)
    
    # Cards do dev
    _renderizar_cards_dev(analise)
    
    # Throughput e Produtividade
    _renderizar_throughput(analise)
    
    # Comparativo com o Time
    _renderizar_comparativo_time(df, analise)
    
    # Distribuição por Status
    _renderizar_distribuicao_status(analise)


def _renderizar_indicadores_individuais_dev(analise: dict, mat: dict):
    """Renderiza indicadores individuais do DEV - Estilo harmonizado."""
    
    # Helper para mini-cards compactos (para flexbox)
    def mini_card(valor, titulo, subtitulo, cor="#6b7280"):
        bg = f"{cor}10" if cor != "#6b7280" else "white"
        border = f"{cor}40" if cor != "#6b7280" else "#e5e7eb"
        return f'<div style="flex: 1; min-width: 0; background: {bg}; border: 1px solid {border}; border-radius: 8px; padding: 10px 8px; text-align: center; height: 72px; display: flex; flex-direction: column; justify-content: center;"><div style="font-size: 24px; font-weight: 700; color: {cor}; line-height: 1;">{valor}</div><div style="font-size: 11px; font-weight: 600; color: #374151; margin-top: 3px;">{titulo}</div><div style="font-size: 10px; color: #6b7280;">{subtitulo}</div></div>'
    
    def renderizar_linha(cards_html):
        return f'<div style="display: flex; gap: 8px; margin-bottom: 8px;">{"".join(cards_html)}</div>'
    
    def cor_status(valor, verde, amarelo):
        if valor < verde:
            return "#22c55e"
        elif valor < amarelo:
            return "#f59e0b"
        return "#ef4444"
    
    def cor_status_inv(valor, verde, amarelo):
        if valor >= verde:
            return "#22c55e"
        elif valor >= amarelo:
            return "#f59e0b"
        return "#ef4444"
    
    df_dev = analise['df']
    concluidos = len(df_dev[df_dev['status_cat'] == 'done'])
    
    # ===== LINHA 1: KPIs Principais =====
    st.markdown("##### 📊 Indicadores Individuais")
    
    cards_linha1 = [
        mini_card(str(analise['cards']), "Total Cards", f"{analise['sp_total']} SP", "#3b82f6"),
        mini_card(str(concluidos), "Concluídos", "validados", cor_status_inv(concluidos, 5, 2)),
        mini_card(str(analise['bugs_total']), "Bugs", "encontrados", cor_status(analise['bugs_total'], 3, 8)),
        mini_card(f"{analise['zero_bugs']}%", "Zero Bugs", "taxa FPY", cor_status_inv(analise['zero_bugs'], 80, 60)),
        mini_card(f"{analise['fk_medio']:.1f}", f"FK {mat['emoji']}", mat['selo'], cor_status_inv(analise['fk_medio'], 3, 2)),
    ]
    st.markdown(renderizar_linha(cards_linha1), unsafe_allow_html=True)
    
    # ===== LINHA 2: Status de Cards =====
    cards_impedidos = df_dev[df_dev['status_cat'] == 'blocked']
    cards_reprovados = df_dev[df_dev['status_cat'] == 'rejected']
    em_dev = len(df_dev[df_dev['status_cat'] == 'development'])
    em_cr = len(df_dev[df_dev['status_cat'] == 'code_review'])
    tempo = analise['tempo_medio'] if isinstance(analise['tempo_medio'], (int, float)) else 0
    cor_lt = "#22c55e" if tempo <= 3 else "#f59e0b" if tempo <= 7 else "#ef4444"
    
    cards_linha2 = [
        mini_card(str(em_dev), "🔧 Em Dev", "desenvolvimento", cor_status(em_dev, 3, 5)),
        mini_card(str(em_cr), "👀 Code Review", "aguardando", cor_status(em_cr, 2, 4)),
        mini_card(str(len(cards_impedidos)), "🚫 Impedidos", "bloqueados", cor_status(len(cards_impedidos), 1, 2)),
        mini_card(str(len(cards_reprovados)), "❌ Reprovados", "falha QA", cor_status(len(cards_reprovados), 1, 2)),
        mini_card(f"{tempo:.1f}d" if isinstance(tempo, float) else f"{tempo}d", "Lead Time", "médio", cor_lt),
    ]
    st.markdown(renderizar_linha(cards_linha2), unsafe_allow_html=True)
    
    # Cards com problemas em expander
    if len(cards_impedidos) > 0 or len(cards_reprovados) > 0:
        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        with st.expander(f"🚨 Cards com problemas ({len(cards_impedidos) + len(cards_reprovados)})", expanded=False):
            all_problemas = pd.concat([cards_impedidos, cards_reprovados]) if not cards_reprovados.empty and not cards_impedidos.empty else (cards_impedidos if not cards_impedidos.empty else cards_reprovados)
            for _, row in all_problemas.iterrows():
                status_icon = "🚫" if row['status_cat'] == 'blocked' else "❌"
                status_name = "Impedido" if row['status_cat'] == 'blocked' else "Reprovado"
                ambiente = row.get('ambiente', '') if 'ambiente' in row.index else ''
                card_link = card_link_com_popup(row['ticket_id'], ambiente=ambiente)
                st.markdown(f"""
                <div style="padding: 10px 12px; margin: 6px 0; border-left: 4px solid #ef4444; background: rgba(239, 68, 68, 0.08); border-radius: 6px;">
                    <strong>{status_icon}</strong> {card_link} - {row['titulo']}<br>
                    <small style="color: #6b7280;">🧑‍🔬 QA: {row['qa']} | {status_name} | {int(row['sp'])} SP</small>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)


def _renderizar_selo_maturidade(analise: dict, mat: dict):
    """Renderiza o selo de maturidade do desenvolvedor."""
    with st.expander(f"{mat['emoji']} Selo de Maturidade: {mat['selo']}", expanded=False):
        col1, col2 = st.columns([1, 2])
        
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
            st.markdown("""
            **Como é calculado o Fator K?**
            
            O Fator K mede a qualidade da entrega considerando esforço (SP) e bugs encontrados.
            
            **Fórmula:** `FK = SP / (Bugs + 1)`
            
            | Selo | Fator K | Classificação |
            |------|---------|---------------|
            | 🥇 Gold | ≥ 3.0 | Excelente |
            | 🥈 Silver | 2.0 - 2.9 | Bom |
            | 🥉 Bronze | 1.0 - 1.9 | Regular |
            | ⚠️ Risco | < 1.0 | Crítico |
            """)


def _renderizar_resumo_semana(analise: dict, dev_sel: str):
    """Renderiza o resumo semanal do desenvolvedor."""
    with st.expander("📅 Resumo da Semana", expanded=False):
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
        
        # KPIs da Semana - Harmonizados
        def mini_card_semana(valor, titulo, subtitulo, cor="#6b7280"):
            bg = cor + "10" if cor != "#6b7280" else "white"
            border = cor + "40" if cor != "#6b7280" else "#e5e7eb"
            return '<div style="background: ' + bg + '; border: 2px solid ' + border + '; border-radius: 12px; padding: 16px 12px; text-align: center; height: 95px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);"><div style="font-size: 28px; font-weight: 700; color: ' + cor + '; line-height: 1.1;">' + valor + '</div><div style="font-size: 12px; font-weight: 600; color: #374151; margin-top: 4px;">' + titulo + '</div><div style="font-size: 10px; color: #6b7280;">' + subtitulo + '</div></div>'
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(mini_card_semana(str(len(df_semana)), "📋 Trabalhados", semana_selecionada, "#3b82f6"), unsafe_allow_html=True)
        with col2:
            st.markdown(mini_card_semana(str(len(df_done_semana)), "✅ Concluídos", "entregues", "#22c55e"), unsafe_allow_html=True)
        with col3:
            bugs_semana = int(df_done_semana['bugs'].sum()) if not df_done_semana.empty else 0
            cor_bugs = '#22c55e' if bugs_semana == 0 else '#f59e0b' if bugs_semana < 3 else '#ef4444'
            st.markdown(mini_card_semana(str(bugs_semana), "🐛 Bugs", "pelo QA", cor_bugs), unsafe_allow_html=True)
        with col4:
            sp_semana = int(df_done_semana['sp'].sum()) if not df_done_semana.empty else 0
            st.markdown(mini_card_semana(str(sp_semana), "📐 SP", "entregues", "#22c55e"), unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        
        # Evolução da Semana
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
        
        # Resumo textual - PRIMEIRO na lista de expanders
        with st.expander("📝 Resumo para Daily/Retro", expanded=False):
            total_done = len(df_done_semana)
            total_sp = int(df_done_semana['sp'].sum()) if not df_done_semana.empty else 0
            total_bugs = int(df_done_semana['bugs'].sum()) if not df_done_semana.empty else 0
            clean_rate = len(df_done_semana[df_done_semana['bugs'] == 0]) / total_done * 100 if total_done > 0 else 0
            
            cards_lista = ""
            if not df_done_semana.empty:
                df_done_semana_sorted = df_done_semana.sort_values('resolutiondate' if 'resolutiondate' in df_done_semana.columns else 'atualizado', ascending=False)
                cards_lista = "\n".join([f"- {row['ticket_id']}: {row['titulo']}" for _, row in df_done_semana_sorted.iterrows()])
            
            resumo_texto = f"""📊 Resumo Semanal - {dev_sel}
📅 Período: {segunda_semana.strftime('%d/%m')} a {sexta_semana.strftime('%d/%m')}

• {total_done} cards entregues
• {total_sp} Story Points
• {total_bugs} bugs encontrados pelo QA
• {clean_rate:.0f}% taxa de entrega limpa

Cards concluídos:
{cards_lista if cards_lista else "Nenhum card concluído esta semana"}"""
            
            st.code(resumo_texto, language=None)
        
        # Cards Concluídos na Semana
        with st.expander(f"✅ Cards Concluídos na Semana ({len(df_done_semana)})", expanded=False):
            st.caption("Cards que você entregou esta semana")
            
            if not df_done_semana.empty:
                df_done_semana_sorted = df_done_semana.sort_values('resolutiondate' if 'resolutiondate' in df_done_semana.columns else 'atualizado', ascending=False)
                
                # Container com scroll
                cards_html = '<div style="max-height: 350px; overflow-y: auto; padding-right: 8px;">'
                
                jira_base = "https://ninatecnologia.atlassian.net/browse"
                
                for idx, (_, row) in enumerate(df_done_semana_sorted.head(20).iterrows()):
                    data_ref = row.get('resolutiondate') if pd.notna(row.get('resolutiondate')) else row.get('atualizado')
                    data_conclusao = data_ref.strftime("%d/%m %H:%M") if pd.notna(data_ref) else "N/A"
                    bugs = int(row['bugs'])
                    bugs_cor = '#16a34a' if bugs == 0 else '#d97706' if bugs == 1 else '#dc2626'
                    bugs_bg = '#f0fdf4' if bugs == 0 else '#fffbeb' if bugs == 1 else '#fef2f2'
                    ambiente = row.get('ambiente', '') if 'ambiente' in row.index else ''
                    ticket_id = row['ticket_id']
                    titulo = str(row['titulo'])[:55]
                    sp = str(int(row['sp']))
                    qa = str(row['qa'])
                    lead_time = str(round(row['lead_time'], 1))
                    projeto = row.get('projeto', 'SD')
                    
                    link_jira = f'{jira_base}/{ticket_id}'
                    link_nina = f'?card={ticket_id}&projeto={projeto}'
                    ticket_cor = "#8b5cf6" if projeto == "PB" else "#2563eb"
                    
                    badge_bugs = f'<span style="background:{bugs_bg};color:{bugs_cor};padding:3px 8px;border-radius:6px;font-size:10px;font-weight:600;">{"✅ Clean" if bugs == 0 else f"🐛 {bugs} bugs"}</span>'
                    
                    # Badge de ambiente
                    ambiente_badge = ''
                    if ambiente:
                        amb_lower = str(ambiente).lower()
                        if 'produção' in amb_lower or 'producao' in amb_lower:
                            ambiente_badge = '<span style="background:#fef2f2;color:#dc2626;padding:3px 8px;border-radius:6px;font-size:10px;font-weight:600;border:1px solid #fecaca;">🔴 PROD</span>'
                        elif 'homologação' in amb_lower or 'homologacao' in amb_lower:
                            ambiente_badge = '<span style="background:#fffbeb;color:#d97706;padding:3px 8px;border-radius:6px;font-size:10px;font-weight:600;border:1px solid #fde68a;">🟡 HML</span>'
                        elif 'develop' in amb_lower:
                            ambiente_badge = '<span style="background:#f0fdf4;color:#16a34a;padding:3px 8px;border-radius:6px;font-size:10px;font-weight:600;border:1px solid #bbf7d0;">🟢 DEV</span>'
                    
                    cards_html += f'''
<div style="padding:14px 16px;margin:10px 0;border-radius:10px;border-left:4px solid {bugs_cor};background:rgba(139,92,246,0.04);box-shadow:0 1px 3px rgba(0,0,0,0.08);transition:all 0.2s ease;" onmouseover="this.style.background='rgba(139,92,246,0.08)';this.style.boxShadow='0 4px 12px rgba(0,0,0,0.1)';this.style.transform='translateY(-1px)'" onmouseout="this.style.background='rgba(139,92,246,0.04)';this.style.boxShadow='0 1px 3px rgba(0,0,0,0.08)';this.style.transform='translateY(0)'">
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
        <div style="display:flex;align-items:center;gap:8px;">
            <span class="card-link-wrapper">
                <a href="{link_jira}" target="_blank" class="card-link-id" style="color:{ticket_cor};font-weight:700;font-size:13px;">{ticket_id}</a>
                <a href="{link_nina}" target="_blank" class="card-action-btn card-action-nina">📊 NinaDash</a>
            </span>
            {ambiente_badge}
            <span style="color:#64748b;font-size:13px;"> - {titulo}...</span>
        </div>
        <div style="display:flex;gap:8px;align-items:center;">
            {badge_bugs}
            <span style="background:#f5f3ff;color:#7c3aed;padding:3px 8px;border-radius:6px;font-size:10px;font-weight:600;">{sp} SP</span>
        </div>
    </div>
    <div style="margin-top:8px;font-size:12px;color:#64748b;display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
        <span>📅 {data_conclusao}</span>
        <span>👤 QA: {qa}</span>
        <span>⏱️ Lead Time: {lead_time}d</span>
    </div>
</div>'''
                
                cards_html += '</div>'
                st.markdown(cards_html, unsafe_allow_html=True)
                
                if len(df_done_semana_sorted) > 20:
                    st.caption(f"📋 Mostrando 20 de {len(df_done_semana_sorted)} cards")
            else:
                st.info("💡 Nenhum card foi concluído nesta semana.")
        
        # Tempo de Ciclo por Card
        if not df_done_semana.empty:
            with st.expander("⏱️ Tempo de Ciclo dos Cards da Semana", expanded=False):
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


def _renderizar_cards_dev(analise: dict):
    """Renderiza lista de cards do desenvolvedor com UI moderna."""
    with st.expander(f"📋 Cards", expanded=False):
        df_cards = analise['df']
        
        if not df_cards.empty:
            # Container com scroll
            cards_html = '<div style="max-height: 350px; overflow-y: auto; padding-right: 8px;">'
            
            jira_base = "https://ninatecnologia.atlassian.net/browse"
            
            for idx, (_, row) in enumerate(df_cards.head(30).iterrows()):
                bugs = int(row['bugs'])
                bugs_cor = '#dc2626' if bugs >= 2 else '#d97706' if bugs == 1 else '#16a34a'
                bugs_bg = '#fef2f2' if bugs >= 2 else '#fffbeb' if bugs == 1 else '#f0fdf4'
                ambiente = row.get('ambiente', '') if 'ambiente' in row.index else ''
                ticket_id = row['ticket_id']
                titulo = str(row['titulo'])[:55]
                sp = str(row['sp'])
                status = str(row['status'])[:20]
                lead_time = str(round(row['lead_time'], 1))
                projeto = row.get('projeto', 'SD')
                
                link_jira = f'{jira_base}/{ticket_id}'
                link_nina = f'?card={ticket_id}&projeto={projeto}'
                ticket_cor = "#8b5cf6" if projeto == "PB" else "#2563eb"
                
                # Badge de ambiente
                ambiente_badge = ''
                if ambiente:
                    amb_lower = str(ambiente).lower()
                    if 'produção' in amb_lower or 'producao' in amb_lower:
                        ambiente_badge = '<span style="background:#fef2f2;color:#dc2626;padding:3px 8px;border-radius:6px;font-size:10px;font-weight:600;border:1px solid #fecaca;">🔴 PROD</span>'
                    elif 'homologação' in amb_lower or 'homologacao' in amb_lower:
                        ambiente_badge = '<span style="background:#fffbeb;color:#d97706;padding:3px 8px;border-radius:6px;font-size:10px;font-weight:600;border:1px solid #fde68a;">🟡 HML</span>'
                    elif 'develop' in amb_lower:
                        ambiente_badge = '<span style="background:#f0fdf4;color:#16a34a;padding:3px 8px;border-radius:6px;font-size:10px;font-weight:600;border:1px solid #bbf7d0;">🟢 DEV</span>'
                
                cards_html += f'''
<div style="padding:14px 16px;margin:10px 0;border-radius:10px;border-left:4px solid {bugs_cor};background:rgba(248,250,252,0.8);box-shadow:0 1px 3px rgba(0,0,0,0.08);transition:all 0.2s ease;" onmouseover="this.style.background='rgba(241,245,249,1)';this.style.boxShadow='0 4px 12px rgba(0,0,0,0.1)';this.style.transform='translateY(-1px)'" onmouseout="this.style.background='rgba(248,250,252,0.8)';this.style.boxShadow='0 1px 3px rgba(0,0,0,0.08)';this.style.transform='translateY(0)'">
    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:8px;">
        <span class="card-link-wrapper">
            <a href="{link_jira}" target="_blank" class="card-link-id" style="color:{ticket_cor};font-weight:700;font-size:13px;">{ticket_id}</a>
            <a href="{link_nina}" target="_blank" class="card-action-btn card-action-nina">📊 NinaDash</a>
        </span>
        {ambiente_badge}
        <span style="color:#64748b;font-size:13px;flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"> - {titulo}...</span>
    </div>
    <div style="display:flex;align-items:center;gap:12px;font-size:12px;color:#64748b;flex-wrap:wrap;">
        <span style="background:{bugs_bg};color:{bugs_cor};padding:3px 8px;border-radius:6px;font-weight:600;">🐛 {bugs} bugs</span>
        <span style="background:#f5f3ff;color:#7c3aed;padding:3px 8px;border-radius:6px;font-weight:500;">📊 {sp} SP</span>
        <span style="background:#f1f5f9;color:#475569;padding:3px 8px;border-radius:6px;font-weight:500;">📍 {status}</span>
        <span>⏱️ {lead_time}d</span>
    </div>
</div>'''
            
            cards_html += '</div>'
            st.markdown(cards_html, unsafe_allow_html=True)
            
            if len(df_cards) > 30:
                st.caption(f"📋 Mostrando 30 de {len(df_cards)} cards")
        else:
            st.info("Nenhum card atribuído")


def _renderizar_throughput(analise: dict):
    """Renderiza métricas de throughput e produtividade."""
    with st.expander("📈 Throughput e Produtividade", expanded=False):
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


def _renderizar_comparativo_time(df: pd.DataFrame, analise: dict):
    """Renderiza comparativo com a média do time."""
    with st.expander("📊 Comparativo com o Time", expanded=False):
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


def _renderizar_distribuicao_status(analise: dict):
    """Renderiza distribuição por status."""
    with st.expander("📊 Distribuição por Status", expanded=False):
        status_count = analise['df']['status_cat'].value_counts().reset_index()
        status_count.columns = ['Status', 'Cards']
        status_count['Status'] = status_count['Status'].map(lambda x: STATUS_NOMES.get(x, x))
        
        if not status_count.empty:
            fig = px.pie(status_count, values='Cards', names='Status', hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
