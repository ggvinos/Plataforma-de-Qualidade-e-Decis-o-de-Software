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

# Para compatibilidade com código existente
try:
    import extra_streamlit_components as stx
    HAS_STX = True
except ImportError:
    HAS_STX = False

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
# COOKIE MANAGER (COMPATIBILIDADE)
# ==============================================================================

def get_cookie_manager():
    """
    Retorna instância do CookieManager para compatibilidade.
    NOTA: A v2 não depende de cookies, mas mantém para código legado.
    """
    if HAS_STX:
        return stx.CookieManager(key="ninadash_compat_cm")
    return None


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
    """
    Exibe tela de login com campos para usuário e senha.
    Tenta autenticar automaticamente em todos os ambientes (Produção → Homolog → Dev).
    """
    
    # CSS para esconder "Press enter to submit" e estilizar
    st.markdown("""
    <style>
        /* Esconde "Press Enter to submit form" */
        .stForm [data-testid="stFormSubmitButton"] + div {
            display: none !important;
        }
        div[data-testid="InputInstructions"] {
            display: none !important;
        }
        .stForm small {
            display: none !important;
        }
        
        /* Estilos do login */
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
        
        # Container fixo para mensagens
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
                sucesso, mensagem, ambiente = autenticar_usuario(usuario, senha)
                
                if sucesso:
                    msg_container.success("✅ Bem-vindo! Redirecionando...")
                    import time
                    time.sleep(0.5)
                    st.rerun()
                else:
                    msg_container.error(mensagem)
        
        # Footer
        st.markdown("<div class='login-footer'>© 2026 Nina Tecnologia • Dashboard de Inteligência de QA</div>", unsafe_allow_html=True)


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

# Cores por tipo de role
ROLE_CORES = {
    "ADMIN": "#AF0C37",
    "LIDERANCA": "#7c3aed", 
    "LIDERANÇA": "#7c3aed",
    "DEV": "#3b82f6",
    "QA": "#22c55e",
    "PRODUTO": "#f59e0b",
    "SUPORTE": "#06b6d4",
    "CS": "#ec4899",
    "IMPLANTAÇÃO": "#8b5cf6",
    "COMERCIAL": "#64748b",
    "VIEWER": "#6b7280",
}


def renderizar_usuario_sidebar(colaborador_data: dict = None, is_mapeado: bool = True):
    """
    Renderiza informações do usuário com múltiplos papéis na sidebar.
    
    Args:
        colaborador_data: Dados completos do colaborador (nome, times, is_admin, etc.)
        is_mapeado: Se o usuário está mapeado no sistema
    """
    if not esta_autenticado():
        return
    
    email = st.session_state.get("usuario_autenticado", "usuário@confirmationcall.com.br")
    nome = email.split("@")[0].replace(".", " ").title() if "@" in email else email
    
    # Usa nome do colaborador se disponível
    if colaborador_data and colaborador_data.get("nome"):
        nome = colaborador_data["nome"]
    
    # Monta lista de roles
    roles = []
    cor_principal = "#6b7280"  # Cor padrão (viewer)
    
    if not is_mapeado:
        roles = ["Sem vínculo"]
        cor_principal = "#ef4444"
    elif colaborador_data:
        # Super Admin tem prioridade
        if colaborador_data.get("is_admin"):
            roles.append("Super Admin")
            cor_principal = "#AF0C37"
        
        # Adiciona times (evita duplicar se já tem admin)
        times = colaborador_data.get("times", [])
        for time in times:
            time_upper = time.upper()
            # Não adiciona LIDERANÇA se já é admin
            if time_upper in ["LIDERANÇA", "LIDERANCA"] and colaborador_data.get("is_admin"):
                continue
            roles.append(time.title())
            # Pega cor do primeiro time se não for admin
            if cor_principal == "#6b7280":
                cor_principal = ROLE_CORES.get(time_upper, "#6b7280")
        
        # Se não tem roles, usa o perfil_acesso
        if not roles:
            perfil = colaborador_data.get("perfil_acesso", "VIEWER")
            roles.append(perfil.title())
            cor_principal = ROLE_CORES.get(perfil.upper(), "#6b7280")
    
    # Formata roles como string
    roles_texto = " • ".join(roles) if roles else "Viewer"
    
    # Ícone baseado no primeiro role
    icone = "👑" if "Super Admin" in roles else "👤"
    
    # Card do usuário com múltiplos papéis
    st.markdown(f"""
    <div style="
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 10px 12px;
        margin: 0;
    ">
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="
                width: 36px; 
                height: 36px; 
                background: linear-gradient(135deg, {cor_principal} 0%, {cor_principal}cc 100%);
                border-radius: 50%; 
                display: flex; 
                align-items: center; 
                justify-content: center;
                color: white;
                font-weight: 600;
                font-size: 14px;
                flex-shrink: 0;
            ">{nome[0].upper()}</div>
            <div style="flex: 1; min-width: 0;">
                <div style="font-size: 13px; color: #1f2937; font-weight: 600; line-height: 1.3; 
                            overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{nome}</div>
                <div style="font-size: 10px; color: #6b7280; margin-top: 2px; line-height: 1.3;
                            overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                    {icone} {roles_texto}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def renderizar_logout_sidebar():
    """
    Renderiza informações do usuário de forma compacta na sidebar.
    DEPRECADO: Use renderizar_usuario_sidebar() com colaborador_data.
    """
    renderizar_usuario_sidebar()


def renderizar_botao_sair():
    """Renderiza apenas o botão de sair - para uso no footer."""
    if not esta_autenticado():
        return
    
    if st.button("🚪 Sair", use_container_width=True, key="btn_logout_footer", type="secondary"):
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
