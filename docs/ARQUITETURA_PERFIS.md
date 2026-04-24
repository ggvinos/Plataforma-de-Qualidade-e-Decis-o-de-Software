# 🏗️ ARQUITETURA PROPOSTA - DIAGRAMA VISUAL

---

## 📊 FLUXO ATUAL vs PROPOSTO

### ❌ FLUXO ATUAL (Sem Controle de Acesso)

```
┌─────────────────────┐
│  Usuário loga       │
│  email + senha      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  API ConfirmationCall│
│  Retorna JWT        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Armazena em cookie │
│  (Email + Token)    │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────────────┐
│  Carrega TODOS os dados:     │
│  - SD (Suporte)              │
│  - DEV (Desenvolvimento)     │
│  - QA (Qualidade)            │
│  - PB (Produto)              │
│                              │
│  ⚠️ SEM FILTRO               │
│  ⚠️ Dev vê suporte           │
│  ⚠️ Suporte vê desenvolvimento
│  ⚠️ Inseguro!                │
└──────────────────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  Exibe no dashboard          │
│  TUDO para TODOS             │
└──────────────────────────────┘
```

---

### ✅ FLUXO PROPOSTO (Com Controle de Acesso)

```
┌──────────────────────┐
│   Usuário loga       │
│   email + senha      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────┐
│  API ConfirmationCall            │
│  Retorna: JWT                    │
│           (+ info de time, se tiver)
└──────────┬───────────────────────┘
           │
           ▼
   ┌───────────────────────────────┐
   │   NOVO STEP: Carregar Perfil  │ ← 🆕 AQUI ADICIONAMOS!
   │   ┌─────────────────────────┐ │
   │   │ De onde vem?            │ │
   │   │ Opção A: Jira API       │ │ ← Se Jira tem dados
   │   │ Opção B: BD Local       │ │ ← Se Jira não tem
   │   └─────────────────────────┘ │
   │                               │
   │   Dados carregados:           │
   │   - Email: user@...           │
   │   - Time: "development"       │
   │   - Nível: 1 (básico)         │
   │   - Projetos: ["SD", "QA"]    │
   └──────────┬────────────────────┘
              │
              ▼
   ┌──────────────────────────────────┐
   │  Armazena em cookie + session    │
   │  (Email + Token + PERFIL)        │ ← Novo campo
   └──────────┬─────────────────────────┘
              │
              ▼
   ┌──────────────────────────────────────┐
   │  NOVO: Middleware de Acesso          │ ← 🆕 VERIFICA AQUI!
   │                                      │
   │  if not pode_acessar(user, "aba"):  │
   │     mostra erro ou esconde aba       │
   └──────────┬──────────────────────────┘
              │
              ▼
┌────────────────────────────────────────┐
│ Carrega dados FILTRADOS:               │
│                                        │
│ Para Dev:                              │
│  - SD: Apenas cards de DEV             │
│  - DEV: Apenas ranking de devs         │
│  - NÃO vê: QA, Suporte, Produto       │
│                                        │
│ Para QA:                               │
│  - QA: Apenas seu time QA              │
│  - DEV: Visão geral (sem detalhes)    │
│  - NÃO vê: Suporte                     │
│                                        │
│ Para Liderança:                        │
│  - TUDO (todas as abas, sem filtro)   │
│                                        │
│ ✅ Seguro!                             │
│ ✅ Filtrado no backend (JQL)           │
└────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────┐
│  Exibe no dashboard                │
│  APENAS dados permitidos           │
│  Cada pessoa vê seu contexto       │
└────────────────────────────────────┘
```

---

## 🎯 CENÁRIO A: JIRA TEM DADOS

```
┌──────────────────────────────────────────┐
│  1. Usuário Autentica                    │
│     email@confirmationcall.com.br        │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  2. Buscar Perfil no Jira                │
│     GET /rest/api/3/users/{id}           │
│     Resposta:                            │
│     {                                    │
│       name: "dev1",                      │
│       email: "dev1@...",                 │
│       groups: ["developers"],        ← 📌
│       department: "Development"     ← 📌
│     }                                    │
└──────────┬──────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│  3. Mapear Time                          │
│     groups = ["developers"]              │
│     → time = "development"               │
│     → nivel_acesso = 1                   │
│     → projetos = ["SD", "QA"]            │
└──────────┬──────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│  4. Gerar JQL Filtrado                   │
│                                          │
│  Original:                               │
│    project = SD AND status != Done      │
│                                          │
│  Com filtro:                             │
│    project = SD AND                      │
│    status != Done AND                    │
│    assignee IN (dev1, dev2, dev3)    ← Devs do time
│                                          │
│  Result: Apenas 60 cards (vs 500)       │
└──────────┬──────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│  5. Cache + Renderizar                   │
│                                          │
│  session_state = {                       │
│    logged_in: true,                      │
│    user: "dev1@...",                     │
│    time: "development",              ← Novo!
│    nivel_acesso: 1,                 ← Novo!
│    perfil_expiracao: datetime(...)   ← Novo!
│  }                                       │
│                                          │
│  Dashboard vê perfil e filtra abas      │
└──────────────────────────────────────────┘

⏱️ Tempo: 12-19 horas
✅ Automático (sem admin manual)
```

---

## 🎯 CENÁRIO B: SEM DADOS NO JIRA

```
┌──────────────────────────────────────────┐
│  1. Usuário Autentica                    │
│     email@confirmationcall.com.br        │
└──────────┬───────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│  2. Buscar Perfil em BD Local            │
│     SELECT * FROM perfis_acesso          │
│     WHERE email = ?                      │
│     Resultado:                           │
│     {                                    │
│       email: "dev1@...",                 │
│       time: "development",           ← Atribuído manualmente
│       nivel_acesso: 1,                   │
│       projetos: ["SD", "QA"],            │
│       ativo: true                        │
│     }                                    │
└──────────┬──────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│  3. Verificar Permissões                 │
│     if time == "development":            │
│       pode_ver = ["SD", "QA"]            │
│       nao_pode_ver = ["suporte", "produto"]
│                                          │
│     if nivel_acesso < 2:                 │
│       esconde = ["admin"]                │
└──────────┬──────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│  4. Renderizar com Restrições            │
│                                          │
│  ✅ Mostra:                              │
│     - Aba SD (projeto seu)               │
│     - Aba Dev (seu time)                 │
│                                          │
│  ❌ Esconde:                             │
│     - Aba Suporte (outro projeto)        │
│     - Aba Admin (não é admin)            │
│     - Aba Liderança (sem permissão)     │
└──────────┬──────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│  5. Painel Admin (se admin)              │
│                                          │
│  Apenas usuários com                     │
│  nivel_acesso >= 2 veem:                │
│                                          │
│  - Lista dos 38 funcionários             │
│  - Atribuir time a cada um               │
│  - Definir nível de acesso               │
│  - Log de mudanças                       │
│                                          │
│  Interface Streamlit simples             │
└──────────────────────────────────────────┘

⏱️ Tempo: 16-22 horas
✅ Total controle manual
✅ Sem dependência do Jira
⚠️ Admin precisa manter atualizado
```

---

## 📁 ESTRUTURA DE DIRETÓRIOS

### NOVO layout

```
projeto/
├── modulos/
│   ├── __init__.py
│   ├── confirmation_call_auth.py (MODIFICADO)
│   │   └─ Adiciona: carregar_perfil()
│   │
│   ├── auth_perfil.py (NOVO)
│   │   ├─ get_perfil_usuario()
│   │   ├─ validar_acesso_aba()
│   │   ├─ filtrar_jql_por_time()
│   │   └─ salvar_perfil_cache()
│   │
│   ├── acesso_control.py (NOVO)
│   │   ├─ middleware_acesso()
│   │   ├─ pode_acessar()
│   │   ├─ pode_ver_aba()
│   │   └─ gerar_filtro_jql()
│   │
│   ├── admin.py (NOVO - se usar Cenário B)
│   │   ├─ painel_admin()
│   │   ├─ listar_usuarios()
│   │   ├─ editar_perfil_usuario()
│   │   ├─ atribuir_time()
│   │   └─ log_mudancas()
│   │
│   ├── jira_api.py (MODIFICADO)
│   │   └─ buscar_dados_jira_cached() agora filtra por time
│   │
│   ├── abas.py (MODIFICADO)
│   │   └─ Cada aba verifica acesso antes de renderizar
│   │
│   └── [arquivos originais...]
│
├── data/ (NOVO - se usar Cenário B)
│   ├── perfis_acesso.db (NOVO - SQLite)
│   │   └─ Tabelas:
│   │      ├─ usuarios (email, nome, ativo)
│   │      ├─ perfis (usuario_id, time, nivel_acesso, projetos)
│   │      └─ logs_acesso (usuario_id, acao, data)
│   │
│   └── schema.sql (NOVO)
│
├── app_modularizado.py (MODIFICADO)
│   └─ Adiciona middleware de acesso no início
│
├── .streamlit/
│   └─ secrets.toml (verificar se tem)
│
├── requirements.txt (SEM MUDANÇAS)
│
└── DOCUMENTAÇÃO/
    ├── ANALISE_PERFIS_ACESSO.md (NOVO) ✅ Criado
    ├── GUIA_INVESTIGACAO_PERFIS.md (NOVO) ✅ Criado
    └── ARQUITETURA_PERFIS.md (NOVO - este arquivo)
```

---

## 🔐 FLUXO DE SEGURANÇA

```
┌────────────────────────────────────────────┐
│  REQUISIÇÃO: Carregar Aba DEV              │
└────────────────┬───────────────────────────┘
                 │
                 ▼
    ┌─────────────────────────────┐
    │  ✅ VALIDAÇÃO 1             │
    │  Token JWT válido?          │
    │  ✅ SIM → Continua          │
    │  ❌ NÃO → Redireciona login │
    └─────────────┬───────────────┘
                  │
                  ▼
    ┌─────────────────────────────┐
    │  ✅ VALIDAÇÃO 2             │
    │  Perfil em cache?           │
    │  ✅ SIM → Valida expiração  │
    │  ❌ NÃO → Carrega do BD     │
    └─────────────┬───────────────┘
                  │
                  ▼
    ┌─────────────────────────────────┐
    │  ✅ VALIDAÇÃO 3                 │
    │  Usuário pode ver "aba_dev"?    │
    │                                 │
    │  if time == "development":      │
    │    ✅ SIM → Vai para Jira       │
    │  else:                          │
    │    ❌ NÃO → Mostra erro         │
    └─────────────┬───────────────────┘
                  │
                  ▼
    ┌─────────────────────────────────┐
    │  ✅ VALIDAÇÃO 4                 │
    │  Montar JQL filtrado            │
    │                                 │
    │  jql = "project=SD AND          │
    │         assignee IN (dev1,dev2) │
    │         AND [outros filtros]"   │
    └─────────────┬───────────────────┘
                  │
                  ▼
    ┌─────────────────────────────────┐
    │  ✅ VALIDAÇÃO 5                 │
    │  Buscar dados do Jira           │
    │  com JQL filtrado               │
    │                                 │
    │  Apenas 60 cards (não 500!)     │
    └─────────────┬───────────────────┘
                  │
                  ▼
    ┌─────────────────────────────────┐
    │  ✅ VALIDAÇÃO 6                 │
    │  Renderizar no Frontend         │
    │                                 │
    │  ✅ Mostrar apenas dados        │
    │     permitidos pelo perfil      │
    └─────────────────────────────────┘

⏱️ Total: ~500ms (com cache ~100ms)
🔒 Seguro em 6 camadas!
```

---

## 📊 TABELA DE ACESSO PROPOSTA

### Por Papel/Time

```
┌─────────────┬──────────────┬──────────┬─────────────────┐
│ Time/Papel  │ Nível Acesso │ Abas VE  │ Dados Vistos     │
├─────────────┼──────────────┼──────────┼─────────────────┤
│ Dev         │ 1 (básico)   │ Visão,   │ Apenas dev do    │
│ Development │              │ Dev, QA* │ time             │
│             │              │          │ (* filtrado)     │
├─────────────┼──────────────┼──────────┼─────────────────┤
│ QA          │ 1 (básico)   │ Visão,   │ Apenas QA do     │
│ Quality     │              │ QA, Dev* │ time             │
│ Assurance   │              │          │ (* filtrado)     │
├─────────────┼──────────────┼──────────┼─────────────────┤
│ Suporte     │ 1 (básico)   │ Visão,   │ Apenas tickets   │
│ Service     │              │ SD*      │ do suporte       │
│ Desk        │              │          │                  │
├─────────────┼──────────────┼──────────┼─────────────────┤
│ Produto     │ 2 (avançado) │ Todas    │ Visão executiva  │
│ Product     │              │ exceto   │ (sem detalhes    │
│             │              │ Admin    │ de dev)          │
├─────────────┼──────────────┼──────────┼─────────────────┤
│ Liderança   │ 3 (admin)    │ TODAS    │ TUDO SEM FILTRO  │
│ Tech Lead/  │              │ +Admin   │ (visão completa) │
│ Manager     │              │          │                  │
└─────────────┴──────────────┴──────────┴─────────────────┘

* = Filtrado (dados aparecem mas com restrições)
```

---

## ⏰ TIMELINE DE IMPLEMENTAÇÃO

```
┌──────────────────────────────────────────────────────────┐
│  FASE 0: Investigação (VOCÊ fazer)                       │
│  ├─ Verificar Jira: 30 min                               │
│  ├─ Verificar ConfirmationCall: 30 min                   │
│  ├─ Decidir com Liderança: 1 hora                        │
│  └─ Compartilhar resultados: 30 min                      │
│  ⏱️ Total: 2-3 HORAS (pode fazer hoje!)                  │
└────────┬─────────────────────────────────────────────────┘
         │
         ▼ (depois de aprovação)
┌──────────────────────────────────────────────────────────┐
│  FASE 1: Setup (1 dia)                                   │
│  ├─ Criar estrutura de diretórios                        │
│  ├─ Criar BD (se Cenário B)                              │
│  └─ Setup inicial de código                              │
│  ⏱️ Estimado: 4-6 HORAS                                  │
└────────┬─────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│  FASE 2: Autenticação + Perfil (2 dias)                  │
│  ├─ Modificar auth para carregar perfil                  │
│  ├─ Criar modulos/auth_perfil.py                         │
│  ├─ Testes de autenticação                               │
│  └─ Validar cache de perfil                              │
│  ⏱️ Estimado: 8-10 HORAS                                 │
└────────┬─────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│  FASE 3: Middleware + Filtros (2 dias)                   │
│  ├─ Criar modulos/acesso_control.py                      │
│  ├─ Implementar filtros JQL                              │
│  ├─ Validar acesso por aba                               │
│  └─ Testes de segurança                                  │
│  ⏱️ Estimado: 8-10 HORAS                                 │
└────────┬─────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│  FASE 4: Painel Admin (1-2 dias) [SE CENÁRIO B]          │
│  ├─ Criar modulos/admin.py                               │
│  ├─ Interface de gestão de usuários                      │
│  ├─ Testes com dados reais                               │
│  └─ Documentação de uso                                  │
│  ⏱️ Estimado: 6-8 HORAS                                  │
└────────┬─────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│  FASE 5: Testes + Deploy (1 dia)                         │
│  ├─ Testes unitários                                     │
│  ├─ Testes de integração                                 │
│  ├─ Testes de segurança (penetration)                    │
│  ├─ Deploy em homolog                                    │
│  └─ Deploy em produção                                   │
│  ⏱️ Estimado: 6-8 HORAS                                  │
└──────────────────────────────────────────────────────────┘

📊 CRONOGRAMA TOTAL:
├─ Cenário A (Jira): 2-3 dias
├─ Cenário B (Admin): 3-4 dias
└─ Com testes robustos: +1 dia
```

---

**✅ DOCUMENTAÇÃO COMPLETA**

Agora você tem:
1. **ANALISE_PERFIS_ACESSO.md** - Análise estratégica
2. **GUIA_INVESTIGACAO_PERFIS.md** - Como verificar dados
3. **ARQUITETURA_PERFIS.md** - Este arquivo (visual)

Próximo passo: Fazer a investigação! 🔍
