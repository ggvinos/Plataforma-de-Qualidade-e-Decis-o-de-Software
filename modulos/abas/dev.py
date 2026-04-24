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
from modulos.helpers import criar_card_metrica, get_tooltip_help
from modulos.utils import card_link_com_popup
from modulos.widgets import (
    mostrar_tooltip,
    exibir_concentracao_time,
    exibir_concentracao_simplificada,
)


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
        _renderizar_ranking_geral(df, devs)
    else:
        _renderizar_metricas_individuais(df, dev_sel)


def _renderizar_ranking_geral(df: pd.DataFrame, devs: list):
    """Renderiza a visão de ranking geral dos desenvolvedores."""
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
    
    # Análise para Tech Lead
    _renderizar_analise_tech_lead(df)
    
    # Cards Impedidos e Reprovados
    _renderizar_cards_impedidos_reprovados(df)


def _renderizar_analise_time(df: pd.DataFrame):
    """Renderiza análise geral do time de desenvolvimento."""
    with st.expander("📊 Análise do Time de Desenvolvimento", expanded=False):
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


def _renderizar_analise_tech_lead(df: pd.DataFrame):
    """Renderiza análise específica para Tech Lead."""
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


def _renderizar_cards_impedidos_reprovados(df: pd.DataFrame):
    """Renderiza seção de cards impedidos e reprovados."""
    cards_impedidos_dev = df[df['status_cat'] == 'blocked']
    cards_reprovados_dev = df[df['status_cat'] == 'rejected']
    
    if len(cards_impedidos_dev) > 0 or len(cards_reprovados_dev) > 0:
        with st.expander("🚨 Cards Impedidos e Reprovados", expanded=False):
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
    
    # Selo de Maturidade
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


def _renderizar_selo_maturidade(analise: dict, mat: dict):
    """Renderiza o selo de maturidade do desenvolvedor."""
    with st.expander(f"{mat['emoji']} Selo de Maturidade: {mat['selo']}", expanded=False):
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
    """Renderiza lista de cards do desenvolvedor."""
    with st.expander(f"📋 Cards", expanded=False):
        for _, row in analise['df'].iterrows():
            bugs_cor = '#ef4444' if row['bugs'] >= 2 else '#eab308' if row['bugs'] == 1 else '#22c55e'
            card_link = card_link_com_popup(row['ticket_id'])
            st.markdown(f"""
            <div style="padding: 10px; margin: 5px 0; border-left: 3px solid {bugs_cor}; background: rgba(100,100,100,0.05); border-radius: 4px;">
                <strong>{card_link}</strong> - {row['titulo'][:50]}...<br>
                <small style="color: #94a3b8;">🐛 {row['bugs']} bugs | 📊 {row['sp']} SP | 📍 {row['status']} | ⏱️ {row['lead_time']:.1f}d</small>
            </div>
            """, unsafe_allow_html=True)


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
