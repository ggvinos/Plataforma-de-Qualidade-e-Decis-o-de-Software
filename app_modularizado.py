"""
================================================================================
JIRA DASHBOARD v8.82 - NINA TECNOLOGIA - VERSÃO COMPLETA E ENRIQUECIDA
================================================================================
📊 NinaDash — Dashboard de Inteligência e Métricas de QA

🎯 Propósito: Transformar o QA de um processo sem visibilidade em um sistema 
   de inteligência operacional baseado em dados.

MELHORIAS v8.82:
- 🔧 FIX: Corrigido Meu Dashboard que não mostrava filtros corretamente
- 👤 PESSOAS: Lista de pessoas agora carrega corretamente
- ➕ ADICIONAR: Botão de adicionar widget agora funciona
- 📊 DEBUG: Mostra quantidade de dados e pessoas encontradas
- 🧹 SIMPLIFICADO: Interface mais limpa e direta

MELHORIAS v8.81:
- 🎨 MEU DASHBOARD: Tela totalmente nova para construir dashboards personalizados
- ➕ ADICIONAR WIDGETS: Construtor no topo para adicionar métricas  
- ⬆️⬇️ REORDENAR: Mova widgets para cima ou para baixo
- 🗑️ REMOVER: Exclua widgets que não precisa mais
- 📊 TEMPLATES: Visão Executiva, Foco DEV, Foco QA
- 💾 PERSISTÊNCIA: Dashboard salvo em cookie
- 🧹 SIDEBAR LIMPA: Apenas logo e botão voltar na tela do dashboard

MELHORIAS v8.80:
- 🎯 CONSULTA PERSONALIZADA: Tela separada para consultas avançadas
- 🔍 FILTROS DINÂMICOS: Pessoa, status, período, produto personalizados
- 📋 TIPOS DE CONSULTA: Cards, métricas, comparativos, tendências, bugs
- 💾 CONSULTAS SALVAS: Salve suas consultas favoritas
- 📅 PERÍODOS FLEXÍVEIS: Predefinidos ou datas personalizadas
- ⬅️ BOTÃO NA SIDEBAR: Acesso rápido à ferramenta avançada

MELHORIAS v8.78:
- 🎨 DESIGN REFINADO: Melhor espaçamento entre elementos
- ⬅️ BOTÃO VOLTAR NA SIDEBAR: Indica card ativo + volta fácil
- Link de compartilhamento mais compacto e funcional
- Visual mais limpo nas métricas do card
- Expanders fechados por padrão para menos poluição visual

MELHORIAS v8.6:
- 📱 SIDEBAR REFATORADA: Busca de card em destaque no topo
- 📤 COMPARTILHAMENTO FUNCIONAL: Link direto via query params
- Layout reorganizado: Logo → Busca → Filtros → Rodapé NINA
- URL persistente: ?card=SD-1234&projeto=SD

MELHORIAS v8.5:
- 🔍 BUSCA DE CARD INDIVIDUAL: Pesquise qualquer card pelo ID
- Painel completo com todas as métricas do card
- Fator K individual, janela de validação, aging, lead time
- Flags de fluxo (criado/finalizado na sprint, fora período)
- Timeline completa, resumo executivo automático

MELHORIAS v8.4:
- Aba Backlog exclusiva para projeto PB (Product Backlog)
- Health Score do backlog, análise de aging, cards estagnados
- Recomendações automáticas de ação

MELHORIAS v8.0:
- Header com logo Nina + subtítulo explicativo do objetivo
- Tooltips/explicações em TODAS as métricas (FPY, DDP, Fator K, etc)
- Seções colapsáveis em todas as abas (toggle open/close)
- Listagens COMPLETAS (opção de ver todos os cards)
- Aba Histórico enriquecida com múltiplos gráficos
- Mais métricas em cada aba
- Aba QA (sem "Gargalos" no nome)
- Auto-load + Cache inteligente
- Cards clicáveis com links Jira
- Métricas Ellen: iniciado/finalizado sprint, fora período, hotfix/produto

CAMPOS MAPEADOS JIRA NINA:
- customfield_11257: Story Points (principal)
- customfield_10016: Story Points (alternativo)
- customfield_11157: Bugs Encontrados  
- customfield_10020: Sprint
- customfield_11290: Complexidade de Teste
- customfield_10487: QA Responsável
- customfield_10102: Produto
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

# Phase 7: Novos módulos temáticos (blocos mentais)
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

from modulos.changelog import exibir_changelog

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA (DEVE SER PRIMEIRO)
# ==============================================================================

configure_page()

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


def salvar_dashboard_personalizado(nome: str, metricas: List[str], config: Dict = None):
    """Salva um dashboard personalizado."""
    inicializar_dashboards_personalizados()
    
    st.session_state.dashboards_personalizados[nome] = {
        "nome": nome,
        "metricas": metricas,
        "config": config or {},
        "criado_em": datetime.now().isoformat(),
        "atualizado_em": datetime.now().isoformat()
    }


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
    
    # ========== VERIFICAR LOGIN (via session_state ou cookie) ==========
    if not verificar_login():
        # Mostra tela de login
        mostrar_tela_login()
        return
    
    # ========== USUÁRIO LOGADO - DASHBOARD ==========
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
    
    # Inicializa modo Meu Dashboard
    if 'modo_consulta_personalizada' not in st.session_state:
        st.session_state.modo_consulta_personalizada = False
    
    # Verifica se veio via query param para Meu Dashboard
    if query_params.get("tela", None) == "meu_dashboard":
        st.session_state.modo_consulta_personalizada = True
    
    # ===============================================================
    # MODO MEU DASHBOARD - TELA SEPARADA COM SIDEBAR LIMPA
    # ===============================================================
    if st.session_state.modo_consulta_personalizada:
        # SIDEBAR MINIMALISTA - apenas logo, usuário e voltar
        with st.sidebar:
            # Logo
            st.markdown('''
            <div style="text-align: center; padding: 10px 0 5px 0;">
                <svg width="70" height="70" viewBox="0 0 187 187" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M173.709 89.2107C172.209 86.6048 169.414 84.838 166.225 84.838C163.036 84.838 160.241 86.5649 158.741 89.1627H151.683C149.465 58.8237 124.495 35 94.0216 35C63.5489 35 38.5862 58.8237 36.3678 89.1627H29.1759C27.6759 86.5649 24.8734 84.798 21.6682 84.798C18.463 84.798 15.6605 86.5806 14.1605 89.2031C13.4184 90.4899 13 92.001 13 93.6C13 95.1987 13.4184 96.7017 14.1605 97.997C15.6605 100.619 18.463 102.306 21.6682 102.306C24.8734 102.306 27.6838 100.435 29.1759 97.8369H36.3678C38.5862 128.168 63.5489 152 94.0216 152C124.495 152 149.465 128.176 151.675 97.8369H158.686C160.178 100.435 162.996 102.354 166.217 102.354C169.438 102.354 172.256 100.611 173.749 97.9648C174.475 96.6856 174.885 95.2148 174.885 93.6319C174.885 92.049 174.451 90.5222 173.701 89.2188L173.709 89.2107ZM111.145 125.554C107.971 131.518 101.758 135.459 94.5981 135.459C87.4374 135.459 81.2248 131.566 78.0509 125.602C77.1666 123.947 78.3667 122.092 80.2219 122.092H108.982C110.837 122.092 112.029 123.891 111.153 125.554H111.145ZM140.528 94.1277C140.528 103.825 132.76 111.691 123.184 111.691H65.4432C55.8675 111.691 48.0991 103.825 48.0991 94.1277V93.7199C48.0991 84.0223 55.8675 76.1557 65.4432 76.1557H123.184C132.76 76.1557 140.528 84.0223 140.528 93.7199V94.1277Z" fill="#AF0C37"/>
                <path d="M76.5809 105.311C82.9686 105.311 88.1466 100.068 88.1466 93.5996C88.1466 87.1312 82.9686 81.8875 76.5809 81.8875C70.1936 81.8875 65.0156 87.1312 65.0156 93.5996C65.0156 100.068 70.1936 105.311 76.5809 105.311Z" fill="#AF0C37"/>
                <path d="M111.437 105.311C117.824 105.311 123.002 100.068 123.002 93.5996C123.002 87.1312 117.824 81.8875 111.437 81.8875C105.049 81.8875 99.8712 87.1312 99.8712 93.5996C99.8712 100.068 105.049 105.311 111.437 105.311Z" fill="#AF0C37"/>
                </svg>
            </div>
            <div style="text-align: center; margin-bottom: 5px;">
                <h2 style="color: #AF0C37; margin: 0; font-size: 1.8em;">NinaDash</h2>
                <p style="color: #666; font-size: 0.85em; margin: 2px 0 0 0; font-style: italic;">
                    Meu Dashboard
                </p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Usuário logado
            user_nome = st.session_state.get("user_nome", "Usuário")
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #AF0C37 0%, #8F0A2E 100%); 
                        padding: 10px; border-radius: 8px; margin: 10px 0; text-align: center;">
                <p style="margin: 0; color: white; font-size: 13px;">👤 {user_nome}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Botão voltar (grande e em destaque)
            if st.button("⬅️ Voltar ao Dashboard", type="primary", use_container_width=True, key="btn_voltar_meu_dashboard"):
                st.session_state.modo_consulta_personalizada = False
                st.query_params.clear()
                st.rerun()
            
            st.markdown("---")
            
            # Rodapé minimalista
            st.markdown("""
            <div style="text-align: center; padding: 10px 0; color: #999; font-size: 0.75em;">
                📌 N9 • Qualidade e Decisão
            </div>
            """, unsafe_allow_html=True)
        
        # CARREGA DADOS DE TODOS OS PROJETOS
        with st.spinner("🔄 Carregando dados de todos os projetos..."):
            todos_dfs = []
            
            for proj in ["SD", "QA", "PB"]:
                try:
                    jql_proj = f'project = {proj} ORDER BY created DESC'
                    issues_proj, _ = buscar_dados_jira_cached(proj, jql_proj)
                    if issues_proj:
                        df_proj = processar_issues(issues_proj)
                        df_proj['projeto'] = proj
                        todos_dfs.append(df_proj)
                except:
                    pass
            
            if todos_dfs:
                df_todos = pd.concat(todos_dfs, ignore_index=True)
            else:
                st.error("❌ Não foi possível carregar dados")
                st.stop()
        
        # RENDERIZA A TELA MEU DASHBOARD
        tela_consulta_personalizada(df_todos)
        return  # Sai da função main() - não renderiza mais nada
    
    # ===============================================================
    # MODO NORMAL - SIDEBAR COMPLETA COM FILTROS
    # ===============================================================
    
    # Se veio via URL, ativa a busca automaticamente
    if card_compartilhado and not st.session_state.busca_ativa:
        st.session_state.busca_ativa = True
        st.session_state.card_buscado = card_compartilhado
        st.session_state.projeto_buscado = projeto_param if projeto_param else "SD"
    
    # Sidebar reorganizada
    with st.sidebar:
        # ===== HEADER: Logo centralizada + Nome + Descrição =====
        st.markdown('''
        <div style="text-align: center; padding: 10px 0 5px 0;">
            <svg width="70" height="70" viewBox="0 0 187 187" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M173.709 89.2107C172.209 86.6048 169.414 84.838 166.225 84.838C163.036 84.838 160.241 86.5649 158.741 89.1627H151.683C149.465 58.8237 124.495 35 94.0216 35C63.5489 35 38.5862 58.8237 36.3678 89.1627H29.1759C27.6759 86.5649 24.8734 84.798 21.6682 84.798C18.463 84.798 15.6605 86.5806 14.1605 89.2031C13.4184 90.4899 13 92.001 13 93.6C13 95.1987 13.4184 96.7017 14.1605 97.997C15.6605 100.619 18.463 102.306 21.6682 102.306C24.8734 102.306 27.6838 100.435 29.1759 97.8369H36.3678C38.5862 128.168 63.5489 152 94.0216 152C124.495 152 149.465 128.176 151.675 97.8369H158.686C160.178 100.435 162.996 102.354 166.217 102.354C169.438 102.354 172.256 100.611 173.749 97.9648C174.475 96.6856 174.885 95.2148 174.885 93.6319C174.885 92.049 174.451 90.5222 173.701 89.2188L173.709 89.2107ZM111.145 125.554C107.971 131.518 101.758 135.459 94.5981 135.459C87.4374 135.459 81.2248 131.566 78.0509 125.602C77.1666 123.947 78.3667 122.092 80.2219 122.092H108.982C110.837 122.092 112.029 123.891 111.153 125.554H111.145ZM140.528 94.1277C140.528 103.825 132.76 111.691 123.184 111.691H65.4432C55.8675 111.691 48.0991 103.825 48.0991 94.1277V93.7199C48.0991 84.0223 55.8675 76.1557 65.4432 76.1557H123.184C132.76 76.1557 140.528 84.0223 140.528 93.7199V94.1277Z" fill="#AF0C37"/>
            <path d="M76.5809 105.311C82.9686 105.311 88.1466 100.068 88.1466 93.5996C88.1466 87.1312 82.9686 81.8875 76.5809 81.8875C70.1936 81.8875 65.0156 87.1312 65.0156 93.5996C65.0156 100.068 70.1936 105.311 76.5809 105.311Z" fill="#AF0C37"/>
            <path d="M111.437 105.311C117.824 105.311 123.002 100.068 123.002 93.5996C123.002 87.1312 117.824 81.8875 111.437 81.8875C105.049 81.8875 99.8712 87.1312 99.8712 93.5996C99.8712 100.068 105.049 105.311 111.437 105.311Z" fill="#AF0C37"/>
            </svg>
        </div>
        <div style="text-align: center; margin-bottom: 5px;">
            <h2 style="color: #AF0C37; margin: 0; font-size: 1.8em;">NinaDash</h2>
            <p style="color: #666; font-size: 0.85em; margin: 2px 0 0 0; font-style: italic;">
                Transformando dados em decisões
            </p>
        </div>
        ''', unsafe_allow_html=True)
        
        # ===== USUÁRIO LOGADO =====
        user_nome = st.session_state.get("user_nome", "Usuário")
        user_email = st.session_state.get("user_email", "")
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #AF0C37 0%, #8F0A2E 100%); 
                    padding: 12px; border-radius: 8px; margin: 10px 0; text-align: center;">
            <p style="margin: 0; color: white; font-size: 14px; font-weight: 500;">👤 {user_nome}</p>
            <p style="margin: 4px 0 0 0; color: #fecdd3; font-size: 11px;">{user_email}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botão de Logout
        if st.button("🚪 Sair", use_container_width=True, key="btn_logout"):
            fazer_logout()
            st.rerun()
        
        if not verificar_credenciais():
            st.error("⚠️ Credenciais não configuradas!")
            st.markdown("""
            Configure em `.streamlit/secrets.toml`:
            ```toml
            [jira]
            email = "seu-email"
            token = "seu-token"
            ```
            """)
            st.stop()
        
        st.markdown("---")
        
        # ===== SEÇÃO 1: BUSCA DE CARD =====
        st.markdown("##### 🔍 Busca Rápida de Card")
        
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
            <div style="background: #fef3c7; border: 1px solid #f59e0b; border-radius: 6px; 
                        padding: 8px; margin: 8px 0; text-align: center;">
                <p style="margin: 0; color: #92400e; font-size: 0.85em;">
                    📍 <b>Visualizando:</b> {st.session_state.card_buscado.upper()}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Botão para voltar ao dashboard
            if st.button("⬅️ Voltar ao Dashboard", type="primary", use_container_width=True, key="btn_voltar"):
                st.session_state.busca_ativa = False
                st.session_state.card_buscado = ""
                st.session_state.projeto_buscado = "SD"
                st.query_params.clear()
                st.rerun()
        
        st.markdown("---")
        
        # ===== SEÇÃO 2: FILTROS (só mostra quando NÃO está pesquisando) =====
        if not st.session_state.busca_ativa:
            st.markdown("##### ⚙️ Filtros do Dashboard")
            
            projeto = st.selectbox("📁 Projeto", projetos_lista, index=0, key="projeto_dash")
            
            # Índice padrão do filtro baseado no projeto E na aba
            # PB, VALPROD e aba Suporte usam "Todo o período" (index=0)
            # SD/QA usam "Sprint Ativa" (index=1)
            aba_suporte = st.query_params.get("aba", None) == "suporte"
            indice_filtro_padrao = 0 if projeto in ["PB", "VALPROD"] or aba_suporte else 1
            
            filtro_sprint = st.selectbox(
                "🗓️ Período",
                ["Todo o período", "Sprint Ativa", "Últimos 30 dias", "Últimos 90 dias"],
                index=indice_filtro_padrao
            )
            
            # Nota: Filtro de Produto será adicionado após carregar os dados
            # Ferramentas Avançadas também será adicionado após Produto
            
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
        
        # AUTO-LOAD
        with st.spinner("🔄 Carregando dados do Jira..."):
            issues, ultima_atualizacao = buscar_dados_jira_cached(projeto, jql)
        
        if issues is None:
            st.error("❌ Não foi possível carregar dados do Jira")
            st.stop()
        
        if len(issues) == 0:
            st.warning("⚠️ Nenhum card encontrado para os filtros selecionados")
            st.stop()
        
        df = processar_issues(issues)
        
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
            # Adiciona Produto aos filtros principais
            produtos_disponiveis = ['Todos'] + sorted(df['produto'].unique().tolist())
            filtro_produto = st.selectbox("📦 Produto", produtos_disponiveis, index=0, key="filtro_produto_main")
            
            if filtro_produto != 'Todos':
                df = df[df['produto'] == filtro_produto]
            
            # ===== SEÇÃO DE FERRAMENTAS AVANÇADAS (após todos os filtros) =====
            st.markdown("---")
            st.markdown("##### 🔍 Ferramentas Avançadas")
            
            if st.button("🎨 Meu Dashboard", use_container_width=True, key="btn_meu_dashboard", 
                        help="Monte seu dashboard personalizado com widgets"):
                st.session_state.modo_consulta_personalizada = True
                st.query_params["tela"] = "meu_dashboard"
                st.rerun()
            
            # ===== RODAPÉ DA SIDEBAR (sempre no final) =====
            st.markdown("---")
            st.markdown("""
            <div style="text-align: center; padding: 5px 0;">
                <p style="color: #AF0C37; font-weight: bold; margin: 0; font-size: 0.85em;">
                    📌 N9 • Qualidade e Decisão de Software
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Changelog (extraído para modulos/changelog.py)
            exibir_changelog()


if __name__ == "__main__":
    main()
