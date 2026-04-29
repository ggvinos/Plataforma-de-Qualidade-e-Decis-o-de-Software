"""
================================================================================
📊 NinaDash v8.82 — Dashboard de Inteligência e Qualidade
================================================================================

Orquestrador modularizado. Lógica em modulos/, funções em abas.py.

👉 Histórico completo: veja MELHORIAS.md
================================================================================
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from typing import Optional, Dict, List, Any, Tuple
import json
import os
import io
import base64
import random
import extra_streamlit_components as stx

# ==============================================================================
# IMPORTS DOS MÓDULOS (Fase 1 de Modularização)
# ==============================================================================

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
    PB_FUNIL_ETAPAS,
    TEMAS_NAO_CLIENTES,
    NINADASH_URL,
)

from modulos.utils import (
    link_jira,
    card_link_com_popup,
    card_link_para_html,
    traduzir_link,
    calcular_dias_necessarios_validacao,
    avaliar_janela_validacao,
    get_secrets,
    verificar_credenciais,
)

from modulos.auth import (
    fazer_logout,
)

from modulos.confirmation_call_auth import (
    verificar_e_bloquear,
    renderizar_logout_sidebar,
    renderizar_usuario_sidebar,
    renderizar_botao_sair,
    obter_usuario_autenticado,
    get_cookie_manager,
)

from modulos.permissoes_usuario import (
    obter_permissoes_usuario,
    get_info_usuario_logado,
    usuario_eh_admin,
    verificar_acesso_aba,
    registrar_acesso,
)

# Constante para nome do cookie de consultas
COOKIE_CONSULTAS_NAME = "ninadash_consultas_salvas"

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
    aba_visao_geral_v2,  # Nova versão orientada a decisão
    aba_qa,
    aba_dev,
    aba_governanca,
    aba_produto,
    aba_backlog,
    aba_produto_pb,      # Aba Produto específica para PB
    aba_historico_pb,    # Aba Histórico específica para PB
    aba_suporte_implantacao,
    aba_historico,
    aba_lideranca,
    aba_sobre,
    aba_admin,  # Painel Administrativo
)

# Phase 7: Novos módulos temáticos (blocos mentais)
# REFATORAÇÃO V2: Nova visualização de cards com hierarquia visual
from modulos.cards_v2 import exibir_card_detalhado_v2

# Funções auxiliares do módulo original (para compatibilidade)
from modulos.cards import (
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
)

from modulos.changelog import exibir_changelog

# ==============================================================================
# FUNÇÃO AUXILIAR DE VERIFICAÇÃO DE ACESSO
# ==============================================================================

def renderizar_aba_com_permissao(nome_aba: str, funcao_aba, *args, **kwargs):
    """
    Renderiza uma aba (a verificação de permissão já foi feita na construção das abas).
    
    Args:
        nome_aba: Nome interno da aba (ex: "qa", "dev", "admin")
        funcao_aba: Função que renderiza a aba
        *args, **kwargs: Argumentos para a função da aba
    """
    try:
        funcao_aba(*args, **kwargs)
    except Exception as e:
        st.error(f"❌ Erro na aba {nome_aba}: {str(e)}")


def construir_abas_permitidas(projeto: str) -> list:
    """
    Constrói a lista de abas baseado nas permissões do usuário.
    Retorna lista de tuplas: (nome_display, nome_interno, funcao_aba)
    """
    permissoes = st.session_state.get("user_permissions", {})
    abas_permitidas = permissoes.get("abas_permitidas", ["visao_geral", "sobre"])
    
    if projeto == "PB":
        # Todas as abas possíveis para PB - experiência 100% focada em Produto
        todas_abas = [
            ("📊 Visão Geral", "visao_geral", aba_backlog),    # Funil de Produto + KPIs
            ("📦 Demandas", "produto", aba_produto_pb),        # Análise de Demandas
            ("📈 Evolução", "historico", aba_historico_pb),    # Evolução do Backlog
            ("ℹ️ Sobre", "sobre", aba_sobre),
            ("⚙️ Admin", "admin", aba_admin),
        ]
    else:
        # Todas as abas possíveis para SD/QA/DVG
        todas_abas = [
            ("📊 Visão Geral", "visao_geral", aba_visao_geral_v2),
            ("🔬 QA", "qa", aba_qa),
            ("👨‍💻 Dev", "dev", aba_dev),
            ("🎯 Suporte/Implantação", "suporte", aba_suporte_implantacao),
            ("🏢 Clientes", "clientes", aba_clientes),
            ("📋 Governança", "governanca", aba_governanca),
            ("📦 Produto", "produto", aba_produto),
            ("📈 Histórico", "historico", aba_historico),
            ("🎯 Liderança", "lideranca", aba_lideranca),
            ("ℹ️ Sobre", "sobre", aba_sobre),
            ("⚙️ Admin", "admin", aba_admin),
        ]
    
    # Filtra apenas as abas que o usuário tem permissão
    return [(nome, interno, func) for nome, interno, func in todas_abas if interno in abas_permitidas]

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA (DEVE SER PRIMEIRO)
# ==============================================================================

configure_page()

# ==============================================================================
# VERIFICAÇÃO DE AUTENTICAÇÃO (DEVE SER SEGUNDO - BLOQUEIA SEM LOGIN)
# ==============================================================================

verificar_e_bloquear()

# ==============================================================================
# CARREGAMENTO DE PERMISSÕES DO USUÁRIO
# ==============================================================================

# Obtém permissões do usuário após autenticação
# Sempre recarrega para garantir dados atualizados (é rápido)
user_email = st.session_state.get("user_email", "") or st.session_state.get("usuario_autenticado", "")
if user_email:
    # Registra o acesso na primeira vez
    if "acesso_registrado" not in st.session_state:
        registrar_acesso(user_email)
        st.session_state.acesso_registrado = True
    
    # Sempre atualiza as permissões para refletir mudanças no admin
    st.session_state.user_permissions = get_info_usuario_logado(user_email)
else:
    st.session_state.user_permissions = None

# Mostra aviso se usuário não está mapeado
if st.session_state.get("user_permissions") and not st.session_state.user_permissions.get("is_mapeado", True):
    st.warning("""
    ⚠️ **Perfil não mapeado** - Seu acesso está limitado às abas Visão Geral e Sobre.  
    Entre em contato com um administrador para configurar seu perfil de acesso.
    """)

# ==============================================================================
# LOADING VISUAL DURANTE INICIALIZAÇÃO
# ==============================================================================

# Mostra loading visual na primeira vez que o app é carregado após login
if "app_initialized" not in st.session_state:
    st.session_state.app_initialized = False

if not st.session_state.app_initialized:
    # Mostra loading visual compacto
    col1, col2, col3 = st.columns([0.2, 3.6, 0.2], gap="small")
    with col2:
        st.markdown("""
        <div style="
            text-align: center;
            padding: 40px 20px;
            background: white;
            border-radius: 8px;
            margin: 100px 0;
        ">
            <div style="font-size: 48px; margin-bottom: 20px; animation: spin 2s linear infinite;">⏳</div>
            <p style="color: #AF0C37; font-weight: bold; font-size: 18px; margin: 0 0 10px 0;">
                Carregando Dashboard
            </p>
            <p style="color: #666; font-size: 14px; margin: 0;">
                Sincronizando dados do Jira...
            </p>
        </div>
        <style>
            @keyframes spin {{
                from {{ transform: rotate(0deg); }}
                to {{ transform: rotate(360deg); }}
            }}
        </style>
        """, unsafe_allow_html=True)
    
    # Marca como inicializado
    st.session_state.app_initialized = True
    st.rerun()

# CSS global para o popup (deve ser inserido uma vez na página)
CARD_POPUP_CSS = """
<style>
    /* Wrapper do link com botão NinaDash */
    .card-link-wrapper {
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    
    /* ID do ticket (link para Jira) */
    .card-link-id {
        font-weight: 600;
        text-decoration: none;
        padding: 1px 3px;
        border-radius: 3px;
        transition: all 0.2s ease;
    }
    .card-link-id:hover {
        background: rgba(59, 130, 246, 0.1);
        text-decoration: underline;
    }
    
    /* Botão NinaDash - escondido por padrão, aparece no hover do wrapper */
    .card-action-btn {
        display: none;
        align-items: center;
        gap: 3px;
        padding: 3px 8px;
        font-size: 11px;
        font-weight: 500;
        text-decoration: none;
        border-radius: 4px;
        transition: all 0.15s ease;
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        color: #475569;
        white-space: nowrap;
    }
    
    /* Mostrar botão no hover do wrapper */
    .card-link-wrapper:hover .card-action-btn {
        display: inline-flex;
    }
    
    /* Hover NinaDash */
    .card-action-nina:hover {
        background: #AF0C37;
        border-color: #AF0C37;
        color: white;
    }
</style>
"""


# ==============================================================================


def _salvar_consultas_cookie():
    """Salva as consultas no cookie para persistência."""
    try:
        import json
        cookie_manager = get_cookie_manager()
        # Converte filtros datetime para string antes de serializar
        consultas_serializaveis = {}
        for nome, consulta in st.session_state.consultas_salvas.items():
            consulta_copia = consulta.copy()
            filtros_copia = consulta_copia.get('filtros', {}).copy()
            # Remove datetime objects que não são serializáveis
            for key in ['data_inicio', 'data_fim']:
                if key in filtros_copia and isinstance(filtros_copia[key], datetime):
                    filtros_copia[key] = filtros_copia[key].isoformat()
            consulta_copia['filtros'] = filtros_copia
            consultas_serializaveis[nome] = consulta_copia
        
        cookie_manager.set(
            COOKIE_CONSULTAS_NAME,
            json.dumps(consultas_serializaveis),
            expires_at=datetime.now() + timedelta(days=365)  # 1 ano
        )
    except Exception as e:
        pass  # Silently fail cookie save


def calcular_lista_cards(metrica_key: str, df: pd.DataFrame):
    """Calcula lista de cards para exibição."""
    try:
        if metrica_key == "code_review_fila":
            em_cr = df[df['status_categoria'] == 'code_review']
            return em_cr[['key', 'resumo', 'responsavel']].to_dict('records')
        
        elif metrica_key == "cards_aguardando_qa":
            aguardando = df[df['status_categoria'] == 'waiting_qa']
            return aguardando[['key', 'resumo', 'qa_responsavel']].to_dict('records')
        
        elif metrica_key == "cards_impedidos":
            impedidos = df[df['status_categoria'] == 'blocked']
            return impedidos[['key', 'resumo', 'responsavel']].to_dict('records')
        
        elif metrica_key == "cards_bloqueados":
            bloqueados = df[df['status'].str.lower().str.contains('bloque|block', na=False)]
            return bloqueados[['key', 'resumo', 'responsavel']].to_dict('records')
        
        return []
    except Exception:
        return []


def filtrar_comentarios_pb(comentarios: List[Dict]) -> List[Dict]:
    """
    Filtra e classifica comentários para Product Backlog (PB).
    Tags específicas para contexto de produto, não de QA.
    
    Classificações PB:
    - decisao: Aprovações, decisões, definições
    - duvida: Perguntas, questionamentos
    - requisito: Detalhamento, escopo, critérios
    - alinhamento: Reuniões, alinhamentos
    - normal: Comentários gerais
    """
    if not comentarios:
        return []
    
    # Padrões de automação a serem filtrados
    padroes_automacao = [
        "mentioned this issue in a commit",
        "mentioned this issue in a branch",
        "merge branch",
        "pushed a commit",
        "created a branch",
        "deleted branch",
        "opened a pull request",
        "closed a pull request",
        "merged a pull request",
        "mentioned this issue in a pull request",
        "linked a pull request",
        "connected this issue",
        "referenced this issue",
        "/confirmationcall on branch",
        "on branch sd-",
        "on branch SD-",
        "on branch pb-",
        "on branch PB-",
    ]
    
    # Padrões para DECISÃO/APROVAÇÃO
    padroes_decisao = [
        "aprovado",
        "aprovação",
        "aprovei",
        "aprovar",
        "decidido",
        "decisão",
        "definido",
        "definição",
        "definimos",
        "ficou definido",
        "ficou decidido",
        "vamos fazer",
        "vamos seguir",
        "seguir com",
        "ok para",
        "pode seguir",
        "pode prosseguir",
        "liberado",
        "confirmado",
        "confirmação",
        "validado pelo",
        "validado por",
        "alinhado com",
        "combinado",
        "acordado",
    ]
    
    # Padrões para DÚVIDA/PERGUNTA
    padroes_duvida = [
        "dúvida",
        "duvida",
        "pergunta",
        "questão",
        "questao",
        "?",  # comentários com interrogação
        "não entendi",
        "não ficou claro",
        "poderia esclarecer",
        "pode explicar",
        "como funciona",
        "como seria",
        "qual seria",
        "qual é",
        "o que seria",
        "o que significa",
        "faz sentido",
        "seria possível",
        "é possível",
        "tem como",
        "precisamos entender",
        "preciso entender",
        "precisamos definir",
        "aguardando esclarecimento",
        "aguardando retorno",
        "favor esclarecer",
        "por favor esclarecer",
    ]
    
    # Padrões para REQUISITO/ESCOPO
    padroes_requisito = [
        "requisito",
        "critério de aceite",
        "critérios de aceite",
        "criterio de aceite",
        "ac:",
        "escopo",
        "funcionalidade",
        "deve permitir",
        "deve ser possível",
        "o sistema deve",
        "o usuário deve",
        "o usuário poderá",
        "será necessário",
        "deverá",
        "regra de negócio",
        "regra:",
        "detalhamento",
        "especificação",
        "fluxo:",
        "comportamento esperado",
        "cenário de uso",
        "caso de uso",
        "user story",
        "história de usuário",
        "como um",
        "eu quero",
        "para que",
    ]
    
    # Padrões para ALINHAMENTO
    padroes_alinhamento = [
        "alinhamento",
        "alinhado",
        "alinhei",
        "reunião",
        "conversei",
        "conversamos",
        "falei com",
        "falamos com",
        "discutimos",
        "discutido",
        "apresentamos",
        "apresentado",
        "feedback do",
        "retorno do",
        "segundo o",
        "conforme",
        "de acordo com",
        "stakeholder",
        "product owner",
        "po disse",
        "cliente disse",
        "cliente solicitou",
        "solicitação do",
        "pedido do",
    ]
    
    comentarios_filtrados = []
    
    for com in comentarios:
        texto_lower = com.get('texto', '').lower()
        autor = com.get('autor', '').lower()
        
        # Verifica se é automação
        eh_automacao = False
        for padrao in padroes_automacao:
            if padrao.lower() in texto_lower:
                eh_automacao = True
                break
        
        if any(bot in autor for bot in ['automation', 'bot', 'github', 'bitbucket', 'gitlab', 'jira']):
            eh_automacao = True
        
        if eh_automacao:
            continue
        
        # Classifica (ordem de prioridade)
        classificacao = 'normal'
        
        # 1. Decisão
        for padrao in padroes_decisao:
            if padrao in texto_lower:
                classificacao = 'decisao'
                break
        
        # 2. Dúvida (se não foi decisão)
        if classificacao == 'normal':
            for padrao in padroes_duvida:
                if padrao in texto_lower:
                    classificacao = 'duvida'
                    break
        
        # 3. Requisito
        if classificacao == 'normal':
            for padrao in padroes_requisito:
                if padrao in texto_lower:
                    classificacao = 'requisito'
                    break
        
        # 4. Alinhamento
        if classificacao == 'normal':
            for padrao in padroes_alinhamento:
                if padrao in texto_lower:
                    classificacao = 'alinhamento'
                    break
        
        # Parse da data
        try:
            data_parsed = datetime.fromisoformat(com['data'].replace('Z', '+00:00')).replace(tzinfo=None)
        except:
            data_parsed = datetime.now()
        
        comentarios_filtrados.append({
            **com,
            'classificacao': classificacao,
            'data_parsed': data_parsed,
        })
    
    # Ordena por data
    comentarios_filtrados.sort(key=lambda x: x['data_parsed'])
    
    # Numera os eventos
    contadores = {'decisao': 0, 'duvida': 0, 'requisito': 0, 'alinhamento': 0}
    for com in comentarios_filtrados:
        if com['classificacao'] in contadores:
            contadores[com['classificacao']] += 1
            com['numero_evento'] = contadores[com['classificacao']]
    
    return comentarios_filtrados


def main():
    """Função principal do dashboard."""
    
    # ========== CSS GLOBAL PARA ESCONDER WARNINGS ==========
    # Injeta CSS imediatamente para esconder qualquer warning do CookieManager
    st.markdown("""
    <style>
    /* Esconde warnings/exceptions do Streamlit (CookieManager) */
    .stException, [data-testid="stException"], 
    .stWarning, [data-testid="stWarning"],
    div[data-testid="stNotification"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        overflow: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ========== USUÁRIO LOGADO - DASHBOARD =====
    # (verificar_e_bloquear() já foi chamado no topo do script)
    aplicar_estilos()
    
    # CSS global para popup de cards (permite escolher NinaDash ou Jira)
    st.markdown(CARD_POPUP_CSS, unsafe_allow_html=True)
    
    # Header principal com logo Nina
    mostrar_header_nina()
    
    # ========== GERENCIAMENTO DE QUERY PARAMS ==========
    # Captura query params para compartilhamento de busca
    query_params = st.query_params
    card_compartilhado = query_params.get("card", None)
    projeto_param = query_params.get("projeto", None)
    qa_compartilhado = query_params.get("qa", None)
    dev_compartilhado = query_params.get("dev", None)
    pessoa_compartilhada = query_params.get("pessoa", None)
    cliente_compartilhado = query_params.get("cliente", None)
    
    # Verifica se é um link compartilhado válido
    eh_link_compartilhado = any([card_compartilhado, qa_compartilhado, dev_compartilhado, pessoa_compartilhada, cliente_compartilhado])
    
    # Se NÃO é link compartilhado mas tem query_params de aba, limpa tudo
    # Isso evita "poluição" de URL quando o usuário navega normalmente
    if not eh_link_compartilhado and query_params.get("aba", None):
        # Limpa todos os query params para URL limpa
        st.query_params.clear()
    
    # Inicializa session_state para controle de busca
    if 'busca_ativa' not in st.session_state:
        st.session_state.busca_ativa = False
    if 'card_buscado' not in st.session_state:
        st.session_state.card_buscado = ""
    if 'projeto_buscado' not in st.session_state:
        st.session_state.projeto_buscado = "SD"
    
    # Inicializa session_state para controle de atualização do Jira
    if 'ultima_atualizacao_jira' not in st.session_state:
        st.session_state.ultima_atualizacao_jira = None
    if 'atualizando_jira' not in st.session_state:
        st.session_state.atualizando_jira = False
    if 'erro_atualizacao' not in st.session_state:
        st.session_state.erro_atualizacao = False
    
    # ===============================================================
    # MODO NORMAL - SIDEBAR COMPLETA COM FILTROS
    # ===============================================================
    
    # Se veio via URL, ativa a busca automaticamente
    if card_compartilhado and not st.session_state.busca_ativa:
        st.session_state.busca_ativa = True
        st.session_state.card_buscado = card_compartilhado
        st.session_state.projeto_buscado = projeto_param if projeto_param else "SD"
    
    # Obtém informações de permissão do usuário
    email_usuario = obter_usuario_autenticado()
    colaborador_data, abas_permitidas, is_mapeado = obter_permissoes_usuario(email_usuario) if email_usuario else ({}, [], False)
    
    # Sidebar reorganizada - Nova estrutura UX
    with st.sidebar:
        # ================================================================
        # BLOCO 1: HEADER (Logo + Usuário)
        # ================================================================
        st.markdown('''
        <div style="text-align: center; padding: 4px 0 0 0;">
            <svg width="38" height="38" viewBox="0 0 187 187" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M173.709 89.2107C172.209 86.6048 169.414 84.838 166.225 84.838C163.036 84.838 160.241 86.5649 158.741 89.1627H151.683C149.465 58.8237 124.495 35 94.0216 35C63.5489 35 38.5862 58.8237 36.3678 89.1627H29.1759C27.6759 86.5649 24.8734 84.798 21.6682 84.798C18.463 84.798 15.6605 86.5806 14.1605 89.2031C13.4184 90.4899 13 92.001 13 93.6C13 95.1987 13.4184 96.7017 14.1605 97.997C15.6605 100.619 18.463 102.306 21.6682 102.306C24.8734 102.306 27.6838 100.435 29.1759 97.8369H36.3678C38.5862 128.168 63.5489 152 94.0216 152C124.495 152 149.465 128.176 151.675 97.8369H158.686C160.178 100.435 162.996 102.354 166.217 102.354C169.438 102.354 172.256 100.611 173.749 97.9648C174.475 96.6856 174.885 95.2148 174.885 93.6319C174.885 92.049 174.451 90.5222 173.701 89.2188L173.709 89.2107ZM111.145 125.554C107.971 131.518 101.758 135.459 94.5981 135.459C87.4374 135.459 81.2248 131.566 78.0509 125.602C77.1666 123.947 78.3667 122.092 80.2219 122.092H108.982C110.837 122.092 112.029 123.891 111.153 125.554H111.145ZM140.528 94.1277C140.528 103.825 132.76 111.691 123.184 111.691H65.4432C55.8675 111.691 48.0991 103.825 48.0991 94.1277V93.7199C48.0991 84.0223 55.8675 76.1557 65.4432 76.1557H123.184C132.76 76.1557 140.528 84.0223 140.528 93.7199V94.1277Z" fill="#AF0C37"/>
            <path d="M76.5809 105.311C82.9686 105.311 88.1466 100.068 88.1466 93.5996C88.1466 87.1312 82.9686 81.8875 76.5809 81.8875C70.1936 81.8875 65.0156 87.1312 65.0156 93.5996C65.0156 100.068 70.1936 105.311 76.5809 105.311Z" fill="#AF0C37"/>
            <path d="M111.437 105.311C117.824 105.311 123.002 100.068 123.002 93.5996C123.002 87.1312 117.824 81.8875 111.437 81.8875C105.049 81.8875 99.8712 87.1312 99.8712 93.5996C99.8712 100.068 105.049 105.311 111.437 105.311Z" fill="#AF0C37"/>
            </svg>
            <div style="font-size: 1.2em; font-weight: 700; color: #AF0C37; margin: 0;">NinaDash</div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
        
        # Usuário com múltiplos papéis
        renderizar_usuario_sidebar(colaborador_data, is_mapeado)
        
        # ================================================================
        # BLOCO 2: ATUALIZAR JIRA (separado)
        # ================================================================
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        
        # Estado do botão
        atualizando = st.session_state.get('atualizando_jira', False)
        erro_att = st.session_state.get('erro_atualizacao', False)
        
        if atualizando:
            st.button("🔄 Atualizando...", use_container_width=True, disabled=True, key="btn_att_jira")
        elif erro_att:
            if st.button("⚠️ Erro - Tentar novamente", use_container_width=True, type="secondary", key="btn_att_jira"):
                st.session_state.erro_atualizacao = False
                st.session_state.atualizando_jira = True
                st.cache_data.clear()
                st.rerun()
        else:
            if st.button("🔄 Atualizar dados", use_container_width=True, type="primary", key="btn_att_jira"):
                st.session_state.atualizando_jira = True
                st.cache_data.clear()
                st.rerun()
        
        # Texto auxiliar de última atualização (separado do botão)
        ultima_att = st.session_state.get('ultima_atualizacao_jira')
        if ultima_att:
            minutos = int((datetime.now() - ultima_att).total_seconds() / 60)
            if minutos < 1:
                tempo_texto = "agora mesmo"
            elif minutos < 60:
                tempo_texto = f"há {minutos} min"
            else:
                horas = minutos // 60
                tempo_texto = f"há {horas}h"
            st.markdown(f"""
            <div style="text-align: center; font-size: 10px; color: #9ca3af; margin-top: 2px;">
                Última atualização: {tempo_texto}
            </div>
            """, unsafe_allow_html=True)
        
        if not verificar_credenciais():
            st.error("⚠️ Credenciais Jira não configuradas!")
            st.markdown("""
            Configure em `.streamlit/secrets.toml`:
            ```toml
            [jira]
            email = "seu-email"
            token = "seu-token"
            ```
            """)
            st.stop()
        
        # ================================================================
        # BLOCO 3: BUSCA RÁPIDA
        # ================================================================
        st.markdown("<div style='border-top: 1px solid #e5e7eb; margin: 12px 0 8px 0;'></div>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 11px; font-weight: 600; color: #6b7280; margin: 0 0 6px 0; letter-spacing: 0.5px;'>🔍 BUSCA RÁPIDA</p>", unsafe_allow_html=True)
        
        # Projeto para busca
        projetos_lista = ["SD", "QA", "PB", "VALPROD"]
        projeto_busca_index = 0
        if st.session_state.busca_ativa and st.session_state.projeto_buscado in projetos_lista:
            projeto_busca_index = projetos_lista.index(st.session_state.projeto_buscado)
        
        # Extrai número inicial se estiver buscando
        numero_inicial = ""
        if st.session_state.busca_ativa and st.session_state.card_buscado:
            numero_inicial = st.session_state.card_buscado.upper()
            for prefix in ["SD-", "QA-", "PB-", "VALPROD-"]:
                if numero_inicial.startswith(prefix):
                    numero_inicial = numero_inicial[len(prefix):]
                    break
        
        # Formulário permite Enter para buscar
        with st.form(key="form_busca_card", clear_on_submit=False):
            col_proj, col_num = st.columns([1.5, 1.5])
            with col_proj:
                projeto_busca = st.selectbox(
                    "Projeto",
                    projetos_lista,
                    index=projeto_busca_index,
                    label_visibility="collapsed",
                    help="SD, QA, PB ou VALPROD"
                )
            
            with col_num:
                numero_card_input = st.text_input(
                    "Número",
                    value=numero_inicial,
                    placeholder="1234",
                    label_visibility="collapsed",
                    max_chars=10
                )
            
            # Botão de buscar (submete com Enter também)
            buscar_clicado = st.form_submit_button("🔍 Buscar", use_container_width=True)
            
            if buscar_clicado:
                if numero_card_input:
                    st.session_state.busca_ativa = True
                    st.session_state.card_buscado = f"{projeto_busca}-{numero_card_input}"
                    st.session_state.projeto_buscado = projeto_busca
                    st.rerun()
                else:
                    st.warning("Digite o número do card")
        
        # Mostra indicador de pesquisa ativa
        if st.session_state.busca_ativa and st.session_state.card_buscado:
            st.markdown(f"""
            <div style="background: #fef3c7; border: 1px solid #f59e0b; border-radius: 4px; 
                        padding: 6px 10px; margin: 6px 0; text-align: center;">
                <span style="color: #92400e; font-size: 12px;">
                    📍 <b>{st.session_state.card_buscado.upper()}</b>
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            # Botão para voltar ao dashboard
            if st.button("⬅️ Voltar", type="secondary", use_container_width=True, key="btn_voltar"):
                st.session_state.busca_ativa = False
                st.session_state.card_buscado = ""
                st.session_state.projeto_buscado = "SD"
                st.query_params.clear()
                st.rerun()
        
        # ================================================================
        # BLOCO 4: CONTEXTO ATUAL (sem duplicação visual)
        # ================================================================
        if not st.session_state.busca_ativa:
            st.markdown("<div style='border-top: 1px solid #e5e7eb; margin: 12px 0 8px 0;'></div>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 11px; font-weight: 600; color: #6b7280; margin: 0 0 8px 0; letter-spacing: 0.5px;'>📌 CONTEXTO ATUAL</p>", unsafe_allow_html=True)
            
            # Cores por projeto
            cores_projeto = {"SD": "#3b82f6", "QA": "#22c55e", "PB": "#f59e0b", "VALPROD": "#8b5cf6"}
            
            # --- PROJETO ---
            # Estado para controlar edição
            if 'editando_projeto' not in st.session_state:
                st.session_state.editando_projeto = False
            
            col_label, col_valor = st.columns([1.2, 2])
            with col_label:
                st.markdown("<span style='font-size: 12px; color: #6b7280;'>📁 Projeto</span>", unsafe_allow_html=True)
            with col_valor:
                projeto = st.selectbox(
                    "Projeto", 
                    projetos_lista, 
                    index=0, 
                    key="projeto_dash", 
                    label_visibility="collapsed"
                )
            
            # --- PERÍODO ---
            aba_suporte = st.query_params.get("aba", None) == "suporte"
            indice_filtro_padrao = 0 if projeto in ["PB", "VALPROD"] or aba_suporte else 1
            
            col_label2, col_valor2 = st.columns([1.2, 2])
            with col_label2:
                st.markdown("<span style='font-size: 12px; color: #6b7280;'>📅 Período</span>", unsafe_allow_html=True)
            with col_valor2:
                filtro_sprint = st.selectbox(
                    "Período",
                    ["Todo período", "Sprint Ativa", "Últimos 30d", "Últimos 90d"],
                    index=indice_filtro_padrao,
                    label_visibility="collapsed"
                )
            
            # Mapeamento para JQL
            filtro_sprint_map = {
                "Todo período": "Todo o período",
                "Sprint Ativa": "Sprint Ativa",
                "Últimos 30d": "Últimos 30 dias",
                "Últimos 90d": "Últimos 90 dias"
            }
            filtro_sprint = filtro_sprint_map.get(filtro_sprint, filtro_sprint)
            
            # Nota: Filtro de Produto será adicionado após carregar os dados
            
        else:
            # Quando pesquisando, usa o projeto da busca
            projeto = st.session_state.projeto_buscado
            filtro_sprint = "Sprint Ativa"  # Não usado na busca específica
    
    # ===== MODO BUSCA DE CARD ESPECÍFICO =====
    if st.session_state.busca_ativa and st.session_state.card_buscado:
        busca_card = st.session_state.card_buscado
        projeto_busca = st.session_state.projeto_buscado
        
        # Atualiza a URL com os parâmetros de compartilhamento
        st.query_params["card"] = busca_card
        st.query_params["projeto"] = projeto_busca
        
        # Busca o card específico (sem filtros de período)
        with st.spinner(f"🔍 Buscando {busca_card}..."):
            issue, links, comentarios, historico_transicoes = buscar_card_especifico(busca_card)
        
        if issue:
            # Processa o card encontrado
            card_data = processar_issue_unica(issue)
            exibir_card_detalhado_v2(card_data, links, comentarios, historico_transicoes, projeto_busca)
        else:
            st.warning(f"⚠️ Card **{busca_card}** não encontrado.")
            st.info("💡 Verifique se o ID está correto. O card será buscado em todo o histórico do projeto.")
    
    # ===== MODO DASHBOARD NORMAL =====
    else:
        # JQL
        if filtro_sprint == "Todo o período":
            jql = f'project = {projeto} ORDER BY created DESC'
        elif filtro_sprint == "Sprint Ativa":
            jql = f'project = {projeto} AND sprint in openSprints() ORDER BY created DESC'
        elif filtro_sprint == "Últimos 30 dias":
            jql = f'project = {projeto} AND created >= -30d ORDER BY created DESC'
        else:
            jql = f'project = {projeto} AND created >= -90d ORDER BY created DESC'
        
        # ===== LOADING VISUAL APRIMORADO =====
        # Placeholder para loading animado
        loading_placeholder = st.empty()
        
        # Mostra loading ANTES de iniciar a busca
        with loading_placeholder.container():
            st.markdown("""
            <style>
            @keyframes pulse {
                0% { opacity: 0.6; transform: scale(0.98); }
                50% { opacity: 1; transform: scale(1); }
                100% { opacity: 0.6; transform: scale(0.98); }
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .loading-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 80px 20px;
                animation: pulse 2s ease-in-out infinite;
            }
            .loading-spinner {
                width: 60px;
                height: 60px;
                border: 4px solid #f3f3f3;
                border-top: 4px solid #AF0C37;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-bottom: 20px;
            }
            .loading-text {
                color: #666;
                font-size: 1.1em;
                margin-top: 10px;
            }
            .loading-subtext {
                color: #999;
                font-size: 0.9em;
                margin-top: 5px;
            }
            </style>
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <div style="color: #AF0C37; font-size: 1.5em; font-weight: bold;">Carregando NinaDash</div>
                <div class="loading-text">🔄 Conectando ao Jira...</div>
                <div class="loading-subtext">Buscando dados do projeto """ + projeto + """</div>
                <div style="color: #aaa; font-size: 0.8em; margin-top: 15px;">Isso pode levar alguns segundos...</div>
            </div>
            """, unsafe_allow_html=True)
        
        # AUTO-LOAD - busca os dados (loading fica visível até terminar)
        try:
            issues, ultima_atualizacao = buscar_dados_jira_cached(projeto, jql)
            # Salva última atualização e reseta estados
            st.session_state.ultima_atualizacao_jira = ultima_atualizacao
            st.session_state.atualizando_jira = False
            st.session_state.erro_atualizacao = False
        except Exception as e:
            st.session_state.atualizando_jira = False
            st.session_state.erro_atualizacao = True
            issues = None
            ultima_atualizacao = datetime.now()
        
        # NOTA: loading_placeholder.empty() é chamado mais abaixo,
        # após todo o processamento estar completo
        
        # ===== TRATAMENTO DE ERRO COM BOTÃO TENTAR NOVAMENTE =====
        if issues is None:
            st.markdown("""
            <div style="text-align: center; padding: 60px 20px;">
                <div style="font-size: 4em; margin-bottom: 20px;">⚠️</div>
                <h2 style="color: #dc2626; margin-bottom: 10px;">Não foi possível conectar ao Jira</h2>
                <p style="color: #666; margin-bottom: 5px;">O servidor demorou muito para responder (timeout).</p>
                <p style="color: #888; font-size: 0.9em;">Isso pode acontecer quando há muitos dados ou a conexão está lenta.</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔄 Tentar Novamente", use_container_width=True, type="primary"):
                    st.cache_data.clear()
                    st.rerun()
            
            st.info("💡 **Dica:** Tente selecionar um período menor (ex: Sprint Ativa ou Últimos 30 dias)")
            st.stop()
        
        if len(issues) == 0:
            st.warning("⚠️ Nenhum card encontrado para os filtros selecionados")
            st.stop()
        
        df = processar_issues(issues)
        
        # ===== AVISO INFORMATIVO (dispensável) =====
        if 'aviso_fechado' not in st.session_state:
            st.session_state.aviso_fechado = False
        
        if not st.session_state.aviso_fechado:
            aviso_col1, aviso_col2 = st.columns([0.95, 0.05])
            with aviso_col1:
                st.markdown("""
                <div style="background: linear-gradient(90deg, #d1fae5 0%, #ecfdf5 100%); 
                            border-left: 4px solid #10b981; 
                            padding: 8px 12px; 
                            border-radius: 0 8px 8px 0; 
                            font-size: 0.85em;">
                    <span style="color: #065f46;">
                        📊 <strong>Dados sincronizados com o Jira!</strong> Métricas calculadas em tempo real a partir dos cards do projeto.
                    </span>
                </div>
                """, unsafe_allow_html=True)
            with aviso_col2:
                if st.button("✕", key="fechar_aviso", help="Fechar aviso"):
                    st.session_state.aviso_fechado = True
                    st.rerun()
        
        # Adiciona coluna de projeto ao df principal
        df['projeto'] = projeto
        
        # ===== BUSCA TODOS OS PROJETOS PARA ABA SUPORTE/IMPLANTAÇÃO =====
        # Essa aba precisa de dados de todos os projetos para mostrar "onde estão meus cards"
        todos_dfs = [df]  # Começa com o df do projeto selecionado
        
        # Busca SD (se não for o projeto atual)
        if projeto != "SD":
            try:
                if filtro_sprint == "Todo o período":
                    jql_sd = 'project = SD ORDER BY created DESC'
                elif filtro_sprint == "Sprint Ativa":
                    jql_sd = 'project = SD AND sprint in openSprints() ORDER BY created DESC'
                elif filtro_sprint == "Últimos 30 dias":
                    jql_sd = 'project = SD AND created >= -30d ORDER BY created DESC'
                else:
                    jql_sd = 'project = SD AND created >= -90d ORDER BY created DESC'
                
                issues_sd, _ = buscar_dados_jira_cached("SD", jql_sd)
                if issues_sd:
                    df_sd = processar_issues(issues_sd)
                    df_sd['projeto'] = 'SD'
                    todos_dfs.append(df_sd)
            except:
                pass
        
        # Busca QA (se não for o projeto atual)
        if projeto != "QA":
            try:
                if filtro_sprint == "Todo o período":
                    jql_qa = 'project = QA ORDER BY created DESC'
                elif filtro_sprint == "Sprint Ativa":
                    jql_qa = 'project = QA AND sprint in openSprints() ORDER BY created DESC'
                elif filtro_sprint == "Últimos 30 dias":
                    jql_qa = 'project = QA AND created >= -30d ORDER BY created DESC'
                else:
                    jql_qa = 'project = QA AND created >= -90d ORDER BY created DESC'
                
                issues_qa, _ = buscar_dados_jira_cached("QA", jql_qa)
                if issues_qa:
                    df_qa = processar_issues(issues_qa)
                    df_qa['projeto'] = 'QA'
                    todos_dfs.append(df_qa)
            except:
                pass
        
        # Busca PB (sempre todo período, não tem sprint)
        if projeto != "PB":
            try:
                jql_pb = 'project = PB ORDER BY created DESC'
                issues_pb, _ = buscar_dados_jira_cached("PB", jql_pb)
                if issues_pb:
                    df_pb = processar_issues(issues_pb)
                    df_pb['projeto'] = 'PB'
                    todos_dfs.append(df_pb)
            except:
                pass
        
        # Busca VALPROD (sempre todo período)
        if projeto != "VALPROD":
            try:
                jql_valprod = 'project = VALPROD ORDER BY created DESC'
                issues_valprod, _ = buscar_dados_jira_cached("VALPROD", jql_valprod)
                if issues_valprod:
                    df_valprod = processar_issues(issues_valprod)
                    df_valprod['projeto'] = 'VALPROD'
                    todos_dfs.append(df_valprod)
            except:
                pass
        
        # Combina todos os DataFrames
        df_todos = pd.concat(todos_dfs, ignore_index=True) if len(todos_dfs) > 0 else df.copy()
        
        # Garante que df_todos tenha a coluna 'projeto'
        if 'projeto' not in df_todos.columns:
            df_todos['projeto'] = projeto
        
        # Filtro por produto (dentro da sidebar, junto aos outros filtros)
        with st.sidebar:
            # Adiciona Produto aos filtros (compacto)
            produtos_disponiveis = ['Todos'] + sorted(df['produto'].unique().tolist())
            filtro_produto = st.selectbox("Produto", produtos_disponiveis, index=0, key="filtro_produto_main", label_visibility="collapsed")
            
            # Badge do produto
            if filtro_produto != 'Todos':
                df = df[df['produto'] == filtro_produto]
                st.markdown(f"""
                <div style="background: #dbeafe; border-radius: 4px; padding: 4px 8px; margin: -8px 0 4px 0; text-align: center;">
                    <span style="font-size: 11px; color: #1d4ed8;">
                        📦 {filtro_produto}
                    </span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background: #f3f4f6; border-radius: 4px; padding: 4px 8px; margin: -8px 0 4px 0; text-align: center;">
                    <span style="font-size: 11px; color: #6b7280;">
                        📦 Todos os produtos
                    </span>
                </div>
                """, unsafe_allow_html=True)
            
            # ================================================================
            # BLOCO 4: FOOTER (Sair + Versão)
            # ================================================================
            st.markdown("<div style='border-top: 1px solid #eee; margin: 16px 0 8px 0;'></div>", unsafe_allow_html=True)
            
            # Botão de sair
            renderizar_botao_sair()
            
            # Versão e créditos
            st.markdown("""
            <div style="text-align: center; padding: 8px 0 4px 0;">
                <p style="color: #9ca3af; font-size: 10px; margin: 0;">
                    NinaDash v8.82
                </p>
                <p style="color: #d1d5db; font-size: 9px; margin: 2px 0 0 0;">
                    N9 • Qualidade de Software
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Changelog (compacto)
            exibir_changelog()
        
        # ===== RENDERIZA AS ABAS DO DASHBOARD (DINÂMICO POR PERMISSÕES) =====
        # Remove o loading AGORA que todo o processamento terminou
        loading_placeholder.empty()
        
        # Constrói apenas as abas que o usuário tem permissão para ver
        abas_permitidas = construir_abas_permitidas(projeto)
        
        if not abas_permitidas:
            st.warning("⚠️ Você não tem acesso a nenhuma aba. Entre em contato com um administrador.")
        else:
            # Cria as abas dinamicamente
            nomes_abas = [aba[0] for aba in abas_permitidas]
            tabs = st.tabs(nomes_abas)
            
            # Mapeamento de abas que precisam de argumentos especiais
            args_especiais = {
                "backlog": (df,),
                "visao_geral": (df, ultima_atualizacao),
                "qa": (df,),
                "dev": (df,),
                "suporte": (df_todos,),  # Usa df_todos para suporte
                "clientes": (df_todos,),  # Usa df_todos para clientes
                "governanca": (df,),
                "produto": (df,),
                "historico": (df,),
                "lideranca": (df,),
                "sobre": (),
                "admin": (),
            }
            
            # Renderiza cada aba com seus argumentos
            for i, (nome_display, nome_interno, funcao_aba) in enumerate(abas_permitidas):
                with tabs[i]:
                    args = args_especiais.get(nome_interno, ())
                    renderizar_aba_com_permissao(nome_interno, funcao_aba, *args)


if __name__ == "__main__":
    main()
