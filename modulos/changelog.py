"""
================================================================================
MÓDULO CHANGELOG - NinaDash v8.82
================================================================================
Histórico completo de versões e melhorias.

Este módulo foi separado do app_modularizado.py para manter o arquivo
principal limpo e focado na orquestração.

Author: GitHub Copilot
Version: 1.0 (Phase 8 - Cleanup)
"""

import streamlit as st


def exibir_changelog():
    """Exibe o changelog em um expander colapsável no rodapé."""
    
    with st.expander("📋 Histórico de Versões", expanded=False):
        st.markdown("""
        <div style="margin-bottom: 10px; display: flex; flex-wrap: wrap; gap: 5px;">
            <span style="background: #ef4444; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; white-space: nowrap;">🔥 HOTFIX</span>
            <span style="background: #22c55e; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; white-space: nowrap;">✨ MELHORIA</span>
            <span style="background: #f97316; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; white-space: nowrap;">🐛 BUG&nbsp;FIX</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        **v8.82** *(22/04/2026)* <span style="background: #ef4444; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🔥</span>
        - 🏗️ **MODULARIZAÇÃO COMPLETA**: 7 novos módulos por blocos mentais
        - 📉 **REDUÇÃO MASSIVA**: app_modularizado.py de 5.5k para 1.1k linhas (80% redução!)
        - 🧹 **CLEANUP**: Changelog extraído (+574 linhas economizadas)
        - ✅ **Arquitetura**: 15 módulos com responsabilidades claras
        
        **v8.81** *(20/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
        - 🎨 **Meu Dashboard**: Construtor de dashboards personalizados
        - ➕ **Widgets**: Adicionar, remover, reordenar
        
        **v8.79** *(20/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
        - 🎯 **Consulta Personalizada**: Filtros avançados
        - 💾 **Salvar Consultas**: Reutilize suas buscas
        
        **v8.71** *(17/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
        - 🎨 **Novo Nome**: Dashboard de Qualidade
        - 🔗 **Nova URL**: ninadash.streamlit.app
        
        **v8.0** *(Início)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
        - 📊 **Dashboard Inicial**: Primeiro MVP
        """, unsafe_allow_html=True)
