"""
================================================================================
ABA: CENTRAL DE DECISÃO - NinaDash v8.82
================================================================================
Painel consolidado com indicadores de todas as áreas para tomada de decisão.

Mostra:
- Cards de status do fluxo (Backlog → Done)
- Métricas de cada área (Dev, QA, Produto, Suporte)
- Indicadores de saúde do projeto
- Alertas e ações recomendadas
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from modulos.config import STATUS_NOMES, STATUS_CORES
from modulos.calculos import (
    calcular_metricas_governanca,
    calcular_fpy,
    calcular_ddp,
    calcular_lead_time,
    calcular_health_score,
)


def criar_card_indicador(
    titulo: str, 
    valor: int, 
    percentual: float, 
    cor: str = "#3b82f6",
    icone: str = "📊",
    tendencia: str = None,  # "up", "down", "stable"
    destaque: bool = False
) -> str:
    """
    Cria um card de indicador estilizado.
    
    Args:
        titulo: Nome do indicador
        valor: Quantidade absoluta
        percentual: Percentual do total
        cor: Cor do card (hex)
        icone: Emoji do indicador
        tendencia: Direção da tendência
        destaque: Se deve destacar o card
    
    Returns:
        HTML do card
    """
    # Ícone de tendência
    tendencia_html = ""
    if tendencia == "up":
        tendencia_html = '<span style="color: #22c55e; font-size: 12px;">↑</span>'
    elif tendencia == "down":
        tendencia_html = '<span style="color: #ef4444; font-size: 12px;">↓</span>'
    elif tendencia == "stable":
        tendencia_html = '<span style="color: #6b7280; font-size: 12px;">→</span>'
    
    # Estilo de destaque
    border_style = f"3px solid {cor}" if destaque else f"1px solid {cor}40"
    shadow = "0 4px 12px rgba(0,0,0,0.1)" if destaque else "0 2px 4px rgba(0,0,0,0.05)"
    
    return f"""
    <div class="indicador-card hover-lift" style="
        background: linear-gradient(135deg, {cor}08 0%, {cor}15 100%);
        border: {border_style};
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.4s ease-out;
        box-shadow: {shadow};
    ">
        <div style="font-size: 11px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
            {icone} {titulo}
        </div>
        <div style="font-size: 32px; font-weight: 700; color: {cor}; line-height: 1;">
            {percentual:.0f}%
        </div>
        <div style="font-size: 24px; font-weight: 600; color: #1f2937; margin-top: 4px;">
            {valor} {tendencia_html}
        </div>
    </div>
    """


def criar_mini_card_metrica(
    titulo: str,
    valor: str,
    cor: str = "#6b7280",
    subtitulo: str = ""
) -> str:
    """Cria um mini card de métrica."""
    return f"""
    <div class="mini-card-animated" style="
        background: {cor}10;
        border-left: 3px solid {cor};
        border-radius: 6px;
        padding: 10px 12px;
        margin: 4px 0;
    ">
        <div style="font-size: 10px; color: #6b7280; text-transform: uppercase;">{titulo}</div>
        <div style="font-size: 18px; font-weight: 600; color: {cor};">{valor}</div>
        {f'<div style="font-size: 10px; color: #9ca3af;">{subtitulo}</div>' if subtitulo else ''}
    </div>
    """


def calcular_metricas_fluxo(df: pd.DataFrame) -> Dict:
    """
    Calcula métricas do fluxo de desenvolvimento.
    
    Returns:
        Dict com contagem e percentual por status
    """
    total = len(df)
    if total == 0:
        return {}
    
    # Categorias principais do fluxo
    categorias = {
        'backlog': {'nome': 'Backlog', 'icone': '📋', 'cor': '#64748b'},
        'development': {'nome': 'Desenvolvimento', 'icone': '💻', 'cor': '#3b82f6'},
        'code_review': {'nome': 'Code Review', 'icone': '👀', 'cor': '#8b5cf6'},
        'waiting_qa': {'nome': 'Aguardando QA', 'icone': '⏳', 'cor': '#f59e0b'},
        'testing': {'nome': 'Em Teste', 'icone': '🧪', 'cor': '#06b6d4'},
        'done': {'nome': 'Concluído', 'icone': '✅', 'cor': '#22c55e'},
        'blocked': {'nome': 'Bloqueado', 'icone': '🚫', 'cor': '#ef4444'},
    }
    
    metricas = {}
    for cat_key, cat_info in categorias.items():
        count = len(df[df['status_cat'] == cat_key])
        pct = (count / total * 100) if total > 0 else 0
        metricas[cat_key] = {
            'nome': cat_info['nome'],
            'icone': cat_info['icone'],
            'cor': cat_info['cor'],
            'quantidade': count,
            'percentual': pct
        }
    
    return metricas


def calcular_metricas_areas(df: pd.DataFrame) -> Dict:
    """
    Calcula métricas por área (Dev, QA, Produto, Suporte).
    """
    metricas = {
        'dev': {
            'cards_ativos': len(df[df['status_cat'].isin(['development', 'code_review'])]),
            'bugs_criados': int(df['bugs'].sum()),
            'sp_em_progresso': int(df[df['status_cat'].isin(['development', 'code_review', 'testing'])]['sp'].sum()),
        },
        'qa': {
            'cards_fila': len(df[df['status_cat'] == 'waiting_qa']),
            'cards_teste': len(df[df['status_cat'] == 'testing']),
            'bugs_encontrados': int(df['bugs'].sum()),
        },
        'geral': {
            'total_cards': len(df),
            'sp_total': int(df['sp'].sum()),
            'concluidos': len(df[df['status_cat'] == 'done']),
            'bloqueados': len(df[df['status_cat'] == 'blocked']),
        }
    }
    return metricas


def criar_secao_alertas(df: pd.DataFrame) -> List[Dict]:
    """
    Gera lista de alertas baseados nas métricas.
    """
    alertas = []
    total = len(df)
    
    # Alerta: Muitos cards bloqueados
    bloqueados = len(df[df['status_cat'] == 'blocked'])
    if bloqueados > 0:
        alertas.append({
            'tipo': 'critical' if bloqueados > 3 else 'warning',
            'titulo': f'🚫 {bloqueados} card(s) bloqueado(s)',
            'descricao': 'Requer atenção imediata para destravar o fluxo',
            'acao': 'Ver bloqueados'
        })
    
    # Alerta: Fila de QA grande
    fila_qa = len(df[df['status_cat'] == 'waiting_qa'])
    if fila_qa > 5:
        alertas.append({
            'tipo': 'warning',
            'titulo': f'⏳ {fila_qa} cards aguardando QA',
            'descricao': 'Fila de validação acima do ideal',
            'acao': 'Priorizar QA'
        })
    
    # Alerta: Code Review acumulado
    em_review = len(df[df['status_cat'] == 'code_review'])
    if em_review > 5:
        alertas.append({
            'tipo': 'warning',
            'titulo': f'👀 {em_review} cards em Code Review',
            'descricao': 'Acúmulo de revisões pendentes',
            'acao': 'Acelerar reviews'
        })
    
    # Alerta: SP sem preenchimento
    gov = calcular_metricas_governanca(df)
    if gov['sp']['pct'] < 50:
        alertas.append({
            'tipo': 'info',
            'titulo': f"📊 {gov['sp']['pct']:.0f}% cards com SP",
            'descricao': 'Story Points incompletos prejudicam métricas',
            'acao': 'Preencher SP'
        })
    
    # Alerta positivo: Boa taxa de conclusão
    concluidos = len(df[df['status_cat'] == 'done'])
    pct_concluido = (concluidos / total * 100) if total > 0 else 0
    if pct_concluido >= 70:
        alertas.append({
            'tipo': 'success',
            'titulo': f'✅ {pct_concluido:.0f}% da sprint concluída',
            'descricao': 'Excelente progresso!',
            'acao': None
        })
    
    return alertas


def aba_central_decisao(df: pd.DataFrame, ultima_atualizacao: datetime):
    """
    Aba Central de Decisão - Painel consolidado de indicadores.
    """
    
    # Header
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: white;
        padding: 20px 24px;
        border-radius: 12px;
        margin-bottom: 24px;
        animation: fadeIn 0.3s ease-out;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="margin: 0; font-size: 24px; font-weight: 700;">🎯 Central de Decisão</h2>
                <p style="margin: 4px 0 0 0; opacity: 0.8; font-size: 14px;">
                    Visão consolidada de todos os indicadores
                </p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 12px; opacity: 0.7;">Última atualização</div>
                <div style="font-size: 14px; font-weight: 600;">
                    {ultima_atualizacao.strftime('%H:%M')} • {ultima_atualizacao.strftime('%d/%m')}
                </div>
            </div>
        </div>
    </div>
    """.format(ultima_atualizacao=ultima_atualizacao), unsafe_allow_html=True)
    
    # Calcula métricas
    metricas_fluxo = calcular_metricas_fluxo(df)
    metricas_areas = calcular_metricas_areas(df)
    alertas = criar_secao_alertas(df)
    
    # ===== SEÇÃO 1: FLUXO DE DESENVOLVIMENTO =====
    st.markdown("""
    <div style="margin-bottom: 12px;">
        <span style="font-size: 16px; font-weight: 600; color: #1f2937;">📊 Status do Fluxo</span>
        <span style="font-size: 12px; color: #6b7280; margin-left: 8px;">Pipeline de desenvolvimento</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Cards do fluxo principal (6 colunas)
    fluxo_ordem = ['backlog', 'development', 'code_review', 'waiting_qa', 'testing', 'done']
    cols = st.columns(6)
    
    for i, status_key in enumerate(fluxo_ordem):
        if status_key in metricas_fluxo:
            m = metricas_fluxo[status_key]
            with cols[i]:
                # Destaque para done e blocked
                destaque = status_key in ['done', 'blocked']
                st.markdown(criar_card_indicador(
                    titulo=m['nome'],
                    valor=m['quantidade'],
                    percentual=m['percentual'],
                    cor=m['cor'],
                    icone=m['icone'],
                    destaque=destaque
                ), unsafe_allow_html=True)
    
    # Card de bloqueados (se houver)
    if metricas_fluxo.get('blocked', {}).get('quantidade', 0) > 0:
        m = metricas_fluxo['blocked']
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
            border: 2px solid #ef4444;
            border-radius: 8px;
            padding: 12px 16px;
            margin: 12px 0;
            display: flex;
            align-items: center;
            gap: 12px;
            animation: fadeInUp 0.4s ease-out;
        ">
            <span style="font-size: 24px;">🚫</span>
            <div>
                <div style="font-weight: 600; color: #dc2626;">{m['quantidade']} Card(s) Bloqueado(s)</div>
                <div style="font-size: 12px; color: #991b1b;">Requer atenção imediata</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    
    # ===== SEÇÃO 2: MÉTRICAS POR ÁREA =====
    col_dev, col_qa, col_geral = st.columns(3)
    
    with col_dev:
        st.markdown("""
        <div style="
            background: #f0f9ff;
            border: 1px solid #bae6fd;
            border-radius: 10px;
            padding: 16px;
            animation: fadeInUp 0.4s ease-out;
        ">
            <div style="font-size: 14px; font-weight: 600; color: #0369a1; margin-bottom: 12px;">
                💻 Desenvolvimento
            </div>
        """, unsafe_allow_html=True)
        
        ma = metricas_areas['dev']
        st.markdown(criar_mini_card_metrica("Cards Ativos", str(ma['cards_ativos']), "#3b82f6"), unsafe_allow_html=True)
        st.markdown(criar_mini_card_metrica("SP em Progresso", str(ma['sp_em_progresso']), "#8b5cf6"), unsafe_allow_html=True)
        st.markdown(criar_mini_card_metrica("Bugs Reportados", str(ma['bugs_criados']), "#ef4444"), unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_qa:
        st.markdown("""
        <div style="
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-radius: 10px;
            padding: 16px;
            animation: fadeInUp 0.45s ease-out;
        ">
            <div style="font-size: 14px; font-weight: 600; color: #15803d; margin-bottom: 12px;">
                🧪 Qualidade
            </div>
        """, unsafe_allow_html=True)
        
        mq = metricas_areas['qa']
        st.markdown(criar_mini_card_metrica("Fila QA", str(mq['cards_fila']), "#f59e0b"), unsafe_allow_html=True)
        st.markdown(criar_mini_card_metrica("Em Teste", str(mq['cards_teste']), "#06b6d4"), unsafe_allow_html=True)
        st.markdown(criar_mini_card_metrica("Bugs Encontrados", str(mq['bugs_encontrados']), "#ef4444"), unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_geral:
        st.markdown("""
        <div style="
            background: #faf5ff;
            border: 1px solid #e9d5ff;
            border-radius: 10px;
            padding: 16px;
            animation: fadeInUp 0.5s ease-out;
        ">
            <div style="font-size: 14px; font-weight: 600; color: #7c3aed; margin-bottom: 12px;">
                📈 Visão Geral
            </div>
        """, unsafe_allow_html=True)
        
        mg = metricas_areas['geral']
        pct_done = (mg['concluidos'] / mg['total_cards'] * 100) if mg['total_cards'] > 0 else 0
        st.markdown(criar_mini_card_metrica("Total Cards", str(mg['total_cards']), "#6b7280"), unsafe_allow_html=True)
        st.markdown(criar_mini_card_metrica("Story Points", str(mg['sp_total']), "#8b5cf6"), unsafe_allow_html=True)
        st.markdown(criar_mini_card_metrica("Taxa Conclusão", f"{pct_done:.0f}%", "#22c55e"), unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    
    # ===== SEÇÃO 3: ALERTAS E RECOMENDAÇÕES =====
    if alertas:
        st.markdown("""
        <div style="margin-bottom: 12px;">
            <span style="font-size: 16px; font-weight: 600; color: #1f2937;">⚡ Alertas e Recomendações</span>
        </div>
        """, unsafe_allow_html=True)
        
        for alerta in alertas:
            tipo = alerta['tipo']
            cores = {
                'critical': ('#fef2f2', '#ef4444', '#dc2626'),
                'warning': ('#fffbeb', '#f59e0b', '#d97706'),
                'info': ('#eff6ff', '#3b82f6', '#2563eb'),
                'success': ('#f0fdf4', '#22c55e', '#16a34a'),
            }
            bg, border, text = cores.get(tipo, cores['info'])
            
            st.markdown(f"""
            <div class="alert-{tipo}" style="
                background: {bg};
                border-left: 4px solid {border};
                border-radius: 8px;
                padding: 12px 16px;
                margin: 8px 0;
                animation: fadeInUp 0.4s ease-out;
            ">
                <div style="font-weight: 600; color: {text}; margin-bottom: 4px;">
                    {alerta['titulo']}
                </div>
                <div style="font-size: 13px; color: #4b5563;">
                    {alerta['descricao']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # ===== SEÇÃO 4: MÉTRICAS DE QUALIDADE =====
    with st.expander("🔬 Métricas Técnicas de Qualidade", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        # FPY
        fpy = calcular_fpy(df)
        with col1:
            cor = "#22c55e" if fpy >= 80 else "#f59e0b" if fpy >= 60 else "#ef4444"
            st.markdown(f"""
            <div style="text-align: center; padding: 16px; background: {cor}10; border-radius: 8px; border: 1px solid {cor}30;">
                <div style="font-size: 28px; font-weight: 700; color: {cor};">{fpy:.0f}%</div>
                <div style="font-size: 12px; color: #6b7280;">FPY (First Pass Yield)</div>
            </div>
            """, unsafe_allow_html=True)
        
        # DDP
        ddp = calcular_ddp(df)
        with col2:
            cor = "#22c55e" if ddp <= 10 else "#f59e0b" if ddp <= 20 else "#ef4444"
            st.markdown(f"""
            <div style="text-align: center; padding: 16px; background: {cor}10; border-radius: 8px; border: 1px solid {cor}30;">
                <div style="font-size: 28px; font-weight: 700; color: {cor};">{ddp:.1f}</div>
                <div style="font-size: 12px; color: #6b7280;">DDP (Densidade Defeitos)</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Lead Time
        lead_time = calcular_lead_time(df)
        with col3:
            cor = "#22c55e" if lead_time <= 5 else "#f59e0b" if lead_time <= 10 else "#ef4444"
            st.markdown(f"""
            <div style="text-align: center; padding: 16px; background: {cor}10; border-radius: 8px; border: 1px solid {cor}30;">
                <div style="font-size: 28px; font-weight: 700; color: {cor};">{lead_time:.1f}d</div>
                <div style="font-size: 12px; color: #6b7280;">Lead Time Médio</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Health Score
        health = calcular_health_score(df)
        with col4:
            cor = "#22c55e" if health >= 70 else "#f59e0b" if health >= 50 else "#ef4444"
            st.markdown(f"""
            <div style="text-align: center; padding: 16px; background: {cor}10; border-radius: 8px; border: 1px solid {cor}30;">
                <div style="font-size: 28px; font-weight: 700; color: {cor};">{health:.0f}</div>
                <div style="font-size: 12px; color: #6b7280;">Health Score</div>
            </div>
            """, unsafe_allow_html=True)
