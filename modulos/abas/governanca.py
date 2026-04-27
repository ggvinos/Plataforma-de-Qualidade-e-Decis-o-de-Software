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
    
    # ===== PIPELINE DE AMBIENTE (DevOps) =====
    st.markdown("##### 🚀 Pipeline de Ambiente (Ciclo de Deploy)")
    
    # Calcula métricas de ambiente
    if 'ambiente' in df.columns:
        total_cards = len(df)
        
        # Cards por ambiente
        df_dev = df[df['ambiente'].str.lower().str.contains('develop', na=False)]
        df_hml = df[df['ambiente'].str.lower().str.contains('homolog', na=False)]
        df_prod = df[df['ambiente'].str.lower().str.contains('produ', na=False)]
        df_sem_ambiente = df[df['ambiente'].isna() | (df['ambiente'] == '')]
        
        n_dev = len(df_dev)
        n_hml = len(df_hml)
        n_prod = len(df_prod)
        n_sem = len(df_sem_ambiente)
        
        pct_preenchido = ((total_cards - n_sem) / total_cards * 100) if total_cards > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            cor = "#16a34a"
            st.markdown(mini_card(str(n_dev), "🟢 Develop", f"{(n_dev/total_cards*100) if total_cards > 0 else 0:.0f}%", cor), unsafe_allow_html=True)
        
        with col2:
            cor = "#d97706"
            extra = "🚀 Próxima Release" if n_hml > 0 else ""
            st.markdown(mini_card(str(n_hml), "🟡 Homologação", extra or f"{(n_hml/total_cards*100) if total_cards > 0 else 0:.0f}%", cor), unsafe_allow_html=True)
        
        with col3:
            cor = "#dc2626"
            st.markdown(mini_card(str(n_prod), "🔴 Produção", f"{(n_prod/total_cards*100) if total_cards > 0 else 0:.0f}%", cor), unsafe_allow_html=True)
        
        with col4:
            cor = cor_status_inv(pct_preenchido, 80, 50)
            st.markdown(mini_card(f"{pct_preenchido:.0f}%", "📊 Preenchido", f"{n_sem} sem ambiente", cor), unsafe_allow_html=True)
        
        # Detalhes por ambiente
        with st.expander("🔍 Detalhes por Ambiente", expanded=False):
            st.markdown("""
            <div style="background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; padding: 12px 16px; margin-bottom: 16px;">
                <div style="font-size: 13px; font-weight: 600; color: #0369a1; margin-bottom: 8px;">📚 Ciclo de Desenvolvimento (DevOps)</div>
                <div style="font-size: 12px; color: #334155; line-height: 1.8;">
                    <b>🟢 Develop</b> — Código em desenvolvimento ou testes internos. Sem impacto em clientes.<br>
                    <b>🟡 Homologação</b> — Validação pelo cliente/PO. Vai subir na próxima release.<br>
                    <b>🔴 Produção</b> — Já está em produção. Impactando clientes diretamente.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if n_hml > 0:
                st.markdown("**🟡 Cards em Homologação (próxima release):**")
                mostrar_lista_tickets_completa(df_hml.to_dict('records'), "Em Homologação")
            
            if n_prod > 0:
                st.markdown("**🔴 Cards em Produção:**")
                mostrar_lista_tickets_completa(df_prod.to_dict('records'), "Em Produção")
            
            if n_sem > 10:
                st.warning(f"⚠️ {n_sem} cards sem ambiente definido. Preencha o campo 'Ambiente Desenvolvido' no Jira.")
    else:
        st.info("📊 Campo 'ambiente' não disponível nos dados. Atualize a página para carregar.")
    
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    
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
        
        if 'ambiente' in df.columns and n_sem > 0:
            df_export = df_sem_ambiente[['ticket_id', 'titulo', 'status', 'desenvolvedor']].copy()
            csv = df_export.to_csv(index=False)
            st.download_button("📥 Baixar cards sem Ambiente", csv, "cards_sem_ambiente.csv", "text/csv")
