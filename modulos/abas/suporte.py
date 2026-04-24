"""
================================================================================
ABA SUPORTE/IMPLANTAÇÃO - NinaDash v8.82
================================================================================
Visão consolidada para times de suporte/implantação.

Funcionalidades:
- Visão geral do time (quando "Ver Todos")
- Cards aguardando ação
- Validação em produção
- Cards concluídos
- Análise por projeto
- Cards aguardando resposta

Author: GitHub Copilot
Version: 1.0 (Phase 6)
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
import plotly.express as px

from modulos.config import NINADASH_URL
from modulos.helpers import criar_card_metrica, formatar_tempo_relativo
from modulos.utils import card_link_com_popup


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
        _renderizar_visao_geral(df_todos)
        return
    
    st.markdown("---")
    
    # ========== FILTRAR CARDS DA PESSOA ==========
    df_pessoa = df_todos[df_todos['relator'] == pessoa_selecionada].copy()
    
    if df_pessoa.empty:
        st.warning(f"⚠️ Nenhum card encontrado para **{pessoa_selecionada}** no período selecionado.")
        return
    
    _renderizar_visao_individual(df_todos, df_pessoa, pessoa_selecionada)


def _renderizar_visao_geral(df_todos: pd.DataFrame):
    """Renderiza a visão geral quando 'Ver Todos' está selecionado."""
    st.markdown("---")
    
    # ===== MÉTRICAS GERAIS DO TIME =====
    st.markdown("#### 📊 Métricas Gerais do Time")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_cards = len(df_todos)
    
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
    with st.expander("📊 Distribuição de Cards", expanded=False):
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
    
    with st.expander(f"⏳ Cards Aguardando Ação ({total_aguardando})", expanded=False):
        st.caption("Cards que precisam de ação. O **responsável** mostrado é quem deve agir no card.")
        
        # Checkbox para ver todos os cards
        ver_todos_cards = st.checkbox("📋 Ver todos os cards (sem limite)", key="ver_todos_cards_aguardando", value=False)
        limite_cards = 999 if ver_todos_cards else 20
        
        col_aguard1, col_aguard2, col_aguard3 = st.columns(3)
        
        with col_aguard1:
            st.markdown(f"##### 💬 Aguardando Resposta ({len(df_aguard_resp)})")
            _renderizar_lista_cards_aguardando(df_aguard_resp, 'SD', limite_cards, 'amarelo')
        
        with col_aguard2:
            st.markdown(f"##### 🔍 Validação Produção ({len(df_valprod_pend)})")
            _renderizar_lista_cards_aguardando(df_valprod_pend, 'VALPROD', limite_cards, 'laranja')
        
        with col_aguard3:
            st.markdown(f"##### 📦 Backlog ({len(df_pb_aguard)})")
            _renderizar_lista_cards_aguardando(df_pb_aguard, 'PB', limite_cards, 'azul')
    
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


def _renderizar_lista_cards_aguardando(df_cards: pd.DataFrame, projeto_default: str, limite: int, cor_card: str):
    """Renderiza uma lista de cards aguardando ação."""
    if df_cards.empty:
        st.info("Nenhum card aguardando")
        return
    
    cores_classes = {
        'amarelo': 'card-lista-amarelo',
        'laranja': 'card-lista-laranja',
        'azul': 'card-lista-azul'
    }
    classe_card = cores_classes.get(cor_card, 'card-lista')
    
    cards_html = f'<div class="scroll-container" style="max-height: 400px;">'
    for _, card in df_cards.head(limite).iterrows():
        projeto = card.get('projeto', projeto_default)
        tipo = card.get('tipo', 'TAREFA')
        tipo_cor = "#ef4444" if tipo == "HOTFIX" else "#f97316" if tipo == "BUG" else "#64748b"
        responsavel = card.get('responsavel') or card.get('desenvolvedor') or card.get('qa') or card.get('relator', 'N/A')
        if not responsavel or responsavel == 'Não atribuído':
            responsavel = card.get('relator', 'N/A')
        titulo = str(card.get('titulo', card.get('resumo', '')))[:80]
        ticket_id = card.get('ticket_id', '')
        popup_html = card_link_com_popup(ticket_id, projeto)
        
        cards_html += f'''
        <div class="{classe_card}">
            <div style="display: flex; align-items: center; gap: 4px; flex-wrap: wrap; margin-bottom: 4px;">
                <span style="background: #64748b; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">{projeto}</span>
                <span style="background: {tipo_cor}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">{tipo}</span>
                {popup_html}
            </div>
            <div style="font-size: 13px; line-height: 1.4;">{titulo}{"..." if len(str(card.get("titulo", ""))) > 80 else ""}</div>
            <div style="font-size: 11px; margin-top: 4px;">👤 {responsavel}</div>
        </div>'''
    cards_html += '</div>'
    
    if len(df_cards) > limite:
        cards_html += f'<p style="color: #64748b; font-size: 12px; margin-top: 8px; text-align: center;">... e mais {len(df_cards) - limite} cards</p>'
    
    st.markdown(cards_html, unsafe_allow_html=True)


def _renderizar_visao_individual(df_todos: pd.DataFrame, df_pessoa: pd.DataFrame, pessoa_selecionada: str):
    """Renderiza a visão individual de uma pessoa."""
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
    _renderizar_metricas_pessoa(df_pessoa)
    
    # Cards aguardando minha ação
    _renderizar_cards_aguardando_minha_acao(df_todos, df_pessoa, pessoa_selecionada)
    
    # Cards para validar em produção
    _renderizar_cards_validar_producao(df_pessoa)
    
    # Cards concluídos
    _renderizar_cards_concluidos(df_pessoa)
    
    # Onde estão meus cards
    _renderizar_onde_estao_meus_cards(df_pessoa)
    
    # Cards aguardando resposta
    _renderizar_cards_aguardando_resposta(df_pessoa)
    
    # Meus cards no PB
    _renderizar_cards_pb(df_pessoa)
    
    # Meus cards em SD/QA
    _renderizar_cards_sd_qa(df_pessoa)
    
    # Tooltip explicativo
    _renderizar_tooltip_sobre()


def _renderizar_metricas_pessoa(df_pessoa: pd.DataFrame):
    """Renderiza as métricas por projeto da pessoa."""
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


def _renderizar_cards_aguardando_minha_acao(df_todos: pd.DataFrame, df_pessoa: pd.DataFrame, pessoa_selecionada: str):
    """Renderiza os cards aguardando ação da pessoa."""
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
        with st.expander(f"🔬 Cards Aguardando Minha Ação ({len(df_minha_acao)})", expanded=False):
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


def _renderizar_cards_validar_producao(df_pessoa: pd.DataFrame):
    """Renderiza os cards para validar em produção."""
    df_valprod = df_pessoa[df_pessoa['projeto'] == 'VALPROD'] if 'projeto' in df_pessoa.columns else pd.DataFrame()
    
    with st.expander("🔍 Cards para Validar em Produção", expanded=False):
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


def _renderizar_cards_concluidos(df_pessoa: pd.DataFrame):
    """Renderiza os cards concluídos."""
    with st.expander("✅ Cards Concluídos", expanded=False):
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


def _renderizar_onde_estao_meus_cards(df_pessoa: pd.DataFrame):
    """Renderiza a seção 'Onde estão meus cards?'."""
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


def _renderizar_cards_aguardando_resposta(df_pessoa: pd.DataFrame):
    """Renderiza os cards aguardando resposta."""
    with st.expander("💬 Cards Aguardando Resposta", expanded=False):
        # Cards com status "aguardando" em qualquer projeto (várias variações)
        filtro_aguardando = 'aguardando|waiting|pendente resposta|aguarda |em espera'
        df_aguardando = df_pessoa[df_pessoa['status'].str.lower().str.contains(filtro_aguardando, na=False, regex=True)]
        
        if not df_aguardando.empty:
            st.markdown(f"##### 💬 {len(df_aguardando)} cards aguardando algum retorno")
            
            for _, card in df_aguardando.iterrows():
                projeto = card.get('projeto', 'SD')
                tipo = card.get('tipo', 'TAREFA')
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


def _renderizar_cards_pb(df_pessoa: pd.DataFrame):
    """Renderiza os cards no Product Backlog."""
    df_pb = df_pessoa[df_pessoa['projeto'] == 'PB'] if 'projeto' in df_pessoa.columns else pd.DataFrame()
    
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


def _renderizar_cards_sd_qa(df_pessoa: pd.DataFrame):
    """Renderiza os cards em SD/QA."""
    df_sd = df_pessoa[df_pessoa['projeto'] == 'SD'] if 'projeto' in df_pessoa.columns else pd.DataFrame()
    df_qa = df_pessoa[df_pessoa['projeto'] == 'QA'] if 'projeto' in df_pessoa.columns else pd.DataFrame()
    df_dev = pd.concat([df_sd, df_qa]) if not df_sd.empty or not df_qa.empty else pd.DataFrame()
    
    with st.expander("📋 Meus Cards em Desenvolvimento (SD/QA)", expanded=False):
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


def _renderizar_tooltip_sobre():
    """Renderiza o tooltip explicativo sobre a aba."""
    with st.expander("ℹ️ Sobre esta Aba", expanded=False):
        st.markdown("""
        ### 🎯 Suporte e Implantação — O que analisamos?
        
        Esta aba foi criada para você acompanhar **seus cards em todos os projetos**:
        
        | Seção | O que mostra |
        |-------|--------------|
        | **🔬 Cards Aguardando Minha Validação** | Cards para você validar como QA |
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
