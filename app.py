"""
================================================================================
JIRA DASHBOARD v8.0 - NINA TECNOLOGIA - VERSÃO COMPLETA E ENRIQUECIDA
================================================================================
📊 NinaDash — Dashboard de Inteligência e Métricas de QA

🎯 Propósito: Transformar o QA de um processo sem visibilidade em um sistema 
   de inteligência operacional baseado em dados.

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

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA (DEVE SER PRIMEIRO)
# ==============================================================================
st.set_page_config(
    page_title="NinaDash - Métricas de Qualidade",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# TOOLTIPS E EXPLICAÇÕES DAS MÉTRICAS 
# ==============================================================================

TOOLTIPS = {
    "fator_k": {
        "titulo": "Fator K (Maturidade)",
        "descricao": "Razão entre Story Points entregues e bugs encontrados. Quanto maior, melhor a qualidade do código.",
        "formula": "FK = SP / (Bugs + 1)",
        "interpretacao": {
            "🥇 Gold (≥3.0)": "Excelente qualidade, código maduro",
            "🥈 Silver (2.0-2.9)": "Boa qualidade, dentro do esperado",
            "🥉 Bronze (1.0-1.9)": "Regular, precisa de atenção",
            "⚠️ Risco (<1.0)": "Crítico, requer intervenção imediata"
        },
        "fonte": "Métrica interna NINA baseada em práticas ISTQB"
    },
    "ddp": {
        "titulo": "DDP - Defect Detection Percentage",
        "descricao": "Percentual de defeitos encontrados pelo QA antes da produção. Mede a eficácia do time de testes em filtrar bugs.",
        "formula": "DDP = (Bugs encontrados em QA / Total de Bugs estimados) × 100",
        "interpretacao": {
            "≥85%": "Excelente - QA muito eficaz",
            "70-84%": "Bom - Processo funcionando",
            "50-69%": "Regular - Precisa melhorar",
            "<50%": "Crítico - Muitos bugs escapando para produção"
        },
        "fonte": "ISTQB Foundation Level - Test Metrics"
    },
    "fpy": {
        "titulo": "FPY - First Pass Yield (Rendimento de Primeira Passagem)",
        "descricao": "Percentual de cards aprovados na PRIMEIRA validação, sem nenhum bug. Indica a qualidade do código entregue pelo desenvolvimento.",
        "formula": "FPY = (Cards sem bugs / Total de cards) × 100",
        "interpretacao": {
            "≥80%": "Excelente - Código de alta qualidade",
            "60-79%": "Bom - Dentro do esperado",
            "40-59%": "Regular - Revisar práticas de desenvolvimento",
            "<40%": "Crítico - Alto retrabalho, código instável"
        },
        "fonte": "Six Sigma / Lean Manufacturing adaptado para software"
    },
    "lead_time": {
        "titulo": "Lead Time (Tempo de Ciclo Total)",
        "descricao": "Tempo total desde a criação do card até sua conclusão. Inclui desenvolvimento, code review e validação QA.",
        "formula": "Lead Time = Data de Conclusão - Data de Criação",
        "interpretacao": {
            "≤5 dias": "Fluxo muito ágil",
            "6-10 dias": "Tempo saudável",
            "11-15 dias": "Atenção ao processo",
            ">15 dias": "Investigar gargalos"
        },
        "fonte": "Kanban / Lean Metrics"
    },
    "health_score": {
        "titulo": "Health Score (Saúde da Release)",
        "descricao": "Pontuação composta (0-100) que avalia a saúde geral da release considerando múltiplos fatores de qualidade.",
        "formula": "HS = (Conclusão×30 + DDP×25 + FPY×20 + Gargalos×15 + LeadTime×10) / 100",
        "interpretacao": {
            "≥75": "🟢 Saudável - Release pode seguir",
            "50-74": "🟡 Atenção - Monitorar riscos",
            "25-49": "🟠 Alerta - Ação necessária",
            "<25": "🔴 Crítico - Avaliar adiamento"
        },
        "fonte": "Composite Score baseado em ISTQB Test Process Improvement"
    },
    "throughput": {
        "titulo": "Throughput (Vazão)",
        "descricao": "Quantidade de cards ou Story Points concluídos por período (sprint). Indica a capacidade de entrega do time.",
        "formula": "Throughput = Cards concluídos / Período",
        "interpretacao": {
            "Crescente": "Time ganhando velocidade",
            "Estável": "Capacidade previsível",
            "Decrescente": "Investigar impedimentos"
        },
        "fonte": "Kanban Metrics / Flow Efficiency"
    },
    "wip": {
        "titulo": "WIP - Work In Progress",
        "descricao": "Quantidade de cards em andamento simultaneamente. WIP alto pode indicar gargalos e sobrecarga.",
        "formula": "WIP = Cards não concluídos e não no backlog",
        "interpretacao": {
            "≤ Capacidade": "Fluxo saudável",
            "> Capacidade": "Sobrecarga - Risco de atrasos"
        },
        "fonte": "Kanban / Little's Law"
    },
    "defect_density": {
        "titulo": "Densidade de Defeitos",
        "descricao": "Quantidade de bugs por Story Point. Indica a taxa de defeitos relativa ao tamanho da entrega.",
        "formula": "DD = Total de Bugs / Total de SP",
        "interpretacao": {
            "≤0.2": "Baixa densidade - Excelente",
            "0.21-0.5": "Densidade aceitável",
            "0.51-1.0": "Densidade alta - Atenção",
            ">1.0": "Crítico - Muitos bugs por SP"
        },
        "fonte": "IEEE 982.1 - Software Quality Metrics"
    },
}

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


def mostrar_tooltip(metrica_key: str):
    """Mostra tooltip explicativo de uma métrica."""
    if metrica_key not in TOOLTIPS:
        return
    
    tooltip = TOOLTIPS[metrica_key]
    with st.expander(f"ℹ️ O que é {tooltip['titulo']}?", expanded=False):
        st.markdown(f"**{tooltip['descricao']}**")
        st.code(tooltip['formula'], language="text")
        st.markdown("**Interpretação:**")
        for nivel, desc in tooltip['interpretacao'].items():
            st.markdown(f"- {nivel}: {desc}")
        st.caption(f"📚 Fonte: {tooltip['fonte']}")


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
        
        # MÉTRICAS Ellen/Produto
        criado_na_sprint = False
        if sprint_start and sprint_end:
            criado_na_sprint = sprint_start <= criado <= sprint_end
        
        finalizado_mesma_sprint = False
        if status_cat == 'done' and criado_na_sprint:
            finalizado_mesma_sprint = True
        
        adicionado_fora_periodo = False
        if sprint_start and criado > sprint_start + timedelta(days=2):
            adicionado_fora_periodo = True
        
        # Janela de 3 dias úteis
        dentro_janela = dias_ate_release >= 3
        
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
            'dentro_janela': dentro_janela,
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
            "faltando": df_sem_hotfix[~df_sem_hotfix['sp_preenchido']][['ticket_id', 'titulo', 'desenvolvedor', 'link']].to_dict('records') if total_sem_hotfix > 0 else []
        },
        "bugs": {
            "preenchido": int(df['bugs_preenchido'].sum()),
            "total": total,
            "pct": round(df['bugs_preenchido'].sum() / total * 100, 1),
            "faltando": df[~df['bugs_preenchido']][['ticket_id', 'titulo', 'desenvolvedor', 'link']].to_dict('records')
        },
        "complexidade": {
            "preenchido": int(df['complexidade_preenchida'].sum()),
            "total": total,
            "pct": round(df['complexidade_preenchida'].sum() / total * 100, 1),
            "faltando": df[~df['complexidade_preenchida']][['ticket_id', 'titulo', 'desenvolvedor', 'link']].to_dict('records')
        },
        "qa": {
            "preenchido": int(df['qa_preenchido'].sum()),
            "total": total,
            "pct": round(df['qa_preenchido'].sum() / total * 100, 1),
            "faltando": df[~df['qa_preenchido']][['ticket_id', 'titulo', 'desenvolvedor', 'link']].to_dict('records')
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
        "fila_completa": waiting_qa,
        "em_teste": testing,
    }


def calcular_metricas_produto(df: pd.DataFrame) -> Dict:
    """Calcula métricas específicas por produto (métricas Ellen)."""
    hotfix_por_produto = df[df['tipo'] == 'HOTFIX'].groupby('produto').size().reset_index(name='hotfixes')
    finalizados_mesma_sprint = df[df['finalizado_mesma_sprint'] == True]
    adicionados_fora = df[df['adicionado_fora_periodo'] == True]
    
    return {
        "hotfix_por_produto": hotfix_por_produto,
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


def calcular_metricas_dev(df: pd.DataFrame) -> Dict:
    """Calcula métricas por desenvolvedor."""
    dev_stats = df.groupby('desenvolvedor').agg({
        'ticket_id': 'count',
        'sp': 'sum',
        'bugs': 'sum',
    }).reset_index()
    dev_stats.columns = ['Desenvolvedor', 'Cards', 'SP', 'Bugs']
    dev_stats['FK'] = dev_stats.apply(lambda x: calcular_fator_k(x['SP'], x['Bugs']), axis=1)
    dev_stats['Maturidade'] = dev_stats['FK'].apply(lambda x: classificar_maturidade(x)['selo'])
    
    return {"stats": dev_stats.sort_values('Cards', ascending=False)}


# ==============================================================================
# DADOS DE TENDÊNCIA (HISTÓRICO)
# ==============================================================================

def gerar_dados_tendencia() -> pd.DataFrame:
    """Gera dados históricos para demonstração de tendências."""
    sprints = [f"Release {i}" for i in range(230, 239)]
    
    dados = []
    for i, sprint in enumerate(sprints):
        # Progressão gradual com alguma variação
        base_fk = 1.2 + (i * 0.22) + random.uniform(-0.2, 0.2)
        base_fpy = 40 + (i * 5) + random.uniform(-4, 4)
        base_ddp = 65 + (i * 3.5) + random.uniform(-4, 4)
        base_health = 45 + (i * 5.5) + random.uniform(-6, 6)
        
        dados.append({
            'sprint': sprint,
            'fator_k': round(min(4, max(0.5, base_fk)), 2),
            'fpy': round(min(95, max(25, base_fpy)), 1),
            'ddp': round(min(98, max(45, base_ddp)), 1),
            'health_score': round(min(95, max(20, base_health)), 0),
            'bugs_total': max(3, 35 - (i * 3) + random.randint(-4, 4)),
            'cards_total': random.randint(35, 55),
            'sp_total': random.randint(80, 150),
            'lead_time_medio': round(max(3, 14 - (i * 0.9) + random.uniform(-1, 1)), 1),
            'throughput': random.randint(25, 45),
            'taxa_reprovacao': round(max(2, 25 - (i * 2) + random.uniform(-3, 3)), 1),
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
            df_export = df[['ticket_id', 'titulo', 'tipo', 'status', 'desenvolvedor', 'qa', 
                            'sp', 'bugs', 'sprint', 'produto', 'lead_time']].copy()
            df_export.to_excel(writer, sheet_name='Cards', index=False)
            
            metricas_df = pd.DataFrame([
                {'Métrica': 'Total de Cards', 'Valor': len(df)},
                {'Métrica': 'Story Points Total', 'Valor': int(df['sp'].sum())},
                {'Métrica': 'Bugs Encontrados', 'Valor': int(df['bugs'].sum())},
                {'Métrica': 'Cards Concluídos', 'Valor': len(df[df['status_cat'] == 'done'])},
                {'Métrica': 'Health Score', 'Valor': metricas.get('health_score', 'N/A')},
            ])
            metricas_df.to_excel(writer, sheet_name='Métricas', index=False)
            
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
    /* Header Nina - Fundo escuro para contrastar com logo vermelha */
    .nina-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white;
        padding: 20px 25px;
        border-radius: 12px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 20px;
        border: 1px solid #334155;
    }
    .nina-logo {
        width: 60px;
        height: 60px;
        flex-shrink: 0;
    }
    .nina-logo svg {
        width: 100%;
        height: 100%;
    }
    .nina-title {
        font-size: 24px;
        font-weight: bold;
        margin: 0;
        color: #f8fafc;
    }
    .nina-subtitle {
        font-size: 14px;
        opacity: 0.85;
        margin: 5px 0 0 0;
        color: #cbd5e1;
    }
    .nina-highlight {
        color: #AF0C37;
        font-weight: bold;
    }
    
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
    
    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, rgba(99, 102, 241, 0.1), transparent);
        padding: 10px 15px;
        border-radius: 8px;
        margin: 20px 0 10px 0;
        border-left: 4px solid #6366f1;
    }
    
    /* Hide Streamlit elements */
    #MainMenu, .stDeployButton { display: none !important; }
    </style>
    """, unsafe_allow_html=True)


# ==============================================================================
# COMPONENTES UI
# ==============================================================================

def mostrar_header_nina():
    """Mostra header principal com logo SVG da Nina."""
    # Logo SVG da Nina (vermelho #AF0C37)
    logo_svg = '''<svg width="60" height="60" viewBox="0 0 187 187" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M173.709 89.2107C172.209 86.6048 169.414 84.838 166.225 84.838C163.036 84.838 160.241 86.5649 158.741 89.1627H151.683C149.465 58.8237 124.495 35 94.0216 35C63.5489 35 38.5862 58.8237 36.3678 89.1627H29.1759C27.6759 86.5649 24.8734 84.798 21.6682 84.798C18.463 84.798 15.6605 86.5806 14.1605 89.2031C13.4184 90.4899 13 92.001 13 93.6C13 95.1987 13.4184 96.7017 14.1605 97.997C15.6605 100.619 18.463 102.306 21.6682 102.306C24.8734 102.306 27.6838 100.435 29.1759 97.8369H36.3678C38.5862 128.168 63.5489 152 94.0216 152C124.495 152 149.465 128.176 151.675 97.8369H158.686C160.178 100.435 162.996 102.354 166.217 102.354C169.438 102.354 172.256 100.611 173.749 97.9648C174.475 96.6856 174.885 95.2148 174.885 93.6319C174.885 92.049 174.451 90.5222 173.701 89.2188L173.709 89.2107ZM111.145 125.554C107.971 131.518 101.758 135.459 94.5981 135.459C87.4374 135.459 81.2248 131.566 78.0509 125.602C77.1666 123.947 78.3667 122.092 80.2219 122.092H108.982C110.837 122.092 112.029 123.891 111.153 125.554H111.145ZM140.528 94.1277C140.528 103.825 132.76 111.691 123.184 111.691H65.4432C55.8675 111.691 48.0991 103.825 48.0991 94.1277V93.7199C48.0991 84.0223 55.8675 76.1557 65.4432 76.1557H123.184C132.76 76.1557 140.528 84.0223 140.528 93.7199V94.1277Z" fill="#AF0C37"/>
    <path d="M76.5809 105.311C82.9686 105.311 88.1466 100.068 88.1466 93.5996C88.1466 87.1312 82.9686 81.8875 76.5809 81.8875C70.1936 81.8875 65.0156 87.1312 65.0156 93.5996C65.0156 100.068 70.1936 105.311 76.5809 105.311Z" fill="#AF0C37"/>
    <path d="M111.437 105.311C117.824 105.311 123.002 100.068 123.002 93.5996C123.002 87.1312 117.824 81.8875 111.437 81.8875C105.049 81.8875 99.8712 87.1312 99.8712 93.5996C99.8712 100.068 105.049 105.311 111.437 105.311Z" fill="#AF0C37"/>
    </svg>'''
    
    st.markdown(f"""
    <div class="nina-header">
        <div class="nina-logo">{logo_svg}</div>
        <div>
            <p class="nina-title"><span class="nina-highlight">NinaDash</span> — Dashboard de Inteligência e Métricas de QA</p>
            <p class="nina-subtitle">📊 Transformando dados em decisões: visibilidade de qualidade, gargalos e maturidade do time</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


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


def mostrar_card_ticket(row: dict, compacto: bool = False):
    """Mostra card de ticket COM LINK para Jira."""
    bugs = row.get('bugs', 0)
    risco = 'high' if bugs >= 3 else 'medium' if bugs >= 1 else 'low'
    link = row.get('link', link_jira(row.get('ticket_id', '')))
    
    titulo = str(row.get('titulo', ''))[:60] + ('...' if len(str(row.get('titulo', ''))) > 60 else '')
    
    if compacto:
        st.markdown(f"""
        <div class="ticket-card ticket-risk-{risco}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <a href="{link}" target="_blank" style="color: #6366f1; font-weight: bold; text-decoration: none;">🔗 {row.get('ticket_id', '')}</a>
                <span style="opacity: 0.7;">{row.get('sp', 0)} SP | 🐛 {bugs}</span>
            </div>
            <p style="margin: 5px 0 0 0; font-size: 13px; opacity: 0.9;">{titulo}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="ticket-card ticket-risk-{risco}">
            <div style="display: flex; justify-content: space-between;">
                <a href="{link}" target="_blank" style="color: #6366f1; font-weight: bold; text-decoration: none;">🔗 {row.get('ticket_id', '')}</a>
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


def mostrar_lista_tickets_completa(items: list, titulo: str, mostrar_todos: bool = False):
    """Mostra lista de tickets com opção de ver TODOS."""
    if not items:
        st.info(f"Nenhum card em: {titulo}")
        return
    
    total = len(items)
    
    with st.expander(f"📋 {titulo} ({total} cards)", expanded=False):
        # Checkbox para mostrar todos
        if total > 5:
            mostrar_todos = st.checkbox(f"Mostrar todos os {total} cards", key=f"mostrar_todos_{titulo}", value=mostrar_todos)
        else:
            mostrar_todos = True
        
        limite = total if mostrar_todos else min(5, total)
        
        for i, item in enumerate(items[:limite]):
            if isinstance(item, dict):
                mostrar_card_ticket(item, compacto=True)
            elif isinstance(item, pd.Series):
                mostrar_card_ticket(item.to_dict(), compacto=True)
        
        if not mostrar_todos and total > 5:
            st.caption(f"📌 Mais {total - 5} cards ocultos. Marque acima para ver todos.")


def mostrar_lista_df_completa(df: pd.DataFrame, titulo: str):
    """Mostra lista de tickets de um DataFrame com opção de ver todos."""
    if df.empty:
        st.info(f"Nenhum card em: {titulo}")
        return
    
    items = df.to_dict('records')
    mostrar_lista_tickets_completa(items, titulo)


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
    
    # Faixas de maturidade
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
    fig.add_hline(y=85, line_dash="dot", line_color="#3b82f6", annotation_text="Meta DDP (85%)")
    
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


def criar_grafico_tendencia_health(df_tendencia: pd.DataFrame) -> go.Figure:
    """Cria gráfico de tendência do Health Score."""
    fig = go.Figure()
    
    colors = ['#22c55e' if h >= 75 else '#eab308' if h >= 50 else '#f97316' if h >= 25 else '#ef4444' 
              for h in df_tendencia['health_score']]
    
    fig.add_trace(go.Bar(
        x=df_tendencia['sprint'], y=df_tendencia['health_score'],
        marker_color=colors,
        text=df_tendencia['health_score'].astype(int), textposition='outside'
    ))
    
    fig.add_hline(y=75, line_dash="dash", line_color="#22c55e", annotation_text="Saudável (≥75)")
    fig.add_hline(y=50, line_dash="dash", line_color="#eab308", annotation_text="Atenção (≥50)")
    
    fig.update_layout(
        title="🏥 Evolução do Health Score",
        xaxis_title="Sprint", yaxis_title="Health Score",
        template='plotly_white', height=350
    )
    return fig


def criar_grafico_throughput(df_tendencia: pd.DataFrame) -> go.Figure:
    """Cria gráfico de throughput."""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_tendencia['sprint'], y=df_tendencia['throughput'],
        name='Cards Entregues', marker_color='#3b82f6',
        text=df_tendencia['throughput'], textposition='outside'
    ))
    
    fig.add_trace(go.Scatter(
        x=df_tendencia['sprint'], y=df_tendencia['sp_total'],
        mode='lines+markers', name='SP Total',
        line=dict(color='#8b5cf6', width=2), yaxis='y2'
    ))
    
    fig.update_layout(
        title="📦 Throughput por Sprint",
        xaxis_title="Sprint",
        yaxis=dict(title="Cards", side='left'),
        yaxis2=dict(title="Story Points", side='right', overlaying='y'),
        template='plotly_white', height=350,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def criar_grafico_lead_time(df_tendencia: pd.DataFrame) -> go.Figure:
    """Cria gráfico de lead time."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_tendencia['sprint'], y=df_tendencia['lead_time_medio'],
        mode='lines+markers+text', name='Lead Time Médio',
        line=dict(color='#f59e0b', width=3), marker=dict(size=10),
        text=df_tendencia['lead_time_medio'].apply(lambda x: f"{x:.1f}d"),
        textposition='top center'
    ))
    
    fig.add_hline(y=7, line_dash="dash", line_color="#22c55e", annotation_text="Meta (≤7 dias)")
    
    fig.update_layout(
        title="⏱️ Lead Time Médio por Sprint",
        xaxis_title="Sprint", yaxis_title="Dias",
        template='plotly_white', height=350
    )
    return fig


def criar_grafico_reprovacao(df_tendencia: pd.DataFrame) -> go.Figure:
    """Cria gráfico de taxa de reprovação."""
    fig = go.Figure()
    
    colors = ['#ef4444' if r > 15 else '#f97316' if r > 10 else '#22c55e' 
              for r in df_tendencia['taxa_reprovacao']]
    
    fig.add_trace(go.Bar(
        x=df_tendencia['sprint'], y=df_tendencia['taxa_reprovacao'],
        marker_color=colors,
        text=df_tendencia['taxa_reprovacao'].apply(lambda x: f"{x:.0f}%"), textposition='outside'
    ))
    
    fig.add_hline(y=10, line_dash="dash", line_color="#22c55e", annotation_text="Meta (≤10%)")
    
    fig.update_layout(
        title="❌ Taxa de Reprovação por Sprint",
        xaxis_title="Sprint", yaxis_title="% Reprovados",
        template='plotly_white', height=350
    )
    return fig


def criar_grafico_estagio_por_produto(df: pd.DataFrame) -> go.Figure:
    """Cria gráfico de estágio por produto."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="Sem dados", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
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
        if st.button("🔄 Atualizar Dados", type="secondary"):
            st.cache_data.clear()
            st.rerun()
    
    # Sprint info
    sprint_atual = df['sprint'].mode().iloc[0] if not df.empty else "Sem Sprint"
    dias_release = df['dias_ate_release'].max() if 'dias_ate_release' in df.columns else 0
    
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #AF0C37, #8B0A2C); color: white; padding: 15px 20px; border-radius: 10px; margin-bottom: 20px;">
        <span style="font-size: 18px; font-weight: bold;">🚀 {sprint_atual}</span>
        <span style="float: right;">📅 {dias_release} dias até a release</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Alertas de governança
    gov = calcular_metricas_governanca(df)
    if gov['sp']['pct'] < 50:
        st.markdown(f"""
        <div class="alert-critical">
            <b>⚠️ ALERTA: Apenas {gov['sp']['pct']:.0f}% dos cards têm Story Points preenchidos!</b>
            <p>Isso impacta diretamente nas métricas de capacidade, qualidade e decisões de release.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # KPIs principais COM TOOLTIPS
    with st.expander("📈 KPIs Principais da Sprint", expanded=True):
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
            criar_card_metrica(str(bugs_total), "Bugs Encontrados", cor)
        
        with col5:
            fk = calcular_fator_k(sp_total, bugs_total)
            mat = classificar_maturidade(fk)
            cor_map = {'#22c55e': 'green', '#eab308': 'yellow', '#f97316': 'orange', '#ef4444': 'red'}
            criar_card_metrica(f"{fk:.1f}", f"Fator K {mat['emoji']}", cor_map.get(mat['cor'], 'blue'), mat['selo'])
        
        # Tooltip do Fator K
        mostrar_tooltip("fator_k")
    
    # Métricas de Qualidade COM TOOLTIPS
    with st.expander("🎯 Métricas de Qualidade", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        fpy = calcular_fpy(df)
        ddp = calcular_ddp(df)
        lead = calcular_lead_time(df)
        health = calcular_health_score(df)
        
        with col1:
            cor = 'green' if fpy['valor'] >= 80 else 'yellow' if fpy['valor'] >= 60 else 'red'
            criar_card_metrica(f"{fpy['valor']:.0f}%", "FPY", cor, f"{fpy['sem_bugs']}/{fpy['total']} sem bugs")
        
        with col2:
            cor = 'green' if ddp['valor'] >= 85 else 'yellow' if ddp['valor'] >= 70 else 'red'
            criar_card_metrica(f"{ddp['valor']:.0f}%", "DDP", cor, f"{ddp['bugs_qa']} bugs detectados")
        
        with col3:
            cor = 'green' if lead['medio'] <= 7 else 'yellow' if lead['medio'] <= 14 else 'red'
            criar_card_metrica(f"{lead['medio']:.1f}d", "Lead Time", cor, f"P85: {lead['p85']}d")
        
        with col4:
            cor = 'green' if health['score'] >= 75 else 'yellow' if health['score'] >= 50 else 'red'
            criar_card_metrica(f"{health['score']:.0f}", "Health Score", cor, health['status'])
        
        # Tooltips das métricas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            mostrar_tooltip("fpy")
        with col2:
            mostrar_tooltip("ddp")
        with col3:
            mostrar_tooltip("lead_time")
        with col4:
            mostrar_tooltip("health_score")
    
    # Distribuição por status COM LISTAGEM COMPLETA
    with st.expander("📋 Cards por Status", expanded=True):
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
                
                # Listagem COMPLETA
                df_status = df[df['status_cat'] == status]
                if not df_status.empty:
                    mostrar_lista_df_completa(df_status, nome)
    
    # Gráficos
    with st.expander("📊 Gráficos de Distribuição", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            tipo_count = df['tipo'].value_counts().reset_index()
            tipo_count.columns = ['tipo', 'count']
            
            fig = px.pie(tipo_count, values='count', names='tipo', title='Distribuição por Tipo',
                         color='tipo', color_discrete_map={'TAREFA': '#3b82f6', 'BUG': '#ef4444', 'HOTFIX': '#f59e0b', 'SUGESTÃO': '#8b5cf6'},
                         hole=0.4)
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            prod_count = df['produto'].value_counts().reset_index()
            prod_count.columns = ['produto', 'count']
            
            fig = px.bar(prod_count.head(6), x='produto', y='count', title='Cards por Produto',
                         color='count', color_continuous_scale='Blues')
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)


def aba_qa(df: pd.DataFrame):
    """Aba de QA (análise de validação e gargalos)."""
    st.markdown("### 🔬 Análise de QA")
    st.caption("Monitore o funil de validação, identifique gargalos e acompanhe a carga do time de QA")
    
    metricas_qa = calcular_metricas_qa(df)
    
    # KPIs de QA
    with st.expander("📊 Indicadores de QA", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_fila = metricas_qa['funil']['waiting_qa'] + metricas_qa['funil']['testing']
            cor = 'green' if total_fila < 5 else 'yellow' if total_fila < 10 else 'red'
            criar_card_metrica(str(total_fila), "Fila de QA", cor, f"({metricas_qa['funil']['waiting_qa']} aguardando)")
        
        with col2:
            tempo = metricas_qa['tempo']['waiting']
            cor = 'green' if tempo < 2 else 'yellow' if tempo < 5 else 'red'
            criar_card_metrica(f"{tempo:.1f}d", "Tempo Médio na Fila", cor)
        
        with col3:
            aging = metricas_qa['aging']['total']
            cor = 'green' if aging == 0 else 'yellow' if aging < 3 else 'red'
            criar_card_metrica(str(aging), f"Cards Aging (>{REGRAS['dias_aging_alerta']}d)", cor)
        
        with col4:
            taxa = metricas_qa['taxa_reprovacao']
            cor = 'green' if taxa < 10 else 'yellow' if taxa < 20 else 'red'
            criar_card_metrica(f"{taxa:.0f}%", "Taxa de Reprovação", cor)
    
    # Funil e Carga
    with st.expander("📈 Funil de Validação e Carga por QA", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            fig = criar_grafico_funil_qa(metricas_qa)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
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
    
    # Cards com aging - COM LISTAGEM COMPLETA
    with st.expander("⏰ Cards Envelhecidos (Aging)", expanded=False):
        aging_waiting = metricas_qa['aging']['waiting']
        aging_testing = metricas_qa['aging']['testing']
        
        if not aging_waiting.empty or not aging_testing.empty:
            st.markdown(f"""
            <div class="alert-warning">
                <b>⚠️ {metricas_qa['aging']['total']} card(s) estão há mais de {REGRAS['dias_aging_alerta']} dias no mesmo status!</b>
            </div>
            """, unsafe_allow_html=True)
            
            if not aging_waiting.empty:
                mostrar_lista_df_completa(aging_waiting, "Aging - Aguardando QA")
            
            if not aging_testing.empty:
                mostrar_lista_df_completa(aging_testing, "Aging - Em Validação")
        else:
            st.success("✅ Nenhum card envelhecido! Fluxo de QA saudável.")
    
    # Fila completa COM LISTAGEM COMPLETA
    with st.expander("📋 Fila Completa - Aguardando Validação", expanded=False):
        fila_qa = df[df['status_cat'] == 'waiting_qa'].sort_values('dias_em_status', ascending=False)
        mostrar_lista_df_completa(fila_qa, "Aguardando QA")
    
    # Em validação COM LISTAGEM COMPLETA
    with st.expander("🧪 Em Validação", expanded=False):
        em_teste = df[df['status_cat'] == 'testing'].sort_values('dias_em_status', ascending=False)
        mostrar_lista_df_completa(em_teste, "Em Validação")


def aba_governanca(df: pd.DataFrame):
    """Aba de Governança de Dados."""
    st.markdown("### 📋 Governança de Dados")
    st.caption("Monitore o preenchimento dos campos obrigatórios para garantir métricas confiáveis")
    
    gov = calcular_metricas_governanca(df)
    
    media_preenchimento = (gov['sp']['pct'] + gov['bugs']['pct'] + gov['complexidade']['pct'] + gov['qa']['pct']) / 4
    
    # Alerta geral
    with st.expander("📊 Status Geral da Governança", expanded=True):
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
                <p>Alguns campos precisam de atenção para melhorar a qualidade das métricas.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-success">
                <b>✅ Dados em boa qualidade!</b>
                <p>Os campos obrigatórios estão bem preenchidos.</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.metric("Média de Preenchimento", f"{media_preenchimento:.0f}%")
    
    # Campos obrigatórios - COM LISTAGEM COMPLETA
    campos = [
        ("Story Points", gov['sp'], "Obrigatório para todos os cards (exceto Hotfix que assume 2 SP por padrão)"),
        ("Bugs Encontrados", gov['bugs'], "Preencher após validação - essencial para métricas de qualidade"),
        ("Complexidade de Teste", gov['complexidade'], "Meta futura - ajuda a balancear carga de QA"),
        ("QA Responsável", gov['qa'], "Obrigatório - indica quem está validando"),
    ]
    
    for nome, dados, obs in campos:
        with st.expander(f"📌 {nome} - {dados['pct']:.0f}% preenchido ({dados['preenchido']}/{dados['total']})", expanded=False):
            cor = '#22c55e' if dados['pct'] >= 80 else '#f59e0b' if dados['pct'] >= 50 else '#ef4444'
            
            st.markdown(f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width: {dados['pct']}%; background: {cor};">
                    {dados['pct']:.0f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.caption(obs)
            
            # Listagem COMPLETA dos faltando
            if dados['faltando']:
                mostrar_lista_tickets_completa(dados['faltando'], f"Cards sem {nome}")
            else:
                st.success(f"✅ Todos os cards têm {nome} preenchido!")
    
    # Exportar lista para cobrança
    with st.expander("📥 Exportar Listas para Cobrança", expanded=False):
        if gov['sp']['faltando']:
            df_export = pd.DataFrame(gov['sp']['faltando'])
            csv = df_export.to_csv(index=False)
            st.download_button("📥 Baixar cards sem Story Points", csv, "cards_sem_sp.csv", "text/csv")
        
        if gov['bugs']['faltando']:
            df_export = pd.DataFrame(gov['bugs']['faltando'])
            csv = df_export.to_csv(index=False)
            st.download_button("📥 Baixar cards sem Bugs preenchido", csv, "cards_sem_bugs.csv", "text/csv")


def aba_produto(df: pd.DataFrame):
    """Aba de métricas por Produto (métricas Ellen)."""
    st.markdown("### 📦 Métricas por Produto")
    st.caption("Visualize métricas segmentadas por produto - inclui métricas de fluxo da sprint")
    
    metricas_prod = calcular_metricas_produto(df)
    
    # KPIs novas métricas Ellen
    with st.expander("🎯 Indicadores de Fluxo da Sprint", expanded=True):
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
            criar_card_metrica(str(total_fora), "Cards Adicionados Fora do Período", cor, "Adicionados após início da sprint")
        
        with col3:
            total_hotfix = len(df[df['tipo'] == 'HOTFIX'])
            cor = 'green' if total_hotfix < 5 else 'yellow' if total_hotfix < 10 else 'red'
            criar_card_metrica(str(total_hotfix), "Total de Hotfixes", cor)
        
        st.caption("💡 **Dica:** Cards adicionados fora do período comprometem o planejamento da sprint")
    
    # Cards adicionados fora do período - COM LISTAGEM COMPLETA
    with st.expander("⚠️ Cards Adicionados Fora do Período", expanded=False):
        if not metricas_prod['adicionados_fora'].empty:
            st.markdown("""
            <div class="alert-warning">
                <b>Estes cards foram adicionados após o início da sprint</b>
                <p>Isso pode indicar escopo não planejado ou emergências.</p>
            </div>
            """, unsafe_allow_html=True)
            mostrar_lista_df_completa(metricas_prod['adicionados_fora'], "Cards Fora do Período")
        else:
            st.success("✅ Nenhum card foi adicionado fora do período!")
    
    # Gráficos
    with st.expander("📊 Visualizações por Produto", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            fig = criar_grafico_hotfix_por_produto(df)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = criar_grafico_estagio_por_produto(df)
            st.plotly_chart(fig, use_container_width=True)
    
    # Tabela resumo por produto
    with st.expander("📋 Resumo por Produto", expanded=True):
        produto_stats = df.groupby('produto').agg({
            'ticket_id': 'count',
            'sp': 'sum',
            'bugs': 'sum',
        }).reset_index()
        produto_stats.columns = ['produto', 'Cards', 'SP', 'Bugs']
        produto_stats['FK'] = produto_stats.apply(lambda x: calcular_fator_k(x['SP'], x['Bugs']), axis=1)
        
        hotfix_count = df[df['tipo'] == 'HOTFIX'].groupby('produto').size().reset_index(name='Hotfixes')
        produto_stats = produto_stats.merge(hotfix_count, on='produto', how='left').fillna(0)
        produto_stats['Hotfixes'] = produto_stats['Hotfixes'].astype(int)
        produto_stats = produto_stats.rename(columns={'produto': 'Produto'})
        
        st.dataframe(produto_stats.sort_values('Cards', ascending=False), hide_index=True, use_container_width=True)


def aba_historico(df: pd.DataFrame):
    """Aba de Histórico/Tendências - ENRIQUECIDA."""
    st.markdown("### 📈 Histórico e Tendências")
    st.caption("Visualize a evolução das métricas ao longo das sprints. *Dados demonstrativos para visualização do potencial da ferramenta.*")
    
    df_tendencia = gerar_dados_tendencia()
    
    # Insights automáticos
    with st.expander("💡 Insights Automáticos", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        ultimo_fk = df_tendencia['fator_k'].iloc[-1]
        primeiro_fk = df_tendencia['fator_k'].iloc[0]
        variacao_fk = ((ultimo_fk - primeiro_fk) / primeiro_fk) * 100 if primeiro_fk > 0 else 0
        
        with col1:
            if variacao_fk > 0:
                st.markdown(f"""
                <div class="alert-success">
                    <b>📈 Fator K em crescimento</b>
                    <p>+{variacao_fk:.1f}% nas últimas sprints</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="alert-warning">
                    <b>📉 Fator K em queda</b>
                    <p>{variacao_fk:.1f}% nas últimas sprints</p>
                </div>
                """, unsafe_allow_html=True)
        
        ultimo_fpy = df_tendencia['fpy'].iloc[-1]
        with col2:
            if ultimo_fpy >= 80:
                st.markdown(f"""
                <div class="alert-success">
                    <b>✅ FPY acima da meta</b>
                    <p>{ultimo_fpy:.1f}% (meta: 80%)</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="alert-info">
                    <b>ℹ️ FPY abaixo da meta</b>
                    <p>{ultimo_fpy:.1f}% ({80 - ultimo_fpy:.1f}% abaixo)</p>
                </div>
                """, unsafe_allow_html=True)
        
        ultimo_lead = df_tendencia['lead_time_medio'].iloc[-1]
        with col3:
            if ultimo_lead <= 7:
                st.markdown(f"""
                <div class="alert-success">
                    <b>⚡ Lead Time saudável</b>
                    <p>{ultimo_lead:.1f} dias (meta: ≤7)</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="alert-warning">
                    <b>⏱️ Lead Time alto</b>
                    <p>{ultimo_lead:.1f} dias (meta: ≤7)</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Gráficos de evolução
    with st.expander("🏆 Evolução do Fator K (Maturidade)", expanded=True):
        fig = criar_grafico_tendencia_fator_k(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
        mostrar_tooltip("fator_k")
    
    with st.expander("📊 Evolução de Qualidade (FPY e DDP)", expanded=True):
        fig = criar_grafico_tendencia_qualidade(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            mostrar_tooltip("fpy")
        with col2:
            mostrar_tooltip("ddp")
    
    with st.expander("🐛 Evolução de Bugs", expanded=False):
        fig = criar_grafico_tendencia_bugs(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("🏥 Evolução do Health Score", expanded=False):
        fig = criar_grafico_tendencia_health(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
        mostrar_tooltip("health_score")
    
    with st.expander("📦 Throughput (Vazão de Entrega)", expanded=False):
        fig = criar_grafico_throughput(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
        mostrar_tooltip("throughput")
    
    with st.expander("⏱️ Lead Time Médio", expanded=False):
        fig = criar_grafico_lead_time(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
        mostrar_tooltip("lead_time")
    
    with st.expander("❌ Taxa de Reprovação", expanded=False):
        fig = criar_grafico_reprovacao(df_tendencia)
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabela de dados históricos
    with st.expander("📋 Dados Históricos Completos", expanded=False):
        st.dataframe(df_tendencia, hide_index=True, use_container_width=True)


def aba_lideranca(df: pd.DataFrame):
    """Aba de Liderança com decisões estratégicas."""
    st.markdown("### 🎯 Painel de Liderança")
    st.caption("Visão executiva para tomada de decisão - Go/No-Go de release")
    
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
        decisao_msg = "Cards bloqueados ou taxa de conclusão muito baixa - avaliar riscos"
    elif pct_conclusao < 50 and dias_release < 3:
        decisao = "⚠️ REVISAR ESCOPO"
        decisao_cor = "yellow"
        decisao_msg = "Pouco tempo e muitos cards pendentes - considerar redução de escopo"
    else:
        decisao = "✅ NO CAMINHO"
        decisao_cor = "green"
        decisao_msg = "Sprint progredindo conforme esperado"
    
    # Layout
    with st.expander("🚦 Decisão de Release (Go/No-Go)", expanded=True):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"""
            <div class="status-card status-{decisao_cor}" style="padding: 25px;">
                <p style="font-size: 24px; margin: 0;">{decisao}</p>
                <p class="card-label" style="margin-top: 10px;">{decisao_msg}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            cor_health = 'green' if health['score'] >= 75 else 'yellow' if health['score'] >= 50 else 'red'
            criar_card_metrica(f"{health['score']:.0f}", "Health Score", cor_health, health['status'])
        
        with col2:
            col_a, col_b, col_c, col_d = st.columns(4)
            
            with col_a:
                st.metric("Cards", total_cards)
            with col_b:
                st.metric("Concluídos", f"{pct_conclusao:.0f}%")
            with col_c:
                st.metric("Fator K", f"{fk:.1f}", mat['selo'])
            with col_d:
                st.metric("Dias até Release", dias_release)
            
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
        
        mostrar_tooltip("health_score")
    
    # Pontos de atenção COM LISTAGEM COMPLETA
    with st.expander("🚨 Pontos de Atenção", expanded=True):
        # Cards bloqueados
        bloqueados_df = df[df['status_cat'].isin(['blocked', 'rejected'])]
        if not bloqueados_df.empty:
            st.markdown(f"""
            <div class="alert-critical">
                <b>🚫 {len(bloqueados_df)} card(s) bloqueado(s)/reprovado(s)</b>
            </div>
            """, unsafe_allow_html=True)
            mostrar_lista_df_completa(bloqueados_df, "Cards Bloqueados/Reprovados")
        
        # Alta prioridade não concluídos
        alta_prio = df[(df['prioridade'].isin(['Alta', 'Muito Alta', 'Muito alto', 'Alto', 'Highest', 'High'])) & (df['status_cat'] != 'done')]
        if not alta_prio.empty:
            st.markdown(f"""
            <div class="alert-warning">
                <b>⚠️ {len(alta_prio)} card(s) de alta prioridade em andamento</b>
            </div>
            """, unsafe_allow_html=True)
            mostrar_lista_df_completa(alta_prio, "Alta Prioridade Pendentes")
        
        # Fora da janela de 3 dias
        fora_janela = df[(~df['dentro_janela']) & (df['status_cat'] != 'done')]
        if not fora_janela.empty:
            st.markdown(f"""
            <div class="alert-info">
                <b>ℹ️ {len(fora_janela)} card(s) fora da janela de 3 dias úteis</b>
            </div>
            """, unsafe_allow_html=True)
            mostrar_lista_df_completa(fora_janela, "Fora da Janela de Release")
        
        if bloqueados_df.empty and alta_prio.empty and fora_janela.empty:
            st.success("✅ Nenhum ponto crítico identificado!")
    
    # Performance por Desenvolvedor
    with st.expander("👨‍💻 Performance por Desenvolvedor", expanded=False):
        dev_metricas = calcular_metricas_dev(df)
        st.dataframe(dev_metricas['stats'], hide_index=True, use_container_width=True)
    
    # Exportação
    with st.expander("📥 Exportar Dados", expanded=False):
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
                st.info("Instale openpyxl para exportar Excel: pip install openpyxl")


def aba_sobre():
    """Aba Sobre - Objetivo do Dashboard e Fontes das Métricas."""
    st.markdown("### ℹ️ Sobre o NinaDash")
    st.caption("Objetivo, métricas utilizadas e referências teóricas")
    
    # Sobre a NINA
    with st.expander("🤖 NINA Tecnologia", expanded=True):
        st.markdown("""
        <div style="background: linear-gradient(135deg, #AF0C37 0%, #8B0A2C 100%); padding: 24px; border-radius: 12px; margin-bottom: 16px;">
            <h3 style="margin: 0 0 12px 0; color: #ffffff;">🤖 NINA Tecnologia</h3>
            <p style="margin: 0 0 16px 0; color: #fecdd3; font-size: 15px; line-height: 1.6;">
                A <b style="color: #fff;">NINA</b> é uma empresa de tecnologia especializada em <b style="color: #fff;">soluções digitais inovadoras</b>, 
                com foco em desenvolvimento de software de alta qualidade. Nossa missão é transformar ideias em produtos 
                digitais que geram valor real para nossos clientes.
            </p>
            <div style="display: flex; gap: 16px; flex-wrap: wrap;">
                <div style="background: rgba(255,255,255,0.15); padding: 12px 16px; border-radius: 8px; flex: 1; min-width: 200px;">
                    <p style="margin: 0; color: #fecdd3; font-size: 12px;">🎯 MISSÃO</p>
                    <p style="margin: 4px 0 0 0; color: #fff; font-size: 14px; font-weight: 500;">Entregar software de qualidade com excelência operacional</p>
                </div>
                <div style="background: rgba(255,255,255,0.15); padding: 12px 16px; border-radius: 8px; flex: 1; min-width: 200px;">
                    <p style="margin: 0; color: #fecdd3; font-size: 12px;">👁️ VISÃO</p>
                    <p style="margin: 4px 0 0 0; color: #fff; font-size: 14px; font-weight: 500;">Ser referência em qualidade de software no Brasil</p>
                </div>
                <div style="background: rgba(255,255,255,0.15); padding: 12px 16px; border-radius: 8px; flex: 1; min-width: 200px;">
                    <p style="margin: 0; color: #fecdd3; font-size: 12px;">💎 VALORES</p>
                    <p style="margin: 4px 0 0 0; color: #fff; font-size: 14px; font-weight: 500;">Qualidade, Transparência, Inovação</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Objetivo do Dashboard
    with st.expander("🎯 Objetivo do Dashboard", expanded=True):
        st.markdown("""
        ### 📊 NinaDash — Dashboard de Inteligência e Métricas de QA
        
        **Propósito central:** Transformar o QA de um processo sem visibilidade em um **sistema de inteligência operacional baseado em dados**.
        
        ---
        
        #### 🚨 Problema que resolve
        
        | Antes do NinaDash | Depois do NinaDash |
        |---|---|
        | ❌ Falta de mensuração real do tempo de validação | ✅ Coleta automatizada de métricas |
        | ❌ Zero previsibilidade de entregas | ✅ Cálculo em tempo real de SLAs |
        | ❌ Uso do Notion como controle manual | ✅ Integração direta com Jira |
        | ❌ Falta de segurança na validação de cards | ✅ Monitoramento da janela de release (3 dias úteis) |
        | ❌ Decisões baseadas em "feeling" | ✅ Decisão orientada por dados |
        
        ---
        
        #### ⚡ Diferencial
        
        | Dashboards Comuns | NinaDash |
        |---|---|
        | Métricas genéricas | Métricas baseadas em QA (ISTQB) |
        | Dados estáticos | Integração em tempo real |
        | Foco em volume | Foco em **qualidade e maturidade** |
        | Sem contexto de QA | Janela de release com dias úteis |
        | Métricas isoladas | Health Score para decisão Go/No-Go |
        """)
    
    # Métricas implementadas
    with st.expander("📊 Métricas Implementadas (ISTQB-Aligned)", expanded=True):
        st.markdown("""
        O dashboard implementa métricas fundamentais do **ISTQB Foundation Level**, fornecendo uma visão completa do ciclo de qualidade:
        
        | Métrica | Descrição | Impacto |
        |---------|-----------|---------|
        | **FPY (First Pass Yield)** | Cards aprovados de primeira sem bugs | Mede eficiência do desenvolvimento |
        | **DDP (Defect Detection Percentage)** | Eficácia do QA em encontrar bugs | Indica maturidade do processo de testes |
        | **Fator K** | Relação SP/Bugs (SP/(Bugs+1)) | Classifica maturidade individual |
        | **Lead Time** | Tempo do início ao fim do card | Identifica gargalos no fluxo |
        | **Health Score** | Score composto de saúde da release | Suporta decisão Go/No-Go |
        | **WIP (Work In Progress)** | Cards simultâneos por pessoa | Controla sobrecarga |
        | **Throughput** | Vazão de entrega por sprint | Indica capacidade do time |
        """)
    
    # Fórmulas
    with st.expander("🧮 Fórmulas Principais", expanded=False):
        st.markdown("""
        ### Fator K (Maturidade)
        ```
        FK = SP / (Bugs + 1)
        ```
        - **🥇 Gold (≥3.0):** Excelente qualidade
        - **🥈 Silver (2.0-2.9):** Boa qualidade
        - **🥉 Bronze (1.0-1.9):** Regular
        - **⚠️ Risco (<1.0):** Crítico
        
        ---
        
        ### Health Score (Saúde da Release)
        ```
        HS = (Conclusão×30 + DDP×25 + FPY×20 + Gargalos×15 + LeadTime×10) / 100
        ```
        - **🟢 ≥75:** Saudável - Release pode seguir
        - **🟡 50-74:** Atenção - Monitorar riscos
        - **🟠 25-49:** Alerta - Ação necessária
        - **🔴 <25:** Crítico - Avaliar adiamento
        
        ---
        
        ### First Pass Yield (FPY)
        ```
        FPY = (Cards sem bugs / Total de cards) × 100
        ```
        
        ### Defect Detection Percentage (DDP)
        ```
        DDP = (Bugs encontrados em QA / Total estimado de bugs) × 100
        ```
        
        ### Janela de Release
        ```
        ≥ 3 dias úteis antes da release = Dentro da janela ✅
        ```
        """)
    
    # Fundamentos Teóricos
    with st.expander("📚 Fundamentos Teóricos", expanded=False):
        st.markdown("""
        ### 🎓 ISTQB/CTFL - International Software Testing Qualifications Board
        
        O **ISTQB Foundation Level (CTFL)** define padrões globais para métricas de teste:
        
        **Métricas de Processo** (implementadas no dashboard):
        - *Defect Detection Percentage (DDP)*: Eficácia do QA
        - *First Pass Yield (FPY)*: Qualidade na primeira entrega
        - *Rework Effort Ratio*: Esforço gasto em correções
        
        **Métricas de Produto**:
        - *Defect Density*: Bugs por unidade de tamanho (SP)
        - *Test Coverage*: Cobertura de testes automatizados
        
        > *"We cannot improve what we cannot measure"* - ISTQB Syllabus
        
        **Referência**: [ISTQB CTFL Syllabus v4.0](https://www.istqb.org/certifications/certified-tester-foundation-level)
        
        ---
        
        ### 🔄 TDD - Test-Driven Development (Kent Beck)
        
        O **TDD** segue o ciclo **Red-Green-Refactor**:
        1. 🔴 **Red**: Escrever um teste que falha
        2. 🟢 **Green**: Escrever código mínimo para passar
        3. 🔵 **Refactor**: Melhorar o código mantendo testes passando
        
        **Como o Fator K se relaciona com TDD**:
        - Devs que praticam TDD tendem a ter **FK mais alto**
        - Menos bugs = maior proporção SP/Bugs
        - Selo Gold incentiva a prática
        
        **Referência**: [Martin Fowler - TDD](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
        
        ---
        
        ### 📈 Shift-Left Testing
        
        O conceito move as atividades de teste para o início do ciclo:
        
        ```
        Tradicional:  Requisitos → Desenvolvimento → [TESTES] → Deploy
        Shift-Left:   [TESTES] → Requisitos → [TESTES] → Dev → [TESTES] → Deploy
        ```
        
        **Estatísticas da indústria**:
        - Bug encontrado em dev: **$100** para corrigir
        - Bug encontrado em QA: **$1.500** para corrigir  
        - Bug encontrado em produção: **$10.000+** para corrigir
        
        > O dashboard ajuda a NINA a encontrar bugs mais cedo, economizando recursos.
        """)
    
    # Tomada de Decisão
    with st.expander("🧠 Tomada de Decisão por Perfil", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 👥 Para QA
            - Priorização de cards
            - Gestão de carga
            - Avaliação de risco de release
            - Identificação de aging
            """)
        
        with col2:
            st.markdown("""
            ### 🧑‍💼 Para Liderança
            - Go / No-Go de release
            - Performance do time
            - Identificação de gargalos
            - Health Score da sprint
            """)
        
        with col3:
            st.markdown("""
            ### 👨‍💻 Para Devs
            - Feedback de qualidade (Fator K)
            - Taxa de retrabalho
            - Tempo de ciclo
            - Cards pendentes
            """)
    
    # Governança
    with st.expander("🏢 Governança", expanded=False):
        st.markdown("""
        | Informação | Valor |
        |------------|-------|
        | **Desenvolvido por** | QA NINA |
        | **Mantido por** | Vinícios Ferreira |
        | **Versão** | v8.1 |
        | **Última atualização** | Abril 2026 |
        | **Stack** | Python, Streamlit, Plotly, Pandas |
        | **Integração** | Jira API REST |
        """)


# ==============================================================================
# FUNÇÃO PRINCIPAL
# ==============================================================================

def main():
    """Função principal do dashboard."""
    aplicar_estilos()
    
    # Header principal com logo Nina
    mostrar_header_nina()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🌲 NinaDash")
        st.caption("v8.0 - Inteligência de QA")
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
        
        projeto = st.selectbox("📁 Projeto", ["SD", "QA", "PB"], index=0)
        
        filtro_sprint = st.selectbox(
            "🗓️ Período",
            ["Sprint Ativa", "Últimos 30 dias", "Últimos 90 dias"],
            index=0
        )
        
        st.markdown("---")
        st.caption("📌 NINA Tecnologia")
        st.caption("Transformando dados em decisões")
    
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
        st.warning("⚠️ Nenhum card encontrado para os filtros selecionados")
        st.stop()
    
    df = processar_issues(issues)
    
    # Filtro por produto
    with st.sidebar:
        produtos_disponiveis = ['Todos'] + sorted(df['produto'].unique().tolist())
        filtro_produto = st.selectbox("📦 Produto", produtos_disponiveis, index=0)
        
        if filtro_produto != 'Todos':
            df = df[df['produto'] == filtro_produto]
    
    # Abas - TODAS AS FUNCIONALIDADES
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Visão Geral",
        "🔬 QA",
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
        aba_governanca(df)
    
    with tab4:
        aba_produto(df)
    
    with tab5:
        aba_historico(df)
    
    with tab6:
        aba_lideranca(df)
    
    with tab7:
        aba_sobre()


if __name__ == "__main__":
    main()
