"""
================================================================================
MÓDULO GRAFICOS - NinaDash v8.82
================================================================================
Gráficos - Funções de criação de visualizações Plotly

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


# ==============================================================================
# FUNÇÕES DO MÓDULO
# ==============================================================================

def criar_grafico_concentracao(matriz: pd.DataFrame, titulo: str, tipo: str = "dev") -> go.Figure:
    """Cria heatmap de concentração para visualização."""
    if matriz.empty:
        fig = go.Figure()
        fig.add_annotation(text="Sem dados suficientes", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    # Calcula percentuais
    matriz_pct = matriz.div(matriz.sum(axis=0), axis=1) * 100
    matriz_pct = matriz_pct.fillna(0)
    
    # Define escala de cores baseado no tipo
    colorscale = 'Blues' if tipo == "dev" else 'Purples'
    
    fig = go.Figure(data=go.Heatmap(
        z=matriz_pct.values,
        x=matriz_pct.columns.tolist(),
        y=matriz_pct.index.tolist(),
        colorscale=colorscale,
        text=matriz.values,  # Mostra valores absolutos
        texttemplate="%{text}",
        textfont={"size": 11},
        hovertemplate="<b>%{y}</b><br>%{x}: %{text} cards (%{z:.0f}%)<extra></extra>",
        colorbar=dict(title="%", ticksuffix="%")
    ))
    
    fig.update_layout(
        title=titulo,
        xaxis_title="",
        yaxis_title="",
        height=max(300, len(matriz) * 35 + 100),
        margin=dict(l=20, r=20, t=50, b=20),
    )
    
    return fig


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




