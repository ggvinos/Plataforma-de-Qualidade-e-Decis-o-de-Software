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
    criar_card_metrica, exportar_para_csv, exportar_para_excel
)
from modulos.widgets import (
    mostrar_tooltip, mostrar_lista_df_completa
)
from modulos.graficos import criar_grafico_concentracao
from modulos._abas_legacy import exibir_historico_validacoes


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
    _renderizar_decisao_release(decisao, decisao_cor, decisao_msg, health, total_cards, pct_conclusao, fk, mat, dias_release)
    _renderizar_pontos_atencao(df)
    _renderizar_esforco_time(df)
    _renderizar_interacao_qa_dev(df)
    _renderizar_concentracao_conhecimento(df)
    _renderizar_performance_dev(df)
    _renderizar_historico_validacoes_lideranca(df)
    _renderizar_exportacao(df, health)


def _renderizar_decisao_release(decisao, decisao_cor, decisao_msg, health, total_cards, pct_conclusao, fk, mat, dias_release):
    """Renderiza a seção de decisão Go/No-Go."""
    with st.expander("🚦 Decisão de Release (Go/No-Go)", expanded=False):
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


def _renderizar_esforco_time(df: pd.DataFrame):
    """Renderiza a seção de esforço do time."""
    with st.expander("💪 Esforço do Time (DEV + QA)", expanded=False):
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
        devs_ativos = df[df['desenvolvedor'] != 'Não atribuído']['desenvolvedor'].nunique()
        with col3:
            velocidade = sp_entregues / devs_ativos if devs_ativos > 0 else 0
            criar_card_metrica(f"{velocidade:.1f}", "Velocidade", "blue", "SP/DEV entregue")


def _renderizar_interacao_qa_dev(df: pd.DataFrame):
    """Renderiza a seção de interação QA x DEV."""
    with st.expander("🤝 Interação QA x DEV (Visão Liderança)", expanded=False):
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


def _renderizar_performance_dev(df: pd.DataFrame):
    """Renderiza a seção de performance por desenvolvedor."""
    with st.expander("👨‍💻 Performance por Desenvolvedor", expanded=False):
        dev_metricas = calcular_metricas_dev(df)
        st.dataframe(dev_metricas['stats'], hide_index=True, use_container_width=True)


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
