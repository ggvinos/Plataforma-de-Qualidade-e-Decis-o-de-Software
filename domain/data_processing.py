"""
Processamento de dados, transformações e métricas de negócio.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from config import (
    CUSTOM_FIELDS,
    STATUS_FLOW,
    REGRAS,
    TEMAS_NAO_CLIENTES,
    JIRA_BASE_URL,
)
from integrations import extrair_texto_adf

def calcular_dias_necessarios_validacao(complexidade: str) -> int:
    """Calcula dias necessários para validação baseado na complexidade."""
    janela = REGRAS["janela_complexidade"]
    return janela.get(complexidade, janela.get("default", 3))

def avaliar_janela_validacao(dias_ate_release: int, complexidade: str) -> Dict:
    """Avalia se há janela suficiente para validação."""
    dias_necessarios = calcular_dias_necessarios_validacao(complexidade)
    dentro_janela = dias_ate_release >= dias_necessarios
    
    if dias_ate_release <= 0:
        status = "expirado"
    elif dias_ate_release < dias_necessarios:
        status = "fora"
    elif dias_ate_release < dias_necessarios + 2:
        status = "risco"
    else:
        status = "ok"
    
    return {
        "dentro_janela": dentro_janela,
        "status": status,
        "dias_necessarios": dias_necessarios,
        "dias_disponíveis": dias_ate_release
    }

def processar_issue_unica(issue: Dict) -> Dict:
    """Processa uma issue única do Jira."""
    hoje = datetime.now()
    f = issue.get('fields', {})
    
    # Tipo
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
    
    # Dev e Relator
    dev = f.get('assignee', {}).get('displayName', 'Não atribuído') if f.get('assignee') else 'Não atribuído'
    relator = f.get('reporter', {}).get('displayName', 'Não informado') if f.get('reporter') else 'Não informado'
    
    # Story Points
    sp = f.get(CUSTOM_FIELDS['story_points']) or f.get(CUSTOM_FIELDS['story_points_alt']) or 0
    sp_original = bool(f.get(CUSTOM_FIELDS['story_points']) or f.get(CUSTOM_FIELDS['story_points_alt']))
    sp_estimado = False
    if sp == 0 and tipo == "HOTFIX":
        sp = REGRAS["hotfix_sp_default"]
        sp_estimado = True
    
    # Sprint
    sprint_f = f.get(CUSTOM_FIELDS['sprint'], [])
    sprint_atual = None
    if sprint_f:
        for s in sprint_f:
            if s.get('state') == 'active':
                sprint_atual = s
                break
        if not sprint_atual:
            sprint_atual = sprint_f[-1]
    
    sprint = sprint_atual.get('name', 'Sem Sprint') if sprint_atual else 'Sem Sprint'
    sprint_end = None
    sprint_state = sprint_atual.get('state', '') if sprint_atual else ''
    if sprint_atual:
        sprint_end_str = sprint_atual.get('endDate')
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
    
    # Métricas
    dias_em_status = (hoje - atualizado).days
    lead_time = (resolutiondate - criado).days if resolutiondate else (hoje - criado).days
    dias_ate_release = 0
    if sprint_end:
        dias_ate_release = max(0, (sprint_end - hoje).days)
    
    # Janela de validação
    janela_info = avaliar_janela_validacao(dias_ate_release, complexidade)
    
    # Descrição
    descricao = f.get('description', '') or ''
    if isinstance(descricao, dict):
        try:
            content = descricao.get('content', [])
            partes = []
            for item in content:
                if item.get('type') == 'paragraph':
                    for text_item in item.get('content', []):
                        if text_item.get('type') == 'text':
                            partes.append(text_item.get('text', ''))
            descricao = ' '.join(partes)
        except:
            descricao = ''
    
    # Labels e componentes
    labels = f.get('labels', []) or []
    componentes_raw = f.get('components', []) or []
    componentes = [c.get('name', '') for c in componentes_raw] if componentes_raw else []
    
    # Epic Link
    epic_link = ''
    parent = f.get('parent', {})
    if parent:
        epic_link = parent.get('key', '')
    
    ticket_id = issue.get('key', '')
    
    return {
        'ticket_id': ticket_id,
        'titulo': f.get('summary', ''),
        'tipo': tipo,
        'tipo_original': tipo_original,
        'status': status,
        'status_cat': status_cat,
        'projeto': projeto,
        'desenvolvedor': dev,
        'relator': relator,
        'qa': qa,
        'sp': int(sp) if sp else 0,
        'sp_original': sp_original,
        'sp_estimado': sp_estimado,
        'bugs': int(bugs) if bugs else 0,
        'sprint': sprint,
        'prioridade': f.get('priority', {}).get('name', 'Média') if f.get('priority') else 'Média',
        'complexidade': complexidade,
        'produto': produto,
        'criado': criado,
        'atualizado': atualizado,
        'resolutiondate': resolutiondate,
        'dias_em_status': dias_em_status,
        'lead_time': lead_time,
        'dias_ate_release': dias_ate_release,
        'dentro_janela': janela_info["dentro_janela"],
        'janela_status': janela_info["status"],
        'janela_dias_necessarios': janela_info["dias_necessarios"],
        'sp_preenchido': sp_original,
        'bugs_preenchido': f.get(CUSTOM_FIELDS['bugs_encontrados']) is not None,
        'complexidade_preenchida': bool(complexidade),
        'qa_preenchido': qa != 'Não atribuído',
        'descricao': descricao,
        'labels': labels,
        'componentes': componentes,
        'epic_link': epic_link,
    }

def processar_issues(issues: List[Dict]) -> pd.DataFrame:
    """Processa lista de issues do Jira para DataFrame."""
    dados = []
    hoje = datetime.now()
    
    for issue in issues:
        f = issue.get('fields', {})
        
        # Tipo
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
        
        # Dev e Relator
        dev = f.get('assignee', {}).get('displayName', 'Não atribuído') if f.get('assignee') else 'Não atribuído'
        relator = f.get('reporter', {}).get('displayName', 'Não informado') if f.get('reporter') else 'Não informado'
        
        # Story Points
        sp = f.get(CUSTOM_FIELDS['story_points']) or f.get(CUSTOM_FIELDS['story_points_alt']) or 0
        sp_original = bool(f.get(CUSTOM_FIELDS['story_points']) or f.get(CUSTOM_FIELDS['story_points_alt']))
        if sp == 0 and tipo == "HOTFIX":
            sp = REGRAS["hotfix_sp_default"]
        
        # Sprint
        sprint_f = f.get(CUSTOM_FIELDS['sprint'], [])
        sprint_atual = None
        if sprint_f:
            for s in sprint_f:
                if s.get('state') == 'active':
                    sprint_atual = s
                    break
            if not sprint_atual:
                sprint_atual = sprint_f[-1]
        
        sprint = sprint_atual.get('name', 'Sem Sprint') if sprint_atual else 'Sem Sprint'
        sprint_id = sprint_atual.get('id') if sprint_atual else None
        sprint_state = sprint_atual.get('state', '') if sprint_atual else ''
        sprint_start = None
        sprint_end = None
        if sprint_atual:
            sprint_start_str = sprint_atual.get('startDate')
            sprint_end_str = sprint_atual.get('endDate')
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
        
        # Temas
        temas_f = f.get(CUSTOM_FIELDS['temas'], [])
        temas = temas_f if isinstance(temas_f, list) else []
        tema_principal = temas[0] if temas else 'Sem tema'
        
        # Importância
        importancia_f = f.get(CUSTOM_FIELDS['importancia'])
        importancia = importancia_f.get('value', 'Não definido') if isinstance(importancia_f, dict) else 'Não definido'
        
        # SLA
        sla_f = f.get(CUSTOM_FIELDS['sla_status'])
        sla_status = sla_f.get('value', '') if isinstance(sla_f, dict) else ''
        sla_atrasado = sla_status == 'Atrasado'
        
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
        
        # Métricas
        dias_em_status = (hoje - atualizado).days
        lead_time = (resolutiondate - criado).days if resolutiondate else (hoje - criado).days
        dias_ate_release = 0
        if sprint_end:
            dias_ate_release = max(0, (sprint_end - hoje).days)
        
        # Análise de Sprint
        criado_na_sprint = False
        if sprint_start and sprint_end:
            criado_na_sprint = sprint_start <= criado <= sprint_end
        
        finalizado_mesma_sprint = False
        if status_cat == 'done' and criado_na_sprint:
            finalizado_mesma_sprint = True
        
        adicionado_fora_periodo = False
        if sprint_start and criado > sprint_start + timedelta(days=2):
            adicionado_fora_periodo = True
        
        # Janela de validação
        janela_info = avaliar_janela_validacao(dias_ate_release, complexidade)
        dentro_janela = janela_info["dentro_janela"]
        janela_status = janela_info["status"]
        janela_dias_necessarios = janela_info["dias_necessarios"]
        
        # Flags
        sp_preenchido = sp_original
        bugs_preenchido = f.get(CUSTOM_FIELDS['bugs_encontrados']) is not None
        complexidade_preenchida = bool(complexidade)
        qa_preenchido = qa != 'Não atribuído'
        
        # Link PB
        issuelinks = f.get('issuelinks', [])
        origem_pb = None
        tem_link_pb = False
        for link in issuelinks:
            outward = link.get('outwardIssue', {})
            if outward.get('key', '').startswith('PB-'):
                origem_pb = outward.get('key')
                tem_link_pb = True
                break
            inward = link.get('inwardIssue', {})
            if inward.get('key', '').startswith('PB-'):
                origem_pb = inward.get('key')
                tem_link_pb = True
                break
        
        ticket_id = issue.get('key', '')
        
        dados.append({
            'ticket_id': ticket_id,
            'titulo': f.get('summary', ''),
            'tipo': tipo,
            'tipo_original': tipo_original,
            'status': status,
            'status_cat': status_cat,
            'projeto': projeto,
            'desenvolvedor': dev,
            'relator': relator,
            'qa': qa,
            'sp': int(sp) if sp else 0,
            'sp_original': sp_original,
            'bugs': int(bugs) if bugs else 0,
            'sprint': sprint,
            'sprint_id': sprint_id,
            'sprint_state': sprint_state,
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
            'janela_status': janela_status,
            'janela_dias_necessarios': janela_dias_necessarios,
            'sp_preenchido': sp_preenchido,
            'bugs_preenchido': bugs_preenchido,
            'complexidade_preenchida': complexidade_preenchida,
            'qa_preenchido': qa_preenchido,
            'criado_na_sprint': criado_na_sprint,
            'finalizado_mesma_sprint': finalizado_mesma_sprint,
            'adicionado_fora_periodo': adicionado_fora_periodo,
            'temas': temas,
            'tema_principal': tema_principal,
            'importancia': importancia,
            'sla_status': sla_status,
            'sla_atrasado': sla_atrasado,
            'origem_pb': origem_pb,
            'tem_link_pb': tem_link_pb,
        })
    
    return pd.DataFrame(dados)

# Funções de métricas
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

def analisar_dev_detalhado(df: pd.DataFrame, dev_nome: str) -> Optional[Dict]:
    """Análise completa de um desenvolvedor."""
    df_dev = df[df['desenvolvedor'] == dev_nome]
    if df_dev.empty:
        return None
    
    sp_total = int(df_dev['sp'].sum())
    bugs_total = int(df_dev['bugs'].sum())
    
    fk_medio = calcular_fator_k(sp_total, bugs_total)
    maturidade = classificar_maturidade(fk_medio)
    
    zero_bugs = len(df_dev[df_dev['bugs'] == 0]) / len(df_dev) * 100 if len(df_dev) > 0 else 0
    
    return {
        'df': df_dev,
        'cards': len(df_dev),
        'sp_total': sp_total,
        'bugs_total': bugs_total,
        'fk_medio': fk_medio,
        'maturidade': maturidade,
        'zero_bugs': round(zero_bugs, 1),
        'tempo_medio': round(df_dev['lead_time'].mean(), 1) if not df_dev.empty else 0,
    }

def calcular_concentracao_conhecimento(df: pd.DataFrame) -> Dict:
    """Calcula concentração de conhecimento por DEV e QA."""
    if df.empty:
        return {
            "alertas_dev": [],
            "alertas_qa": [],
            "qas_principais": [],
        }
    
    # Filtra QAs principais
    qas_principais = []
    if not df.empty:
        qa_counts = df[df['qa'] != 'Não atribuído'].groupby('qa').size().reset_index(name='total_cards')
        qas_principais = qa_counts[qa_counts['total_cards'] >= 5]['qa'].tolist()
    
    return {
        "alertas_dev": [],
        "alertas_qa": [],
        "qas_principais": qas_principais,
    }
