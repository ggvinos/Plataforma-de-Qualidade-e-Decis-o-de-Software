"""
Exports das funções de autenticação.
"""

from .login import (
    get_secrets,
    verificar_credenciais,
    get_cookie_manager,
    verificar_login,
    validar_email_corporativo,
    extrair_nome_usuario,
    fazer_login,
    fazer_logout,
    mostrar_tela_loading,
    mostrar_tela_login,
    COOKIE_AUTH_NAME,
    COOKIE_EXPIRY_DAYS,
)

__all__ = [
    "get_secrets",
    "verificar_credenciais",
    "get_cookie_manager",
    "verificar_login",
    "validar_email_corporativo",
    "extrair_nome_usuario",
    "fazer_login",
    "fazer_logout",
    "mostrar_tela_loading",
    "mostrar_tela_login",
    "COOKIE_AUTH_NAME",
    "COOKIE_EXPIRY_DAYS",
]
