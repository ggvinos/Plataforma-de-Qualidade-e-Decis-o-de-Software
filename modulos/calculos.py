"""
================================================================================
MÓDULO DE CÁLCULOS - NinaDash v8.82
================================================================================
Contém todas as funções de cálculo de métricas, concentração e processamento.

Responsabilidades:
- Cálculo de métricas (FPY, DDP, Fator K, Lead Time, etc)
- Análise de concentração de conhecimento
- Processamento de issues
- Cálculos de governança, QA, produto e health scores

Dependências:
- streamlit (para cache_data, components)
- pandas (para DataFrames)
- plotly (para gráficos)
- datetime (para datas)
- modulos.config (CUSTOM_FIELDS, REGRAS, STATUS_FLOW, TEMAS_NAO_CLIENTES)
- modulos.utils (link_jira, avaliar_janela_validacao)

Author: GitHub Copilot
Version: 1.0 (Phase 4)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple

from modulos.config import (
    CUSTOM_FIELDS,
    REGRAS,
    STATUS_FLOW,
    TEMAS_NAO_CLIENTES,
)

from modulos.utils import (
    link_jira,
    avaliar_janela_validacao,
)


# ==============================================================================
# CÁLCULOS BÁSICOS DE MÉTRICAS
# ==============================================================================

def calcular_fator_k(sp: int, bugs: int) -> float:
    """
    Calcula Fator K = SP / (Bugs + 1)
    
    Métrica de maturidade do desenvolvedor:
    - Quanto maior o SP em relação aos bugs, mais maduro/confiável
    - +1 evita divisão por zero
    
    Args:
        sp: Story Points
        bugs: Bugs encontrados
    
    Returns:
        Fator K arredondado a 2 casas decimais
    """
    if sp == 0:
        return 0
    return round(sp / (bugs + 1), 2)


def classificar_maturidade(fk: float) -> Dict:
    """
    Classifica nível de maturidade baseado no Fator K.
    
    Escala:
    - Gold: FK >= 3.0 (Excelente)
    - Silver: FK >= 2.0 (Bom)
    - Bronze: FK >= 1.0 (Regular)
    - Risco: FK < 1.0 (Crítico)
    
    Args:
        fk: Fator K
    
    Returns:
        Dict com selo, emoji, cor e descrição
    """
    if fk >= 3.0:
        return {"selo": "Gold", "emoji": "🥇", "cor": "#22c55e", "desc": "Excelente"}
    elif fk >= 2.0:
        return {"selo": "Silver", "emoji": "🥈", "cor": "#eab308", "desc": "Bom"}
    elif fk >= 1.0:
        return {"selo": "Bronze", "emoji": "🥉", "cor": "#f97316", "desc": "Regular"}
    else:
        return {"selo": "Risco", "emoji": "⚠️", "cor": "#ef4444", "desc": "Crítico"}


def calcular_ddp(df: pd.DataFrame) -> Dict:
    """
    Defect Detection Percentage (DDP).
    
    Percentual de bugs encontrados em QA vs bugs que escapariam para produção.
    
    Formula: DDP = (Bugs_QA / (Bugs_QA + Bugs_Prod_Estimados)) * 100
    
    Args:
        df: DataFrame com cards
    
    Returns:
        Dict com {'valor': float, 'bugs_qa': int}
    """
    bugs_qa = df['bugs'].sum()
    bugs_estimados_prod = max(1, len(df) * 0.05)
    total_bugs = bugs_qa + bugs_estimados_prod
    ddp = (bugs_qa / total_bugs * 100) if total_bugs > 0 else 100
    return {"valor": round(ddp, 1), "bugs_qa": int(bugs_qa)}


def calcular_fpy(df: pd.DataFrame) -> Dict:
    """
    First Pass Yield (FPY).
    
    Percentual de cards entregues SEM bugs na primeira tentativa.
    
    Args:
        df: DataFrame com cards
    
    Returns:
        Dict com {'valor': float, 'sem_bugs': int, 'total': int}
    """
    total = len(df)
    if total == 0:
        return {"valor": 0, "sem_bugs": 0, "total": 0}
    sem_bugs = len(df[df['bugs'] == 0])
    fpy = sem_bugs / total * 100
    return {"valor": round(fpy, 1), "sem_bugs": sem_bugs, "total": total}


def calcular_lead_time(df: pd.DataFrame) -> Dict:
    """
    Lead time médio e percentis (p50, p85, p95).
    
    Tempo desde criação até resolução em dias.
    
    Args:
        df: DataFrame com cards
    
    Returns:
        Dict com {'medio', 'p50', 'p85', 'p95'} todos em dias
    """
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
    """
    Análise completa de um desenvolvedor individual.
    
    Args:
        df: DataFrame com cards
        dev_nome: Nome do desenvolvedor
    
    Returns:
        Dict com análise ou None se dev não encontrado
    """
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


# ==============================================================================
# ANÁLISE DE CONCENTRAÇÃO DE CONHECIMENTO
# ==============================================================================

def filtrar_qas_principais(df: pd.DataFrame, min_cards: int = 5) -> List[str]:
    """
    Retorna lista dos QAs principais (que mais validaram cards).
    Filtra pessoas que eventualmente validam mas não são QAs do time.
    
    Args:
        df: DataFrame com os cards
        min_cards: Mínimo de cards para ser considerado QA principal
    
    Returns:
        Lista de nomes dos QAs principais
    """
    if df.empty:
        return []
    
    # Conta cards por QA
    qa_counts = df[df['qa'] != 'Não atribuído'].groupby('qa').size().reset_index(name='total_cards')
    
    # Filtra apenas QAs com quantidade significativa de cards
    qas_principais = qa_counts[qa_counts['total_cards'] >= min_cards]['qa'].tolist()
    
    return qas_principais


def calcular_concentracao_conhecimento(df: pd.DataFrame) -> Dict:
    """
    Calcula métricas de concentração de conhecimento por DEV e QA,
    segmentado por Produto e Cliente.
    
    Identificapontos de risco onde conhecimento está muito centralizado.
    
    Args:
        df: DataFrame com cards
    
    Returns:
        Dict com matrizes, índices, alertas e recomendações
    """
    if df.empty:
        return {
            "dev_produto": pd.DataFrame(),
            "qa_produto": pd.DataFrame(),
            "dev_cliente": pd.DataFrame(),
            "qa_cliente": pd.DataFrame(),
            "alertas_dev": [],
            "alertas_qa": [],
            "recomendacoes": [],
            "indices": {},
            "qas_principais": [],
        }
    
    # Filtra QAs principais
    qas_principais = filtrar_qas_principais(df)
    
    # Cópia para manipulação
    df_analise = df.copy()
    
    # Extrai cliente do campo tema_principal (filtra temas internos)
    def extrair_cliente(tema):
        if not tema or tema == 'Sem tema':
            return 'Sem cliente'
        tema_lower = tema.lower().strip()
        for interno in TEMAS_NAO_CLIENTES:
            if interno.lower() in tema_lower:
                return 'Interno/Plataforma'
        return tema
    
    df_analise['cliente'] = df_analise['tema_principal'].apply(extrair_cliente)
    
    # ==================== MATRIZ DEV x PRODUTO ====================
    dev_produto = df_analise[df_analise['desenvolvedor'] != 'Não atribuído'].groupby(
        ['desenvolvedor', 'produto']
    ).agg({
        'ticket_id': 'count',
        'sp': 'sum',
        'bugs': 'sum'
    }).reset_index()
    dev_produto.columns = ['DEV', 'Produto', 'Cards', 'SP', 'Bugs']
    
    matriz_dev_produto = dev_produto.pivot_table(
        index='DEV', 
        columns='Produto', 
        values='Cards', 
        fill_value=0,
        aggfunc='sum'
    )
    
    # ==================== MATRIZ QA x PRODUTO ====================
    df_qa = df_analise[(df_analise['qa'].isin(qas_principais)) & (df_analise['qa'] != 'Não atribuído')]
    
    qa_produto = df_qa.groupby(['qa', 'produto']).agg({
        'ticket_id': 'count',
        'sp': 'sum',
        'bugs': 'sum'
    }).reset_index()
    qa_produto.columns = ['QA', 'Produto', 'Cards', 'SP', 'Bugs']
    
    matriz_qa_produto = qa_produto.pivot_table(
        index='QA', 
        columns='Produto', 
        values='Cards', 
        fill_value=0,
        aggfunc='sum'
    ) if not qa_produto.empty else pd.DataFrame()
    
    # ==================== MATRIZ DEV x CLIENTE ====================
    dev_cliente = df_analise[df_analise['desenvolvedor'] != 'Não atribuído'].groupby(
        ['desenvolvedor', 'cliente']
    ).agg({
        'ticket_id': 'count',
        'sp': 'sum',
        'bugs': 'sum'
    }).reset_index()
    dev_cliente.columns = ['DEV', 'Cliente', 'Cards', 'SP', 'Bugs']
    
    matriz_dev_cliente = dev_cliente.pivot_table(
        index='DEV', 
        columns='Cliente', 
        values='Cards', 
        fill_value=0,
        aggfunc='sum'
    )
    
    # ==================== MATRIZ QA x CLIENTE ====================
    qa_cliente = df_qa.groupby(['qa', 'cliente']).agg({
        'ticket_id': 'count',
        'sp': 'sum',
        'bugs': 'sum'
    }).reset_index()
    qa_cliente.columns = ['QA', 'Cliente', 'Cards', 'SP', 'Bugs']
    
    matriz_qa_cliente = qa_cliente.pivot_table(
        index='QA', 
        columns='Cliente', 
        values='Cards', 
        fill_value=0,
        aggfunc='sum'
    ) if not qa_cliente.empty else pd.DataFrame()
    
    # ==================== CÁLCULO DE ÍNDICES ====================
    alertas_dev = []
    alertas_qa = []
    indices = {
        "dev_produto": {},
        "qa_produto": {},
        "dev_cliente": {},
        "qa_cliente": {},
    }
    
    # Análise DEV x Produto
    for produto in matriz_dev_produto.columns:
        col = matriz_dev_produto[produto]
        total = col.sum()
        if total > 0:
            max_val = col.max()
            max_dev = col.idxmax()
            concentracao = (max_val / total) * 100
            
            indices["dev_produto"][produto] = {
                "top_pessoa": max_dev,
                "top_cards": int(max_val),
                "total_cards": int(total),
                "concentracao_pct": round(concentracao, 1),
                "pessoas_atuando": int((col > 0).sum()),
            }
            
            if concentracao >= 80:
                alertas_dev.append({
                    "tipo": "critico",
                    "contexto": "produto",
                    "nome": produto,
                    "pessoa": max_dev,
                    "pct": round(concentracao, 1),
                    "msg": f"🔴 CRÍTICO: {max_dev} desenvolveu {concentracao:.0f}% dos cards do produto '{produto}'"
                })
            elif concentracao >= 60:
                alertas_dev.append({
                    "tipo": "atencao",
                    "contexto": "produto",
                    "nome": produto,
                    "pessoa": max_dev,
                    "pct": round(concentracao, 1),
                    "msg": f"🟡 ATENÇÃO: {max_dev} desenvolveu {concentracao:.0f}% dos cards do produto '{produto}'"
                })
    
    # Análise QA x Produto
    if not matriz_qa_produto.empty:
        for produto in matriz_qa_produto.columns:
            col = matriz_qa_produto[produto]
            total = col.sum()
            if total > 0:
                max_val = col.max()
                max_qa = col.idxmax()
                concentracao = (max_val / total) * 100
                
                indices["qa_produto"][produto] = {
                    "top_pessoa": max_qa,
                    "top_cards": int(max_val),
                    "total_cards": int(total),
                    "concentracao_pct": round(concentracao, 1),
                    "pessoas_atuando": int((col > 0).sum()),
                }
                
                if concentracao >= 80:
                    alertas_qa.append({
                        "tipo": "critico",
                        "contexto": "produto",
                        "nome": produto,
                        "pessoa": max_qa,
                        "pct": round(concentracao, 1),
                        "msg": f"🔴 CRÍTICO: {max_qa} validou {concentracao:.0f}% dos cards do produto '{produto}'"
                    })
                elif concentracao >= 60:
                    alertas_qa.append({
                        "tipo": "atencao",
                        "contexto": "produto",
                        "nome": produto,
                        "pessoa": max_qa,
                        "pct": round(concentracao, 1),
                        "msg": f"🟡 ATENÇÃO: {max_qa} validou {concentracao:.0f}% dos cards do produto '{produto}'"
                    })
    
    # Análise DEV x Cliente
    for cliente in matriz_dev_cliente.columns:
        if cliente in ['Sem cliente', 'Interno/Plataforma']:
            continue
        col = matriz_dev_cliente[cliente]
        total = col.sum()
        if total >= 3:
            max_val = col.max()
            max_dev = col.idxmax()
            concentracao = (max_val / total) * 100
            
            indices["dev_cliente"][cliente] = {
                "top_pessoa": max_dev,
                "top_cards": int(max_val),
                "total_cards": int(total),
                "concentracao_pct": round(concentracao, 1),
                "pessoas_atuando": int((col > 0).sum()),
            }
            
            if concentracao >= 80:
                alertas_dev.append({
                    "tipo": "critico",
                    "contexto": "cliente",
                    "nome": cliente,
                    "pessoa": max_dev,
                    "pct": round(concentracao, 1),
                    "msg": f"🔴 CRÍTICO: {max_dev} desenvolveu {concentracao:.0f}% dos cards do cliente '{cliente}'"
                })
            elif concentracao >= 60:
                alertas_dev.append({
                    "tipo": "atencao",
                    "contexto": "cliente",
                    "nome": cliente,
                    "pessoa": max_dev,
                    "pct": round(concentracao, 1),
                    "msg": f"🟡 ATENÇÃO: {max_dev} desenvolveu {concentracao:.0f}% dos cards do cliente '{cliente}'"
                })
    
    # Análise QA x Cliente
    if not matriz_qa_cliente.empty:
        for cliente in matriz_qa_cliente.columns:
            if cliente in ['Sem cliente', 'Interno/Plataforma']:
                continue
            col = matriz_qa_cliente[cliente]
            total = col.sum()
            if total >= 3:
                max_val = col.max()
                max_qa = col.idxmax()
                concentracao = (max_val / total) * 100
                
                indices["qa_cliente"][cliente] = {
                    "top_pessoa": max_qa,
                    "top_cards": int(max_val),
                    "total_cards": int(total),
                    "concentracao_pct": round(concentracao, 1),
                    "pessoas_atuando": int((col > 0).sum()),
                }
                
                if concentracao >= 80:
                    alertas_qa.append({
                        "tipo": "critico",
                        "contexto": "cliente",
                        "nome": cliente,
                        "pessoa": max_qa,
                        "pct": round(concentracao, 1),
                        "msg": f"🔴 CRÍTICO: {max_qa} validou {concentracao:.0f}% dos cards do cliente '{cliente}'"
                    })
                elif concentracao >= 60:
                    alertas_qa.append({
                        "tipo": "atencao",
                        "contexto": "cliente",
                        "nome": cliente,
                        "pessoa": max_qa,
                        "pct": round(concentracao, 1),
                        "msg": f"🟡 ATENÇÃO: {max_qa} validou {concentracao:.0f}% dos cards do cliente '{cliente}'"
                    })
    
    # Recomendações
    recomendacoes = gerar_recomendacoes_rodizio(
        matriz_dev_produto, matriz_qa_produto,
        matriz_dev_cliente, matriz_qa_cliente,
        alertas_dev, alertas_qa
    )
    
    return {
        "dev_produto": dev_produto,
        "qa_produto": qa_produto,
        "dev_cliente": dev_cliente,
        "qa_cliente": qa_cliente,
        "matriz_dev_produto": matriz_dev_produto,
        "matriz_qa_produto": matriz_qa_produto,
        "matriz_dev_cliente": matriz_dev_cliente,
        "matriz_qa_cliente": matriz_qa_cliente,
        "alertas_dev": alertas_dev,
        "alertas_qa": alertas_qa,
        "recomendacoes": recomendacoes,
        "indices": indices,
        "qas_principais": qas_principais,
    }


def gerar_recomendacoes_rodizio(
    matriz_dev_produto: pd.DataFrame,
    matriz_qa_produto: pd.DataFrame,
    matriz_dev_cliente: pd.DataFrame,
    matriz_qa_cliente: pd.DataFrame,
    alertas_dev: List[Dict],
    alertas_qa: List[Dict]
) -> List[Dict]:
    """
    Gera recomendações automáticas de rodízio baseado nas concentrações.
    
    Args:
        Matrizes de concentração e alertas detectados
    
    Returns:
        Lista de recomendações de rodízio
    """
    recomendacoes = []
    
    # Para cada alerta crítico de DEV, sugere outros DEVs
    for alerta in alertas_dev:
        if alerta["tipo"] == "critico":
            contexto = alerta["contexto"]
            nome = alerta["nome"]
            pessoa_dominante = alerta["pessoa"]
            
            if contexto == "produto" and not matriz_dev_produto.empty and nome in matriz_dev_produto.columns:
                col = matriz_dev_produto[nome]
                devs_sem_experiencia = col[col == 0].index.tolist()
                devs_pouca_experiencia = col[(col > 0) & (col < col.max() * 0.3)].index.tolist()
                
                sugestoes = devs_pouca_experiencia[:3] if devs_pouca_experiencia else devs_sem_experiencia[:3]
                
                if sugestoes:
                    recomendacoes.append({
                        "tipo": "rodizio_dev",
                        "contexto": contexto,
                        "nome": nome,
                        "pessoa_atual": pessoa_dominante,
                        "sugestoes": sugestoes,
                        "msg": f"🔄 **Rodízio para '{nome}':** Considere atribuir próximos cards a {', '.join(sugestoes)}"
                    })
    
    # Para cada alerta crítico de QA, sugere outros QAs
    for alerta in alertas_qa:
        if alerta["tipo"] == "critico":
            contexto = alerta["contexto"]
            nome = alerta["nome"]
            
            if contexto == "produto" and not matriz_qa_produto.empty and nome in matriz_qa_produto.columns:
                col = matriz_qa_produto[nome]
                qas_sem_experiencia = col[col == 0].index.tolist()
                qas_pouca_experiencia = col[(col > 0) & (col < col.max() * 0.3)].index.tolist()
                
                sugestoes = qas_pouca_experiencia[:2] if qas_pouca_experiencia else qas_sem_experiencia[:2]
                
                if sugestoes:
                    recomendacoes.append({
                        "tipo": "rodizio_qa",
                        "contexto": contexto,
                        "nome": nome,
                        "sugestoes": sugestoes,
                        "msg": f"🔄 **Rodízio de QA para '{nome}':** Considere atribuir validações a {', '.join(sugestoes)}"
                    })
    
    # Recomendação geral se houver muitos alertas
    total_alertas = len([a for a in alertas_dev + alertas_qa if a["tipo"] == "critico"])
    if total_alertas >= 3:
        recomendacoes.insert(0, {
            "tipo": "geral",
            "msg": f"⚠️ **{total_alertas} áreas com concentração crítica.** Revisar distribuição na próxima sprint planning."
        })
    
    return recomendacoes


def calcular_concentracao_pessoa(df: pd.DataFrame, pessoa: str, tipo: str = "dev") -> Dict:
    """
    Calcula a concentração de conhecimento de uma pessoa específica (DEV ou QA).
    
    Args:
        df: DataFrame com cards
        pessoa: Nome da pessoa
        tipo: "dev" ou "qa"
    
    Returns:
        Dict com resumo de concentração (produtos, clientes, alertas)
    """
    if df.empty:
        return {"produtos": [], "clientes": [], "alertas": [], "total_cards": 0}
    
    coluna = 'desenvolvedor' if tipo == "dev" else 'qa'
    df_pessoa = df[df[coluna] == pessoa].copy()
    
    if df_pessoa.empty:
        return {"produtos": [], "clientes": [], "alertas": [], "total_cards": 0}
    
    total_cards = len(df_pessoa)
    
    # Extrai cliente
    def extrair_cliente(tema):
        if not tema or tema == 'Sem tema':
            return 'Sem cliente'
        tema_lower = tema.lower().strip()
        for interno in TEMAS_NAO_CLIENTES:
            if interno.lower() in tema_lower:
                return 'Interno/Plataforma'
        return tema
    
    df_pessoa['cliente'] = df_pessoa['tema_principal'].apply(extrair_cliente)
    
    # Por produto
    por_produto = df_pessoa.groupby('produto').agg({
        'ticket_id': 'count',
        'sp': 'sum'
    }).reset_index()
    por_produto.columns = ['nome', 'cards', 'sp']
    por_produto['pct'] = (por_produto['cards'] / total_cards * 100).round(1)
    por_produto = por_produto.sort_values('cards', ascending=False)
    
    # Por cliente
    por_cliente = df_pessoa.groupby('cliente').agg({
        'ticket_id': 'count',
        'sp': 'sum'
    }).reset_index()
    por_cliente.columns = ['nome', 'cards', 'sp']
    por_cliente['pct'] = (por_cliente['cards'] / total_cards * 100).round(1)
    por_cliente = por_cliente.sort_values('cards', ascending=False)
    
    # Alertas (concentração >= 60%)
    alertas = []
    for _, row in por_produto.iterrows():
        if row['pct'] >= 60 and row['nome'] != 'Não definido':
            alertas.append({
                "tipo": "produto",
                "nome": row['nome'],
                "pct": row['pct'],
                "cards": row['cards']
            })
    
    for _, row in por_cliente.iterrows():
        if row['pct'] >= 60 and row['nome'] not in ['Sem cliente', 'Interno/Plataforma']:
            alertas.append({
                "tipo": "cliente",
                "nome": row['nome'],
                "pct": row['pct'],
                "cards": row['cards']
            })
    
    return {
        "produtos": por_produto.to_dict('records'),
        "clientes": por_cliente.to_dict('records'),
        "alertas": alertas,
        "total_cards": total_cards
    }


# ==============================================================================
# CÁLCULOS DE GOVERNANÇA E MÉTRICAS POR CONTEXTO
# ==============================================================================

def calcular_metricas_governanca(df: pd.DataFrame) -> Dict:
    """
    Calcula métricas de governança de dados.
    
    Verifica preenchimento de campos críticos: SP, Bugs, Complexidade, QA.
    
    Args:
        df: DataFrame com cards
    
    Returns:
        Dict com taxas de preenchimento por campo
    """
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
    """
    Calcula métricas específicas de QA e gargalos.
    
    Analisa funil de validação, carga, aging e taxa de reprovação.
    
    Args:
        df: DataFrame com cards
    
    Returns:
        Dict com métricas de QA
    """
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
    """
    Calcula métricas por produto (Ellen metrics).
    
    Analisa hotfixes, finalizações na sprint e itens adicionados fora.
    
    Args:
        df: DataFrame com cards
    
    Returns:
        Dict com métricas de produto
    """
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
    """
    Calcula score de saúde da release (0-100).
    
    Baseado em: conclusão (30%), DDP (25%), FPY (20%), gargalos (15%), lead time (10%).
    
    Args:
        df: DataFrame com cards
    
    Returns:
        Dict com score total, status e detalhes por componente
    """
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
    """
    Calcula métricas por desenvolvedor.
    
    Agregações de cards, SP, bugs e Fator K.
    
    Args:
        df: DataFrame com cards
    
    Returns:
        Dict com stats por DEV
    """
    dev_stats = df.groupby('desenvolvedor').agg({
        'ticket_id': 'count',
        'sp': 'sum',
        'bugs': 'sum',
    }).reset_index()
    dev_stats.columns = ['Desenvolvedor', 'Cards', 'SP', 'Bugs']
    dev_stats['FK'] = dev_stats.apply(lambda x: calcular_fator_k(x['SP'], x['Bugs']), axis=1)
    dev_stats['Maturidade'] = dev_stats['FK'].apply(lambda x: classificar_maturidade(x)['selo'])
    
    return {"stats": dev_stats.sort_values('Cards', ascending=False)}


def calcular_metricas_backlog(df: pd.DataFrame) -> Dict:
    """Calcula métricas específicas para análise do Product Backlog."""
    hoje = datetime.now()
    
    # Categorias de status que representam "backlog" (não concluído, não em dev ativo)
    # Inclui status específicos do projeto PB
    categorias_backlog = [
        'backlog', 
        'pb_revisao_produto', 
        'pb_roteiro', 
        'pb_ux', 
        'pb_esforco', 
        'pb_aguarda_dev',
        'pb_aguardando_resposta',
        'unknown'  # Inclui unknown para capturar itens não mapeados
    ]
    
    # Filtrar itens no backlog (status de backlog ou PB)
    df_backlog = df[df['status_cat'].isin(categorias_backlog)]
    
    # Se não houver itens, considerar todos não concluídos
    if df_backlog.empty:
        df_backlog = df[~df['status_cat'].isin(['done', 'deferred', 'valprod_aprovado'])]
    
    # REMOVER HOTFIX - não passa por produto, vai direto pra dev
    df_backlog = df_backlog[df_backlog['tipo'] != 'HOTFIX']
    
    total_backlog = len(df_backlog)
    
    if total_backlog == 0:
        return {
            "total_itens": 0,
            "sp_pendentes": 0,
            "idade_media": 0,
            "idade_mediana": 0,
            "pct_sem_sp": 0,
            "pct_sem_responsavel": 0,
            "cards_aging": pd.DataFrame(),
            "por_prioridade": {},
            "por_tipo": {},
            "por_produto": pd.DataFrame(),
            "score_saude": 100,
            "status_saude": "🟢 Saudável",
            "faixas_idade": {"0-15": 0, "16-30": 0, "31-60": 0, "61-90": 0, "90+": 0},
            "cards_sem_sprint": pd.DataFrame(),
            "cards_sem_responsavel": pd.DataFrame(),
            "cards_sem_sp": pd.DataFrame(),
            "cards_estagnados": pd.DataFrame(),
            "mais_antigo": 0,
            "df_backlog": df_backlog,
            "recomendacoes": [],
        }
    
    # Calcular idade em dias
    df_backlog = df_backlog.copy()
    df_backlog['idade_dias'] = df_backlog['criado'].apply(lambda x: (hoje - x).days if pd.notna(x) else 0)
    df_backlog['dias_sem_update'] = df_backlog['atualizado'].apply(lambda x: (hoje - x).days if pd.notna(x) else 0)
    
    # Métricas básicas
    sp_pendentes = int(df_backlog['sp'].sum())
    idade_media = df_backlog['idade_dias'].mean()
    idade_mediana = df_backlog['idade_dias'].median()
    mais_antigo = df_backlog['idade_dias'].max()
    
    # Cards sem estimativa
    sem_sp = df_backlog[df_backlog['sp'] == 0]
    pct_sem_sp = len(sem_sp) / total_backlog * 100 if total_backlog > 0 else 0
    
    # Cards sem responsável
    sem_responsavel = df_backlog[df_backlog['desenvolvedor'] == 'Não atribuído']
    pct_sem_responsavel = len(sem_responsavel) / total_backlog * 100 if total_backlog > 0 else 0
    
    # Faixas de idade
    faixas_idade = {
        "0-15": len(df_backlog[df_backlog['idade_dias'] <= 15]),
        "16-30": len(df_backlog[(df_backlog['idade_dias'] > 15) & (df_backlog['idade_dias'] <= 30)]),
        "31-60": len(df_backlog[(df_backlog['idade_dias'] > 30) & (df_backlog['idade_dias'] <= 60)]),
        "61-90": len(df_backlog[(df_backlog['idade_dias'] > 60) & (df_backlog['idade_dias'] <= 90)]),
        "90+": len(df_backlog[df_backlog['idade_dias'] > 90]),
    }
    
    # Cards aging (> 60 dias)
    cards_aging = df_backlog[df_backlog['idade_dias'] > 60].sort_values('idade_dias', ascending=False)
    
    # Cards estagnados (sem update há mais de 30 dias)
    cards_estagnados = df_backlog[df_backlog['dias_sem_update'] > 30].sort_values('dias_sem_update', ascending=False)
    
    # Cards sem sprint
    cards_sem_sprint = df_backlog[df_backlog['sprint'] == 'Sem Sprint']
    
    # Distribuição por prioridade
    por_prioridade = df_backlog['prioridade'].value_counts().to_dict()
    
    # Distribuição por tipo
    por_tipo = df_backlog['tipo'].value_counts().to_dict()
    
    # Por produto
    por_produto = df_backlog.groupby('produto').agg({
        'ticket_id': 'count',
        'sp': 'sum',
        'idade_dias': 'mean'
    }).reset_index()
    por_produto.columns = ['Produto', 'Cards', 'SP', 'Idade Média']
    por_produto['Idade Média'] = por_produto['Idade Média'].round(1)
    
    # Calcular score de saúde do backlog (0-100)
    # Componentes:
    # - Idade média (30%) - penaliza se > 30 dias
    # - % sem SP (25%) - penaliza itens sem estimativa
    # - Taxa de crescimento aprox (25%) - baseado em aging
    # - Priorização (20%) - penaliza se muitos críticos
    
    score_idade = max(0, 30 - (idade_media / 3)) if idade_media <= 90 else 0
    score_sp = max(0, 25 - (pct_sem_sp / 2))
    score_aging = max(0, 25 - (faixas_idade["90+"] * 2))
    
    pct_criticos = por_prioridade.get('Highest', 0) + por_prioridade.get('High', 0) + por_prioridade.get('Alta', 0)
    pct_criticos = (pct_criticos / total_backlog * 100) if total_backlog > 0 else 0
    score_priorizacao = max(0, 20 - (pct_criticos / 2))
    
    score_saude = round(score_idade + score_sp + score_aging + score_priorizacao, 0)
    
    if score_saude >= 75:
        status_saude = "🟢 Saudável"
    elif score_saude >= 50:
        status_saude = "🟡 Atenção"
    elif score_saude >= 25:
        status_saude = "🟠 Alerta"
    else:
        status_saude = "🔴 Crítico"
    
    # Gerar recomendações
    recomendacoes = []
    
    if faixas_idade["90+"] > 0:
        recomendacoes.append({
            "tipo": "🗑️ Candidatos a Descarte",
            "msg": f"{faixas_idade['90+']} itens estão há mais de 90 dias no backlog. Considere descartá-los.",
            "criticidade": "alta"
        })
    
    if pct_sem_sp > 30:
        recomendacoes.append({
            "tipo": "📝 Refinamento Necessário",
            "msg": f"{pct_sem_sp:.0f}% do backlog não tem estimativa. Agende um grooming.",
            "criticidade": "media"
        })
    
    if pct_sem_responsavel > 40:
        recomendacoes.append({
            "tipo": "👤 Atribuir Responsáveis",
            "msg": f"{pct_sem_responsavel:.0f}% dos itens não têm responsável definido.",
            "criticidade": "media"
        })
    
    if len(cards_estagnados) > 5:
        recomendacoes.append({
            "tipo": "⏸️ Cards Estagnados",
            "msg": f"{len(cards_estagnados)} cards não são atualizados há mais de 30 dias.",
            "criticidade": "media"
        })
    
    if idade_media > 60:
        recomendacoes.append({
            "tipo": "⚠️ Backlog Envelhecido",
            "msg": f"Idade média de {idade_media:.0f} dias. Revise a priorização.",
            "criticidade": "alta"
        })
    
    return {
        "total_itens": total_backlog,
        "sp_pendentes": sp_pendentes,
        "idade_media": round(idade_media, 1),
        "idade_mediana": round(idade_mediana, 1),
        "pct_sem_sp": round(pct_sem_sp, 1),
        "pct_sem_responsavel": round(pct_sem_responsavel, 1),
        "cards_aging": cards_aging,
        "por_prioridade": por_prioridade,
        "por_tipo": por_tipo,
        "por_produto": por_produto,
        "score_saude": score_saude,
        "status_saude": status_saude,
        "faixas_idade": faixas_idade,
        "cards_sem_sprint": cards_sem_sprint,
        "cards_sem_responsavel": sem_responsavel,
        "cards_sem_sp": sem_sp,
        "cards_estagnados": cards_estagnados,
        "mais_antigo": mais_antigo,
        "df_backlog": df_backlog,
        "recomendacoes": recomendacoes,
    }


# ==============================================================================
# PROCESSAMENTO DE ISSUES
# ==============================================================================

def processar_issue_unica(issue: Dict) -> Dict:
    """
    Processa uma issue única do Jira para dicionário de dados.
    
    Extrai todos os campos necessários para análise.
    
    Args:
        issue: Issue dict do Jira API
    
    Returns:
        Dict com dados processados da issue
    """
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
    
    # Desenvolvedor
    dev = f.get('assignee', {}).get('displayName', 'Não atribuído') if f.get('assignee') else 'Não atribuído'
    
    # Relator
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
    if sprint_atual and sprint_atual.get('endDate'):
        try:
            sprint_end = datetime.fromisoformat(sprint_atual.get('endDate').replace('Z', '+00:00')).replace(tzinfo=None)
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
    
    # Labels
    labels = f.get('labels', []) or []
    
    # Componentes
    componentes_raw = f.get('components', []) or []
    componentes = [c.get('name', '') for c in componentes_raw] if componentes_raw else []
    
    # Epic Link
    epic_link = ''
    parent = f.get('parent', {})
    if parent:
        epic_link = parent.get('key', '')
    
    # Métricas
    dias_em_status = (hoje - atualizado).days
    lead_time = (resolutiondate - criado).days if resolutiondate else (hoje - criado).days
    
    dias_ate_release = 0
    if sprint_end:
        dias_ate_release = max(0, (sprint_end - hoje).days)
    
    janela_info = avaliar_janela_validacao(dias_ate_release, complexidade)
    
    # Ambiente Desenvolvido
    ambiente_f = f.get(CUSTOM_FIELDS['ambiente_desenvolvido'])
    ambiente = ambiente_f.get('value', '') if isinstance(ambiente_f, dict) else ''
    ambiente_normalizado = ambiente.lower() if ambiente else ''
    em_producao = 'produção' in ambiente_normalizado or 'producao' in ambiente_normalizado
    em_homologacao = 'homologação' in ambiente_normalizado or 'homologacao' in ambiente_normalizado
    em_develop = 'develop' in ambiente_normalizado
    vai_subir_proxima_release = em_homologacao
    
    ticket_id = issue.get('key', '')
    
    return {
        'ticket_id': ticket_id,
        'link': link_jira(ticket_id),
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
        'criado_na_sprint': False,
        'finalizado_mesma_sprint': False,
        'adicionado_fora_periodo': False,
        'descricao': descricao,
        'labels': labels,
        'componentes': componentes,
        'epic_link': epic_link,
        'ambiente': ambiente,
        'em_producao': em_producao,
        'em_homologacao': em_homologacao,
        'em_develop': em_develop,
        'vai_subir_proxima_release': vai_subir_proxima_release,
    }


def processar_issues(issues: List[Dict]) -> pd.DataFrame:
    """
    Processa múltiplas issues do Jira para DataFrame.
    
    Aplica todas as transformações, mapeamentos e cálculos.
    
    Args:
        issues: List de issues do Jira API
    
    Returns:
        DataFrame com todas as issues processadas
    """
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
        
        # Desenvolvedor
        dev = f.get('assignee', {}).get('displayName', 'Não atribuído') if f.get('assignee') else 'Não atribuído'
        
        # Relator
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
        
        # Ambiente Desenvolvido (Develop, Homologação, Produção)
        ambiente_f = f.get(CUSTOM_FIELDS['ambiente_desenvolvido'])
        ambiente = ambiente_f.get('value', '') if isinstance(ambiente_f, dict) else ''
        # Normaliza para comparação
        ambiente_normalizado = ambiente.lower() if ambiente else ''
        em_producao = 'produção' in ambiente_normalizado or 'producao' in ambiente_normalizado
        em_homologacao = 'homologação' in ambiente_normalizado or 'homologacao' in ambiente_normalizado
        em_develop = 'develop' in ambiente_normalizado
        vai_subir_proxima_release = em_homologacao  # Cards em homologação sobem na próxima release
        
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
        
        # Issue Links - detectar origem do PB
        issuelinks = f.get('issuelinks', [])
        origem_pb = None
        tem_link_pb = False
        for link in issuelinks:
            # Link para card do PB (outward = implements)
            outward = link.get('outwardIssue', {})
            if outward.get('key', '').startswith('PB-'):
                origem_pb = outward.get('key')
                tem_link_pb = True
                break
            # Link reverso (inward = is implemented by)
            inward = link.get('inwardIssue', {})
            if inward.get('key', '').startswith('PB-'):
                origem_pb = inward.get('key')
                tem_link_pb = True
                break
        
        # Métricas
        dias_em_status = (hoje - atualizado).days
        lead_time = (resolutiondate - criado).days if resolutiondate else (hoje - criado).days
        
        dias_ate_release = 0
        if sprint_end:
            dias_ate_release = max(0, (sprint_end - hoje).days)
        
        # Flags
        criado_na_sprint = False
        if sprint_start and sprint_end:
            criado_na_sprint = sprint_start <= criado <= sprint_end
        
        finalizado_mesma_sprint = False
        if status_cat == 'done' and criado_na_sprint:
            finalizado_mesma_sprint = True
        
        adicionado_fora_periodo = False
        if sprint_start and criado > sprint_start + timedelta(days=2):
            adicionado_fora_periodo = True
        
        janela_info = avaliar_janela_validacao(dias_ate_release, complexidade)
        dentro_janela = janela_info["dentro_janela"]
        janela_status = janela_info["status"]
        janela_dias_necessarios = janela_info["dias_necessarios"]
        
        # Preenchimento
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
            'ambiente': ambiente,
            'em_producao': em_producao,
            'em_homologacao': em_homologacao,
            'em_develop': em_develop,
            'vai_subir_proxima_release': vai_subir_proxima_release,
        })
    
    return pd.DataFrame(dados)
