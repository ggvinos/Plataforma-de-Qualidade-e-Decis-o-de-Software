"""
================================================================================
JIRA DASHBOARD v6.0 - NINA TECNOLOGIA
================================================================================
FOCO: SD (Software Development) + Visibilidade QA + Governança de Dados

MELHORIAS v6.0:
- Auto-load de dados ao abrir (sem clique manual)
- Cache inteligente (5 min) com indicador de última atualização
- Aba QA/Gargalos: Funil de validação, tempo em status, aging
- Aba Governança: % campos preenchidos, lista para cobrança
- Filtro por Produto (Plataforma, NinaChat, HUB, etc.)
- Status corrigidos: EM VALIDAÇÃO, Tarefas pendentes
- Hotfix assume 2 SP quando vazio
- Alertas visuais para campos não preenchidos

CAMPOS MAPEADOS JIRA NINA:
- customfield_10487: QA (user)
- customfield_11157: Bugs Encontrados  
- customfield_11257: Story Points (principal)
- customfield_10016: Story Points (alternativo)
- customfield_10020: Sprint
- customfield_11290: Complexidade de Teste
- customfield_10102: Produto
================================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from typing import Optional, Dict, List, Any, Tuple
import json
import os

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA (DEVE SER PRIMEIRO)
# ==============================================================================
st.set_page_config(
    page_title="NINA Dashboard - Métricas SD",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# CONFIGURAÇÕES GLOBAIS
# ==============================================================================

JIRA_BASE_URL = "https://ninatecnologia.atlassian.net"

# Custom Fields mapeados do Jira NINA
CUSTOM_FIELDS = {
    "story_points": "customfield_11257",
    "story_points_alt": "customfield_10016", 
    "sprint": "customfield_10020",
    "bugs_encontrados": "customfield_11157",
    "complexidade_teste": "customfield_11290",
    "qa_responsavel": "customfield_10487",
    "produto": "customfield_10102",
}

# Status do fluxo - CORRIGIDO com todos os status reais
STATUS_FLOW = {
    "backlog": ["Backlog", "To Do", "Tarefas pendentes"],
    "development": ["Em andamento"],
    "code_review": ["EM REVISÃO"],
    "waiting_qa": ["AGUARDANDO VALIDAÇÃO"],
    "testing": ["EM VALIDAÇÃO"],
    "done": ["Concluído"],
    "blocked": ["IMPEDIDO"],
    "rejected": ["REPROVADO"],
    "deferred": ["Validado - Adiado", "DESCARTADO"],
}

# Nomes amigáveis para status
STATUS_NOMES = {
    "backlog": "📋 Backlog",
    "development": "💻 Desenvolvimento",
    "code_review": "👀 Code Review",
    "waiting_qa": "⏳ Aguardando QA",
    "testing": "🧪 Em Validação",
    "done": "✅ Concluído",
    "blocked": "🚫 Bloqueado",
    "rejected": "❌ Reprovado",
    "deferred": "📅 Adiado",
    "unknown": "❓ Desconhecido"
}

# Cores para status
STATUS_CORES = {
    "backlog": "#64748b",
    "development": "#3b82f6",
    "code_review": "#8b5cf6",
    "waiting_qa": "#f59e0b",
    "testing": "#06b6d4",
    "done": "#22c55e",
    "blocked": "#ef4444",
    "rejected": "#dc2626",
    "deferred": "#6b7280",
    "unknown": "#9ca3af"
}

# Regras de negócio
REGRAS = {
    "hotfix_sp_default": 2,  # SP padrão para Hotfix quando vazio
    "cache_ttl_minutos": 5,  # Tempo de cache em minutos
    "dias_aging_alerta": 3,  # Dias para alerta de aging em QA
}

# ==============================================================================
# FUNÇÕES DE CREDENCIAIS
# ==============================================================================

def get_secrets():
    """Carrega credenciais de forma segura."""
    try:
        if "jira" in st.secrets:
            return {
                "email": st.secrets["jira"]["email"],
                "token": st.secrets["jira"]["token"],
            }
    except:
        pass
    
    # Fallback para variáveis de ambiente
    return {
        "email": os.getenv("JIRA_API_EMAIL", ""),
        "token": os.getenv("JIRA_API_TOKEN", ""),
    }


def verificar_credenciais() -> bool:
    """Verifica se as credenciais estão configuradas."""
    secrets = get_secrets()
    return bool(secrets["email"] and secrets["token"])


# ==============================================================================
# CACHE E AUTO-LOAD
# ==============================================================================

@st.cache_data(ttl=300, show_spinner=False)  # Cache de 5 minutos
def buscar_dados_jira_cached(projeto: str, jql: str) -> Tuple[Optional[List[Dict]], datetime]:
    """Busca dados do Jira com cache."""
    secrets = get_secrets()
    if not secrets["email"] or not secrets["token"]:
        return None, datetime.now()
    
    base_url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
    headers = {"Accept": "application/json"}
    
    fields = [
        "key", "summary", "status", "issuetype", "assignee", "created", "updated",
        "resolutiondate", "priority", "project", "labels",
        CUSTOM_FIELDS["story_points"],
        CUSTOM_FIELDS["story_points_alt"],
        CUSTOM_FIELDS["sprint"],
        CUSTOM_FIELDS["bugs_encontrados"],
        CUSTOM_FIELDS["complexidade_teste"],
        CUSTOM_FIELDS["qa_responsavel"],
        CUSTOM_FIELDS["produto"],
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
            if not next_page_token or len(all_issues) >= 500:
                break
        
        return all_issues, datetime.now()
    
    except Exception as e:
        st.error(f"Erro ao conectar com Jira: {e}")
        return None, datetime.now()


def processar_issues(issues: List[Dict]) -> pd.DataFrame:
    """Processa issues do Jira para DataFrame."""
    dados = []
    hoje = datetime.now()
    
    for issue in issues:
        f = issue.get('fields', {})
        
        # Tipo do ticket
        tipo_original = f.get('issuetype', {}).get('name', 'Desconhecido')
        tipo = "TAREFA"
        if any(t in tipo_original for t in ["Hotfix", "Hotfeature"]):
            tipo = "HOTFIX"
        elif any(t in tipo_original for t in ["Bug", "Impeditivo"]):
            tipo = "BUG"
        elif "Sugestão" in tipo_original:
            tipo = "SUGESTÃO"
        
        # Projeto
        projeto = f.get('project', {}).get('key', 'N/A')
        
        # Desenvolvedor
        dev = f.get('assignee', {}).get('displayName', 'Não atribuído') if f.get('assignee') else 'Não atribuído'
        
        # Story Points - com regra de Hotfix
        sp = f.get(CUSTOM_FIELDS['story_points']) or f.get(CUSTOM_FIELDS['story_points_alt']) or 0
        if sp == 0 and tipo == "HOTFIX":
            sp = REGRAS["hotfix_sp_default"]  # Aplicar default para Hotfix
        
        # Sprint
        sprint_f = f.get(CUSTOM_FIELDS['sprint'], [])
        sprint = sprint_f[-1].get('name', 'Sem Sprint') if sprint_f else 'Sem Sprint'
        sprint_end = None
        if sprint_f:
            sprint_end_str = sprint_f[-1].get('endDate')
            if sprint_end_str:
                try:
                    sprint_end = datetime.fromisoformat(sprint_end_str.replace('Z', '+00:00')).replace(tzinfo=None)
                except:
                    pass
        
        # Status
        status = f.get('status', {}).get('name', 'Desconhecido')
        status_cat = 'unknown'
        for cat, statuses in STATUS_FLOW.items():
            if any(s.lower() == status.lower() for s in statuses):
                status_cat = cat
                break
        
        # Bugs
        bugs = f.get(CUSTOM_FIELDS['bugs_encontrados']) or 0
        
        # Complexidade
        comp = f.get(CUSTOM_FIELDS['complexidade_teste'])
        complexidade = comp.get('value', '') if isinstance(comp, dict) else ''
        
        # QA
        qa_f = f.get(CUSTOM_FIELDS['qa_responsavel'])
        qa = 'Não atribuído'
        if qa_f:
            if isinstance(qa_f, dict):
                qa = qa_f.get('displayName', 'Não atribuído')
            elif isinstance(qa_f, list) and qa_f:
                qa = qa_f[0].get('displayName', 'Não atribuído')
        
        # Produto
        produto_f = f.get(CUSTOM_FIELDS['produto'], [])
        produtos = [p.get('value', '') for p in produto_f] if produto_f else []
        produto = produtos[0] if produtos else 'Não definido'
        
        # Datas
        try:
            criado = datetime.fromisoformat(f.get('created', '').replace('Z', '+00:00')).replace(tzinfo=None)
        except:
            criado = hoje
        
        try:
            atualizado = datetime.fromisoformat(f.get('updated', '').replace('Z', '+00:00')).replace(tzinfo=None)
        except:
            atualizado = hoje
        
        # Métricas calculadas
        dias_em_status = (hoje - atualizado).days
        lead_time = (atualizado - criado).days if status_cat == 'done' else (hoje - criado).days
        
        # Dias até release
        dias_ate_release = 0
        if sprint_end:
            dias_ate_release = max(0, (sprint_end - hoje).days)
        
        # Flags
        sp_preenchido = bool(f.get(CUSTOM_FIELDS['story_points']) or f.get(CUSTOM_FIELDS['story_points_alt']))
        bugs_preenchido = f.get(CUSTOM_FIELDS['bugs_encontrados']) is not None
        complexidade_preenchida = bool(complexidade)
        qa_preenchido = qa != 'Não atribuído'
        
        dados.append({
            'ticket_id': issue.get('key', ''),
            'titulo': f.get('summary', ''),
            'tipo': tipo,
            'tipo_original': tipo_original,
            'status': status,
            'status_cat': status_cat,
            'projeto': projeto,
            'desenvolvedor': dev,
            'qa': qa,
            'sp': int(sp) if sp else 0,
            'sp_original': bool(f.get(CUSTOM_FIELDS['story_points']) or f.get(CUSTOM_FIELDS['story_points_alt'])),
            'bugs': int(bugs) if bugs else 0,
            'sprint': sprint,
            'sprint_end': sprint_end,
            'prioridade': f.get('priority', {}).get('name', 'Média') if f.get('priority') else 'Média',
            'complexidade': complexidade,
            'produto': produto,
            'produtos': produtos,
            'criado': criado,
            'atualizado': atualizado,
            'dias_em_status': dias_em_status,
            'lead_time': lead_time,
            'dias_ate_release': dias_ate_release,
            # Flags de preenchimento
            'sp_preenchido': sp_preenchido,
            'bugs_preenchido': bugs_preenchido,
            'complexidade_preenchida': complexidade_preenchida,
            'qa_preenchido': qa_preenchido,
        })
    
    return pd.DataFrame(dados)


# ==============================================================================
# FUNÇÕES DE MÉTRICAS
# ==============================================================================

def calcular_fator_k(sp: int, bugs: int) -> float:
    """Calcula Fator K = SP / (Bugs + 1)"""
    if sp == 0:
        return 0
    return round(sp / (bugs + 1), 2)


def classificar_maturidade(fk: float) -> Dict:
    """Classifica maturidade baseado no Fator K."""
    if fk >= 3.0:
        return {"selo": "Gold", "emoji": "🥇", "cor": "#22c55e"}
    elif fk >= 2.0:
        return {"selo": "Silver", "emoji": "🥈", "cor": "#eab308"}
    elif fk >= 1.0:
        return {"selo": "Bronze", "emoji": "🥉", "cor": "#f97316"}
    else:
        return {"selo": "Risco", "emoji": "⚠️", "cor": "#ef4444"}


def calcular_metricas_governanca(df: pd.DataFrame) -> Dict:
    """Calcula métricas de governança de dados."""
    total = len(df)
    if total == 0:
        return {
            "sp": {"preenchido": 0, "total": 0, "pct": 0},
            "bugs": {"preenchido": 0, "total": 0, "pct": 0},
            "complexidade": {"preenchido": 0, "total": 0, "pct": 0},
            "qa": {"preenchido": 0, "total": 0, "pct": 0},
        }
    
    # Excluir Hotfix da contagem de SP (não é obrigatório)
    df_sem_hotfix = df[df['tipo'] != 'HOTFIX']
    total_sem_hotfix = len(df_sem_hotfix)
    
    return {
        "sp": {
            "preenchido": int(df_sem_hotfix['sp_preenchido'].sum()) if total_sem_hotfix > 0 else 0,
            "total": total_sem_hotfix,
            "pct": round(df_sem_hotfix['sp_preenchido'].sum() / total_sem_hotfix * 100, 1) if total_sem_hotfix > 0 else 0,
            "faltando": df_sem_hotfix[~df_sem_hotfix['sp_preenchido']]['ticket_id'].tolist() if total_sem_hotfix > 0 else []
        },
        "bugs": {
            "preenchido": int(df['bugs_preenchido'].sum()),
            "total": total,
            "pct": round(df['bugs_preenchido'].sum() / total * 100, 1),
            "faltando": df[~df['bugs_preenchido']]['ticket_id'].tolist()
        },
        "complexidade": {
            "preenchido": int(df['complexidade_preenchida'].sum()),
            "total": total,
            "pct": round(df['complexidade_preenchida'].sum() / total * 100, 1),
            "faltando": df[~df['complexidade_preenchida']]['ticket_id'].tolist()
        },
        "qa": {
            "preenchido": int(df['qa_preenchido'].sum()),
            "total": total,
            "pct": round(df['qa_preenchido'].sum() / total * 100, 1),
            "faltando": df[~df['qa_preenchido']]['ticket_id'].tolist()
        },
    }


def calcular_metricas_qa(df: pd.DataFrame) -> Dict:
    """Calcula métricas específicas de QA."""
    
    # Funil de validação
    waiting_qa = df[df['status_cat'] == 'waiting_qa']
    testing = df[df['status_cat'] == 'testing']
    done = df[df['status_cat'] == 'done']
    blocked = df[df['status_cat'] == 'blocked']
    rejected = df[df['status_cat'] == 'rejected']
    
    # Tempo médio em cada status de QA
    tempo_waiting = waiting_qa['dias_em_status'].mean() if not waiting_qa.empty else 0
    tempo_testing = testing['dias_em_status'].mean() if not testing.empty else 0
    
    # Cards "envelhecidos" (mais de X dias em QA)
    aging_waiting = waiting_qa[waiting_qa['dias_em_status'] >= REGRAS['dias_aging_alerta']]
    aging_testing = testing[testing['dias_em_status'] >= REGRAS['dias_aging_alerta']]
    
    # Carga por QA
    carga_qa = df[df['status_cat'].isin(['waiting_qa', 'testing'])].groupby('qa').agg({
        'ticket_id': 'count',
        'sp': 'sum'
    }).reset_index()
    carga_qa.columns = ['QA', 'Cards', 'SP']
    
    # Taxa de reprovação
    total_validados = len(done) + len(rejected)
    taxa_reprovacao = len(rejected) / total_validados * 100 if total_validados > 0 else 0
    
    return {
        "funil": {
            "waiting_qa": len(waiting_qa),
            "testing": len(testing),
            "done": len(done),
            "blocked": len(blocked),
            "rejected": len(rejected),
        },
        "tempo": {
            "waiting": round(tempo_waiting, 1),
            "testing": round(tempo_testing, 1),
        },
        "aging": {
            "waiting": aging_waiting,
            "testing": aging_testing,
            "total": len(aging_waiting) + len(aging_testing),
        },
        "carga_qa": carga_qa,
        "taxa_reprovacao": round(taxa_reprovacao, 1),
    }


# ==============================================================================
# ESTILOS CSS
# ==============================================================================

def aplicar_estilos():
    st.markdown("""
    <style>
    /* Cards de status */
    .status-card {
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 2px solid;
        margin-bottom: 10px;
        transition: transform 0.2s;
    }
    .status-card:hover {
        transform: translateY(-3px);
    }
    .status-green { background: rgba(34, 197, 94, 0.1); border-color: #22c55e; }
    .status-yellow { background: rgba(234, 179, 8, 0.1); border-color: #eab308; }
    .status-orange { background: rgba(249, 115, 22, 0.1); border-color: #f97316; }
    .status-red { background: rgba(239, 68, 68, 0.1); border-color: #ef4444; }
    .status-blue { background: rgba(59, 130, 246, 0.1); border-color: #3b82f6; }
    .status-purple { background: rgba(139, 92, 246, 0.1); border-color: #8b5cf6; }
    .status-gray { background: rgba(107, 114, 128, 0.1); border-color: #6b7280; }
    
    .big-number { font-size: 36px; font-weight: bold; margin: 0; }
    .card-label { font-size: 14px; opacity: 0.8; margin-top: 5px; }
    .card-sublabel { font-size: 12px; opacity: 0.6; margin-top: 3px; }
    
    /* Alertas */
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
    
    /* Barra de progresso */
    .progress-bar {
        background: #e5e7eb;
        border-radius: 10px;
        height: 24px;
        overflow: hidden;
        margin: 5px 0;
    }
    .progress-fill {
        height: 100%;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 12px;
    }
    
    /* Header */
    .header-bar {
        background: linear-gradient(90deg, #AF0C37, #8B0A2C);
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    /* Ticket cards */
    .ticket-item {
        background: rgba(100, 100, 100, 0.05);
        border-radius: 8px;
        padding: 10px 15px;
        margin: 5px 0;
        border-left: 4px solid;
    }
    .ticket-critical { border-left-color: #ef4444; }
    .ticket-warning { border-left-color: #f59e0b; }
    .ticket-normal { border-left-color: #22c55e; }
    
    /* Última atualização */
    .update-badge {
        background: rgba(34, 197, 94, 0.2);
        color: #166534;
        padding: 5px 12px;
        border-radius: 15px;
        font-size: 12px;
        display: inline-block;
    }
    .update-badge-stale {
        background: rgba(234, 179, 8, 0.2);
        color: #854d0e;
    }
    
    /* Hide Streamlit elements */
    #MainMenu, .stDeployButton { display: none !important; }
    </style>
    """, unsafe_allow_html=True)


# ==============================================================================
# COMPONENTES UI
# ==============================================================================

def mostrar_indicador_atualizacao(ultima_atualizacao: datetime):
    """Mostra indicador de última atualização."""
    agora = datetime.now()
    diff = (agora - ultima_atualizacao).total_seconds() / 60  # minutos
    
    if diff < 1:
        texto = "Atualizado agora"
        classe = "update-badge"
    elif diff < REGRAS['cache_ttl_minutos']:
        texto = f"Atualizado há {int(diff)} min"
        classe = "update-badge"
    else:
        texto = f"Dados de {int(diff)} min atrás"
        classe = "update-badge update-badge-stale"
    
    st.markdown(f'<span class="{classe}">🕐 {texto}</span>', unsafe_allow_html=True)


def criar_card_metrica(valor: str, titulo: str, cor: str = "blue", subtitulo: str = ""):
    """Cria card de métrica visual."""
    st.markdown(f"""
    <div class="status-card status-{cor}">
        <p class="big-number">{valor}</p>
        <p class="card-label">{titulo}</p>
        {f'<p class="card-sublabel">{subtitulo}</p>' if subtitulo else ''}
    </div>
    """, unsafe_allow_html=True)


def criar_barra_progresso(valor: float, cor: str = "#3b82f6", label: str = ""):
    """Cria barra de progresso."""
    st.markdown(f"""
    <div class="progress-bar">
        <div class="progress-fill" style="width: {min(100, valor)}%; background: {cor};">
            {label or f'{valor:.0f}%'}
        </div>
    </div>
    """, unsafe_allow_html=True)


def criar_grafico_funil_qa(metricas_qa: Dict) -> go.Figure:
    """Cria gráfico de funil de validação QA."""
    funil = metricas_qa['funil']
    
    labels = ['⏳ Aguardando QA', '🧪 Em Validação', '✅ Concluído']
    values = [funil['waiting_qa'], funil['testing'], funil['done']]
    colors = ['#f59e0b', '#06b6d4', '#22c55e']
    
    # Adicionar bloqueados/reprovados se existirem
    if funil['blocked'] > 0:
        labels.append('🚫 Bloqueado')
        values.append(funil['blocked'])
        colors.append('#ef4444')
    
    if funil['rejected'] > 0:
        labels.append('❌ Reprovado')
        values.append(funil['rejected'])
        colors.append('#dc2626')
    
    fig = go.Figure(go.Funnel(
        y=labels,
        x=values,
        textinfo="value+percent total",
        marker=dict(color=colors),
        connector=dict(line=dict(color="royalblue", dash="dot", width=2))
    ))
    
    fig.update_layout(
        title="Funil de Validação QA",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


def criar_grafico_carga_qa(carga_qa: pd.DataFrame) -> go.Figure:
    """Cria gráfico de carga por QA."""
    if carga_qa.empty:
        fig = go.Figure()
        fig.add_annotation(text="Sem dados", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    fig = px.bar(
        carga_qa.sort_values('Cards', ascending=True),
        x='Cards',
        y='QA',
        orientation='h',
        color='SP',
        color_continuous_scale='Blues',
        title='Carga por QA (Cards em validação)'
    )
    
    fig.update_layout(
        height=max(200, len(carga_qa) * 40),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


def criar_grafico_distribuicao_status(df: pd.DataFrame) -> go.Figure:
    """Cria gráfico de distribuição por status."""
    status_count = df['status_cat'].value_counts().reset_index()
    status_count.columns = ['status_cat', 'count']
    status_count['nome'] = status_count['status_cat'].map(STATUS_NOMES)
    status_count['cor'] = status_count['status_cat'].map(STATUS_CORES)
    
    fig = px.pie(
        status_count,
        values='count',
        names='nome',
        color='nome',
        color_discrete_map={STATUS_NOMES[k]: v for k, v in STATUS_CORES.items()},
        title='Distribuição por Status',
        hole=0.4
    )
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


def criar_grafico_governanca(gov: Dict) -> go.Figure:
    """Cria gráfico de governança de dados."""
    campos = ['Story Points', 'Bugs', 'Complexidade', 'QA']
    valores = [gov['sp']['pct'], gov['bugs']['pct'], gov['complexidade']['pct'], gov['qa']['pct']]
    cores = ['#ef4444' if v < 50 else '#f59e0b' if v < 80 else '#22c55e' for v in valores]
    
    fig = go.Figure(go.Bar(
        x=campos,
        y=valores,
        marker_color=cores,
        text=[f'{v:.0f}%' for v in valores],
        textposition='outside'
    ))
    
    fig.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="Meta 80%")
    
    fig.update_layout(
        title="% Campos Preenchidos",
        yaxis_title="Preenchimento (%)",
        yaxis=dict(range=[0, 110]),
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


# ==============================================================================
# ABAS DO DASHBOARD
# ==============================================================================

def aba_visao_geral(df: pd.DataFrame, ultima_atualizacao: datetime):
    """Aba principal com visão geral da sprint."""
    
    # Header com última atualização
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("### 📊 Visão Geral da Sprint")
    with col2:
        mostrar_indicador_atualizacao(ultima_atualizacao)
    with col3:
        if st.button("🔄 Atualizar", type="secondary"):
            st.cache_data.clear()
            st.rerun()
    
    # Sprint info
    sprint_atual = df['sprint'].mode().iloc[0] if not df.empty else "Sem Sprint"
    dias_release = df['dias_ate_release'].max() if 'dias_ate_release' in df.columns else 0
    
    st.markdown(f"""
    <div class="header-bar">
        <span style="font-size: 18px; font-weight: bold;">🚀 {sprint_atual}</span>
        <span style="float: right;">📅 {dias_release} dias até a release</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Alertas de governança
    gov = calcular_metricas_governanca(df)
    if gov['sp']['pct'] < 50:
        st.markdown(f"""
        <div class="alert-critical">
            <b>⚠️ ALERTA: Apenas {gov['sp']['pct']:.0f}% dos cards têm Story Points!</b>
            <p>Isso impacta diretamente nas métricas de capacidade e qualidade.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # KPIs principais
    st.markdown("#### 📈 KPIs da Sprint")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        criar_card_metrica(str(len(df)), "Total Cards", "blue")
    
    with col2:
        sp_total = int(df['sp'].sum())
        criar_card_metrica(str(sp_total), "Story Points", "purple")
    
    with col3:
        concluidos = len(df[df['status_cat'] == 'done'])
        pct = concluidos / len(df) * 100 if len(df) > 0 else 0
        cor = 'green' if pct >= 70 else 'yellow' if pct >= 40 else 'red'
        criar_card_metrica(f"{pct:.0f}%", "Concluído", cor, f"{concluidos}/{len(df)} cards")
    
    with col4:
        bugs_total = int(df['bugs'].sum())
        cor = 'green' if bugs_total < 10 else 'yellow' if bugs_total < 20 else 'red'
        criar_card_metrica(str(bugs_total), "Bugs", cor)
    
    with col5:
        sp_total = df['sp'].sum()
        fk = calcular_fator_k(sp_total, bugs_total)
        mat = classificar_maturidade(fk)
        cor_map = {'#22c55e': 'green', '#eab308': 'yellow', '#f97316': 'orange', '#ef4444': 'red'}
        cor = cor_map.get(mat['cor'], 'blue')
        criar_card_metrica(f"{fk:.1f}", f"Fator K {mat['emoji']}", cor, mat['selo'])
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        fig = criar_grafico_distribuicao_status(df)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Distribuição por tipo
        tipo_count = df['tipo'].value_counts().reset_index()
        tipo_count.columns = ['tipo', 'count']
        
        fig = px.bar(
            tipo_count,
            x='tipo',
            y='count',
            color='tipo',
            title='Distribuição por Tipo',
            color_discrete_map={'TAREFA': '#3b82f6', 'BUG': '#ef4444', 'HOTFIX': '#f59e0b', 'SUGESTÃO': '#8b5cf6'}
        )
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabela resumida
    st.markdown("#### 📋 Cards em Andamento")
    df_andamento = df[~df['status_cat'].isin(['done', 'backlog', 'deferred'])]
    
    if not df_andamento.empty:
        df_display = df_andamento[['ticket_id', 'titulo', 'tipo', 'status', 'desenvolvedor', 'qa', 'sp', 'bugs', 'dias_em_status']].copy()
        df_display.columns = ['Ticket', 'Título', 'Tipo', 'Status', 'Dev', 'QA', 'SP', 'Bugs', 'Dias']
        df_display['Título'] = df_display['Título'].str[:50] + '...'
        
        st.dataframe(df_display, hide_index=True, use_container_width=True)
    else:
        st.info("Nenhum card em andamento no momento.")


def aba_qa_gargalos(df: pd.DataFrame):
    """Aba de QA e Gargalos."""
    st.markdown("### 🔬 Análise de QA e Gargalos")
    st.caption("Identifique gargalos no processo de validação e monitore a carga do time de QA")
    
    metricas_qa = calcular_metricas_qa(df)
    
    # KPIs de QA
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_fila = metricas_qa['funil']['waiting_qa'] + metricas_qa['funil']['testing']
        cor = 'green' if total_fila < 5 else 'yellow' if total_fila < 10 else 'red'
        criar_card_metrica(str(total_fila), "Fila de QA", cor, f"({metricas_qa['funil']['waiting_qa']} aguardando)")
    
    with col2:
        tempo = metricas_qa['tempo']['waiting']
        cor = 'green' if tempo < 2 else 'yellow' if tempo < 5 else 'red'
        criar_card_metrica(f"{tempo:.1f}d", "Tempo Médio Fila", cor)
    
    with col3:
        aging = metricas_qa['aging']['total']
        cor = 'green' if aging == 0 else 'yellow' if aging < 3 else 'red'
        criar_card_metrica(str(aging), f"Aging (>{REGRAS['dias_aging_alerta']}d)", cor)
    
    with col4:
        taxa = metricas_qa['taxa_reprovacao']
        cor = 'green' if taxa < 10 else 'yellow' if taxa < 20 else 'red'
        criar_card_metrica(f"{taxa:.0f}%", "Taxa Reprovação", cor)
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        fig = criar_grafico_funil_qa(metricas_qa)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = criar_grafico_carga_qa(metricas_qa['carga_qa'])
        st.plotly_chart(fig, use_container_width=True)
    
    # Cards com aging
    st.markdown("#### ⏰ Cards Envelhecidos (Atenção!)")
    st.caption(f"Cards há mais de {REGRAS['dias_aging_alerta']} dias em status de QA")
    
    aging_df = pd.concat([metricas_qa['aging']['waiting'], metricas_qa['aging']['testing']])
    
    if not aging_df.empty:
        for _, row in aging_df.iterrows():
            cor_classe = 'ticket-critical' if row['dias_em_status'] > 5 else 'ticket-warning'
            st.markdown(f"""
            <div class="ticket-item {cor_classe}">
                <b><a href="{JIRA_BASE_URL}/browse/{row['ticket_id']}" target="_blank">{row['ticket_id']}</a></b> - {row['titulo'][:60]}...
                <br><small>QA: {row['qa']} | {row['dias_em_status']} dias | {row['status']}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ Nenhum card envelhecido! Fluxo de QA saudável.")
    
    # Cards aguardando validação
    st.markdown("---")
    st.markdown("#### ⏳ Fila Completa - Aguardando Validação")
    
    fila_qa = df[df['status_cat'] == 'waiting_qa'].sort_values('dias_em_status', ascending=False)
    
    if not fila_qa.empty:
        df_fila = fila_qa[['ticket_id', 'titulo', 'desenvolvedor', 'qa', 'sp', 'dias_em_status', 'prioridade']].copy()
        df_fila.columns = ['Ticket', 'Título', 'Dev', 'QA', 'SP', 'Dias Aguardando', 'Prioridade']
        df_fila['Título'] = df_fila['Título'].str[:40] + '...'
        st.dataframe(df_fila, hide_index=True, use_container_width=True)
    else:
        st.info("Nenhum card aguardando validação no momento.")


def aba_governanca(df: pd.DataFrame):
    """Aba de Governança de Dados."""
    st.markdown("### 📋 Governança de Dados")
    st.caption("Monitore o preenchimento dos campos obrigatórios para garantir métricas confiáveis")
    
    gov = calcular_metricas_governanca(df)
    
    # Alerta geral
    media_preenchimento = (gov['sp']['pct'] + gov['bugs']['pct'] + gov['complexidade']['pct'] + gov['qa']['pct']) / 4
    
    if media_preenchimento < 50:
        st.markdown("""
        <div class="alert-critical">
            <b>🚨 ATENÇÃO: Qualidade dos dados comprometida!</b>
            <p>Muitos campos obrigatórios não estão preenchidos. Isso impacta diretamente nas métricas e decisões.</p>
        </div>
        """, unsafe_allow_html=True)
    elif media_preenchimento < 80:
        st.markdown("""
        <div class="alert-warning">
            <b>⚠️ Oportunidade de melhoria nos dados</b>
            <p>Alguns campos ainda precisam de preenchimento para métricas mais precisas.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-success">
            <b>✅ Dados em boa qualidade!</b>
            <p>A maioria dos campos obrigatórios está preenchida.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Gráfico de governança
    col1, col2 = st.columns([1, 1])
    
    with col1:
        fig = criar_grafico_governanca(gov)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 Detalhamento")
        
        campos = [
            ("Story Points", gov['sp'], "Obrigatório (exceto Hotfix)"),
            ("Bugs Encontrados", gov['bugs'], "Preencher após validação"),
            ("Complexidade Teste", gov['complexidade'], "Meta futura"),
            ("QA Responsável", gov['qa'], "Obrigatório"),
        ]
        
        for nome, dados, obs in campos:
            cor = '#22c55e' if dados['pct'] >= 80 else '#f59e0b' if dados['pct'] >= 50 else '#ef4444'
            st.markdown(f"""
            **{nome}**  
            <div class="progress-bar">
                <div class="progress-fill" style="width: {dados['pct']}%; background: {cor};">
                    {dados['preenchido']}/{dados['total']} ({dados['pct']:.0f}%)
                </div>
            </div>
            <small style="opacity: 0.7;">{obs}</small>
            """, unsafe_allow_html=True)
            st.markdown("")
    
    st.markdown("---")
    
    # Lista de cards para cobrança
    st.markdown("#### 📝 Cards sem Story Points (para cobrança)")
    st.caption("Lista de cards que precisam de Story Points preenchidos. Exclui Hotfix.")
    
    if gov['sp']['faltando']:
        # Expandir para mostrar detalhes
        with st.expander(f"Ver {len(gov['sp']['faltando'])} cards sem SP"):
            df_faltando = df[df['ticket_id'].isin(gov['sp']['faltando'])][['ticket_id', 'titulo', 'tipo', 'desenvolvedor', 'status']]
            df_faltando.columns = ['Ticket', 'Título', 'Tipo', 'Dev', 'Status']
            df_faltando['Título'] = df_faltando['Título'].str[:50] + '...'
            st.dataframe(df_faltando, hide_index=True, use_container_width=True)
        
        # Botão de exportar
        csv = df[df['ticket_id'].isin(gov['sp']['faltando'])][['ticket_id', 'titulo', 'desenvolvedor']].to_csv(index=False)
        st.download_button(
            "📥 Exportar lista para cobrança",
            csv,
            "cards_sem_sp.csv",
            "text/csv"
        )
    else:
        st.success("✅ Todos os cards têm Story Points preenchidos!")


def aba_produto(df: pd.DataFrame):
    """Aba de métricas por Produto."""
    st.markdown("### 📦 Métricas por Produto")
    st.caption("Visualize a distribuição de cards e métricas segmentadas por produto")
    
    # Distribuição por produto
    produto_stats = df.groupby('produto').agg({
        'ticket_id': 'count',
        'sp': 'sum',
        'bugs': 'sum',
    }).reset_index()
    produto_stats.columns = ['Produto', 'Cards', 'SP', 'Bugs']
    produto_stats['FK'] = produto_stats.apply(lambda x: calcular_fator_k(x['SP'], x['Bugs']), axis=1)
    produto_stats = produto_stats.sort_values('Cards', ascending=False)
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            produto_stats,
            values='Cards',
            names='Produto',
            title='Distribuição por Produto',
            hole=0.4
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            produto_stats,
            x='Produto',
            y='SP',
            color='FK',
            color_continuous_scale='RdYlGn',
            title='Story Points por Produto'
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabela detalhada
    st.markdown("#### 📊 Resumo por Produto")
    
    # Adicionar classificação
    produto_stats['Maturidade'] = produto_stats['FK'].apply(lambda x: classificar_maturidade(x)['emoji'] + ' ' + classificar_maturidade(x)['selo'])
    
    st.dataframe(
        produto_stats[['Produto', 'Cards', 'SP', 'Bugs', 'FK', 'Maturidade']],
        hide_index=True,
        use_container_width=True
    )


def aba_lideranca(df: pd.DataFrame):
    """Aba de Liderança com decisões estratégicas."""
    st.markdown("### 🎯 Painel de Liderança")
    st.caption("Visão executiva para tomada de decisão")
    
    # Métricas globais
    total_cards = len(df)
    sp_total = int(df['sp'].sum())
    bugs_total = int(df['bugs'].sum())
    concluidos = len(df[df['status_cat'] == 'done'])
    pct_conclusao = concluidos / total_cards * 100 if total_cards > 0 else 0
    
    # Fator K geral
    fk = calcular_fator_k(sp_total, bugs_total)
    mat = classificar_maturidade(fk)
    
    # Health Score simplificado
    health = min(100, (pct_conclusao * 0.5) + (min(fk, 4) * 12.5))
    
    # Card de decisão Go/No-Go
    dias_release = df['dias_ate_release'].max() if 'dias_ate_release' in df.columns else 10
    bloqueados = len(df[df['status_cat'].isin(['blocked', 'rejected'])])
    
    if bloqueados > 0 or pct_conclusao < 30:
        decisao = "🛑 ATENÇÃO NECESSÁRIA"
        decisao_cor = "red"
        decisao_msg = "Cards bloqueados ou taxa de conclusão muito baixa"
    elif pct_conclusao < 50 and dias_release < 3:
        decisao = "⚠️ REVISAR ESCOPO"
        decisao_cor = "yellow"
        decisao_msg = "Pouco tempo e muitos cards pendentes"
    else:
        decisao = "✅ NO CAMINHO"
        decisao_cor = "green"
        decisao_msg = "Sprint progredindo conforme esperado"
    
    # Layout principal
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div class="status-card status-{decisao_cor}" style="padding: 25px;">
            <p style="font-size: 24px; margin: 0;">{decisao}</p>
            <p class="card-label" style="margin-top: 10px;">{decisao_msg}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        cor_health = 'green' if health >= 70 else 'yellow' if health >= 50 else 'red'
        criar_card_metrica(f"{health:.0f}", "Health Score", cor_health, "Saúde da Release")
    
    with col2:
        # KPIs em linha
        col_a, col_b, col_c, col_d = st.columns(4)
        
        with col_a:
            st.metric("Cards", total_cards)
        with col_b:
            st.metric("Concluídos", f"{pct_conclusao:.0f}%")
        with col_c:
            st.metric("Fator K", f"{fk:.1f}", mat['selo'])
        with col_d:
            st.metric("Dias Release", dias_release)
        
        st.markdown("---")
        
        # Pontos de atenção
        st.markdown("**🚨 Pontos de Atenção:**")
        
        pontos = []
        
        if bloqueados > 0:
            pontos.append(f"🚫 {bloqueados} card(s) bloqueado(s)/reprovado(s)")
        
        gov = calcular_metricas_governanca(df)
        if gov['sp']['pct'] < 50:
            pontos.append(f"📊 {100-gov['sp']['pct']:.0f}% dos cards sem Story Points")
        
        metricas_qa = calcular_metricas_qa(df)
        if metricas_qa['aging']['total'] > 0:
            pontos.append(f"⏰ {metricas_qa['aging']['total']} card(s) envelhecido(s) em QA")
        
        if metricas_qa['funil']['waiting_qa'] > 10:
            pontos.append(f"⏳ Fila de QA alta: {metricas_qa['funil']['waiting_qa']} cards")
        
        if pontos:
            for p in pontos:
                st.markdown(f"- {p}")
        else:
            st.success("Nenhum ponto crítico identificado!")
    
    st.markdown("---")
    
    # Métricas por desenvolvedor
    st.markdown("#### 👨‍💻 Performance por Desenvolvedor")
    
    dev_stats = df.groupby('desenvolvedor').agg({
        'ticket_id': 'count',
        'sp': 'sum',
        'bugs': 'sum',
        'lead_time': 'mean'
    }).reset_index()
    dev_stats.columns = ['Desenvolvedor', 'Cards', 'SP', 'Bugs', 'Lead Time']
    dev_stats['FK'] = dev_stats.apply(lambda x: calcular_fator_k(x['SP'], x['Bugs']), axis=1)
    dev_stats['Lead Time'] = dev_stats['Lead Time'].round(1)
    dev_stats = dev_stats.sort_values('FK', ascending=False)
    
    st.dataframe(dev_stats, hide_index=True, use_container_width=True)


# ==============================================================================
# FUNÇÃO PRINCIPAL
# ==============================================================================

def main():
    """Função principal do dashboard."""
    aplicar_estilos()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎯 NINA Dashboard")
        st.markdown("---")
        
        # Verificar credenciais
        if not verificar_credenciais():
            st.error("⚠️ Credenciais não configuradas!")
            st.markdown("""
            Configure em `.streamlit/secrets.toml`:
            ```toml
            [jira]
            email = "seu-email@empresa.com"
            token = "seu-token"
            ```
            """)
            st.stop()
        
        # Projeto
        projeto = st.selectbox("Projeto", ["SD", "QA", "PB"], index=0)
        
        # Filtro de Sprint
        filtro_sprint = st.selectbox(
            "Sprint",
            ["Sprint Ativa", "Últimos 30 dias", "Últimos 90 dias"],
            index=0
        )
        
        st.markdown("---")
        
        # Info
        st.caption("v6.0 - NINA Tecnologia")
        st.caption("Dados atualizados automaticamente")
    
    # Construir JQL baseado nos filtros
    if filtro_sprint == "Sprint Ativa":
        jql = f'project = {projeto} AND sprint in openSprints() ORDER BY created DESC'
    elif filtro_sprint == "Últimos 30 dias":
        jql = f'project = {projeto} AND created >= -30d ORDER BY created DESC'
    else:
        jql = f'project = {projeto} AND created >= -90d ORDER BY created DESC'
    
    # AUTO-LOAD: Carregar dados automaticamente
    with st.spinner("🔄 Carregando dados do Jira..."):
        issues, ultima_atualizacao = buscar_dados_jira_cached(projeto, jql)
    
    if issues is None:
        st.error("❌ Não foi possível carregar dados do Jira")
        st.stop()
    
    if len(issues) == 0:
        st.warning("⚠️ Nenhum card encontrado com os filtros selecionados")
        st.stop()
    
    # Processar dados
    df = processar_issues(issues)
    
    # Filtro por produto (sidebar)
    with st.sidebar:
        produtos_disponiveis = ['Todos'] + sorted(df['produto'].unique().tolist())
        filtro_produto = st.selectbox("Produto", produtos_disponiveis, index=0)
        
        if filtro_produto != 'Todos':
            df = df[df['produto'] == filtro_produto]
    
    # Header
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h1 style="margin: 0;">📊 Dashboard SD - NINA</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Abas
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Visão Geral",
        "🔬 QA & Gargalos",
        "📋 Governança",
        "📦 Produto",
        "🎯 Liderança"
    ])
    
    with tab1:
        aba_visao_geral(df, ultima_atualizacao)
    
    with tab2:
        aba_qa_gargalos(df)
    
    with tab3:
        aba_governanca(df)
    
    with tab4:
        aba_produto(df)
    
    with tab5:
        aba_lideranca(df)


# ==============================================================================
# EXECUÇÃO
# ==============================================================================

if __name__ == "__main__":
    main()
