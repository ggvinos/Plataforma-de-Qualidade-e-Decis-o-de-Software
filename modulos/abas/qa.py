"""
================================================================================
ABA: QA - NinaDash v8.82
================================================================================
Aba de QA - Análise de validação, gargalos e comparativo entre QAs.

Mostra:
- KPIs de validação (fila, taxa reprovação, DDP)
- Cards impedidos e reprovados
- Funil de validação e carga por QA
- Concentração de conhecimento
- Comparativo entre QAs
- Interação QA x DEV
- Análise de bugs e retrabalho
- Janela de validação (risco)
- Cards envelhecidos
- Métricas individuais por QA

Dependências:
- modulos.config: STATUS_NOMES, STATUS_CORES, NINADASH_URL, REGRAS
- modulos.calculos: calcular_metricas_qa, calcular_ddp, calcular_fpy, calcular_lead_time
- modulos.helpers: criar_card_metrica, get_tooltip_help, formatar_tempo_relativo
- modulos.graficos: criar_grafico_funil_qa
- modulos.utils: card_link_com_popup
- modulos.widgets: mostrar_tooltip, exibir_concentracao_time, exibir_concentracao_simplificada, mostrar_lista_df_completa
- modulos._abas_legacy: exibir_historico_validacoes
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import urllib.parse

from modulos.config import STATUS_NOMES, STATUS_CORES, NINADASH_URL, REGRAS
from modulos.calculos import (
    calcular_metricas_qa,
    calcular_ddp,
    calcular_fpy,
    calcular_lead_time,
)
from modulos.helpers import criar_card_metrica, get_tooltip_help, formatar_tempo_relativo, obter_contexto_periodo
from modulos.graficos import criar_grafico_funil_qa
from modulos.utils import card_link_com_popup
from modulos.widgets import (
    mostrar_tooltip,
    exibir_concentracao_time,
    exibir_concentracao_simplificada,
    mostrar_lista_df_completa,
)
from modulos._abas_legacy import exibir_historico_validacoes


def aba_qa(df: pd.DataFrame):
    """Aba de QA (análise de validação, gargalos e comparativo entre QAs)."""
    ctx = obter_contexto_periodo()
    
    st.markdown("### 🔬 Análise de QA")
    st.caption(f"Monitore o funil de validação, identifique gargalos e compare a performance dos QAs • **{ctx['emoji']} {ctx['titulo']}**")
    
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
    
    st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
    
    if qa_sel == "👀 Visão Geral do Time":
        _renderizar_visao_geral_time(df, metricas_qa, qas)
    else:
        _renderizar_metricas_individuais(df, qa_sel)


# =============================================================================
# VISÃO GERAL DO TIME
# =============================================================================

def _renderizar_visao_geral_time(df: pd.DataFrame, metricas_qa: dict, qas: list):
    """Renderiza a visão geral do time de QA."""
    # KPIs de QA
    _renderizar_kpis_qa(df, metricas_qa)
    
    # Cards Impedidos/Reprovados
    _renderizar_cards_impedidos_reprovados(df)
    
    # Funil e Carga
    _renderizar_funil_e_carga(metricas_qa)
    
    # Concentração de Conhecimento do Time QA
    exibir_concentracao_time(df, "qa")
    
    # Comparativo entre QAs
    _renderizar_comparativo_qas(df, qas)
    
    # Interação QA x DEV
    _renderizar_interacao_qa_dev(df)
    
    # Análise de Bugs
    _renderizar_analise_bugs(df)
    
    # Janela de Validação
    _renderizar_janela_validacao(df)
    
    # Cards Aging
    _renderizar_cards_aging(metricas_qa)
    
    # Filas
    _renderizar_filas(df)
    
    # Histórico de Validações
    with st.expander("✅ Histórico de Cards Validados", expanded=False):
        exibir_historico_validacoes(df, key_prefix="qa_geral")


def _renderizar_kpis_qa(df: pd.DataFrame, metricas_qa: dict):
    """Renderiza os KPIs principais de QA - Estilo harmonizado."""
    
    # Helper para criar mini-cards harmonizados
    def mini_card(valor, titulo, subtitulo, cor="#6b7280"):
        bg = f"{cor}10" if cor != "#6b7280" else "white"
        border = f"{cor}40" if cor != "#6b7280" else "#e5e7eb"
        return f'<div style="background: {bg}; border: 2px solid {border}; border-radius: 12px; padding: 16px 12px; text-align: center; height: 95px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);"><div style="font-size: 28px; font-weight: 700; color: {cor}; line-height: 1.1;">{valor}</div><div style="font-size: 12px; font-weight: 600; color: #374151; margin-top: 4px;">{titulo}</div><div style="font-size: 10px; color: #6b7280;">{subtitulo}</div></div>'
    
    # Cores do sistema
    def cor_status(valor, verde, amarelo):
        """Retorna cor baseado em thresholds (verde se < verde, amarelo se < amarelo, vermelho se >=)"""
        if valor < verde:
            return "#22c55e"
        elif valor < amarelo:
            return "#f59e0b"
        return "#ef4444"
    
    def cor_status_inv(valor, verde, amarelo):
        """Inverso - verde se >= verde, amarelo se >= amarelo"""
        if valor >= verde:
            return "#22c55e"
        elif valor >= amarelo:
            return "#f59e0b"
        return "#ef4444"
    
    # ===== LINHA 1: KPIs Principais =====
    st.markdown("##### 📊 Indicadores de QA")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_fila = metricas_qa['funil']['waiting_qa'] + metricas_qa['funil']['testing']
        cor = cor_status(total_fila, 5, 10)
        st.markdown(mini_card(str(total_fila), "Fila de QA", f"{metricas_qa['funil']['waiting_qa']} aguardando", cor), unsafe_allow_html=True)
    
    with col2:
        tempo = metricas_qa['tempo']['waiting']
        cor = cor_status(tempo, 2, 5)
        st.markdown(mini_card(f"{tempo:.1f}d", "Tempo Médio", "na fila", cor), unsafe_allow_html=True)
    
    with col3:
        aging = metricas_qa['aging']['total']
        cor = cor_status(aging, 1, 3)
        st.markdown(mini_card(str(aging), "Aging", f">{REGRAS['dias_aging_alerta']}d", cor), unsafe_allow_html=True)
    
    with col4:
        taxa = metricas_qa['taxa_reprovacao']
        cor = cor_status(taxa, 10, 20)
        st.markdown(mini_card(f"{taxa:.0f}%", "Reprovação", "taxa", cor), unsafe_allow_html=True)
    
    with col5:
        ddp = calcular_ddp(df)
        cor = cor_status_inv(ddp['valor'], 85, 70)
        st.markdown(mini_card(f"{ddp['valor']:.0f}%", "DDP", "detecção defeitos", cor), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
    
    # ===== LINHA 2: Status de Cards =====
    cards_impedidos = df[df['status_cat'] == 'blocked']
    cards_reprovados = df[df['status_cat'] == 'rejected']
    total_validados = len(df[df['status_cat'] == 'done'])
    total_com_bugs = len(df[(df['status_cat'] == 'done') & (df['bugs'] > 0)])
    bug_rate = total_com_bugs / total_validados * 100 if total_validados > 0 else 0
    sp_bloqueado = int(cards_impedidos['sp'].sum()) + int(cards_reprovados['sp'].sum())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cor = cor_status(len(cards_impedidos), 1, 3)
        st.markdown(mini_card(str(len(cards_impedidos)), "🚫 Impedidos", "bloqueados", cor), unsafe_allow_html=True)
    
    with col2:
        cor = cor_status(len(cards_reprovados), 1, 3)
        st.markdown(mini_card(str(len(cards_reprovados)), "❌ Reprovados", "falha validação", cor), unsafe_allow_html=True)
    
    with col3:
        cor = cor_status(bug_rate, 20, 40)
        st.markdown(mini_card(f"{bug_rate:.0f}%", "Bug Rate", f"{total_com_bugs} com bugs", cor), unsafe_allow_html=True)
    
    with col4:
        cor = cor_status(sp_bloqueado, 1, 10)
        st.markdown(mini_card(str(sp_bloqueado), "SP Travados", "imp. + repr.", cor), unsafe_allow_html=True)
    
    # Espaçamento antes da próxima seção
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)


def _renderizar_cards_impedidos_reprovados(df: pd.DataFrame):
    """Renderiza a seção de cards impedidos e reprovados."""
    cards_impedidos = df[df['status_cat'] == 'blocked']
    cards_reprovados = df[df['status_cat'] == 'rejected']
    
    if len(cards_impedidos) > 0 or len(cards_reprovados) > 0:
        with st.expander("🚨 Cards Impedidos e Reprovados", expanded=False):
            # KPIs no topo
            col_kpi1, col_kpi2 = st.columns(2)
            with col_kpi1:
                cor = "#ef4444" if len(cards_impedidos) > 0 else "#22c55e"
                st.markdown(f'<div style="background: {cor}10; border: 1px solid {cor}40; border-radius: 8px; padding: 12px; text-align: center; margin-bottom: 12px;"><div style="font-size: 24px; font-weight: 700; color: {cor};">{len(cards_impedidos)}</div><div style="font-size: 13px; color: #374151; font-weight: 600;">🚫 Impedidos</div></div>', unsafe_allow_html=True)
            with col_kpi2:
                cor = "#ef4444" if len(cards_reprovados) > 0 else "#22c55e"
                st.markdown(f'<div style="background: {cor}10; border: 1px solid {cor}40; border-radius: 8px; padding: 12px; text-align: center; margin-bottom: 12px;"><div style="font-size: 24px; font-weight: 700; color: {cor};">{len(cards_reprovados)}</div><div style="font-size: 13px; color: #374151; font-weight: 600;">❌ Reprovados</div></div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div style="font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 8px;">🚫 Cards Impedidos</div>', unsafe_allow_html=True)
                if not cards_impedidos.empty:
                    html_impedidos = '<div style="max-height: 350px; overflow-y: auto;">'
                    for _, row in cards_impedidos.iterrows():
                        card_link = card_link_com_popup(row['ticket_id'])
                        titulo = str(row['titulo'])[:50] + "..." if len(str(row['titulo'])) > 50 else str(row['titulo'])
                        dev = str(row['desenvolvedor'])
                        qa = str(row['qa'])
                        sp = int(row['sp'])
                        html_impedidos += f'<div style="background: #FEF2F2; border-left: 3px solid #EF4444; border-radius: 0 8px 8px 0; padding: 10px 12px; margin-bottom: 8px;">'
                        html_impedidos += f'<div style="font-size: 13px; font-weight: 600; color: #374151;">{card_link}</div>'
                        html_impedidos += f'<div style="font-size: 12px; color: #6b7280; margin-top: 4px;">{titulo}</div>'
                        html_impedidos += f'<div style="font-size: 11px; color: #9ca3af; margin-top: 6px;">👤 {dev} · 🧑‍🔬 {qa} · {sp} SP</div>'
                        html_impedidos += '</div>'
                    html_impedidos += '</div>'
                    st.markdown(html_impedidos, unsafe_allow_html=True)
                else:
                    st.markdown('<div style="background: #F0FDF4; border-radius: 8px; padding: 16px; text-align: center;"><span style="font-size: 18px;">✅</span><div style="font-size: 13px; color: #166534; margin-top: 4px;">Nenhum card impedido</div></div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div style="font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 8px;">❌ Cards Reprovados</div>', unsafe_allow_html=True)
                if not cards_reprovados.empty:
                    html_reprovados = '<div style="max-height: 350px; overflow-y: auto;">'
                    for _, row in cards_reprovados.iterrows():
                        card_link = card_link_com_popup(row['ticket_id'])
                        titulo = str(row['titulo'])[:50] + "..." if len(str(row['titulo'])) > 50 else str(row['titulo'])
                        dev = str(row['desenvolvedor'])
                        qa = str(row['qa'])
                        sp = int(row['sp'])
                        bugs = int(row['bugs'])
                        html_reprovados += f'<div style="background: #FEF2F2; border-left: 3px solid #DC2626; border-radius: 0 8px 8px 0; padding: 10px 12px; margin-bottom: 8px;">'
                        html_reprovados += f'<div style="font-size: 13px; font-weight: 600; color: #374151;">{card_link}</div>'
                        html_reprovados += f'<div style="font-size: 12px; color: #6b7280; margin-top: 4px;">{titulo}</div>'
                        html_reprovados += f'<div style="font-size: 11px; color: #9ca3af; margin-top: 6px;">👤 {dev} · 🧑‍🔬 {qa} · {sp} SP · <span style="color: #EF4444;">🐛 {bugs}</span></div>'
                        html_reprovados += '</div>'
                    html_reprovados += '</div>'
                    st.markdown(html_reprovados, unsafe_allow_html=True)
                else:
                    st.markdown('<div style="background: #F0FDF4; border-radius: 8px; padding: 16px; text-align: center;"><span style="font-size: 18px;">✅</span><div style="font-size: 13px; color: #166534; margin-top: 4px;">Nenhum card reprovado</div></div>', unsafe_allow_html=True)


def _renderizar_funil_e_carga(metricas_qa: dict):
    """Renderiza o funil de validação e carga por QA."""
    with st.expander("📈 Funil de Validação e Carga por QA", expanded=False):
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


def _renderizar_comparativo_qas(df: pd.DataFrame, qas: list):
    """Renderiza o comparativo entre QAs."""
    with st.expander("📊 Comparativo de Performance entre QAs", expanded=False):
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


def _renderizar_interacao_qa_dev(df: pd.DataFrame):
    """Renderiza a seção de interação QA x DEV."""
    with st.expander("🤝 Interação QA x DEV", expanded=False):
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


def _renderizar_analise_bugs(df: pd.DataFrame):
    """Renderiza a análise de bugs e retrabalho."""
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


def _renderizar_janela_validacao(df: pd.DataFrame):
    """Renderiza a janela de validação (análise de risco)."""
    with st.expander("🕐 Janela de Validação (Análise de Risco)", expanded=False):
        # Info box com novo design
        st.markdown('''
        <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 8px; padding: 14px 16px; margin-bottom: 16px;">
            <div style="font-size: 14px; font-weight: 600; color: #1E40AF; margin-bottom: 8px;">📋 Regras de Janela de Validação</div>
            <div style="font-size: 13px; color: #374151; line-height: 1.6;">A janela considera a <b>complexidade de teste</b> do card para determinar se há tempo suficiente:</div>
            <div style="display: flex; gap: 16px; margin-top: 10px;">
                <div style="background: white; border-radius: 6px; padding: 8px 12px; flex: 1; text-align: center;">
                    <div style="font-size: 12px; color: #EF4444; font-weight: 600;">🔴 Alta</div>
                    <div style="font-size: 11px; color: #6b7280;">3+ dias</div>
                </div>
                <div style="background: white; border-radius: 6px; padding: 8px 12px; flex: 1; text-align: center;">
                    <div style="font-size: 12px; color: #F59E0B; font-weight: 600;">🟡 Média</div>
                    <div style="font-size: 11px; color: #6b7280;">2 dias</div>
                </div>
                <div style="background: white; border-radius: 6px; padding: 8px 12px; flex: 1; text-align: center;">
                    <div style="font-size: 12px; color: #22C55E; font-weight: 600;">🟢 Baixa</div>
                    <div style="font-size: 11px; color: #6b7280;">1 dia</div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        cards_qa = df[df['status_cat'].isin(['waiting_qa', 'testing'])]
        
        if not cards_qa.empty:
            fora_janela = cards_qa[cards_qa['janela_status'] == 'fora']
            em_risco = cards_qa[cards_qa['janela_status'] == 'risco']
            dentro_janela = cards_qa[cards_qa['janela_status'] == 'ok']
            
            # KPIs com novo design
            col1, col2, col3 = st.columns(3)
            with col1:
                cor = "#EF4444" if len(fora_janela) > 0 else "#22C55E"
                st.markdown(f'<div style="background: {cor}10; border: 1px solid {cor}40; border-radius: 8px; padding: 12px; text-align: center; margin-bottom: 12px;"><div style="font-size: 24px; font-weight: 700; color: {cor};">{len(fora_janela)}</div><div style="font-size: 13px; color: #374151; font-weight: 600;">🚨 Fora da Janela</div></div>', unsafe_allow_html=True)
            with col2:
                cor = "#F59E0B" if len(em_risco) > 0 else "#22C55E"
                st.markdown(f'<div style="background: {cor}10; border: 1px solid {cor}40; border-radius: 8px; padding: 12px; text-align: center; margin-bottom: 12px;"><div style="font-size: 24px; font-weight: 700; color: {cor};">{len(em_risco)}</div><div style="font-size: 13px; color: #374151; font-weight: 600;">⚠️ Em Risco</div></div>', unsafe_allow_html=True)
            with col3:
                cor = "#22C55E"
                st.markdown(f'<div style="background: {cor}10; border: 1px solid {cor}40; border-radius: 8px; padding: 12px; text-align: center; margin-bottom: 12px;"><div style="font-size: 24px; font-weight: 700; color: {cor};">{len(dentro_janela)}</div><div style="font-size: 13px; color: #374151; font-weight: 600;">✅ Dentro da Janela</div></div>', unsafe_allow_html=True)
            
            if not fora_janela.empty:
                st.markdown('<div style="font-size: 14px; font-weight: 600; color: #374151; margin: 16px 0 8px 0;">🚨 Cards FORA da Janela</div>', unsafe_allow_html=True)
                df_fora = fora_janela[['ticket_id', 'titulo', 'complexidade', 'dias_ate_release', 'desenvolvedor', 'sp']].copy()
                df_fora.columns = ['Ticket', 'Título', 'Complexidade', 'Dias Disponíveis', 'Dev', 'SP']
                st.dataframe(df_fora, hide_index=True, use_container_width=True)
        else:
            st.markdown('<div style="background: #F0FDF4; border-radius: 8px; padding: 16px; text-align: center;"><span style="font-size: 18px;">✅</span><div style="font-size: 13px; color: #166534; margin-top: 4px;">Nenhum card aguardando validação!</div></div>', unsafe_allow_html=True)


def _renderizar_cards_aging(metricas_qa: dict):
    """Renderiza cards envelhecidos (aging)."""
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


def _renderizar_filas(df: pd.DataFrame):
    """Renderiza as filas de validação."""
    with st.expander("📋 Fila - Aguardando Validação", expanded=False):
        fila_qa = df[df['status_cat'] == 'waiting_qa'].sort_values('dias_em_status', ascending=False)
        mostrar_lista_df_completa(fila_qa, "Aguardando QA")
    
    with st.expander("🧪 Em Validação", expanded=False):
        em_teste = df[df['status_cat'] == 'testing'].sort_values('dias_em_status', ascending=False)
        mostrar_lista_df_completa(em_teste, "Em Validação")


# =============================================================================
# MÉTRICAS INDIVIDUAIS
# =============================================================================

def _renderizar_metricas_individuais(df: pd.DataFrame, qa_sel: str):
    """Renderiza métricas individuais do QA selecionado."""
    df_qa = df[df['qa'] == qa_sel]
    
    if df_qa.empty:
        st.warning(f"Nenhum card atribuído para {qa_sel}")
        return
    
    # Header com título e botão de compartilhamento
    base_url = NINADASH_URL
    share_url = f"{base_url}?aba=qa&qa={urllib.parse.quote(qa_sel)}"
    
    col_titulo, col_share = st.columns([3, 1])
    with col_titulo:
        st.markdown(f"### 👤 Métricas de {qa_sel}")
    with col_share:
        # Botão Copiar Link
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
    _renderizar_kpis_individuais(df, df_qa, qa_sel)
    
    # Áreas de Atuação
    exibir_concentracao_simplificada(df, qa_sel, "qa", expanded=False)
    
    # Resumo da Semana
    _renderizar_resumo_semana_qa(df_qa, qa_sel)
    
    # Distribuição por Status
    _renderizar_distribuicao_status_qa(df_qa)
    
    # Bugs por Desenvolvedor
    _renderizar_bugs_por_dev(df_qa)
    
    # Cards em Fila
    _renderizar_cards_fila_qa(df_qa)
    
    # Throughput e Eficiência
    _renderizar_throughput_qa(df_qa, qa_sel)
    
    # Comparativo com o Time
    _renderizar_comparativo_time_qa(df, df_qa)
    
    # Distribuição de Complexidade
    _renderizar_distribuicao_complexidade(df_qa)
    
    # Cards Validados
    _renderizar_cards_validados_qa(df_qa)


def _renderizar_kpis_individuais(df: pd.DataFrame, df_qa: pd.DataFrame, qa_sel: str):
    """Renderiza KPIs individuais do QA - Estilo harmonizado."""
    
    # Helper para criar mini-cards harmonizados
    def mini_card(valor, titulo, subtitulo, cor="#6b7280"):
        bg = f"{cor}10" if cor != "#6b7280" else "white"
        border = f"{cor}40" if cor != "#6b7280" else "#e5e7eb"
        return f'<div style="background: {bg}; border: 2px solid {border}; border-radius: 12px; padding: 16px 12px; text-align: center; height: 95px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);"><div style="font-size: 28px; font-weight: 700; color: {cor}; line-height: 1.1;">{valor}</div><div style="font-size: 12px; font-weight: 600; color: #374151; margin-top: 4px;">{titulo}</div><div style="font-size: 10px; color: #6b7280;">{subtitulo}</div></div>'
    
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
    
    # Cálculos
    validados = len(df_qa[df_qa['status_cat'] == 'done'])
    em_fila = len(df_qa[df_qa['status_cat'].isin(['waiting_qa', 'testing'])])
    bugs_encontrados = int(df_qa['bugs'].sum())
    cards_sem_bugs = len(df_qa[(df_qa['status_cat'] == 'done') & (df_qa['bugs'] == 0)])
    fpy_val = cards_sem_bugs / validados * 100 if validados > 0 else 0
    sp_total = int(df_qa['sp'].sum())
    lead_time_medio = df_qa['lead_time'].mean() if not df_qa.empty else 0
    aging_qa = len(df_qa[df_qa['dias_em_status'] > REGRAS['dias_aging_alerta']])
    
    # ===== LINHA 1: KPIs Principais =====
    st.markdown("##### 📊 Indicadores Individuais")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(mini_card(str(len(df_qa)), "Total Cards", f"{sp_total} SP", "#3b82f6"), unsafe_allow_html=True)
    
    with col2:
        cor = cor_status_inv(validados, 5, 2)
        st.markdown(mini_card(str(validados), "Validados", "concluídos", cor), unsafe_allow_html=True)
    
    with col3:
        cor = cor_status(em_fila, 3, 6)
        st.markdown(mini_card(str(em_fila), "Em Fila", "aguardando", cor), unsafe_allow_html=True)
    
    with col4:
        st.markdown(mini_card(str(bugs_encontrados), "Bugs", "encontrados", "#8b5cf6"), unsafe_allow_html=True)
    
    with col5:
        cor = cor_status_inv(fpy_val, 80, 60)
        st.markdown(mini_card(f"{fpy_val:.0f}%", "FPY", "first pass yield", cor), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
    
    # ===== LINHA 2: Métricas Secundárias =====
    cards_impedidos_qa = df_qa[df_qa['status_cat'] == 'blocked']
    cards_reprovados_qa = df_qa[df_qa['status_cat'] == 'rejected']
    sp_travado = int(cards_impedidos_qa['sp'].sum()) + int(cards_reprovados_qa['sp'].sum())
    em_validacao = len(df_qa[df_qa['status_cat'] == 'testing'])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        cor = "#22c55e" if lead_time_medio <= 3 else "#f59e0b" if lead_time_medio <= 7 else "#ef4444"
        st.markdown(mini_card(f"{lead_time_medio:.1f}d", "Lead Time", "médio", cor), unsafe_allow_html=True)
    
    with col2:
        cor = cor_status(aging_qa, 1, 3)
        st.markdown(mini_card(str(aging_qa), "Aging", f">{REGRAS['dias_aging_alerta']}d", cor), unsafe_allow_html=True)
    
    with col3:
        cor = cor_status(len(cards_impedidos_qa), 1, 2)
        st.markdown(mini_card(str(len(cards_impedidos_qa)), "🚫 Impedidos", "bloqueados", cor), unsafe_allow_html=True)
    
    with col4:
        cor = cor_status(len(cards_reprovados_qa), 1, 2)
        st.markdown(mini_card(str(len(cards_reprovados_qa)), "❌ Reprovados", "falha", cor), unsafe_allow_html=True)
    
    with col5:
        st.markdown(mini_card(str(em_validacao), "🧪 Validando", "em teste", "#3b82f6"), unsafe_allow_html=True)
    
    # Lista cards impedidos/reprovados se existirem
    if len(cards_impedidos_qa) > 0 or len(cards_reprovados_qa) > 0:
        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        with st.expander(f"🚨 Cards com problemas ({len(cards_impedidos_qa) + len(cards_reprovados_qa)})", expanded=False):
            all_problemas = pd.concat([cards_impedidos_qa, cards_reprovados_qa]) if not cards_reprovados_qa.empty else cards_impedidos_qa
            for _, row in all_problemas.iterrows():
                status_icon = "🚫" if row['status_cat'] == 'blocked' else "❌"
                status_name = "Impedido" if row['status_cat'] == 'blocked' else "Reprovado"
                card_link = card_link_com_popup(row['ticket_id'])
                st.markdown(f"""
                <div style="padding: 10px 12px; margin: 6px 0; border-left: 4px solid #ef4444; background: rgba(239, 68, 68, 0.08); border-radius: 6px;">
                    <strong>{status_icon}</strong> {card_link} - {row['titulo']}<br>
                    <small style="color: #6b7280;">👤 DEV: {row['desenvolvedor']} | {status_name} | {int(row['sp'])} SP</small>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)


def _renderizar_resumo_semana_qa(df_qa: pd.DataFrame, qa_sel: str):
    """Renderiza o resumo semanal do QA."""
    with st.expander("📅 Resumo da Semana", expanded=False):
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
        fim_sexta = sexta_semana + timedelta(days=1) - timedelta(seconds=1)
        inicio_semana = segunda_semana.replace(hour=0, minute=0, second=0)
        
        # Exibe período selecionado
        st.markdown(f"""
        <div style="background: #f1f5f9; padding: 8px 15px; border-radius: 6px; margin-bottom: 15px; text-align: center;">
            <span style="color: #64748b;">📅 Período: <strong>{segunda_semana.strftime('%d/%m')} (Seg)</strong> a <strong>{sexta_semana.strftime('%d/%m')} (Sex)</strong></span>
        </div>
        """, unsafe_allow_html=True)
        
        # Filtra cards CONCLUÍDOS na semana usando resolutiondate
        df_validados_semana = df_qa[
            (df_qa['status_cat'] == 'done') & 
            (df_qa['resolutiondate'].notna()) &
            (df_qa['resolutiondate'] >= inicio_semana) & 
            (df_qa['resolutiondate'] <= fim_sexta)
        ].copy() if 'resolutiondate' in df_qa.columns else pd.DataFrame()
        
        # Fallback para atualizado
        if df_validados_semana.empty:
            df_validados_semana = df_qa[
                (df_qa['status_cat'] == 'done') & 
                (df_qa['atualizado'] >= inicio_semana) & 
                (df_qa['atualizado'] <= fim_sexta)
            ].copy() if 'atualizado' in df_qa.columns else pd.DataFrame()
        
        # Cards que tiveram atividade na semana
        df_semana = df_qa[
            (df_qa['atualizado'] >= inicio_semana) & 
            (df_qa['atualizado'] <= fim_sexta)
        ].copy() if 'atualizado' in df_qa.columns else pd.DataFrame()
        
        # Helper para mini-cards harmonizados
        def mini_card(valor, titulo, subtitulo, cor="#6b7280"):
            bg = f"{cor}10" if cor != "#6b7280" else "white"
            border = f"{cor}40" if cor != "#6b7280" else "#e5e7eb"
            return f'<div style="background: {bg}; border: 2px solid {border}; border-radius: 12px; padding: 16px 12px; text-align: center; height: 95px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);"><div style="font-size: 28px; font-weight: 700; color: {cor}; line-height: 1.1;">{valor}</div><div style="font-size: 12px; font-weight: 600; color: #374151; margin-top: 4px;">{titulo}</div><div style="font-size: 10px; color: #6b7280;">{subtitulo}</div></div>'
        
        # KPIs da Semana - Novo estilo
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(mini_card(str(len(df_semana)), "Cards Trabalhados", semana_selecionada, "#3b82f6"), unsafe_allow_html=True)
        with col2:
            st.markdown(mini_card(str(len(df_validados_semana)), "Validações", "concluídos", "#22c55e"), unsafe_allow_html=True)
        with col3:
            bugs_semana = int(df_validados_semana['bugs'].sum()) if not df_validados_semana.empty else 0
            st.markdown(mini_card(str(bugs_semana), "Bugs", "encontrados", "#8b5cf6"), unsafe_allow_html=True)
        with col4:
            sp_semana = int(df_validados_semana['sp'].sum()) if not df_validados_semana.empty else 0
            st.markdown(mini_card(str(sp_semana), "SP Entregues", "story points", "#22c55e"), unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        
        # Evolução da Semana
        _renderizar_evolucao_semana_qa(df_qa, inicio_semana, fim_sexta, segunda_semana)
        
        st.markdown("---")
        
        # 📝 Resumo para Daily/Retro - PRIMEIRO!
        _renderizar_resumo_daily_retro_qa(df_qa, df_validados_semana, segunda_semana, sexta_semana, qa_sel)
        
        # Cards em Trabalho
        _renderizar_cards_em_trabalho_qa(df_qa)
        
        # Cards Reprovados
        _renderizar_cards_reprovados_qa(df_qa)
        
        # Cards Impedidos
        _renderizar_cards_impedidos_qa(df_qa)
        
        # Cards Validados na Semana
        _renderizar_cards_validados_semana(df_validados_semana, df_qa, segunda_semana, sexta_semana, qa_sel)


def _renderizar_evolucao_semana_qa(df_qa: pd.DataFrame, inicio_semana, fim_sexta, segunda_semana):
    """Renderiza gráfico de evolução da semana."""
    st.markdown("**📈 Evolução da Semana**")
    st.caption("💡 Mostra a fila diminuindo e os concluídos aumentando ao longo da semana")
    
    # Calcula a evolução dia a dia
    cards_fila_semana = df_qa[
        (df_qa['status_cat'].isin(['waiting_qa', 'testing', 'done'])) &
        (df_qa['atualizado'] >= inicio_semana) & 
        (df_qa['atualizado'] <= fim_sexta)
    ].copy() if 'atualizado' in df_qa.columns else pd.DataFrame()
    
    total_fila_inicial = len(cards_fila_semana)
    
    dias_evolucao = []
    
    for i in range(5):  # 0=seg, 4=sex
        dia = segunda_semana + timedelta(days=i)
        dia_str = dia.strftime("%d/%m")
        dia_nome = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex'][i]
        
        dia_fim = pd.Timestamp(dia.date()) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        
        if 'resolutiondate' in df_qa.columns:
            col_resolution = df_qa['resolutiondate']
            if hasattr(col_resolution.dtype, 'tz') and col_resolution.dtype.tz is not None:
                col_resolution = col_resolution.dt.tz_localize(None)
            
            concluidos_ate_dia = len(df_qa[
                (df_qa['status_cat'] == 'done') &
                (col_resolution.notna()) &
                (col_resolution >= inicio_semana) &
                (col_resolution <= dia_fim)
            ])
            
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


def _renderizar_resumo_daily_retro_qa(df_qa: pd.DataFrame, df_validados_semana: pd.DataFrame, segunda_semana, sexta_semana, qa_sel: str):
    """Renderiza resumo para Daily/Retro - PRIMEIRO na lista de expanders."""
    df_em_trabalho = df_qa[df_qa['status_cat'].isin(['waiting_qa', 'testing'])].copy()
    df_reprovados_qa = df_qa[df_qa['status_cat'] == 'rejected'].copy()
    df_impedidos_qa = df_qa[df_qa['status_cat'] == 'blocked'].copy()
    
    with st.expander("📝 Resumo para Daily/Retro", expanded=False):
        total_validados = len(df_validados_semana)
        total_sp_validados = int(df_validados_semana['sp'].sum()) if not df_validados_semana.empty else 0
        total_bugs = int(df_validados_semana['bugs'].sum()) if not df_validados_semana.empty else 0
        clean_rate = len(df_validados_semana[df_validados_semana['bugs'] == 0]) / total_validados * 100 if total_validados > 0 else 0
        
        # Monta resumo completo
        resumo_em_trabalho = ""
        if not df_em_trabalho.empty:
            df_em_trabalho_sorted = df_em_trabalho.sort_values('atualizado', ascending=False)
            resumo_em_trabalho = "\n🔄 Em trabalho:\n" + "\n".join([f"  • {row['ticket_id']}: {row['titulo']} ({'Aguardando' if row['status_cat'] == 'waiting_qa' else 'Validando'})" for _, row in df_em_trabalho_sorted.iterrows()])
        
        resumo_reprovados = ""
        if not df_reprovados_qa.empty:
            df_reprovados_sorted = df_reprovados_qa.sort_values('atualizado', ascending=False)
            resumo_reprovados = "\n❌ Reprovados:\n" + "\n".join([f"  • {row['ticket_id']}: {row['titulo']} ({int(row['bugs'])} bugs)" for _, row in df_reprovados_sorted.iterrows()])
        
        resumo_impedidos = ""
        if not df_impedidos_qa.empty:
            resumo_impedidos = "\n🚫 Impedidos:\n" + "\n".join([f"  • {row['ticket_id']}: {row['titulo']}" for _, row in df_impedidos_qa.iterrows()])
        
        resumo_validados = ""
        if not df_validados_semana.empty:
            df_validados_semana_sorted = df_validados_semana.sort_values('resolutiondate' if 'resolutiondate' in df_validados_semana.columns and df_validados_semana['resolutiondate'].notna().any() else 'atualizado', ascending=False)
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


def _renderizar_cards_em_trabalho_qa(df_qa: pd.DataFrame):
    """Renderiza cards em trabalho do QA."""
    df_em_trabalho = df_qa[df_qa['status_cat'].isin(['waiting_qa', 'testing'])].copy()
    
    with st.expander(f"🔄 Cards em Trabalho ({len(df_em_trabalho)})", expanded=False):
        st.caption("Cards que você está trabalhando agora (aguardando validação + em validação)")
        
        if not df_em_trabalho.empty:
            df_em_trabalho_sorted = df_em_trabalho.sort_values('atualizado', ascending=False)
            
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


def _renderizar_cards_reprovados_qa(df_qa: pd.DataFrame):
    """Renderiza cards reprovados pelo QA."""
    df_reprovados_qa = df_qa[df_qa['status_cat'] == 'rejected'].copy()
    
    with st.expander(f"❌ Cards Reprovados ({len(df_reprovados_qa)})", expanded=False):
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


def _renderizar_cards_impedidos_qa(df_qa: pd.DataFrame):
    """Renderiza cards impedidos do QA."""
    df_impedidos_qa = df_qa[df_qa['status_cat'] == 'blocked'].copy()
    
    with st.expander(f"🚫 Cards Impedidos ({len(df_impedidos_qa)})", expanded=False):
        st.caption("Cards bloqueados que precisam de atenção")
        
        if not df_impedidos_qa.empty:
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
        else:
            st.info("💡 Nenhum card impedido no momento")


def _renderizar_cards_validados_semana(df_validados_semana: pd.DataFrame, df_qa: pd.DataFrame, segunda_semana, sexta_semana, qa_sel: str):
    """Renderiza cards validados na semana."""
    
    with st.expander(f"✅ Cards Validados na Semana ({len(df_validados_semana)})", expanded=False):
        st.caption("Cards que você concluiu a validação")
        
        if not df_validados_semana.empty:
            sort_col = 'resolutiondate' if 'resolutiondate' in df_validados_semana.columns and df_validados_semana['resolutiondate'].notna().any() else 'atualizado'
            df_validados_semana_sorted = df_validados_semana.sort_values(sort_col, ascending=False)
            
            st.markdown('<div class="scroll-container" style="max-height: 400px;">', unsafe_allow_html=True)
            for _, row in df_validados_semana_sorted.iterrows():
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
        else:
            st.info("💡 Nenhum card foi validado nesta semana.")
    
    # Tempo de Ciclo por Card
    if not df_validados_semana.empty:
        with st.expander("⏱️ Tempo de Ciclo dos Cards da Semana", expanded=False):
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


def _renderizar_distribuicao_status_qa(df_qa: pd.DataFrame):
    """Renderiza distribuição por status do QA."""
    with st.expander("📊 Distribuição por Status", expanded=False):
        status_count = df_qa['status_cat'].value_counts().reset_index()
        status_count.columns = ['Status', 'Cards']
        status_count['Status'] = status_count['Status'].map(lambda x: STATUS_NOMES.get(x, x))
        
        fig = px.pie(status_count, values='Cards', names='Status', hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)


def _renderizar_bugs_por_dev(df_qa: pd.DataFrame):
    """Renderiza bugs por desenvolvedor que o QA validou."""
    with st.expander("🐛 Bugs por Desenvolvedor", expanded=False):
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


def _renderizar_cards_fila_qa(df_qa: pd.DataFrame):
    """Renderiza cards em fila do QA."""
    with st.expander("📋 Cards em Fila (Aguardando/Validando)", expanded=False):
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


def _renderizar_throughput_qa(df_qa: pd.DataFrame, qa_sel: str):
    """Renderiza throughput e eficiência do QA."""
    validados = len(df_qa[df_qa['status_cat'] == 'done'])
    cards_sem_bugs = len(df_qa[(df_qa['status_cat'] == 'done') & (df_qa['bugs'] == 0)])
    fpy_val = cards_sem_bugs / validados * 100 if validados > 0 else 0
    
    with st.expander("📈 Throughput e Eficiência", expanded=False):
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


def _renderizar_comparativo_time_qa(df: pd.DataFrame, df_qa: pd.DataFrame):
    """Renderiza comparativo com a média do time."""
    validados = len(df_qa[df_qa['status_cat'] == 'done'])
    
    with st.expander("📊 Comparativo com o Time", expanded=False):
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
            st.metric("Cards Validados", meus_validados, f"{diff_validados:+.0f} vs média", delta_color="normal")
        with col2:
            diff_sp = meu_sp - media_time_sp
            st.metric("Story Points", meu_sp, f"{diff_sp:+.0f} vs média", delta_color="normal")
        with col3:
            diff_bugs = meus_bugs - media_time_bugs
            st.metric("Bugs Encontrados", meus_bugs, f"{diff_bugs:+.0f} vs média", delta_color="inverse")


def _renderizar_distribuicao_complexidade(df_qa: pd.DataFrame):
    """Renderiza distribuição de complexidade."""
    with st.expander("🎯 Distribuição de Complexidade (SP)", expanded=False):
        sp_dist = df_qa.groupby('sp').size().reset_index(name='Cards')
        if not sp_dist.empty:
            fig = px.bar(sp_dist, x='sp', y='Cards', title="Cards por Story Points",
                         color='sp', color_continuous_scale='Blues')
            fig.update_layout(height=300, xaxis_title="Story Points", yaxis_title="Quantidade")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sem dados de SP")


def _renderizar_cards_validados_qa(df_qa: pd.DataFrame):
    """Renderiza histórico de cards validados."""
    with st.expander("✅ Cards Validados (Histórico)", expanded=False):
        cards_done = df_qa[df_qa['status_cat'] == 'done'].sort_values('lead_time', ascending=False)
        
        if not cards_done.empty:
            # Container com scroll (classe global)
            cards_html = '<div class="scroll-container" style="max-height: 350px;">'
            
            for _, row in cards_done.iterrows():
                bugs = int(row['bugs'])
                bugs_cor = '#ef4444' if bugs >= 2 else '#eab308' if bugs == 1 else '#22c55e'
                card_link = card_link_com_popup(row['ticket_id'])
                titulo = str(row['titulo'])[:50]
                dev = str(row['desenvolvedor'])
                sp = str(row['sp'])
                lead_time = str(round(row['lead_time'], 1))
                
                cards_html += '<div style="padding: 10px; margin: 5px 0; border-left: 3px solid ' + bugs_cor + '; background: rgba(100,100,100,0.05); border-radius: 4px;">'
                cards_html += '<div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">'
                cards_html += card_link
                cards_html += '<span style="color: #64748b;"> - ' + titulo + '...</span>'
                cards_html += '</div>'
                cards_html += '<small style="color: #94a3b8;">🐛 ' + str(bugs) + ' bugs | 👤 ' + dev + ' | ' + sp + ' SP | ⏱️ ' + lead_time + 'd</small>'
                cards_html += '</div>'
            
            cards_html += '</div>'
            st.markdown(cards_html, unsafe_allow_html=True)
            
            if len(cards_done) > 20:
                st.caption(f"📋 {len(cards_done)} cards validados")
        else:
            st.info("Nenhum card validado ainda")
