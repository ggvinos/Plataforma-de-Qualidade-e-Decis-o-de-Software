# 🔧 Troubleshooting - Erro JSON na Autenticação

**Erro**: `Expecting value: line 1 column 1 (char 0)`

**Status**: ❌ API retorna resposta inválida (não é JSON)

---

## 🎯 O Que Significa

Este erro acontece quando:

1. ✅ A requisição chegou até a API
2. ✅ A API respondeu
3. ❌ A resposta NÃO é JSON válido
4. ❌ Pode ser: HTML (erro 404), string vazia, ou resposta corrompida

---

## 🔍 Como Diagnosticar

### Opção 1: Teste Automático (RECOMENDADO)

```bash
# Execute este script:
python3 test_cc_dev.py

# Ele irá:
# 1. Pedir suas credenciais
# 2. Testar endpoint de desenvolvimento
# 3. Mostrar exatamente o que a API retornou
# 4. Diagnóstico automático do problema
```

### Opção 2: Teste Manual com curl

```bash
# Substitua USUARIO e SENHA pelas suas:
curl -X POST https://api.develop.confirmationcall.com.br/api/user/loginjwt \
  -H "Content-Type: application/json" \
  -u "vinicios.ferreira@confirmationcall.com.br:Parkour@30" \
  -v
```

**O que procurar na resposta**:
- `> Authorization: Basic ...` ← Deve estar presente
- `< HTTP/1.1 200 OK` ← Status code
- `< Content-Type: application/json` ← Deve ser JSON
- Corpo da resposta com `{"token": "..."}` ← Token

### Opção 3: Script Python Simples

```python
import requests
from requests.auth import HTTPBasicAuth

response = requests.post(
    "https://api.develop.confirmationcall.com.br/api/user/loginjwt",
    auth=HTTPBasicAuth("vinicios.ferreira@confirmationcall.com.br", "Parkour@30")
)

print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('content-type')}")
print(f"Resposta (primeiros 500 chars):")
print(response.text[:500])
```

---

## 🛠️ Possíveis Causas e Soluções

### Causa 1: Endpoint Incorreto ❌

**Sintoma**: Status 404 + HTML de erro

**Solução**:
```
Verificar se endpoint está correto:
✓ Desenvolvimento: https://api.develop.confirmationcall.com.br/api/user/loginjwt
✓ Homologação: https://api.homolog.confirmationcall.com.br/api/user/loginjwt
✓ Produção: https://api.confirmationcall.com.br/api/user/loginjwt
```

### Causa 2: Credenciais Inválidas ❌

**Sintoma**: Status 401 + JSON com erro

**Solução**:
```
Verifique:
1. Email correto: vinicios.ferreira@confirmationcall.com.br
2. Senha correta: Parkour@30 (sem espaços antes/depois)
3. Caps Lock não está ativo
4. Conta ainda está ativa no ConfirmationCall
```

### Causa 3: Firewall/VPN Bloqueando ❌

**Sintoma**: Timeout ou ConnectionError

**Solução**:
```bash
# Teste se consegue chegar na API:
ping api.develop.confirmationcall.com.br
curl https://api.develop.confirmationcall.com.br

# Se falhar:
1. Desative VPN temporariamente
2. Verifique se firewall corporativo não está bloqueando
3. Contato com IT corporativo
```

### Causa 4: API do ConfirmationCall Offline ❌

**Sintoma**: Status 500 + HTML de erro

**Solução**:
```
1. Teste outro ambiente (Produção/Homologação)
2. Verifique status page do ConfirmationCall
3. Contacte admin do ConfirmationCall
```

### Causa 5: Response Content-Type Incorreto ❌

**Sintoma**: Status 200 mas resposta é HTML

**Solução**:
```
Se curl mostra:
< Content-Type: text/html

Então API está retornando HTML em vez de JSON
Contacte admin do ConfirmationCall
```

---

## 📊 Checklist de Diagnóstico

- [ ] Executei `python3 test_cc_dev.py`
- [ ] Anotei o status code exato
- [ ] Anotei o Content-Type da resposta
- [ ] Vi qual é o conteúdo (HTML/JSON/vazio)
- [ ] Testei as 3 opções de ambiente
- [ ] Verifiquei credenciais (sem espaços)
- [ ] Testei sem VPN/firewall
- [ ] Compartilhei resultado com admin

---

## 📝 Informações para Reportar ao Admin

Se ainda não conseguir resolver, compile as seguintes informações:

### Template para Report

```
Título: Erro de Autenticação no ConfirmationCall - Desenvolvimento

Ambiente: Desenvolvimento
Usuário: vinicios.ferreira@confirmationcall.com.br
Data/Hora: [DATA E HORA]

Status Code: [EX: 404, 200, timeout]
Content-Type: [EX: text/html, application/json]
Resposta (primeiros 200 chars): [EX: {"error": "..."}]

Erro Específico: Expecting value: line 1 column 1 (char 0)

Testes Executados:
☐ test_cc_dev.py
☐ curl manualmente
☐ Sem VPN/firewall
☐ Credenciais duplicadas
☐ Testei todos os 3 ambientes

Resultado do test_cc_dev.py:
[COLE SAÍDA AQUI]
```

---

## ✅ Se Funcionar

Quando o teste passar:

```bash
# Resultado esperado:
✅ Status 200 OK - Resposta bem-sucedida
✅ Resposta em JSON válido
✅ Token encontrado: eyJ...
✅ SUCESSO - Login funcionando!
```

**Próximos passos**:
1. Volte para Streamlit
2. Clique em "Entrar" novamente
3. Dashboard deve carregar normalmente
4. Se ainda não funcionar, limpe cache: `rm -rf ~/.streamlit/cache`

---

## 🔗 Referências

- Documentação oficial: AUTENTICACAO_CONFIRMATIONCALL.md
- Quick start: GUIA_RAPIDO_AUTH.md
- Testes: test_cc_dev.py

---

## 📞 Suporte

1. **Primeiro**: Execute `python3 test_cc_dev.py`
2. **Então**: Compare resultado com este documento
3. **Finalmente**: Contacte admin com informações do report

---

**Status**: Este documento ajuda a diagnosticar o erro específico  
**Atualizado**: 2026-04-22  
**Versão**: 1.0
