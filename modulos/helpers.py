"""
================================================================================
MÓDULO HELPERS - NinaDash v8.82
================================================================================
Helpers & Utilities - Funções auxiliares

Dependências:
- streamlit, pandas, plotly, datetime
- modulos.config, modulos.utils, modulos.calculos, modulos.jira_api, modulos.processamento

Author: GitHub Copilot
Version: 1.0 (Phase 7)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

from modulos.config import (
    JIRA_BASE_URL, CUSTOM_FIELDS, STATUS_FLOW, STATUS_NOMES, STATUS_CORES,
    TOOLTIPS, REGRAS, PB_FUNIL_ETAPAS, TEMAS_NAO_CLIENTES
)
from modulos.utils import (
    link_jira, card_link_com_popup, traduzir_link,
    calcular_dias_necessarios_validacao, avaliar_janela_validacao, get_secrets
)
from modulos.calculos import (
    calcular_fator_k, calcular_ddp, calcular_fpy, calcular_lead_time,
    analisar_dev_detalhado, filtrar_qas_principais,
    calcular_concentracao_conhecimento, gerar_recomendacoes_rodizio,
    calcular_metricas_governanca, calcular_metricas_qa, calcular_metricas_produto,
    calcular_health_score, calcular_metricas_dev, calcular_metricas_backlog
)
from modulos.jira_api import (
    buscar_dados_jira_cached, buscar_card_especifico,
    gerar_icone_tabler, gerar_badge_status, obter_icone_status,
    extrair_historico_transicoes, extrair_texto_adf
)


# ==============================================================================
# FUNÇÕES DO MÓDULO
# ==============================================================================

def calcular_valor_metrica(metrica_key: str, df: pd.DataFrame):
    """Calcula o valor de uma métrica KPI."""
    try:
        if metrica_key == "fator_k_geral":
            total_sp = df['story_points'].sum()
            total_bugs = df['bugs_encontrados'].sum()
            return f"{total_sp / (total_bugs + 1):.2f}"
        
        elif metrica_key == "fpy":
            metricas = calcular_fpy(df)
            return f"{metricas.get('fpy', 0):.1f}%"
        
        elif metrica_key == "ddp":
            metricas = calcular_ddp(df)
            return f"{metricas.get('ddp', 0):.1f}%"
        
        elif metrica_key == "health_score":
            metricas = calcular_health_score(df)
            return f"{metricas.get('score', 0):.0f}"
        
        elif metrica_key == "throughput_cards":
            concluidos = df[df['status_categoria'] == 'done']
            return str(len(concluidos))
        
        elif metrica_key == "throughput_sp":
            concluidos = df[df['status_categoria'] == 'done']
            return str(int(concluidos['story_points'].sum()))
        
        elif metrica_key == "lead_time":
            metricas = calcular_lead_time(df)
            return f"{metricas.get('media', 0):.1f} dias"
        
        elif metrica_key == "wip":
            em_andamento = df[~df['status_categoria'].isin(['done', 'backlog', 'deferred'])]
            return str(len(em_andamento))
        
        elif metrica_key == "velocidade_media":
            concluidos = df[df['status_categoria'] == 'done']
            if len(concluidos) > 0:
                return f"{concluidos['story_points'].mean():.1f} SP"
            return "0 SP"
        
        elif metrica_key == "total_bugs":
            return str(int(df['bugs_encontrados'].sum()))
        
        elif metrica_key == "densidade_bugs":
            total_sp = df['story_points'].sum()
            total_bugs = df['bugs_encontrados'].sum()
            if total_sp > 0:
                return f"{total_bugs / total_sp:.2f}"
            return "0.00"
        
        elif metrica_key == "taxa_reprovacao":
            reprovados = df[df['status_categoria'] == 'rejected']
            total = len(df)
            if total > 0:
                return f"{(len(reprovados) / total) * 100:.1f}%"
            return "0%"
        
        return None
    except Exception:
        return None




def calcular_dados_grafico(metrica_key: str, df: pd.DataFrame):
    """Calcula dados para gráficos de barra/pizza."""
    try:
        if metrica_key == "bugs_por_dev":
            bugs_dev = df.groupby('responsavel')['bugs_encontrados'].sum().sort_values(ascending=False)
            return bugs_dev.head(10)
        
        elif metrica_key == "carga_qa":
            em_qa = df[df['status_categoria'].isin(['waiting_qa', 'testing'])]
            return em_qa['qa_responsavel'].value_counts().head(10)
        
        elif metrica_key == "cards_por_status":
            return df['status'].value_counts()
        
        elif metrica_key == "cards_por_dev":
            return df['responsavel'].value_counts().head(10)
        
        elif metrica_key == "por_produto":
            return df['produto'].value_counts()
        
        elif metrica_key == "hotfix_produto":
            hotfixes = df[df['tipo'].str.lower().str.contains('hotfix', na=False)]
            return hotfixes['produto'].value_counts()
        
        elif metrica_key == "top_clientes":
            if 'temas' in df.columns:
                # Extrai clientes dos temas
                clientes = []
                for temas in df['temas'].dropna():
                    if isinstance(temas, list):
                        clientes.extend(temas)
                    elif isinstance(temas, str):
                        clientes.append(temas)
                return pd.Series(clientes).value_counts().head(10)
            return pd.Series()
        
        elif metrica_key == "clientes_bugs":
            if 'temas' in df.columns:
                df_com_bugs = df[df['bugs_encontrados'] > 0]
                clientes = []
                for _, row in df_com_bugs.iterrows():
                    temas = row.get('temas', [])
                    if isinstance(temas, list):
                        for tema in temas:
                            clientes.append(tema)
                return pd.Series(clientes).value_counts().head(10)
            return pd.Series()
        
        return None
    except Exception:
        return None




def calcular_dados_tabela(metrica_key: str, df: pd.DataFrame):
    """Calcula dados para tabelas."""
    try:
        if metrica_key == "ranking_devs":
            # Agrupa por desenvolvedor
            ranking = df.groupby('responsavel').agg({
                'story_points': 'sum',
                'bugs_encontrados': 'sum',
                'key': 'count'
            }).reset_index()
            ranking.columns = ['Desenvolvedor', 'SP', 'Bugs', 'Cards']
            ranking['Fator K'] = ranking['SP'] / (ranking['Bugs'] + 1)
            ranking = ranking.sort_values('Fator K', ascending=False)
            return ranking[['Desenvolvedor', 'Cards', 'SP', 'Bugs', 'Fator K']].head(15)
        
        elif metrica_key == "aging_qa":
            em_qa = df[df['status_categoria'].isin(['waiting_qa', 'testing'])].copy()
            if 'data_criacao' in em_qa.columns:
                em_qa['Dias'] = (datetime.now() - pd.to_datetime(em_qa['data_criacao'])).dt.days
                return em_qa[['key', 'resumo', 'qa_responsavel', 'Dias']].sort_values('Dias', ascending=False).head(10)
            return pd.DataFrame()
        
        elif metrica_key == "fator_k_dev":
            # Similar ao ranking_devs mas focado no FK
            ranking = df.groupby('responsavel').agg({
                'story_points': 'sum',
                'bugs_encontrados': 'sum'
            }).reset_index()
            ranking['Fator K'] = ranking['story_points'] / (ranking['bugs_encontrados'] + 1)
            ranking = ranking.sort_values('Fator K', ascending=False)
            ranking.columns = ['Desenvolvedor', 'SP', 'Bugs', 'Fator K']
            return ranking.head(15)
        
        return None
    except Exception:
        return None




def calcular_dados_heatmap(metrica_key: str, df: pd.DataFrame):
    """Calcula dados para heatmaps."""
    try:
        if metrica_key == "concentracao_dev":
            conc = calcular_concentracao_conhecimento(df)
            return conc.get('matriz_dev')
        
        elif metrica_key == "concentracao_qa":
            conc = calcular_concentracao_conhecimento(df)
            return conc.get('matriz_qa')
        
        return None
    except Exception:
        return None




def calcular_dados_funil(metrica_key: str, df: pd.DataFrame):
    """Calcula dados para gráficos de funil."""
    try:
        if metrica_key == "funil_qa":
            metricas = calcular_metricas_qa(df)
            return metricas
        return None
    except Exception:
        return None




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
    /* Header Nina - Fundo branco para melhor contraste */
    .nina-header {
        background: #ffffff;
        color: #1e293b;
        padding: 20px 25px;
        border-radius: 12px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
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
        color: #1e293b;
    }
    .nina-subtitle {
        font-size: 14px;
        opacity: 0.75;
        margin: 5px 0 0 0;
        color: #64748b;
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
        min-height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: center;
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
    .card-sublabel { font-size: 12px; opacity: 0.6; margin-top: 3px; min-height: 16px; }
    
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
    
    /* Scroll container para listagens */
    .scroll-container {
        max-height: 450px;
        overflow-y: auto;
        padding-right: 8px;
        margin: 10px 0;
        scrollbar-width: thin;
        scrollbar-color: #cbd5e1 #f1f5f9;
    }
    .scroll-container::-webkit-scrollbar {
        width: 6px;
    }
    .scroll-container::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 3px;
    }
    .scroll-container::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 3px;
    }
    .scroll-container::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    
    /* Card de listagem padrão */
    .card-lista {
        background: rgba(100, 100, 100, 0.05);
        padding: 12px 15px;
        margin: 8px 0;
        border-radius: 8px;
        border-left: 4px solid #64748b;
        transition: all 0.2s ease;
    }
    .card-lista:hover {
        transform: translateX(3px);
        background: rgba(100, 100, 100, 0.1);
    }
    /* Variantes coloridas - herdam estilos base */
    .card-lista-amarelo, .card-lista-verde, .card-lista-azul, .card-lista-roxo, .card-lista-vermelho, .card-lista-laranja {
        padding: 12px 15px;
        margin: 8px 0;
        border-radius: 8px;
        border-left: 4px solid;
        transition: all 0.2s ease;
    }
    .card-lista-amarelo:hover, .card-lista-verde:hover, .card-lista-azul:hover, .card-lista-roxo:hover, .card-lista-vermelho:hover, .card-lista-laranja:hover {
        transform: translateX(3px);
        filter: brightness(0.95);
    }
    .card-lista-amarelo { border-left-color: #f59e0b; background: rgba(245, 158, 11, 0.08); }
    .card-lista-verde { border-left-color: #22c55e; background: rgba(34, 197, 94, 0.08); }
    .card-lista-azul { border-left-color: #3b82f6; background: rgba(59, 130, 246, 0.08); }
    .card-lista-roxo { border-left-color: #8b5cf6; background: rgba(139, 92, 246, 0.08); }
    .card-lista-vermelho { border-left-color: #ef4444; background: rgba(239, 68, 68, 0.08); }
    .card-lista-laranja { border-left-color: #f97316; background: rgba(249, 115, 22, 0.08); }
    
    /* Hide Streamlit elements */
    #MainMenu, .stDeployButton { display: none !important; }
    </style>
    """, unsafe_allow_html=True)




def get_tooltip_help(tooltip_key: str) -> str:
    """Retorna texto de ajuda para st.metric (aparece no ícone ?)."""
    if tooltip_key not in TOOLTIPS:
        return ""
    
    tip = TOOLTIPS[tooltip_key]
    help_text = f"{tip['titulo']}: {tip['descricao']}"
    if tip.get('formula'):
        help_text += f" | Fórmula: {tip['formula']}"
    return help_text


# ==============================================================================
# COMPONENTES UI
# ==============================================================================



def formatar_tempo_relativo(dt: datetime) -> str:
    """
    Formata uma datetime como tempo relativo (ex: "há 5 min", "há 2h", "há 3 dias").
    
    Args:
        dt: datetime a ser formatada
        
    Returns:
        String formatada com tempo relativo
    """
    if dt is None or pd.isna(dt):
        return ""
    
    agora = datetime.now()
    
    # Garante que dt seja datetime
    if isinstance(dt, str):
        try:
            dt = pd.to_datetime(dt)
        except:
            return ""
    
    # Se dt tem timezone, remove para comparação
    if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    
    diff = agora - dt
    segundos = diff.total_seconds()
    
    if segundos < 0:
        return "agora"
    elif segundos < 60:
        return "agora"
    elif segundos < 3600:  # menos de 1 hora
        minutos = int(segundos / 60)
        return f"há {minutos} min"
    elif segundos < 86400:  # menos de 1 dia
        horas = int(segundos / 3600)
        return f"há {horas}h"
    elif segundos < 604800:  # menos de 1 semana
        dias = int(segundos / 86400)
        return f"há {dias}d"
    elif segundos < 2592000:  # menos de 30 dias
        semanas = int(segundos / 604800)
        return f"há {semanas} sem"
    else:
        meses = int(segundos / 2592000)
        return f"há {meses} mês" if meses == 1 else f"há {meses} meses"




def criar_card_metrica(valor: str, titulo: str, cor: str = "blue", subtitulo: str = "", tooltip_key: str = ""):
    """Cria card de métrica visual. tooltip_key é ignorado (usar st.metric com help para tooltips)."""
    # Sempre mostra sublabel para manter altura uniforme
    sublabel_content = subtitulo if subtitulo else "&nbsp;"
    st.markdown(f"""
    <div class="status-card status-{cor}">
        <p class="big-number">{valor}</p>
        <p class="card-label">{titulo}</p>
        <p class="card-sublabel">{sublabel_content}</p>
    </div>
    """, unsafe_allow_html=True)




def gerar_html_card_ticket(row: dict, compacto: bool = False) -> str:
    """Gera HTML de um card de ticket (retorna string, não renderiza)."""
    bugs = row.get('bugs', 0)
    risco = 'high' if bugs >= 3 else 'medium' if bugs >= 1 else 'low'
    card_link = card_link_com_popup(row.get('ticket_id', ''))
    titulo = str(row.get('titulo', ''))[:60] + ('...' if len(str(row.get('titulo', ''))) > 60 else '')
    cor_bug = '#ef4444' if bugs >= 3 else '#f97316' if bugs >= 1 else '#22c55e'
    
    # Ícone de bugs com Tabler
    bug_icon = gerar_icone_tabler_html('bug', tamanho=16, cor=cor_bug)
    
    if compacto:
        return f'<div class="ticket-card ticket-risk-{risco}"><div style="display: flex; justify-content: space-between; align-items: center;">{card_link}<span style="opacity: 0.7;">{row.get("sp", 0)} SP | {bug_icon}{bugs}</span></div><p style="margin: 5px 0 0 0; font-size: 13px; opacity: 0.9;">{titulo}</p></div>'
    else:
        status_badge = gerar_badge_status(row.get("status", "N/A"))
        return f'<div class="ticket-card ticket-risk-{risco}"><div style="display: flex; justify-content: space-between;">{card_link}<span style="color: {cor_bug}; font-weight: bold;">{bug_icon}{bugs} bugs</span></div><p style="margin: 8px 0;">{row.get("titulo", "")}</p><p style="font-size: 12px; opacity: 0.8;"><b>Dev:</b> {row.get("desenvolvedor", "N/A")} | <b>QA:</b> {row.get("qa", "N/A")} | <b>SP:</b> {row.get("sp", 0)} | {status_badge}</p></div>'




