"""
NinaDash v8.82 - Dashboard Modularizado de Inteligência e Métricas de QA

Este arquivo é o orquestrador principal que importa todos os módulos
e configura a aplicação Streamlit.
"""

import streamlit as st
from config import NINA_LOGO_SVG
from auth import verificar_login, mostrar_tela_loading, mostrar_tela_login, fazer_logout
from integrations import buscar_dados_jira_cached
from domain import processar_issues

# ==============================================================================
# INICIALIZAÇÃO DE SESSION STATE
# ==============================================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.user_nome = None

# ==============================================================================
# FLUXO DE AUTENTICAÇÃO
# ==============================================================================

if not verificar_login():
    mostrar_tela_login()
    st.stop()

# ==============================================================================
# APLICAÇÃO PRINCIPAL
# ==============================================================================

def main():
    """Função principal da aplicação."""
    
    # Sidebar com info do usuário
    with st.sidebar:
        st.markdown(f"### {NINA_LOGO_SVG}", unsafe_allow_html=True)
        st.markdown("---")
        
        st.markdown(f"**👤 {st.session_state.user_nome}**")
        st.markdown(f"`{st.session_state.user_email}`")
        
        if st.button("🚪 Logout"):
            fazer_logout()
            st.rerun()
    
    # Título da aplicação
    st.title("📊 NinaDash v8.82")
    st.markdown("Inteligência de QA para Decisão")
    
    # Menu de navegação
    pagina = st.sidebar.radio(
        "📋 Selecione a aba",
        [
            "Visão Geral",
            "QA", 
            "Dev",
            "Governança",
            "Produto",
            "Histórico",
            "Liderança",
            "Meu Dashboard",
            "Sobre"
        ]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Status:** ✅ Conectado")
    st.sidebar.markdown("*Versão 8.82 - Modularizada*")
    
    # Renderizar página selecionada
    if pagina == "Visão Geral":
        st.info("📄 Página 'Visão Geral' - Em desenvolvimento")
    elif pagina == "QA":
        st.info("📄 Página 'QA' - Em desenvolvimento")
    elif pagina == "Dev":
        st.info("📄 Página 'Dev' - Em desenvolvimento")
    elif pagina == "Governança":
        st.info("📄 Página 'Governança' - Em desenvolvimento")
    elif pagina == "Produto":
        st.info("📄 Página 'Produto' - Em desenvolvimento")
    elif pagina == "Histórico":
        st.info("📄 Página 'Histórico' - Em desenvolvimento")
    elif pagina == "Liderança":
        st.info("📄 Página 'Liderança' - Em desenvolvimento")
    elif pagina == "Meu Dashboard":
        st.info("📄 Página 'Meu Dashboard' - Em desenvolvimento")
    elif pagina == "Sobre":
        st.markdown("""
        ## Sobre o NinaDash
        
        **NinaDash** é um dashboard de inteligência operacional para QA, desenvolvido
        para transformar o processo de testes em um sistema baseado em dados.
        
        ### Versão
        - 📦 v8.82 (Modularizada)
        
        ### Módulos
        - `config/` - Configurações globais e constantes
        - `auth/` - Autenticação com cookies
        - `integrations/` - Integração com Jira
        - `domain/` - Lógica de negócio e métricas
        - `ui/` - Interface e componentes (em desenvolvimento)
        - `utils/` - Utilitários gerais
        
        ### Referência
        - **Fator K**: Maturidade do código (SP / Bugs + 1)
        - **DDP**: Defect Detection Percentage
        - **FPY**: First Pass Yield
        - **Health Score**: Saúde da release composta
        """)

if __name__ == "__main__":
    main()
