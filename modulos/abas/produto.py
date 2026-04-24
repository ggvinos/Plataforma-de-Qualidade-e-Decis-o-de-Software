"""
================================================================================
ABA PRODUTO - NinaDash v8.82
================================================================================
Métricas por Produto (métricas Ellen).

Funcionalidades:
- Indicadores de fluxo da sprint
- Cards adicionados fora do período
- Visualizações por produto
- Resumo por produto

Author: GitHub Copilot
Version: 1.0 (Phase 6)
"""

import streamlit as st
import pandas as pd

from modulos.calculos import calcular_fator_k, calcular_metricas_produto
from modulos.widgets import mostrar_lista_df_completa
from modulos.graficos import (
    criar_grafico_hotfix_por_produto,
    criar_grafico_estagio_por_produto,
)


def aba_produto(df: pd.DataFrame):
    """Aba de métricas por Produto (métricas Ellen)."""
    st.markdown("### 📦 Métricas por Produto")
    st.caption("Visualize métricas segmentadas por produto - inclui métricas de fluxo da sprint")
    
    metricas_prod = calcular_metricas_produto(df)
    
    # Helper para mini-cards harmonizados
    def mini_card(valor, titulo, subtitulo, cor="#6b7280"):
        bg = f"{cor}10" if cor != "#6b7280" else "white"
        border = f"{cor}40" if cor != "#6b7280" else "#e5e7eb"
        return f'<div style="background: {bg}; border: 2px solid {border}; border-radius: 12px; padding: 16px 12px; text-align: center; height: 95px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);"><div style="font-size: 28px; font-weight: 700; color: {cor}; line-height: 1.1;">{valor}</div><div style="font-size: 12px; font-weight: 600; color: #374151; margin-top: 4px;">{titulo}</div><div style="font-size: 10px; color: #6b7280;">{subtitulo}</div></div>'
    
    def cor_status(valor, verde, amarelo):
        if valor < verde:
            return "#22c55e"
        elif valor < amarelo:
            return "#f59e0b"
        return "#ef4444"
    
    def cor_status_inv(valor, verde, amarelo):
        if valor >= verde:
            return "#22c55e"
        elif valor >= amarelo:
            return "#f59e0b"
        return "#ef4444"
    
    # ===== INDICADORES DE FLUXO =====
    st.markdown("##### 🎯 Indicadores de Fluxo da Sprint")
    
    total_finalizados = metricas_prod['total_finalizados_mesma_sprint']
    total_done = len(df[df['status_cat'] == 'done'])
    pct = total_finalizados / total_done * 100 if total_done > 0 else 0
    total_fora = metricas_prod['total_adicionados_fora']
    total_hotfix = len(df[df['tipo'] == 'HOTFIX'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cor = cor_status_inv(pct, 70, 40)
        st.markdown(mini_card(str(total_finalizados), "✅ Iniciados/Finalizados", f"{pct:.0f}% dos done", cor), unsafe_allow_html=True)
    
    with col2:
        cor = cor_status(total_fora, 3, 6)
        st.markdown(mini_card(str(total_fora), "⚠️ Fora do Período", "adicionados depois", cor), unsafe_allow_html=True)
    
    with col3:
        cor = cor_status(total_hotfix, 5, 10)
        st.markdown(mini_card(str(total_hotfix), "🔥 Hotfixes", "emergências", cor), unsafe_allow_html=True)
    
    with col4:
        st.markdown(mini_card(str(total_done), "📦 Concluídos", "total done", "#3b82f6"), unsafe_allow_html=True)
    
    st.caption("💡 Cards adicionados fora do período comprometem o planejamento da sprint")
    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
    
    # Cards adicionados fora do período - COM LISTAGEM COMPLETA
    with st.expander("⚠️ Cards Adicionados Fora do Período", expanded=False):
        if not metricas_prod['adicionados_fora'].empty:
            st.markdown("""
            <div class="alert-warning">
                <b>Estes cards foram adicionados após o início da sprint</b>
                <p>Isso pode indicar escopo não planejado ou emergências.</p>
            </div>
            """, unsafe_allow_html=True)
            mostrar_lista_df_completa(metricas_prod['adicionados_fora'], "Cards Fora do Período")
        else:
            st.success("✅ Nenhum card foi adicionado fora do período!")
    
    # Gráficos
    with st.expander("📊 Visualizações por Produto", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            fig = criar_grafico_hotfix_por_produto(df)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = criar_grafico_estagio_por_produto(df)
            st.plotly_chart(fig, use_container_width=True)
    
    # Tabela resumo por produto
    with st.expander("📋 Resumo por Produto", expanded=False):
        produto_stats = df.groupby('produto').agg({
            'ticket_id': 'count',
            'sp': 'sum',
            'bugs': 'sum',
        }).reset_index()
        produto_stats.columns = ['produto', 'Cards', 'SP', 'Bugs']
        produto_stats['FK'] = produto_stats.apply(lambda x: calcular_fator_k(x['SP'], x['Bugs']), axis=1)
        
        hotfix_count = df[df['tipo'] == 'HOTFIX'].groupby('produto').size().reset_index(name='Hotfixes')
        produto_stats = produto_stats.merge(hotfix_count, on='produto', how='left').fillna(0)
        produto_stats['Hotfixes'] = produto_stats['Hotfixes'].astype(int)
        produto_stats = produto_stats.rename(columns={'produto': 'Produto'})
        
        st.dataframe(produto_stats.sort_values('Cards', ascending=False), hide_index=True, use_container_width=True)
