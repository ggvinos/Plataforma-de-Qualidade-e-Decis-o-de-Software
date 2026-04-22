"""
================================================================================
JIRA DASHBOARD v8.82 - NINA TECNOLOGIA - VERSÃO COMPLETA E ENRIQUECIDA
================================================================================
📊 NinaDash — Dashboard de Inteligência e Métricas de QA

🎯 Propósito: Transformar o QA de um processo sem visibilidade em um sistema 
   de inteligência operacional baseado em dados.

MELHORIAS v8.82:
- 🔧 FIX: Corrigido Meu Dashboard que não mostrava filtros corretamente
- 👤 PESSOAS: Lista de pessoas agora carrega corretamente
- ➕ ADICIONAR: Botão de adicionar widget agora funciona
- 📊 DEBUG: Mostra quantidade de dados e pessoas encontradas
- 🧹 SIMPLIFICADO: Interface mais limpa e direta

MELHORIAS v8.81:
- 🎨 MEU DASHBOARD: Tela totalmente nova para construir dashboards personalizados
- ➕ ADICIONAR WIDGETS: Construtor no topo para adicionar métricas  
- ⬆️⬇️ REORDENAR: Mova widgets para cima ou para baixo
- 🗑️ REMOVER: Exclua widgets que não precisa mais
- 📊 TEMPLATES: Visão Executiva, Foco DEV, Foco QA
- 💾 PERSISTÊNCIA: Dashboard salvo em cookie
- 🧹 SIDEBAR LIMPA: Apenas logo e botão voltar na tela do dashboard

MELHORIAS v8.80:
- 🎯 CONSULTA PERSONALIZADA: Tela separada para consultas avançadas
- 🔍 FILTROS DINÂMICOS: Pessoa, status, período, produto personalizados
- 📋 TIPOS DE CONSULTA: Cards, métricas, comparativos, tendências, bugs
- 💾 CONSULTAS SALVAS: Salve suas consultas favoritas
- 📅 PERÍODOS FLEXÍVEIS: Predefinidos ou datas personalizadas
- ⬅️ BOTÃO NA SIDEBAR: Acesso rápido à ferramenta avançada

MELHORIAS v8.78:
- 🎨 DESIGN REFINADO: Melhor espaçamento entre elementos
- ⬅️ BOTÃO VOLTAR NA SIDEBAR: Indica card ativo + volta fácil
- Link de compartilhamento mais compacto e funcional
- Visual mais limpo nas métricas do card
- Expanders fechados por padrão para menos poluição visual

MELHORIAS v8.6:
- 📱 SIDEBAR REFATORADA: Busca de card em destaque no topo
- 📤 COMPARTILHAMENTO FUNCIONAL: Link direto via query params
- Layout reorganizado: Logo → Busca → Filtros → Rodapé NINA
- URL persistente: ?card=SD-1234&projeto=SD

MELHORIAS v8.5:
- 🔍 BUSCA DE CARD INDIVIDUAL: Pesquise qualquer card pelo ID
- Painel completo com todas as métricas do card
- Fator K individual, janela de validação, aging, lead time
- Flags de fluxo (criado/finalizado na sprint, fora período)
- Timeline completa, resumo executivo automático

MELHORIAS v8.4:
- Aba Backlog exclusiva para projeto PB (Product Backlog)
- Health Score do backlog, análise de aging, cards estagnados
- Recomendações automáticas de ação

MELHORIAS v8.0:
- Header com logo Nina + subtítulo explicativo do objetivo
- Tooltips/explicações em TODAS as métricas (FPY, DDP, Fator K, etc)
- Seções colapsáveis em todas as abas (toggle open/close)
- Listagens COMPLETAS (opção de ver todos os cards)
- Aba Histórico enriquecida com múltiplos gráficos
- Mais métricas em cada aba
- Aba QA (sem "Gargalos" no nome)
- Auto-load + Cache inteligente
- Cards clicáveis com links Jira
- Métricas Ellen: iniciado/finalizado sprint, fora período, hotfix/produto

CAMPOS MAPEADOS JIRA NINA:
- customfield_11257: Story Points (principal)
- customfield_10016: Story Points (alternativo)
- customfield_11157: Bugs Encontrados  
- customfield_10020: Sprint
- customfield_11290: Complexidade de Teste
- customfield_10487: QA Responsável
- customfield_10102: Produto
================================================================================
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from typing import Optional, Dict, List, Any, Tuple
import json
import os
import io
import base64
import random
import extra_streamlit_components as stx

# ==============================================================================
# IMPORTS DOS MÓDULOS (Fase 1 de Modularização)
# ==============================================================================

from modulos.config import (
    configure_page,
    JIRA_BASE_URL,
    CUSTOM_FIELDS,
    STATUS_FLOW,
    STATUS_NOMES,
    STATUS_CORES,
    TOOLTIPS,
    REGRAS,
    NINA_LOGO_SVG,
    PB_FUNIL_ETAPAS,
    TEMAS_NAO_CLIENTES,
    NINADASH_URL,
)

from modulos.utils import (
    link_jira,
    card_link_com_popup,
    card_link_para_html,
    traduzir_link,
    calcular_dias_necessarios_validacao,
    avaliar_janela_validacao,
    get_secrets,
    verificar_credenciais,
)

from modulos.auth import (
    verificar_login,
    fazer_login,
    fazer_logout,
    mostrar_tela_login,
    mostrar_tela_loading,
    validar_email_corporativo,
    extrair_nome_usuario,
    get_cookie_manager,
)

from modulos.jira_api import (
    buscar_dados_jira_cached,
    buscar_card_especifico,
    extrair_historico_transicoes,
    extrair_texto_adf,
    gerar_icone_tabler,
    gerar_icone_tabler_html,
    gerar_badge_status,
    obter_icone_evento,
    obter_icone_status,
)

from modulos.calculos import (
    calcular_fator_k,
    classificar_maturidade,
    calcular_ddp,
    calcular_fpy,
    calcular_lead_time,
    analisar_dev_detalhado,
    filtrar_qas_principais,
    calcular_concentracao_conhecimento,
    gerar_recomendacoes_rodizio,
    calcular_concentracao_pessoa,
    calcular_metricas_governanca,
    calcular_metricas_qa,
    calcular_metricas_produto,
    calcular_health_score,
    calcular_metricas_dev,
    calcular_metricas_backlog,
    processar_issue_unica,
    processar_issues,
)

from modulos.processamento import (
    calcular_periodo_datas,
    filtrar_df_por_consulta,
    aplicar_filtros_widget,
    preparar_df_com_metricas_filtro,
    validar_filtros,
    resetar_filtros,
)

from modulos.abas import (
    aba_clientes,
    aba_visao_geral,
    aba_qa,
    aba_dev,
    aba_governanca,
    aba_produto,
    aba_backlog,
    aba_suporte_implantacao,
    aba_historico,
    aba_lideranca,
    aba_sobre,
    aba_dashboard_personalizado,
)

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA (DEVE SER PRIMEIRO)
# ==============================================================================

configure_page()

# CSS global para o popup (deve ser inserido uma vez na página)
CARD_POPUP_CSS = """
<style>
    /* Wrapper do link com botão NinaDash */
    .card-link-wrapper {
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    
    /* ID do ticket (link para Jira) */
    .card-link-id {
        font-weight: 600;
        text-decoration: none;
        padding: 1px 3px;
        border-radius: 3px;
        transition: all 0.2s ease;
    }
    .card-link-id:hover {
        background: rgba(59, 130, 246, 0.1);
        text-decoration: underline;
    }
    
    /* Botão NinaDash - escondido por padrão, aparece no hover do wrapper */
    .card-action-btn {
        display: none;
        align-items: center;
        gap: 3px;
        padding: 3px 8px;
        font-size: 11px;
        font-weight: 500;
        text-decoration: none;
        border-radius: 4px;
        transition: all 0.15s ease;
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        color: #475569;
        white-space: nowrap;
    }
    
    /* Mostrar botão no hover do wrapper */
    .card-link-wrapper:hover .card-action-btn {
        display: inline-flex;
    }
    
    /* Hover NinaDash */
    .card-action-nina:hover {
        background: #AF0C37;
        border-color: #AF0C37;
        color: white;
    }
</style>
"""


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


def inicializar_meu_dashboard():
    """Inicializa o sistema de Meu Dashboard."""
    if 'meu_dashboard_widgets' not in st.session_state:
        # Tenta carregar do cookie
        try:
            cookie_manager = get_cookie_manager()
            dashboard_cookie = cookie_manager.get(COOKIE_DASHBOARD_NAME)
            if dashboard_cookie:
                import json
                st.session_state.meu_dashboard_widgets = json.loads(dashboard_cookie)
            else:
                st.session_state.meu_dashboard_widgets = []
        except:
            st.session_state.meu_dashboard_widgets = []
    
    if 'modo_meu_dashboard' not in st.session_state:
        st.session_state.modo_meu_dashboard = False


def _salvar_dashboard_cookie():
    """Salva o dashboard no cookie para persistência."""
    try:
        import json
        cookie_manager = get_cookie_manager()
        
        # Serializa os widgets (remove datetime objects)
        widgets_serializaveis = []
        for widget in st.session_state.meu_dashboard_widgets:
            widget_copia = widget.copy()
            filtros_copia = widget_copia.get('filtros', {}).copy()
            for key in ['data_inicio', 'data_fim']:
                if key in filtros_copia:
                    if isinstance(filtros_copia[key], datetime):
                        filtros_copia[key] = filtros_copia[key].isoformat()
            widget_copia['filtros'] = filtros_copia
            widgets_serializaveis.append(widget_copia)
        
        cookie_manager.set(
            COOKIE_DASHBOARD_NAME,
            json.dumps(widgets_serializaveis),
            expires_at=datetime.now() + timedelta(days=365)
        )
    except:
        pass


def adicionar_widget(tipo_widget: str, filtros: Dict):
    """Adiciona um widget ao dashboard."""
    inicializar_meu_dashboard()
    
    widget_info = CATALOGO_WIDGETS.get(tipo_widget, {})
    novo_widget = {
        "id": f"widget_{datetime.now().timestamp()}",
        "tipo": tipo_widget,
        "nome": widget_info.get('nome', tipo_widget),
        "filtros": filtros.copy(),
        "criado_em": datetime.now().isoformat()
    }
    st.session_state.meu_dashboard_widgets.append(novo_widget)
    _salvar_dashboard_cookie()


def remover_widget(widget_id: str):
    """Remove um widget do dashboard."""
    st.session_state.meu_dashboard_widgets = [
        w for w in st.session_state.meu_dashboard_widgets if w['id'] != widget_id
    ]
    _salvar_dashboard_cookie()


def mover_widget_cima(widget_id: str):
    """Move um widget para cima na lista."""
    widgets = st.session_state.meu_dashboard_widgets
    for i, w in enumerate(widgets):
        if w['id'] == widget_id and i > 0:
            widgets[i], widgets[i-1] = widgets[i-1], widgets[i]
            break
    _salvar_dashboard_cookie()


def mover_widget_baixo(widget_id: str):
    """Move um widget para baixo na lista."""
    widgets = st.session_state.meu_dashboard_widgets
    for i, w in enumerate(widgets):
        if w['id'] == widget_id and i < len(widgets) - 1:
            widgets[i], widgets[i+1] = widgets[i+1], widgets[i]
            break
    _salvar_dashboard_cookie()


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


def _salvar_consultas_cookie():
    """Salva as consultas no cookie para persistência."""
    try:
        import json
        cookie_manager = get_cookie_manager()
        # Converte filtros datetime para string antes de serializar
        consultas_serializaveis = {}
        for nome, consulta in st.session_state.consultas_salvas.items():
            consulta_copia = consulta.copy()
            filtros_copia = consulta_copia.get('filtros', {}).copy()
            # Remove datetime objects que não são serializáveis
            for key in ['data_inicio', 'data_fim']:
                if key in filtros_copia and isinstance(filtros_copia[key], datetime):
                    filtros_copia[key] = filtros_copia[key].isoformat()
            consulta_copia['filtros'] = filtros_copia
            consultas_serializaveis[nome] = consulta_copia
        
        cookie_manager.set(
            COOKIE_CONSULTAS_NAME,
            json.dumps(consultas_serializaveis),
            expires_at=datetime.now() + timedelta(days=365)  # 1 ano
        )
    except Exception as e:
        pass  # Silently fail cookie save


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
def inicializar_dashboards_personalizados():
    """Inicializa o armazenamento de dashboards personalizados no session_state."""
    if 'dashboards_personalizados' not in st.session_state:
        st.session_state.dashboards_personalizados = {}
    if 'dashboard_ativo' not in st.session_state:
        st.session_state.dashboard_ativo = None
    if 'modo_builder' not in st.session_state:
        st.session_state.modo_builder = False


def salvar_dashboard_personalizado(nome: str, metricas: List[str], config: Dict = None):
    """Salva um dashboard personalizado."""
    inicializar_dashboards_personalizados()
    
    st.session_state.dashboards_personalizados[nome] = {
        "nome": nome,
        "metricas": metricas,
        "config": config or {},
        "criado_em": datetime.now().isoformat(),
        "atualizado_em": datetime.now().isoformat()
    }


def carregar_dashboard_personalizado(nome: str) -> Optional[Dict]:
    """Carrega um dashboard personalizado."""
    inicializar_dashboards_personalizados()
    return st.session_state.dashboards_personalizados.get(nome)


def listar_dashboards_personalizados() -> List[str]:
    """Lista todos os dashboards personalizados."""
    inicializar_dashboards_personalizados()
    return list(st.session_state.dashboards_personalizados.keys())


def excluir_dashboard_personalizado(nome: str):
    """Exclui um dashboard personalizado."""
    inicializar_dashboards_personalizados()
    if nome in st.session_state.dashboards_personalizados:
        del st.session_state.dashboards_personalizados[nome]


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


def calcular_valor_metrica(metrica_key: str, df: pd.DataFrame):
    """Calcula o valor de uma métrica KPI."""
    try:
        if metrica_key == "fator_k_geral":
            total_sp = df['story_points'].sum()
            total_bugs = df['bugs_encontrados'].sum()
            return f"{total_sp / (total_bugs + 1):.2f}"
        
        elif metrica_key == "fpy":
            metricas = calcular_fpy(df)
            return f"{metricas.get('fpy', 0):.1f}%"
        
        elif metrica_key == "ddp":
            metricas = calcular_ddp(df)
            return f"{metricas.get('ddp', 0):.1f}%"
        
        elif metrica_key == "health_score":
            metricas = calcular_health_score(df)
            return f"{metricas.get('score', 0):.0f}"
        
        elif metrica_key == "throughput_cards":
            concluidos = df[df['status_categoria'] == 'done']
            return str(len(concluidos))
        
        elif metrica_key == "throughput_sp":
            concluidos = df[df['status_categoria'] == 'done']
            return str(int(concluidos['story_points'].sum()))
        
        elif metrica_key == "lead_time":
            metricas = calcular_lead_time(df)
            return f"{metricas.get('media', 0):.1f} dias"
        
        elif metrica_key == "wip":
            em_andamento = df[~df['status_categoria'].isin(['done', 'backlog', 'deferred'])]
            return str(len(em_andamento))
        
        elif metrica_key == "velocidade_media":
            concluidos = df[df['status_categoria'] == 'done']
            if len(concluidos) > 0:
                return f"{concluidos['story_points'].mean():.1f} SP"
            return "0 SP"
        
        elif metrica_key == "total_bugs":
            return str(int(df['bugs_encontrados'].sum()))
        
        elif metrica_key == "densidade_bugs":
            total_sp = df['story_points'].sum()
            total_bugs = df['bugs_encontrados'].sum()
            if total_sp > 0:
                return f"{total_bugs / total_sp:.2f}"
            return "0.00"
        
        elif metrica_key == "taxa_reprovacao":
            reprovados = df[df['status_categoria'] == 'rejected']
            total = len(df)
            if total > 0:
                return f"{(len(reprovados) / total) * 100:.1f}%"
            return "0%"
        
        return None
    except Exception:
        return None


def calcular_dados_grafico(metrica_key: str, df: pd.DataFrame):
    """Calcula dados para gráficos de barra/pizza."""
    try:
        if metrica_key == "bugs_por_dev":
            bugs_dev = df.groupby('responsavel')['bugs_encontrados'].sum().sort_values(ascending=False)
            return bugs_dev.head(10)
        
        elif metrica_key == "carga_qa":
            em_qa = df[df['status_categoria'].isin(['waiting_qa', 'testing'])]
            return em_qa['qa_responsavel'].value_counts().head(10)
        
        elif metrica_key == "cards_por_status":
            return df['status'].value_counts()
        
        elif metrica_key == "cards_por_dev":
            return df['responsavel'].value_counts().head(10)
        
        elif metrica_key == "por_produto":
            return df['produto'].value_counts()
        
        elif metrica_key == "hotfix_produto":
            hotfixes = df[df['tipo'].str.lower().str.contains('hotfix', na=False)]
            return hotfixes['produto'].value_counts()
        
        elif metrica_key == "top_clientes":
            if 'temas' in df.columns:
                # Extrai clientes dos temas
                clientes = []
                for temas in df['temas'].dropna():
                    if isinstance(temas, list):
                        clientes.extend(temas)
                    elif isinstance(temas, str):
                        clientes.append(temas)
                return pd.Series(clientes).value_counts().head(10)
            return pd.Series()
        
        elif metrica_key == "clientes_bugs":
            if 'temas' in df.columns:
                df_com_bugs = df[df['bugs_encontrados'] > 0]
                clientes = []
                for _, row in df_com_bugs.iterrows():
                    temas = row.get('temas', [])
                    if isinstance(temas, list):
                        for tema in temas:
                            clientes.append(tema)
                return pd.Series(clientes).value_counts().head(10)
            return pd.Series()
        
        return None
    except Exception:
        return None


def calcular_dados_tabela(metrica_key: str, df: pd.DataFrame):
    """Calcula dados para tabelas."""
    try:
        if metrica_key == "ranking_devs":
            # Agrupa por desenvolvedor
            ranking = df.groupby('responsavel').agg({
                'story_points': 'sum',
                'bugs_encontrados': 'sum',
                'key': 'count'
            }).reset_index()
            ranking.columns = ['Desenvolvedor', 'SP', 'Bugs', 'Cards']
            ranking['Fator K'] = ranking['SP'] / (ranking['Bugs'] + 1)
            ranking = ranking.sort_values('Fator K', ascending=False)
            return ranking[['Desenvolvedor', 'Cards', 'SP', 'Bugs', 'Fator K']].head(15)
        
        elif metrica_key == "aging_qa":
            em_qa = df[df['status_categoria'].isin(['waiting_qa', 'testing'])].copy()
            if 'data_criacao' in em_qa.columns:
                em_qa['Dias'] = (datetime.now() - pd.to_datetime(em_qa['data_criacao'])).dt.days
                return em_qa[['key', 'resumo', 'qa_responsavel', 'Dias']].sort_values('Dias', ascending=False).head(10)
            return pd.DataFrame()
        
        elif metrica_key == "fator_k_dev":
            # Similar ao ranking_devs mas focado no FK
            ranking = df.groupby('responsavel').agg({
                'story_points': 'sum',
                'bugs_encontrados': 'sum'
            }).reset_index()
            ranking['Fator K'] = ranking['story_points'] / (ranking['bugs_encontrados'] + 1)
            ranking = ranking.sort_values('Fator K', ascending=False)
            ranking.columns = ['Desenvolvedor', 'SP', 'Bugs', 'Fator K']
            return ranking.head(15)
        
        return None
    except Exception:
        return None


def calcular_lista_cards(metrica_key: str, df: pd.DataFrame):
    """Calcula lista de cards para exibição."""
    try:
        if metrica_key == "code_review_fila":
            em_cr = df[df['status_categoria'] == 'code_review']
            return em_cr[['key', 'resumo', 'responsavel']].to_dict('records')
        
        elif metrica_key == "cards_aguardando_qa":
            aguardando = df[df['status_categoria'] == 'waiting_qa']
            return aguardando[['key', 'resumo', 'qa_responsavel']].to_dict('records')
        
        elif metrica_key == "cards_impedidos":
            impedidos = df[df['status_categoria'] == 'blocked']
            return impedidos[['key', 'resumo', 'responsavel']].to_dict('records')
        
        elif metrica_key == "cards_bloqueados":
            bloqueados = df[df['status'].str.lower().str.contains('bloque|block', na=False)]
            return bloqueados[['key', 'resumo', 'responsavel']].to_dict('records')
        
        return []
    except Exception:
        return []


def calcular_dados_heatmap(metrica_key: str, df: pd.DataFrame):
    """Calcula dados para heatmaps."""
    try:
        if metrica_key == "concentracao_dev":
            conc = calcular_concentracao_conhecimento(df)
            return conc.get('matriz_dev')
        
        elif metrica_key == "concentracao_qa":
            conc = calcular_concentracao_conhecimento(df)
            return conc.get('matriz_qa')
        
        return None
    except Exception:
        return None


def calcular_dados_funil(metrica_key: str, df: pd.DataFrame):
    """Calcula dados para gráficos de funil."""
    try:
        if metrica_key == "funil_qa":
            metricas = calcular_metricas_qa(df)
            return metricas
        return None
    except Exception:
        return None


def criar_grafico_funil_personalizado(dados: Dict, titulo: str):
    """Cria um gráfico de funil simplificado."""
    try:
        # Extrai valores do funil
        aguardando = dados.get('aguardando_qa', 0)
        em_validacao = dados.get('em_validacao', 0)
        concluidos = dados.get('validados', 0)
        reprovados = dados.get('reprovados', 0)
        
        labels = ['Aguardando QA', 'Em Validação', 'Concluídos', 'Reprovados']
        valores = [aguardando, em_validacao, concluidos, reprovados]
        
        fig = go.Figure(go.Funnel(
            y=labels,
            x=valores,
            textposition="inside",
            textinfo="value+percent initial",
            marker={"color": ["#f59e0b", "#3b82f6", "#22c55e", "#ef4444"]}
        ))
        fig.update_layout(height=300, title=titulo)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Erro no funil: {e}")


def exibir_card_detalhado_v2(card: Dict, links: List[Dict], comentarios: List[Dict], historico: List[Dict] = None, projeto: str = "SD") -> bool:
    """
    Exibe painel detalhado com informações de um card específico.
    Adapta o conteúdo conforme o projeto:
    - SD: Completo (bugs, FK, qualidade, janela, comentários)
    - QA: Foco em aging, automação, tempo parado
    - PB: Backlog - sem bugs, foco em prioridade e estimativa
    """
    if not card:
        return False
    
    # Garante que historico seja uma lista
    if historico is None:
        historico = []
    
    # Gera URL de compartilhamento
    base_url = NINADASH_URL
    share_url = f"{base_url}?card={card['ticket_id']}&projeto={projeto}"
    
    # ===== HEADER DO CARD =====
    # Cor do header varia por projeto
    header_colors = {
        "SD": ("linear-gradient(135deg, #AF0C37 0%, #8a0a2c 100%)", "🔍"),
        "QA": ("linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)", "🤖"),
        "PB": ("linear-gradient(135deg, #059669 0%, #047857 100%)", "📋")
    }
    header_bg, header_icon = header_colors.get(projeto, header_colors["SD"])
    
    st.markdown(f"""
    <div style='background: {header_bg}; 
                color: white; padding: 20px; border-radius: 12px; margin-bottom: 15px;'>
        <h2 style='margin: 0; color: white; font-size: 1.5em;'>
            {header_icon} {card['ticket_id']}
        </h2>
        <p style='margin: 8px 0 0 0; opacity: 0.9; font-size: 0.95em;'>
            {card['titulo'][:120]}{'...' if len(card['titulo']) > 120 else ''}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== BOTÕES DE AÇÃO =====
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        st.link_button("🔗 Abrir no Jira", card['link'], use_container_width=True)
    
    with col2:
        # Usar components.html para JavaScript funcionar (iframe isolado)
        components.html(f"""
        <style>
            html, body {{
                margin: 0 !important;
                padding: 0 !important;
                overflow: hidden;
            }}
        </style>
        <button id="copyBtn" style="
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            border: none;
            padding: 0 16px;
            border-radius: 8px;
            cursor: pointer;
            width: 100%;
            height: 36px;
            font-size: 14px;
            font-weight: 500;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        ">📋 Copiar Link</button>
        <script>
            document.getElementById('copyBtn').addEventListener('click', function() {{
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
        """, height=36)
    
    with col3:
        st.caption(f"Sprint: **{card['sprint']}** | Produto: **{card['produto']}**")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========================================================================
    # CONTEÚDO ESPECÍFICO POR PROJETO
    # ========================================================================
    
    if projeto == "SD":
        exibir_detalhes_sd(card, links, comentarios, historico)
    elif projeto == "QA":
        exibir_detalhes_qa(card, links, comentarios, historico)
    elif projeto == "PB":
        exibir_detalhes_pb(card, links, comentarios, historico)
    else:
        exibir_detalhes_sd(card, links, comentarios, historico)  # Fallback
    
    return True


def exibir_detalhes_sd(card: Dict, links: List[Dict], comentarios: List[Dict], historico: List[Dict] = None):
    """Exibe detalhes para projeto SD (Service Desk) - Completo com qualidade."""
    
    # Garante que historico seja uma lista
    if historico is None:
        historico = []
    
    # ===== KPIs PRINCIPAIS (CARDS ESTILIZADOS) =====
    fk = calcular_fator_k(card['sp'], card['bugs'])
    mat = classificar_maturidade(fk)
    
    # Cores por status
    status_cores = {
        "Done": "#22c55e", "Concluído": "#22c55e",
        "Em Validação": "#3b82f6", "Aguardando Validação": "#f59e0b",
        "Desenvolvimento": "#8b5cf6", "Code Review": "#ec4899",
        "Blocked": "#ef4444", "Reprovado": "#ef4444"
    }
    status_cor = status_cores.get(card['status'], "#6b7280")
    
    st.markdown(f"""
    <div style='display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;'>
        <div style='background: linear-gradient(135deg, {status_cor}15, {status_cor}05); border: 1px solid {status_cor}40; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>📌</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Status</div>
            <div style='font-size: 14px; font-weight: 600; color: {status_cor}; margin-top: 4px; word-wrap: break-word;'>{card['status']}</div>
        </div>
        <div style='background: linear-gradient(135deg, #6366f115, #6366f105); border: 1px solid #6366f140; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>🎯</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Tipo</div>
            <div style='font-size: 14px; font-weight: 600; color: #6366f1; margin-top: 4px;'>{card['tipo']}</div>
        </div>
        <div style='background: linear-gradient(135deg, #f9731615, #f9731605); border: 1px solid #f9731640; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>⚡</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Prioridade</div>
            <div style='font-size: 14px; font-weight: 600; color: #f97316; margin-top: 4px;'>{card['prioridade']}</div>
        </div>
        <div style='background: linear-gradient(135deg, {mat['cor']}15, {mat['cor']}05); border: 1px solid {mat['cor']}40; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>🎖️</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Fator K</div>
            <div style='font-size: 14px; font-weight: 600; color: {mat['cor']}; margin-top: 4px;'>{fk:.2f} {mat['emoji']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== INFORMAÇÕES BÁSICAS =====
    with st.expander("📋 **Informações Básicas**", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
| Campo | Valor |
|-------|-------|
| **Projeto** | {card['projeto']} |
| **Sprint** | {card['sprint']} |
| **Produto** | {card['produto']} |
| **Tipo Original** | {card['tipo_original']} |
            """)
        
        with col2:
            # Indicador visual se SP foi estimado pela regra de Hotfix
            sp_display = f"{card['sp']} ⚠️ *estimado*" if card.get('sp_estimado', False) else str(card['sp'])
            st.markdown(f"""
| Campo | Valor |
|-------|-------|
| **Desenvolvedor** | {card['desenvolvedor']} |
| **QA Responsável** | {card['qa']} |
| **Story Points** | {sp_display} |
| **Complexidade** | {card['complexidade'] if card['complexidade'] else 'Não definida'} |
            """)
    
    # ===== MÉTRICAS DE QUALIDADE =====
    with st.expander("📊 **Métricas de Qualidade**", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        fk = calcular_fator_k(card['sp'], card['bugs'])
        mat = classificar_maturidade(fk)
        
        with col1:
            st.markdown(f"""
<div style='background: {mat['cor']}15; padding: 12px; border-radius: 8px; text-align: center; border-left: 3px solid {mat['cor']}; margin-bottom: 8px;'>
    <h3 style='margin:0; color: {mat['cor']}; font-size: 1.4em;'>{fk:.2f}</h3>
    <small style='color: #666;'>Fator K</small><br>
    <span style='font-size: 18px;'>{mat['emoji']}</span>
    <small style='color: {mat['cor']};'>{mat['desc']}</small>
</div>
            """, unsafe_allow_html=True)
        
        with col2:
            bugs_cor = "#22c55e" if card['bugs'] == 0 else "#f97316" if card['bugs'] <= 2 else "#ef4444"
            st.markdown(f"""
<div style='background: {bugs_cor}15; padding: 12px; border-radius: 8px; text-align: center; border-left: 3px solid {bugs_cor}; margin-bottom: 8px;'>
    <h3 style='margin:0; color: {bugs_cor}; font-size: 1.4em;'>{card['bugs']}</h3>
    <small style='color: #666;'>Bugs</small><br>
    <span style='font-size: 18px;'>{'✅' if card['bugs'] == 0 else '⚠️' if card['bugs'] <= 2 else '🐛'}</span>
</div>
            """, unsafe_allow_html=True)
        
        with col3:
            sp_estimado_aviso = "<br><small style='color: #f59e0b;'>⚠️ Estimado</small>" if card.get('sp_estimado', False) else ""
            st.markdown(f"""
<div style='background: #3b82f615; padding: 12px; border-radius: 8px; text-align: center; border-left: 3px solid #3b82f6; margin-bottom: 8px;'>
    <h3 style='margin:0; color: #3b82f6; font-size: 1.4em;'>{card['sp']}</h3>
    <small style='color: #666;'>Story Points</small>{sp_estimado_aviso}<br>
    <span style='font-size: 18px;'>{'🎯' if card['sp'] > 0 else '❓'}</span>
</div>
            """, unsafe_allow_html=True)
        
        with col4:
            fpy_individual = 100 if card['bugs'] == 0 else 0
            fpy_cor = "#22c55e" if fpy_individual == 100 else "#ef4444"
            st.markdown(f"""
<div style='background: {fpy_cor}15; padding: 12px; border-radius: 8px; text-align: center; border-left: 3px solid {fpy_cor}; margin-bottom: 8px;'>
    <h3 style='margin:0; color: {fpy_cor}; font-size: 1.4em;'>{fpy_individual}%</h3>
    <small style='color: #666;'>FPY</small><br>
    <span style='font-size: 18px;'>{'✅' if fpy_individual == 100 else '🔄'}</span>
</div>
            """, unsafe_allow_html=True)
    
    # ===== ANÁLISE DE TEMPO =====
    with st.expander("⏱️ **Análise de Tempo**", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            lead_cor = "#22c55e" if card['lead_time'] <= 7 else "#f97316" if card['lead_time'] <= 14 else "#ef4444"
            st.markdown(f"""
<div style='background: {lead_cor}15; padding: 12px; border-radius: 8px; text-align: center; border-left: 3px solid {lead_cor}; margin-bottom: 8px;'>
    <h3 style='margin:0; color: {lead_cor}; font-size: 1.3em;'>{card['lead_time']} dias</h3>
    <small style='color: #666;'>Lead Time</small><br>
    <span style='font-size: 16px;'>{'🚀' if card['lead_time'] <= 7 else '⏳' if card['lead_time'] <= 14 else '🐢'}</span>
    <small style='color: {lead_cor};'>{'Rápido' if card['lead_time'] <= 7 else 'Normal' if card['lead_time'] <= 14 else 'Lento'}</small>
</div>
            """, unsafe_allow_html=True)
        
        with col2:
            aging_cor = "#22c55e" if card['dias_em_status'] <= 3 else "#f97316" if card['dias_em_status'] <= 7 else "#ef4444"
            st.markdown(f"""
<div style='background: {aging_cor}15; padding: 12px; border-radius: 8px; text-align: center; border-left: 3px solid {aging_cor}; margin-bottom: 8px;'>
    <h3 style='margin:0; color: {aging_cor}; font-size: 1.3em;'>{card['dias_em_status']} dias</h3>
    <small style='color: #666;'>No Status Atual</small><br>
    <span style='font-size: 16px;'>{'✅' if card['dias_em_status'] <= 3 else '⚠️' if card['dias_em_status'] <= 7 else '🚨'}</span>
    <small style='color: {aging_cor};'>{'OK' if card['dias_em_status'] <= 3 else 'Atenção' if card['dias_em_status'] <= 7 else 'Aging'}</small>
</div>
            """, unsafe_allow_html=True)
        
        with col3:
            release_cor = "#22c55e" if card['dias_ate_release'] >= 3 else "#f97316" if card['dias_ate_release'] >= 1 else "#ef4444"
            st.markdown(f"""
<div style='background: {release_cor}15; padding: 12px; border-radius: 8px; text-align: center; border-left: 3px solid {release_cor}; margin-bottom: 8px;'>
    <h3 style='margin:0; color: {release_cor}; font-size: 1.3em;'>{card['dias_ate_release']} dias</h3>
    <small style='color: #666;'>Até Release</small><br>
    <span style='font-size: 16px;'>{'✅' if card['dias_ate_release'] >= 3 else '⚠️' if card['dias_ate_release'] >= 1 else '🚨'}</span>
</div>
            """, unsafe_allow_html=True)
        
        # Timeline
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**📅 Timeline**")
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            st.caption(f"**Criação:** {card['criado'].strftime('%d/%m/%Y') if pd.notna(card['criado']) else 'N/A'}")
        with col_t2:
            st.caption(f"**Atualização:** {card['atualizado'].strftime('%d/%m/%Y') if pd.notna(card['atualizado']) else 'N/A'}")
        with col_t3:
            st.caption(f"**Resolução:** {card['resolutiondate'].strftime('%d/%m/%Y') if pd.notna(card['resolutiondate']) else 'Pendente'}")
    
    # ===== JANELA DE VALIDAÇÃO =====
    with st.expander("🕐 **Janela de Validação**", expanded=False):
        janela_cor = "#22c55e" if card['janela_status'] == 'ok' else "#f97316" if card['janela_status'] == 'risco' else "#ef4444"
        janela_emoji = "✅" if card['janela_status'] == 'ok' else "⚠️" if card['janela_status'] == 'risco' else "🚨"
        janela_texto = "Dentro da Janela" if card['janela_status'] == 'ok' else "Janela em Risco" if card['janela_status'] == 'risco' else "Fora da Janela"
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
<div style='background: {janela_cor}15; padding: 12px; border-radius: 8px; text-align: center; border-left: 3px solid {janela_cor};'>
    <span style='font-size: 24px;'>{janela_emoji}</span>
    <h4 style='margin: 5px 0; color: {janela_cor}; font-size: 1em;'>{janela_texto}</h4>
</div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
<div style='background: #6366f115; padding: 12px; border-radius: 8px; text-align: center; border-left: 3px solid #6366f1;'>
    <h3 style='margin:0; color: #6366f1; font-size: 1.2em;'>{card['janela_dias_necessarios']}d</h3>
    <small style='color: #666;'>Necessários</small>
</div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
<div style='background: #8b5cf615; padding: 12px; border-radius: 8px; text-align: center; border-left: 3px solid #8b5cf6;'>
    <h3 style='margin:0; color: #8b5cf6; font-size: 1.2em;'>{card['dias_ate_release']}d</h3>
    <small style='color: #666;'>Disponíveis</small>
</div>
            """, unsafe_allow_html=True)
    
    # ===== RESUMO EXECUTIVO =====
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📝 Resumo Executivo")
    
    insights = []
    
    if card['bugs'] == 0:
        insights.append("✅ **Qualidade**: Zero bugs")
    elif card['bugs'] <= 2:
        insights.append(f"⚠️ **Qualidade**: {card['bugs']} bug(s)")
    else:
        insights.append(f"🚨 **Qualidade**: {card['bugs']} bugs")
    
    if card['lead_time'] <= 7:
        insights.append(f"✅ **Velocidade**: {card['lead_time']}d")
    elif card['lead_time'] <= 14:
        insights.append(f"⚠️ **Velocidade**: {card['lead_time']}d")
    else:
        insights.append(f"🚨 **Velocidade**: {card['lead_time']}d")
    
    if card['janela_status'] == 'ok':
        insights.append("✅ **Janela**: OK")
    elif card['janela_status'] == 'risco':
        insights.append("⚠️ **Janela**: Risco")
    else:
        insights.append("🚨 **Janela**: FORA")
    
    if card['dias_em_status'] > 7:
        insights.append(f"🚨 **Aging**: {card['dias_em_status']}d")
    
    cols = st.columns(len(insights)) if insights else [st]
    for i, insight in enumerate(insights):
        with cols[i]:
            st.markdown(insight)
    
    # ===== DESCRIÇÃO DO CARD =====
    descricao = card.get('descricao', '')
    if descricao and descricao.strip():
        with st.expander("📝 **Descrição**", expanded=False):
            st.markdown(f"""
<div style='background: #f8fafc; padding: 16px; border-radius: 8px; border-left: 3px solid #3b82f6;'>
    <div style='color: #374151; line-height: 1.6; white-space: pre-wrap;'>{descricao}</div>
</div>
            """, unsafe_allow_html=True)
    
    # ===== TIMELINE DE TRANSIÇÕES =====
    if historico:
        exibir_timeline_transicoes(historico, "📜 Timeline Completa do Card")
    
    # ===== CARDS VINCULADOS =====
    exibir_cards_vinculados(links)
    
    # ===== COMENTÁRIOS =====
    exibir_comentarios(comentarios, projeto="SD")


def exibir_detalhes_qa(card: Dict, links: List[Dict], comentarios: List[Dict], historico: List[Dict] = None):
    """Exibe detalhes para projeto QA - Foco em automação e tempo parado."""
    
    # Garante que historico seja uma lista
    if historico is None:
        historico = []
    
    # ===== KPIs PRINCIPAIS (CARDS ESTILIZADOS - QA) =====
    # Cores por status
    status_cores = {
        "Done": "#22c55e", "Concluído": "#22c55e",
        "Em Validação": "#3b82f6", "Aguardando Validação": "#f59e0b",
        "Desenvolvimento": "#8b5cf6", "Code Review": "#ec4899",
        "Blocked": "#ef4444", "Reprovado": "#ef4444"
    }
    status_cor = status_cores.get(card['status'], "#6b7280")
    sp_estimado_badge = "<span style='background:#f59e0b; color:white; font-size:9px; padding:2px 6px; border-radius:4px; margin-left:4px;'>estimado</span>" if card.get('sp_estimado', False) else ""
    
    st.markdown(f"""
    <div style='display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;'>
        <div style='background: linear-gradient(135deg, {status_cor}15, {status_cor}05); border: 1px solid {status_cor}40; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>📌</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Status</div>
            <div style='font-size: 14px; font-weight: 600; color: {status_cor}; margin-top: 4px; word-wrap: break-word;'>{card['status']}</div>
        </div>
        <div style='background: linear-gradient(135deg, #6366f115, #6366f105); border: 1px solid #6366f140; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>🎯</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Tipo</div>
            <div style='font-size: 14px; font-weight: 600; color: #6366f1; margin-top: 4px;'>{card['tipo']}</div>
        </div>
        <div style='background: linear-gradient(135deg, #f9731615, #f9731605); border: 1px solid #f9731640; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>⚡</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Prioridade</div>
            <div style='font-size: 14px; font-weight: 600; color: #f97316; margin-top: 4px;'>{card['prioridade']}</div>
        </div>
        <div style='background: linear-gradient(135deg, #3b82f615, #3b82f605); border: 1px solid #3b82f640; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>📊</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Story Points</div>
            <div style='font-size: 14px; font-weight: 600; color: #3b82f6; margin-top: 4px;'>{card['sp']}{sp_estimado_badge}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== ALERTA DE AGING (DESTAQUE PARA QA) =====
    aging_cor = "#22c55e" if card['dias_em_status'] <= 7 else "#f97316" if card['dias_em_status'] <= 30 else "#ef4444"
    aging_emoji = "✅" if card['dias_em_status'] <= 7 else "⚠️" if card['dias_em_status'] <= 30 else "🚨"
    
    st.markdown(f"""
    <div style='background: {aging_cor}15; padding: 20px; border-radius: 12px; 
                border-left: 4px solid {aging_cor}; margin-bottom: 20px;'>
        <div style='display: flex; align-items: center; gap: 15px;'>
            <span style='font-size: 40px;'>{aging_emoji}</span>
            <div>
                <h3 style='margin: 0; color: {aging_cor}; font-size: 1.3em;'>
                    {card['dias_em_status']} dias no status atual
                </h3>
                <p style='margin: 5px 0 0 0; color: #666; font-size: 0.9em;'>
                    Status: <b>{card['status']}</b> | 
                    {'Atividade recente' if card['dias_em_status'] <= 7 else 'Possível bloqueio - verificar impedimentos' if card['dias_em_status'] <= 30 else 'Card parado há muito tempo - ação necessária'}
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== INFORMAÇÕES DO CARD =====
    with st.expander("📋 **Informações do Card de Automação**", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
| Campo | Valor |
|-------|-------|
| **Projeto** | {card['projeto']} |
| **Sprint** | {card['sprint']} |
| **Produto** | {card['produto']} |
| **Tipo** | {card['tipo_original']} |
            """)
        
        with col2:
            sp_display_pb = f"{card['sp']} ⚠️ *estimado*" if card.get('sp_estimado', False) else str(card['sp'])
            st.markdown(f"""
| Campo | Valor |
|-------|-------|
| **Responsável** | {card['desenvolvedor']} |
| **Story Points** | {sp_display_pb} |
| **Criado** | {card['criado'].strftime('%d/%m/%Y') if pd.notna(card['criado']) else 'N/A'} |
| **Atualizado** | {card['atualizado'].strftime('%d/%m/%Y') if pd.notna(card['atualizado']) else 'N/A'} |
            """)
    
    # ===== ANÁLISE DE TEMPO =====
    with st.expander("⏱️ **Análise de Tempo**", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            lead_cor = "#22c55e" if card['lead_time'] <= 14 else "#f97316" if card['lead_time'] <= 30 else "#ef4444"
            st.markdown(f"""
<div style='background: {lead_cor}15; padding: 15px; border-radius: 8px; text-align: center; border-left: 3px solid {lead_cor};'>
    <h3 style='margin:0; color: {lead_cor}; font-size: 1.4em;'>{card['lead_time']} dias</h3>
    <small style='color: #666;'>Lead Time Total</small>
</div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
<div style='background: {aging_cor}15; padding: 15px; border-radius: 8px; text-align: center; border-left: 3px solid {aging_cor};'>
    <h3 style='margin:0; color: {aging_cor}; font-size: 1.4em;'>{card['dias_em_status']} dias</h3>
    <small style='color: #666;'>Parado no Status</small>
</div>
            """, unsafe_allow_html=True)
        
        with col3:
            criado_ha = (datetime.now() - card['criado']).days if pd.notna(card['criado']) else 0
            st.markdown(f"""
<div style='background: #6366f115; padding: 15px; border-radius: 8px; text-align: center; border-left: 3px solid #6366f1;'>
    <h3 style='margin:0; color: #6366f1; font-size: 1.4em;'>{criado_ha} dias</h3>
    <small style='color: #666;'>Desde Criação</small>
</div>
            """, unsafe_allow_html=True)
    
    # ===== RESUMO =====
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📝 Situação do Card de Automação")
    
    if card['dias_em_status'] <= 7:
        st.success("✅ Card com atividade recente. Desenvolvimento em andamento normal.")
    elif card['dias_em_status'] <= 30:
        st.warning("⚠️ Card parado há mais de uma semana. Verificar se há impedimentos ou necessidade de repriorização.")
    else:
        st.error("🚨 Card parado há muito tempo. Recomenda-se revisar a necessidade ou arquivar se não for mais relevante.")
    
    # ===== TIMELINE DE TRANSIÇÕES =====
    if historico:
        exibir_timeline_transicoes(historico, "📜 Timeline Completa do Card")
    
    # ===== CARDS VINCULADOS =====
    exibir_cards_vinculados(links)
    
    # ===== COMENTÁRIOS =====
    exibir_comentarios(comentarios, projeto="QA")


def exibir_detalhes_pb(card: Dict, links: List[Dict], comentarios: List[Dict], historico: List[Dict] = None):
    """Exibe detalhes para projeto PB (Backlog) - Sem bugs, foco em prioridade."""
    
    # Garante que historico seja uma lista
    if historico is None:
        historico = []
    
    # ===== KPIs PRINCIPAIS (CARDS ESTILIZADOS - PB) =====
    # Cores por status
    status_cores = {
        "Done": "#22c55e", "Concluído": "#22c55e",
        "Em Validação": "#3b82f6", "Aguardando Validação": "#f59e0b",
        "Desenvolvimento": "#8b5cf6", "Code Review": "#ec4899",
        "Blocked": "#ef4444", "Reprovado": "#ef4444",
        "Backlog": "#6b7280", "To Do": "#6b7280"
    }
    status_cor = status_cores.get(card['status'], "#6b7280")
    sp_valor = card['sp'] if card['sp'] > 0 else "N/A"
    
    st.markdown(f"""
    <div style='display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;'>
        <div style='background: linear-gradient(135deg, {status_cor}15, {status_cor}05); border: 1px solid {status_cor}40; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>📌</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Status</div>
            <div style='font-size: 14px; font-weight: 600; color: {status_cor}; margin-top: 4px; word-wrap: break-word;'>{card['status']}</div>
        </div>
        <div style='background: linear-gradient(135deg, #6366f115, #6366f105); border: 1px solid #6366f140; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>🎯</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Tipo</div>
            <div style='font-size: 14px; font-weight: 600; color: #6366f1; margin-top: 4px;'>{card['tipo']}</div>
        </div>
        <div style='background: linear-gradient(135deg, #f9731615, #f9731605); border: 1px solid #f9731640; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>⚡</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Prioridade</div>
            <div style='font-size: 14px; font-weight: 600; color: #f97316; margin-top: 4px;'>{card['prioridade']}</div>
        </div>
        <div style='background: linear-gradient(135deg, #3b82f615, #3b82f605); border: 1px solid #3b82f640; 
                    border-radius: 12px; padding: 16px; text-align: center;'>
            <div style='font-size: 24px; margin-bottom: 8px;'>📊</div>
            <div style='font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px;'>Estimativa</div>
            <div style='font-size: 14px; font-weight: 600; color: #3b82f6; margin-top: 4px;'>{sp_valor} SP</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== INDICADOR DE PRIORIZAÇÃO =====
    prioridade_map = {
        "Highest": ("#ef4444", "🔴", "Crítica"),
        "High": ("#f97316", "🟠", "Alta"),
        "Medium": ("#eab308", "🟡", "Média"),
        "Low": ("#22c55e", "🟢", "Baixa"),
        "Lowest": ("#6b7280", "⚪", "Muito Baixa")
    }
    prio_info = prioridade_map.get(card['prioridade'], ("#6b7280", "⚪", card['prioridade']))
    
    st.markdown(f"""
    <div style='background: {prio_info[0]}15; padding: 20px; border-radius: 12px; 
                border-left: 4px solid {prio_info[0]}; margin-bottom: 20px;'>
        <div style='display: flex; align-items: center; gap: 15px;'>
            <span style='font-size: 40px;'>{prio_info[1]}</span>
            <div>
                <h3 style='margin: 0; color: {prio_info[0]}; font-size: 1.3em;'>
                    Prioridade: {prio_info[2]}
                </h3>
                <p style='margin: 5px 0 0 0; color: #666; font-size: 0.9em;'>
                    Item de backlog aguardando priorização para desenvolvimento
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== INFORMAÇÕES DO ITEM =====
    with st.expander("📋 **Informações do Item de Backlog**", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            epic_texto = f"[{card.get('epic_link', '')}]({link_jira(card.get('epic_link', ''))})" if card.get('epic_link') else 'Sem Epic'
            st.markdown(f"""
| Campo | Valor |
|-------|-------|
| **Projeto** | {card['projeto']} |
| **Produto** | {card['produto']} |
| **Tipo** | {card['tipo_original']} |
| **Estimativa** | {card['sp']} SP |
| **Epic/Parent** | {epic_texto} |
            """)
        
        with col2:
            responsavel = card.get('desenvolvedor', 'Não atribuído')
            if responsavel == 'Não atribuído':
                responsavel = card.get('relator', 'Não informado')
            st.markdown(f"""
| Campo | Valor |
|-------|-------|
| **Relator** | {card.get('relator', 'Não informado')} |
| **Responsável** | {responsavel} |
| **Data Criação** | {card['criado'].strftime('%d/%m/%Y') if pd.notna(card['criado']) else 'N/A'} |
| **Última Atualização** | {card['atualizado'].strftime('%d/%m/%Y') if pd.notna(card['atualizado']) else 'N/A'} |
| **Status** | {card['status']} |
            """)
        
        # Componentes se houver
        componentes = card.get('componentes', [])
        if componentes:
            comp_texto = ', '.join(componentes)
            st.markdown(f"""
            <div style='background: #6366f115; padding: 10px 15px; border-radius: 8px; 
                        border-left: 3px solid #6366f1; margin-top: 10px;'>
                <strong style='color: #6366f1;'>🧩 Componentes:</strong> {comp_texto}
            </div>
            """, unsafe_allow_html=True)
        
        # Labels se houver
        labels = card.get('labels', [])
        if labels:
            labels_html = ' '.join([f"<span style='background: #8b5cf620; color: #8b5cf6; padding: 3px 8px; border-radius: 12px; font-size: 0.85em; margin-right: 5px;'>{l}</span>" for l in labels])
            st.markdown(f"""
            <div style='background: #8b5cf610; padding: 10px 15px; border-radius: 8px; 
                        border-left: 3px solid #8b5cf6; margin-top: 10px;'>
                <strong style='color: #8b5cf6;'>🏷️ Labels:</strong><br>
                <div style='margin-top: 8px;'>{labels_html}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Resolução/Roteiro em destaque se estiver preenchido
        resolucao = card.get('resolucao', '')
        if resolucao:
            cor_resolucao = "#22c55e" if resolucao.lower() in ['done', 'concluído', 'vai ser feito', 'aprovado'] else "#f59e0b"
            st.markdown(f"""
            <div style='background: {cor_resolucao}15; padding: 12px 15px; border-radius: 8px; 
                        border-left: 3px solid {cor_resolucao}; margin-top: 10px;'>
                <strong style='color: {cor_resolucao};'>📋 Resolução/Roteiro:</strong> {resolucao}
            </div>
            """, unsafe_allow_html=True)
    
    # ===== DESCRIÇÃO DO ITEM =====
    descricao = card.get('descricao', '')
    if descricao and len(descricao.strip()) > 0:
        with st.expander("📝 **Descrição**", expanded=True):
            # Limita a descrição se for muito longa
            desc_display = descricao[:2000] + '...' if len(descricao) > 2000 else descricao
            st.markdown(f"""
            <div style='background: #f8fafc; padding: 15px; border-radius: 8px; 
                        border: 1px solid #e2e8f0; line-height: 1.6;'>
                {desc_display}
            </div>
            """, unsafe_allow_html=True)
    
    # ===== TEMPO NO BACKLOG =====
    with st.expander("⏱️ **Tempo no Backlog**", expanded=True):
        dias_no_backlog = (datetime.now() - card['criado']).days if pd.notna(card['criado']) else 0
        
        col1, col2 = st.columns(2)
        
        with col1:
            backlog_cor = "#22c55e" if dias_no_backlog <= 30 else "#f97316" if dias_no_backlog <= 90 else "#ef4444"
            st.markdown(f"""
<div style='background: {backlog_cor}15; padding: 15px; border-radius: 8px; text-align: center; border-left: 3px solid {backlog_cor};'>
    <h3 style='margin:0; color: {backlog_cor}; font-size: 1.4em;'>{dias_no_backlog} dias</h3>
    <small style='color: #666;'>No Backlog</small><br>
    <small style='color: {backlog_cor};'>{'Recente' if dias_no_backlog <= 30 else 'Aguardando há algum tempo' if dias_no_backlog <= 90 else 'Revisar relevância'}</small>
</div>
            """, unsafe_allow_html=True)
        
        with col2:
            estimado = card['sp'] > 0
            est_cor = "#22c55e" if estimado else "#f97316"
            st.markdown(f"""
<div style='background: {est_cor}15; padding: 15px; border-radius: 8px; text-align: center; border-left: 3px solid {est_cor};'>
    <h3 style='margin:0; color: {est_cor}; font-size: 1.4em;'>{'✅' if estimado else '❓'}</h3>
    <small style='color: #666;'>Estimativa</small><br>
    <small style='color: {est_cor};'>{f'{card["sp"]} Story Points' if estimado else 'Não estimado'}</small>
</div>
            """, unsafe_allow_html=True)
    
    # ===== RESUMO =====
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📝 Situação do Item")
    
    insights = []
    
    if dias_no_backlog <= 30:
        insights.append("✅ Item recente no backlog")
    elif dias_no_backlog <= 90:
        insights.append("⚠️ Item aguardando há algum tempo")
    else:
        insights.append("🚨 Revisar relevância do item")
    
    if card['sp'] > 0:
        insights.append(f"✅ Estimado: {card['sp']} SP")
    else:
        insights.append("⚠️ Sem estimativa")
    
    if card['prioridade'] in ["Highest", "High"]:
        insights.append("🔴 Alta prioridade")
    
    cols = st.columns(len(insights)) if insights else [st]
    for i, insight in enumerate(insights):
        with cols[i]:
            st.markdown(insight)
    
    # ===== TIMELINE DE TRANSIÇÕES =====
    if historico:
        exibir_timeline_transicoes(historico, "📜 Timeline Completa do Card")
    
    # ===== CARDS VINCULADOS =====
    exibir_cards_vinculados(links)
    
    # ===== COMENTÁRIOS =====
    exibir_comentarios(comentarios, projeto="PB")


def exibir_timeline_transicoes(historico: List[Dict], titulo: str = "📜 Timeline Completa do Card"):
    """
    Exibe uma timeline visual completa com todas as transições do card.
    Usa components.html para scroll horizontal real.
    Scroll posicionado automaticamente no status atual.
    """
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not historico or len(historico) == 0:
        with st.expander(f"{titulo} (0 eventos)", expanded=False):
            st.info("Histórico não disponível")
        return
    
    # Filtra transições de status para métricas
    transicoes_status = [h for h in historico if h['tipo'] in ['criacao', 'transicao', 'resolucao']]
    
    # Calcula métricas gerais
    total_eventos = len(historico)
    total_dias = sum(e.get('duracao_dias', 0) for e in historico)
    qtd_retrabalhos = len([h for h in historico if h['tipo'] == 'transicao' and any(x in str(h.get('para', '')).lower() for x in ['desenvolviment', 'development', 'andamento'])])
    qtd_rejeicoes = len([h for h in historico if any(x in str(h.get('para', '')).lower() for x in ['reprovado', 'rejected', 'recusado'])])
    
    with st.expander(f"{titulo} ({len(historico)} eventos)", expanded=True):
        
        if historico:
            # Monta os cards da timeline com todos eventos
            cards_html = ""
            for i, evento in enumerate(historico):
                # Data completa com ano
                data_fmt = evento['data'].strftime('%d/%m/%Y') if evento['data'] else 'N/A'
                hora_fmt = evento['data'].strftime('%H:%M') if evento['data'] else ''
                
                # Dia da semana
                dias_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
                dia_semana = dias_semana[evento['data'].weekday()] if evento['data'] else ''
                
                # Duração formatada
                duracao_dias = evento.get('duracao_dias', 0)
                duracao_horas = evento.get('duracao_horas', 0)
                if duracao_dias > 0:
                    duracao = f"{duracao_dias} dia{'s' if duracao_dias > 1 else ''}"
                elif duracao_horas > 0:
                    duracao = f"{duracao_horas}h"
                else:
                    duracao = "< 1h"
                
                # Indicador de tempo (se ficou muito tempo)
                alerta_tempo = ""
                if duracao_dias >= 5:
                    alerta_tempo = "<div style='font-size:10px; color:#ef4444; margin-top:4px;'>⚠️ Tempo elevado</div>"
                elif duracao_dias >= 3:
                    alerta_tempo = "<div style='font-size:10px; color:#f59e0b; margin-top:4px;'>⏰ Atenção ao tempo</div>"
                
                is_current = (i == len(historico) - 1)
                current_id = "current-status" if is_current else ""
                badge = "<div style='background:linear-gradient(135deg, #22c55e 0%, #16a34a 100%); color:white; font-size:11px; padding:6px 12px; border-radius:12px; margin-top:10px; display:inline-block; font-weight:600; box-shadow:0 2px 4px rgba(34,197,94,0.3);'>📍 STATUS ATUAL</div>" if is_current else ""
                arrow = "" if is_current else "<div style='display:flex; align-items:center; padding:0 8px; color:#94a3b8; font-size:28px; font-weight:300;'>→</div>"
                
                # Número do passo
                passo_num = f"<div style='position:absolute; top:-10px; left:-10px; background:{evento['cor']}; color:white; font-size:10px; font-weight:700; width:22px; height:22px; border-radius:50%; display:flex; align-items:center; justify-content:center; box-shadow:0 2px 4px rgba(0,0,0,0.2);'>{i+1}</div>"
                
                # Campo modificado
                campo = evento.get('campo', 'Status')
                tipo = evento.get('tipo', 'transicao')
                
                # Ícone baseado no tipo
                tipo_icone = {
                    'criacao': '🎫 Criação',
                    'transicao': '🔄 Status',
                    'atribuicao': '👤 Atribuição',
                    'qa_atribuicao': '🧪 QA',
                    'sprint': '🏃 Sprint',
                    'estimativa': '📊 Estimativa',
                    'bugs': '🐛 Bugs',
                    'resolucao': '✅ Resolução'
                }.get(tipo, f'📋 {campo}')
                
                campo_display = f"<div style='font-size:11px; color:#64748b; margin-bottom:6px; background:#f1f5f9; padding:4px 8px; border-radius:6px; display:inline-block;'>{tipo_icone}</div>"
                
                # Valor anterior (de) se existir
                de_valor = evento.get('de', '')
                de_display = f"<div style='font-size:12px; color:#94a3b8; margin-bottom:4px;'><span style='text-decoration:line-through; color:#ef4444;'>{str(de_valor)[:25]}</span></div>" if de_valor else ""
                
                # Valor novo (para) - destaque principal
                para_valor = evento.get('para', 'N/A')
                
                # Autor
                autor = evento.get('autor', 'Sistema')
                
                # Detalhes extras se disponível
                detalhes = evento.get('detalhes', '')
                
                cards_html += f'''
                <div id="{current_id}" style="position:relative; flex:0 0 auto; width:220px; background:white; border-radius:14px; padding:18px; border-top:5px solid {evento['cor']}; box-shadow:0 4px 16px rgba(0,0,0,0.08); font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; {'border:2px solid #22c55e; box-shadow:0 4px 20px rgba(34,197,94,0.2);' if is_current else ''}">
                    {passo_num}
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
                        <div style="font-size:32px;">{evento['icone']}</div>
                        <div style="text-align:right;">
                            <div style="font-size:13px; color:#1e293b; font-weight:700;">{data_fmt}</div>
                            <div style="font-size:11px; color:#64748b;">{dia_semana}, {hora_fmt}</div>
                        </div>
                    </div>
                    {campo_display}
                    {de_display}
                    <div style="font-weight:700; font-size:14px; color:{evento['cor']}; margin-bottom:10px; word-wrap:break-word; line-height:1.4; padding:10px; background:{evento['cor']}15; border-radius:10px; border-left:3px solid {evento['cor']};">{str(para_valor)[:35]}</div>
                    <div style="display:flex; justify-content:space-between; align-items:center; padding-top:10px; border-top:1px solid #f1f5f9;">
                        <div style="font-size:11px; color:#64748b; max-width:110px; overflow:hidden; text-overflow:ellipsis;">👤 {str(autor)[:20]}</div>
                        <div style="font-size:11px; background:linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%); color:#475569; padding:5px 10px; border-radius:10px; font-weight:600;">⏱️ {duracao}</div>
                    </div>
                    {alerta_tempo}
                    {badge}
                </div>
                {arrow}
                '''
            
            altura = 380
            
            # HTML completo com scroll posicionado no final (status atual)
            html_completo = f'''
            <style>
                .timeline-container {{
                    overflow-x: auto;
                    overflow-y: hidden !important;
                    padding: 20px 15px;
                    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                    border-radius: 14px;
                    border: 1px solid #e2e8f0;
                    max-height: 320px;
                }}
                .timeline-container::-webkit-scrollbar {{
                    height: 10px;
                }}
                .timeline-container::-webkit-scrollbar-track {{
                    background: #e2e8f0;
                    border-radius: 4px;
                    margin-right: 5px;
                }}
                .timeline-container::-webkit-scrollbar-thumb {{
                    background: #94a3b8;
                    border-radius: 6px;
                    cursor: grab;
                }}
                .timeline-container::-webkit-scrollbar-thumb:hover {{
                    background: #64748b;
                    cursor: grabbing;
                }}
            </style>
            <div class="timeline-container" id="timeline-scroll">
                <div style="display:flex; flex-direction:row; align-items:stretch; gap:10px; width:max-content; height:fit-content;">
                    {cards_html}
                </div>
            </div>
            <p style="font-size:12px; color:#94a3b8; text-align:center; margin:12px 0 0 0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
                ⬅️ Arraste para ver histórico completo | 📍 Posicionado no status atual ➡️
            </p>
            <script>
                // Auto-scroll para o status atual (final)
                setTimeout(function() {{
                    var container = document.getElementById('timeline-scroll');
                    if (container) {{
                        container.scrollLeft = container.scrollWidth;
                    }}
                }}, 100);
            </script>
            '''
            
            components.html(html_completo, height=altura, scrolling=False)
        else:
            st.info("Nenhum evento registrado.")
        
        # ===== MÉTRICAS DE TEMPO =====
        st.markdown("---")
        st.markdown("##### ⏱️ Métricas de Tempo por Status")
        
        # Agrupa tempo por status
        tempo_por_status = {}
        for evento in transicoes_status:
            if evento['tipo'] == 'transicao' and evento.get('de'):
                status_anterior = evento['de']
                if status_anterior not in tempo_por_status:
                    tempo_por_status[status_anterior] = 0
                # Procura o tempo que ficou nesse status (olhando o evento anterior)
                idx = transicoes_status.index(evento)
                if idx > 0:
                    evento_anterior = transicoes_status[idx - 1]
                    tempo_por_status[status_anterior] += evento_anterior.get('duracao_dias', 0)
        
        # Adiciona tempo no status atual
        if transicoes_status:
            ultimo = transicoes_status[-1]
            status_atual = ultimo.get('para', 'Desconhecido')
            tempo_por_status[status_atual] = ultimo.get('duracao_dias', 0)
        
        if tempo_por_status:
            cols = st.columns(min(len(tempo_por_status), 5))
            for i, (status, dias) in enumerate(tempo_por_status.items()):
                with cols[i % len(cols)]:
                    icone, cor = obter_icone_status(status)
                    st.markdown(f"""
<div style='background:{cor}15; padding:10px; border-radius:8px; text-align:center; border-left:3px solid {cor};'>
    <div style='font-size:18px;'>{icone}</div>
    <div style='font-size:11px; color:#666;'>{status[:15]}{'...' if len(status) > 15 else ''}</div>
    <div style='font-size:16px; font-weight:600; color:{cor};'>{dias}d</div>
</div>
                    """, unsafe_allow_html=True)
        
        # ===== QUANTIDADE DE REPROVAÇÕES =====
        reprovacoes = len([h for h in historico if h['tipo'] == 'transicao' and h.get('para') and
                          any(x in h['para'].lower() for x in ['reprovado', 'rejected', 'recusado'])])
        retornos_dev = len([h for h in historico if h['tipo'] == 'transicao' and h.get('de') and h.get('para') and
                           any(x in h['de'].lower() for x in ['validação', 'qa', 'testing']) and
                           any(x in h['para'].lower() for x in ['desenvolvimento', 'andamento', 'development'])])
        
        if reprovacoes > 0 or retornos_dev > 0:
            st.markdown("---")
            st.markdown("##### 🔄 Análise de Retrabalho")
            col1, col2 = st.columns(2)
            
            with col1:
                cor_rep = "#ef4444" if reprovacoes > 0 else "#22c55e"
                st.markdown(f"""
<div style='background:{cor_rep}15; padding:12px; border-radius:8px; text-align:center; border-left:3px solid {cor_rep};'>
    <div style='font-size:22px;'>❌</div>
    <div style='font-size:24px; font-weight:700; color:{cor_rep};'>{reprovacoes}</div>
    <div style='font-size:12px; color:#666;'>Reprovações</div>
</div>
                """, unsafe_allow_html=True)
            
            with col2:
                cor_ret = "#f97316" if retornos_dev > 0 else "#22c55e"
                st.markdown(f"""
<div style='background:{cor_ret}15; padding:12px; border-radius:8px; text-align:center; border-left:3px solid {cor_ret};'>
    <div style='font-size:22px;'>🔄</div>
    <div style='font-size:24px; font-weight:700; color:{cor_ret};'>{retornos_dev}</div>
    <div style='font-size:12px; color:#666;'>Retornos p/ Dev</div>
</div>
                """, unsafe_allow_html=True)


def exibir_cards_vinculados(links: List[Dict]):
    """Exibe seção de cards vinculados com popup para navegar. Inclui links transitivos (2º nível)."""
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not links or len(links) == 0:
        # Mostra mensagem quando não há vínculos
        with st.expander("🔗 **Cards Vinculados (0)**", expanded=False):
            st.markdown("""
<div style='background: #f8fafc; padding: 15px; border-radius: 8px; text-align: center; color: #64748b;'>
    <span style='font-size: 1.5em;'>🔗</span><br>
    <span style='font-size: 0.9em;'>Nenhum card vinculado</span><br>
    <span style='font-size: 0.8em; color: #94a3b8;'>Este card não possui links com outros cards no Jira</span>
</div>
            """, unsafe_allow_html=True)
        return
    
    # Separa links de primeiro e segundo nível
    links_nivel_1 = [l for l in links if l.get('nivel', 1) == 1]
    links_nivel_2 = [l for l in links if l.get('nivel', 1) == 2]
    
    with st.expander(f"🔗 **Cards Vinculados ({len(links)})**", expanded=True):
        # Links de primeiro nível (diretos)
        if links_nivel_1:
            st.markdown("**🔵 Links Diretos:**")
            for link in links_nivel_1:
                tipo_cor = "#6366f1" if link['tipo'] == 'Pai' else "#22c55e" if link['tipo'] == 'Subtarefa' else "#f59e0b"
                card_popup_html = card_link_com_popup(link['ticket_id'])
                st.markdown(f"""
<div style='background: {tipo_cor}10; padding: 10px 15px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid {tipo_cor};'>
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <div>
            <span style='color: {tipo_cor}; font-weight: bold; font-size: 0.85em;'>{link['tipo']}</span>
            <span style='color: #666; font-size: 0.8em;'> • {link['direcao']}</span>
            <br>
            {card_popup_html}
            <span style='color: #666; font-size: 0.85em;'> - {link['titulo'][:60]}{'...' if len(link['titulo']) > 60 else ''}</span>
        </div>
        <div style='text-align: right;'>
            <span style='background: #e5e7eb; padding: 3px 8px; border-radius: 4px; font-size: 0.75em;'>
                {link['status']}
            </span>
        </div>
    </div>
</div>
                    """, unsafe_allow_html=True)
            
            # Links de segundo nível (transitivos)
            if links_nivel_2:
                st.markdown("---")
                st.markdown("**🔗 Outros Cards Relacionados** *(via cards vinculados)*:")
                st.caption("Cards conectados através dos links diretos acima")
                for link in links_nivel_2:
                    card_popup_html = card_link_com_popup(link['ticket_id'])
                    via_text = f" (via {link.get('via', '')})" if link.get('via') else ""
                    st.markdown(f"""
<div style='background: #f1f5f9; padding: 8px 12px; border-radius: 6px; margin-bottom: 6px; border-left: 3px dashed #94a3b8;'>
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <div>
            <span style='color: #64748b; font-size: 0.8em;'>{link['tipo']} • {link['direcao']}</span>
            <span style='color: #94a3b8; font-size: 0.75em;'>{via_text}</span>
            <br>
            {card_popup_html}
            <span style='color: #64748b; font-size: 0.8em;'> - {link['titulo'][:50]}{'...' if len(link['titulo']) > 50 else ''}</span>
        </div>
        <div>
            <span style='background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-size: 0.7em; color: #64748b;'>
                {link['status']}
            </span>
        </div>
    </div>
</div>
                    """, unsafe_allow_html=True)


def filtrar_e_classificar_comentarios(comentarios: List[Dict]) -> List[Dict]:
    """
    Filtra comentários de automação e classifica os relevantes.
    Adiciona contexto temporal (antes/depois de eventos importantes).
    
    Classificações:
    - bug: Comentário relacionado a bug/defeito
    - reprovacao: Comentário de reprovação
    - impedido: Comentário de impedimento
    - retorno_dev: Resposta do desenvolvedor a bug/reprovação
    - normal: Comentário comum (com contexto temporal)
    """
    if not comentarios:
        return []
    
    # Padrões de automação a serem filtrados (case insensitive)
    padroes_automacao = [
        "mentioned this issue in a commit",
        "mentioned this issue in a branch",
        "merge branch",
        "pushed a commit",
        "created a branch",
        "deleted branch",
        "opened a pull request",
        "closed a pull request",
        "merged a pull request",
        "mentioned this issue in a pull request",
        "linked a pull request",
        "connected this issue",
        "disconnected this issue",
        "moved this issue",
        "added a commit",
        "referenced this issue",
        "mentioned this page",
        "/confirmationcall on branch",
        "Elintondm /",
        "on branch sd-",
        "on branch SD-",
        "into homolog",
        "into master",
        "into main",
        "into develop",
    ]
    
    # Padrões para identificar comentários de bugs (AMPLIADO)
    padroes_bug = [
        # HASHTAG BUG (padrão usado pelo QA)
        "#bug",
        "# bug",
        "#Bug",
        "# Bug",
        # Padrões diretos de bug
        "bug encontrado",
        "bug identificado", 
        "bug registrado",
        "bugs identificados",
        "bugs encontrados",
        "alguns bugs",
        "bug:",
        "bug 1",
        "bug 2", 
        "bug 3",
        "bug 4",
        "bug 5",
        "bug#",
        "bug #",
        # Foram identificados
        "foram identificados",
        "foi identificado",
        "foram encontrados",
        "foi encontrado",
        # Defeitos/erros
        "defeito encontrado",
        "defeito identificado",
        "defeito:",
        "erro encontrado",
        "erro identificado",
        "erro:",
        "erro interno",
        "erro genérico",
        "falha encontrada",
        "falha identificada",
        "falha:",
        # Problemas de comportamento
        "problema encontrado",
        "problema identificado",
        "problema:",
        "inconsistência",
        "inconsistência encontrada",
        "falta de feedback",
        "não dá retorno",
        "sem retorno ao",
        "não dá feedback",
        # Interface/UX com problemas
        "funciona apenas como",
        "impedindo que o usuário",
        "obrigando-o",
        "obrigando o usuário",
        "não é possível realizar",
        "não estão traduzidas",
        "informação em inglês",
        "informações não estão",
        "deve impedir",
        "deveria impedir",
        "não impede",
        # Sistema retornando erros
        "sistema retornou",
        "sistema permitiu",
        "sistema não",
        "api retorna",
        "api retornou",
        "backend retornar",
        "retornar invalid",
        "retorna a informação",
        # Comportamento
        "não está funcionando",
        "não funciona",
        "não funcionou",
        "parou de funcionar",
        "comportamento incorreto",
        "comportamento inesperado",
        "comportamento errado",
        # Erros técnicos
        "retornou erro",
        "retorna erro",
        "apresentou erro",
        "apresenta erro",
        "deu erro",
        "está com erro",
        "erro ao",
        "falhou ao",
        "não consegue",
        "não carrega",
        "não abre",
        "não salva",
        "não exibe",
        "não mostra",
        "não aparece",
        "trava",
        "travou",
        "congelou",
        "quebrou",
        "crashou",
        # Porém/mas com problemas
        "porem",  # usuário usa sem acento
        "porém",
        "ainda não é possível",
        "ainda não",
        "mas não",
        "mas as informações",
        # Cenários de teste
        "cenário de bug",
        "cenário:",
        "cenário 1",
        "cenário 2",
        "cenário 3",
        "cenário 4",
        "cenário 5",
        "caso de bug",
        # Evidências
        "evidência de bug",
        "evidência do bug",
        "evidência:",
        "print do bug",
        "screenshot do erro",
        "anexo do bug",
        "devtools",
        "devTools",
        "DevTools",
        # Registro
        "registrando bug",
        "registrar bug",
        "abrir bug",
        "aberto bug",
        "abrindo bug",
        "novo bug",
        # QA reportando
        "encontrei um",
        "encontrei o",
        "identifiquei um",
        "identifiquei o",
        "verifiquei que",
        "percebi que",
        "notei que",
        "observei que",
        "ao testar",
        "durante o teste",
        "na validação",
        "validando",
        "ao tentar",
        "ao clicar",
        "ao acessar",
        "ao editar",
        "ao criar",
        "ao salvar",
    ]
    
    # Padrões para identificar comentários de reprovação
    padroes_reprovacao = [
        "reprovado",
        "reprovação",
        "reprovei",
        "reprovando",
        "não aprovado",
        "reprovar",
        "card reprovado",
        "tarefa reprovada",
        "retornando para",
        "devolvendo para",
        "devolvido para",
        "voltando para desenvolvimento",
        "retornar para desenvolvimento",
        "retornado para desenvolvimento",
        "ajustes necessários",
        "necessita de ajustes",
        "correções necessárias",
        "necessita correção",
        "não passou na validação",
        "não passou no teste",
        "falhou na validação",
        "não atende",
        "não atendeu",
        "favor corrigir",
        "por favor corrigir",
        "correção necessária",
        "precisa de correção",
        "precisa corrigir",
        "precisa ajustar",
        "não está conforme",
        "fora do esperado",
        "diferente do esperado",
    ]
    
    # Padrões para identificar comentários de impedimento
    padroes_impedido = [
        "impedido",
        "impedimento",
        "bloqueado",
        "bloqueio",
        "dependência",
        "aguardando",
        "aguardar",
        "esperar",
        "esperando",
        "não pode prosseguir",
        "não consigo continuar",
        "não é possível continuar",
        "parado",
        "pausado",
        "travado",
        "bloqueando",
        "depende de",
        "dependendo de",
        "precisa de",
        "necessita de ambiente",
        "ambiente indisponível",
        "sem acesso",
        "não tenho acesso",
        "aguardando retorno",
        "aguardando resposta",
    ]
    
    # Padrões para identificar retorno do DEV
    padroes_retorno_dev = [
        "corrigido",
        "correção feita",
        "correção realizada",
        "ajustado",
        "ajuste feito",
        "ajuste realizado",
        "pronto para",
        "disponível para",
        "liberado para",
        "pode testar",
        "pode validar",
        "favor validar",
        "por favor validar",
        "validar novamente",
        "retestando",
        "para revalidação",
        "para retestar",
        "já corrigi",
        "já ajustei",
        "feito o ajuste",
        "feita a correção",
        "resolvido",
        "solucionado",
        "implementado",
        "alterado conforme",
        "atualizado conforme",
    ]
    
    # Primeira passagem: filtrar automações e classificar
    comentarios_pre = []
    for com in comentarios:
        texto_lower = com.get('texto', '').lower()
        autor = com.get('autor', '').lower()
        
        # Verifica se é automação (pula se for)
        eh_automacao = False
        for padrao in padroes_automacao:
            if padrao.lower() in texto_lower:
                eh_automacao = True
                break
        
        if any(bot in autor for bot in ['automation', 'bot', 'github', 'bitbucket', 'gitlab', 'jira']):
            eh_automacao = True
        
        if eh_automacao:
            continue
        
        # Classifica o comentário (ordem de prioridade)
        classificacao = 'normal'
        
        # 1. Verifica bug (maior prioridade para QA)
        for padrao in padroes_bug:
            if padrao in texto_lower:
                classificacao = 'bug'
                break
        
        # 2. Verifica reprovação
        if classificacao == 'normal':
            for padrao in padroes_reprovacao:
                if padrao in texto_lower:
                    classificacao = 'reprovacao'
                    break
        
        # 3. Verifica impedimento
        if classificacao == 'normal':
            for padrao in padroes_impedido:
                if padrao in texto_lower:
                    classificacao = 'impedido'
                    break
        
        # 4. Verifica retorno do DEV
        if classificacao == 'normal':
            for padrao in padroes_retorno_dev:
                if padrao in texto_lower:
                    classificacao = 'retorno_dev'
                    break
        
        # Parse da data
        try:
            data_parsed = datetime.fromisoformat(com['data'].replace('Z', '+00:00')).replace(tzinfo=None)
        except:
            data_parsed = datetime.now()
        
        comentarios_pre.append({
            **com,
            'classificacao': classificacao,
            'data_parsed': data_parsed,
            'contexto': None
        })
    
    # Ordena por data
    comentarios_pre.sort(key=lambda x: x['data_parsed'])
    
    # Segunda passagem: adicionar contexto temporal
    eventos = []
    for i, com in enumerate(comentarios_pre):
        if com['classificacao'] in ['bug', 'reprovacao', 'impedido']:
            eventos.append({
                'indice': i,
                'tipo': com['classificacao'],
                'data': com['data_parsed'],
                'numero': len([e for e in eventos if e['tipo'] == com['classificacao']]) + 1
            })
    
    # Atribui contexto aos comentários normais e retorno_dev
    for i, com in enumerate(comentarios_pre):
        if com['classificacao'] in ['normal', 'retorno_dev']:
            evento_anterior = None
            evento_posterior = None
            
            for ev in eventos:
                if ev['indice'] < i:
                    evento_anterior = ev
                elif ev['indice'] > i and evento_posterior is None:
                    evento_posterior = ev
            
            if evento_anterior and evento_posterior:
                dist_ant = i - evento_anterior['indice']
                dist_pos = evento_posterior['indice'] - i
                
                if dist_ant <= dist_pos:
                    tipo_nome = {'bug': 'Bug', 'reprovacao': 'Reprovação', 'impedido': 'Impedimento'}[evento_anterior['tipo']]
                    com['contexto'] = f"Após {tipo_nome} #{evento_anterior['numero']}"
                else:
                    tipo_nome = {'bug': 'Bug', 'reprovacao': 'Reprovação', 'impedido': 'Impedimento'}[evento_posterior['tipo']]
                    com['contexto'] = f"Antes {tipo_nome} #{evento_posterior['numero']}"
            elif evento_anterior:
                tipo_nome = {'bug': 'Bug', 'reprovacao': 'Reprovação', 'impedido': 'Impedimento'}[evento_anterior['tipo']]
                com['contexto'] = f"Após {tipo_nome} #{evento_anterior['numero']}"
            elif evento_posterior:
                tipo_nome = {'bug': 'Bug', 'reprovacao': 'Reprovação', 'impedido': 'Impedimento'}[evento_posterior['tipo']]
                com['contexto'] = f"Antes {tipo_nome} #{evento_posterior['numero']}"
    
    # Numera os eventos no resultado final
    contadores = {'bug': 0, 'reprovacao': 0, 'impedido': 0, 'retorno_dev': 0}
    for com in comentarios_pre:
        if com['classificacao'] in contadores:
            contadores[com['classificacao']] += 1
            com['numero_evento'] = contadores[com['classificacao']]
    
    return comentarios_pre


def exibir_comentarios(comentarios: List[Dict], projeto: str = "SD"):
    """Exibe seção de comentários do card (filtrados e classificados) com filtros interativos."""
    
    # Usa classificação diferente para PB (Product Backlog)
    if projeto == "PB":
        exibir_comentarios_pb(comentarios)
        return
    
    # Para SD e QA: classificação com tags de QA
    comentarios_filtrados = filtrar_e_classificar_comentarios(comentarios)
    
    total_original = len(comentarios) if comentarios else 0
    total_filtrado = len(comentarios_filtrados)
    filtrados = total_original - total_filtrado
    
    # Conta por classificação
    bugs = sum(1 for c in comentarios_filtrados if c.get('classificacao') == 'bug')
    reprovacoes = sum(1 for c in comentarios_filtrados if c.get('classificacao') == 'reprovacao')
    impedidos = sum(1 for c in comentarios_filtrados if c.get('classificacao') == 'impedido')
    retornos = sum(1 for c in comentarios_filtrados if c.get('classificacao') == 'retorno_dev')
    normais = sum(1 for c in comentarios_filtrados if c.get('classificacao') == 'normal')
    
    if comentarios_filtrados and len(comentarios_filtrados) > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Monta título com contagens
        titulo_extra = []
        if bugs > 0:
            titulo_extra.append(f"🐛 {bugs}")
        if reprovacoes > 0:
            titulo_extra.append(f"❌ {reprovacoes}")
        if impedidos > 0:
            titulo_extra.append(f"🚫 {impedidos}")
        if retornos > 0:
            titulo_extra.append(f"🔄 {retornos}")
        titulo_sufixo = f" | {' '.join(titulo_extra)}" if titulo_extra else ""
        
        with st.expander(f"💬 **Comentários ({total_filtrado})**{titulo_sufixo}", expanded=True):
            # Aviso sobre comentários filtrados
            if filtrados > 0:
                st.caption(f"ℹ️ {filtrados} comentário(s) de automação foram ocultados")
            
            # FILTROS INTERATIVOS
            st.markdown("##### 🔍 Filtrar comentários:")
            
            # Filtro de busca por texto
            col_busca, col_autor = st.columns([2, 1])
            with col_busca:
                busca_texto = st.text_input("🔎 Buscar no texto:", placeholder="Digite para filtrar...", key="busca_comentario_texto")
            
            # Filtro por autor
            autores = list(set([c.get('autor', 'Desconhecido') for c in comentarios_filtrados]))
            autores.sort()
            with col_autor:
                autor_selecionado = st.selectbox("👤 Filtrar por autor:", ["Todos"] + autores, key="filtro_autor_comentario")
            
            # Filtros por tipo
            st.markdown("**Por tipo:**")
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                filtro_todos = st.checkbox("Todos", value=True, key="filtro_com_todos")
            with col2:
                filtro_bug = st.checkbox(f"🐛 Bug ({bugs})", value=False, key="filtro_com_bug", disabled=bugs==0)
            with col3:
                filtro_reprov = st.checkbox(f"❌ Reprov ({reprovacoes})", value=False, key="filtro_com_reprov", disabled=reprovacoes==0)
            with col4:
                filtro_imped = st.checkbox(f"🚫 Imped ({impedidos})", value=False, key="filtro_com_imped", disabled=impedidos==0)
            with col5:
                filtro_retorno = st.checkbox(f"🔄 Retorno ({retornos})", value=False, key="filtro_com_retorno", disabled=retornos==0)
            with col6:
                filtro_normal = st.checkbox(f"💬 Outros ({normais})", value=False, key="filtro_com_normal", disabled=normais==0)
            
            # Determina quais tipos exibir
            tipos_exibir = []
            if filtro_todos and not (filtro_bug or filtro_reprov or filtro_imped or filtro_retorno or filtro_normal):
                tipos_exibir = ['bug', 'reprovacao', 'impedido', 'retorno_dev', 'normal']
            else:
                if filtro_bug:
                    tipos_exibir.append('bug')
                if filtro_reprov:
                    tipos_exibir.append('reprovacao')
                if filtro_imped:
                    tipos_exibir.append('impedido')
                if filtro_retorno:
                    tipos_exibir.append('retorno_dev')
                if filtro_normal:
                    tipos_exibir.append('normal')
            
            # Se nenhum selecionado, mostra todos
            if not tipos_exibir:
                tipos_exibir = ['bug', 'reprovacao', 'impedido', 'retorno_dev', 'normal']
            
            # Filtra comentários por tipo
            comentarios_exibir = [c for c in comentarios_filtrados if c.get('classificacao') in tipos_exibir]
            
            # Aplica filtro de busca por texto
            if busca_texto:
                busca_lower = busca_texto.lower()
                comentarios_exibir = [c for c in comentarios_exibir if busca_lower in c.get('texto', '').lower()]
            
            # Aplica filtro por autor
            if autor_selecionado and autor_selecionado != "Todos":
                comentarios_exibir = [c for c in comentarios_exibir if c.get('autor') == autor_selecionado]
            
            st.markdown("---")
            
            # Legenda
            st.markdown("""
            <div style='display: flex; gap: 12px; margin-bottom: 15px; flex-wrap: wrap; font-size: 0.85em;'>
                <span>🐛 <b style='color: #dc2626;'>Bug</b></span>
                <span>❌ <b style='color: #ea580c;'>Reprovação</b></span>
                <span>🚫 <b style='color: #9333ea;'>Impedimento</b></span>
                <span>🔄 <b style='color: #0891b2;'>Retorno DEV</b></span>
                <span>💬 <b style='color: #64748b;'>Contexto</b></span>
            </div>
            """, unsafe_allow_html=True)
            
            if not comentarios_exibir:
                st.info("Nenhum comentário encontrado para os filtros selecionados.")
            else:
                st.caption(f"Exibindo {len(comentarios_exibir)} de {total_filtrado} comentários")
            
            for i, com in enumerate(comentarios_exibir):
                # Formata a data
                try:
                    data_com = datetime.fromisoformat(com['data'].replace('Z', '+00:00'))
                    data_formatada = data_com.strftime('%d/%m/%Y %H:%M')
                except:
                    data_formatada = com['data'][:10] if com['data'] else 'Data desconhecida'
                
                # Define cores e badges baseado na classificação
                classificacao = com.get('classificacao', 'normal')
                numero_evento = com.get('numero_evento', '')
                contexto = com.get('contexto', '')
                
                if classificacao == 'bug':
                    cor_borda = '#dc2626'
                    cor_fundo = '#fef2f2'
                    cor_avatar = '#dc2626'
                    badge = f'<span style="background: #dc2626; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; font-weight: bold;">🐛 Bug #{numero_evento}</span>'
                elif classificacao == 'reprovacao':
                    cor_borda = '#ea580c'
                    cor_fundo = '#fff7ed'
                    cor_avatar = '#ea580c'
                    badge = f'<span style="background: #ea580c; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; font-weight: bold;">❌ Reprovação #{numero_evento}</span>'
                elif classificacao == 'impedido':
                    cor_borda = '#9333ea'
                    cor_fundo = '#faf5ff'
                    cor_avatar = '#9333ea'
                    badge = f'<span style="background: #9333ea; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; font-weight: bold;">🚫 Impedimento #{numero_evento}</span>'
                elif classificacao == 'retorno_dev':
                    cor_borda = '#0891b2'
                    cor_fundo = '#ecfeff'
                    cor_avatar = '#0891b2'
                    contexto_badge = f' <span style="background: #e2e8f0; color: #475569; padding: 2px 6px; border-radius: 8px; font-size: 0.7em; margin-left: 5px;">{contexto}</span>' if contexto else ''
                    badge = f'<span style="background: #0891b2; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; font-weight: bold;">🔄 Retorno #{numero_evento}</span>{contexto_badge}'
                else:
                    cor_borda = '#94a3b8'
                    cor_fundo = '#f8fafc'
                    cor_avatar = '#64748b'
                    if contexto:
                        badge = f'<span style="background: #e2e8f0; color: #475569; padding: 3px 10px; border-radius: 12px; font-size: 0.75em;">{contexto}</span>'
                    else:
                        badge = ''
                
                st.markdown(f"""
<div style='background: {cor_fundo}; padding: 14px 16px; border-radius: 10px; margin-bottom: 12px; border-left: 4px solid {cor_borda}; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'>
    <div style='display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-bottom: 10px;'>
        <div style='display: flex; align-items: center; gap: 10px;'>
            <div style='width: 36px; height: 36px; border-radius: 50%; background: {cor_avatar}; 
                        display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 0.9em;'>
                {com['autor'][0].upper() if com['autor'] else '?'}
            </div>
            <div>
                <strong style='color: #1e293b; font-size: 0.95em;'>{com['autor']}</strong>
                <div style='color: #64748b; font-size: 0.8em;'>{data_formatada}</div>
            </div>
        </div>
        <div>{badge}</div>
    </div>
    <div style='color: #334155; font-size: 0.9em; line-height: 1.6; padding-left: 46px; white-space: pre-wrap;'>{com['texto'][:1000]}{'...' if len(com['texto']) > 1000 else ''}</div>
</div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        filtrados_msg = f" ({filtrados} de automação ocultados)" if filtrados > 0 else ""
        with st.expander(f"💬 **Comentários (0)**{filtrados_msg}", expanded=False):
            if filtrados > 0:
                st.caption(f"ℹ️ Este card tem {filtrados} comentário(s) de automação que foram ocultados.")
            else:
                st.caption("Nenhum comentário de usuário neste card.")


def filtrar_comentarios_pb(comentarios: List[Dict]) -> List[Dict]:
    """
    Filtra e classifica comentários para Product Backlog (PB).
    Tags específicas para contexto de produto, não de QA.
    
    Classificações PB:
    - decisao: Aprovações, decisões, definições
    - duvida: Perguntas, questionamentos
    - requisito: Detalhamento, escopo, critérios
    - alinhamento: Reuniões, alinhamentos
    - normal: Comentários gerais
    """
    if not comentarios:
        return []
    
    # Padrões de automação a serem filtrados
    padroes_automacao = [
        "mentioned this issue in a commit",
        "mentioned this issue in a branch",
        "merge branch",
        "pushed a commit",
        "created a branch",
        "deleted branch",
        "opened a pull request",
        "closed a pull request",
        "merged a pull request",
        "mentioned this issue in a pull request",
        "linked a pull request",
        "connected this issue",
        "referenced this issue",
        "/confirmationcall on branch",
        "on branch sd-",
        "on branch SD-",
        "on branch pb-",
        "on branch PB-",
    ]
    
    # Padrões para DECISÃO/APROVAÇÃO
    padroes_decisao = [
        "aprovado",
        "aprovação",
        "aprovei",
        "aprovar",
        "decidido",
        "decisão",
        "definido",
        "definição",
        "definimos",
        "ficou definido",
        "ficou decidido",
        "vamos fazer",
        "vamos seguir",
        "seguir com",
        "ok para",
        "pode seguir",
        "pode prosseguir",
        "liberado",
        "confirmado",
        "confirmação",
        "validado pelo",
        "validado por",
        "alinhado com",
        "combinado",
        "acordado",
    ]
    
    # Padrões para DÚVIDA/PERGUNTA
    padroes_duvida = [
        "dúvida",
        "duvida",
        "pergunta",
        "questão",
        "questao",
        "?",  # comentários com interrogação
        "não entendi",
        "não ficou claro",
        "poderia esclarecer",
        "pode explicar",
        "como funciona",
        "como seria",
        "qual seria",
        "qual é",
        "o que seria",
        "o que significa",
        "faz sentido",
        "seria possível",
        "é possível",
        "tem como",
        "precisamos entender",
        "preciso entender",
        "precisamos definir",
        "aguardando esclarecimento",
        "aguardando retorno",
        "favor esclarecer",
        "por favor esclarecer",
    ]
    
    # Padrões para REQUISITO/ESCOPO
    padroes_requisito = [
        "requisito",
        "critério de aceite",
        "critérios de aceite",
        "criterio de aceite",
        "ac:",
        "escopo",
        "funcionalidade",
        "deve permitir",
        "deve ser possível",
        "o sistema deve",
        "o usuário deve",
        "o usuário poderá",
        "será necessário",
        "deverá",
        "regra de negócio",
        "regra:",
        "detalhamento",
        "especificação",
        "fluxo:",
        "comportamento esperado",
        "cenário de uso",
        "caso de uso",
        "user story",
        "história de usuário",
        "como um",
        "eu quero",
        "para que",
    ]
    
    # Padrões para ALINHAMENTO
    padroes_alinhamento = [
        "alinhamento",
        "alinhado",
        "alinhei",
        "reunião",
        "conversei",
        "conversamos",
        "falei com",
        "falamos com",
        "discutimos",
        "discutido",
        "apresentamos",
        "apresentado",
        "feedback do",
        "retorno do",
        "segundo o",
        "conforme",
        "de acordo com",
        "stakeholder",
        "product owner",
        "po disse",
        "cliente disse",
        "cliente solicitou",
        "solicitação do",
        "pedido do",
    ]
    
    comentarios_filtrados = []
    
    for com in comentarios:
        texto_lower = com.get('texto', '').lower()
        autor = com.get('autor', '').lower()
        
        # Verifica se é automação
        eh_automacao = False
        for padrao in padroes_automacao:
            if padrao.lower() in texto_lower:
                eh_automacao = True
                break
        
        if any(bot in autor for bot in ['automation', 'bot', 'github', 'bitbucket', 'gitlab', 'jira']):
            eh_automacao = True
        
        if eh_automacao:
            continue
        
        # Classifica (ordem de prioridade)
        classificacao = 'normal'
        
        # 1. Decisão
        for padrao in padroes_decisao:
            if padrao in texto_lower:
                classificacao = 'decisao'
                break
        
        # 2. Dúvida (se não foi decisão)
        if classificacao == 'normal':
            for padrao in padroes_duvida:
                if padrao in texto_lower:
                    classificacao = 'duvida'
                    break
        
        # 3. Requisito
        if classificacao == 'normal':
            for padrao in padroes_requisito:
                if padrao in texto_lower:
                    classificacao = 'requisito'
                    break
        
        # 4. Alinhamento
        if classificacao == 'normal':
            for padrao in padroes_alinhamento:
                if padrao in texto_lower:
                    classificacao = 'alinhamento'
                    break
        
        # Parse da data
        try:
            data_parsed = datetime.fromisoformat(com['data'].replace('Z', '+00:00')).replace(tzinfo=None)
        except:
            data_parsed = datetime.now()
        
        comentarios_filtrados.append({
            **com,
            'classificacao': classificacao,
            'data_parsed': data_parsed,
        })
    
    # Ordena por data
    comentarios_filtrados.sort(key=lambda x: x['data_parsed'])
    
    # Numera os eventos
    contadores = {'decisao': 0, 'duvida': 0, 'requisito': 0, 'alinhamento': 0}
    for com in comentarios_filtrados:
        if com['classificacao'] in contadores:
            contadores[com['classificacao']] += 1
            com['numero_evento'] = contadores[com['classificacao']]
    
    return comentarios_filtrados


def exibir_comentarios_pb(comentarios: List[Dict]):
    """Exibe comentários para cards de Product Backlog (PB) com tags de produto."""
    
    comentarios_filtrados = filtrar_comentarios_pb(comentarios)
    
    total_original = len(comentarios) if comentarios else 0
    total_filtrado = len(comentarios_filtrados)
    filtrados = total_original - total_filtrado
    
    # Conta por classificação
    decisoes = sum(1 for c in comentarios_filtrados if c.get('classificacao') == 'decisao')
    duvidas = sum(1 for c in comentarios_filtrados if c.get('classificacao') == 'duvida')
    requisitos = sum(1 for c in comentarios_filtrados if c.get('classificacao') == 'requisito')
    alinhamentos = sum(1 for c in comentarios_filtrados if c.get('classificacao') == 'alinhamento')
    normais = sum(1 for c in comentarios_filtrados if c.get('classificacao') == 'normal')
    
    if comentarios_filtrados and len(comentarios_filtrados) > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Monta título com contagens
        titulo_extra = []
        if decisoes > 0:
            titulo_extra.append(f"✅ {decisoes}")
        if duvidas > 0:
            titulo_extra.append(f"❓ {duvidas}")
        if requisitos > 0:
            titulo_extra.append(f"📋 {requisitos}")
        if alinhamentos > 0:
            titulo_extra.append(f"🤝 {alinhamentos}")
        titulo_sufixo = f" | {' '.join(titulo_extra)}" if titulo_extra else ""
        
        with st.expander(f"💬 **Comentários ({total_filtrado})**{titulo_sufixo}", expanded=True):
            if filtrados > 0:
                st.caption(f"ℹ️ {filtrados} comentário(s) de automação foram ocultados")
            
            # FILTROS INTERATIVOS para PB
            st.markdown("##### 🔍 Filtrar comentários:")
            
            # Filtro de busca por texto e autor
            col_busca, col_autor = st.columns([2, 1])
            with col_busca:
                busca_texto_pb = st.text_input("🔎 Buscar no texto:", placeholder="Digite para filtrar...", key="busca_comentario_texto_pb")
            
            autores_pb = list(set([c.get('autor', 'Desconhecido') for c in comentarios_filtrados]))
            autores_pb.sort()
            with col_autor:
                autor_selecionado_pb = st.selectbox("👤 Filtrar por autor:", ["Todos"] + autores_pb, key="filtro_autor_comentario_pb")
            
            # Filtros por tipo
            st.markdown("**Por tipo:**")
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                filtro_todos = st.checkbox("Todos", value=True, key="filtro_pb_todos")
            with col2:
                filtro_decisao = st.checkbox(f"✅ Decisão ({decisoes})", value=False, key="filtro_pb_decisao", disabled=decisoes==0)
            with col3:
                filtro_duvida = st.checkbox(f"❓ Dúvida ({duvidas})", value=False, key="filtro_pb_duvida", disabled=duvidas==0)
            with col4:
                filtro_requisito = st.checkbox(f"📋 Requisito ({requisitos})", value=False, key="filtro_pb_requisito", disabled=requisitos==0)
            with col5:
                filtro_alinhamento = st.checkbox(f"🤝 Alinhamento ({alinhamentos})", value=False, key="filtro_pb_alinhamento", disabled=alinhamentos==0)
            with col6:
                filtro_normal = st.checkbox(f"💬 Outros ({normais})", value=False, key="filtro_pb_normal", disabled=normais==0)
            
            # Determina quais tipos exibir
            tipos_exibir = []
            if filtro_todos and not (filtro_decisao or filtro_duvida or filtro_requisito or filtro_alinhamento or filtro_normal):
                tipos_exibir = ['decisao', 'duvida', 'requisito', 'alinhamento', 'normal']
            else:
                if filtro_decisao:
                    tipos_exibir.append('decisao')
                if filtro_duvida:
                    tipos_exibir.append('duvida')
                if filtro_requisito:
                    tipos_exibir.append('requisito')
                if filtro_alinhamento:
                    tipos_exibir.append('alinhamento')
                if filtro_normal:
                    tipos_exibir.append('normal')
            
            if not tipos_exibir:
                tipos_exibir = ['decisao', 'duvida', 'requisito', 'alinhamento', 'normal']
            
            comentarios_exibir = [c for c in comentarios_filtrados if c.get('classificacao') in tipos_exibir]
            
            # Aplica filtro de busca por texto
            if busca_texto_pb:
                busca_lower = busca_texto_pb.lower()
                comentarios_exibir = [c for c in comentarios_exibir if busca_lower in c.get('texto', '').lower()]
            
            # Aplica filtro por autor
            if autor_selecionado_pb and autor_selecionado_pb != "Todos":
                comentarios_exibir = [c for c in comentarios_exibir if c.get('autor') == autor_selecionado_pb]
            
            st.markdown("---")
            
            # Legenda para PB
            st.markdown("""
            <div style='display: flex; gap: 12px; margin-bottom: 15px; flex-wrap: wrap; font-size: 0.85em;'>
                <span>✅ <b style='color: #16a34a;'>Decisão</b></span>
                <span>❓ <b style='color: #ca8a04;'>Dúvida</b></span>
                <span>📋 <b style='color: #2563eb;'>Requisito</b></span>
                <span>🤝 <b style='color: #7c3aed;'>Alinhamento</b></span>
                <span>💬 <b style='color: #64748b;'>Geral</b></span>
            </div>
            """, unsafe_allow_html=True)
            
            if not comentarios_exibir:
                st.info("Nenhum comentário encontrado para os filtros selecionados.")
            else:
                st.caption(f"Exibindo {len(comentarios_exibir)} de {total_filtrado} comentários")
            
            for i, com in enumerate(comentarios_exibir):
                try:
                    data_com = datetime.fromisoformat(com['data'].replace('Z', '+00:00'))
                    data_formatada = data_com.strftime('%d/%m/%Y %H:%M')
                except:
                    data_formatada = com['data'][:10] if com['data'] else 'Data desconhecida'
                
                classificacao = com.get('classificacao', 'normal')
                numero_evento = com.get('numero_evento', '')
                
                if classificacao == 'decisao':
                    cor_borda = '#16a34a'  # Verde
                    cor_fundo = '#f0fdf4'
                    cor_avatar = '#16a34a'
                    badge = f'<span style="background: #16a34a; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; font-weight: bold;">✅ Decisão #{numero_evento}</span>'
                elif classificacao == 'duvida':
                    cor_borda = '#ca8a04'  # Amarelo escuro
                    cor_fundo = '#fefce8'
                    cor_avatar = '#ca8a04'
                    badge = f'<span style="background: #ca8a04; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; font-weight: bold;">❓ Dúvida #{numero_evento}</span>'
                elif classificacao == 'requisito':
                    cor_borda = '#2563eb'  # Azul
                    cor_fundo = '#eff6ff'
                    cor_avatar = '#2563eb'
                    badge = f'<span style="background: #2563eb; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; font-weight: bold;">📋 Requisito #{numero_evento}</span>'
                elif classificacao == 'alinhamento':
                    cor_borda = '#7c3aed'  # Roxo
                    cor_fundo = '#f5f3ff'
                    cor_avatar = '#7c3aed'
                    badge = f'<span style="background: #7c3aed; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; font-weight: bold;">🤝 Alinhamento #{numero_evento}</span>'
                else:
                    cor_borda = '#94a3b8'
                    cor_fundo = '#f8fafc'
                    cor_avatar = '#64748b'
                    badge = ''
                
                st.markdown(f"""
<div style='background: {cor_fundo}; padding: 14px 16px; border-radius: 10px; margin-bottom: 12px; border-left: 4px solid {cor_borda}; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'>
    <div style='display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-bottom: 10px;'>
        <div style='display: flex; align-items: center; gap: 10px;'>
            <div style='width: 36px; height: 36px; border-radius: 50%; background: {cor_avatar}; 
                        display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 0.9em;'>
                {com['autor'][0].upper() if com['autor'] else '?'}
            </div>
            <div>
                <strong style='color: #1e293b; font-size: 0.95em;'>{com['autor']}</strong>
                <div style='color: #64748b; font-size: 0.8em;'>{data_formatada}</div>
            </div>
        </div>
        <div>{badge}</div>
    </div>
    <div style='color: #334155; font-size: 0.9em; line-height: 1.6; padding-left: 46px; white-space: pre-wrap;'>{com['texto'][:1000]}{'...' if len(com['texto']) > 1000 else ''}</div>
</div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        filtrados_msg = f" ({filtrados} de automação ocultados)" if filtrados > 0 else ""
        with st.expander(f"💬 **Comentários (0)**{filtrados_msg}", expanded=False):
            if filtrados > 0:
                st.caption(f"ℹ️ Este card tem {filtrados} comentário(s) de automação que foram ocultados.")
            else:
                st.caption("Nenhum comentário neste card.")


# ==============================================================================
# DADOS DE TENDÊNCIA (HISTÓRICO)
# ==============================================================================

def gerar_dados_tendencia() -> pd.DataFrame:
    """Gera dados históricos para demonstração de tendências."""
    sprints = [f"Release {i}" for i in range(230, 239)]
    
    dados = []
    for i, sprint in enumerate(sprints):
        # Progressão gradual com alguma variação
        base_fk = 1.2 + (i * 0.22) + random.uniform(-0.2, 0.2)
        base_fpy = 40 + (i * 5) + random.uniform(-4, 4)
        base_ddp = 65 + (i * 3.5) + random.uniform(-4, 4)
        base_health = 45 + (i * 5.5) + random.uniform(-6, 6)
        
        dados.append({
            'sprint': sprint,
            'fator_k': round(min(4, max(0.5, base_fk)), 2),
            'fpy': round(min(95, max(25, base_fpy)), 1),
            'ddp': round(min(98, max(45, base_ddp)), 1),
            'health_score': round(min(95, max(20, base_health)), 0),
            'bugs_total': max(3, 35 - (i * 3) + random.randint(-4, 4)),
            'cards_total': random.randint(35, 55),
            'sp_total': random.randint(80, 150),
            'lead_time_medio': round(max(3, 14 - (i * 0.9) + random.uniform(-1, 1)), 1),
            'throughput': random.randint(25, 45),
            'taxa_reprovacao': round(max(2, 25 - (i * 2) + random.uniform(-3, 3)), 1),
        })
    
    return pd.DataFrame(dados)


# ==============================================================================
# EXPORTAÇÃO
# ==============================================================================

def exportar_para_csv(df: pd.DataFrame) -> str:
    """Exporta dados para CSV."""
    df_export = df[['ticket_id', 'titulo', 'tipo', 'status', 'desenvolvedor', 'qa', 
                    'sp', 'bugs', 'sprint', 'produto', 'prioridade', 'lead_time']].copy()
    return df_export.to_csv(index=False)


def exportar_para_excel(df: pd.DataFrame, metricas: Dict) -> bytes:
    """Exporta dados para Excel com múltiplas abas."""
    output = io.BytesIO()
    
    try:
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export = df[['ticket_id', 'titulo', 'tipo', 'status', 'desenvolvedor', 'qa', 
                            'sp', 'bugs', 'sprint', 'produto', 'lead_time']].copy()
            df_export.to_excel(writer, sheet_name='Cards', index=False)
            
            metricas_df = pd.DataFrame([
                {'Métrica': 'Total de Cards', 'Valor': len(df)},
                {'Métrica': 'Story Points Total', 'Valor': int(df['sp'].sum())},
                {'Métrica': 'Bugs Encontrados', 'Valor': int(df['bugs'].sum())},
                {'Métrica': 'Cards Concluídos', 'Valor': len(df[df['status_cat'] == 'done'])},
                {'Métrica': 'Health Score', 'Valor': metricas.get('health_score', 'N/A')},
            ])
            metricas_df.to_excel(writer, sheet_name='Métricas', index=False)
            
            dev_stats = df.groupby('desenvolvedor').agg({
                'ticket_id': 'count', 'sp': 'sum', 'bugs': 'sum'
            }).reset_index()
            dev_stats.columns = ['Desenvolvedor', 'Cards', 'SP', 'Bugs']
            dev_stats.to_excel(writer, sheet_name='Por Desenvolvedor', index=False)
        
        return output.getvalue()
    except:
        return None


# ==============================================================================
# ESTILOS CSS
# ==============================================================================

def aplicar_estilos():
    st.markdown("""
    <style>
    /* Header Nina - Fundo branco para melhor contraste */
    .nina-header {
        background: #ffffff;
        color: #1e293b;
        padding: 20px 25px;
        border-radius: 12px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .nina-logo {
        width: 60px;
        height: 60px;
        flex-shrink: 0;
    }
    .nina-logo svg {
        width: 100%;
        height: 100%;
    }
    .nina-title {
        font-size: 24px;
        font-weight: bold;
        margin: 0;
        color: #1e293b;
    }
    .nina-subtitle {
        font-size: 14px;
        opacity: 0.75;
        margin: 5px 0 0 0;
        color: #64748b;
    }
    .nina-highlight {
        color: #AF0C37;
        font-weight: bold;
    }
    
    /* Cards de status */
    .status-card {
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 2px solid;
        margin-bottom: 10px;
        transition: transform 0.2s;
        min-height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .status-card:hover { transform: translateY(-3px); }
    .status-green { background: rgba(34, 197, 94, 0.1); border-color: #22c55e; }
    .status-yellow { background: rgba(234, 179, 8, 0.1); border-color: #eab308; }
    .status-orange { background: rgba(249, 115, 22, 0.1); border-color: #f97316; }
    .status-red { background: rgba(239, 68, 68, 0.1); border-color: #ef4444; }
    .status-blue { background: rgba(59, 130, 246, 0.1); border-color: #3b82f6; }
    .status-purple { background: rgba(139, 92, 246, 0.1); border-color: #8b5cf6; }
    .status-gray { background: rgba(107, 114, 128, 0.1); border-color: #6b7280; }
    
    .big-number { font-size: 36px; font-weight: bold; margin: 0; }
    .card-label { font-size: 14px; opacity: 0.8; margin-top: 5px; }
    .card-sublabel { font-size: 12px; opacity: 0.6; margin-top: 3px; min-height: 16px; }
    
    /* Alertas */
    .alert-critical {
        background: rgba(239, 68, 68, 0.15);
        border-left: 4px solid #ef4444;
        padding: 15px; border-radius: 8px; margin: 10px 0;
    }
    .alert-warning {
        background: rgba(234, 179, 8, 0.15);
        border-left: 4px solid #eab308;
        padding: 15px; border-radius: 8px; margin: 10px 0;
    }
    .alert-info {
        background: rgba(59, 130, 246, 0.15);
        border-left: 4px solid #3b82f6;
        padding: 15px; border-radius: 8px; margin: 10px 0;
    }
    .alert-success {
        background: rgba(34, 197, 94, 0.15);
        border-left: 4px solid #22c55e;
        padding: 15px; border-radius: 8px; margin: 10px 0;
    }
    
    /* Ticket cards clicáveis */
    .ticket-card {
        border-radius: 10px;
        padding: 12px 15px;
        margin: 8px 0;
        border-left: 4px solid;
        background: rgba(100, 100, 100, 0.05);
        transition: all 0.2s ease;
    }
    .ticket-card:hover {
        transform: translateX(5px);
        background: rgba(100, 100, 100, 0.1);
    }
    .ticket-risk-high { border-left-color: #ef4444; }
    .ticket-risk-medium { border-left-color: #f97316; }
    .ticket-risk-low { border-left-color: #22c55e; }
    
    /* Barra de progresso */
    .progress-bar {
        background: #e5e7eb;
        border-radius: 10px;
        height: 24px;
        overflow: hidden;
        margin: 5px 0;
    }
    .progress-fill {
        height: 100%;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 12px;
    }
    
    /* Última atualização */
    .update-badge {
        background: rgba(34, 197, 94, 0.2);
        color: #166534;
        padding: 5px 12px;
        border-radius: 15px;
        font-size: 12px;
        display: inline-block;
    }
    .update-badge-stale {
        background: rgba(234, 179, 8, 0.2);
        color: #854d0e;
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, rgba(99, 102, 241, 0.1), transparent);
        padding: 10px 15px;
        border-radius: 8px;
        margin: 20px 0 10px 0;
        border-left: 4px solid #6366f1;
    }
    
    /* Scroll container para listagens */
    .scroll-container {
        max-height: 450px;
        overflow-y: auto;
        padding-right: 8px;
        margin: 10px 0;
        scrollbar-width: thin;
        scrollbar-color: #cbd5e1 #f1f5f9;
    }
    .scroll-container::-webkit-scrollbar {
        width: 6px;
    }
    .scroll-container::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 3px;
    }
    .scroll-container::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 3px;
    }
    .scroll-container::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    
    /* Card de listagem padrão */
    .card-lista {
        background: rgba(100, 100, 100, 0.05);
        padding: 12px 15px;
        margin: 8px 0;
        border-radius: 8px;
        border-left: 4px solid #64748b;
        transition: all 0.2s ease;
    }
    .card-lista:hover {
        transform: translateX(3px);
        background: rgba(100, 100, 100, 0.1);
    }
    /* Variantes coloridas - herdam estilos base */
    .card-lista-amarelo, .card-lista-verde, .card-lista-azul, .card-lista-roxo, .card-lista-vermelho, .card-lista-laranja {
        padding: 12px 15px;
        margin: 8px 0;
        border-radius: 8px;
        border-left: 4px solid;
        transition: all 0.2s ease;
    }
    .card-lista-amarelo:hover, .card-lista-verde:hover, .card-lista-azul:hover, .card-lista-roxo:hover, .card-lista-vermelho:hover, .card-lista-laranja:hover {
        transform: translateX(3px);
        filter: brightness(0.95);
    }
    .card-lista-amarelo { border-left-color: #f59e0b; background: rgba(245, 158, 11, 0.08); }
    .card-lista-verde { border-left-color: #22c55e; background: rgba(34, 197, 94, 0.08); }
    .card-lista-azul { border-left-color: #3b82f6; background: rgba(59, 130, 246, 0.08); }
    .card-lista-roxo { border-left-color: #8b5cf6; background: rgba(139, 92, 246, 0.08); }
    .card-lista-vermelho { border-left-color: #ef4444; background: rgba(239, 68, 68, 0.08); }
    .card-lista-laranja { border-left-color: #f97316; background: rgba(249, 115, 22, 0.08); }
    
    /* Hide Streamlit elements */
    #MainMenu, .stDeployButton { display: none !important; }
    </style>
    """, unsafe_allow_html=True)


def get_tooltip_help(tooltip_key: str) -> str:
    """Retorna texto de ajuda para st.metric (aparece no ícone ?)."""
    if tooltip_key not in TOOLTIPS:
        return ""
    
    tip = TOOLTIPS[tooltip_key]
    help_text = f"{tip['titulo']}: {tip['descricao']}"
    if tip.get('formula'):
        help_text += f" | Fórmula: {tip['formula']}"
    return help_text


# ==============================================================================
# COMPONENTES UI
# ==============================================================================

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


def formatar_tempo_relativo(dt: datetime) -> str:
    """
    Formata uma datetime como tempo relativo (ex: "há 5 min", "há 2h", "há 3 dias").
    
    Args:
        dt: datetime a ser formatada
        
    Returns:
        String formatada com tempo relativo
    """
    if dt is None or pd.isna(dt):
        return ""
    
    agora = datetime.now()
    
    # Garante que dt seja datetime
    if isinstance(dt, str):
        try:
            dt = pd.to_datetime(dt)
        except:
            return ""
    
    # Se dt tem timezone, remove para comparação
    if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    
    diff = agora - dt
    segundos = diff.total_seconds()
    
    if segundos < 0:
        return "agora"
    elif segundos < 60:
        return "agora"
    elif segundos < 3600:  # menos de 1 hora
        minutos = int(segundos / 60)
        return f"há {minutos} min"
    elif segundos < 86400:  # menos de 1 dia
        horas = int(segundos / 3600)
        return f"há {horas}h"
    elif segundos < 604800:  # menos de 1 semana
        dias = int(segundos / 86400)
        return f"há {dias}d"
    elif segundos < 2592000:  # menos de 30 dias
        semanas = int(segundos / 604800)
        return f"há {semanas} sem"
    else:
        meses = int(segundos / 2592000)
        return f"há {meses} mês" if meses == 1 else f"há {meses} meses"


def criar_card_metrica(valor: str, titulo: str, cor: str = "blue", subtitulo: str = "", tooltip_key: str = ""):
    """Cria card de métrica visual. tooltip_key é ignorado (usar st.metric com help para tooltips)."""
    # Sempre mostra sublabel para manter altura uniforme
    sublabel_content = subtitulo if subtitulo else "&nbsp;"
    st.markdown(f"""
    <div class="status-card status-{cor}">
        <p class="big-number">{valor}</p>
        <p class="card-label">{titulo}</p>
        <p class="card-sublabel">{sublabel_content}</p>
    </div>
    """, unsafe_allow_html=True)


def gerar_html_card_ticket(row: dict, compacto: bool = False) -> str:
    """Gera HTML de um card de ticket (retorna string, não renderiza)."""
    bugs = row.get('bugs', 0)
    risco = 'high' if bugs >= 3 else 'medium' if bugs >= 1 else 'low'
    card_link = card_link_com_popup(row.get('ticket_id', ''))
    titulo = str(row.get('titulo', ''))[:60] + ('...' if len(str(row.get('titulo', ''))) > 60 else '')
    cor_bug = '#ef4444' if bugs >= 3 else '#f97316' if bugs >= 1 else '#22c55e'
    
    # Ícone de bugs com Tabler
    bug_icon = gerar_icone_tabler_html('bug', tamanho=16, cor=cor_bug)
    
    if compacto:
        return f'<div class="ticket-card ticket-risk-{risco}"><div style="display: flex; justify-content: space-between; align-items: center;">{card_link}<span style="opacity: 0.7;">{row.get("sp", 0)} SP | {bug_icon}{bugs}</span></div><p style="margin: 5px 0 0 0; font-size: 13px; opacity: 0.9;">{titulo}</p></div>'
    else:
        status_badge = gerar_badge_status(row.get("status", "N/A"))
        return f'<div class="ticket-card ticket-risk-{risco}"><div style="display: flex; justify-content: space-between;">{card_link}<span style="color: {cor_bug}; font-weight: bold;">{bug_icon}{bugs} bugs</span></div><p style="margin: 8px 0;">{row.get("titulo", "")}</p><p style="font-size: 12px; opacity: 0.8;"><b>Dev:</b> {row.get("desenvolvedor", "N/A")} | <b>QA:</b> {row.get("qa", "N/A")} | <b>SP:</b> {row.get("sp", 0)} | {status_badge}</p></div>'


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

def criar_grafico_funil_qa(metricas_qa: Dict) -> go.Figure:
    """Cria gráfico de funil de validação QA."""
    funil = metricas_qa['funil']
    
    labels = ['⏳ Aguardando QA', '🧪 Em Validação', '✅ Concluído']
    values = [funil['waiting_qa'], funil['testing'], funil['done']]
    colors = ['#f59e0b', '#06b6d4', '#22c55e']
    
    if funil['blocked'] > 0:
        labels.append('🚫 Bloqueado')
        values.append(funil['blocked'])
        colors.append('#ef4444')
    
    if funil['rejected'] > 0:
        labels.append('❌ Reprovado')
        values.append(funil['rejected'])
        colors.append('#dc2626')
    
    fig = go.Figure(go.Funnel(
        y=labels, x=values,
        textinfo="value+percent total",
        marker=dict(color=colors),
        connector=dict(line=dict(color="royalblue", dash="dot", width=2))
    ))
    
    fig.update_layout(title="Funil de Validação QA", height=350, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def criar_grafico_tendencia_fator_k(df_tendencia: pd.DataFrame) -> go.Figure:
    """Cria gráfico de tendência do Fator K."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_tendencia['sprint'], y=df_tendencia['fator_k'],
        mode='lines+markers', name='Fator K',
        line=dict(color='#6366f1', width=3),
        marker=dict(size=10),
        hovertemplate='<b>%{x}</b><br>Fator K: %{y:.2f}<extra></extra>'
    ))
    
    # Faixas de maturidade
    fig.add_hline(y=3.0, line_dash="dash", line_color="#22c55e", annotation_text="Gold (≥3.0)")
    fig.add_hline(y=2.0, line_dash="dash", line_color="#eab308", annotation_text="Silver (≥2.0)")
    fig.add_hline(y=1.0, line_dash="dash", line_color="#f97316", annotation_text="Bronze (≥1.0)")
    
    fig.update_layout(
        title="📈 Evolução do Fator K (Maturidade)",
        xaxis_title="Sprint", yaxis_title="Fator K",
        hovermode='x unified', template='plotly_white', height=350
    )
    return fig


def criar_grafico_tendencia_qualidade(df_tendencia: pd.DataFrame) -> go.Figure:
    """Cria gráfico de tendência FPY e DDP."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_tendencia['sprint'], y=df_tendencia['fpy'],
        mode='lines+markers', name='FPY (%)',
        line=dict(color='#22c55e', width=2), marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=df_tendencia['sprint'], y=df_tendencia['ddp'],
        mode='lines+markers', name='DDP (%)',
        line=dict(color='#3b82f6', width=2), marker=dict(size=8)
    ))
    
    fig.add_hline(y=80, line_dash="dot", line_color="#22c55e", annotation_text="Meta FPY (80%)")
    fig.add_hline(y=85, line_dash="dot", line_color="#3b82f6", annotation_text="Meta DDP (85%)")
    
    fig.update_layout(
        title="📊 Evolução de Qualidade (FPY e DDP)",
        xaxis_title="Sprint", yaxis_title="Percentual (%)",
        hovermode='x unified', template='plotly_white', height=350,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def criar_grafico_tendencia_bugs(df_tendencia: pd.DataFrame) -> go.Figure:
    """Cria gráfico de tendência de bugs."""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_tendencia['sprint'], y=df_tendencia['bugs_total'],
        name='Bugs Encontrados', marker_color='#ef4444',
        text=df_tendencia['bugs_total'], textposition='outside'
    ))
    
    fig.add_trace(go.Scatter(
        x=df_tendencia['sprint'],
        y=df_tendencia['bugs_total'].rolling(3, min_periods=1).mean(),
        mode='lines', name='Média Móvel (3 sprints)',
        line=dict(color='#6366f1', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title="🐛 Bugs por Sprint",
        xaxis_title="Sprint", yaxis_title="Quantidade de Bugs",
        template='plotly_white', height=350, showlegend=True
    )
    return fig


def criar_grafico_tendencia_health(df_tendencia: pd.DataFrame) -> go.Figure:
    """Cria gráfico de tendência do Health Score."""
    fig = go.Figure()
    
    colors = ['#22c55e' if h >= 75 else '#eab308' if h >= 50 else '#f97316' if h >= 25 else '#ef4444' 
              for h in df_tendencia['health_score']]
    
    fig.add_trace(go.Bar(
        x=df_tendencia['sprint'], y=df_tendencia['health_score'],
        marker_color=colors,
        text=df_tendencia['health_score'].astype(int), textposition='outside'
    ))
    
    fig.add_hline(y=75, line_dash="dash", line_color="#22c55e", annotation_text="Saudável (≥75)")
    fig.add_hline(y=50, line_dash="dash", line_color="#eab308", annotation_text="Atenção (≥50)")
    
    fig.update_layout(
        title="🏥 Evolução do Health Score",
        xaxis_title="Sprint", yaxis_title="Health Score",
        template='plotly_white', height=350
    )
    return fig


def criar_grafico_throughput(df_tendencia: pd.DataFrame) -> go.Figure:
    """Cria gráfico de throughput."""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_tendencia['sprint'], y=df_tendencia['throughput'],
        name='Cards Entregues', marker_color='#3b82f6',
        text=df_tendencia['throughput'], textposition='outside'
    ))
    
    fig.add_trace(go.Scatter(
        x=df_tendencia['sprint'], y=df_tendencia['sp_total'],
        mode='lines+markers', name='SP Total',
        line=dict(color='#8b5cf6', width=2), yaxis='y2'
    ))
    
    fig.update_layout(
        title="📦 Throughput por Sprint",
        xaxis_title="Sprint",
        yaxis=dict(title="Cards", side='left'),
        yaxis2=dict(title="Story Points", side='right', overlaying='y'),
        template='plotly_white', height=350,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def criar_grafico_lead_time(df_tendencia: pd.DataFrame) -> go.Figure:
    """Cria gráfico de lead time."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_tendencia['sprint'], y=df_tendencia['lead_time_medio'],
        mode='lines+markers+text', name='Lead Time Médio',
        line=dict(color='#f59e0b', width=3), marker=dict(size=10),
        text=df_tendencia['lead_time_medio'].apply(lambda x: f"{x:.1f}d"),
        textposition='top center'
    ))
    
    fig.add_hline(y=7, line_dash="dash", line_color="#22c55e", annotation_text="Meta (≤7 dias)")
    
    fig.update_layout(
        title="⏱️ Lead Time Médio por Sprint",
        xaxis_title="Sprint", yaxis_title="Dias",
        template='plotly_white', height=350
    )
    return fig


def criar_grafico_reprovacao(df_tendencia: pd.DataFrame) -> go.Figure:
    """Cria gráfico de taxa de reprovação."""
    fig = go.Figure()
    
    colors = ['#ef4444' if r > 15 else '#f97316' if r > 10 else '#22c55e' 
              for r in df_tendencia['taxa_reprovacao']]
    
    fig.add_trace(go.Bar(
        x=df_tendencia['sprint'], y=df_tendencia['taxa_reprovacao'],
        marker_color=colors,
        text=df_tendencia['taxa_reprovacao'].apply(lambda x: f"{x:.0f}%"), textposition='outside'
    ))
    
    fig.add_hline(y=10, line_dash="dash", line_color="#22c55e", annotation_text="Meta (≤10%)")
    
    fig.update_layout(
        title="❌ Taxa de Reprovação por Sprint",
        xaxis_title="Sprint", yaxis_title="% Reprovados",
        template='plotly_white', height=350
    )
    return fig


def criar_grafico_estagio_por_produto(df: pd.DataFrame) -> go.Figure:
    """Cria gráfico de estágio por produto."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Sem dados", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    data = df.groupby(['produto', 'status_cat']).size().reset_index(name='count')
    
    fig = px.bar(
        data, x='produto', y='count', color='status_cat',
        color_discrete_map=STATUS_CORES,
        title='Estágio de Cards por Produto',
        labels={'count': 'Cards', 'produto': 'Produto', 'status_cat': 'Status'}
    )
    
    fig.update_layout(height=400, barmode='stack')
    return fig


def criar_grafico_hotfix_por_produto(df: pd.DataFrame) -> go.Figure:
    """Cria gráfico de hotfix por produto."""
    hotfix_df = df[df['tipo'] == 'HOTFIX']
    
    if hotfix_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Nenhum Hotfix encontrado", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    data = hotfix_df.groupby('produto').size().reset_index(name='count')
    
    fig = px.pie(
        data, values='count', names='produto',
        title='🔥 Hotfixes por Produto',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(height=350)
    return fig


# ==============================================================================
# ABAS DO DASHBOARD
# ==============================================================================

def criar_grafico_aging_backlog(faixas: Dict) -> go.Figure:
    """Cria gráfico de barras para faixas de aging do backlog."""
    labels = ['0-15 dias', '16-30 dias', '31-60 dias', '61-90 dias', '90+ dias']
    values = [faixas['0-15'], faixas['16-30'], faixas['31-60'], faixas['61-90'], faixas['90+']]
    colors = ['#22c55e', '#eab308', '#f97316', '#ef4444', '#7f1d1d']
    
    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker_color=colors,
        text=values,
        textposition='auto',
    ))
    
    fig.update_layout(
        title="📊 Distribuição por Idade no Backlog",
        xaxis_title="Faixa de Idade",
        yaxis_title="Quantidade de Cards",
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=False
    )
    
    return fig


def criar_grafico_prioridade_backlog(por_prioridade: Dict) -> go.Figure:
    """Cria gráfico de pizza para distribuição por prioridade."""
    labels = list(por_prioridade.keys())
    values = list(por_prioridade.values())
    
    # Cores por prioridade
    cores_prioridade = {
        'Highest': '#7f1d1d',
        'High': '#ef4444',
        'Alta': '#ef4444',
        'Medium': '#f59e0b',
        'Média': '#f59e0b',
        'Low': '#22c55e',
        'Baixa': '#22c55e',
        'Lowest': '#64748b',
    }
    colors = [cores_prioridade.get(l, '#6b7280') for l in labels]
    
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        marker_colors=colors,
        textinfo='label+percent',
        hole=0.4
    ))
    
    fig.update_layout(
        title="🎯 Distribuição por Prioridade",
        height=350,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


def criar_grafico_tipo_backlog(por_tipo: Dict) -> go.Figure:
    """Cria gráfico de barras horizontais para distribuição por tipo."""
    labels = list(por_tipo.keys())
    values = list(por_tipo.values())
    
    cores_tipo = {
        'TAREFA': '#3b82f6',
        'BUG': '#ef4444',
        'HOTFIX': '#f97316',
        'SUGESTÃO': '#8b5cf6',
    }
    colors = [cores_tipo.get(l, '#6b7280') for l in labels]
    
    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation='h',
        marker_color=colors,
        text=values,
        textposition='auto',
    ))
    
    fig.update_layout(
        title="📋 Distribuição por Tipo",
        xaxis_title="Quantidade",
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


def criar_grafico_backlog_por_produto(df_produto: pd.DataFrame) -> go.Figure:
    """Cria gráfico de barras para backlog por produto."""
    if df_produto.empty:
        fig = go.Figure()
        fig.add_annotation(text="Sem dados por produto", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_produto['Produto'],
        y=df_produto['Cards'],
        name='Cards',
        marker_color='#3b82f6',
        text=df_produto['Cards'],
        textposition='auto',
    ))
    
    fig.update_layout(
        title="📦 Backlog por Produto",
        xaxis_title="Produto",
        yaxis_title="Quantidade de Cards",
        height=350,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


def main():
    """Função principal do dashboard."""
    
    # ========== CSS GLOBAL PARA ESCONDER WARNINGS ==========
    # Injeta CSS imediatamente para esconder qualquer warning do CookieManager
    st.markdown("""
    <style>
    /* Esconde warnings/exceptions do Streamlit (CookieManager) */
    .stException, [data-testid="stException"], 
    .stWarning, [data-testid="stWarning"],
    div[data-testid="stNotification"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        overflow: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ========== VERIFICAR LOGIN (via session_state ou cookie) ==========
    if not verificar_login():
        # Mostra tela de login
        mostrar_tela_login()
        return
    
    # ========== USUÁRIO LOGADO - DASHBOARD ==========
    aplicar_estilos()
    
    # CSS global para popup de cards (permite escolher NinaDash ou Jira)
    st.markdown(CARD_POPUP_CSS, unsafe_allow_html=True)
    
    # Header principal com logo Nina
    mostrar_header_nina()
    
    # ========== GERENCIAMENTO DE QUERY PARAMS ==========
    # Captura query params para compartilhamento de busca
    query_params = st.query_params
    card_compartilhado = query_params.get("card", None)
    projeto_param = query_params.get("projeto", None)
    qa_compartilhado = query_params.get("qa", None)
    dev_compartilhado = query_params.get("dev", None)
    pessoa_compartilhada = query_params.get("pessoa", None)
    cliente_compartilhado = query_params.get("cliente", None)
    
    # Verifica se é um link compartilhado válido
    eh_link_compartilhado = any([card_compartilhado, qa_compartilhado, dev_compartilhado, pessoa_compartilhada, cliente_compartilhado])
    
    # Se NÃO é link compartilhado mas tem query_params de aba, limpa tudo
    # Isso evita "poluição" de URL quando o usuário navega normalmente
    if not eh_link_compartilhado and query_params.get("aba", None):
        # Limpa todos os query params para URL limpa
        st.query_params.clear()
    
    # Inicializa session_state para controle de busca
    if 'busca_ativa' not in st.session_state:
        st.session_state.busca_ativa = False
    if 'card_buscado' not in st.session_state:
        st.session_state.card_buscado = ""
    if 'projeto_buscado' not in st.session_state:
        st.session_state.projeto_buscado = "SD"
    
    # Inicializa modo Meu Dashboard
    if 'modo_consulta_personalizada' not in st.session_state:
        st.session_state.modo_consulta_personalizada = False
    
    # Verifica se veio via query param para Meu Dashboard
    if query_params.get("tela", None) == "meu_dashboard":
        st.session_state.modo_consulta_personalizada = True
    
    # ===============================================================
    # MODO MEU DASHBOARD - TELA SEPARADA COM SIDEBAR LIMPA
    # ===============================================================
    if st.session_state.modo_consulta_personalizada:
        # SIDEBAR MINIMALISTA - apenas logo, usuário e voltar
        with st.sidebar:
            # Logo
            st.markdown('''
            <div style="text-align: center; padding: 10px 0 5px 0;">
                <svg width="70" height="70" viewBox="0 0 187 187" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M173.709 89.2107C172.209 86.6048 169.414 84.838 166.225 84.838C163.036 84.838 160.241 86.5649 158.741 89.1627H151.683C149.465 58.8237 124.495 35 94.0216 35C63.5489 35 38.5862 58.8237 36.3678 89.1627H29.1759C27.6759 86.5649 24.8734 84.798 21.6682 84.798C18.463 84.798 15.6605 86.5806 14.1605 89.2031C13.4184 90.4899 13 92.001 13 93.6C13 95.1987 13.4184 96.7017 14.1605 97.997C15.6605 100.619 18.463 102.306 21.6682 102.306C24.8734 102.306 27.6838 100.435 29.1759 97.8369H36.3678C38.5862 128.168 63.5489 152 94.0216 152C124.495 152 149.465 128.176 151.675 97.8369H158.686C160.178 100.435 162.996 102.354 166.217 102.354C169.438 102.354 172.256 100.611 173.749 97.9648C174.475 96.6856 174.885 95.2148 174.885 93.6319C174.885 92.049 174.451 90.5222 173.701 89.2188L173.709 89.2107ZM111.145 125.554C107.971 131.518 101.758 135.459 94.5981 135.459C87.4374 135.459 81.2248 131.566 78.0509 125.602C77.1666 123.947 78.3667 122.092 80.2219 122.092H108.982C110.837 122.092 112.029 123.891 111.153 125.554H111.145ZM140.528 94.1277C140.528 103.825 132.76 111.691 123.184 111.691H65.4432C55.8675 111.691 48.0991 103.825 48.0991 94.1277V93.7199C48.0991 84.0223 55.8675 76.1557 65.4432 76.1557H123.184C132.76 76.1557 140.528 84.0223 140.528 93.7199V94.1277Z" fill="#AF0C37"/>
                <path d="M76.5809 105.311C82.9686 105.311 88.1466 100.068 88.1466 93.5996C88.1466 87.1312 82.9686 81.8875 76.5809 81.8875C70.1936 81.8875 65.0156 87.1312 65.0156 93.5996C65.0156 100.068 70.1936 105.311 76.5809 105.311Z" fill="#AF0C37"/>
                <path d="M111.437 105.311C117.824 105.311 123.002 100.068 123.002 93.5996C123.002 87.1312 117.824 81.8875 111.437 81.8875C105.049 81.8875 99.8712 87.1312 99.8712 93.5996C99.8712 100.068 105.049 105.311 111.437 105.311Z" fill="#AF0C37"/>
                </svg>
            </div>
            <div style="text-align: center; margin-bottom: 5px;">
                <h2 style="color: #AF0C37; margin: 0; font-size: 1.8em;">NinaDash</h2>
                <p style="color: #666; font-size: 0.85em; margin: 2px 0 0 0; font-style: italic;">
                    Meu Dashboard
                </p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Usuário logado
            user_nome = st.session_state.get("user_nome", "Usuário")
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #AF0C37 0%, #8F0A2E 100%); 
                        padding: 10px; border-radius: 8px; margin: 10px 0; text-align: center;">
                <p style="margin: 0; color: white; font-size: 13px;">👤 {user_nome}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Botão voltar (grande e em destaque)
            if st.button("⬅️ Voltar ao Dashboard", type="primary", use_container_width=True, key="btn_voltar_meu_dashboard"):
                st.session_state.modo_consulta_personalizada = False
                st.query_params.clear()
                st.rerun()
            
            st.markdown("---")
            
            # Rodapé minimalista
            st.markdown("""
            <div style="text-align: center; padding: 10px 0; color: #999; font-size: 0.75em;">
                📌 N9 • Qualidade e Decisão
            </div>
            """, unsafe_allow_html=True)
        
        # CARREGA DADOS DE TODOS OS PROJETOS
        with st.spinner("🔄 Carregando dados de todos os projetos..."):
            todos_dfs = []
            
            for proj in ["SD", "QA", "PB"]:
                try:
                    jql_proj = f'project = {proj} ORDER BY created DESC'
                    issues_proj, _ = buscar_dados_jira_cached(proj, jql_proj)
                    if issues_proj:
                        df_proj = processar_issues(issues_proj)
                        df_proj['projeto'] = proj
                        todos_dfs.append(df_proj)
                except:
                    pass
            
            if todos_dfs:
                df_todos = pd.concat(todos_dfs, ignore_index=True)
            else:
                st.error("❌ Não foi possível carregar dados")
                st.stop()
        
        # RENDERIZA A TELA MEU DASHBOARD
        tela_consulta_personalizada(df_todos)
        return  # Sai da função main() - não renderiza mais nada
    
    # ===============================================================
    # MODO NORMAL - SIDEBAR COMPLETA COM FILTROS
    # ===============================================================
    
    # Se veio via URL, ativa a busca automaticamente
    if card_compartilhado and not st.session_state.busca_ativa:
        st.session_state.busca_ativa = True
        st.session_state.card_buscado = card_compartilhado
        st.session_state.projeto_buscado = projeto_param if projeto_param else "SD"
    
    # Sidebar reorganizada
    with st.sidebar:
        # ===== HEADER: Logo centralizada + Nome + Descrição =====
        st.markdown('''
        <div style="text-align: center; padding: 10px 0 5px 0;">
            <svg width="70" height="70" viewBox="0 0 187 187" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M173.709 89.2107C172.209 86.6048 169.414 84.838 166.225 84.838C163.036 84.838 160.241 86.5649 158.741 89.1627H151.683C149.465 58.8237 124.495 35 94.0216 35C63.5489 35 38.5862 58.8237 36.3678 89.1627H29.1759C27.6759 86.5649 24.8734 84.798 21.6682 84.798C18.463 84.798 15.6605 86.5806 14.1605 89.2031C13.4184 90.4899 13 92.001 13 93.6C13 95.1987 13.4184 96.7017 14.1605 97.997C15.6605 100.619 18.463 102.306 21.6682 102.306C24.8734 102.306 27.6838 100.435 29.1759 97.8369H36.3678C38.5862 128.168 63.5489 152 94.0216 152C124.495 152 149.465 128.176 151.675 97.8369H158.686C160.178 100.435 162.996 102.354 166.217 102.354C169.438 102.354 172.256 100.611 173.749 97.9648C174.475 96.6856 174.885 95.2148 174.885 93.6319C174.885 92.049 174.451 90.5222 173.701 89.2188L173.709 89.2107ZM111.145 125.554C107.971 131.518 101.758 135.459 94.5981 135.459C87.4374 135.459 81.2248 131.566 78.0509 125.602C77.1666 123.947 78.3667 122.092 80.2219 122.092H108.982C110.837 122.092 112.029 123.891 111.153 125.554H111.145ZM140.528 94.1277C140.528 103.825 132.76 111.691 123.184 111.691H65.4432C55.8675 111.691 48.0991 103.825 48.0991 94.1277V93.7199C48.0991 84.0223 55.8675 76.1557 65.4432 76.1557H123.184C132.76 76.1557 140.528 84.0223 140.528 93.7199V94.1277Z" fill="#AF0C37"/>
            <path d="M76.5809 105.311C82.9686 105.311 88.1466 100.068 88.1466 93.5996C88.1466 87.1312 82.9686 81.8875 76.5809 81.8875C70.1936 81.8875 65.0156 87.1312 65.0156 93.5996C65.0156 100.068 70.1936 105.311 76.5809 105.311Z" fill="#AF0C37"/>
            <path d="M111.437 105.311C117.824 105.311 123.002 100.068 123.002 93.5996C123.002 87.1312 117.824 81.8875 111.437 81.8875C105.049 81.8875 99.8712 87.1312 99.8712 93.5996C99.8712 100.068 105.049 105.311 111.437 105.311Z" fill="#AF0C37"/>
            </svg>
        </div>
        <div style="text-align: center; margin-bottom: 5px;">
            <h2 style="color: #AF0C37; margin: 0; font-size: 1.8em;">NinaDash</h2>
            <p style="color: #666; font-size: 0.85em; margin: 2px 0 0 0; font-style: italic;">
                Transformando dados em decisões
            </p>
        </div>
        ''', unsafe_allow_html=True)
        
        # ===== USUÁRIO LOGADO =====
        user_nome = st.session_state.get("user_nome", "Usuário")
        user_email = st.session_state.get("user_email", "")
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #AF0C37 0%, #8F0A2E 100%); 
                    padding: 12px; border-radius: 8px; margin: 10px 0; text-align: center;">
            <p style="margin: 0; color: white; font-size: 14px; font-weight: 500;">👤 {user_nome}</p>
            <p style="margin: 4px 0 0 0; color: #fecdd3; font-size: 11px;">{user_email}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botão de Logout
        if st.button("🚪 Sair", use_container_width=True, key="btn_logout"):
            fazer_logout()
            st.rerun()
        
        if not verificar_credenciais():
            st.error("⚠️ Credenciais não configuradas!")
            st.markdown("""
            Configure em `.streamlit/secrets.toml`:
            ```toml
            [jira]
            email = "seu-email"
            token = "seu-token"
            ```
            """)
            st.stop()
        
        st.markdown("---")
        
        # ===== SEÇÃO 1: BUSCA DE CARD =====
        st.markdown("##### 🔍 Busca Rápida de Card")
        
        # Projeto para busca
        projetos_lista = ["SD", "QA", "PB", "VALPROD"]
        projeto_busca_index = 0
        if st.session_state.busca_ativa and st.session_state.projeto_buscado in projetos_lista:
            projeto_busca_index = projetos_lista.index(st.session_state.projeto_buscado)
        
        # Extrai número inicial se estiver buscando
        numero_inicial = ""
        if st.session_state.busca_ativa and st.session_state.card_buscado:
            numero_inicial = st.session_state.card_buscado.upper()
            for prefix in ["SD-", "QA-", "PB-", "VALPROD-"]:
                if numero_inicial.startswith(prefix):
                    numero_inicial = numero_inicial[len(prefix):]
                    break
        
        # Formulário permite Enter para buscar
        with st.form(key="form_busca_card", clear_on_submit=False):
            col_proj, col_num = st.columns([1.5, 1.5])
            with col_proj:
                projeto_busca = st.selectbox(
                    "Projeto",
                    projetos_lista,
                    index=projeto_busca_index,
                    label_visibility="collapsed",
                    help="SD, QA, PB ou VALPROD"
                )
            
            with col_num:
                numero_card_input = st.text_input(
                    "Número",
                    value=numero_inicial,
                    placeholder="1234",
                    label_visibility="collapsed",
                    max_chars=10
                )
            
            # Botão de buscar (submete com Enter também)
            buscar_clicado = st.form_submit_button("🔍 Buscar", use_container_width=True)
            
            if buscar_clicado:
                if numero_card_input:
                    st.session_state.busca_ativa = True
                    st.session_state.card_buscado = f"{projeto_busca}-{numero_card_input}"
                    st.session_state.projeto_buscado = projeto_busca
                    st.rerun()
                else:
                    st.warning("Digite o número do card")
        
        # Mostra indicador de pesquisa ativa
        if st.session_state.busca_ativa and st.session_state.card_buscado:
            st.markdown(f"""
            <div style="background: #fef3c7; border: 1px solid #f59e0b; border-radius: 6px; 
                        padding: 8px; margin: 8px 0; text-align: center;">
                <p style="margin: 0; color: #92400e; font-size: 0.85em;">
                    📍 <b>Visualizando:</b> {st.session_state.card_buscado.upper()}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Botão para voltar ao dashboard
            if st.button("⬅️ Voltar ao Dashboard", type="primary", use_container_width=True, key="btn_voltar"):
                st.session_state.busca_ativa = False
                st.session_state.card_buscado = ""
                st.session_state.projeto_buscado = "SD"
                st.query_params.clear()
                st.rerun()
        
        st.markdown("---")
        
        # ===== SEÇÃO 2: FILTROS (só mostra quando NÃO está pesquisando) =====
        if not st.session_state.busca_ativa:
            st.markdown("##### ⚙️ Filtros do Dashboard")
            
            projeto = st.selectbox("📁 Projeto", projetos_lista, index=0, key="projeto_dash")
            
            # Índice padrão do filtro baseado no projeto E na aba
            # PB, VALPROD e aba Suporte usam "Todo o período" (index=0)
            # SD/QA usam "Sprint Ativa" (index=1)
            aba_suporte = st.query_params.get("aba", None) == "suporte"
            indice_filtro_padrao = 0 if projeto in ["PB", "VALPROD"] or aba_suporte else 1
            
            filtro_sprint = st.selectbox(
                "🗓️ Período",
                ["Todo o período", "Sprint Ativa", "Últimos 30 dias", "Últimos 90 dias"],
                index=indice_filtro_padrao
            )
            
            # Nota: Filtro de Produto será adicionado após carregar os dados
            # Ferramentas Avançadas também será adicionado após Produto
            
        else:
            # Quando pesquisando, usa o projeto da busca
            projeto = st.session_state.projeto_buscado
            filtro_sprint = "Sprint Ativa"  # Não usado na busca específica
    
    # ===== MODO BUSCA DE CARD ESPECÍFICO =====
    if st.session_state.busca_ativa and st.session_state.card_buscado:
        busca_card = st.session_state.card_buscado
        projeto_busca = st.session_state.projeto_buscado
        
        # Atualiza a URL com os parâmetros de compartilhamento
        st.query_params["card"] = busca_card
        st.query_params["projeto"] = projeto_busca
        
        # Busca o card específico (sem filtros de período)
        with st.spinner(f"🔍 Buscando {busca_card}..."):
            issue, links, comentarios, historico_transicoes = buscar_card_especifico(busca_card)
        
        if issue:
            # Processa o card encontrado
            card_data = processar_issue_unica(issue)
            exibir_card_detalhado_v2(card_data, links, comentarios, historico_transicoes, projeto_busca)
        else:
            st.warning(f"⚠️ Card **{busca_card}** não encontrado.")
            st.info("💡 Verifique se o ID está correto. O card será buscado em todo o histórico do projeto.")
    
    # ===== MODO DASHBOARD NORMAL =====
    else:
        # JQL
        if filtro_sprint == "Todo o período":
            jql = f'project = {projeto} ORDER BY created DESC'
        elif filtro_sprint == "Sprint Ativa":
            jql = f'project = {projeto} AND sprint in openSprints() ORDER BY created DESC'
        elif filtro_sprint == "Últimos 30 dias":
            jql = f'project = {projeto} AND created >= -30d ORDER BY created DESC'
        else:
            jql = f'project = {projeto} AND created >= -90d ORDER BY created DESC'
        
        # AUTO-LOAD
        with st.spinner("🔄 Carregando dados do Jira..."):
            issues, ultima_atualizacao = buscar_dados_jira_cached(projeto, jql)
        
        if issues is None:
            st.error("❌ Não foi possível carregar dados do Jira")
            st.stop()
        
        if len(issues) == 0:
            st.warning("⚠️ Nenhum card encontrado para os filtros selecionados")
            st.stop()
        
        df = processar_issues(issues)
        
        # Adiciona coluna de projeto ao df principal
        df['projeto'] = projeto
        
        # ===== BUSCA TODOS OS PROJETOS PARA ABA SUPORTE/IMPLANTAÇÃO =====
        # Essa aba precisa de dados de todos os projetos para mostrar "onde estão meus cards"
        todos_dfs = [df]  # Começa com o df do projeto selecionado
        
        # Busca SD (se não for o projeto atual)
        if projeto != "SD":
            try:
                if filtro_sprint == "Todo o período":
                    jql_sd = 'project = SD ORDER BY created DESC'
                elif filtro_sprint == "Sprint Ativa":
                    jql_sd = 'project = SD AND sprint in openSprints() ORDER BY created DESC'
                elif filtro_sprint == "Últimos 30 dias":
                    jql_sd = 'project = SD AND created >= -30d ORDER BY created DESC'
                else:
                    jql_sd = 'project = SD AND created >= -90d ORDER BY created DESC'
                
                issues_sd, _ = buscar_dados_jira_cached("SD", jql_sd)
                if issues_sd:
                    df_sd = processar_issues(issues_sd)
                    df_sd['projeto'] = 'SD'
                    todos_dfs.append(df_sd)
            except:
                pass
        
        # Busca QA (se não for o projeto atual)
        if projeto != "QA":
            try:
                if filtro_sprint == "Todo o período":
                    jql_qa = 'project = QA ORDER BY created DESC'
                elif filtro_sprint == "Sprint Ativa":
                    jql_qa = 'project = QA AND sprint in openSprints() ORDER BY created DESC'
                elif filtro_sprint == "Últimos 30 dias":
                    jql_qa = 'project = QA AND created >= -30d ORDER BY created DESC'
                else:
                    jql_qa = 'project = QA AND created >= -90d ORDER BY created DESC'
                
                issues_qa, _ = buscar_dados_jira_cached("QA", jql_qa)
                if issues_qa:
                    df_qa = processar_issues(issues_qa)
                    df_qa['projeto'] = 'QA'
                    todos_dfs.append(df_qa)
            except:
                pass
        
        # Busca PB (sempre todo período, não tem sprint)
        if projeto != "PB":
            try:
                jql_pb = 'project = PB ORDER BY created DESC'
                issues_pb, _ = buscar_dados_jira_cached("PB", jql_pb)
                if issues_pb:
                    df_pb = processar_issues(issues_pb)
                    df_pb['projeto'] = 'PB'
                    todos_dfs.append(df_pb)
            except:
                pass
        
        # Busca VALPROD (sempre todo período)
        if projeto != "VALPROD":
            try:
                jql_valprod = 'project = VALPROD ORDER BY created DESC'
                issues_valprod, _ = buscar_dados_jira_cached("VALPROD", jql_valprod)
                if issues_valprod:
                    df_valprod = processar_issues(issues_valprod)
                    df_valprod['projeto'] = 'VALPROD'
                    todos_dfs.append(df_valprod)
            except:
                pass
        
        # Combina todos os DataFrames
        df_todos = pd.concat(todos_dfs, ignore_index=True) if len(todos_dfs) > 0 else df.copy()
        
        # Garante que df_todos tenha a coluna 'projeto'
        if 'projeto' not in df_todos.columns:
            df_todos['projeto'] = projeto
        
        # Filtro por produto (dentro da sidebar, junto aos outros filtros)
        with st.sidebar:
            # Adiciona Produto aos filtros principais
            produtos_disponiveis = ['Todos'] + sorted(df['produto'].unique().tolist())
            filtro_produto = st.selectbox("📦 Produto", produtos_disponiveis, index=0, key="filtro_produto_main")
            
            if filtro_produto != 'Todos':
                df = df[df['produto'] == filtro_produto]
            
            # ===== SEÇÃO DE FERRAMENTAS AVANÇADAS (após todos os filtros) =====
            st.markdown("---")
            st.markdown("##### 🔍 Ferramentas Avançadas")
            
            if st.button("🎨 Meu Dashboard", use_container_width=True, key="btn_meu_dashboard", 
                        help="Monte seu dashboard personalizado com widgets"):
                st.session_state.modo_consulta_personalizada = True
                st.query_params["tela"] = "meu_dashboard"
                st.rerun()
            
            # ===== RODAPÉ DA SIDEBAR (sempre no final) =====
            st.markdown("---")
            st.markdown("""
            <div style="text-align: center; padding: 5px 0;">
                <p style="color: #AF0C37; font-weight: bold; margin: 0; font-size: 0.85em;">
                    📌 N9 • Qualidade e Decisão de Software
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Changelog em expander
            with st.expander("📋 Histórico de Versões", expanded=False):
                st.markdown("""
                <div style="margin-bottom: 10px; display: flex; flex-wrap: wrap; gap: 5px;">
                    <span style="background: #ef4444; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; white-space: nowrap;">🔥 HOTFIX</span>
                    <span style="background: #22c55e; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; white-space: nowrap;">✨ MELHORIA</span>
                    <span style="background: #f97316; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; white-space: nowrap;">🐛 BUG&nbsp;FIX</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                **v8.81** *(20/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎨 **Meu Dashboard**: Tela totalmente nova para construir dashboards personalizados
                - ➕ **Adicionar Widgets**: Construtor no topo para adicionar métricas
                - ⬆️⬇️ **Reordenar**: Mova widgets para cima ou para baixo
                - 🗑️ **Remover**: Exclua widgets que não precisa mais
                - 📊 **Templates**: Visão Executiva, Foco DEV, Foco QA
                - 💾 **Persistência**: Dashboard salvo em cookie
                - 🧹 **Sidebar Limpa**: Apenas logo e botão voltar na tela do dashboard
                
                **v8.80** *(20/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                
                **v8.79** *(20/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎯 **Consulta Personalizada**: Tela separada acessível pela sidebar
                - 🔍 **Filtros Avançados**: Pessoa, papel (DEV/QA/Relator), status, período
                - 📅 **Períodos Flexíveis**: Sprint atual, últimas semanas, mês, ou datas customizadas
                - 📊 **Tipos de Consulta**: Cards de pessoa, métricas, comparativos, bugs
                - 💾 **Salvar Consultas**: Guarde suas consultas favoritas para reusar
                - ⬅️ **Botão na Sidebar**: Acesso rápido abaixo dos filtros
                
                **v8.78** *(20/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎨 **Nova Aba: Meu Dashboard**: Crie dashboards personalizados!
                - 📊 **Catálogo de Métricas**: 30+ métricas disponíveis para escolher
                - 💾 **Persistência**: Dashboards salvos na sessão
                - 🎯 **Templates Rápidos**: Visão Executiva, Foco QA, Foco Dev
                - 📈 **Tipos de Visualização**: KPIs, gráficos, tabelas, heatmaps
                - 🔧 **Gerenciamento**: Criar, visualizar e excluir dashboards
                
                **v8.77** *(17/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🏢 **Aba Clientes Reposicionada**: Agora entre Suporte e Governança
                - 💰 **Desenvolvimento Pago**: Detecta cards pagos via label
                - 📊 **KPIs de Clientes**: Cards pagos, % conclusão, SP total
                - 👀 **Visão Geral do Time**: Padrão igual às abas QA/Dev/Suporte
                - 🎨 **Cards com Tag Pago**: Indicador visual 💰 PAGO nos cards
                - 📈 **Top Clientes Dev Pago**: Ranking de clientes com mais desenvolvimento pago
                
                **v8.76** *(17/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🏢 **Nova Aba Clientes**: Análise completa de clientes em aba dedicada
                - 📊 **Dados de Todos Projetos**: Aba Clientes ignora filtro de projeto (mostra tudo)
                - 🔗 **Link Compartilhável**: Copiar link direto para cliente específico
                - 💰 **Categorização**: Indicadores de desenvolvimento pago vs manutenção
                - 📅 **Timeline**: Gráfico de evolução de cards por mês para cada cliente
                - 🐛 **Top Bugs**: Ranking de clientes com mais bugs
                - 🔐 **Login via Cookie**: Método mais robusto usando CookieManager
                
                **v8.75** *(17/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🏢 **Análise por Cliente**: Nova seção em Visão Geral para pesquisar clientes
                - 📊 **Top Clientes**: Ranking dos clientes com mais cards
                - 👥 **Responsáveis**: Ver quem mais trata cada cliente (Relator, Dev, QA)
                - 📄 **Últimos Cards**: Histórico recente por cliente
                - 🔐 **Fix Login**: Corrigido localStorage usando parent.window
                
                **v8.74** *(17/04/2026)* <span style="background: #ef4444; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🔥</span>
                - 🔐 **Login via localStorage**: Substitui cookies por localStorage (mais confiável)
                - ⚡ **Auto-login**: JavaScript detecta email salvo e faz login automático
                - 🔄 **Persiste entre Refreshes**: Atualizar página mantém o login
                
                **v8.73** *(17/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔗 **URL Limpa**: Remove params da URL ao navegar (não polui mais)
                - 🚫 **Selectbox sem Params**: QA/Dev/Suporte não alteram mais a URL
                
                **v8.72** *(17/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔗 **URL Centralizada**: Constante `NINADASH_URL` para facilitar alterações
                - 🐛 **Fix TypeError**: Corrigido erro de comparação de datas com timezone
                - 🔄 **Cookies**: Novo domínio requer login na primeira vez (normal)
                
                **v8.71** *(17/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎨 **Novo Nome**: Dashboard de Qualidade e Decisão de Software
                - 🔗 **Nova URL**: ninadash.streamlit.app (mais curta e fácil)
                - 📊 **Barra de Progresso**: Visual da sprint com % concluído
                - 📈 **KPIs Simplificados**: 5 métricas essenciais (Cards, SP, Concluído, Bugs, Dias)
                - 🔬 **Métricas Técnicas**: FPY/DDP/Lead Time/Health/Fator K em expander separado
                - 📋 **Cards por Status**: Layout 2 colunas (mais espaço para leitura)
                - 🔄 **Botão Atualizar**: Integrado com indicador de última atualização
                - 📝 **Subtítulo Atualizado**: Foco em todo o time, não só QA
                
                **v8.70** *(17/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📦 **Expanders Padronizados**: Todas as seções agora podem ser ocultadas
                - 👤 **Fix Responsável**: Prioriza campo `responsavel` corretamente (não QA)
                - 📝 **Título Completo**: Aumentado de 50 para 80 caracteres
                - ✅ **Checkbox Ver Todos**: Voltou! Remove limite de 20 cards
                - 🎨 **Fonte Padronizada**: Cards com fonte consistente e legível
                - 📊 **Gráficos com Explicação**: Captions descritivos nos gráficos
                - 🔧 **Cards Aguardando Aberto**: Agora inicia expandido por padrão
                
                **v8.69** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📋 **Botão Copiar Link Padronizado**: Mesmo estilo do QA/Dev (height=45px)
                - 📜 **Cards Aguardando Ação em Expander**: Agora pode ocultar/expandir
                - 🔄 **Scroll Interno Funcional**: Usa components.html com scrolling=True
                - 🚫 **Removido Checkbox Ver Todos**: Substituído por scroll interno
                
                **v8.68** *(16/04/2026)* <span style="background: #ef4444; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🔥</span>
                - 🔧 **Fix Redirecionamento**: Corrigido bug que redirecionava para aba Dev
                - 📌 **Isolamento de Abas**: QA/Dev/Suporte não interferem mais entre si
                - 🔗 **Query Params**: Só atualiza URL quando a própria aba está ativa
                - ✅ Checkbox "Ver todos" não muda mais a aba ativa
                
                **v8.67** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📋 **Botão Copiar Link**: Movido para linha do título (não corta mais)
                - 📝 **Título nos Cards**: Cards Aguardando Ação agora mostram título
                - 📜 **Scroll em Ver Todos**: Scroll automático em listas longas (max 400px)
                - 👤 **Representante Cliente**: Cards onde você é Rep. Cliente ou Responsável
                - 🏷️ **Badge de Papel**: Mostra se você é QA, Rep. Cliente ou Responsável
                
                **v8.66** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📋 **Reordenação Expanders**: Prioriza cards de validação
                - 🔬 "Cards Aguardando Minha Validação" agora é o primeiro
                - ✅ "Cards Concluídos" movido para cima (mais visível)
                - 💬 "Cards Aguardando Resposta" fechado por padrão
                - 📊 "Onde estão meus cards?" fechado por padrão
                - 🔘 **Fix Botão Copiar**: Ajustado padding interno
                
                **v8.65** *(16/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔗 **Fix Copiar Link Suporte**: Botão funciona igual QA/Dev
                - ✅ Feedback visual: muda cor e mostra "Copiado!"
                - 📋 Usa mesmo padrão components.html
                
                **v8.64** *(16/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 👤 **Responsável nos Cards**: Mostra quem precisa agir
                - 📏 **Fix Copiar Link**: Botão alinhado com selectbox
                - 📝 Legenda explicativa em "Cards Aguardando Ação"
                
                **v8.63** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🕐 **Tempo de Atualização**: Mostra "há X min/h/d" nos cards
                - 🔬 **Cards Aguardando Minha Validação**: Nova seção para QA
                - 📏 **Fix Copiar Link**: Alinhado com seletor de pessoa
                - 🔍 **Filtro Aguardando**: Inclui mais variações de status
                - 📊 **QA Cards em Trabalho**: Ordenado por atualização
                
                **v8.62** *(16/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔧 **Fix UI Visão Geral**: Removido card desalinhado
                - 🤖 **Filtro Bots**: Automation for Jira removido do Top 15
                - 🔗 **Popup Links**: Cards Aguardando agora têm popup
                - ☑️ **Ver Todos**: Checkbox para expandir listas de cards
                - 📏 **Fix Botão Copiar**: Aumentado height do botão
                - ✅ **Métrica Concluídos**: Adicionada no resumo por pessoa
                - 📝 **Renomeado**: "Entregues" → "Concluídos"
                - 🔍 **Emoji Fix**: Validação Produção usa 🔍 (pendente)
                
                **v8.61** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 👥 **Ver Todos**: Opção no seletor para visão geral do time
                - 📊 **Gráficos na Visão Geral**: Pizza por projeto, barras por status, tipos
                - 🏆 **Cards Entregues**: Nova seção mostrando entregas por pessoa
                - 📅 **Filtro Padrão**: "Todo o período" para aba Suporte
                - 📋 **Top 15 Pessoas**: Ranking com barras visuais
                - ⏳ **Cards Aguardando**: Visão rápida de pendências por categoria
                
                **v8.60** *(16/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔗 **Fix Copiar Link**: Aba Suporte copia para clipboard
                - 📋 Mesmo padrão das abas QA e Dev
                - ✅ Feedback visual "Copiado!" após clicar
                
                **v8.59** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🏷️ **Cards com Título Completo**: Mostra nome do card
                - 🔖 **Tipo do Card**: Badge colorido (HOTFIX/BUG/TAREFA)
                - 🎨 Layout melhorado nas listagens
                - 📋 Mais informações visíveis em cada card
                
                **v8.58** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎯 **Aba Suporte Refatorada**: Igual QA/Dev
                - 👤 Seletor de pessoa (qualquer um pode ver qualquer pessoa)
                - 🔄 Busca TODOS os projetos (SD, QA, PB, VALPROD)
                - 📊 Gráfico "Onde estão meus cards?" por projeto/status
                - 🔗 Link compartilhável: ?aba=suporte&pessoa=Nome
                
                **v8.57** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎯 Nova ABA: Suporte/Implantação (v1)
                - 🆕 Projeto VALPROD adicionado ao sistema
                - 📊 Status específicos do PB mapeados
                
                **v8.56** *(16/04/2026)* <span style="background: #ef4444; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🔥</span>
                - 📊 **Sem Limite de Cards**: Removido limite de 500 cards
                - 🔄 Busca TODOS os cards do período selecionado
                - 🚀 Histórico completo disponível
                
                **v8.55** *(16/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🎨 **Fix Hover Popup**: CSS puro (funciona em todos locais)
                - 🔴 NinaDash: hover vermelho (#AF0C37) + texto branco
                - 🔵 Jira: hover azul (#3b82f6) + texto branco
                - ⬜ **Tela Loading**: Fundo branco + texto vermelho
                
                **v8.54** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎨 **Popup UX**: Hover vermelho no "Ver no NinaDash"
                - ⏳ **Tela de Loading**: Substituiu flash de login ao abrir
                - 🔄 Loading animado com logo NINA durante verificação
                
                **v8.53** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🚀 **Popup em TODAS aparições de cards**
                - 📊 QA: Em Trabalho, Reprovados, Impedidos, Validados
                - 👨‍💻 DEV: Code Review, Críticos, Resumo Semanal
                - 📋 Listagens, Filas e Cards do desenvolvedor
                - 🔗 18 locais atualizados com navegação NinaDash/Jira
                
                **v8.52** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🆕 **Popup de Navegação**: Clique em qualquer card exibe menu
                - 📊 Opção "Ver no NinaDash" (abre em nova aba)
                - 🔗 Opção "Abrir no Jira" (abre em nova aba)
                - 🎯 Aplicado em Cards Vinculados, Listagens e Resumos
                
                **v8.51** *(16/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔧 **Fix:** Botão "Copiar Link" alinhamento corrigido
                - 📝 **Novo:** Seção Descrição adicionada nos cards SD
                
                **v8.50** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🔄 **Novo:** Cards em Trabalho no resumo QA individual
                - ❌ **Novo:** Cards Reprovados listados no resumo
                - 🚫 **Novo:** Cards Impedidos listados no resumo
                - 📝 Resumo completo copiável (ideal para daily/retro)
                - 📊 Todas as categorias: em trabalho, reprovados, impedidos, validados
                
                **v8.49** *(15/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🚫 Cards Impedidos/Reprovados em QA e DEV
                - 🐛 Fix navegação entre QA/DEV
                
                **v8.48** *(15/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📈 Gráfico "Evolução da Semana"
                - 📝 Títulos completos em toda ferramenta
                
                **v8.47** *(15/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🐛 Dados históricos usam `resolutiondate`
                
                **v8.46** *(15/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📆 Seletor de semanas (2-4 semanas atrás)
                
                **v8.45** *(15/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📅 "Resumo da Semana" QA/DEV
                
                **v8.44** *(15/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🤝 **Novo:** Seção "Interação QA x DEV" na aba QA
                - 💪 **Novo:** Seção "Esforço do Time" na aba Liderança
                - 🤝 **Novo:** "Interação QA x DEV" visão Liderança
                - 🗓️ **UX:** Filtro padrão: PB=Todo período, SD/QA=Sprint Ativa
                - 🌟 Heatmap de interações, ranking de duplas, FPY por parceria
                - 📊 Carga por DEV e QA, throughput, velocidade do time
                
                **v8.43** *(15/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 📏 **Fix:** Cards de métricas agora com altura uniforme
                - 📏 **Fix:** Legenda de tags não quebra mais linha
                
                **v8.42** *(15/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎨 **UX:** Barra de release com cor sólida (remov. gradiente)
                - 📏 **UX:** Cards de métricas com tamanho uniforme
                - 📏 **UX:** Espaçamento corrigido em "Cards por Status"
                - 🏷️ **UX:** Tags visuais no histórico de versões
                
                **v8.41** <span style="background: #ef4444; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🔥</span>
                - 🔧 **Fix crítico:** Sprint agora pega a ATIVA, não a mais frequente
                - 📊 Filtra por `sprint_state == 'active'` antes de exibir
                - 🚨 **Release atrasada:** Barra vermelha + alerta visual
                - ⚡ **Release hoje:** Barra amarela com destaque
                - 📅 Cálculo correto de dias até release
                
                **v8.40** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎯 **Análise de Sprint (SD)** - Planejado vs Entregue!
                - 📊 Taxa de entrega da sprint com métricas visuais
                - 🚨 Cards fora do planejamento (Hotfix, PB, Criação direta)
                - 📋 Cards originados do PB por produto
                - ⏰ **PB: Aguarda Revisão** com alerta de SLA atrasado
                - 😴 **PB: Cards parados** - slider para definir dias sem atuação
                - 🏷️ **PB: Análise por Temas** - total por tema/cliente + cruzamento
                - ⏱️ **PB: Tempo de Vida por Importância** - Alto/Médio/Baixo
                - 🔎 **Filtros de comentários**: busca por texto + filtro por autor
                - 📦 Novos campos: Temas, Importância, SLA, Issue Links
                
                **v8.39** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📦 **Tags específicas por projeto** - PB tem tags de Produto!
                - ✅ PB: Decisão (verde) - aprovações e definições
                - ❓ PB: Dúvida (amarelo) - perguntas e questionamentos
                - 📋 PB: Requisito (azul) - escopo e critérios de aceite
                - 🤝 PB: Alinhamento (roxo) - reuniões e conversas
                - 🎨 SD/QA mantém tags de QA (Bug, Reprovação, etc.)
                
                **v8.38** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🐛 Detecção de #bug (hashtag) - padrão do QA
                - 🔍 +50 novos padrões de bugs adicionados
                - 🌐 Detecta problemas de tradução, UX, interface
                - ⚠️ Detecta "sistema retornou", "api retornou", "devTools"
                - 📝 Detecta "ao tentar", "ao clicar", "ao criar", etc.
                
                **v8.37** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🔍 Filtros interativos para tipos de comentários
                - 🐛 Detecção de bugs ampliada (80+ padrões)
                - 🔄 Nova categoria: Retorno DEV (ciano)
                - 📊 Checkboxes para filtrar: Bug, Reprovação, Impedimento, Retorno, Outros
                - 🎨 Visual ainda mais distinto por categoria
                - 📈 Contador de comentários exibidos vs total
                
                **v8.36** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎨 Visual de comentários completamente reformulado
                - 🐛 Bug: fundo vermelho claro + borda vermelha + badge numerado
                - ❌ Reprovação: fundo laranja claro + borda laranja + badge numerado  
                - 🚫 Impedimento: fundo roxo claro + borda roxa + badge numerado
                - 📍 Contexto temporal: "Antes Reprovação #1", "Após Bug #2"
                - 📊 Legenda visual no topo dos comentários
                
                **v8.35** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🧠 Comentários inteligentes: filtra automações do GitHub
                - 🐛 Destaca comentários de bugs (borda vermelha)
                - ❌ Destaca comentários de reprovação (borda laranja)
                - 📊 Mostra contagem de bugs/reprovações no título
                - ℹ️ Informa quantos comentários de automação foram ocultados
                
                **v8.34** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📦 Refatoração da aba Produto (PB) a pedido da Ellen
                - 🚫 PB: Hotfix removido (não passa por produto)
                - 📅 Filtro: "Todo o período" agora é padrão
                - 📝 PB: Descrição, Labels, Componentes e Epic nos cards
                - 👤 PB: Mostra Responsável no card pesquisado
                
                **v8.33** <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔧 Fix: Login persistente restaurado corretamente
                - 🍪 Usa get_all() para aguardar cookies carregarem
                - ⚡ Corrigido timing assíncrono do CookieManager
                
                **v8.32** <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔧 Fix: CachedWidgetWarning no CookieManager
                - 🍪 Removido @st.cache_resource (widgets não podem ser cacheados)
                - 🛡️ Tratamento de erros em todas operações com cookies
                
                **v8.31** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🔒 Login persistente agora usa cookies (mais confiável)
                - 🍪 Biblioteca extra-streamlit-components para gerenciar cookies
                - ⏰ Cookie expira em 30 dias
                
                **v8.30** <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔧 Fix: Login persistente agora funciona corretamente
                - 🔒 Mantém sessão entre atualizações e novas abas
                
                **v8.29** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🔒 "Lembrar de mim" - login persistente no navegador
                - 🔓 Não precisa mais fazer login toda vez que atualiza
                - 🧹 Logout limpa o login salvo
                
                **v8.28** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📋 PB: Mostra "Relator" em vez de "Criado por"
                - 📋 PB: Adiciona campo "Resolução/Roteiro" em destaque
                - 🔍 Melhoria na visão de produto para itens de backlog
                
                **v8.27** <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔧 Fix: Removido tooltips customizados que quebravam layout
                - ℹ️ Mantido help nativo do Streamlit (ícone ?) nos st.metric
                
                **v8.26** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 💡 Tooltips em todas as métricas (hover para explicação)
                - ℹ️ FPY, DDP, Fator K, Lead Time, Health Score explicados
                - 📊 Captions explicativos em Throughput e Produtividade
                
                **v8.25** <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🧹 Fix: URL limpa - remove params cruzados QA/Dev
                - 🧹 Clear total ao voltar para visão geral
                
                **v8.24** <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🧹 Fix: Limpa parâmetros da URL ao voltar para visão geral
                
                **v8.23** *(14/04/2026)*
                - 🚀 Navegação direta via link compartilhado
                - ⬅️ Botão "Ver Dashboard Completo" para voltar
                
                **v8.22** *(14/04/2026)*
                - 🔗 Fix: Botão "Copiar Link" para QA/Dev (igual ao card individual)
                - ✅ URL correta do Streamlit Cloud
                
                **v8.21** *(14/04/2026)*
                - 🔗 Links compartilháveis para QA e Dev individuais
                - 📊 Novas métricas: throughput, eficiência, comparativo
                - 📈 Gráficos de tendência individual
                - 🎯 URL params: ?aba=qa&qa=Nome ou ?aba=dev&dev=Nome
                
                **v8.20** *(14/04/2026)*
                - 📦 Filtro Produto acima do rodapé
                
                **v8.19** *(13/04/2026)*
                - 📋 Changelog na sidebar
                
                **v8.18** *(13/04/2026)*
                - ✅ Botão "Copiar Link" funcionando
                
                **v8.17** *(13/04/2026)*
                - 🔧 Fix erro React #231
                
                **v8.16** *(13/04/2026)*
                - 🔧 Fix busca (colunas iguais)
                
                **v8.15** *(13/04/2026)*
                - 🔔 Toast ao copiar link
                
                **v8.14** *(13/04/2026)*
                - 🎨 KPIs em cards estilizados
                
                **v8.13** *(13/04/2026)*
                - ⌨️ Busca funciona com Enter
                
                **v8.12** *(13/04/2026)*
                - ⚠️ Indicador SP estimado
                
                **v8.11** *(12/04/2026)*
                - 🔍 Botão "Buscar" explícito
                
                **v8.10** *(12/04/2026)*
                - 🏠 Logo centralizada, UX
                
                **v8.9** *(12/04/2026)*
                - 💬 Comentários do Jira
                - 📦 Conteúdo por projeto
                
                **v8.8** *(11/04/2026)*
                - 🔗 Card linkages
                - 🔍 Busca simplificada
                
                **v8.7** *(10/04/2026)*
                - ⬅️ Botão voltar sidebar
                - 🎨 Design refinado
                
                **v8.6** *(09/04/2026)*
                - 📱 Sidebar refatorada
                - 📤 Link compartilhável
                
                **v8.5** *(08/04/2026)*
                - 🔍 Busca de card individual
                - 📊 Painel completo do card
                """, unsafe_allow_html=True)
        
        # Captura query params para navegação direta (QA/Dev/Suporte individual)
        aba_param = st.query_params.get("aba", None)
        qa_param = st.query_params.get("qa", None)
        dev_param = st.query_params.get("dev", None)
        pessoa_param = st.query_params.get("pessoa", None)
        
        # NAVEGAÇÃO DIRETA via link compartilhado
        if aba_param == "suporte" and pessoa_param:
            # Mostra diretamente a aba Suporte com a pessoa selecionada
            col_header, col_voltar = st.columns([4, 1])
            with col_header:
                st.markdown(f"### 🔗 Link Compartilhado: Suporte/Implantação")
            with col_voltar:
                if st.button("⬅️ Ver Dashboard Completo", use_container_width=True, key="btn_voltar_suporte"):
                    st.query_params.clear()
                    st.rerun()
            st.markdown("---")
            aba_suporte_implantacao(df_todos)
            return
        
        if aba_param == "qa" and qa_param:
            # Mostra diretamente a aba QA com o colaborador selecionado
            col_header, col_voltar = st.columns([4, 1])
            with col_header:
                st.markdown(f"### 🔗 Link Compartilhado: Métricas de QA")
            with col_voltar:
                if st.button("⬅️ Ver Dashboard Completo", use_container_width=True, key="btn_voltar_qa"):
                    st.query_params.clear()
                    st.rerun()
            st.markdown("---")
            aba_qa(df)
            return
        
        if aba_param == "dev" and dev_param:
            # Mostra diretamente a aba Dev com o colaborador selecionado
            col_header, col_voltar = st.columns([4, 1])
            with col_header:
                st.markdown(f"### 🔗 Link Compartilhado: Métricas de Dev")
            with col_voltar:
                if st.button("⬅️ Ver Dashboard Completo", use_container_width=True, key="btn_voltar_dev"):
                    st.query_params.clear()
                    st.rerun()
            st.markdown("---")
            aba_dev(df)
            return
        
        # Abas condicionais por projeto (fluxo normal)
        if projeto == "PB":
            # Projeto PB: Aba de Backlog como foco principal
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📋 Backlog",
                "📊 Visão Geral",
                "📦 Produto",
                "📈 Histórico",
                "ℹ️ Sobre"
            ])
            
            with tab1:
                aba_backlog(df)
            
            with tab2:
                aba_visao_geral(df, ultima_atualizacao)
            
            with tab3:
                aba_produto(df)
            
            with tab4:
                aba_historico(df)
            
            with tab5:
                aba_sobre()
        
        elif projeto == "VALPROD":
            # Projeto VALPROD: Foco em Validação em Produção + Suporte
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🎯 Suporte/Implantação",
                "📊 Visão Geral",
                "📋 Governança",
                "📈 Histórico",
                "ℹ️ Sobre"
            ])
            
            with tab1:
                aba_suporte_implantacao(df_todos)
            
            with tab2:
                aba_visao_geral(df, ultima_atualizacao)
            
            with tab3:
                aba_governanca(df)
            
            with tab4:
                aba_historico(df)
            
            with tab5:
                aba_sobre()
        
        else:
            # Projetos SD e QA: Abas completas com QA/Dev + Clientes + Suporte
            tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
                "📊 Visão Geral",
                "🔬 QA",
                "👨‍💻 Dev",
                "🎯 Suporte/Implantação",
                "🏢 Clientes",
                "📋 Governança",
                "📦 Produto",
                "📈 Histórico",
                "🎯 Liderança",
                "ℹ️ Sobre"
            ])
            
            with tab1:
                aba_visao_geral(df, ultima_atualizacao)
            
            with tab2:
                aba_qa(df)
            
            with tab3:
                aba_dev(df)
            
            with tab4:
                aba_suporte_implantacao(df_todos)
            
            with tab5:
                aba_clientes(df_todos)
            
            with tab6:
                aba_governanca(df)
            
            with tab7:
                aba_produto(df)
            
            with tab8:
                aba_historico(df)
            
            with tab9:
                aba_lideranca(df)
            
            with tab10:
                aba_sobre()


if __name__ == "__main__":
    main()
