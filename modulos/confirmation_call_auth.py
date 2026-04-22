"""
🔐 CONFIRMATION CALL AUTH - Autenticação com API JWT

Integração com API do ConfirmationCall usando Basic Auth para obtenção de JWT.
Gerencia estado de autenticação em session_state com persistência em cookies.

Endpoints:
- Develop: https://api.develop.confirmationcall.com.br/api/user/loginjwt
- Homolog: https://api.homolog.confirmationcall.com.br/api/user/loginjwt
- Produção: https://api.confirmationcall.com.br/api/user/loginjwt
"""

import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import json

# ==============================================================================
# CONFIGURAÇÃO
# ==============================================================================

ENDPOINTS = {
    "Desenvolvimento": "https://api.develop.confirmationcall.com.br/api/user/loginjwt",
    "Homologação": "https://api.homolog.confirmationcall.com.br/api/user/loginjwt",
    "Produção": "https://api.confirmationcall.com.br/api/user/loginjwt",
}

TIMEOUT_SEGUNDOS = 10
COOKIE_JWT_NAME = "ninadash_jwt_token"
COOKIE_EXPIRY_DAYS = 30


# ==============================================================================
# AUTENTICAÇÃO COM API CONFIRMATION CALL
# ==============================================================================

def autenticar_com_confirmation_call(
    usuario: str,
    senha: str,
    ambiente: str = "Produção"
) -> Tuple[bool, Optional[str], str]:
    """
    Autentica usuário com a API do ConfirmationCall usando Basic Auth.
    
    Args:
        usuario: Nome de usuário
        senha: Senha do usuário
        ambiente: "Desenvolvimento", "Homologação" ou "Produção"
    
    Returns:
        (sucesso: bool, token_jwt: Optional[str], mensagem: str)
    """
    
    if ambiente not in ENDPOINTS:
        return False, None, f"❌ Ambiente inválido. Escolha entre: {', '.join(ENDPOINTS.keys())}"
    
    if not usuario or not senha:
        return False, None, "❌ Usuário e senha são obrigatórios"
    
    try:
        endpoint = ENDPOINTS[ambiente]
        
        # Configura Basic Auth
        auth = HTTPBasicAuth(usuario, senha)
        
        # Headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        # Realiza requisição
        response = requests.post(
            endpoint,
            auth=auth,
            headers=headers,
            timeout=TIMEOUT_SEGUNDOS,
            verify=True  # Valida certificado SSL
        )
        
        # Trata resposta
        if response.status_code == 200:
            data = response.json()
            token = data.get("token") or data.get("access_token")
            
            if not token:
                return False, None, "❌ Resposta inválida: token não encontrado na resposta"
            
            return True, token, f"✅ Autenticado com sucesso no ambiente {ambiente}"
        
        elif response.status_code == 401:
            return False, None, "❌ Credenciais inválidas (Usuário ou Senha incorretos)"
        
        elif response.status_code == 403:
            return False, None, "❌ Acesso negado. Usuário não tem permissão para este ambiente"
        
        elif response.status_code == 404:
            return False, None, f"❌ Endpoint não encontrado no ambiente {ambiente}"
        
        elif response.status_code == 500:
            return False, None, f"❌ Erro no servidor do ConfirmationCall ({ambiente})"
        
        else:
            return False, None, f"❌ Erro na autenticação (Status: {response.status_code})"
    
    except requests.exceptions.Timeout:
        return False, None, f"⏱️ Timeout ao conectar com {ambiente} (excedeu {TIMEOUT_SEGUNDOS}s)"
    
    except requests.exceptions.ConnectionError:
        return False, None, f"🌐 Erro de conexão com o servidor {ambiente}. Verifique sua internet."
    
    except requests.exceptions.RequestException as e:
        return False, None, f"❌ Erro na requisição: {str(e)}"
    
    except json.JSONDecodeError:
        return False, None, "❌ Resposta inválida do servidor (não é JSON válido)"
    
    except Exception as e:
        return False, None, f"❌ Erro inesperado: {str(e)}"


# ==============================================================================
# GERENCIAMENTO DE STATE
# ==============================================================================

def inicializar_session_state():
    """Inicializa variáveis de autenticação no session_state."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "jwt_token" not in st.session_state:
        st.session_state.jwt_token = None
    if "usuario_autenticado" not in st.session_state:
        st.session_state.usuario_autenticado = None
    if "ambiente_autenticacao" not in st.session_state:
        st.session_state.ambiente_autenticacao = None
    if "tempo_autenticacao" not in st.session_state:
        st.session_state.tempo_autenticacao = None


def verificar_autenticacao() -> bool:
    """
    Verifica se o usuário está autenticado.
    Retorna True se autenticado, False caso contrário.
    """
    return st.session_state.get("authenticated", False) and st.session_state.get("jwt_token")


def salvar_autenticacao(usuario: str, token: str, ambiente: str):
    """Salva informações de autenticação no session_state."""
    st.session_state.authenticated = True
    st.session_state.jwt_token = token
    st.session_state.usuario_autenticado = usuario
    st.session_state.ambiente_autenticacao = ambiente
    st.session_state.tempo_autenticacao = datetime.now()


def limpar_autenticacao():
    """Limpa informações de autenticação do session_state."""
    st.session_state.authenticated = False
    st.session_state.jwt_token = None
    st.session_state.usuario_autenticado = None
    st.session_state.ambiente_autenticacao = None
    st.session_state.tempo_autenticacao = None


# ==============================================================================
# INTERFACE DE LOGIN
# ==============================================================================

def tela_login():
    """
    Exibe tela de login com campos para usuário, senha e seleção de ambiente.
    Integra-se com a API do ConfirmationCall para autenticação.
    """
    st.set_page_config(
        page_title="Nina Dashboard - Login",
        page_icon="🔐",
        layout="centered",
    )
    
    # Inicializa state
    inicializar_session_state()
    
    # Layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center'>
                <h1>🔐 Nina Dashboard</h1>
                <p style='color: #666; margin-bottom: 30px'>
                    Autenticação Segura com ConfirmationCall
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("---")
        
        # Formulário de login
        with st.form("form_login", clear_on_submit=False):
            usuario = st.text_input(
                "👤 Usuário",
                placeholder="Seu usuário ConfirmationCall",
                help="Usuário registrado no ConfirmationCall"
            )
            
            senha = st.text_input(
                "🔑 Senha",
                type="password",
                placeholder="Sua senha",
                help="Senha do ConfirmationCall"
            )
            
            ambiente = st.selectbox(
                "🌐 Ambiente",
                options=list(ENDPOINTS.keys()),
                index=2,  # Produção por padrão
                help="Selecione o ambiente para autenticação"
            )
            
            st.markdown("")  # Espaço
            
            col_login, col_demo = st.columns(2)
            
            with col_login:
                btn_login = st.form_submit_button(
                    "🚀 Entrar",
                    use_container_width=True,
                    type="primary"
                )
            
            with col_demo:
                st.form_submit_button(
                    "ℹ️ Sobre",
                    use_container_width=True,
                    disabled=True
                )
            
            # Processa login
            if btn_login:
                if not usuario or not senha:
                    st.error("❌ Preencha todos os campos!")
                else:
                    with st.spinner(f"🔄 Conectando a {ambiente}..."):
                        sucesso, token, mensagem = autenticar_com_confirmation_call(
                            usuario, senha, ambiente
                        )
                    
                    if sucesso:
                        salvar_autenticacao(usuario, token, ambiente)
                        st.success(mensagem)
                        st.success(f"✨ Bem-vindo, {usuario}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(mensagem)
        
        st.markdown("---")
        
        # Informações de segurança
        with st.expander("🛡️ Informações de Segurança"):
            st.markdown(
                """
                #### Como Funciona?
                1. **Envio Seguro**: Credenciais são enviadas via HTTPS com SSL
                2. **Basic Auth**: Autenticação básica no cabeçalho da requisição
                3. **JWT Token**: Recebimento de token de autorização
                4. **Session State**: Token armazenado apenas na sessão do navegador
                5. **Sem Persistência Local**: Dados não salvos em disco
                
                #### Segurança
                - ✅ Conexão HTTPS criptografada
                - ✅ Validação de certificado SSL
                - ✅ Timeout de conexão (10s)
                - ✅ Sem armazenamento de senha
                - ✅ Token JWT para autorização
                
                #### Ambiente
                - **Desenvolvimento**: Testes e homologação
                - **Homologação**: Pré-produção
                - **Produção**: Ambiente de produção
                """
            )
        
        st.markdown("")
        st.caption("© 2026 Nina Tecnologia - Dashboard de Inteligência QA")


# ==============================================================================
# COMPONENTE LOGOUT (SIDEBAR)
# ==============================================================================

def renderizar_logout_sidebar():
    """
    Renderiza botão de logout na sidebar com informações do usuário autenticado.
    Deve ser chamado dentro de st.sidebar.
    """
    if not verificar_autenticacao():
        return
    
    st.markdown("---")
    
    usuario = st.session_state.get("usuario_autenticado", "Usuário")
    ambiente = st.session_state.get("ambiente_autenticacao", "")
    
    st.markdown(f"### 👤 {usuario}")
    st.caption(f"🌐 {ambiente}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔓 Sair", use_container_width=True):
            limpar_autenticacao()
            st.success("✅ Desconectado com sucesso")
            st.rerun()
    
    with col2:
        if st.button("🔄 Renovar", use_container_width=True, help="Renovar token JWT"):
            st.info("ℹ️ Função de renovação em desenvolvimento")
    
    st.markdown("---")


# ==============================================================================
# MIDDLEWARE DE AUTENTICAÇÃO
# ==============================================================================

def verificar_e_bloquear():
    """
    Middleware que bloqueia acesso ao dashboard se não autenticado.
    Deve ser chamado no início do app.py APÓS st.set_page_config().
    """
    inicializar_session_state()
    
    # Se não autenticado, mostra tela de login e interrompe execução
    if not verificar_autenticacao():
        tela_login()
        st.stop()


# ==============================================================================
# UTILITÁRIOS
# ==============================================================================

def obter_token_jwt() -> Optional[str]:
    """Retorna o token JWT atual, se autenticado."""
    if verificar_autenticacao():
        return st.session_state.jwt_token
    return None


def obter_usuario_autenticado() -> Optional[str]:
    """Retorna o usuário autenticado, se houver."""
    return st.session_state.get("usuario_autenticado")


def tempo_sessao() -> Optional[timedelta]:
    """Retorna o tempo decorrido desde a autenticação."""
    tempo_auth = st.session_state.get("tempo_autenticacao")
    if tempo_auth:
        return datetime.now() - tempo_auth
    return None
