# 🎯 ÁRVORE DE DECISÃO - PERFIS DE ACESSO

> Siga este diagrama para tomar a decisão correta

---

## 📊 DECISÃO PRINCIPAL

```
┌─────────────────────────────────────────────────────────┐
│  PERGUNTA CRÍTICA:                                      │
│  "O Jira retorna informação de team/department?"        │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼ SIM                   ▼ NÃO
    ┌─────────┐            ┌─────────┐
    │ CENÁRIO │            │ CENÁRIO │
    │    A    │            │    B    │
    │ (JIRA)  │            │ (ADMIN) │
    └────┬────┘            └────┬────┘
         │                      │
         ▼                      ▼
    ⭐⭐ Baixo           ⭐⭐⭐ Médio
    12-19h             16-22h
    Automático         Manual
    SEM banco BD       COM banco BD
    
    👇                 👇
    
    VÁ PARA             VÁ PARA
    PRÓXIMA SEÇÃO       PRÓXIMA SEÇÃO
```

---

## 🔍 COMO DESCOBRIR: CENÁRIO A ou B?

### ⚡ TESTE RÁPIDO (5 MINUTOS)

Execute no terminal:

```bash
# Copie e cole isso no terminal:

curl -H "Authorization: Bearer SEU_TOKEN" \
  https://ninatecnologia.atlassian.net/rest/api/3/myself | grep -E "(team|department|group|organization)"

# Se retornar algo → CENÁRIO A ✅
# Se retornar vazio → CENÁRIO B ❌
```

---

## ✅ CENÁRIO A: JIRA TEM DADOS (Recomendado)

```
QUANDO USAR:
├─ Jira retorna "team" ou "department"
├─ ConfirmationCall retorna info de time
└─ Você quer solução automática

COMO FUNCIONA:
├─ 1. Usuário loga
├─ 2. Buscar profile do Jira
├─ 3. Extrair team/department
├─ 4. Filtrar dados por time
└─ 5. Renderizar com restrições

VANTAGENS:
✅ Simples (menos código)
✅ Automático (sem admin)
✅ Sincroniza automaticamente
✅ Fonte de verdade = Jira
✅ Fácil manutenção

DESVANTAGENS:
❌ Depende do Jira
❌ Se Jira cair, acesso quebra
❌ Menos customizável

TEMPO:
⏱️ 12-19 horas (~2 dias)

ESTRUTURA DE DIRETÓRIOS:
✨ NOVOS:
   ├─ modulos/auth_perfil.py
   ├─ modulos/acesso_control.py
   └─ (2 arquivos)

🔧 MODIFICADOS:
   ├─ modulos/confirmation_call_auth.py
   ├─ modulos/jira_api.py
   ├─ modulos/abas.py
   └─ app_modularizado.py

📦 BANCO DE DADOS:
   ❌ NÃO precisa!

PRÓXIMO PASSO:
→ Ir para seção "IMPLEMENTAÇÃO CENÁRIO A"
```

---

## ✅ CENÁRIO B: PAINEL ADMIN LOCAL

```
QUANDO USAR:
├─ Jira NÃO retorna team/department
├─ Você quer mais controle
├─ Pode designar um admin
└─ Quer regras customizáveis

COMO FUNCIONA:
├─ 1. Admin cria BD local (SQLite)
├─ 2. Admin atribui email → team
├─ 3. Usuário loga
├─ 4. Carregar perfil do BD
├─ 5. Filtrar dados por time
└─ 6. Renderizar com restrições

VANTAGENS:
✅ Total controle manual
✅ Não depende do Jira
✅ Regras very customizáveis
✅ Auditoria fácil
✅ Funciona offline

DESVANTAGENS:
❌ Mais código
❌ Admin precisa manter atualizado
❌ Pode desincronizar se Jira muda
❌ Mais complexo

TEMPO:
⏱️ 16-22 horas (~3 dias)

ESTRUTURA DE DIRETÓRIOS:
✨ NOVOS:
   ├─ modulos/auth_perfil.py
   ├─ modulos/acesso_control.py
   ├─ modulos/admin.py ← PAINEL ADMIN
   └─ data/perfis_acesso.db ← BD LOCAL

🔧 MODIFICADOS:
   ├─ modulos/confirmation_call_auth.py
   ├─ modulos/jira_api.py
   ├─ modulos/abas.py
   └─ app_modularizado.py

📦 BANCO DE DADOS:
   ✅ SIM! SQLite local
   └─ Tabelas: usuarios, perfis, logs

PRÓXIMO PASSO:
→ Ir para seção "IMPLEMENTAÇÃO CENÁRIO B"
```

---

## 🚀 IMPLEMENTAÇÃO CENÁRIO A

```
┌────────────────────────────────────────┐
│  SE VOCÊ ESCOLHEU CENÁRIO A:           │
│  "Jira retorna team/department"        │
└────────────────────────────────────────┘

PASSO 1: Análise
└─ Verificar que campos exatamente retorna Jira
   └─ department? team? groups?
   └─ Salvar response JSON

PASSO 2: Criar modulos/auth_perfil.py
├─ Função: get_perfil_usuario(email, token_jira)
│  └─ Chama API Jira /users/{id}
│  └─ Extrai team do JSON
│  └─ Mapeia para perfil padrão
│
├─ Função: mapear_time_para_perfil(time_jira)
│  └─ Converte "developers" → "development"
│  └─ Define projetos visíveis
│  └─ Define nível de acesso
│
└─ Função: salvar_perfil_cache(perfil)
   └─ Armazena em session_state
   └─ Define expiração

PASSO 3: Modificar modulos/confirmation_call_auth.py
└─ Após login bem-sucedido:
   ├─ Chamar get_perfil_usuario()
   ├─ Armazenar em session_state
   └─ Incluir em cookie (encrypted)

PASSO 4: Criar modulos/acesso_control.py
├─ Função: pode_acessar_aba(usuario, aba)
│  └─ Verifica se time tem permissão
│
├─ Função: gerar_jql_filtrado(usuario, jql_base)
│  └─ Adiciona filtro: AND assignee IN (team_members)
│  └─ Retorna JQL completo
│
└─ Função: middleware_acesso(usuario)
   └─ Verifica a cada requisição
   └─ Nega acesso se não permitido

PASSO 5: Modificar modulos/jira_api.py
└─ Na função buscar_dados_jira_cached():
   ├─ Receber usuario_perfil como parâmetro
   ├─ Chamar gerar_jql_filtrado()
   └─ Buscar com JQL filtrado

PASSO 6: Modificar modulos/abas.py
└─ No início de cada aba:
   ├─ Verificar pode_acessar_aba()
   ├─ Se SIM: Renderizar com dados filtrados
   └─ Se NÃO: Mostrar mensagem de acesso negado

PASSO 7: Modificar app_modularizado.py
└─ Logo após verificar_e_bloquear():
   ├─ Chamar middleware_acesso()
   ├─ Se acesso negado: Mostrar página de erro
   └─ Se OK: Continuar normal

TESTES:
├─ Fazer login como DEV
│  └─ Verificar que vê apenas cards de DEV
├─ Fazer login como QA
│  └─ Verificar que vê apenas cards de QA
├─ Fazer login como ADMIN
│  └─ Verificar que vê TODOS os cards
└─ Tentar bypassar (dev acessando /qa)
   └─ Verificar que não consegue

TEMPO ESTIMADO:
Dias 1-2: Implementação
Dia 3: Testes + adjusts
Total: 12-19 horas
```

---

## 🚀 IMPLEMENTAÇÃO CENÁRIO B

```
┌────────────────────────────────────────┐
│  SE VOCÊ ESCOLHEU CENÁRIO B:           │
│  "Painel Admin Local"                  │
└────────────────────────────────────────┘

PASSO 1: Criar banco de dados
└─ Criar: data/perfis_acesso.db (SQLite)
   ├─ Tabela: usuarios
   │  ├─ id (PK)
   │  ├─ email (UNIQUE)
   │  ├─ nome
   │  ├─ ativo (bool)
   │  └─ criado_em
   │
   ├─ Tabela: perfis
   │  ├─ id (PK)
   │  ├─ usuario_id (FK)
   │  ├─ time (dev, qa, suporte, produto, lideranca)
   │  ├─ nivel_acesso (1-3)
   │  ├─ projetos_visíveis (JSON)
   │  ├─ atualizado_em
   │  └─ atualizado_por
   │
   └─ Tabela: logs_acesso
      ├─ id (PK)
      ├─ usuario_id (FK)
      ├─ acao (login, view_aba, mudança_perfil)
      ├─ dados (JSON com contexto)
      └─ data_hora

PASSO 2: Criar modulos/auth_perfil.py
├─ Função: conectar_bd()
│  └─ Abre conexão SQLite
│
├─ Função: get_perfil_usuario(email)
│  └─ SELECT * FROM perfis WHERE usuario_id = (SELECT id FROM usuarios WHERE email = ?)
│
├─ Função: criar_usuario(email, nome)
│  └─ INSERT INTO usuarios
│
├─ Função: atualizar_perfil(usuario_id, time, nivel)
│  └─ UPDATE perfis
│
└─ Função: registrar_log(usuario_id, acao, dados)
   └─ INSERT INTO logs_acesso

PASSO 3: Criar modulos/admin.py
├─ Função: tela_admin()
│  └─ Só para usuarios com nivel_acesso >= 2
│
├─ Seção 1: Listar todos os 38 usuários
│  └─ Tabela: Email | Nome | Time | Nível | Ações
│
├─ Seção 2: Editar perfil
│  ├─ Seletor: Email
│  ├─ Input: Nome
│  ├─ Radio: Time (dev, qa, suporte, produto, lideranca)
│  ├─ Radio: Nível (1, 2, 3)
│  └─ Botão: Salvar
│
├─ Seção 3: Importar emails
│  └─ Ler lista dos 38 funcionários (se tiver)
│  └─ Criar usuários em batch
│
└─ Seção 4: Logs
   └─ Tabela: Usuário | Ação | Data | Detalhes

PASSO 4: Criar modulos/acesso_control.py
├─ Função: pode_acessar_aba(usuario, aba)
│  └─ SELECT * FROM perfis WHERE usuario_id = ?
│  └─ Verificar se aba está em projetos_visíveis
│
├─ Função: gerar_jql_filtrado(usuario, jql_base)
│  └─ Similar ao Cenário A mas com dados do BD
│
└─ Função: middleware_acesso(usuario)
   └─ Valida a cada requisição

PASSO 5-7: Mesmo que Cenário A
└─ Modificar jira_api.py, abas.py, app_modularizado.py
└─ Mesma arquitetura de acesso

TESTES:
├─ Fazer login como Admin
│  └─ Verificar que acessa painel admin
│  └─ Editar um usuário
│  └─ Verificar que mudança reflete
├─ Fazer login como usuário editado
│  └─ Verificar novo time/acesso
├─ Tentar acessar admin como não-admin
│  └─ Verificar que nega acesso
└─ Testes de segurança (SQL injection, etc)

TEMPO ESTIMADO:
Dia 1: BD + admin.py (8 horas)
Dia 2: Integração + testes (8 horas)
Total: 16 horas
```

---

## 🎓 ESTRUTURA DE TIMES - DEFINIR COM LIDERANÇA

```
Defina com sua liderança qual configuração usar:

OPÇÃO 1: Simples (Recomendada para começar)
├─ Admin (2-3): Tudo
├─ Dev (12): Vê Dev + Visão Geral
├─ QA (10): Vê QA + Visão Geral
├─ Outros (13): Vê apenas sua aba
└─ Total: 38

OPÇÃO 2: Granular
├─ Liderança (3): Tudo + Painel Admin
├─ Dev Backend (6): Vê Dev (backend filter)
├─ Dev Frontend (6): Vê Dev (frontend filter)
├─ QA Automação (5): Vê QA (automação filter)
├─ QA Manual (5): Vê QA (manual filter)
├─ Suporte Nível 1 (4): Vê Suporte (N1 filter)
├─ Suporte Nível 2 (2): Vê Suporte (N2 filter)
└─ Total: 38

OPÇÃO 3: Sua Proposta
└─ Customizado conforme necessidade

Para implementar:
→ Defina no documento INVESTIGACAO_RESULTADOS.md
→ Compartilhe comigo
→ Começamos a codificar!
```

---

## ✅ CHECKLIST - ANTES DE COMEÇAR

### Investigação (Você fazer)
- [ ] Ler os 3 documentos (ANALISE, GUIA, ARQUITETURA)
- [ ] Executar testes do GUIA_INVESTIGACAO_PERFIS.md
- [ ] Preencher INVESTIGACAO_RESULTADOS.md
- [ ] Decidir: Cenário A ou B?
- [ ] Definir estrutura de times com liderança

### Implementação (Eu fazer, com sua aprovação)
- [ ] Criar estrutura de diretórios
- [ ] Escrever modulos/auth_perfil.py
- [ ] Escrever modulos/acesso_control.py
- [ ] Modificar confirmation_call_auth.py
- [ ] Modificar jira_api.py
- [ ] Modificar abas.py
- [ ] Modificar app_modularizado.py
- [ ] Testes completos
- [ ] Deploy homolog
- [ ] Deploy produção

### Rollout (Você + Liderança)
- [ ] Comunicado a todos os 38 usuários
- [ ] Atribuição de times (Cenário B)
- [ ] Testes com dados reais
- [ ] Hotfixes conforme necessário

---

## 🚨 AVISOS IMPORTANTES

```
⚠️ NÃO TENTE CODIFICAR ANTES:
   ❌ Antes de completar investigação
   ❌ Antes de aprovação de liderança
   ❌ Sem decidir Cenário A ou B
   ❌ Sem definir estrutura de times

✅ FAÇA:
   ✅ Ler análise (vai entender bem melhor)
   ✅ Fazer investigação (30 min-1h)
   ✅ Conversar com liderança (15 min)
   ✅ Depois chamar para começar

⏱️ TIMING:
   Investigação: Hoje ou amanhã
   Aprovação: Amanhã
   Implementação: A partir de terça
```

---

## 📊 SUMÁRIO VISUAL

```
QUAL CENÁRIO?
│
├─ Jira TEM dados de time?
│  └─ SIM → CENÁRIO A (12-19h, automático) ⭐
│  └─ NÃO → CENÁRIO B (16-22h, admin)
│
QUAL ESTRUTURA?
│
├─ 2-3 Liderança (tudo)
├─ 10-12 Dev (apenas dev)
├─ 8-10 QA (apenas qa)
├─ 4-6 Produto (executivo)
└─ 8-10 Suporte (apenas suporte)
│
IMPLEMENTAÇÃO
│
├─ Criar modulos/auth_perfil.py
├─ Criar modulos/acesso_control.py
├─ Criar modulos/admin.py (se Cenário B)
├─ Modificar 4 arquivos
└─ Testar + Deploy
```

---

## 🎯 PRÓXIMO PASSO

**HOJE OU AMANHÃ:**
1. Ler os 3 documentos (1 hora)
2. Executar testes investigação (30 min)
3. Responder: A ou B?
4. Compartilhar com liderança

**DEPOIS:**
5. Chama para comenzar a codificar! 🚀

---

**Criado em**: 23/04/2026
**Status**: Pronto para Decisão
**Próxima Conversa**: Após investigação
