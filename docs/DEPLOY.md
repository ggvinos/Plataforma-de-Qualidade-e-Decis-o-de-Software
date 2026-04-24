# 🚀 Guia de Deploy - NinaDash v8.82 Modularizada

## ✅ Status Atual

- ✅ **Estrutura modularizada** criada e em produção
- ✅ **Backup** do código anterior em `app_v8p82_backup.py`
- ✅ **Repositório** atualizado com commit e push
- ✅ **Pronto para teste**

---

## 📋 Requisitos

### Python
```bash
python --version  # Deve ser 3.8+
```

### Dependências (requirements.txt)
```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.18.0
requests>=2.31.0
python-dotenv>=1.0.0
openpyxl>=3.1.0
extra-streamlit-components>=0.1.60
```

---

## 🔧 Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/ggvinos/Plataforma-de-Qualidade-e-Decis-o-de-Software.git
cd "Jira Dasboard"
```

### 2. Crie um ambiente virtual
```bash
# Linux/Mac
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instale dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as credenciais

**Opção A: Usando arquivo `.streamlit/secrets.toml`**
```toml
[jira]
email = "seu.email@confirmationcall.com.br"
token = "seu_token_jira"
```

**Opção B: Usando variáveis de ambiente**
```bash
export JIRA_API_EMAIL="seu.email@confirmationcall.com.br"
export JIRA_API_TOKEN="seu_token_jira"
```

---

## 🎯 Executar Localmente

### Para Desenvolvimento (com hot reload)
```bash
streamlit run app.py
```

A aplicação abrirá em `http://localhost:8501`

### Para Produção (sem hot reload)
```bash
streamlit run app.py \
  --logger.level=error \
  --client.showErrorDetails=false \
  --server.headless=true
```

---

## 📁 Estrutura do Projeto

```
Jira Dasboard/
├── app.py                       ← NOVO: Versão modularizada (PRINCIPAL)
├── app_v8p82_backup.py          ← BACKUP: Versão monolítica anterior
├── requirements.txt
├── README.md
├── MODULARIZACAO.md             ← Guia de modularização
├── DEPLOY.md                    ← Este arquivo
│
├── config/
│   ├── __init__.py
│   └── settings.py              (constantes, tooltips, mapeamentos)
│
├── auth/
│   ├── __init__.py
│   └── login.py                 (autenticação com cookies)
│
├── integrations/
│   ├── __init__.py
│   └── jira_api.py              (API Jira, cache)
│
├── domain/
│   ├── __init__.py
│   └── data_processing.py       (métricas, processamento)
│
├── ui/
│   ├── __init__.py
│   └── pages/                   (em desenvolvimento)
│
└── utils/
    └── __init__.py
```

---

## 🧪 Teste de Funcionalidade

### 1. Login
```
Email: seu.email@confirmationcall.com.br
Deve retornar sucesso (@ confirmationcall.com.br)
```

### 2. Busca de Dados
Verifique se consegue conectar com a API Jira:
- Credentials corretos?
- VPN ativa (se necessário)?
- Token válido?

### 3. Processamento de Dados
A estrutura modular permite testar cada parte isoladamente:

```python
# Testar config
from config import TOOLTIPS, STATUS_FLOW
print(TOOLTIPS["fator_k"])

# Testar auth
from auth import validar_email_corporativo
print(validar_email_corporativo("teste@confirmationcall.com.br"))

# Testar integrations
from integrations import buscar_dados_jira_cached
issues, _ = buscar_dados_jira_cached("SD", "project = SD")

# Testar domain
from domain import processar_issues, calcular_fator_k
df = processar_issues(issues)
fk = calcular_fator_k(10, 2)
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'config'"
**Solução:** Verifique que está na pasta correta do projeto
```bash
cd "/home/viniciosferreira/Documentos/Projetos NINA/Jira Dasboard"
pwd  # Deve mostrar o caminho correto
```

### "streamlit: comando não encontrado"
**Solução:** Ative o ambiente virtual
```bash
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### Erro de autenticação
**Solução:** Verifique credenciais
```bash
echo $JIRA_API_EMAIL  # Linux/Mac
echo %JIRA_API_EMAIL%  # Windows
```

### Erro de conexão com Jira
**Solução:** Verifique se a URL está correta em `config/settings.py`
```python
JIRA_BASE_URL = "https://ninatecnologia.atlassian.net"
```

---

## 📊 Deploy em Produção

### Option 1: Streamlit Community Cloud
```bash
# Fazer push para GitHub
git add .
git commit -m "feat: Deploy em Streamlit Cloud"
git push origin main

# Ir para https://share.streamlit.io
# Conectar repositório e fazer deploy
```

### Option 2: Server Próprio
```bash
# Instalar supervisor ou pm2
pip install supervisor

# Criar arquivo de config
sudo nano /etc/supervisor/conf.d/ninadash.conf
```

### Option 3: Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.headless=true"]
```

---

## 📈 Monitoramento

### Logs
```bash
# Ver logs em tempo real
tail -f ~/.streamlit/logs/*.log

# Ver logs de erro
grep ERROR ~/.streamlit/logs/*.log
```

### Performance
- Verifique cache de 5 min em `config/settings.py`
- Monitore conexões com Jira API
- Analise DataFrame processing

---

## 🔄 Atualizar Código

Se precisar voltar para a versão anterior:
```bash
# Backup da versão atual
cp app.py app_current.py

# Restaurar versão anterior
cp app_v8p82_backup.py app.py

# Commit
git add app.py
git commit -m "revert: Voltar para versão monolítica"
git push origin main
```

---

## ✨ Próximas Etapas

1. **Completar UI** - Criar páginas em `ui/pages/`
2. **Testes** - Adicionar testes unitários
3. **CI/CD** - Configurar GitHub Actions
4. **Docs** - Expandir documentação
5. **Monitoramento** - Setup de alertas

---

## 📞 Suporte

Para dúvidas:
1. Leia [MODULARIZACAO.md](MODULARIZACAO.md)
2. Verifique `config/settings.py` para constantes
3. Teste módulos isoladamente em Python shell
4. Veja logs do Streamlit

---

## 📝 Checklist de Deploy

- [ ] Ambiente virtual criado e ativado
- [ ] `requirements.txt` instalado
- [ ] Credenciais Jira configuradas
- [ ] `streamlit run app.py` funciona localmente
- [ ] Login funciona
- [ ] Busca de dados funciona
- [ ] Métricas calculam corretamente
- [ ] Código commitado e pushed
- [ ] Pronto para testes!

---

**Status:** ✅ Pronto para Deploy  
**Versão:** 8.82 Modularizada  
**Data:** 22/04/2026
