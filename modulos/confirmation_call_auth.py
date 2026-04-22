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

# Import do SVG da logo
try:
    from modulos.config import NINA_LOGO_SVG
except ImportError:
    # Fallback se não conseguir importar
    NINA_LOGO_SVG = ''

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
        
        # Debug: Log resposta para troubleshooting
        debug_info = {
            "status": response.status_code,
            "headers": dict(response.headers),
            "content_length": len(response.content),
            "content_type": response.headers.get("content-type", "unknown"),
        }
        
        # Trata resposta baseado no status code
        if response.status_code == 200:
            token = None
            
            try:
                # Tenta fazer parse JSON (formato 1)
                data = response.json()
                token = data.get("token") or data.get("access_token")
                
                if token:
                    return True, token, f"✅ Autenticado com sucesso no ambiente {ambiente}"
            
            except json.JSONDecodeError:
                # Não é JSON, tenta como token puro (formato 2)
                pass
            
            # Se não encontrou token em JSON, tenta considerar resposta como token puro
            if not token:
                resposta_texto = response.text.strip() if response.text else ""
                
                # Valida se parece com JWT (tem 3 partes separadas por pontos)
                if resposta_texto and resposta_texto.count(".") == 2:
                    # Parece ser um JWT válido
                    token = resposta_texto
                    return True, token, f"✅ Autenticado com sucesso no ambiente {ambiente}"
                
                # Nenhum formato válido
                return False, None, f"❌ Servidor retornou sucesso (200) mas resposta não contém token válido.\nResposta: {resposta_texto[:200]}\n\nContate o administrador do ConfirmationCall."
        
        elif response.status_code == 401:
            return False, None, "❌ Credenciais inválidas (Usuário ou Senha incorretos)"
        
        elif response.status_code == 403:
            return False, None, "❌ Acesso negado. Usuário não tem permissão para este ambiente"
        
        elif response.status_code == 404:
            # Tenta extrair mais info
            try:
                erro_msg = response.json().get("message", "")
                if erro_msg:
                    return False, None, f"❌ Endpoint não encontrado no ambiente {ambiente}\nDetalhes: {erro_msg}"
            except:
                pass
            return False, None, f"❌ Endpoint não encontrado no ambiente {ambiente}\nURL: {endpoint}"
        
        elif response.status_code == 500:
            try:
                erro_msg = response.json().get("message", "Erro interno no servidor")
                return False, None, f"❌ Erro no servidor ConfirmationCall ({ambiente}): {erro_msg}"
            except:
                return False, None, f"❌ Erro no servidor do ConfirmationCall ({ambiente})"
        
        else:
            # Tenta extrair info de erro se disponível
            try:
                erro_response = response.json()
                erro_msg = erro_response.get("message") or erro_response.get("error") or str(erro_response)
                return False, None, f"❌ Erro na autenticação (Status {response.status_code}): {erro_msg}"
            except:
                return False, None, f"❌ Erro na autenticação (Status: {response.status_code})\nVerifique se as credenciais estão corretas."
    
    except requests.exceptions.Timeout:
        return False, None, f"⏱️ Timeout ao conectar com {ambiente} (excedeu {TIMEOUT_SEGUNDOS}s)\nVerifique sua conexão de internet."
    
    except requests.exceptions.ConnectionError as e:
        return False, None, f"🌐 Erro de conexão com o servidor {ambiente}.\nDetalhes: {str(e)}\nVerifique sua internet ou se há firewall bloqueando."
    
    except requests.exceptions.RequestException as e:
        return False, None, f"❌ Erro na requisição: {str(e)}"
    
    except json.JSONDecodeError as e:
        return False, None, f"❌ Resposta inválida do servidor (não é JSON válido)\nErro: {str(e)}"
    
    except Exception as e:
        return False, None, f"❌ Erro inesperado: {str(e)}\nTipo: {type(e).__name__}"


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
    Segue o design visual padrão da Nina com logo e favicon.
    """
    st.set_page_config(
        page_title="NinaDash - Autenticação",
        page_icon="favicon.svg",
        layout="centered",
    )
    
    # Inicializa state
    inicializar_session_state()
    
    # CSS customizado para tela de login
    st.markdown("""
    <style>
        /* Centro do conteúdo */
        .login-container {
            margin-top: 60px;
            margin-bottom: 60px;
        }
        
        /* Logo */
        .login-logo {
            text-align: center;
            margin-bottom: 30px;
        }
        
        /* Título */
        .login-title {
            text-align: center;
            color: #AF0C37;
            font-size: 2.2em;
            font-weight: 700;
            margin: 0;
            margin-bottom: 5px;
        }
        
        /* Subtítulo */
        .login-subtitle {
            text-align: center;
            color: #666;
            font-size: 0.95em;
            margin: 5px 0 30px 0;
            font-style: italic;
        }
        
        /* Formulário */
        .login-form {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 30px;
            margin: 20px 0;
        }
        
        /* Footer */
        .login-footer {
            text-align: center;
            color: #999;
            font-size: 0.85em;
            margin-top: 40px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Layout: Centralizado
    col1, col2, col3 = st.columns([1, 2.5, 1])
    
    with col2:
        # ==== LOGO DA NINA ====
        st.markdown(f"""
        <div class='login-logo'>
            {NINA_LOGO_SVG}
        </div>
        """, unsafe_allow_html=True)
        
        # ==== TÍTULO E SUBTÍTULO ====
        st.markdown("""
        <h1 class='login-title'>NinaDash</h1>
        <p class='login-subtitle'>Transformando dados em decisões</p>
        """, unsafe_allow_html=True)
        
        # Linha divisória
        st.markdown("---")
        
        # ==== FORMULÁRIO DE LOGIN ====
        with st.form("form_login", clear_on_submit=False):
            st.markdown("""
            <h3 style='text-align: center; color: #333; margin-top: 0;'>Autenticação ConfirmationCall</h3>
            """, unsafe_allow_html=True)
            
            st.markdown("")  # Espaço
            
            usuario = st.text_input(
                "👤 Usuário",
                placeholder="nome.sobrenome@confirmationcall.com.br",
                help="Seu usuário ConfirmationCall"
            )
            
            senha = st.text_input(
                "🔑 Senha",
                type="password",
                placeholder="Sua senha",
                help="Sua senha do ConfirmationCall"
            )
            
            ambiente = st.selectbox(
                "🌐 Ambiente",
                options=list(ENDPOINTS.keys()),
                index=2,  # Produção por padrão
                help="Selecione o ambiente para autenticação"
            )
            
            st.markdown("")  # Espaço
            
            # Botões
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                btn_login = st.form_submit_button(
                    "🚀 Entrar",
                    use_container_width=True,
                    type="primary"
                )
            
            with col_btn2:
                st.form_submit_button(
                    "❓ Ajuda",
                    use_container_width=True,
                    disabled=True
                )
            
            # ==== PROCESSA LOGIN ====
            if btn_login:
                if not usuario or not senha:
                    st.error("❌ Por favor, preencha todos os campos!")
                else:
                    with st.spinner(f"🔄 Autenticando no {ambiente}..."):
                        sucesso, token, mensagem = autenticar_com_confirmation_call(
                            usuario, senha, ambiente
                        )
                    
                    if sucesso:
                        # Login bem-sucedido
                        salvar_autenticacao(usuario, token, ambiente)
                        st.success(mensagem)
                        st.success(f"✨ Bem-vindo, {usuario}!")
                        st.balloons()
                        st.rerun()
                    else:
                        # Erro no login
                        st.error(mensagem)
                        
                        # Expander com troubleshooting
                        with st.expander("🔧 Informações de Troubleshooting"):
                            st.markdown("""
                            ### Dicas de Resolução:
                            
                            **❌ "Credenciais inválidas (401)":**
                            - Verifique se usuário e senha estão corretos
                            - Confirme que não há espaços extras
                            - Tente novamente ou contacte admin
                            
                            **❌ "Acesso negado (403)":**
                            - Seu usuário não tem permissão neste ambiente
                            - Contacte administrador do ConfirmationCall
                            
                            **❌ "Timeout ou Erro de Conexão":**
                            - Verifique sua conexão de internet
                            - Tente desativar VPN/proxy
                            - Tente outro ambiente
                            
                            **🔍 Para Mais Informações:**
                            Execute no terminal:
                            """)
                            st.code("python3 test_cc_dev.py", language="bash")
        
        # Linha divisória
        st.markdown("---")
        
        # ==== INFORMAÇÕES DE SEGURANÇA ====
        with st.expander("🛡️ Informações de Segurança"):
            st.markdown("""
            #### ✅ Proteção Implementada
            - **HTTPS/SSL**: Todas as comunicações criptografadas
            - **Basic Auth**: Credenciais enviadas com segurança
            - **JWT Token**: Autorização sem armazenar senha
            - **Session State**: Token armazenado apenas na sessão
            - **Sem Persistência**: Nenhum dado salvo localmente
            
            #### 🌐 Ambientes Disponíveis
            - **Desenvolvimento**: Testes e integração
            - **Homologação**: Pré-produção
            - **Produção**: Ambiente de produção
            """)
        
        # ==== FOOTER ====
        st.markdown("<div class='login-footer'>© 2026 Nina Tecnologia<br/>Dashboard de Inteligência de QA</div>", unsafe_allow_html=True)


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
