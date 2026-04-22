#!/usr/bin/env python3
"""
🔍 Teste Específico - API ConfirmationCall Desenvolvimento

Execute: python3 test_cc_dev.py

Este script testa especificamente o ambiente de DESENVOLVIMENTO
com suas credenciais, sem expor informações sensíveis.
"""

import requests
from requests.auth import HTTPBasicAuth
import json
import sys
from getpass import getpass

print("=" * 80)
print("🔍 TESTE ESPECÍFICO - CONFIRMATIONCALL DESENVOLVIMENTO")
print("=" * 80)

# Credenciais
print("\n📋 Insira suas credenciais (não serão salvas):\n")

usuario = input("👤 Usuário: ").strip()
if not usuario:
    print("❌ Usuário não pode estar vazio")
    sys.exit(1)

senha = getpass("🔑 Senha: ")
if not senha:
    print("❌ Senha não pode estar vazia")
    sys.exit(1)

# Endpoint de desenvolvimento
ENDPOINT = "https://api.develop.confirmationcall.com.br/api/user/loginjwt"

print("\n" + "=" * 80)
print("🚀 INICIANDO TESTE")
print("=" * 80)

print(f"\n📍 Endpoint: {ENDPOINT}")
print(f"👤 Usuário: {usuario}")
print(f"🔑 Senha: ••••{'*' * len(senha)}")

try:
    print("\n📤 Enviando requisição...")
    
    auth = HTTPBasicAuth(usuario, senha)
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "NinaDash-Dev-Test/1.0"
    }
    
    response = requests.post(
        ENDPOINT,
        auth=auth,
        headers=headers,
        timeout=10,
        verify=True
    )
    
    print(f"✅ Resposta recebida")
    print(f"\n📥 Status Code: {response.status_code}")
    print(f"📥 Content-Type: {response.headers.get('content-type', 'não definido')}")
    print(f"📥 Content-Length: {len(response.content)} bytes")
    
    # Análise do status
    print(f"\n🔍 Análise do Status Code:")
    
    if response.status_code == 200:
        print("✅ Status 200 OK - Resposta bem-sucedida")
        
        # Tenta parse JSON
        try:
            data = response.json()
            print("✅ Resposta em JSON válido")
            
            # Procura por token
            if "token" in data:
                token = data["token"]
                print(f"✅ Token encontrado: {token[:50]}...")
                print(f"✅ SUCESSO - Login funcionando!")
            elif "access_token" in data:
                token = data["access_token"]
                print(f"✅ Access token encontrado: {token[:50]}...")
                print(f"✅ SUCESSO - Login funcionando!")
            else:
                print(f"⚠️  JSON não contém token")
                print(f"   Keys disponíveis: {list(data.keys())}")
                print(f"   Conteúdo: {data}")
        
        except json.JSONDecodeError as e:
            print(f"❌ PROBLEMA: Status 200 mas resposta não é JSON!")
            print(f"   Erro: {str(e)}")
            print(f"   Conteúdo (primeiros 200 chars): {response.text[:200]}")
            print(f"\n   📞 Contacte o admin do ConfirmationCall - possível problema no servidor")
    
    elif response.status_code == 401:
        print("❌ Status 401 Unauthorized")
        print("   Causa: Credenciais inválidas")
        print("   Ação: Verifique usuário e senha")
        
        try:
            data = response.json()
            if "message" in data:
                print(f"   Detalhes: {data['message']}")
        except:
            pass
    
    elif response.status_code == 403:
        print("❌ Status 403 Forbidden")
        print("   Causa: Acesso negado para este ambiente")
        print("   Ação: Verifique permissões com admin")
        
        try:
            data = response.json()
            if "message" in data:
                print(f"   Detalhes: {data['message']}")
        except:
            pass
    
    elif response.status_code == 404:
        print("❌ Status 404 Not Found")
        print("   Causa: Endpoint não encontrado")
        print(f"   URL testada: {ENDPOINT}")
        print("   Ação: Verifique a URL do endpoint com admin")
    
    elif response.status_code == 500:
        print("❌ Status 500 Internal Server Error")
        print("   Causa: Erro no servidor ConfirmationCall")
        print("   Ação: Verifique com admin se servidor está online")
        
        try:
            data = response.json()
            if "message" in data:
                print(f"   Detalhes: {data['message']}")
        except:
            pass
    
    else:
        print(f"❌ Status {response.status_code} - Desconhecido")
        print("   Tente consultar admin sobre este código de erro")
        
        try:
            data = response.json()
            print(f"   Resposta JSON: {data}")
        except:
            print(f"   Resposta texto: {response.text[:200]}")

except requests.exceptions.Timeout:
    print("❌ TIMEOUT - Conexão expirou após 10 segundos")
    print("   Possíveis causas:")
    print("   • Sua internet está lenta ou desconectada")
    print("   • Servidor ConfirmationCall está muito lento")
    print("   • Firewall/VPN está bloqueando")

except requests.exceptions.ConnectionError as e:
    print("❌ ERRO DE CONEXÃO")
    print(f"   Detalhes: {str(e)}")
    print("   Possíveis causas:")
    print("   • Sua internet está desconectada")
    print("   • Firewall/VPN está bloqueando")
    print("   • Servidor ConfirmationCall está offline")

except requests.exceptions.RequestException as e:
    print("❌ ERRO NA REQUISIÇÃO")
    print(f"   Detalhes: {str(e)}")

except Exception as e:
    print("❌ ERRO INESPERADO")
    print(f"   Tipo: {type(e).__name__}")
    print(f"   Detalhes: {str(e)}")

print("\n" + "=" * 80)
print("📝 PRÓXIMOS PASSOS")
print("=" * 80)

print("""
Se o teste passou (Status 200 + Token):
  ✅ Suas credenciais estão corretas
  ✅ Acesso ao ambiente de desenvolvimento está OK
  → Tente fazer login novamente no Streamlit
  → Se ainda não funcionar, pode ser bug local

Se o teste falhou:
  ❌ Anote o status code e mensagem de erro
  ❌ Compartilhe com o admin do ConfirmationCall
  ❌ Inclua também a saída completa deste teste
  
Para reportar:
  • Diga qual status code recebeu
  • Diga qual ambiente está testando
  • Inclua a saída completa do teste
  • Não inclua sua senha (já testamos aqui)
""")
