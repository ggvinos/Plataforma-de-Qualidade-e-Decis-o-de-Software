"""
🔐 CONFIRMATION CALL AUTH - Autenticação com API JWT

Integração com API do ConfirmationCall usando Basic Auth para obtenção de JWT.
Gerencia estado de autenticação em session_state + COOKIES para persistência.

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
import time
import extra_streamlit_components as stx

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

# Ordem de tentativa dos ambientes (mais provável primeiro)
ORDEM_AMBIENTES = ["Produção", "Homologação", "Desenvolvimento"]

TIMEOUT_SEGUNDOS = 5  # Timeout menor para tentar mais rápido

# Configuração de Cookies para persistência
COOKIE_AUTH_NAME = "ninadash_jwt_auth"
COOKIE_EXPIRY_DAYS = 30


# ==============================================================================
# GERENCIADOR DE COOKIES (SINGLETON)
# ==============================================================================

@st.cache_resource(show_spinner=False)
def get_cookie_manager():
    """Retorna instância única do CookieManager."""
    return stx.CookieManager(key="ninadash_jwt_cookie_manager")


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
        usuario: Nome de usuário (pode ser nome.sobrenome ou nome.sobrenome@confirmationcall.com.br)
        senha: Senha do usuário
        ambiente: "Desenvolvimento", "Homologação" ou "Produção"
    
    Returns:
        (sucesso: bool, token_jwt: Optional[str], mensagem: str)
    """
    
    if ambiente not in ENDPOINTS:
        return False, None, f"Ambiente inválido. Escolha entre: {', '.join(ENDPOINTS.keys())}"
    
    if not usuario or not senha:
        return False, None, "Usuário e senha são obrigatórios"
    
    # Se o usuário não tiver domínio, adiciona @confirmationcall.com.br
    if "@" not in usuario:
        usuario = f"{usuario}@confirmationcall.com.br"
    
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


def autenticar_automatico(usuario: str, senha: str) -> Tuple[bool, Optional[str], str, str]:
    """
    Tenta autenticar em todos os ambientes automaticamente.
    Ordem: Produção → Homologação → Desenvolvimento
    
    Args:
        usuario: Nome de usuário
        senha: Senha do usuário
    
    Returns:
        (sucesso: bool, token_jwt: Optional[str], mensagem: str, ambiente: str)
    """
    if not usuario or not senha:
        return False, None, "Usuário e senha são obrigatórios", ""
    
    erros = []
    credenciais_invalidas_count = 0
    
    for ambiente in ORDEM_AMBIENTES:
        sucesso, token, mensagem = autenticar_com_confirmation_call(usuario, senha, ambiente)
        
        if sucesso:
            return True, token, f"✅ Autenticado com sucesso!", ambiente
        
        # Conta quantos ambientes retornaram credenciais inválidas
        if "Credenciais inválidas" in mensagem or "401" in mensagem:
            credenciais_invalidas_count += 1
        
        # Guarda o erro para mostrar depois se nenhum funcionar
        erros.append(f"{ambiente}: {mensagem}")
    
    # Se TODOS os ambientes retornaram credenciais inválidas, é senha errada
    if credenciais_invalidas_count == len(ORDEM_AMBIENTES):
        return False, None, "❌ Usuário ou senha incorretos", ""
    
    # Nenhum ambiente funcionou (mistura de erros)
    return False, None, "❌ Não foi possível conectar aos servidores.\nTente novamente mais tarde.", ""


# ==============================================================================
# GERENCIAMENTO DE STATE + COOKIES
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
    if "cookie_checked" not in st.session_state:
        st.session_state.cookie_checked = False


def restaurar_sessao_do_cookie() -> bool:
    """
    Tenta restaurar a sessão a partir do cookie salvo.
    Retorna True se conseguiu restaurar, False caso contrário.
    """
    try:
        cookie_manager = get_cookie_manager()
        auth_data = cookie_manager.get(COOKIE_AUTH_NAME)
        
        if auth_data:
            # Parse dos dados do cookie (formato JSON)
            if isinstance(auth_data, str):
                data = json.loads(auth_data)
            else:
                data = auth_data
            
            # Verifica se tem os campos necessários
            if data.get("token") and data.get("usuario"):
                # Restaura sessão
                st.session_state.authenticated = True
                st.session_state.jwt_token = data["token"]
                st.session_state.usuario_autenticado = data["usuario"]
                st.session_state.ambiente_autenticacao = data.get("ambiente", "Produção")
                st.session_state.tempo_autenticacao = datetime.now()
                
                # Para compatibilidade com auth.py
                st.session_state.logged_in = True
                st.session_state.user_email = data["usuario"]
                nome_usuario = data["usuario"].split("@")[0].replace(".", " ").title()
                st.session_state.user_nome = nome_usuario
                
                return True
    except Exception as e:
        # Se falhar ao ler cookie, ignora silenciosamente
        pass
    
    return False


def verificar_autenticacao() -> bool:
    """
    Verifica se o usuário está autenticado.
    Ordem de verificação:
    1. session_state (mais rápido, já autenticado nesta sessão)
    2. Cookie (persistência entre recarregamentos/abas)
    
    Retorna True se autenticado, False caso contrário.
    """
    # 1. Primeiro verifica session_state (mais rápido)
    if st.session_state.get("authenticated", False) and st.session_state.get("jwt_token"):
        return True
    
    # 2. Tenta restaurar do cookie (apenas uma vez por sessão para evitar loop)
    if not st.session_state.get("cookie_checked", False):
        st.session_state.cookie_checked = True
        if restaurar_sessao_do_cookie():
            return True
    
    return False


def salvar_autenticacao(usuario: str, token: str, ambiente: str, lembrar: bool = True):
    """
    Salva informações de autenticação no session_state e opcionalmente no cookie.
    
    Args:
        usuario: Email do usuário
        token: Token JWT
        ambiente: Ambiente de autenticação
        lembrar: Se True, salva cookie para persistência (padrão: True)
    """
    # Salva em session_state
    st.session_state.authenticated = True
    st.session_state.jwt_token = token
    st.session_state.usuario_autenticado = usuario
    st.session_state.ambiente_autenticacao = ambiente
    st.session_state.tempo_autenticacao = datetime.now()
    
    # Para compatibilidade com auth.py
    st.session_state.logged_in = True
    st.session_state.user_email = usuario
    nome_usuario = usuario.split("@")[0].replace(".", " ").title() if "@" in usuario else usuario
    st.session_state.user_nome = nome_usuario
    
    # Salva no cookie para persistência
    if lembrar:
        try:
            cookie_manager = get_cookie_manager()
            auth_data = json.dumps({
                "token": token,
                "usuario": usuario,
                "ambiente": ambiente,
                "salvo_em": datetime.now().isoformat()
            })
            cookie_manager.set(
                COOKIE_AUTH_NAME,
                auth_data,
                expires_at=datetime.now() + timedelta(days=COOKIE_EXPIRY_DAYS)
            )
        except Exception as e:
            # Se falhar ao salvar cookie, login ainda funciona na sessão
            pass


def limpar_autenticacao():
    """Limpa informações de autenticação do session_state e cookie."""
    # Limpa session_state
    st.session_state.authenticated = False
    st.session_state.jwt_token = None
    st.session_state.usuario_autenticado = None
    st.session_state.ambiente_autenticacao = None
    st.session_state.tempo_autenticacao = None
    st.session_state.cookie_checked = False
    
    # Limpa compatibilidade com auth.py
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.user_nome = None
    
    # Remove cookie
    try:
        cookie_manager = get_cookie_manager()
        cookie_manager.delete(COOKIE_AUTH_NAME)
    except Exception:
        pass


# ==============================================================================
# INTERFACE DE LOGIN
# ==============================================================================

def tela_login():
    """
    Exibe tela de login com campos para usuário e senha.
    Tenta autenticar automaticamente em todos os ambientes (Produção → Homolog → Dev).
    """
    st.set_page_config(
        page_title="NinaDash - Autenticação",
        page_icon="favicon.svg",
        layout="centered",
    )
    
    inicializar_session_state()
    
    # CSS para esconder "Press enter to submit" e estilizar
    st.markdown("""
    <style>
        .nina-red { color: #AF0C37; font-weight: 700; }
        .login-header { text-align: center; margin-bottom: 20px; }
        .login-header svg { max-width: 100px; height: auto; }
        .login-title { text-align: center; font-size: 1.2em; color: #333; margin: 0 0 5px 0; font-weight: 600; }
        .login-subtitle { text-align: center; color: #666; font-size: 0.85em; margin: 0 0 20px 0; }
        .login-footer { text-align: center; color: #999; font-size: 0.75em; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)
    
    # Centraliza conteúdo usando colunas
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo
        st.markdown(f"<div class='login-header'>{NINA_LOGO_SVG}</div>", unsafe_allow_html=True)
        
        # Título e subtítulo
        st.markdown("<p class='login-title'>Bem-vindo ao <span class='nina-red'>NinaDash</span></p>", unsafe_allow_html=True)
        st.markdown("<p class='login-subtitle'>Plataforma de Qualidade e Decisão de Software</p>", unsafe_allow_html=True)
        
        # Container fixo para mensagens - usa info como placeholder para manter tamanho
        msg_container = st.empty()
        msg_container.info("Insira suas credenciais para acessar o dashboard")
        
        # Form simplificado - sem seleção de ambiente
        with st.form("login_form", clear_on_submit=False):
            usuario = st.text_input("Usuário", placeholder="nome.sobrenome")
            senha = st.text_input("Senha", type="password", placeholder="Sua senha")
            lembrar = st.checkbox("Lembrar do acesso", value=True, help="Mantém você conectado por 30 dias")
            
            submitted = st.form_submit_button("Entrar", use_container_width=True, type="primary")
        
        # Processa fora do form para usar o container fixo
        if submitted:
            if not usuario or not senha:
                msg_container.error("Preencha todos os campos!")
            else:
                msg_container.info("🔄 Conectando...")
                
                # Tenta autenticar automaticamente em todos os ambientes
                sucesso, token, mensagem, ambiente = autenticar_automatico(usuario, senha)
                
                if sucesso:
                    email = usuario if "@" in usuario else f"{usuario}@confirmationcall.com.br"
                    salvar_autenticacao(email, token, ambiente, lembrar=lembrar)
                    msg_container.success("Bem-vindo!")
                    st.rerun()
                else:
                    msg_container.error(mensagem)
        
        # Footer
        st.markdown("<div class='login-footer'>© 2026 Nina Tecnologia • Dashboard de Inteligência de QA</div>", unsafe_allow_html=True)


# ==============================================================================
# COMPONENTE LOGOUT (SIDEBAR)
# ==============================================================================

def renderizar_logout_sidebar():
    """
    Renderiza informações do usuário em um card e botão de logout na sidebar.
    Deve ser chamado dentro de st.sidebar.
    """
    if not verificar_autenticacao():
        return
    
    usuario_email = st.session_state.get("usuario_autenticado", "usuário@confirmationcall.com.br")
    
    # Extrai apenas o nome (primeira parte antes do @)
    nome_usuario = usuario_email.split("@")[0].replace(".", " ").title() if "@" in usuario_email else usuario_email
    
    # Tenta obter o perfil do usuário
    perfil_info = st.session_state.get("user_permissions", {})
    perfil = perfil_info.get("perfil", "Pendente") if perfil_info else "Pendente"
    is_mapeado = perfil_info.get("is_mapeado", False) if perfil_info else False
    
    # Define cor e texto do perfil
    if not is_mapeado or perfil == "NAO_MAPEADO":
        perfil_texto = "⏳ Perfil Pendente"
        perfil_cor = "#f59e0b"
    elif perfil == "ADMIN":
        perfil_texto = f"👑 {perfil}"
        perfil_cor = "#ef4444"
    else:
        perfil_texto = perfil
        perfil_cor = "#22c55e"
    
    # Card com informações do usuário (UX: similar a aba de perfil)
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #f8f9fa 0%, #f0f1f5 100%);
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 16px;
        margin: 10px 0;
    ">
        <div style="font-size: 12px; color: #666; margin-bottom: 8px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Usuário</div>
        <div style="font-size: 16px; color: #AF0C37; font-weight: 600; margin-bottom: 4px;">{nome_usuario}</div>
        <div style="font-size: 12px; color: #999; word-break: break-all; margin-bottom: 8px;">{usuario_email}</div>
        <div style="font-size: 11px; color: {perfil_cor}; font-weight: 600; padding: 3px 8px; background: {perfil_cor}15; border-radius: 4px; display: inline-block;">{perfil_texto}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Botão de sair
    if st.button("Sair", use_container_width=True, key="btn_logout_sidebar"):
        limpar_autenticacao()
        st.rerun()


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
