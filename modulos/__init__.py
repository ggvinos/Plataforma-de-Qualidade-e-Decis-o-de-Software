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

from modulos.auth import (
    verificar_login,
    fazer_login,
    fazer_logout,
    mostrar_tela_login,
    mostrar_tela_loading,
    validar_email_corporativo,
    extrair_nome_usuario,
    get_cookie_manager,
)

from modulos.jira_api import (
    buscar_dados_jira_cached,
    buscar_card_especifico,
    extrair_historico_transicoes,
    extrair_texto_adf,
    gerar_icone_tabler,
    gerar_icone_tabler_html,
    gerar_badge_status,
    obter_icone_evento,
    obter_icone_status,
)

from modulos.calculos import (
    calcular_fator_k,
    classificar_maturidade,
    calcular_ddp,
    calcular_fpy,
    calcular_lead_time,
    analisar_dev_detalhado,
    filtrar_qas_principais,
    calcular_concentracao_conhecimento,
    gerar_recomendacoes_rodizio,
    calcular_concentracao_pessoa,
    calcular_metricas_governanca,
    calcular_metricas_qa,
    calcular_metricas_produto,
    calcular_health_score,
    calcular_metricas_dev,
    calcular_metricas_backlog,
    processar_issue_unica,
    processar_issues,
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
    # auth
    'verificar_login',
    'fazer_login',
    'fazer_logout',
    'mostrar_tela_login',
    'mostrar_tela_loading',
    'validar_email_corporativo',
    'extrair_nome_usuario',
    'get_cookie_manager',
    # jira_api
    'buscar_dados_jira_cached',
    'buscar_card_especifico',
    'extrair_historico_transicoes',
    'extrair_texto_adf',
    'gerar_icone_tabler',
    'gerar_icone_tabler_html',
    'gerar_badge_status',
    'obter_icone_evento',
    'obter_icone_status',
    # calculos (Phase 4)
    'calcular_fator_k',
    'classificar_maturidade',
    'calcular_ddp',
    'calcular_fpy',
    'calcular_lead_time',
    'analisar_dev_detalhado',
    'filtrar_qas_principais',
    'calcular_concentracao_conhecimento',
    'gerar_recomendacoes_rodizio',
    'calcular_concentracao_pessoa',
    'calcular_metricas_governanca',
    'calcular_metricas_qa',
    'calcular_metricas_produto',
    'calcular_health_score',
    'calcular_metricas_dev',
    'calcular_metricas_backlog',
    'processar_issue_unica',
    'processar_issues',
]

