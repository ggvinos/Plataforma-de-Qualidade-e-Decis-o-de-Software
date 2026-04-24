# 🔐 ANÁLISE: IMPLEMENTAÇÃO DE PERFIS DE ACESSO POR TIME

**Documento de Viabilidade** | Data: 23/04/2026 | Total de Funcionários: 38

---

## 📋 RESUMO EXECUTIVO

Você quer implementar **controle de acesso por time**, permitindo que cada pessoa veja apenas dados relevantes (exemplo: suporte não vê DEV, DEV não vê QA). 

✅ **CONCLUSÃO: É TOTALMENTE VIÁVEL**

Existem **2 caminhos técnicos** dependendo de onde está armazenado o "time" de cada pessoa:

| Caminho | Complexidade | Tempo | Recomendação |
|---------|-------------|-------|--------------|
| **A: Jira tem dados de time** | ⭐⭐ Baixa | 12-19h | 🏆 Se Jira tiver campo |
| **B: Painel admin local** | ⭐⭐⭐ Média | 16-22h | ✅ Alternativa segura |

---

## 🔍 ACHADOS DA INVESTIGAÇÃO

### 1️⃣ Autenticação Atual
```
📊 Como funciona agora:
├─ Login: Email (nome.sobrenome@confirmationcall.com.br) + Senha
├─ Token: JWT via API ConfirmationCall
├─ Armazenamento: Cookie (30 dias)
├─ Sistema: APENAS captura email + nome
└─ Acesso: ❌ NENHUM controle - TODOS veem TUDO

👤 Dados do usuário disponíveis:
   ✅ Email: viniciosferreira@confirmationcall.com.br
   ✅ Nome: Viniciosferreira (extraído do email)
   ❌ Time/Departamento: NÃO CAPTURADO
   ❌ Cargo: NÃO CAPTURADO
```

### 2️⃣ Dados no Jira

O Jira armazena informações sobre os **cards/issues**, mas **precisa verificar**:

```
Campos que PODEM ter info de time:
├─ Assignee (desenvolvedor que pega a tarefa)
│  └─ Jira API pode retornar: departamento, grupo
├─ QA Responsável (customfield_10487)
│  └─ Pode ter metadata de grupo
├─ Reporter (quem criou o card)
│  └─ Pode ter departamento
└─ ❓ Campo customizado não mapeado?
   └─ Pode existir "Team", "Department", "Group"
```

**⚠️ AÇÃO NECESSÁRIA**: Verificar API do Jira se retorna departamento/time do usuário

---

## 3️⃣ CENÁRIOS DE IMPLEMENTAÇÃO

### 🎯 Cenário A: Jira retorna informação de Time

**SE você encontrar** que Jira API retorna `department`, `team` ou `groups`:

```python
# Fluxo simples:
1. Usuário loga
   → Email: dev1@confirmationcall.com.br
   
2. Buscar dados do usuário no Jira
   → Retorna: {name: "Dev1", department: "Development", team: "Backend"}
   
3. Armazenar no session_state + cookie
   
4. Ao carregar dados, filtrar por time
   → Jira: "project = SD AND assignee IN (dev1, dev2, dev3)"
   → Dashboard: Exibe apenas dados do seu time
```

**Vantagens**:
- ✅ Sincroniza automaticamente (fonte de verdade = Jira)
- ✅ Menos linhas de código
- ✅ Mais fácil manutenção futura

**Desvantagens**:
- ❌ Dependente de Jira (se Jira cair, acesso quebra)

---

### 🎯 Cenário B: Jira NÃO retorna informação

**SE Jira não tiver dados de departamento**, você precisaria de **Painel Administrativo Local**:

```python
# Fluxo com banco de dados local:

TABELA: perfis_acesso
┌─ email: dev1@confirmationcall.com.br
├─ time: "development"
├─ nivel_acesso: 1 (básico)
├─ projetos_visíveis: ["SD"]
├─ atualizado_em: 2026-04-23
└─ ativo: true

Painel Admin (apenas Liderança):
├─ Listar todos os 38 funcionários
├─ Atribuir time a cada um
├─ Definir nível de acesso
└─ Log de mudanças
```

**Vantagens**:
- ✅ Total controle manual
- ✅ Regras mais customizáveis
- ✅ Não depende do Jira
- ✅ Auditoria fácil

**Desvantagens**:
- ❌ Admin precisa manter atualizado
- ❌ Mais código para manter
- ❌ Pode desincronizar

---

## 4️⃣ ESTRUTURA DE TIMES PROPOSTA

Com 38 funcionários, sugerimos:

```
👨‍💼 LIDERANÇA (2-3 pessoas)
   └─ Acesso: TUDO (todas as abas, todos os dados)
   └─ Senha super-user para Painel Admin

💻 DESENVOLVIMENTO (10-12 pessoas)
   ├─ Abas visíveis: Dev, Visão Geral (filtrada)
   ├─ Vê: Cards de DEV, suas métricas, ranking
   └─ NÃO vê: QA, Suporte, dados de cliente

🧪 QA (8-10 pessoas)
   ├─ Abas visíveis: QA, Visão Geral (filtrada)
   ├─ Vê: Cards em validação, bugs, seu performance
   └─ NÃO vê: DEV detalhado, Suporte

📦 PRODUTO (4-6 pessoas)
   ├─ Abas visíveis: Produto, Liderança (executivo)
   ├─ Vê: Visão geral, métricas, roadmap
   └─ NÃO vê: Detalhes técnicos de dev/qa

📞 SUPORTE/SERVICE DESK (8-10 pessoas)
   ├─ Abas visíveis: Dashboard customizado (SD apenas)
   ├─ Vê: Tickets do suporte, resoluções
   └─ NÃO vê: DEV, QA, internals
```

---

## 5️⃣ IMPACTO NAS ABAS ATUAIS

```
ABA: VISÃO GERAL
   ANTES: Mostra dados de TODOS os projetos/pessoas
   DEPOIS: Mostra apenas do seu time
   Exemplo: Dev não vê KPIs de QA ou Suporte

ABA: DEV
   ANTES: Ranking de TODOS os devs
   DEPOIS: Ranking apenas do seu time
   Exemplo: Dev backend vê apenas backend devs

ABA: QA
   ANTES: Todos os QAs e bugs
   DEPOIS: Apenas seu time de QA
   Exemplo: QA mobile vê apenas bugs do mobile

ABA: PRODUTO
   ANTES: Todos os produtos
   DEPOIS: Seus produtos (se Produto) ou TUDO (Liderança)
   Exemplo: Produto de FP vê apenas FP

ABA: LIDERANÇA
   ANTES: Visível para TODOS (problema de segurança!)
   DEPOIS: Apenas Liderança (nivel_acesso >= 2)
   Exemplo: Dev não vê painel executivo
```

---

## 6️⃣ PRÓXIMAS AÇÕES (ANTES DE CODIFICAR)

### 🔍 INVESTIGAÇÃO URGENTE

**1. Verificar Jira** (você ou admin Jira)

```bash
# Testar qual informação vem da API
curl -H "Authorization: Bearer YOUR_JIRA_TOKEN" \
https://ninatecnologia.atlassian.net/rest/api/3/users

# Procurar na resposta por:
# - "department"
# - "team" 
# - "groups"
# - "organization"
# - "custom_fields"
```

Ou use a interface Jira:
- Admin > Usuários e Permissões
- Clique em um usuário
- Veja se há campo de "Departamento" ou "Time"

**2. Verificar ConfirmationCall**

- O endpoint `/api/user/loginjwt` que você usa para login...
- Retorna MAIS informações além do token?
- Existe endpoint que retorna departamento?

**3. Decisão com Liderança**

- Confirmar estrutura de times (6 opções acima, ou customizada)
- Definir permissões específicas
- Decidir: Jira (automático) vs Painel Admin (manual)

---

## 7️⃣ ESTIMATIVA DE TRABALHO

### Se usar Jira (Cenário A): **12-19 horas**

```
📊 Investigação Jira API
   └─ Verificar se retorna team/department: 2-4h
   
💾 Extrair dados na autenticação
   └─ Modificar modulos/confirmation_call_auth.py: 3-5h
   
🛡️ Criar middleware de acesso
   └─ Novo arquivo modulos/auth_perfil.py: 4-6h
   
✅ Testes de segurança
   └─ Garantir que filtros funcionam: 3-4h

TOTAL: 12-19 horas (~2-3 dias de trabalho)
```

### Se usar Painel Admin (Cenário B): **16-22 horas**

```
📊 Investigação (mesma): 2-4h

💾 Criar banco de dados local (SQLite)
   └─ Schema de perfis + migração: 2-3h
   
🎨 Desenvolver Painel Admin
   └─ Interface de atribuição (Streamlit): 6-8h
   
🛡️ Middleware de acesso (mesma)
   └─ modulos/auth_perfil.py: 4-6h
   
✅ Testes: 3-4h

TOTAL: 16-22 horas (~3-4 dias)
```

---

## 8️⃣ IMPACTO TÉCNICO

### Arquivos que SERÃO CRIADOS

```
✨ NOVOS:
├─ modulos/auth_perfil.py
│  └─ Carrega perfil do usuário
├─ modulos/acesso_control.py
│  └─ Middleware de verificação
├─ modulos/admin.py (se painel necessário)
│  └─ Interface de gestão
└─ data/perfis_acesso.db (se painel necessário)
   └─ SQLite com atribuições

🔧 MODIFICADOS:
├─ modulos/confirmation_call_auth.py
│  └─ Adiciona carregamento de perfil
├─ modulos/jira_api.py
│  └─ Adiciona filtro JQL por time
├─ modulos/abas.py
│  └─ Adiciona verificações de acesso
└─ app_modularizado.py
   └─ Middleware na renderização principal
```

### Performance

```
ANTES: Cada requisição retorna TODOS os 500+ cards
DEPOIS: 
   ├─ Dev vê ~60 cards (seu projeto)
   ├─ QA vê ~80 cards (seus validados)
   ├─ Suporte vê ~40 cards (seus tickets)
   └─ Liderança vê TODOS
   
BENEFÍCIO: ⚡ Mais rápido + menos dados trafegando
```

---

## 9️⃣ SEGURANÇA CONSIDERADA

```
✅ VALIDAÇÕES:
├─ Perfil verificado a cada requisição (não confiar em frontend)
├─ Token JWT + Perfil = ambos necessários
├─ Filtros aplicados no JQL (banco de dados)
├─ Sem "brechas" no frontend (nem localStorage)
└─ Logs de acesso (quem viu o quê)

⚠️ CUIDADOS:
├─ Admin panel apenas com autenticação dupla (senha)
├─ Histórico de mudanças auditável
├─ Backups regulares dos perfis
└─ Teste: Tentar bypassar acesso (penetration testing)
```

---

## 🎯 RECOMENDAÇÃO FINAL

```
IF Jira retorna department/team:
   → Use CENÁRIO A (automático, simples)
   → Tempo: 2-3 dias
   → Recomendado ⭐⭐⭐⭐⭐

ELSE:
   → Use CENÁRIO B (painel admin, controle)
   → Tempo: 3-4 dias
   → Seguro, sem dependências externas ⭐⭐⭐⭐

AMBOS:
   → Implementação robusta
   → Segurança nível empresarial
   → Escalável para 100+ usuários
```

---

## ✅ PRÓXIMO PASSO

### 🔍 INVESTIGAÇÃO (VOCÊ FAZER - 30 MINUTOS)

1. **Verificar Jira Admin** (5 min)
   - Menu > Configuração > Usuários e Permissões
   - Clicar em um usuário
   - Screenshot dos campos disponíveis

2. **Verificar ConfirmationCall** (10 min)
   - Documentação da API
   - Verificar resposta do `/api/user/loginjwt`
   - Se retorna mais dados

3. **Decidir com Liderança** (15 min)
   - Qual estrutura de times? (sugestão acima)
   - Jira ou Painel Admin?
   - Quem é admin?

### 📝 DEPOIS

- ✅ Passar investigação para mim
- ✅ Aprovação da estrutura de times
- ✅ Começamos a codificar

---

## 📞 DÚVIDAS FREQUENTES

**P: Quanto tempo até estar pronto?**
R: Após investigação: 2-4 dias. Rollout seguro: +1 semana.

**P: Quebra algum acesso existente?**
R: Não. Implementamos com feature flag. Ativa gradualmente.

**P: Pode quebrar Jira?**
R: Não. Apenas filtramos leitura. Jira permanece intacto.

**P: E se alguém tentar bypassar?**
R: Não consegue (filtro no backend, não frontend).

**P: Precisa de banco de dados?**
R: Só se Jira não tiver dados. Aí usamos SQLite local.

**P: Precisa mudar login?**
R: Não. Login continua igual. Apenas adicionamos "time" após login.

---

## 📊 MATRIZ DE DECISÃO

```
┌─────────────────────┬──────────────────┬──────────────────┐
│ Critério            │ Cenário A (Jira) │ Cenário B (Admin)│
├─────────────────────┼──────────────────┼──────────────────┤
│ Complexidade        │ ⭐⭐             │ ⭐⭐⭐          │
│ Tempo               │ 12-19h           │ 16-22h           │
│ Manutenção          │ Baixa            │ Média            │
│ Automatização       │ Alta             │ Manual           │
│ Dependências        │ Jira API         │ Nenhuma          │
│ Customização        │ Limitada         │ Alta             │
│ Recomendado?        │ SIM (se possível)│ SIM (fallback)   │
└─────────────────────┴──────────────────┴──────────────────┘
```

---

**⏰ Documento finalizado em 23/04/2026**
**📌 Awaiting: Investigação + Aprovação da Liderança**
