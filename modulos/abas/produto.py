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
from modulos.helpers import criar_card_metrica
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
    
    # KPIs novas métricas Ellen
    with st.expander("🎯 Indicadores de Fluxo da Sprint", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_finalizados = metricas_prod['total_finalizados_mesma_sprint']
            total_done = len(df[df['status_cat'] == 'done'])
            pct = total_finalizados / total_done * 100 if total_done > 0 else 0
            cor = 'green' if pct >= 70 else 'yellow' if pct >= 40 else 'red'
            criar_card_metrica(f"{total_finalizados}", "Iniciados e Finalizados na Sprint", cor, f"{pct:.0f}% dos concluídos")
        
        with col2:
            total_fora = metricas_prod['total_adicionados_fora']
            cor = 'green' if total_fora < 3 else 'yellow' if total_fora < 6 else 'red'
            criar_card_metrica(str(total_fora), "Cards Adicionados Fora do Período", cor, "Adicionados após início da sprint")
        
        with col3:
            total_hotfix = len(df[df['tipo'] == 'HOTFIX'])
            cor = 'green' if total_hotfix < 5 else 'yellow' if total_hotfix < 10 else 'red'
            criar_card_metrica(str(total_hotfix), "Total de Hotfixes", cor)
        
        st.caption("💡 **Dica:** Cards adicionados fora do período comprometem o planejamento da sprint")
    
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
