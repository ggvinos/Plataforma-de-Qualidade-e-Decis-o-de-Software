"""
🔐 CONFIRMATION CALL AUTH v2 - Autenticação Simplificada

Versão simplificada e robusta da autenticação com ConfirmationCall.
Foco em: FUNCIONAR SEMPRE, sem dependência de cookies complexos.
"""

import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
from typing import Optional, Tuple
import json

# Import do SVG da logo
try:
    from modulos.config import NINA_LOGO_SVG
except ImportError:
    NINA_LOGO_SVG = ''

# ==============================================================================
# CONFIGURAÇÃO
# ==============================================================================

ENDPOINTS = {
    "Produção": "https://api.confirmationcall.com.br/api/user/loginjwt",
    "Homologação": "https://api.homolog.confirmationcall.com.br/api/user/loginjwt",
    "Desenvolvimento": "https://api.develop.confirmationcall.com.br/api/user/loginjwt",
}

ORDEM_AMBIENTES = ["Produção", "Homologação", "Desenvolvimento"]
TIMEOUT_SEGUNDOS = 8  # Timeout maior para garantir resposta


# ==============================================================================
# AUTENTICAÇÃO COM API
# ==============================================================================

def _autenticar_ambiente(usuario: str, senha: str, ambiente: str) -> Tuple[bool, Optional[str], str]:
    """Tenta autenticar em um ambiente específico."""
    
    if ambiente not in ENDPOINTS:
        return False, None, "Ambiente inválido"
    
    # Adiciona domínio se necessário
    if "@" not in usuario:
        usuario = f"{usuario}@confirmationcall.com.br"
    
    try:
        response = requests.post(
            ENDPOINTS[ambiente],
            auth=HTTPBasicAuth(usuario, senha),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=TIMEOUT_SEGUNDOS,
            verify=True
        )
        
        if response.status_code == 200:
            # Tenta extrair token
            try:
                data = response.json()
                token = data.get("token") or data.get("access_token")
                if token:
                    return True, token, f"✅ Autenticado em {ambiente}"
            except:
                pass
            
            # Tenta como texto puro (JWT)
            texto = response.text.strip()
            if texto and texto.count(".") == 2:
                return True, texto, f"✅ Autenticado em {ambiente}"
            
            return False, None, "Resposta inválida do servidor"
        
        elif response.status_code == 401:
            return False, None, "CREDENCIAIS_INVALIDAS"
        
        elif response.status_code == 403:
            return False, None, "ACESSO_NEGADO"
        
        else:
            return False, None, f"Erro {response.status_code}"
    
    except requests.exceptions.Timeout:
        return False, None, "TIMEOUT"
    
    except requests.exceptions.ConnectionError:
        return False, None, "SEM_CONEXAO"
    
    except Exception as e:
        return False, None, f"Erro: {str(e)}"


def autenticar_usuario(usuario: str, senha: str) -> Tuple[bool, str, str]:
    """
    Tenta autenticar em todos os ambientes automaticamente.
    
    Returns:
        (sucesso: bool, mensagem: str, ambiente: str)
    """
    if not usuario or not senha:
        return False, "❌ Preencha usuário e senha", ""
    
    # Conta erros por tipo
    credenciais_invalidas = 0
    sem_conexao = 0
    ultimo_erro = ""
    
    for ambiente in ORDEM_AMBIENTES:
        sucesso, token, msg = _autenticar_ambiente(usuario, senha, ambiente)
        
        if sucesso:
            # SUCESSO! Salva na sessão
            email = usuario if "@" in usuario else f"{usuario}@confirmationcall.com.br"
            st.session_state.authenticated = True
            st.session_state.jwt_token = token
            st.session_state.usuario_autenticado = email
            st.session_state.ambiente_autenticacao = ambiente
            st.session_state.tempo_autenticacao = datetime.now()
            
            # Compatibilidade
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.session_state.user_nome = email.split("@")[0].replace(".", " ").title()
            
            return True, f"✅ Bem-vindo!", ambiente
        
        # Conta tipo de erro
        if msg == "CREDENCIAIS_INVALIDAS":
            credenciais_invalidas += 1
        elif msg in ["TIMEOUT", "SEM_CONEXAO"]:
            sem_conexao += 1
        
        ultimo_erro = msg
    
    # Análise dos erros
    if credenciais_invalidas == len(ORDEM_AMBIENTES):
        return False, "❌ Usuário ou senha incorretos", ""
    
    if sem_conexao == len(ORDEM_AMBIENTES):
        return False, "❌ Sem conexão com o servidor. Verifique sua internet.", ""
    
    # Erro misto
    return False, f"❌ Não foi possível autenticar. Tente novamente.", ""


# ==============================================================================
# VERIFICAÇÃO DE AUTENTICAÇÃO
# ==============================================================================

def esta_autenticado() -> bool:
    """Verifica se o usuário está autenticado (apenas session_state)."""
    return (
        st.session_state.get("authenticated", False) and 
        st.session_state.get("jwt_token") is not None
    )


def fazer_logout():
    """Limpa a sessão do usuário."""
    keys_to_clear = [
        "authenticated", "jwt_token", "usuario_autenticado", 
        "ambiente_autenticacao", "tempo_autenticacao",
        "logged_in", "user_email", "user_nome",
        "user_permissions", "acesso_registrado"
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


# ==============================================================================
# INTERFACE DE LOGIN
# ==============================================================================

def tela_login():
    """Exibe tela de login simples e funcional."""
    
    st.markdown("""
    <style>
        .nina-red { color: #AF0C37; font-weight: 700; }
        .login-box { 
            max-width: 400px; 
            margin: 50px auto; 
            padding: 30px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }
        .login-title { text-align: center; font-size: 1.5em; margin-bottom: 5px; }
        .login-subtitle { text-align: center; color: #666; font-size: 0.9em; margin-bottom: 25px; }
        .login-footer { text-align: center; color: #999; font-size: 0.75em; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)
    
    # Centraliza
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo Nina
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 20px;">
            {NINA_LOGO_SVG}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<p class='login-title'>Bem-vindo ao <span class='nina-red'>NinaDash</span></p>", unsafe_allow_html=True)
        st.markdown("<p class='login-subtitle'>Plataforma de Qualidade e Decisão de Software</p>", unsafe_allow_html=True)
        
        # Mensagem de status
        msg_placeholder = st.empty()
        
        # Formulário
        with st.form("login_form_v2", clear_on_submit=False):
            usuario = st.text_input(
                "👤 Usuário", 
                placeholder="nome.sobrenome",
                help="Seu login do ConfirmationCall (sem @confirmationcall.com.br)"
            )
            
            senha = st.text_input(
                "🔒 Senha", 
                type="password", 
                placeholder="Sua senha"
            )
            
            col_btn1, col_btn2 = st.columns([3, 1])
            with col_btn1:
                submitted = st.form_submit_button("🚀 Entrar", use_container_width=True, type="primary")
        
        # Processa login
        if submitted:
            if not usuario or not senha:
                msg_placeholder.error("⚠️ Preencha usuário e senha!")
            else:
                with st.spinner("🔄 Autenticando..."):
                    sucesso, mensagem, ambiente = autenticar_usuario(usuario, senha)
                
                if sucesso:
                    msg_placeholder.success(mensagem)
                    st.balloons()
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    msg_placeholder.error(mensagem)
        
        # Footer
        st.markdown("<div class='login-footer'>© 2026 Nina Tecnologia</div>", unsafe_allow_html=True)


# ==============================================================================
# MIDDLEWARE PRINCIPAL
# ==============================================================================

def verificar_e_bloquear():
    """
    Middleware simples: se não autenticado, mostra login e para.
    Deve ser chamado APÓS st.set_page_config().
    """
    if not esta_autenticado():
        tela_login()
        st.stop()


# ==============================================================================
# COMPONENTE SIDEBAR
# ==============================================================================

def renderizar_logout_sidebar():
    """Renderiza info do usuário e botão logout na sidebar."""
    
    if not esta_autenticado():
        return
    
    email = st.session_state.get("usuario_autenticado", "")
    nome = email.split("@")[0].replace(".", " ").title() if "@" in email else email
    ambiente = st.session_state.get("ambiente_autenticacao", "")
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #f8f9fa 0%, #f0f1f5 100%);
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 16px;
        margin: 10px 0;
    ">
        <div style="font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 0.5px;">Conectado</div>
        <div style="font-size: 15px; color: #AF0C37; font-weight: 600; margin: 4px 0;">{nome}</div>
        <div style="font-size: 11px; color: #999;">{email}</div>
        <div style="font-size: 10px; color: #bbb; margin-top: 4px;">🌐 {ambiente}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Sair", use_container_width=True, key="btn_logout_v2"):
        fazer_logout()
        st.rerun()


# ==============================================================================
# UTILITÁRIOS
# ==============================================================================

def obter_usuario_autenticado() -> Optional[str]:
    """Retorna o email do usuário autenticado."""
    return st.session_state.get("usuario_autenticado")


def obter_token_jwt() -> Optional[str]:
    """Retorna o token JWT se autenticado."""
    if esta_autenticado():
        return st.session_state.get("jwt_token")
    return None
