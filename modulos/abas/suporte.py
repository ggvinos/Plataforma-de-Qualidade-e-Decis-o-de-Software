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
from modulos.helpers import criar_card_metrica, formatar_tempo_relativo, obter_contexto_periodo, gerar_badge_ambiente
from modulos.utils import card_link_com_popup


def aba_suporte_implantacao(df_todos: pd.DataFrame):
    """
    Aba de Suporte e Implantação - Visão consolidada para times de suporte/implantação.
    
    Similar às abas QA e Dev:
    - Seletor de pessoa (relator): inclui "Ver Todos" para visão geral
    - Visão de cards em TODOS os projetos
    - Foco: "Onde estão meus cards?" + "O que precisa de validação/resposta?"
    
    IMPORTANTE: Usa status_cat para consistência com a Visão Geral.
    
    Args:
        df_todos: DataFrame com cards de TODOS os projetos (SD, QA, PB, VALPROD)
    """
    ctx = obter_contexto_periodo()
    
    st.markdown("### 🎯 Suporte e Implantação")
    st.caption(f"Acompanhe seus cards em todos os projetos: SD, QA, PB e VALPROD • **{ctx['emoji']} {ctx['titulo']}**")
    
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
        st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
        _renderizar_visao_geral(df_todos)
        return
    
    st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
    
    # ========== FILTRAR CARDS DA PESSOA ==========
    df_pessoa = df_todos[df_todos['relator'] == pessoa_selecionada].copy()
    
    if df_pessoa.empty:
        st.warning(f"⚠️ Nenhum card encontrado para **{pessoa_selecionada}** no período selecionado.")
        return
    
    _renderizar_visao_individual(df_todos, df_pessoa, pessoa_selecionada)


def _renderizar_visao_geral(df_todos: pd.DataFrame):
    """Renderiza a visão geral quando 'Ver Todos' está selecionado."""
    
    # Helper para mini-cards compactos (para flexbox)
    def mini_card(valor, titulo, subtitulo, cor="#6b7280"):
        bg = f"{cor}10" if cor != "#6b7280" else "white"
        border = f"{cor}40" if cor != "#6b7280" else "#e5e7eb"
        return f'<div style="flex: 1; min-width: 0; background: {bg}; border: 1px solid {border}; border-radius: 8px; padding: 10px 8px; text-align: center; height: 72px; display: flex; flex-direction: column; justify-content: center;"><div style="font-size: 24px; font-weight: 700; color: {cor}; line-height: 1;">{valor}</div><div style="font-size: 11px; font-weight: 600; color: #374151; margin-top: 3px;">{titulo}</div><div style="font-size: 10px; color: #6b7280;">{subtitulo}</div></div>'
    
    def renderizar_linha(cards_html):
        return f'<div style="display: flex; gap: 8px; margin-bottom: 8px;">{"".join(cards_html)}</div>'
    
    # ===== INDICADORES DO TIME =====
    st.markdown("##### 📊 Indicadores do Time")
    
    total_cards = len(df_todos)
    total_sd = len(df_todos[df_todos['projeto'] == 'SD']) if 'projeto' in df_todos.columns else 0
    total_qa = len(df_todos[df_todos['projeto'] == 'QA']) if 'projeto' in df_todos.columns else 0
    total_pb = len(df_todos[df_todos['projeto'] == 'PB']) if 'projeto' in df_todos.columns else 0
    total_valprod = len(df_todos[df_todos['projeto'] == 'VALPROD']) if 'projeto' in df_todos.columns else 0
    pessoas_unicas = df_todos['relator'].nunique()
    
    pct_sd = f"{(total_sd/total_cards*100):.0f}%" if total_cards > 0 else "0%"
    pct_qa = f"{(total_qa/total_cards*100):.0f}%" if total_cards > 0 else "0%"
    pct_pb = f"{(total_pb/total_cards*100):.0f}%" if total_cards > 0 else "0%"
    pct_vp = f"{(total_valprod/total_cards*100):.0f}%" if total_cards > 0 else "0%"
    
    cards_linha1 = [
        mini_card(str(total_sd), "📋 SD", pct_sd, "#3b82f6"),
        mini_card(str(total_qa), "🔬 QA", pct_qa, "#22c55e"),
        mini_card(str(total_pb), "📦 PB", pct_pb, "#f59e0b"),
        mini_card(str(total_valprod), "✅ VALPROD", pct_vp, "#8b5cf6"),
        mini_card(str(pessoas_unicas), "👥 Pessoas", "no time", "#6b7280"),
    ]
    st.markdown(renderizar_linha(cards_linha1), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    
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
    has_status_cat = 'status_cat' in df_todos.columns
    
    # Conta totais usando status_cat para consistência
    if has_status_cat:
        # Aguardando QA + Bloqueados = precisam de ação
        df_aguard_qa = df_todos[df_todos['status_cat'] == 'waiting_qa']
        df_bloqueados = df_todos[df_todos['status_cat'].isin(['blocked', 'rejected'])]
        df_aguard_resp = pd.concat([df_aguard_qa, df_bloqueados]).drop_duplicates(subset=['ticket_id']) if 'ticket_id' in df_todos.columns else pd.concat([df_aguard_qa, df_bloqueados])
        
        # VALPROD pendentes
        df_valprod_pend = df_todos[(df_todos['projeto'] == 'VALPROD') & 
                                   (~df_todos['status_cat'].isin(['done', 'valprod_aprovado']))]
        
        # PB aguardando
        df_pb_aguard = df_todos[(df_todos['projeto'] == 'PB') & 
                                (df_todos['status_cat'].isin(['pb_revisao_produto', 'pb_ux', 
                                                               'pb_esforco', 'pb_aguarda_dev', 'pb_aguardando_resposta']))]
    else:
        # Fallback para string matching
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
    
    # Cores com CSS inline para garantir renderização
    cores_bg = {
        'amarelo': 'rgba(245, 158, 11, 0.08)',
        'laranja': 'rgba(249, 115, 22, 0.08)',
        'azul': 'rgba(59, 130, 246, 0.08)'
    }
    cores_borda = {
        'amarelo': '#f59e0b',
        'laranja': '#f97316',
        'azul': '#3b82f6'
    }
    bg = cores_bg.get(cor_card, 'rgba(100, 100, 100, 0.08)')
    borda = cores_borda.get(cor_card, '#64748b')
    
    # URL base do Jira
    jira_base = "https://ninatecnologia.atlassian.net/browse"
    
    cards_html = f'<div style="max-height: 400px; overflow-y: auto;">'
    for _, card in df_cards.head(limite).iterrows():
        projeto = card.get('projeto', projeto_default)
        tipo = card.get('tipo', 'TAREFA')
        tipo_cor = "#ef4444" if tipo == "HOTFIX" else "#f97316" if tipo == "BUG" else "#64748b"
        responsavel = card.get('responsavel') or card.get('desenvolvedor') or card.get('qa') or card.get('relator', 'N/A')
        if not responsavel or responsavel == 'Não atribuído':
            responsavel = card.get('relator', 'N/A')
        titulo = str(card.get('titulo', card.get('resumo', '')))[:80]
        ticket_id = card.get('ticket_id', '')
        
        # Link direto para o Jira (sem popup complexo)
        link_jira = f'{jira_base}/{ticket_id}'
        ticket_cor = "#8b5cf6" if projeto == "PB" else "#3b82f6" if projeto == "SD" else "#22c55e"
        
        # Badge de ambiente (se preenchido)
        ambiente = card.get('ambiente', '')
        ambiente_badge = ''
        if ambiente:
            ambiente_lower = str(ambiente).lower()
            if 'produção' in ambiente_lower or 'producao' in ambiente_lower:
                ambiente_badge = '<span style="background: #fef2f2; color: #dc2626; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 600; margin-left: 4px;">🔴 PROD</span>'
            elif 'homologação' in ambiente_lower or 'homologacao' in ambiente_lower:
                ambiente_badge = '<span style="background: #fffbeb; color: #d97706; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 600; margin-left: 4px;">🟡 HML</span>'
            elif 'develop' in ambiente_lower:
                ambiente_badge = '<span style="background: #f0fdf4; color: #16a34a; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 600; margin-left: 4px;">🟢 DEV</span>'
        
        # CSS inline completo para garantir renderização
        cards_html += f'''
        <div style="padding: 12px 15px; margin: 8px 0; border-radius: 8px; border-left: 4px solid {borda}; background: {bg};">
            <div style="display: flex; align-items: center; gap: 4px; flex-wrap: wrap; margin-bottom: 4px;">
                <span style="background: #64748b; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">{projeto}</span>
                <span style="background: {tipo_cor}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">{tipo}</span>
                <a href="{link_jira}" target="_blank" style="color: {ticket_cor}; font-weight: 600; text-decoration: none;">{ticket_id}</a>
                {ambiente_badge}
            </div>
            <div style="font-size: 13px; line-height: 1.4; color: #1f2937;">{titulo}{"..." if len(str(card.get("titulo", ""))) > 80 else ""}</div>
            <div style="font-size: 11px; margin-top: 4px; color: #6b7280;">👤 {responsavel}</div>
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
    """Renderiza as métricas por projeto da pessoa - Estilo harmonizado.
    
    IMPORTANTE: Usa status_cat para consistência com a Visão Geral.
    - Em Desenvolvimento: status_cat in ['development', 'code_review']
    - Aguardando QA: status_cat == 'waiting_qa'
    - Em Validação: status_cat == 'testing'
    - Concluído: status_cat == 'done'
    """
    
    # Helper para mini-cards compactos (para flexbox)
    def mini_card(valor, titulo, subtitulo, cor="#6b7280"):
        bg = f"{cor}10" if cor != "#6b7280" else "white"
        border = f"{cor}40" if cor != "#6b7280" else "#e5e7eb"
        return f'<div style="flex: 1; min-width: 0; background: {bg}; border: 1px solid {border}; border-radius: 8px; padding: 10px 8px; text-align: center; height: 72px; display: flex; flex-direction: column; justify-content: center;"><div style="font-size: 24px; font-weight: 700; color: {cor}; line-height: 1;">{valor}</div><div style="font-size: 11px; font-weight: 600; color: #374151; margin-top: 3px;">{titulo}</div><div style="font-size: 10px; color: #6b7280;">{subtitulo}</div></div>'
    
    def renderizar_linha(cards_html):
        return f'<div style="display: flex; gap: 8px; margin-bottom: 8px;">{"".join(cards_html)}</div>'
    
    st.markdown("##### 📊 Meus Cards por Status")
    
    # Usa status_cat para consistência com outras abas
    has_status_cat = 'status_cat' in df_pessoa.columns
    
    if has_status_cat:
        # Em Desenvolvimento = development + code_review (igual Visão Geral)
        em_dev = len(df_pessoa[df_pessoa['status_cat'].isin(['development', 'code_review'])])
        
        # Aguardando QA = waiting_qa
        aguardando_qa = len(df_pessoa[df_pessoa['status_cat'] == 'waiting_qa'])
        
        # Em Validação/Teste = testing
        em_teste = len(df_pessoa[df_pessoa['status_cat'] == 'testing'])
        
        # Concluídos = done (único critério confiável)
        concluidos = len(df_pessoa[df_pessoa['status_cat'] == 'done'])
        
        # Bloqueados = blocked + rejected
        bloqueados = len(df_pessoa[df_pessoa['status_cat'].isin(['blocked', 'rejected'])])
    else:
        # Fallback para string matching se status_cat não existir
        em_dev = len(df_pessoa[df_pessoa['status'].str.lower().str.contains('andamento|revisão', na=False)])
        aguardando_qa = len(df_pessoa[df_pessoa['status'].str.upper().str.contains('AGUARDANDO VALIDAÇÃO', na=False)])
        em_teste = len(df_pessoa[df_pessoa['status'].str.upper().str.contains('EM VALIDAÇÃO', na=False)])
        concluidos = len(df_pessoa[df_pessoa['status'].str.lower().str.contains('concluído', na=False)])
        bloqueados = len(df_pessoa[df_pessoa['status'].str.lower().str.contains('impedido|reprovado', na=False)])
    
    # Calcula pendentes de validação em produção
    df_valprod = df_pessoa[df_pessoa['projeto'] == 'VALPROD'] if 'projeto' in df_pessoa.columns else pd.DataFrame()
    if has_status_cat and not df_valprod.empty:
        pendentes_valprod = len(df_valprod[~df_valprod['status_cat'].isin(['done', 'valprod_aprovado'])])
    elif not df_valprod.empty:
        pendentes_valprod = len(df_valprod[~df_valprod['status'].str.lower().str.contains('aprovado|validado|concluído', na=False)])
    else:
        pendentes_valprod = 0
    
    cor_dev = "#3b82f6" if em_dev > 0 else "#6b7280"
    cor_qa = "#f59e0b" if aguardando_qa > 0 else "#6b7280"
    cor_teste = "#06b6d4" if em_teste > 0 else "#6b7280"
    cor_valprod = "#ef4444" if pendentes_valprod > 0 else "#8b5cf6"
    
    cards_linha1 = [
        mini_card(str(em_dev), "💻 Em Dev", "desenvolvimento", cor_dev),
        mini_card(str(aguardando_qa), "⏳ Aguard. QA", "na fila", cor_qa),
        mini_card(str(em_teste), "🧪 Em Teste", "validando", cor_teste),
        mini_card(str(pendentes_valprod), "🔍 Val. Prod", "pendentes", cor_valprod),
        mini_card(str(concluidos), "✅ Concluídos", "finalizados", "#22c55e"),
    ]
    st.markdown(renderizar_linha(cards_linha1), unsafe_allow_html=True)
    
    # Linha 2: Detalhamento se houver bloqueados ou por projeto
    if bloqueados > 0:
        st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
        cards_extra = [mini_card(str(bloqueados), "🚫 Bloqueados", "impeditivos", "#ef4444")]
        st.markdown(renderizar_linha(cards_extra), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)


def _renderizar_cards_aguardando_minha_acao(df_todos: pd.DataFrame, df_pessoa: pd.DataFrame, pessoa_selecionada: str):
    """Renderiza os cards aguardando ação da pessoa.
    
    MELHORIAS IMPLEMENTADAS:
    1. Usa status_cat para consistência com Visão Geral
    2. Separa claramente os papéis: QA, Desenvolvedor, Representante
    3. Mostra apenas cards em status que REALMENTE precisam de ação
    """
    has_status_cat = 'status_cat' in df_todos.columns
    
    # ===== SEÇÃO 1: Cards para EU VALIDAR (sou QA responsável) =====
    df_validar_qa = pd.DataFrame()
    if 'qa' in df_todos.columns:
        if has_status_cat:
            # Cards onde sou QA e estão aguardando minha validação ou em validação
            df_validar_qa = df_todos[
                (df_todos['qa'] == pessoa_selecionada) & 
                (df_todos['status_cat'].isin(['waiting_qa', 'testing']))
            ]
        else:
            df_validar_qa = df_todos[
                (df_todos['qa'] == pessoa_selecionada) & 
                (df_todos['status'].str.lower().str.contains('aguardando validação|validação|testing|em teste|em qa', na=False, regex=True))
            ]
    
    # ===== SEÇÃO 2: Cards para EU DESENVOLVER (sou desenvolvedor e card voltou) =====
    df_voltar_dev = pd.DataFrame()
    if 'responsavel' in df_todos.columns or 'desenvolvedor' in df_todos.columns:
        col_dev = 'desenvolvedor' if 'desenvolvedor' in df_todos.columns else 'responsavel'
        if has_status_cat:
            # Cards reprovados ou que voltaram para mim
            df_voltar_dev = df_todos[
                (df_todos[col_dev] == pessoa_selecionada) & 
                (df_todos['status_cat'].isin(['rejected', 'blocked']))
            ]
        else:
            df_voltar_dev = df_todos[
                (df_todos[col_dev] == pessoa_selecionada) & 
                (df_todos['status'].str.lower().str.contains('reprovado|impedido|bloqueado|rejeitado', na=False, regex=True))
            ]
    
    # ===== SEÇÃO 3: Cards como Representante do Cliente =====
    df_rep_cliente = pd.DataFrame()
    if 'representante_cliente' in df_todos.columns:
        if has_status_cat:
            df_rep_cliente = df_todos[
                (df_todos['representante_cliente'] == pessoa_selecionada) & 
                (df_todos['status_cat'].isin(['testing', 'waiting_qa', 'valprod_pendente', 'valprod_validando']))
            ]
        else:
            df_rep_cliente = df_todos[
                (df_todos['representante_cliente'] == pessoa_selecionada) & 
                (df_todos['status'].str.lower().str.contains('aguardando|validação|teste|cliente', na=False, regex=True))
            ]
    
    # Combina e remove duplicados
    df_minha_acao = pd.concat([df_validar_qa, df_voltar_dev, df_rep_cliente])
    if not df_minha_acao.empty:
        df_minha_acao = df_minha_acao.drop_duplicates(subset=['ticket_id'])
    
    # ===== RENDERIZAÇÃO =====
    total_acao = len(df_minha_acao)
    cor_titulo = "#ef4444" if total_acao > 0 else "#22c55e"
    icone = "⚠️" if total_acao > 0 else "✅"
    
    with st.expander(f"{icone} O que você precisa fazer ({total_acao})", expanded=total_acao > 0):
        if total_acao == 0:
            st.success("✅ Nenhum card aguardando sua ação no momento!")
            return
        
        # Mostra resumo por papel
        n_qa = len(df_validar_qa)
        n_voltar = len(df_voltar_dev)
        n_rep = len(df_rep_cliente)
        
        cols_resumo = st.columns(3)
        with cols_resumo[0]:
            st.metric("🔬 Para Validar (QA)", n_qa)
        with cols_resumo[1]:
            st.metric("🔄 Voltaram (Correção)", n_voltar)
        with cols_resumo[2]:
            st.metric("👤 Rep. Cliente", n_rep)
        
        st.markdown("---")
        
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
            acao_necessaria = ""
            cor_papel = "#8b5cf6"
            if card.get('qa') == pessoa_selecionada and card['ticket_id'] in df_validar_qa['ticket_id'].values if not df_validar_qa.empty else False:
                papeis.append("QA")
                acao_necessaria = "👉 VALIDAR"
                cor_papel = "#06b6d4"
            if card['ticket_id'] in df_voltar_dev['ticket_id'].values if not df_voltar_dev.empty else False:
                papeis.append("Dev")
                acao_necessaria = "👉 CORRIGIR"
                cor_papel = "#ef4444"
            if card.get('representante_cliente') == pessoa_selecionada:
                papeis.append("Rep. Cliente")
                acao_necessaria = "👉 APROVAR"
                cor_papel = "#f59e0b"
            
            papel_texto = " • ".join(papeis) if papeis else "Validador"
            
            card_link = card_link_com_popup(card['ticket_id'], projeto)
            sufixo = '...' if len(str(card.get('titulo', ''))) > 70 else ''
            
            # Define cor do card baseado no papel
            card_class = "card-lista-roxo"
            if "CORRIGIR" in acao_necessaria:
                card_class = "card-lista"  # Vermelho
            elif "VALIDAR" in acao_necessaria:
                card_class = "card-lista-cyan"  # Ciano
            
            html_minha_acao += f'<div class="{card_class}" style="border-left-color: {cor_papel};">'
            html_minha_acao += '<div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px; flex-wrap: wrap;">'
            html_minha_acao += '<span style="background: #64748b; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">' + projeto + '</span>'
            html_minha_acao += '<span style="background: ' + tipo_cor + '; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">' + tipo + '</span>'
            html_minha_acao += '<span style="background: ' + cor_papel + '; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; font-weight: bold;">' + acao_necessaria + '</span>'
            html_minha_acao += card_link
            html_minha_acao += '<span style="color: #7c3aed; font-size: 0.75em; margin-left: auto;">🕐 ' + tempo_atualizacao + '</span>'
            html_minha_acao += '</div>'
            html_minha_acao += '<div style="color: #374151; font-size: 0.9em; line-height: 1.4;">' + titulo + sufixo + '</div>'
            html_minha_acao += '<div style="color: #64748b; font-size: 0.8em; margin-top: 4px;">Por: ' + relator + ' • ' + papel_texto + ' • ' + status_card + '</div>'
            html_minha_acao += '</div>'
        
        html_minha_acao += '</div>'
        st.markdown(html_minha_acao, unsafe_allow_html=True)


def _renderizar_cards_validar_producao(df_pessoa: pd.DataFrame):
    """Renderiza os cards para validar em produção usando status_cat."""
    has_status_cat = 'status_cat' in df_pessoa.columns
    df_valprod = df_pessoa[df_pessoa['projeto'] == 'VALPROD'] if 'projeto' in df_pessoa.columns else pd.DataFrame()
    
    with st.expander("🔍 Cards para Validar em Produção", expanded=False):
        if not df_valprod.empty:
            # Filtra pendentes usando status_cat se disponível
            if has_status_cat:
                df_pendentes = df_valprod[~df_valprod['status_cat'].isin(['done', 'valprod_aprovado'])]
            else:
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
    """Renderiza os cards concluídos usando status_cat para consistência."""
    has_status_cat = 'status_cat' in df_pessoa.columns
    
    with st.expander("✅ Cards Concluídos", expanded=False):
        # Filtra cards concluídos usando status_cat se disponível
        if has_status_cat:
            df_concluidos_lista = df_pessoa[df_pessoa['status_cat'].isin(['done', 'valprod_aprovado'])]
        else:
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
    """Renderiza a seção 'Onde estão meus cards?' usando status_cat para consistência."""
    from modulos.config import STATUS_NOMES, STATUS_CORES
    
    has_status_cat = 'status_cat' in df_pessoa.columns
    
    with st.expander("📊 Onde estão meus cards? (Fluxo de Status)", expanded=False):
        if has_status_cat:
            col_graf, col_lista = st.columns([1, 1])
            
            with col_graf:
                # Gráfico de barras por status_cat (consistente com Visão Geral)
                status_counts = df_pessoa['status_cat'].value_counts().reset_index()
                status_counts.columns = ['status_cat', 'count']
                
                # Adiciona nomes amigáveis
                status_counts['nome'] = status_counts['status_cat'].map(
                    lambda x: STATUS_NOMES.get(x, x.replace('_', ' ').title())
                )
                status_counts['cor'] = status_counts['status_cat'].map(
                    lambda x: STATUS_CORES.get(x, '#64748b')
                )
                
                if not status_counts.empty:
                    fig = px.bar(
                        status_counts, 
                        x='nome', 
                        y='count',
                        color='nome',
                        color_discrete_map={
                            row['nome']: row['cor'] for _, row in status_counts.iterrows()
                        },
                        title='📊 Meus Cards por Status (Mesmo critério da Visão Geral)'
                    )
                    fig.update_layout(
                        height=350, 
                        showlegend=False,
                        xaxis_title="Status",
                        yaxis_title="Quantidade"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col_lista:
                st.markdown("##### 📋 Detalhamento por Status")
                
                # Agrupa por status_cat para mostrar fluxo
                fluxo_ordem = ['backlog', 'development', 'code_review', 'waiting_qa', 'testing', 'done', 'blocked', 'rejected']
                
                for cat in fluxo_ordem:
                    df_cat = df_pessoa[df_pessoa['status_cat'] == cat]
                    if not df_cat.empty:
                        nome = STATUS_NOMES.get(cat, cat)
                        cor = STATUS_CORES.get(cat, '#64748b')
                        st.markdown(
                            f"<div style='display: flex; align-items: center; gap: 8px; margin: 4px 0;'>"
                            f"<span style='background: {cor}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; min-width: 140px;'>{nome}</span>"
                            f"<span style='font-weight: bold; font-size: 16px;'>{len(df_cat)}</span>"
                            f"</div>", 
                            unsafe_allow_html=True
                        )
                
                # Outros status não mapeados
                outros = df_pessoa[~df_pessoa['status_cat'].isin(fluxo_ordem)]
                if not outros.empty:
                    st.markdown(f"<div style='margin-top: 8px; color: #64748b;'>Outros: {len(outros)}</div>", unsafe_allow_html=True)
        else:
            # Fallback: sem status_cat
            if 'projeto' in df_pessoa.columns:
                col_graf, col_lista = st.columns([1, 1])
                
                with col_graf:
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
                                cor = "#22c55e" if 'concluído' in status.lower() or 'validado' in status.lower() or 'aprovado' in status.lower() else \
                                      "#ef4444" if 'reprovado' in status.lower() or 'impedido' in status.lower() else \
                                      "#f59e0b" if 'aguardando' in status.lower() else \
                                      "#3b82f6"
                                st.markdown(f"<span style='color: {cor};'>●</span> {status}: **{count}**", unsafe_allow_html=True)
                            st.markdown("")


def _renderizar_cards_aguardando_resposta(df_pessoa: pd.DataFrame):
    """Renderiza os cards aguardando resposta usando status_cat para consistência."""
    has_status_cat = 'status_cat' in df_pessoa.columns
    
    with st.expander("💬 Cards Aguardando Resposta", expanded=False):
        # Cards com status "aguardando" - usando status_cat se disponível
        if has_status_cat:
            df_aguardando = df_pessoa[df_pessoa['status_cat'].isin([
                'pb_aguardando_resposta', 'waiting_qa', 'blocked'
            ])]
        else:
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
        
        Esta aba foi criada para você acompanhar **seus cards em todos os projetos**.
        
        **⚠️ IMPORTANTE: Consistência com a Visão Geral**
        
        Todos os números aqui usam os **mesmos critérios** da Visão Geral:
        
        | Status mostrado | O que significa (status_cat) |
        |-----------------|------------------------------|
        | **💻 Em Dev** | Em andamento ou Code Review |
        | **⏳ Aguard. QA** | Aguardando Validação (fila do QA) |
        | **🧪 Em Teste** | Em Validação (QA validando) |
        | **✅ Concluído** | Concluído (pronto) |
        | **🚫 Bloqueado** | Impedido ou Reprovado |
        
        ### 📋 Seções Disponíveis
        
        | Seção | O que mostra |
        |-------|--------------|
        | **⚠️ O que você precisa fazer** | Cards onde você precisa agir (validar, corrigir, aprovar) |
        | **🔍 Cards para Validar em Produção** | Cards do VALPROD que você precisa testar em produção |
        | **✅ Cards Concluídos** | Cards finalizados com sucesso |
        | **📊 Onde estão meus cards?** | Visão geral por status (mesmo critério da Visão Geral) |
        | **💬 Cards Aguardando Resposta** | Cards que precisam de retorno de alguém |
        
        ### 🎯 Dicas de Uso:
        - Selecione seu nome para ver **seus cards específicos**
        - A seção "**O que você precisa fazer**" mostra suas pendências
        - Cards com **👉 VALIDAR** = você é o QA responsável
        - Cards com **👉 CORRIGIR** = voltou para você (foi reprovado)
        - Cards com **👉 APROVAR** = você é representante do cliente
        - Copie o link para compartilhar sua visão com outros
        
        ### 🔄 Por que os números são iguais à Visão Geral?
        
        Usamos `status_cat` (categoria do status) em vez de procurar por texto no nome do status.
        Isso garante que "3 em desenvolvimento" aqui seja **exatamente** igual a "3 em desenvolvimento" na Visão Geral.
        """)
