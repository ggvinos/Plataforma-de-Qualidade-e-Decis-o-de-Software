"""
================================================================================
MÓDULO DE PROCESSAMENTO - NinaDash v8.82
================================================================================
Contém funções de processamento de dados e aplicação de filtros.

Responsabilidades:
- Cálculo de períodos de data
- Aplicação de filtros a DataFrames
- Processamento de consultas personalizadas

Dependências:
- pandas (para DataFrames)
- datetime (para datas)
- modulos.utils (link_jira se necessário)
- modulos.config (constantes)

Author: GitHub Copilot
Version: 1.0 (Phase 5)
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Tuple, Any

from modulos.config import STATUS_FLOW


# ==============================================================================
# PROCESSAMENTO DE PERÍODOS E DATAS
# ==============================================================================

def calcular_periodo_datas(
    periodo: str,
    data_inicio_custom: datetime = None,
    data_fim_custom: datetime = None
) -> Tuple[datetime, datetime]:
    """
    Calcula as datas de início e fim baseado no período selecionado.
    
    Períodos suportados:
    - sprint_atual: últimas 2 semanas
    - ultima_semana: últimos 7 dias
    - ultimas_2_semanas: últimos 14 dias
    - ultimo_mes: últimos 30 dias
    - ultimos_3_meses: últimos 90 dias
    - todo_periodo: últimos 5 anos
    - personalizado: data_inicio_custom até data_fim_custom
    
    Args:
        periodo: Tipo de período a calcular
        data_inicio_custom: Data início para período personalizado
        data_fim_custom: Data fim para período personalizado
    
    Returns:
        Tuple (data_inicio, data_fim) como datetime
    """
    hoje = datetime.now()
    
    if periodo == "sprint_atual":
        return hoje - timedelta(days=14), hoje
    elif periodo == "ultima_semana":
        return hoje - timedelta(days=7), hoje
    elif periodo == "ultimas_2_semanas":
        return hoje - timedelta(days=14), hoje
    elif periodo == "ultimo_mes":
        return hoje - timedelta(days=30), hoje
    elif periodo == "ultimos_3_meses":
        return hoje - timedelta(days=90), hoje
    elif periodo == "todo_periodo":
        return hoje - timedelta(days=365*5), hoje  # 5 anos
    elif periodo == "personalizado" and data_inicio_custom and data_fim_custom:
        return data_inicio_custom, data_fim_custom
    else:
        # Default: último mês
        return hoje - timedelta(days=30), hoje


# ==============================================================================
# FILTROS DE DATAFRAMES
# ==============================================================================

def filtrar_df_por_consulta(df: pd.DataFrame, tipo: str, filtros: Dict) -> pd.DataFrame:
    """
    Filtra o DataFrame baseado nos filtros da consulta.
    
    Suporta filtros por:
    - Período (data_criacao)
    - Pessoa (responsável, QA, relator)
    - Status
    - Produto
    
    Args:
        df: DataFrame com os cards
        tipo: Tipo de consulta (não usado diretamente, apenas para contexto)
        filtros: Dict com filtros a aplicar
    
    Returns:
        DataFrame filtrado
    """
    df_filtrado = df.copy()
    
    # Filtro por período
    if filtros.get('periodo') and filtros['periodo']:
        data_inicio, data_fim = calcular_periodo_datas(
            filtros['periodo'],
            filtros.get('data_inicio'),
            filtros.get('data_fim')
        )
        
        # Tenta usar campo criado se existe
        if 'criado' in df_filtrado.columns:
            df_filtrado['data_criacao_dt'] = pd.to_datetime(df_filtrado['criado'], errors='coerce')
            df_filtrado['data_criacao_dt'] = df_filtrado['data_criacao_dt'].dt.tz_localize(None)
            df_filtrado = df_filtrado[
                (df_filtrado['data_criacao_dt'] >= data_inicio) & 
                (df_filtrado['data_criacao_dt'] <= data_fim)
            ]
    
    # Filtro por pessoa
    if filtros.get('pessoa') and filtros['pessoa'] != "Todos":
        pessoa = filtros['pessoa']
        papel = filtros.get('papel_pessoa', 'qualquer')
        
        if papel == 'desenvolvedor':
            df_filtrado = df_filtrado[
                df_filtrado['desenvolvedor'].str.contains(pessoa, case=False, na=False)
            ]
        elif papel == 'qa':
            df_filtrado = df_filtrado[
                df_filtrado['qa'].str.contains(pessoa, case=False, na=False)
            ]
        elif papel == 'relator':
            df_filtrado = df_filtrado[
                df_filtrado['relator'].str.contains(pessoa, case=False, na=False)
            ]
        else:  # qualquer papel
            df_filtrado = df_filtrado[
                df_filtrado['desenvolvedor'].str.contains(pessoa, case=False, na=False) |
                df_filtrado['qa'].str.contains(pessoa, case=False, na=False) |
                df_filtrado['relator'].str.contains(pessoa, case=False, na=False)
            ]
    
    # Filtro por status
    if filtros.get('status') and filtros['status'] != "todos":
        status_map = {
            "concluido": ["done"],
            "em_andamento": ["in_progress"],
            "em_validacao": ["testing"],
            "aguardando_qa": ["waiting_qa"],
            "code_review": ["code_review"],
            "impedido": ["blocked"],
            "reprovado": ["rejected"],
            "backlog": ["backlog"],
        }
        categorias = status_map.get(filtros['status'], [])
        if categorias and 'status_cat' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['status_cat'].isin(categorias)]
    
    # Filtro por produto
    if filtros.get('produto') and filtros['produto'] != "Todos":
        if 'produto' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['produto'] == filtros['produto']]
    
    return df_filtrado


def aplicar_filtros_widget(df: pd.DataFrame, filtros: Dict) -> pd.DataFrame:
    """
    Aplica filtros ao DataFrame para um widget específico.
    
    Versão simplificada de filtrar_df_por_consulta, focada em widgets.
    
    Args:
        df: DataFrame com os cards
        filtros: Dict com filtros a aplicar
    
    Returns:
        DataFrame filtrado
    """
    df_filtrado = df.copy()
    
    # Filtro por período
    if filtros.get('periodo'):
        data_inicio, data_fim = calcular_periodo_datas(
            filtros['periodo'],
            filtros.get('data_inicio'),
            filtros.get('data_fim')
        )
        
        if 'criado' in df_filtrado.columns:
            try:
                df_filtrado['data_criacao_dt'] = pd.to_datetime(
                    df_filtrado['criado'],
                    errors='coerce'
                )
                df_filtrado['data_criacao_dt'] = df_filtrado['data_criacao_dt'].dt.tz_localize(None)
                df_filtrado = df_filtrado[
                    (df_filtrado['data_criacao_dt'] >= data_inicio) & 
                    (df_filtrado['data_criacao_dt'] <= data_fim)
                ]
            except Exception:
                # Se algo der errado com datas, continua sem filtrar
                pass
    
    # Filtro por pessoa
    if filtros.get('pessoa') and filtros['pessoa'] != 'Todos':
        pessoa = filtros['pessoa']
        papel = filtros.get('papel_pessoa', 'qualquer')
        
        try:
            if papel == 'desenvolvedor' and 'desenvolvedor' in df_filtrado.columns:
                df_filtrado = df_filtrado[
                    df_filtrado['desenvolvedor'].str.contains(pessoa, case=False, na=False)
                ]
            elif papel == 'qa' and 'qa' in df_filtrado.columns:
                df_filtrado = df_filtrado[
                    df_filtrado['qa'].str.contains(pessoa, case=False, na=False)
                ]
            elif papel == 'relator' and 'relator' in df_filtrado.columns:
                df_filtrado = df_filtrado[
                    df_filtrado['relator'].str.contains(pessoa, case=False, na=False)
                ]
            else:  # qualquer papel
                condicoes = []
                if 'desenvolvedor' in df_filtrado.columns:
                    condicoes.append(
                        df_filtrado['desenvolvedor'].str.contains(pessoa, case=False, na=False)
                    )
                if 'qa' in df_filtrado.columns:
                    condicoes.append(
                        df_filtrado['qa'].str.contains(pessoa, case=False, na=False)
                    )
                if 'relator' in df_filtrado.columns:
                    condicoes.append(
                        df_filtrado['relator'].str.contains(pessoa, case=False, na=False)
                    )
                
                if condicoes:
                    df_filtrado = df_filtrado[
                        condicoes[0] if len(condicoes) == 1 
                        else (condicoes[0] | condicoes[1]) if len(condicoes) == 2
                        else (condicoes[0] | condicoes[1] | condicoes[2])
                    ]
        except Exception:
            # Se algo der errado com filtro de pessoa, continua sem filtrar
            pass
    
    # Filtro por status
    if filtros.get('status') and filtros['status'] != 'todos':
        status_map = {
            "concluido": ["done"],
            "em_andamento": ["in_progress"],
            "em_validacao": ["testing"],
            "aguardando_qa": ["waiting_qa"],
            "code_review": ["code_review"],
            "impedido": ["blocked"],
            "reprovado": ["rejected"],
            "backlog": ["backlog"],
        }
        categorias = status_map.get(filtros['status'], [])
        if categorias and 'status_cat' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['status_cat'].isin(categorias)]
    
    # Filtro por projeto
    if filtros.get('projeto') and filtros['projeto'] != 'Todos':
        if 'projeto' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['projeto'] == filtros['projeto']]
    
    # Filtro por produto
    if filtros.get('produto') and filtros['produto'] != 'Todos':
        if 'produto' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['produto'] == filtros['produto']]
    
    return df_filtrado


# ==============================================================================
# PROCESSAMENTO DE DADOS AGREGADO
# ==============================================================================

def preparar_df_com_metricas_filtro(
    df: pd.DataFrame,
    filtros: Dict
) -> Dict[str, Any]:
    """
    Prepara um DataFrame aplicando filtros e calculando métricas básicas.
    
    Útil para dashboards que precisam aplicar filtros e mostrar métricas resumidas.
    
    Args:
        df: DataFrame com os cards
        filtros: Dict com filtros a aplicar
    
    Returns:
        Dict com 'df' (filtrado) e 'metricas' (resumo)
    """
    df_filtrado = aplicar_filtros_widget(df, filtros)
    
    metricas = {
        'total': len(df_filtrado),
        'sp_total': int(df_filtrado['sp'].sum()) if 'sp' in df_filtrado.columns else 0,
        'bugs_total': int(df_filtrado['bugs'].sum()) if 'bugs' in df_filtrado.columns else 0,
        'concluidos': len(df_filtrado[df_filtrado['status_cat'] == 'done']) if 'status_cat' in df_filtrado.columns else 0,
    }
    
    return {
        'df': df_filtrado,
        'metricas': metricas,
        'vazio': df_filtrado.empty
    }


def validar_filtros(filtros: Dict) -> bool:
    """
    Valida se os filtros estão em formato correto.
    
    Args:
        filtros: Dict com filtros
    
    Returns:
        True se filtros válidos, False caso contrário
    """
    if not isinstance(filtros, dict):
        return False
    
    # Verifica chaves obrigatórias (nenhuma neste caso - tudo é opcional)
    # Mas valida tipos se as chaves existem
    tipos_esperados = {
        'periodo': str,
        'pessoa': str,
        'papel_pessoa': str,
        'status': str,
        'produto': str,
        'projeto': str,
    }
    
    for chave, tipo_esperado in tipos_esperados.items():
        if chave in filtros and filtros[chave] is not None:
            if not isinstance(filtros[chave], tipo_esperado):
                return False
    
    return True


def resetar_filtros() -> Dict:
    """
    Retorna um Dict com filtros resetados (padrão).
    
    Returns:
        Dict com filtros padrão
    """
    return {
        'periodo': 'ultimo_mes',
        'pessoa': 'Todos',
        'papel_pessoa': 'qualquer',
        'status': 'todos',
        'produto': 'Todos',
        'projeto': 'Todos',
    }
