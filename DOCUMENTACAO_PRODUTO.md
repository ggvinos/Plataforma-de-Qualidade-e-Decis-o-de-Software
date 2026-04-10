# 📊 NinaDash — Documentação de Produto
## Dashboard de Inteligência e Métricas de QA

---

# 1. VISÃO DO PRODUTO

## O que é o NinaDash

O **NinaDash** é um dashboard interativo desenvolvido em Python/Streamlit para análise de métricas de desenvolvimento e QA, integrado diretamente com a API do Jira da NINA Tecnologia.

A ferramenta nasceu de uma necessidade real: **transformar o processo de QA, que era um "buraco negro" sem dados nem previsibilidade**, em um motor automatizado de inteligência operacional.

## Qual problema resolve

Antes do NinaDash:
- A falta de dados impedia a mensuração do tempo real de cada validação
- Não havia previsibilidade das entregas
- O Notion era apenas um quadro de tarefas manual
- Impossível saber quanto tempo cada card precisaria para validação segura

O NinaDash resolve:
- **Automatiza a coleta de métricas** — eliminando preenchimento manual de datas
- **Calcula em tempo real** se as diretrizes de prazos (SLAs) estão sendo respeitadas
- **Monitora a janela de corte** de 3 dias úteis antes da release
- **Dá segurança técnica** aos QAs, especialmente em Hotfixes

## Por que essa ferramenta existe

O time precisava entender **exatamente quanto tempo cada demanda precisa para ser liberada com segurança**. Sem isso:
- Releases eram arriscadas
- QAs não tinham previsibilidade
- Liderança não tinha visibilidade do processo
- Decisões eram baseadas em "feeling" ao invés de dados

## Diferencial em relação a dashboards comuns

| Dashboards Comuns | NinaDash |
|---|---|
| Métricas genéricas | Métricas ISTQB/CTFL customizadas para QA |
| Dados estáticos | Integração em tempo real com Jira |
| Foco em quantidade | Foco em **maturidade do código** (Fator K) |
| Sem contexto de QA | **Janela de Release** com dias úteis |
| Métricas isoladas | **Health Score composto** para decisão |

---

# 2. COMO A FERRAMENTA AJUDA NA TOMADA DE DECISÃO

## Tipos de Decisões Suportadas

### Para QAs
- **Priorização de cards**: Identificar quais cards estão fora da janela de 3 dias
- **Gestão de carga**: Balancear validações por complexidade
- **Risco de release**: Saber quando pedir mais tempo

### Para Liderança
- **Saúde da release**: Health Score consolidado (go/no-go)
- **Performance do time**: Throughput, Lead Time, MTTR
- **Qualidade do desenvolvimento**: Fator K por desenvolvedor
- **Gargalos**: Visualizar onde o fluxo está travando

### Para Desenvolvedores
- **Feedback de qualidade**: Bugs encontrados por card
- **Maturidade da entrega**: Quantos bugs voltam do QA
- **Tempo de ciclo**: Quanto tempo cada validação demora

## Cenários Reais de Uso

### Cenário 1: Release em Risco
> **Se** a taxa de cards "Fora da Janela" aumenta para >30%
> **Então** o time pode:
> - Escalar para liderança
> - Negociar adiamento de funcionalidades
> - Priorizar apenas cards críticos

### Cenário 2: Desenvolvedor com Alto Retrabalho
> **Se** o Fator K de um desenvolvedor está em "Risco" (<1.0)
> **Então** o time pode:
> - Agendar pair programming com QA
> - Revisar práticas de code review
> - Identificar padrões de erro

### Cenário 3: Hotfix Crítico
> **Se** um Hotfix chega com 1 dia até a release
> **Então** o dashboard mostra:
> - Alerta visual vermelho
> - Complexidade de validação necessária
> - Risco de entrega sem validação completa

---

# 3. MÉTRICAS DE QUALIDADE (BASEADAS NO JIRA)

## Categorias de Métricas

### 🔴 Bugs e Qualidade

| Métrica | O que mede | Por que é importante | Decisão |
|---|---|---|---|
| **Bugs Encontrados** | Total de falhas detectadas por card | Expõe instabilidade do código | Identificar padrões de erro por dev |
| **Quantidade de Reprovações** | Vezes que o card voltou para Dev | Mede retrabalho real | Otimizar code review |
| **DDP (Defect Detection %)** | Bugs encontrados pelo QA vs total | Eficácia do time de testes | Ajustar cobertura de testes |
| **FPY (First Pass Yield)** | Cards aprovados na primeira tentativa | Qualidade do desenvolvimento | Meta de melhoria contínua |

### 🟡 Performance e Fluxo

| Métrica | O que mede | Por que é importante | Decisão |
|---|---|---|---|
| **Lead Time** | Tempo do início ao fim do card | Velocidade total de entrega | Identificar gargalos |
| **Tempo de Ciclo QA** | Dias úteis em validação | Previsibilidade do QA | Estimar prazos com precisão |
| **MTTR (Mean Time To Repair)** | Tempo médio para corrigir bug | Agilidade de resposta | Priorizar bugs antigos |
| **Throughput** | Cards concluídos por período | Capacidade de entrega | Planejamento de sprint |

### 🟢 Maturidade e Saúde

| Métrica | O que mede | Por que é importante | Decisão |
|---|---|---|---|
| **Fator K (Maturidade)** | SP / (Bugs × fator de rigor) | Qualidade do código entregue | Selo Gold/Silver/Bronze/Risco |
| **Health Score** | Pontuação composta da release | Visão consolidada de saúde | Decisão de go/no-go |
| **Dentro da Janela** | Cards com ≥3 dias úteis para release | Segurança do processo de QA | Alertar atropelos de cronograma |
| **WIP (Work In Progress)** | Cards em andamento agora | Sobrecarga do time | Limitar multitarefa |

## Explicação Detalhada das Métricas Principais

### Fator K — Índice de Maturidade
```
Fórmula: FK = SP / (Bugs + 1)
```

| Selo | Fator K | Significado |
|---|---|---|
| 🥇 Gold | ≥ 3.0 | Excelente qualidade, código maduro |
| 🥈 Silver | 2.0 - 2.9 | Boa qualidade, dentro do esperado |
| 🥉 Bronze | 1.0 - 1.9 | Regular, precisa de atenção |
| ⚠️ Risco | < 1.0 | Crítico, requer intervenção imediata |

### Health Score — Saúde da Release
```
Fórmula: HS = (Conclusão×30 + DDP×25 + FPY×20 + Gargalos×15 + LeadTime×10) / 100
```

| Score | Status | Recomendação |
|---|---|---|
| ≥ 75 | 🟢 Saudável | Release pode seguir |
| 50 - 74 | 🟡 Atenção | Monitorar riscos |
| 25 - 49 | 🟠 Alerta | Ação necessária |
| < 25 | 🔴 Crítico | Avaliar adiamento |

### Dentro da Janela de Release
```
Regra: Card entregue ≥ 3 dias úteis antes da Release
```
- ✅ **Dentro**: QA tem tempo seguro para testar
- ⚠️ **Fora**: Validação às pressas, risco de escape

---

# 4. COMO A FERRAMENTA FOI CONSTRUÍDA

## Ideia Inicial

O ponto de partida foi **transformar o Notion de um quadro de tarefas manual** em um motor de dados automatizado. Objetivos iniciais:
1. Eliminar preenchimento manual de datas
2. Criar fórmulas para cálculo em tempo real de SLAs
3. Monitorar a janela de corte de 3 dias úteis
4. Dar segurança técnica aos QAs em Hotfixes

## Evolução da Interface

### Tela de Login
- Design clean com logo NINA
- Autenticação via email autorizado
- Validação de permissões antes do acesso

### Dashboard Principal
- Layout focado em dados
- Gráficos interativos com Plotly
- Filtros na sidebar (Projeto, Sprint, Dev, QA)
- Cards de status com cores semânticas

## Decisões Técnicas

### Stack Escolhido
- **Python** — Linguagem padrão da empresa para automação
- **Streamlit** — Deploy rápido, interface reativa
- **Plotly** — Gráficos interativos avançados
- **Pandas** — Processamento de dados
- **API Jira** — Integração em tempo real

### Campos Customizados no Jira
```python
CUSTOM_FIELDS = {
    "story_points": "customfield_11257",
    "sprint": "customfield_10020",
    "bugs_encontrados": "customfield_11157",
    "dias_ate_release": "customfield_11357",
    "janela_testes": "customfield_11358",
    "complexidade_teste": "customfield_11290",
    "qa_responsavel": "customfield_10487",
    "desenvolvedor": "customfield_10455",
}
```

### Projetos Mapeados
| Código | Nome | Descrição |
|---|---|---|
| SD | Desenvolvimento | Projeto principal |
| QA | Quality Assurance | Cards de validação |
| PB | Backlog de Produto | Backlog geral |
| VALPROD | Validação em Produção | Bugs em produção |

## Estrutura do Sistema

```
app.py (principal)
├── Autenticação (login com email)
├── Sidebar (filtros)
├── Aba: Visão Geral
│   ├── Métricas principais
│   ├── Health Score
│   └── Alertas críticos
├── Aba: Por Desenvolvedor
│   ├── Fator K individual
│   └── Ranking de qualidade
├── Aba: Por QA
│   ├── Cards por responsável
│   └── Tempo de ciclo
└── Aba: Liderança
    ├── Decisões estratégicas
    ├── Tendências
    └── Exportação de dados
```

---

# 5. DECISÕES DE DESIGN E PRODUTO

## Identidade Visual

- **Cor principal**: `#AF0C37` (Vermelho NINA)
- **Background**: Opções em branco e azul escuro
- **Logo**: SVG em variações (cinza, vermelho)
- **Fontes**: Sistema padrão Streamlit

## Princípios de Layout

### 1. Clareza sobre Estética
O dashboard prioriza **dados legíveis** sobre decoração visual. Cada elemento tem propósito.

### 2. Hierarquia de Informação
- **Nível 1**: Health Score e alertas críticos
- **Nível 2**: Métricas principais (cards coloridos)
- **Nível 3**: Gráficos detalhados
- **Nível 4**: Tabelas e dados brutos

### 3. Cores Semânticas
```css
🟢 Verde (#22c55e): Saudável, aprovado
🟡 Amarelo (#eab308): Atenção, moderado
🟠 Laranja (#f97316): Alerta, precisa ação
🔴 Vermelho (#ef4444): Crítico, urgente
🔵 Azul (#3b82f6): Informativo, neutro
🟣 Roxo (#8b5cf6): Destaque especial
```

### 4. Separação Login vs Dashboard
- **Login**: Tela simples, apenas autenticação
- **Dashboard**: Interface densa com dados
- **Motivo**: Usuário não autorizado não vê dados sensíveis

## Tooltips Explicativos

Cada métrica possui tooltip com:
- Título da métrica
- Descrição do que mede
- Fórmula de cálculo
- Tabela de interpretação
- Fonte/referência (ISTQB, Six Sigma, etc.)

---

# 6. DESAFIOS ENCONTRADOS

## Problemas Técnicos

### 1. Geração Inconsistente de UI por IA
- **Problema**: Prompts mal definidos geravam interfaces diferentes a cada execução
- **Solução**: Estruturar prompts com exemplos específicos e constraints claros

### 2. Limitação de Contexto/Token
- **Problema**: IA perdia contexto em conversas longas
- **Solução**: Documentar decisões no Notion para referência

### 3. Campos Customizados do Jira
- **Problema**: IDs de campos variam por instalação
- **Solução**: Mapeamento centralizado em `CUSTOM_FIELDS`

### 4. Cálculo de Dias Úteis
- **Problema**: Jira não calcula dias úteis nativamente
- **Solução**: Função Python customizada excluindo sábados/domingos

## Problemas de Processo

### 1. Definição de Métricas
- **Problema**: Quais métricas realmente importam?
- **Solução**: Mapear decisões que precisam de dados primeiro

### 2. Preenchimento Manual
- **Problema**: QAs esqueciam de preencher campos
- **Solução**: Automatizar o máximo possível via Jira Automation

### 3. Resistência à Mudança
- **Problema**: Time acostumado com processo manual
- **Solução**: Mostrar valor com métricas de impacto reais

---

# 7. HISTÓRICO DE EVOLUÇÃO

## Fase 1 — Ideia Inicial
**Período**: Conceito no Notion

✅ Criação da documentação "Inteligência e Métricas QA"
✅ Definição das primeiras métricas:
   - Status do Teste
   - Tipo de Solicitação (BUG, FEATURE, HOTFIX)
   - Complexidade (Validation Points 1-5)
   - Índice de Estabilidade
   - Dentro da Janela
   - Tempo de Ciclo QA

✅ Criação do Dicionário de Propriedades (Manual dos QAs)
✅ Definição da Tabela de Esforço de QA

---

## Fase 2 — Exploração de UI
**Período**: Primeiras implementações

✅ Primeiras telas geradas com IA
⚠️ Problemas encontrados:
   - Inconsistência entre gerações
   - Layouts quebrados em mobile
   - Cores não seguiam identidade visual

✅ Ajustes de UX:
   - Definição de paleta de cores
   - Padronização de cards
   - Animações de entrada (fadeInUp, slideIn)

---

## Fase 3 — Estruturação do Produto
**Período**: Dashboard funcional

✅ Definição correta do login
✅ Separação entre UI de entrada e dashboard
✅ Integração real com API do Jira
✅ Métricas ISTQB implementadas:
   - Fator K (Maturidade)
   - DDP (Defect Detection Percentage)
   - FPY (First Pass Yield)
   - MTTR (Mean Time To Repair)
   - Health Score

✅ Modo PoC funcionando sem credenciais (dados simulados)

---

## Fase 4 — Estado Atual
**Data**: Abril 2026

### O que já está definido
- ✅ Dashboard v5.1 funcional
- ✅ 9 métricas ISTQB implementadas
- ✅ Tooltips explicativos em todas as métricas
- ✅ Integração com 4 projetos Jira (SD, QA, PB, VALPROD)
- ✅ Filtros por Projeto, Sprint, Dev, QA
- ✅ Modo demonstração com dados fictícios
- ✅ Autenticação por email autorizado
- ✅ Gráficos interativos Plotly
- ✅ Alertas críticos automáticos
- ✅ **Exportação de dados (Excel, CSV, TXT)**
- ✅ **Gráficos de tendência por Sprint**
- ✅ **Cálculo de dias úteis (excluindo finais de semana)**
- ✅ **Cards de Health Score separados e responsivos**

### O que ainda falta
- ⏳ Deploy em Streamlit Cloud
- ⏳ Compartilhamento via link público (ngrok)
- ⏳ Histórico real de tendências (integração com banco de dados)
- ⏳ Alertas automáticos por email/Slack
- ⏳ Automações no Jira para campos calculados
- ⏳ Testes automatizados do dashboard

---

# 8. PRÓXIMOS PASSOS

## Curto Prazo (Próximas semanas)

1. **Deploy em Produção**
   - Configurar Streamlit Cloud
   - Configurar secrets com credenciais reais
   - Testar com dados de produção

2. **Automações no Jira**
   - Incremento automático de "Quantidade de Reprovações"
   - Cálculo automático de "Maturidade da Entrega"
   - Sinalização visual de cards "Fora da Janela"

## Médio Prazo (Próximos meses)

3. **Refinamento de Métricas**
   - Validar fórmulas com time de liderança
   - Ajustar níveis de rigor (0.5, 1.0, 1.5, 3.0)
   - Adicionar métricas de negócio (valor entregue)

4. **Histórico Real de Tendências**
   - Integração com banco de dados para persistir histórico
   - Gráficos de evolução temporal com dados reais
   - Comparação sprint vs sprint
   - Previsões baseadas em histórico

## Longo Prazo (Visão futura)

5. **Insights Automáticos com IA**
   - Agente NINA personalizado para análise
   - Sugestões automáticas de ação
   - Detecção de anomalias

6. **Integração com Outros Sistemas**
   - Slack para alertas
   - Confluence para documentação automática
   - GitHub para correlação com PRs

---

# APÊNDICE

## Tabela de Rigor de Tolerância

### 1. Rigor Tolerante (0.5)
| Bugs | Maturidade | Status |
|---|---|---|
| 1 | 93% | 🟢 EXCELENTE |
| 2 | 88% | 🟡 ESTÁVEL |
| 4 | 78% | 🟡 ESTÁVEL |
| 7 | 67% | 🟠 ATENÇÃO |
| 15+ | < 45% | 🔴 CRÍTICO |

### 2. Rigor Padrão (1.0)
| Bugs | Maturidade | Status |
|---|---|---|
| 0 | 100% | 🟢 EXCELENTE |
| 1 | 88% | 🟡 ESTÁVEL |
| 3 | 70% | 🟡 ESTÁVEL |
| 4 | 64% | 🟠 ATENÇÃO |
| 10 | 41% | 🔴 CRÍTICO |

### 3. Rigor Exigente (1.5)
| Bugs | Maturidade | Status |
|---|---|---|
| 1 | 82% | 🟡 ESTÁVEL |
| 2 | 70% | 🟡 ESTÁVEL |
| 3 | 61% | 🟠 ATENÇÃO |
| 5 | 48% | 🟠 ATENÇÃO |
| 6 | 44% | 🔴 CRÍTICO |

### 4. Rigor Crítico (3.0)
| Bugs | Maturidade | Status |
|---|---|---|
| 1 | 70% | 🟡 ESTÁVEL |
| 2 | 54% | 🟠 ATENÇÃO |
| 3 | 44% | 🔴 CRÍTICO |
| 5 | 32% | 🔴 CRÍTICO |
| 7 | 25% | 🔴 CRÍTICO |

---

## Comandos para Executar

```bash
# Navegar para o projeto
cd "/home/viniciosferreira/Documentos/Projetos NINA/Jira Dasboard"

# Instalar dependências
pip install -r requirements.txt

# Executar dashboard
python -m streamlit run app.py
```

**Acessos:**
- Local: http://localhost:8501
- Rede: http://192.168.15.154:8501

---

## Governança

- **Criado por**: Time de QA NINA Tecnologia
- **Mantido por**: Vinícios Ferreira
- **Última atualização**: Abril 2026
- **Versão atual**: v5.1

---

## Changelog v5.1

### Novas Funcionalidades
- ✅ **Exportação de Dados**
  - Exportar para Excel (.xlsx) com múltiplas abas
  - Exportar para CSV
  - Gerar relatório resumido em texto
  
- ✅ **Gráficos de Tendência por Sprint**
  - Evolução do Fator K
  - Tendência de Qualidade (FPY e DDP)
  - Bugs por Sprint
  - Health Score histórico
  - Análises automáticas de tendência
  
### Correções
- ✅ **Cálculo de Dias Úteis** — Agora exclui sábados e domingos corretamente
- ✅ **Cards do Health Score** — Separados em Pontuação e Status para melhor legibilidade
- ✅ **Layout Responsivo** — Métricas executivas agora empilham corretamente em telas menores

---

*Documento estruturado para importação no Notion. Todos os dados são baseados na documentação oficial do projeto.*
