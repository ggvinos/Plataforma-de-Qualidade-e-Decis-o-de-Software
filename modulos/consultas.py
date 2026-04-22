"""
================================================================================
MÓDULO CONSULTAS - NinaDash v8.82
================================================================================
Consultas Personalizadas

Dependências:
- streamlit, pandas, plotly, datetime
- modulos.config, modulos.utils, modulos.calculos, modulos.jira_api, modulos.processamento

Author: GitHub Copilot
Version: 1.0 (Phase 7)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

from modulos.config import (
    JIRA_BASE_URL, CUSTOM_FIELDS, STATUS_FLOW, STATUS_NOMES, STATUS_CORES,
    TOOLTIPS, REGRAS, PB_FUNIL_ETAPAS, TEMAS_NAO_CLIENTES
)
from modulos.utils import (
    link_jira, card_link_com_popup, traduzir_link,
    calcular_dias_necessarios_validacao, avaliar_janela_validacao, get_secrets
)
from modulos.calculos import (
    calcular_fator_k, calcular_ddp, calcular_fpy, calcular_lead_time,
    analisar_dev_detalhado, filtrar_qas_principais,
    calcular_concentracao_conhecimento, gerar_recomendacoes_rodizio,
    calcular_metricas_governanca, calcular_metricas_qa, calcular_metricas_produto,
    calcular_health_score, calcular_metricas_dev, calcular_metricas_backlog
)
from modulos.jira_api import (
    buscar_dados_jira_cached, buscar_card_especifico,
    gerar_icone_tabler, gerar_badge_status, obter_icone_status,
    extrair_historico_transicoes, extrair_texto_adf
)

from modulos.processamento import filtrar_df_por_consulta, aplicar_filtros_widget, calcular_periodo_datas


# ==============================================================================
# FUNÇÕES DO MÓDULO
# ==============================================================================

def inicializar_consultas_personalizadas():
    """Inicializa o sistema de consultas personalizadas, carregando do cookie se existir."""
    if 'consultas_salvas' not in st.session_state:
        # Tenta carregar do cookie
        try:
            cookie_manager = get_cookie_manager()
            consultas_cookie = cookie_manager.get(COOKIE_CONSULTAS_NAME)
            if consultas_cookie:
                import json
                st.session_state.consultas_salvas = json.loads(consultas_cookie)
            else:
                st.session_state.consultas_salvas = {}
        except:
            st.session_state.consultas_salvas = {}
    
    if 'modo_consulta_personalizada' not in st.session_state:
        st.session_state.modo_consulta_personalizada = False
    if 'consulta_atual' not in st.session_state:
        st.session_state.consulta_atual = None
    if 'consulta_executar' not in st.session_state:
        st.session_state.consulta_executar = None




def entrar_modo_consulta():
    """Ativa o modo de consulta personalizada."""
    st.session_state.modo_consulta_personalizada = True




def sair_modo_consulta():
    """Desativa o modo de consulta personalizada."""
    st.session_state.modo_consulta_personalizada = False
    st.session_state.consulta_atual = None




def salvar_consulta(nome: str, tipo: str, filtros: Dict):
    """Salva uma consulta personalizada no session_state e no cookie."""
    inicializar_consultas_personalizadas()
    st.session_state.consultas_salvas[nome] = {
        "nome": nome,
        "tipo": tipo,
        "filtros": filtros.copy(),
        "criado_em": datetime.now().isoformat()
    }
    _salvar_consultas_cookie()




def listar_consultas_salvas() -> Dict:
    """Lista todas as consultas salvas."""
    inicializar_consultas_personalizadas()
    return st.session_state.consultas_salvas




def excluir_consulta(nome: str):
    """Exclui uma consulta salva."""
    if nome in st.session_state.consultas_salvas:
        del st.session_state.consultas_salvas[nome]
        _salvar_consultas_cookie()






def renderizar_resultado_consulta(df_filtrado: pd.DataFrame, tipo: str, filtros: Dict):
    """Renderiza o resultado da consulta."""
    
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum resultado encontrado para os filtros selecionados.")
        return
    
    consulta = TIPOS_CONSULTA.get(tipo, {})
    visualizacao = consulta.get('visualizacao', 'lista_cards')
    
    # === VISUALIZAÇÃO: LISTA DE CARDS ===
    if visualizacao in ['lista_cards', 'lista_cards_bugs']:
        st.markdown(f"### 📋 {len(df_filtrado)} Cards Encontrados")
        
        # Métricas resumo
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Cards", len(df_filtrado))
        with col2:
            sp_total = int(df_filtrado['story_points'].sum())
            st.metric("Story Points", sp_total)
        with col3:
            bugs_total = int(df_filtrado['bugs_encontrados'].sum())
            st.metric("Bugs", bugs_total)
        with col4:
            concluidos = len(df_filtrado[df_filtrado['status_categoria'] == 'done'])
            st.metric("Concluídos", concluidos)
        
        st.markdown("---")
        
        # Lista de cards
        for _, row in df_filtrado.head(50).iterrows():
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    st.markdown(f"**[{row['key']}]({link_jira(row['key'])})**")
                with col2:
                    titulo = str(row.get('resumo', ''))[:80]
                    st.markdown(f"{titulo}")
                    st.caption(f"📌 {row.get('status', 'N/A')} | 👤 {row.get('responsavel', 'N/A')}")
                with col3:
                    sp = row.get('story_points', 0)
                    bugs = row.get('bugs_encontrados', 0)
                    st.markdown(f"**{sp} SP** | 🐛 {bugs}")
            st.markdown("---")
        
        if len(df_filtrado) > 50:
            st.info(f"Mostrando 50 de {len(df_filtrado)} cards. Refine os filtros para ver menos resultados.")
    
    # === VISUALIZAÇÃO: MÉTRICAS ===
    elif visualizacao == 'metricas':
        st.markdown("### 📊 Métricas Calculadas")
        
        # KPIs principais
        col1, col2, col3, col4 = st.columns(4)
        
        total_cards = len(df_filtrado)
        sp_total = int(df_filtrado['story_points'].sum())
        bugs_total = int(df_filtrado['bugs_encontrados'].sum())
        concluidos = len(df_filtrado[df_filtrado['status_categoria'] == 'done'])
        
        with col1:
            st.metric("Total Cards", total_cards)
        with col2:
            st.metric("Story Points", sp_total)
        with col3:
            st.metric("Bugs Encontrados", bugs_total)
        with col4:
            taxa_conclusao = (concluidos / total_cards * 100) if total_cards > 0 else 0
            st.metric("Taxa Conclusão", f"{taxa_conclusao:.1f}%")
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Fator K
            fk = sp_total / (bugs_total + 1)
            st.metric("Fator K", f"{fk:.2f}", help="SP / (Bugs + 1)")
        
        with col2:
            # FPY
            sem_bugs = len(df_filtrado[df_filtrado['bugs_encontrados'] == 0])
            fpy = (sem_bugs / total_cards * 100) if total_cards > 0 else 0
            st.metric("FPY", f"{fpy:.1f}%", help="Cards sem bugs / Total")
        
        with col3:
            # Média SP
            media_sp = df_filtrado['story_points'].mean() if total_cards > 0 else 0
            st.metric("Média SP/Card", f"{media_sp:.1f}")
        
        # Gráfico de status
        st.markdown("---")
        st.markdown("#### 📈 Distribuição por Status")
        status_counts = df_filtrado['status'].value_counts()
        fig = px.bar(x=status_counts.index, y=status_counts.values, labels={'x': 'Status', 'y': 'Quantidade'})
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # === VISUALIZAÇÃO: COMPARATIVO ===
    elif visualizacao == 'comparativo':
        st.markdown("### ⚖️ Comparativo")
        
        pessoas = filtros.get('pessoas_multiplas', [])
        if not pessoas:
            st.warning("Selecione pessoas para comparar")
            return
        
        dados_comparativo = []
        for pessoa in pessoas:
            df_pessoa = df_filtrado[
                df_filtrado['responsavel'].str.contains(pessoa, case=False, na=False) |
                df_filtrado['qa_responsavel'].str.contains(pessoa, case=False, na=False)
            ]
            dados_comparativo.append({
                'Pessoa': pessoa,
                'Cards': len(df_pessoa),
                'SP': int(df_pessoa['story_points'].sum()),
                'Bugs': int(df_pessoa['bugs_encontrados'].sum()),
                'FK': round(df_pessoa['story_points'].sum() / (df_pessoa['bugs_encontrados'].sum() + 1), 2)
            })
        
        df_comp = pd.DataFrame(dados_comparativo)
        st.dataframe(df_comp, use_container_width=True, hide_index=True)
        
        # Gráfico comparativo
        fig = px.bar(df_comp, x='Pessoa', y=['Cards', 'SP', 'Bugs'], barmode='group')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # === VISUALIZAÇÃO: FATOR K DETALHADO ===
    elif visualizacao == 'metricas_fk':
        st.markdown("### 🎯 Análise Fator K Detalhado")
        
        # Por desenvolvedor
        fk_dev = df_filtrado.groupby('responsavel').agg({
            'story_points': 'sum',
            'bugs_encontrados': 'sum',
            'key': 'count'
        }).reset_index()
        fk_dev.columns = ['Desenvolvedor', 'SP', 'Bugs', 'Cards']
        fk_dev['Fator K'] = fk_dev['SP'] / (fk_dev['Bugs'] + 1)
        fk_dev = fk_dev.sort_values('Fator K', ascending=False)
        
        st.dataframe(fk_dev.head(15), use_container_width=True, hide_index=True)
        
        # Gráfico
        fig = px.bar(fk_dev.head(10), x='Desenvolvedor', y='Fator K', color='Fator K',
                    color_continuous_scale='RdYlGn')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)




def tela_consulta_personalizada(df_todos: pd.DataFrame):
    """Renderiza a tela de Meu Dashboard - Dashboard Builder personalizado."""
    
    inicializar_meu_dashboard()
    
    # ===============================================
    # HEADER
    # ===============================================
    st.markdown("""
    <div style="text-align: center; padding: 10px 0 20px;">
        <h1 style="color: #AF0C37; margin: 0; font-size: 2em;">🎨 Meu Dashboard</h1>
        <p style="color: #666; font-size: 1em; margin-top: 5px;">Monte seu dashboard personalizado</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ===============================================
    # DEBUG: Mostra dados carregados
    # ===============================================
    st.info(f"📊 Dados carregados: {len(df_todos)} cards de {df_todos['projeto'].nunique() if 'projeto' in df_todos.columns else 0} projetos")
    
    # ===============================================
    # SEÇÃO 1: CONSTRUTOR DE WIDGET (TOPO)
    # ===============================================
    st.markdown("### ➕ Adicionar Widget")
    
    # Coleta lista de pessoas ANTES de renderizar os filtros
    pessoas_lista = []
    if 'responsavel' in df_todos.columns:
        responsaveis = df_todos['responsavel'].dropna().unique().tolist()
        pessoas_lista.extend([p for p in responsaveis if p and p != 'Não atribuído' and len(str(p)) > 2])
    if 'qa_responsavel' in df_todos.columns:
        qas = df_todos['qa_responsavel'].dropna().unique().tolist()
        pessoas_lista.extend([p for p in qas if p and p not in pessoas_lista and len(str(p)) > 2])
    pessoas_lista = sorted(list(set(pessoas_lista)))
    
    # DEBUG: Mostra quantas pessoas encontrou
    st.caption(f"👥 {len(pessoas_lista)} pessoas encontradas nos dados")
    
    # Linha 1: Tipo de widget
    col_tipo = st.columns([1])[0]
    with col_tipo:
        # Lista todos os widgets disponíveis
        opcoes_widgets = list(CATALOGO_WIDGETS.keys())
        
        tipo_widget = st.selectbox(
            "📊 Selecione o tipo de visualização",
            options=opcoes_widgets,
            format_func=lambda x: f"{CATALOGO_WIDGETS[x]['nome']} - {CATALOGO_WIDGETS[x]['descricao']}",
            key="select_tipo_widget_novo"
        )
    
    # Linha 2: Filtros em colunas
    st.markdown("**Filtros (opcional):**")
    col_pessoa, col_status, col_periodo = st.columns(3)
    
    with col_pessoa:
        pessoa_selecionada = st.selectbox(
            "👤 Pessoa",
            options=["Todos"] + pessoas_lista,
            key="filtro_pessoa_novo",
            help="Filtra por responsável, QA ou relator"
        )
    
    with col_status:
        status_selecionado = st.selectbox(
            "🏷️ Status",
            options=list(STATUS_FILTRO.keys()),
            format_func=lambda x: STATUS_FILTRO[x],
            key="filtro_status_novo"
        )
    
    with col_periodo:
        periodo_selecionado = st.selectbox(
            "📅 Período",
            options=list(PERIODOS_PREDEFINIDOS.keys()),
            format_func=lambda x: PERIODOS_PREDEFINIDOS[x],
            key="filtro_periodo_novo",
            index=5  # Todo o Período
        )
    
    # Botão de adicionar
    if st.button("➕ ADICIONAR WIDGET AO DASHBOARD", type="primary", use_container_width=True, key="btn_add_widget_novo"):
        filtros_novos = {
            "pessoa": pessoa_selecionada,
            "status": status_selecionado,
            "periodo": periodo_selecionado
        }
        adicionar_widget(tipo_widget, filtros_novos)
        st.success(f"✅ Widget '{CATALOGO_WIDGETS[tipo_widget]['nome']}' adicionado!")
        st.rerun()
    
    st.markdown("---")
    
    # ===============================================
    # SEÇÃO 2: WIDGETS ADICIONADOS (ABAIXO)
    # ===============================================
    widgets = st.session_state.get('meu_dashboard_widgets', [])
    
    if not widgets:
        # Estado vazio
        st.markdown("""
        <div style="text-align: center; padding: 40px 20px; background: #f8f9fa; 
                    border-radius: 10px; border: 2px dashed #dee2e6;">
            <h3 style="color: #6c757d; margin: 0;">📭 Seu dashboard está vazio</h3>
            <p style="color: #adb5bd; margin-top: 10px;">Selecione um tipo de widget acima e clique em "Adicionar"</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 💡 Ou comece com um template pronto:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Visão Executiva", use_container_width=True, key="tpl_exec"):
                adicionar_widget("kpi_total_cards", {"periodo": "todo_periodo"})
                adicionar_widget("kpi_story_points", {"periodo": "todo_periodo"})
                adicionar_widget("kpi_fator_k", {"periodo": "todo_periodo"})
                adicionar_widget("grafico_status", {"periodo": "todo_periodo"})
                st.rerun()
        
        with col2:
            if st.button("👨‍💻 Foco DEV", use_container_width=True, key="tpl_dev"):
                adicionar_widget("tabela_ranking_devs", {"periodo": "todo_periodo"})
                adicionar_widget("grafico_bugs_dev", {"periodo": "todo_periodo"})
                st.rerun()
        
        with col3:
            if st.button("🔬 Foco QA", use_container_width=True, key="tpl_qa"):
                adicionar_widget("kpi_bugs", {"periodo": "todo_periodo"})
                adicionar_widget("tabela_aging", {"status": "todos"})
                st.rerun()
    
    else:
        # Mostra contagem e botão limpar
        col_info, col_limpar = st.columns([4, 1])
        with col_info:
            st.markdown(f"### 📊 Seus Widgets ({len(widgets)})")
        with col_limpar:
            if st.button("🗑️ Limpar Tudo", key="btn_limpar"):
                st.session_state.meu_dashboard_widgets = []
                _salvar_dashboard_cookie()
                st.rerun()
        
        # Renderiza cada widget
        for idx, widget in enumerate(widgets):
            with st.container():
                # Header do widget
                col_titulo, col_acoes = st.columns([5, 1])
                
                widget_info = CATALOGO_WIDGETS.get(widget.get('tipo', ''), {})
                
                with col_titulo:
                    st.markdown(f"#### {widget_info.get('nome', widget.get('tipo', 'Widget'))}")
                    
                    # Mostra filtros aplicados
                    filtros = widget.get('filtros', {})
                    filtros_txt = []
                    if filtros.get('pessoa') and filtros['pessoa'] != 'Todos':
                        filtros_txt.append(f"👤 {filtros['pessoa']}")
                    if filtros.get('status') and filtros['status'] != 'todos':
                        filtros_txt.append(f"🏷️ {STATUS_FILTRO.get(filtros['status'], '')}")
                    if filtros.get('periodo'):
                        filtros_txt.append(f"📅 {PERIODOS_PREDEFINIDOS.get(filtros['periodo'], '')}")
                    if filtros_txt:
                        st.caption(" | ".join(filtros_txt))
                
                with col_acoes:
                    col_up, col_down, col_del = st.columns(3)
                    with col_up:
                        if idx > 0 and st.button("⬆️", key=f"up_{idx}"):
                            mover_widget_cima(widget['id'])
                            st.rerun()
                    with col_down:
                        if idx < len(widgets) - 1 and st.button("⬇️", key=f"down_{idx}"):
                            mover_widget_baixo(widget['id'])
                            st.rerun()
                    with col_del:
                        if st.button("🗑️", key=f"del_{idx}"):
                            remover_widget(widget['id'])
                            st.rerun()
                
                # Renderiza conteúdo do widget
                filtros = widget.get('filtros', {})
                df_widget = aplicar_filtros_widget(df_todos.copy(), filtros)
                
                if df_widget.empty:
                    st.warning("Nenhum dado encontrado para os filtros aplicados")
                else:
                    tipo = widget.get('tipo', '')
                    tipo_viz = widget_info.get('tipo', 'kpi')
                    
                    if tipo_viz == 'kpi':
                        renderizar_kpi_widget(tipo, df_widget)
                    elif tipo_viz == 'grafico_barra':
                        renderizar_grafico_widget(tipo, df_widget)
                    elif tipo_viz == 'tabela':
                        renderizar_tabela_widget(tipo, df_widget)
                    elif tipo_viz == 'lista':
                        renderizar_lista_widget(tipo, df_widget, filtros)
                
                st.markdown("---")


# Mantém compatibilidade com a função antiga mas redireciona para nova


