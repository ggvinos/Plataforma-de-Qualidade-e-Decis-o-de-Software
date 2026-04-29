"""
================================================================================
MÓDULO DE ABAS - NinaDash v8.82
================================================================================
Subpacote contendo abas divididas por funcionalidade.

Estrutura:
- visao_geral.py: aba_visao_geral()
- dev.py: aba_dev()
- qa.py: aba_qa()
- backlog.py: aba_backlog()
- clientes.py: aba_clientes()
- governanca.py: aba_governanca()
- historico.py: aba_historico()
- lideranca.py: aba_lideranca()
- produto.py: aba_produto()
- sobre.py: aba_sobre()
- suporte.py: aba_suporte_implantacao()

Todas as funções são re-exportadas aqui para manter compatibilidade
com imports existentes no app_modularizado.py.
"""

# Funções extraídas para arquivos separados
from modulos.abas.visao_geral import aba_visao_geral
from modulos.abas.visao_geral_v2 import aba_visao_geral_v2  # Nova versão orientada a decisão
from modulos.abas.central_decisao import aba_central_decisao  # Central de Decisão
from modulos.abas.dev import aba_dev
from modulos.abas.qa import aba_qa
from modulos.abas.backlog import aba_backlog, aba_produto_pb, aba_historico_pb
from modulos.abas.clientes import aba_clientes
from modulos.abas.governanca import aba_governanca
from modulos.abas.historico import aba_historico
from modulos.abas.lideranca import aba_lideranca
from modulos.abas.produto import aba_produto
from modulos.abas.sobre import aba_sobre
from modulos.abas.suporte import aba_suporte_implantacao
from modulos.abas.admin import aba_admin  # Painel Administrativo

# Funções que permanecem no arquivo legacy (usadas por múltiplas abas)
from modulos._abas_legacy import (
    exibir_historico_validacoes,
)

__all__ = [
    'aba_visao_geral',
    'aba_visao_geral_v2',
    'aba_central_decisao',
    'aba_admin',
    'aba_backlog',
    'aba_clientes',
    'aba_dev',
    'aba_governanca',
    'aba_historico',
    'aba_historico_pb',
    'aba_lideranca',
    'aba_produto',
    'aba_produto_pb',
    'aba_qa',
    'aba_sobre',
    'aba_suporte_implantacao',
    'exibir_historico_validacoes',
]
