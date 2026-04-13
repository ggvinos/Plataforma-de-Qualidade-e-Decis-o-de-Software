vinicios.ferreira@confirmationcall.com.br"""
================================================================================
JIRA DASHBOARD - MÉTRICAS DE QUALIDADE E ENTREGA
================================================================================
Autor: Dashboard de Métricas para Tech Lead
Descrição: Dashboard Streamlit para visualização de métricas de entrega,
           qualidade e gestão de bugs integrado com Jira API.

INSTRUÇÕES DE CUSTOMIZAÇÃO:
---------------------------
Procure por "# TODO: CUSTOMIZAR" no código para encontrar os pontos que você
deve alterar para adaptar aos Custom Fields do seu Jira.

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

# URL base do Jira
JIRA_BASE_URL = "https://ninatecnologia.atlassian.net"

# Mapeamento dos Custom Fields - Baseado nos campos reais do seu Jira
CUSTOM_FIELDS = {
    "story_points": "customfield_10016",       # Story point estimate
    "story_points_alt1": "customfield_10036",  # Story Points (alternativo)
    "story_points_alt2": "customfield_11091",  # Story Points (alternativo 2)
    "sprint": "customfield_10020",             # Sprint
    "bugs_encontrados": "customfield_11157",   # Bugs Encontrados
    "dias_ate_release": "customfield_11357",   # Dias até a Release
    "janela_testes": "customfield_11358",      # Janela de Testes
    "status_maturidade": "customfield_11224",  # Status de Maturidade
    "complexidade_teste": "customfield_11290", # Complexidade de Teste
    "plano_testes": "customfield_11024",       # Plano de testes
    "qa_responsavel": "customfield_10784",     # QA (array)
    "qa_user": "customfield_10487",            # QA (user)
    "desenvolvedor": "customfield_10455",      # Desenvolvedor
    "desenvolvedor_array": "customfield_10785",# Desenvolvedor (array)
}

# Mapeamento dos tipos de ticket da empresa
TIPOS_TICKET = {
    "HOTFIX": ["Hotfix", "Hotfeature"],
    "BUG": ["Bug", "Impeditivo de entrega"],
    "TAREFA": ["Tarefa", "Task", "Subtarefa"],
    "EPIC": ["Epic"],
    "SUGESTÃO": ["Sugestão", "Improvement"],
    "DEV_PAGO": ["Desenvolvimento pago"],
}

# Configuração dos selos de maturidade (Fator K)
# Quanto MAIOR o Fator K, MELHOR a qualidade
SELOS_MATURIDADE = {
    "Gold": {"min": 3.0, "cor": "#FFD700", "emoji": "🥇"},
    "Silver": {"min": 2.0, "cor": "#C0C0C0", "emoji": "🥈"},
    "Bronze": {"min": 1.0, "cor": "#CD7F32", "emoji": "🥉"},
    "Risco": {"min": 0, "cor": "#FF4444", "emoji": "⚠️"},
}


# ==============================================================================
# FUNÇÕES DE CONEXÃO COM JIRA
# ==============================================================================

def verificar_credenciais_jira() -> bool:
    """
    Verifica se as credenciais do Jira estão configuradas.
    
    Returns:
        bool: True se as credenciais estão preenchidas, False caso contrário.
    """
    email = st.session_state.get("jira_email", "")
    token = st.session_state.get("jira_token", "")
    return bool(email and token)


def buscar_dados_jira(jql_query: str) -> Optional[List[Dict]]:
    """
    Executa uma consulta JQL na API do Jira (Nova API POST).
    
    Args:
        jql_query: Query JQL para buscar os tickets.
        
    Returns:
        Lista de issues encontradas ou None em caso de erro.
    """
    if not verificar_credenciais_jira():
        return None
    
    email = st.session_state.get("jira_email")
    token = st.session_state.get("jira_token")
    
    url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Campos a buscar - incluindo todos os custom fields relevantes
    fields = [
        "summary",
        "status",
        "issuetype",
        "assignee",
        "created",
        "updated",
        "resolutiondate",
        "priority",
        "project",
        "labels",
        "components",
        CUSTOM_FIELDS["story_points"],
        CUSTOM_FIELDS["story_points_alt1"],
        CUSTOM_FIELDS["story_points_alt2"],
        CUSTOM_FIELDS["sprint"],
        CUSTOM_FIELDS["bugs_encontrados"],
        CUSTOM_FIELDS["dias_ate_release"],
        CUSTOM_FIELDS["janela_testes"],
        CUSTOM_FIELDS["status_maturidade"],
        CUSTOM_FIELDS["complexidade_teste"],
        CUSTOM_FIELDS["plano_testes"],
        CUSTOM_FIELDS["qa_responsavel"],
        CUSTOM_FIELDS["qa_user"],
        CUSTOM_FIELDS["desenvolvedor"],
        CUSTOM_FIELDS["desenvolvedor_array"],
    ]
    
    payload = json.dumps({
        "jql": jql_query,
        "maxResults": 100,
        "fields": fields
    })
    
    try:
        response = requests.post(
            url,
            headers=headers,
            data=payload,
            auth=(email, token)
        )
        response.raise_for_status()
        return response.json().get("issues", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar com Jira: {str(e)}")
        return None


def transformar_dados_jira(issues: List[Dict], data_release: datetime) -> pd.DataFrame:
    """
    Transforma os dados brutos da API do Jira para o formato do DataFrame.
    
    Args:
        issues: Lista de issues retornadas pela API do Jira.
        data_release: Data da próxima release.
        
    Returns:
        DataFrame formatado para o dashboard.
    """
    dados = []
    
    for issue in issues:
        fields = issue.get('fields', {})
        
        # Extrair tipo do ticket
        issue_type = fields.get('issuetype', {}).get('name', 'Unknown')
        tipo = 'TAREFA'  # Default
        for tipo_key, nomes in TIPOS_TICKET.items():
            if issue_type in nomes:
                tipo = tipo_key
                break
        
        # Extrair projeto
        projeto = fields.get('project', {}).get('key', 'N/A')
        
        # Extrair desenvolvedor (tentar vários campos)
        desenvolvedor = 'Não atribuído'
        
        # Primeiro tenta o assignee padrão
        assignee = fields.get('assignee')
        if assignee:
            desenvolvedor = assignee.get('displayName', 'Não atribuído')
        
        # Ou tenta custom field de desenvolvedor
        dev_custom = fields.get(CUSTOM_FIELDS['desenvolvedor'])
        if dev_custom and isinstance(dev_custom, dict):
            desenvolvedor = dev_custom.get('displayName', desenvolvedor)
        
        # Extrair Story Points (tentar vários campos)
        story_points = (
            fields.get(CUSTOM_FIELDS['story_points']) or 
            fields.get(CUSTOM_FIELDS['story_points_alt1']) or 
            fields.get(CUSTOM_FIELDS['story_points_alt2']) or 
            0
        )
        
        # Extrair Sprint
        sprint_field = fields.get(CUSTOM_FIELDS['sprint'], [])
        if sprint_field and isinstance(sprint_field, list) and len(sprint_field) > 0:
            sprint = sprint_field[-1].get('name', 'Sem Sprint')
        else:
            sprint = 'Sem Sprint'
        
        # Extrair Bugs Encontrados (campo customizado)
        bugs_encontrados = fields.get(CUSTOM_FIELDS['bugs_encontrados'], 0) or 0
        
        # Extrair Janela de Testes
        janela_testes = fields.get(CUSTOM_FIELDS['janela_testes'], '')
        
        # Extrair Dias até Release
        dias_ate_release = fields.get(CUSTOM_FIELDS['dias_ate_release'], '')
        
        # Extrair Status de Maturidade
        status_maturidade = fields.get(CUSTOM_FIELDS['status_maturidade'], '')
        
        # Extrair Complexidade de Teste
        complexidade_teste = fields.get(CUSTOM_FIELDS['complexidade_teste'])
        if complexidade_teste and isinstance(complexidade_teste, dict):
            complexidade_teste = complexidade_teste.get('value', 'N/A')
        else:
            complexidade_teste = 'N/A'
        
        # Extrair QA responsável
        qa_responsavel = 'Não atribuído'
        qa_field = fields.get(CUSTOM_FIELDS['qa_user']) or fields.get(CUSTOM_FIELDS['qa_responsavel'])
        if qa_field:
            if isinstance(qa_field, dict):
                qa_responsavel = qa_field.get('displayName', 'Não atribuído')
            elif isinstance(qa_field, list) and len(qa_field) > 0:
                qa_responsavel = qa_field[0].get('displayName', 'Não atribuído')
        
        # Prioridade
        prioridade = fields.get('priority', {})
        prioridade_nome = prioridade.get('name', 'Médio') if prioridade else 'Médio'
        
        # Data de criação
        data_criacao_str = fields.get('created', '')
        try:
            data_criacao = datetime.fromisoformat(data_criacao_str.replace('Z', '+00:00')).replace(tzinfo=None)
        except:
            data_criacao = datetime.now()
        
        # Data de atualização
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
            'data_release': data_release
        })
    
    return pd.DataFrame(dados)


def buscar_e_transformar_dados_jira(projetos: str, data_release: datetime) -> Optional[pd.DataFrame]:
    """
    Busca dados do Jira e transforma para o formato do dashboard.
    
    Args:
        projetos: Códigos dos projetos no Jira separados por vírgula (ex: 'SD,QA,PB').
        data_release: Data da próxima release.
        
    Returns:
        DataFrame com os dados ou None em caso de erro.
    """
    # Construir JQL para múltiplos projetos
    proj_list = [p.strip() for p in projetos.split(',')]
    if len(proj_list) == 1:
        jql = f'project = "{proj_list[0]}" AND created >= -90d ORDER BY created DESC'
    else:
        proj_in = ', '.join([f'"{p}"' for p in proj_list])
        jql = f'project IN ({proj_in}) AND created >= -90d ORDER BY created DESC'
    
    issues = buscar_dados_jira(jql)
    
    if issues is None:
        return None
    
    if len(issues) == 0:
        st.warning("Nenhum ticket encontrado com a JQL especificada.")
        return None
    
    return transformar_dados_jira(issues, data_release)


# ==============================================================================
# FUNÇÕES DE DADOS MOCKADOS (PARA PoC)
# ==============================================================================

def gerar_dados_mockados() -> pd.DataFrame:
    """
    Gera dados fictícios para demonstração do dashboard.
    Simula dados realistas baseados na estrutura do Jira da empresa.
    
    Returns:
        DataFrame com dados mockados para demonstração.
    """
    
    # Desenvolvedores baseados nos reais
    desenvolvedores = [
        "Ellen Haderspeck", "Christopher Krauss", "Augusto Oliveira", 
        "Rafael Teles", "João Pedro Menegali", "Carlos Daniel",
        "Cristian Yamamoto", "Elinton Dozol"
    ]
    
    # QAs
    qas = ["Irla Rafaela", "Larissa Carneiro", "João Pedro Greif", "Não atribuído"]
    
    # Tipos de ticket baseados nos reais
    tipos = ["TAREFA", "BUG", "HOTFIX", "SUGESTÃO"]
    tipos_originais = {
        "TAREFA": "Tarefa",
        "BUG": "Bug", 
        "HOTFIX": "Hotfix",
        "SUGESTÃO": "Sugestão"
    }
    
    # Status baseados nos reais
    status_list = [
        "Backlog", "Em andamento", "EM DESENVOLVIMENTO", 
        "AGUARDANDO VALIDAÇÃO", "EM REVISÃO", "Concluído"
    ]
    
    # Projetos
    projetos = ["SD", "VALPROD", "PB", "QA"]
    
    # Sprints
    sprints = ["Sprint 23", "Sprint 24", "Sprint 25 (Atual)"]
    
    # Complexidade de teste
    complexidades = ["Baixa", "Média", "Alta", "Muito Alta"]
    
    # Prioridades
    prioridades = ["Baixo", "Médio", "Alto", "Muito alto"]
    
    dados = []
    hoje = datetime.now()
    data_release = hoje + timedelta(days=random.randint(5, 15))
    
    for i in range(80):
        tipo = random.choices(tipos, weights=[50, 25, 15, 10])[0]
        projeto = random.choices(projetos, weights=[40, 30, 20, 10])[0]
        
        # Story Points variam por tipo
        if tipo == "TAREFA":
            sp = random.choice([3, 5, 8, 13])
        elif tipo == "BUG":
            sp = random.choice([1, 2, 3])
        elif tipo == "HOTFIX":
            sp = random.choice([1, 2])
        else:
            sp = random.choice([1, 2, 3, 5])
        
        # Bugs encontrados
        if tipo == "TAREFA":
            bugs = random.choices([0, 1, 2, 3, 4, 5], weights=[30, 25, 20, 15, 7, 3])[0]
        else:
            bugs = random.choices([0, 1, 2], weights=[70, 20, 10])[0]
        
        data_criacao = hoje - timedelta(days=random.randint(1, 60))
        status = random.choice(status_list)
        sprint = random.choices(sprints, weights=[20, 30, 50])[0]
        
        # Calcular janela de testes
        janela = random.randint(2, 15) if status in ["AGUARDANDO VALIDAÇÃO", "Concluído"] else None
        
        dados.append({
            "ticket_id": f"{projeto}-{1000 + i}",
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
            "data_release": data_release if sprint == "Sprint 25 (Atual)" else None
        })
    
    return pd.DataFrame(dados)


# ==============================================================================
# FUNÇÕES DE CÁLCULO DE MÉTRICAS
# ==============================================================================

def calcular_fator_k(story_points: int, bugs: int, rigor: float = 1.5) -> float:
    """
    Calcula o Fator K (Maturidade de Entrega).
    
    Fórmula: SP / (Quantidade de Bugs * Rigor)
    
    Args:
        story_points: Quantidade de Story Points do card.
        bugs: Número de bugs encontrados relacionados ao card.
        rigor: Fator de rigor/peso dos bugs (padrão: 1.5).
        
    Returns:
        Valor do Fator K. Retorna infinito se não houver bugs.
    """
    if bugs == 0:
        return float('inf')  # Perfeito - sem bugs
    
    return story_points / (bugs * rigor)


def classificar_maturidade(fator_k: float) -> Dict[str, Any]:
    """
    Classifica o Fator K em um selo de maturidade.
    
    Args:
        fator_k: Valor calculado do Fator K.
        
    Returns:
        Dicionário com nome do selo, cor e emoji.
    """
    if fator_k == float('inf'):
        return {
            "selo": "Gold", 
            "cor": SELOS_MATURIDADE["Gold"]["cor"],
            "emoji": SELOS_MATURIDADE["Gold"]["emoji"],
            "descricao": "Excelente! Sem bugs."
        }
    
    for selo, config in SELOS_MATURIDADE.items():
        if fator_k >= config["min"]:
            return {
                "selo": selo,
                "cor": config["cor"],
                "emoji": config["emoji"],
                "descricao": f"Fator K: {fator_k:.2f}"
            }
    
    return {
        "selo": "Risco",
        "cor": SELOS_MATURIDADE["Risco"]["cor"],
        "emoji": SELOS_MATURIDADE["Risco"]["emoji"],
        "descricao": "Atenção! Alta taxa de bugs."
    }


def calcular_dias_para_release(data_release: datetime) -> int:
    """
    Calcula quantos dias faltam para a release.
    
    Args:
        data_release: Data prevista da release.
        
    Returns:
        Número de dias até a release (negativo se já passou).
    """
    hoje = datetime.now()
    delta = data_release - hoje
    return delta.days


def calcular_janela_teste(data_entrega_qa: datetime, data_release: datetime) -> int:
    """
    Calcula a janela de teste disponível.
    
    Args:
        data_entrega_qa: Data que o Dev entregou para QA.
        data_release: Data prevista da release.
        
    Returns:
        Número de dias disponíveis para teste.
    """
    if data_entrega_qa is None or data_release is None:
        return None
    
    delta = data_release - data_entrega_qa
    return delta.days


# ==============================================================================
# FUNÇÕES DE ANÁLISE AVANÇADA (QA LEAD)
# ==============================================================================

def analisar_divida_tecnica_teste(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifica Dívida Técnica de Teste:
    Cards com Alta Complexidade que entraram em validação com menos de 2 dias.
    
    Returns:
        DataFrame com cards classificados como dívida técnica.
    """
    df_analise = df.copy()
    
    # Converter janela_testes para numérico
    df_analise['janela_num'] = pd.to_numeric(df_analise['janela_testes'], errors='coerce').fillna(0)
    
    # Identificar dívida técnica:
    # Alta/Muito Alta complexidade + menos de 2 dias de janela
    condicao_divida = (
        (df_analise['complexidade_teste'].isin(['Alta', 'Muito Alta'])) & 
        (df_analise['janela_num'] > 0) & 
        (df_analise['janela_num'] < 2)
    )
    
    df_analise['divida_tecnica'] = condicao_divida
    df_analise['motivo_divida'] = df_analise.apply(
        lambda row: f"Complexidade {row['complexidade_teste']} com apenas {row['janela_num']:.0f} dia(s)" 
        if row['divida_tecnica'] else None,
        axis=1
    )
    
    return df_analise[df_analise['divida_tecnica']]


def analisar_risco_baixa_cobertura(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifica cards com risco de baixa cobertura de testes:
    Cards com muitos Story Points (>=5) que não geraram bugs em QA.
    
    Lógica: Se um card complexo não teve nenhum bug, pode indicar
    teste superficial ou falta de cenários de teste.
    
    Returns:
        DataFrame com cards suspeitos.
    """
    df_analise = df.copy()
    
    # Cards com SP >= 5 e zero bugs encontrados (e que já passaram por QA)
    status_pos_qa = ['Concluído', 'ENTREGUE', 'Done', 'EM REVISÃO', 'AGUARDANDO VALIDAÇÃO']
    
    condicao_risco = (
        (df_analise['story_points'] >= 5) & 
        (df_analise['bugs_encontrados'] == 0) &
        (df_analise['status'].isin(status_pos_qa))
    )
    
    df_analise['risco_cobertura'] = condicao_risco
    df_analise['alerta_cobertura'] = df_analise.apply(
        lambda row: f"⚠️ {row['story_points']} SP sem bugs - Verificar cobertura de testes" 
        if row['risco_cobertura'] else None,
        axis=1
    )
    
    return df_analise[df_analise['risco_cobertura']]


def analisar_performance_dev(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analisa performance de desenvolvedores baseado no Fator K.
    
    Identifica padrões de instabilidade por desenvolvedor.
    
    Returns:
        DataFrame com métricas agregadas por desenvolvedor.
    """
    df_analise = df.copy()
    
    # Calcular Fator K para cada card
    df_analise['fator_k'] = df_analise.apply(
        lambda row: calcular_fator_k(row['story_points'], row['bugs_encontrados']),
        axis=1
    )
    
    # Substituir infinito por um valor alto para cálculos
    df_analise['fator_k_calc'] = df_analise['fator_k'].apply(
        lambda x: 10 if x == float('inf') else x
    )
    
    # Agregar por desenvolvedor
    metricas_dev = df_analise.groupby('desenvolvedor').agg({
        'ticket_id': 'count',
        'story_points': 'sum',
        'bugs_encontrados': 'sum',
        'fator_k_calc': 'mean'
    }).reset_index()
    
    metricas_dev.columns = ['Desenvolvedor', 'Total Cards', 'Total SP', 'Total Bugs', 'Fator K Médio']
    
    # Calcular taxa de bugs por SP
    metricas_dev['Taxa Bugs/SP'] = (metricas_dev['Total Bugs'] / metricas_dev['Total SP'].replace(0, 1)).round(2)
    
    # Classificar performance
    def classificar_performance(row):
        if row['Fator K Médio'] >= 3:
            return '🟢 Excelente'
        elif row['Fator K Médio'] >= 2:
            return '🟡 Bom'
        elif row['Fator K Médio'] >= 1:
            return '🟠 Atenção'
        else:
            return '🔴 Crítico'
    
    metricas_dev['Performance'] = metricas_dev.apply(classificar_performance, axis=1)
    
    return metricas_dev.sort_values('Fator K Médio', ascending=True)


def analisar_go_no_go(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Análise Go/No-Go automática para decisão de release.
    
    Identifica cards que devem ser removidos da release baseado em:
    - Baixo Fator K
    - Alta Complexidade de Teste
    - Poucos dias restantes
    
    Returns:
        Dicionário com análise completa e recomendações.
    """
    df_analise = df.copy()
    
    # Converter campos numéricos
    df_analise['janela_num'] = pd.to_numeric(df_analise['janela_testes'], errors='coerce').fillna(0)
    df_analise['dias_release_num'] = pd.to_numeric(df_analise['dias_ate_release'], errors='coerce').fillna(999)
    
    # Calcular Fator K
    df_analise['fator_k'] = df_analise.apply(
        lambda row: calcular_fator_k(row['story_points'], row['bugs_encontrados']),
        axis=1
    )
    
    # Calcular score de risco (quanto MAIOR, mais arriscado)
    def calcular_score_risco(row):
        score = 0
        
        # Fator K baixo = alto risco
        fk = row['fator_k'] if row['fator_k'] != float('inf') else 10
        if fk < 1:
            score += 40
        elif fk < 2:
            score += 20
        elif fk < 3:
            score += 10
        
        # Alta complexidade = alto risco
        if row['complexidade_teste'] == 'Muito Alta':
            score += 30
        elif row['complexidade_teste'] == 'Alta':
            score += 20
        elif row['complexidade_teste'] == 'Média':
            score += 10
        
        # Poucos dias = alto risco
        if row['janela_num'] < 2:
            score += 30
        elif row['janela_num'] < 3:
            score += 20
        elif row['janela_num'] < 5:
            score += 10
        
        # Muitos bugs = alto risco
        if row['bugs_encontrados'] >= 5:
            score += 25
        elif row['bugs_encontrados'] >= 3:
            score += 15
        elif row['bugs_encontrados'] >= 1:
            score += 5
        
        return score
    
    df_analise['score_risco'] = df_analise.apply(calcular_score_risco, axis=1)
    
    # Classificar decisão
    def decisao_go_no_go(score):
        if score >= 70:
            return '🔴 NO-GO (Remover da Release)'
        elif score >= 50:
            return '🟠 RISCO ALTO (Reavaliar)'
        elif score >= 30:
            return '🟡 ATENÇÃO (Monitorar)'
        else:
            return '🟢 GO (Aprovado)'
    
    df_analise['decisao'] = df_analise['score_risco'].apply(decisao_go_no_go)
    
    # Separar por decisão
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
    """
    Calcula a saúde geral da release.
    
    Returns:
        Dicionário com status da saúde e métricas.
    """
    if df.empty:
        return {
            'status': '⚪ Sem Dados',
            'cor': '#808080',
            'score': 0,
            'motivos': ['Sem dados para análise']
        }
    
    # Análise Go/No-Go
    analise = analisar_go_no_go(df)
    
    # Calcular score de saúde (0-100, quanto MAIOR melhor)
    total_cards = len(df)
    if total_cards == 0:
        return {'status': '⚪ Sem Dados', 'cor': '#808080', 'score': 0, 'motivos': []}
    
    # Porcentagem de cards aprovados
    pct_aprovados = (analise['total_go'] / total_cards) * 100
    pct_risco = ((analise['total_no_go'] + analise['total_risco']) / total_cards) * 100
    
    # Fator K médio geral
    df_temp = df.copy()
    df_temp['fator_k'] = df_temp.apply(
        lambda row: calcular_fator_k(row['story_points'], row['bugs_encontrados']),
        axis=1
    )
    df_temp['fator_k_calc'] = df_temp['fator_k'].apply(lambda x: 10 if x == float('inf') else x)
    fator_k_medio = df_temp['fator_k_calc'].mean()
    
    # Total de bugs
    total_bugs = df['bugs_encontrados'].sum()
    total_sp = df['story_points'].sum()
    taxa_bugs = (total_bugs / total_sp * 100) if total_sp > 0 else 0
    
    # Calcular score final
    score = 0
    motivos = []
    
    # Peso: Cards aprovados (40%)
    score += (pct_aprovados / 100) * 40
    
    # Peso: Fator K médio (30%)
    if fator_k_medio >= 3:
        score += 30
    elif fator_k_medio >= 2:
        score += 20
    elif fator_k_medio >= 1:
        score += 10
    else:
        motivos.append(f"Fator K médio baixo: {fator_k_medio:.2f}")
    
    # Peso: Taxa de bugs (30%)
    if taxa_bugs < 5:
        score += 30
    elif taxa_bugs < 10:
        score += 20
    elif taxa_bugs < 20:
        score += 10
    else:
        motivos.append(f"Taxa de bugs alta: {taxa_bugs:.1f}%")
    
    # Adicionar motivos específicos
    if analise['total_no_go'] > 0:
        motivos.append(f"{analise['total_no_go']} cards marcados como NO-GO")
    if analise['total_risco'] > 0:
        motivos.append(f"{analise['total_risco']} cards com risco alto")
    if pct_risco > 30:
        motivos.append(f"{pct_risco:.0f}% dos cards com problemas")
    
    # Determinar status
    if score >= 80:
        status = '🟢 ESTÁVEL'
        cor = '#28a745'
    elif score >= 60:
        status = '🟡 ALERTA'
        cor = '#ffc107'
    else:
        status = '🔴 CRÍTICA'
        cor = '#dc3545'
    
    return {
        'status': status,
        'cor': cor,
        'score': round(score, 1),
        'motivos': motivos,
        'pct_aprovados': pct_aprovados,
        'fator_k_medio': fator_k_medio,
        'taxa_bugs': taxa_bugs,
        'total_bugs': total_bugs,
        'total_sp': total_sp
    }


def gerar_top_riscos(df: pd.DataFrame, top_n: int = 3) -> List[Dict]:
    """
    Gera lista dos top N riscos da release.
    
    Returns:
        Lista de dicionários com os cards mais arriscados.
    """
    analise = analisar_go_no_go(df)
    df_ordenado = analise['df_completo'].sort_values('score_risco', ascending=False)
    
    riscos = []
    for i, row in df_ordenado.head(top_n).iterrows():
        risco = {
            'ticket': row['ticket_id'],
            'titulo': row['titulo'][:50] + '...' if len(row['titulo']) > 50 else row['titulo'],
            'score': row['score_risco'],
            'decisao': row['decisao'],
            'desenvolvedor': row['desenvolvedor'],
            'motivos': []
        }
        
        # Identificar motivos específicos
        if row['bugs_encontrados'] >= 3:
            risco['motivos'].append(f"{row['bugs_encontrados']} bugs encontrados")
        
        fk = row['fator_k'] if row['fator_k'] != float('inf') else 10
        if fk < 2:
            risco['motivos'].append(f"Fator K: {fk:.2f}")
        
        if row['complexidade_teste'] in ['Alta', 'Muito Alta']:
            risco['motivos'].append(f"Complexidade: {row['complexidade_teste']}")
        
        if row['janela_num'] < 3:
            risco['motivos'].append(f"Apenas {row['janela_num']:.0f} dias para teste")
        
        riscos.append(risco)
    
    return riscos


def gerar_recomendacoes(df: pd.DataFrame) -> List[Dict]:
    """
    Gera recomendações técnicas baseadas na análise dos dados.
    
    Returns:
        Lista de recomendações acionáveis.
    """
    recomendacoes = []
    
    # Análise Go/No-Go
    analise = analisar_go_no_go(df)
    saude = calcular_saude_release(df)
    
    # Recomendação 1: Cards NO-GO
    if analise['total_no_go'] > 0:
        cards = analise['no_go']['ticket_id'].tolist()
        recomendacoes.append({
            'prioridade': '🔴 URGENTE',
            'acao': 'Mover para próxima sprint',
            'descricao': f"Remover {analise['total_no_go']} card(s) da release atual para garantir qualidade",
            'cards': cards[:5],
            'impacto': 'Alto'
        })
    
    # Recomendação 2: Risco de baixa cobertura
    df_cobertura = analisar_risco_baixa_cobertura(df)
    if not df_cobertura.empty:
        cards = df_cobertura['ticket_id'].tolist()
        recomendacoes.append({
            'prioridade': '🟠 IMPORTANTE',
            'acao': 'Revisão de casos de teste',
            'descricao': f"{len(df_cobertura)} card(s) com SP alto sem bugs. Verificar se a cobertura de testes está adequada.",
            'cards': cards[:5],
            'impacto': 'Médio'
        })
    
    # Recomendação 3: Dívida técnica de teste
    df_divida = analisar_divida_tecnica_teste(df)
    if not df_divida.empty:
        recomendacoes.append({
            'prioridade': '🟡 ATENÇÃO',
            'acao': 'Antecipar entregas',
            'descricao': f"{len(df_divida)} card(s) entraram tarde demais para validação adequada. Revisar processo de handover Dev→QA.",
            'cards': df_divida['ticket_id'].tolist()[:5],
            'impacto': 'Médio'
        })
    
    # Recomendação 4: Performance de devs
    perf_dev = analisar_performance_dev(df)
    devs_criticos = perf_dev[perf_dev['Performance'].str.contains('Crítico')]
    if not devs_criticos.empty:
        devs = devs_criticos['Desenvolvedor'].tolist()
        recomendacoes.append({
            'prioridade': '🟠 IMPORTANTE',
            'acao': 'Mentoria técnica',
            'descricao': f"Oferecer suporte técnico para: {', '.join(devs[:3])}. Padrão de bugs acima da média.",
            'cards': [],
            'impacto': 'Alto'
        })
    
    # Recomendação 5: Saúde geral
    if saude['score'] < 60:
        recomendacoes.append({
            'prioridade': '🔴 URGENTE',
            'acao': 'Reunião de alinhamento',
            'descricao': f"Saúde da release em {saude['score']:.0f}%. Convocar reunião com Tech Lead para revisar escopo.",
            'cards': [],
            'impacto': 'Alto'
        })
    
    return recomendacoes


def analisar_gargalo_qa(df: pd.DataFrame, num_qas: int = 2) -> Dict[str, Any]:
    """
    Analisa gargalo de validação baseado na capacidade do time de QA.
    
    Args:
        df: DataFrame com os dados
        num_qas: Número de QAs no time
        
    Returns:
        Análise de capacidade e gargalo
    """
    # Status que indicam "aguardando QA"
    status_aguardando_qa = ['AGUARDANDO VALIDAÇÃO', 'EM REVISÃO', 'QA', 'Tarefas pendentes']
    
    df_aguardando = df[df['status'].isin(status_aguardando_qa)]
    
    # Estimar capacidade diária por QA (em SP)
    capacidade_diaria_qa = 5  # SP por QA por dia
    capacidade_total_diaria = capacidade_diaria_qa * num_qas
    
    # Total de SP aguardando validação
    sp_aguardando = df_aguardando['story_points'].sum()
    
    # Dias necessários para validar tudo
    dias_necessarios = sp_aguardando / capacidade_total_diaria if capacidade_total_diaria > 0 else 0
    
    # Cards por complexidade aguardando
    complexidade_aguardando = df_aguardando.groupby('complexidade_teste').size().to_dict()
    
    # Identificar sobrecarga
    if dias_necessarios > 3:
        status_gargalo = '🔴 Sobrecarga Crítica'
        recomendacao = 'Priorizar cards de menor complexidade ou adicionar recurso de QA'
    elif dias_necessarios > 2:
        status_gargalo = '🟡 Atenção'
        recomendacao = 'Monitorar progresso diário'
    else:
        status_gargalo = '🟢 Saudável'
        recomendacao = 'Capacidade adequada'
    
    return {
        'cards_aguardando': len(df_aguardando),
        'sp_aguardando': sp_aguardando,
        'dias_necessarios': round(dias_necessarios, 1),
        'capacidade_diaria': capacidade_total_diaria,
        'status': status_gargalo,
        'recomendacao': recomendacao,
        'por_complexidade': complexidade_aguardando,
        'df_aguardando': df_aguardando
    }


# ==============================================================================
# FUNÇÕES DE VISUALIZAÇÃO
# ==============================================================================

def criar_grafico_bugs_desenvolvedor(df: pd.DataFrame) -> go.Figure:
    """
    Cria gráfico de barras com quantidade de bugs por desenvolvedor.
    """
    bugs_por_dev = df.groupby('desenvolvedor')['bugs_encontrados'].sum().reset_index()
    bugs_por_dev = bugs_por_dev.sort_values('bugs_encontrados', ascending=True)
    
    fig = px.bar(
        bugs_por_dev,
        x='bugs_encontrados',
        y='desenvolvedor',
        orientation='h',
        title='🐛 Bugs por Desenvolvedor',
        labels={'bugs_encontrados': 'Quantidade de Bugs', 'desenvolvedor': 'Desenvolvedor'},
        color='bugs_encontrados',
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


def criar_grafico_distribuicao_tickets(df: pd.DataFrame) -> go.Figure:
    """
    Cria gráfico de pizza com distribuição de tipos de ticket.
    """
    distribuicao = df['tipo'].value_counts().reset_index()
    distribuicao.columns = ['tipo', 'quantidade']
    
    cores = {
        'FEATURE': '#4CAF50',
        'BUG': '#F44336',
        'HOTFIX': '#FF9800',
        'SUGESTÃO': '#2196F3'
    }
    
    fig = px.pie(
        distribuicao,
        values='quantidade',
        names='tipo',
        title='📊 Distribuição de Tickets',
        color='tipo',
        color_discrete_map=cores,
        hole=0.4  # Donut chart
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


def criar_grafico_janela_teste(df: pd.DataFrame) -> go.Figure:
    """
    Cria gráfico de barras horizontais mostrando a janela de teste por card.
    Usa o campo janela_testes do Jira quando disponível.
    """
    # Filtrar cards com janela de testes preenchida
    df_qa = df[df['janela_testes'].astype(str).str.strip() != ''].copy()
    
    if df_qa.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem dados de janela de teste disponíveis",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Converter janela_testes para número
    df_qa['janela_num'] = pd.to_numeric(df_qa['janela_testes'], errors='coerce').fillna(0).astype(int)
    
    # Ordenar por janela de teste
    df_qa = df_qa.sort_values('janela_num', ascending=False).head(20)
    
    # Definir cores baseadas na janela (vermelho = pouco tempo, verde = bastante tempo)
    cores = ['#F44336' if j < 3 else '#FF9800' if j < 5 else '#4CAF50' 
             for j in df_qa['janela_num']]
    
    fig = go.Figure(go.Bar(
        x=df_qa['janela_num'],
        y=df_qa['ticket_id'],
        orientation='h',
        marker_color=cores,
        text=df_qa['janela_num'].astype(str) + ' dias',
        textposition='outside'
    ))
    
    fig.update_layout(
        title='⏰ Janela de Teste por Card (dias até release)',
        xaxis_title='Dias disponíveis para QA',
        yaxis_title='Ticket',
        height=max(300, len(df_qa) * 30),
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False
    )
    
    # Adicionar linha de referência (3 dias = limite crítico)
    fig.add_vline(x=3, line_dash="dash", line_color="red", 
                  annotation_text="Limite crítico (3 dias)")
    
    return fig


def criar_grafico_maturidade_cards(df: pd.DataFrame) -> go.Figure:
    """
    Cria gráfico mostrando a maturidade (Fator K) de cada card.
    """
    df_features = df[df['tipo'] == 'FEATURE'].copy()
    
    if df_features.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="Sem features para análise de maturidade",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    df_features['fator_k'] = df_features.apply(
        lambda row: calcular_fator_k(row['story_points'], row['bugs_encontrados']),
        axis=1
    )
    
    # Limitar infinito para visualização
    df_features['fator_k_viz'] = df_features['fator_k'].apply(
        lambda x: 10 if x == float('inf') else min(x, 10)
    )
    
    df_features['classificacao'] = df_features['fator_k'].apply(
        lambda x: classificar_maturidade(x)['selo']
    )
    
    cores_maturidade = {
        'Gold': '#FFD700',
        'Silver': '#C0C0C0',
        'Bronze': '#CD7F32',
        'Risco': '#FF4444'
    }
    
    fig = px.bar(
        df_features,
        x='ticket_id',
        y='fator_k_viz',
        color='classificacao',
        color_discrete_map=cores_maturidade,
        title='🏆 Maturidade de Entrega (Fator K) por Feature',
        labels={'fator_k_viz': 'Fator K', 'ticket_id': 'Ticket'},
        hover_data=['story_points', 'bugs_encontrados', 'desenvolvedor']
    )
    
    # Adicionar linhas de referência para os selos
    fig.add_hline(y=3, line_dash="dot", line_color="gold", 
                  annotation_text="Gold (≥3)")
    fig.add_hline(y=2, line_dash="dot", line_color="silver", 
                  annotation_text="Silver (≥2)")
    fig.add_hline(y=1, line_dash="dot", line_color="#CD7F32", 
                  annotation_text="Bronze (≥1)")
    
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_tickangle=-45
    )
    
    return fig


def criar_tabela_detalhada(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria tabela detalhada com métricas calculadas para exibição.
    """
    df_tabela = df.copy()
    
    # Calcular Fator K
    df_tabela['fator_k'] = df_tabela.apply(
        lambda row: calcular_fator_k(row['story_points'], row['bugs_encontrados']),
        axis=1
    )
    
    # Classificar maturidade
    df_tabela['maturidade'] = df_tabela['fator_k'].apply(
        lambda x: classificar_maturidade(x)['emoji'] + ' ' + classificar_maturidade(x)['selo']
    )
    
    # Formatar Fator K para exibição
    df_tabela['fator_k_fmt'] = df_tabela['fator_k'].apply(
        lambda x: '∞ (Perfeito)' if x == float('inf') else f'{x:.2f}'
    )
    
    # Selecionar colunas para exibição
    colunas = ['ticket_id', 'titulo', 'tipo', 'status', 'projeto', 'desenvolvedor', 
               'qa_responsavel', 'story_points', 'bugs_encontrados', 'fator_k_fmt', 
               'maturidade', 'prioridade', 'complexidade_teste', 'janela_testes']
    
    # Filtrar apenas colunas que existem
    colunas_existentes = [c for c in colunas if c in df_tabela.columns]
    
    df_tabela = df_tabela[colunas_existentes]
    
    # Renomear colunas
    rename_map = {
        'ticket_id': 'Ticket', 'titulo': 'Título', 'tipo': 'Tipo', 
        'status': 'Status', 'projeto': 'Projeto', 'desenvolvedor': 'Dev',
        'qa_responsavel': 'QA', 'story_points': 'SP', 'bugs_encontrados': 'Bugs',
        'fator_k_fmt': 'Fator K', 'maturidade': 'Maturidade', 
        'prioridade': 'Prioridade', 'complexidade_teste': 'Complex. Teste',
        'janela_testes': 'Janela QA'
    }
    df_tabela = df_tabela.rename(columns=rename_map)
    
    return df_tabela


# ==============================================================================
# INTERFACE PRINCIPAL DO STREAMLIT
# ==============================================================================

def main():
    """
    Função principal que configura e executa o dashboard Streamlit.
    """
    
    # Configuração da página
    st.set_page_config(
        page_title="Jira Dashboard - Métricas de Qualidade",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS customizado para melhorar a aparência
    st.markdown("""
        <style>
        .metric-card {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }
        .selo-gold { color: #FFD700; font-size: 48px; }
        .selo-silver { color: #C0C0C0; font-size: 48px; }
        .selo-bronze { color: #CD7F32; font-size: 48px; }
        .selo-risco { color: #FF4444; font-size: 48px; }
        .stMetric {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # -------------------------------------------------------------------------
    # SIDEBAR - Filtros e Configurações
    # -------------------------------------------------------------------------
    
    with st.sidebar:
        st.title("⚙️ Configurações")
        
        st.markdown("---")
        
        # Seção de credenciais do Jira
        st.subheader("🔐 Credenciais Jira")
        
        jira_email = st.text_input(
            "Email Jira",
            key="jira_email",
            placeholder="seu.email@empresa.com",
            help="Email da sua conta Jira/Atlassian"
        )
        
        jira_token = st.text_input(
            "API Token",
            type="password",
            key="jira_token",
            placeholder="API Token do Atlassian",
            help="Gere em: id.atlassian.com/manage-profile/security/api-tokens"
        )
        
        # Mostrar status da conexão
        if verificar_credenciais_jira():
            st.success("✅ Credenciais configuradas")
        else:
            st.warning("⚠️ Usando dados mockados (PoC)")
        
        st.markdown("---")
        
        # Filtros
        st.subheader("🔍 Filtros")
        
        # Carregar dados para obter opções de filtro
        if 'dados' not in st.session_state:
            st.session_state.dados = gerar_dados_mockados()
        
        df = st.session_state.dados
        
        # Filtro de Projeto (se existir a coluna)
        if 'projeto' in df.columns:
            projetos_disponiveis = ["Todos"] + sorted(df['projeto'].unique().tolist())
            projeto_selecionado = st.selectbox(
                "Projeto",
                projetos_disponiveis,
                index=0,
                help="Selecione o projeto para filtrar"
            )
        else:
            projeto_selecionado = "Todos"
        
        # Filtro de Sprint
        sprints_disponiveis = ["Todas"] + sorted(df['sprint'].unique().tolist())
        sprint_selecionada = st.selectbox(
            "Sprint",
            sprints_disponiveis,
            index=0,
            help="Selecione a sprint para filtrar os dados"
        )
        
        # Filtro de Desenvolvedor
        devs_disponiveis = ["Todos"] + sorted(df['desenvolvedor'].unique().tolist())
        dev_selecionado = st.selectbox(
            "Desenvolvedor",
            devs_disponiveis,
            index=0,
            help="Selecione um desenvolvedor específico"
        )
        
        # Filtro de Tipo de Ticket
        tipos_disponiveis = ["Todos"] + sorted(df['tipo'].unique().tolist())
        tipo_selecionado = st.selectbox(
            "Tipo de Ticket",
            tipos_disponiveis,
            index=0,
            help="Filtre por tipo de ticket"
        )
        
        # Filtro de Status
        if 'status' in df.columns:
            status_disponiveis = ["Todos"] + sorted(df['status'].unique().tolist())
            status_selecionado = st.selectbox(
                "Status",
                status_disponiveis,
                index=0,
                help="Filtre por status do ticket"
            )
        else:
            status_selecionado = "Todos"
        
        st.markdown("---")
        
        # Configurações do Projeto Jira
        st.subheader("📁 Projetos Jira")
        
        projeto_jira = st.text_input(
            "Projetos (separados por vírgula)",
            value="SD, VALPROD, PB, QA",
            key="projeto_jira",
            help="Códigos dos projetos no Jira separados por vírgula"
        )
        
        # Configurações de Release
        st.subheader("📅 Configuração de Release")
        
        data_release_input = st.date_input(
            "Data da Próxima Release",
            value=datetime.now() + timedelta(days=10),
            help="Defina a data prevista para a próxima release"
        )
        
        st.markdown("---")
        
        # Botão para recarregar dados
        if st.button("🔄 Carregar Dados do Jira", use_container_width=True):
            if verificar_credenciais_jira():
                with st.spinner("Buscando dados do Jira..."):
                    data_release_dt = datetime.combine(data_release_input, datetime.min.time())
                    df_jira = buscar_e_transformar_dados_jira(projeto_jira, data_release_dt)
                    
                    if df_jira is not None and not df_jira.empty:
                        st.session_state.dados = df_jira
                        st.session_state.dados_reais = True
                        st.success(f"✅ {len(df_jira)} tickets carregados do Jira!")
                        st.rerun()
                    else:
                        st.error("Não foi possível carregar dados do Jira.")
            else:
                st.warning("Preencha as credenciais do Jira primeiro!")
        
        if st.button("📊 Usar Dados de Demonstração", use_container_width=True):
            st.session_state.dados = gerar_dados_mockados()
            st.session_state.dados_reais = False
            st.success("Dados de demonstração carregados!")
            st.rerun()
        
        st.markdown("---")
        st.caption("Dashboard v2.0 - NINA Tecnologia")
    
    # -------------------------------------------------------------------------
    # CORPO PRINCIPAL
    # -------------------------------------------------------------------------
    
    # Título e status
    st.title("📊 Jira Dashboard - Métricas de Qualidade e Entrega")
    
    # Indicador de fonte de dados
    if st.session_state.get('dados_reais', False):
        st.success("🟢 Conectado ao Jira - Dados Reais")
    else:
        st.warning("🟡 Modo Demonstração - Dados Simulados")
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if projeto_selecionado != "Todos" and 'projeto' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['projeto'] == projeto_selecionado]
    
    if sprint_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado['sprint'] == sprint_selecionada]
    
    if dev_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado['desenvolvedor'] == dev_selecionado]
    
    if tipo_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado['tipo'] == tipo_selecionado]
    
    if status_selecionado != "Todos" and 'status' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['status'] == status_selecionado]
    
    # Verificar se há dados após filtragem
    if df_filtrado.empty:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
        return
    
    # =========================================================================
    # PAINEL ESTRATÉGICO DE QA (NOVO)
    # =========================================================================
    
    # Calcular saúde da release
    saude = calcular_saude_release(df_filtrado)
    
    # Header com status da saúde
    st.markdown("---")
    col_saude1, col_saude2 = st.columns([1, 3])
    
    with col_saude1:
        st.markdown(f"""
        <div style="background-color: {saude['cor']}20; border-left: 5px solid {saude['cor']}; 
                    padding: 20px; border-radius: 10px; text-align: center;">
            <h1 style="margin: 0; font-size: 48px;">{saude['status'].split()[0]}</h1>
            <h3 style="margin: 5px 0;">{saude['status'].split()[1] if len(saude['status'].split()) > 1 else ''}</h3>
            <p style="font-size: 24px; margin: 0;"><b>Score: {saude['score']}/100</b></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_saude2:
        st.markdown("### 🎯 Resumo Executivo da Release")
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            st.metric("Fator K Médio", f"{saude['fator_k_medio']:.2f}")
        with col_m2:
            st.metric("Taxa de Bugs", f"{saude['taxa_bugs']:.1f}%")
        with col_m3:
            st.metric("Cards Aprovados", f"{saude['pct_aprovados']:.0f}%")
        with col_m4:
            analise_gono = analisar_go_no_go(df_filtrado)
            st.metric("Cards em Risco", analise_gono['total_no_go'] + analise_gono['total_risco'])
        
        if saude['motivos']:
            st.warning("**Pontos de Atenção:** " + " | ".join(saude['motivos']))
    
    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # TOP 3 RISCOS
    # -------------------------------------------------------------------------
    
    st.markdown("### 🚨 Top 3 Riscos da Release")
    
    riscos = gerar_top_riscos(df_filtrado)
    
    if riscos:
        cols_risco = st.columns(3)
        
        for i, risco in enumerate(riscos):
            with cols_risco[i]:
                cor_borda = '#dc3545' if risco['score'] >= 70 else '#ffc107' if risco['score'] >= 50 else '#28a745'
                
                st.markdown(f"""
                <div style="border: 2px solid {cor_borda}; border-radius: 10px; padding: 15px; 
                            background-color: {cor_borda}10; height: 200px;">
                    <h4 style="margin: 0;">{risco['decisao']}</h4>
                    <p style="font-weight: bold; margin: 5px 0;">{risco['ticket']}</p>
                    <p style="font-size: 12px; color: #666;">{risco['titulo']}</p>
                    <p><b>Score Risco:</b> {risco['score']}</p>
                    <p><b>Dev:</b> {risco['desenvolvedor']}</p>
                    <p style="font-size: 11px;">{'<br>'.join(risco['motivos'][:3])}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.success("✅ Nenhum risco crítico identificado!")
    
    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # ANÁLISE GO/NO-GO
    # -------------------------------------------------------------------------
    
    st.markdown("### 🚦 Análise Go/No-Go Automática")
    
    analise = analisar_go_no_go(df_filtrado)
    
    col_go1, col_go2, col_go3, col_go4 = st.columns(4)
    
    with col_go1:
        st.markdown(f"""
        <div style="background-color: #28a74520; padding: 15px; border-radius: 10px; text-align: center;">
            <h2 style="color: #28a745; margin: 0;">{analise['total_go']}</h2>
            <p>🟢 GO</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_go2:
        st.markdown(f"""
        <div style="background-color: #ffc10720; padding: 15px; border-radius: 10px; text-align: center;">
            <h2 style="color: #ffc107; margin: 0;">{analise['total_atencao']}</h2>
            <p>🟡 ATENÇÃO</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_go3:
        st.markdown(f"""
        <div style="background-color: #fd7e1420; padding: 15px; border-radius: 10px; text-align: center;">
            <h2 style="color: #fd7e14; margin: 0;">{analise['total_risco']}</h2>
            <p>🟠 RISCO ALTO</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_go4:
        st.markdown(f"""
        <div style="background-color: #dc354520; padding: 15px; border-radius: 10px; text-align: center;">
            <h2 style="color: #dc3545; margin: 0;">{analise['total_no_go']}</h2>
            <p>🔴 NO-GO</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Mostrar cards NO-GO
    if analise['total_no_go'] > 0:
        with st.expander(f"⚠️ Ver {analise['total_no_go']} cards marcados como NO-GO", expanded=True):
            df_no_go = analise['no_go'][['ticket_id', 'titulo', 'desenvolvedor', 'story_points', 
                                          'bugs_encontrados', 'complexidade_teste', 'score_risco']].copy()
            df_no_go.columns = ['Ticket', 'Título', 'Dev', 'SP', 'Bugs', 'Complexidade', 'Score Risco']
            st.dataframe(df_no_go, hide_index=True, use_container_width=True)
            
            st.error("""
            **Recomendação:** Estes cards devem ser removidos da release atual. 
            O risco acumulado (Baixo Fator K + Alta Complexidade + Janela curta) 
            compromete a qualidade da entrega.
            """)
    
    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # ANÁLISE DE GARGALO DO QA
    # -------------------------------------------------------------------------
    
    st.markdown("### 🔄 Análise de Gargalo de Validação (QA)")
    
    gargalo = analisar_gargalo_qa(df_filtrado)
    
    col_gar1, col_gar2 = st.columns([2, 1])
    
    with col_gar1:
        st.markdown(f"""
        <div style="border: 2px solid #6c757d; border-radius: 10px; padding: 20px;">
            <h4>{gargalo['status']}</h4>
            <p><b>Cards aguardando validação:</b> {gargalo['cards_aguardando']}</p>
            <p><b>Story Points na fila:</b> {gargalo['sp_aguardando']}</p>
            <p><b>Capacidade diária do QA:</b> {gargalo['capacidade_diaria']} SP/dia (2 QAs)</p>
            <p><b>Dias necessários para validar tudo:</b> {gargalo['dias_necessarios']} dias</p>
            <hr>
            <p><b>Recomendação:</b> {gargalo['recomendacao']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_gar2:
        if gargalo['por_complexidade']:
            st.markdown("**Por Complexidade:**")
            for comp, qtd in gargalo['por_complexidade'].items():
                emoji = '🔴' if comp in ['Alta', 'Muito Alta'] else '🟡' if comp == 'Média' else '🟢'
                st.markdown(f"{emoji} {comp}: **{qtd}** cards")
    
    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # AUDITORIA: RISCO DE BAIXA COBERTURA
    # -------------------------------------------------------------------------
    
    st.markdown("### 🔍 Auditoria CPFL - Cobertura de Testes")
    
    col_aud1, col_aud2 = st.columns(2)
    
    with col_aud1:
        st.markdown("#### ⚠️ Risco de Baixa Cobertura")
        st.caption("Cards com SP alto (≥5) que não geraram bugs - possível teste superficial")
        
        df_cobertura = analisar_risco_baixa_cobertura(df_filtrado)
        
        if not df_cobertura.empty:
            for _, row in df_cobertura.head(5).iterrows():
                st.warning(f"""
                **{row['ticket_id']}** - {row['story_points']} SP, 0 bugs  
                Dev: {row['desenvolvedor']} | Status: {row['status']}
                """)
        else:
            st.success("✅ Nenhum risco de baixa cobertura identificado")
    
    with col_aud2:
        st.markdown("#### 📅 Dívida Técnica de Teste")
        st.caption("Cards complexos que entraram tarde demais para validação adequada")
        
        df_divida = analisar_divida_tecnica_teste(df_filtrado)
        
        if not df_divida.empty:
            for _, row in df_divida.head(5).iterrows():
                st.error(f"""
                **{row['ticket_id']}** - {row['motivo_divida']}  
                Dev: {row['desenvolvedor']}
                """)
        else:
            st.success("✅ Nenhuma dívida técnica de teste identificada")
    
    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # RECOMENDAÇÕES TÉCNICAS
    # -------------------------------------------------------------------------
    
    st.markdown("### 💡 Recomendações Técnicas para o Tech Lead")
    
    recomendacoes = gerar_recomendacoes(df_filtrado)
    
    if recomendacoes:
        for rec in recomendacoes:
            with st.expander(f"{rec['prioridade']} - {rec['acao']}", expanded=rec['prioridade'].startswith('🔴')):
                st.markdown(f"**{rec['descricao']}**")
                st.markdown(f"*Impacto: {rec['impacto']}*")
                
                if rec['cards']:
                    st.markdown("**Cards afetados:**")
                    st.code(", ".join(rec['cards']))
    else:
        st.success("✅ Nenhuma recomendação urgente no momento!")
    
    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # PERFORMANCE DE ENGENHARIA
    # -------------------------------------------------------------------------
    
    st.markdown("### 👨‍💻 Performance de Engenharia (por Desenvolvedor)")
    
    perf_dev = analisar_performance_dev(df_filtrado)
    
    col_perf1, col_perf2 = st.columns([2, 1])
    
    with col_perf1:
        # Gráfico de performance
        fig_perf = px.bar(
            perf_dev,
            x='Desenvolvedor',
            y='Fator K Médio',
            color='Performance',
            color_discrete_map={
                '🟢 Excelente': '#28a745',
                '🟡 Bom': '#ffc107',
                '🟠 Atenção': '#fd7e14',
                '🔴 Crítico': '#dc3545'
            },
            title='Fator K Médio por Desenvolvedor'
        )
        fig_perf.add_hline(y=2, line_dash="dash", line_color="gray", 
                          annotation_text="Meta (Fator K ≥ 2)")
        st.plotly_chart(fig_perf, use_container_width=True)
    
    with col_perf2:
        st.markdown("**Legenda:**")
        st.markdown("- 🟢 **Excelente:** FK ≥ 3")
        st.markdown("- 🟡 **Bom:** FK ≥ 2")
        st.markdown("- 🟠 **Atenção:** FK ≥ 1")
        st.markdown("- 🔴 **Crítico:** FK < 1")
        
        st.markdown("---")
        
        # Devs que precisam de suporte
        devs_atencao = perf_dev[perf_dev['Performance'].str.contains('Crítico|Atenção')]
        if not devs_atencao.empty:
            st.markdown("**🎯 Sugerir mentoria para:**")
            for _, dev in devs_atencao.iterrows():
                st.markdown(f"- {dev['Desenvolvedor']} (FK: {dev['Fator K Médio']:.2f})")
    
    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # MÉTRICAS PRINCIPAIS (Cards no topo)
    # -------------------------------------------------------------------------
    
    st.markdown("### 📈 Métricas Gerais")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Métrica 1: Total de Tickets
    with col1:
        st.metric(
            label="📋 Total de Tickets",
            value=len(df_filtrado),
            delta=f"{len(df_filtrado) - len(df)}" if sprint_selecionada != "Todas" else None
        )
    
    # Métrica 2: Story Points Totais
    with col2:
        total_sp = df_filtrado['story_points'].sum()
        st.metric(
            label="📊 Story Points",
            value=total_sp
        )
    
    # Métrica 3: Total de Bugs
    with col3:
        total_bugs = df_filtrado['bugs_encontrados'].sum()
        st.metric(
            label="🐛 Bugs Encontrados",
            value=total_bugs,
            delta=None,
            delta_color="inverse"
        )
    
    # Métrica 4: Dias até Release
    with col4:
        dias_release = calcular_dias_para_release(
            datetime.combine(data_release_input, datetime.min.time())
        )
        st.metric(
            label="📅 Dias até Release",
            value=dias_release,
            delta="urgente!" if dias_release <= 3 else None,
            delta_color="inverse" if dias_release <= 3 else "normal"
        )
    
    # Métrica 5: Fator K Médio
    with col5:
        # Calcular Fator K médio (apenas para cards com bugs > 0)
        df_com_bugs = df_filtrado[df_filtrado['bugs_encontrados'] > 0]
        if not df_com_bugs.empty:
            fator_k_medio = df_com_bugs.apply(
                lambda row: calcular_fator_k(row['story_points'], row['bugs_encontrados']),
                axis=1
            ).mean()
            classificacao_media = classificar_maturidade(fator_k_medio)
            st.metric(
                label=f"{classificacao_media['emoji']} Fator K Médio",
                value=f"{fator_k_medio:.2f}",
                delta=classificacao_media['selo']
            )
        else:
            st.metric(
                label="🥇 Fator K Médio",
                value="∞",
                delta="Gold - Sem bugs!"
            )
    
    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # MATURIDADE DE ENTREGA (Fator K)
    # -------------------------------------------------------------------------
    
    st.markdown("### 🏆 Maturidade de Entrega (Fator K)")
    
    col_mat1, col_mat2 = st.columns([2, 1])
    
    with col_mat1:
        fig_maturidade = criar_grafico_maturidade_cards(df_filtrado)
        st.plotly_chart(fig_maturidade, width='stretch')
    
    with col_mat2:
        st.markdown("""
        #### 📖 Como interpretar o Fator K
        
        **Fórmula:** `SP / (Bugs × 1.5)`
        
        | Selo | Fator K | Significado |
        |------|---------|-------------|
        | 🥇 Gold | ≥ 3.0 | Excelente qualidade |
        | 🥈 Silver | ≥ 2.0 | Boa qualidade |
        | 🥉 Bronze | ≥ 1.0 | Qualidade aceitável |
        | ⚠️ Risco | < 1.0 | Necessita atenção |
        
        **Dica:** Cards com Fator K ∞ não tiveram bugs!
        """)
    
    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # GRÁFICOS PRINCIPAIS
    # -------------------------------------------------------------------------
    
    st.markdown("### 📊 Análise Visual")
    
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        fig_bugs = criar_grafico_bugs_desenvolvedor(df_filtrado)
        st.plotly_chart(fig_bugs, width='stretch')
    
    with col_graf2:
        fig_dist = criar_grafico_distribuicao_tickets(df_filtrado)
        st.plotly_chart(fig_dist, width='stretch')
    
    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # JANELA DE TESTE (Métrica Nova para Tech Lead)
    # -------------------------------------------------------------------------
    
    st.markdown("### ⏰ Janela de Teste (Entrega Dev → Release)")
    
    st.info("""
    💡 **Para o Tech Lead:** Este gráfico mostra quantos dias cada card tem disponível 
    para testes entre a entrega do Dev e a Release. Use para cobrar entregas mais cedo 
    e evitar esmagar o QA no final da sprint!
    """)
    
    fig_janela = criar_grafico_janela_teste(df_filtrado)
    st.plotly_chart(fig_janela, width='stretch')
    
    # Alertas de janela crítica
    df_qa = df_filtrado[df_filtrado['janela_testes'].astype(str).str.strip() != ''].copy()
    if not df_qa.empty:
        df_qa['janela_num'] = pd.to_numeric(df_qa['janela_testes'], errors='coerce').fillna(0).astype(int)
        tickets_criticos = df_qa[df_qa['janela_num'] < 3]
        if not tickets_criticos.empty:
            st.error(f"""
            ⚠️ **ATENÇÃO:** {len(tickets_criticos)} ticket(s) com janela de teste crítica (< 3 dias)!
            
            Tickets: {', '.join(tickets_criticos['ticket_id'].tolist())}
            """)
    
    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # TABELA DETALHADA
    # -------------------------------------------------------------------------
    
    st.markdown("### 📋 Visão Detalhada dos Tickets")
    
    # Toggle para mostrar/ocultar tabela
    if st.checkbox("Mostrar tabela completa", value=True):
        df_tabela = criar_tabela_detalhada(df_filtrado)
        
        # Configurar a tabela com destaque condicional
        st.dataframe(
            df_tabela,
            width='stretch',
            hide_index=True,
            height=400
        )
        
        # Botão para download
        csv = df_tabela.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"metricas_jira_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # -------------------------------------------------------------------------
    # FOOTER
    # -------------------------------------------------------------------------
    
    st.markdown("---")
    st.caption(
        f"🕐 Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | "
        f"Modo: {'🟢 Jira Real' if verificar_credenciais_jira() else '🟡 Dados Mockados (PoC)'}"
    )


# ==============================================================================
# PONTO DE ENTRADA
# ==============================================================================

if __name__ == "__main__":
    main()
