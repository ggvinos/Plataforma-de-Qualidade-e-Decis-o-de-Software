"""
================================================================================
MÓDULO WIDGETS - NinaDash v8.82
================================================================================
Widgets - Componentes reutilizáveis de UI

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

from modulos.processamento import aplicar_filtros_widget
from modulos.utils import link_jira


# ==============================================================================
# FUNÇÕES DO MÓDULO
# ==============================================================================

def mostrar_tooltip(metrica_key: str):
    """Mostra tooltip explicativo de uma métrica."""
    if metrica_key not in TOOLTIPS:
        return
    
    tooltip = TOOLTIPS[metrica_key]
    with st.expander(f"ℹ️ O que é {tooltip['titulo']}?", expanded=False):
        st.markdown(f"**{tooltip['descricao']}**")
        st.code(tooltip['formula'], language="text")
        st.markdown("**Interpretação:**")
        for nivel, desc in tooltip['interpretacao'].items():
            st.markdown(f"- {nivel}: {desc}")
        st.caption(f"📚 Fonte: {tooltip['fonte']}")


# ==============================================================================
# CONSULTAS PERSONALIZADAS - SISTEMA DE MÉTRICAS AVANÇADAS
# ==============================================================================

# Tipos de consulta disponíveis
TIPOS_CONSULTA = {
    "cards_pessoa": {
        "nome": "📋 Cards de uma Pessoa",
        "descricao": "Lista de cards filtrados por pessoa (responsável, QA, relator)",
        "filtros": ["pessoa", "papel_pessoa", "status", "periodo"],
        "visualizacao": "lista_cards"
    },
    "metricas_pessoa": {
        "nome": "📊 Métricas de uma Pessoa", 
        "descricao": "KPIs e métricas agregadas para uma pessoa específica",
        "filtros": ["pessoa", "papel_pessoa", "periodo"],
        "visualizacao": "metricas"
    },
    "cards_status": {
        "nome": "🏷️ Cards por Status",
        "descricao": "Cards filtrados por status específico",
        "filtros": ["status", "pessoa", "periodo"],
        "visualizacao": "lista_cards"
    },
    "cards_produto": {
        "nome": "📦 Cards por Produto",
        "descricao": "Cards filtrados por produto",
        "filtros": ["produto", "status", "pessoa", "periodo"],
        "visualizacao": "lista_cards"
    },
    "comparativo_pessoas": {
        "nome": "⚖️ Comparativo entre Pessoas",
        "descricao": "Compare métricas entre várias pessoas",
        "filtros": ["pessoas_multiplas", "papel_pessoa", "periodo"],
        "visualizacao": "comparativo"
    },
    "tendencia_periodo": {
        "nome": "📈 Tendência por Período",
        "descricao": "Evolução de métricas ao longo do tempo",
        "filtros": ["metrica", "pessoa", "periodo_range"],
        "visualizacao": "grafico_linha"
    },
    "bugs_analise": {
        "nome": "🐛 Análise de Bugs",
        "descricao": "Bugs encontrados com filtros avançados",
        "filtros": ["pessoa", "papel_pessoa", "produto", "periodo"],
        "visualizacao": "lista_cards_bugs"
    },
    "fator_k_detalhado": {
        "nome": "🎯 Fator K Detalhado",
        "descricao": "Análise detalhada do Fator K por pessoa/produto",
        "filtros": ["pessoa", "produto", "periodo"],
        "visualizacao": "metricas_fk"
    },
}

# Status disponíveis para filtro
STATUS_FILTRO = {
    "todos": "Todos os status",
    "concluido": "✅ Concluído",
    "em_andamento": "🔄 Em Andamento",
    "em_validacao": "🧪 Em Validação/QA",
    "aguardando_qa": "⏳ Aguardando QA",
    "code_review": "👀 Code Review",
    "impedido": "🚫 Impedido/Bloqueado",
    "reprovado": "❌ Reprovado",
    "backlog": "📋 Backlog",
}

# Papéis de pessoa
PAPEIS_PESSOA = {
    "qualquer": "Qualquer papel",
    "responsavel": "👨‍💻 Responsável/Dev",
    "qa": "🔬 QA Responsável",
    "relator": "📝 Relator/Criador",
}

# Períodos predefinidos
PERIODOS_PREDEFINIDOS = {
    "sprint_atual": "Sprint Atual",
    "ultima_semana": "Última Semana",
    "ultimas_2_semanas": "Últimas 2 Semanas",
    "ultimo_mes": "Último Mês",
    "ultimos_3_meses": "Últimos 3 Meses",
    "todo_periodo": "Todo o Período",
    "personalizado": "📅 Período Personalizado",
}

# ===============================================================================
# CATÁLOGO DE WIDGETS PARA MEU DASHBOARD
# ===============================================================================

CATALOGO_WIDGETS = {
    # === KPIs SIMPLES ===
    "kpi_total_cards": {
        "nome": "📋 Total de Cards",
        "categoria": "📊 KPIs",
        "descricao": "Total de cards no período",
        "tipo": "kpi",
        "filtros": ["pessoa", "status", "periodo"],
    },
    "kpi_story_points": {
        "nome": "⭐ Story Points",
        "categoria": "📊 KPIs",
        "descricao": "Total de Story Points",
        "tipo": "kpi",
        "filtros": ["pessoa", "status", "periodo"],
    },
    "kpi_bugs": {
        "nome": "🐛 Total de Bugs",
        "categoria": "📊 KPIs",
        "descricao": "Quantidade de bugs encontrados",
        "tipo": "kpi",
        "filtros": ["pessoa", "periodo"],
    },
    "kpi_fator_k": {
        "nome": "🎯 Fator K",
        "categoria": "📊 KPIs",
        "descricao": "Razão SP/Bugs (qualidade)",
        "tipo": "kpi",
        "filtros": ["pessoa", "periodo"],
    },
    "kpi_fpy": {
        "nome": "✅ FPY",
        "categoria": "📊 KPIs",
        "descricao": "First Pass Yield - % aprovados de primeira",
        "tipo": "kpi",
        "filtros": ["pessoa", "periodo"],
    },
    "kpi_taxa_conclusao": {
        "nome": "🏁 Taxa de Conclusão",
        "categoria": "📊 KPIs",
        "descricao": "% de cards concluídos",
        "tipo": "kpi",
        "filtros": ["pessoa", "periodo"],
    },
    
    # === GRÁFICOS ===
    "grafico_status": {
        "nome": "📊 Gráfico por Status",
        "categoria": "📈 Gráficos",
        "descricao": "Distribuição de cards por status",
        "tipo": "grafico_barra",
        "filtros": ["pessoa", "periodo"],
    },
    "grafico_produto": {
        "nome": "📦 Gráfico por Produto",
        "categoria": "📈 Gráficos",
        "descricao": "Distribuição de cards por produto",
        "tipo": "grafico_barra",
        "filtros": ["pessoa", "periodo"],
    },
    "grafico_responsavel": {
        "nome": "👤 Gráfico por Responsável",
        "categoria": "📈 Gráficos",
        "descricao": "Cards por responsável",
        "tipo": "grafico_barra",
        "filtros": ["status", "periodo"],
    },
    "grafico_bugs_dev": {
        "nome": "🐛 Bugs por Dev",
        "categoria": "📈 Gráficos",
        "descricao": "Bugs encontrados por desenvolvedor",
        "tipo": "grafico_barra",
        "filtros": ["periodo"],
    },
    
    # === TABELAS ===
    "tabela_ranking_devs": {
        "nome": "🏆 Ranking Devs",
        "categoria": "📋 Tabelas",
        "descricao": "Ranking de desenvolvedores por Fator K",
        "tipo": "tabela",
        "filtros": ["periodo"],
    },
    "tabela_cards_recentes": {
        "nome": "🕐 Cards Recentes",
        "categoria": "📋 Tabelas",
        "descricao": "Últimos cards atualizados",
        "tipo": "tabela",
        "filtros": ["pessoa", "status"],
    },
    "tabela_aging": {
        "nome": "⏰ Aging",
        "categoria": "📋 Tabelas",
        "descricao": "Cards há muito tempo parados",
        "tipo": "tabela",
        "filtros": ["status"],
    },
    
    # === LISTAS ===
    "lista_cards_pessoa": {
        "nome": "📋 Cards de uma Pessoa",
        "categoria": "📝 Listas",
        "descricao": "Lista de cards de uma pessoa específica",
        "tipo": "lista",
        "filtros": ["pessoa", "papel_pessoa", "status", "periodo"],
    },
    "lista_bugs": {
        "nome": "🐛 Lista de Bugs",
        "categoria": "📝 Listas",
        "descricao": "Lista de bugs encontrados",
        "tipo": "lista",
        "filtros": ["pessoa", "periodo"],
    },
}

# Nome do cookie para consultas salvas
COOKIE_CONSULTAS_NAME = "ninadash_consultas_salvas"
COOKIE_DASHBOARD_NAME = "ninadash_meu_dashboard"




def renderizar_widget(widget: Dict, df: pd.DataFrame, idx: int, total: int):
    """Renderiza um widget individual com controles."""
    
    tipo = widget['tipo']
    filtros = widget.get('filtros', {})
    widget_info = CATALOGO_WIDGETS.get(tipo, {})
    
    # Aplica filtros ao DataFrame
    df_filtrado = aplicar_filtros_widget(df, filtros)
    
    # Container do widget com borda
    with st.container():
        # Header do widget com controles
        col_titulo, col_controles = st.columns([4, 1])
        
        with col_titulo:
            st.markdown(f"#### {widget_info.get('nome', tipo)}")
            # Mostra filtros ativos
            filtros_texto = []
            if filtros.get('pessoa') and filtros['pessoa'] != 'Todos':
                filtros_texto.append(f"👤 {filtros['pessoa']}")
            if filtros.get('status') and filtros['status'] != 'todos':
                filtros_texto.append(f"🏷️ {STATUS_FILTRO.get(filtros['status'], filtros['status'])}")
            if filtros.get('periodo'):
                filtros_texto.append(f"📅 {PERIODOS_PREDEFINIDOS.get(filtros['periodo'], filtros['periodo'])}")
            if filtros_texto:
                st.caption(" | ".join(filtros_texto))
        
        with col_controles:
            col_up, col_down, col_del = st.columns(3)
            with col_up:
                if idx > 0:
                    if st.button("⬆️", key=f"up_{widget['id']}", help="Mover para cima"):
                        mover_widget_cima(widget['id'])
                        st.rerun()
            with col_down:
                if idx < total - 1:
                    if st.button("⬇️", key=f"down_{widget['id']}", help="Mover para baixo"):
                        mover_widget_baixo(widget['id'])
                        st.rerun()
            with col_del:
                if st.button("🗑️", key=f"del_{widget['id']}", help="Remover"):
                    remover_widget(widget['id'])
                    st.rerun()
        
        # Conteúdo do widget
        tipo_viz = widget_info.get('tipo', 'kpi')
        
        if df_filtrado.empty:
            st.info("Nenhum dado para os filtros selecionados")
        elif tipo_viz == 'kpi':
            renderizar_kpi_widget(tipo, df_filtrado)
        elif tipo_viz == 'grafico_barra':
            renderizar_grafico_widget(tipo, df_filtrado)
        elif tipo_viz == 'tabela':
            renderizar_tabela_widget(tipo, df_filtrado)
        elif tipo_viz == 'lista':
            renderizar_lista_widget(tipo, df_filtrado, filtros)
        
        st.markdown("---")





def renderizar_kpi_widget(tipo: str, df: pd.DataFrame):
    """Renderiza um widget KPI."""
    
    if tipo == "kpi_total_cards":
        valor = len(df)
        st.metric("Total de Cards", f"{valor:,}")
    
    elif tipo == "kpi_story_points":
        valor = int(df['story_points'].sum())
        st.metric("Story Points", f"{valor:,}")
    
    elif tipo == "kpi_bugs":
        valor = int(df['bugs_encontrados'].sum())
        st.metric("Bugs Encontrados", f"{valor:,}")
    
    elif tipo == "kpi_fator_k":
        sp = df['story_points'].sum()
        bugs = df['bugs_encontrados'].sum()
        fk = sp / (bugs + 1)
        cor = "normal" if fk >= 3 else "inverse"
        st.metric("Fator K", f"{fk:.2f}", help="SP / (Bugs + 1)")
    
    elif tipo == "kpi_fpy":
        total = len(df)
        sem_bugs = len(df[df['bugs_encontrados'] == 0])
        fpy = (sem_bugs / total * 100) if total > 0 else 0
        st.metric("FPY", f"{fpy:.1f}%", help="Cards sem bugs")
    
    elif tipo == "kpi_taxa_conclusao":
        total = len(df)
        concluidos = len(df[df['status_categoria'] == 'done'])
        taxa = (concluidos / total * 100) if total > 0 else 0
        st.metric("Taxa Conclusão", f"{taxa:.1f}%")




def renderizar_grafico_widget(tipo: str, df: pd.DataFrame):
    """Renderiza um widget de gráfico."""
    
    if tipo == "grafico_status":
        contagem = df['status'].value_counts().head(10)
        fig = px.bar(x=contagem.index, y=contagem.values, labels={'x': 'Status', 'y': 'Quantidade'})
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    elif tipo == "grafico_produto":
        contagem = df['produto'].value_counts().head(10)
        fig = px.bar(x=contagem.index, y=contagem.values, labels={'x': 'Produto', 'y': 'Quantidade'})
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    elif tipo == "grafico_responsavel":
        contagem = df['responsavel'].value_counts().head(10)
        fig = px.bar(x=contagem.index, y=contagem.values, labels={'x': 'Responsável', 'y': 'Quantidade'})
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    elif tipo == "grafico_bugs_dev":
        bugs_dev = df.groupby('responsavel')['bugs_encontrados'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(x=bugs_dev.index, y=bugs_dev.values, labels={'x': 'Desenvolvedor', 'y': 'Bugs'})
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)




def renderizar_tabela_widget(tipo: str, df: pd.DataFrame):
    """Renderiza um widget de tabela."""
    
    if tipo == "tabela_ranking_devs":
        ranking = df.groupby('responsavel').agg({
            'story_points': 'sum',
            'bugs_encontrados': 'sum',
            'key': 'count'
        }).reset_index()
        ranking.columns = ['Desenvolvedor', 'SP', 'Bugs', 'Cards']
        ranking['FK'] = (ranking['SP'] / (ranking['Bugs'] + 1)).round(2)
        ranking = ranking.sort_values('FK', ascending=False).head(10)
        st.dataframe(ranking, use_container_width=True, hide_index=True, height=300)
    
    elif tipo == "tabela_cards_recentes":
        colunas = ['key', 'resumo', 'responsavel', 'status', 'story_points']
        colunas_existentes = [c for c in colunas if c in df.columns]
        df_recentes = df[colunas_existentes].head(10)
        st.dataframe(df_recentes, use_container_width=True, hide_index=True, height=300)
    
    elif tipo == "tabela_aging":
        # Cards parados há mais de 7 dias
        if 'data_atualizacao' in df.columns:
            df['data_atualizacao_dt'] = pd.to_datetime(df['data_atualizacao'], errors='coerce')
            df['dias_parado'] = (datetime.now() - df['data_atualizacao_dt'].dt.tz_localize(None)).dt.days
            aging = df[df['dias_parado'] > 7][['key', 'resumo', 'status', 'dias_parado']].sort_values('dias_parado', ascending=False).head(10)
            st.dataframe(aging, use_container_width=True, hide_index=True, height=300)
        else:
            st.info("Dados de atualização não disponíveis")




def renderizar_lista_widget(tipo: str, df: pd.DataFrame, filtros: Dict):
    """Renderiza um widget de lista de cards."""
    
    if tipo in ["lista_cards_pessoa", "lista_bugs"]:
        for _, row in df.head(15).iterrows():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"**[{row['key']}]({link_jira(row['key'])})**")
            with col2:
                titulo = str(row.get('resumo', ''))[:60]
                st.markdown(f"{titulo}")
                st.caption(f"👤 {row.get('responsavel', 'N/A')} | 📌 {row.get('status', 'N/A')}")
        
        if len(df) > 15:
            st.caption(f"... e mais {len(df) - 15} cards")




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




def renderizar_metrica_personalizada(metrica_key: str, df: pd.DataFrame):
    """Renderiza uma métrica do catálogo no dashboard personalizado."""
    if metrica_key not in CATALOGO_METRICAS:
        st.warning(f"⚠️ Métrica '{metrica_key}' não encontrada")
        return
    
    metrica = CATALOGO_METRICAS[metrica_key]
    tipo = metrica["tipo"]
    
    # Header da métrica
    st.markdown(f"#### {metrica['nome']}")
    st.caption(metrica['descricao'])
    
    try:
        # === KPIs (números simples) ===
        if tipo == "kpi":
            valor = calcular_valor_metrica(metrica_key, df)
            if valor is not None:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.metric(label=metrica['nome'], value=valor)
        
        # === Gráficos de Barra ===
        elif tipo == "grafico_barra":
            dados = calcular_dados_grafico(metrica_key, df)
            if dados is not None and not dados.empty:
                fig = px.bar(dados, x=dados.index, y=dados.values, 
                           title=metrica['nome'],
                           labels={'x': '', 'y': 'Quantidade'})
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        # === Gráficos de Pizza ===
        elif tipo == "grafico_pizza":
            dados = calcular_dados_grafico(metrica_key, df)
            if dados is not None and not dados.empty:
                fig = px.pie(values=dados.values, names=dados.index,
                           title=metrica['nome'])
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        # === Tabelas ===
        elif tipo == "tabela":
            dados = calcular_dados_tabela(metrica_key, df)
            if dados is not None and not dados.empty:
                st.dataframe(dados, use_container_width=True, height=250)
        
        # === Listas de Cards ===
        elif tipo == "lista_cards":
            cards = calcular_lista_cards(metrica_key, df)
            if cards is not None and len(cards) > 0:
                for card in cards[:10]:  # Limita a 10 cards
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.markdown(f"**{card.get('key', 'N/A')}**")
                    with col2:
                        titulo = card.get('titulo', card.get('resumo', ''))[:60]
                        st.markdown(f"{titulo}")
            else:
                st.info("Nenhum card encontrado")
        
        # === Heatmaps ===
        elif tipo == "heatmap":
            dados = calcular_dados_heatmap(metrica_key, df)
            if dados is not None and not dados.empty:
                fig = px.imshow(dados, aspect='auto', color_continuous_scale='RdYlGn',
                              title=metrica['nome'])
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
        
        # === Funil ===
        elif tipo == "grafico_funil":
            dados = calcular_dados_funil(metrica_key, df)
            if dados:
                criar_grafico_funil_personalizado(dados, metrica['nome'])
        
        else:
            st.info(f"Tipo de visualização '{tipo}' em desenvolvimento")
            
    except Exception as e:
        st.error(f"Erro ao renderizar métrica: {str(e)}")




def mostrar_header_nina():
    """Mostra header principal com logo SVG da Nina."""
    # Logo SVG da Nina (vermelho #AF0C37)
    logo_svg = '''<svg width="60" height="60" viewBox="0 0 187 187" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M173.709 89.2107C172.209 86.6048 169.414 84.838 166.225 84.838C163.036 84.838 160.241 86.5649 158.741 89.1627H151.683C149.465 58.8237 124.495 35 94.0216 35C63.5489 35 38.5862 58.8237 36.3678 89.1627H29.1759C27.6759 86.5649 24.8734 84.798 21.6682 84.798C18.463 84.798 15.6605 86.5806 14.1605 89.2031C13.4184 90.4899 13 92.001 13 93.6C13 95.1987 13.4184 96.7017 14.1605 97.997C15.6605 100.619 18.463 102.306 21.6682 102.306C24.8734 102.306 27.6838 100.435 29.1759 97.8369H36.3678C38.5862 128.168 63.5489 152 94.0216 152C124.495 152 149.465 128.176 151.675 97.8369H158.686C160.178 100.435 162.996 102.354 166.217 102.354C169.438 102.354 172.256 100.611 173.749 97.9648C174.475 96.6856 174.885 95.2148 174.885 93.6319C174.885 92.049 174.451 90.5222 173.701 89.2188L173.709 89.2107ZM111.145 125.554C107.971 131.518 101.758 135.459 94.5981 135.459C87.4374 135.459 81.2248 131.566 78.0509 125.602C77.1666 123.947 78.3667 122.092 80.2219 122.092H108.982C110.837 122.092 112.029 123.891 111.153 125.554H111.145ZM140.528 94.1277C140.528 103.825 132.76 111.691 123.184 111.691H65.4432C55.8675 111.691 48.0991 103.825 48.0991 94.1277V93.7199C48.0991 84.0223 55.8675 76.1557 65.4432 76.1557H123.184C132.76 76.1557 140.528 84.0223 140.528 93.7199V94.1277Z" fill="#AF0C37"/>
    <path d="M76.5809 105.311C82.9686 105.311 88.1466 100.068 88.1466 93.5996C88.1466 87.1312 82.9686 81.8875 76.5809 81.8875C70.1936 81.8875 65.0156 87.1312 65.0156 93.5996C65.0156 100.068 70.1936 105.311 76.5809 105.311Z" fill="#AF0C37"/>
    <path d="M111.437 105.311C117.824 105.311 123.002 100.068 123.002 93.5996C123.002 87.1312 117.824 81.8875 111.437 81.8875C105.049 81.8875 99.8712 87.1312 99.8712 93.5996C99.8712 100.068 105.049 105.311 111.437 105.311Z" fill="#AF0C37"/>
    </svg>'''
    
    st.markdown(f"""
    <div class="nina-header">
        <div class="nina-logo">{logo_svg}</div>
        <div>
            <p class="nina-title"><span class="nina-highlight">NinaDash</span> — Dashboard de Qualidade e Decisão de Software</p>
            <p class="nina-subtitle">📊 Visibilidade, métricas e decisões inteligentes para todo o time</p>
        </div>
    </div>
    """, unsafe_allow_html=True)




def mostrar_indicador_atualizacao(ultima_atualizacao: datetime):
    """Mostra indicador de última atualização."""
    agora = datetime.now()
    diff = (agora - ultima_atualizacao).total_seconds() / 60
    
    if diff < 1:
        texto = "Atualizado agora"
        classe = "update-badge"
    elif diff < REGRAS['cache_ttl_minutos']:
        texto = f"Atualizado há {int(diff)} min"
        classe = "update-badge"
    else:
        texto = f"Dados de {int(diff)} min atrás"
        classe = "update-badge update-badge-stale"
    
    st.markdown(f'<span class="{classe}">🕐 {texto}</span>', unsafe_allow_html=True)




def mostrar_card_ticket(row: dict, compacto: bool = False):
    """Mostra card de ticket COM LINK para Jira."""
    html = gerar_html_card_ticket(row, compacto)
    st.markdown(html, unsafe_allow_html=True)




def mostrar_lista_tickets_completa(items: list, titulo: str, mostrar_todos: bool = False, max_height: int = 450):
    """
    Mostra lista de tickets com scroll individual e opção de ver TODOS.
    
    Args:
        items: Lista de dicionários com dados dos cards
        titulo: Título da seção
        mostrar_todos: Se True, mostra todos os cards (sem limite inicial)
        max_height: Altura máxima do container de scroll (default 450px)
    """
    if not items:
        st.info(f"Nenhum card em: {titulo}")
        return
    
    total = len(items)
    
    with st.expander(f"📋 {titulo} ({total} cards)", expanded=False):
        # Checkbox para mostrar todos
        if total > 5:
            mostrar_todos = st.checkbox(f"Mostrar todos os {total} cards", key=f"mostrar_todos_{titulo}", value=mostrar_todos)
        else:
            mostrar_todos = True
        
        limite = total if mostrar_todos else min(5, total)
        
        # Construir HTML completo em string única (necessário para scroll funcionar)
        html_lista = f'<div class="scroll-container" style="max-height: {max_height}px;">'
        
        for i, item in enumerate(items[:limite]):
            if isinstance(item, dict):
                html_lista += gerar_html_card_ticket(item, compacto=True)
            elif isinstance(item, pd.Series):
                html_lista += gerar_html_card_ticket(item.to_dict(), compacto=True)
        
        html_lista += '</div>'
        st.markdown(html_lista, unsafe_allow_html=True)
        
        if not mostrar_todos and total > 5:
            st.caption(f"📌 Mais {total - 5} cards ocultos. Marque acima para ver todos.")




def mostrar_lista_df_completa(df: pd.DataFrame, titulo: str):
    """Mostra lista de tickets de um DataFrame com opção de ver todos."""
    if df.empty:
        st.info(f"Nenhum card em: {titulo}")
        return
    
    items = df.to_dict('records')
    mostrar_lista_tickets_completa(items, titulo)




def renderizar_lista_com_scroll(df: pd.DataFrame, titulo: str = None, max_height: int = 400, 
                                 cor_classe: str = "", mostrar_checkbox: bool = True,
                                 limite_inicial: int = 20, key_prefix: str = "lista",
                                 campos_customizados: dict = None):
    """
    Renderiza uma lista de cards com scroll individual usando design padronizado.
    
    Args:
        df: DataFrame com os cards
        titulo: Título opcional da seção (se None, não mostra título)
        max_height: Altura máxima do container de scroll
        cor_classe: Classe CSS de cor (amarelo, verde, azul, roxo, vermelho, laranja)
        mostrar_checkbox: Se True, mostra checkbox "Ver todos"
        limite_inicial: Limite inicial de cards (se checkbox ativo)
        key_prefix: Prefixo para keys do Streamlit (evitar duplicatas)
        campos_customizados: Dict com campos customizados a exibir {campo: label}
    
    Returns:
        None (renderiza diretamente no Streamlit)
    """
    if df.empty:
        st.info("Nenhum card encontrado.")
        return
    
    total = len(df)
    
    # Checkbox para ver todos
    mostrar_todos = False
    if mostrar_checkbox and total > limite_inicial:
        mostrar_todos = st.checkbox(
            f"📋 Ver todos os {total} cards", 
            key=f"{key_prefix}_ver_todos_{titulo or 'lista'}",
            value=False
        )
    else:
        mostrar_todos = True
    
    limite = total if mostrar_todos else min(limite_inicial, total)
    
    # Título se especificado
    if titulo:
        st.markdown(f"##### {titulo} ({total})")
    
    # Container com scroll
    cards_html = f'<div class="scroll-container" style="max-height: {max_height}px;">'
    
    for _, card in df.head(limite).iterrows():
        projeto = card.get('projeto', 'SD')
        tipo = card.get('tipo', 'TAREFA')
        tipo_cor = "#ef4444" if tipo == "HOTFIX" else "#f97316" if tipo == "BUG" else "#6366f1" if tipo == "SUGESTÃO" else "#64748b"
        
        # Responsável (prioridade: responsavel > desenvolvedor > qa > relator)
        responsavel = card.get('responsavel') or card.get('desenvolvedor') or card.get('qa') or card.get('relator', 'N/A')
        if not responsavel or responsavel == 'Não atribuído':
            responsavel = card.get('relator', 'N/A')
        
        titulo_card = str(card.get('titulo', card.get('resumo', '')))[:80]
        ticket_id = card.get('ticket_id', '')
        status = card.get('status', '')
        
        # Classe de cor
        classe_cor = f"card-lista-{cor_classe}" if cor_classe else "card-lista"
        
        # Popup do card
        popup_html = card_link_com_popup(ticket_id, projeto)
        
        # Campos customizados
        info_extra = ""
        if campos_customizados:
            extras = []
            for campo, label in campos_customizados.items():
                valor = card.get(campo, '')
                if valor and valor != 'N/A' and valor != 'Não atribuído':
                    extras.append(f"<b>{label}:</b> {valor}")
            if extras:
                info_extra = f'<div style="font-size: 11px; color: #64748b; margin-top: 4px;">{" | ".join(extras)}</div>'
        
        cards_html += f'''
        <div class="{classe_cor}">
            <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-bottom: 4px;">
                <span style="background: #64748b; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">{projeto}</span>
                <span style="background: {tipo_cor}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">{tipo}</span>
                {popup_html}
                <span style="background: #e5e7eb; color: #374151; padding: 2px 6px; border-radius: 3px; font-size: 10px; margin-left: auto;">{status[:20]}</span>
            </div>
            <div style="font-size: 13px; color: #374151; line-height: 1.4;">{titulo_card}{"..." if len(str(card.get("titulo", ""))) > 80 else ""}</div>
            <div style="font-size: 11px; color: #64748b; margin-top: 4px;">👤 {responsavel}</div>
            {info_extra}
        </div>'''
    
    cards_html += '</div>'
    
    st.markdown(cards_html, unsafe_allow_html=True)
    
    if not mostrar_todos and total > limite_inicial:
        st.caption(f"📌 Mais {total - limite_inicial} cards ocultos. Marque acima para ver todos.")


# ==============================================================================
# GRÁFICOS
# ==============================================================================



