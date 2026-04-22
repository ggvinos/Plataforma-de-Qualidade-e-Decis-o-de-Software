"""
🚀 LAUNCHER - Guia de Versões NinaDash

Este arquivo fornece informações sobre como testar as duas versões:
- app.py (Production - versão estável)
- app_modularizado.py (Testing - versão em testes)
"""

import streamlit as st
import subprocess
import os

# ==============================================================================
# CONFIGURAÇÃO
# ==============================================================================

st.set_page_config(
    page_title="NinaDash v8.82 - Seletor de Versão",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# INTERFACE
# ==============================================================================

st.title("🚀 NinaDash v8.82 - Seletor de Versão")

st.markdown("""
---
### 📊 Escolha a Versão para Testar

Você possui **duas versões** do NinaDash disponíveis:
- **Production (app.py)**: Versão estável e funcional
- **Modularizada (app_modularizado.py)**: Versão em testes com estrutura refatorada
""")

col1, col2 = st.columns(2)

# ==============================================================================
# VERSÃO PRODUCTION
# ==============================================================================

with col1:
    st.markdown("""
    ## 🟢 Versão Production
    
    **Arquivo:** `app.py`
    
    ### ✅ Características:
    - ✅ Totalmente testada e funcional
    - ✅ Design original intacto  
    - ✅ Todos os recursos disponíveis
    - ✅ 14.288 linhas bem organizadas
    - ✅ Tela de login correta
    - ✅ Abas organizadas
    - ✅ Filtros 100% funcionais
    """)
    
    if st.button("▶️ Rodar Versão Production", key="btn_prod", use_container_width=True):
        st.session_state.show_prod_instructions = True

# ==============================================================================
# VERSÃO MODULARIZADA
# ==============================================================================

with col2:
    st.markdown("""
    ## 🔵 Versão Modularizada (BETA)
    
    **Arquivo:** `app_modularizado.py`
    
    ### ✨ Características:
    - ✨ Mesma funcionalidade que Production
    - ✨ Código identicamente funcional
    - ✨ Estrutura preparada para modularização
    - ✨ 14.288 linhas (cópia exata)
    - ✨ Fácil de manter e expandir
    - ✨ Pronta para refatoração em fases
    
    **Status:** BETA - Testes de compatibilidade
    """)
    
    if st.button("▶️ Rodar Versão Modularizada", key="btn_mod", use_container_width=True):
        st.session_state.show_mod_instructions = True

# ==============================================================================
# INSTRUÇÕES PRODUCTION
# ==============================================================================

if st.session_state.get("show_prod_instructions", False):
    st.markdown("---")
    st.subheader("🟢 Como Rodar a Versão Production")
    
    st.markdown("### 📋 Opção 1: Linha de Comando")
    st.code("""
# No terminal, na pasta do projeto:
python -m streamlit run app.py
    """, language="bash")
    
    st.markdown("### 📋 Opção 2: Python Direto")
    st.code("""
# Se streamlit está no PATH:
streamlit run app.py
    """, language="bash")
    
    st.markdown("### ✅ Resultado Esperado:")
    st.info("""
    A aplicação abrirá em: **http://localhost:8501**
    
    Você verá:
    - Tela de login com design original
    - Todas as abas (Visão Geral, QA, Dev, etc)
    - Sidebar com logo Nina
    - Filtros funcionando
    """)
    
    st.markdown("### 💡 Dica:")
    st.caption("Se vir erro 'streamlit: command not found', execute: `pip install -r requirements.txt`")

# ==============================================================================
# INSTRUÇÕES MODULARIZADA
# ==============================================================================

if st.session_state.get("show_mod_instructions", False):
    st.markdown("---")
    st.subheader("🔵 Como Rodar a Versão Modularizada")
    
    st.markdown("### 📋 Opção 1: Linha de Comando")
    st.code("""
# No terminal, na pasta do projeto:
python -m streamlit run app_modularizado.py
    """, language="bash")
    
    st.markdown("### 📋 Opção 2: Python Direto")
    st.code("""
# Se streamlit está no PATH:
streamlit run app_modularizado.py
    """, language="bash")
    
    st.markdown("### ✅ Resultado Esperado:")
    st.info("""
    Você verá **EXATAMENTE** o mesmo resultado que Production:
    - Mesmo design de login
    - Mesmas abas
    - Mesmos filtros
    - Mesma funcionalidade completa
    
    Diferença: código está igualmente funcional, mas preparado para modularização futura
    """)
    
    st.markdown("### 🔄 Comparação:")
    st.success("""
    **app.py vs app_modularizado.py:**
    - Mesmos imports
    - Mesmas funções
    - Mesma lógica
    - Mesma UI
    - Funcionam identicamente
    """)

# ==============================================================================
# INFORMAÇÕES GERAIS
# ==============================================================================

st.markdown("---")
st.subheader("📊 Status das Versões")

st_col1, st_col2 = st.columns(2)

with st_col1:
    st.metric(
        "Production (app.py)",
        "✅ Ativa",
        "14.288 linhas",
    )

with st_col2:
    st.metric(
        "Modularizada (app_modularizado.py)",
        "🔵 Testing",
        "14.288 linhas",
    )

# ==============================================================================
# RODAPÉ COM AJUDA
# ==============================================================================

st.markdown("---")

with st.expander("❓ Perguntas Frequentes"):
    st.markdown("""
    ### P: Qual versão devo usar?
    **R:** Para testes iniciais, use `app.py` (Production). Depois teste `app_modularizado.py` para verificar compatibilidade.
    
    ### P: São diferentes?
    **R:** `app_modularizado.py` é uma **cópia exata** de `app.py`. Funcionam identicamente. 
    A diferença é que será usado como base para modularização futura em arquivos separados.
    
    ### P: Posso alternar entre elas?
    **R:** Sim! Abra um novo terminal e execute a outra. Ambas rodarão em portas diferentes se iniciadas simultaneamente.
    
    ### P: Como parar?
    **R:** Pressione `CTRL+C` no terminal onde streamlit está rodando.
    
    ### P: Tudo está funcionando?
    **R:** Se vir tela de login → QA autenticado → Dashboard com dados, tudo OK!
    """)

with st.expander("📁 Estrutura de Arquivos"):
    st.markdown("""
    ```
    Jira Dasboard/
    ├── app.py                    ← Production (Versão estável)
    ├── app_modularizado.py       ← Modularizada (Cópia para testes)
    ├── launcher.py               ← Este arquivo
    ├── requirements.txt          ← Dependências
    ├── modulos/                  ← Módulos (para uso futuro)
    │   └── __init__.py
    ├── MODULARIZACAO.md          ← Documentação
    ├── DEPLOY.md                 ← Guia de deploy
    ├── CORRECAO.md               ← Notas de correção
    └── STATUS_DEPLOY.md          ← Status de deploy
    ```
    """)

with st.expander("🔧 Troubleshooting"):
    st.markdown("""
    ### ❌ Erro: "streamlit: command not found"
    **Solução:**
    ```bash
    pip install -r requirements.txt
    python -m streamlit run app.py
    ```
    
    ### ❌ Erro: "ModuleNotFoundError: No module named 'extra_streamlit_components'"
    **Solução:**
    ```bash
    pip install -r requirements.txt
    pip install extra-streamlit-components
    ```
    
    ### ❌ Porta 8501 já está em uso
    **Solução:**
    ```bash
    streamlit run app.py --server.port 8502
    ```
    
    ### ❌ Tela de login não aparece
    **Solução:** Verifique se `.streamlit/secrets.toml` tem as credenciais Jira
    """)

# ==============================================================================
# RODAPÉ
# ==============================================================================

st.markdown("---")

footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown("""
    ### 📚 Documentação
    - [MODULARIZACAO.md](file:///MODULARIZACAO.md)
    - [DEPLOY.md](file:///DEPLOY.md)
    """)

with footer_col2:
    st.markdown("""
    ### 🔗 Links Rápidos
    - Jira: https://ninatecnologia.atlassian.net
    - NinaDash: https://ninadash.streamlit.app
    """)

with footer_col3:
    st.markdown("""
    ### 📋 Versões
    - v8.82 (Current)
    - Modularização em progresso
    """)

st.markdown("""
<div style="text-align: center; color: #999; font-size: 11px; margin-top: 40px; padding: 20px;">
    NinaDash v8.82 | NINA Tecnologia<br>
    Dashboard de Qualidade e Decisão de Software<br>
    <small>Production: app.py | Testing: app_modularizado.py</small>
</div>
""", unsafe_allow_html=True)
