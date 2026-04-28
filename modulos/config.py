"""
📋 CONFIG - Configurações Globais do NinaDash

Este módulo contém TODAS as constantes, mapeamentos e configurações
usadas em toda a aplicação.
"""

import streamlit as st

# ==============================================================================
# CONFIGURAÇÃO INICIAL DA PÁGINA
# ==============================================================================

# Logo SVG da Nina
NINA_LOGO_SVG = '''<svg width="187" height="187" viewBox="0 0 187 187" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M173.709 89.2107C172.209 86.6048 169.414 84.838 166.225 84.838C163.036 84.838 160.241 86.5649 158.741 89.1627H151.683C149.465 58.8237 124.495 35 94.0216 35C63.5489 35 38.5862 58.8237 36.3678 89.1627H29.1759C27.6759 86.5649 24.8734 84.798 21.6682 84.798C18.463 84.798 15.6605 86.5806 14.1605 89.2031C13.4184 90.4899 13 92.001 13 93.6C13 95.1987 13.4184 96.7017 14.1605 97.997C15.6605 100.619 18.463 102.306 21.6682 102.306C24.8734 102.306 27.6838 100.435 29.1759 97.8369H36.3678C38.5862 128.168 63.5489 152 94.0216 152C124.495 152 149.465 128.176 151.675 97.8369H158.686C160.178 100.435 162.996 102.354 166.217 102.354C169.438 102.354 172.256 100.611 173.749 97.9648C174.475 96.6856 174.885 95.2148 174.885 93.6319C174.885 92.049 174.451 90.5222 173.701 89.2188L173.709 89.2107ZM111.145 125.554C107.971 131.518 101.758 135.459 94.5981 135.459C87.4374 135.459 81.2248 131.566 78.0509 125.602C77.1666 123.947 78.3667 122.092 80.2219 122.092H108.982C110.837 122.092 112.029 123.891 111.153 125.554H111.145ZM140.528 94.1277C140.528 103.825 132.76 111.691 123.184 111.691H65.4432C55.8675 111.691 48.0991 103.825 48.0991 94.1277V93.7199C48.0991 84.0223 55.8675 76.1557 65.4432 76.1557H123.184C132.76 76.1557 140.528 84.0223 140.528 93.7199V94.1277Z" fill="#AF0C37"/>
<path d="M76.5809 105.311C82.9686 105.311 88.1466 100.068 88.1466 93.5996C88.1466 87.1312 82.9686 81.8875 76.5809 81.8875C70.1936 81.8875 65.0156 87.1312 65.0156 93.5996C65.0156 100.068 70.1936 105.311 76.5809 105.311Z" fill="#AF0C37"/>
<path d="M111.437 105.311C117.824 105.311 123.002 100.068 123.002 93.5996C123.002 87.1312 117.824 81.8875 111.437 81.8875C105.049 81.8875 99.8712 87.1312 99.8712 93.5996C99.8712 100.068 105.049 105.311 111.437 105.311Z" fill="#AF0C37"/>
</svg>'''

def configure_page():
    """Configura a página Streamlit. DEVE ser chamado no início de app.py"""
    st.set_page_config(
        page_title="NinaDash - Qualidade e Decisão de Software",
        page_icon="favicon.svg",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# ==============================================================================
# API JIRA
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
    "temas": "customfield_10520",
    "importancia": "customfield_10522",
    "sla_status": "customfield_11124",
    "ambiente_desenvolvido": "customfield_10586",
}

# ==============================================================================
# TEMAS E CLIENTES
# ==============================================================================

TEMAS_NAO_CLIENTES = [
    "nina",
    "interna",
    "interno",
    "internal",
    "nina tecnologia",
    "nina - interno",
    "plataforma",
]

NINADASH_URL = "https://ninadash.streamlit.app/"

# ==============================================================================
# STATUS E FLUXO
# ==============================================================================

STATUS_FLOW = {
    "backlog": ["Backlog", "To Do", "Tarefas pendentes"],
    "development": ["Em andamento", "EM DESENVOLVIMENTO"],
    "code_review": ["EM REVISÃO"],
    "waiting_qa": ["AGUARDANDO VALIDAÇÃO"],
    "testing": ["EM VALIDAÇÃO"],
    "done": ["Concluído", "ENTREGUE"],
    "blocked": ["IMPEDIDO"],
    "rejected": ["REPROVADO"],
    "deferred": ["Validado - Adiado", "DESCARTADO"],
    "pb_revisao_produto": ["Aguardando Revisão de Produto", "Revisão de Produto", "Análise de Produto", "AGUARDA REVISÃO DE PRODUTO"],
    "pb_roteiro": ["Em Roteiro", "Roteiro", "Definição de Roteiro"],
    "pb_ux": ["UX/Design", "UX Design", "Análise UX", "UX/UI", "AGUARDA UX"],
    "pb_esforco": ["Aguardando Esforço", "Estimativa de Esforço", "Aguarda Esforço", "AGUARDA ESFORÇO"],
    "pb_aguarda_dev": ["Aguardando Desenvolvimento", "Aguarda Desenvolvimento", "Fila de Desenvolvimento", "AGUARDA DESENVOLVIMENTO"],
    "pb_aguardando_resposta": ["Aguardando Resposta", "Aguardando Cliente", "Aguarda Retorno"],
    "valprod_pendente": ["Pendente", "Aguardando Validação", "Para Validar"],
    "valprod_validando": ["Em Validação", "Validando"],
    "valprod_aprovado": ["Aprovado", "Validado", "Concluído"],
    "valprod_rejeitado": ["Rejeitado", "Reprovado", "Com Problemas"],
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
    "unknown": "❓ Desconhecido",
    "pb_revisao_produto": "📝 Revisão Produto",
    "pb_roteiro": "📋 Em Roteiro",
    "pb_ux": "🎨 UX/Design",
    "pb_esforco": "⏱️ Aguarda Esforço",
    "pb_aguarda_dev": "💻 Aguarda Dev",
    "pb_aguardando_resposta": "💬 Aguardando Resposta",
    "valprod_pendente": "⏳ Pendente Val Prod",
    "valprod_validando": "🔍 Validando",
    "valprod_aprovado": "✅ Aprovado",
    "valprod_rejeitado": "❌ Rejeitado",
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
    "unknown": "#9ca3af",
    "pb_revisao_produto": "#6366f1",
    "pb_roteiro": "#8b5cf6",
    "pb_ux": "#ec4899",
    "pb_esforco": "#f97316",
    "pb_aguarda_dev": "#14b8a6",
    "pb_aguardando_resposta": "#f59e0b",
    "valprod_pendente": "#f59e0b",
    "valprod_validando": "#3b82f6",
    "valprod_aprovado": "#22c55e",
    "valprod_rejeitado": "#ef4444",
}

# ==============================================================================
# TRADUÇÃO DE LINK TYPES
# ==============================================================================

TRADUCAO_LINK_TYPES = {
    "Relates": "Relacionado",
    "Blocks": "Bloqueia",
    "Clones": "Clone",
    "Duplicate": "Duplicado",
    "Parent": "Pai",
    "Subtask": "Subtarefa",
    "Epic Link": "Épico",
    "Polaris work item link": "Implementação",
    "Issue split": "Divisão",
    "relates to": "relacionado a",
    "is related to": "relacionado a",
    "blocks": "bloqueia",
    "is blocked by": "bloqueado por",
    "clones": "clona",
    "is cloned by": "clonado por",
    "duplicates": "duplica",
    "is duplicated by": "duplicado por",
    "implements": "implementa",
    "is implemented by": "implementado por",
    "is split by": "dividido por",
    "split to": "dividido para",
    "is parent of": "é pai de",
    "is child of": "é filho de",
    "depends on": "depende de",
    "is depended on by": "dependência de",
}

# ==============================================================================
# ETAPAS DO PB
# ==============================================================================

PB_FUNIL_ETAPAS = [
    ("pb_revisao_produto", "📝 Revisão Produto"),
    ("pb_ux", "🎨 UX/Design"),
    ("pb_esforco", "⏱️ Aguarda Esforço"),
    ("pb_aguarda_dev", "💻 Aguarda Dev"),
]

# ==============================================================================
# REGRAS E DEFAULTS
# ==============================================================================

REGRAS = {
    "hotfix_sp_default": 2,
    "cache_ttl_minutos": 5,
    "dias_aging_alerta": 3,
    "janela_complexidade": {
        "Alta": 3,
        "Média": 2,
        "Baixa": 1,
        "default": 3,
    },
}

# ==============================================================================
# TOOLTIPS - EXPLICAÇÃO DAS MÉTRICAS
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
        "titulo": "FPY - First Pass Yield",
        "descricao": "Percentual de cards aprovados na PRIMEIRA validação, sem nenhum bug. Indica a qualidade do código entregue.",
        "formula": "FPY = (Cards sem bugs / Total de cards) × 100",
        "interpretacao": {
            "≥80%": "Excelente - Código de alta qualidade",
            "60-79%": "Bom - Dentro do esperado",
            "40-59%": "Regular - Revisar práticas",
            "<40%": "Crítico - Alto retrabalho"
        },
        "fonte": "Six Sigma / Lean Manufacturing"
    },
    "lead_time": {
        "titulo": "Lead Time (Tempo de Ciclo Total)",
        "descricao": "Tempo total desde a criação do card até sua conclusão.",
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
        "descricao": "Pontuação composta que avalia a saúde geral da release.",
        "formula": "HS = (Conclusão×30 + DDP×25 + FPY×20 + Gargalos×15 + LeadTime×10) / 100",
        "interpretacao": {
            "≥75": "🟢 Saudável",
            "50-74": "🟡 Atenção",
            "25-49": "🟠 Alerta",
            "<25": "🔴 Crítico"
        },
        "fonte": "ISTQB Test Process Improvement"
    },
    "throughput": {
        "titulo": "Throughput (Vazão)",
        "descricao": "Quantidade de cards concluídos por período.",
        "formula": "Throughput = Cards concluídos / Período",
        "interpretacao": {
            "Crescente": "Time ganhando velocidade",
            "Estável": "Capacidade previsível",
            "Decrescente": "Investigar impedimentos"
        },
        "fonte": "Kanban Metrics"
    },
    "wip": {
        "titulo": "WIP - Work In Progress",
        "descricao": "Quantidade de cards em andamento simultaneamente.",
        "formula": "WIP = Cards não concluídos",
        "interpretacao": {
            "≤ Capacidade": "Fluxo saudável",
            "> Capacidade": "Sobrecarga"
        },
        "fonte": "Kanban"
    },
    "defect_density": {
        "titulo": "Densidade de Defeitos",
        "descricao": "Quantidade de bugs por Story Point.",
        "formula": "DD = Total de Bugs / Total de SP",
        "interpretacao": {
            "≤0.2": "Baixa - Excelente",
            "0.21-0.5": "Aceitável",
            "0.51-1.0": "Alta",
            ">1.0": "Crítico"
        },
        "fonte": "IEEE 982.1"
    },
}

# ==============================================================================
# CATÁLOGO E CATEGORIAS DE MÉTRICAS (para dashboard personalizado)
# ==============================================================================

CATEGORIAS_METRICAS = [
    "📊 Qualidade",
    "🚀 Produtividade", 
    "🐛 Bugs",
    "🔬 QA",
    "👨‍💻 Desenvolvimento",
    "📋 Status",
    "📦 Produto",
    "🎯 Concentração",
    "🏢 Clientes",
]

CATALOGO_METRICAS = {
    # === MÉTRICAS DE QUALIDADE ===
    "fator_k_geral": {
        "nome": "Fator K (Geral)",
        "categoria": "📊 Qualidade",
        "descricao": "Razão entre Story Points e Bugs do projeto inteiro",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_fator_k_geral"
    },
    "fator_k_dev": {
        "nome": "Fator K por Desenvolvedor",
        "categoria": "📊 Qualidade",
        "descricao": "Fator K individual de cada desenvolvedor",
        "tipo": "tabela",
        "parametros": ["desenvolvedor"],
        "funcao": "calcular_fator_k_dev"
    },
    "fpy": {
        "nome": "FPY - First Pass Yield",
        "categoria": "📊 Qualidade",
        "descricao": "% de cards aprovados na primeira validação",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_fpy"
    },
    "ddp": {
        "nome": "DDP - Defect Detection",
        "categoria": "📊 Qualidade",
        "descricao": "% de defeitos encontrados antes da produção",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_ddp"
    },
    "health_score": {
        "nome": "Health Score",
        "categoria": "📊 Qualidade",
        "descricao": "Pontuação de saúde da release (0-100)",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_health_score"
    },
    
    # === MÉTRICAS DE PRODUTIVIDADE ===
    "throughput_cards": {
        "nome": "Throughput (Cards)",
        "categoria": "🚀 Produtividade",
        "descricao": "Quantidade de cards concluídos",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_throughput_cards"
    },
    "throughput_sp": {
        "nome": "Throughput (Story Points)",
        "categoria": "🚀 Produtividade",
        "descricao": "Quantidade de SP entregues",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_throughput_sp"
    },
    "lead_time": {
        "nome": "Lead Time Médio",
        "categoria": "🚀 Produtividade",
        "descricao": "Tempo médio do card (criação → conclusão)",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_lead_time"
    },
    "wip": {
        "nome": "WIP - Work In Progress",
        "categoria": "🚀 Produtividade",
        "descricao": "Cards em andamento agora",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_wip"
    },
    "velocidade_media": {
        "nome": "Velocidade Média",
        "categoria": "🚀 Produtividade",
        "descricao": "SP médio por card concluído",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_velocidade_media"
    },
    
    # === MÉTRICAS DE BUGS ===
    "total_bugs": {
        "nome": "Total de Bugs",
        "categoria": "🐛 Bugs",
        "descricao": "Quantidade total de bugs encontrados",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_total_bugs"
    },
    "densidade_bugs": {
        "nome": "Densidade de Bugs",
        "categoria": "🐛 Bugs",
        "descricao": "Bugs por Story Point",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_densidade_bugs"
    },
    "bugs_por_dev": {
        "nome": "Bugs por Desenvolvedor",
        "categoria": "🐛 Bugs",
        "descricao": "Ranking de bugs por desenvolvedor",
        "tipo": "grafico_barra",
        "parametros": [],
        "funcao": "calcular_bugs_por_dev"
    },
    
    # === MÉTRICAS DE QA ===
    "carga_qa": {
        "nome": "Carga por QA",
        "categoria": "🔬 QA",
        "descricao": "Cards em validação por QA",
        "tipo": "grafico_barra",
        "parametros": ["qa"],
        "funcao": "calcular_carga_qa"
    },
    "funil_qa": {
        "nome": "Funil de QA",
        "categoria": "🔬 QA",
        "descricao": "Status do funil de validação",
        "tipo": "grafico_funil",
        "parametros": [],
        "funcao": "calcular_funil_qa"
    },
    "aging_qa": {
        "nome": "Aging QA",
        "categoria": "🔬 QA",
        "descricao": "Cards aguardando validação há muito tempo",
        "tipo": "tabela",
        "parametros": [],
        "funcao": "calcular_aging_qa"
    },
    "taxa_reprovacao": {
        "nome": "Taxa de Reprovação",
        "categoria": "🔬 QA",
        "descricao": "% de cards reprovados",
        "tipo": "kpi",
        "parametros": [],
        "funcao": "calcular_taxa_reprovacao"
    },
    
    # === MÉTRICAS DE DESENVOLVIMENTO ===
    "ranking_devs": {
        "nome": "Ranking de Desenvolvedores",
        "categoria": "👨‍💻 Desenvolvimento",
        "descricao": "Ranking por Fator K, SP e bugs",
        "tipo": "tabela",
        "parametros": [],
        "funcao": "calcular_ranking_devs"
    },
    "code_review_fila": {
        "nome": "Fila de Code Review",
        "categoria": "👨‍💻 Desenvolvimento",
        "descricao": "Cards aguardando code review",
        "tipo": "lista_cards",
        "parametros": [],
        "funcao": "calcular_code_review_fila"
    },
    "cards_por_dev": {
        "nome": "Cards por Desenvolvedor",
        "categoria": "👨‍💻 Desenvolvimento",
        "descricao": "Distribuição de cards por desenvolvedor",
        "tipo": "grafico_pizza",
        "parametros": [],
        "funcao": "calcular_cards_por_dev"
    },
    
    # === MÉTRICAS DE STATUS ===
    "cards_por_status": {
        "nome": "Cards por Status",
        "categoria": "📋 Status",
        "descricao": "Distribuição de cards por status",
        "tipo": "grafico_barra",
        "parametros": [],
        "funcao": "calcular_cards_por_status"
    },
    "cards_aguardando_qa": {
        "nome": "Aguardando QA",
        "categoria": "📋 Status",
        "descricao": "Cards aguardando validação",
        "tipo": "lista_cards",
        "parametros": [],
        "funcao": "calcular_aguardando_qa"
    },
    "cards_impedidos": {
        "nome": "Cards Impedidos",
        "categoria": "📋 Status",
        "descricao": "Cards com impedimentos",
        "tipo": "lista_cards",
        "parametros": [],
        "funcao": "calcular_impedidos"
    },
    "cards_bloqueados": {
        "nome": "Cards Bloqueados",
        "categoria": "📋 Status",
        "descricao": "Cards bloqueados",
        "tipo": "lista_cards",
        "parametros": [],
        "funcao": "calcular_bloqueados"
    },
    
    # === MÉTRICAS DE PRODUTO ===
    "por_produto": {
        "nome": "Cards por Produto",
        "categoria": "📦 Produto",
        "descricao": "Distribuição por produto",
        "tipo": "grafico_pizza",
        "parametros": [],
        "funcao": "calcular_por_produto"
    },
    "hotfix_por_produto": {
        "nome": "Hotfixes por Produto",
        "categoria": "📦 Produto",
        "descricao": "Hotfixes agrupados por produto",
        "tipo": "grafico_barra",
        "parametros": [],
        "funcao": "calcular_hotfix_produto"
    },
    
    # === MÉTRICAS DE CONCENTRAÇÃO ===
    "concentracao_dev": {
        "nome": "Concentração DEV",
        "categoria": "🎯 Concentração",
        "descricao": "Concentração de conhecimento por DEV",
        "tipo": "heatmap",
        "parametros": [],
        "funcao": "calcular_concentracao_dev"
    },
    "concentracao_qa": {
        "nome": "Concentração QA",
        "categoria": "🎯 Concentração",
        "descricao": "Concentração de conhecimento por QA",
        "tipo": "heatmap",
        "parametros": [],
        "funcao": "calcular_concentracao_qa"
    },
    
    # === MÉTRICAS DE CLIENTE ===
    "top_clientes": {
        "nome": "Top Clientes",
        "categoria": "🏢 Clientes",
        "descricao": "Clientes com mais cards",
        "tipo": "grafico_barra",
        "parametros": [],
        "funcao": "calcular_top_clientes"
    },
    "clientes_bugs": {
        "nome": "Bugs por Cliente",
        "categoria": "🏢 Clientes",
        "descricao": "Clientes com mais bugs reportados",
        "tipo": "grafico_barra",
        "parametros": [],
        "funcao": "calcular_clientes_bugs"
    },
}
