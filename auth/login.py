"""
Autenticação de usuários com persistência em cookies.
"""

import streamlit as st
import extra_streamlit_components as stx
import os
import time
from datetime import datetime, timedelta
from typing import Dict

COOKIE_AUTH_NAME = "ninadash_auth_v2"
COOKIE_EXPIRY_DAYS = 30

def get_secrets() -> Dict:
    """Carrega credenciais de forma segura."""
    try:
        if "jira" in st.secrets:
            return {
                "email": st.secrets["jira"]["email"],
                "token": st.secrets["jira"]["token"],
            }
    except:
        pass
    return {
        "email": os.getenv("JIRA_API_EMAIL", ""),
        "token": os.getenv("JIRA_API_TOKEN", ""),
    }

def verificar_credenciais() -> bool:
    """Verifica se as credenciais estão configuradas."""
    secrets = get_secrets()
    return bool(secrets["email"] and secrets["token"])

@st.cache_resource(show_spinner=False)
def get_cookie_manager():
    """Retorna instância única do CookieManager."""
    return stx.CookieManager(key="ninadash_cookie_manager")

def verificar_login() -> bool:
    """Verifica se o usuário está logado (session, cookie ou query params)."""
    # 1. Verifica session_state
    if st.session_state.get("logged_in", False) and st.session_state.get("user_email"):
        return True
    
    # 2. Verifica cookie
    try:
        cookie_manager = get_cookie_manager()
        auth_cookie = cookie_manager.get(COOKIE_AUTH_NAME)
        
        if auth_cookie and validar_email_corporativo(auth_cookie):
            st.session_state.logged_in = True
            st.session_state.user_email = auth_cookie
            st.session_state.user_nome = extrair_nome_usuario(auth_cookie)
            return True
    except Exception:
        pass
    
    # 3. Verifica query_params
    auto_login_email = st.query_params.get("_auth", None)
    if auto_login_email and validar_email_corporativo(auto_login_email):
        st.session_state.logged_in = True
        st.session_state.user_email = auto_login_email
        st.session_state.user_nome = extrair_nome_usuario(auto_login_email)
        try:
            cookie_manager = get_cookie_manager()
            cookie_manager.set(COOKIE_AUTH_NAME, auto_login_email, expires_at=datetime.now() + timedelta(days=COOKIE_EXPIRY_DAYS))
        except Exception:
            pass
        if "_auth" in st.query_params:
            del st.query_params["_auth"]
        return True
    
    return False

def validar_email_corporativo(email: str) -> bool:
    """Valida se é um email corporativo autorizado."""
    if not email or "@" not in email:
        return False
    return email.lower().strip().endswith("@confirmationcall.com.br")

def extrair_nome_usuario(email: str) -> str:
    """Extrai o nome do usuário do e-mail corporativo."""
    if not email or "@" not in email:
        return "Usuário"
    
    nome_parte = email.split("@")[0]
    nome_formatado = nome_parte.replace(".", " ").title()
    return nome_formatado

def fazer_login(email: str, lembrar: bool = True) -> bool:
    """Realiza login do usuário com persistência em cookie."""
    email_lower = email.lower().strip()
    
    if validar_email_corporativo(email_lower):
        st.session_state.logged_in = True
        st.session_state.user_email = email_lower
        st.session_state.user_nome = extrair_nome_usuario(email_lower)
        
        if lembrar:
            try:
                cookie_manager = get_cookie_manager()
                cookie_manager.set(
                    COOKIE_AUTH_NAME, 
                    email_lower, 
                    expires_at=datetime.now() + timedelta(days=COOKIE_EXPIRY_DAYS)
                )
            except Exception:
                pass
        
        return True
    
    return False

def fazer_logout():
    """Remove sessão do usuário e limpa cookie."""
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.user_nome = None
    
    try:
        cookie_manager = get_cookie_manager()
        cookie_manager.delete(COOKIE_AUTH_NAME)
    except Exception:
        pass
    
    if 'dados_carregados' in st.session_state:
        del st.session_state.dados_carregados

def mostrar_tela_loading():
    """Tela de carregamento enquanto verifica autenticação."""
    st.markdown("""
    <style>
    .stApp {
        background: #ffffff !important;
    }
    
    header[data-testid="stHeader"],
    [data-testid="stSidebar"],
    #MainMenu, footer {
        display: none !important;
    }
    
    .block-container {
        max-width: 100% !important;
        padding: 0 !important;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(0.95); }
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        padding: 20px;
        background: #ffffff;
    }
    
    .loading-logo {
        animation: pulse 2s ease-in-out infinite;
        margin-bottom: 30px;
    }
    
    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 4px solid rgba(175, 12, 55, 0.2);
        border-top: 4px solid #AF0C37;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 20px;
    }
    
    .loading-text {
        color: #AF0C37;
        font-size: 1.1em;
        font-weight: 500;
    }
    </style>
    
    <div class="loading-container">
        <div class="loading-logo">
            <svg width="100" height="100" viewBox="0 0 187 187" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M173.709 89.2107C172.209 86.6048 169.414 84.838 166.225 84.838C163.036 84.838 160.241 86.5649 158.741 89.1627H151.683C149.465 58.8237 124.495 35 94.0216 35C63.5489 35 38.5862 58.8237 36.3678 89.1627H29.1759C27.6759 86.5649 24.8734 84.798 21.6682 84.798C18.463 84.798 15.6605 86.5806 14.1605 89.2031C13.4184 90.4899 13 92.001 13 93.6C13 95.1987 13.4184 96.7017 14.1605 97.997C15.6605 100.619 18.463 102.306 21.6682 102.306C24.8734 102.306 27.6838 100.435 29.1759 97.8369H36.3678C38.5862 128.168 63.5489 152 94.0216 152C124.495 152 149.465 128.176 151.675 97.8369H158.686C160.178 100.435 162.996 102.354 166.217 102.354C169.438 102.354 172.256 100.611 173.749 97.9648C174.475 96.6856 174.885 95.2148 174.885 93.6319C174.885 92.049 174.451 90.5222 173.701 89.2188L173.709 89.2107ZM111.145 125.554C107.971 131.518 101.758 135.459 94.5981 135.459C87.4374 135.459 81.2248 131.566 78.0509 125.602C77.1666 123.947 78.3667 122.092 80.2219 122.092H108.982C110.837 122.092 112.029 123.891 111.153 125.554H111.145ZM140.528 94.1277C140.528 103.825 132.76 111.691 123.184 111.691H65.4432C55.8675 111.691 48.0991 103.825 48.0991 94.1277V93.7199C48.0991 84.0223 55.8675 76.1557 65.4432 76.1557H123.184C132.76 76.1557 140.528 84.0223 140.528 93.7199V94.1277Z" fill="#AF0C37"/>
            <path d="M76.5809 105.311C82.9686 105.311 88.1466 100.068 88.1466 93.5996C88.1466 87.1312 82.9686 81.8875 76.5809 81.8875C70.1936 81.8875 65.0156 87.1312 65.0156 93.5996C65.0156 100.068 70.1936 105.311 76.5809 105.311Z" fill="#AF0C37"/>
            <path d="M111.437 105.311C117.824 105.311 123.002 100.068 123.002 93.5996C123.002 87.1312 117.824 81.8875 111.437 81.8875C105.049 81.8875 99.8712 87.1312 99.8712 93.5996C99.8712 100.068 105.049 105.311 111.437 105.311Z" fill="#AF0C37"/>
            </svg>
        </div>
        <div class="loading-spinner"></div>
        <p class="loading-text">Carregando NinaDash...</p>
    </div>
    """, unsafe_allow_html=True)
    
    time.sleep(0.3)
    st.rerun()

def mostrar_tela_login():
    """Tela de login simplificada e profissional."""
    st.markdown("""
    <style>
    .stException, [data-testid="stException"] {
        display: none !important;
    }
    
    .stApp {
        background: #F7F7F8 !important;
    }
    
    header[data-testid="stHeader"],
    [data-testid="stSidebar"],
    #MainMenu, footer {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.markdown("<h1 style='text-align:center'>NinaDash</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center'>Inteligência de QA para Decisão</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        email_input = st.text_input("Email corporativo", placeholder="nome.sobrenome@confirmationcall.com.br")
        lembrar = st.checkbox("Lembrar login neste dispositivo", value=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Login", type="primary", use_container_width=True):
                if email_input:
                    if fazer_login(email_input, lembrar):
                        st.success("Login realizado! Recarregando...")
                        st.rerun()
                    else:
                        st.error("❌ Email deve ser @confirmationcall.com.br")
                else:
                    st.error("Preencha o email")
        
        with col_b:
            if st.button("Sair", use_container_width=True):
                fazer_logout()
                st.rerun()
