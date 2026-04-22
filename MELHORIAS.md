# 📋 NinaDash - Histórico de Melhorias Detalhado

## 🎯 Propósito Geral
Transformar o QA de um processo sem visibilidade em um sistema de inteligência operacional baseado em dados.

---

## v8.82 - MODULARIZAÇÃO COMPLETA
- 🔧 **FIX**: Corrigido Meu Dashboard que não mostrava filtros corretamente
- 👤 **PESSOAS**: Lista de pessoas agora carrega corretamente
- ➕ **ADICIONAR**: Botão de adicionar widget agora funciona
- 📊 **DEBUG**: Mostra quantidade de dados e pessoas encontradas
- 🧹 **SIMPLIFICADO**: Interface mais limpa e direta

## v8.81 - MEU DASHBOARD
- 🎨 **MEU DASHBOARD**: Tela totalmente nova para construir dashboards personalizados
- ➕ **ADICIONAR WIDGETS**: Construtor no topo para adicionar métricas  
- ⬆️⬇️ **REORDENAR**: Mova widgets para cima ou para baixo
- 🗑️ **REMOVER**: Exclua widgets que não precisa mais
- 📊 **TEMPLATES**: Visão Executiva, Foco DEV, Foco QA
- 💾 **PERSISTÊNCIA**: Dashboard salvo em cookie
- 🧹 **SIDEBAR LIMPA**: Apenas logo e botão voltar na tela do dashboard

## v8.80 - CONSULTA PERSONALIZADA
- 🎯 **CONSULTA PERSONALIZADA**: Tela separada para consultas avançadas
- 🔍 **FILTROS DINÂMICOS**: Pessoa, status, período, produto personalizados
- 📋 **TIPOS DE CONSULTA**: Cards, métricas, comparativos, tendências, bugs
- 💾 **CONSULTAS SALVAS**: Salve suas consultas favoritas
- 📅 **PERÍODOS FLEXÍVEIS**: Predefinidos ou datas personalizadas
- ⬅️ **BOTÃO NA SIDEBAR**: Acesso rápido à ferramenta avançada

## v8.78 - DESIGN REFINADO
- 🎨 **DESIGN REFINADO**: Melhor espaçamento entre elementos
- ⬅️ **BOTÃO VOLTAR NA SIDEBAR**: Indica card ativo + volta fácil
- Link de compartilhamento mais compacto e funcional
- Visual mais limpo nas métricas do card
- Expanders fechados por padrão para menos poluição visual

## v8.6 - SIDEBAR REFATORADA
- 📱 **SIDEBAR REFATORADA**: Busca de card em destaque no topo
- 📤 **COMPARTILHAMENTO FUNCIONAL**: Link direto via query params
- Layout reorganizado: Logo → Busca → Filtros → Rodapé NINA
- URL persistente: `?card=SD-1234&projeto=SD`

## v8.5 - BUSCA DE CARD INDIVIDUAL
- 🔍 **BUSCA DE CARD INDIVIDUAL**: Pesquise qualquer card pelo ID
- Painel completo com todas as métricas do card
- Fator K individual, janela de validação, aging, lead time
- Flags de fluxo (criado/finalizado na sprint, fora período)
- Timeline completa, resumo executivo automático

## v8.4 - BACKLOG EXCLUSIVO
- Aba Backlog exclusiva para projeto PB (Product Backlog)
- Health Score do backlog, análise de aging, cards estagnados
- Recomendações automáticas de ação

## v8.0 - VERSÃO INICIAL
- Header com logo Nina + subtítulo explicativo do objetivo
- Tooltips/explicações em TODAS as métricas (FPY, DDP, Fator K, etc)
- Seções colapsáveis em todas as abas (toggle open/close)
- Listagens COMPLETAS (opção de ver todos os cards)
- Aba Histórico enriquecida com múltiplos gráficos
- Mais métricas em cada aba
- Aba QA (sem "Gargalos" no nome)
- Auto-load + Cache inteligente
- Cards clicáveis com links Jira
- Métricas Ellen: iniciado/finalizado sprint, fora período, hotfix/produto

---

## 🎯 CAMPOS MAPEADOS - JIRA NINA

| Campo | Custom Field | Propósito |
|-------|--------------|----------|
| Story Points | customfield_11257 | Estimativa principal |
| Story Points Alt | customfield_10016 | Alternativa de estimativa |
| Bugs Encontrados | customfield_11157 | Quantidade de bugs |
| Sprint | customfield_10020 | Sprint atual |
| Complexidade de Teste | customfield_11290 | Complexidade |
| QA Responsável | customfield_10487 | Owner QA |
| Produto | customfield_10102 | Produto associado |
