"""
Integração com API Jira para busca e processamento de dados.
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from config import JIRA_BASE_URL, CUSTOM_FIELDS, STATUS_FLOW, REGRAS, traduzir_link
from auth import get_secrets

@st.cache_data(ttl=300, show_spinner=False)
def buscar_dados_jira_cached(projeto: str, jql: str) -> Tuple[Optional[List[Dict]], datetime]:
    """Busca dados do Jira com cache de 5 minutos."""
    secrets = get_secrets()
    if not secrets["email"] or not secrets["token"]:
        return None, datetime.now()
    
    base_url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
    headers = {"Accept": "application/json"}
    
    fields = [
        "key", "summary", "status", "issuetype", "assignee", "created", "updated",
        "resolutiondate", "priority", "project", "labels", "reporter", "resolution",
        "issuelinks",
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
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            all_issues.extend(data.get("issues", []))
            
            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break
        
        return all_issues, datetime.now()
    
    except Exception as e:
        st.error(f"Erro ao conectar com Jira: {e}")
        return None, datetime.now()

@st.cache_data(ttl=300, show_spinner=False)
def buscar_card_especifico(ticket_id: str) -> Tuple[Optional[Dict], Optional[List[Dict]], Optional[List[Dict]], Optional[List[Dict]]]:
    """Busca um card específico pelo ID com seus links, comentários e histórico."""
    secrets = get_secrets()
    if not secrets["email"] or not secrets["token"]:
        return None, None, None, None
    
    try:
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
        ]
        
        params = {"fields": ",".join(fields), "expand": "renderedFields,changelog"}
        
        response = requests.get(
            base_url,
            headers=headers,
            params=params,
            auth=(secrets["email"], secrets["token"]),
            timeout=30
        )
        
        if response.status_code == 404:
            return None, None, None, None
        
        response.raise_for_status()
        issue = response.json()
        
        # Extrai os links do card
        links = []
        fields_data = issue.get('fields', {})
        
        # Links diretos
        issue_links = fields_data.get('issuelinks', [])
        for link in issue_links:
            link_type = traduzir_link(link.get('type', {}).get('name', 'Relacionado'))
            
            if 'outwardIssue' in link:
                linked = link['outwardIssue']
                links.append({
                    'tipo': link_type,
                    'direcao': traduzir_link(link.get('type', {}).get('outward', 'relacionado a')),
                    'ticket_id': linked.get('key', ''),
                    'titulo': linked.get('fields', {}).get('summary', ''),
                    'status': linked.get('fields', {}).get('status', {}).get('name', ''),
                    'link': f"{JIRA_BASE_URL}/browse/{linked.get('key', '')}",
                    'nivel': 1
                })
            
            if 'inwardIssue' in link:
                linked = link['inwardIssue']
                links.append({
                    'tipo': link_type,
                    'direcao': traduzir_link(link.get('type', {}).get('inward', 'relacionado a')),
                    'ticket_id': linked.get('key', ''),
                    'titulo': linked.get('fields', {}).get('summary', ''),
                    'status': linked.get('fields', {}).get('status', {}).get('name', ''),
                    'link': f"{JIRA_BASE_URL}/browse/{linked.get('key', '')}",
                    'nivel': 1
                })
        
        # Parent
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
        
        # Subtasks
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
        
        # Busca links transitivos
        links_primeiro_nivel = [l['ticket_id'] for l in links]
        links_transitivos = []
        
        for link_info in links:
            try:
                linked_ticket = link_info['ticket_id']
                if not linked_ticket:
                    continue
                
                linked_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{linked_ticket}"
                linked_params = {"fields": "issuelinks,summary,status"}
                
                linked_response = requests.get(
                    linked_url,
                    headers=headers,
                    params=linked_params,
                    auth=(secrets["email"], secrets["token"]),
                    timeout=10
                )
                
                if linked_response.status_code == 200:
                    linked_data = linked_response.json()
                    linked_fields = linked_data.get('fields', {})
                    linked_issue_links = linked_fields.get('issuelinks', [])
                    
                    for sub_link in linked_issue_links:
                        sub_type = traduzir_link(sub_link.get('type', {}).get('name', 'Relacionado'))
                        
                        if 'outwardIssue' in sub_link:
                            sub_linked = sub_link['outwardIssue']
                            sub_key = sub_linked.get('key', '')
                            if sub_key and sub_key != ticket_id and sub_key not in links_primeiro_nivel:
                                links_transitivos.append({
                                    'tipo': sub_type,
                                    'direcao': traduzir_link(sub_link.get('type', {}).get('outward', 'relacionado a')),
                                    'ticket_id': sub_key,
                                    'titulo': sub_linked.get('fields', {}).get('summary', ''),
                                    'status': sub_linked.get('fields', {}).get('status', {}).get('name', ''),
                                    'link': f"{JIRA_BASE_URL}/browse/{sub_key}",
                                    'nivel': 2,
                                    'via': linked_ticket
                                })
                        
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
                continue
        
        seen = set(l['ticket_id'] for l in links)
        for lt in links_transitivos:
            if lt['ticket_id'] not in seen:
                links.append(lt)
                seen.add(lt['ticket_id'])
        
        # Busca comentários
        comentarios = []
        try:
            comments_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}/comment"
            comments_response = requests.get(
                comments_url,
                headers=headers,
                auth=(secrets["email"], secrets["token"]),
                timeout=15
            )
            if comments_response.status_code == 200:
                comments_data = comments_response.json()
                for comment in comments_data.get('comments', []):
                    author = comment.get('author', {})
                    author_type = author.get('accountType', 'user')
                    
                    if author_type == 'app':
                        continue
                    
                    display_name = author.get('displayName', '')
                    bot_patterns = ['bot', 'automation', 'jira', 'webhook', 'integration', 'service']
                    is_bot = any(pattern.lower() in display_name.lower() for pattern in bot_patterns)
                    if is_bot:
                        continue
                    
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
            pass
        
        # Extrai histórico de transições
        historico_transicoes = extrair_historico_transicoes(issue, ticket_id)
        
        return issue, links, comentarios, historico_transicoes
    
    except Exception as e:
        st.error(f"Erro ao buscar card: {e}")
        return None, None, None, None

def extrair_historico_transicoes(issue: Dict, ticket_id: str) -> List[Dict]:
    """Extrai histórico de transições de status do changelog."""
    historico = []
    
    try:
        changelog = issue.get('changelog', {})
        histories = changelog.get('histories', [])
        
        for history in histories:
            criado = history.get('created', '')
            autor = history.get('author', {}).get('displayName', 'Sistema')
            
            for item in history.get('items', []):
                if item.get('field') == 'status':
                    historico.append({
                        'data': datetime.fromisoformat(criado.replace('Z', '+00:00')).replace(tzinfo=None),
                        'de': item.get('fromString', '-'),
                        'para': item.get('toString', '-'),
                        'autor': autor,
                        'tipo': 'transicao'
                    })
        
        # Ordena por data
        historico.sort(key=lambda x: x['data'])
    
    except Exception:
        pass
    
    return historico

def extrair_texto_adf(adf_content: Dict) -> str:
    """Extrai texto plano de ADF (Atlassian Document Format)."""
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
    return ' '.join(texto).strip()
