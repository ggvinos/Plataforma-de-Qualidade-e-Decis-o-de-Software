"""
================================================================================
ABA LIDERANÇA - NinaDash v8.82
================================================================================
Painel de Liderança com decisões estratégicas.

Funcionalidades:
- Go/No-Go de release
- Health Score composto
- Pontos de atenção
- Esforço do time (DEV + QA)
- Interação QA x DEV
- Análise de concentração de conhecimento
- Performance por desenvolvedor
- Histórico de validações
- Exportação de dados

Author: GitHub Copilot
Version: 1.0 (Phase 6)
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

from modulos.calculos import (
    calcular_fator_k, calcular_health_score, classificar_maturidade,
    calcular_concentracao_conhecimento, calcular_metricas_dev
)
from modulos.helpers import (
    exportar_para_csv, exportar_para_excel, obter_contexto_periodo
)
from modulos.widgets import (
    mostrar_tooltip, mostrar_lista_df_completa, mostrar_lista_tickets_completa
)
from modulos.utils import card_link_com_popup
from modulos.graficos import criar_grafico_concentracao
from modulos._abas_legacy import exibir_historico_validacoes


# Helper global para mini-cards harmonizados
def _mini_card(valor, titulo, subtitulo, cor="#6b7280"):
    bg = f"{cor}10" if cor != "#6b7280" else "white"
    border = f"{cor}40" if cor != "#6b7280" else "#e5e7eb"
    return f'<div style="background: {bg}; border: 2px solid {border}; border-radius: 12px; padding: 16px 12px; text-align: center; height: 95px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);"><div style="font-size: 28px; font-weight: 700; color: {cor}; line-height: 1.1;">{valor}</div><div style="font-size: 12px; font-weight: 600; color: #374151; margin-top: 4px;">{titulo}</div><div style="font-size: 10px; color: #6b7280;">{subtitulo}</div></div>'

def _cor_status(valor, verde, amarelo):
    if valor < verde:
        return "#22c55e"
    elif valor < amarelo:
        return "#f59e0b"
    return "#ef4444"

def _cor_status_inv(valor, verde, amarelo):
    if valor >= verde:
        return "#22c55e"
    elif valor >= amarelo:
        return "#f59e0b"
    return "#ef4444"


def aba_lideranca(df: pd.DataFrame):
    """Aba de Liderança com decisões estratégicas."""
    ctx = obter_contexto_periodo()
    
    st.markdown("### 🎯 Painel de Liderança")
    st.caption(f"Visão executiva para tomada de decisão - Go/No-Go de release • **{ctx['emoji']} {ctx['titulo']}**")
    
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
    _renderizar_decisao_release(decisao, decisao_cor, decisao_msg, health, total_cards, pct_conclusao, fk, mat, dias_release)
    _renderizar_esforco_time(df)
    _renderizar_composicao_health(health)
    _renderizar_pontos_atencao(df)
    _renderizar_interacao_qa_dev(df)
    _renderizar_analise_tech_lead(df)
    _renderizar_concentracao_conhecimento(df)
    _renderizar_cards_proxima_release(df)
    _renderizar_lista_completa_por_ambiente(df)
    _renderizar_performance_dev(df)
    _renderizar_historico_validacoes_lideranca(df)
    _renderizar_exportacao(df, health)


def _renderizar_decisao_release(decisao, decisao_cor, decisao_msg, health, total_cards, pct_conclusao, fk, mat, dias_release):
    """Renderiza a seção de decisão Go/No-Go."""
    
    # ===== INDICADORES PRINCIPAIS (SEMPRE VISÍVEIS) =====
    st.markdown("##### 🚦 Decisão de Release")
    
    # Badge de decisão
    cores_badge = {"red": "#ef4444", "yellow": "#f59e0b", "green": "#22c55e"}
    cor_hex = cores_badge.get(decisao_cor, "#6b7280")
    st.markdown(f"""
    <div style="background: {cor_hex}15; border: 2px solid {cor_hex}; border-radius: 12px; padding: 12px 16px; margin-bottom: 16px; display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 20px; font-weight: 700; color: {cor_hex};">{decisao}</span>
        <span style="font-size: 13px; color: #374151;">{decisao_msg}</span>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        cor = _cor_status_inv(health['score'], 75, 50)
        st.markdown(_mini_card(f"{health['score']:.0f}", "🏥 Health Score", health['status'], cor), unsafe_allow_html=True)
    
    with col2:
        st.markdown(_mini_card(str(total_cards), "📋 Cards", "total sprint", "#3b82f6"), unsafe_allow_html=True)
    
    with col3:
        cor = _cor_status_inv(pct_conclusao, 70, 40)
        st.markdown(_mini_card(f"{pct_conclusao:.0f}%", "✅ Conclusão", "done/total", cor), unsafe_allow_html=True)
    
    with col4:
        cor = _cor_status_inv(fk, 3, 2)
        st.markdown(_mini_card(f"{fk:.1f}", "🏆 Fator K", mat['selo'], cor), unsafe_allow_html=True)
    
    with col5:
        cor = _cor_status(dias_release, 3, 5) if dias_release else "#6b7280"
        st.markdown(_mini_card(str(dias_release), "⏱️ Dias Release", "restantes", cor), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)


def _renderizar_composicao_health(health: dict):
    """Renderiza a composição do Health Score em expander separado."""
    with st.expander("📊 Composição do Health Score", expanded=False):
        nomes = {'conclusao': 'Conclusão', 'ddp': 'DDP', 'fpy': 'FPY', 'gargalos': 'Gargalos', 'lead_time': 'Lead Time'}
        cols = st.columns(5)
        
        for i, (key, det) in enumerate(health['detalhes'].items()):
            with cols[i]:
                pct = det['score'] / det['peso'] * 100 if det['peso'] > 0 else 0
                cor = _cor_status_inv(pct, 70, 40)
                st.markdown(_mini_card(f"{det['score']:.0f}/{det['peso']}", f"📊 {nomes.get(key, key)}", f"{pct:.0f}%", cor), unsafe_allow_html=True)
        
        mostrar_tooltip("health_score")


def _renderizar_pontos_atencao(df: pd.DataFrame):
    """Renderiza a seção de pontos de atenção."""
    with st.expander("🚨 Pontos de Atenção", expanded=False):
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
            colunas_fora = ['ticket_id', 'titulo', 'complexidade', 'dias_ate_release', 'janela_dias_necessarios', 'qa']
            if 'ambiente' in fora_janela.columns:
                colunas_fora.insert(2, 'ambiente')
            df_fora = fora_janela[[c for c in colunas_fora if c in fora_janela.columns]].copy()
            colunas_renomeadas = ['Ticket', 'Título', 'Complexidade', 'Dias Disponíveis', 'Dias Necessários', 'QA']
            if 'ambiente' in fora_janela.columns:
                colunas_renomeadas.insert(2, 'Ambiente')
            df_fora.columns = colunas_renomeadas
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


def _renderizar_esforco_time(df: pd.DataFrame):
    """Renderiza a seção de esforço do time."""
    
    # ===== INDICADORES DE ESFORÇO (SEMPRE VISÍVEIS) =====
    st.markdown("##### 💪 Esforço do Time")
    
    devs_ativos = df[df['desenvolvedor'] != 'Não atribuído']['desenvolvedor'].nunique()
    qas_ativos = df[df['qa'] != 'Não atribuído']['qa'].nunique()
    media_cards_dev = len(df) / devs_ativos if devs_ativos > 0 else 0
    media_cards_qa = len(df) / qas_ativos if qas_ativos > 0 else 0
    throughput = len(df[df['status_cat'] == 'done'])
    sp_entregues = int(df[df['status_cat'] == 'done']['sp'].sum())
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(_mini_card(str(devs_ativos), "👨‍💻 DEVs", "ativos", "#3b82f6"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(_mini_card(str(qas_ativos), "🔬 QAs", "ativos", "#8b5cf6"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(_mini_card(f"{media_cards_dev:.1f}", "📋 Cards/DEV", "média", "#6b7280"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(_mini_card(f"{media_cards_qa:.1f}", "📋 Cards/QA", "média", "#6b7280"), unsafe_allow_html=True)
    
    with col5:
        st.markdown(_mini_card(str(throughput), "✅ Throughput", "cards done", "#22c55e"), unsafe_allow_html=True)
    
    with col6:
        st.markdown(_mini_card(str(sp_entregues), "📐 SP Entregues", "story points", "#22c55e"), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
    
    # Detalhes em expander
    with st.expander("📊 Distribuição de Carga DEV/QA", expanded=False):
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


def _renderizar_interacao_qa_dev(df: pd.DataFrame):
    """Renderiza a seção de interação QA x DEV."""
    with st.expander("🤝 Interação QA x DEV", expanded=False):
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
                st.markdown(_mini_card(str(total_parcerias), "🤝 Parcerias", "QA-DEV", "#3b82f6"), unsafe_allow_html=True)
            
            with col2:
                media_cards_parceria = matriz['Cards'].mean()
                st.markdown(_mini_card(f"{media_cards_parceria:.1f}", "📋 Média", "cards/parceria", "#6b7280"), unsafe_allow_html=True)
            
            with col3:
                parcerias_sem_bugs = len(matriz[matriz['Bugs'] == 0])
                pct_sem_bugs = parcerias_sem_bugs / total_parcerias * 100 if total_parcerias > 0 else 0
                cor = _cor_status_inv(pct_sem_bugs, 70, 40)
                st.markdown(_mini_card(f"{pct_sem_bugs:.0f}%", "✅ Sem Bugs", "parcerias", cor), unsafe_allow_html=True)
            
            with col4:
                fk_medio = matriz['FK'].mean()
                cor = _cor_status_inv(fk_medio, 3, 2)
                st.markdown(_mini_card(f"{fk_medio:.1f}", "🏆 FK Médio", "parcerias", cor), unsafe_allow_html=True)
        else:
            st.info("💡 Sem dados de interação QA-DEV. Verifique se os cards têm QA e Desenvolvedor atribuídos.")


def _renderizar_concentracao_conhecimento(df: pd.DataFrame):
    """Renderiza a seção de análise de concentração de conhecimento."""
    with st.expander("🔄 Análise de Concentração de Conhecimento (Rodízio)", expanded=False):
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
            cor = "#ef4444" if total_criticos > 0 else "#22c55e"
            st.markdown(_mini_card(str(total_criticos), "🚨 Críticos", "≥80% conc.", cor), unsafe_allow_html=True)
        with col2:
            cor = "#f59e0b" if total_atencao > 0 else "#22c55e"
            st.markdown(_mini_card(str(total_atencao), "⚠️ Atenção", "60-79% conc.", cor), unsafe_allow_html=True)
        with col3:
            st.markdown(_mini_card(str(total_recomendacoes), "💡 Sugestões", "rodízio", "#3b82f6"), unsafe_allow_html=True)
        with col4:
            # Calcula score geral de distribuição
            total_indices = len(concentracao['indices'].get('dev_produto', {})) + len(concentracao['indices'].get('qa_produto', {}))
            indices_saudaveis = sum(1 for d in concentracao['indices'].get('dev_produto', {}).values() if d['concentracao_pct'] < 60)
            indices_saudaveis += sum(1 for d in concentracao['indices'].get('qa_produto', {}).values() if d['concentracao_pct'] < 60)
            score_distribuicao = (indices_saudaveis / total_indices * 100) if total_indices > 0 else 100
            cor = _cor_status_inv(score_distribuicao, 70, 40)
            st.markdown(_mini_card(f"{score_distribuicao:.0f}%", "📊 Distribuição", "saudável", cor), unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        
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


def _renderizar_cards_proxima_release(df: pd.DataFrame):
    """Renderiza seção de cards que vão subir na próxima release."""
    with st.expander("🚀 Cards na Próxima Release", expanded=True):
        # Cards em homologação
        if 'ambiente' in df.columns:
            # Filtra cards em homologação (ambiente HML)
            cards_hml = df[df['ambiente'].str.lower().str.contains('homolog', na=False)]
            # Filtra cards em produção
            cards_prod = df[df['ambiente'].str.lower().str.contains('produ', na=False)]
            # Cards em develop
            cards_dev = df[df['ambiente'].str.lower().str.contains('develop', na=False)]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f'''
                <div style="background: #fffbeb; border: 2px solid #d97706; border-radius: 10px; padding: 14px; text-align: center;">
                    <div style="font-size: 28px; font-weight: 700; color: #d97706;">{len(cards_hml)}</div>
                    <div style="font-size: 13px; font-weight: 600; color: #92400e;">🟡 Em Homologação</div>
                    <div style="font-size: 11px; color: #b45309; margin-top: 4px;">Sobem na próxima release</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2:
                st.markdown(f'''
                <div style="background: #f0fdf4; border: 2px solid #16a34a; border-radius: 10px; padding: 14px; text-align: center;">
                    <div style="font-size: 28px; font-weight: 700; color: #16a34a;">{len(cards_dev)}</div>
                    <div style="font-size: 13px; font-weight: 600; color: #166534;">🟢 Em Develop</div>
                    <div style="font-size: 11px; color: #15803d; margin-top: 4px;">Ainda em testes</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col3:
                st.markdown(f'''
                <div style="background: #fef2f2; border: 2px solid #dc2626; border-radius: 10px; padding: 14px; text-align: center;">
                    <div style="font-size: 28px; font-weight: 700; color: #dc2626;">{len(cards_prod)}</div>
                    <div style="font-size: 13px; font-weight: 600; color: #991b1b;">🔴 Em Produção</div>
                    <div style="font-size: 11px; color: #b91c1c; margin-top: 4px;">Já publicados</div>
                </div>
                ''', unsafe_allow_html=True)
            
            # Lista de cards em homologação
            if not cards_hml.empty:
                st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
                st.markdown("**🚀 Cards que sobem na próxima release:**")
                
                # Usa função padrão da plataforma com botão NinaDash
                cards_list = cards_hml.to_dict('records')
                mostrar_lista_tickets_completa(cards_list, "Em Homologação - Próxima Release")
            else:
                st.info("Nenhum card em homologação no momento")
        else:
            st.warning("⚠️ Campo 'Ambiente' não disponível nos dados")
            st.caption("O campo de ambiente permite identificar onde cada card está deployado")


def _renderizar_lista_completa_por_ambiente(df: pd.DataFrame):
    """Renderiza lista completa de cards agrupados por ambiente."""
    with st.expander("🌍 Lista de Cards por Ambiente", expanded=False):
        st.markdown('<div style="font-size: 13px; color: #6b7280; margin-bottom: 16px;">Visualize todos os cards organizados pelo ambiente de deploy</div>', unsafe_allow_html=True)
        
        if 'ambiente' not in df.columns:
            st.warning("⚠️ Campo 'Ambiente' não disponível nos dados")
            return
        
        # Classificar cards por ambiente
        cards_dev = df[df['ambiente'].str.lower().str.contains('develop', na=False)]
        cards_hml = df[df['ambiente'].str.lower().str.contains('homolog', na=False)]
        cards_prod = df[df['ambiente'].str.lower().str.contains('produ', na=False)]
        cards_sem = df[df['ambiente'].isna() | (df['ambiente'] == '')]
        
        # Resumo geral
        total = len(df)
        st.markdown(f"""
        <div style="display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap;">
            <div style="background: #f0fdf4; border: 1px solid #16a34a40; border-radius: 8px; padding: 8px 16px;">
                <span style="font-weight: 600; color: #16a34a;">🟢 DEV: {len(cards_dev)}</span>
            </div>
            <div style="background: #fffbeb; border: 1px solid #d9770640; border-radius: 8px; padding: 8px 16px;">
                <span style="font-weight: 600; color: #d97706;">🟡 HML: {len(cards_hml)}</span>
            </div>
            <div style="background: #fef2f2; border: 1px solid #dc262640; border-radius: 8px; padding: 8px 16px;">
                <span style="font-weight: 600; color: #dc2626;">🔴 PROD: {len(cards_prod)}</span>
            </div>
            <div style="background: #f3f4f6; border: 1px solid #6b728040; border-radius: 8px; padding: 8px 16px;">
                <span style="font-weight: 600; color: #6b7280;">⚪ Sem: {len(cards_sem)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Seletor de ambiente
        tab_dev, tab_hml, tab_prod, tab_sem = st.tabs(["🟢 Develop", "🟡 Homologação", "🔴 Produção", "⚪ Sem Ambiente"])
        
        with tab_dev:
            if not cards_dev.empty:
                mostrar_lista_tickets_completa(cards_dev.to_dict('records'), f"Develop ({len(cards_dev)} cards)")
            else:
                st.info("Nenhum card em ambiente Develop")
        
        with tab_hml:
            if not cards_hml.empty:
                st.markdown("""
                <div style="background: #fffbeb; border: 1px solid #d97706; border-radius: 8px; padding: 10px; margin-bottom: 12px;">
                    <span style="font-weight: 600; color: #d97706;">🚀 Estes cards sobem na próxima release</span>
                </div>
                """, unsafe_allow_html=True)
                mostrar_lista_tickets_completa(cards_hml.to_dict('records'), f"Homologação ({len(cards_hml)} cards)")
            else:
                st.info("Nenhum card em ambiente Homologação")
        
        with tab_prod:
            if not cards_prod.empty:
                mostrar_lista_tickets_completa(cards_prod.to_dict('records'), f"Produção ({len(cards_prod)} cards)")
            else:
                st.info("Nenhum card em ambiente Produção")
        
        with tab_sem:
            if not cards_sem.empty:
                st.markdown("""
                <div style="background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 10px; margin-bottom: 12px;">
                    <span style="font-weight: 600; color: #d97706;">⚠️ Estes cards precisam ter o ambiente preenchido</span>
                </div>
                """, unsafe_allow_html=True)
                mostrar_lista_tickets_completa(cards_sem.to_dict('records'), f"Sem Ambiente ({len(cards_sem)} cards)")
            else:
                st.success("✅ Todos os cards têm ambiente preenchido")


def _renderizar_performance_dev(df: pd.DataFrame):
    """Renderiza a seção de performance por desenvolvedor."""
    with st.expander("👨‍💻 Performance por Desenvolvedor", expanded=False):
        dev_metricas = calcular_metricas_dev(df)
        st.dataframe(dev_metricas['stats'], hide_index=True, use_container_width=True)


def _renderizar_analise_tech_lead(df: pd.DataFrame):
    """Renderiza análise específica para Tech Lead - WIP, Code Review, Velocidade."""
    with st.expander("🎯 Análise para Tech Lead", expanded=False):
        st.markdown('<div style="font-size: 13px; color: #6b7280; margin-bottom: 12px;">Visão gerencial do time de desenvolvimento: carga, WIP e velocidade</div>', unsafe_allow_html=True)
        
        col_tl1, col_tl2 = st.columns(2)
        
        with col_tl1:
            st.markdown('<div style="font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 8px;">📊 Distribuição de Story Points por Dev</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 12px; color: #9ca3af; margin-bottom: 8px;">Quem está assumindo mais complexidade</div>', unsafe_allow_html=True)
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
            st.markdown('<div style="font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 8px;">🚀 Status de Entrega por Dev</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 12px; color: #9ca3af; margin-bottom: 8px;">Progresso: Concluído vs Em andamento</div>', unsafe_allow_html=True)
            
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
        
        # WIP e Velocidade
        col_tl3, col_tl4 = st.columns(2)
        
        with col_tl3:
            st.markdown('<div style="font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 8px;">⏳ Work-In-Progress (WIP) por Dev</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 12px; color: #9ca3af; margin-bottom: 8px;">Quantos cards cada dev está trabalhando agora</div>', unsafe_allow_html=True)
            
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
                st.markdown('<div style="background: #F0FDF4; border-radius: 8px; padding: 16px; text-align: center;"><span style="font-size: 18px;">✅</span><div style="font-size: 13px; color: #166534; margin-top: 4px;">Nenhum dev com WIP no momento</div></div>', unsafe_allow_html=True)
        
        with col_tl4:
            st.markdown('<div style="font-size: 14px; font-weight: 600; color: #374151; margin-bottom: 8px;">📈 Velocidade do Time (SP/Card)</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size: 12px; color: #9ca3af; margin-bottom: 8px;">Eficiência: média de Story Points por card entregue</div>', unsafe_allow_html=True)
            
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
        
        # Cards Críticos
        st.markdown('<div style="font-size: 14px; font-weight: 600; color: #374151; margin: 16px 0 8px 0;">🔴 Cards Críticos (Alta Prioridade em Dev)</div>', unsafe_allow_html=True)
        
        criticos_dev = df[(df['prioridade'].isin(['Alta', 'Muito Alta', 'Muito alto', 'Alto'])) & 
                          (df['status_cat'].isin(['development', 'code_review', 'backlog']))]
        
        if not criticos_dev.empty:
            col1, col2 = st.columns(2)
            for i, (_, row) in enumerate(criticos_dev.head(6).iterrows()):
                with col1 if i % 2 == 0 else col2:
                    titulo = str(row['titulo'])[:45] + "..." if len(str(row['titulo'])) > 45 else str(row['titulo'])
                    ambiente = row.get('ambiente', '') if 'ambiente' in row.index else ''
                    ambiente_badge = ""
                    if ambiente:
                        ambiente_lower = ambiente.lower()
                        if 'produção' in ambiente_lower or 'producao' in ambiente_lower:
                            ambiente_badge = '<span style="background: #fef2f2; color: #dc2626; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 600; margin-left: 6px;">🔴 PROD</span>'
                        elif 'homologação' in ambiente_lower or 'homologacao' in ambiente_lower:
                            ambiente_badge = '<span style="background: #fffbeb; color: #d97706; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 600; margin-left: 6px;">🟡 HML</span>'
                        elif 'develop' in ambiente_lower:
                            ambiente_badge = '<span style="background: #f0fdf4; color: #16a34a; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 600; margin-left: 6px;">🟢 DEV</span>'
                    st.markdown(f'<div style="background: #FEF2F2; border-left: 3px solid #EF4444; border-radius: 0 8px 8px 0; padding: 10px 12px; margin-bottom: 8px;"><div style="font-size: 13px; font-weight: 600; color: #374151;">{row["ticket_id"]}{ambiente_badge}</div><div style="font-size: 12px; color: #6b7280; margin-top: 4px;">{titulo}</div><div style="font-size: 11px; color: #9ca3af; margin-top: 6px;">⚠️ {row["prioridade"]} · 👤 {row["desenvolvedor"]} · {row["sp"]} SP</div></div>', unsafe_allow_html=True)
            
            if len(criticos_dev) > 6:
                st.markdown(f'<div style="background: #FEF2F2; border-radius: 8px; padding: 10px; text-align: center; margin-top: 8px;"><span style="font-size: 13px; color: #EF4444; font-weight: 600;">⚠️ {len(criticos_dev)} cards de alta prioridade ainda em desenvolvimento!</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background: #F0FDF4; border-radius: 8px; padding: 16px; text-align: center;"><span style="font-size: 18px;">✅</span><div style="font-size: 13px; color: #166534; margin-top: 4px;">Nenhum card crítico pendente</div></div>', unsafe_allow_html=True)


def _renderizar_historico_validacoes_lideranca(df: pd.DataFrame):
    """Renderiza a seção de histórico de validações."""
    with st.expander("✅ Histórico de Cards Validados", expanded=False):
        exibir_historico_validacoes(df, key_prefix="lideranca")


def _renderizar_exportacao(df: pd.DataFrame, health: dict):
    """Renderiza a seção de exportação de dados."""
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
