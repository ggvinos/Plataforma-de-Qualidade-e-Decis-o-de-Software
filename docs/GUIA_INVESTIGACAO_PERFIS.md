# 🔎 GUIA DE INVESTIGAÇÃO TÉCNICA

## Verificar se Jira e ConfirmationCall têm dados de Time

---

## 1️⃣ VERIFICAR JIRA (Interface Web)

### Passo a Passo

1. **Acesse o Jira**
   - URL: https://ninatecnologia.atlassian.net
   - Clique em ⚙️ (Configuração) no canto superior direito

2. **Vá para Usuários**
   - Clique em `Administração` ou `Settings`
   - Procure por `Usuários` ou `People`
   - Ou: https://ninatecnologia.atlassian.net/people

3. **Clique em um usuário (ex: você ou outro dev)**

4. **CAPTURE TODO CAMPO VISÍVEL**
   ```
   Procure especialmente por:
   ✅ Name
   ✅ Email
   ✅ Display Name
   ✅ Account ID
   ❓ Department (se existir)
   ❓ Team (se existir)
   ❓ Organization (se existir)
   ❓ Job Title (se existir)
   ❓ Groups (se existir)
   ❓ Site Role (se existir)
   ❓ Location (se existir)
   ```

5. **Screenshot**
   - Tire screenshot de TODOS os campos do usuário
   - Cole no arquivo: `INVESTIGACAO_JIRA.txt`

---

## 2️⃣ VERIFICAR JIRA API (Teste HTTP)

### Via Python (no seu terminal)

```python
# Abra um terminal e rode:

python3 << 'EOF'
import requests
import json

# Credenciais (do seu .streamlit/secrets.toml)
EMAIL = "seu-email@confirmationcall.com.br"
TOKEN = "seu-token-jira"  # PAT token

# Buscar usuário atual
url = "https://ninatecnologia.atlassian.net/rest/api/3/myself"
response = requests.get(url, auth=(EMAIL, TOKEN))

print("=" * 60)
print("RESPOSTA DA API JIRA - /myself")
print("=" * 60)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
print()

# Buscar um usuário específico
# Primeiro, precisamos do account ID
account_id = response.json().get('accountId')
print(f"Seu Account ID: {account_id}")
print()

# Agora buscar detalhes completos
url2 = f"https://ninatecnologia.atlassian.net/rest/api/3/users/{account_id}"
response2 = requests.get(url2, auth=(EMAIL, TOKEN))

print("=" * 60)
print("RESPOSTA DA API JIRA - /users/{accountId}")
print("=" * 60)
print(json.dumps(response2.json(), indent=2, ensure_ascii=False))

EOF
```

### Via cURL (no Terminal)

```bash
# Versão 1: Obter usuário atual
curl -u "seu-email@confirmationcall.com.br:seu-token" \
  https://ninatecnologia.atlassian.net/rest/api/3/myself | jq '.'

# Versão 2: Listar TODOS os usuários (se tiver permissão)
curl -u "seu-email@confirmationcall.com.br:seu-token" \
  https://ninatecnologia.atlassian.net/rest/api/3/users/search | jq '.'
```

### 🎯 O que procurar na resposta

```json
{
  "self": "...",
  "accountId": "...",
  "accountType": "atlassian",
  "name": "viniciosferreira",
  "key": "viniciosferreira",
  "emailAddress": "viniciosferreira@confirmationcall.com.br",
  "avatarUrls": {...},
  "displayName": "Viniciosferreira",
  "active": true,
  "timezone": "America/Sao_Paulo",
  "locale": "pt_BR",
  "groups": {...},                    ← PROCURE AQUI 👀
  "applicationRoles": {...},          ← E AQUI 👀
  "expand": "groups,applicationRoles" ← Pode ter mais dados
}
```

**Se ver "groups" ou "applicationRoles" com dados, significa que PODE ter info de time!**

---

## 3️⃣ VERIFICAR ConfirmationCall API

### Objetivo
Verificar se a API de login retorna MAIS informações além do token JWT

### Teste: Analisar o que retorna

```python
import requests
import json
import base64
from requests.auth import HTTPBasicAuth

# Dados
USUARIO = "seu-email@confirmationcall.com.br"
SENHA = "sua-senha"
ENDPOINT = "https://api.confirmationcall.com.br/api/user/loginjwt"  # Produção

# Fazer login
response = requests.post(
    ENDPOINT,
    auth=HTTPBasicAuth(USUARIO, SENHA),
    headers={"Content-Type": "application/json"},
    timeout=10
)

print("=" * 60)
print("RESPOSTA ConfirmationCall")
print("=" * 60)
print(f"Status Code: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print()

# Tentar parse como JSON
try:
    data = response.json()
    print("Retornou JSON:")
    print(json.dumps(data, indent=2))
except:
    print("Retornou texto puro:")
    print(response.text)
    
    # Se for JWT, descodificar
    if response.text.count('.') == 2:
        print("\n📌 Parece ser JWT. Decodificando payload:")
        token = response.text
        parts = token.split('.')
        
        # O payload é a segunda parte
        payload = parts[1]
        
        # Adicionar padding se necessário
        padding = 4 - (len(payload) % 4)
        if padding != 4:
            payload += '=' * padding
        
        try:
            decoded = base64.urlsafe_b64decode(payload)
            import json
            jwt_data = json.loads(decoded)
            print(json.dumps(jwt_data, indent=2))
        except Exception as e:
            print(f"Erro ao decodificar: {e}")

```

### 🎯 O que procurar na resposta

```json
{
  "token": "eyJ...",  ← Token JWT (será grande)
  "user": {           ← Procure aqui! Pode ter info de time
    "id": "123",
    "name": "Viniciosferreira",
    "email": "viniciosferreira@confirmationcall.com.br",
    "department": "Development",   ← 👀 ACHADO!
    "team": "Backend",             ← 👀 ACHADO!
    "role": "Developer",           ← 👀 Pode ser útil
    "groups": ["dev", "backend"]   ← 👀 ACHADO!
  }
}
```

---

## 4️⃣ VERIFICAR SE JIRA TEM CAMPO CUSTOMIZADO DE TIME

### Via Interface Jira

1. Acesse: https://ninatecnologia.atlassian.net/
2. ⚙️ Settings → Issues
3. Procure por "Custom Fields"
4. PROCURE por nomes como:
   - "Team"
   - "Department"
   - "Group"
   - "Grupo"
   - "Time"
   - "Departamento"
   - "Squad"
   - "Organização"

5. Se encontrar, anote o **Custom Field ID** (ex: `customfield_12345`)

---

## 5️⃣ TEMPLATE DE RESPOSTA

Crie um arquivo: `INVESTIGACAO_RESULTADOS.md`

```markdown
# 📊 RESULTADOS DA INVESTIGAÇÃO

## Jira - Interface Web
- [ ] Campo "Department" encontrado? SIM / NÃO
- [ ] Campo "Team" encontrado? SIM / NÃO
- [ ] Campo "Group" encontrado? SIM / NÃO
- [ ] Outros campos de interesse: _______________

## Jira - API

### GET /rest/api/3/myself
```
[Cole a resposta JSON aqui]
```

**Análise**: Contém info de time? SIM / NÃO

### GET /rest/api/3/users/{accountId}
```
[Cole a resposta JSON aqui]
```

**Análise**: Contém info de time? SIM / NÃO

## ConfirmationCall API

### POST /api/user/loginjwt
```
[Cole a resposta aqui]
```

**Análise**: Contém info de time? SIM / NÃO

## Conclusão

- ✅ Melhor opção: **CENÁRIO A (Jira)** / **CENÁRIO B (Admin)**
- 📝 Próximos passos: _______________
- 👥 Estrutura de times recomendada: _______________
```

---

## 6️⃣ TROUBLESHOOTING

### Erro: "401 Unauthorized" na Jira API
**Solução**: 
- Verifique se o token está certo
- Use PAT (Personal Access Token) em vez de senha
- Gerar em: https://id.atlassian.com/manage-profile/security/api-tokens

### Erro: "403 Forbidden"
**Solução**:
- Seu usuário não tem permissão de admin
- Peça para um admin Jira fazer a investigação

### Erro: "404 Not Found" na API
**Solução**:
- Verifique a URL
- Use: `https://ninatecnologia.atlassian.net/rest/api/3/...`

### Erro: "Connection refused" no ConfirmationCall
**Solução**:
- Verifique a URL do endpoint
- Pode ser `https://api.develop.confirmationcall.com.br/...` (dev)
- Ou `https://api.confirmationcall.com.br/...` (prod)

---

## 7️⃣ RESUMO - O QUE FAZER

1. **Execute o script Python do item 2**
   - Capture a resposta do Jira API
   
2. **Execute o script Python do item 3**
   - Capture a resposta do ConfirmationCall

3. **Verifique pela Interface do Jira (item 1)**
   - Procure campos de time manualmente

4. **Crie arquivo `INVESTIGACAO_RESULTADOS.md`**
   - Cole todas as respostas
   - Marque SIM/NÃO

5. **Nos compartilhe os resultados**
   - Com isso, decidimos qual cenário usar
   - E começamos a codificar!

---

## 📧 Próximo Passo

Após fazer essa investigação, envie:
- `INVESTIGACAO_RESULTADOS.md`
- Screenshots da interface Jira
- Confirmação da estrutura de times

Aí começamos a implementar! 🚀
