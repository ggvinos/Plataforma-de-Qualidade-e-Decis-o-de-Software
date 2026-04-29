"""
================================================================================
MÓDULO CARDS V2 - NinaDash v8.82
================================================================================
Refatoração completa da visualização de cards

Author: NinaDash Team
Version: 2.2 (Correções de renderização)
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from modulos.config import NINADASH_URL
from modulos.utils import link_jira, card_link_com_popup
from modulos.calculos import calcular_fator_k, classificar_maturidade
from modulos.jira_api import obter_icone_status, extrair_texto_adf
from modulos.helpers import obter_info_ambiente
from modulos.cards import exibir_comentarios, exibir_timeline_transicoes


# ==============================================================================
# FUNÇÃO PRINCIPAL
# ==============================================================================

def exibir_card_detalhado_v2(card: Dict, links: List[Dict], comentarios: List[Dict], 
                             historico: List[Dict] = None, projeto: str = "SD") -> bool:
    """Exibe painel detalhado de um card - versão compacta e harmoniosa."""
    if not card:
        return False
    
    if historico is None:
        historico = []
    
    # =========================================================================
    # 1. HEADER - IDENTIDADE DO CARD
    # =========================================================================
    _renderizar_header(card, projeto)
    
    # =========================================================================
    # 2. PAINEL DE MÉTRICAS COMPACTO
    # =========================================================================
    _renderizar_metricas_compactas(card, historico, projeto)
    
    # =========================================================================
    # 3. TIMELINE (completa)
    # =========================================================================
    if historico:
        exibir_timeline_transicoes(historico, "📜 Timeline Completa do Card")
    
    # =========================================================================
    # 4. INFORMAÇÕES BÁSICAS + DESCRIÇÃO
    # =========================================================================
    _renderizar_info_descricao(card, projeto)
    
    # =========================================================================
    # 5. CARDS VINCULADOS
    # =========================================================================
    _renderizar_cards_vinculados(links)
    
    # =========================================================================
    # 6. COMENTÁRIOS
    # =========================================================================
    exibir_comentarios(comentarios, projeto=projeto)
    
    return True


# ==============================================================================
# HEADER DO CARD
# ==============================================================================

def _renderizar_header(card: Dict, projeto: str):
    """Renderiza header com identidade do card."""
    
    cores_projeto = {"SD": "#AF0C37", "QA": "#6366f1", "PB": "#059669"}
    cor = cores_projeto.get(projeto, "#1e293b")
    
    # Badge de ambiente
    ambiente = card.get('ambiente', '')
    ambiente_badge = ""
    if ambiente:
        info_amb = obter_info_ambiente(ambiente)
        ambiente_badge = f'''<span style="background: rgba(255,255,255,0.95); color: {info_amb['cor']}; padding: 6px 12px; border-radius: 8px; font-size: 0.65em; font-weight: 600; margin-left: 12px;">{info_amb['emoji']} {info_amb['nome']}</span>'''
    
    # Título seguro
    titulo = card['titulo'][:100] + ('...' if len(card['titulo']) > 100 else '')
    titulo = titulo.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    
    # Header HTML
    header_html = f'''<div style="background: linear-gradient(135deg, {cor} 0%, {cor}dd 100%); color: white; padding: 24px; border-radius: 16px; margin-bottom: 20px;"><div style="font-size: 1.8em; font-weight: 700; margin-bottom: 8px; display: flex; align-items: center; gap: 12px;">{card['ticket_id']}{ambiente_badge}</div><div style="font-size: 1em; opacity: 0.9; line-height: 1.4;">{titulo}</div><div style="margin-top: 12px; font-size: 0.85em; opacity: 0.8;">📍 {card['sprint']} • 📦 {card['produto']}</div></div>'''
    st.markdown(header_html, unsafe_allow_html=True)
    
    # Botões de ação
    share_url = f"{NINADASH_URL}?card={card['ticket_id']}&projeto={projeto}"
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        st.link_button("🔗 Abrir no Jira", card['link'], use_container_width=True)
    with col2:
        # Botão copiar com JavaScript funcional
        copy_btn_html = f"""
        <style>
            html, body {{ margin: 0 !important; padding: 0 !important; overflow: hidden; }}
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
        """
        components.html(copy_btn_html, height=36)


# ==============================================================================
# PAINEL DE MÉTRICAS COMPACTO (unifica diagnóstico + alertas + KPIs)
# ==============================================================================

def _renderizar_metricas_compactas(card: Dict, historico: List[Dict], projeto: str):
    """
    Renderiza painel único e compacto com todas as métricas.
    Evita duplicação e mantém visual harmonioso.
    """
    from modulos.calculos import calcular_fator_k, classificar_maturidade
    
    status_lower = card['status'].lower()
    is_done = any(x in status_lower for x in ['done', 'concluído', 'concluido', 'finalizado', 'closed', 'fechado'])
    
    # ========== CALCULA STATUS GERAL ==========
    if is_done:
        if projeto == "SD" and card['bugs'] == 0:
            status_geral = ("saudavel", "#22c55e", "✅ Concluído", "")
        elif projeto == "SD":
            status_geral = ("saudavel", "#22c55e", "✅ Concluído", "")
        else:
            status_geral = ("saudavel", "#22c55e", "✅ Concluído", "")
    else:
        # Avalia situação baseado em pontos
        pontos = 0
        
        if projeto == "SD" and card['bugs'] > 3:
            pontos += 2
        elif projeto == "SD" and card['bugs'] > 0:
            pontos += 1
        
        if card['dias_em_status'] > 7:
            pontos += 1
        
        if card['lead_time'] > 21:
            pontos += 1
        
        if pontos >= 3:
            status_geral = ("critico", "#ef4444", "🚨 Atenção Necessária", "")
        elif pontos >= 1:
            status_geral = ("atencao", "#f59e0b", "⚠️ Monitorar", "")
        else:
            status_geral = ("saudavel", "#22c55e", "✅ Saudável", "")
    
    # ========== RENDERIZA PAINEL COMPACTO ==========
    if projeto == "SD":
        _renderizar_metricas_sd_compactas(card, status_geral, historico)
    elif projeto == "QA":
        _renderizar_metricas_qa_compactas(card, status_geral)
    elif projeto == "PB":
        _renderizar_metricas_pb_compactas(card, status_geral)


def _mini_card(icone: str, label: str, valor: str, cor: str = "#64748b") -> str:
    """Card de métrica minimalista."""
    return f'''<div style="text-align: center; padding: 8px 4px;"><div style="font-size: 1.1em;">{icone}</div><div style="font-size: 1.2em; font-weight: 700; color: {cor};">{valor}</div><div style="font-size: 0.65em; color: #94a3b8; text-transform: uppercase;">{label}</div></div>'''


def _renderizar_metricas_sd_compactas(card: Dict, status_geral: tuple, historico: List[Dict]):
    """Métricas SD em layout compacto e limpo."""
    from modulos.calculos import calcular_fator_k, classificar_maturidade
    
    status_tipo, status_cor, status_titulo, status_msg = status_geral
    
    # Cálculos
    fk = calcular_fator_k(card['sp'], card['bugs'])
    mat = classificar_maturidade(fk)
    fpy = "100%" if card['bugs'] == 0 else "0%"
    
    # Cores baseadas em valores
    cor_bugs = "#22c55e" if card['bugs'] == 0 else "#f59e0b" if card['bugs'] <= 2 else "#ef4444"
    cor_lead = "#22c55e" if card['lead_time'] <= 7 else "#f59e0b" if card['lead_time'] <= 14 else "#ef4444"
    cor_aging = "#22c55e" if card['dias_em_status'] <= 3 else "#f59e0b" if card['dias_em_status'] <= 7 else "#ef4444"
    cor_fpy = "#22c55e" if card['bugs'] == 0 else "#ef4444"
    cor_sp = "#3b82f6" if card['sp'] > 0 else "#f59e0b"
    
    # Conta retornos para dev
    retornos = 0
    if historico:
        for h in historico:
            if h.get('tipo') == 'transicao':
                de = str(h.get('de', '')).lower()
                para = str(h.get('para', '')).lower()
                if any(x in de for x in ['validação', 'qa', 'testing']):
                    if any(x in para for x in ['desenvolvimento', 'andamento', 'dev']):
                        retornos += 1
    
    # Alertas especiais
    alertas = []
    if 'block' in card['status'].lower():
        alertas.append(("🚫", "Bloqueado", "#ef4444"))
    if card['sp'] == 0:
        alertas.append(("📊", "Sem Pontos", "#f59e0b"))
    if retornos >= 2:
        alertas.append(("🔄", f"{retornos}x Retornos", "#f59e0b"))
    
    # Background
    bg_colors = {"saudavel": "#f0fdf4", "atencao": "#fffbeb", "critico": "#fef2f2"}
    bg = bg_colors.get(status_tipo, '#f8fafc')
    
    # Extrai emoji e texto do status
    status_parts = status_titulo.split(maxsplit=1)
    status_emoji = status_parts[0] if status_parts else "✅"
    status_texto = status_parts[1] if len(status_parts) > 1 else ""
    
    # Monta mini cards COM NOMES CLAROS
    m1 = f'<div style="text-align:center;"><div style="font-size:14px;">{status_emoji}</div><div style="font-size:10px; font-weight:600; color:{status_cor};">{status_texto}</div></div>'
    m2 = f'<div style="text-align:center;"><div style="font-size:14px; font-weight:700; color:{cor_bugs};">{card["bugs"]}</div><div style="font-size:9px; color:#94a3b8;">BUGS</div></div>'
    m3 = f'<div style="text-align:center;"><div style="font-size:14px; font-weight:700; color:{cor_lead};">{card["lead_time"]}d</div><div style="font-size:9px; color:#94a3b8;">TEMPO TOTAL</div></div>'
    m4 = f'<div style="text-align:center;"><div style="font-size:14px; font-weight:700; color:{cor_aging};">{card["dias_em_status"]}d</div><div style="font-size:9px; color:#94a3b8;">NO STATUS</div></div>'
    m5 = f'<div style="text-align:center;"><div style="font-size:14px; font-weight:700; color:{cor_sp};">{card["sp"]}</div><div style="font-size:9px; color:#94a3b8;">PONTOS</div></div>'
    
    # HTML compacto em uma linha (5 colunas - removido FPY/Score por agora)
    html = f'<div style="background:{bg}; border:1px solid {status_cor}40; border-radius:8px; padding:10px 12px; margin-bottom:8px; display:grid; grid-template-columns:repeat(5,1fr); gap:8px; align-items:center;">{m1}{m2}{m3}{m4}{m5}</div>'
    st.markdown(html, unsafe_allow_html=True)
    
    # Alertas em linha (se houver)
    if alertas:
        alertas_html = " ".join([f'<span style="background:{cor}15; color:{cor}; padding:2px 6px; border-radius:4px; font-size:11px;">{icone} {txt}</span>' for icone, txt, cor in alertas])
        st.markdown(f'<div style="margin-bottom:8px;">{alertas_html}</div>', unsafe_allow_html=True)
    
    # Seção técnica expansível
    with st.expander("📊 Métricas Técnicas", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Score de Qualidade", f"{fk:.2f}", help="Fator K = pontos / (1 + bugs). Maior é melhor.")
            st.caption(f"Maturidade: **{mat['selo']}** ({mat['desc']})")
        with col2:
            st.metric("FPY (First Pass Yield)", fpy, help="100% se sem bugs na primeira entrega, 0% se teve bugs.")
        with col3:
            st.metric("Retornos p/ Dev", retornos, help="Quantas vezes voltou do QA para desenvolvimento.")


def _renderizar_metricas_qa_compactas(card: Dict, status_geral: tuple):
    """Métricas QA em layout compacto."""
    status_tipo, status_cor, status_titulo, status_msg = status_geral
    
    cor_lead = "#22c55e" if card['lead_time'] <= 14 else "#f59e0b" if card['lead_time'] <= 30 else "#ef4444"
    cor_aging = "#22c55e" if card['dias_em_status'] <= 7 else "#f59e0b" if card['dias_em_status'] <= 30 else "#ef4444"
    cor_sp = "#3b82f6" if card['sp'] > 0 else "#f59e0b"
    
    bg_colors = {"saudavel": "#f0fdf4", "atencao": "#fffbeb", "critico": "#fef2f2"}
    bg = bg_colors.get(status_tipo, '#f8fafc')
    
    status_parts = status_titulo.split(maxsplit=1)
    status_emoji = status_parts[0] if status_parts else "✅"
    status_texto = status_parts[1] if len(status_parts) > 1 else ""
    
    # Mini cards inline COM NOMES CLAROS
    m1 = f'<div style="text-align:center;"><div style="font-size:14px;">{status_emoji}</div><div style="font-size:10px; font-weight:600; color:{status_cor};">{status_texto}</div></div>'
    m2 = f'<div style="text-align:center;"><div style="font-size:14px; font-weight:700; color:{cor_lead};">{card["lead_time"]}d</div><div style="font-size:9px; color:#94a3b8;">TEMPO TOTAL</div></div>'
    m3 = f'<div style="text-align:center;"><div style="font-size:14px; font-weight:700; color:{cor_aging};">{card["dias_em_status"]}d</div><div style="font-size:9px; color:#94a3b8;">NO STATUS</div></div>'
    m4 = f'<div style="text-align:center;"><div style="font-size:14px; font-weight:700; color:{cor_sp};">{card["sp"]}</div><div style="font-size:9px; color:#94a3b8;">PONTOS</div></div>'
    
    html = f'<div style="background:{bg}; border:1px solid {status_cor}40; border-radius:8px; padding:10px 12px; margin-bottom:8px; display:grid; grid-template-columns:repeat(4,1fr); gap:8px; align-items:center;">{m1}{m2}{m3}{m4}</div>'
    st.markdown(html, unsafe_allow_html=True)


def _renderizar_metricas_pb_compactas(card: Dict, status_geral: tuple):
    """Métricas PB em layout compacto."""
    status_tipo, status_cor, status_titulo, status_msg = status_geral
    
    dias_backlog = (datetime.now() - card['criado']).days if pd.notna(card['criado']) else 0
    cor_backlog = "#22c55e" if dias_backlog <= 30 else "#f59e0b" if dias_backlog <= 90 else "#ef4444"
    cor_sp = "#22c55e" if card['sp'] > 0 else "#f59e0b"
    
    prio_cores = {"Highest": "#ef4444", "High": "#f97316", "Medium": "#eab308", "Low": "#22c55e", "Lowest": "#6b7280"}
    cor_prio = prio_cores.get(card['prioridade'], "#6b7280")
    
    bg_colors = {"saudavel": "#f0fdf4", "atencao": "#fffbeb", "critico": "#fef2f2"}
    bg = bg_colors.get(status_tipo, '#f8fafc')
    
    status_parts = status_titulo.split(maxsplit=1)
    status_emoji = status_parts[0] if status_parts else "✅"
    status_texto = status_parts[1] if len(status_parts) > 1 else ""
    
    prio_short = card['prioridade'] if card['prioridade'] else "-"
    sp_val = str(card['sp']) if card['sp'] > 0 else "?"
    
    # Mini cards inline COM NOMES CLAROS
    m1 = f'<div style="text-align:center;"><div style="font-size:14px;">{status_emoji}</div><div style="font-size:10px; font-weight:600; color:{status_cor};">{status_texto}</div></div>'
    m2 = f'<div style="text-align:center;"><div style="font-size:14px; font-weight:700; color:{cor_prio};">{prio_short}</div><div style="font-size:9px; color:#94a3b8;">PRIORIDADE</div></div>'
    m3 = f'<div style="text-align:center;"><div style="font-size:14px; font-weight:700; color:{cor_backlog};">{dias_backlog}d</div><div style="font-size:9px; color:#94a3b8;">NO BACKLOG</div></div>'
    m4 = f'<div style="text-align:center;"><div style="font-size:14px; font-weight:700; color:{cor_sp};">{sp_val}</div><div style="font-size:9px; color:#94a3b8;">PONTOS</div></div>'
    
    html = f'<div style="background:{bg}; border:1px solid {status_cor}40; border-radius:8px; padding:10px 12px; margin-bottom:8px; display:grid; grid-template-columns:repeat(4,1fr); gap:8px; align-items:center;">{m1}{m2}{m3}{m4}</div>'
    st.markdown(html, unsafe_allow_html=True)


# ==============================================================================
# TIMELINE COMPACTA
# ==============================================================================

def _exibir_timeline_simples(historico: List[Dict]):
    """Timeline visual simplificada - apenas os cards, sem métricas extras."""
    
    if not historico:
        return
    
    total_eventos = len(historico)
    total_dias = sum(e.get('duracao_dias', 0) for e in historico)
    
    with st.expander(f"📜 **Timeline** ({total_eventos} eventos • {total_dias}d)", expanded=False):
        
        # Monta cards da timeline
        cards_html = ""
        for i, evento in enumerate(historico):
            data_fmt = evento['data'].strftime('%d/%m') if evento.get('data') else ''
            duracao = evento.get('duracao_dias', 0)
            para = str(evento.get('para', ''))[:18]
            cor = evento.get('cor', '#6366f1')
            icone = evento.get('icone', '📋')
            
            is_current = (i == len(historico) - 1)
            current_style = "border: 2px solid #22c55e; box-shadow: 0 2px 8px rgba(34,197,94,0.25);" if is_current else ""
            badge = '<div style="background:#22c55e; color:white; font-size:9px; padding:3px 6px; border-radius:4px; margin-top:6px;">ATUAL</div>' if is_current else ""
            arrow = "" if is_current else '<div style="color:#cbd5e1; font-size:20px; padding:0 6px;">→</div>'
            
            # Alerta visual se ficou muito tempo
            tempo_alert = ""
            if duracao >= 5:
                tempo_alert = f'<div style="color:#ef4444; font-size:9px; margin-top:2px;">⚠️ {duracao}d</div>'
            
            cards_html += f'''
            <div style="flex:0 0 auto; min-width:120px; background:white; border-radius:10px; padding:12px; border-top:4px solid {cor}; {current_style}">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                    <span style="font-size:18px;">{icone}</span>
                    <span style="font-size:10px; color:#94a3b8;">{data_fmt}</span>
                </div>
                <div style="font-size:12px; font-weight:600; color:{cor}; line-height:1.3;">{para}</div>
                <div style="font-size:10px; color:#64748b; margin-top:4px;">⏱️ {duracao}d</div>
                {tempo_alert}
                {badge}
            </div>
            {arrow}
            '''
        
        # HTML completo com scroll
        html_completo = f'''
        <div style="overflow-x:auto; padding:12px 4px; background:#f8fafc; border-radius:10px;">
            <div style="display:flex; align-items:center; gap:4px; width:max-content;">
                {cards_html}
            </div>
        </div>
        <p style="font-size:11px; color:#94a3b8; text-align:center; margin-top:8px;">⬅️ Arraste para ver histórico completo ➡️</p>
        '''
        
        components.html(html_completo, height=200, scrolling=False)


def _renderizar_timeline_compacta(historico: List[Dict], card: Dict):
    """Timeline simplificada e compacta."""
    
    if not historico:
        return
    
    # Métricas rápidas
    total_dias = sum(e.get('duracao_dias', 0) for e in historico)
    gargalos = len([e for e in historico if e.get('duracao_dias', 0) >= 5])
    
    # Conta retornos
    retornos = 0
    for h in historico:
        if h.get('tipo') == 'transicao':
            de = str(h.get('de', '')).lower()
            para = str(h.get('para', '')).lower()
            if any(x in de for x in ['validação', 'qa', 'testing']):
                if any(x in para for x in ['desenvolvimento', 'andamento', 'dev']):
                    retornos += 1
    
    with st.expander(f"📜 **Jornada** — {len(historico)} eventos • {total_dias}d total" + (f" • {gargalos} gargalos" if gargalos else ""), expanded=False):
        
        # Timeline horizontal compacta
        timeline_items = []
        for i, evento in enumerate(historico[-8:]):  # Últimos 8 eventos
            data_fmt = evento['data'].strftime('%d/%m') if evento.get('data') else ''
            duracao = evento.get('duracao_dias', 0)
            para = str(evento.get('para', ''))[:12]
            cor = evento.get('cor', '#6366f1')
            
            is_gargalo = duracao >= 5
            gargalo_style = "border: 2px solid #ef4444;" if is_gargalo else ""
            
            item_html = f'<div style="flex: 0 0 auto; background: white; padding: 8px 12px; border-radius: 8px; border-top: 3px solid {cor}; min-width: 90px; {gargalo_style}"><div style="font-size: 10px; color: #94a3b8;">{data_fmt}</div><div style="font-size: 12px; font-weight: 600; color: {cor};">{para}</div><div style="font-size: 10px; color: #64748b;">{duracao}d</div></div>'
            timeline_items.append(item_html)
        
        # Junta itens com setas
        seta = '<span style="color: #94a3b8; font-size: 16px; padding: 0 4px;">→</span>'
        items_html = seta.join(timeline_items)
        
        # HTML final em uma linha
        html = f'<div style="overflow-x: auto; padding: 8px;"><div style="display: flex; gap: 4px; align-items: center; flex-wrap: nowrap;">{items_html}</div></div>'
        st.markdown(html, unsafe_allow_html=True)
        
        # Insights em uma linha
        insights = []
        if gargalos > 0:
            maior = max([e for e in historico if e.get('duracao_dias', 0) >= 5], key=lambda x: x.get('duracao_dias', 0))
            insights.append(f"⏰ {maior.get('duracao_dias')}d em '{maior.get('para', 'N/A')[:15]}'")
        if retornos > 0:
            insights.append(f"🔄 {retornos} retorno(s) DEV")
        
        if insights:
            st.caption(" • ".join(insights))


# ==============================================================================
# DIAGNÓSTICO SIMPLIFICADO (mantido para compatibilidade)
# ==============================================================================

def _calcular_diagnostico(card: Dict, historico: List[Dict], projeto: str) -> Dict:
    """Calcula diagnóstico geral do card com linguagem simples."""
    
    # Cards concluídos (Done) não precisam de alertas
    status_lower = card['status'].lower()
    is_done = any(x in status_lower for x in ['done', 'concluído', 'concluido', 'finalizado', 'closed', 'fechado'])
    
    if is_done:
        # Card concluído - mostra resumo positivo
        motivos = []
        if projeto == "SD":
            if card['bugs'] == 0:
                motivos.append("✨ Aprovado de primeira (FPY 100%)")
            else:
                motivos.append(f"{card['bugs']} bug(s) corrigido(s)")
        motivos.append("Card finalizado com sucesso")
        
        return {
            "status": "saudavel",
            "emoji": "✅",
            "titulo": "Concluído",
            "cor": "#22c55e",
            "motivos": motivos[:2]
        }
    
    pontos_criticos = 0
    pontos_atencao = 0
    motivos = []
    
    if projeto == "SD":
        # Bugs (linguagem simples)
        if card['bugs'] > 3:
            pontos_criticos += 2
            motivos.append(f"{card['bugs']} bugs encontrados")
        elif card['bugs'] > 0:
            pontos_atencao += 1
            motivos.append(f"{card['bugs']} bug(s) registrado(s)")
        
        # Janela de validação (só se não está Done)
        if card.get('janela_status') == 'fora':
            pontos_criticos += 2
            motivos.append("Fora do prazo de validação")
        elif card.get('janela_status') == 'risco':
            pontos_atencao += 1
            motivos.append("Prazo apertado para validar")
    
    # Lead Time (só para cards em andamento)
    if card['lead_time'] > 21:
        pontos_atencao += 1
        motivos.append(f"Em andamento há {card['lead_time']} dias")
    
    # Aging no status atual (só se faz sentido - não para Done)
    if card['dias_em_status'] > 7:
        pontos_atencao += 1
        motivos.append(f"Há {card['dias_em_status']} dias neste status")
    
    # SP zerado
    if card['sp'] == 0 and projeto in ['SD', 'QA']:
        pontos_atencao += 1
        motivos.append("Sem estimativa de esforço")
    
    # QA não atribuído
    if projeto == "SD" and not card.get('qa'):
        pontos_atencao += 1
        motivos.append("Sem QA responsável")
    
    # Retrabalhos
    if historico:
        retornos = len([h for h in historico if h['tipo'] == 'transicao' and h.get('de') and 
                       any(x in str(h.get('de', '')).lower() for x in ['validação', 'qa', 'testing']) and
                       any(x in str(h.get('para', '')).lower() for x in ['desenvolvimento', 'andamento'])])
        if retornos > 1:
            pontos_criticos += 1
            motivos.append(f"Voltou {retornos}x para correção")
        elif retornos == 1:
            pontos_atencao += 1
            motivos.append("Voltou 1x para correção")
    
    # Determina status
    if pontos_criticos >= 2:
        status = "critico"
        emoji = "🚨"
        titulo = "Precisa de Atenção Urgente"
        cor = "#ef4444"
    elif pontos_criticos >= 1 or pontos_atencao >= 2:
        status = "atencao"
        emoji = "⚠️"
        titulo = "Alguns Pontos de Atenção"
        cor = "#f59e0b"
    else:
        status = "saudavel"
        emoji = "✅"
        titulo = "Tudo OK"
        cor = "#22c55e"
        if not motivos:
            motivos.append("Card em bom estado")
    
    return {
        "status": status,
        "emoji": emoji,
        "titulo": titulo,
        "cor": cor,
        "motivos": motivos[:3]
    }


def _renderizar_diagnostico(diagnostico: Dict, card: Dict, projeto: str):
    """Renderiza card de diagnóstico simplificado."""
    
    motivos_text = " • ".join(diagnostico['motivos']) if diagnostico['motivos'] else ""
    
    bg_colors = {
        "saudavel": "linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%)",
        "atencao": "linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)",
        "critico": "linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)"
    }
    
    diag_html = f"""
    <div style="background: {bg_colors.get(diagnostico['status'], bg_colors['saudavel'])}; 
                padding: 20px 24px; border-radius: 14px; margin-bottom: 20px;
                border: 2px solid {diagnostico['cor']}; display: flex; align-items: center; gap: 16px;">
        <div style="font-size: 2.5em;">{diagnostico['emoji']}</div>
        <div>
            <h3 style="color: {diagnostico['cor']}; margin: 0; font-size: 1.3em;">{diagnostico['titulo']}</h3>
            <p style="margin: 4px 0 0 0; font-size: 0.9em; color: #475569;">{motivos_text}</p>
        </div>
    </div>
    """
    st.markdown(diag_html, unsafe_allow_html=True)


# ==============================================================================
# INFORMAÇÕES + DESCRIÇÃO
# ==============================================================================

def _renderizar_info_descricao(card: Dict, projeto: str):
    """Renderiza informações básicas (padrão antigo com expander)."""
    
    with st.expander("📋 **Informações Básicas**", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
| Campo | Valor |
|-------|-------|
| **Projeto** | {card.get('projeto', 'SD')} |
| **Sprint** | {card['sprint']} |
| **Produto** | {card['produto']} |
| **Tipo** | {card['tipo_original']} |
            """)
        
        with col2:
            qa_linha = f"| **QA Responsável** | {card.get('qa', 'Não atribuído')} |" if projeto == "SD" else ""
            bugs_linha = f"| **Bugs** | {card['bugs']} |" if projeto == "SD" else ""
            complexidade = card.get('complexidade', 'Não definida') or 'Não definida'
            
            st.markdown(f"""
| Campo | Valor |
|-------|-------|
| **Desenvolvedor** | {card['desenvolvedor']} |
{qa_linha}
| **Story Points** | {card['sp']} |
{f"| **Complexidade** | {complexidade} |" if projeto == "SD" else ""}
{bugs_linha}
            """)
    
    # Descrição do card (se existir)
    descricao = card.get('descricao', '')
    if descricao and str(descricao).strip():
        with st.expander("📝 **Descrição do Card**", expanded=False):
            desc_safe = str(descricao)[:3000]
            desc_safe = desc_safe.replace('<', '&lt;').replace('>', '&gt;')
            st.markdown(f'''<div style="background: #f8fafc; padding: 16px; border-radius: 8px; border-left: 3px solid #3b82f6; line-height: 1.6; white-space: pre-wrap;">{desc_safe}{'...' if len(str(descricao)) > 3000 else ''}</div>''', unsafe_allow_html=True)


# ==============================================================================
# CARDS VINCULADOS (IMPORTANTE!)
# ==============================================================================

def _renderizar_cards_vinculados(links: List[Dict]):
    """Renderiza seção de cards vinculados com botão NinaDash - padrão da plataforma."""
    
    if not links:
        with st.expander("🔗 **Cards Vinculados (0)**", expanded=False):
            st.markdown('''<div style="background: #f8fafc; padding: 15px; border-radius: 8px; text-align: center; color: #64748b;"><span style="font-size: 1.5em;">🔗</span><br><span style="font-size: 0.9em;">Nenhum card vinculado</span></div>''', unsafe_allow_html=True)
        return
    
    # Separa por nível
    links_nivel_1 = [l for l in links if l.get('nivel', 1) == 1]
    links_nivel_2 = [l for l in links if l.get('nivel', 1) == 2]
    
    with st.expander(f"🔗 **Cards Vinculados ({len(links)})**", expanded=True):
        
        # Links diretos
        if links_nivel_1:
            st.markdown("**🔵 Links Diretos:**")
            for link in links_nivel_1:
                tipo_cores = {"Pai": "#6366f1", "Subtarefa": "#22c55e", "Bloqueia": "#ef4444", "Bloqueado por": "#f97316"}
                tipo_cor = tipo_cores.get(link['tipo'], "#64748b")
                
                # Usa card_link_com_popup para ter o botão NinaDash
                card_popup_html = card_link_com_popup(link['ticket_id'])
                titulo_safe = link['titulo'][:60] + ('...' if len(link['titulo']) > 60 else '')
                
                link_html = f'''<div style="background: {tipo_cor}10; padding: 10px 15px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid {tipo_cor};"><div style="display: flex; justify-content: space-between; align-items: center;"><div><span style="color: {tipo_cor}; font-weight: bold; font-size: 0.85em;">{link['tipo']}</span><span style="color: #666; font-size: 0.8em;"> • {link.get('direcao', '')}</span><br>{card_popup_html}<span style="color: #666; font-size: 0.85em;"> - {titulo_safe}</span></div><div style="text-align: right;"><span style="background: #e5e7eb; padding: 3px 8px; border-radius: 4px; font-size: 0.75em;">{link['status']}</span></div></div></div>'''
                st.markdown(link_html, unsafe_allow_html=True)
        
        # Links de segundo nível
        if links_nivel_2:
            st.markdown("---")
            st.markdown("**🔗 Outros Cards Relacionados** *(via cards vinculados)*:")
            st.caption("Cards conectados através dos links diretos acima")
            for link in links_nivel_2[:10]:
                card_popup_html = card_link_com_popup(link['ticket_id'])
                via_text = f" (via {link.get('via', '')})" if link.get('via') else ""
                titulo_safe = link['titulo'][:50] + ('...' if len(link['titulo']) > 50 else '')
                
                link_html = f'''<div style="background: #f1f5f9; padding: 8px 12px; border-radius: 6px; margin-bottom: 6px; border-left: 3px dashed #94a3b8;"><div style="display: flex; justify-content: space-between; align-items: center;"><div><span style="color: #64748b; font-size: 0.8em;">{link['tipo']} • {link.get('direcao', '')}</span><span style="color: #94a3b8; font-size: 0.75em;">{via_text}</span><br>{card_popup_html}<span style="color: #64748b; font-size: 0.8em;"> - {titulo_safe}</span></div><div><span style="background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-size: 0.7em; color: #64748b;">{link['status']}</span></div></div></div>'''
                st.markdown(link_html, unsafe_allow_html=True)
            
            if len(links_nivel_2) > 10:
                st.caption(f"... e mais {len(links_nivel_2) - 10} cards relacionados")


# ==============================================================================
# ALERTAS AUTOMÁTICOS
# ==============================================================================

def _gerar_alertas(card: Dict, historico: List[Dict], projeto: str) -> List[Dict]:
    """
    Gera lista de alertas inteligentes baseados em cruzamento de dados.
    
    Regras de cruzamento:
    - Bugs + Lead Time = possível problema de qualidade sistêmico
    - SP zerado + Em andamento = risco de scope creep
    - Muitos retornos + Bugs = padrão de retrabalho
    - Tempo alto em status + Sem QA = possível gargalo de processo
    """
    
    alertas = []
    status_lower = card['status'].lower()
    is_done = any(x in status_lower for x in ['done', 'concluído', 'concluido', 'finalizado'])
    
    # ========== ALERTAS CRÍTICOS ==========
    
    # Card bloqueado
    if 'block' in status_lower or 'impedido' in status_lower:
        alertas.append({
            "tipo": "critico",
            "icone": "🚫",
            "texto": f"Card BLOQUEADO — Status: {card['status']}",
            "contexto": "Requer ação imediata para desbloquear"
        })
    
    # Cruzamento: Muitos bugs + Lead Time alto = problema sistêmico
    if projeto == "SD" and card['bugs'] > 3 and card['lead_time'] > 14:
        alertas.append({
            "tipo": "critico",
            "icone": "🔥",
            "texto": f"{card['bugs']} bugs + {card['lead_time']} dias = Problema de qualidade",
            "contexto": "Considerar revisão do escopo ou pair programming"
        })
    elif projeto == "SD" and card['bugs'] > 3:
        alertas.append({
            "tipo": "critico",
            "icone": "🐛",
            "texto": f"Alto volume de bugs ({card['bugs']})",
            "contexto": "Qualidade comprometida — revisar code review"
        })
    
    # Sem QA em status que precisa
    if projeto == "SD" and not card.get('qa'):
        status_precisa_qa = ['validação', 'qa', 'testing', 'code review', 'review', 'homologação']
        if any(s in status_lower for s in status_precisa_qa):
            alertas.append({
                "tipo": "critico",
                "icone": "👤",
                "texto": "Sem QA atribuído para validar",
                "contexto": "Card em validação sem responsável definido"
            })
        elif not is_done:
            alertas.append({
                "tipo": "atencao",
                "icone": "👤",
                "texto": "QA não atribuído",
                "contexto": "Atribuir antes de chegar na validação"
            })
    
    # ========== ALERTAS DE ATENÇÃO ==========
    
    # Cruzamento: Lead Time alto + Parado em status = Gargalo
    if card['lead_time'] > 14 and card['dias_em_status'] > 5:
        alertas.append({
            "tipo": "atencao",
            "icone": "⏰",
            "texto": f"Possível gargalo: {card['dias_em_status']}d no status atual",
            "contexto": f"Lead Time total já está em {card['lead_time']} dias"
        })
    elif card['dias_em_status'] > 7:
        alertas.append({
            "tipo": "atencao",
            "icone": "⏰",
            "texto": f"Parado há {card['dias_em_status']} dias",
            "contexto": "Verificar se há impedimento não registrado"
        })
    
    # Cruzamento: SP zerado + Em andamento = risco
    if card['sp'] == 0 and projeto in ['SD', 'QA']:
        if any(s in status_lower for s in ['andamento', 'progress', 'doing', 'desenvolvimento']):
            alertas.append({
                "tipo": "atencao",
                "icone": "📊",
                "texto": "Em andamento sem estimativa de esforço",
                "contexto": "Risco de scope creep — definir SP"
            })
        elif not is_done:
            alertas.append({
                "tipo": "atencao",
                "icone": "📊",
                "texto": "Story Points não definidos",
                "contexto": "Estimar antes do desenvolvimento"
            })
    
    # Complexidade não definida (SD)
    if projeto == "SD":
        complexidade = card.get('complexidade', 'Não definida') or 'Não definida'
        if complexidade == 'Não definida' and not is_done:
            alertas.append({
                "tipo": "atencao",
                "icone": "🧠",
                "texto": "Complexidade não definida",
                "contexto": "Importante para planejamento de sprint"
            })
    
    # Lead Time acima do esperado
    if card['lead_time'] > 21 and not is_done:
        alertas.append({
            "tipo": "atencao",
            "icone": "📅",
            "texto": f"Lead Time crítico: {card['lead_time']} dias",
            "contexto": "Acima do esperado para maioria dos cards"
        })
    
    # Análise de histórico - retornos para DEV
    if historico:
        retornos = len([h for h in historico if h.get('tipo') == 'transicao' and 
                       any(x in str(h.get('de', '')).lower() for x in ['validação', 'qa', 'testing']) and
                       any(x in str(h.get('para', '')).lower() for x in ['desenvolvimento', 'andamento', 'dev'])])
        
        if retornos >= 2:
            # Cruzamento: Muitos retornos + Bugs = padrão de retrabalho
            if projeto == "SD" and card['bugs'] > 0:
                alertas.append({
                    "tipo": "atencao",
                    "icone": "🔄",
                    "texto": f"{retornos} retornos + {card['bugs']} bugs = padrão de retrabalho",
                    "contexto": "Revisar critérios de aceite e definição de pronto"
                })
            else:
                alertas.append({
                    "tipo": "atencao",
                    "icone": "🔄",
                    "texto": f"Card retornou {retornos}x para correção",
                    "contexto": "Verificar qualidade da comunicação de requisitos"
                })
    
    # ========== ALERTAS DE SUCESSO ==========
    
    # FPY 100% (First Pass Yield)
    if projeto == "SD" and card['bugs'] == 0 and is_done:
        alertas.append({
            "tipo": "sucesso",
            "icone": "🏆",
            "texto": "Aprovado de primeira! FPY 100%",
            "contexto": "Zero bugs — excelente qualidade de entrega"
        })
    
    # Entrega rápida
    if is_done and card['lead_time'] <= 5:
        alertas.append({
            "tipo": "sucesso",
            "icone": "⚡",
            "texto": f"Entrega rápida: {card['lead_time']} dias",
            "contexto": "Abaixo da média esperada"
        })
    
    return alertas[:6]


def _renderizar_alertas(alertas: List[Dict]):
    """Renderiza alertas inteligentes em expander."""
    
    # Conta por tipo para mostrar no título
    criticos = len([a for a in alertas if a['tipo'] == 'critico'])
    atencao = len([a for a in alertas if a['tipo'] == 'atencao'])
    sucesso = len([a for a in alertas if a['tipo'] == 'sucesso'])
    
    # Monta título dinâmico
    titulo_extra = []
    if criticos > 0:
        titulo_extra.append(f"🚨 {criticos}")
    if atencao > 0:
        titulo_extra.append(f"⚠️ {atencao}")
    if sucesso > 0:
        titulo_extra.append(f"✅ {sucesso}")
    
    titulo_suffix = f" — {' | '.join(titulo_extra)}" if titulo_extra else ""
    
    with st.expander(f"🔔 **Alertas Inteligentes ({len(alertas)})**{titulo_suffix}", expanded=True):
        
        # Aviso de cruzamento de dados
        st.markdown("""
        <div style="background: #f1f5f9; padding: 8px 12px; border-radius: 8px; margin-bottom: 12px; 
                    font-size: 11px; color: #64748b; display: flex; align-items: center; gap: 8px;">
            <span>🧠</span>
            <span>Alertas gerados por análise automática de múltiplos indicadores</span>
        </div>
        """, unsafe_allow_html=True)
        
        cores_tipo = {
            "critico": ("#fef2f2", "#ef4444", "🚨"),
            "atencao": ("#fffbeb", "#f59e0b", "⚠️"),
            "info": ("#eff6ff", "#3b82f6", "ℹ️"),
            "sucesso": ("#f0fdf4", "#22c55e", "✅")
        }
        
        for alerta in alertas:
            bg, border, badge = cores_tipo.get(alerta['tipo'], cores_tipo['info'])
            contexto_html = f'<div style="font-size: 11px; color: #64748b; margin-top: 4px;">{alerta.get("contexto", "")}</div>' if alerta.get('contexto') else ""
            
            alert_html = f'''
            <div style="background: {bg}; padding: 14px 16px; border-radius: 12px; margin-bottom: 10px; 
                        border-left: 4px solid {border};">
                <div style="display: flex; align-items: flex-start; gap: 12px;">
                    <span style="font-size: 1.5em;">{alerta['icone']}</span>
                    <div style="flex: 1;">
                        <div style="font-weight: 600; color: #1e293b; font-size: 0.95em;">{alerta['texto']}</div>
                        {contexto_html}
                    </div>
                    <span style="font-size: 0.8em;">{badge}</span>
                </div>
            </div>
            '''
            st.markdown(alert_html, unsafe_allow_html=True)


# ==============================================================================
# KPIs ORGANIZADOS POR CONTEXTO
# ==============================================================================

def _renderizar_kpis(card: Dict, projeto: str):
    """Renderiza KPIs organizados em grupos por contexto."""
    
    if projeto == "SD":
        _renderizar_grupos_metricas_sd(card)
    elif projeto == "QA":
        _renderizar_grupos_metricas_qa(card)
    elif projeto == "PB":
        _renderizar_grupos_metricas_pb(card)


def _criar_card_metrica_v2(icone: str, label: str, valor: str, cor: str, 
                           status: str = "normal", insight: str = "") -> str:
    """
    Cria HTML de um card de métrica visual com design moderno.
    
    Args:
        icone: Emoji do indicador
        label: Nome do indicador
        valor: Valor a exibir
        cor: Cor principal (hex)
        status: "saudavel", "atencao", "critico", "normal"
        insight: Texto de insight/contexto (opcional)
    """
    # Cores de fundo baseadas no status
    bg_colors = {
        "saudavel": f"linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)",
        "atencao": f"linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)",
        "critico": f"linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)",
        "normal": f"linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)"
    }
    
    border_colors = {
        "saudavel": "#22c55e",
        "atencao": "#f59e0b",
        "critico": "#ef4444",
        "normal": cor
    }
    
    bg = bg_colors.get(status, bg_colors["normal"])
    border = border_colors.get(status, cor)
    
    # Status badge
    status_badges = {
        "saudavel": '<span style="background: #22c55e; color: white; font-size: 9px; padding: 2px 6px; border-radius: 4px; font-weight: 600;">✓ OK</span>',
        "atencao": '<span style="background: #f59e0b; color: white; font-size: 9px; padding: 2px 6px; border-radius: 4px; font-weight: 600;">⚠ ATENÇÃO</span>',
        "critico": '<span style="background: #ef4444; color: white; font-size: 9px; padding: 2px 6px; border-radius: 4px; font-weight: 600;">🚨 CRÍTICO</span>',
        "normal": ""
    }
    badge = status_badges.get(status, "")
    
    insight_html = f'<div style="font-size: 10px; color: #64748b; margin-top: 6px; line-height: 1.3;">{insight}</div>' if insight else ""
    
    return f"""
    <div style="background: {bg}; border-radius: 14px; padding: 18px; text-align: center; 
                border: 2px solid {border}; min-height: 130px;
                display: flex; flex-direction: column; justify-content: center;
                box-shadow: 0 2px 8px rgba(0,0,0,0.04); transition: all 0.2s ease;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 1.8em;">{icone}</span>
            {badge}
        </div>
        <div style="font-size: 0.7em; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">{label}</div>
        <div style="font-size: 1.6em; font-weight: 700; color: {cor}; margin-top: 4px;">{valor}</div>
        {insight_html}
    </div>
    """


def _criar_grupo_cards(titulo: str, icone: str, cor_titulo: str) -> str:
    """Cria header de um grupo de cards."""
    return f"""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 2px solid {cor_titulo}20;">
        <span style="font-size: 1.3em;">{icone}</span>
        <span style="font-size: 1em; font-weight: 700; color: {cor_titulo}; text-transform: uppercase; letter-spacing: 0.5px;">{titulo}</span>
    </div>
    """


def _renderizar_grupos_metricas_sd(card: Dict):
    """Renderiza os 3 grupos de métricas para SD."""
    
    # Cálculos de qualidade
    from modulos.calculos import calcular_fator_k, classificar_maturidade
    fk = calcular_fator_k(card['sp'], card['bugs'])
    mat = classificar_maturidade(fk)
    fpy = 100 if card['bugs'] == 0 else 0
    
    # Determina status de qualidade
    if card['bugs'] == 0:
        status_qualidade = "saudavel"
        insight_qualidade = "Excelente! Sem bugs reportados"
    elif card['bugs'] <= 2:
        status_qualidade = "atencao"
        insight_qualidade = f"{card['bugs']} bug(s) - monitorar correções"
    else:
        status_qualidade = "critico"
        insight_qualidade = f"Alto volume de bugs detectado"
    
    # Status do score
    if fk >= 0.8:
        status_score = "saudavel"
        insight_score = "Score saudável para entrega"
    elif fk >= 0.5:
        status_score = "atencao"
        insight_score = "Qualidade pode ser melhorada"
    else:
        status_score = "critico"
        insight_score = "Qualidade comprometida"
    
    # Status FPY
    status_fpy = "saudavel" if fpy == 100 else "critico"
    insight_fpy = "Aprovado de primeira!" if fpy == 100 else "Precisou de correções"
    
    # Cálculos de tempo
    if card['lead_time'] <= 7:
        status_lead = "saudavel"
        classificacao_lead = "Rápido"
        insight_lead = "Dentro do tempo ideal"
    elif card['lead_time'] <= 14:
        status_lead = "normal"
        classificacao_lead = "Normal"
        insight_lead = "Tempo aceitável"
    elif card['lead_time'] <= 21:
        status_lead = "atencao"
        classificacao_lead = "Lento"
        insight_lead = "Acima da média esperada"
    else:
        status_lead = "critico"
        classificacao_lead = "Crítico"
        insight_lead = f"⚠️ Possível gargalo no fluxo"
    
    # Status do aging
    if card['dias_em_status'] <= 3:
        status_aging = "saudavel"
        insight_aging = "Fluxo normal"
    elif card['dias_em_status'] <= 7:
        status_aging = "atencao"
        insight_aging = "Verificar se há bloqueio"
    else:
        status_aging = "critico"
        insight_aging = f"⚠️ Parado há muito tempo"
    
    # Status de esforço
    if card['sp'] > 0:
        status_sp = "saudavel"
        insight_sp = f"Estimativa definida"
    else:
        status_sp = "atencao"
        insight_sp = "Sem estimativa de esforço"
    
    complexidade = card.get('complexidade', 'Não definida') or 'Não definida'
    if complexidade and complexidade != 'Não definida':
        status_complex = "saudavel"
        insight_complex = f"Complexidade mapeada"
    else:
        status_complex = "atencao"
        insight_complex = "Definir para melhor planejamento"
    
    # ========== GRUPO QUALIDADE ==========
    with st.expander("📊 **Qualidade** — Score, Bugs e FPY", expanded=True):
        st.markdown(_criar_grupo_cards("Indicadores de Qualidade", "🎖️", "#6366f1"), unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(_criar_card_metrica_v2(
                "🎖️", "Score Qualidade", f"{fk:.2f}", mat['cor'],
                status_score, insight_score
            ), unsafe_allow_html=True)
        with col2:
            cor_bugs = "#22c55e" if card['bugs'] == 0 else "#f59e0b" if card['bugs'] <= 2 else "#ef4444"
            st.markdown(_criar_card_metrica_v2(
                "🐛", "Bugs", str(card['bugs']), cor_bugs,
                status_qualidade, insight_qualidade
            ), unsafe_allow_html=True)
        with col3:
            cor_fpy = "#22c55e" if fpy == 100 else "#ef4444"
            st.markdown(_criar_card_metrica_v2(
                "🎯", "1ª Vez OK (FPY)", f"{fpy}%", cor_fpy,
                status_fpy, insight_fpy
            ), unsafe_allow_html=True)
    
    # ========== GRUPO TEMPO ==========
    with st.expander("⏱️ **Tempo** — Lead Time e Aging", expanded=True):
        st.markdown(_criar_grupo_cards("Indicadores de Tempo", "⏱️", "#0891b2"), unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            cor_lead = "#22c55e" if card['lead_time'] <= 7 else "#f59e0b" if card['lead_time'] <= 14 else "#ef4444"
            st.markdown(_criar_card_metrica_v2(
                "📅", "Lead Time", f"{card['lead_time']}d ({classificacao_lead})", cor_lead,
                status_lead, insight_lead
            ), unsafe_allow_html=True)
        with col2:
            cor_aging = "#22c55e" if card['dias_em_status'] <= 3 else "#f59e0b" if card['dias_em_status'] <= 7 else "#ef4444"
            st.markdown(_criar_card_metrica_v2(
                "📍", "No Status Atual", f"{card['dias_em_status']}d", cor_aging,
                status_aging, insight_aging
            ), unsafe_allow_html=True)
    
    # ========== GRUPO ESFORÇO ==========
    with st.expander("🧩 **Esforço** — Story Points e Complexidade", expanded=True):
        st.markdown(_criar_grupo_cards("Indicadores de Esforço", "🧩", "#8b5cf6"), unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            cor_sp = "#22c55e" if card['sp'] > 0 else "#f59e0b"
            sp_valor = str(card['sp']) if card['sp'] > 0 else "0 ⚠️"
            st.markdown(_criar_card_metrica_v2(
                "📊", "Story Points", sp_valor, cor_sp,
                status_sp, insight_sp
            ), unsafe_allow_html=True)
        with col2:
            cor_complex = "#8b5cf6" if complexidade != 'Não definida' else "#f59e0b"
            complex_valor = complexidade if complexidade != 'Não definida' else "? ⚠️"
            st.markdown(_criar_card_metrica_v2(
                "🧠", "Complexidade", complex_valor, cor_complex,
                status_complex, insight_complex
            ), unsafe_allow_html=True)


def _renderizar_grupos_metricas_qa(card: Dict):
    """Renderiza grupos de métricas para QA."""
    
    # Status de tempo
    if card['dias_em_status'] <= 7:
        status_aging = "saudavel"
        insight_aging = "Dentro do esperado"
    elif card['dias_em_status'] <= 30:
        status_aging = "atencao"
        insight_aging = "Verificar progresso"
    else:
        status_aging = "critico"
        insight_aging = "Muito tempo parado"
    
    if card['lead_time'] <= 14:
        status_lead = "saudavel"
        classificacao_lead = "Bom"
        insight_lead = "Tempo adequado"
    elif card['lead_time'] <= 30:
        status_lead = "atencao"
        classificacao_lead = "Normal"
        insight_lead = "Monitorar progresso"
    else:
        status_lead = "critico"
        classificacao_lead = "Lento"
        insight_lead = "Acima do esperado"
    
    # Status de esforço
    status_sp = "saudavel" if card['sp'] > 0 else "atencao"
    insight_sp = "Estimado" if card['sp'] > 0 else "Sem estimativa"
    
    # ========== GRUPO TEMPO ==========
    with st.expander("⏱️ **Tempo** — Lead Time e Status", expanded=True):
        st.markdown(_criar_grupo_cards("Indicadores de Tempo", "⏱️", "#0891b2"), unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            cor_aging = "#22c55e" if card['dias_em_status'] <= 7 else "#f59e0b" if card['dias_em_status'] <= 30 else "#ef4444"
            st.markdown(_criar_card_metrica_v2(
                "📍", "No Status Atual", f"{card['dias_em_status']}d", cor_aging,
                status_aging, insight_aging
            ), unsafe_allow_html=True)
        with col2:
            cor_lead = "#22c55e" if card['lead_time'] <= 14 else "#f59e0b" if card['lead_time'] <= 30 else "#ef4444"
            st.markdown(_criar_card_metrica_v2(
                "📅", "Lead Time", f"{card['lead_time']}d ({classificacao_lead})", cor_lead,
                status_lead, insight_lead
            ), unsafe_allow_html=True)
    
    # ========== GRUPO ESFORÇO ==========
    with st.expander("🧩 **Esforço** — Story Points", expanded=True):
        st.markdown(_criar_grupo_cards("Indicadores de Esforço", "🧩", "#8b5cf6"), unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            cor_sp = "#22c55e" if card['sp'] > 0 else "#f59e0b"
            sp_valor = str(card['sp']) if card['sp'] > 0 else "0 ⚠️"
            st.markdown(_criar_card_metrica_v2(
                "📊", "Story Points", sp_valor, cor_sp,
                status_sp, insight_sp
            ), unsafe_allow_html=True)
        with col2:
            st.markdown(_criar_card_metrica_v2(
                "📌", "Status", card['status'][:15], "#6366f1",
                "normal", ""
            ), unsafe_allow_html=True)


def _renderizar_grupos_metricas_pb(card: Dict):
    """Renderiza grupos de métricas para PB (Product Backlog)."""
    
    dias_backlog = (datetime.now() - card['criado']).days if pd.notna(card['criado']) else 0
    
    # Status de prioridade
    prio_status = {
        "Highest": ("critico", "#ef4444", "Prioridade máxima!"),
        "High": ("atencao", "#f97316", "Alta prioridade"),
        "Medium": ("normal", "#eab308", "Prioridade média"),
        "Low": ("saudavel", "#22c55e", "Pode aguardar"),
        "Lowest": ("saudavel", "#6b7280", "Baixa urgência")
    }
    status_prio, cor_prio, insight_prio = prio_status.get(card['prioridade'], ("normal", "#6b7280", ""))
    
    # Status de backlog
    if dias_backlog <= 30:
        status_backlog = "saudavel"
        insight_backlog = "Item recente"
    elif dias_backlog <= 90:
        status_backlog = "atencao"
        insight_backlog = "Verificar relevância"
    else:
        status_backlog = "critico"
        insight_backlog = "⚠️ Considerar priorizar ou arquivar"
    
    # Status de estimativa
    status_sp = "saudavel" if card['sp'] > 0 else "atencao"
    insight_sp = "Estimado" if card['sp'] > 0 else "Precisa estimar"
    
    # ========== GRUPO PRIORIDADE ==========
    with st.expander("⚡ **Priorização** — Urgência e Tempo no Backlog", expanded=True):
        st.markdown(_criar_grupo_cards("Indicadores de Prioridade", "⚡", "#ef4444"), unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(_criar_card_metrica_v2(
                "⚡", "Prioridade", card['prioridade'], cor_prio,
                status_prio, insight_prio
            ), unsafe_allow_html=True)
        with col2:
            cor_backlog = "#22c55e" if dias_backlog <= 30 else "#f59e0b" if dias_backlog <= 90 else "#ef4444"
            st.markdown(_criar_card_metrica_v2(
                "📅", "No Backlog", f"{dias_backlog}d", cor_backlog,
                status_backlog, insight_backlog
            ), unsafe_allow_html=True)
    
    # ========== GRUPO ESFORÇO ==========
    with st.expander("🧩 **Esforço** — Estimativa", expanded=True):
        st.markdown(_criar_grupo_cards("Indicadores de Esforço", "🧩", "#8b5cf6"), unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            cor_sp = "#22c55e" if card['sp'] > 0 else "#f59e0b"
            sp_valor = f"{card['sp']} SP" if card['sp'] > 0 else "? SP ⚠️"
            st.markdown(_criar_card_metrica_v2(
                "📊", "Estimativa", sp_valor, cor_sp,
                status_sp, insight_sp
            ), unsafe_allow_html=True)
        with col2:
            st.markdown(_criar_card_metrica_v2(
                "📌", "Status", card['status'][:15], "#6b7280",
                "normal", ""
            ), unsafe_allow_html=True)


# ==============================================================================
# TIMELINE
# ==============================================================================

def _renderizar_timeline_v2(historico: List[Dict], card: Dict):
    """Renderiza timeline interpretativa com insights automáticos."""
    
    if not historico:
        return
    
    # ========== ANÁLISE INTELIGENTE DO HISTÓRICO ==========
    total_dias = sum(e.get('duracao_dias', 0) for e in historico)
    gargalos = [e for e in historico if e.get('duracao_dias', 0) >= 5]
    
    # Detecta retornos para desenvolvimento (retrabalho)
    retornos_dev = []
    for i, e in enumerate(historico):
        if e.get('tipo') == 'transicao':
            de_lower = str(e.get('de', '')).lower()
            para_lower = str(e.get('para', '')).lower()
            
            # Detecta retorno de QA/Validação para DEV
            if any(x in de_lower for x in ['validação', 'qa', 'testing', 'review', 'homologação']):
                if any(x in para_lower for x in ['desenvolvimento', 'andamento', 'dev', 'progress', 'doing']):
                    retornos_dev.append(e)
    
    # Detecta períodos de inatividade (> 3 dias sem mudança)
    periodos_inativos = [e for e in historico if e.get('duracao_dias', 0) > 3 and e.get('tipo') == 'transicao']
    
    # Detecta saltos de fluxo (pulou etapas)
    saltos_fluxo = []
    fluxo_normal = ['backlog', 'todo', 'andamento', 'doing', 'review', 'validação', 'qa', 'done']
    for e in historico:
        if e.get('tipo') == 'transicao':
            de_lower = str(e.get('de', '')).lower()
            para_lower = str(e.get('para', '')).lower()
            # Detecta se pulou de backlog direto para done, etc
            if 'backlog' in de_lower and 'done' in para_lower:
                saltos_fluxo.append(e)
    
    # Gera insights textuais
    insights = []
    
    if len(gargalos) > 0:
        maior_gargalo = max(gargalos, key=lambda x: x.get('duracao_dias', 0))
        insights.append({
            "tipo": "critico",
            "icone": "⏰",
            "texto": f"Ficou {maior_gargalo.get('duracao_dias', 0)} dias em '{maior_gargalo.get('para', 'N/A')}'"
        })
    
    if len(retornos_dev) > 0:
        insights.append({
            "tipo": "atencao",
            "icone": "🔄",
            "texto": f"{len(retornos_dev)} retorno(s) para desenvolvimento (retrabalho)"
        })
    
    if len(periodos_inativos) > 2:
        insights.append({
            "tipo": "atencao",
            "icone": "💤",
            "texto": f"{len(periodos_inativos)} períodos de inatividade detectados"
        })
    
    if len(saltos_fluxo) > 0:
        insights.append({
            "tipo": "info",
            "icone": "⚡",
            "texto": f"Fluxo acelerado: pulou etapas do processo"
        })
    
    # Status geral da jornada
    if len(gargalos) == 0 and len(retornos_dev) == 0:
        status_jornada = ("saudavel", "#22c55e", "Fluxo saudável")
    elif len(gargalos) >= 2 or len(retornos_dev) >= 2:
        status_jornada = ("critico", "#ef4444", "Fluxo com problemas")
    else:
        status_jornada = ("atencao", "#f59e0b", "Alguns pontos de atenção")
    
    with st.expander(f"📜 **Jornada do Card** — {status_jornada[2]}", expanded=True):
        
        # ========== MÉTRICAS RESUMIDAS NO TOPO ==========
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {status_jornada[1]}10 0%, {status_jornada[1]}05 100%); 
                    border: 2px solid {status_jornada[1]}40; border-radius: 12px; padding: 16px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-around; text-align: center; flex-wrap: wrap; gap: 12px;">
                <div style="min-width: 80px;">
                    <div style="font-size: 1.8em; font-weight: 700; color: {status_jornada[1]};">{len(gargalos)}</div>
                    <div style="font-size: 0.75em; color: #64748b; text-transform: uppercase;">⚠️ Gargalos</div>
                </div>
                <div style="min-width: 80px;">
                    <div style="font-size: 1.8em; font-weight: 700; color: #0891b2;">{total_dias}d</div>
                    <div style="font-size: 0.75em; color: #64748b; text-transform: uppercase;">⏱️ Tempo Total</div>
                </div>
                <div style="min-width: 80px;">
                    <div style="font-size: 1.8em; font-weight: 700; color: #8b5cf6;">{len(retornos_dev)}</div>
                    <div style="font-size: 0.75em; color: #64748b; text-transform: uppercase;">🔄 Retornos DEV</div>
                </div>
                <div style="min-width: 80px;">
                    <div style="font-size: 1.8em; font-weight: 700; color: #64748b;">{len(historico)}</div>
                    <div style="font-size: 0.75em; color: #64748b; text-transform: uppercase;">📊 Eventos</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ========== INSIGHTS AUTOMÁTICOS ==========
        if insights:
            st.markdown("**🧠 Insights Automáticos:**")
            for insight in insights[:4]:
                cores = {"critico": "#fef2f2", "atencao": "#fffbeb", "info": "#eff6ff"}
                borders = {"critico": "#ef4444", "atencao": "#f59e0b", "info": "#3b82f6"}
                bg = cores.get(insight['tipo'], "#f8fafc")
                border = borders.get(insight['tipo'], "#64748b")
                
                st.markdown(f"""
                <div style="background: {bg}; padding: 10px 14px; border-radius: 8px; margin-bottom: 6px; 
                            border-left: 3px solid {border}; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.2em;">{insight['icone']}</span>
                    <span style="font-size: 0.9em; color: #1e293b;">{insight['texto']}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        
        # ========== TIMELINE VISUAL ==========
        cards_html = ""
        for i, evento in enumerate(historico):
            data_fmt = evento['data'].strftime('%d/%m/%y') if evento.get('data') else 'N/A'
            hora_fmt = evento['data'].strftime('%H:%M') if evento.get('data') else ''
            
            duracao_dias = evento.get('duracao_dias', 0)
            duracao = f"{duracao_dias}d" if duracao_dias > 0 else "< 1h"
            
            is_current = (i == len(historico) - 1)
            is_gargalo = duracao_dias >= 5
            is_retorno = evento in retornos_dev
            
            border_style = "2px solid #22c55e;" if is_current else ""
            
            # Badges
            badges_html = ""
            if is_gargalo:
                badges_html += '<div style="font-size:9px; background:#ef4444; color:white; padding:2px 6px; border-radius:4px; margin-top:4px;">⏰ GARGALO</div>'
            if is_retorno:
                badges_html += '<div style="font-size:9px; background:#f59e0b; color:white; padding:2px 6px; border-radius:4px; margin-top:4px;">🔄 RETORNO</div>'
            if is_current:
                badges_html += '<div style="background:#22c55e; color:white; font-size:10px; padding:4px 8px; border-radius:6px; margin-top:6px;">📍 ATUAL</div>'
            
            para_valor = str(evento.get('para', 'N/A'))[:25]
            arrow = "" if is_current else '<div style="display:flex; align-items:center; padding:0 6px; color:#94a3b8; font-size:24px;">→</div>'
            
            cor = evento.get('cor', '#6366f1')
            icone = evento.get('icone', '📋')
            
            cards_html += f'''
            <div style="position:relative; flex:0 0 auto; width:180px; background:white; border-radius:12px; 
                        padding:14px; border-top:4px solid {cor}; {border_style}
                        box-shadow:0 2px 8px rgba(0,0,0,0.06); font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
                <div style="position:absolute; top:-10px; left:-8px; background:{cor}; color:white; 
                            font-size:10px; font-weight:700; width:20px; height:20px; border-radius:50%; 
                            display:flex; align-items:center; justify-content:center;">{i+1}</div>
                <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                    <span style="font-size:24px;">{icone}</span>
                    <div style="text-align:right;">
                        <div style="font-size:12px; color:#1e293b; font-weight:600;">{data_fmt}</div>
                        <div style="font-size:10px; color:#64748b;">{hora_fmt}</div>
                    </div>
                </div>
                <div style="font-weight:600; font-size:13px; color:{cor}; padding:8px; 
                            background:{cor}15; border-radius:8px; word-wrap:break-word;">
                    {para_valor}
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px; padding-top:8px; border-top:1px solid #f1f5f9;">
                    <span style="font-size:10px; color:#64748b;">👤 {str(evento.get('autor', 'Sistema'))[:12]}</span>
                    <span style="font-size:10px; background:#f1f5f9; padding:3px 6px; border-radius:6px; font-weight:600;">⏱️ {duracao}</span>
                </div>
                {badges_html}
            </div>
            {arrow}
            '''
        
        html_completo = f'''
        <style>
            .timeline-v2::-webkit-scrollbar {{ height: 8px; }}
            .timeline-v2::-webkit-scrollbar-track {{ background: #e2e8f0; border-radius: 4px; }}
            .timeline-v2::-webkit-scrollbar-thumb {{ background: #94a3b8; border-radius: 4px; }}
        </style>
        <div class="timeline-v2" style="overflow-x:auto; padding:15px 10px; background:#f8fafc; border-radius:12px; border:1px solid #e2e8f0;">
            <div style="display:flex; align-items:stretch; gap:8px; width:max-content;">
                {cards_html}
            </div>
        </div>
        <p style="font-size:11px; color:#94a3b8; text-align:center; margin:10px 0;">⬅️ Arraste para ver histórico | 📍 Status atual ➡️</p>
        <script>
            setTimeout(function() {{
                var el = document.querySelector('.timeline-v2');
                if (el) el.scrollLeft = el.scrollWidth;
            }}, 100);
        </script>
        '''
        
        components.html(html_completo, height=300, scrolling=False)
