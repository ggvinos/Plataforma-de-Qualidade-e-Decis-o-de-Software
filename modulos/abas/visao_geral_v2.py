"""
================================================================================
ABA: VISÃO GERAL V2 - NinaDash (Decision-Oriented Dashboard)
================================================================================
Versão UX v5 - Layout EXECUTIVO para tomada de decisão.

Filosofia:
- Escaneável em 3 segundos
- Hierarquia visual clara
- Sem truncamento de informações importantes
- Cores usadas com moderação (vermelho só para crítico real)

Hierarquia:
1. Header compacto + Badge de status
2. Card de Decisão: [ STATUS | CONTEXTO COMPLETO | MÉTRICAS ]
3. Grid Principal: [ Problemas | Ações | Progresso ]
4. Indicadores: Mini-cards com cores suaves
5. Expansíveis: Métricas técnicas, detalhes

Author: UX Refactor v5
================================================================================
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

from modulos.config import STATUS_NOMES, STATUS_CORES
from modulos.calculos import (
    calcular_metricas_governanca,
    calcular_fpy,
    calcular_ddp,
    calcular_lead_time,
    calcular_health_score,
    calcular_fator_k,
    classificar_maturidade,
    calcular_metricas_qa,
)
from modulos.helpers import criar_card_metrica, obter_contexto_periodo
from modulos.utils import card_link_com_popup
from modulos.widgets import mostrar_tooltip, mostrar_lista_df_completa


# ==============================================================================
# SISTEMA DE CORES CONSISTENTE
# ==============================================================================

CORES_DECISAO = {
    "critico": "#ef4444",      # Vermelho - Ação imediata
    "alerta": "#f97316",       # Laranja - Precisa atenção
    "atencao": "#f59e0b",      # Amarelo - Monitorar
    "saudavel": "#22c55e",     # Verde - Dentro do esperado
    "neutro": "#6b7280",       # Cinza - Sem dados/N/A
    "info": "#3b82f6",         # Azul - Informativo
}

GRADIENTES_DECISAO = {
    "go": "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
    "atencao": "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
    "risco": "linear-gradient(135deg, #f97316 0%, #ea580c 100%)",
    "nogo": "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)",
}


# ==============================================================================
# METAS E THRESHOLDS PARA DECISÃO
# ==============================================================================

METAS_SPRINT = {
    "pct_conclusao": {
        "meta": 80,       # Meta de % concluído no final
        "alerta": 60,     # Abaixo disso é alerta
        "critico": 40,    # Abaixo disso é crítico
    },
    "bugs_max": {
        "saudavel": 10,   # Até 10 bugs é OK
        "alerta": 20,     # 10-20 é alerta
        # Acima de 20 é crítico
    },
    "health_score": {
        "go": 75,         # Acima de 75 = GO
        "atencao": 50,    # 50-75 = Atenção
        "risco": 25,      # 25-50 = Risco
        # Abaixo de 25 = NO-GO
    },
    "dias_restantes": {
        "confortavel": 5, # Mais de 5 dias = confortável
        "alerta": 3,      # 3-5 dias = alerta
        "critico": 1,     # 1-2 dias = crítico
    },
    "fpy": {
        "excelente": 80,
        "bom": 60,
        "ruim": 40,
    },
    "ddp": {
        "excelente": 85,
        "bom": 70,
        "ruim": 50,
    }
}


# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================

def calcular_progresso_esperado(dias_passados: int, dias_total: int) -> float:
    """Calcula o progresso esperado baseado no tempo decorrido."""
    if dias_total <= 0:
        return 100.0
    return min(100.0, (dias_passados / dias_total) * 100)


def avaliar_status_sprint(pct_atual: float, pct_esperado: float) -> dict:
    """Avalia se a sprint está adiantada, no ritmo ou atrasada."""
    diff = pct_atual - pct_esperado
    
    if diff >= 5:
        return {"status": "adiantado", "emoji": "🚀", "cor": CORES_DECISAO["saudavel"], "texto": "Adiantado"}
    elif diff >= -5:
        return {"status": "no_ritmo", "emoji": "✅", "cor": CORES_DECISAO["saudavel"], "texto": "No Ritmo"}
    elif diff >= -15:
        return {"status": "atencao", "emoji": "⚠️", "cor": CORES_DECISAO["atencao"], "texto": "Levemente Atrasado"}
    else:
        return {"status": "atrasado", "emoji": "🚨", "cor": CORES_DECISAO["critico"], "texto": "Atrasado"}


def obter_decisao_release(health_score: float, dias_restantes: int, pct_conclusao: float, bugs: int) -> dict:
    """
    Determina a decisão de release baseada em múltiplos fatores.
    
    Retorna: {
        "decisao": "GO" | "ATENÇÃO" | "RISCO" | "NO-GO",
        "cor": cor_hex,
        "gradiente": gradiente_css,
        "emoji": emoji,
        "motivo": texto_explicativo,
        "problemas": lista_de_problemas,
        "acao": acao_recomendada
    }
    """
    problemas = []
    pontos_risco = 0
    
    # Avalia Health Score
    if health_score < METAS_SPRINT["health_score"]["risco"]:
        problemas.append(f"Health Score crítico: {health_score:.0f}/100")
        pontos_risco += 3
    elif health_score < METAS_SPRINT["health_score"]["atencao"]:
        problemas.append(f"Health Score baixo: {health_score:.0f}/100")
        pontos_risco += 2
    elif health_score < METAS_SPRINT["health_score"]["go"]:
        problemas.append(f"Health Score moderado: {health_score:.0f}/100")
        pontos_risco += 1
    
    # Avalia Dias Restantes
    if dias_restantes is not None and dias_restantes <= 0:
        problemas.append(f"Release atrasada em {abs(dias_restantes)} dia(s)")
        pontos_risco += 3
    elif dias_restantes is not None and dias_restantes <= METAS_SPRINT["dias_restantes"]["critico"]:
        problemas.append(f"Apenas {dias_restantes} dia(s) restante(s)")
        pontos_risco += 2
    elif dias_restantes is not None and dias_restantes <= METAS_SPRINT["dias_restantes"]["alerta"]:
        problemas.append(f"{dias_restantes} dias restantes - atenção ao prazo")
        pontos_risco += 1
    
    # Avalia % Conclusão
    if pct_conclusao < METAS_SPRINT["pct_conclusao"]["critico"]:
        problemas.append(f"Apenas {pct_conclusao:.0f}% concluído - muito abaixo da meta")
        pontos_risco += 2
    elif pct_conclusao < METAS_SPRINT["pct_conclusao"]["alerta"]:
        problemas.append(f"{pct_conclusao:.0f}% concluído - abaixo da meta de {METAS_SPRINT['pct_conclusao']['meta']}%")
        pontos_risco += 1
    
    # Avalia Bugs
    if bugs > METAS_SPRINT["bugs_max"]["alerta"]:
        problemas.append(f"{bugs} bugs encontrados - acima do tolerável")
        pontos_risco += 2
    elif bugs > METAS_SPRINT["bugs_max"]["saudavel"]:
        problemas.append(f"{bugs} bugs - monitorar resolução")
        pontos_risco += 1
    
    # Decisão final
    if pontos_risco == 0:
        return {
            "decisao": "GO",
            "cor": CORES_DECISAO["saudavel"],
            "gradiente": GRADIENTES_DECISAO["go"],
            "emoji": "✅",
            "motivo": "Todos os indicadores estão dentro do esperado",
            "problemas": [],
            "acao": "Manter acompanhamento regular"
        }
    elif pontos_risco <= 2:
        return {
            "decisao": "ATENÇÃO",
            "cor": CORES_DECISAO["atencao"],
            "gradiente": GRADIENTES_DECISAO["atencao"],
            "emoji": "⚠️",
            "motivo": "Alguns indicadores precisam de monitoramento",
            "problemas": problemas,
            "acao": "Revisar itens sinalizados e acompanhar evolução"
        }
    elif pontos_risco <= 5:
        return {
            "decisao": "RISCO",
            "cor": CORES_DECISAO["alerta"],
            "gradiente": GRADIENTES_DECISAO["risco"],
            "emoji": "🚨",
            "motivo": "Existem riscos significativos para a release",
            "problemas": problemas,
            "acao": "Convocar reunião de alinhamento e priorizar resolução"
        }
    else:
        return {
            "decisao": "NO-GO",
            "cor": CORES_DECISAO["critico"],
            "gradiente": GRADIENTES_DECISAO["nogo"],
            "emoji": "🛑",
            "motivo": "A release não deve prosseguir sem intervenção",
            "problemas": problemas,
            "acao": "URGENTE: Escalar para liderança e definir plano de ação"
        }


def criar_card_acionavel(
    valor: str, 
    titulo: str, 
    meta: str = None, 
    status: str = "neutro",  # saudavel, atencao, alerta, critico
    subtitulo: str = "",
    tendencia: str = None,  # up, down, stable
    tooltip: str = None
):
    """
    Cria card de métrica acionável com comparação de meta.
    """
    cor = CORES_DECISAO.get(status, CORES_DECISAO["neutro"])
    
    # Ícone de tendência
    tendencia_html = ""
    if tendencia == "up":
        tendencia_html = f'<span style="color: {CORES_DECISAO["saudavel"]}; font-size: 14px;">↑</span>'
    elif tendencia == "down":
        tendencia_html = f'<span style="color: {CORES_DECISAO["critico"]}; font-size: 14px;">↓</span>'
    elif tendencia == "stable":
        tendencia_html = f'<span style="color: {CORES_DECISAO["neutro"]}; font-size: 14px;">→</span>'
    
    # Meta HTML
    meta_html = ""
    if meta:
        meta_html = f'<div style="font-size: 11px; color: #9ca3af; margin-top: 4px;">{meta}</div>'
    
    # Subtítulo HTML
    subtitulo_html = ""
    if subtitulo:
        subtitulo_html = f'<div style="font-size: 12px; color: #6b7280;">{subtitulo}</div>'
    
    tooltip_attr = f'title="{tooltip}"' if tooltip else ''
    
    # Altura mínima fixa para uniformidade dos cards
    html = f'<div style="background: white; border: 2px solid {cor}; border-radius: 12px; padding: 16px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05); min-height: 120px; display: flex; flex-direction: column; justify-content: center;" {tooltip_attr}><div style="font-size: 28px; font-weight: 700; color: {cor};">{valor} {tendencia_html}</div><div style="font-size: 13px; font-weight: 600; color: #374151; margin-top: 4px;">{titulo}</div>{subtitulo_html}{meta_html}</div>'
    st.markdown(html, unsafe_allow_html=True)


def identificar_gargalos(df: pd.DataFrame) -> list:
    """
    Identifica gargalos e riscos operacionais na sprint.
    
    Retorna lista de dicts com:
    - tipo: categoria do problema
    - severidade: critico, alerta, atencao
    - titulo: descrição curta
    - cards: lista de cards afetados
    - acao: ação recomendada
    """
    gargalos = []
    hoje = datetime.now()
    
    # 1. Cards em Code Review há muito tempo (>48h)
    if 'status_cat' in df.columns and 'atualizado' in df.columns:
        em_cr = df[df['status_cat'] == 'code_review'].copy()
        if not em_cr.empty:
            # Verifica tempo em CR
            cards_cr_antigos = []
            for _, row in em_cr.iterrows():
                if pd.notna(row.get('atualizado')):
                    try:
                        atualizado = row['atualizado']
                        if isinstance(atualizado, str):
                            atualizado = datetime.fromisoformat(atualizado.replace('Z', '+00:00'))
                        dias_em_cr = (hoje - atualizado.replace(tzinfo=None)).days if hasattr(atualizado, 'replace') else 0
                        if dias_em_cr >= 2:
                            cards_cr_antigos.append({
                                'ticket_id': row['ticket_id'],
                                'titulo': str(row.get('titulo', ''))[:50],
                                'dias': dias_em_cr
                            })
                    except:
                        pass
            
            if cards_cr_antigos:
                gargalos.append({
                    "tipo": "code_review",
                    "severidade": "alerta" if len(cards_cr_antigos) <= 3 else "critico",
                    "titulo": f"📝 {len(cards_cr_antigos)} cards parados em Code Review",
                    "cards": cards_cr_antigos,
                    "acao": "Priorizar revisão de código com os desenvolvedores"
                })
    
    # 2. Cards bloqueados/impedidos
    bloqueados = df[df['status_cat'].isin(['blocked', 'rejected'])]
    if not bloqueados.empty:
        cards_bloqueados = [
            {'ticket_id': row['ticket_id'], 'titulo': str(row.get('titulo', ''))[:50], 'status': row['status']}
            for _, row in bloqueados.iterrows()
        ]
        gargalos.append({
            "tipo": "bloqueio",
            "severidade": "critico",
            "titulo": f"🚫 {len(bloqueados)} cards bloqueados/reprovados",
            "cards": cards_bloqueados,
            "acao": "Resolver impedimentos imediatamente"
        })
    
    # 3. Fila de QA muito grande
    em_fila_qa = df[df['status_cat'] == 'waiting_qa']
    if len(em_fila_qa) > 10:
        gargalos.append({
            "tipo": "fila_qa",
            "severidade": "alerta" if len(em_fila_qa) <= 15 else "critico",
            "titulo": f"⏳ {len(em_fila_qa)} cards aguardando validação",
            "cards": [{'ticket_id': row['ticket_id'], 'titulo': str(row.get('titulo', ''))[:50]} for _, row in em_fila_qa.head(5).iterrows()],
            "acao": "Aumentar capacidade de QA ou redistribuir carga"
        })
    
    # 4. Cards com muitos bugs
    cards_com_bugs = df[df['bugs'] >= 3]
    if not cards_com_bugs.empty:
        cards_problematicos = [
            {'ticket_id': row['ticket_id'], 'titulo': str(row.get('titulo', ''))[:50], 'bugs': row['bugs']}
            for _, row in cards_com_bugs.iterrows()
        ]
        gargalos.append({
            "tipo": "qualidade",
            "severidade": "alerta",
            "titulo": f"🐛 {len(cards_com_bugs)} cards com 3+ bugs",
            "cards": cards_problematicos,
            "acao": "Analisar padrão de bugs e revisar código"
        })
    
    # 5. Story Points não preenchidos
    gov = calcular_metricas_governanca(df)
    if gov['sp']['pct'] < 50:
        gargalos.append({
            "tipo": "governanca",
            "severidade": "atencao",
            "titulo": f"📊 Apenas {gov['sp']['pct']:.0f}% dos cards têm Story Points",
            "cards": [],
            "acao": "Solicitar preenchimento de SP para métricas confiáveis"
        })
    
    # Ordena por severidade
    ordem_severidade = {"critico": 0, "alerta": 1, "atencao": 2}
    gargalos.sort(key=lambda x: ordem_severidade.get(x["severidade"], 3))
    
    return gargalos


# ==============================================================================
# COMPONENTES DE UI - VERSÃO GRID COMPACTO (UX v5)
# ==============================================================================

def renderizar_decisao_inline(decisao: dict, health_score: float, pct_conclusao: float, pct_esperado: float, dias_restantes: int):
    """
    Renderiza decisão em card horizontal com 4 áreas principais.
    Layout: [ STATUS | DIAGNÓSTICO | AÇÃO | RESUMO ]
    
    Design baseado em UX profissional:
    - Fundo limpo (branco/cinza claro)
    - Vermelho usado com moderação (apenas status, ícones críticos, botão primário)
    - Hierarquia visual clara
    - Escaneável em 3 segundos
    """
    tipo_decisao = decisao['decisao']
    cor_status = decisao['cor']
    
    # Cálculos
    atraso = pct_conclusao - pct_esperado
    dias_val = dias_restantes if dias_restantes is not None else 0
    
    # Cores semânticas por tipo de decisão
    cores_map = {
        'NO-GO': {'bg': '#FEF2F2', 'border': '#FECACA', 'primary': '#EF4444', 'text': '#DC2626'},
        'RISCO': {'bg': '#FFF7ED', 'border': '#FFEDD5', 'primary': '#F97316', 'text': '#EA580C'},
        'ATENÇÃO': {'bg': '#FFFBEB', 'border': '#FEF3C7', 'primary': '#F59E0B', 'text': '#D97706'},
        'GO': {'bg': '#F0FDF4', 'border': '#BBF7D0', 'primary': '#22C55E', 'text': '#16A34A'},
    }
    cores = cores_map.get(tipo_decisao, cores_map['GO'])
    
    # Textos dinâmicos baseados na decisão
    textos = {
        'NO-GO': {
            'subtitulo': 'Release bloqueada',
            'motivo': 'A release não deve prosseguir sem intervenção.',
            'impacto': 'Risco alto de bugs em produção e retrabalho significativo.',
            'acao': 'Escalar para liderança imediatamente',
            'acao2': 'Convocar reunião de crise com o time',
            'acao3': 'Definir plano de ação e responsáveis',
            'icone': '✕',
        },
        'RISCO': {
            'subtitulo': 'Riscos identificados',
            'motivo': 'Indicadores abaixo do esperado.',
            'impacto': 'Possível atraso na entrega ou bugs em produção.',
            'acao': 'Convocar reunião de alinhamento urgente',
            'acao2': 'Priorizar resolução dos bloqueios',
            'acao3': 'Revisar escopo se necessário',
            'icone': '⚠',
        },
        'ATENÇÃO': {
            'subtitulo': 'Monitoramento ativo',
            'motivo': 'Métricas próximas aos limites.',
            'impacto': 'Monitorar diariamente para evitar escalonamento.',
            'acao': 'Revisar itens sinalizados',
            'acao2': 'Acompanhar evolução diária',
            'acao3': 'Preparar plano de contingência',
            'icone': '!',
        },
        'GO': {
            'subtitulo': 'Release autorizada',
            'motivo': 'Sprint sob controle.',
            'impacto': 'Baixo risco de problemas em produção.',
            'acao': 'Prosseguir com a release',
            'acao2': 'Comunicar stakeholders',
            'acao3': 'Preparar rollback se necessário',
            'icone': '✓',
        },
    }
    txt = textos.get(tipo_decisao, textos['GO'])
    
    # Cores para métricas
    health_cor = "#EF4444" if health_score < 50 else "#F59E0B" if health_score < 75 else "#22C55E"
    prog_cor = "#EF4444" if pct_conclusao < 40 else "#F59E0B" if pct_conclusao < 70 else "#22C55E"
    atraso_cor = "#EF4444" if atraso < -10 else "#F59E0B" if atraso < 0 else "#22C55E"
    
    # Variação do Health Score
    health_var = f"-{100 - int(health_score)}%" if health_score < 80 else f"+{int(health_score) - 70}%"
    health_var_cor = "#EF4444" if health_score < 70 else "#22C55E"
    
    # Card de decisão harmonizado - layout 4 colunas com títulos alinhados
    html = f'''<div style="background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
<div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 16px;">

<div>
<div style="font-size: 11px; font-weight: 600; color: #6B7280; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; height: 16px;">🚦 Decisão</div>
<div style="background: white; border: 2px solid {cores['primary']}40; border-radius: 8px; padding: 16px; text-align: center;">
<div style="background: {cores['primary']}; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 8px;">
<span style="color: white; font-size: 18px; font-weight: bold;">{txt['icone']}</span>
</div>
<div style="font-size: 20px; font-weight: 800; color: {cores['text']};">{tipo_decisao}</div>
<div style="font-size: 11px; color: #6B7280; margin-top: 4px;">{txt['subtitulo']}</div>
</div>
</div>

<div>
<div style="font-size: 13px; font-weight: 600; color: #6B7280; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; height: 16px;">Diagnóstico</div>
<div style="display: flex; flex-direction: column; gap: 6px;">
<div style="background: white; border: 1px solid #E5E7EB; border-radius: 8px; padding: 10px;">
<div style="display: flex; align-items: flex-start; gap: 8px;">
<span style="color: {cores['primary']}; font-size: 14px;">⚠️</span>
<div>
<div style="font-size: 12px; color: #9CA3AF; text-transform: uppercase;">Motivo principal</div>
<div style="font-size: 13px; color: #374151; line-height: 1.4;">{txt['motivo']}</div>
</div>
</div>
</div>
<div style="background: white; border: 1px solid #E5E7EB; border-radius: 8px; padding: 10px;">
<div style="display: flex; align-items: flex-start; gap: 8px;">
<span style="color: #F59E0B; font-size: 14px;">ℹ️</span>
<div>
<div style="font-size: 12px; color: #9CA3AF; text-transform: uppercase;">Impacto</div>
<div style="font-size: 13px; color: #374151; line-height: 1.4;">{txt['impacto']}</div>
</div>
</div>
</div>
</div>
</div>

<div>
<div style="font-size: 13px; font-weight: 600; color: #6B7280; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; height: 16px;">Ações Recomendadas</div>
<div style="display: flex; flex-direction: column; gap: 6px;">
<div style="background: {cores['bg']}; border: 1px solid {cores['border']}; border-radius: 8px; padding: 10px;">
<div style="display: flex; align-items: flex-start; gap: 8px;">
<span style="font-size: 14px;">💡</span>
<div style="font-size: 13px; color: #374151; line-height: 1.4;">{txt['acao']}</div>
</div>
</div>
<div style="background: {cores['bg']}; border: 1px solid {cores['border']}; border-radius: 8px; padding: 10px;">
<div style="display: flex; align-items: flex-start; gap: 8px;">
<span style="font-size: 14px;">📋</span>
<div style="font-size: 13px; color: #374151; line-height: 1.4;">{txt['acao2']}</div>
</div>
</div>
<div style="background: {cores['bg']}; border: 1px solid {cores['border']}; border-radius: 8px; padding: 10px;">
<div style="display: flex; align-items: flex-start; gap: 8px;">
<span style="font-size: 14px;">👥</span>
<div style="font-size: 13px; color: #374151; line-height: 1.4;">{txt['acao3']}</div>
</div>
</div>
</div>
</div>

<div>
<div style="font-size: 13px; font-weight: 600; color: #6B7280; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; height: 16px;">Cenário</div>
<div style="display: flex; gap: 6px;">
<div style="background: white; border: 1px solid #E5E7EB; border-radius: 8px; padding: 12px 10px; text-align: center; flex: 1; display: flex; flex-direction: column; justify-content: center;">
<span style="font-size: 18px; color: {health_cor};">❤️</span>
<div style="font-size: 11px; color: #9CA3AF; margin-top: 4px;">Health</div>
<div style="font-size: 24px; font-weight: 700; color: {health_cor}; margin-top: 2px;">{health_score:.0f}</div>
<div style="font-size: 12px; color: {health_var_cor}; font-weight: 500; margin-top: 2px;">{health_var}</div>
</div>
<div style="display: flex; flex-direction: column; gap: 6px; flex: 1;">
<div style="background: white; border: 1px solid #E5E7EB; border-radius: 8px; padding: 10px 8px; text-align: center; flex: 1; display: flex; flex-direction: column; justify-content: center;">
<span style="font-size: 14px; color: {prog_cor};">📊</span>
<div style="font-size: 10px; color: #9CA3AF; margin-top: 2px;">Progresso</div>
<div style="font-size: 15px; font-weight: 700; color: #374151;">{pct_conclusao:.0f}%</div>
</div>
<div style="background: white; border: 1px solid #E5E7EB; border-radius: 8px; padding: 10px 8px; text-align: center; flex: 1; display: flex; flex-direction: column; justify-content: center;">
<span style="font-size: 14px; color: {atraso_cor};">⏱️</span>
<div style="font-size: 10px; color: #9CA3AF; margin-top: 2px;">{"Atraso" if dias_val < 0 else "Restante"}</div>
<div style="font-size: 15px; font-weight: 700; color: {atraso_cor};">{abs(dias_val) if dias_val < 0 else dias_val}d</div>
</div>
</div>
</div>
</div>

</div>
</div>'''
    st.markdown(html, unsafe_allow_html=True)


def renderizar_grid_principal(gargalos: list, pct_conclusao: float, pct_esperado: float, bugs_total: int, concluidos: int, em_andamento: int, total: int, dias_passados: int, dias_total: int):
    """
    Renderiza grid de 3 colunas: [ Problemas | Ações | Progresso ]
    Layout limpo e escaneável.
    """
    col1, col2, col3 = st.columns(3)
    
    # ========== COLUNA 1: PROBLEMAS ==========
    with col1:
        st.markdown('<div style="font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 8px;">🔥 Problemas</div>', unsafe_allow_html=True)
        
        problemas = []
        for g in gargalos[:4]:
            sev = g["severidade"]
            badge = "CRÍTICO" if sev == "critico" else "ALERTA" if sev == "alerta" else "ATENÇÃO"
            badge_cor = "#dc2626" if sev == "critico" else "#ea580c" if sev == "alerta" else "#d97706"
            titulo = g["titulo"].replace("📝 ", "").replace("🚫 ", "").replace("⏳ ", "").replace("🐛 ", "").replace("📊 ", "")[:40]
            problemas.append((titulo, badge, badge_cor, sev))
        
        if pct_conclusao < 60:
            sev = "critico" if pct_conclusao < 40 else "alerta"
            badge = "CRÍTICO" if pct_conclusao < 40 else "ALERTA"
            badge_cor = "#dc2626" if pct_conclusao < 40 else "#ea580c"
            problemas.insert(0, (f"Apenas {pct_conclusao:.0f}% concluído", badge, badge_cor, sev))
        
        if not problemas:
            st.markdown('<div style="background: #f0fdf4; border-radius: 8px; padding: 16px; text-align: center;"><span style="font-size: 18px;">✅</span><div style="font-size: 12px; color: #166534; margin-top: 4px;">Sem problemas</div></div>', unsafe_allow_html=True)
        else:
            for titulo, badge, badge_cor, sev in problemas[:4]:
                borda_peso = "3px" if sev == "critico" else "2px"
                html = f'<div style="background: white; border-left: {borda_peso} solid {badge_cor}; padding: 6px 10px; margin-bottom: 4px; border-radius: 0 6px 6px 0; display: flex; justify-content: space-between; align-items: center; gap: 8px;"><span style="font-size: 13px; color: #374151; flex: 1; line-height: 1.3;">{titulo}</span><span style="background: {badge_cor}12; color: {badge_cor}; padding: 2px 5px; border-radius: 4px; font-size: 10px; font-weight: 700; white-space: nowrap;">{badge}</span></div>'
                st.markdown(html, unsafe_allow_html=True)
    
    # ========== COLUNA 2: AÇÕES ==========
    with col2:
        st.markdown('<div style="font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 8px;">📌 Ações Prioritárias</div>', unsafe_allow_html=True)
        
        acoes = []
        for g in gargalos:
            if g["severidade"] == "critico":
                if "bloqueado" in g["titulo"].lower():
                    acoes.append(("Resolver bloqueados", "Tech Lead"))
                elif "review" in g["titulo"].lower():
                    acoes.append(("Priorizar code review", "Devs"))
                elif "aguardando" in g["titulo"].lower():
                    acoes.append(("Acelerar validação QA", "QA Lead"))
        
        if bugs_total > 15:
            acoes.append(("Reduzir bugs críticos", "Dev + QA"))
        if pct_conclusao < 40:
            acoes.append(("Revisar escopo sprint", "PO"))
        
        for g in gargalos:
            if "story points" in g["titulo"].lower():
                acoes.append(("Atualizar Story Points", "Tech Lead"))
                break
        
        # Remove duplicatas
        acoes_unicas = []
        vistas = set()
        for a, r in acoes:
            if a not in vistas:
                acoes_unicas.append((a, r))
                vistas.add(a)
        
        if not acoes_unicas:
            st.markdown('<div style="background: #f0fdf4; border-radius: 8px; padding: 16px; text-align: center;"><span style="font-size: 18px;">✅</span><div style="font-size: 12px; color: #166534; margin-top: 4px;">Nenhuma ação urgente</div></div>', unsafe_allow_html=True)
        else:
            for i, (acao, resp) in enumerate(acoes_unicas[:4], 1):
                cor_num = "#dc2626" if i == 1 else "#ea580c" if i == 2 else "#6b7280"
                html = f'<div style="background: white; border: 1px solid #f3f4f6; padding: 6px 10px; margin-bottom: 4px; border-radius: 6px; display: flex; align-items: center; gap: 8px;"><span style="background: {cor_num}; color: white; min-width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700;">{i}</span><div style="flex: 1;"><div style="font-size: 13px; font-weight: 500; color: #374151;">{acao}</div><div style="font-size: 11px; color: #9ca3af;">{resp}</div></div></div>'
                st.markdown(html, unsafe_allow_html=True)
    
    # ========== COLUNA 3: PROGRESSO ==========
    with col3:
        st.markdown('<div style="font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 8px;">📊 Progresso</div>', unsafe_allow_html=True)
        
        atraso = pct_conclusao - pct_esperado
        if atraso >= 0:
            atraso_cor = "#22c55e"
            impacto = "No ritmo"
            impacto_icon = "✅"
        elif atraso >= -15:
            atraso_cor = "#f59e0b"
            impacto = "Leve atraso"
            impacto_icon = "⚠️"
        else:
            atraso_cor = "#ef4444"
            impacto = "Risco de não entrega"
            impacto_icon = "🚨"
        
        tempo_info = f"Dia {dias_passados}/{dias_total}" if dias_passados is not None and dias_total else ""
        
        html_progresso = f'''<div style="background: white; border: 1px solid #f3f4f6; border-radius: 8px; padding: 12px;">
<div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
<span style="font-size: 28px; font-weight: 700; color: #1f2937;">{pct_conclusao:.0f}%</span>
<span style="font-size: 12px; color: #9ca3af;">{tempo_info}</span>
</div>
<div style="background: #e5e7eb; border-radius: 4px; height: 8px; margin-bottom: 8px; position: relative;">
<div style="background: linear-gradient(90deg, #22c55e, #16a34a); width: {min(100, pct_conclusao)}%; height: 100%; border-radius: 4px;"></div>
<div style="position: absolute; left: {min(100, max(0, pct_esperado))}%; top: -2px; bottom: -2px; width: 2px; background: #374151;"></div>
</div>
<div style="display: flex; justify-content: space-between; font-size: 12px; color: #6b7280; margin-bottom: 8px;">
<span>✅ {concluidos}</span><span>🔄 {em_andamento}</span><span>📋 {total}</span>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; padding-top: 8px; border-top: 1px solid #f3f4f6;">
<span style="font-size: 12px; color: #6b7280;">Meta: {pct_esperado:.0f}%</span>
<span style="font-size: 13px; font-weight: 600; color: {atraso_cor};">{"+" if atraso >= 0 else ""}{atraso:.0f}%</span>
</div>
<div style="font-size: 12px; color: {atraso_cor}; margin-top: 6px; text-align: center; font-weight: 500;">{impacto_icon} {impacto}</div>
</div>'''
        st.markdown(html_progresso, unsafe_allow_html=True)


def renderizar_indicadores_compactos(df: pd.DataFrame, total: int, concluidos: int, pct_conclusao: float, sp_total: int, bugs_total: int, dias_restantes: int, pct_esperado: float):
    """
    Renderiza indicadores em linha compacta (altura reduzida).
    """
    
    sp_concluido = int(df[df['status_cat'] == 'done']['sp'].sum()) if 'status_cat' in df.columns else 0
    pct_sp = (sp_concluido / sp_total * 100) if sp_total > 0 else 0
    
    # Status colors
    cor_conclusao = "#22c55e" if pct_conclusao >= 80 else "#f59e0b" if pct_conclusao >= 60 else "#ef4444"
    cor_bugs = "#22c55e" if bugs_total <= 10 else "#f59e0b" if bugs_total <= 20 else "#ef4444"
    cor_dias = "#22c55e" if dias_restantes and dias_restantes > 5 else "#f59e0b" if dias_restantes and dias_restantes > 2 else "#ef4444"
    tendencia = "↑" if pct_conclusao > pct_esperado else "↓" if pct_conclusao < pct_esperado - 10 else "→"
    tendencia_cor = "#22c55e" if pct_conclusao > pct_esperado else "#ef4444" if pct_conclusao < pct_esperado - 10 else "#6b7280"
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    def mini_card(valor, titulo, subtitulo, cor="#6b7280"):
        return f'<div style="background: white; border: 1px solid {cor}40; border-radius: 8px; padding: 12px 8px; text-align: center; height: 80px; display: flex; flex-direction: column; justify-content: center;"><div style="font-size: 22px; font-weight: 700; color: {cor};">{valor}</div><div style="font-size: 13px; font-weight: 600; color: #374151;">{titulo}</div><div style="font-size: 12px; color: #9ca3af;">{subtitulo}</div></div>'
    
    with col1:
        st.markdown(mini_card(str(total), "Cards", f"{concluidos} ok"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(mini_card(str(sp_total), "Story Points", f"{sp_concluido} ({pct_sp:.0f}%)", "#3b82f6"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(mini_card(f"{pct_conclusao:.0f}%", "Concluído", f"{tendencia} Meta: 80%", cor_conclusao), unsafe_allow_html=True)
    
    with col4:
        st.markdown(mini_card(str(bugs_total), "Bugs", f"Limite: 10", cor_bugs), unsafe_allow_html=True)
    
    with col5:
        dias_val = str(dias_restantes) if dias_restantes is not None else "—"
        st.markdown(mini_card(dias_val, "Dias", "restantes", cor_dias if dias_restantes else "#6b7280"), unsafe_allow_html=True)


# ==============================================================================
# ABA PRINCIPAL
# ==============================================================================

def aba_visao_geral_v2(df: pd.DataFrame, ultima_atualizacao: datetime):
    """
    Aba de Visão Geral V2 - Orientada a Decisão.
    
    Hierarquia:
    1. Bloco de Decisão (GO/NO-GO)
    2. Progresso da Sprint (Esperado vs Atual)
    3. Cards Acionáveis
    4. Riscos e Gargalos
    5. Métricas Técnicas (colapsado)
    6. Detalhes (colapsado)
    """
    
    # ==== CONTEXTO DE PERÍODO ====
    ctx = obter_contexto_periodo()
    
    # ==== HEADER COMPACTO ====
    agora = datetime.now()
    diff = (agora - ultima_atualizacao).total_seconds() / 60
    tempo_texto = "agora" if diff < 1 else f"há {int(diff)}min" if diff < 60 else f"há {int(diff/60)}h"
    
    # Header com botão de atualização integrado
    col_titulo, col_periodo, col_refresh = st.columns([2, 2, 1])
    with col_titulo:
        st.markdown('<div style="font-size: 18px; font-weight: 700; color: #1f2937; padding-top: 4px;">🎯 Central de Decisão</div>', unsafe_allow_html=True)
    with col_periodo:
        # Badge mostrando o período selecionado
        cor_badge = "#3b82f6" if ctx["eh_sprint"] else "#6b7280" if ctx["eh_todo_periodo"] else "#f59e0b"
        st.markdown(f'''
        <div style="display: flex; align-items: center; justify-content: center; padding-top: 4px;">
            <span style="background: {cor_badge}15; color: {cor_badge}; padding: 4px 12px; border-radius: 12px; font-size: 13px; font-weight: 500; border: 1px solid {cor_badge}40;">
                {ctx["emoji"]} {ctx["titulo"]}
            </span>
        </div>
        ''', unsafe_allow_html=True)
    with col_refresh:
        if st.button(f"🔄 Atualizar", help=f"Última atualização: {tempo_texto}", type="secondary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # ==== COLETA DE DADOS ====
    
    # Sprint info
    sprint_atual = "Sem Sprint"
    sprint_end = None
    sprint_start = None
    
    try:
        if 'sprint_state' in df.columns:
            df_sprint_ativa = df[df['sprint_state'] == 'active']
            if not df_sprint_ativa.empty:
                sprint_atual = df_sprint_ativa['sprint'].iloc[0] if pd.notna(df_sprint_ativa['sprint'].iloc[0]) else "Sem Sprint"
                if 'sprint_end' in df_sprint_ativa.columns:
                    se = df_sprint_ativa['sprint_end'].dropna()
                    sprint_end = se.iloc[0] if not se.empty else None
                if 'sprint_start' in df_sprint_ativa.columns:
                    ss = df_sprint_ativa['sprint_start'].dropna()
                    sprint_start = ss.iloc[0] if not ss.empty else None
            else:
                if not df.empty and 'sprint' in df.columns:
                    mode_result = df['sprint'].mode()
                    sprint_atual = mode_result.iloc[0] if not mode_result.empty else "Sem Sprint"
                if 'sprint_end' in df.columns:
                    se = df['sprint_end'].dropna()
                    sprint_end = se.iloc[0] if not se.empty else None
                if 'sprint_start' in df.columns:
                    ss = df['sprint_start'].dropna()
                    sprint_start = ss.iloc[0] if not ss.empty else None
        else:
            if not df.empty and 'sprint' in df.columns:
                mode_result = df['sprint'].mode()
                sprint_atual = mode_result.iloc[0] if not mode_result.empty else "Sem Sprint"
            if 'sprint_end' in df.columns:
                se = df['sprint_end'].dropna()
                sprint_end = se.iloc[0] if not se.empty else None
    except Exception:
        sprint_atual = "Sem Sprint"
        sprint_end = None
        sprint_start = None
    
    hoje = datetime.now()
    dias_restantes = None
    dias_passados = None
    dias_total = None
    
    try:
        if sprint_end is not None:
            # Garante que sprint_end é datetime
            if isinstance(sprint_end, str):
                sprint_end = datetime.fromisoformat(sprint_end.replace('Z', '+00:00')).replace(tzinfo=None)
            elif hasattr(sprint_end, 'replace'):
                sprint_end = sprint_end.replace(tzinfo=None) if hasattr(sprint_end, 'tzinfo') and sprint_end.tzinfo else sprint_end
            
            dias_restantes = (sprint_end - hoje).days
            
            if sprint_start is not None:
                if isinstance(sprint_start, str):
                    sprint_start = datetime.fromisoformat(sprint_start.replace('Z', '+00:00')).replace(tzinfo=None)
                elif hasattr(sprint_start, 'replace'):
                    sprint_start = sprint_start.replace(tzinfo=None) if hasattr(sprint_start, 'tzinfo') and sprint_start.tzinfo else sprint_start
                
                dias_total = (sprint_end - sprint_start).days
                dias_passados = (hoje - sprint_start).days
    except Exception:
        dias_restantes = None
        dias_passados = None
        dias_total = None
    
    # Métricas básicas
    total = len(df)
    concluidos = len(df[df['status_cat'] == 'done'])
    pct_conclusao = (concluidos / total * 100) if total > 0 else 0
    
    em_dev = len(df[df['status_cat'] == 'development'])
    em_review = len(df[df['status_cat'] == 'code_review'])
    em_fila_qa = len(df[df['status_cat'] == 'waiting_qa'])
    em_teste = len(df[df['status_cat'] == 'testing'])
    em_andamento = em_dev + em_review + em_fila_qa + em_teste
    
    sp_total = int(df['sp'].sum())
    bugs_total = int(df['bugs'].sum())
    
    # Health Score
    health = calcular_health_score(df)
    
    # Progresso esperado
    pct_esperado = 0
    if dias_total and dias_total > 0 and dias_passados is not None:
        pct_esperado = calcular_progresso_esperado(dias_passados, dias_total)
    
    # Decisão de Release
    decisao = obter_decisao_release(health['score'], dias_restantes, pct_conclusao, bugs_total)
    
    # Gargalos
    gargalos = identificar_gargalos(df)
    
    # ==== BANNER DO PERÍODO - ADAPTATIVO ====
    badge_status = ""
    badge_cor = "#6b7280"
    info_tempo = ""
    
    # Quando é Sprint Ativa, mostra informações de tempo
    if ctx["eh_sprint"] and dias_restantes is not None:
        if dias_restantes < 0:
            badge_cor = "#dc2626"
            badge_status = f'<span style="background: {badge_cor}; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; margin-left: 8px;">ATRASADA {abs(dias_restantes)}d</span>'
            info_tempo = f'<span style="color: #dc2626; font-weight: 600;">+{abs(dias_restantes)} dias além do prazo</span>'
        elif dias_restantes == 0:
            badge_cor = "#f59e0b"
            badge_status = f'<span style="background: {badge_cor}; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; margin-left: 8px;">HOJE</span>'
            info_tempo = '<span style="color: #f59e0b; font-weight: 600;">Último dia!</span>'
        elif dias_restantes <= 2:
            badge_cor = "#ea580c"
            badge_status = f'<span style="background: {badge_cor}; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; margin-left: 8px;">{dias_restantes}d</span>'
            info_tempo = f'<span style="color: #ea580c;">Faltam {dias_restantes} dias</span>'
        else:
            badge_status = f'<span style="background: #e5e7eb; color: #374151; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 500; margin-left: 8px;">{dias_restantes}d restantes</span>'
            if dias_passados is not None and dias_total:
                info_tempo = f'<span style="color: #6b7280;">Dia {dias_passados} de {dias_total}</span>'
            else:
                info_tempo = f'<span style="color: #6b7280;">{dias_restantes} dias restantes</span>'
        titulo_banner = f"🚀 {sprint_atual}"
    elif ctx["eh_sprint"]:
        # Sprint ativa mas sem datas definidas
        info_tempo = '<span style="color: #9ca3af;">Datas não definidas</span>'
        titulo_banner = f"🚀 {sprint_atual}"
    elif ctx["eh_todo_periodo"]:
        # Todo o período - mostra total de cards
        info_tempo = f'<span style="color: #6b7280;">{total} cards no total</span>'
        titulo_banner = f"📆 {ctx['titulo']}"
    else:
        # Últimos 30/90 dias
        info_tempo = f'<span style="color: #6b7280;">{total} cards criados</span>'
        titulo_banner = f"{ctx['emoji']} {ctx['titulo']}"
    
    banner_html = f'<div style="background: #f9fafb; border: 1px solid #e5e7eb; padding: 8px 14px; border-radius: 8px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;"><div style="display: flex; align-items: center;"><span style="font-size: 13px; font-weight: 600; color: #374151;">{titulo_banner}</span>{badge_status}</div><span style="font-size: 12px;">{info_tempo}</span></div>'
    st.markdown(banner_html, unsafe_allow_html=True)
    
    # Governança para verificações
    gov = calcular_metricas_governanca(df)
    
    # ==== 1. BLOCO DE DECISÃO - INLINE ULTRA-COMPACTO ====
    renderizar_decisao_inline(decisao, health['score'], pct_conclusao, pct_esperado, dias_restantes)
    
    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)
    
    # ==== 2. GRID PRINCIPAL: [ Problemas | Ações | Progresso ] ====
    renderizar_grid_principal(
        gargalos=gargalos,
        pct_conclusao=pct_conclusao,
        pct_esperado=pct_esperado,
        bugs_total=bugs_total,
        concluidos=concluidos,
        em_andamento=em_andamento,
        total=total,
        dias_passados=dias_passados,
        dias_total=dias_total
    )
    
    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)
    
    # ==== 3. INDICADORES COMPACTOS ====
    st.markdown("##### 📈 Indicadores")
    renderizar_indicadores_compactos(df, total, concluidos, pct_conclusao, sp_total, bugs_total, dias_restantes, pct_esperado)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==== 4. MÉTRICAS TÉCNICAS ====
    with st.expander("🔬 Métricas Técnicas", expanded=False):
        # Explicação das métricas
        st.markdown("""
        <div style="background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; padding: 12px 16px; margin-bottom: 16px;">
            <div style="font-size: 13px; font-weight: 600; color: #0369a1; margin-bottom: 8px;">📚 O que cada métrica significa:</div>
            <div style="font-size: 12px; color: #334155; line-height: 1.8;">
                <b>FPY (First Pass Yield)</b> — % de cards aprovados na primeira tentativa de QA. Quanto maior, menos retrabalho.<br>
                <b>DDP (Defect Detection Percentage)</b> — % de bugs encontrados pelo QA antes de ir para produção. Quanto maior, melhor a cobertura.<br>
                <b>Lead Time</b> — Tempo médio (dias) desde criação até conclusão de um card. Quanto menor, mais ágil.<br>
                <b>Health Score</b> — Nota geral de saúde do projeto (0-100). Considera FPY, DDP, Lead Time, WIP e gargalos.<br>
                <b>FK (Fator K)</b> — Story Points entregues dividido por bugs. FK ≥ 3 = Maturidade | FK < 2 = Atenção
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        fpy = calcular_fpy(df)
        ddp = calcular_ddp(df)
        lead = calcular_lead_time(df)
        fk = calcular_fator_k(sp_total, bugs_total)
        mat = classificar_maturidade(fk)
        
        def mini_tech_card(valor, titulo, meta, cor):
            return f'<div style="background: white; border: 1px solid {cor}40; border-radius: 8px; padding: 10px 6px; text-align: center; height: 75px; display: flex; flex-direction: column; justify-content: center; margin-bottom: 12px;"><div style="font-size: 18px; font-weight: 700; color: {cor};">{valor}</div><div style="font-size: 12px; font-weight: 600; color: #374151;">{titulo}</div><div style="font-size: 11px; color: #9ca3af;">{meta}</div></div>'
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        cor_fpy = "#22c55e" if fpy['valor'] >= 80 else "#f59e0b" if fpy['valor'] >= 60 else "#ef4444"
        cor_ddp = "#22c55e" if ddp['valor'] >= 85 else "#f59e0b" if ddp['valor'] >= 70 else "#ef4444"
        cor_lead = "#22c55e" if lead['medio'] <= 7 else "#f59e0b" if lead['medio'] <= 14 else "#ef4444"
        cor_hs = "#22c55e" if health['score'] >= 75 else "#f59e0b" if health['score'] >= 50 else "#ef4444"
        cor_fk = "#22c55e" if fk >= 3 else "#f59e0b" if fk >= 2 else "#ef4444"
        
        with col1:
            st.markdown(mini_tech_card(f"{fpy['valor']:.0f}%", "FPY", "Meta: 80%", cor_fpy), unsafe_allow_html=True)
        with col2:
            st.markdown(mini_tech_card(f"{ddp['valor']:.0f}%", "DDP", "Meta: 85%", cor_ddp), unsafe_allow_html=True)
        with col3:
            st.markdown(mini_tech_card(f"{lead['medio']:.1f}d", "Lead Time", "Meta: ≤7d", cor_lead), unsafe_allow_html=True)
        with col4:
            st.markdown(mini_tech_card(f"{health['score']:.0f}", "Health", "Meta: ≥75", cor_hs), unsafe_allow_html=True)
        with col5:
            st.markdown(mini_tech_card(f"{fk:.1f}", f"FK {mat['emoji']}", mat['selo'], cor_fk), unsafe_allow_html=True)
    
    # ==== 5. CARDS POR STATUS ====
    with st.expander("📋 Distribuição por Status", expanded=False):
        status_counts = df.groupby('status_cat').size().to_dict()
        
        # Legenda do fluxo
        st.markdown('<div style="background: #f8fafc; border-radius: 8px; padding: 12px 16px; margin-bottom: 16px;"><div style="font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 8px;">📌 Fluxo de trabalho:</div><div style="font-size: 12px; color: #6b7280; line-height: 1.6;">🟣 <b>Desenvolvimento</b> → 🩷 <b>Code Review</b> (revisão de código) → 🟠 <b>Aguardando QA</b> (na fila) → 🔵 <b>Em Teste</b> (QA testando) → 🟢 <b>Concluído</b></div></div>', unsafe_allow_html=True)
        
        etapas = [
            ('development', 'Desenvolvimento', '#8b5cf6'),
            ('code_review', 'Code Review', '#ec4899'),
            ('waiting_qa', 'Aguardando QA', '#f59e0b'),
            ('testing', 'Em Teste', '#3b82f6'),
            ('done', 'Concluído', '#22c55e'),
        ]
        
        cols = st.columns(len(etapas))
        for i, (status_key, nome, cor) in enumerate(etapas):
            count = status_counts.get(status_key, 0)
            pct = (count / total * 100) if total > 0 else 0
            
            with cols[i]:
                html = f'<div style="text-align: center; padding: 12px 8px; background: {cor}10; border-radius: 8px; border: 1px solid {cor}40; margin-bottom: 12px;"><div style="font-size: 22px; font-weight: 700; color: {cor};">{count}</div><div style="font-size: 12px; color: {cor}; font-weight: 600;">{nome}</div><div style="font-size: 11px; color: #9ca3af;">{pct:.0f}%</div></div>'
                st.markdown(html, unsafe_allow_html=True)
        
        st.markdown('<div style="font-size: 13px; font-weight: 600; color: #374151; margin: 8px 0;">🔍 Filtrar cards por etapa:</div>', unsafe_allow_html=True)
        status_selecionado = st.selectbox("Selecione a etapa:", options=[s[1] for s in etapas], index=0, key="status_filter", label_visibility="collapsed")
        
        status_key = next((s[0] for s in etapas if s[1] == status_selecionado), None)
        if status_key:
            df_status = df[df['status_cat'] == status_key]
            if not df_status.empty:
                mostrar_lista_df_completa(df_status, status_selecionado)
            else:
                st.info(f"Nenhum card em '{status_selecionado}'")
    
    # ==== 6. ANÁLISE DE SPRINT ====
    projeto_atual = df['projeto'].iloc[0] if not df.empty and 'projeto' in df.columns else 'SD'
    if projeto_atual in ['SD', 'QA']:
        with st.expander("🎯 Planejado vs Entregue", expanded=False):
            df_sprint = df[df['sprint'] != 'Sem Sprint'].copy() if 'sprint' in df.columns else df.copy()
            
            if not df_sprint.empty:
                total_sprint = len(df_sprint)
                
                if 'adicionado_fora_periodo' in df_sprint.columns:
                    adicionados_depois = df_sprint[df_sprint['adicionado_fora_periodo'] == True]
                else:
                    adicionados_depois = pd.DataFrame()
                
                hotfixes = df_sprint[df_sprint['tipo'] == 'HOTFIX'] if 'tipo' in df_sprint.columns else pd.DataFrame()
                n_fora = len(adicionados_depois)
                n_hotfix = len(hotfixes)
                
                def mini_plan_card(valor, titulo, meta, cor):
                    return f'<div style="background: white; border: 1px solid {cor}40; border-radius: 8px; padding: 10px 6px; text-align: center; height: 75px; display: flex; flex-direction: column; justify-content: center; margin-bottom: 12px;"><div style="font-size: 18px; font-weight: 700; color: {cor};">{valor}</div><div style="font-size: 12px; font-weight: 600; color: #374151;">{titulo}</div><div style="font-size: 11px; color: #9ca3af;">{meta}</div></div>'
                
                cor_entrega = "#22c55e" if pct_conclusao >= 80 else "#f59e0b" if pct_conclusao >= 60 else "#ef4444"
                cor_fora = "#22c55e" if n_fora <= 3 else "#f59e0b" if n_fora <= 6 else "#ef4444"
                cor_hotfix = "#22c55e" if n_hotfix == 0 else "#f59e0b" if n_hotfix <= 3 else "#ef4444"
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(mini_plan_card(f"{pct_conclusao:.0f}%", "Taxa Entrega", "Meta: 80%", cor_entrega), unsafe_allow_html=True)
                with col2:
                    st.markdown(mini_plan_card(str(n_fora), "Fora Plano", "Limite: 3", cor_fora), unsafe_allow_html=True)
                with col3:
                    st.markdown(mini_plan_card(str(n_hotfix), "Hotfixes", "urgências", cor_hotfix), unsafe_allow_html=True)
            else:
                st.info("Nenhum card com sprint definida")
    
    # ==== 7. GRÁFICOS ====
    with st.expander("📊 Visualizações", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de distribuição por tipo
            if 'tipo' in df.columns:
                tipo_count = df['tipo'].value_counts().reset_index()
                tipo_count.columns = ['tipo', 'count']
                
                cores_tipo = {
                    'TAREFA': '#3b82f6',
                    'BUG': '#ef4444',
                    'HOTFIX': '#f97316',
                    'SUGESTÃO': '#8b5cf6',
                    'MELHORIA': '#22c55e'
                }
                
                fig = px.pie(
                    tipo_count, 
                    values='count', 
                    names='tipo',
                    title='Distribuição por Tipo',
                    color='tipo',
                    color_discrete_map=cores_tipo,
                    hole=0.4
                )
                fig.update_layout(height=320, margin=dict(t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Dados de tipo não disponíveis")
        
        with col2:
            # Gráfico de bugs por desenvolvedor (top 5)
            if 'desenvolvedor' in df.columns and 'bugs' in df.columns:
                dev_bugs = df.groupby('desenvolvedor').agg({
                    'bugs': 'sum',
                    'ticket_id': 'count'
                }).reset_index()
                dev_bugs.columns = ['Desenvolvedor', 'Bugs', 'Cards']
                dev_bugs = dev_bugs[dev_bugs['Desenvolvedor'] != 'Não atribuído']
                dev_bugs = dev_bugs.sort_values('Bugs', ascending=True).tail(6)
                
                if not dev_bugs.empty:
                    fig = px.bar(
                        dev_bugs,
                        y='Desenvolvedor',
                        x='Bugs',
                        title='Bugs por Desenvolvedor (Top 6)',
                        orientation='h',
                        color='Bugs',
                        color_continuous_scale=['#22c55e', '#f59e0b', '#ef4444']
                    )
                    fig.update_layout(height=320, margin=dict(t=40, b=20), showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Sem dados de bugs por desenvolvedor")
            else:
                st.info("Dados de desenvolvedores não disponíveis")
