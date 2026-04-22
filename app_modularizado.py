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
            
            # Changelog em expander
            with st.expander("📋 Histórico de Versões", expanded=False):
                st.markdown("""
                <div style="margin-bottom: 10px; display: flex; flex-wrap: wrap; gap: 5px;">
                    <span style="background: #ef4444; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; white-space: nowrap;">🔥 HOTFIX</span>
                    <span style="background: #22c55e; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; white-space: nowrap;">✨ MELHORIA</span>
                    <span style="background: #f97316; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; white-space: nowrap;">🐛 BUG&nbsp;FIX</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                **v8.81** *(20/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎨 **Meu Dashboard**: Tela totalmente nova para construir dashboards personalizados
                - ➕ **Adicionar Widgets**: Construtor no topo para adicionar métricas
                - ⬆️⬇️ **Reordenar**: Mova widgets para cima ou para baixo
                - 🗑️ **Remover**: Exclua widgets que não precisa mais
                - 📊 **Templates**: Visão Executiva, Foco DEV, Foco QA
                - 💾 **Persistência**: Dashboard salvo em cookie
                - 🧹 **Sidebar Limpa**: Apenas logo e botão voltar na tela do dashboard
                
                **v8.80** *(20/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                
                **v8.79** *(20/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎯 **Consulta Personalizada**: Tela separada acessível pela sidebar
                - 🔍 **Filtros Avançados**: Pessoa, papel (DEV/QA/Relator), status, período
                - 📅 **Períodos Flexíveis**: Sprint atual, últimas semanas, mês, ou datas customizadas
                - 📊 **Tipos de Consulta**: Cards de pessoa, métricas, comparativos, bugs
                - 💾 **Salvar Consultas**: Guarde suas consultas favoritas para reusar
                - ⬅️ **Botão na Sidebar**: Acesso rápido abaixo dos filtros
                
                **v8.78** *(20/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎨 **Nova Aba: Meu Dashboard**: Crie dashboards personalizados!
                - 📊 **Catálogo de Métricas**: 30+ métricas disponíveis para escolher
                - 💾 **Persistência**: Dashboards salvos na sessão
                - 🎯 **Templates Rápidos**: Visão Executiva, Foco QA, Foco Dev
                - 📈 **Tipos de Visualização**: KPIs, gráficos, tabelas, heatmaps
                - 🔧 **Gerenciamento**: Criar, visualizar e excluir dashboards
                
                **v8.77** *(17/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🏢 **Aba Clientes Reposicionada**: Agora entre Suporte e Governança
                - 💰 **Desenvolvimento Pago**: Detecta cards pagos via label
                - 📊 **KPIs de Clientes**: Cards pagos, % conclusão, SP total
                - 👀 **Visão Geral do Time**: Padrão igual às abas QA/Dev/Suporte
                - 🎨 **Cards com Tag Pago**: Indicador visual 💰 PAGO nos cards
                - 📈 **Top Clientes Dev Pago**: Ranking de clientes com mais desenvolvimento pago
                
                **v8.76** *(17/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🏢 **Nova Aba Clientes**: Análise completa de clientes em aba dedicada
                - 📊 **Dados de Todos Projetos**: Aba Clientes ignora filtro de projeto (mostra tudo)
                - 🔗 **Link Compartilhável**: Copiar link direto para cliente específico
                - 💰 **Categorização**: Indicadores de desenvolvimento pago vs manutenção
                - 📅 **Timeline**: Gráfico de evolução de cards por mês para cada cliente
                - 🐛 **Top Bugs**: Ranking de clientes com mais bugs
                - 🔐 **Login via Cookie**: Método mais robusto usando CookieManager
                
                **v8.75** *(17/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🏢 **Análise por Cliente**: Nova seção em Visão Geral para pesquisar clientes
                - 📊 **Top Clientes**: Ranking dos clientes com mais cards
                - 👥 **Responsáveis**: Ver quem mais trata cada cliente (Relator, Dev, QA)
                - 📄 **Últimos Cards**: Histórico recente por cliente
                - 🔐 **Fix Login**: Corrigido localStorage usando parent.window
                
                **v8.74** *(17/04/2026)* <span style="background: #ef4444; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🔥</span>
                - 🔐 **Login via localStorage**: Substitui cookies por localStorage (mais confiável)
                - ⚡ **Auto-login**: JavaScript detecta email salvo e faz login automático
                - 🔄 **Persiste entre Refreshes**: Atualizar página mantém o login
                
                **v8.73** *(17/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔗 **URL Limpa**: Remove params da URL ao navegar (não polui mais)
                - 🚫 **Selectbox sem Params**: QA/Dev/Suporte não alteram mais a URL
                
                **v8.72** *(17/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔗 **URL Centralizada**: Constante `NINADASH_URL` para facilitar alterações
                - 🐛 **Fix TypeError**: Corrigido erro de comparação de datas com timezone
                - 🔄 **Cookies**: Novo domínio requer login na primeira vez (normal)
                
                **v8.71** *(17/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎨 **Novo Nome**: Dashboard de Qualidade e Decisão de Software
                - 🔗 **Nova URL**: ninadash.streamlit.app (mais curta e fácil)
                - 📊 **Barra de Progresso**: Visual da sprint com % concluído
                - 📈 **KPIs Simplificados**: 5 métricas essenciais (Cards, SP, Concluído, Bugs, Dias)
                - 🔬 **Métricas Técnicas**: FPY/DDP/Lead Time/Health/Fator K em expander separado
                - 📋 **Cards por Status**: Layout 2 colunas (mais espaço para leitura)
                - 🔄 **Botão Atualizar**: Integrado com indicador de última atualização
                - 📝 **Subtítulo Atualizado**: Foco em todo o time, não só QA
                
                **v8.70** *(17/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📦 **Expanders Padronizados**: Todas as seções agora podem ser ocultadas
                - 👤 **Fix Responsável**: Prioriza campo `responsavel` corretamente (não QA)
                - 📝 **Título Completo**: Aumentado de 50 para 80 caracteres
                - ✅ **Checkbox Ver Todos**: Voltou! Remove limite de 20 cards
                - 🎨 **Fonte Padronizada**: Cards com fonte consistente e legível
                - 📊 **Gráficos com Explicação**: Captions descritivos nos gráficos
                - 🔧 **Cards Aguardando Aberto**: Agora inicia expandido por padrão
                
                **v8.69** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📋 **Botão Copiar Link Padronizado**: Mesmo estilo do QA/Dev (height=45px)
                - 📜 **Cards Aguardando Ação em Expander**: Agora pode ocultar/expandir
                - 🔄 **Scroll Interno Funcional**: Usa components.html com scrolling=True
                - 🚫 **Removido Checkbox Ver Todos**: Substituído por scroll interno
                
                **v8.68** *(16/04/2026)* <span style="background: #ef4444; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🔥</span>
                - 🔧 **Fix Redirecionamento**: Corrigido bug que redirecionava para aba Dev
                - 📌 **Isolamento de Abas**: QA/Dev/Suporte não interferem mais entre si
                - 🔗 **Query Params**: Só atualiza URL quando a própria aba está ativa
                - ✅ Checkbox "Ver todos" não muda mais a aba ativa
                
                **v8.67** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📋 **Botão Copiar Link**: Movido para linha do título (não corta mais)
                - 📝 **Título nos Cards**: Cards Aguardando Ação agora mostram título
                - 📜 **Scroll em Ver Todos**: Scroll automático em listas longas (max 400px)
                - 👤 **Representante Cliente**: Cards onde você é Rep. Cliente ou Responsável
                - 🏷️ **Badge de Papel**: Mostra se você é QA, Rep. Cliente ou Responsável
                
                **v8.66** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📋 **Reordenação Expanders**: Prioriza cards de validação
                - 🔬 "Cards Aguardando Minha Validação" agora é o primeiro
                - ✅ "Cards Concluídos" movido para cima (mais visível)
                - 💬 "Cards Aguardando Resposta" fechado por padrão
                - 📊 "Onde estão meus cards?" fechado por padrão
                - 🔘 **Fix Botão Copiar**: Ajustado padding interno
                
                **v8.65** *(16/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔗 **Fix Copiar Link Suporte**: Botão funciona igual QA/Dev
                - ✅ Feedback visual: muda cor e mostra "Copiado!"
                - 📋 Usa mesmo padrão components.html
                
                **v8.64** *(16/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 👤 **Responsável nos Cards**: Mostra quem precisa agir
                - 📏 **Fix Copiar Link**: Botão alinhado com selectbox
                - 📝 Legenda explicativa em "Cards Aguardando Ação"
                
                **v8.63** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🕐 **Tempo de Atualização**: Mostra "há X min/h/d" nos cards
                - 🔬 **Cards Aguardando Minha Validação**: Nova seção para QA
                - 📏 **Fix Copiar Link**: Alinhado com seletor de pessoa
                - 🔍 **Filtro Aguardando**: Inclui mais variações de status
                - 📊 **QA Cards em Trabalho**: Ordenado por atualização
                
                **v8.62** *(16/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔧 **Fix UI Visão Geral**: Removido card desalinhado
                - 🤖 **Filtro Bots**: Automation for Jira removido do Top 15
                - 🔗 **Popup Links**: Cards Aguardando agora têm popup
                - ☑️ **Ver Todos**: Checkbox para expandir listas de cards
                - 📏 **Fix Botão Copiar**: Aumentado height do botão
                - ✅ **Métrica Concluídos**: Adicionada no resumo por pessoa
                - 📝 **Renomeado**: "Entregues" → "Concluídos"
                - 🔍 **Emoji Fix**: Validação Produção usa 🔍 (pendente)
                
                **v8.61** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 👥 **Ver Todos**: Opção no seletor para visão geral do time
                - 📊 **Gráficos na Visão Geral**: Pizza por projeto, barras por status, tipos
                - 🏆 **Cards Entregues**: Nova seção mostrando entregas por pessoa
                - 📅 **Filtro Padrão**: "Todo o período" para aba Suporte
                - 📋 **Top 15 Pessoas**: Ranking com barras visuais
                - ⏳ **Cards Aguardando**: Visão rápida de pendências por categoria
                
                **v8.60** *(16/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔗 **Fix Copiar Link**: Aba Suporte copia para clipboard
                - 📋 Mesmo padrão das abas QA e Dev
                - ✅ Feedback visual "Copiado!" após clicar
                
                **v8.59** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🏷️ **Cards com Título Completo**: Mostra nome do card
                - 🔖 **Tipo do Card**: Badge colorido (HOTFIX/BUG/TAREFA)
                - 🎨 Layout melhorado nas listagens
                - 📋 Mais informações visíveis em cada card
                
                **v8.58** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎯 **Aba Suporte Refatorada**: Igual QA/Dev
                - 👤 Seletor de pessoa (qualquer um pode ver qualquer pessoa)
                - 🔄 Busca TODOS os projetos (SD, QA, PB, VALPROD)
                - 📊 Gráfico "Onde estão meus cards?" por projeto/status
                - 🔗 Link compartilhável: ?aba=suporte&pessoa=Nome
                
                **v8.57** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎯 Nova ABA: Suporte/Implantação (v1)
                - 🆕 Projeto VALPROD adicionado ao sistema
                - 📊 Status específicos do PB mapeados
                
                **v8.56** *(16/04/2026)* <span style="background: #ef4444; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🔥</span>
                - 📊 **Sem Limite de Cards**: Removido limite de 500 cards
                - 🔄 Busca TODOS os cards do período selecionado
                - 🚀 Histórico completo disponível
                
                **v8.55** *(16/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🎨 **Fix Hover Popup**: CSS puro (funciona em todos locais)
                - 🔴 NinaDash: hover vermelho (#AF0C37) + texto branco
                - 🔵 Jira: hover azul (#3b82f6) + texto branco
                - ⬜ **Tela Loading**: Fundo branco + texto vermelho
                
                **v8.54** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎨 **Popup UX**: Hover vermelho no "Ver no NinaDash"
                - ⏳ **Tela de Loading**: Substituiu flash de login ao abrir
                - 🔄 Loading animado com logo NINA durante verificação
                
                **v8.53** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🚀 **Popup em TODAS aparições de cards**
                - 📊 QA: Em Trabalho, Reprovados, Impedidos, Validados
                - 👨‍💻 DEV: Code Review, Críticos, Resumo Semanal
                - 📋 Listagens, Filas e Cards do desenvolvedor
                - 🔗 18 locais atualizados com navegação NinaDash/Jira
                
                **v8.52** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🆕 **Popup de Navegação**: Clique em qualquer card exibe menu
                - 📊 Opção "Ver no NinaDash" (abre em nova aba)
                - 🔗 Opção "Abrir no Jira" (abre em nova aba)
                - 🎯 Aplicado em Cards Vinculados, Listagens e Resumos
                
                **v8.51** *(16/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔧 **Fix:** Botão "Copiar Link" alinhamento corrigido
                - 📝 **Novo:** Seção Descrição adicionada nos cards SD
                
                **v8.50** *(16/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🔄 **Novo:** Cards em Trabalho no resumo QA individual
                - ❌ **Novo:** Cards Reprovados listados no resumo
                - 🚫 **Novo:** Cards Impedidos listados no resumo
                - 📝 Resumo completo copiável (ideal para daily/retro)
                - 📊 Todas as categorias: em trabalho, reprovados, impedidos, validados
                
                **v8.49** *(15/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🚫 Cards Impedidos/Reprovados em QA e DEV
                - 🐛 Fix navegação entre QA/DEV
                
                **v8.48** *(15/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📈 Gráfico "Evolução da Semana"
                - 📝 Títulos completos em toda ferramenta
                
                **v8.47** *(15/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🐛 Dados históricos usam `resolutiondate`
                
                **v8.46** *(15/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📆 Seletor de semanas (2-4 semanas atrás)
                
                **v8.45** *(15/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📅 "Resumo da Semana" QA/DEV
                
                **v8.44** *(15/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🤝 **Novo:** Seção "Interação QA x DEV" na aba QA
                - 💪 **Novo:** Seção "Esforço do Time" na aba Liderança
                - 🤝 **Novo:** "Interação QA x DEV" visão Liderança
                - 🗓️ **UX:** Filtro padrão: PB=Todo período, SD/QA=Sprint Ativa
                - 🌟 Heatmap de interações, ranking de duplas, FPY por parceria
                - 📊 Carga por DEV e QA, throughput, velocidade do time
                
                **v8.43** *(15/04/2026)* <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 📏 **Fix:** Cards de métricas agora com altura uniforme
                - 📏 **Fix:** Legenda de tags não quebra mais linha
                
                **v8.42** *(15/04/2026)* <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎨 **UX:** Barra de release com cor sólida (remov. gradiente)
                - 📏 **UX:** Cards de métricas com tamanho uniforme
                - 📏 **UX:** Espaçamento corrigido em "Cards por Status"
                - 🏷️ **UX:** Tags visuais no histórico de versões
                
                **v8.41** <span style="background: #ef4444; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🔥</span>
                - 🔧 **Fix crítico:** Sprint agora pega a ATIVA, não a mais frequente
                - 📊 Filtra por `sprint_state == 'active'` antes de exibir
                - 🚨 **Release atrasada:** Barra vermelha + alerta visual
                - ⚡ **Release hoje:** Barra amarela com destaque
                - 📅 Cálculo correto de dias até release
                
                **v8.40** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎯 **Análise de Sprint (SD)** - Planejado vs Entregue!
                - 📊 Taxa de entrega da sprint com métricas visuais
                - 🚨 Cards fora do planejamento (Hotfix, PB, Criação direta)
                - 📋 Cards originados do PB por produto
                - ⏰ **PB: Aguarda Revisão** com alerta de SLA atrasado
                - 😴 **PB: Cards parados** - slider para definir dias sem atuação
                - 🏷️ **PB: Análise por Temas** - total por tema/cliente + cruzamento
                - ⏱️ **PB: Tempo de Vida por Importância** - Alto/Médio/Baixo
                - 🔎 **Filtros de comentários**: busca por texto + filtro por autor
                - 📦 Novos campos: Temas, Importância, SLA, Issue Links
                
                **v8.39** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📦 **Tags específicas por projeto** - PB tem tags de Produto!
                - ✅ PB: Decisão (verde) - aprovações e definições
                - ❓ PB: Dúvida (amarelo) - perguntas e questionamentos
                - 📋 PB: Requisito (azul) - escopo e critérios de aceite
                - 🤝 PB: Alinhamento (roxo) - reuniões e conversas
                - 🎨 SD/QA mantém tags de QA (Bug, Reprovação, etc.)
                
                **v8.38** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🐛 Detecção de #bug (hashtag) - padrão do QA
                - 🔍 +50 novos padrões de bugs adicionados
                - 🌐 Detecta problemas de tradução, UX, interface
                - ⚠️ Detecta "sistema retornou", "api retornou", "devTools"
                - 📝 Detecta "ao tentar", "ao clicar", "ao criar", etc.
                
                **v8.37** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🔍 Filtros interativos para tipos de comentários
                - 🐛 Detecção de bugs ampliada (80+ padrões)
                - 🔄 Nova categoria: Retorno DEV (ciano)
                - 📊 Checkboxes para filtrar: Bug, Reprovação, Impedimento, Retorno, Outros
                - 🎨 Visual ainda mais distinto por categoria
                - 📈 Contador de comentários exibidos vs total
                
                **v8.36** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🎨 Visual de comentários completamente reformulado
                - 🐛 Bug: fundo vermelho claro + borda vermelha + badge numerado
                - ❌ Reprovação: fundo laranja claro + borda laranja + badge numerado  
                - 🚫 Impedimento: fundo roxo claro + borda roxa + badge numerado
                - 📍 Contexto temporal: "Antes Reprovação #1", "Após Bug #2"
                - 📊 Legenda visual no topo dos comentários
                
                **v8.35** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🧠 Comentários inteligentes: filtra automações do GitHub
                - 🐛 Destaca comentários de bugs (borda vermelha)
                - ❌ Destaca comentários de reprovação (borda laranja)
                - 📊 Mostra contagem de bugs/reprovações no título
                - ℹ️ Informa quantos comentários de automação foram ocultados
                
                **v8.34** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📦 Refatoração da aba Produto (PB) a pedido da Ellen
                - 🚫 PB: Hotfix removido (não passa por produto)
                - 📅 Filtro: "Todo o período" agora é padrão
                - 📝 PB: Descrição, Labels, Componentes e Epic nos cards
                - 👤 PB: Mostra Responsável no card pesquisado
                
                **v8.33** <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔧 Fix: Login persistente restaurado corretamente
                - 🍪 Usa get_all() para aguardar cookies carregarem
                - ⚡ Corrigido timing assíncrono do CookieManager
                
                **v8.32** <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔧 Fix: CachedWidgetWarning no CookieManager
                - 🍪 Removido @st.cache_resource (widgets não podem ser cacheados)
                - 🛡️ Tratamento de erros em todas operações com cookies
                
                **v8.31** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🔒 Login persistente agora usa cookies (mais confiável)
                - 🍪 Biblioteca extra-streamlit-components para gerenciar cookies
                - ⏰ Cookie expira em 30 dias
                
                **v8.30** <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔧 Fix: Login persistente agora funciona corretamente
                - 🔒 Mantém sessão entre atualizações e novas abas
                
                **v8.29** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 🔒 "Lembrar de mim" - login persistente no navegador
                - 🔓 Não precisa mais fazer login toda vez que atualiza
                - 🧹 Logout limpa o login salvo
                
                **v8.28** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 📋 PB: Mostra "Relator" em vez de "Criado por"
                - 📋 PB: Adiciona campo "Resolução/Roteiro" em destaque
                - 🔍 Melhoria na visão de produto para itens de backlog
                
                **v8.27** <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🔧 Fix: Removido tooltips customizados que quebravam layout
                - ℹ️ Mantido help nativo do Streamlit (ícone ?) nos st.metric
                
                **v8.26** <span style="background: #22c55e; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">✨</span>
                - 💡 Tooltips em todas as métricas (hover para explicação)
                - ℹ️ FPY, DDP, Fator K, Lead Time, Health Score explicados
                - 📊 Captions explicativos em Throughput e Produtividade
                
                **v8.25** <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🧹 Fix: URL limpa - remove params cruzados QA/Dev
                - 🧹 Clear total ao voltar para visão geral
                
                **v8.24** <span style="background: #f97316; color: white; padding: 1px 6px; border-radius: 3px; font-size: 10px;">🐛</span>
                - 🧹 Fix: Limpa parâmetros da URL ao voltar para visão geral
                
                **v8.23** *(14/04/2026)*
                - 🚀 Navegação direta via link compartilhado
                - ⬅️ Botão "Ver Dashboard Completo" para voltar
                
                **v8.22** *(14/04/2026)*
                - 🔗 Fix: Botão "Copiar Link" para QA/Dev (igual ao card individual)
                - ✅ URL correta do Streamlit Cloud
                
                **v8.21** *(14/04/2026)*
                - 🔗 Links compartilháveis para QA e Dev individuais
                - 📊 Novas métricas: throughput, eficiência, comparativo
                - 📈 Gráficos de tendência individual
                - 🎯 URL params: ?aba=qa&qa=Nome ou ?aba=dev&dev=Nome
                
                **v8.20** *(14/04/2026)*
                - 📦 Filtro Produto acima do rodapé
                
                **v8.19** *(13/04/2026)*
                - 📋 Changelog na sidebar
                
                **v8.18** *(13/04/2026)*
                - ✅ Botão "Copiar Link" funcionando
                
                **v8.17** *(13/04/2026)*
                - 🔧 Fix erro React #231
                
                **v8.16** *(13/04/2026)*
                - 🔧 Fix busca (colunas iguais)
                
                **v8.15** *(13/04/2026)*
                - 🔔 Toast ao copiar link
                
                **v8.14** *(13/04/2026)*
                - 🎨 KPIs em cards estilizados
                
                **v8.13** *(13/04/2026)*
                - ⌨️ Busca funciona com Enter
                
                **v8.12** *(13/04/2026)*
                - ⚠️ Indicador SP estimado
                
                **v8.11** *(12/04/2026)*
                - 🔍 Botão "Buscar" explícito
                
                **v8.10** *(12/04/2026)*
                - 🏠 Logo centralizada, UX
                
                **v8.9** *(12/04/2026)*
                - 💬 Comentários do Jira
                - 📦 Conteúdo por projeto
                
                **v8.8** *(11/04/2026)*
                - 🔗 Card linkages
                - 🔍 Busca simplificada
                
                **v8.7** *(10/04/2026)*
                - ⬅️ Botão voltar sidebar
                - 🎨 Design refinado
                
                **v8.6** *(09/04/2026)*
                - 📱 Sidebar refatorada
                - 📤 Link compartilhável
                
                **v8.5** *(08/04/2026)*
                - 🔍 Busca de card individual
                - 📊 Painel completo do card
                """, unsafe_allow_html=True)
        
        # Captura query params para navegação direta (QA/Dev/Suporte individual)
        aba_param = st.query_params.get("aba", None)
        qa_param = st.query_params.get("qa", None)
        dev_param = st.query_params.get("dev", None)
        pessoa_param = st.query_params.get("pessoa", None)
        
        # NAVEGAÇÃO DIRETA via link compartilhado
        if aba_param == "suporte" and pessoa_param:
            # Mostra diretamente a aba Suporte com a pessoa selecionada
            col_header, col_voltar = st.columns([4, 1])
            with col_header:
                st.markdown(f"### 🔗 Link Compartilhado: Suporte/Implantação")
            with col_voltar:
                if st.button("⬅️ Ver Dashboard Completo", use_container_width=True, key="btn_voltar_suporte"):
                    st.query_params.clear()
                    st.rerun()
            st.markdown("---")
            aba_suporte_implantacao(df_todos)
            return
        
        if aba_param == "qa" and qa_param:
            # Mostra diretamente a aba QA com o colaborador selecionado
            col_header, col_voltar = st.columns([4, 1])
            with col_header:
                st.markdown(f"### 🔗 Link Compartilhado: Métricas de QA")
            with col_voltar:
                if st.button("⬅️ Ver Dashboard Completo", use_container_width=True, key="btn_voltar_qa"):
                    st.query_params.clear()
                    st.rerun()
            st.markdown("---")
            aba_qa(df)
            return
        
        if aba_param == "dev" and dev_param:
            # Mostra diretamente a aba Dev com o colaborador selecionado
            col_header, col_voltar = st.columns([4, 1])
            with col_header:
                st.markdown(f"### 🔗 Link Compartilhado: Métricas de Dev")
            with col_voltar:
                if st.button("⬅️ Ver Dashboard Completo", use_container_width=True, key="btn_voltar_dev"):
                    st.query_params.clear()
                    st.rerun()
            st.markdown("---")
            aba_dev(df)
            return
        
        # Abas condicionais por projeto (fluxo normal)
        if projeto == "PB":
            # Projeto PB: Aba de Backlog como foco principal
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📋 Backlog",
                "📊 Visão Geral",
                "📦 Produto",
                "📈 Histórico",
                "ℹ️ Sobre"
            ])
            
            with tab1:
                aba_backlog(df)
            
            with tab2:
                aba_visao_geral(df, ultima_atualizacao)
            
            with tab3:
                aba_produto(df)
            
            with tab4:
                aba_historico(df)
            
            with tab5:
                aba_sobre()
        
        elif projeto == "VALPROD":
            # Projeto VALPROD: Foco em Validação em Produção + Suporte
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🎯 Suporte/Implantação",
                "📊 Visão Geral",
                "📋 Governança",
                "📈 Histórico",
                "ℹ️ Sobre"
            ])
            
            with tab1:
                aba_suporte_implantacao(df_todos)
            
            with tab2:
                aba_visao_geral(df, ultima_atualizacao)
            
            with tab3:
                aba_governanca(df)
            
            with tab4:
                aba_historico(df)
            
            with tab5:
                aba_sobre()
        
        else:
            # Projetos SD e QA: Abas completas com QA/Dev + Clientes + Suporte
            tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
                "📊 Visão Geral",
                "🔬 QA",
                "👨‍💻 Dev",
                "🎯 Suporte/Implantação",
                "🏢 Clientes",
                "📋 Governança",
                "📦 Produto",
                "📈 Histórico",
                "🎯 Liderança",
                "ℹ️ Sobre"
            ])
            
            with tab1:
                aba_visao_geral(df, ultima_atualizacao)
            
            with tab2:
                aba_qa(df)
            
            with tab3:
                aba_dev(df)
            
            with tab4:
                aba_suporte_implantacao(df_todos)
            
            with tab5:
                aba_clientes(df_todos)
            
            with tab6:
                aba_governanca(df)
            
            with tab7:
                aba_produto(df)
            
            with tab8:
                aba_historico(df)
            
            with tab9:
                aba_lideranca(df)
            
            with tab10:
                aba_sobre()


if __name__ == "__main__":
    main()
