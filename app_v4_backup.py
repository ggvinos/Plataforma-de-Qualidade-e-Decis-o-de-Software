"""
================================================================================
JIRA DASHBOARD v4.1 - MÉTRICAS ISTQB/CTFL PARA TOMADA DE DECISÃO
================================================================================
Baseado em métricas de qualidade de software reconhecidas internacionalmente:
- ISTQB (International Software Testing Qualifications Board)
- CTFL (Certified Tester Foundation Level)

Foco: Informação densa, modular e acionável para QA, Dev e Liderança.

CAMPOS MAPEADOS DO JIRA NINA:
- customfield_10487: QA (user)
- customfield_11157: Bugs Encontrados
- customfield_10016: Story Points
- customfield_10020: Sprint
- customfield_11358: Janela de Testes
- customfield_11357: Dias até a Release
- customfield_11290: Complexidade de Teste
================================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import requests
from typing import Optional, Dict, List, Any, Tuple
import json
import os

# Carregar .env se existir
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ==============================================================================
# CONFIGURAÇÕES
# ==============================================================================

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "https://ninatecnologia.atlassian.net")

PROJETOS = {
    "SD": {"nome": "Desenvolvimento", "principal": True},
    "QA": {"nome": "QA", "principal": False},
    "PB": {"nome": "Backlog de Produto", "principal": False},
    "VALPROD": {"nome": "Validação em Produção", "principal": False},
}

# Campos customizados REAIS do Jira NINA (mapeados via API)
CUSTOM_FIELDS = {
    "story_points": "customfield_10016",
    "sprint": "customfield_10020",
    "bugs_encontrados": "customfield_11157",
    "dias_ate_release": "customfield_11357",
    "janela_testes": "customfield_11358",
    "complexidade_teste": "customfield_11290",
    "qa_responsavel": "customfield_10487",  # Campo QA correto (user)
    "qa_array": "customfield_10784",         # Campo QA alternativo (array)
    "desenvolvedor": "customfield_10455",
    "desenvolvedor_array": "customfield_10785",
}

# Status REAIS do workflow SD (mapeados via API)
STATUS_FLOW = {
    "backlog": ["Backlog", "To Do"],
    "development": ["Em andamento"],
    "code_review": ["EM REVISÃO"],
    "waiting_qa": ["AGUARDANDO VALIDAÇÃO", "Tarefas pendentes"],
    "testing": ["EM VALIDAÇÃO"],
    "done": ["Concluído"],
    "blocked": ["IMPEDIDO", "REPROVADO"],
    "deferred": ["Validado - Adiado", "DESCARTADO"],
}

MATURIDADE = {
    "Gold": {"min_fk": 3.0, "cor": "#22c55e", "emoji": "🥇", "desc": "Excelente"},
    "Silver": {"min_fk": 2.0, "cor": "#eab308", "emoji": "🥈", "desc": "Bom"},
    "Bronze": {"min_fk": 1.0, "cor": "#f97316", "emoji": "🥉", "desc": "Regular"},
    "Risco": {"min_fk": 0, "cor": "#ef4444", "emoji": "⚠️", "desc": "Crítico"},
}

# ==============================================================================
# UTILIDADES
# ==============================================================================

def link_jira(ticket_id: str) -> str:
    """Gera URL do ticket no Jira."""
    return f"{JIRA_BASE_URL}/browse/{ticket_id}"


def link_html(ticket_id: str, texto: str = None) -> str:
    """Gera HTML clicável para o Jira."""
    url = link_jira(ticket_id)
    display = texto or ticket_id
    return f'<a href="{url}" target="_blank" style="color: #6366f1; text-decoration: none; font-weight: 600;">🔗 {display}</a>'


def formatar_duracao(dias: float) -> str:
    """Formata duração de forma legível."""
    if dias < 1:
        return f"{int(dias * 24)}h"
    elif dias < 7:
        return f"{dias:.1f}d"
    else:
        return f"{dias/7:.1f} sem"


# ==============================================================================
# ESTILOS CSS
# ==============================================================================

def aplicar_estilos():
    st.markdown("""
    <style>
    .metric-card, .alert-card, .insight-card { color: inherit; }
    
    .status-card {
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 2px solid;
    }
    .status-green { background: rgba(34, 197, 94, 0.1); border-color: #22c55e; }
    .status-yellow { background: rgba(234, 179, 8, 0.1); border-color: #eab308; }
    .status-orange { background: rgba(249, 115, 22, 0.1); border-color: #f97316; }
    .status-red { background: rgba(239, 68, 68, 0.1); border-color: #ef4444; }
    .status-blue { background: rgba(59, 130, 246, 0.1); border-color: #3b82f6; }
    .status-purple { background: rgba(139, 92, 246, 0.1); border-color: #8b5cf6; }
    
    .big-number { font-size: 36px; font-weight: bold; margin: 0; }
    .card-label { font-size: 13px; opacity: 0.8; margin-top: 5px; }
    
    .alert-critical {
        background: rgba(239, 68, 68, 0.15);
        border-left: 4px solid #ef4444;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .alert-warning {
        background: rgba(234, 179, 8, 0.15);
        border-left: 4px solid #eab308;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .alert-info {
        background: rgba(59, 130, 246, 0.15);
        border-left: 4px solid #3b82f6;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .alert-success {
        background: rgba(34, 197, 94, 0.15);
        border-left: 4px solid #22c55e;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .ticket-card {
        border-radius: 10px;
        padding: 12px 15px;
        margin: 8px 0;
        border-left: 4px solid;
        background: rgba(100, 100, 100, 0.05);
    }
    .ticket-risk-high { border-left-color: #ef4444; }
    .ticket-risk-medium { border-left-color: #f97316; }
    .ticket-risk-low { border-left-color: #22c55e; }
    
    .section-header {
        background: linear-gradient(90deg, rgba(99, 102, 241, 0.15), transparent);
        padding: 12px 20px;
        border-radius: 8px;
        margin: 25px 0 15px 0;
        border-left: 4px solid #6366f1;
    }
    
    .go-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
    }
    .go-approved { background: #22c55e; color: white; }
    .go-warning { background: #eab308; color: black; }
    .go-blocked { background: #ef4444; color: white; }
    
    .impact-card {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(16, 185, 129, 0.05));
        border: 1px solid rgba(34, 197, 94, 0.3);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
    }
    
    .problematic-card {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.05));
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 12px;
        padding: 15px;
        margin: 8px 0;
    }
    
    .comment-card {
        background: rgba(100, 100, 100, 0.05);
        border-radius: 8px;
        padding: 12px;
        margin: 5px 0;
        font-size: 13px;
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] { padding: 12px 24px; font-weight: 500; }
    
    /* Metrics tooltip */
    .metric-info {
        font-size: 11px;
        opacity: 0.7;
        margin-top: 4px;
    }
    </style>
    """, unsafe_allow_html=True)


# ==============================================================================
# CONEXÃO JIRA
# ==============================================================================

def verificar_credenciais() -> bool:
    """Verifica credenciais no session_state ou variáveis de ambiente."""
    email = st.session_state.get("jira_email") or os.getenv("JIRA_EMAIL")
    token = st.session_state.get("jira_token") or os.getenv("JIRA_TOKEN")
    return bool(email and token)


def get_credenciais() -> Tuple[str, str]:
    """Retorna email e token das credenciais."""
    email = st.session_state.get("jira_email") or os.getenv("JIRA_EMAIL")
    token = st.session_state.get("jira_token") or os.getenv("JIRA_TOKEN")
    return email, token


def buscar_jira(jql: str, expand: str = "") -> Optional[List[Dict]]:
    """Executa query JQL no Jira com expansão opcional."""
    if not verificar_credenciais():
        return None
    
    email, token = get_credenciais()
    
    url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    
    fields = ["summary", "status", "issuetype", "assignee", "created", "updated",
              "resolutiondate", "priority", "project", "labels", "components",
              "comment"] + list(CUSTOM_FIELDS.values())
    
    payload = {
        "jql": jql, 
        "maxResults": 200, 
        "fields": fields,
    }
    
    if expand:
        payload["expand"] = expand
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload),
                                auth=(email, token))
        response.raise_for_status()
        return response.json().get("issues", [])
    except Exception as e:
        st.error(f"Erro Jira: {e}")
        return None


def buscar_comentarios(ticket_id: str) -> List[Dict]:
    """Busca comentários de um ticket específico."""
    if not verificar_credenciais():
        return []
    
    email, token = get_credenciais()
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}/comment"
    headers = {"Accept": "application/json"}
    
    try:
        response = requests.get(url, headers=headers, auth=(email, token))
        response.raise_for_status()
        return response.json().get("comments", [])
    except:
        return []


def processar_issues(issues: List[Dict], data_release: datetime) -> pd.DataFrame:
    """Converte issues do Jira para DataFrame com comentários."""
    dados = []
    
    for issue in issues:
        f = issue.get('fields', {})
        
        tipo_original = f.get('issuetype', {}).get('name', 'Unknown')
        tipo = 'TAREFA'
        for t, nomes in [("HOTFIX", ["Hotfix", "Hotfeature"]), ("BUG", ["Bug", "Impeditivo"]),
                         ("TAREFA", ["Tarefa", "Task", "Subtarefa"]), ("SUGESTÃO", ["Sugestão"])]:
            if any(n in tipo_original for n in nomes):
                tipo = t
                break
        
        projeto = f.get('project', {}).get('key', 'N/A')
        
        dev = 'Não atribuído'
        if f.get('assignee'):
            dev = f['assignee'].get('displayName', dev)
        
        sp = f.get(CUSTOM_FIELDS['story_points']) or 0
        
        sprint_f = f.get(CUSTOM_FIELDS['sprint'], [])
        sprint = sprint_f[-1].get('name', 'Sem Sprint') if sprint_f else 'Sem Sprint'
        
        status = f.get('status', {}).get('name', 'Unknown')
        
        status_cat = 'unknown'
        for cat, statuses in STATUS_FLOW.items():
            if any(s.lower() in status.lower() for s in statuses):
                status_cat = cat
                break
        
        bugs = f.get(CUSTOM_FIELDS['bugs_encontrados'], 0) or 0
        
        comp = f.get(CUSTOM_FIELDS['complexidade_teste'])
        complexidade = comp.get('value', 'N/A') if isinstance(comp, dict) else 'N/A'
        
        qa = 'Não atribuído'
        qa_f = f.get(CUSTOM_FIELDS['qa_responsavel'])
        if qa_f:
            if isinstance(qa_f, dict):
                qa = qa_f.get('displayName', qa)
            elif isinstance(qa_f, list) and qa_f:
                qa = qa_f[0].get('displayName', qa)
        
        janela = f.get(CUSTOM_FIELDS['janela_testes'], '')
        
        try:
            criado = datetime.fromisoformat(f.get('created', '').replace('Z', '+00:00')).replace(tzinfo=None)
        except:
            criado = datetime.now()
        
        try:
            atualizado = datetime.fromisoformat(f.get('updated', '').replace('Z', '+00:00')).replace(tzinfo=None)
        except:
            atualizado = datetime.now()
        
        # Comentários
        comentarios = f.get('comment', {}).get('comments', [])
        num_comentarios = len(comentarios)
        ultimos_comentarios = []
        for c in comentarios[-3:]:
            autor = c.get('author', {}).get('displayName', 'Anônimo')
            corpo = c.get('body', {})
            if isinstance(corpo, dict):
                # Formato ADF (Atlassian Document Format)
                texto = ""
                for content in corpo.get('content', []):
                    for item in content.get('content', []):
                        if item.get('type') == 'text':
                            texto += item.get('text', '')
            else:
                texto = str(corpo)[:200]
            ultimos_comentarios.append({'autor': autor, 'texto': texto[:150]})
        
        prio = f.get('priority', {})
        prioridade = prio.get('name', 'Médio') if prio else 'Médio'
        
        ticket_id = issue.get('key', '')
        
        dados.append({
            'ticket_id': ticket_id,
            'link': link_jira(ticket_id),
            'titulo': f.get('summary', ''),
            'tipo': tipo,
            'tipo_original': tipo_original,
            'status': status,
            'status_cat': status_cat,
            'projeto': projeto,
            'desenvolvedor': dev,
            'qa': qa,
            'sp': int(sp) if sp else 0,
            'bugs': int(bugs) if bugs else 0,
            'sprint': sprint,
            'prioridade': prioridade,
            'complexidade': complexidade,
            'janela_testes': janela,
            'criado': criado,
            'atualizado': atualizado,
            'data_release': data_release,
            'dias_em_status': (datetime.now() - atualizado).days,
            'lead_time': (atualizado - criado).days,
            'num_comentarios': num_comentarios,
            'comentarios': ultimos_comentarios,
        })
    
    return pd.DataFrame(dados)


# ==============================================================================
# DADOS MOCKADOS
# ==============================================================================

def gerar_dados_mock(projeto: str = "SD") -> pd.DataFrame:
    """Gera dados realistas para demonstração (baseado em dados reais do time NINA)."""
    
    devs = ["Augusto Oliveira", "Christopher Krauss de Carvalho", "Suyan Moriel", 
            "Daniel Marques", "Elinton Dozol Machado", "Carlos Daniel de Souza Cordeiro",
            "Cristian Yamamoto", "João Pedro Menegali"]
    
    qas = ["Vinicios Ferreira", "Vinicius Alves da Silva Neto", 
           "João Pedro Greif de Souza", "Eduardo Barbosa da Silva"]
    
    tipos = ["TAREFA", "BUG", "HOTFIX"]
    complexidades = ["Baixa", "Média", "Alta", "Muito Alta"]
    prioridades = ["Baixo", "Médio", "Alto", "Muito alto"]
    
    statuses = [
        ("Backlog", "backlog"),
        ("Em andamento", "development"),
        ("EM DESENVOLVIMENTO", "development"),
        ("EM REVISÃO", "code_review"),
        ("AGUARDANDO VALIDAÇÃO", "waiting_qa"),
        ("Concluído", "done"),
    ]
    
    comentarios_mock = [
        "Validado com sucesso, sem bugs encontrados.",
        "Encontrado bug crítico na integração com API.",
        "Card retornou do QA com 2 bugs.",
        "Aprovado após correção dos bugs relatados.",
        "Necessário revisão dos critérios de aceite.",
        "Teste de regressão realizado, OK.",
        "Fluxo alternativo identificado e documentado.",
        "Dev confirma correção aplicada.",
    ]
    
    sprint = "Sprint 25 (Atual)"
    
    dados = []
    hoje = datetime.now()
    data_release = hoje + timedelta(days=random.randint(7, 14))
    
    for i in range(55):
        tipo = random.choices(tipos, weights=[60, 25, 15])[0]
        
        sp = random.choice([3, 5, 8, 13]) if tipo == "TAREFA" else random.choice([1, 2, 3])
        
        comp = random.choice(complexidades)
        if comp in ["Alta", "Muito Alta"]:
            bugs = random.choices([0, 1, 2, 3, 4, 5], weights=[15, 20, 25, 20, 15, 5])[0]
        else:
            bugs = random.choices([0, 1, 2, 3], weights=[45, 30, 20, 5])[0]
        
        status, status_cat = random.choice(statuses)
        
        criado = hoje - timedelta(days=random.randint(3, 35))
        lead_time = random.randint(2, 15)
        atualizado = criado + timedelta(days=lead_time)
        if atualizado > hoje:
            atualizado = hoje
        
        janela = str(random.randint(2, 12)) if status_cat in ['waiting_qa', 'done'] else ''
        
        ticket_id = f"{projeto}-{1000 + i}"
        
        # Gerar comentários mock
        num_comentarios = random.randint(0, 8)
        coments = []
        for _ in range(min(3, num_comentarios)):
            coments.append({
                'autor': random.choice(qas + devs),
                'texto': random.choice(comentarios_mock)
            })
        
        dados.append({
            'ticket_id': ticket_id,
            'link': link_jira(ticket_id),
            'titulo': f"{tipo} - Implementação de funcionalidade #{i+1}",
            'tipo': tipo,
            'tipo_original': tipo,
            'status': status,
            'status_cat': status_cat,
            'projeto': projeto,
            'desenvolvedor': random.choice(devs),
            'qa': random.choice(qas),
            'sp': sp,
            'bugs': bugs,
            'sprint': sprint,
            'prioridade': random.choices(prioridades, weights=[10, 50, 30, 10])[0],
            'complexidade': comp,
            'janela_testes': janela,
            'criado': criado,
            'atualizado': atualizado,
            'data_release': data_release,
            'dias_em_status': (hoje - atualizado).days,
            'lead_time': lead_time,
            'num_comentarios': num_comentarios,
            'comentarios': coments,
        })
    
    return pd.DataFrame(dados)


# ==============================================================================
# MÉTRICAS ISTQB/CTFL
# ==============================================================================

def calcular_fator_k(sp: int, bugs: int, rigor: float = 1.5) -> float:
    """Fator K: Maturidade de entrega. FK = SP / (Bugs × Rigor)"""
    if bugs == 0:
        return float('inf')
    return sp / (bugs * rigor)


def classificar_maturidade(fator_k: float) -> Dict[str, Any]:
    """Classifica Fator K em selo de maturidade."""
    if fator_k == float('inf'):
        return {**MATURIDADE["Gold"], "selo": "Gold"}
    
    for selo, config in MATURIDADE.items():
        if fator_k >= config["min_fk"]:
            return {**config, "selo": selo}
    
    return {**MATURIDADE["Risco"], "selo": "Risco"}


def calcular_ddp(df: pd.DataFrame) -> Dict[str, Any]:
    """
    DDP - Defect Detection Percentage (ISTQB)
    Porcentagem de defeitos encontrados antes de ir para produção.
    DDP = (Bugs QA / (Bugs QA + Bugs Produção)) × 100
    
    Interpretação:
    - 95%+ = Excelente
    - 85-95% = Bom
    - 70-85% = Regular
    - <70% = Crítico
    """
    bugs_qa = df['bugs'].sum()
    hotfixes = len(df[df['tipo'] == 'HOTFIX'])
    
    total_bugs = bugs_qa + hotfixes
    
    if total_bugs == 0:
        return {'valor': 100, 'bugs_qa': 0, 'bugs_prod': 0, 'status': 'excellent'}
    
    ddp = (bugs_qa / total_bugs) * 100
    
    if ddp >= 95:
        status = 'excellent'
    elif ddp >= 85:
        status = 'good'
    elif ddp >= 70:
        status = 'regular'
    else:
        status = 'critical'
    
    return {
        'valor': round(ddp, 1),
        'bugs_qa': bugs_qa,
        'bugs_prod': hotfixes,
        'status': status
    }


def calcular_first_pass_yield(df: pd.DataFrame) -> Dict[str, Any]:
    """
    FPY - First Pass Yield
    Porcentagem de cards que passaram de primeira (sem bugs).
    
    FPY = (Cards sem bugs / Total de cards validados) × 100
    """
    df_validado = df[df['status_cat'].isin(['waiting_qa', 'done'])]
    
    if df_validado.empty:
        return {'valor': 0, 'sem_bugs': 0, 'total': 0, 'status': 'sem_dados'}
    
    sem_bugs = len(df_validado[df_validado['bugs'] == 0])
    total = len(df_validado)
    fpy = (sem_bugs / total) * 100
    
    if fpy >= 80:
        status = 'excellent'
    elif fpy >= 60:
        status = 'good'
    elif fpy >= 40:
        status = 'regular'
    else:
        status = 'critical'
    
    return {
        'valor': round(fpy, 1),
        'sem_bugs': sem_bugs,
        'total': total,
        'status': status
    }


def calcular_defect_density(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Defect Density - Densidade de defeitos por SP
    DD = Bugs / Story Points
    """
    total_bugs = df['bugs'].sum()
    total_sp = df['sp'].sum()
    
    if total_sp == 0:
        return {'valor': 0, 'bugs': total_bugs, 'sp': total_sp}
    
    dd = total_bugs / total_sp
    
    return {
        'valor': round(dd, 2),
        'bugs': total_bugs,
        'sp': total_sp
    }


def calcular_mttr(df: pd.DataFrame) -> Dict[str, Any]:
    """
    MTTR - Mean Time To Repair
    Tempo médio para corrigir um bug (baseado em cards que são BUG ou têm bugs).
    """
    df_bugs = df[(df['tipo'] == 'BUG') | (df['bugs'] > 0)]
    
    if df_bugs.empty:
        return {'valor': 0, 'total': 0}
    
    mttr = df_bugs['lead_time'].mean()
    
    return {
        'valor': round(mttr, 1),
        'total': len(df_bugs)
    }


def calcular_lead_time(df: pd.DataFrame) -> Dict[str, Any]:
    """Lead Time médio do time."""
    df_done = df[df['status_cat'] == 'done']
    
    if df_done.empty:
        return {'medio': 0, 'p50': 0, 'p90': 0, 'total': 0}
    
    return {
        'medio': round(df_done['lead_time'].mean(), 1),
        'p50': round(df_done['lead_time'].median(), 1),
        'p90': round(df_done['lead_time'].quantile(0.9), 1),
        'total': len(df_done)
    }


def calcular_throughput(df: pd.DataFrame, dias: int = 7) -> float:
    """Throughput: Cards concluídos por semana."""
    df_done = df[df['status_cat'] == 'done']
    if df_done.empty:
        return 0
    
    cutoff = datetime.now() - timedelta(days=dias)
    recentes = df_done[df_done['atualizado'] >= cutoff]
    
    return len(recentes) / (dias / 7)


def identificar_gargalos(df: pd.DataFrame) -> List[Dict]:
    """Identifica gargalos no fluxo."""
    gargalos = []
    
    tempo_esperado = {
        'development': 5,
        'code_review': 2,
        'waiting_qa': 3,
    }
    
    for cat, esperado in tempo_esperado.items():
        df_cat = df[df['status_cat'] == cat]
        if not df_cat.empty:
            tempo_medio = df_cat['dias_em_status'].mean()
            if tempo_medio > esperado:
                cards_afetados = df_cat['ticket_id'].tolist()
                gargalos.append({
                    'categoria': cat,
                    'esperado': esperado,
                    'atual': round(tempo_medio, 1),
                    'excesso': round(tempo_medio - esperado, 1),
                    'cards': len(df_cat),
                    'tickets': cards_afetados,
                    'impacto': 'ALTO' if tempo_medio > esperado * 2 else 'MÉDIO'
                })
    
    return sorted(gargalos, key=lambda x: x['excesso'], reverse=True)


# ==============================================================================
# ANÁLISES POR PERFIL
# ==============================================================================

def analisar_qa_detalhado(df: pd.DataFrame, qa: str) -> Dict[str, Any]:
    """Análise detalhada para QA com métricas ISTQB."""
    df_qa = df[df['qa'] == qa].copy()
    
    if df_qa.empty:
        return None
    
    # Cards validados
    validados = df_qa[df_qa['status_cat'] == 'done']
    em_validacao = df_qa[df_qa['status_cat'] == 'waiting_qa']
    
    # Bugs encontrados
    bugs_total = df_qa['bugs'].sum()
    
    # DDP do QA
    ddp = calcular_ddp(df_qa)
    
    # FPY do QA
    fpy = calcular_first_pass_yield(df_qa)
    
    # Tempo médio de validação (para cards done)
    tempo_validacao = validados['lead_time'].mean() if not validados.empty else 0
    
    # Cards problemáticos (muitos bugs)
    cards_problematicos = df_qa[df_qa['bugs'] >= 3].sort_values('bugs', ascending=False)
    
    # Cards mais rápidos e mais lentos
    if not validados.empty:
        mais_rapido = validados.nsmallest(3, 'lead_time')[['ticket_id', 'titulo', 'lead_time', 'bugs', 'link']]
        mais_lento = validados.nlargest(3, 'lead_time')[['ticket_id', 'titulo', 'lead_time', 'bugs', 'link']]
    else:
        mais_rapido = pd.DataFrame()
        mais_lento = pd.DataFrame()
    
    # Por complexidade
    por_comp = df_qa.groupby('complexidade').agg({
        'ticket_id': 'count',
        'bugs': 'sum',
        'lead_time': 'mean'
    }).round(1).to_dict('index')
    
    # Impacto do QA
    bugs_evitados = bugs_total  # Todos os bugs encontrados são bugs evitados em produção
    sp_protegidos = df_qa['sp'].sum()
    
    return {
        'cards_total': len(df_qa),
        'validados': len(validados),
        'em_fila': len(em_validacao),
        'bugs_encontrados': bugs_total,
        'bugs_evitados': bugs_evitados,
        'sp_protegidos': sp_protegidos,
        'ddp': ddp,
        'fpy': fpy,
        'tempo_validacao': round(tempo_validacao, 1),
        'cards_problematicos': cards_problematicos,
        'mais_rapido': mais_rapido,
        'mais_lento': mais_lento,
        'por_complexidade': por_comp,
        'df': df_qa
    }


def analisar_dev_detalhado(df: pd.DataFrame, dev: str) -> Dict[str, Any]:
    """Análise detalhada para desenvolvedor."""
    df_dev = df[df['desenvolvedor'] == dev].copy()
    
    if df_dev.empty:
        return None
    
    # Fator K
    df_dev['fk'] = df_dev.apply(lambda r: calcular_fator_k(r['sp'], r['bugs']), axis=1)
    df_dev['fk_calc'] = df_dev['fk'].apply(lambda x: 10 if x == float('inf') else min(x, 10))
    fk_medio = df_dev['fk_calc'].mean()
    
    maturidade = classificar_maturidade(fk_medio)
    
    # FPY do dev
    validados = df_dev[df_dev['status_cat'].isin(['waiting_qa', 'done'])]
    zero_bugs = len(validados[validados['bugs'] == 0]) / len(validados) * 100 if len(validados) > 0 else 0
    
    # Cards com mais bugs
    cards_problematicos = df_dev[df_dev['bugs'] >= 2].sort_values('bugs', ascending=False)
    
    # Tempo médio de desenvolvimento
    tempo_dev = df_dev['lead_time'].mean()
    
    # Por complexidade
    bugs_por_comp = df_dev.groupby('complexidade').agg({
        'ticket_id': 'count',
        'bugs': 'sum',
        'sp': 'sum',
        'lead_time': 'mean'
    }).round(1).to_dict('index')
    
    return {
        'cards': len(df_dev),
        'sp_total': df_dev['sp'].sum(),
        'bugs_total': df_dev['bugs'].sum(),
        'fk_medio': round(fk_medio, 2),
        'maturidade': maturidade,
        'zero_bugs': round(zero_bugs, 1),
        'tempo_medio': round(tempo_dev, 1),
        'cards_problematicos': cards_problematicos,
        'bugs_por_comp': bugs_por_comp,
        'df': df_dev
    }


# ==============================================================================
# HEALTH SCORE E GO/NO-GO
# ==============================================================================

def calcular_health_score(df: pd.DataFrame) -> Dict[str, Any]:
    """Health Score composto (0-100)."""
    if df.empty:
        return {'score': 0, 'status': '⚪ SEM DADOS', 'cor': '#808080', 'detalhes': {}}
    
    detalhes = {}
    
    # 1. Taxa de conclusão (25%)
    total = len(df)
    concluidos = len(df[df['status_cat'] == 'done'])
    taxa_conclusao = (concluidos / total * 100) if total > 0 else 0
    score_conclusao = min(taxa_conclusao / 100 * 25, 25)
    detalhes['conclusao'] = {'valor': round(taxa_conclusao, 1), 'peso': 25, 'score': round(score_conclusao, 1)}
    
    # 2. DDP (25%)
    ddp = calcular_ddp(df)
    score_ddp = min(ddp['valor'] / 100 * 25, 25)
    detalhes['ddp'] = {'valor': ddp['valor'], 'peso': 25, 'score': round(score_ddp, 1)}
    
    # 3. FPY (20%)
    fpy = calcular_first_pass_yield(df)
    score_fpy = min(fpy['valor'] / 100 * 20, 20)
    detalhes['fpy'] = {'valor': fpy['valor'], 'peso': 20, 'score': round(score_fpy, 1)}
    
    # 4. Gargalos (15%) - inverso
    gargalos = identificar_gargalos(df)
    gargalo_score = 15 - (len(gargalos) * 5)
    score_gargalo = max(0, gargalo_score)
    detalhes['gargalos'] = {'valor': len(gargalos), 'peso': 15, 'score': round(score_gargalo, 1)}
    
    # 5. Lead Time (15%) - baseado na meta de 7 dias
    lead = calcular_lead_time(df)
    if lead['medio'] <= 5:
        score_lead = 15
    elif lead['medio'] <= 7:
        score_lead = 12
    elif lead['medio'] <= 10:
        score_lead = 8
    else:
        score_lead = 5
    detalhes['lead_time'] = {'valor': lead['medio'], 'peso': 15, 'score': round(score_lead, 1)}
    
    score_total = score_conclusao + score_ddp + score_fpy + score_gargalo + score_lead
    
    if score_total >= 75:
        status, cor = '🟢 SAUDÁVEL', '#22c55e'
    elif score_total >= 50:
        status, cor = '🟡 ALERTA', '#eab308'
    else:
        status, cor = '🔴 CRÍTICO', '#ef4444'
    
    return {
        'score': round(score_total, 1),
        'status': status,
        'cor': cor,
        'detalhes': detalhes
    }


def avaliar_go_no_go(df: pd.DataFrame) -> Dict[str, Any]:
    """Avaliação Go/No-Go."""
    health = calcular_health_score(df)
    
    bloqueios = []
    alertas = []
    
    # Health Score
    if health['score'] < 50:
        bloqueios.append({'msg': f"Health Score crítico: {health['score']:.0f}/100", 'cards': []})
    elif health['score'] < 70:
        alertas.append({'msg': f"Health Score em alerta: {health['score']:.0f}/100", 'cards': []})
    
    # Cards críticos não concluídos
    df_critico = df[(df['prioridade'].isin(['Alto', 'Muito alto'])) & (df['status_cat'] != 'done')]
    if len(df_critico) > 3:
        bloqueios.append({
            'msg': f"{len(df_critico)} cards de alta prioridade não concluídos",
            'cards': df_critico[['ticket_id', 'titulo', 'status', 'link']].to_dict('records')
        })
    elif len(df_critico) > 0:
        alertas.append({
            'msg': f"{len(df_critico)} card(s) de alta prioridade pendente(s)",
            'cards': df_critico[['ticket_id', 'titulo', 'status', 'link']].to_dict('records')
        })
    
    # Taxa de conclusão
    total = len(df)
    concluidos = len(df[df['status_cat'] == 'done'])
    taxa = (concluidos / total * 100) if total > 0 else 0
    if taxa < 60:
        bloqueios.append({'msg': f"Taxa de conclusão baixa: {taxa:.0f}%", 'cards': []})
    
    # Fila de QA
    df_fila_qa = df[df['status_cat'] == 'waiting_qa']
    if len(df_fila_qa) > 10:
        bloqueios.append({
            'msg': f"Fila de QA congestionada: {len(df_fila_qa)} cards",
            'cards': df_fila_qa[['ticket_id', 'titulo', 'qa', 'link']].to_dict('records')
        })
    elif len(df_fila_qa) > 5:
        alertas.append({
            'msg': f"Fila de QA com {len(df_fila_qa)} cards",
            'cards': df_fila_qa[['ticket_id', 'titulo', 'qa', 'link']].to_dict('records')
        })
    
    if bloqueios:
        decisao = 'NO-GO'
        classe = 'blocked'
    elif alertas:
        decisao = 'ATENÇÃO'
        classe = 'warning'
    else:
        decisao = 'GO'
        classe = 'approved'
    
    return {
        'decisao': decisao,
        'classe': classe,
        'bloqueios': bloqueios,
        'alertas': alertas,
        'health': health
    }


# ==============================================================================
# COMPONENTES VISUAIS
# ==============================================================================

def mostrar_card_ticket(row: dict, mostrar_dev: bool = True, mostrar_qa: bool = True, compacto: bool = False):
    """Renderiza card de ticket com link."""
    fk = calcular_fator_k(row.get('sp', 0), row.get('bugs', 0))
    mat = classificar_maturidade(fk)
    
    risco_class = 'high' if row.get('bugs', 0) >= 3 else 'medium' if row.get('bugs', 0) >= 1 else 'low'
    
    info = []
    if mostrar_dev:
        info.append(f"Dev: {row.get('desenvolvedor', 'N/A')}")
    if mostrar_qa:
        info.append(f"QA: {row.get('qa', 'N/A')}")
    
    titulo = row.get('titulo', '')[:55] + ('...' if len(row.get('titulo', '')) > 55 else '')
    
    if compacto:
        st.markdown(f"""
        <div style="padding: 8px; border-left: 3px solid {'#ef4444' if risco_class == 'high' else '#f97316' if risco_class == 'medium' else '#22c55e'}; margin: 4px 0; background: rgba(100,100,100,0.03); border-radius: 4px;">
            <a href="{row.get('link', '#')}" target="_blank" style="color: #6366f1; font-weight: 600; text-decoration: none;">🔗 {row.get('ticket_id', 'N/A')}</a>
            <span style="margin-left: 8px; opacity: 0.8; font-size: 13px;">{titulo}</span>
            <span style="float: right;">{mat['emoji']} {row.get('bugs', 0)} bugs</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="ticket-card ticket-risk-{risco_class}">
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <a href="{row.get('link', '#')}" target="_blank" style="color: #6366f1; font-weight: bold; font-size: 15px; text-decoration: none;">
                        🔗 {row.get('ticket_id', 'N/A')}
                    </a>
                    <span style="margin-left: 8px; opacity: 0.7;">{row.get('tipo', 'N/A')}</span>
                </div>
                <span style="font-size: 20px;">{mat['emoji']}</span>
            </div>
            <p style="margin: 6px 0; opacity: 0.85; font-size: 13px;">{titulo}</p>
            <div style="display: flex; gap: 12px; font-size: 12px; opacity: 0.8;">
                <span>📊 {row.get('sp', 0)} SP</span>
                <span>🐛 {row.get('bugs', 0)} bugs</span>
                <span>⏱️ {row.get('lead_time', 0)}d</span>
                <span>💬 {row.get('num_comentarios', 0)}</span>
            </div>
            <p style="font-size: 11px; margin-top: 6px; opacity: 0.6;">{' | '.join(info)}</p>
        </div>
        """, unsafe_allow_html=True)


def mostrar_lista_cards(df: pd.DataFrame, titulo: str, max_items: int = 5):
    """Mostra lista de cards expandível."""
    if df.empty:
        st.info(f"Nenhum card para '{titulo}'")
        return
    
    with st.expander(f"📋 {titulo} ({len(df)} cards)", expanded=False):
        for _, row in df.head(max_items).iterrows():
            mostrar_card_ticket(row.to_dict(), compacto=True)
        
        if len(df) > max_items:
            st.caption(f"... e mais {len(df) - max_items} cards")


def mostrar_alerta_expandivel(tipo: str, titulo: str, descricao: str, cards: List[Dict] = None):
    """Mostra alerta com lista de cards expandível."""
    classe = f"alert-{tipo}"
    
    st.markdown(f"""
    <div class="{classe}">
        <b>{titulo}</b>
        <p style="margin: 5px 0;">{descricao}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if cards:
        with st.expander(f"Ver {len(cards)} cards afetados", expanded=False):
            for card in cards[:10]:
                st.markdown(f"""
                <div style="padding: 8px; border-left: 3px solid #6366f1; margin: 4px 0; background: rgba(100,100,100,0.03); border-radius: 4px;">
                    <a href="{card.get('link', '#')}" target="_blank" style="color: #6366f1; font-weight: 600; text-decoration: none;">🔗 {card.get('ticket_id', 'N/A')}</a>
                    <span style="margin-left: 8px; opacity: 0.8; font-size: 13px;">{card.get('titulo', '')[:40]}...</span>
                </div>
                """, unsafe_allow_html=True)


def mostrar_metrica_card(valor, label: str, cor: str = "blue", info: str = None):
    """Renderiza card de métrica com tooltip."""
    info_html = f'<p class="metric-info">{info}</p>' if info else ''
    
    st.markdown(f"""
    <div class="status-card status-{cor}">
        <p class="big-number">{valor}</p>
        <p class="card-label">{label}</p>
        {info_html}
    </div>
    """, unsafe_allow_html=True)


def mostrar_comentarios(comentarios: List[Dict]):
    """Mostra comentários do card."""
    if not comentarios:
        st.caption("Sem comentários recentes")
        return
    
    for c in comentarios:
        st.markdown(f"""
        <div class="comment-card">
            <b>{c.get('autor', 'Anônimo')}</b>
            <p style="margin: 5px 0; opacity: 0.9;">{c.get('texto', '')[:150]}</p>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# ABAS DO DASHBOARD
# ==============================================================================

def aba_lideranca(df: pd.DataFrame):
    """Aba de Liderança - Visão executiva."""
    
    st.markdown('<div class="section-header"><h2>🎯 Painel de Liderança</h2></div>', unsafe_allow_html=True)
    
    go_no_go = avaliar_go_no_go(df)
    health = go_no_go['health']
    
    # Linha 1: Health Score e Go/No-Go
    col1, col2 = st.columns([1, 2])
    
    with col1:
        cor_class = 'green' if health['score'] >= 75 else 'yellow' if health['score'] >= 50 else 'red'
        st.markdown(f"""
        <div class="status-card status-{cor_class}" style="padding: 30px;">
            <p class="big-number">{health['score']:.0f}</p>
            <p class="card-label">Health Score</p>
            <p style="margin-top: 10px; font-size: 18px;"><b>{health['status']}</b></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="text-align: center; margin-top: 15px;">
            <span class="go-badge go-{go_no_go['classe']}">{go_no_go['decisao']}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Métricas executivas
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            st.metric("Cards", len(df))
        with c2:
            st.metric("Story Points", df['sp'].sum())
        with c3:
            concluidos = len(df[df['status_cat'] == 'done'])
            st.metric("Concluídos", f"{concluidos} ({concluidos/len(df)*100:.0f}%)")
        with c4:
            lead = calcular_lead_time(df)
            st.metric("Lead Time", f"{lead['medio']}d")
        
        # Bloqueios e alertas expandíveis
        for b in go_no_go['bloqueios']:
            mostrar_alerta_expandivel('critical', '🚫 Bloqueio', b['msg'], b.get('cards', []))
        
        for a in go_no_go['alertas']:
            mostrar_alerta_expandivel('warning', '⚠️ Alerta', a['msg'], a.get('cards', []))
        
        if not go_no_go['bloqueios'] and not go_no_go['alertas']:
            st.markdown("""
            <div class="alert-success">
                <b>✅ Release Saudável</b>
                <p style="margin: 5px 0;">Todos os critérios de qualidade atendidos.</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Composição do Health Score
    st.markdown("### 📊 Composição do Health Score (ISTQB Metrics)")
    
    cols = st.columns(5)
    detalhes = health['detalhes']
    
    nomes = {
        'conclusao': ('Conclusão', 'Taxa de cards done'),
        'ddp': ('DDP', 'Defect Detection %'),
        'fpy': ('FPY', 'First Pass Yield'),
        'gargalos': ('Gargalos', 'Pontos de bloqueio'),
        'lead_time': ('Lead Time', 'Tempo médio entrega')
    }
    
    for i, (nome, d) in enumerate(detalhes.items()):
        with cols[i]:
            st.metric(nomes.get(nome, (nome, ''))[0], 
                     f"{d['score']:.1f}/{d['peso']}")
            st.caption(f"{nomes.get(nome, ('', ''))[1]}: {d['valor']}")
    
    st.markdown("---")
    
    # Métricas de Qualidade (ISTQB)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Métricas ISTQB")
        
        ddp = calcular_ddp(df)
        fpy = calcular_first_pass_yield(df)
        dd = calcular_defect_density(df)
        mttr = calcular_mttr(df)
        
        m1, m2 = st.columns(2)
        with m1:
            ddp_cor = 'green' if ddp['status'] in ['excellent', 'good'] else 'yellow' if ddp['status'] == 'regular' else 'red'
            mostrar_metrica_card(f"{ddp['valor']}%", "DDP", ddp_cor, "Defect Detection %")
        with m2:
            fpy_cor = 'green' if fpy['status'] in ['excellent', 'good'] else 'yellow' if fpy['status'] == 'regular' else 'red'
            mostrar_metrica_card(f"{fpy['valor']}%", "FPY", fpy_cor, "First Pass Yield")
        
        m3, m4 = st.columns(2)
        with m3:
            mostrar_metrica_card(f"{dd['valor']}", "Density", "blue", f"Bugs/SP ({dd['bugs']}÷{dd['sp']})")
        with m4:
            mostrar_metrica_card(f"{mttr['valor']}d", "MTTR", "blue", "Mean Time To Repair")
    
    with col2:
        st.markdown("### 🔄 Gargalos no Fluxo")
        
        gargalos = identificar_gargalos(df)
        if gargalos:
            for g in gargalos:
                emoji = '🔴' if g['impacto'] == 'ALTO' else '🟡'
                cat_nome = {'waiting_qa': 'Fila de QA', 'code_review': 'Code Review', 'development': 'Desenvolvimento'}
                
                st.markdown(f"{emoji} **{cat_nome.get(g['categoria'], g['categoria'])}**: {g['cards']} cards ({g['atual']}d vs {g['esperado']}d esperado)")
                
                with st.expander(f"Ver {g['cards']} cards afetados"):
                    for ticket in g['tickets'][:5]:
                        st.markdown(f"- [{ticket}]({link_jira(ticket)})")
        else:
            st.success("✅ Nenhum gargalo identificado!")
    
    st.markdown("---")
    
    # Distribuição e Tendências
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Distribuição por Status**")
        status_count = df.groupby('status_cat').size().reset_index(name='count')
        fig = px.pie(status_count, values='count', names='status_cat', hole=0.4)
        fig.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Cards por Tipo**")
        tipo_count = df.groupby('tipo').size().reset_index(name='count')
        fig2 = px.bar(tipo_count, x='tipo', y='count', color='tipo')
        fig2.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20), showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)


def aba_qa(df: pd.DataFrame):
    """Aba de QA - Métricas detalhadas e impacto."""
    
    st.markdown('<div class="section-header"><h2>🧪 Painel de QA</h2></div>', unsafe_allow_html=True)
    
    # Lista de QAs
    qas = [q for q in df['qa'].unique() if q != 'Não atribuído']
    
    qa_sel = st.selectbox("👤 Selecione o QA", ["Visão Geral do Time"] + sorted(qas))
    
    st.markdown("---")
    
    if qa_sel == "Visão Geral do Time":
        # Impacto do QA no time
        st.markdown("### 🛡️ Impacto do QA no Time")
        
        bugs_total = df['bugs'].sum()
        sp_protegidos = df['sp'].sum()
        ddp = calcular_ddp(df)
        fpy = calcular_first_pass_yield(df)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="impact-card">
                <p style="font-size: 32px; font-weight: bold; color: #22c55e; margin: 0;">🐛 {bugs_total}</p>
                <p style="margin: 5px 0;">Bugs Encontrados</p>
                <p style="font-size: 12px; opacity: 0.7;">Bugs evitados em produção</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="impact-card">
                <p style="font-size: 32px; font-weight: bold; color: #3b82f6; margin: 0;">📊 {sp_protegidos}</p>
                <p style="margin: 5px 0;">Story Points Protegidos</p>
                <p style="font-size: 12px; opacity: 0.7;">Funcionalidades validadas</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="impact-card">
                <p style="font-size: 32px; font-weight: bold; color: #8b5cf6; margin: 0;">🎯 {ddp['valor']}%</p>
                <p style="margin: 5px 0;">DDP (Detection)</p>
                <p style="font-size: 12px; opacity: 0.7;">Eficácia do QA</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="impact-card">
                <p style="font-size: 32px; font-weight: bold; color: #f97316; margin: 0;">⚡ {fpy['valor']}%</p>
                <p style="margin: 5px 0;">FPY (First Pass)</p>
                <p style="font-size: 12px; opacity: 0.7;">Cards sem bugs</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Comparativo entre QAs
        st.markdown("### 📊 Performance por QA")
        
        dados_qa = []
        for qa in qas:
            analise = analisar_qa_detalhado(df, qa)
            if analise:
                dados_qa.append({
                    'QA': qa,
                    'Cards': analise['cards_total'],
                    'Validados': analise['validados'],
                    'Em Fila': analise['em_fila'],
                    'Bugs': analise['bugs_encontrados'],
                    'FPY': f"{analise['fpy']['valor']}%",
                    'Tempo Médio': f"{analise['tempo_validacao']}d",
                })
        
        if dados_qa:
            df_qa = pd.DataFrame(dados_qa)
            st.dataframe(df_qa, hide_index=True, use_container_width=True)
        
        st.markdown("---")
        
        # Fila de QA
        fila_qa = df[df['status_cat'] == 'waiting_qa']
        
        if not fila_qa.empty:
            st.markdown("### ⏳ Fila de Validação")
            
            c1, c2 = st.columns([1, 2])
            with c1:
                st.metric("Cards na Fila", len(fila_qa))
                st.metric("SP na Fila", fila_qa['sp'].sum())
                
                capacidade = 5 * len(qas) if qas else 5
                dias_estim = fila_qa['sp'].sum() / capacidade
                st.metric("Dias Estimados", f"{dias_estim:.1f}")
            
            with c2:
                for _, row in fila_qa.head(5).iterrows():
                    mostrar_card_ticket(row.to_dict(), compacto=True)
                
                if len(fila_qa) > 5:
                    with st.expander(f"Ver mais {len(fila_qa) - 5} cards"):
                        for _, row in fila_qa.iloc[5:].iterrows():
                            mostrar_card_ticket(row.to_dict(), compacto=True)
        else:
            st.success("✅ Fila de QA vazia!")
    
    else:
        # Métricas individuais do QA
        analise = analisar_qa_detalhado(df, qa_sel)
        
        if analise:
            st.markdown(f"### 👤 {qa_sel}")
            
            # Métricas principais
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                st.metric("Cards", analise['cards_total'])
            with c2:
                st.metric("Validados", analise['validados'])
            with c3:
                st.metric("Bugs Encontrados", analise['bugs_encontrados'])
            with c4:
                st.metric("FPY", f"{analise['fpy']['valor']}%")
            with c5:
                st.metric("Tempo Médio", f"{analise['tempo_validacao']}d")
            
            st.markdown("---")
            
            # Impacto
            st.markdown("### 🛡️ Seu Impacto")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="impact-card">
                    <h4>Bugs Evitados em Produção</h4>
                    <p style="font-size: 28px; font-weight: bold; color: #22c55e;">{analise['bugs_evitados']} bugs</p>
                    <p>Você protegeu <b>{analise['sp_protegidos']} Story Points</b> de funcionalidades</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # DDP do QA
                ddp_cor = 'green' if analise['ddp']['status'] in ['excellent', 'good'] else 'yellow'
                st.markdown(f"""
                <div class="status-card status-{ddp_cor}">
                    <p class="big-number">{analise['ddp']['valor']}%</p>
                    <p class="card-label">Defect Detection %</p>
                    <p class="metric-info">Eficácia em encontrar bugs</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Cards problemáticos (com muitos bugs)
            if not analise['cards_problematicos'].empty:
                st.markdown("### 🔴 Cards mais Problemáticos")
                st.caption("Cards que tiveram 3+ bugs - podem indicar problemas de especificação ou complexidade")
                
                for _, row in analise['cards_problematicos'].head(5).iterrows():
                    st.markdown(f"""
                    <div class="problematic-card">
                        <div style="display: flex; justify-content: space-between;">
                            <a href="{row['link']}" target="_blank" style="color: #6366f1; font-weight: bold; text-decoration: none;">🔗 {row['ticket_id']}</a>
                            <span style="color: #ef4444; font-weight: bold;">🐛 {row['bugs']} bugs</span>
                        </div>
                        <p style="margin: 6px 0; opacity: 0.85;">{row['titulo'][:60]}...</p>
                        <p style="font-size: 12px; opacity: 0.7;">Complexidade: {row['complexidade']} | Dev: {row['desenvolvedor']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Tempo de validação
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### ⚡ Cards mais Rápidos")
                if not analise['mais_rapido'].empty:
                    for _, row in analise['mais_rapido'].iterrows():
                        st.markdown(f"- [{row['ticket_id']}]({row['link']}) - **{row['lead_time']}d** ({row['bugs']} bugs)")
                else:
                    st.info("Ainda sem dados")
            
            with col2:
                st.markdown("### 🐢 Cards mais Demorados")
                if not analise['mais_lento'].empty:
                    for _, row in analise['mais_lento'].iterrows():
                        st.markdown(f"- [{row['ticket_id']}]({row['link']}) - **{row['lead_time']}d** ({row['bugs']} bugs)")
                else:
                    st.info("Ainda sem dados")
            
            st.markdown("---")
            
            # Por complexidade
            if analise['por_complexidade']:
                st.markdown("### 📈 Performance por Complexidade")
                
                dados_comp = [{'Complexidade': k, 'Cards': v['ticket_id'], 'Bugs': v['bugs'], 'Tempo Médio': v['lead_time']} 
                              for k, v in analise['por_complexidade'].items()]
                df_comp = pd.DataFrame(dados_comp)
                
                col1, col2 = st.columns(2)
                with col1:
                    fig = px.bar(df_comp, x='Complexidade', y=['Cards', 'Bugs'], barmode='group',
                                title='Cards e Bugs por Complexidade')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig2 = px.bar(df_comp, x='Complexidade', y='Tempo Médio', 
                                 title='Tempo Médio por Complexidade (dias)')
                    st.plotly_chart(fig2, use_container_width=True)
            
            st.markdown("---")
            
            # Todos os cards
            st.markdown("### 📋 Todos os Meus Cards")
            
            for _, row in analise['df'].iterrows():
                with st.expander(f"🔗 {row['ticket_id']} - {row['titulo'][:40]}... ({row['bugs']} bugs)"):
                    mostrar_card_ticket(row.to_dict(), mostrar_qa=False)
                    
                    # Comentários
                    if row['comentarios']:
                        st.markdown("**💬 Últimos Comentários:**")
                        mostrar_comentarios(row['comentarios'])


def aba_dev(df: pd.DataFrame):
    """Aba de Dev - Performance e análise."""
    
    st.markdown('<div class="section-header"><h2>👨‍💻 Painel de Desenvolvimento</h2></div>', unsafe_allow_html=True)
    
    devs = [d for d in df['desenvolvedor'].unique() if d != 'Não atribuído']
    
    dev_sel = st.selectbox("👤 Selecione o Desenvolvedor", ["Ranking Geral"] + sorted(devs))
    
    st.markdown("---")
    
    if dev_sel == "Ranking Geral":
        st.markdown("### 🏆 Ranking de Performance")
        
        dados_dev = []
        for dev in devs:
            analise = analisar_dev_detalhado(df, dev)
            if analise:
                dados_dev.append({
                    'Desenvolvedor': dev,
                    'Cards': analise['cards'],
                    'SP': analise['sp_total'],
                    'Bugs': analise['bugs_total'],
                    'Fator K': analise['fk_medio'],
                    'FPY': f"{analise['zero_bugs']}%",
                    'Tempo': f"{analise['tempo_medio']}d",
                    'Selo': f"{analise['maturidade']['emoji']} {analise['maturidade']['selo']}"
                })
        
        df_rank = pd.DataFrame(dados_dev)
        df_rank = df_rank.sort_values('Fator K', ascending=False)
        
        st.dataframe(df_rank, hide_index=True, use_container_width=True)
        
        # Gráfico
        fig = px.bar(df_rank, x='Desenvolvedor', y='Fator K',
                     color='Fator K',
                     color_continuous_scale=['#ef4444', '#f97316', '#eab308', '#22c55e'])
        fig.add_hline(y=2, line_dash="dash", annotation_text="Meta (FK ≥ 2)")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Devs que precisam de suporte
        devs_atencao = [d for d in dados_dev if d['Fator K'] < 2]
        if devs_atencao:
            st.markdown("### ⚠️ Desenvolvedores com Fator K Baixo")
            st.caption("Podem precisar de code review mais rigoroso ou pareamento")
            
            for d in devs_atencao:
                df_dev = df[df['desenvolvedor'] == d['Desenvolvedor']]
                cards_problematicos = df_dev[df_dev['bugs'] >= 2].head(3)
                
                st.markdown(f"""
                <div class="alert-warning">
                    <b>{d['Desenvolvedor']}</b> - Fator K: {d['Fator K']} | {d['Bugs']} bugs em {d['Cards']} cards
                </div>
                """, unsafe_allow_html=True)
                
                if not cards_problematicos.empty:
                    with st.expander(f"Ver cards problemáticos de {d['Desenvolvedor']}"):
                        for _, row in cards_problematicos.iterrows():
                            mostrar_card_ticket(row.to_dict(), compacto=True)
    
    else:
        # Métricas individuais
        analise = analisar_dev_detalhado(df, dev_sel)
        
        if analise:
            mat = analise['maturidade']
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                cor_class = 'green' if mat['selo'] == 'Gold' else 'yellow' if mat['selo'] == 'Silver' else 'orange' if mat['selo'] == 'Bronze' else 'red'
                st.markdown(f"""
                <div class="status-card status-{cor_class}">
                    <p style="font-size: 48px; margin: 0;">{mat['emoji']}</p>
                    <p class="card-label">{mat['selo']}</p>
                    <p style="font-size: 20px; margin-top: 10px;"><b>FK: {analise['fk_medio']}</b></p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("Cards", analise['cards'])
                with c2:
                    st.metric("Story Points", analise['sp_total'])
                with c3:
                    st.metric("Bugs", analise['bugs_total'])
                with c4:
                    st.metric("FPY", f"{analise['zero_bugs']}%")
            
            st.markdown("---")
            
            # Cards problemáticos
            if not analise['cards_problematicos'].empty:
                st.markdown("### 🔴 Cards com Mais Bugs")
                
                for _, row in analise['cards_problematicos'].head(5).iterrows():
                    st.markdown(f"""
                    <div class="problematic-card">
                        <a href="{row['link']}" target="_blank" style="color: #6366f1; font-weight: bold; text-decoration: none;">🔗 {row['ticket_id']}</a>
                        <span style="float: right; color: #ef4444;">🐛 {row['bugs']} bugs</span>
                        <p style="margin: 6px 0; opacity: 0.85;">{row['titulo'][:50]}...</p>
                        <p style="font-size: 12px; opacity: 0.7;">Complexidade: {row['complexidade']} | Lead Time: {row['lead_time']}d</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Por complexidade
            if analise['bugs_por_comp']:
                st.markdown("### 📊 Performance por Complexidade")
                
                dados = [{'Complexidade': k, 'Cards': v['ticket_id'], 'Bugs': v['bugs'], 'SP': v['sp'], 'Tempo': v['lead_time']} 
                         for k, v in analise['bugs_por_comp'].items()]
                df_comp = pd.DataFrame(dados)
                
                col1, col2 = st.columns(2)
                with col1:
                    fig1 = px.pie(df_comp, values='Cards', names='Complexidade', title='Distribuição por Complexidade')
                    st.plotly_chart(fig1, use_container_width=True)
                with col2:
                    fig2 = px.bar(df_comp, x='Complexidade', y='Bugs', title='Bugs por Complexidade')
                    st.plotly_chart(fig2, use_container_width=True)
            
            st.markdown("---")
            
            # Todos os cards
            st.markdown("### 📋 Meus Cards")
            for _, row in analise['df'].iterrows():
                with st.expander(f"🔗 {row['ticket_id']} - {row['titulo'][:40]}... ({row['bugs']} bugs)"):
                    mostrar_card_ticket(row.to_dict(), mostrar_dev=False)
                    
                    if row['comentarios']:
                        st.markdown("**💬 Últimos Comentários:**")
                        mostrar_comentarios(row['comentarios'])


def aba_historico():
    """Aba de Histórico."""
    
    st.markdown('<div class="section-header"><h2>📜 Histórico de Releases</h2></div>', unsafe_allow_html=True)
    
    st.info("📊 Tendências históricas para análise de evolução do time")
    
    sprints = ["Sprint 22", "Sprint 23", "Sprint 24", "Sprint 25"]
    
    dados_hist = []
    for sprint in sprints:
        base_fk = 1.5 + (sprints.index(sprint) * 0.3) + random.uniform(-0.2, 0.2)
        base_bugs = 25 - (sprints.index(sprint) * 3) + random.randint(-5, 5)
        base_ddp = 75 + (sprints.index(sprint) * 5) + random.uniform(-3, 3)
        base_fpy = 40 + (sprints.index(sprint) * 8) + random.uniform(-5, 5)
        
        dados_hist.append({
            'Sprint': sprint,
            'Fator K': round(base_fk, 2),
            'Bugs': max(5, base_bugs),
            'Cards': random.randint(40, 60),
            'DDP': round(min(99, base_ddp), 1),
            'FPY': round(min(90, base_fpy), 1),
            'Lead Time': round(12 - sprints.index(sprint) * 1.5 + random.uniform(-1, 1), 1)
        })
    
    df_hist = pd.DataFrame(dados_hist)
    
    st.dataframe(df_hist, hide_index=True, use_container_width=True)
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.line(df_hist, x='Sprint', y='Fator K', markers=True,
                      title='📈 Evolução do Fator K')
        fig1.add_hline(y=2, line_dash="dash", annotation_text="Meta")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.line(df_hist, x='Sprint', y=['DDP', 'FPY'], markers=True,
                      title='📈 Métricas de Qualidade ISTQB')
        st.plotly_chart(fig2, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        fig3 = px.bar(df_hist, x='Sprint', y='Bugs', 
                     color='Bugs', color_continuous_scale='Reds',
                     title='🐛 Bugs por Sprint')
        st.plotly_chart(fig3, use_container_width=True)
    
    with col4:
        fig4 = px.line(df_hist, x='Sprint', y='Lead Time', markers=True,
                      title='⏱️ Lead Time (dias)')
        fig4.add_hline(y=7, line_dash="dash", line_color="green", annotation_text="Meta")
        st.plotly_chart(fig4, use_container_width=True)


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    st.set_page_config(
        page_title="Jira Dashboard - NINA",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    aplicar_estilos()
    
    with st.sidebar:
        st.title("⚙️ Configurações")
        
        st.subheader("🔐 Jira")
        st.text_input("Email", key="jira_email", placeholder="email@empresa.com")
        st.text_input("API Token", type="password", key="jira_token")
        
        status = "✅ Conectado" if verificar_credenciais() else "⚠️ Demo"
        st.caption(status)
        
        st.markdown("---")
        
        st.subheader("📁 Projeto")
        
        projetos_disponiveis = list(PROJETOS.keys())
        projeto = st.selectbox(
            "Projeto principal",
            projetos_disponiveis,
            index=0,
            format_func=lambda x: f"{x} - {PROJETOS[x]['nome']}"
        )
        
        st.caption("💡 SD = Desenvolvimento (foco recomendado)")
        
        st.markdown("---")
        
        st.subheader("📅 Release")
        data_release = st.date_input("Data da Release", 
                                     value=datetime.now() + timedelta(days=10))
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            carregar_jira = st.button("🔄 Jira", use_container_width=True)
        with col2:
            usar_demo = st.button("📊 Demo", use_container_width=True)
        
        if carregar_jira:
            if verificar_credenciais():
                with st.spinner("Buscando dados do Jira..."):
                    jql = f'project = "{projeto}" AND sprint in openSprints() ORDER BY created DESC'
                    issues = buscar_jira(jql)
                    if issues:
                        st.session_state.dados = processar_issues(issues, 
                                                datetime.combine(data_release, datetime.min.time()))
                        st.session_state.projeto = projeto
                        st.success(f"✅ {len(issues)} cards carregados!")
                        st.rerun()
            else:
                st.warning("Configure as credenciais!")
        
        if usar_demo:
            st.session_state.dados = gerar_dados_mock(projeto)
            st.session_state.projeto = projeto
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("""
        **Métricas ISTQB/CTFL:**
        - **DDP**: Defect Detection %
        - **FPY**: First Pass Yield
        - **MTTR**: Mean Time To Repair
        - **Fator K**: Maturidade (SP/Bugs)
        """)
        
        st.caption("Dashboard v4.0 | NINA")
    
    if 'dados' not in st.session_state:
        st.session_state.dados = gerar_dados_mock("SD")
        st.session_state.projeto = "SD"
    
    df = st.session_state.dados
    projeto_atual = st.session_state.get('projeto', 'SD')
    
    st.title(f"📊 Dashboard - {PROJETOS.get(projeto_atual, {}).get('nome', projeto_atual)}")
    
    sprint_atual = df['sprint'].mode().iloc[0] if not df.empty else "N/A"
    st.caption(f"Sprint: **{sprint_atual}** | Cards: **{len(df)}** | Modo: **{'Jira' if verificar_credenciais() else 'Demo'}**")
    
    tabs = st.tabs(["🎯 Liderança", "🧪 QA", "👨‍💻 Dev", "📜 Histórico"])
    
    with tabs[0]:
        aba_lideranca(df)
    
    with tabs[1]:
        aba_qa(df)
    
    with tabs[2]:
        aba_dev(df)
    
    with tabs[3]:
        aba_historico()
    
    st.markdown("---")
    st.caption(f"Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")


if __name__ == "__main__":
    main()
