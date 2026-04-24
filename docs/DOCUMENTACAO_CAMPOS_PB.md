# 📊 DOCUMENTAÇÃO COMPLETA - NinaDash PB (Product Backlog)

> **Objetivo deste documento:** Mapear todos os campos, métricas e informações da aba PB do dashboard para análise de gargalos, saúde do backlog e suporte à tomada de decisão de priorização.

---

## 📌 OBJETIVO DA ABA PB

A aba **Product Backlog** foi criada para responder às seguintes perguntas:

1. **Qual o tamanho do nosso backlog?** → Volume e Story Points pendentes
2. **O backlog está saudável ou engargalado?** → Aging, taxa de crescimento
3. **Quais itens estão "esquecidos"?** → Cards antigos sem movimentação
4. **A priorização está funcionando?** → Distribuição por prioridade
5. **Quanto tempo leva para um item sair do backlog?** → Lead Time de backlog
6. **Temos capacidade para resolver o backlog atual?** → Projeção de sprints

---

## 📌 CAMPOS JIRA UTILIZADOS (FONTE DE DADOS)

| Campo Jira | Custom Field ID | Obrigatoriedade | Descrição | Usado em |
|------------|-----------------|-----------------|-----------|----------|
| **Story Points** | `customfield_11257` / `customfield_10016` | Obrigatório | Esforço estimado do card | Tamanho Backlog, Projeções |
| **Sprint** | `customfield_10020` | Automático | Sprint atribuída | Identificar itens não planejados |
| **Status** | Campo nativo | Automático | Estado atual do card | Distribuição, Aging |
| **Prioridade** | Campo nativo | Automático | Alta, Média, Baixa | Alertas, Priorização |
| **Produto** | `customfield_10102` | Obrigatório | Produto ao qual pertence | Segmentação |
| **Responsável** | Campo nativo | Automático | Desenvolvedor atribuído | Cards órfãos |
| **Data Criação** | Campo nativo | Automático | Quando foi criado | Aging, Lead Time |
| **Data Atualização** | Campo nativo | Automático | Última movimentação | Cards estagnados |
| **Tipo** | Campo nativo | Automático | TAREFA, BUG, HOTFIX, SUGESTÃO | Distribuição |

---

## 📑 SEÇÕES DA ABA PB

---

# 1️⃣ SAÚDE DO BACKLOG

**Objetivo:** Fornecer uma visão rápida da saúde geral do backlog com indicadores-chave.

### 1.1 KPIs Principais (Expandível)

| Métrica | Fórmula/Cálculo | Fonte | Objetivo | Criticidade |
|---------|-----------------|-------|----------|-------------|
| **Total de Itens** | Contagem de cards no backlog | Status = backlog | Volume total | Alta |
| **Story Points Pendentes** | Soma de SP no backlog | SP + Status | Esforço pendente | Alta |
| **Idade Média (dias)** | Média (hoje - data_criacao) | Datas | Saúde do fluxo | Alta |
| **% Sem Estimativa** | Cards sem SP / Total × 100 | SP | Qualidade do refinamento | Média |
| **% Sem Responsável** | Cards não atribuídos / Total × 100 | Responsável | Cards órfãos | Média |

### 1.2 Indicador de Saúde do Backlog

| Score | Critérios | Status | Ação |
|-------|-----------|--------|------|
| 🟢 Saudável | Idade média ≤ 30 dias, crescimento ≤ 10% | OK | Manter ritmo |
| 🟡 Atenção | Idade média 31-60 dias OU crescimento 11-25% | Monitorar | Revisar priorização |
| 🟠 Alerta | Idade média 61-90 dias OU crescimento 26-50% | Ação | Grooming urgente |
| 🔴 Crítico | Idade média > 90 dias OU crescimento > 50% | Crítico | Reavaliação completa |

---

# 2️⃣ ANÁLISE DE AGING (ENVELHECIMENTO)

**Objetivo:** Identificar itens que estão há muito tempo no backlog sem movimentação.

### 2.1 Distribuição por Faixas de Idade (Gráfico)

| Faixa | Descrição | Cor | Ação Recomendada |
|-------|-----------|-----|------------------|
| **0-15 dias** | Recém-criados | Verde | Normal |
| **16-30 dias** | Aguardando priorização | Amarelo | Revisar na próxima sprint |
| **31-60 dias** | Atrasados | Laranja | Avaliar relevância |
| **61-90 dias** | Críticos | Vermelho | Decidir: fazer ou descartar |
| **>90 dias** | Abandonados | Vermelho escuro | Candidatos a descarte |

### 2.2 Cards Aging (Expandível + Listagem)

| Campo | Descrição | Criticidade |
|-------|-----------|-------------|
| Ticket ID | Link clicável para Jira | Alta |
| Título | Descrição do card | Média |
| Dias no Backlog | Idade em dias | Alta |
| Prioridade | Alta/Média/Baixa | Alta |
| Produto | Produto relacionado | Média |
| SP | Story Points | Média |
| Último Update | Data última movimentação | Alta |

### 2.3 Métricas de Aging

| Métrica | Fórmula | Objetivo |
|---------|---------|----------|
| **Idade Mediana** | Mediana dos dias de criação | Visão menos influenciada por outliers |
| **Cards > 60 dias** | Contagem | Identificar acúmulo |
| **Cards > 90 dias** | Contagem | Candidatos a descarte |
| **Mais Antigo** | Max (idade) | Pior caso |

---

# 3️⃣ FLUXO DE ENTRADA E SAÍDA

**Objetivo:** Entender se o backlog está crescendo, estável ou diminuindo.

### 3.1 Taxa de Crescimento (Gráfico de Linha)

| Métrica | Fórmula | Interpretação |
|---------|---------|---------------|
| **Taxa de Entrada** | Cards criados / período | Demanda nova |
| **Taxa de Saída** | Cards saindo do backlog / período | Capacidade de execução |
| **Taxa de Crescimento** | (Entrada - Saída) / Entrada × 100 | Positivo = crescendo, Negativo = diminuindo |

### 3.2 Projeção de Resolução

| Métrica | Fórmula | Objetivo |
|---------|---------|----------|
| **Velocidade Média** | SP concluídos / sprint | Capacidade do time |
| **SP no Backlog** | Soma de SP | Esforço pendente |
| **Sprints para Zerar** | SP backlog / Velocidade média | Previsibilidade |
| **Cards/Sprint** | Média de cards concluídos | Throughput |

### 3.3 Indicadores de Fluxo

| Indicador | Interpretação |
|-----------|---------------|
| 📈 Backlog Crescendo | Entrada > Saída - Risco de acúmulo |
| ➡️ Backlog Estável | Entrada ≈ Saída - Equilíbrio saudável |
| 📉 Backlog Diminuindo | Entrada < Saída - Time absorvendo dívida |

---

# 4️⃣ PRIORIZAÇÃO E DISTRIBUIÇÃO

**Objetivo:** Validar se a priorização está equilibrada e coerente.

### 4.1 Distribuição por Prioridade (Gráfico Pizza)

| Prioridade | Benchmark Recomendado | Alerta se |
|------------|----------------------|-----------|
| **Crítica/Bloqueante** | ≤ 5% | > 10% |
| **Alta** | 15-25% | > 40% |
| **Média** | 40-60% | < 30% |
| **Baixa** | 15-30% | < 10% (itens pequenos deveriam existir) |

### 4.2 Alertas de Priorização

| Alerta | Critério | Ação |
|--------|----------|------|
| 🚨 **Muitos itens críticos** | > 10% críticos | Reavaliar o que é realmente crítico |
| ⚠️ **Alta prioridade represada** | Alta + idade > 30 dias | Priorizar ou rebaixar |
| ℹ️ **Backlog desequilibrado** | Distribuição fora do benchmark | Revisar critérios de prioridade |

### 4.3 Distribuição por Tipo (Gráfico)

| Tipo | Descrição | Benchmark |
|------|-----------|-----------|
| **TAREFA** | Novas funcionalidades | 50-60% |
| **BUG** | Correções de defeitos | 15-25% |
| **SUGESTÃO** | Melhorias propostas | 10-20% |
| **HOTFIX** | Não deveria estar no backlog | < 5% |

### 4.4 Distribuição por Produto (Gráfico)

| Visualização | Objetivo |
|--------------|----------|
| Barras empilhadas | Ver concentração por produto |
| Cards/SP por produto | Identificar produtos com mais demanda |

---

# 5️⃣ CARDS ÓRFÃOS E PROBLEMÁTICOS

**Objetivo:** Identificar itens que precisam de atenção especial.

### 5.1 Cards Sem Sprint (Não Planejados)

| Campo | Descrição |
|-------|-----------|
| Total | Quantidade de cards sem sprint atribuída |
| Lista | Tabela com detalhes |
| Alerta | Cards com alta prioridade sem planejamento |

### 5.2 Cards Sem Responsável

| Campo | Descrição |
|-------|-----------|
| Total | Cards não atribuídos |
| Risco | Ninguém "dono" do item |

### 5.3 Cards Sem Estimativa (SP)

| Campo | Descrição |
|-------|-----------|
| Total | Cards sem Story Points |
| Impacto | Impossível calcular capacidade |

### 5.4 Cards Estagnados

| Critério | Descrição |
|----------|-----------|
| **Definição** | Cards que não foram atualizados há > 30 dias |
| **Risco** | Podem estar esquecidos ou bloqueados |
| **Ação** | Verificar se ainda são relevantes |

---

# 6️⃣ VISÃO POR PRODUTO

**Objetivo:** Segmentar o backlog por produto para análise específica.

### 6.1 Resumo por Produto (Tabela)

| Campo | Descrição |
|-------|-----------|
| Produto | Nome do produto |
| Total Cards | Quantidade de itens |
| SP Pendentes | Story Points no backlog |
| Idade Média | Dias médios |
| % Críticos | Alta + Crítica prioridade |
| Cards > 60 dias | Itens envelhecidos |

### 6.2 Gráfico Comparativo

| Visualização | Objetivo |
|--------------|----------|
| Barras | Comparar tamanho do backlog por produto |
| Treemap | Visualizar proporção |

---

# 7️⃣ RECOMENDAÇÕES AUTOMÁTICAS

**Objetivo:** Gerar insights acionáveis com base nos dados.

### 7.1 Tipos de Recomendações

| Tipo | Gatilho | Recomendação |
|------|---------|--------------|
| 🗑️ **Candidatos a Descarte** | Idade > 90 dias + Baixa prioridade | "Considere descartar estes X itens" |
| 📅 **Revisar Prioridade** | Alta prioridade + > 30 dias | "X itens de alta prioridade estão parados há mais de 30 dias" |
| 📝 **Refinar Backlog** | > 20% sem SP | "X% do backlog não tem estimativa" |
| 👤 **Atribuir Responsável** | Sem dono + Alta prioridade | "X itens prioritários não têm responsável" |
| ⚡ **Grooming Urgente** | Backlog crescendo > 25% | "Backlog cresceu X% - agende grooming" |

---

## 📊 RESUMO DE CRITICIDADE DOS CAMPOS

### CAMPOS ALTA CRITICIDADE (Essenciais para PB)

| Campo | Usado em | Impacto se ausente |
|-------|----------|-------------------|
| **Status** | Identificar backlog | Impossível filtrar |
| **Data Criação** | Aging, Fluxo | Sem métricas de tempo |
| **Story Points** | Projeções, Tamanho | Capacidade não calculável |
| **Prioridade** | Distribuição, Alertas | Sem priorização visível |

### CAMPOS MÉDIA CRITICIDADE

| Campo | Usado em | Impacto se ausente |
|-------|----------|-------------------|
| **Produto** | Segmentação | Sem visão por produto |
| **Responsável** | Cards órfãos | Sem identificar não atribuídos |
| **Data Atualização** | Estagnados | Sem identificar parados |

### CAMPOS BAIXA CRITICIDADE

| Campo | Usado em | Impacto se ausente |
|-------|----------|-------------------|
| **Sprint** | Identificar não planejados | Parcial |
| **Tipo** | Distribuição | Visão complementar |

---

## 🎯 DECISÕES SUPORTADAS PELA ABA PB

### Para Product Owner/PO

| Decisão | Métricas de Suporte |
|---------|---------------------|
| **O que priorizar na próxima sprint?** | Itens por prioridade + idade |
| **O que descartar?** | Cards > 90 dias + baixa prioridade |
| **O backlog está saudável?** | Score de saúde, aging |
| **Qual produto precisa de mais atenção?** | Backlog por produto |

### Para Liderança

| Decisão | Métricas de Suporte |
|---------|---------------------|
| **Temos capacidade para entregar o backlog?** | Projeção de sprints |
| **O time está absorvendo ou acumulando dívida?** | Taxa de crescimento |
| **Precisamos de mais recursos?** | SP pendentes vs velocidade |

### Para o Time

| Decisão | Métricas de Suporte |
|---------|---------------------|
| **Quais itens estão esquecidos?** | Cards estagnados |
| **O que precisa de refinamento?** | Sem SP, sem responsável |
| **Onde está o gargalo?** | Distribuição por status/produto |

---

## 🔮 FÓRMULAS IMPLEMENTADAS

```python
# Idade média do backlog
idade_media = (hoje - df['criado']).mean().days

# Taxa de crescimento
taxa_crescimento = ((entrada - saida) / entrada) * 100

# Sprints para zerar backlog
sprints_para_zerar = sp_backlog / velocidade_media

# Score de Saúde do Backlog (0-100)
score = (
    (1 - min(idade_media/90, 1)) * 30 +  # Idade (30%)
    (1 - min(pct_sem_sp/50, 1)) * 25 +   # Estimativas (25%)
    (1 - min(taxa_crescimento/50, 1)) * 25 +  # Crescimento (25%)
    (1 - min(pct_criticos/20, 1)) * 20   # Priorização (20%)
)

# Faixas de aging
faixa_0_15 = len(df[df['idade'] <= 15])
faixa_16_30 = len(df[(df['idade'] > 15) & (df['idade'] <= 30)])
faixa_31_60 = len(df[(df['idade'] > 30) & (df['idade'] <= 60)])
faixa_61_90 = len(df[(df['idade'] > 60) & (df['idade'] <= 90)])
faixa_90_plus = len(df[df['idade'] > 90])
```

---

## 📋 DIFERENÇAS ENTRE ABAS SD vs PB

| Aspecto | Aba SD (Service Desk) | Aba PB (Product Backlog) |
|---------|----------------------|--------------------------|
| **Foco** | Sprint atual, execução | Backlog geral, planejamento |
| **Tempo** | Dias até release | Idade dos itens |
| **Métricas** | FK, FPY, DDP | Aging, Taxa Crescimento |
| **Público** | QA, Dev, Liderança | PO, Liderança, Time |
| **Decisão** | Go/No-Go release | Priorização, Descarte |
| **Gargalos** | Fila de QA, Code Review | Itens estagnados, órfãos |

---

*Documento gerado para NinaDash v8.4 - Aba PB - Abril 2026*
