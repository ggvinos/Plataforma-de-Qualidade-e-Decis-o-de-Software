# 📋 Relatório de Qualidade de Código - NinaDash

**Data:** 23/04/2026  
**Versão Analisada:** v8.82  
**Analista:** GitHub Copilot (QA Automatizado)

---

## 📊 Resumo Executivo

| Categoria | Status | Score |
|-----------|--------|-------|
| Estrutura de Testes | 🔴 Crítico | 25/100 |
| Qualidade de Código | 🟡 Atenção | 60/100 |
| Cobertura de Testes | 🔴 Crítico | 15/100 |
| Documentação | 🟢 Bom | 75/100 |
| Arquitetura | 🟡 Atenção | 55/100 |

**Score Geral: 46/100** 🟠

---

## 🔴 PROBLEMAS CRÍTICOS

### 1. Imports Faltando no app_modularizado.py

**Arquivo:** [app_modularizado.py](../app_modularizado.py#L331)

```python
# ERRO: Funções usadas mas não importadas
get_cookie_manager()       # Não importado
COOKIE_CONSULTAS_NAME      # Não definido
```

**Correção Necessária:**
```python
from modulos.confirmation_call_auth import (
    verificar_e_bloquear,
    renderizar_logout_sidebar,
    obter_usuario_autenticado,
    get_cookie_manager,  # ADICIONAR
)

# Definir no arquivo:
COOKIE_CONSULTAS_NAME = "ninadash_consultas_salvas"
```

### 2. Ausência de Framework de Testes

**Problema:** Não há pytest, unittest ou coverage instalados.

**Impacto:**
- Scripts de teste são manuais, não automatizados
- Sem cobertura de código
- Sem CI/CD possível
- Regressões passam despercebidas

**Solução:**
```bash
pip install pytest pytest-cov pytest-mock
```

### 3. Arquivos Muito Grandes (God Objects)

| Arquivo | Linhas | Status |
|---------|--------|--------|
| `modulos/_abas_legacy.py` | 5.206 | 🔴 Crítico |
| `modulos/cards.py` | 2.284 | 🔴 Alto |
| `modulos/calculos.py` | 1.517 | 🟡 Médio |
| `modulos/widgets.py` | 988 | 🟡 Médio |

**Recomendação:** Dividir em módulos menores (< 500 linhas por arquivo).

---

## 🟡 PROBLEMAS DE ATENÇÃO

### 4. Exception Handling Genérico

**50+ ocorrências** de tratamento de exceção inadequado:

```python
# ❌ RUIM - Esconde erros
try:
    # código
except:
    pass

# ❌ RUIM - Muito genérico
except Exception as e:
    pass

# ✅ BOM - Específico e logado
except ValueError as e:
    logger.warning(f"Valor inválido: {e}")
    return valor_default
```

**Arquivos mais afetados:**
- `modulos/confirmation_call_auth.py` - 12 ocorrências
- `modulos/calculos.py` - 11 ocorrências
- `modulos/helpers.py` - 7 ocorrências

### 5. Falta de Type Hints Consistentes

Muitas funções têm type hints parciais ou ausentes:

```python
# ❌ Atual
def calcular_dados_grafico(metrica_key: str, df: pd.DataFrame):
    # ...
    return None  # Tipo de retorno não especificado

# ✅ Recomendado
def calcular_dados_grafico(metrica_key: str, df: pd.DataFrame) -> Optional[pd.Series]:
    """Docstring com tipos documentados."""
    ...
```

### 6. Funções Duplicadas

Código duplicado identificado:
- `aba_backlog()` existe em `abas.py` E `_abas_legacy.py`
- `filtrar_matriz()` definida múltiplas vezes inline
- Lógica de link Jira repetida em vários módulos

---

## 📈 ANÁLISE DOS TESTES EXISTENTES

### Estrutura Atual (/tests/)

| Arquivo | Tipo | Cobertura |
|---------|------|-----------|
| `DEBUG_COLUMNS.py` | Debug script | N/A |
| `test_backlog_fix.py` | Validação manual | Parcial |
| `test_cc_connection.py` | Teste conexão | API externa |
| `test_cc_dev.py` | Teste interativo | Manual |
| `test_confirmation_call_auth.py` | Smoke test | Básico |
| `test_jwt_fix.py` | Validação JWT | Específico |
| `test_pb_fix.py` | Teste estrutura | Imports |
| `test_phase15.py` | E2E parcial | Imports |

### Problemas Identificados

1. **Não são testes automatizados** - Scripts manuais com `print()`
2. **Sem assertions padronizadas** - Uso de `if` ao invés de `assert`
3. **Sem fixtures ou mocks** - Dependem de API real
4. **Sem isolamento** - Testes podem afetar uns aos outros

### Exemplo de Teste Atual vs Recomendado

```python
# ❌ ATUAL (test_backlog_fix.py)
print("✅ Function returns all required keys")
if missing_keys:
    print(f"❌ Missing keys: {missing_keys}")
    sys.exit(1)

# ✅ RECOMENDADO (usando pytest)
import pytest
from modulos.calculos import calcular_metricas_backlog

def test_calcular_metricas_backlog_returns_all_keys():
    df = create_sample_df()  # fixture
    metricas = calcular_metricas_backlog(df)
    
    required_keys = ['score_saude', 'status_saude', 'total_itens']
    for key in required_keys:
        assert key in metricas, f"Missing key: {key}"
```

---

## 🔍 EDGE CASES NÃO COBERTOS

### 1. DataFrames Vazios
```python
# Funções que podem falhar com df vazio:
- calcular_concentracao_conhecimento()
- calcular_metricas_backlog()
- calcular_lead_time()

# Verificação necessária:
if df.empty:
    return resultado_vazio_padrao
```

### 2. Valores None/NaN
```python
# Campos que podem ser None:
- card['desenvolvedor']
- card['qa']
- card['produto']

# Tratamento necessário:
desenvolvedor = card.get('desenvolvedor') or 'Não atribuído'
```

### 3. Conexão com API
```python
# Sem tratamento para:
- Timeout de conexão
- Rate limiting do Jira
- Token JWT expirado
- Credenciais inválidas (parcial)
```

### 4. Dados Malformados
```python
# Campos esperados mas que podem estar ausentes:
- customfield_* do Jira
- Datas em formato incorreto
- Sprints sem formato padrão
```

---

## ✅ RECOMENDAÇÕES DE MELHORIAS

### Prioridade Alta (Implementar Imediatamente)

1. **Corrigir imports em app_modularizado.py**
   - Adicionar `get_cookie_manager` ao import
   - Definir `COOKIE_CONSULTAS_NAME`

2. **Instalar pytest e configurar CI**
   ```bash
   pip install pytest pytest-cov pytest-mock
   ```

3. **Criar arquivo conftest.py com fixtures**

### Prioridade Média (Próximas Sprints)

4. **Refatorar arquivos grandes**
   - Dividir `_abas_legacy.py` em módulos por aba
   - Extrair lógica de `cards.py` para `card_renderer.py`

5. **Melhorar exception handling**
   - Substituir `except:` por exceções específicas
   - Adicionar logging em vez de `pass`

6. **Adicionar validação de entrada**
   - Verificar DataFrames vazios
   - Validar campos obrigatórios

### Prioridade Baixa (Dívida Técnica)

7. **Completar type hints**
8. **Remover código duplicado**
9. **Adicionar docstrings completas**

---

## 📁 ESTRUTURA DE TESTES RECOMENDADA

```
tests/
├── __init__.py
├── conftest.py              # Fixtures globais
├── unit/
│   ├── __init__.py
│   ├── test_calculos.py     # Testes de cálculos
│   ├── test_utils.py        # Testes de utilidades
│   ├── test_helpers.py      # Testes de helpers
│   └── test_processamento.py
├── integration/
│   ├── __init__.py
│   ├── test_jira_api.py     # Testes com mock de API
│   └── test_auth.py         # Testes de autenticação
└── e2e/
    ├── __init__.py
    └── test_dashboard.py    # Testes end-to-end
```

---

## 📝 EXEMPLO DE CONFTEST.PY

```python
import pytest
import pandas as pd
from datetime import datetime, timedelta

@pytest.fixture
def sample_df():
    """DataFrame de exemplo para testes."""
    return pd.DataFrame({
        'ticket_id': ['SD-1', 'SD-2', 'SD-3'],
        'titulo': ['Task 1', 'Task 2', 'Task 3'],
        'status': ['DONE', 'IN_PROGRESS', 'BACKLOG'],
        'status_categoria': ['done', 'development', 'backlog'],
        'desenvolvedor': ['Dev1', 'Dev2', 'Dev1'],
        'qa': ['QA1', 'QA1', 'Não atribuído'],
        'sp': [5, 3, 8],
        'bugs': [0, 1, 0],
        'produto': ['Prod1', 'Prod1', 'Prod2'],
        'criado': [datetime.now() - timedelta(days=d) for d in [10, 5, 2]],
        'lead_time': [10, 5, 0],
    })

@pytest.fixture
def empty_df():
    """DataFrame vazio para testes de edge case."""
    return pd.DataFrame()

@pytest.fixture
def mock_jira_response():
    """Mock de resposta da API Jira."""
    return {
        'issues': [
            {'key': 'SD-1', 'fields': {'summary': 'Test'}}
        ]
    }
```

---

## 📊 MÉTRICAS DE QUALIDADE SUGERIDAS

| Métrica | Valor Atual | Meta |
|---------|-------------|------|
| Cobertura de Testes | ~5% | > 70% |
| Complexidade Ciclomática | Alta | Média |
| Duplicação de Código | ~15% | < 5% |
| Type Hint Coverage | ~40% | > 90% |
| Docstring Coverage | ~60% | > 80% |

---

## 🚀 PRÓXIMOS PASSOS

1. [ ] Corrigir erros de import críticos
2. [ ] Instalar pytest e criar primeiros testes
3. [ ] Adicionar testes para funções de cálculo
4. [ ] Configurar GitHub Actions para CI
5. [ ] Refatorar `_abas_legacy.py`
6. [ ] Implementar logging estruturado
7. [ ] Adicionar validação de dados de entrada

---

*Relatório gerado automaticamente - GitHub Copilot QA*
