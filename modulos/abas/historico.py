"""
================================================================================
ABA HISTÓRICO - NinaDash v8.82
================================================================================
Histórico e Tendências.

Funcionalidades:
- Insights automáticos
- Evolução do Fator K
- Evolução de qualidade (FPY/DDP)
- Evolução de bugs
- Health Score histórico
- Throughput e Lead Time

Author: GitHub Copilot
Version: 1.0 (Phase 6)
"""

import streamlit as st
import pandas as pd

from modulos.helpers import gerar_dados_tendencia
from modulos.widgets import mostrar_tooltip
from modulos.graficos import (
    criar_grafico_tendencia_fator_k,
    criar_grafico_tendencia_qualidade,
    criar_grafico_tendencia_bugs,
    criar_grafico_tendencia_health,
    criar_grafico_throughput,
    criar_grafico_lead_time,
    criar_grafico_reprovacao,
)


def aba_historico(df: pd.DataFrame):
    """Aba de Histórico/Tendências - ENRIQUECIDA."""
    st.markdown("### 📈 Histórico e Tendências")
    st.caption("Visualize a evolução das métricas ao longo das sprints. *Dados demonstrativos para visualização do potencial da ferramenta.*")
    
    df_tendencia = gerar_dados_tendencia()
    
    # Helper para mini-cards harmonizados
    def mini_card(valor, titulo, subtitulo, cor="#6b7280"):
        bg = f"{cor}10" if cor != "#6b7280" else "white"
        border = f"{cor}40" if cor != "#6b7280" else "#e5e7eb"
        return f'<div style="background: {bg}; border: 2px solid {border}; border-radius: 12px; padding: 16px 12px; text-align: center; height: 95px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);"><div style="font-size: 28px; font-weight: 700; color: {cor}; line-height: 1.1;">{valor}</div><div style="font-size: 12px; font-weight: 600; color: #374151; margin-top: 4px;">{titulo}</div><div style="font-size: 10px; color: #6b7280;">{subtitulo}</div></div>'
    
    # ===== INSIGHTS AUTOMÁTICOS =====
    st.markdown("##### 💡 Insights Automáticos")
    
    ultimo_fk = df_tendencia['fator_k'].iloc[-1]
    primeiro_fk = df_tendencia['fator_k'].iloc[0]
    variacao_fk = ((ultimo_fk - primeiro_fk) / primeiro_fk) * 100 if primeiro_fk > 0 else 0
    ultimo_fpy = df_tendencia['fpy'].iloc[-1]
    ultimo_lead = df_tendencia['lead_time_medio'].iloc[-1]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if variacao_fk > 0:
            cor = "#22c55e"
            status = f"📈 +{variacao_fk:.1f}%"
        else:
            cor = "#f59e0b"
            status = f"📉 {variacao_fk:.1f}%"
        st.markdown(mini_card(f"{ultimo_fk:.1f}", "🏆 Fator K", status, cor), unsafe_allow_html=True)
    
    with col2:
        if ultimo_fpy >= 80:
            cor = "#22c55e"
            status = "✅ Acima meta"
        else:
            cor = "#f59e0b"
            status = f"⚠️ {80 - ultimo_fpy:.1f}% abaixo"
        st.markdown(mini_card(f"{ultimo_fpy:.0f}%", "📊 FPY", status, cor), unsafe_allow_html=True)
    
    with col3:
        if ultimo_lead <= 7:
            cor = "#22c55e"
            status = "⚡ Saudável"
        else:
            cor = "#ef4444"
            status = f"⏱️ Meta: ≤7d"
        st.markdown(mini_card(f"{ultimo_lead:.1f}d", "⏱️ Lead Time", status, cor), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    
    # Gráficos de evolução
    with st.expander("🏆 Evolução do Fator K (Maturidade)", expanded=False):
        fig = criar_grafico_tendencia_fator_k(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
        mostrar_tooltip("fator_k")
    
    with st.expander("📊 Evolução de Qualidade (FPY e DDP)", expanded=False):
        fig = criar_grafico_tendencia_qualidade(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            mostrar_tooltip("fpy")
        with col2:
            mostrar_tooltip("ddp")
    
    with st.expander("🐛 Evolução de Bugs", expanded=False):
        fig = criar_grafico_tendencia_bugs(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("🏥 Evolução do Health Score", expanded=False):
        fig = criar_grafico_tendencia_health(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
        mostrar_tooltip("health_score")
    
    with st.expander("📦 Throughput (Vazão de Entrega)", expanded=False):
        fig = criar_grafico_throughput(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
        mostrar_tooltip("throughput")
    
    with st.expander("⏱️ Lead Time Médio", expanded=False):
        fig = criar_grafico_lead_time(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
        mostrar_tooltip("lead_time")
    
    with st.expander("❌ Taxa de Reprovação", expanded=False):
        fig = criar_grafico_reprovacao(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabela de dados históricos
    with st.expander("📋 Dados Históricos Completos", expanded=False):
        st.dataframe(df_tendencia, hide_index=True, use_container_width=True)
