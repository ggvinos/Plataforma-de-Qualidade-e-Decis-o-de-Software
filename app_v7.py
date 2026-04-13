"""
================================================================================
JIRA DASHBOARD v7.0 - NINA TECNOLOGIA - VERSÃO COMPLETA
================================================================================
FOCO: SD (Software Development) + Visibilidade QA + Governança + Histórico

MELHORIAS v7.0 (combinação v5 + v6 + novas métricas):
- Auto-load de dados ao abrir (sem clique manual)
- Cache inteligente (5 min) com indicador de última atualização
- Aba QA/Gargalos: Funil de validação, tempo em status, aging
- Aba Governança: % campos preenchidos, lista para cobrança
- Aba Histórico: Tendências por sprint (Fator K, FPY, DDP, Bugs)
- Filtro por Produto (Plataforma, NinaChat, HUB, etc.)
- Cards CLICÁVEIS com links diretos para o Jira
- Exportação Excel/CSV/TXT
- NOVAS MÉTRICAS (Ellen/Produto):
  - Cards iniciados e finalizados na mesma sprint
  - Cards adicionados fora do período da sprint
  - Hotfix por produto
  - Estágio de card por produto

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
import io
import base64

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

CUSTOM_FIELDS = {
    "story_points": "customfield_11257",
    "story_points_alt": "customfield_10016", 
    "sprint": "customfield_10020",
    "bugs_encontrados": "customfield_11157",
    "complexidade_teste": "customfield_11290",
    "qa_responsavel": "customfield_10487",
    "produto": "customfield_10102",
}

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

REGRAS = {
    "hotfix_sp_default": 2,
    "cache_ttl_minutos": 5,
    "dias_aging_alerta": 3,
}

# ==============================================================================
# UTILITÁRIOS
# ==============================================================================

def link_jira(ticket_id: str) -> str:
    """Gera link para o Jira."""
    return f"{JIRA_BASE_URL}/browse/{ticket_id}"


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
        sp_original = bool(f.get(CUSTOM_FIELDS['story_points']) or f.get(CUSTOM_FIELDS['story_points_alt']))
        if sp == 0 and tipo == "HOTFIX":
            sp = REGRAS["hotfix_sp_default"]
        
        # Sprint
        sprint_f = f.get(CUSTOM_FIELDS['sprint'], [])
        sprint = sprint_f[-1].get('name', 'Sem Sprint') if sprint_f else 'Sem Sprint'
        sprint_id = sprint_f[-1].get('id') if sprint_f else None
        sprint_start = None
        sprint_end = None
        if sprint_f:
            sprint_start_str = sprint_f[-1].get('startDate')
            sprint_end_str = sprint_f[-1].get('endDate')
            if sprint_start_str:
                try:
                    sprint_start = datetime.fromisoformat(sprint_start_str.replace('Z', '+00:00')).replace(tzinfo=None)
                except:
                    pass
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
        
        resolutiondate = None
        if f.get('resolutiondate'):
            try:
                resolutiondate = datetime.fromisoformat(f.get('resolutiondate').replace('Z', '+00:00')).replace(tzinfo=None)
            except:
                pass
        
        # Métricas calculadas
        dias_em_status = (hoje - atualizado).days
        lead_time = (resolutiondate - criado).days if resolutiondate else (hoje - criado).days
        
        # Dias até release
        dias_ate_release = 0
        if sprint_end:
            dias_ate_release = max(0, (sprint_end - hoje).days)
        
        # NOVAS MÉTRICAS (Ellen/Produto)
        # 1. Card criado dentro do período da sprint?
        criado_na_sprint = False
        if sprint_start and sprint_end:
            criado_na_sprint = sprint_start <= criado <= sprint_end
        
        # 2. Card finalizado na mesma sprint que começou?
        finalizado_mesma_sprint = False
        if status_cat == 'done' and criado_na_sprint:
            finalizado_mesma_sprint = True
        
        # 3. Card adicionado fora do período (depois do início)
        adicionado_fora_periodo = False
        if sprint_start and criado > sprint_start + timedelta(days=2):  # Mais de 2 dias após início
            adicionado_fora_periodo = True
        
        # Flags de preenchimento
        sp_preenchido = sp_original
        bugs_preenchido = f.get(CUSTOM_FIELDS['bugs_encontrados']) is not None
        complexidade_preenchida = bool(complexidade)
        qa_preenchido = qa != 'Não atribuído'
        
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
            'sp_original': sp_original,
            'bugs': int(bugs) if bugs else 0,
            'sprint': sprint,
            'sprint_id': sprint_id,
            'sprint_start': sprint_start,
            'sprint_end': sprint_end,
            'prioridade': f.get('priority', {}).get('name', 'Média') if f.get('priority') else 'Média',
            'complexidade': complexidade,
            'produto': produto,
            'produtos': produtos,
            'criado': criado,
            'atualizado': atualizado,
            'resolutiondate': resolutiondate,
            'dias_em_status': dias_em_status,
            'lead_time': lead_time,
            'dias_ate_release': dias_ate_release,
            # Flags de preenchimento
            'sp_preenchido': sp_preenchido,
            'bugs_preenchido': bugs_preenchido,
            'complexidade_preenchida': complexidade_preenchida,
            'qa_preenchido': qa_preenchido,
            # Novas métricas Ellen
            'criado_na_sprint': criado_na_sprint,
            'finalizado_mesma_sprint': finalizado_mesma_sprint,
            'adicionado_fora_periodo': adicionado_fora_periodo,
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
        return {"selo": "Gold", "emoji": "🥇", "cor": "#22c55e", "desc": "Excelente"}
    elif fk >= 2.0:
        return {"selo": "Silver", "emoji": "🥈", "cor": "#eab308", "desc": "Bom"}
    elif fk >= 1.0:
        return {"selo": "Bronze", "emoji": "🥉", "cor": "#f97316", "desc": "Regular"}
    else:
        return {"selo": "Risco", "emoji": "⚠️", "cor": "#ef4444", "desc": "Crítico"}


def calcular_ddp(df: pd.DataFrame) -> Dict:
    """Defect Detection Percentage."""
    bugs_qa = df['bugs'].sum()
    bugs_estimados_prod = max(1, len(df) * 0.05)
    total_bugs = bugs_qa + bugs_estimados_prod
    ddp = (bugs_qa / total_bugs * 100) if total_bugs > 0 else 100
    return {"valor": round(ddp, 1), "bugs_qa": int(bugs_qa)}


def calcular_fpy(df: pd.DataFrame) -> Dict:
    """First Pass Yield."""
    total = len(df)
    if total == 0:
        return {"valor": 0, "sem_bugs": 0, "total": 0}
    sem_bugs = len(df[df['bugs'] == 0])
    fpy = sem_bugs / total * 100
    return {"valor": round(fpy, 1), "sem_bugs": sem_bugs, "total": total}


def calcular_lead_time(df: pd.DataFrame) -> Dict:
    """Lead time médio e percentis."""
    if df.empty:
        return {"medio": 0, "p50": 0, "p85": 0, "p95": 0}
    lead_times = df['lead_time']
    return {
        "medio": round(lead_times.mean(), 1),
        "p50": round(lead_times.quantile(0.5), 1),
        "p85": round(lead_times.quantile(0.85), 1),
        "p95": round(lead_times.quantile(0.95), 1),
    }


def calcular_metricas_governanca(df: pd.DataFrame) -> Dict:
    """Calcula métricas de governança de dados."""
    total = len(df)
    if total == 0:
        return {
            "sp": {"preenchido": 0, "total": 0, "pct": 0, "faltando": []},
            "bugs": {"preenchido": 0, "total": 0, "pct": 0, "faltando": []},
            "complexidade": {"preenchido": 0, "total": 0, "pct": 0, "faltando": []},
            "qa": {"preenchido": 0, "total": 0, "pct": 0, "faltando": []},
        }
    
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
    waiting_qa = df[df['status_cat'] == 'waiting_qa']
    testing = df[df['status_cat'] == 'testing']
    done = df[df['status_cat'] == 'done']
    blocked = df[df['status_cat'] == 'blocked']
    rejected = df[df['status_cat'] == 'rejected']
    
    tempo_waiting = waiting_qa['dias_em_status'].mean() if not waiting_qa.empty else 0
    tempo_testing = testing['dias_em_status'].mean() if not testing.empty else 0
    
    aging_waiting = waiting_qa[waiting_qa['dias_em_status'] >= REGRAS['dias_aging_alerta']]
    aging_testing = testing[testing['dias_em_status'] >= REGRAS['dias_aging_alerta']]
    
    carga_qa = df[df['status_cat'].isin(['waiting_qa', 'testing'])].groupby('qa').agg({
        'ticket_id': 'count',
        'sp': 'sum'
    }).reset_index()
    carga_qa.columns = ['QA', 'Cards', 'SP']
    
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


def calcular_metricas_produto(df: pd.DataFrame) -> Dict:
    """Calcula métricas específicas por produto (novas métricas Ellen)."""
    # Hotfix por produto
    hotfix_por_produto = df[df['tipo'] == 'HOTFIX'].groupby('produto').size().reset_index(name='hotfixes')
    
    # Estágio por produto
    estagio_por_produto = df.groupby(['produto', 'status_cat']).size().unstack(fill_value=0)
    
    # Cards finalizados na mesma sprint
    finalizados_mesma_sprint = df[df['finalizado_mesma_sprint'] == True]
    
    # Cards adicionados fora do período
    adicionados_fora = df[df['adicionado_fora_periodo'] == True]
    
    return {
        "hotfix_por_produto": hotfix_por_produto,
        "estagio_por_produto": estagio_por_produto,
        "finalizados_mesma_sprint": finalizados_mesma_sprint,
        "adicionados_fora": adicionados_fora,
        "total_finalizados_mesma_sprint": len(finalizados_mesma_sprint),
        "total_adicionados_fora": len(adicionados_fora),
    }


def calcular_health_score(df: pd.DataFrame) -> Dict:
    """Calcula score de saúde da release (0-100)."""
    detalhes = {}
    
    # 1. Taxa de conclusão (peso 30)
    concluidos = len(df[df['status_cat'] == 'done'])
    taxa_conclusao = concluidos / len(df) * 100 if len(df) > 0 else 0
    score_conclusao = min(30, taxa_conclusao * 0.3)
    detalhes['conclusao'] = {'peso': 30, 'score': round(score_conclusao, 1), 'valor': f"{taxa_conclusao:.0f}%"}
    
    # 2. DDP (peso 25)
    ddp = calcular_ddp(df)
    score_ddp = min(25, ddp['valor'] * 0.25)
    detalhes['ddp'] = {'peso': 25, 'score': round(score_ddp, 1), 'valor': f"{ddp['valor']}%"}
    
    # 3. FPY (peso 20)
    fpy = calcular_fpy(df)
    score_fpy = min(20, fpy['valor'] * 0.2)
    detalhes['fpy'] = {'peso': 20, 'score': round(score_fpy, 1), 'valor': f"{fpy['valor']}%"}
    
    # 4. Gargalos (peso 15)
    metricas_qa = calcular_metricas_qa(df)
    penalidade = metricas_qa['aging']['total'] * 3
    score_gargalos = max(0, 15 - penalidade)
    detalhes['gargalos'] = {'peso': 15, 'score': score_gargalos, 'valor': f"{metricas_qa['aging']['total']} aging"}
    
    # 5. Lead Time (peso 10)
    lead = calcular_lead_time(df)
    score_lead = 10 if lead['medio'] <= 7 else 7 if lead['medio'] <= 10 else 4 if lead['medio'] <= 14 else 0
    detalhes['lead_time'] = {'peso': 10, 'score': score_lead, 'valor': f"{lead['medio']} dias"}
    
    score_total = sum(d['score'] for d in detalhes.values())
    
    if score_total >= 75:
        status = "🟢 Saudável"
    elif score_total >= 50:
        status = "🟡 Atenção"
    elif score_total >= 25:
        status = "🟠 Alerta"
    else:
        status = "🔴 Crítico"
    
    return {'score': score_total, 'status': status, 'detalhes': detalhes}


# ==============================================================================
# DADOS DE TENDÊNCIA (HISTÓRICO)
# ==============================================================================

def gerar_dados_tendencia_mock() -> pd.DataFrame:
    """Gera dados históricos simulados para demonstração de tendências."""
    import random
    sprints = [f"Release {i}" for i in range(233, 239)]
    
    dados = []
    for i, sprint in enumerate(sprints):
        base_fk = 1.5 + (i * 0.25) + random.uniform(-0.3, 0.3)
        base_fpy = 45 + (i * 5) + random.uniform(-5, 5)
        base_ddp = 70 + (i * 3) + random.uniform(-5, 5)
        base_health = 50 + (i * 5) + random.uniform(-8, 8)
        
        dados.append({
            'sprint': sprint,
            'fator_k': round(min(4, max(0.5, base_fk)), 2),
            'fpy': round(min(95, max(30, base_fpy)), 1),
            'ddp': round(min(98, max(50, base_ddp)), 1),
            'health_score': round(min(95, max(25, base_health)), 0),
            'bugs_total': max(5, 30 - (i * 3) + random.randint(-5, 5)),
            'cards_total': random.randint(40, 60),
            'lead_time_medio': round(max(3, 12 - (i * 0.8) + random.uniform(-1, 1)), 1),
        })
    
    return pd.DataFrame(dados)


# ==============================================================================
# EXPORTAÇÃO
# ==============================================================================

def exportar_para_csv(df: pd.DataFrame) -> str:
    """Exporta dados para CSV."""
    df_export = df[['ticket_id', 'titulo', 'tipo', 'status', 'desenvolvedor', 'qa', 
                    'sp', 'bugs', 'sprint', 'produto', 'prioridade', 'lead_time']].copy()
    return df_export.to_csv(index=False)


def exportar_para_excel(df: pd.DataFrame, metricas: Dict) -> bytes:
    """Exporta dados para Excel com múltiplas abas."""
    output = io.BytesIO()
    
    try:
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Aba 1: Dados dos Cards
            df_export = df[['ticket_id', 'titulo', 'tipo', 'status', 'desenvolvedor', 'qa', 
                            'sp', 'bugs', 'sprint', 'produto', 'lead_time']].copy()
            df_export.to_excel(writer, sheet_name='Cards', index=False)
            
            # Aba 2: Métricas
            metricas_df = pd.DataFrame([
                {'Métrica': 'Total de Cards', 'Valor': len(df)},
                {'Métrica': 'Story Points Total', 'Valor': int(df['sp'].sum())},
                {'Métrica': 'Bugs Encontrados', 'Valor': int(df['bugs'].sum())},
                {'Métrica': 'Cards Concluídos', 'Valor': len(df[df['status_cat'] == 'done'])},
                {'Métrica': 'Health Score', 'Valor': metricas.get('health_score', 'N/A')},
            ])
            metricas_df.to_excel(writer, sheet_name='Métricas', index=False)
            
            # Aba 3: Por Desenvolvedor
            dev_stats = df.groupby('desenvolvedor').agg({
                'ticket_id': 'count', 'sp': 'sum', 'bugs': 'sum'
            }).reset_index()
            dev_stats.columns = ['Desenvolvedor', 'Cards', 'SP', 'Bugs']
            dev_stats.to_excel(writer, sheet_name='Por Desenvolvedor', index=False)
        
        return output.getvalue()
    except:
        return None


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
    .status-card:hover { transform: translateY(-3px); }
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
        padding: 15px; border-radius: 8px; margin: 10px 0;
    }
    .alert-warning {
        background: rgba(234, 179, 8, 0.15);
        border-left: 4px solid #eab308;
        padding: 15px; border-radius: 8px; margin: 10px 0;
    }
    .alert-info {
        background: rgba(59, 130, 246, 0.15);
        border-left: 4px solid #3b82f6;
        padding: 15px; border-radius: 8px; margin: 10px 0;
    }
    .alert-success {
        background: rgba(34, 197, 94, 0.15);
        border-left: 4px solid #22c55e;
        padding: 15px; border-radius: 8px; margin: 10px 0;
    }
    
    /* Ticket cards clicáveis */
    .ticket-card {
        border-radius: 10px;
        padding: 12px 15px;
        margin: 8px 0;
        border-left: 4px solid;
        background: rgba(100, 100, 100, 0.05);
        transition: all 0.2s ease;
    }
    .ticket-card:hover {
        transform: translateX(5px);
        background: rgba(100, 100, 100, 0.1);
    }
    .ticket-risk-high { border-left-color: #ef4444; }
    .ticket-risk-medium { border-left-color: #f97316; }
    .ticket-risk-low { border-left-color: #22c55e; }
    
    /* Header */
    .header-bar {
        background: linear-gradient(90deg, #AF0C37, #8B0A2C);
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
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
    diff = (agora - ultima_atualizacao).total_seconds() / 60
    
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


def mostrar_card_ticket(row: pd.Series, compacto: bool = False):
    """Mostra card de ticket COM LINK para Jira."""
    bugs = row.get('bugs', 0)
    risco = 'high' if bugs >= 3 else 'medium' if bugs >= 1 else 'low'
    link = row.get('link', link_jira(row['ticket_id']))
    
    if compacto:
        st.markdown(f"""
        <div class="ticket-card ticket-risk-{risco}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <a href="{link}" target="_blank" style="color: #6366f1; font-weight: bold; text-decoration: none;">🔗 {row['ticket_id']}</a>
                <span style="opacity: 0.7;">{row.get('sp', 0)} SP | 🐛 {bugs}</span>
            </div>
            <p style="margin: 5px 0 0 0; font-size: 13px; opacity: 0.9;">{str(row.get('titulo', ''))[:50]}...</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="ticket-card ticket-risk-{risco}">
            <div style="display: flex; justify-content: space-between;">
                <a href="{link}" target="_blank" style="color: #6366f1; font-weight: bold; text-decoration: none;">🔗 {row['ticket_id']}</a>
                <span style="color: {'#ef4444' if bugs >= 3 else '#f97316' if bugs >= 1 else '#22c55e'}; font-weight: bold;">🐛 {bugs} bugs</span>
            </div>
            <p style="margin: 8px 0;">{row.get('titulo', '')}</p>
            <p style="font-size: 12px; opacity: 0.8;">
                <b>Dev:</b> {row.get('desenvolvedor', 'N/A')} | 
                <b>QA:</b> {row.get('qa', 'N/A')} | 
                <b>SP:</b> {row.get('sp', 0)} | 
                <b>{row.get('status', 'N/A')}</b>
            </p>
        </div>
        """, unsafe_allow_html=True)


def mostrar_lista_tickets_expandivel(df: pd.DataFrame, titulo: str, max_inicial: int = 5):
    """Mostra lista de tickets com expander."""
    if df.empty:
        st.info(f"Nenhum card em: {titulo}")
        return
    
    with st.expander(f"📋 {titulo} ({len(df)} cards)", expanded=False):
        for i, (_, row) in enumerate(df.iterrows()):
            if i < max_inicial:
                mostrar_card_ticket(row, compacto=True)
            elif i == max_inicial:
                st.caption(f"... e mais {len(df) - max_inicial} cards")
                break


# ==============================================================================
# GRÁFICOS
# ==============================================================================

def criar_grafico_funil_qa(metricas_qa: Dict) -> go.Figure:
    """Cria gráfico de funil de validação QA."""
    funil = metricas_qa['funil']
    
    labels = ['⏳ Aguardando QA', '🧪 Em Validação', '✅ Concluído']
    values = [funil['waiting_qa'], funil['testing'], funil['done']]
    colors = ['#f59e0b', '#06b6d4', '#22c55e']
    
    if funil['blocked'] > 0:
        labels.append('🚫 Bloqueado')
        values.append(funil['blocked'])
        colors.append('#ef4444')
    
    if funil['rejected'] > 0:
        labels.append('❌ Reprovado')
        values.append(funil['rejected'])
        colors.append('#dc2626')
    
    fig = go.Figure(go.Funnel(
        y=labels, x=values,
        textinfo="value+percent total",
        marker=dict(color=colors),
        connector=dict(line=dict(color="royalblue", dash="dot", width=2))
    ))
    
    fig.update_layout(title="Funil de Validação QA", height=300, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def criar_grafico_tendencia_fator_k(df_tendencia: pd.DataFrame) -> go.Figure:
    """Cria gráfico de tendência do Fator K."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_tendencia['sprint'], y=df_tendencia['fator_k'],
        mode='lines+markers', name='Fator K',
        line=dict(color='#6366f1', width=3),
        marker=dict(size=10),
        hovertemplate='<b>%{x}</b><br>Fator K: %{y:.2f}<extra></extra>'
    ))
    
    fig.add_hline(y=3.0, line_dash="dash", line_color="#22c55e", annotation_text="Gold (≥3.0)")
    fig.add_hline(y=2.0, line_dash="dash", line_color="#eab308", annotation_text="Silver (≥2.0)")
    fig.add_hline(y=1.0, line_dash="dash", line_color="#f97316", annotation_text="Bronze (≥1.0)")
    
    fig.update_layout(
        title="📈 Evolução do Fator K (Maturidade)",
        xaxis_title="Sprint", yaxis_title="Fator K",
        hovermode='x unified', template='plotly_white', height=350
    )
    return fig


def criar_grafico_tendencia_qualidade(df_tendencia: pd.DataFrame) -> go.Figure:
    """Cria gráfico de tendência FPY e DDP."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_tendencia['sprint'], y=df_tendencia['fpy'],
        mode='lines+markers', name='FPY (%)',
        line=dict(color='#22c55e', width=2), marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=df_tendencia['sprint'], y=df_tendencia['ddp'],
        mode='lines+markers', name='DDP (%)',
        line=dict(color='#3b82f6', width=2), marker=dict(size=8)
    ))
    
    fig.add_hline(y=80, line_dash="dot", line_color="#22c55e", annotation_text="Meta FPY (80%)")
    
    fig.update_layout(
        title="📊 Evolução de Qualidade (FPY e DDP)",
        xaxis_title="Sprint", yaxis_title="Percentual (%)",
        hovermode='x unified', template='plotly_white', height=350,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def criar_grafico_tendencia_bugs(df_tendencia: pd.DataFrame) -> go.Figure:
    """Cria gráfico de tendência de bugs."""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_tendencia['sprint'], y=df_tendencia['bugs_total'],
        name='Bugs Encontrados', marker_color='#ef4444',
        text=df_tendencia['bugs_total'], textposition='outside'
    ))
    
    fig.add_trace(go.Scatter(
        x=df_tendencia['sprint'],
        y=df_tendencia['bugs_total'].rolling(3, min_periods=1).mean(),
        mode='lines', name='Média Móvel (3 sprints)',
        line=dict(color='#6366f1', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title="🐛 Bugs por Sprint",
        xaxis_title="Sprint", yaxis_title="Quantidade de Bugs",
        template='plotly_white', height=350, showlegend=True
    )
    return fig


def criar_grafico_estagio_por_produto(df: pd.DataFrame) -> go.Figure:
    """Cria gráfico de estágio por produto."""
    # Agrupar por produto e status
    data = df.groupby(['produto', 'status_cat']).size().reset_index(name='count')
    
    fig = px.bar(
        data, x='produto', y='count', color='status_cat',
        color_discrete_map=STATUS_CORES,
        title='Estágio de Cards por Produto',
        labels={'count': 'Cards', 'produto': 'Produto', 'status_cat': 'Status'}
    )
    
    fig.update_layout(height=400, barmode='stack')
    return fig


def criar_grafico_hotfix_por_produto(df: pd.DataFrame) -> go.Figure:
    """Cria gráfico de hotfix por produto."""
    hotfix_df = df[df['tipo'] == 'HOTFIX']
    
    if hotfix_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Nenhum Hotfix encontrado", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    data = hotfix_df.groupby('produto').size().reset_index(name='count')
    
    fig = px.pie(
        data, values='count', names='produto',
        title='🔥 Hotfixes por Produto',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(height=350)
    return fig


# ==============================================================================
# ABAS DO DASHBOARD
# ==============================================================================

def aba_visao_geral(df: pd.DataFrame, ultima_atualizacao: datetime):
    """Aba principal com visão geral da sprint."""
    
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
        criar_card_metrica(f"{pct:.0f}%", "Concluído", cor, f"{concluidos}/{len(df)}")
    
    with col4:
        bugs_total = int(df['bugs'].sum())
        cor = 'green' if bugs_total < 10 else 'yellow' if bugs_total < 20 else 'red'
        criar_card_metrica(str(bugs_total), "Bugs", cor)
    
    with col5:
        fk = calcular_fator_k(sp_total, bugs_total)
        mat = classificar_maturidade(fk)
        cor_map = {'#22c55e': 'green', '#eab308': 'yellow', '#f97316': 'orange', '#ef4444': 'red'}
        criar_card_metrica(f"{fk:.1f}", f"Fator K {mat['emoji']}", cor_map.get(mat['cor'], 'blue'), mat['selo'])
    
    st.markdown("---")
    
    # Distribuição por status COM LISTAGEM
    st.markdown("#### 📋 Cards por Status")
    
    status_counts = df.groupby('status_cat').size().to_dict()
    
    cols = st.columns(4)
    status_order = ['development', 'code_review', 'waiting_qa', 'testing']
    
    for i, status in enumerate(status_order):
        with cols[i]:
            count = status_counts.get(status, 0)
            nome = STATUS_NOMES.get(status, status)
            cor = STATUS_CORES.get(status, '#6b7280')
            
            st.markdown(f"""
            <div style="background: {cor}20; border-left: 4px solid {cor}; padding: 15px; border-radius: 8px;">
                <p style="font-size: 28px; font-weight: bold; margin: 0;">{count}</p>
                <p style="font-size: 13px; margin: 5px 0 0 0;">{nome}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Mostrar cards expandíveis
            df_status = df[df['status_cat'] == status]
            if not df_status.empty:
                mostrar_lista_tickets_expandivel(df_status, nome, max_inicial=3)
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição por tipo
        tipo_count = df['tipo'].value_counts().reset_index()
        tipo_count.columns = ['tipo', 'count']
        
        fig = px.pie(tipo_count, values='count', names='tipo', title='Distribuição por Tipo',
                     color='tipo', color_discrete_map={'TAREFA': '#3b82f6', 'BUG': '#ef4444', 'HOTFIX': '#f59e0b', 'SUGESTÃO': '#8b5cf6'},
                     hole=0.4)
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Distribuição por produto
        prod_count = df['produto'].value_counts().reset_index()
        prod_count.columns = ['produto', 'count']
        
        fig = px.bar(prod_count.head(6), x='produto', y='count', title='Cards por Produto',
                     color='count', color_continuous_scale='Blues')
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)


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
        # Carga por QA
        if not metricas_qa['carga_qa'].empty:
            fig = px.bar(
                metricas_qa['carga_qa'].sort_values('Cards', ascending=True),
                x='Cards', y='QA', orientation='h', color='SP',
                color_continuous_scale='Blues', title='Carga por QA'
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum card em validação no momento.")
    
    # Cards com aging - COM LINKS
    st.markdown("#### ⏰ Cards Envelhecidos (Atenção!)")
    
    aging_df = pd.concat([metricas_qa['aging']['waiting'], metricas_qa['aging']['testing']])
    
    if not aging_df.empty:
        for _, row in aging_df.iterrows():
            mostrar_card_ticket(row, compacto=False)
    else:
        st.success("✅ Nenhum card envelhecido! Fluxo de QA saudável.")
    
    # Fila completa COM LINKS
    st.markdown("---")
    st.markdown("#### ⏳ Fila Completa - Aguardando Validação")
    
    fila_qa = df[df['status_cat'] == 'waiting_qa'].sort_values('dias_em_status', ascending=False)
    mostrar_lista_tickets_expandivel(fila_qa, "Aguardando QA", max_inicial=10)


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
            <p>Muitos campos obrigatórios não estão preenchidos. Isso impacta diretamente nas métricas.</p>
        </div>
        """, unsafe_allow_html=True)
    elif media_preenchimento < 80:
        st.markdown("""
        <div class="alert-warning">
            <b>⚠️ Oportunidade de melhoria nos dados</b>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-success">
            <b>✅ Dados em boa qualidade!</b>
        </div>
        """, unsafe_allow_html=True)
    
    # Barras de progresso
    st.markdown("#### 📊 Campos Obrigatórios")
    
    campos = [
        ("Story Points", gov['sp'], "Obrigatório (exceto Hotfix)"),
        ("Bugs Encontrados", gov['bugs'], "Preencher após validação"),
        ("Complexidade Teste", gov['complexidade'], "Meta futura"),
        ("QA Responsável", gov['qa'], "Obrigatório"),
    ]
    
    for nome, dados, obs in campos:
        cor = '#22c55e' if dados['pct'] >= 80 else '#f59e0b' if dados['pct'] >= 50 else '#ef4444'
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{nome}** ({dados['preenchido']}/{dados['total']})")
            st.markdown(f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width: {dados['pct']}%; background: {cor};">
                    {dados['pct']:.0f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.caption(obs)
        with col2:
            if dados['faltando']:
                with st.expander(f"Ver {len(dados['faltando'])} faltando"):
                    for ticket in dados['faltando'][:10]:
                        st.markdown(f"- [{ticket}]({link_jira(ticket)})")
                    if len(dados['faltando']) > 10:
                        st.caption(f"...e mais {len(dados['faltando'])-10}")
    
    # Exportar lista para cobrança
    st.markdown("---")
    if gov['sp']['faltando']:
        csv = df[df['ticket_id'].isin(gov['sp']['faltando'])][['ticket_id', 'titulo', 'desenvolvedor']].to_csv(index=False)
        st.download_button("📥 Exportar cards sem SP", csv, "cards_sem_sp.csv", "text/csv")


def aba_produto(df: pd.DataFrame):
    """Aba de métricas por Produto (com novas métricas Ellen)."""
    st.markdown("### 📦 Métricas por Produto")
    st.caption("Visualize métricas segmentadas por produto")
    
    metricas_prod = calcular_metricas_produto(df)
    
    # KPIs novas métricas Ellen
    st.markdown("#### 🎯 Indicadores de Fluxo da Sprint")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_finalizados = metricas_prod['total_finalizados_mesma_sprint']
        total_done = len(df[df['status_cat'] == 'done'])
        pct = total_finalizados / total_done * 100 if total_done > 0 else 0
        cor = 'green' if pct >= 70 else 'yellow' if pct >= 40 else 'red'
        criar_card_metrica(f"{total_finalizados}", "Iniciados e Finalizados na Sprint", cor, f"{pct:.0f}% dos concluídos")
    
    with col2:
        total_fora = metricas_prod['total_adicionados_fora']
        cor = 'green' if total_fora < 3 else 'yellow' if total_fora < 6 else 'red'
        criar_card_metrica(str(total_fora), "Cards Fora do Período", cor, "Adicionados após início")
    
    with col3:
        total_hotfix = len(df[df['tipo'] == 'HOTFIX'])
        cor = 'green' if total_hotfix < 5 else 'yellow' if total_hotfix < 10 else 'red'
        criar_card_metrica(str(total_hotfix), "Total Hotfixes", cor)
    
    st.markdown("---")
    
    # Cards adicionados fora do período - COM LINKS
    if not metricas_prod['adicionados_fora'].empty:
        st.markdown("#### ⚠️ Cards Adicionados Fora do Período da Sprint")
        st.caption("Estes cards foram adicionados após o início da sprint, comprometendo o planejamento")
        
        for _, row in metricas_prod['adicionados_fora'].head(10).iterrows():
            mostrar_card_ticket(row, compacto=True)
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        fig = criar_grafico_hotfix_por_produto(df)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = criar_grafico_estagio_por_produto(df)
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabela resumo por produto
    st.markdown("#### 📊 Resumo por Produto")
    
    produto_stats = df.groupby('produto').agg({
        'ticket_id': 'count',
        'sp': 'sum',
        'bugs': 'sum',
    }).reset_index()
    produto_stats.columns = ['Produto', 'Cards', 'SP', 'Bugs']
    produto_stats['FK'] = produto_stats.apply(lambda x: calcular_fator_k(x['SP'], x['Bugs']), axis=1)
    
    # Adicionar hotfixes
    hotfix_count = df[df['tipo'] == 'HOTFIX'].groupby('produto').size().reset_index(name='Hotfixes')
    produto_stats = produto_stats.merge(hotfix_count, on='Produto', how='left').fillna(0)
    produto_stats['Hotfixes'] = produto_stats['Hotfixes'].astype(int)
    
    st.dataframe(produto_stats.sort_values('Cards', ascending=False), hide_index=True, use_container_width=True)


def aba_historico(df: pd.DataFrame):
    """Aba de Histórico/Tendências."""
    st.markdown("### 📈 Histórico e Tendências")
    st.caption("Visualize a evolução das métricas ao longo das sprints. *Dados demonstrativos - integração com histórico em desenvolvimento.*")
    
    df_tendencia = gerar_dados_tendencia_mock()
    
    # Tabs para diferentes visualizações
    tab1, tab2, tab3 = st.tabs(["🏆 Fator K", "📊 Qualidade (FPY/DDP)", "🐛 Bugs"])
    
    with tab1:
        fig = criar_grafico_tendencia_fator_k(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
        
        # Análise automática
        ultimo_fk = df_tendencia['fator_k'].iloc[-1]
        primeiro_fk = df_tendencia['fator_k'].iloc[0]
        variacao = ((ultimo_fk - primeiro_fk) / primeiro_fk) * 100 if primeiro_fk > 0 else 0
        
        if variacao > 0:
            st.success(f"📈 **Tendência positiva:** Fator K melhorou {variacao:.1f}% nas últimas sprints")
        else:
            st.warning(f"📉 **Tendência de atenção:** Fator K reduziu {abs(variacao):.1f}% nas últimas sprints")
    
    with tab2:
        fig = criar_grafico_tendencia_qualidade(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
        
        ultimo_fpy = df_tendencia['fpy'].iloc[-1]
        if ultimo_fpy >= 80:
            st.success(f"✅ FPY atual ({ultimo_fpy:.1f}%) está acima da meta de 80%")
        else:
            st.info(f"ℹ️ FPY atual ({ultimo_fpy:.1f}%) está {80 - ultimo_fpy:.1f}% abaixo da meta")
    
    with tab3:
        fig = criar_grafico_tendencia_bugs(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
        
        ultimo_bugs = df_tendencia['bugs_total'].iloc[-1]
        media_bugs = df_tendencia['bugs_total'].mean()
        
        if ultimo_bugs < media_bugs:
            st.success(f"📉 Sprint atual com menos bugs ({ultimo_bugs}) que a média ({media_bugs:.0f})")
        else:
            st.warning(f"📈 Sprint atual com mais bugs ({ultimo_bugs}) que a média ({media_bugs:.0f})")


def aba_lideranca(df: pd.DataFrame):
    """Aba de Liderança com decisões estratégicas."""
    st.markdown("### 🎯 Painel de Liderança")
    st.caption("Visão executiva para tomada de decisão")
    
    # Health Score
    health = calcular_health_score(df)
    
    # Métricas globais
    total_cards = len(df)
    sp_total = int(df['sp'].sum())
    bugs_total = int(df['bugs'].sum())
    concluidos = len(df[df['status_cat'] == 'done'])
    pct_conclusao = concluidos / total_cards * 100 if total_cards > 0 else 0
    fk = calcular_fator_k(sp_total, bugs_total)
    mat = classificar_maturidade(fk)
    
    # Card de decisão
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
    
    # Layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div class="status-card status-{decisao_cor}" style="padding: 25px;">
            <p style="font-size: 24px; margin: 0;">{decisao}</p>
            <p class="card-label" style="margin-top: 10px;">{decisao_msg}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        cor_health = 'green' if health['score'] >= 70 else 'yellow' if health['score'] >= 50 else 'red'
        criar_card_metrica(f"{health['score']:.0f}", "Health Score", cor_health, health['status'])
    
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
        
        # Composição do Health Score
        st.markdown("**📊 Composição do Health Score:**")
        cols = st.columns(5)
        nomes = {'conclusao': 'Conclusão', 'ddp': 'DDP', 'fpy': 'FPY', 'gargalos': 'Gargalos', 'lead_time': 'Lead Time'}
        
        for i, (key, det) in enumerate(health['detalhes'].items()):
            with cols[i]:
                cor = '#22c55e' if det['score'] >= det['peso'] * 0.7 else '#f59e0b' if det['score'] >= det['peso'] * 0.4 else '#ef4444'
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; background: {cor}20; border-radius: 8px;">
                    <p style="font-size: 18px; font-weight: bold; margin: 0;">{det['score']:.0f}/{det['peso']}</p>
                    <p style="font-size: 11px; margin: 3px 0 0 0;">{nomes.get(key, key)}</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Pontos de atenção COM LINKS
    st.markdown("#### 🚨 Pontos de Atenção")
    
    # Cards bloqueados
    bloqueados_df = df[df['status_cat'].isin(['blocked', 'rejected'])]
    if not bloqueados_df.empty:
        st.markdown(f"""
        <div class="alert-critical">
            <b>🚫 {len(bloqueados_df)} card(s) bloqueado(s)/reprovado(s)</b>
        </div>
        """, unsafe_allow_html=True)
        for _, row in bloqueados_df.iterrows():
            mostrar_card_ticket(row, compacto=True)
    
    # Alta prioridade não concluídos
    alta_prio = df[(df['prioridade'].isin(['Alta', 'Muito Alta', 'Muito alto', 'Alto'])) & (df['status_cat'] != 'done')]
    if not alta_prio.empty:
        st.markdown(f"""
        <div class="alert-warning">
            <b>⚠️ {len(alta_prio)} card(s) de alta prioridade em andamento</b>
        </div>
        """, unsafe_allow_html=True)
        mostrar_lista_tickets_expandivel(alta_prio, "Alta Prioridade Pendentes", max_inicial=5)
    
    if bloqueados_df.empty and alta_prio.empty:
        st.success("✅ Nenhum ponto crítico identificado!")
    
    st.markdown("---")
    
    # Exportação
    st.markdown("#### 📥 Exportar Dados")
    col1, col2 = st.columns(2)
    
    with col1:
        csv = exportar_para_csv(df)
        st.download_button("📄 Baixar CSV", csv, f"nina_dashboard_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
    
    with col2:
        try:
            excel = exportar_para_excel(df, {'health_score': health['score']})
            if excel:
                st.download_button("📊 Baixar Excel", excel, f"nina_dashboard_{datetime.now().strftime('%Y%m%d')}.xlsx", 
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except:
            st.info("Instale openpyxl para exportar Excel")


# ==============================================================================
# FUNÇÃO PRINCIPAL
# ==============================================================================

def main():
    """Função principal do dashboard."""
    aplicar_estilos()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎯 NINA Dashboard")
        st.caption("v7.0 - Versão Completa")
        st.markdown("---")
        
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
        
        projeto = st.selectbox("Projeto", ["SD", "QA", "PB"], index=0)
        
        filtro_sprint = st.selectbox(
            "Sprint",
            ["Sprint Ativa", "Últimos 30 dias", "Últimos 90 dias"],
            index=0
        )
        
        st.markdown("---")
        st.caption("NINA Tecnologia")
    
    # JQL
    if filtro_sprint == "Sprint Ativa":
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
        st.warning("⚠️ Nenhum card encontrado")
        st.stop()
    
    df = processar_issues(issues)
    
    # Filtro por produto
    with st.sidebar:
        produtos_disponiveis = ['Todos'] + sorted(df['produto'].unique().tolist())
        filtro_produto = st.selectbox("Produto", produtos_disponiveis, index=0)
        
        if filtro_produto != 'Todos':
            df = df[df['produto'] == filtro_produto]
    
    # Header
    st.markdown("# 📊 Dashboard SD - NINA")
    
    # Abas - TODAS AS FUNCIONALIDADES
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Visão Geral",
        "🔬 QA & Gargalos",
        "📋 Governança",
        "📦 Produto",
        "📈 Histórico",
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
        aba_historico(df)
    
    with tab6:
        aba_lideranca(df)


if __name__ == "__main__":
    main()
