"""
================================================================================
JIRA DASHBOARD - MÉTRICAS DE QUALIDADE E ENTREGA v2.0
================================================================================
Autor: QA Lead - NINA Tecnologia
Descrição: Dashboard Streamlit com visões específicas para Liderança, QA e Dev.

Navegação por Abas:
- 🎯 Liderança: Decisões estratégicas e saúde da release
- 🧪 QA: Métricas individuais dos testadores
- 👨‍💻 Dev: Performance individual dos desenvolvedores
- 📜 Histórico: Releases anteriores

================================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import requests
from typing import Optional, Dict, List, Any
import json

# ==============================================================================
# CONFIGURAÇÕES GLOBAIS
# ==============================================================================

JIRA_BASE_URL = "https://ninatecnologia.atlassian.net"

CUSTOM_FIELDS = {
    "story_points": "customfield_10016",
    "story_points_alt1": "customfield_10036",
    "story_points_alt2": "customfield_11091",
    "sprint": "customfield_10020",
    "bugs_encontrados": "customfield_11157",
    "dias_ate_release": "customfield_11357",
    "janela_testes": "customfield_11358",
    "status_maturidade": "customfield_11224",
    "complexidade_teste": "customfield_11290",
    "plano_testes": "customfield_11024",
    "qa_responsavel": "customfield_10784",
    "qa_user": "customfield_10487",
    "desenvolvedor": "customfield_10455",
    "desenvolvedor_array": "customfield_10785",
}

TIPOS_TICKET = {
    "HOTFIX": ["Hotfix", "Hotfeature"],
    "BUG": ["Bug", "Impeditivo de entrega"],
    "TAREFA": ["Tarefa", "Task", "Subtarefa"],
    "EPIC": ["Epic"],
    "SUGESTÃO": ["Sugestão", "Improvement"],
    "DEV_PAGO": ["Desenvolvimento pago"],
}

SELOS_MATURIDADE = {
    "Gold": {"min": 3.0, "cor": "#FFD700", "emoji": "🥇"},
    "Silver": {"min": 2.0, "cor": "#C0C0C0", "emoji": "🥈"},
    "Bronze": {"min": 1.0, "cor": "#CD7F32", "emoji": "🥉"},
    "Risco": {"min": 0, "cor": "#FF4444", "emoji": "⚠️"},
}

# ==============================================================================
# CSS PARA DARK MODE E ESTILIZAÇÃO
# ==============================================================================

def aplicar_css_customizado():
    """Aplica CSS que funciona bem em dark mode e light mode."""
    st.markdown("""
    <style>
    /* Cards com fundo que funciona em dark mode */
    .metric-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.1));
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
    }
    
    /* Status cards com cores que funcionam em ambos os modos */
    .status-card-green {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(22, 163, 74, 0.1));
        border: 2px solid rgba(34, 197, 94, 0.5);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    
    .status-card-yellow {
        background: linear-gradient(135deg, rgba(234, 179, 8, 0.15), rgba(202, 138, 4, 0.1));
        border: 2px solid rgba(234, 179, 8, 0.5);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    
    .status-card-red {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(220, 38, 38, 0.1));
        border: 2px solid rgba(239, 68, 68, 0.5);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    
    .status-card-blue {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(37, 99, 235, 0.1));
        border: 2px solid rgba(59, 130, 246, 0.5);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    
    .status-card-orange {
        background: linear-gradient(135deg, rgba(249, 115, 22, 0.15), rgba(234, 88, 12, 0.1));
        border: 2px solid rgba(249, 115, 22, 0.5);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    
    /* Números grandes dentro dos cards */
    .big-number {
        font-size: 42px;
        font-weight: bold;
        margin: 0;
        line-height: 1.2;
    }
    
    .card-label {
        font-size: 14px;
        opacity: 0.8;
        margin-top: 5px;
    }
    
    /* Risk card */
    .risk-card {
        border-radius: 12px;
        padding: 15px;
        margin: 8px 0;
        border-left: 4px solid;
    }
    
    .risk-high {
        background: rgba(239, 68, 68, 0.1);
        border-left-color: #ef4444;
    }
    
    .risk-medium {
        background: rgba(249, 115, 22, 0.1);
        border-left-color: #f97316;
    }
    
    .risk-low {
        background: rgba(234, 179, 8, 0.1);
        border-left-color: #eab308;
    }
    
    /* Links do Jira */
    .jira-link {
        color: #6366f1 !important;
        text-decoration: none;
        font-weight: 600;
    }
    
    .jira-link:hover {
        text-decoration: underline;
    }
    
    /* Seção header */
    .section-header {
        background: linear-gradient(90deg, rgba(99, 102, 241, 0.2), transparent);
        padding: 10px 15px;
        border-radius: 8px;
        margin: 20px 0 15px 0;
        border-left: 4px solid #6366f1;
    }
    
    /* Tabela customizada */
    .dataframe {
        font-size: 13px !important;
    }
    
    /* Esconder âncoras de seção */
    .css-1629p8f h1, .css-1629p8f h2, .css-1629p8f h3 {
        scroll-margin-top: 2rem;
    }
    
    /* Melhorar tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 8px 8px 0 0;
    }
    </style>
    """, unsafe_allow_html=True)


# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================

def gerar_link_jira(ticket_id: str) -> str:
    """Gera link direto para o ticket no Jira."""
    return f"{JIRA_BASE_URL}/browse/{ticket_id}"


def criar_link_jira_html(ticket_id: str) -> str:
    """Cria HTML de link clicável para o Jira."""
    url = gerar_link_jira(ticket_id)
    return f'<a href="{url}" target="_blank" class="jira-link">🔗 {ticket_id}</a>'


def verificar_credenciais_jira() -> bool:
    """Verifica se as credenciais do Jira estão configuradas."""
    email = st.session_state.get("jira_email", "")
    token = st.session_state.get("jira_token", "")
    return bool(email and token)


def buscar_dados_jira(jql_query: str) -> Optional[List[Dict]]:
    """Executa consulta JQL na API do Jira."""
    if not verificar_credenciais_jira():
        return None
    
    email = st.session_state.get("jira_email")
    token = st.session_state.get("jira_token")
    
    url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    
    fields = [
        "summary", "status", "issuetype", "assignee", "created", "updated",
        "resolutiondate", "priority", "project", "labels", "components",
        CUSTOM_FIELDS["story_points"], CUSTOM_FIELDS["story_points_alt1"],
        CUSTOM_FIELDS["story_points_alt2"], CUSTOM_FIELDS["sprint"],
        CUSTOM_FIELDS["bugs_encontrados"], CUSTOM_FIELDS["dias_ate_release"],
        CUSTOM_FIELDS["janela_testes"], CUSTOM_FIELDS["status_maturidade"],
        CUSTOM_FIELDS["complexidade_teste"], CUSTOM_FIELDS["plano_testes"],
        CUSTOM_FIELDS["qa_responsavel"], CUSTOM_FIELDS["qa_user"],
        CUSTOM_FIELDS["desenvolvedor"], CUSTOM_FIELDS["desenvolvedor_array"],
    ]
    
    payload = json.dumps({"jql": jql_query, "maxResults": 100, "fields": fields})
    
    try:
        response = requests.post(url, headers=headers, data=payload, auth=(email, token))
        response.raise_for_status()
        return response.json().get("issues", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar com Jira: {str(e)}")
        return None


def transformar_dados_jira(issues: List[Dict], data_release: datetime) -> pd.DataFrame:
    """Transforma dados da API do Jira para DataFrame."""
    dados = []
    
    for issue in issues:
        fields = issue.get('fields', {})
        
        issue_type = fields.get('issuetype', {}).get('name', 'Unknown')
        tipo = 'TAREFA'
        for tipo_key, nomes in TIPOS_TICKET.items():
            if issue_type in nomes:
                tipo = tipo_key
                break
        
        projeto = fields.get('project', {}).get('key', 'N/A')
        
        desenvolvedor = 'Não atribuído'
        assignee = fields.get('assignee')
        if assignee:
            desenvolvedor = assignee.get('displayName', 'Não atribuído')
        dev_custom = fields.get(CUSTOM_FIELDS['desenvolvedor'])
        if dev_custom and isinstance(dev_custom, dict):
            desenvolvedor = dev_custom.get('displayName', desenvolvedor)
        
        story_points = (
            fields.get(CUSTOM_FIELDS['story_points']) or 
            fields.get(CUSTOM_FIELDS['story_points_alt1']) or 
            fields.get(CUSTOM_FIELDS['story_points_alt2']) or 0
        )
        
        sprint_field = fields.get(CUSTOM_FIELDS['sprint'], [])
        if sprint_field and isinstance(sprint_field, list) and len(sprint_field) > 0:
            sprint = sprint_field[-1].get('name', 'Sem Sprint')
        else:
            sprint = 'Sem Sprint'
        
        bugs_encontrados = fields.get(CUSTOM_FIELDS['bugs_encontrados'], 0) or 0
        janela_testes = fields.get(CUSTOM_FIELDS['janela_testes'], '')
        dias_ate_release = fields.get(CUSTOM_FIELDS['dias_ate_release'], '')
        status_maturidade = fields.get(CUSTOM_FIELDS['status_maturidade'], '')
        
        complexidade_teste = fields.get(CUSTOM_FIELDS['complexidade_teste'])
        if complexidade_teste and isinstance(complexidade_teste, dict):
            complexidade_teste = complexidade_teste.get('value', 'N/A')
        else:
            complexidade_teste = 'N/A'
        
        qa_responsavel = 'Não atribuído'
        qa_field = fields.get(CUSTOM_FIELDS['qa_user']) or fields.get(CUSTOM_FIELDS['qa_responsavel'])
        if qa_field:
            if isinstance(qa_field, dict):
                qa_responsavel = qa_field.get('displayName', 'Não atribuído')
            elif isinstance(qa_field, list) and len(qa_field) > 0:
                qa_responsavel = qa_field[0].get('displayName', 'Não atribuído')
        
        prioridade = fields.get('priority', {})
        prioridade_nome = prioridade.get('name', 'Médio') if prioridade else 'Médio'
        
        data_criacao_str = fields.get('created', '')
        try:
            data_criacao = datetime.fromisoformat(data_criacao_str.replace('Z', '+00:00')).replace(tzinfo=None)
        except:
            data_criacao = datetime.now()
        
        data_atualizacao_str = fields.get('updated', '')
        try:
            data_atualizacao = datetime.fromisoformat(data_atualizacao_str.replace('Z', '+00:00')).replace(tzinfo=None)
        except:
            data_atualizacao = datetime.now()
        
        dados.append({
            'ticket_id': issue.get('key', ''),
            'titulo': fields.get('summary', ''),
            'tipo': tipo,
            'tipo_original': issue_type,
            'status': fields.get('status', {}).get('name', 'Unknown'),
            'projeto': projeto,
            'desenvolvedor': desenvolvedor,
            'qa_responsavel': qa_responsavel,
            'story_points': int(story_points) if story_points else 0,
            'bugs_encontrados': int(bugs_encontrados) if bugs_encontrados else 0,
            'sprint': sprint,
            'prioridade': prioridade_nome,
            'complexidade_teste': complexidade_teste,
            'status_maturidade': status_maturidade or 'N/A',
            'janela_testes': janela_testes,
            'dias_ate_release': dias_ate_release,
            'data_criacao': data_criacao,
            'data_atualizacao': data_atualizacao,
            'data_release': data_release,
            'link_jira': gerar_link_jira(issue.get('key', ''))
        })
    
    return pd.DataFrame(dados)


def buscar_e_transformar_dados_jira(projetos: str, data_release: datetime) -> Optional[pd.DataFrame]:
    """Busca e transforma dados do Jira."""
    proj_list = [p.strip() for p in projetos.split(',')]
    if len(proj_list) == 1:
        jql = f'project = "{proj_list[0]}" AND created >= -90d ORDER BY created DESC'
    else:
        proj_in = ', '.join([f'"{p}"' for p in proj_list])
        jql = f'project IN ({proj_in}) AND created >= -90d ORDER BY created DESC'
    
    issues = buscar_dados_jira(jql)
    
    if issues is None or len(issues) == 0:
        return None
    
    return transformar_dados_jira(issues, data_release)


# ==============================================================================
# DADOS MOCKADOS
# ==============================================================================

def gerar_dados_mockados(sprint_atual: bool = True) -> pd.DataFrame:
    """Gera dados fictícios para demonstração."""
    
    desenvolvedores = [
        "Ellen Haderspeck", "Christopher Krauss", "Augusto Oliveira", 
        "Rafael Teles", "João Pedro Menegali", "Carlos Daniel",
        "Cristian Yamamoto", "Elinton Dozol"
    ]
    
    qas = ["Irla Rafaela", "Larissa Carneiro"]
    
    tipos = ["TAREFA", "BUG", "HOTFIX", "SUGESTÃO"]
    tipos_originais = {"TAREFA": "Tarefa", "BUG": "Bug", "HOTFIX": "Hotfix", "SUGESTÃO": "Sugestão"}
    
    status_list = [
        "Backlog", "Em andamento", "EM DESENVOLVIMENTO", 
        "AGUARDANDO VALIDAÇÃO", "EM REVISÃO", "Concluído"
    ]
    
    projetos = ["SD", "VALPROD", "PB", "QA"]
    
    if sprint_atual:
        sprints = ["Sprint 25 (Atual)"]
    else:
        sprints = ["Sprint 22", "Sprint 23", "Sprint 24"]
    
    complexidades = ["Baixa", "Média", "Alta", "Muito Alta"]
    prioridades = ["Baixo", "Médio", "Alto", "Muito alto"]
    
    dados = []
    hoje = datetime.now()
    data_release = hoje + timedelta(days=random.randint(5, 15))
    
    num_tickets = 50 if sprint_atual else 80
    
    for i in range(num_tickets):
        tipo = random.choices(tipos, weights=[50, 25, 15, 10])[0]
        projeto = random.choices(projetos, weights=[40, 30, 20, 10])[0]
        
        if tipo == "TAREFA":
            sp = random.choice([3, 5, 8, 13])
        elif tipo == "BUG":
            sp = random.choice([1, 2, 3])
        elif tipo == "HOTFIX":
            sp = random.choice([1, 2])
        else:
            sp = random.choice([1, 2, 3, 5])
        
        if tipo == "TAREFA":
            bugs = random.choices([0, 1, 2, 3, 4, 5], weights=[30, 25, 20, 15, 7, 3])[0]
        else:
            bugs = random.choices([0, 1, 2], weights=[70, 20, 10])[0]
        
        data_criacao = hoje - timedelta(days=random.randint(1, 60))
        status = random.choice(status_list)
        sprint = random.choice(sprints)
        
        janela = random.randint(2, 15) if status in ["AGUARDANDO VALIDAÇÃO", "Concluído", "EM REVISÃO"] else None
        
        ticket_id = f"{projeto}-{1000 + i}"
        
        dados.append({
            "ticket_id": ticket_id,
            "titulo": f"{tipos_originais[tipo]} - Implementação #{i+1}",
            "tipo": tipo,
            "tipo_original": tipos_originais[tipo],
            "status": status,
            "projeto": projeto,
            "desenvolvedor": random.choice(desenvolvedores),
            "qa_responsavel": random.choice(qas),
            "story_points": sp,
            "bugs_encontrados": bugs,
            "sprint": sprint,
            "prioridade": random.choices(prioridades, weights=[10, 60, 25, 5])[0],
            "complexidade_teste": random.choice(complexidades),
            "status_maturidade": random.choice(["Gold", "Silver", "Bronze", "Risco", "N/A"]),
            "janela_testes": str(janela) if janela else "",
            "dias_ate_release": str(random.randint(3, 20)),
            "data_criacao": data_criacao,
            "data_atualizacao": data_criacao + timedelta(days=random.randint(0, 10)),
            "data_release": data_release if sprint_atual else data_criacao + timedelta(days=14),
            "link_jira": gerar_link_jira(ticket_id)
        })
    
    return pd.DataFrame(dados)


# ==============================================================================
# FUNÇÕES DE CÁLCULO DE MÉTRICAS
# ==============================================================================

def calcular_fator_k(story_points: int, bugs: int, rigor: float = 1.5) -> float:
    """Calcula o Fator K (Maturidade de Entrega)."""
    if bugs == 0:
        return float('inf')
    return story_points / (bugs * rigor)


def classificar_maturidade(fator_k: float) -> Dict[str, Any]:
    """Classifica o Fator K em um selo de maturidade."""
    if fator_k == float('inf'):
        return {"selo": "Gold", "cor": SELOS_MATURIDADE["Gold"]["cor"],
                "emoji": SELOS_MATURIDADE["Gold"]["emoji"], "descricao": "Excelente! Sem bugs."}
    
    for selo, config in SELOS_MATURIDADE.items():
        if fator_k >= config["min"]:
            return {"selo": selo, "cor": config["cor"], "emoji": config["emoji"],
                    "descricao": f"Fator K: {fator_k:.2f}"}
    
    return {"selo": "Risco", "cor": SELOS_MATURIDADE["Risco"]["cor"],
            "emoji": SELOS_MATURIDADE["Risco"]["emoji"], "descricao": "Atenção! Alta taxa de bugs."}


def analisar_go_no_go(df: pd.DataFrame) -> Dict[str, Any]:
    """Análise Go/No-Go automática para decisão de release."""
    df_analise = df.copy()
    
    df_analise['janela_num'] = pd.to_numeric(df_analise['janela_testes'], errors='coerce').fillna(0)
    df_analise['dias_release_num'] = pd.to_numeric(df_analise['dias_ate_release'], errors='coerce').fillna(999)
    
    df_analise['fator_k'] = df_analise.apply(
        lambda row: calcular_fator_k(row['story_points'], row['bugs_encontrados']), axis=1)
    
    def calcular_score_risco(row):
        score = 0
        fk = row['fator_k'] if row['fator_k'] != float('inf') else 10
        if fk < 1: score += 40
        elif fk < 2: score += 20
        elif fk < 3: score += 10
        
        if row['complexidade_teste'] == 'Muito Alta': score += 30
        elif row['complexidade_teste'] == 'Alta': score += 20
        elif row['complexidade_teste'] == 'Média': score += 10
        
        if row['janela_num'] > 0:
            if row['janela_num'] < 2: score += 30
            elif row['janela_num'] < 3: score += 20
            elif row['janela_num'] < 5: score += 10
        
        if row['bugs_encontrados'] >= 5: score += 25
        elif row['bugs_encontrados'] >= 3: score += 15
        elif row['bugs_encontrados'] >= 1: score += 5
        
        return score
    
    df_analise['score_risco'] = df_analise.apply(calcular_score_risco, axis=1)
    
    def decisao_go_no_go(score):
        if score >= 70: return '🔴 NO-GO'
        elif score >= 50: return '🟠 RISCO'
        elif score >= 30: return '🟡 ATENÇÃO'
        else: return '🟢 GO'
    
    df_analise['decisao'] = df_analise['score_risco'].apply(decisao_go_no_go)
    
    cards_no_go = df_analise[df_analise['score_risco'] >= 70]
    cards_risco = df_analise[(df_analise['score_risco'] >= 50) & (df_analise['score_risco'] < 70)]
    cards_atencao = df_analise[(df_analise['score_risco'] >= 30) & (df_analise['score_risco'] < 50)]
    cards_go = df_analise[df_analise['score_risco'] < 30]
    
    return {
        'df_completo': df_analise,
        'no_go': cards_no_go,
        'risco_alto': cards_risco,
        'atencao': cards_atencao,
        'aprovados': cards_go,
        'total_no_go': len(cards_no_go),
        'total_risco': len(cards_risco),
        'total_atencao': len(cards_atencao),
        'total_go': len(cards_go)
    }


def calcular_saude_release(df: pd.DataFrame) -> Dict[str, Any]:
    """Calcula a saúde geral da release."""
    if df.empty:
        return {'status': '⚪ Sem Dados', 'cor': '#808080', 'score': 0, 'motivos': []}
    
    analise = analisar_go_no_go(df)
    total_cards = len(df)
    
    pct_aprovados = (analise['total_go'] / total_cards) * 100
    pct_risco = ((analise['total_no_go'] + analise['total_risco']) / total_cards) * 100
    
    df_temp = df.copy()
    df_temp['fator_k'] = df_temp.apply(
        lambda row: calcular_fator_k(row['story_points'], row['bugs_encontrados']), axis=1)
    df_temp['fator_k_calc'] = df_temp['fator_k'].apply(lambda x: 10 if x == float('inf') else x)
    fator_k_medio = df_temp['fator_k_calc'].mean()
    
    total_bugs = df['bugs_encontrados'].sum()
    total_sp = df['story_points'].sum()
    taxa_bugs = (total_bugs / total_sp * 100) if total_sp > 0 else 0
    
    score = 0
    motivos = []
    
    score += (pct_aprovados / 100) * 40
    
    if fator_k_medio >= 3: score += 30
    elif fator_k_medio >= 2: score += 20
    elif fator_k_medio >= 1: score += 10
    else: motivos.append(f"Fator K médio baixo: {fator_k_medio:.2f}")
    
    if taxa_bugs < 5: score += 30
    elif taxa_bugs < 10: score += 20
    elif taxa_bugs < 20: score += 10
    else: motivos.append(f"Taxa de bugs alta: {taxa_bugs:.1f}%")
    
    if analise['total_no_go'] > 0:
        motivos.append(f"{analise['total_no_go']} card(s) NO-GO")
    if analise['total_risco'] > 0:
        motivos.append(f"{analise['total_risco']} card(s) risco alto")
    
    if score >= 80:
        status, cor = '🟢 ESTÁVEL', '#22c55e'
    elif score >= 60:
        status, cor = '🟡 ALERTA', '#eab308'
    else:
        status, cor = '🔴 CRÍTICA', '#ef4444'
    
    return {
        'status': status, 'cor': cor, 'score': round(score, 1),
        'motivos': motivos, 'pct_aprovados': pct_aprovados,
        'fator_k_medio': fator_k_medio, 'taxa_bugs': taxa_bugs,
        'total_bugs': total_bugs, 'total_sp': total_sp
    }


def analisar_metricas_qa(df: pd.DataFrame, qa_nome: str) -> Dict[str, Any]:
    """Analisa métricas específicas de um QA."""
    df_qa = df[df['qa_responsavel'] == qa_nome].copy()
    
    if df_qa.empty:
        return {'total_cards': 0, 'total_sp': 0, 'bugs_encontrados': 0,
                'media_bugs': 0, 'cards_concluidos': 0, 'eficiencia': 0}
    
    total_cards = len(df_qa)
    total_sp = df_qa['story_points'].sum()
    bugs_total = df_qa['bugs_encontrados'].sum()
    
    status_concluido = ['Concluído', 'Done', 'ENTREGUE']
    cards_concluidos = len(df_qa[df_qa['status'].isin(status_concluido)])
    
    eficiencia = (cards_concluidos / total_cards * 100) if total_cards > 0 else 0
    
    por_complexidade = df_qa.groupby('complexidade_teste').agg({
        'ticket_id': 'count',
        'bugs_encontrados': 'sum'
    }).to_dict('index')
    
    return {
        'total_cards': total_cards,
        'total_sp': total_sp,
        'bugs_encontrados': bugs_total,
        'media_bugs': bugs_total / total_cards if total_cards > 0 else 0,
        'cards_concluidos': cards_concluidos,
        'eficiencia': eficiencia,
        'por_complexidade': por_complexidade,
        'df': df_qa
    }


def analisar_metricas_dev(df: pd.DataFrame, dev_nome: str) -> Dict[str, Any]:
    """Analisa métricas específicas de um desenvolvedor."""
    df_dev = df[df['desenvolvedor'] == dev_nome].copy()
    
    if df_dev.empty:
        return {'total_cards': 0, 'total_sp': 0, 'bugs_total': 0,
                'fator_k_medio': 0, 'taxa_bugs': 0}
    
    total_cards = len(df_dev)
    total_sp = df_dev['story_points'].sum()
    bugs_total = df_dev['bugs_encontrados'].sum()
    
    df_dev['fator_k'] = df_dev.apply(
        lambda row: calcular_fator_k(row['story_points'], row['bugs_encontrados']), axis=1)
    df_dev['fator_k_calc'] = df_dev['fator_k'].apply(lambda x: 10 if x == float('inf') else x)
    fator_k_medio = df_dev['fator_k_calc'].mean()
    
    taxa_bugs = (bugs_total / total_sp * 100) if total_sp > 0 else 0
    
    status_concluido = ['Concluído', 'Done', 'ENTREGUE']
    cards_concluidos = len(df_dev[df_dev['status'].isin(status_concluido)])
    
    maturidade = classificar_maturidade(fator_k_medio)
    
    por_tipo = df_dev.groupby('tipo').agg({
        'ticket_id': 'count',
        'bugs_encontrados': 'sum',
        'story_points': 'sum'
    }).to_dict('index')
    
    return {
        'total_cards': total_cards,
        'total_sp': total_sp,
        'bugs_total': bugs_total,
        'fator_k_medio': fator_k_medio,
        'taxa_bugs': taxa_bugs,
        'cards_concluidos': cards_concluidos,
        'maturidade': maturidade,
        'por_tipo': por_tipo,
        'df': df_dev
    }


# ==============================================================================
# COMPONENTES DE VISUALIZAÇÃO
# ==============================================================================

def mostrar_card_ticket(row: pd.Series, show_dev: bool = True, show_qa: bool = True):
    """Mostra um card de ticket com link para o Jira."""
    fator_k = calcular_fator_k(row['story_points'], row['bugs_encontrados'])
    maturidade = classificar_maturidade(fator_k)
    
    info_extra = []
    if show_dev:
        info_extra.append(f"**Dev:** {row['desenvolvedor']}")
    if show_qa:
        info_extra.append(f"**QA:** {row['qa_responsavel']}")
    
    st.markdown(f"""
    <div class="risk-card {'risk-high' if row.get('score_risco', 0) >= 70 else 'risk-medium' if row.get('score_risco', 0) >= 50 else 'risk-low'}">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <a href="{row['link_jira']}" target="_blank" style="font-weight: bold; font-size: 16px; color: #6366f1;">
                    🔗 {row['ticket_id']}
                </a>
                <span style="margin-left: 10px; opacity: 0.8;">{row['tipo']}</span>
            </div>
            <div>
                <span style="font-size: 20px;">{maturidade['emoji']}</span>
            </div>
        </div>
        <p style="margin: 8px 0; opacity: 0.9;">{row['titulo'][:60]}{'...' if len(row['titulo']) > 60 else ''}</p>
        <div style="display: flex; gap: 15px; font-size: 13px;">
            <span>📊 {row['story_points']} SP</span>
            <span>🐛 {row['bugs_encontrados']} bugs</span>
            <span>📋 {row['status']}</span>
        </div>
        <div style="margin-top: 8px; font-size: 12px; opacity: 0.8;">
            {' | '.join(info_extra)}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# ABAS DO DASHBOARD
# ==============================================================================

def aba_lideranca(df: pd.DataFrame):
    """Aba de Liderança - Decisões estratégicas."""
    st.markdown('<div class="section-header"><h2>🎯 Painel de Liderança - Decisões Estratégicas</h2></div>', 
                unsafe_allow_html=True)
    
    # Saúde da Release
    saude = calcular_saude_release(df)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        status_class = 'green' if 'ESTÁVEL' in saude['status'] else 'yellow' if 'ALERTA' in saude['status'] else 'red'
        st.markdown(f"""
        <div class="status-card-{status_class}">
            <p class="big-number">{saude['score']}</p>
            <p class="card-label">Score de Saúde</p>
            <h3 style="margin-top: 10px;">{saude['status']}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📊 Métricas Executivas")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Cards", len(df))
        with m2:
            st.metric("Story Points", df['story_points'].sum())
        with m3:
            st.metric("Bugs Encontrados", df['bugs_encontrados'].sum())
        with m4:
            st.metric("Fator K Médio", f"{saude['fator_k_medio']:.2f}")
        
        if saude['motivos']:
            st.warning("**⚠️ Pontos de Atenção:** " + " | ".join(saude['motivos']))
    
    st.markdown("---")
    
    # Go/No-Go
    st.markdown("### 🚦 Análise Go/No-Go")
    
    analise = analisar_go_no_go(df)
    
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
        <div class="status-card-green">
            <p class="big-number">{analise['total_go']}</p>
            <p class="card-label">🟢 GO</p>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"""
        <div class="status-card-yellow">
            <p class="big-number">{analise['total_atencao']}</p>
            <p class="card-label">🟡 ATENÇÃO</p>
        </div>
        """, unsafe_allow_html=True)
    
    with c3:
        st.markdown(f"""
        <div class="status-card-orange">
            <p class="big-number">{analise['total_risco']}</p>
            <p class="card-label">🟠 RISCO</p>
        </div>
        """, unsafe_allow_html=True)
    
    with c4:
        st.markdown(f"""
        <div class="status-card-red">
            <p class="big-number">{analise['total_no_go']}</p>
            <p class="card-label">🔴 NO-GO</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Cards NO-GO
    if analise['total_no_go'] > 0:
        st.markdown("### 🚨 Cards que Devem Sair da Release")
        st.error("Estes cards possuem risco acumulado muito alto. Recomenda-se mover para próxima sprint.")
        
        for _, row in analise['no_go'].head(5).iterrows():
            mostrar_card_ticket(row)
    
    st.markdown("---")
    
    # Top Riscos
    st.markdown("### 🔥 Top 5 Maiores Riscos")
    
    df_riscos = analise['df_completo'].sort_values('score_risco', ascending=False).head(5)
    
    for _, row in df_riscos.iterrows():
        mostrar_card_ticket(row)
    
    st.markdown("---")
    
    # Recomendações
    st.markdown("### 💡 Recomendações para o Tech Lead")
    
    recomendacoes = []
    
    if analise['total_no_go'] > 0:
        recomendacoes.append({
            'prioridade': '🔴 URGENTE',
            'acao': f"Remover {analise['total_no_go']} card(s) da release",
            'motivo': 'Risco alto de comprometer a qualidade da entrega'
        })
    
    # Verificar devs com baixo fator K
    df_temp = df.copy()
    df_temp['fator_k'] = df_temp.apply(
        lambda row: calcular_fator_k(row['story_points'], row['bugs_encontrados']), axis=1)
    df_temp['fator_k_calc'] = df_temp['fator_k'].apply(lambda x: 10 if x == float('inf') else x)
    
    perf_dev = df_temp.groupby('desenvolvedor').agg({
        'fator_k_calc': 'mean',
        'bugs_encontrados': 'sum'
    }).reset_index()
    
    devs_criticos = perf_dev[perf_dev['fator_k_calc'] < 2]
    if not devs_criticos.empty:
        recomendacoes.append({
            'prioridade': '🟠 IMPORTANTE',
            'acao': f"Suporte técnico para: {', '.join(devs_criticos['desenvolvedor'].tolist()[:3])}",
            'motivo': 'Fator K abaixo da meta (< 2.0)'
        })
    
    if saude['score'] < 70:
        recomendacoes.append({
            'prioridade': '🟡 ATENÇÃO',
            'acao': 'Convocar reunião de alinhamento',
            'motivo': f'Saúde da release em {saude["score"]:.0f}%'
        })
    
    for rec in recomendacoes:
        st.info(f"""
        **{rec['prioridade']}**: {rec['acao']}  
        *Motivo: {rec['motivo']}*
        """)
    
    if not recomendacoes:
        st.success("✅ Nenhuma ação urgente necessária!")


def aba_qa(df: pd.DataFrame):
    """Aba de QA - Métricas individuais dos testadores."""
    st.markdown('<div class="section-header"><h2>🧪 Painel de QA - Métricas de Validação</h2></div>', 
                unsafe_allow_html=True)
    
    # Lista de QAs
    qas = df['qa_responsavel'].unique().tolist()
    qas = [qa for qa in qas if qa != 'Não atribuído']
    
    if not qas:
        st.warning("Nenhum QA encontrado nos dados.")
        return
    
    # Seletor de QA
    qa_selecionado = st.selectbox("Selecione o QA", ["Visão Geral"] + qas)
    
    st.markdown("---")
    
    if qa_selecionado == "Visão Geral":
        # Comparativo entre QAs
        st.markdown("### 📊 Comparativo entre QAs")
        
        dados_qas = []
        for qa in qas:
            metricas = analisar_metricas_qa(df, qa)
            dados_qas.append({
                'QA': qa,
                'Cards': metricas['total_cards'],
                'SP Validados': metricas['total_sp'],
                'Bugs Encontrados': metricas['bugs_encontrados'],
                'Média Bugs/Card': round(metricas['media_bugs'], 2),
                'Eficiência': f"{metricas['eficiencia']:.0f}%"
            })
        
        df_qas = pd.DataFrame(dados_qas)
        st.dataframe(df_qas, hide_index=True, width='stretch')
        
        # Gráfico comparativo
        fig = px.bar(df_qas, x='QA', y=['Cards', 'Bugs Encontrados'], 
                     barmode='group', title='Cards vs Bugs por QA')
        fig.update_layout(height=400)
        st.plotly_chart(fig, width='stretch')
        
        # Cards aguardando QA
        st.markdown("### ⏳ Fila de Validação")
        
        status_aguardando = ['AGUARDANDO VALIDAÇÃO', 'EM REVISÃO', 'Tarefas pendentes']
        df_fila = df[df['status'].isin(status_aguardando)]
        
        if not df_fila.empty:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Cards na Fila", len(df_fila))
            with c2:
                st.metric("SP na Fila", df_fila['story_points'].sum())
            with c3:
                capacidade = 5 * len(qas)  # 5 SP por QA por dia
                dias = df_fila['story_points'].sum() / capacidade
                st.metric("Dias Estimados", f"{dias:.1f}")
            
            st.markdown("**Cards aguardando:**")
            for _, row in df_fila.head(5).iterrows():
                mostrar_card_ticket(row, show_qa=False)
        else:
            st.success("✅ Nenhum card aguardando validação!")
    
    else:
        # Métricas individuais do QA
        metricas = analisar_metricas_qa(df, qa_selecionado)
        
        st.markdown(f"### 👤 Métricas de {qa_selecionado}")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Cards Atribuídos", metricas['total_cards'])
        with c2:
            st.metric("SP Validados", metricas['total_sp'])
        with c3:
            st.metric("Bugs Encontrados", metricas['bugs_encontrados'])
        with c4:
            st.metric("Eficiência", f"{metricas['eficiencia']:.0f}%")
        
        # Cards por complexidade
        if metricas['por_complexidade']:
            st.markdown("### 📈 Por Complexidade de Teste")
            
            dados_comp = []
            for comp, valores in metricas['por_complexidade'].items():
                dados_comp.append({
                    'Complexidade': comp,
                    'Cards': valores['ticket_id'],
                    'Bugs': valores['bugs_encontrados']
                })
            
            df_comp = pd.DataFrame(dados_comp)
            
            fig = px.bar(df_comp, x='Complexidade', y=['Cards', 'Bugs'],
                        barmode='group', title='Distribuição por Complexidade')
            st.plotly_chart(fig, width='stretch')
        
        # Lista de cards do QA
        st.markdown("### 📋 Meus Cards")
        
        for _, row in metricas['df'].iterrows():
            mostrar_card_ticket(row, show_qa=False)


def aba_dev(df: pd.DataFrame):
    """Aba de Dev - Métricas individuais dos desenvolvedores."""
    st.markdown('<div class="section-header"><h2>👨‍💻 Painel de Desenvolvimento - Performance Individual</h2></div>', 
                unsafe_allow_html=True)
    
    # Lista de desenvolvedores
    devs = df['desenvolvedor'].unique().tolist()
    devs = [d for d in devs if d != 'Não atribuído']
    
    if not devs:
        st.warning("Nenhum desenvolvedor encontrado nos dados.")
        return
    
    # Seletor de Dev
    dev_selecionado = st.selectbox("Selecione o Desenvolvedor", ["Visão Geral"] + sorted(devs))
    
    st.markdown("---")
    
    if dev_selecionado == "Visão Geral":
        # Ranking de desenvolvedores
        st.markdown("### 🏆 Ranking de Performance")
        
        dados_devs = []
        for dev in devs:
            metricas = analisar_metricas_dev(df, dev)
            dados_devs.append({
                'Desenvolvedor': dev,
                'Cards': metricas['total_cards'],
                'SP': metricas['total_sp'],
                'Bugs': metricas['bugs_total'],
                'Fator K': round(metricas['fator_k_medio'], 2),
                'Taxa Bugs': f"{metricas['taxa_bugs']:.1f}%",
                'Performance': metricas['maturidade']['emoji'] + ' ' + metricas['maturidade']['selo']
            })
        
        df_devs = pd.DataFrame(dados_devs)
        df_devs = df_devs.sort_values('Fator K', ascending=False)
        
        st.dataframe(df_devs, hide_index=True, width='stretch')
        
        # Gráfico de Fator K
        fig = px.bar(df_devs, x='Desenvolvedor', y='Fator K',
                     color='Fator K',
                     color_continuous_scale=['#ef4444', '#f97316', '#eab308', '#22c55e'],
                     title='Fator K por Desenvolvedor')
        fig.add_hline(y=2, line_dash="dash", line_color="gray", 
                      annotation_text="Meta (FK ≥ 2)")
        fig.update_layout(height=400)
        st.plotly_chart(fig, width='stretch')
        
        # Devs que precisam de atenção
        devs_atencao = [d for d in dados_devs if d['Fator K'] < 2]
        if devs_atencao:
            st.markdown("### ⚠️ Desenvolvedores que Precisam de Suporte")
            for dev in devs_atencao:
                st.warning(f"**{dev['Desenvolvedor']}**: Fator K = {dev['Fator K']} | {dev['Bugs']} bugs em {dev['Cards']} cards")
    
    else:
        # Métricas individuais do desenvolvedor
        metricas = analisar_metricas_dev(df, dev_selecionado)
        
        st.markdown(f"### 👤 Performance de {dev_selecionado}")
        
        # Selo de maturidade
        col1, col2 = st.columns([1, 3])
        
        with col1:
            maturidade = metricas['maturidade']
            st.markdown(f"""
            <div class="status-card-{'green' if maturidade['selo'] == 'Gold' else 'yellow' if maturidade['selo'] == 'Silver' else 'orange' if maturidade['selo'] == 'Bronze' else 'red'}">
                <p style="font-size: 48px; margin: 0;">{maturidade['emoji']}</p>
                <p class="card-label">{maturidade['selo']}</p>
                <p style="font-size: 24px; margin-top: 10px;"><b>FK: {metricas['fator_k_medio']:.2f}</b></p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Cards", metricas['total_cards'])
            with c2:
                st.metric("Story Points", metricas['total_sp'])
            with c3:
                st.metric("Bugs Gerados", metricas['bugs_total'])
            with c4:
                st.metric("Taxa de Bugs", f"{metricas['taxa_bugs']:.1f}%")
        
        # Por tipo de ticket
        if metricas['por_tipo']:
            st.markdown("### 📈 Por Tipo de Ticket")
            
            dados_tipo = []
            for tipo, valores in metricas['por_tipo'].items():
                dados_tipo.append({
                    'Tipo': tipo,
                    'Cards': valores['ticket_id'],
                    'SP': valores['story_points'],
                    'Bugs': valores['bugs_encontrados']
                })
            
            df_tipo = pd.DataFrame(dados_tipo)
            
            col1, col2 = st.columns(2)
            with col1:
                fig1 = px.pie(df_tipo, values='Cards', names='Tipo', title='Distribuição por Tipo')
                st.plotly_chart(fig1, width='stretch')
            with col2:
                fig2 = px.bar(df_tipo, x='Tipo', y='Bugs', title='Bugs por Tipo')
                st.plotly_chart(fig2, width='stretch')
        
        # Lista de cards
        st.markdown("### 📋 Meus Cards")
        
        for _, row in metricas['df'].iterrows():
            mostrar_card_ticket(row, show_dev=False)


def aba_historico(df_atual: pd.DataFrame):
    """Aba de Histórico - Releases anteriores."""
    st.markdown('<div class="section-header"><h2>📜 Histórico de Releases</h2></div>', 
                unsafe_allow_html=True)
    
    st.info("Esta seção mostra dados de sprints/releases anteriores para análise de tendências.")
    
    # Gerar dados mockados de releases anteriores
    df_historico = gerar_dados_mockados(sprint_atual=False)
    
    # Métricas por sprint
    sprints = df_historico['sprint'].unique()
    
    dados_sprints = []
    for sprint in sprints:
        df_sprint = df_historico[df_historico['sprint'] == sprint]
        saude = calcular_saude_release(df_sprint)
        
        dados_sprints.append({
            'Sprint': sprint,
            'Cards': len(df_sprint),
            'SP': df_sprint['story_points'].sum(),
            'Bugs': df_sprint['bugs_encontrados'].sum(),
            'Fator K': round(saude['fator_k_medio'], 2),
            'Saúde': saude['status']
        })
    
    df_sprints = pd.DataFrame(dados_sprints)
    
    st.markdown("### 📊 Resumo por Sprint")
    st.dataframe(df_sprints, hide_index=True, width='stretch')
    
    # Gráfico de tendência
    st.markdown("### 📈 Evolução do Fator K")
    
    fig = px.line(df_sprints, x='Sprint', y='Fator K', markers=True,
                  title='Tendência do Fator K ao Longo das Sprints')
    fig.add_hline(y=2, line_dash="dash", line_color="green", annotation_text="Meta")
    fig.update_layout(height=400)
    st.plotly_chart(fig, width='stretch')
    
    # Comparativo de bugs
    st.markdown("### 🐛 Evolução de Bugs")
    
    fig2 = px.bar(df_sprints, x='Sprint', y='Bugs', 
                  color='Bugs', color_continuous_scale='Reds',
                  title='Total de Bugs por Sprint')
    st.plotly_chart(fig2, width='stretch')
    
    # Detalhe por sprint
    st.markdown("### 🔍 Detalhe por Sprint")
    
    sprint_detalhe = st.selectbox("Selecione a Sprint", sprints)
    
    df_detalhe = df_historico[df_historico['sprint'] == sprint_detalhe]
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Cards", len(df_detalhe))
    with c2:
        st.metric("Story Points", df_detalhe['story_points'].sum())
    with c3:
        st.metric("Bugs", df_detalhe['bugs_encontrados'].sum())
    
    st.markdown("**Cards da Sprint:**")
    for _, row in df_detalhe.head(10).iterrows():
        mostrar_card_ticket(row)


# ==============================================================================
# FUNÇÃO PRINCIPAL
# ==============================================================================

def main():
    """Função principal do dashboard."""
    
    # Configuração da página
    st.set_page_config(
        page_title="Jira Dashboard - NINA",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Aplicar CSS
    aplicar_css_customizado()
    
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Configurações")
        
        st.markdown("---")
        
        # Credenciais
        st.subheader("🔐 Jira")
        jira_email = st.text_input("Email", key="jira_email", placeholder="email@empresa.com")
        jira_token = st.text_input("API Token", type="password", key="jira_token")
        
        if verificar_credenciais_jira():
            st.success("✅ Conectado")
        else:
            st.warning("⚠️ Modo Demo")
        
        st.markdown("---")
        
        # Projetos
        st.subheader("📁 Projetos")
        projeto_jira = st.text_input("Códigos", value="SD, VALPROD, PB, QA", key="projeto_jira")
        
        # Release
        st.subheader("📅 Release")
        data_release = st.date_input("Data da Release", value=datetime.now() + timedelta(days=10))
        
        st.markdown("---")
        
        # Botões
        if st.button("🔄 Carregar do Jira", width='stretch'):
            if verificar_credenciais_jira():
                with st.spinner("Buscando dados..."):
                    df = buscar_e_transformar_dados_jira(projeto_jira, 
                            datetime.combine(data_release, datetime.min.time()))
                    if df is not None:
                        st.session_state.dados = df
                        st.session_state.dados_reais = True
                        st.success(f"✅ {len(df)} cards carregados!")
                        st.rerun()
            else:
                st.warning("Configure as credenciais!")
        
        if st.button("📊 Usar Demo", width='stretch'):
            st.session_state.dados = gerar_dados_mockados()
            st.session_state.dados_reais = False
            st.rerun()
        
        st.markdown("---")
        st.caption("Dashboard v2.0 | NINA Tecnologia")
    
    # Carregar dados
    if 'dados' not in st.session_state:
        st.session_state.dados = gerar_dados_mockados()
        st.session_state.dados_reais = False
    
    df = st.session_state.dados
    
    # Header
    st.title("📊 Jira Dashboard - Métricas de Qualidade")
    
    if st.session_state.get('dados_reais', False):
        st.success("🟢 Conectado ao Jira - Dados Reais")
    else:
        st.info("🟡 Modo Demonstração - Dados Simulados")
    
    # Tabs principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Liderança", 
        "🧪 QA", 
        "👨‍💻 Dev", 
        "📜 Histórico"
    ])
    
    with tab1:
        aba_lideranca(df)
    
    with tab2:
        aba_qa(df)
    
    with tab3:
        aba_dev(df)
    
    with tab4:
        aba_historico(df)
    
    # Footer
    st.markdown("---")
    st.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}")


if __name__ == "__main__":
    main()
