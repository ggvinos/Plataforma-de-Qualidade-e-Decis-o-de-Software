"""
================================================================================
JIRA DASHBOARD v5.0 - MÉTRICAS ISTQB/CTFL PARA TOMADA DE DECISÃO
================================================================================
- Totalmente em português brasileiro
- Tooltips explicativos em todas as métricas
- Aba de Liderança expandida para decisões estratégicas
- Compartilhamento via link externo
- Textos em terceira pessoa

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
import urllib.parse

# Carregar .env se existir
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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
        "descricao": "Percentual de defeitos encontrados pelo QA antes da produção. Mede a eficácia do time de testes.",
        "formula": "DDP = (Bugs em QA / Total de Bugs) × 100",
        "interpretacao": {
            "≥85%": "Excelente - QA muito eficaz",
            "70-84%": "Bom - Processo funcionando",
            "50-69%": "Regular - Precisa melhorar",
            "<50%": "Crítico - Muitos bugs escapando"
        },
        "fonte": "ISTQB Foundation Level - Test Metrics"
    },
    "fpy": {
        "titulo": "FPY - First Pass Yield",
        "descricao": "Percentual de cards aprovados na primeira validação, sem bugs. Indica qualidade do desenvolvimento.",
        "formula": "FPY = (Cards sem bugs / Total de cards) × 100",
        "interpretacao": {
            "≥80%": "Excelente - Código de alta qualidade",
            "60-79%": "Bom - Dentro do esperado",
            "40-59%": "Regular - Revisar práticas",
            "<40%": "Crítico - Alto retrabalho"
        },
        "fonte": "Six Sigma / Lean Manufacturing adaptado para software"
    },
    "mttr": {
        "titulo": "MTTR - Mean Time To Repair",
        "descricao": "Tempo médio para corrigir um bug após identificado. Quanto menor, mais ágil o time.",
        "formula": "MTTR = Σ(Tempo de correção) / Nº de bugs",
        "interpretacao": {
            "≤1 dia": "Excelente resposta",
            "2-3 dias": "Tempo aceitável",
            "4-7 dias": "Precisa melhorar",
            ">7 dias": "Gargalo crítico"
        },
        "fonte": "ITIL / DevOps Metrics"
    },
    "lead_time": {
        "titulo": "Lead Time",
        "descricao": "Tempo total desde a criação do card até sua conclusão. Inclui desenvolvimento, code review e QA.",
        "formula": "Lead Time = Data Conclusão - Data Criação",
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
        "descricao": "Pontuação composta que avalia a saúde geral da release considerando múltiplos fatores.",
        "formula": "HS = (Conclusão×30 + DDP×25 + FPY×20 + Gargalos×15 + LeadTime×10) / 100",
        "interpretacao": {
            "≥75": "🟢 Saudável - Release pode seguir",
            "50-74": "🟡 Atenção - Monitorar riscos",
            "25-49": "🟠 Alerta - Ação necessária",
            "<25": "🔴 Crítico - Avaliar adiamento"
        },
        "fonte": "Composite Score baseado em ISTQB Test Process Improvement"
    },
    "defect_density": {
        "titulo": "Densidade de Defeitos",
        "descricao": "Quantidade de bugs por Story Point. Indica a taxa de defeitos relativa ao tamanho.",
        "formula": "DD = Total de Bugs / Total de SP",
        "interpretacao": {
            "≤0.2": "Baixa densidade - Excelente",
            "0.21-0.5": "Densidade aceitável",
            "0.51-1.0": "Densidade alta - Atenção",
            ">1.0": "Crítico - Muitos bugs/SP"
        },
        "fonte": "IEEE 982.1 - Software Quality Metrics"
    },
    "throughput": {
        "titulo": "Throughput (Vazão)",
        "descricao": "Quantidade de cards/SP concluídos por período. Indica a capacidade de entrega do time.",
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
        "descricao": "Quantidade de cards em andamento simultaneamente. WIP alto pode indicar gargalos.",
        "formula": "WIP = Cards não concluídos e não no backlog",
        "interpretacao": {
            "≤ Capacidade": "Fluxo saudável",
            "> Capacidade": "Sobrecarga - Risco de atrasos"
        },
        "fonte": "Kanban / Little's Law"
    }
}

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

CUSTOM_FIELDS = {
    "story_points": "customfield_11257",  # Campo correto de Story Points
    "story_points_alt": "customfield_10016",  # Campo alternativo
    "sprint": "customfield_10020",
    "bugs_encontrados": "customfield_11157",
    "dias_ate_release": "customfield_11357",
    "janela_testes": "customfield_11358",
    "complexidade_teste": "customfield_11290",
    "qa_responsavel": "customfield_10487",
    "qa_array": "customfield_10784",
    "desenvolvedor": "customfield_10455",
    "desenvolvedor_array": "customfield_10785",
    # Novos campos baseados no documento
    "produto": "customfield_10XXX",  # Ajustar ID real - Produto (NinaChat, Plataforma, etc.)
    "cliente": "customfield_10YYY",  # Ajustar ID real - Cliente
    "ambiente": "customfield_10ZZZ",  # Ajustar ID real - Ambiente (Produção, Homolog)
    "maturidade": "customfield_10WWW",  # Ajustar ID real - Status de Maturidade
    "work_type_id": "customfield_10VVV",  # Work type id (10200=Hotfix, 10364=Hotfeature)
}

# Mapeamento de Work Type ID conforme documento
WORK_TYPE_MAP = {
    "10009": "Tarefa",
    "10011": "Bug",
    "10463": "Refatoração",
    "10200": "Hotfix",
    "10364": "Hotfeature",
    "10199": "Impeditivo de entrega",
}

STATUS_FLOW = {
    "backlog": ["Backlog", "To Do", "Tarefas pendentes"],
    "development": ["Em andamento"],
    "code_review": ["EM REVISÃO"],
    "waiting_qa": ["AGUARDANDO VALIDAÇÃO"],
    "testing": ["EM VALIDAÇÃO"],
    "done": ["Concluído"],
    "blocked": ["IMPEDIDO"],
    "rework": ["REPROVADO"],  # Separado para métricas de retrabalho
    "deferred": ["Validado - Adiado", "DESCARTADO"],
}

MATURIDADE = {
    "Gold": {"min_fk": 3.0, "cor": "#22c55e", "emoji": "🥇", "desc": "Excelente"},
    "Silver": {"min_fk": 2.0, "cor": "#eab308", "emoji": "🥈", "desc": "Bom"},
    "Bronze": {"min_fk": 1.0, "cor": "#f97316", "emoji": "🥉", "desc": "Regular"},
    "Risco": {"min_fk": 0.01, "cor": "#ef4444", "emoji": "⚠️", "desc": "Atenção"},
    "Sem SP": {"min_fk": -1, "cor": "#9ca3af", "emoji": "📊", "desc": "Sem dados de SP"},
}

# Nomes traduzidos para status
STATUS_NOMES = {
    "backlog": "Backlog",
    "development": "Desenvolvimento",
    "code_review": "Revisão de Código",
    "waiting_qa": "Aguardando QA",
    "testing": "Em Validação",
    "done": "Concluído",
    "blocked": "Bloqueado",
    "rework": "Reprovado/Retrabalho",
    "deferred": "Adiado",
    "unknown": "Desconhecido"
}

# ==============================================================================
# UTILIDADES
# ==============================================================================

def link_jira(ticket_id: str) -> str:
    return f"{JIRA_BASE_URL}/browse/{ticket_id}"


def link_html(ticket_id: str, texto: str = None) -> str:
    url = link_jira(ticket_id)
    display = texto or ticket_id
    return f'<a href="{url}" target="_blank" style="color: #6366f1; text-decoration: none; font-weight: 600;">🔗 {display}</a>'


def formatar_duracao(dias: float) -> str:
    if dias < 1:
        return f"{int(dias * 24)}h"
    elif dias < 7:
        return f"{dias:.1f} dias"
    else:
        return f"{dias/7:.1f} semanas"


def extrair_campo_texto(fields: Dict, campo: str, default: str = 'N/A') -> str:
    """Extrai valor de texto de um campo do Jira (pode ser dict, list ou string)."""
    if not campo:
        return default
    valor = fields.get(campo)
    if valor is None:
        return default
    if isinstance(valor, dict):
        return valor.get('value', valor.get('name', valor.get('displayName', default)))
    if isinstance(valor, list) and valor:
        primeiro = valor[0]
        if isinstance(primeiro, dict):
            return primeiro.get('value', primeiro.get('name', primeiro.get('displayName', default)))
        return str(primeiro)
    return str(valor) if valor else default


def extrair_maturidade_cor(texto: str) -> str:
    """Extrai cor do status de maturidade baseado no emoji/texto."""
    texto_lower = texto.lower()
    if '🟢' in texto or 'excelente' in texto_lower:
        return 'green'
    elif '🟡' in texto or 'estável' in texto_lower or 'estavel' in texto_lower:
        return 'yellow'
    elif '🔴' in texto or 'crítico' in texto_lower or 'critico' in texto_lower:
        return 'red'
    return 'blue'


def mostrar_tooltip(metrica_key: str):
    """Mostra tooltip compacto com informações da métrica (hover)."""
    if metrica_key not in TOOLTIPS:
        return
    
    t = TOOLTIPS[metrica_key]
    
    # Versão compacta: descrição curta, fórmula e detalhes no help
    descricao_curta = t['descricao'].split('.')[0] + '.'
    detalhes_help = f"**{t['titulo']}**\n\n{t['descricao']}\n\n**Fórmula:** {t['formula']}\n\n**Referência:** {t['fonte']}"
    st.caption(f"ℹ️ {descricao_curta}", help=detalhes_help)


def gerar_link_compartilhamento() -> str:
    """Gera URL para compartilhamento do dashboard com parâmetros atuais."""
    params = {}
    if 'projeto' in st.session_state:
        params['projeto'] = st.session_state.projeto
    if 'filtro_qa' in st.session_state:
        params['qa'] = st.session_state.filtro_qa
    if 'filtro_dev' in st.session_state:
        params['dev'] = st.session_state.filtro_dev
    
    base_url = "http://localhost:8501"  # Mudar para URL real quando deployado
    if params:
        return f"{base_url}?{urllib.parse.urlencode(params)}"
    return base_url


# ==============================================================================
# DESIGN SYSTEM NINA DARK v6.0 - PALETA UNIFICADA
# ==============================================================================

# Paleta de cores PADRONIZADA - SEM VARIAÇÕES
CORES = {
    # Backgrounds (hierarquia clara)
    'bg_principal': '#0e1117',      # Fundo principal da página
    'bg_sidebar': '#111827',         # Sidebar
    'bg_card': '#1f2937',            # Cards, containers, gráficos
    'bg_hover': '#374151',           # Estados hover
    'bg_input': '#1f2937',           # Inputs, selects
    
    # Textos (contraste garantido)
    'texto_primario': '#ffffff',     # Texto principal - máximo contraste
    'texto_secundario': '#d1d5db',   # Texto secundário - bom contraste
    'texto_desabilitado': '#6b7280', # Texto desabilitado
    
    # Bordas
    'borda': '#374151',              # Bordas e separadores
    'borda_sutil': '#2a2a2a',        # Bordas mais sutis
    
    # Cores de destaque
    'nina_red': '#AF0C37',
    'nina_red_hover': '#d40f43',
    
    # Cores semânticas
    'verde': '#22c55e',
    'amarelo': '#eab308',
    'vermelho': '#ef4444',
    'azul': '#3b82f6',
}


def aplicar_tema_plotly(fig):
    """
    Aplica tema DARK padronizado ao gráfico Plotly.
    Fundo igual aos cards, grid discreto, tooltips legíveis.
    """
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor=CORES['bg_card'],
        plot_bgcolor=CORES['bg_card'],
        font=dict(
            color=CORES['texto_primario'],
            size=12
        ),
        title_font=dict(
            color=CORES['texto_primario'],
            size=16
        ),
        legend=dict(
            bgcolor=CORES['bg_card'],
            font=dict(color=CORES['texto_primario']),
            bordercolor=CORES['borda']
        ),
        xaxis=dict(
            gridcolor=CORES['borda'],
            linecolor=CORES['borda'],
            tickfont=dict(color=CORES['texto_primario']),
            title_font=dict(color=CORES['texto_primario']),
            zerolinecolor=CORES['borda']
        ),
        yaxis=dict(
            gridcolor=CORES['borda'],
            linecolor=CORES['borda'],
            tickfont=dict(color=CORES['texto_primario']),
            title_font=dict(color=CORES['texto_primario']),
            zerolinecolor=CORES['borda']
        ),
        # TOOLTIP LEGÍVEL - fundo escuro, texto branco
        hoverlabel=dict(
            bgcolor=CORES['bg_card'],
            font_size=13,
            font_color=CORES['texto_primario'],
            bordercolor=CORES['borda']
        ),
        margin=dict(t=40, b=40, l=40, r=40)
    )
    return fig


def plotly_chart_themed(fig, **kwargs):
    """Wrapper para st.plotly_chart que aplica tema dark padronizado."""
    aplicar_tema_plotly(fig)
    st.plotly_chart(fig, **kwargs)


def aplicar_estilos():
    """
    CSS MINIMALISTA - Usa tema padrão do Streamlit (claro)
    Apenas customizações essenciais para branding NINA
    """
    
    css = f"""
    <style>
    /* ==============================================
       NINA - CSS MINIMALISTA (TEMA CLARO)
       ============================================== */
    
    /* Ocultar elementos desnecessários */
    .stDeployButton,
    [data-testid="stDeployButton"],
    #MainMenu {{
        display: none !important;
    }}
    
    /* Botões com cor NINA */
    .stButton > button {{
        background-color: {CORES['nina_red']} !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
    }}
    
    .stButton > button:hover {{
        background-color: {CORES['nina_red_hover']} !important;
    }}
    
    /* Tab selecionada com cor NINA */
    .stTabs [aria-selected="true"] {{
        background-color: {CORES['nina_red']} !important;
        color: #ffffff !important;
    }}
    
    /* Header com logo centralizada */
    .nina-header {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px 0 30px 0;
        border-bottom: 2px solid {CORES['nina_red']};
        margin-bottom: 20px;
    }}
    
    .nina-header svg {{
        fill: {CORES['nina_red']};
    }}
    
    .nina-header-title {{
        font-size: 28px;
        font-weight: 700;
        color: #1f2937;
        margin-top: 12px;
    }}
    
    .nina-header-subtitle {{
        font-size: 14px;
        color: #6b7280;
        margin-top: 4px;
    }}
    
    /* Cards customizados */
    .nina-card {{
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 16px;
    }}
    
    .nina-card-green {{ border-left: 4px solid {CORES['verde']}; }}
    .nina-card-yellow {{ border-left: 4px solid {CORES['amarelo']}; }}
    .nina-card-red {{ border-left: 4px solid {CORES['vermelho']}; }}
    .nina-card-nina {{ border-left: 4px solid {CORES['nina_red']}; }}
    
    /* Alertas customizados */
    .nina-alert {{
        background-color: #f9fafb;
        padding: 14px 18px;
        border-radius: 8px;
    }}
    
    .nina-alert-critical {{ border-left: 4px solid {CORES['vermelho']}; }}
    .nina-alert-warning {{ border-left: 4px solid {CORES['amarelo']}; }}
    .nina-alert-success {{ border-left: 4px solid {CORES['verde']}; }}
    .nina-alert-info {{ border-left: 4px solid {CORES['azul']}; }}
    
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)


# ==============================================================================
# CONEXÃO JIRA
# ==============================================================================

def verificar_credenciais() -> bool:
    email = st.session_state.get("jira_email") or os.getenv("JIRA_EMAIL")
    token = st.session_state.get("jira_token") or os.getenv("JIRA_TOKEN")
    return bool(email and token)


def get_credenciais() -> Tuple[str, str]:
    email = st.session_state.get("jira_email") or os.getenv("JIRA_EMAIL")
    token = st.session_state.get("jira_token") or os.getenv("JIRA_TOKEN")
    return email, token


def buscar_jira(jql: str, expand: str = "") -> Optional[List[Dict]]:
    if not verificar_credenciais():
        return None
    
    email, token = get_credenciais()
    url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    
    fields = ["key", "summary", "status", "issuetype", "assignee", "created", "updated",
              "resolutiondate", "priority", "project", "labels", "components",
              "comment"] + list(CUSTOM_FIELDS.values())
    
    payload = {"jql": jql, "maxResults": 200, "fields": fields}
    if expand:
        payload["expand"] = expand
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), auth=(email, token))
        response.raise_for_status()
        return response.json().get("issues", [])
    except Exception as e:
        st.error(f"Erro ao conectar com Jira: {e}")
        return None


def buscar_comentarios(ticket_id: str) -> List[Dict]:
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
    dados = []
    
    for issue in issues:
        f = issue.get('fields', {})
        
        tipo_original = f.get('issuetype', {}).get('name', 'Desconhecido')
        tipo = "TAREFA"
        for t, nomes in [("HOTFIX", ["Hotfix", "Hotfeature"]), ("BUG", ["Bug", "Impeditivo"]),
                         ("TAREFA", ["Tarefa", "Task", "Subtarefa"]), ("SUGESTÃO", ["Sugestão"])]:
            if any(n in tipo_original for n in nomes):
                tipo = t
                break
        
        projeto = f.get('project', {}).get('key', 'N/A')
        
        dev = 'Não atribuído'
        if f.get('assignee'):
            dev = f['assignee'].get('displayName', dev)
        
        # Tentar ler SP de ambos os campos (principal e alternativo)
        sp = f.get(CUSTOM_FIELDS['story_points']) or f.get(CUSTOM_FIELDS.get('story_points_alt', '')) or 0
        
        sprint_f = f.get(CUSTOM_FIELDS['sprint'], [])
        sprint = sprint_f[-1].get('name', 'Sem Sprint') if sprint_f else 'Sem Sprint'
        
        status = f.get('status', {}).get('name', 'Desconhecido')
        
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
        
        comentarios = f.get('comment', {}).get('comments', [])
        num_comentarios = len(comentarios)
        ultimos_comentarios = []
        for c in comentarios[-3:]:
            autor = c.get('author', {}).get('displayName', 'Anônimo')
            corpo = c.get('body', {})
            if isinstance(corpo, dict):
                texto = ""
                for content in corpo.get('content', []):
                    for item in content.get('content', []):
                        if item.get('type') == 'text':
                            texto += item.get('text', '')
            else:
                texto = str(corpo)
            ultimos_comentarios.append({'autor': autor, 'texto': texto[:200]})
        
        ticket_id = issue.get('key', f"ID-{issue.get('id', '?')}")
        
        dados.append({
            'ticket_id': ticket_id,
            'link': link_jira(ticket_id),
            'titulo': f.get('summary', 'Sem título'),
            'tipo': tipo,
            'tipo_original': tipo_original,
            'status': status,
            'status_cat': status_cat,
            'projeto': projeto,
            'desenvolvedor': dev,
            'qa': qa,
            'sp': sp,
            'bugs': bugs,
            'sprint': sprint,
            'prioridade': f.get('priority', {}).get('name', 'Média'),
            'complexidade': complexidade,
            'janela_testes': janela,
            'criado': criado,
            'atualizado': atualizado,
            'data_release': data_release,
            'dias_em_status': (datetime.now() - atualizado).days,
            'lead_time': (atualizado - criado).days,
            'num_comentarios': num_comentarios,
            'comentarios': ultimos_comentarios,
            # Novos campos conforme documento
            'produto': extrair_campo_texto(f, CUSTOM_FIELDS.get('produto'), 'N/A'),
            'cliente': extrair_campo_texto(f, CUSTOM_FIELDS.get('cliente'), 'N/A'),
            'ambiente': extrair_campo_texto(f, CUSTOM_FIELDS.get('ambiente'), 'N/A'),
            'maturidade_jira': extrair_campo_texto(f, CUSTOM_FIELDS.get('maturidade'), 'N/A'),
            'is_hotfix': tipo in ['HOTFIX', 'Hotfix', 'Hotfeature'],
            'is_bug': tipo in ['BUG', 'Bug'],
            'is_producao': 'produção' in str(extrair_campo_texto(f, CUSTOM_FIELDS.get('ambiente'), '')).lower(),
        })
    
    return pd.DataFrame(dados)


def gerar_dados_mock(projeto: str = "SD") -> pd.DataFrame:
    """Gera dados realistas para demonstração."""
    
    devs = ["Augusto Oliveira", "Christopher Krauss de Carvalho", "Suyan Moriel", 
            "Daniel Marques", "Elinton Dozol Machado", "Carlos Daniel de Souza Cordeiro",
            "Cristian Yamamoto", "João Pedro Menegali"]
    
    qas = ["Vinicios Ferreira", "Vinicius Alves da Silva Neto", 
           "João Pedro Greif de Souza", "Eduardo Barbosa da Silva"]
    
    tipos = ["TAREFA", "BUG", "HOTFIX"]
    complexidades = ["Baixa", "Média", "Alta", "Muito Alta"]
    prioridades = ["Baixa", "Média", "Alta", "Muito Alta"]
    
    # Novos campos conforme documento
    produtos = ["NinaChat", "Plataforma", "HUB", "Checkin", "APP Paciente", "Flow"]
    clientes = ["Unimed_Litoral", "Prevencordis", "Mantevida", "Interno", "CAPS", "Clinica ABC"]
    ambientes = ["Produção", "Homologação", "Develop"]
    maturidades = ["🟢 EXCELENTE", "🟡 ESTÁVEL", "🔴 CRÍTICO", "N/A"]
    
    statuses = [
        ("Backlog", "backlog"),
        ("Em andamento", "development"),
        ("EM REVISÃO", "code_review"),
        ("AGUARDANDO VALIDAÇÃO", "waiting_qa"),
        ("EM VALIDAÇÃO", "testing"),
        ("Concluído", "done"),
        ("IMPEDIDO", "blocked"),
        ("REPROVADO", "rework"),  # Novo status para retrabalho
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
            # Novos campos
            'produto': random.choice(produtos),
            'cliente': random.choice(clientes),
            'ambiente': random.choices(ambientes, weights=[30, 50, 20])[0],
            'maturidade_jira': random.choices(maturidades, weights=[40, 35, 15, 10])[0],
            'is_hotfix': tipo == "HOTFIX",
            'is_bug': tipo == "BUG",
            'is_producao': random.random() < 0.3,
        })
    
    return pd.DataFrame(dados)


# ==============================================================================
# MÉTRICAS ISTQB/CTFL
# ==============================================================================

def calcular_fator_k(sp: int, bugs: int, rigor: float = 1.5) -> float:
    """Calcula Fator K. Retorna -1 se não há SP para indicar dados insuficientes."""
    if sp == 0:
        return -1  # Indica que não há dados de SP
    return round(sp / (bugs + 1) * rigor, 2)


def classificar_maturidade(fator_k: float, sp: int = 0, bugs: int = 0) -> Dict:
    """Classifica maturidade baseado no Fator K. Considera casos especiais."""
    # Caso especial: sem Story Points
    if fator_k == -1 or sp == 0:
        # Se não tem bugs, considerar neutro (sem dados suficientes)
        if bugs == 0:
            return {"selo": "Sem SP", **MATURIDADE["Sem SP"]}
        # Se só tem bugs e sem SP, é risco
        return {"selo": "Risco", **MATURIDADE["Risco"]}
    
    for selo, config in MATURIDADE.items():
        if selo == "Sem SP":
            continue  # Pular esse na iteração normal
        if fator_k >= config['min_fk']:
            return {"selo": selo, **config}
    return {"selo": "Risco", **MATURIDADE["Risco"]}


def calcular_ddp(df: pd.DataFrame) -> Dict:
    """Defect Detection Percentage - eficácia do QA."""
    bugs_qa = df['bugs'].sum()
    bugs_estimados_prod = max(1, len(df) * 0.05)  # Estimativa: 5% escapa
    
    total_bugs = bugs_qa + bugs_estimados_prod
    ddp = (bugs_qa / total_bugs * 100) if total_bugs > 0 else 100
    
    status = 'excellent' if ddp >= 85 else 'good' if ddp >= 70 else 'regular' if ddp >= 50 else 'poor'
    return {"valor": round(ddp, 1), "status": status, "bugs_qa": bugs_qa}


def calcular_first_pass_yield(df: pd.DataFrame) -> Dict:
    """First Pass Yield - cards aprovados de primeira."""
    total = len(df)
    if total == 0:
        return {"valor": 0, "status": "poor", "sem_bugs": 0, "total": 0}
    
    sem_bugs = len(df[df['bugs'] == 0])
    fpy = sem_bugs / total * 100
    
    status = 'excellent' if fpy >= 80 else 'good' if fpy >= 60 else 'regular' if fpy >= 40 else 'poor'
    return {"valor": round(fpy, 1), "status": status, "sem_bugs": sem_bugs, "total": total}


def calcular_defect_density(df: pd.DataFrame) -> Dict:
    """Densidade de defeitos por SP."""
    sp_total = df['sp'].sum()
    bugs_total = df['bugs'].sum()
    
    dd = bugs_total / sp_total if sp_total > 0 else 0
    return {"valor": round(dd, 2), "bugs": bugs_total, "sp": sp_total}


def calcular_mttr(df: pd.DataFrame) -> Dict:
    """Mean Time To Repair."""
    bugs_df = df[df['bugs'] > 0]
    if bugs_df.empty:
        return {"valor": 0, "cards_com_bugs": 0}
    
    tempo_medio = bugs_df['lead_time'].mean()
    return {"valor": round(tempo_medio, 1), "cards_com_bugs": len(bugs_df)}


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


def calcular_throughput(df: pd.DataFrame) -> Dict:
    """Vazão de cards concluídos."""
    concluidos = df[df['status_cat'] == 'done']
    return {
        "cards": len(concluidos),
        "sp": concluidos['sp'].sum(),
        "por_dia": round(len(concluidos) / 14, 1),  # Assumindo sprint de 2 semanas
    }


def calcular_wip(df: pd.DataFrame) -> Dict:
    """Work In Progress atual."""
    em_andamento = df[~df['status_cat'].isin(['backlog', 'done', 'deferred'])]
    return {
        "total": len(em_andamento),
        "development": len(df[df['status_cat'] == 'development']),
        "code_review": len(df[df['status_cat'] == 'code_review']),
        "waiting_qa": len(df[df['status_cat'] == 'waiting_qa']),
        "testing": len(df[df['status_cat'] == 'testing']),
        "blocked": len(df[df['status_cat'] == 'blocked']),
        "rework": len(df[df['status_cat'] == 'rework']),
    }


def calcular_taxa_retrabalho(df: pd.DataFrame) -> Dict:
    """Taxa de retrabalho - cards reprovados/que voltaram."""
    total_validados = len(df[df['status_cat'].isin(['done', 'testing', 'rework'])])
    reprovados = len(df[df['status_cat'] == 'rework'])
    cards_com_bugs = len(df[df['bugs'] > 0])
    
    taxa = (reprovados / total_validados * 100) if total_validados > 0 else 0
    taxa_bugs = (cards_com_bugs / len(df) * 100) if len(df) > 0 else 0
    
    return {
        "taxa": round(taxa, 1),
        "reprovados": reprovados,
        "total_validados": total_validados,
        "cards_com_bugs": cards_com_bugs,
        "taxa_bugs": round(taxa_bugs, 1),
    }


def calcular_hotfix_rate(df: pd.DataFrame) -> Dict:
    """Taxa de Hotfix - indica instabilidade do produto."""
    total = len(df)
    if total == 0:
        return {"taxa": 0, "hotfixes": 0, "bugs": 0, "total": 0}
    
    # Usar campo is_hotfix ou verificar pelo tipo
    if 'is_hotfix' in df.columns:
        hotfixes = len(df[df['is_hotfix'] == True])
    else:
        hotfixes = len(df[df['tipo'].isin(['HOTFIX', 'Hotfix', 'Hotfeature'])])
    
    if 'is_bug' in df.columns:
        bugs = len(df[df['is_bug'] == True])
    else:
        bugs = len(df[df['tipo'].isin(['BUG', 'Bug'])])
    
    taxa = ((hotfixes + bugs) / total * 100)
    
    return {
        "taxa": round(taxa, 1),
        "hotfixes": hotfixes,
        "bugs": bugs,
        "total": total,
    }


def calcular_metricas_por_produto(df: pd.DataFrame) -> pd.DataFrame:
    """Métricas agregadas por produto."""
    if 'produto' not in df.columns:
        return pd.DataFrame()
    
    produtos = df[df['produto'] != 'N/A']['produto'].unique()
    dados = []
    
    for produto in produtos:
        df_prod = df[df['produto'] == produto]
        if len(df_prod) == 0:
            continue
        hotfix = calcular_hotfix_rate(df_prod)
        fpy = calcular_first_pass_yield(df_prod)
        
        dados.append({
            'Produto': produto,
            'Cards': len(df_prod),
            'SP': df_prod['sp'].sum(),
            'Bugs': df_prod['bugs'].sum(),
            'Hotfixes': hotfix['hotfixes'],
            'FPY': f"{fpy['valor']}%",
            'Taxa Hotfix': f"{hotfix['taxa']}%",
        })
    
    if not dados:
        return pd.DataFrame()
    
    return pd.DataFrame(dados).sort_values('Cards', ascending=False)


def calcular_eficiencia_qa(df: pd.DataFrame) -> Dict:
    """
    Eficiência QA = Complexidade / Tempo ciclo / Bugs
    Métrica NINA - mede a produtividade do QA considerando a complexidade validada,
    o tempo gasto e a quantidade de bugs encontrados.
    """
    # Filtra cards que passaram pelo QA (testing ou done)
    cards_qa = df[df['status_cat'].isin(['testing', 'done', 'rework'])]
    
    if len(cards_qa) == 0:
        return {
            "valor": 0,
            "complexidade_total": 0,
            "tempo_ciclo_medio": 0,
            "bugs_total": 0,
            "classificacao": "Sem dados",
            "cor": "gray"
        }
    
    # Complexidade total (Story Points como proxy)
    complexidade_total = cards_qa['sp'].sum()
    
    # Tempo de ciclo médio em dias
    lead = calcular_lead_time(cards_qa)
    tempo_ciclo_medio = lead['medio'] if lead['medio'] > 0 else 1
    
    # Bugs encontrados
    bugs_total = cards_qa['bugs'].sum()
    
    # Cálculo da eficiência (quanto maior, melhor)
    # Se bugs = 0, consideramos como máxima eficiência de detecção
    if bugs_total == 0:
        # Sem bugs encontrados - pode indicar código limpo ou QA insuficiente
        if complexidade_total > 0:
            eficiencia = complexidade_total / tempo_ciclo_medio * 10  # Bonus por código limpo
        else:
            eficiencia = 0
    else:
        # Fórmula: (Complexidade / Tempo / Bugs) * 100 para escala legível
        eficiencia = (complexidade_total / tempo_ciclo_medio / bugs_total) * 100
    
    # Classificação baseada na tabela NINA
    if eficiencia >= 80:
        classificacao = "🟢 EXCELENTE"
        cor = "green"
    elif eficiencia >= 50:
        classificacao = "🟡 ESTÁVEL"
        cor = "yellow"
    elif eficiencia >= 30:
        classificacao = "🟠 ATENÇÃO"
        cor = "orange"
    else:
        classificacao = "🔴 CRÍTICO"
        cor = "red"
    
    return {
        "valor": round(eficiencia, 1),
        "complexidade_total": complexidade_total,
        "tempo_ciclo_medio": round(tempo_ciclo_medio, 1),
        "bugs_total": bugs_total,
        "classificacao": classificacao,
        "cor": cor
    }


def identificar_gargalos(df: pd.DataFrame) -> List[Dict]:
    """Identifica gargalos no fluxo."""
    gargalos = []
    
    limites = {
        'waiting_qa': {'esperado': 3, 'limite': 5},
        'code_review': {'esperado': 2, 'limite': 4},
        'development': {'esperado': 5, 'limite': 8},
    }
    
    for cat, lim in limites.items():
        cards_cat = df[df['status_cat'] == cat]
        if not cards_cat.empty:
            tempo_medio = cards_cat['dias_em_status'].mean()
            if tempo_medio > lim['limite'] or len(cards_cat) > 5:
                impacto = 'ALTO' if tempo_medio > lim['limite'] * 1.5 else 'MÉDIO'
                gargalos.append({
                    'categoria': cat,
                    'cards': len(cards_cat),
                    'atual': round(tempo_medio, 1),
                    'esperado': lim['esperado'],
                    'impacto': impacto,
                    'tickets': cards_cat['ticket_id'].tolist(),
                })
    
    return sorted(gargalos, key=lambda x: x['impacto'] == 'ALTO', reverse=True)


def avaliar_go_no_go(df: pd.DataFrame) -> Dict:
    """Avaliação Go/No-Go com base em métricas."""
    bloqueios = []
    alertas = []
    
    # Helper para extrair cards com título
    def extrair_cards_com_titulo(subset):
        return [{'id': row['ticket_id'], 'titulo': row.get('titulo', '')[:60]} for _, row in subset.iterrows()]
    
    # 1. Verifica cards bloqueados
    bloqueados = df[df['status_cat'] == 'blocked']
    if not bloqueados.empty:
        bloqueios.append({
            'tipo': 'blocked',
            'msg': f"{len(bloqueados)} card(s) bloqueado(s) - Resolver antes da release",
            'cards': extrair_cards_com_titulo(bloqueados)
        })
    
    # 2. Fila de QA muito grande
    fila_qa = df[df['status_cat'] == 'waiting_qa']
    if len(fila_qa) > 10:
        alertas.append({
            'tipo': 'queue',
            'msg': f"Fila de QA alta: {len(fila_qa)} cards aguardando validação",
            'cards': extrair_cards_com_titulo(fila_qa)
        })
    
    # 3. Cards críticos não concluídos
    criticos = df[(df['prioridade'].isin(['Alta', 'Muito Alta', 'Muito alto', 'Alto'])) & 
                  (df['status_cat'] != 'done')]
    if not criticos.empty:
        alertas.append({
            'tipo': 'priority',
            'msg': f"{len(criticos)} card(s) de alta prioridade ainda em andamento",
            'cards': extrair_cards_com_titulo(criticos)
        })
    
    # 4. FPY muito baixo
    fpy = calcular_first_pass_yield(df)
    if fpy['valor'] < 40:
        alertas.append({
            'tipo': 'quality',
            'msg': f"FPY baixo ({fpy['valor']}%) - Muitos bugs encontrados",
            'cards': []
        })
    
    # Health Score
    health = calcular_health_score(df)
    
    # Decisão baseada nas classificações NINA (sem bloqueio, apenas alertas)
    # 🟢 EXCELENTE, 🟡 ESTÁVEL, 🟠 ATENÇÃO, 🔴 CRÍTICO
    if bloqueios or health['score'] < 40:
        decisao = "🔴 ANÁLISE REQUERIDA"
        classe = "blocked"
    elif len(alertas) >= 3 or health['score'] < 50:
        decisao = "🟠 ATENÇÃO"
        classe = "warning"
    elif len(alertas) >= 1 or health['score'] < 70:
        decisao = "🟡 ESTÁVEL"
        classe = "stable"
    else:
        decisao = "🟢 EXCELENTE"
        classe = "approved"
    
    return {
        'decisao': decisao,
        'classe': classe,
        'bloqueios': bloqueios,
        'alertas': alertas,
        'health': health,
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
    fpy = calcular_first_pass_yield(df)
    score_fpy = min(20, fpy['valor'] * 0.2)
    detalhes['fpy'] = {'peso': 20, 'score': round(score_fpy, 1), 'valor': f"{fpy['valor']}%"}
    
    # 4. Gargalos (peso 15)
    gargalos = identificar_gargalos(df)
    penalidade_gargalos = len([g for g in gargalos if g['impacto'] == 'ALTO']) * 5
    score_gargalos = max(0, 15 - penalidade_gargalos)
    detalhes['gargalos'] = {'peso': 15, 'score': score_gargalos, 'valor': f"{len(gargalos)} encontrados"}
    
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
# ANÁLISES DETALHADAS
# ==============================================================================

def analisar_qa_detalhado(df: pd.DataFrame, qa_nome: str) -> Optional[Dict]:
    """Análise completa de um QA."""
    df_qa = df[df['qa'] == qa_nome]
    if df_qa.empty:
        return None
    
    validados = df_qa[df_qa['status_cat'] == 'done']
    em_fila = df_qa[df_qa['status_cat'] == 'waiting_qa']
    em_validacao = df_qa[df_qa['status_cat'] == 'testing']
    
    bugs_encontrados = df_qa['bugs'].sum()
    sp_protegidos = df_qa['sp'].sum()
    
    fpy = calcular_first_pass_yield(df_qa)
    ddp = calcular_ddp(df_qa)
    
    tempo_validacao = validados['lead_time'].mean() if not validados.empty else 0
    
    cards_problematicos = df_qa[df_qa['bugs'] >= 3].sort_values('bugs', ascending=False)
    
    mais_rapido = validados.nsmallest(3, 'lead_time') if not validados.empty else pd.DataFrame()
    mais_lento = validados.nlargest(3, 'lead_time') if not validados.empty else pd.DataFrame()
    
    por_complexidade = {}
    for comp in df_qa['complexidade'].unique():
        comp_df = df_qa[df_qa['complexidade'] == comp]
        por_complexidade[comp] = {
            'ticket_id': len(comp_df),
            'bugs': comp_df['bugs'].sum(),
            'lead_time': round(comp_df['lead_time'].mean(), 1) if not comp_df.empty else 0
        }
    
    return {
        'df': df_qa,
        'cards_total': len(df_qa),
        'validados': len(validados),
        'em_fila': len(em_fila),
        'em_validacao': len(em_validacao),
        'bugs_encontrados': bugs_encontrados,
        'bugs_evitados': bugs_encontrados,
        'sp_protegidos': sp_protegidos,
        'fpy': fpy,
        'ddp': ddp,
        'tempo_validacao': round(tempo_validacao, 1),
        'cards_problematicos': cards_problematicos,
        'mais_rapido': mais_rapido,
        'mais_lento': mais_lento,
        'por_complexidade': por_complexidade,
    }


def analisar_dev_detalhado(df: pd.DataFrame, dev_nome: str) -> Optional[Dict]:
    """Análise completa de um desenvolvedor."""
    df_dev = df[df['desenvolvedor'] == dev_nome]
    if df_dev.empty:
        return None
    
    sp_total = df_dev['sp'].sum()
    bugs_total = df_dev['bugs'].sum()
    
    fk_medio = calcular_fator_k(sp_total, bugs_total)
    maturidade = classificar_maturidade(fk_medio, sp_total, bugs_total)
    
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


# ==============================================================================
# COMPONENTES UI
# ==============================================================================

def mostrar_kpi_card(valor: str, titulo: str, cor: str = "blue", subtitulo: str = "", help_text: str = ""):
    """
    Mostra KPI card limpo seguindo melhores práticas de UX/UI.
    - Número grande e em destaque
    - Label curto e claro
    - Tooltip opcional via help nativo do Streamlit
    """
    cor_classe = f"status-{cor}"
    st.markdown(f"""
    <div class="status-card {cor_classe}">
        <p class="big-number">{valor}</p>
        <p class="card-label">{titulo}</p>
        {f'<p class="card-subtitle">{subtitulo}</p>' if subtitulo else ''}
    </div>
    """, unsafe_allow_html=True)
    
    # Tooltip compacto
    if help_text:
        st.caption(f"ℹ️ {help_text}")


def mostrar_metrica_com_tooltip(valor: str, titulo: str, metrica_key: str, cor: str = "blue", subtitulo: str = ""):
    """Mostra métrica com tooltip explicativo em layout responsivo."""
    mostrar_kpi_card(valor, titulo, cor, subtitulo)
    mostrar_tooltip(metrica_key)


@st.dialog("📊 Detalhes")
def dialog_detalhes_cards(titulo: str, cards_df: pd.DataFrame, tipo: str = "lista"):
    """
    Dialog para drill-down nos cards.
    Abre ao clicar em uma métrica/status para ver detalhes.
    """
    st.subheader(titulo)
    
    if cards_df.empty:
        st.info("Nenhum card encontrado")
        return
    
    st.write(f"**{len(cards_df)} cards encontrados**")
    
    # Filtro rápido
    busca = st.text_input("🔍 Buscar", placeholder="ID, título ou desenvolvedor...")
    
    if busca:
        mask = (
            cards_df['ticket_id'].str.contains(busca, case=False, na=False) |
            cards_df['titulo'].str.contains(busca, case=False, na=False) |
            cards_df['desenvolvedor'].str.contains(busca, case=False, na=False)
        )
        cards_df = cards_df[mask]
    
    # Lista de cards
    for _, row in cards_df.head(20).iterrows():
        bugs = row.get('bugs', 0)
        risco = 'high' if bugs >= 3 else 'medium' if bugs >= 1 else 'low'
        
        with st.container():
            st.markdown(f"""
            <div class="ticket-card ticket-risk-{risco}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <a href="{row['link']}" target="_blank" style="color: #6366f1; font-weight: bold; text-decoration: none;">
                        {row['ticket_id']}
                    </a>
                    <div>
                        <span class="mini-badge mini-badge-{'red' if bugs > 0 else 'green'}">{bugs} bugs</span>
                        <span style="margin-left: 8px; font-size: 12px; opacity: 0.7;">{row.get('sp', 0)} SP</span>
                    </div>
                </div>
                <p style="margin: 6px 0; font-size: 13px;">{row.get('titulo', '')[:70]}{'...' if len(str(row.get('titulo', ''))) > 70 else ''}</p>
                <p style="font-size: 11px; opacity: 0.6; margin: 0;">
                    👤 {row.get('desenvolvedor', 'N/A')} | 🧪 {row.get('qa', 'N/A')} | 📊 {row.get('status', 'N/A')}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    if len(cards_df) > 20:
        st.caption(f"... e mais {len(cards_df) - 20} cards")


def botao_drill_down(label: str, df_filtrado: pd.DataFrame, titulo_dialog: str):
    """
    Botão que abre dialog com drill-down de cards.
    Permite ao usuário clicar para ver detalhes.
    """
    if st.button(label, use_container_width=True, type="secondary"):
        dialog_detalhes_cards(titulo_dialog, df_filtrado)


def mostrar_alerta_expandivel(tipo: str, titulo: str, msg: str, cards: List):
    """Mostra alerta com lista expandível de cards (com título)."""
    classe = f"alert-{tipo}" if tipo in ['critical', 'warning', 'info', 'success'] else 'alert-info'
    
    st.markdown(f"""
    <div class="{classe}">
        <b>{titulo}</b>
        <p style="margin: 5px 0;">{msg}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if cards:
        with st.expander(f"📋 Ver {len(cards)} card(s) afetado(s)"):
            for card in cards[:10]:
                # Suporta tanto string simples quanto dict com id e titulo
                if isinstance(card, dict):
                    ticket_id = card.get('id', '')
                    titulo_card = card.get('titulo', '')
                    if titulo_card:
                        st.markdown(f"- [{ticket_id}]({link_jira(ticket_id)}) - {titulo_card}")
                    else:
                        st.markdown(f"- [{ticket_id}]({link_jira(ticket_id)})")
                else:
                    st.markdown(f"- [{card}]({link_jira(card)})")
            if len(cards) > 10:
                st.caption(f"... e mais {len(cards) - 10} cards")


def mostrar_card_ticket(row: Dict, compacto: bool = False, mostrar_qa: bool = True):
    """Mostra card de ticket com informações."""
    bugs = row.get('bugs', 0)
    risco = 'high' if bugs >= 3 else 'medium' if bugs >= 1 else 'low'
    
    if compacto:
        st.markdown(f"""
        <div class="ticket-card ticket-risk-{risco}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <a href="{row['link']}" target="_blank" style="color: #6366f1; font-weight: bold; text-decoration: none;">🔗 {row['ticket_id']}</a>
                <span style="opacity: 0.7;">{row.get('sp', 0)} SP | 🐛 {bugs}</span>
            </div>
            <p style="margin: 5px 0 0 0; font-size: 13px; opacity: 0.9;">{row.get('titulo', '')[:50]}...</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        qa_info = f"<br><b>QA:</b> {row.get('qa', 'N/A')}" if mostrar_qa else ""
        st.markdown(f"""
        <div class="ticket-card ticket-risk-{risco}">
            <div style="display: flex; justify-content: space-between;">
                <a href="{row['link']}" target="_blank" style="color: #6366f1; font-weight: bold; text-decoration: none;">🔗 {row['ticket_id']}</a>
                <span style="color: {'#ef4444' if bugs >= 3 else '#f97316' if bugs >= 1 else '#22c55e'}; font-weight: bold;">🐛 {bugs} bugs</span>
            </div>
            <p style="margin: 8px 0;">{row.get('titulo', '')}</p>
            <p style="font-size: 12px; opacity: 0.8;">
                <b>Dev:</b> {row.get('desenvolvedor', 'N/A')} | 
                <b>SP:</b> {row.get('sp', 0)} | 
                <b>Status:</b> {row.get('status', 'N/A')}{qa_info}
            </p>
        </div>
        """, unsafe_allow_html=True)


def mostrar_comentarios(comentarios: List[Dict]):
    """Mostra lista de comentários."""
    for c in comentarios:
        st.markdown(f"""
        <div class="comment-card">
            <b>{c.get('autor', 'Anônimo')}</b>
            <p style="margin: 5px 0 0 0;">{c.get('texto', '')}</p>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# ABA DE LIDERANÇA (EXPANDIDA)
# ==============================================================================

def aba_lideranca(df: pd.DataFrame):
    """Aba de Liderança - Visão executiva expandida com decisões."""
    
    st.markdown('<div class="section-header"><h2>🎯 Painel de Liderança</h2></div>', unsafe_allow_html=True)
    
    # Botão de compartilhamento
    col_share = st.columns([4, 1])
    with col_share[1]:
        if st.button("📤 Compartilhar", use_container_width=True):
            st.info("Link copiado! (Deploy necessário para link externo)")
    
    go_no_go = avaliar_go_no_go(df)
    health = go_no_go['health']
    
    # ==== SEÇÃO 1: Health Score e Decisão Go/No-Go ====
    st.markdown("### 🎯 Decisão de Release")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        cor_class = 'green' if health['score'] >= 75 else 'yellow' if health['score'] >= 50 else 'orange' if health['score'] >= 25 else 'red'
        st.markdown(f"""
        <div class="status-card status-{cor_class}" style="padding: 30px;">
            <p class="big-number">{int(round(health['score']))}</p>
            <p class="card-label">Pontuação de Saúde</p>
            <p style="margin-top: 10px; font-size: 18px;"><b>{health['status']}</b></p>
        </div>
        """, unsafe_allow_html=True)
        
        mostrar_tooltip("health_score")
        
        # Recomendação da Release - formato informativo (não botão)
        classe_indicador = {
            'approved': 'excellent',
            'stable': 'stable', 
            'warning': 'attention',
            'blocked': 'critical'
        }.get(go_no_go['classe'], 'stable')
        
        st.markdown(f"""
        <div style="text-align: center; margin-top: 15px;">
            <div class="status-indicator {classe_indicador}">
                {go_no_go['decisao']}
            </div>
            <p style="font-size: 11px; margin-top: 8px; opacity: 0.7;">Recomendação baseada nas métricas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Métricas executivas em linha
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            st.metric("Total de Cards", len(df))
        with c2:
            st.metric("Story Points", df['sp'].sum())
        with c3:
            concluidos = len(df[df['status_cat'] == 'done'])
            pct = concluidos/len(df)*100 if len(df) > 0 else 0
            st.metric("Concluídos", f"{concluidos} ({pct:.0f}%)")
        with c4:
            lead = calcular_lead_time(df)
            st.metric("Lead Time Médio", f"{lead['medio']} dias")
        
        # Alertas e pontos de atenção (sem bloqueios)
        for b in go_no_go['bloqueios']:
            mostrar_alerta_expandivel('critical', '🔴 Requer Análise', b['msg'], b.get('cards', []))
        
        for a in go_no_go['alertas']:
            mostrar_alerta_expandivel('warning', '🟠 Ponto de Atenção', a['msg'], a.get('cards', []))
        
        if not go_no_go['bloqueios'] and not go_no_go['alertas']:
            st.markdown("""
            <div class="alert-success">
                <b>🟢 Release Excelente</b>
                <p style="margin: 5px 0;">Todos os critérios de qualidade atendidos.</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==== SEÇÃO 2: Composição do Health Score ====
    st.markdown("### 📊 Composição da Pontuação de Saúde")
    st.caption("Baseado em métricas ISTQB - Clique no ℹ️ para entender cada métrica")
    
    cols = st.columns(5)
    detalhes = health['detalhes']
    
    nomes = {
        'conclusao': ('Conclusão', 'Taxa de cards finalizados', None),
        'ddp': ('DDP', 'Detecção de Defeitos', 'ddp'),
        'fpy': ('FPY', 'Aprovação de Primeira', 'fpy'),
        'gargalos': ('Gargalos', 'Pontos de lentidão', None),
        'lead_time': ('Lead Time', 'Tempo de entrega', 'lead_time')
    }
    
    for i, (nome, d) in enumerate(detalhes.items()):
        with cols[i]:
            titulo, desc, tooltip_key = nomes.get(nome, (nome, '', None))
            cor = 'green' if d['score'] >= d['peso'] * 0.7 else 'yellow' if d['score'] >= d['peso'] * 0.4 else 'red'
            
            st.markdown(f"""
            <div class="status-card status-{cor}" style="padding: 10px;">
                <p style="font-size: 20px; font-weight: bold; margin: 0;">{int(round(d['score']))}/{d['peso']}</p>
                <p class="card-label">{titulo}</p>
                <p class="metric-info">{d['valor']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if tooltip_key:
                mostrar_tooltip(tooltip_key)
    
    st.markdown("---")
    
    # ==== SEÇÃO 3: Métricas de Qualidade ISTQB ====
    st.markdown("### 🧪 Métricas de Qualidade (ISTQB)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ddp = calcular_ddp(df)
        fpy = calcular_first_pass_yield(df)
        
        m1, m2 = st.columns(2)
        with m1:
            ddp_cor = 'green' if ddp['valor'] >= 85 else 'yellow' if ddp['valor'] >= 70 else 'orange' if ddp['valor'] >= 50 else 'red'
            mostrar_metrica_com_tooltip(f"{ddp['valor']}%", "DDP", "ddp", ddp_cor, "Detecção de Defeitos")
        
        with m2:
            fpy_cor = 'green' if fpy['valor'] >= 80 else 'yellow' if fpy['valor'] >= 60 else 'orange' if fpy['valor'] >= 40 else 'red'
            mostrar_metrica_com_tooltip(f"{fpy['valor']}%", "FPY", "fpy", fpy_cor, "Aprovação de Primeira")
        
        dd = calcular_defect_density(df)
        mttr = calcular_mttr(df)
        
        m3, m4 = st.columns(2)
        with m3:
            dd_cor = 'green' if dd['valor'] <= 0.2 else 'yellow' if dd['valor'] <= 0.5 else 'red'
            mostrar_metrica_com_tooltip(f"{dd['valor']}", "Densidade", "defect_density", dd_cor, f"{dd['bugs']} bugs / {dd['sp']} SP")
        
        with m4:
            mttr_cor = 'green' if mttr['valor'] <= 2 else 'yellow' if mttr['valor'] <= 5 else 'red'
            mostrar_metrica_com_tooltip(f"{mttr['valor']} dias", "MTTR", "mttr", mttr_cor, "Tempo Médio de Correção")
    
    with col2:
        st.markdown("#### 🔄 Gargalos Identificados")
        
        gargalos = identificar_gargalos(df)
        if gargalos:
            for g in gargalos:
                emoji = '🔴' if g['impacto'] == 'ALTO' else '🟡'
                cat_nome = STATUS_NOMES.get(g['categoria'], g['categoria'])
                
                with st.expander(f"{emoji} **{cat_nome}**: {g['cards']} cards ({g['atual']} dias vs {g['esperado']} esperado)"):
                    st.caption(f"Impacto: **{g['impacto']}**")
                    for ticket in g['tickets'][:5]:
                        st.markdown(f"- [{ticket}]({link_jira(ticket)})")
                    if len(g['tickets']) > 5:
                        st.caption(f"... e mais {len(g['tickets']) - 5} cards")
        else:
            st.success("✅ Nenhum gargalo identificado!")
    
    st.markdown("---")
    
    # ==== SEÇÃO 4: WIP e Throughput ====
    st.markdown("### 📈 Fluxo de Trabalho")
    
    wip = calcular_wip(df)
    throughput = calcular_throughput(df)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🔄 WIP (Em Andamento)")
        mostrar_tooltip("wip")
        
        st.metric("Total em Andamento", wip['total'])
        
        wip_dados = {
            'Etapa': ['Desenvolvimento', 'Revisão', 'Aguardando QA', 'Em Validação', 'Bloqueado'],
            'Cards': [wip['development'], wip['code_review'], wip['waiting_qa'], wip['testing'], wip['blocked']]
        }
        fig = px.bar(wip_dados, x='Etapa', y='Cards', color='Cards', 
                     color_continuous_scale=['#22c55e', '#eab308', '#ef4444'])
        fig.update_layout(height=200, margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
        plotly_chart_themed(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### ⚡ Vazão (Throughput)")
        mostrar_tooltip("throughput")
        
        st.metric("Cards Concluídos", throughput['cards'])
        st.metric("Story Points Entregues", throughput['sp'])
        st.metric("Cards/Dia (média)", throughput['por_dia'])
    
    with col3:
        st.markdown("#### ⏱️ Lead Time")
        mostrar_tooltip("lead_time")
        
        lead = calcular_lead_time(df)
        st.metric("Médio", f"{int(round(lead['medio']))} dias", help="Tempo médio de conclusão")
        st.metric("Mediana (50%)", f"{int(round(lead['p50']))} dias", help="50% dos cards levam até esse tempo")
        st.metric("Típico (85%)", f"{int(round(lead['p85']))} dias", help="85% dos cards levam até esse tempo")
        st.metric("Máximo esperado (95%)", f"{int(round(lead['p95']))} dias", help="95% dos cards levam até esse tempo")
    
    st.markdown("---")
    
    # ==== SEÇÃO 4.5: Visão por Produto (se disponível) ====
    if 'produto' in df.columns and df['produto'].notna().any():
        produtos_validos = df[df['produto'] != 'N/A']['produto'].unique()
        if len(produtos_validos) > 0:
            st.markdown("### 📦 Saúde por Produto")
            st.caption("Indicadores de qualidade e estabilidade por produto/sistema")
            
            df_produtos = calcular_metricas_por_produto(df)
            if not df_produtos.empty:
                # Cards resumidos por produto
                prod_cols = st.columns(min(4, len(df_produtos)))
                for i, (_, row) in enumerate(df_produtos.head(4).iterrows()):
                    with prod_cols[i]:
                        # Determinar cor baseada nos indicadores
                        taxa_hotfix = float(row['Taxa Hotfix'].replace('%', ''))
                        cor = 'green' if taxa_hotfix < 10 else 'yellow' if taxa_hotfix < 20 else 'red'
                        st.markdown(f"""
                        <div class="status-card status-{cor}" style="padding: 12px;">
                            <p style="font-size: 16px; font-weight: bold; margin: 0;">{row['Produto']}</p>
                            <p class="card-subtitle">{row['Cards']} cards | {row['SP']} SP</p>
                            <p style="font-size: 14px; margin-top: 8px;">🐛 {row['Bugs']} bugs | 🚨 {row['Hotfixes']} hotfixes</p>
                            <p class="metric-info">FPY: {row['FPY']} | Hotfix: {row['Taxa Hotfix']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                with st.expander("📊 Ver tabela completa por produto"):
                    st.dataframe(df_produtos, hide_index=True, use_container_width=True)
            
            st.markdown("---")
    
    # ==== SEÇÃO 5: Previsões e Tendências ====
    st.markdown("### 🔮 Previsões e Recomendações")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="previsao-card">
            <h4>📅 Previsão de Entrega</h4>
        """, unsafe_allow_html=True)
        
        # Calcular previsão
        cards_restantes = len(df[~df['status_cat'].isin(['done', 'deferred'])])
        velocidade = throughput['por_dia'] if throughput['por_dia'] > 0 else 1
        dias_estimados = int(round(cards_restantes / velocidade))
        
        data_prevista = datetime.now() + timedelta(days=dias_estimados)
        
        st.metric("Cards Restantes", cards_restantes)
        st.metric("Dias Estimados", dias_estimados)
        st.metric("Data Prevista", data_prevista.strftime('%d/%m/%Y'))
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="decisao-card">
            <h4>💡 Recomendações para o Tech Lead</h4>
        """, unsafe_allow_html=True)
        
        recomendacoes = []
        
        fpy = calcular_first_pass_yield(df)
        
        # Gera recomendações baseadas nos dados
        if wip['blocked'] > 0:
            recomendacoes.append(f"🚨 **Prioridade 1**: Resolver {wip['blocked']} card(s) bloqueado(s)")
        
        if wip['waiting_qa'] > 5:
            recomendacoes.append(f"⚠️ **Fila de QA**: {wip['waiting_qa']} cards aguardando - considerar realocar QAs")
        
        if fpy['valor'] < 60:
            recomendacoes.append("📋 **Qualidade**: FPY baixo - revisar critérios de aceite e code review")
        
        if lead['medio'] > 10:
            recomendacoes.append(f"⏱️ **Lead Time**: {lead['medio']} dias - analisar gargalos no fluxo")
        
        # Cards de alta prioridade
        alta_prioridade = df[(df['prioridade'].isin(['Alta', 'Muito Alta', 'Muito alto', 'Alto'])) & 
                             (df['status_cat'] != 'done')]
        if not alta_prioridade.empty:
            recomendacoes.append(f"🔥 **Alta Prioridade**: {len(alta_prioridade)} card(s) críticos pendentes")
        
        if not recomendacoes:
            recomendacoes.append("✅ Release em bom estado! Manter monitoramento.")
        
        for r in recomendacoes:
            st.markdown(f"- {r}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==== SEÇÃO 6: Gráficos de Distribuição com Drill-down ====
    st.markdown("### 📊 Visão Geral")
    st.caption("💡 Clique nos botões abaixo de cada status para ver os cards detalhados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Distribuição por Status**")
        status_count = df.groupby('status_cat').size().reset_index(name='count')
        status_count['status_nome'] = status_count['status_cat'].map(STATUS_NOMES)
        fig = px.pie(status_count, values='count', names='status_nome', hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(height=280, margin=dict(t=10, b=10, l=10, r=10))
        plotly_chart_themed(fig, use_container_width=True)
        
        # Botões de drill-down por status
        st.markdown("**🔍 Ver cards por status:**")
        status_cols = st.columns(3)
        status_list = [('done', 'Concluídos', 'green'), ('testing', 'Em Validação', 'blue'), ('blocked', 'Bloqueados', 'red')]
        for i, (status_cat, label, cor) in enumerate(status_list):
            with status_cols[i]:
                count = len(df[df['status_cat'] == status_cat])
                if count > 0:
                    if st.button(f"📋 {label} ({count})", key=f"drill_{status_cat}", use_container_width=True):
                        dialog_detalhes_cards(f"{label} - {count} cards", df[df['status_cat'] == status_cat])
    
    with col2:
        st.markdown("**Cards por Tipo**")
        tipo_count = df.groupby('tipo').size().reset_index(name='count')
        fig2 = px.bar(tipo_count, x='tipo', y='count', color='tipo',
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig2.update_layout(height=280, margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
        plotly_chart_themed(fig2, use_container_width=True)
        
        # Botões de drill-down por tipo
        st.markdown("**🔍 Ver cards por tipo:**")
        tipos = df['tipo'].unique()[:3]  # Top 3 tipos
        tipo_cols = st.columns(3)
        for i, tipo in enumerate(tipos):
            with tipo_cols[i]:
                count = len(df[df['tipo'] == tipo])
                if count > 0:
                    if st.button(f"📋 {tipo[:10]} ({count})", key=f"drill_tipo_{tipo}", use_container_width=True):
                        dialog_detalhes_cards(f"{tipo} - {count} cards", df[df['tipo'] == tipo])
    
    # ==== SEÇÃO 7: Desenvolvedores - Fator K ====
    st.markdown("### 👨‍💻 Performance dos Desenvolvedores")
    
    mostrar_tooltip("fator_k")
    
    devs = [d for d in df['desenvolvedor'].unique() if d != 'Não atribuído']
    dados_dev = []
    
    for dev in devs:
        analise = analisar_dev_detalhado(df, dev)
        if analise:
            # Para o gráfico, usar 0 se FK=-1 (sem SP)
            fk_display = analise['fk_medio'] if analise['fk_medio'] >= 0 else 0
            dados_dev.append({
                'Desenvolvedor': dev,
                'Cards': analise['cards'],
                'SP': analise['sp_total'],
                'Bugs': analise['bugs_total'],
                'Fator K': fk_display,
                'FK Real': analise['fk_medio'],
                'Selo': f"{analise['maturidade']['emoji']} {analise['maturidade']['selo']}"
            })
    
    if dados_dev:
        df_dev = pd.DataFrame(dados_dev).sort_values('Fator K', ascending=False)
        
        # Verificar se há dados de SP
        total_sp = df_dev['SP'].sum()
        
        if total_sp > 0:
            # Mostrar gráfico normal
            fig = px.bar(df_dev, x='Desenvolvedor', y='Fator K', color='Fator K',
                         color_continuous_scale=['#ef4444', '#f97316', '#eab308', '#22c55e'],
                         text='Selo')
            fig.add_hline(y=2, line_dash="dash", annotation_text="Meta FK ≥ 2")
            fig.update_layout(height=320)
            plotly_chart_themed(fig, use_container_width=True)
        else:
            # Mostrar gráfico alternativo por bugs
            st.info("📊 Story Points não cadastrados nos cards. Exibindo ranking por taxa de bugs encontrados.")
            
            df_dev['Taxa de Bugs'] = df_dev.apply(
                lambda x: round(x['Bugs'] / x['Cards'], 2) if x['Cards'] > 0 else 0, axis=1)
            df_dev = df_dev.sort_values('Taxa de Bugs', ascending=True)
            
            fig = px.bar(df_dev, x='Desenvolvedor', y='Taxa de Bugs', color='Taxa de Bugs',
                         color_continuous_scale=['#22c55e', '#eab308', '#f97316', '#ef4444'],
                         text=df_dev['Bugs'].astype(str) + ' bugs')
            fig.update_layout(height=320, title="Taxa de Bugs por Card (menor = melhor)")
            plotly_chart_themed(fig, use_container_width=True)
        
        # Drill-down por desenvolvedor
        st.markdown("**🔍 Ver cards de cada desenvolvedor:**")
        dev_cols = st.columns(min(4, len(dados_dev)))
        for i, dev_data in enumerate(dados_dev[:4]):
            with dev_cols[i]:
                dev_nome = dev_data['Desenvolvedor']
                if st.button(f"👤 {dev_nome.split()[0]}", key=f"drill_dev_{dev_nome}", use_container_width=True):
                    df_dev_cards = df[df['desenvolvedor'] == dev_nome]
                    dialog_detalhes_cards(f"Cards de {dev_nome}", df_dev_cards)
        
        with st.expander("📋 Ver tabela detalhada de desenvolvedores"):
            # Mostrar tabela sem FK Real
            df_display = df_dev[['Desenvolvedor', 'Cards', 'SP', 'Bugs', 'Selo']].copy()
            if total_sp > 0:
                df_display['Fator K'] = df_dev['Fator K']
            st.dataframe(df_display, hide_index=True, use_container_width=True)


# ==============================================================================
# ABA DE QA (EXPANDIDA)
# ==============================================================================

def aba_qa(df: pd.DataFrame):
    """Aba de QA - Métricas detalhadas e impacto."""
    
    st.markdown('<div class="section-header"><h2>🧪 Painel de QA</h2></div>', unsafe_allow_html=True)
    
    qas = [q for q in df['qa'].unique() if q != 'Não atribuído']
    
    qa_sel = st.selectbox("👤 Selecione o QA", ["Visão Geral do Time"] + sorted(qas))
    st.session_state.filtro_qa = qa_sel
    
    st.markdown("---")
    
    if qa_sel == "Visão Geral do Time":
        # ==== Impacto do QA no Time ====
        st.markdown("### 🛡️ Impacto do Time de QA")
        
        bugs_total = int(df['bugs'].sum())
        sp_protegidos = int(df['sp'].sum())
        ddp = calcular_ddp(df)
        fpy = calcular_first_pass_yield(df)
        
        # Contar cards validados (concluídos + em validação)
        cards_validados = len(df[df['status_cat'].isin(['done', 'testing'])])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="impact-card">
                <p style="font-size: 32px; font-weight: bold; color: #22c55e; margin: 0;">🐛 {bugs_total}</p>
                <p style="margin: 5px 0;">Bugs Encontrados</p>
                <p style="font-size: 12px; opacity: 0.7;">Problemas identificados antes de produção</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="impact-card">
                <p style="font-size: 32px; font-weight: bold; color: #3b82f6; margin: 0;">✅ {cards_validados}</p>
                <p style="margin: 5px 0;">Cards Validados</p>
                <p style="font-size: 12px; opacity: 0.7;">Funcionalidades testadas pelo QA</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="impact-card">
                <p style="font-size: 32px; font-weight: bold; color: #8b5cf6; margin: 0;">🎯 {ddp['valor']}%</p>
                <p style="margin: 5px 0;">DDP</p>
                <p style="font-size: 12px; opacity: 0.7;">Taxa de Detecção de Defeitos</p>
            </div>
            """, unsafe_allow_html=True)
            mostrar_tooltip("ddp")
        
        with col4:
            st.markdown(f"""
            <div class="impact-card">
                <p style="font-size: 32px; font-weight: bold; color: #f97316; margin: 0;">⚡ {fpy['valor']}%</p>
                <p style="margin: 5px 0;">FPY</p>
                <p style="font-size: 12px; opacity: 0.7;">Aprovação de Primeira</p>
            </div>
            """, unsafe_allow_html=True)
            mostrar_tooltip("fpy")
        
        st.markdown("---")
        
        # ==== Indicadores de Qualidade e Retrabalho ====
        st.markdown("### 🔄 Indicadores de Retrabalho e Qualidade")
        st.caption("Métricas que ajudam a entender a evolução da qualidade do software")
        
        retrabalho = calcular_taxa_retrabalho(df)
        hotfix = calcular_hotfix_rate(df)
        
        col_r1, col_r2, col_r3, col_r4 = st.columns(4)
        
        with col_r1:
            cor = 'green' if retrabalho['taxa'] < 10 else 'yellow' if retrabalho['taxa'] < 20 else 'red'
            st.markdown(f"""
            <div class="status-card status-{cor}">
                <p class="big-number">{retrabalho['taxa']}%</p>
                <p class="card-label">Taxa de Retrabalho</p>
                <p class="card-subtitle">{retrabalho['reprovados']} reprovados</p>
            </div>
            """, unsafe_allow_html=True)
            st.caption("ℹ️ Cards que voltaram para correção", help="Quanto menor, melhor a qualidade na primeira entrega")
        
        with col_r2:
            cor = 'green' if hotfix['taxa'] < 15 else 'yellow' if hotfix['taxa'] < 30 else 'red'
            st.markdown(f"""
            <div class="status-card status-{cor}">
                <p class="big-number">{hotfix['taxa']}%</p>
                <p class="card-label">Taxa de Hotfix/Bug</p>
                <p class="card-subtitle">{hotfix['hotfixes']} hotfixes, {hotfix['bugs']} bugs</p>
            </div>
            """, unsafe_allow_html=True)
            st.caption("ℹ️ Indica estabilidade do produto", help="Alto = produto instável, precisa de mais testes")
        
        with col_r3:
            cards_zero_bugs = len(df[df['bugs'] == 0])
            pct_zero = int(cards_zero_bugs / len(df) * 100) if len(df) > 0 else 0
            cor = 'green' if pct_zero > 70 else 'yellow' if pct_zero > 50 else 'red'
            st.markdown(f"""
            <div class="status-card status-{cor}">
                <p class="big-number">{pct_zero}%</p>
                <p class="card-label">Zero Bugs</p>
                <p class="card-subtitle">{cards_zero_bugs} de {len(df)} cards</p>
            </div>
            """, unsafe_allow_html=True)
            st.caption("ℹ️ Cards aprovados sem nenhum bug", help="Quanto maior, melhor a qualidade do código")
        
        with col_r4:
            wip = calcular_wip(df)
            em_rework = wip.get('rework', 0)
            cor = 'green' if em_rework == 0 else 'yellow' if em_rework < 3 else 'red'
            st.markdown(f"""
            <div class="status-card status-{cor}">
                <p class="big-number">{em_rework}</p>
                <p class="card-label">Em Retrabalho</p>
                <p class="card-subtitle">Aguardando correção</p>
            </div>
            """, unsafe_allow_html=True)
            st.caption("ℹ️ Cards reprovados aguardando", help="Cards que falharam na validação e precisam de correção")
        
        st.markdown("---")
        
        # ==== VALOR DO QA - Seção de Impacto Estratégico ====
        st.markdown("### 💰 Valor Estratégico do QA")
        st.caption("Estimativa do impacto financeiro e operacional do trabalho de QA")
        
        # Cálculos de valor estimado
        # Premissas: Bug em produção custa ~10x mais para corrigir que em QA
        # Fonte: IBM Systems Sciences Institute, NIST
        custo_medio_bug_producao = 500  # R$ (estimativa conservadora: hora de dev + impacto)
        custo_medio_bug_qa = 50  # R$ (custo de correção quando encontrado pelo QA)
        
        bugs_evitados_prod = int(bugs_total * (ddp['valor'] / 100))
        economia_estimada = bugs_evitados_prod * (custo_medio_bug_producao - custo_medio_bug_qa)
        
        # Cards concluídos sem incidentes (qualidade garantida)
        cards_sem_incidentes = len(df[(df['status_cat'] == 'done') & (df['bugs'] <= 1)])
        
        col_val1, col_val2, col_val3, col_val4 = st.columns(4)
        
        with col_val1:
            st.markdown(f"""
            <div class="impact-card" style="background: linear-gradient(135deg, rgba(34,197,94,0.15), rgba(16,185,129,0.05)); border-color: #22c55e;">
                <p style="font-size: 28px; font-weight: bold; color: #22c55e; margin: 0;">🛡️ {bugs_evitados_prod}</p>
                <p style="margin: 5px 0; font-weight: 600;">Bugs Evitados em Produção</p>
                <p style="font-size: 11px; opacity: 0.7;">Problemas que não chegaram aos usuários</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_val2:
            st.markdown(f"""
            <div class="impact-card" style="background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(14,165,233,0.05)); border-color: #3b82f6;">
                <p style="font-size: 28px; font-weight: bold; color: #3b82f6; margin: 0;">💰 R$ {economia_estimada:,.0f}</p>
                <p style="margin: 5px 0; font-weight: 600;">Economia Estimada</p>
                <p style="font-size: 11px; opacity: 0.7;">Custo evitado de correção em produção</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_val3:
            roi_qa = int((economia_estimada / max(1, bugs_total * custo_medio_bug_qa)) * 100)
            st.markdown(f"""
            <div class="impact-card" style="background: linear-gradient(135deg, rgba(139,92,246,0.15), rgba(124,58,237,0.05)); border-color: #8b5cf6;">
                <p style="font-size: 28px; font-weight: bold; color: #8b5cf6; margin: 0;">📈 {roi_qa}%</p>
                <p style="margin: 5px 0; font-weight: 600;">ROI do QA</p>
                <p style="font-size: 11px; opacity: 0.7;">Retorno sobre investimento em testes</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_val4:
            st.markdown(f"""
            <div class="impact-card" style="background: linear-gradient(135deg, rgba(236,72,153,0.15), rgba(219,39,119,0.05)); border-color: #ec4899;">
                <p style="font-size: 28px; font-weight: bold; color: #ec4899; margin: 0;">✅ {cards_sem_incidentes}</p>
                <p style="margin: 5px 0; font-weight: 600;">Entregas com Qualidade</p>
                <p style="font-size: 11px; opacity: 0.7;">Cards concluídos com até 1 bug</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Insight sobre o valor
        with st.expander("📊 Como calculamos o valor do QA?"):
            st.markdown(f"""
            **Metodologia de cálculo:**
            
            - **Custo médio de bug em produção:** R$ {custo_medio_bug_producao} (inclui tempo de correção urgente, impacto em usuários, rollback)
            - **Custo médio de bug em QA:** R$ {custo_medio_bug_qa} (correção planejada, sem pressão)
            - **Taxa de detecção (DDP):** {ddp['valor']}% dos bugs são encontrados pelo QA antes de produção
            - **Bugs evitados:** {bugs_total} bugs × {ddp['valor']}% = **{bugs_evitados_prod} bugs** que não chegaram em produção
            - **Economia:** {bugs_evitados_prod} × (R$ {custo_medio_bug_producao} - R$ {custo_medio_bug_qa}) = **R$ {economia_estimada:,.0f}**
            
            *Fonte: IBM Systems Sciences Institute - "Integrating Software Assurance into the SDLC"*
            """)
        
        st.markdown("---")
        
        # ==== Comparativo entre QAs ====
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
                    'Bugs Encontrados': analise['bugs_encontrados'],
                    'FPY': f"{analise['fpy']['valor']}%",
                    'Tempo Médio': f"{analise['tempo_validacao']} dias",
                })
        
        if dados_qa:
            df_qa = pd.DataFrame(dados_qa)
            st.dataframe(df_qa, hide_index=True, use_container_width=True)
        
        st.markdown("---")
        
        # ==== Estatísticas Adicionais do QA ====
        st.markdown("### 📈 Análise Detalhada")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bugs por Tipo de Card
            st.markdown("**🐛 Bugs por Tipo de Card**")
            bugs_por_tipo = df.groupby('tipo')['bugs'].sum().reset_index()
            if not bugs_por_tipo.empty and bugs_por_tipo['bugs'].sum() > 0:
                fig_bugs = px.pie(bugs_por_tipo, values='bugs', names='tipo', hole=0.4,
                                  color_discrete_sequence=px.colors.qualitative.Set2)
                fig_bugs.update_layout(height=250, margin=dict(t=20, b=20, l=20, r=20))
                plotly_chart_themed(fig_bugs, use_container_width=True)
            else:
                st.info("Sem bugs registrados por tipo")
        
        with col2:
            # Distribuição de bugs por QA
            st.markdown("**🎯 Bugs Encontrados por QA**")
            bugs_por_qa = df[df['qa'] != 'Não atribuído'].groupby('qa')['bugs'].sum().reset_index()
            if not bugs_por_qa.empty and bugs_por_qa['bugs'].sum() > 0:
                fig_qa_bugs = px.bar(bugs_por_qa.nlargest(5, 'bugs'), x='qa', y='bugs', 
                                     color='bugs', color_continuous_scale=['#22c55e', '#ef4444'])
                fig_qa_bugs.update_layout(height=250, margin=dict(t=20, b=20, l=20, r=20), 
                                          showlegend=False, xaxis_title="", yaxis_title="Bugs")
                plotly_chart_themed(fig_qa_bugs, use_container_width=True)
            else:
                st.info("Sem dados de bugs por QA")
        
        # Métricas de tempo
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("**⏱️ Tempo em Validação**")
            em_validacao = df[df['status_cat'].isin(['waiting_qa', 'testing'])]
            if not em_validacao.empty:
                tempo_medio_fila = em_validacao['dias_em_status'].mean()
                st.metric("Tempo Médio na Fila", f"{int(round(tempo_medio_fila))} dias")
                st.metric("Máximo na Fila", f"{em_validacao['dias_em_status'].max()} dias")
            else:
                st.info("Sem cards em validação")
        
        with col4:
            st.markdown("**📊 Eficiência do Time**")
            concluidos = df[df['status_cat'] == 'done']
            if not concluidos.empty:
                lead_time_qa = concluidos['lead_time'].mean()
                st.metric("Lead Time Médio", f"{lead_time_qa:.1f} dias")
                # Taxa de retrabalho (cards que voltaram - aproximação por bugs > 0)
                cards_com_bugs = len(concluidos[concluidos['bugs'] > 0])
                taxa_retrabalho = cards_com_bugs / len(concluidos) * 100 if len(concluidos) > 0 else 0
                st.metric("Taxa de Retrabalho", f"{taxa_retrabalho:.1f}%", 
                         help="Cards que precisaram de correção antes de aprovar")
            else:
                st.info("Sem cards concluídos")
        
        st.markdown("---")
        
        # ==== Fila de QA ====
        fila_qa = df[df['status_cat'] == 'waiting_qa']
        
        if not fila_qa.empty:
            st.markdown("### ⏳ Fila de Validação")
            
            c1, c2 = st.columns([1, 2])
            with c1:
                st.metric("Cards na Fila", len(fila_qa))
                st.metric("SP na Fila", fila_qa['sp'].sum())
                
                capacidade = 5 * len(qas) if qas else 5
                dias_estim = fila_qa['sp'].sum() / capacidade
                st.metric("Dias Estimados para Limpar", f"{dias_estim:.1f}")
            
            with c2:
                for _, row in fila_qa.head(5).iterrows():
                    mostrar_card_ticket(row.to_dict(), compacto=True)
                
                if len(fila_qa) > 5:
                    with st.expander(f"Ver mais {len(fila_qa) - 5} cards"):
                        for _, row in fila_qa.iloc[5:].iterrows():
                            mostrar_card_ticket(row.to_dict(), compacto=True)
        else:
            st.success("✅ Fila de QA vazia! Todos os cards foram validados.")
    
    else:
        # ==== Métricas individuais do QA (TERCEIRA PESSOA) ====
        analise = analisar_qa_detalhado(df, qa_sel)
        
        if analise:
            st.markdown(f"### 👤 Métricas de {qa_sel}")
            
            # Métricas principais
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                st.metric("Cards Atribuídos", analise['cards_total'])
            with c2:
                st.metric("Cards Validados", analise['validados'])
            with c3:
                st.metric("Bugs Encontrados", analise['bugs_encontrados'])
            with c4:
                st.metric("FPY", f"{analise['fpy']['valor']}%")
            with c5:
                st.metric("Tempo Médio", f"{analise['tempo_validacao']} dias")
            
            st.markdown("---")
            
            # Impacto (TERCEIRA PESSOA)
            st.markdown(f"### 🛡️ Impacto de {qa_sel}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="impact-card">
                    <h4>Bugs Evitados em Produção</h4>
                    <p style="font-size: 28px; font-weight: bold; color: #22c55e;">{analise['bugs_evitados']} bugs</p>
                    <p>{qa_sel} protegeu <b>{analise['sp_protegidos']} Story Points</b> de funcionalidades</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                ddp_cor = 'green' if analise['ddp']['status'] in ['excellent', 'good'] else 'yellow'
                st.markdown(f"""
                <div class="status-card status-{ddp_cor}">
                    <p class="big-number">{analise['ddp']['valor']}%</p>
                    <p class="card-label">Taxa de Detecção (DDP)</p>
                    <p class="metric-info">Eficácia de {qa_sel.split()[0]} em encontrar bugs</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Cards problemáticos (TERCEIRA PESSOA)
            if not analise['cards_problematicos'].empty:
                st.markdown(f"### 🔴 Cards mais Problemáticos de {qa_sel}")
                st.caption("Cards com 3+ bugs - podem indicar problemas de especificação ou alta complexidade")
                
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
            
            # Tempo de validação (TERCEIRA PESSOA)
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"### ⚡ Cards mais Rápidos de {qa_sel.split()[0]}")
                if not analise['mais_rapido'].empty:
                    for _, row in analise['mais_rapido'].iterrows():
                        st.markdown(f"- [{row['ticket_id']}]({row['link']}) - **{row['lead_time']} dias** ({row['bugs']} bugs)")
                else:
                    st.info("Ainda sem dados suficientes")
            
            with col2:
                st.markdown(f"### 🐢 Cards mais Demorados de {qa_sel.split()[0]}")
                if not analise['mais_lento'].empty:
                    for _, row in analise['mais_lento'].iterrows():
                        st.markdown(f"- [{row['ticket_id']}]({row['link']}) - **{row['lead_time']} dias** ({row['bugs']} bugs)")
                else:
                    st.info("Ainda sem dados suficientes")
            
            st.markdown("---")
            
            # Por complexidade
            if analise['por_complexidade']:
                st.markdown(f"### 📈 Performance por Complexidade de {qa_sel.split()[0]}")
                
                dados_comp = [{'Complexidade': k, 'Cards': v['ticket_id'], 'Bugs': v['bugs'], 'Tempo Médio': v['lead_time']} 
                              for k, v in analise['por_complexidade'].items() if k != 'N/A']
                
                if dados_comp:
                    df_comp = pd.DataFrame(dados_comp)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        fig = px.bar(df_comp, x='Complexidade', y=['Cards', 'Bugs'], barmode='group',
                                    title='Cards e Bugs por Complexidade')
                        plotly_chart_themed(fig, use_container_width=True)
                    
                    with col2:
                        fig2 = px.bar(df_comp, x='Complexidade', y='Tempo Médio', 
                                     title='Tempo Médio por Complexidade (dias)')
                        plotly_chart_themed(fig2, use_container_width=True)
            
            st.markdown("---")
            
            # Todos os cards (TERCEIRA PESSOA)
            st.markdown(f"### 📋 Todos os Cards de {qa_sel}")
            
            for _, row in analise['df'].iterrows():
                with st.expander(f"🔗 {row['ticket_id']} - {row['titulo'][:40]}... ({row['bugs']} bugs)"):
                    mostrar_card_ticket(row.to_dict(), mostrar_qa=False)
                    
                    if row['comentarios']:
                        st.markdown("**💬 Últimos Comentários:**")
                        mostrar_comentarios(row['comentarios'])


# ==============================================================================
# ABA DE DEV
# ==============================================================================

def aba_dev(df: pd.DataFrame):
    """Aba de Dev - Performance e análise."""
    
    st.markdown('<div class="section-header"><h2>👨‍💻 Painel de Desenvolvimento</h2></div>', unsafe_allow_html=True)
    
    devs = [d for d in df['desenvolvedor'].unique() if d != 'Não atribuído']
    
    dev_sel = st.selectbox("👤 Selecione o Desenvolvedor", ["Ranking Geral"] + sorted(devs))
    st.session_state.filtro_dev = dev_sel
    
    st.markdown("---")
    
    if dev_sel == "Ranking Geral":
        st.markdown("### 🏆 Ranking de Performance")
        
        col_fk, col_info = st.columns([10, 1])
        with col_info:
            mostrar_tooltip("fator_k")
        
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
                    'Tempo Médio': f"{analise['tempo_medio']} dias",
                    'Selo': f"{analise['maturidade']['emoji']} {analise['maturidade']['selo']}"
                })
        
        df_rank = pd.DataFrame(dados_dev)
        df_rank = df_rank.sort_values('Fator K', ascending=False)
        
        st.dataframe(df_rank, hide_index=True, use_container_width=True)
        
        # Gráfico
        fig = px.bar(df_rank, x='Desenvolvedor', y='Fator K',
                     color='Fator K',
                     color_continuous_scale=['#ef4444', '#f97316', '#eab308', '#22c55e'],
                     text='Selo')
        fig.add_hline(y=2, line_dash="dash", annotation_text="Meta (FK ≥ 2)")
        fig.update_layout(height=400)
        plotly_chart_themed(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Devs que precisam de suporte (somente quem tem bugs E dados de SP)
        # Não incluir quem tem FK=-1 (sem SP) ou quem tem 0 bugs
        devs_atencao = [d for d in dados_dev 
                       if d['Fator K'] >= 0 and d['Fator K'] < 2 and d['Bugs'] > 0]
        if devs_atencao:
            st.markdown("### ⚠️ Desenvolvedores que Precisam de Atenção")
            st.caption("Fator K abaixo de 2 com bugs encontrados - podem se beneficiar de code review mais rigoroso")
            
            for d in devs_atencao:
                df_dev_filter = df[df['desenvolvedor'] == d['Desenvolvedor']]
                cards_problematicos = df_dev_filter[df_dev_filter['bugs'] >= 2].head(3)
                
                with st.expander(f"⚠️ {d['Desenvolvedor']} - FK: {d['Fator K']} | {d['Bugs']} bugs em {d['Cards']} cards"):
                    if not cards_problematicos.empty:
                        st.markdown("**Cards com mais bugs:**")
                        for _, row in cards_problematicos.iterrows():
                            st.markdown(f"- [{row['ticket_id']}]({row['link']}) - {row['bugs']} bugs - {row['titulo'][:40]}...")
        
        st.markdown("---")
        
        # ==== Estatísticas Adicionais de Desenvolvimento ====
        st.markdown("### 📊 Análise do Time de Desenvolvimento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribuição de cards por desenvolvedor
            st.markdown("**📋 Cards por Desenvolvedor**")
            cards_por_dev = df[df['desenvolvedor'] != 'Não atribuído'].groupby('desenvolvedor').size().reset_index(name='cards')
            if not cards_por_dev.empty:
                cards_por_dev = cards_por_dev.nlargest(8, 'cards')
                fig_cards = px.bar(cards_por_dev, x='desenvolvedor', y='cards', 
                                   color='cards', color_continuous_scale='Blues')
                fig_cards.update_layout(height=250, margin=dict(t=20, b=20, l=20, r=20), 
                                        showlegend=False, xaxis_title="", yaxis_title="Cards")
                plotly_chart_themed(fig_cards, use_container_width=True)
            else:
                st.info("Sem dados de cards por desenvolvedor")
        
        with col2:
            # Taxa de bugs por desenvolvedor (bugs/card)
            st.markdown("**🐛 Taxa de Bugs por Card**")
            taxa_bugs = df[df['desenvolvedor'] != 'Não atribuído'].groupby('desenvolvedor').agg({
                'bugs': 'sum', 'ticket_id': 'count'
            }).reset_index()
            taxa_bugs['taxa'] = (taxa_bugs['bugs'] / taxa_bugs['ticket_id']).round(2)
            taxa_bugs = taxa_bugs.nlargest(8, 'taxa')
            
            if not taxa_bugs.empty and taxa_bugs['taxa'].sum() > 0:
                fig_taxa = px.bar(taxa_bugs, x='desenvolvedor', y='taxa', 
                                  color='taxa', color_continuous_scale=['#22c55e', '#eab308', '#ef4444'])
                fig_taxa.update_layout(height=250, margin=dict(t=20, b=20, l=20, r=20), 
                                       showlegend=False, xaxis_title="", yaxis_title="Bugs/Card")
                plotly_chart_themed(fig_taxa, use_container_width=True)
            else:
                st.success("✅ Sem bugs registrados!")
        
        # Métricas gerais do time
        col3, col4, col5 = st.columns(3)
        
        with col3:
            st.metric("Total de Cards", len(df))
            em_andamento = len(df[df['status_cat'] == 'development'])
            st.metric("Em Desenvolvimento", em_andamento)
        
        with col4:
            total_bugs = df['bugs'].sum()
            st.metric("Total de Bugs", int(total_bugs))
            media_bugs = total_bugs / len(df) if len(df) > 0 else 0
            st.metric("Média de Bugs/Card", f"{media_bugs:.2f}")
        
        with col5:
            # Cards sem bugs (qualidade)
            cards_zero_bugs = len(df[df['bugs'] == 0])
            pct_zero_bugs = cards_zero_bugs / len(df) * 100 if len(df) > 0 else 0
            st.metric("Cards sem Bugs", f"{cards_zero_bugs} ({pct_zero_bugs:.0f}%)")
            # Tempo médio de desenvolvimento
            lead_medio = df['lead_time'].mean() if not df.empty else 0
            st.metric("Lead Time Médio", f"{int(round(lead_medio))} dias")
        
        st.markdown("---")
        
        # ==== Métricas por Produto ====
        st.markdown("### 📦 Qualidade por Produto")
        st.caption("Indicadores de qualidade agrupados por produto/sistema")
        
        df_produtos = calcular_metricas_por_produto(df)
        if not df_produtos.empty:
            st.dataframe(df_produtos, hide_index=True, use_container_width=True)
            
            col_prod1, col_prod2 = st.columns(2)
            
            with col_prod1:
                # Gráfico de bugs por produto
                bugs_prod = df[df['produto'] != 'N/A'].groupby('produto')['bugs'].sum().reset_index()
                if not bugs_prod.empty and bugs_prod['bugs'].sum() > 0:
                    fig_prod = px.bar(bugs_prod.nlargest(6, 'bugs'), x='produto', y='bugs',
                                      color='bugs', color_continuous_scale=['#22c55e', '#eab308', '#ef4444'],
                                      title="Bugs por Produto")
                    fig_prod.update_layout(height=250, showlegend=False)
                    plotly_chart_themed(fig_prod, use_container_width=True)
            
            with col_prod2:
                # Gráfico de hotfixes por produto
                if 'is_hotfix' in df.columns:
                    hotfix_prod = df[df['is_hotfix'] == True].groupby('produto').size().reset_index(name='hotfixes')
                    if not hotfix_prod.empty and hotfix_prod['hotfixes'].sum() > 0:
                        fig_hotfix = px.bar(hotfix_prod.nlargest(6, 'hotfixes'), x='produto', y='hotfixes',
                                            color='hotfixes', color_continuous_scale=['#22c55e', '#f97316', '#ef4444'],
                                            title="Hotfixes por Produto")
                        fig_hotfix.update_layout(height=250, showlegend=False)
                        plotly_chart_themed(fig_hotfix, use_container_width=True)
        else:
            st.info("📊 Dados de produto não disponíveis. Configure o campo 'Produto' no Jira para ver esta análise.")
    
    else:
        # Métricas individuais (TERCEIRA PESSOA)
        analise = analisar_dev_detalhado(df, dev_sel)
        
        if analise:
            st.markdown(f"### 👤 Métricas de {dev_sel}")
            
            # Selo de maturidade
            mat = analise['maturidade']
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown(f"""
                <div class="status-card" style="background: {mat['cor']}20; border-color: {mat['cor']}; padding: 20px;">
                    <p style="font-size: 48px; margin: 0;">{mat['emoji']}</p>
                    <p style="font-size: 20px; font-weight: bold; margin: 5px 0;">{mat['selo']}</p>
                    <p style="font-size: 14px; opacity: 0.8;">{mat['desc']}</p>
                    <p style="font-size: 24px; font-weight: bold; margin-top: 10px;">FK: {analise['fk_medio']}</p>
                </div>
                """, unsafe_allow_html=True)
                mostrar_tooltip("fator_k")
            
            with col2:
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("Cards Desenvolvidos", analise['cards'])
                with c2:
                    st.metric("Story Points", analise['sp_total'])
                with c3:
                    st.metric("Bugs Encontrados", analise['bugs_total'])
                with c4:
                    st.metric("Taxa Zero Bugs", f"{analise['zero_bugs']}%")
            
            st.markdown("---")
            
            # Cards do dev (TERCEIRA PESSOA)
            st.markdown(f"### 📋 Cards de {dev_sel}")
            
            for _, row in analise['df'].iterrows():
                with st.expander(f"🔗 {row['ticket_id']} - {row['titulo'][:40]}... ({row['bugs']} bugs)"):
                    mostrar_card_ticket(row.to_dict())
                    
                    if row['comentarios']:
                        st.markdown("**💬 Últimos Comentários:**")
                        mostrar_comentarios(row['comentarios'])


# ==============================================================================
# ABA DE HISTÓRICO
# ==============================================================================

def aba_historico():
    """Aba de Histórico - Tendências e Evolução de Qualidade."""
    
    st.markdown('<div class="section-header"><h2>📜 Histórico e Evolução de Qualidade</h2></div>', unsafe_allow_html=True)
    
    st.info("📊 Acompanhe a evolução das métricas de qualidade ao longo das releases. Dados históricos simulados para demonstração.")
    
    # Dados mock de histórico (mais completos)
    releases = [f"Release {i}" for i in range(233, 239)]
    
    dados_hist = {
        'Release': releases,
        'Cards Concluídos': [45, 52, 48, 55, 51, 58],
        'Story Points': [180, 210, 195, 220, 205, 235],
        'Bugs Encontrados': [12, 15, 10, 18, 14, 11],
        'Hotfixes': [3, 5, 2, 4, 3, 2],
        'Taxa Retrabalho (%)': [18, 22, 15, 25, 19, 14],
        'FPY (%)': [72, 68, 75, 65, 71, 78],
        'DDP (%)': [82, 78, 85, 75, 80, 88],
        'Lead Time (dias)': [9, 10, 8, 10, 8, 7],
    }
    
    df_hist = pd.DataFrame(dados_hist)
    
    # ==== Seção 1: Visão Geral da Evolução ====
    st.markdown("### 📈 Evolução de Qualidade")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # FPY e DDP (métricas de qualidade)
        fig1 = px.line(df_hist, x='Release', y=['FPY (%)', 'DDP (%)'],
                       title='Evolução da Qualidade (FPY e DDP)',
                       markers=True,
                       color_discrete_sequence=['#22c55e', '#3b82f6'])
        fig1.add_hline(y=70, line_dash="dash", annotation_text="Meta FPY ≥ 70%", line_color="#22c55e")
        fig1.add_hline(y=85, line_dash="dash", annotation_text="Meta DDP ≥ 85%", line_color="#3b82f6")
        fig1.update_layout(height=300)
        plotly_chart_themed(fig1, use_container_width=True)
    
    with col2:
        # Taxa de Retrabalho (quanto menor, melhor)
        fig2 = px.line(df_hist, x='Release', y='Taxa Retrabalho (%)',
                       title='Taxa de Retrabalho (menor = melhor)',
                       markers=True,
                       color_discrete_sequence=['#ef4444'])
        fig2.add_hline(y=15, line_dash="dash", annotation_text="Meta ≤ 15%", line_color="#22c55e")
        fig2.update_layout(height=300)
        plotly_chart_themed(fig2, use_container_width=True)
    
    st.markdown("---")
    
    # ==== Seção 2: Volume e Bugs ====
    st.markdown("### 🐛 Evolução de Bugs e Hotfixes")
    
    col3, col4 = st.columns(2)
    
    with col3:
        fig3 = px.bar(df_hist, x='Release', y=['Bugs Encontrados', 'Hotfixes'],
                      title='Bugs e Hotfixes por Release',
                      barmode='group',
                      color_discrete_sequence=['#f97316', '#ef4444'])
        fig3.update_layout(height=280)
        plotly_chart_themed(fig3, use_container_width=True)
    
    with col4:
        # Densidade de bugs (bugs por card)
        df_hist['Densidade Bugs'] = (df_hist['Bugs Encontrados'] / df_hist['Cards Concluídos']).round(2)
        fig4 = px.line(df_hist, x='Release', y='Densidade Bugs',
                       title='Densidade de Bugs (bugs/card)',
                       markers=True,
                       color_discrete_sequence=['#8b5cf6'])
        fig4.add_hline(y=0.2, line_dash="dash", annotation_text="Meta ≤ 0.2", line_color="#22c55e")
        fig4.update_layout(height=280)
        plotly_chart_themed(fig4, use_container_width=True)
    
    st.markdown("---")
    
    # ==== Seção 3: Lead Time e Produtividade ====
    st.markdown("### ⏱️ Produtividade e Lead Time")
    
    col5, col6 = st.columns(2)
    
    with col5:
        fig5 = px.line(df_hist, x='Release', y='Lead Time (dias)',
                       title='Lead Time Médio por Release',
                       markers=True,
                       color_discrete_sequence=['#6366f1'])
        fig5.add_hline(y=7, line_dash="dash", annotation_text="Meta ≤ 7 dias", line_color="#22c55e")
        fig5.update_layout(height=280)
        plotly_chart_themed(fig5, use_container_width=True)
    
    with col6:
        fig6 = px.bar(df_hist, x='Release', y=['Cards Concluídos', 'Story Points'],
                      title='Produtividade por Release',
                      barmode='group',
                      color_discrete_sequence=['#3b82f6', '#22c55e'])
        fig6.update_layout(height=280)
        plotly_chart_themed(fig6, use_container_width=True)
    
    st.markdown("---")
    
    # ==== Seção 4: Tabela Completa ====
    st.markdown("### 📊 Tabela de Histórico Completo")
    
    # Adicionar indicadores visuais
    def colorir_tendencia(val, col):
        """Adiciona cor baseada na tendência."""
        if isinstance(val, (int, float)):
            if col in ['FPY (%)', 'DDP (%)']:
                return 'background-color: rgba(34, 197, 94, 0.2)' if val >= 70 else 'background-color: rgba(239, 68, 68, 0.2)'
            elif col in ['Taxa Retrabalho (%)', 'Density Bugs']:
                return 'background-color: rgba(34, 197, 94, 0.2)' if val <= 15 else 'background-color: rgba(239, 68, 68, 0.2)'
        return ''
    
    st.dataframe(df_hist, hide_index=True, use_container_width=True)
    
    # ==== Seção 5: Insights e Tendências ====
    st.markdown("### 💡 Análise de Tendências")
    
    col_trend1, col_trend2 = st.columns(2)
    
    with col_trend1:
        # Calcular tendências
        fpy_trend = df_hist['FPY (%)'].iloc[-1] - df_hist['FPY (%)'].iloc[0]
        retrabalho_trend = df_hist['Taxa Retrabalho (%)'].iloc[-1] - df_hist['Taxa Retrabalho (%)'].iloc[0]
        
        fpy_emoji = "📈" if fpy_trend > 0 else "📉" if fpy_trend < 0 else "➡️"
        retrabalho_emoji = "📈" if retrabalho_trend < 0 else "📉" if retrabalho_trend > 0 else "➡️"
        
        st.markdown(f"""
        **Tendências Identificadas:**
        
        - {fpy_emoji} **FPY**: {'Melhorando' if fpy_trend > 0 else 'Piorando' if fpy_trend < 0 else 'Estável'} ({fpy_trend:+.1f}% no período)
        - {retrabalho_emoji} **Retrabalho**: {'Melhorando' if retrabalho_trend < 0 else 'Piorando' if retrabalho_trend > 0 else 'Estável'} ({retrabalho_trend:+.1f}% no período)
        """)
    
    with col_trend2:
        # Média do período
        st.markdown(f"""
        **Médias do Período:**
        
        - 📊 **Cards/Release**: {df_hist['Cards Concluídos'].mean():.0f}
        - 🐛 **Bugs/Release**: {df_hist['Bugs Encontrados'].mean():.1f}
        - ⏱️ **Lead Time Médio**: {df_hist['Lead Time (dias)'].mean():.1f} dias
        - ✅ **FPY Médio**: {df_hist['FPY (%)'].mean():.1f}%
        """)
    
    st.markdown("---")
    st.caption("💡 **Dica**: Para dados históricos reais, configure a integração com o Jira para coletar métricas automaticamente ao final de cada release.")


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    st.set_page_config(
        page_title="Dashboard QA - NINA",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # APLICAR DESIGN SYSTEM NINA DARK v6.0
    aplicar_estilos()
    
    # Logo NINA cinza (para dark mode) - SVG inline
    logo_svg = '''<svg width="56" height="56" viewBox="0 0 187 187" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M173.709 89.2107C172.209 86.6048 169.414 84.838 166.225 84.838C163.036 84.838 160.241 86.5649 158.741 89.1627H151.683C149.465 58.8237 124.495 35 94.0216 35C63.5489 35 38.5862 58.8237 36.3678 89.1627H29.1759C27.6759 86.5649 24.8734 84.798 21.6682 84.798C18.463 84.798 15.6605 86.5806 14.1605 89.2031C13.4184 90.4899 13 92.001 13 93.6C13 95.1987 13.4184 96.7017 14.1605 97.997C15.6605 100.619 18.463 102.306 21.6682 102.306C24.8734 102.306 27.6838 100.435 29.1759 97.8369H36.3678C38.5862 128.168 63.5489 152 94.0216 152C124.495 152 149.465 128.176 151.675 97.8369H158.686C160.178 100.435 162.996 102.354 166.217 102.354C169.438 102.354 172.256 100.611 173.749 97.9648C174.475 96.6856 174.885 95.2148 174.885 93.6319C174.885 92.049 174.451 90.5222 173.701 89.2188L173.709 89.2107ZM111.145 125.554C107.971 131.518 101.758 135.459 94.5981 135.459C87.4374 135.459 81.2248 131.566 78.0509 125.602C77.1666 123.947 78.3667 122.092 80.2219 122.092H108.982C110.837 122.092 112.029 123.891 111.153 125.554H111.145ZM140.528 94.1277C140.528 103.825 132.76 111.691 123.184 111.691H65.4432C55.8675 111.691 48.0991 103.825 48.0991 94.1277V93.7199C48.0991 84.0223 55.8675 76.1557 65.4432 76.1557H123.184C132.76 76.1557 140.528 84.0223 140.528 93.7199V94.1277Z" fill="#d1d5db"/>
    <path d="M76.5809 105.311C82.9686 105.311 88.1466 100.068 88.1466 93.5996C88.1466 87.1312 82.9686 81.8875 76.5809 81.8875C70.1936 81.8875 65.0156 87.1312 65.0156 93.5996C65.0156 100.068 70.1936 105.311 76.5809 105.311Z" fill="#d1d5db"/>
    <path d="M111.437 105.311C117.824 105.311 123.002 100.068 123.002 93.5996C123.002 87.1312 117.824 81.8875 111.437 81.8875C105.049 81.8875 99.8712 87.1312 99.8712 93.5996C99.8712 100.068 105.049 105.311 111.437 105.311Z" fill="#d1d5db"/>
    </svg>'''
    
    # ========== HEADER COM LOGO CENTRALIZADA ==========
    st.markdown(f'''
    <div class="nina-header">
        {logo_svg}
        <div class="nina-header-title">Dashboard de Qualidade</div>
        <div class="nina-header-subtitle">NINA Tecnologia | Métricas ISTQB/CTFL</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configurações")
        
        # Credenciais Jira
        st.markdown("#### 🔐 Conexão Jira")
        
        env_email = os.getenv("JIRA_EMAIL", "")
        env_token = os.getenv("JIRA_TOKEN", "")
        
        if env_email:
            st.success(f"✅ Conectado: {env_email.split('@')[0]}...")
        else:
            st.text_input("Email", key="jira_email", placeholder="email@empresa.com")
            st.text_input("API Token", type="password", key="jira_token")
        
        status = "✅ Conectado ao Jira" if verificar_credenciais() else "⚠️ Modo Demonstração"
        st.caption(status)
        
        st.markdown("---")
        
        # Projeto
        st.markdown("#### 📁 Projeto")
        
        projetos_disponiveis = list(PROJETOS.keys())
        projeto = st.selectbox(
            "Projeto principal",
            projetos_disponiveis,
            index=0,
            format_func=lambda x: f"{x} - {PROJETOS[x]['nome']}"
        )
        
        st.caption("💡 SD = Desenvolvimento (foco principal)")
        
        st.markdown("---")
        
        # Release
        st.markdown("#### 📅 Release")
        data_release = st.date_input("Data da Release", 
                                     value=datetime.now() + timedelta(days=10))
        
        st.markdown("---")
        
        # Botões de ação
        col1, col2 = st.columns(2)
        with col1:
            carregar_jira = st.button("🔄 Carregar Jira", use_container_width=True)
        with col2:
            usar_demo = st.button("📊 Usar Demo", use_container_width=True)
        
        if carregar_jira:
            if verificar_credenciais():
                with st.spinner("Buscando dados do Jira..."):
                    jql = f'project = "{projeto}" AND sprint in openSprints() ORDER BY created DESC'
                    issues = buscar_jira(jql)
                    if issues:
                        st.session_state.dados = processar_issues(issues, 
                                                datetime.combine(data_release, datetime.min.time()))
                        st.session_state.projeto = projeto
                        st.session_state.ultima_atualizacao = datetime.now()
                        st.success(f"✅ {len(issues)} cards carregados!")
                        st.rerun()
                    else:
                        # Tentar query alternativa
                        jql_alt = f'project = "{projeto}" AND updated >= -90d ORDER BY updated DESC'
                        issues = buscar_jira(jql_alt)
                        if issues:
                            st.session_state.dados = processar_issues(issues, 
                                                    datetime.combine(data_release, datetime.min.time()))
                            st.session_state.projeto = projeto
                            st.session_state.ultima_atualizacao = datetime.now()
                            st.success(f"✅ {len(issues)} cards carregados (últimos 90 dias)!")
                            st.rerun()
                        else:
                            st.error("Nenhum card encontrado.")
            else:
                st.warning("Configure as credenciais do Jira!")
        
        if usar_demo:
            st.session_state.dados = gerar_dados_mock(projeto)
            st.session_state.projeto = projeto
            st.session_state.ultima_atualizacao = datetime.now()
            st.rerun()
        
        st.markdown("---")
        
        # Legenda das métricas
        st.markdown("**📚 Métricas ISTQB/CTFL:**")
        st.markdown("""
        - **DDP**: Detecção de Defeitos
        - **FPY**: Aprovação de Primeira
        - **MTTR**: Tempo Médio de Correção
        - **FK**: Fator K (Maturidade)
        """)
        
        st.caption("Dashboard v5.0 | NINA Tecnologia")
    
    # Mostrar indicador de atualização (sempre visível)
    if 'ultima_atualizacao' in st.session_state:
        delta = datetime.now() - st.session_state.ultima_atualizacao
        minutos = delta.seconds // 60
        horas = delta.seconds // 3600
        
        if horas > 0:
            tempo_str = f"{horas}h {minutos % 60}min"
        elif minutos > 0:
            tempo_str = f"{minutos} min"
        else:
            tempo_str = "agora"
        
        st.markdown(f"""
        <div class="update-indicator">
            Atualizado há {tempo_str}
        </div>
        """, unsafe_allow_html=True)
    
    # Inicializar dados
    if 'dados' not in st.session_state:
        st.session_state.dados = gerar_dados_mock("SD")
        st.session_state.projeto = "SD"
        st.session_state.ultima_atualizacao = datetime.now()
    
    df = st.session_state.dados
    projeto_atual = st.session_state.get('projeto', 'SD')
    
    # Info da release (sem título duplicado - já está no header)
    release_atual = df['sprint'].mode().iloc[0] if not df.empty else "N/A"
    # Converter nome do sprint para Release se possível
    if release_atual and 'Sprint' in str(release_atual):
        release_atual = release_atual.replace('Sprint', 'Release')
    modo = "Jira" if verificar_credenciais() else "Demonstração"
    st.caption(f"Release: **{release_atual}** | Cards: **{len(df)}** | Modo: **{modo}**")
    
    # Tabs
    tabs = st.tabs(["🎯 Liderança", "🧪 QA", "👨‍💻 Desenvolvimento", "📜 Histórico"])
    
    with tabs[0]:
        aba_lideranca(df)
    
    with tabs[1]:
        aba_qa(df)
    
    with tabs[2]:
        aba_dev(df)
    
    with tabs[3]:
        aba_historico()
    
    # Footer
    st.markdown("---")
    st.caption(f"📅 Atualizado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')} | Dashboard v5.0 - NINA Tecnologia")


if __name__ == "__main__":
    main()
