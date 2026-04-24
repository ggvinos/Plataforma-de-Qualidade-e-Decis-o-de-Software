"""
================================================================================
ABA CLIENTES - NinaDash v8.82
================================================================================
Análise por Clientes/Temas.

Funcionalidades:
- Visão geral do time (quando "Ver Todos")
- Análise detalhada por cliente
- Desenvolvimento pago vs outros
- Responsáveis por cliente
- Timeline e histórico

Author: GitHub Copilot
Version: 1.0 (Phase 6)
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
import plotly.express as px
import html as html_lib

from modulos.config import (
    JIRA_BASE_URL, STATUS_NOMES, STATUS_CORES, TEMAS_NAO_CLIENTES, NINADASH_URL
)
from modulos.helpers import criar_card_metrica, formatar_tempo_relativo


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
        _renderizar_visao_geral(df_temas, clientes_unicos)
    else:
        _renderizar_cliente_selecionado(df_temas, cliente_selecionado)


def _renderizar_visao_geral(df_temas: pd.DataFrame, clientes_unicos: list):
    """Renderiza a visão geral quando 'Ver Todos' está selecionado."""
    # ===== VISÃO GERAL - KPIs GLOBAIS =====
    with st.expander("📊 Indicadores Gerais de Clientes", expanded=False):
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
    with st.expander("📊 Top 15 Clientes por Volume de Cards", expanded=False):
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
        with st.expander("💰 Análise de Desenvolvimento Pago", expanded=False):
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
    with st.expander("🐛 Clientes com Mais Bugs Encontrados", expanded=False):
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


def _renderizar_cliente_selecionado(df_temas: pd.DataFrame, cliente_selecionado: str):
    """Renderiza a análise detalhada de um cliente específico."""
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
    
    with st.expander("📊 Métricas do Cliente", expanded=False):
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
