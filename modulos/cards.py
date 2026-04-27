"""
================================================================================
MÓDULO CARDS - NinaDash v8.82
================================================================================
Card Details - Visualização detalhada de tickets

Dependências:
- streamlit, pandas, plotly, datetime
- modulos.config, modulos.utils, modulos.calculos, modulos.jira_api, modulos.processamento

Author: GitHub Copilot
Version: 1.0 (Phase 7)
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import html
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

from modulos.config import (
    JIRA_BASE_URL, CUSTOM_FIELDS, STATUS_FLOW, STATUS_NOMES, STATUS_CORES,
    TOOLTIPS, REGRAS, PB_FUNIL_ETAPAS, TEMAS_NAO_CLIENTES, NINADASH_URL
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
    calcular_health_score, calcular_metricas_dev, calcular_metricas_backlog,
    classificar_maturidade
)
from modulos.jira_api import (
    buscar_dados_jira_cached, buscar_card_especifico,
    gerar_icone_tabler, gerar_badge_status, obter_icone_status,
    extrair_historico_transicoes, extrair_texto_adf
)

from modulos.jira_api import extrair_historico_transicoes, extrair_texto_adf, gerar_icone_tabler
from modulos.utils import link_jira, traduzir_link
from modulos.helpers import gerar_badge_ambiente, obter_info_ambiente


# ==============================================================================
# FUNÇÕES DO MÓDULO
# ==============================================================================

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
    
    # Badge de ambiente (se preenchido)
    ambiente = card.get('ambiente', '')
    ambiente_badge_html = ""
    if ambiente:
        info_amb = obter_info_ambiente(ambiente)
        ambiente_badge_html = f'<span style="background: rgba(255,255,255,0.95); color: {info_amb["cor"]}; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; margin-left: 12px; vertical-align: middle;">{info_amb["emoji"]} {info_amb["nome"]}</span>'
        if info_amb['vai_subir_proxima_release']:
            ambiente_badge_html += f' <span style="background: rgba(255,255,255,0.2); color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; vertical-align: middle;">🚀 Sobe na próxima release</span>'
    
    # Escapa caracteres especiais no título para evitar quebra do HTML
    titulo_seguro = html.escape(card['titulo'][:120]) + ('...' if len(card['titulo']) > 120 else '')
    
    st.markdown(f'''<div style="background: {header_bg}; color: white; padding: 20px; border-radius: 12px; margin-bottom: 15px;"><h2 style="margin: 0; color: white; font-size: 1.5em;">{header_icon} {card["ticket_id"]} {ambiente_badge_html}</h2><p style="margin: 8px 0 0 0; opacity: 0.9; font-size: 0.95em;">{titulo_seguro}</p></div>''', unsafe_allow_html=True)
    
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




def exibir_comentarios(comentarios: List[Dict], projeto: str = "SD"):
    """Exibe seção de comentários do card (filtrados e classificados) com filtros interativos."""
    
    # Usa classificação diferente para PB (Product Backlog)
    if projeto == "PB":
        exibir_comentarios_pb(comentarios)
        return
    
    # Para SD e QA: classificação com tags de QA
    comentarios_filtrados = filtrar_e_classificar_comentarios(comentarios)
    
    # Garante que comentarios_filtrados não seja None
    if comentarios_filtrados is None:
        comentarios_filtrados = []
    
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




def exibir_comentarios_pb(comentarios: List[Dict]):
    """Exibe comentários para cards de Product Backlog (PB) com tags de produto."""
    
    comentarios_filtrados = filtrar_comentarios_pb(comentarios)
    
    # Garante que comentarios_filtrados não seja None
    if comentarios_filtrados is None:
        comentarios_filtrados = []
    
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



