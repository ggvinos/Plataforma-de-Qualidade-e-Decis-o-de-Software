# 📊 DOCUMENTAÇÃO COMPLETA - NinaDash SD (Service Desk)

> **Objetivo deste documento:** Mapear todos os campos, métricas e informações exibidas em cada aba do dashboard SD para análise de peso e relevância por IA, visando futuras adaptações para projetos QA e PB.

---

## 📌 CAMPOS JIRA UTILIZADOS (FONTE DE DADOS)

Estes são os campos do Jira que alimentam todas as métricas do dashboard:

| Campo Jira | Custom Field ID | Obrigatoriedade | Descrição | Usado em |
|------------|-----------------|-----------------|-----------|----------|
| **Story Points** | `customfield_11257` (principal) / `customfield_10016` (alt) | Obrigatório (exceto Hotfix) | Esforço estimado do card | FK, Velocidade, Carga |
| **Bugs Encontrados** | `customfield_11157` | Obrigatório após validação | Quantidade de bugs encontrados pelo QA | FK, FPY, DDP, Taxa Retrabalho |
| **Sprint** | `customfield_10020` | Automático | Sprint em que o card está | Filtro, Histórico |
| **Complexidade de Teste** | `customfield_11290` | Meta futura | Nível de dificuldade para testar | Carga QA |
| **QA Responsável** | `customfield_10487` | Obrigatório | Quem valida o card | Carga QA, Comparativo QA |
| **Produto** | `customfield_10102` | Obrigatório | Produto ao qual pertence | Aba Produto, Filtros |
| **Status** | Campo nativo | Automático | Estado atual do card | Funil, Fluxo |
| **Tipo** | Campo nativo | Automático | TAREFA, BUG, HOTFIX, SUGESTÃO | Distribuição, Filtros |
| **Prioridade** | Campo nativo | Automático | Alta, Média, Baixa | Alertas, Liderança |
| **Responsável** | Campo nativo | Automático | Desenvolvedor | Aba Dev, FK |
| **Data Criação** | Campo nativo | Automático | Quando foi criado | Lead Time |
| **Data Resolução** | Campo nativo | Automático | Quando foi concluído | Lead Time |

---

## 📑 ABAS DO DASHBOARD

---

# 1️⃣ ABA: VISÃO GERAL

**Objetivo:** Fornecer uma visão rápida e completa do estado atual da sprint, com KPIs principais e alertas.

**Público-alvo:** Todos (QA, Dev, Liderança, PO)

### CAMPOS E MÉTRICAS EXIBIDOS:

#### 1.1 Header da Sprint
| Campo | Descrição | Fonte | Criticidade |
|-------|-----------|-------|-------------|
| Sprint Atual | Nome da sprint ativa | `customfield_10020` | Alta |
| Dias até Release | Tempo restante para deploy | Calculado | Alta |

#### 1.2 KPIs Principais (Expandível)
| Métrica | Fórmula/Cálculo | Fonte Jira | Objetivo | Criticidade |
|---------|-----------------|------------|----------|-------------|
| **Total Cards** | Contagem de issues | Query JQL | Volume total da sprint | Média |
| **Story Points** | Soma de SP | `customfield_11257` | Esforço total planejado | Alta |
| **% Concluído** | (Cards done / Total) × 100 | Status | Progresso da sprint | Alta |
| **Bugs Encontrados** | Soma de bugs | `customfield_11157` | Qualidade do código | Alta |
| **Fator K** | SP / (Bugs + 1) | SP + Bugs | Maturidade geral | Alta |

#### 1.3 Métricas de Qualidade (Expandível)
| Métrica | Fórmula | Fonte | Objetivo | Criticidade |
|---------|---------|-------|----------|-------------|
| **FPY** | (Cards sem bugs / Total) × 100 | Bugs | Qualidade primeira entrega | Alta |
| **DDP** | (Bugs QA / Total estimado) × 100 | Bugs | Eficácia do QA | Alta |
| **Lead Time** | Data Resolução - Data Criação | Datas | Velocidade do fluxo | Média |
| **Health Score** | Score composto (0-100) | Múltiplos | Saúde geral da release | Alta |

#### 1.4 Cards por Status (Expandível + Listagem)
| Status | Descrição | Fonte | Objetivo |
|--------|-----------|-------|----------|
| Desenvolvimento | Cards em dev | Status | WIP de dev |
| Code Review | Aguardando CR | Status | Gargalo de revisão |
| Aguardando QA | Fila do QA | Status | Demanda de validação |
| Em Validação | Sendo testados | Status | Capacidade atual QA |

#### 1.5 Gráficos (Expandível)
| Gráfico | Tipo | Dados | Objetivo |
|---------|------|-------|----------|
| Distribuição por Tipo | Pizza | Tipo do card | Mix de trabalho |
| Cards por Produto | Barras | Produto | Concentração por produto |

---

# 2️⃣ ABA: QA

**Objetivo:** Monitorar o funil de validação, identificar gargalos, comparar performance entre QAs e analisar bugs.

**Público-alvo:** QA, Liderança, Tech Lead

### CAMPOS E MÉTRICAS EXIBIDOS:

#### 2.1 Indicadores de QA (Expandível)
| Métrica | Fórmula | Fonte | Objetivo | Criticidade |
|---------|---------|-------|----------|-------------|
| **Fila de QA** | Aguardando + Em Validação | Status | Demanda atual | Alta |
| **Tempo Médio Fila** | Média dias em waiting_qa | Datas | Velocidade do fluxo | Alta |
| **Cards Aging** | Cards > 3 dias no status | Datas | Identificar travados | Alta |
| **Taxa Reprovação** | (Reprovados / Total validados) × 100 | Status | Qualidade recebida | Média |
| **DDP** | Eficácia detecção | Bugs | Maturidade QA | Alta |

#### 2.2 Funil de Validação (Expandível)
| Visualização | Dados | Objetivo |
|--------------|-------|----------|
| Gráfico Funil | Quantidade por etapa | Visualizar gargalos |
| Carga por QA (Barras) | Cards + SP por QA | Balanceamento |

#### 2.3 Comparativo entre QAs (Expandível)
| Campo | Descrição | Fonte | Objetivo | Criticidade |
|-------|-----------|-------|----------|-------------|
| QA | Nome do QA | `customfield_10487` | Identificação | Alta |
| Cards | Total atribuídos | Query | Volume | Média |
| Validados | Concluídos | Status | Produtividade | Alta |
| Em Fila | Aguardando/Validando | Status | Carga atual | Alta |
| Bugs Encontrados | Soma bugs | Bugs | Eficácia | Alta |
| FPY | % sem bugs | Calculado | Qualidade recebida | Alta |
| SP Total | Soma SP | SP | Complexidade | Média |
| Lead Time | Tempo médio | Datas | Velocidade | Média |

#### 2.4 Gráficos Comparativos
| Gráfico | Tipo | Dados | Objetivo |
|---------|------|-------|----------|
| Bugs por QA | Barras | Bugs/QA | Comparar detecção |
| Cards Validados por QA | Pizza | Done/QA | Distribuição trabalho |

#### 2.5 Análise de Bugs e Retrabalho (Expandível)
| Métrica | Descrição | Fonte | Objetivo |
|---------|-----------|-------|----------|
| Bugs por Tipo de Card | Pizza | Bugs + Tipo | Onde concentrar testes |
| FPY Geral | % primeira passagem | Calculado | Qualidade dev |
| Taxa Retrabalho | % com bugs | Calculado | Custo de qualidade |
| Lead Time Médio | Tempo de ciclo | Datas | Eficiência |
| Devs com mais bugs | Lista rankeada | Bugs/Dev | Atenção do QA |

#### 2.6 Cards Aging (Expandível + Listagem)
| Campo | Descrição | Criticidade |
|-------|-----------|-------------|
| Ticket ID | Link clicável | Alta |
| Título | Descrição | Média |
| Dias no Status | Tempo parado | Alta |
| QA | Responsável | Alta |

#### 2.7 Filas (Expandível + Listagem)
- Aguardando Validação (lista completa)
- Em Validação (lista completa)

---

# 3️⃣ ABA: DEV

**Objetivo:** Avaliar performance individual dos desenvolvedores, ranking de maturidade e identificar necessidades de suporte.

**Público-alvo:** Tech Lead, Desenvolvedores, Liderança

### CAMPOS E MÉTRICAS EXIBIDOS:

#### 3.1 Seletor
| Campo | Opções | Objetivo |
|-------|--------|----------|
| Desenvolvedor | "Ranking Geral" + Lista devs | Filtrar visão |

#### 3.2 Ranking de Performance (Expandível)
| Campo | Fórmula | Fonte | Objetivo | Criticidade |
|-------|---------|-------|----------|-------------|
| Desenvolvedor | Nome | Responsável | Identificação | Alta |
| Cards | Total | Query | Volume | Média |
| SP | Soma | SP | Complexidade | Alta |
| Bugs | Soma | Bugs | Qualidade | Alta |
| **Fator K** | SP / (Bugs + 1) | Calculado | Maturidade | Alta |
| FPY | % sem bugs | Calculado | Primeira passagem | Alta |
| Tempo Médio | Lead time | Datas | Velocidade | Média |
| Selo | 🥇🥈🥉⚠️ | FK | Classificação visual | Alta |

#### 3.3 Gráfico Fator K
| Elemento | Descrição |
|----------|-----------|
| Barras coloridas | FK por dev (vermelho→verde) |
| Linha de meta | FK ≥ 2 |

#### 3.4 Devs que Precisam de Atenção (Expandível)
| Critério | Descrição |
|----------|-----------|
| FK < 2 | Abaixo da meta |
| Bugs > 0 | Tem problemas detectados |
| Cards problemáticos | Lista com mais bugs |

#### 3.5 Análise do Time (Expandível)
| Visualização | Dados | Objetivo |
|--------------|-------|----------|
| Cards por Dev (Barras) | Volume individual | Distribuição |
| Taxa Bugs/Card (Barras) | Bugs/tickets | Qualidade |
| Total Cards | Número | Volume |
| Em Desenvolvimento | Número | WIP |
| Total Bugs | Número | Qualidade |
| Média Bugs/Card | Número | Benchmark |
| Cards sem Bugs | Número + % | Qualidade |
| Lead Time Médio | Dias | Velocidade |

#### 3.6 Análise para Tech Lead (Expandível)
| Métrica | Tipo | Objetivo | Criticidade |
|---------|------|----------|-------------|
| SP por Dev (Pizza) | Distribuição | Quem assume complexidade | Alta |
| Status por Dev (Barras empilhadas) | Concluído vs Andamento | Progresso | Alta |
| WIP por Dev (Barras) | Cards em andamento | Sobrecarga | Alta |
| Fila Code Review (Lista) | Cards aguardando | Gargalo | Alta |
| Velocidade SP/Card (Barras) | Eficiência | Comparar produtividade | Média |
| Cards Críticos (Lista) | Alta prioridade pendente | Riscos | Alta |

#### 3.7 Visão Individual (quando dev selecionado)
| Informação | Descrição | Criticidade |
|------------|-----------|-------------|
| Selo de Maturidade | 🥇🥈🥉⚠️ + FK | Alta |
| Cards Desenvolvidos | Número | Média |
| Story Points | Soma | Alta |
| Bugs Encontrados | Soma | Alta |
| Taxa Zero Bugs | % | Alta |
| Lista de Cards | Todos os cards do dev | Alta |

---

# 4️⃣ ABA: GOVERNANÇA

**Objetivo:** Monitorar a qualidade do preenchimento dos campos obrigatórios para garantir métricas confiáveis.

**Público-alvo:** PO, Liderança, QA

### CAMPOS E MÉTRICAS EXIBIDOS:

#### 4.1 Status Geral (Expandível)
| Métrica | Cálculo | Objetivo |
|---------|---------|----------|
| Média de Preenchimento | (SP + Bugs + Complexidade + QA) / 4 | Qualidade dados |
| Alerta | Crítico se < 50% | Ação imediata |

#### 4.2 Campos Obrigatórios (Expandível por campo)
| Campo | Obrigatoriedade | Exceção | Criticidade |
|-------|-----------------|---------|-------------|
| **Story Points** | Obrigatório | Hotfix (assume 2 SP) | Alta |
| **Bugs Encontrados** | Obrigatório após validação | - | Alta |
| **Complexidade de Teste** | Meta futura | - | Baixa |
| **QA Responsável** | Obrigatório | - | Alta |

#### 4.3 Por cada campo
| Informação | Descrição |
|------------|-----------|
| % Preenchido | Barra de progresso |
| X/Y | Preenchidos vs Total |
| Lista faltando | Cards sem o campo |
| Exportar CSV | Download para cobrança |

---

# 5️⃣ ABA: PRODUTO

**Objetivo:** Visualizar métricas segmentadas por produto e monitorar cards fora do planejamento.

**Público-alvo:** PO, Stakeholders, Liderança

### CAMPOS E MÉTRICAS EXIBIDOS:

#### 5.1 Indicadores de Fluxo (Expandível)
| Métrica | Descrição | Fonte | Criticidade |
|---------|-----------|-------|-------------|
| **Iniciados e Finalizados na Sprint** | Cards criados e concluídos na mesma sprint | Datas | Alta |
| **Cards Fora do Período** | Adicionados após início da sprint | Datas | Alta |
| **Total Hotfixes** | Correções emergenciais | Tipo | Alta |

#### 5.2 Cards Fora do Período (Expandível + Listagem)
| Informação | Objetivo |
|------------|----------|
| Lista completa | Identificar escopo não planejado |
| Alerta visual | Destacar problema |

#### 5.3 Visualizações (Expandível)
| Gráfico | Tipo | Dados | Objetivo |
|---------|------|-------|----------|
| Hotfix por Produto | Barras | Tipo + Produto | Estabilidade por produto |
| Estágio por Produto | Barras empilhadas | Status + Produto | Progresso por produto |

#### 5.4 Resumo por Produto (Expandível)
| Campo | Descrição | Fonte |
|-------|-----------|-------|
| Produto | Nome | `customfield_10102` |
| Cards | Total | Contagem |
| SP | Soma | SP |
| Bugs | Soma | Bugs |
| FK | Fator K | Calculado |
| Hotfixes | Quantidade | Tipo |

---

# 6️⃣ ABA: HISTÓRICO

**Objetivo:** Visualizar a evolução das métricas ao longo das sprints para identificar tendências.

**Público-alvo:** Liderança, QA, Tech Lead

### CAMPOS E MÉTRICAS EXIBIDOS:

#### 6.1 Insights Automáticos (Expandível)
| Insight | Critério | Visualização |
|---------|----------|--------------|
| Fator K | Variação % entre sprints | Alerta verde/amarelo |
| FPY | Comparação com meta (80%) | Alerta |
| Lead Time | Comparação com meta (≤7d) | Alerta |

#### 6.2 Gráficos de Evolução (Expandíveis)
| Gráfico | Métricas | Tipo | Criticidade |
|---------|----------|------|-------------|
| Fator K | FK por sprint | Linha com área | Alta |
| Qualidade | FPY + DDP | Linhas múltiplas | Alta |
| Bugs | Total bugs por sprint | Barras | Média |
| Health Score | HS por sprint | Linha com zonas | Alta |
| Throughput | Cards/SP por sprint | Barras + Linha | Média |
| Lead Time | Dias por sprint | Linha | Média |
| Taxa Reprovação | % por sprint | Linha | Média |

#### 6.3 Dados Históricos (Expandível)
| Informação | Descrição |
|------------|-----------|
| Tabela completa | Todas as métricas por sprint |
| Exportável | Para análise offline |

*Nota: Dados demonstrativos para visualização do potencial*

---

# 7️⃣ ABA: LIDERANÇA

**Objetivo:** Fornecer visão executiva para tomada de decisão Go/No-Go de release.

**Público-alvo:** Gerentes, Diretores, PO

### CAMPOS E MÉTRICAS EXIBIDOS:

#### 7.1 Decisão de Release (Expandível)
| Elemento | Critério | Ação |
|----------|----------|------|
| 🛑 ATENÇÃO NECESSÁRIA | Cards bloqueados ou conclusão < 30% | Avaliar riscos |
| ⚠️ REVISAR ESCOPO | Conclusão < 50% e < 3 dias | Reduzir escopo |
| ✅ NO CAMINHO | Demais casos | Prosseguir |

#### 7.2 Métricas Executivas
| Métrica | Descrição | Criticidade |
|---------|-----------|-------------|
| Health Score | 0-100 + Status | Alta |
| Total Cards | Volume | Média |
| % Concluído | Progresso | Alta |
| Fator K | Maturidade + Selo | Alta |
| Dias até Release | Tempo | Alta |

#### 7.3 Composição Health Score
| Componente | Peso | Descrição |
|------------|------|-----------|
| Conclusão | 30% | % cards done |
| DDP | 25% | Eficácia QA |
| FPY | 20% | Qualidade dev |
| Gargalos | 15% | Bloqueios/Aging |
| Lead Time | 10% | Velocidade |

#### 7.4 Pontos de Atenção (Expandível + Listagem)
| Alerta | Critério | Ação |
|--------|----------|------|
| 🚫 Bloqueados/Reprovados | Status blocked/rejected | Resolver imediato |
| ⚠️ Alta Prioridade | Prioridade alta não done | Priorizar |
| ℹ️ Fora da Janela | < 3 dias úteis | Avaliar postergação |

#### 7.5 Performance por Dev (Expandível)
| Dados | Descrição |
|-------|-----------|
| Tabela resumo | Métricas por desenvolvedor |

#### 7.6 Exportação
| Formato | Conteúdo |
|---------|----------|
| CSV | Dados completos |
| Excel | Dados + Health Score |

---

# 8️⃣ ABA: SOBRE

**Objetivo:** Documentar o objetivo do dashboard, métricas utilizadas e referências teóricas.

**Público-alvo:** Todos

### SEÇÕES:

#### 8.1 NINA Tecnologia
- Missão, Visão, Valores
- Contexto da empresa

#### 8.2 Objetivo do Dashboard
- Problema que resolve (antes/depois)
- Diferenciais vs dashboards comuns

#### 8.3 Métricas Implementadas
| Métrica | Descrição | Impacto |
|---------|-----------|---------|
| FPY | Primeira passagem | Eficiência dev |
| DDP | Detecção defeitos | Maturidade QA |
| Fator K | SP/Bugs | Maturidade individual |
| Lead Time | Tempo de ciclo | Gargalos |
| Health Score | Score composto | Go/No-Go |
| WIP | Work in Progress | Sobrecarga |
| Throughput | Vazão | Capacidade |

#### 8.4 Fórmulas Principais
- Fator K: `SP / (Bugs + 1)`
- Health Score: Composição ponderada
- FPY: `(Sem bugs / Total) × 100`
- DDP: `(Bugs QA / Total estimado) × 100`
- Janela Release: ≥ 3 dias úteis

#### 8.5 Fundamentos Teóricos
- ISTQB/CTFL
- TDD (Kent Beck)
- Shift-Left Testing

#### 8.6 Tomada de Decisão por Perfil
| Perfil | Uso principal |
|--------|---------------|
| QA | Priorização, carga, risco |
| Liderança | Go/No-Go, performance, gargalos |
| Devs | FK, retrabalho, tempo ciclo |

#### 8.7 Abas Disponíveis
- Documentação de cada aba
- Público-alvo
- Funcionalidades

#### 8.8 Governança do Sistema
| Info | Valor |
|------|-------|
| Desenvolvido por | QA NINA |
| Mantido por | Vinícios Ferreira |
| Versão | v8.3 |
| Stack | Python, Streamlit, Plotly, Pandas |
| Integração | Jira API REST |

---

## 📊 RESUMO DE CRITICIDADE DOS CAMPOS

### CAMPOS ALTA CRITICIDADE (Essenciais)
| Campo | Usado em | Impacto se ausente |
|-------|----------|-------------------|
| Story Points | FK, Health Score, Velocidade | Métricas de maturidade zeradas |
| Bugs Encontrados | FK, FPY, DDP, Retrabalho | Impossível medir qualidade |
| QA Responsável | Carga QA, Comparativo | Sem distribuição de carga |
| Status | Funil, Progresso, Alertas | Dashboard inutilizável |

### CAMPOS MÉDIA CRITICIDADE (Importantes)
| Campo | Usado em | Impacto se ausente |
|-------|----------|-------------------|
| Produto | Aba Produto, Filtros | Sem segmentação |
| Prioridade | Alertas, Liderança | Sem priorização de riscos |
| Lead Time | Velocidade, Health Score | Parcial |

### CAMPOS BAIXA CRITICIDADE (Complementares)
| Campo | Usado em | Impacto se ausente |
|-------|----------|-------------------|
| Complexidade de Teste | Carga QA (futuro) | Nenhum atual |

---

## 🔮 CONSIDERAÇÕES PARA PROJETOS QA e PB

### Campos que provavelmente NÃO se aplicam:
- Complexidade de Teste (específico SD)
- QA Responsável (se não há QA dedicado)
- Bugs Encontrados (se não há validação formal)

### Campos que provavelmente SE aplicam:
- Story Points (universal)
- Status (universal)
- Responsável (universal)
- Sprint (universal)
- Produto (universal)

### Métricas que podem ser simplificadas:
- Remover FK se não há medição de bugs
- Remover DDP se não há QA
- Manter Lead Time (universal)
- Manter Throughput (universal)

---

*Documento gerado para análise de IA - NinaDash v8.3 - Abril 2026*
