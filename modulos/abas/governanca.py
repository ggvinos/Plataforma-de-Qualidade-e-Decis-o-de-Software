"""
================================================================================
ABA GOVERNANÇA - NinaDash v8.82
================================================================================
Governança de Dados.

Funcionalidades:
- Status geral da governança
- Monitoramento de campos obrigatórios
- Exportação de listas para cobrança

Author: GitHub Copilot
Version: 1.0 (Phase 6)
"""

import streamlit as st
import pandas as pd

from modulos.calculos import calcular_metricas_governanca
from modulos.widgets import mostrar_lista_tickets_completa
from modulos.helpers import obter_contexto_periodo


def aba_governanca(df: pd.DataFrame):
    """Aba de Governança de Dados."""
    ctx = obter_contexto_periodo()
    
    st.markdown("### 📋 Governança de Dados")
    st.caption(f"Monitore o preenchimento dos campos obrigatórios • **{ctx['emoji']} {ctx['titulo']}**")
    
    gov = calcular_metricas_governanca(df)
    
    media_preenchimento = (gov['sp']['pct'] + gov['bugs']['pct'] + gov['complexidade']['pct'] + gov['qa']['pct']) / 4
    
    # Helper para mini-cards harmonizados
    def mini_card(valor, titulo, subtitulo, cor="#6b7280"):
        bg = f"{cor}10" if cor != "#6b7280" else "white"
        border = f"{cor}40" if cor != "#6b7280" else "#e5e7eb"
        return f'<div style="background: {bg}; border: 2px solid {border}; border-radius: 12px; padding: 16px 12px; text-align: center; height: 95px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);"><div style="font-size: 28px; font-weight: 700; color: {cor}; line-height: 1.1;">{valor}</div><div style="font-size: 12px; font-weight: 600; color: #374151; margin-top: 4px;">{titulo}</div><div style="font-size: 10px; color: #6b7280;">{subtitulo}</div></div>'
    
    def cor_status_inv(valor, verde, amarelo):
        if valor >= verde:
            return "#22c55e"
        elif valor >= amarelo:
            return "#f59e0b"
        return "#ef4444"
    
    # ===== INDICADORES DE GOVERNANÇA =====
    st.markdown("##### 📊 Status da Governança")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        cor = cor_status_inv(media_preenchimento, 80, 50)
        status = "✅ Bom" if media_preenchimento >= 80 else "⚠️ Atenção" if media_preenchimento >= 50 else "🚨 Crítico"
        st.markdown(mini_card(f"{media_preenchimento:.0f}%", "📊 Média Geral", status, cor), unsafe_allow_html=True)
    
    with col2:
        cor = cor_status_inv(gov['sp']['pct'], 80, 50)
        st.markdown(mini_card(f"{gov['sp']['pct']:.0f}%", "📐 Story Points", f"{gov['sp']['preenchido']}/{gov['sp']['total']}", cor), unsafe_allow_html=True)
    
    with col3:
        cor = cor_status_inv(gov['bugs']['pct'], 80, 50)
        st.markdown(mini_card(f"{gov['bugs']['pct']:.0f}%", "🐛 Bugs", f"{gov['bugs']['preenchido']}/{gov['bugs']['total']}", cor), unsafe_allow_html=True)
    
    with col4:
        cor = cor_status_inv(gov['complexidade']['pct'], 80, 50)
        st.markdown(mini_card(f"{gov['complexidade']['pct']:.0f}%", "🎯 Complexidade", f"{gov['complexidade']['preenchido']}/{gov['complexidade']['total']}", cor), unsafe_allow_html=True)
    
    with col5:
        cor = cor_status_inv(gov['qa']['pct'], 80, 50)
        st.markdown(mini_card(f"{gov['qa']['pct']:.0f}%", "👤 QA Resp.", f"{gov['qa']['preenchido']}/{gov['qa']['total']}", cor), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    
    # Campos obrigatórios - COM LISTAGEM COMPLETA
    campos = [
        ("Story Points", gov['sp'], "Obrigatório para todos os cards (exceto Hotfix que assume 2 SP por padrão)"),
        ("Bugs Encontrados", gov['bugs'], "Preencher após validação - essencial para métricas de qualidade"),
        ("Complexidade de Teste", gov['complexidade'], "Meta futura - ajuda a balancear carga de QA"),
        ("QA Responsável", gov['qa'], "Obrigatório - indica quem está validando"),
    ]
    
    for nome, dados, obs in campos:
        with st.expander(f"📌 {nome} - {dados['pct']:.0f}% preenchido ({dados['preenchido']}/{dados['total']})", expanded=False):
            cor = '#22c55e' if dados['pct'] >= 80 else '#f59e0b' if dados['pct'] >= 50 else '#ef4444'
            
            st.markdown(f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width: {dados['pct']}%; background: {cor};">
                    {dados['pct']:.0f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.caption(obs)
            
            # Listagem COMPLETA dos faltando
            if dados['faltando']:
                mostrar_lista_tickets_completa(dados['faltando'], f"Cards sem {nome}")
            else:
                st.success(f"✅ Todos os cards têm {nome} preenchido!")
    
    # Exportar lista para cobrança
    with st.expander("📥 Exportar Listas para Cobrança", expanded=False):
        if gov['sp']['faltando']:
            df_export = pd.DataFrame(gov['sp']['faltando'])
            csv = df_export.to_csv(index=False)
            st.download_button("📥 Baixar cards sem Story Points", csv, "cards_sem_sp.csv", "text/csv")
        
        if gov['bugs']['faltando']:
            df_export = pd.DataFrame(gov['bugs']['faltando'])
            csv = df_export.to_csv(index=False)
            st.download_button("📥 Baixar cards sem Bugs preenchido", csv, "cards_sem_bugs.csv", "text/csv")
