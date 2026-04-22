"""
🎯 NinaDash Modules - Pacote de módulos organizados

Cada módulo tem uma responsabilidade clara:
- config: Constantes e configurações
- utils: Funções auxiliares puras
- calculos: Cálculos de métricas
- auth: Autenticação e cookies
- jira_api: Integração com Jira
- processamento: Processamento de dados
"""

# Import dos módulos principais para facilitar uso
from modulos.config import (
    configure_page,
    JIRA_BASE_URL,
    CUSTOM_FIELDS,
    STATUS_FLOW,
    STATUS_NOMES,
    STATUS_CORES,
    TOOLTIPS,
    REGRAS,
    NINA_LOGO_SVG,
)

from modulos.utils import (
    link_jira,
    traduzir_link,
    calcular_dias_necessarios_validacao,
    avaliar_janela_validacao,
    get_secrets,
    verificar_credenciais,
)

__all__ = [
    # config
    'configure_page',
    'JIRA_BASE_URL',
    'CUSTOM_FIELDS',
    'STATUS_FLOW',
    'STATUS_NOMES',
    'STATUS_CORES',
    'TOOLTIPS',
    'REGRAS',
    'NINA_LOGO_SVG',
    # utils
    'link_jira',
    'traduzir_link',
    'calcular_dias_necessarios_validacao',
    'avaliar_janela_validacao',
    'get_secrets',
    'verificar_credenciais',
]

