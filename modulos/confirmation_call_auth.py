"""
🔐 CONFIRMATION CALL AUTH v4 - Autenticação com LocalStorage

Autenticação robusta com ConfirmationCall + persistência via LocalStorage.
Usa JavaScript direto para maior confiabilidade.
"""

import streamlit as st
import streamlit.components.v1 as components
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
from typing import Optional, Tuple
import json
import time
import hashlib
import os

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
TIMEOUT_SEGUNDOS = 8

# LocalStorage config
STORAGE_KEY = "ninadash_session_v4"
SESSION_EXPIRY_DAYS = 30

# Arquivo de sessão local (fallback para servidor próprio)
SESSION_FILE = ".streamlit/session_cache.json"


# ==============================================================================
# PERSISTÊNCIA VIA ARQUIVO LOCAL (para servidor próprio)
# ==============================================================================

def _get_session_file_path():
    """Retorna caminho do arquivo de sessão."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, ".streamlit", "sessions.json")


def _load_sessions() -> dict:
    """Carrega sessões do arquivo."""
    try:
        path = _get_session_file_path()
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
    except:
        pass
    return {}


def _save_sessions(sessions: dict):
    """Salva sessões no arquivo."""
    try:
        path = _get_session_file_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(sessions, f)
    except:
        pass


def _gerar_session_id() -> str:
    """Gera ID único de sessão baseado em timestamp."""
    return hashlib.md5(f"{datetime.now().isoformat()}{os.urandom(8).hex()}".encode()).hexdigest()[:16]


def salvar_sessao_arquivo(email: str, token: str, ambiente: str) -> str:
    """
    Salva sessão em arquivo local e retorna session_id.
    O session_id pode ser passado via query params para restaurar.
    """
    session_id = _gerar_session_id()
    sessions = _load_sessions()
    
    # Limpa sessões expiradas
    agora = datetime.now()
    sessions = {
        sid: data for sid, data in sessions.items()
        if datetime.fromisoformat(data.get("created", "2000-01-01")) + timedelta(days=SESSION_EXPIRY_DAYS) > agora
    }
    
    # Salva nova sessão
    sessions[session_id] = {
        "email": email,
        "token": token,
        "ambiente": ambiente,
        "created": agora.isoformat()
    }
    
    _save_sessions(sessions)
    return session_id


def restaurar_sessao_arquivo(session_id: str) -> Optional[dict]:
    """Restaura sessão do arquivo usando session_id."""
    if not session_id:
        return None
    
    sessions = _load_sessions()
    data = sessions.get(session_id)
    
    if data:
        # Verifica expiração
        created = datetime.fromisoformat(data.get("created", "2000-01-01"))
        if datetime.now() - created < timedelta(days=SESSION_EXPIRY_DAYS):
            return data
        else:
            # Remove sessão expirada
            del sessions[session_id]
            _save_sessions(sessions)
    
    return None


def limpar_sessao_arquivo(session_id: str):
    """Remove sessão do arquivo."""
    if not session_id:
        return
    
    sessions = _load_sessions()
    if session_id in sessions:
        del sessions[session_id]
        _save_sessions(sessions)


# ==============================================================================
# FUNÇÕES AUXILIARES DE URL
# ==============================================================================

def _ler_session_id_url() -> Optional[str]:
    """Lê session_id da URL (query params)."""
    try:
        params = st.query_params
        return params.get("sid")
    except:
        return None


def _definir_session_id_url(session_id: str):
    """Define session_id na URL."""
    try:
        st.query_params["sid"] = session_id
    except:
        pass


def _limpar_session_id_url():
    """Remove session_id da URL."""
    try:
        if "sid" in st.query_params:
            del st.query_params["sid"]
    except:
        pass


# ==============================================================================
# COMPONENTE DE LEITURA DE LOCALSTORAGE
# ==============================================================================

def _criar_leitor_localstorage():
    """
    Cria componente que lê localStorage e redireciona com session_id na URL.
    Usa iframe com parent.location para redirecionar a página principal.
    """
    # Se já tem sid na URL, não precisa ler localStorage
    if _ler_session_id_url():
        return False
    
    # Injeta script que lê localStorage e redireciona a página PRINCIPAL (parent)
    components.html(f"""
    <script>
        (function() {{
            try {{
                const sid = localStorage.getItem('{STORAGE_KEY}');
                const currentUrl = window.parent.location.href;
                
                if (sid && !currentUrl.includes('sid=')) {{
                    // Adiciona sid na URL e redireciona a página principal
                    const url = new URL(currentUrl);
                    url.searchParams.set('sid', sid);
                    window.parent.location.replace(url.toString());
                }}
            }} catch(e) {{
                // Se falhar com parent, tenta top
                try {{
                    const sid = localStorage.getItem('{STORAGE_KEY}');
                    const currentUrl = window.top.location.href;
                    
                    if (sid && !currentUrl.includes('sid=')) {{
                        const url = new URL(currentUrl);
                        url.searchParams.set('sid', sid);
                        window.top.location.replace(url.toString());
                    }}
                }} catch(e2) {{
                    console.log('Não foi possível redirecionar:', e2);
                }}
            }}
        }})();
    </script>
    """, height=0)
    
    return True


def _injetar_script_salvar(session_id: str):
    """Injeta JavaScript para salvar session_id no localStorage."""
    components.html(f"""
    <script>
        try {{
            localStorage.setItem('{STORAGE_KEY}', '{session_id}');
            console.log('Sessão salva no localStorage:', '{session_id}');
        }} catch(e) {{
            console.error('Erro ao salvar sessão:', e);
        }}
    </script>
    """, height=0)


def _injetar_script_limpar():
    """Injeta JavaScript para limpar localStorage."""
    components.html(f"""
    <script>
        try {{
            localStorage.removeItem('{STORAGE_KEY}');
            console.log('Sessão removida do localStorage');
        }} catch(e) {{
            console.error('Erro ao limpar sessão:', e);
        }}
    </script>
    """, height=0)


# ==============================================================================
# COMPATIBILIDADE - COOKIE MANAGER (PARA CÓDIGO LEGADO)
# ==============================================================================

def get_cookie_manager():
    """
    Retorna None - função mantida para compatibilidade.
    A v4 usa LocalStorage + arquivo, não CookieManager.
    """
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


def autenticar_usuario(usuario: str, senha: str, lembrar: bool = True) -> Tuple[bool, str, str]:
    """
    Tenta autenticar em todos os ambientes automaticamente.
    
    Args:
        usuario: Email ou login do usuário
        senha: Senha do usuário
        lembrar: Se True, salva sessão em cookie para persistência
    
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
            
            # Salva sessão persistente se "lembrar" está marcado
            if lembrar:
                session_id = salvar_sessao_arquivo(email, token, ambiente)
                st.session_state.session_id = session_id
                # Injeta JavaScript para salvar no localStorage
                _injetar_script_salvar(session_id)
                # Também coloca na URL
                _definir_session_id_url(session_id)
            
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
    """Limpa a sessão do usuário (session_state + arquivo + localStorage)."""
    # Limpa sessão do arquivo
    session_id = st.session_state.get("session_id")
    if session_id:
        limpar_sessao_arquivo(session_id)
    
    # Limpa localStorage via JavaScript
    _injetar_script_limpar()
    
    # Limpa URL
    _limpar_session_id_url()
    
    # Limpa session_state
    keys_to_clear = [
        "authenticated", "jwt_token", "usuario_autenticado", 
        "ambiente_autenticacao", "tempo_autenticacao",
        "logged_in", "user_email", "user_nome",
        "user_permissions", "acesso_registrado",
        "session_id", "session_restored"
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
    
    # IMPORTANTE: Script para verificar localStorage e restaurar sessão automaticamente
    # Este script roda na página principal (não em iframe) e consegue redirecionar
    # Se encontrar sessão salva, adiciona ?sid=xxx na URL e recarrega
    components.html(f"""
    <script>
        (function() {{
            // Só executa se não tem sid na URL
            if (!window.location.search.includes('sid=')) {{
                const sid = localStorage.getItem('{STORAGE_KEY}');
                if (sid) {{
                    // Encontrou sessão - adiciona sid na URL e recarrega
                    const url = new URL(window.location.href);
                    url.searchParams.set('sid', sid);
                    window.location.replace(url.toString());
                }}
            }}
        }})();
    </script>
    """, height=0)
    
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
        msg_container.info("🔑 Use suas credenciais do **ConfirmationCall** para acessar")
        
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
                sucesso, mensagem, ambiente = autenticar_usuario(usuario, senha, lembrar=lembrar)
                
                if sucesso:
                    msg_container.success("✅ Bem-vindo! Redirecionando...")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    msg_container.error(mensagem)
        
        # Footer
        st.markdown("<div class='login-footer'>© 2026 Nina Tecnologia • Dashboard de Inteligência de QA</div>", unsafe_allow_html=True)


# ==============================================================================
# MIDDLEWARE PRINCIPAL
# ==============================================================================

def _restaurar_sessao_de_arquivo() -> bool:
    """
    Tenta restaurar sessão usando session_id da URL.
    Retorna True se conseguiu restaurar.
    """
    # Já autenticado?
    if esta_autenticado():
        return True
    
    # Pega session_id da URL
    session_id = _ler_session_id_url()
    if not session_id:
        return False
    
    # Tenta restaurar do arquivo
    dados = restaurar_sessao_arquivo(session_id)
    if not dados:
        # Session inválida, limpa URL
        _limpar_session_id_url()
        return False
    
    # Restaura sessão!
    email = dados["email"]
    st.session_state.authenticated = True
    st.session_state.jwt_token = dados["token"]
    st.session_state.usuario_autenticado = email
    st.session_state.ambiente_autenticacao = dados["ambiente"]
    st.session_state.tempo_autenticacao = datetime.now()
    st.session_state.session_id = session_id
    
    # Compatibilidade
    st.session_state.logged_in = True
    st.session_state.user_email = email
    st.session_state.user_nome = email.split("@")[0].replace(".", " ").title()
    
    st.session_state.session_restored = True
    return True


def verificar_e_bloquear():
    """
    Middleware de autenticação com persistência via LocalStorage + Arquivo.
    
    Fluxo:
    1. Se já autenticado no session_state → continua
    2. Se tem session_id na URL → tenta restaurar do arquivo
    3. Se não tem session_id → injeta JS para ler localStorage e redirecionar
    4. Se não conseguir → mostra tela de login
    
    Deve ser chamado APÓS st.set_page_config().
    """
    # 1. Já autenticado? Passa direto
    if esta_autenticado():
        return
    
    # 2. Tem session_id na URL? Tenta restaurar
    session_id = _ler_session_id_url()
    if session_id:
        if _restaurar_sessao_de_arquivo():
            # Restaurou com sucesso!
            return
    
    # 3. Não autenticado → mostra login
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
    
    # Card do usuário com múltiplos papéis e animações
    st.markdown(f"""
    <div class="user-card-animated hover-glow" style="
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 10px 12px;
        margin: 0;
        animation: fadeIn 0.3s ease-out;
    ">
        <div style="display: flex; align-items: center; gap: 10px;">
            <div class="avatar-animated" style="
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
