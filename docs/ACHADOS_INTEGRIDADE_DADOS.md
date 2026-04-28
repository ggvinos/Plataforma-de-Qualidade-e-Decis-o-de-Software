# Achados da Verificação de Integridade de Dados

**Data:** 28/04/2026  
**Analista:** GitHub Copilot

## Status Atual do Jira (Dados Reais)

### Sprint Atual
- **Nome:** 238
- **State:** active (porém terminou há 14 dias!)
- **startDate:** 2026-03-31T16:29:01.438Z
- **endDate:** 2026-04-14T16:29:57.000Z (14 dias atrás)

### Sprint Futura Aguardando
- **Nome:** 239
- **State:** future
- **startDate:** 2026-04-14T03:00:00.000Z
- **endDate:** 2026-04-28T03:00:00.000Z

### Cards na Sprint 238
| Status | Quantidade |
|--------|------------|
| Concluído | 33 |
| AGUARDANDO VALIDAÇÃO | 11 |
| Tarefas pendentes | 9 |
| EM REVISÃO | 7 |
| Em andamento | 7 |
| IMPEDIDO | 5 |
| EM VALIDAÇÃO | 4 |
| Validado-Adiado | 3 |
| REPROVADO | 2 |
| **TOTAL** | **81** |

---

## 🐛 BUG CRÍTICO: Detecção de "VIRAR SPRINT" não funciona

### Problema
O dashboard deveria mostrar "⚠️ VIRAR SPRINT NO JIRA" quando:
1. Sprint atual está vencida (dias_restantes < 0) ✅
2. Existe sprint futura com startDate <= hoje ❌ **NUNCA DETECTADO**

### Causa Raiz
**Arquivo:** [visao_geral_v2.py](../modulos/abas/visao_geral_v2.py#L903-924)
```python
# Esta verificação nunca encontra nada:
if 'sprint_state' in df.columns:
    df_future = df[df['sprint_state'] == 'future']  # SEMPRE VAZIO!
```

**Motivo:** A query JQL em [app_develop.py](../app_develop.py#L995) usa:
```python
jql = f'project = {projeto} AND sprint in openSprints() ORDER BY created DESC'
```

Isso busca APENAS sprints ativas (state=active), nunca futuras (state=future).

### Impacto
- Dashboard sempre mostra "🚨 RELEASE ATRASADA" mesmo quando existe sprint futura pronta
- Usuário não recebe a indicação correta de que precisa "virar a sprint" no Jira

### Solução Proposta
**Opção A (Recomendada):** Adicionar busca separada de sprint futura
```python
# Em jira_api.py ou consultas.py
def verificar_sprint_futura(projeto):
    """Verifica se existe sprint futura aguardando início"""
    jql = f'project = {projeto} AND sprint in futureSprints() ORDER BY created DESC'
    # Busca limitada (apenas 1 card) para detectar existência
    ...
```

**Opção B:** Modificar JQL para incluir futuras
```python
jql = f'project = {projeto} AND (sprint in openSprints() OR sprint in futureSprints()) ORDER BY created DESC'
```
⚠️ Pode aumentar volume de dados significativamente.

---

## ✅ Validações que Passaram

### 1. Conexão com Jira
- API Atlassian acessível via MCP tools
- CloudId: f69e5df8-ff11-4899-8fe9-804b46f84c82
- Queries JQL funcionando

### 2. Processamento de Dados de Sprint
**Arquivo:** [calculos.py](../modulos/calculos.py#L1340-1370)
- ✅ Extração correta de sprint_state
- ✅ Extração correta de sprint_start/sprint_end
- ✅ Parsing de datas ISO com timezone

### 3. Estrutura de Dados do Card
Campos mapeados corretamente:
- `customfield_10020` → Sprint (array com histórico)
- Status name extraído de `fields.status.name`
- Prioriza sprint com state='active'

---

## 📊 Testes Automatizados Criados

### [test_integridade_dados.py](../tests/test_integridade_dados.py)
- `test_imports` ✅
- `test_conexao_jira` ✅ (com skip se sem credenciais)
- `test_contagem_status` ⚠️ (variação por dados em tempo real)
- `test_sprint_info` ✅
- `test_processamento_issues` ✅

### [test_calculos.py](../tests/unit/test_calculos.py)
- 28 testes passando
- Cobertura de todas as funções de cálculo

### [test_utils.py](../tests/unit/test_utils.py)
- 22 testes passando
- Cobertura de funções utilitárias

---

## 🎯 Recomendações de Ação

### Urgente (Sprint Atual)
1. **MANUAL:** Virar a sprint 238→239 no Jira
2. **FIX:** Implementar detecção correta de sprint futura

### Curto Prazo
3. Adicionar teste de integração que valida detecção de sprint futura
4. Aumentar cobertura de testes para >70%

### Médio Prazo
5. Refatorar módulo calculos.py (1600+ linhas)
6. Remover `except: pass` (50+ ocorrências)
