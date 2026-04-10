# 🎯 NinaDash - Dashboard de Métricas de QA

Dashboard de métricas ISTQB/CTFL para tomada de decisão em projetos de software.

## 🚀 Deploy no Streamlit Community Cloud

### Pré-requisitos
- Conta no [GitHub](https://github.com)
- Conta no [Streamlit Cloud](https://share.streamlit.io)

### Passo a passo

#### 1. Criar repositório no GitHub (privado)
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/nina-dashboard.git
git push -u origin main
```

#### 2. Configurar Streamlit Cloud

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Clique em **"New app"**
3. Conecte seu repositório GitHub
4. Configure:
   - **Repository**: seu-usuario/nina-dashboard
   - **Branch**: main
   - **Main file path**: app.py

#### 3. Configurar Secrets (IMPORTANTE!)

1. Nas configurações do app, vá em **"Secrets"**
2. Cole o conteúdo abaixo (substitua com suas credenciais):

```toml
[jira]
base_url = "https://ninatecnologia.atlassian.net"
email = "seu-email@empresa.com"
token = "SEU_TOKEN_DO_JIRA_AQUI"

[auth]
emails_autorizados = "email1@empresa.com,email2@empresa.com"
```

3. Clique em **"Save"**
4. Faça redeploy do app

## 🔧 Desenvolvimento Local

### Instalar dependências
```bash
pip install -r requirements.txt
```

### Configurar credenciais
```bash
# Copie o arquivo de exemplo
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Edite com suas credenciais
nano .streamlit/secrets.toml
```

### Executar
```bash
streamlit run app.py
# ou
python -m streamlit run app.py
```

Acesse: http://localhost:8501

## 📁 Estrutura

```
├── app.py                    # Aplicação principal
├── requirements.txt          # Dependências Python
├── .gitignore               # Arquivos ignorados pelo Git
├── .streamlit/
│   ├── config.toml          # Configurações do Streamlit
│   ├── secrets.toml         # Credenciais (NÃO COMMITAR!)
│   └── secrets.toml.example # Template de credenciais
└── Desing/                  # Assets visuais
    └── *.svg                # Logos
```

## 🔐 Segurança

- ✅ Credenciais protegidas via `st.secrets`
- ✅ `.streamlit/secrets.toml` no `.gitignore`
- ✅ Autenticação por email
- ✅ Repositório privado recomendado

## 📊 Métricas Disponíveis

- **Fator K** - Maturidade do código
- **DDP** - Defect Detection Percentage
- **FPY** - First Pass Yield
- **MTTR** - Mean Time To Repair
- **Lead Time** - Tempo de entrega
- **Health Score** - Saúde da release

---

© 2026 NINA Tecnologia
