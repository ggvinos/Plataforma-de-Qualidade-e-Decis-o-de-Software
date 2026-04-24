# 📊 NinaDash v8.82 - Guia de Modularização

## 🎯 Introdução

O NinaDash foi **refatorado de um arquivo único (10.000+ linhas) para uma estrutura modularizada** que facilita manutenção, testes e expansão.

Como você é QA (não dev), esta estrutura foi criada para ser **intuitiva e fácil de navegar por domínio de negócio**.

---

## 📁 Estrutura de Pastas

```
Jira Dasboard/
├── app_modularizado.py          ← NOVO: Arquivo principal (orquestrador)
├── app.py                       ← ANTIGO: Versão monolítica (backup)
├── requirements.txt             ← Dependências Python
├── README.md                    ← Este arquivo
│
├── config/                      ← ⚙️  CONFIGURAÇÕES GLOBAIS
│   ├── __init__.py
│   └── settings.py              (constantes, tooltips, status, mapeamentos)
│
├── auth/                        ← 🔐 AUTENTICAÇÃO
│   ├── __init__.py
│   └── login.py                 (login/logout, cookies, validações)
│
├── integrations/                ← 🔗 INTEGRAÇÕES EXTERNAS
│   ├── __init__.py
│   └── jira_api.py              (API Jira, cache, busca de dados)
│
├── domain/                      ← 📊 LÓGICA DE NEGÓCIO (CORE)
│   ├── __init__.py
│   └── data_processing.py       (processamento, métricas, análises)
│
├── ui/                          ← 🎨 INTERFACE E COMPONENTES
│   ├── __init__.py
│   ├── components.py            (cards, badges, ícones - em breve)
│   └── pages/                   (páginas específicas - em breve)
│       ├── __init__.py
│       ├── dashboard.py         (Visão Geral)
│       ├── qa.py                (QA)
│       ├── dev.py               (Dev)
│       ├── governance.py        (Governança)
│       ├── product.py           (Produto)
│       ├── history.py           (Histórico)
│       ├── leadership.py        (Liderança)
│       └── custom.py            (Meu Dashboard)
│
└── utils/                       ← 🛠️  UTILITÁRIOS
    └── __init__.py              (helpers, validadores)
```

---

## 🧩 Módulos Explicados

### 1️⃣ **config/** - Configurações Globais

**Responsabilidade:** Armazenar todas as constantes, tooltips e mapeamentos usados em toda a aplicação.

**O que contém:**
- `TOOLTIPS` - Explicações de cada métrica (FK, DDP, FPY, etc)
- `JIRA_BASE_URL` - URL do Jira
- `CUSTOM_FIELDS` - Mapeamento de campos customizados
- `STATUS_FLOW` - Fluxos de status (backlog, desenvolvimento, etc)
- `STATUS_NOMES` e `STATUS_CORES` - Nomes formatados e cores de status

**Como usar:**
```python
from config import TOOLTIPS, STATUS_FLOW, CUSTOM_FIELDS

# Acessar tooltip de uma métrica
fk_info = TOOLTIPS["fator_k"]  

# Acessar campo customizado
bugs_field = CUSTOM_FIELDS["bugs_encontrados"]  # customfield_11157

# Traduzir um status
status_nome = STATUS_NOMES[status_cat]  # "💻 Desenvolvimento"
```

---

### 2️⃣ **auth/** - Autenticação

**Responsabilidade:** Gerenciar login/logout de usuários com persistência em cookies.

**O que contém:**
- `verificar_login()` - Verifica se usuário está autenticado
- `fazer_login()` - Realiza login corporativo
- `fazer_logout()` - Faz logout e limpa dados
- `validar_email_corporativo()` - Valida domínio @confirmationcall.com.br

**Como usar:**
```python
from auth import verificar_login, fazer_login, fazer_logout

# Verificar se está logado
if not verificar_login():
    st.stop()

# Fazer logout
if st.button("Logout"):
    fazer_logout()
    st.rerun()
```

---

### 3️⃣ **integrations/jira_api.py** - Integração Jira

**Responsabilidade:** Comunicação com API do Jira (busca, cache, processamento).

**O que contém:**
- `buscar_dados_jira_cached()` - Busca issues com cache de 5 min
- `buscar_card_especifico()` - Carrega um card com links, comentários e histórico
- `extrair_historico_transicoes()` - Extrai timeline de mudanças de status
- `extrair_texto_adf()` - Converte ADF (Atlassian Document Format) em texto plano

**Como usar:**
```python
from integrations import buscar_dados_jira_cached, buscar_card_especifico

# Buscar dados com cache
issues, ultima_atualizacao = buscar_dados_jira_cached(
    projeto="SD",
    jql='project = SD AND status != "Concluído"'
)

# Buscar um card específico
issue, links, comentarios, historico = buscar_card_especifico("SD-1234")
```

---

### 4️⃣ **domain/data_processing.py** - Lógica de Negócio

**Responsabilidade:** Processamento de dados, cálculo de métricas e análises (sem Streamlit!).

**O que contém:**
- `processar_issues()` - Converte issues do Jira em DataFrame com métricas
- `calcular_fator_k()` - Calcula maturidade (SP / Bugs + 1)
- `calcular_ddp()` - Defect Detection Percentage
- `calcular_fpy()` - First Pass Yield
- `calcular_lead_time()` - Lead time médio e percentis
- `analisar_dev_detalhado()` - Análise completa de um desenvolvedor
- `calcular_concentracao_conhecimento()` - Identifica concentração de conhecimento

**Como usar:**
```python
from domain import processar_issues, calcular_fator_k, calcular_ddp

# Processar lista de issues
df = processar_issues(issues)

# Calcular métricas
fk = calcular_fator_k(sp=10, bugs=2)  # 3.33

ddp = calcular_ddp(df)  # {'valor': 85.5, 'bugs_qa': 17}
fpy = calcular_fpy(df)  # {'valor': 92.3, 'sem_bugs': 12, 'total': 13}
```

---

### 5️⃣ **ui/** - Interface (Em Desenvolvimento)

**Responsabilidade:** Componentes reutilizáveis e páginas específicas.

**Será dividido em:**
- `components.py` - Cards, badges, ícones, widgets reutilizáveis
- `pages/dashboard.py` - Página "Visão Geral"
- `pages/qa.py` - Página "QA"
- `pages/dev.py` - Página "Dev"
- `pages/governance.py` - Página "Governança"
- ... (outras abas)

---

### 6️⃣ **utils/** - Utilitários

**Responsabilidade:** Funções auxiliares gerais.

**Será usado para:**
- Validações comuns
- Formatadores de dados
- Helpers reutilizáveis

---

## 🚀 Como Usar

### Opção 1: Usar a Versão Modularizada (Recomendado)

```bash
streamlit run app_modularizado.py
```

### Opção 2: Manter a Versão Original

O arquivo `app.py` original ainda existe como backup. Você pode voltar a usá-lo a qualquer momento.

---

## 📝 Exemplo de Uso Completo

```python
import streamlit as st
from config import STATUS_NOMES, TOOLTIPS
from auth import verificar_login
from integrations import buscar_dados_jira_cached
from domain import processar_issues, calcular_fator_k, calcular_ddp

# 1. Verificar autenticação
if not verificar_login():
    st.stop()

# 2. Buscar dados do Jira
issues, _ = buscar_dados_jira_cached("SD", 'project = SD')

# 3. Processar em DataFrame
df = processar_issues(issues)

# 4. Calcular métricas
df_sd = df[df['status_cat'] == 'done']
metricas = {
    'fator_k': calcular_fator_k(df_sd['sp'].sum(), df_sd['bugs'].sum()),
    'ddp': calcular_ddp(df_sd),
}

# 5. Exibir com nomes amigáveis
st.metric("Fator K", metricas['fator_k'])
st.info(TOOLTIPS['fator_k']['descricao'])
```

---

## ✨ Benefícios da Modularização

| Aspecto | Antes (Monolítico) | Depois (Modularizado) |
|---------|------------------|----------------------|
| **Tamanho** | 10.000+ linhas em 1 arquivo | ~300-500 linhas por módulo |
| **Navegação** | Difícil encontrar funções | Fácil: estrutura por domínio |
| **Manutenção** | Alto risco de quebrar tudo | Baixo: mudanças isoladas |
| **Reutilização** | Código espalhado | Funções claras e reutilizáveis |
| **Testes** | Difícil testar tudo junto | Fácil: módulos independentes |
| **Onboarding** | QA perde tempo procurando | QA entende estrutura rápido |

---

## 🔄 Próximos Passos

1. **Criar páginas em `ui/pages/`** - Cada aba será um arquivo Python
2. **Criar componentes em `ui/components.py`** - Cards, badges reutilizáveis
3. **Expandir testes** - Cada módulo pode ser testado isoladamente
4. **Otimizar cache** - Estratégia de cache por módulo

---

## 📞 Perguntas Comuns (QA)

**P: Onde fica a métrica Fator K?**  
R: Em `domain/data_processing.py` - função `calcular_fator_k()`

**P: Como adicionar um novo status?**  
R: Edite `config/settings.py` - dicionário `STATUS_FLOW`

**P: Onde mudo a URL do Jira?**  
R: Em `config/settings.py` - constante `JIRA_BASE_URL`

**P: Como debugar um erro de autenticação?**  
R: Veja `auth/login.py` - funções `verificar_login()` e `fazer_login()`

---

## 🎓 Aprenda Mais

Para entender melhor como o código funciona:

1. **Comece por `app_modularizado.py`** - Vê como tudo se conecta
2. **Depois explore `config/settings.py`** - Entenda as constantes
3. **Leia `domain/data_processing.py`** - Veja a lógica de negócio
4. **Por último `integrations/jira_api.py`** - Entenda como busca dados

---

**Versão:** 8.82  
**Última atualização:** Abril 2026  
**Status:** ✅ Modularização completa
