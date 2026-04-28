"""
🔗 JIRA_API - Integração com Jira Cloud

Acesso às APIs do Jira Cloud, gerenciamento de cache, busca de cards e histórico.
"""

import streamlit as st
import requests
from datetime import datetime
from typing import Tuple, Optional, List, Dict

from modulos.config import (
    JIRA_BASE_URL, CUSTOM_FIELDS, STATUS_FLOW, STATUS_NOMES, STATUS_CORES, 
    TRADUCAO_LINK_TYPES, REGRAS
)
from modulos.utils import traduzir_link, get_secrets, calcular_dias_necessarios_validacao, avaliar_janela_validacao, link_jira


# ==============================================================================
# BUSCA DADOS JIRA COM CACHE
# ==============================================================================

@st.cache_data(ttl=300, show_spinner=False)
def buscar_dados_jira_cached(projeto: str, jql: str) -> Tuple[Optional[List[Dict]], datetime]:
    """Busca dados do Jira com cache."""
    secrets = get_secrets()
    if not secrets["email"] or not secrets["token"]:
        return None, datetime.now()
    
    base_url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
    headers = {"Accept": "application/json"}
    
    fields = [
        "key", "summary", "status", "issuetype", "assignee", "created", "updated",
        "resolutiondate", "priority", "project", "labels", "reporter", "resolution",
        "issuelinks",  # Links para rastrear origem do PB
        CUSTOM_FIELDS["story_points"],
        CUSTOM_FIELDS["story_points_alt"],
        CUSTOM_FIELDS["sprint"],
        CUSTOM_FIELDS["bugs_encontrados"],
        CUSTOM_FIELDS["complexidade_teste"],
        CUSTOM_FIELDS["qa_responsavel"],
        CUSTOM_FIELDS["produto"],
        CUSTOM_FIELDS["temas"],
        CUSTOM_FIELDS["importancia"],
        CUSTOM_FIELDS["sla_status"],
        CUSTOM_FIELDS["ambiente_desenvolvido"],  # Develop, Homologação, Produção
    ]
    
    all_issues = []
    next_page_token = None
    
    try:
        while True:
            params = {
                "jql": jql,
                "maxResults": 100,
                "fields": ",".join(fields)
            }
            if next_page_token:
                params["nextPageToken"] = next_page_token
            
            response = requests.get(
                base_url, 
                headers=headers, 
                params=params, 
                auth=(secrets["email"], secrets["token"]),
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            all_issues.extend(data.get("issues", []))
            
            next_page_token = data.get("nextPageToken")
            # Para quando não há mais páginas (sem limite artificial)
            if not next_page_token:
                break
        
        return all_issues, datetime.now()
    
    except Exception as e:
        st.error(f"Erro ao conectar com Jira: {e}")
        return None, datetime.now()


# ==============================================================================
# VERIFICAR SPRINT FUTURA
# ==============================================================================

@st.cache_data(ttl=60, show_spinner=False)
def verificar_sprint_futura(projeto: str) -> Optional[Dict]:
    """
    Verifica se existe sprint futura aguardando início para o projeto.
    
    Busca apenas 1 card com sprint futura para detectar existência.
    Retorna informações da sprint futura se existir, None caso contrário.
    
    Args:
        projeto: Código do projeto (SD, QA, PB)
    
    Returns:
        Dict com {name, state, startDate, endDate} ou None
    """
    secrets = get_secrets()
    if not secrets["email"] or not secrets["token"]:
        return None
    
    base_url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
    headers = {"Accept": "application/json"}
    
    jql = f'project = {projeto} AND sprint in futureSprints() ORDER BY created DESC'
    
    try:
        params = {
            "jql": jql,
            "maxResults": 1,
            "fields": CUSTOM_FIELDS["sprint"]
        }
        
        response = requests.get(
            base_url, 
            headers=headers, 
            params=params, 
            auth=(secrets["email"], secrets["token"]),
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        issues = data.get("issues", [])
        if not issues:
            return None
        
        # Extrair informações da sprint futura
        sprint_field = issues[0].get("fields", {}).get(CUSTOM_FIELDS["sprint"], [])
        if not sprint_field:
            return None
        
        # Encontrar sprint com state='future'
        for sprint in sprint_field:
            if sprint.get("state") == "future":
                return {
                    "name": sprint.get("name", ""),
                    "state": sprint.get("state", ""),
                    "startDate": sprint.get("startDate"),
                    "endDate": sprint.get("endDate"),
                    "id": sprint.get("id")
                }
        
        return None
    
    except Exception:
        return None


# ==============================================================================
# BUSCA CARD ESPECÍFICO COM LINKS E HISTÓRICO
# ==============================================================================

@st.cache_data(ttl=300, show_spinner=False)
def buscar_card_especifico(ticket_id: str) -> Tuple[Optional[Dict], Optional[List[Dict]], Optional[List[Dict]], Optional[List[Dict]]]:
    """
    Busca um card específico pelo ID, sem filtros de período.
    Retorna: (issue, links, comentarios, historico_transicoes)
    """
    secrets = get_secrets()
    if not secrets["email"] or not secrets["token"]:
        return None, None, None, None
    
    try:
        # Busca o card específico com links e changelog
        base_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}"
        headers = {"Accept": "application/json"}
        
        fields = [
            "key", "summary", "status", "issuetype", "assignee", "created", "updated",
            "resolutiondate", "priority", "project", "labels", "issuelinks", "parent", "subtasks",
            "description", "reporter", "resolution",
            CUSTOM_FIELDS["story_points"],
            CUSTOM_FIELDS["story_points_alt"],
            CUSTOM_FIELDS["sprint"],
            CUSTOM_FIELDS["bugs_encontrados"],
            CUSTOM_FIELDS["complexidade_teste"],
            CUSTOM_FIELDS["qa_responsavel"],
            CUSTOM_FIELDS["produto"],
            CUSTOM_FIELDS["ambiente_desenvolvido"],  # Develop, Homologação, Produção
        ]
        
        # Adiciona changelog para histórico de transições
        params = {"fields": ",".join(fields), "expand": "renderedFields,changelog"}
        
        response = requests.get(
            base_url,
            headers=headers,
            params=params,
            auth=(secrets["email"], secrets["token"]),
            timeout=60
        )
        
        if response.status_code == 404:
            return None, None, None, None
        
        response.raise_for_status()
        issue = response.json()
        
        # Extrai os links do card
        links = []
        fields_data = issue.get('fields', {})
        
        # Links diretos (issuelinks)
        issue_links = fields_data.get('issuelinks', [])
        for link in issue_links:
            link_type = traduzir_link(link.get('type', {}).get('name', 'Relacionado'))
            
            # Link de saída (outwardIssue)
            if 'outwardIssue' in link:
                linked = link['outwardIssue']
                links.append({
                    'tipo': link_type,
                    'direcao': traduzir_link(link.get('type', {}).get('outward', 'relacionado a')),
                    'ticket_id': linked.get('key', ''),
                    'titulo': linked.get('fields', {}).get('summary', ''),
                    'status': linked.get('fields', {}).get('status', {}).get('name', ''),
                    'link': f"{JIRA_BASE_URL}/browse/{linked.get('key', '')}",
                    'nivel': 1  # Link direto (primeiro nível)
                })
            
            # Link de entrada (inwardIssue)
            if 'inwardIssue' in link:
                linked = link['inwardIssue']
                links.append({
                    'tipo': link_type,
                    'direcao': traduzir_link(link.get('type', {}).get('inward', 'relacionado a')),
                    'ticket_id': linked.get('key', ''),
                    'titulo': linked.get('fields', {}).get('summary', ''),
                    'status': linked.get('fields', {}).get('status', {}).get('name', ''),
                    'link': f"{JIRA_BASE_URL}/browse/{linked.get('key', '')}",
                    'nivel': 1  # Link direto (primeiro nível)
                })
        
        # Parent (Epic/Story pai)
        parent = fields_data.get('parent')
        if parent:
            links.append({
                'tipo': 'Parent',
                'direcao': 'é filho de',
                'ticket_id': parent.get('key', ''),
                'titulo': parent.get('fields', {}).get('summary', ''),
                'status': parent.get('fields', {}).get('status', {}).get('name', ''),
                'link': f"{JIRA_BASE_URL}/browse/{parent.get('key', '')}"
            })
        
        # Subtasks (tarefas filhas)
        subtasks = fields_data.get('subtasks', [])
        for sub in subtasks:
            links.append({
                'tipo': 'Subtarefa',
                'direcao': 'é pai de',
                'ticket_id': sub.get('key', ''),
                'titulo': sub.get('fields', {}).get('summary', ''),
                'status': sub.get('fields', {}).get('status', {}).get('name', ''),
                'link': f"{JIRA_BASE_URL}/browse/{sub.get('key', '')}",
                'nivel': 1
            })
        
        # ===== BUSCA LINKS TRANSITIVOS (SEGUNDO NÍVEL) =====
        # Para cada card vinculado, busca seus links também
        links_primeiro_nivel = [l['ticket_id'] for l in links]
        links_transitivos = []
        
        for link_info in links:
            try:
                linked_ticket = link_info['ticket_id']
                if not linked_ticket:
                    continue
                
                # Busca os links do card vinculado (sem recursão adicional)
                linked_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{linked_ticket}"
                linked_params = {"fields": "issuelinks,summary,status"}
                
                linked_response = requests.get(
                    linked_url,
                    headers=headers,
                    params=linked_params,
                    auth=(secrets["email"], secrets["token"]),
                    timeout=30
                )
                
                if linked_response.status_code == 200:
                    linked_data = linked_response.json()
                    linked_fields = linked_data.get('fields', {})
                    linked_issue_links = linked_fields.get('issuelinks', [])
                    
                    for sub_link in linked_issue_links:
                        sub_type = traduzir_link(sub_link.get('type', {}).get('name', 'Relacionado'))
                        
                        # Link de saída
                        if 'outwardIssue' in sub_link:
                            sub_linked = sub_link['outwardIssue']
                            sub_key = sub_linked.get('key', '')
                            # Não adiciona se já está nos links diretos ou é o card original
                            if sub_key and sub_key != ticket_id and sub_key not in links_primeiro_nivel:
                                links_transitivos.append({
                                    'tipo': sub_type,
                                    'direcao': traduzir_link(sub_link.get('type', {}).get('outward', 'relacionado a')),
                                    'ticket_id': sub_key,
                                    'titulo': sub_linked.get('fields', {}).get('summary', ''),
                                    'status': sub_linked.get('fields', {}).get('status', {}).get('name', ''),
                                    'link': f"{JIRA_BASE_URL}/browse/{sub_key}",
                                    'nivel': 2,  # Segundo nível (transitivo)
                                    'via': linked_ticket  # Indica por qual card chegou
                                })
                        
                        # Link de entrada
                        if 'inwardIssue' in sub_link:
                            sub_linked = sub_link['inwardIssue']
                            sub_key = sub_linked.get('key', '')
                            if sub_key and sub_key != ticket_id and sub_key not in links_primeiro_nivel:
                                links_transitivos.append({
                                    'tipo': sub_type,
                                    'direcao': traduzir_link(sub_link.get('type', {}).get('inward', 'relacionado a')),
                                    'ticket_id': sub_key,
                                    'titulo': sub_linked.get('fields', {}).get('summary', ''),
                                    'status': sub_linked.get('fields', {}).get('status', {}).get('name', ''),
                                    'link': f"{JIRA_BASE_URL}/browse/{sub_key}",
                                    'nivel': 2,
                                    'via': linked_ticket
                                })
            except Exception:
                continue  # Falha silenciosa para links transitivos
        
        # Remove duplicatas dos transitivos
        seen = set(l['ticket_id'] for l in links)
        for lt in links_transitivos:
            if lt['ticket_id'] not in seen:
                links.append(lt)
                seen.add(lt['ticket_id'])
        
        # Busca comentários do card
        comentarios = []
        try:
            comments_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}/comment"
            comments_response = requests.get(
                comments_url,
                headers=headers,
                auth=(secrets["email"], secrets["token"]),
                timeout=30
            )
            if comments_response.status_code == 200:
                comments_data = comments_response.json()
                for comment in comments_data.get('comments', []):
                    author = comment.get('author', {})
                    author_type = author.get('accountType', 'user')
                    
                    # Filtra comentários de automações (bots, apps)
                    if author_type == 'app':
                        continue
                    
                    # Também ignora se o displayName contém patterns de automação
                    display_name = author.get('displayName', '')
                    bot_patterns = ['bot', 'automation', 'jira', 'webhook', 'integration', 'service']
                    is_bot = any(pattern.lower() in display_name.lower() for pattern in bot_patterns)
                    if is_bot:
                        continue
                    
                    # Extrai texto do corpo do comentário (formato ADF)
                    body = comment.get('body', {})
                    body_text = extrair_texto_adf(body)
                    
                    if body_text.strip():
                        comentarios.append({
                            'autor': display_name,
                            'avatar': author.get('avatarUrls', {}).get('24x24', ''),
                            'data': comment.get('created', ''),
                            'texto': body_text
                        })
        except Exception:
            pass  # Comentários são opcionais
        
        # ===== EXTRAI HISTÓRICO DE TRANSIÇÕES DO CHANGELOG =====
        historico_transicoes = extrair_historico_transicoes(issue, ticket_id)
        
        return issue, links, comentarios, historico_transicoes
    
    except Exception as e:
        st.error(f"Erro ao buscar card: {e}")
        return None, None, None, None


# ==============================================================================
# EXTRAI HISTÓRICO DE TRANSIÇÕES DO CHANGELOG
# ==============================================================================

def extrair_historico_transicoes(issue: Dict, ticket_id: str) -> List[Dict]:
    """
    Extrai o histórico completo de transições de status do changelog do Jira.
    
    Retorna lista ordenada cronologicamente com:
    - data: datetime da transição
    - de: status anterior
    - para: novo status
    - autor: quem fez a mudança
    - tipo: 'criacao', 'transicao', 'atribuicao', etc
    - campo: nome do campo alterado
    - tempo_no_status: dias que ficou no status anterior
    """
    historico = []
    
    try:
        fields = issue.get('fields', {})
        changelog = issue.get('changelog', {})
        
        # 1. Primeiro evento: Criação do card
        data_criacao_str = fields.get('created', '')
        reporter = fields.get('reporter', {})
        
        if data_criacao_str:
            try:
                data_criacao = datetime.fromisoformat(data_criacao_str.replace('Z', '+00:00')).replace(tzinfo=None)
            except:
                data_criacao = datetime.now()
            
            historico.append({
                'data': data_criacao,
                'de': None,
                'para': 'Criado',
                'autor': reporter.get('displayName', 'Sistema') if reporter else 'Sistema',
                'tipo': 'criacao',
                'campo': 'Card',
                'detalhes': f"Card {ticket_id} criado",
                'icone': gerar_icone_tabler('file', tamanho=32, cor='#22c55e'),
                'cor': '#22c55e'
            })
        
        # 2. Processa todas as entradas do changelog
        histories = changelog.get('histories', [])
        
        for entry in histories:
            entry_date_str = entry.get('created', '')
            author = entry.get('author', {})
            author_name = author.get('displayName', 'Sistema') if author else 'Sistema'
            
            try:
                entry_date = datetime.fromisoformat(entry_date_str.replace('Z', '+00:00')).replace(tzinfo=None)
            except:
                continue
            
            items = entry.get('items', [])
            
            for item in items:
                field = item.get('field', '')
                field_type = item.get('fieldtype', '')
                from_value = item.get('fromString', '') or ''
                to_value = item.get('toString', '') or ''
                
                # Transições de STATUS são as mais importantes
                if field.lower() == 'status':
                    # Determina ícone e cor baseado no status de destino
                    icone, cor = obter_icone_status(to_value)
                    
                    historico.append({
                        'data': entry_date,
                        'de': from_value if from_value else 'Sem status',
                        'para': to_value if to_value else 'Desconhecido',
                        'autor': author_name,
                        'tipo': 'transicao',
                        'campo': 'Status',
                        'detalhes': f"{from_value or 'Início'} → {to_value}",
                        'icone': icone,
                        'cor': cor
                    })
                
                # Também captura mudanças importantes de outros campos
                elif field.lower() in ['assignee', 'responsável']:
                    historico.append({
                        'data': entry_date,
                        'de': from_value if from_value else 'Não atribuído',
                        'para': to_value if to_value else 'Não atribuído',
                        'autor': author_name,
                        'tipo': 'atribuicao',
                        'campo': 'Responsável',
                        'detalhes': f"Atribuído: {from_value or 'Ninguém'} → {to_value or 'Ninguém'}",
                        'icone': gerar_icone_tabler('user-check', tamanho=32, cor='#6366f1'),
                        'cor': '#6366f1'
                    })
                
                elif 'qa' in field.lower() or field == CUSTOM_FIELDS.get('qa_responsavel', ''):
                    historico.append({
                        'data': entry_date,
                        'de': from_value if from_value else 'Não atribuído',
                        'para': to_value if to_value else 'Não atribuído',
                        'autor': author_name,
                        'tipo': 'qa_atribuicao',
                        'campo': 'QA Responsável',
                        'detalhes': f"QA: {from_value or 'Ninguém'} → {to_value or 'Ninguém'}",
                        'icone': gerar_icone_tabler('test-pipe', tamanho=32, cor='#8b5cf6'),
                        'cor': '#8b5cf6'
                    })
                
                elif field.lower() == 'sprint':
                    historico.append({
                        'data': entry_date,
                        'de': from_value if from_value else 'Sem sprint',
                        'para': to_value if to_value else 'Removido da sprint',
                        'autor': author_name,
                        'tipo': 'sprint',
                        'campo': 'Sprint',
                        'detalhes': f"Sprint: {from_value or 'Nenhuma'} → {to_value or 'Removido'}",
                        'icone': gerar_icone_tabler('target', tamanho=32, cor='#f59e0b'),
                        'cor': '#f59e0b'
                    })
                
                elif 'story point' in field.lower() or field == CUSTOM_FIELDS.get('story_points', ''):
                    historico.append({
                        'data': entry_date,
                        'de': from_value if from_value else '0',
                        'para': to_value if to_value else '0',
                        'autor': author_name,
                        'tipo': 'estimativa',
                        'campo': 'Story Points',
                        'detalhes': f"SP: {from_value or '0'} → {to_value or '0'}",
                        'icone': gerar_icone_tabler('chart-bar', tamanho=32, cor='#3b82f6'),
                        'cor': '#3b82f6'
                    })
                
                elif 'bug' in field.lower() or field == CUSTOM_FIELDS.get('bugs_encontrados', ''):
                    historico.append({
                        'data': entry_date,
                        'de': from_value if from_value else '0',
                        'para': to_value if to_value else '0',
                        'autor': author_name,
                        'tipo': 'bugs',
                        'campo': 'Bugs Encontrados',
                        'detalhes': f"Bugs: {from_value or '0'} → {to_value or '0'}",
                        'icone': gerar_icone_tabler('bug', tamanho=32, cor='#ef4444'),
                        'cor': '#ef4444'
                    })
                
                elif field.lower() == 'resolution':
                    cor_resolucao = '#22c55e' if to_value else '#f97316'
                    historico.append({
                        'data': entry_date,
                        'de': from_value if from_value else 'Sem resolução',
                        'para': to_value if to_value else 'Reaberto',
                        'autor': author_name,
                        'tipo': 'resolucao',
                        'campo': 'Resolução',
                        'detalhes': f"Resolução: {to_value or 'Reaberto'}",
                        'icone': gerar_icone_tabler('shield-check', tamanho=32, cor=cor_resolucao) if to_value else gerar_icone_tabler('loader', tamanho=32, cor=cor_resolucao),
                        'cor': cor_resolucao
                    })
        
        # 3. Ordena por data
        historico.sort(key=lambda x: x['data'])
        
        # 4. Calcula tempo em cada status
        for i, evento in enumerate(historico):
            if i < len(historico) - 1:
                proximo = historico[i + 1]
                delta = proximo['data'] - evento['data']
                evento['duracao_dias'] = delta.days
                evento['duracao_horas'] = int(delta.total_seconds() / 3600)
            else:
                # Último evento - calcula até agora
                delta = datetime.now() - evento['data']
                evento['duracao_dias'] = delta.days
                evento['duracao_horas'] = int(delta.total_seconds() / 3600)
        
        return historico
    
    except Exception as e:
        # Em caso de erro, retorna lista vazia
        return []


# ==============================================================================
# EXTRAI TEXTO DE ADF (ATLASSIAN DOCUMENT FORMAT)
# ==============================================================================

def extrair_texto_adf(adf_content: Dict) -> str:
    """Extrai texto plano de conteúdo ADF (Atlassian Document Format)."""
    if not adf_content:
        return ""
    
    texto = []
    
    def extrair_recursivo(node):
        if isinstance(node, dict):
            if node.get('type') == 'text':
                texto.append(node.get('text', ''))
            elif node.get('type') == 'hardBreak':
                texto.append('\n')
            elif node.get('type') == 'mention':
                texto.append(f"@{node.get('attrs', {}).get('text', '')}")
            
            for child in node.get('content', []):
                extrair_recursivo(child)
        elif isinstance(node, list):
            for item in node:
                extrair_recursivo(item)
    
    extrair_recursivo(adf_content)
    return ''.join(texto).strip()


# ==============================================================================
# GERADORES DE ÍCONES E BADGES
# ==============================================================================

def gerar_icone_tabler(nome_icone: str, tamanho: int = 24, cor: str = "currentColor", stroke_width: float = 2) -> str:
    """
    Gera ícone Tabler Icons em formato SVG inline.
    
    Ícones disponíveis: list, clipboard, code, check, x, loader, alert-circle, clock,
    search, user, users, settings, layout, grid, bar-chart, line-chart, trending-up,
    trending-down, inbox, archive, trash, edit, plus, minus, folder, file, database,
    server, wifi, wifi-off, eye, eye-off, lock, unlock, download, upload, share, link,
    bookmark, star, heart, message, send, phone, mail, bug, shield-check, test-pipe,
    user-check, circle-check, circle-x, git-branch, rocket, target, calendar, filter,
    """
    
    # Biblioteca de ícones Tabler em SVG (simplificados)
    icones = {
        'list': '<path d="M9 6h11M9 12h11M9 18h11M5 6v.01M5 12v.01M5 18v.01"/>',
        'check': '<path d="M5 12l4 4l6 -6"/>',
        'x': '<path d="M18 6l-12 12M6 6l12 12"/>',
        'circle-check': '<circle cx="12" cy="12" r="9"/><path d="M9 12l2 2l4 -4"/>',
        'circle-x': '<circle cx="12" cy="12" r="9"/><path d="M15 9l-6 6M9 9l6 6"/>',
        'loader': '<path d="M12 3v6m4.22 -1.22l-4.24 4.24M21 12h-6m1.22 4.22l-4.24 -4.24M12 21v-6M4.22 16.22l4.24 -4.24M3 12h6M7.22 7.22l4.24 4.24"/>',
        'alert-circle': '<circle cx="12" cy="12" r="9"/><path d="M12 8v4M12 16v.01"/>',
        'clock': '<circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 16 14"/>',
        'user': '<path d="M8 7a4 4 0 1 0 8 0a4 4 0 0 0 -8 0M6 21v-2a4 4 0 0 1 4 -4h4a4 4 0 0 1 4 4v2"/>',
        'users': '<path d="M9 7a4 4 0 1 0 8 0a4 4 0 0 0 -8 0M3 21v-2a4 4 0 0 1 4 -4h4a4 4 0 0 1 4 4v2M15 16a4 4 0 0 1 4 -4h2a4 4 0 0 1 4 4v2"/>',
        'user-check': '<path d="M8 7a4 4 0 1 0 8 0a4 4 0 0 0 -8 0M6 21v-2a4 4 0 0 1 4 -4h4a4 4 0 0 1 4 4v2m1 -8l4 4l4 -4"/>',
        'code': '<polyline points="7 8 3 12 7 16M17 8 21 12 17 16M14 4 10 20"/>',
        'git-branch': '<line x1="12" y1="5" x2="12" y2="19"/><path d="M7 12a5 5 0 0 0 5 5 5 5 0 0 0 5 -5"/>',
        'database': '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14a8 3 0 0 0 8 3a8 3 0 0 0 8 -3V5M4 12a8 3 0 0 0 8 3 8 3 0 0 0 8 -3"/>',
        'rocket': '<path d="M4 13c.755 -1.478 2.559 -2.427 4.5 -2.427c2.3 0 4.322 1.453 5.186 3.427c.863 -1.974 2.886 -3.427 5.314 -3.427c1.941 0 3.745 .949 4.5 2.427M7 19c-.577 .962 -1.607 1.6 -2.8 1.6c-1.8 0 -3.2 -1.2 -3.2 -2.8s1.4 -2.8 3.2 -2.8c1.193 0 2.223 .638 2.8 1.6M17 19c.577 .962 1.607 1.6 2.8 1.6c1.8 0 3.2 -1.2 3.2 -2.8s-1.4 -2.8 -3.2 -2.8c-1.193 0 -2.223 .638 -2.8 1.6"/>',
        'target': '<circle cx="12" cy="12" r="1"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="9"/>',
        'trending-up': '<polyline points="3 17 9 11 13 15 21 7M15 7h6v6"/>',
        'trending-down': '<polyline points="3 7 9 13 13 9 21 17M15 17h6v-6"/>',
        'bug': '<path d="M9 9v-1a3 3 0 0 1 6 0v1M3 11a6 6 0 0 0 6 6h6a6 6 0 0 0 6 -6v-7a1 1 0 0 0 -1 -1h-16a1 1 0 0 0 -1 1v7M9 17v3M15 17v3"/>',
        'shield-check': '<path d="M12 3l8 4.5v5.5a9 9 0 0 1 -8 9a9 9 0 0 1 -8 -9v-5.5L12 3M9 12l2 2l4 -4"/>',
        'test-pipe': '<path d="M8 5h10M8 5v12a2 2 0 0 0 2 2h4a2 2 0 0 0 2 -2V5M9 9h6M9 13h6M7 18h10"/>',
        'chart-bar': '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>',
        'chart-line': '<path d="M3 13a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5 -.5v-3a.5.5 0 0 1 .5 -.5h2a.5.5 0 0 1 .5.5v5a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5 -.5v-4"/>',
        'settings': '<path d="M12 1v6m6 -3l-4.24 4.24M12 23v-6m6 3l-4.24 -4.24M1 12h6m-3 -6l4.24 4.24M23 12h-6m3 6l-4.24 -4.24M5.64 5.64l-4.24 -4.24M18.36 18.36l4.24 4.24"/>',
        'calendar': '<rect x="4" y="5" width="16" height="16" rx="2"/><line x1="16" y1="3" x2="16" y2="7"/><line x1="8" y1="3" x2="8" y2="7"/><line x1="4" y1="11" x2="20" y2="11"/>',
        'filter': '<polyline points="4 4 10 14 10 20 14 22 14 14 20 4"/>',
        'search': '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
        'file': '<path d="M14 2H6a2 2 0 0 0 -2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2 -2V8z"/><polyline points="14 2 14 8 20 8"/>',
        'folder': '<path d="M5 4a1 1 0 0 0 -1 1v14a1 1 0 0 0 1 1h14a1 1 0 0 0 1 -1V7a1 1 0 0 0 -1 -1h-10a1 1 0 0 1 -1 -1H5z"/>',
        'download': '<path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2 -2v-2M7 11l5 5l5 -5M12 3v13"/>',
        'upload': '<path d="M21 14v5a2 2 0 0 1 -2 2H5a2 2 0 0 1 -2 -2v-5M17 8l-5 -5l-5 5M12 3v13"/>',
        'message': '<path d="M3 20l1.3 -3.9c-1 -1.5 -1.3 -3.4 -1.3 -5.1 0 -5.5 4.5 -10 10 -10s10 4.5 10 10 -4.5 10 -10 10c-1.7 0 -3.6 -.3 -5.1 -1.3L3 20"/>',
        'send': '<line x1="10" y1="14" x2="21" y2="3"/><path d="M21 3l-6.5 18.75a.55.55 0 0 1 -1 0l-3.5 -7l-7 -3.5a.55.55 0 0 1 0 -1L21 3"/>',
        'edit': '<path d="M7 7H6a2 2 0 0 0 -2 2v9a2 2 0 0 0 2 2h9a2 2 0 0 0 2 -2v-1M20.385 6.585a2.1 2.1 0 0 0 -2.97 -2.97L9 12v3h3L20.385 6.585z"/>',
        'trash': '<polyline points="3 6 5 6 21 6"/><path d="M8 6v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2 -2V6M10 11v6M14 11v6"/>',
        'plus': '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
        'minus': '<line x1="5" y1="12" x2="19" y2="12"/>',
        'eye': '<circle cx="12" cy="12" r="1"/><path d="M12 5C7 5 2.73 7.61 1 11.35C2.73 15.39 7 18 12 18s9.27 -2.61 11 -6.65C21.27 7.61 17 5 12 5"/>',
        'eye-off': '<path d="M1 12s4 -6 11 -6 11 6 11 6M3.6 3.6l16.8 16.8M21 12s-4 6 -11 6 -11 -6 -11 -6"/>',
    }
    
    svg_path = icones.get(nome_icone, icones['list'])  # Default para 'list' se não encontrado
    
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{tamanho}" height="{tamanho}" viewBox="0 0 24 24" fill="none" stroke="{cor}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" style="display:inline-block; vertical-align:middle;">{svg_path}</svg>'


def gerar_icone_tabler_html(nome_icone: str, tamanho: int = 20, cor: str = "#64748b", stroke_width: float = 2) -> str:
    """
    Versão otimizada de gerar_icone_tabler para usar em strings HTML (sem quebras de linha).
    Retorna SVG inline em uma única linha.
    """
    icones = {
        'list': '<path d="M9 6h11M9 12h11M9 18h11M5 6v.01M5 12v.01M5 18v.01"/>',
        'check': '<path d="M5 12l4 4l6 -6"/>',
        'x': '<path d="M18 6l-12 12M6 6l12 12"/>',
        'circle-check': '<circle cx="12" cy="12" r="9"/><path d="M9 12l2 2l4 -4"/>',
        'circle-x': '<circle cx="12" cy="12" r="9"/><path d="M15 9l-6 6M9 9l6 6"/>',
        'bug': '<path d="M9 9v-1a3 3 0 0 1 6 0v1M3 11a6 6 0 0 0 6 6h6a6 6 0 0 0 6 -6v-7a1 1 0 0 0 -1 -1h-16a1 1 0 0 0 -1 1v7M9 17v3M15 17v3"/>',
        'shield-check': '<path d="M12 3l8 4.5v5.5a9 9 0 0 1 -8 9a9 9 0 0 1 -8 -9v-5.5L12 3M9 12l2 2l4 -4"/>',
        'alert-circle': '<circle cx="12" cy="12" r="9"/><path d="M12 8v4M12 16v.01"/>',
    }
    
    svg_path = icones.get(nome_icone, icones['list'])
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{tamanho}" height="{tamanho}" viewBox="0 0 24 24" fill="none" stroke="{cor}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" style="display:inline-block;vertical-align:middle;margin-right:5px;">{svg_path}</svg>'


def gerar_badge_status(status: str, icone_nome: str = None, tamanho_icone: int = 16) -> str:
    """
    Gera um badge HTML com status e ícone Tabler.
    
    Args:
        status: Texto do status
        icone_nome: Nome do ícone Tabler (se None, escolhe baseado no status)
        tamanho_icone: Tamanho do ícone em pixels
    
    Returns:
        String HTML do badge
    """
    mapeamento = {
        'concluído': ('#22c55e', 'circle-check'),
        'done': ('#22c55e', 'circle-check'),
        'reprovado': ('#dc2626', 'circle-x'),
        'rejected': ('#dc2626', 'circle-x'),
        'desenvolvimento': ('#3b82f6', 'code'),
        'development': ('#3b82f6', 'code'),
        'validação': ('#06b6d4', 'shield-check'),
        'qa': ('#06b6d4', 'shield-check'),
        'backlog': ('#64748b', 'list'),
        'warning': ('#f59e0b', 'alert-circle'),
    }
    
    status_lower = status.lower()
    cor = '#64748b'
    icone = 'list'
    
    for chave, (cor_encontrada, icone_encontrado) in mapeamento.items():
        if chave in status_lower:
            cor = cor_encontrada
            icone = icone_encontrado
            break
    
    if icone_nome:
        icone = icone_nome
    
    icon_svg = gerar_icone_tabler_html(icone, tamanho=tamanho_icone, cor=cor)
    
    return f'<span style="display:inline-flex;align-items:center;background:{cor}20;color:{cor};padding:4px 10px;border-radius:8px;font-size:12px;font-weight:600;">{icon_svg}{status}</span>'


def obter_icone_evento(tipo_evento: str, status: str = "") -> Tuple[str, str]:
    """
    Retorna ícone Tabler Icons e cor baseado no tipo de evento.
    
    Args:
        tipo_evento: Type of event ('criacao', 'transicao', 'atribuicao', etc.)
        status: Status value para transições (usado para cores mais precisas)
    
    Returns:
        Tuple[str, str]: (SVG inline, cor_hex)
    """
    mapeamento = {
        'criacao': (gerar_icone_tabler('file', tamanho=32, cor='#22c55e'), '#22c55e'),
        'transicao': (gerar_icone_tabler('git-branch', tamanho=32, cor='#3b82f6'), '#3b82f6'),
        'atribuicao': (gerar_icone_tabler('user-check', tamanho=32, cor='#6366f1'), '#6366f1'),
        'qa_atribuicao': (gerar_icone_tabler('test-pipe', tamanho=32, cor='#8b5cf6'), '#8b5cf6'),
        'sprint': (gerar_icone_tabler('target', tamanho=32, cor='#f59e0b'), '#f59e0b'),
        'estimativa': (gerar_icone_tabler('chart-bar', tamanho=32, cor='#3b82f6'), '#3b82f6'),
        'bugs': (gerar_icone_tabler('bug', tamanho=32, cor='#ef4444'), '#ef4444'),
        'resolucao': (gerar_icone_tabler('shield-check', tamanho=32, cor='#22c55e'), '#22c55e'),
    }
    
    if tipo_evento == 'transicao' and status:
        return obter_icone_status(status)
    
    return mapeamento.get(tipo_evento, (gerar_icone_tabler('list', tamanho=32, cor='#9ca3af'), '#9ca3af'))


def obter_icone_status(status: str) -> Tuple[str, str]:
    """Retorna ícone Tabler Icons e cor baseado no nome do status."""
    status_lower = status.lower() if status else ''
    
    if any(x in status_lower for x in ['backlog', 'to do', 'pendente', 'aberto']):
        return gerar_icone_tabler('list', tamanho=32, cor='#64748b'), '#64748b'
    elif any(x in status_lower for x in ['andamento', 'development', 'desenvolviment', 'em progresso']):
        return gerar_icone_tabler('code', tamanho=32, cor='#3b82f6'), '#3b82f6'
    elif any(x in status_lower for x in ['revisão', 'review', 'code review']):
        return gerar_icone_tabler('git-branch', tamanho=32, cor='#8b5cf6'), '#8b5cf6'
    elif any(x in status_lower for x in ['aguardando validação', 'waiting', 'aguardando qa']):
        return gerar_icone_tabler('clock', tamanho=32, cor='#f59e0b'), '#f59e0b'
    elif any(x in status_lower for x in ['validação', 'em validação', 'testing', 'qa']):
        return gerar_icone_tabler('test-pipe', tamanho=32, cor='#06b6d4'), '#06b6d4'
    elif any(x in status_lower for x in ['concluído', 'done', 'finalizado', 'resolvido']):
        return gerar_icone_tabler('circle-check', tamanho=32, cor='#22c55e'), '#22c55e'
    elif any(x in status_lower for x in ['bloqueado', 'blocked', 'impedido']):
        return gerar_icone_tabler('alert-circle', tamanho=32, cor='#ef4444'), '#ef4444'
    elif any(x in status_lower for x in ['reprovado', 'rejected', 'recusado']):
        return gerar_icone_tabler('circle-x', tamanho=32, cor='#dc2626'), '#dc2626'
    elif any(x in status_lower for x in ['adiado', 'deferred', 'descartado']):
        return gerar_icone_tabler('calendar', tamanho=32, cor='#6b7280'), '#6b7280'
    else:
        return gerar_icone_tabler('list', tamanho=32, cor='#9ca3af'), '#9ca3af'
