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

from modulos.processamento import (
    calcular_periodo_datas,
    filtrar_df_por_consulta,
    aplicar_filtros_widget,
    preparar_df_com_metricas_filtro,
    validar_filtros,
    resetar_filtros,
)

from modulos.abas import (
    aba_clientes,
    aba_visao_geral,
    aba_qa,
    aba_dev,
    aba_governanca,
    aba_produto,
    aba_backlog,
    aba_suporte_implantacao,
    aba_historico,
    aba_lideranca,
    aba_sobre,
    aba_dashboard_personalizado,
)

# Phase 7: Módulos temáticos (blocos mentais)
from modulos.cards import (
    exibir_card_detalhado_v2,
    exibir_detalhes_sd,
    exibir_detalhes_qa,
    exibir_detalhes_pb,
    exibir_timeline_transicoes,
    exibir_cards_vinculados,
    filtrar_e_classificar_comentarios,
    exibir_comentarios,
    filtrar_comentarios_pb,
    exibir_comentarios_pb,
)

from modulos.widgets import (
    mostrar_tooltip,
    renderizar_resultado_consulta,
    renderizar_lista_com_scroll,
    renderizar_widget,
    renderizar_kpi_widget,
    renderizar_grafico_widget,
    renderizar_tabela_widget,
    renderizar_lista_widget,
    mostrar_header_nina,
    mostrar_indicador_atualizacao,
    mostrar_card_ticket,
    mostrar_lista_tickets_completa,
    mostrar_lista_df_completa,
)

from modulos.graficos import (
    criar_grafico_funil_qa,
    criar_grafico_tendencia_fator_k,
    criar_grafico_tendencia_qualidade,
    criar_grafico_tendencia_bugs,
    criar_grafico_tendencia_health,
    criar_grafico_throughput,
    criar_grafico_lead_time,
    criar_grafico_reprovacao,
    criar_grafico_estagio_por_produto,
    criar_grafico_hotfix_por_produto,
    criar_grafico_funil_personalizado,
    criar_grafico_aging_backlog,
    criar_grafico_prioridade_backlog,
    criar_grafico_tipo_backlog,
    criar_grafico_backlog_por_produto,
)

from modulos.helpers import (
    calcular_valor_metrica,
    calcular_dados_grafico,
    calcular_dados_tabela,
    calcular_lista_cards,
    calcular_dados_heatmap,
    calcular_dados_funil,
    gerar_dados_tendencia,
    exportar_para_csv,
    exportar_para_excel,
    aplicar_estilos,
    get_tooltip_help,
    formatar_tempo_relativo,
    criar_card_metrica,
    gerar_html_card_ticket,
)

from modulos.consultas import (
    inicializar_consultas_personalizadas,
    entrar_modo_consulta,
    sair_modo_consulta,
    salvar_consulta,
    listar_consultas_salvas,
    excluir_consulta,
    tela_consulta_personalizada,
)

from modulos.meu_dashboard import (
    inicializar_meu_dashboard,
    adicionar_widget,
    remover_widget,
    mover_widget_cima,
    mover_widget_baixo,
)

from modulos.dashboards_personalizados import (
    inicializar_dashboards_personalizados,
    salvar_dashboard_personalizado,
    carregar_dashboard_personalizado,
    listar_dashboards_personalizados,
    excluir_dashboard_personalizado,
    renderizar_metrica_personalizada,
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
    # processamento (Phase 5)
    'calcular_periodo_datas',
    'filtrar_df_por_consulta',
    'aplicar_filtros_widget',
    'preparar_df_com_metricas_filtro',
    'validar_filtros',
    'resetar_filtros',
    # abas (Phase 6)
    'aba_clientes',
    'aba_visao_geral',
    'aba_qa',
    'aba_dev',
    'aba_governanca',
    'aba_produto',
    'aba_backlog',
    'aba_suporte_implantacao',
    'aba_historico',
    'aba_lideranca',
    'aba_sobre',
    'aba_dashboard_personalizado',
    # cards (Phase 7)
    'exibir_card_detalhado_v2',
    'exibir_detalhes_sd',
    'exibir_detalhes_qa',
    'exibir_detalhes_pb',
    'exibir_timeline_transicoes',
    'exibir_cards_vinculados',
    'filtrar_e_classificar_comentarios',
    'exibir_comentarios',
    'filtrar_comentarios_pb',
    'exibir_comentarios_pb',
    # widgets (Phase 7)
    'mostrar_tooltip',
    'renderizar_resultado_consulta',
    'renderizar_lista_com_scroll',
    'renderizar_widget',
    'renderizar_kpi_widget',
    'renderizar_grafico_widget',
    'renderizar_tabela_widget',
    'renderizar_lista_widget',
    'mostrar_header_nina',
    'mostrar_indicador_atualizacao',
    'mostrar_card_ticket',
    'mostrar_lista_tickets_completa',
    'mostrar_lista_df_completa',
    # graficos (Phase 7)
    'criar_grafico_funil_qa',
    'criar_grafico_tendencia_fator_k',
    'criar_grafico_tendencia_qualidade',
    'criar_grafico_tendencia_bugs',
    'criar_grafico_tendencia_health',
    'criar_grafico_throughput',
    'criar_grafico_lead_time',
    'criar_grafico_reprovacao',
    'criar_grafico_estagio_por_produto',
    'criar_grafico_hotfix_por_produto',
    'criar_grafico_funil_personalizado',
    'criar_grafico_aging_backlog',
    'criar_grafico_prioridade_backlog',
    'criar_grafico_tipo_backlog',
    'criar_grafico_backlog_por_produto',
    # helpers (Phase 7)
    'calcular_valor_metrica',
    'calcular_dados_grafico',
    'calcular_dados_tabela',
    'calcular_lista_cards',
    'calcular_dados_heatmap',
    'calcular_dados_funil',
    'gerar_dados_tendencia',
    'exportar_para_csv',
    'exportar_para_excel',
    'aplicar_estilos',
    'get_tooltip_help',
    'formatar_tempo_relativo',
    'criar_card_metrica',
    'gerar_html_card_ticket',
    # consultas (Phase 7)
    'inicializar_consultas_personalizadas',
    'entrar_modo_consulta',
    'sair_modo_consulta',
    'salvar_consulta',
    'listar_consultas_salvas',
    'excluir_consulta',
    'tela_consulta_personalizada',
    # meu_dashboard (Phase 7)
    'inicializar_meu_dashboard',
    'adicionar_widget',
    'remover_widget',
    'mover_widget_cima',
    'mover_widget_baixo',
    # dashboards_personalizados (Phase 7)
    'inicializar_dashboards_personalizados',
    'salvar_dashboard_personalizado',
    'carregar_dashboard_personalizado',
    'listar_dashboards_personalizados',
    'excluir_dashboard_personalizado',
    'renderizar_metrica_personalizada',
]

