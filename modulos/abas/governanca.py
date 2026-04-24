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


def aba_governanca(df: pd.DataFrame):
    """Aba de Governança de Dados."""
    st.markdown("### 📋 Governança de Dados")
    st.caption("Monitore o preenchimento dos campos obrigatórios para garantir métricas confiáveis")
    
    gov = calcular_metricas_governanca(df)
    
    media_preenchimento = (gov['sp']['pct'] + gov['bugs']['pct'] + gov['complexidade']['pct'] + gov['qa']['pct']) / 4
    
    # Alerta geral
    with st.expander("📊 Status Geral da Governança", expanded=False):
        if media_preenchimento < 50:
            st.markdown("""
            <div class="alert-critical">
                <b>🚨 ATENÇÃO: Qualidade dos dados comprometida!</b>
                <p>Muitos campos obrigatórios não estão preenchidos. Isso impacta diretamente nas métricas e decisões.</p>
            </div>
            """, unsafe_allow_html=True)
        elif media_preenchimento < 80:
            st.markdown("""
            <div class="alert-warning">
                <b>⚠️ Oportunidade de melhoria nos dados</b>
                <p>Alguns campos precisam de atenção para melhorar a qualidade das métricas.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-success">
                <b>✅ Dados em boa qualidade!</b>
                <p>Os campos obrigatórios estão bem preenchidos.</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.metric("Média de Preenchimento", f"{media_preenchimento:.0f}%")
    
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
