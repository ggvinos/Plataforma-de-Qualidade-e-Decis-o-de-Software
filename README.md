# 🎯 NinaDash - Dashboard de Inteligência e Qualidade de Software

Dashboard de métricas ISTQB/CTFL para tomada de decisão em projetos de software, integrado com Jira e ConfirmationCall.

## 📁 Estrutura do Projeto

```
NinaDash/
├── app_modularizado.py      # 🚀 Aplicação principal (use este)
├── app.py                   # Versão legada (backup)
├── requirements.txt         # Dependências Python
├── favicon.svg              # Ícone do app
├── README.md                # Este arquivo
├── .env                     # Variáveis de ambiente (não commitar)
├── .gitignore               # Arquivos ignorados pelo Git
│
├── modulos/                 # 📦 Módulos da aplicação
│   ├── __init__.py          # Inicializador do pacote
│   ├── config.py            # Configurações, constantes, visual
│   ├── auth.py              # Autenticação básica (legado)
│   ├── confirmation_call_auth.py  # 🔐 Autenticação JWT ConfirmationCall
│   ├── jira_api.py          # Integração com API do Jira
│   ├── calculos.py          # Métricas: Fator K, DDP, FPY, Lead Time
│   ├── processamento.py     # Processamento de dados e filtros
│   ├── abas.py              # Componentes das abas do dashboard
│   ├── cards.py             # Visualização de cards/tickets
│   ├── widgets.py           # Componentes visuais reutilizáveis
│   ├── graficos.py          # Gráficos Plotly (funil, tendências)
│   ├── helpers.py           # Funções auxiliares
│   ├── consultas.py         # Sistema de consultas personalizadas
│   ├── utils.py             # Utilitários gerais
│   └── changelog.py         # Histórico de versões
│
├── docs/                    # 📚 Documentação
│   ├── DEPLOY.md            # Guia de deploy
│   ├── MELHORIAS.md         # Histórico de melhorias
│   ├── DOCUMENTACAO_*.md    # Documentação técnica
│   └── ...                  # Outros documentos
│
├── tests/                   # 🧪 Testes
│   └── test_*.py            # Arquivos de teste
│
├── backups/                 # 📦 Versões anteriores
│   └── app_v*.py            # Backups de versões
│
├── Desing/                  # 🎨 Assets visuais
│   └── *.svg                # Logos e ícones
│
└── .streamlit/              # ⚙️ Configurações Streamlit
    ├── config.toml          # Configurações do tema
    └── secrets.toml         # Credenciais (não commitar!)
```

## 🚀 Início Rápido

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar credenciais
```bash
# Copie e edite o arquivo de secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

### 3. Executar
```bash
streamlit run app_modularizado.py
```

Acesse: http://localhost:8501

## 🔐 Autenticação

O NinaDash usa autenticação JWT via ConfirmationCall:

- **Desenvolvimento**: api.develop.confirmationcall.com.br
- **Homologação**: api.homolog.confirmationcall.com.br  
- **Produção**: api.confirmationcall.com.br

## 📊 Métricas Disponíveis

| Métrica | Descrição |
|---------|-----------|
| **Fator K** | Maturidade do código (bugs encontrados em QA vs produção) |
| **DDP** | Defect Detection Percentage |
| **FPY** | First Pass Yield |
| **Lead Time** | Tempo médio de entrega |
| **Throughput** | Capacidade de entrega |
| **Health Score** | Saúde geral do projeto |

## 🛠️ Tecnologias

- **Python 3.10+**
- **Streamlit** - Framework web
- **Plotly** - Gráficos interativos
- **Pandas** - Processamento de dados
- **Requests** - Integração com APIs

## 📝 Licença

© 2026 Nina Tecnologia - Todos os direitos reservados.
- **FPY** - First Pass Yield
- **MTTR** - Mean Time To Repair
- **Lead Time** - Tempo de entrega
- **Health Score** - Saúde da release

---

© 2026 NINA Tecnologia
