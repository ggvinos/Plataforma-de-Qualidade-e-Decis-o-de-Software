"""
🔍 Script de Diagnóstico - Teste de Conexão com API ConfirmationCall

Execute: python3 test_cc_connection.py
"""

import requests
from requests.auth import HTTPBasicAuth
import json

# Credenciais de teste
USUARIO = "vinicios.ferreira@confirmationcall.com.br"
SENHA = "Parkour@30"

ENDPOINTS = {
    "Desenvolvimento": "https://api.develop.confirmationcall.com.br/api/user/loginjwt",
    "Homologação": "https://api.homolog.confirmationcall.com.br/api/user/loginjwt",
    "Produção": "https://api.confirmationcall.com.br/api/user/loginjwt",
}

print("=" * 80)
print("🔍 DIAGNÓSTICO - CONEXÃO COM API CONFIRMATIONCALL")
print("=" * 80)

for ambiente, endpoint in ENDPOINTS.items():
    print(f"\n{'=' * 80}")
    print(f"🌐 Testando: {ambiente}")
    print(f"📍 Endpoint: {endpoint}")
    print("=" * 80)
    
    try:
        # Prepara requisição
        auth = HTTPBasicAuth(USUARIO, SENHA)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "NinaDash-Test/1.0"
        }
        
        print("\n📤 Enviando requisição...")
        print(f"   • Método: POST")
        print(f"   • Auth: Basic (HTTPBasicAuth)")
        print(f"   • Timeout: 10s")
        print(f"   • SSL Verify: Sim")
        
        # Realiza requisição
        response = requests.post(
            endpoint,
            auth=auth,
            headers=headers,
            timeout=10,
            verify=True
        )
        
        # Resposta
        print(f"\n📥 Resposta Recebida:")
        print(f"   • Status Code: {response.status_code}")
        print(f"   • Content-Type: {response.headers.get('content-type', 'não definido')}")
        print(f"   • Content-Length: {len(response.content)} bytes")
        print(f"   • Headers: {dict(response.headers)}")
        
        # Corpo da resposta
        print(f"\n📋 Corpo da Resposta (primeiros 500 chars):")
        print(f"   {response.text[:500] if response.text else '[VAZIO]'}")
        
        # Tenta parse JSON
        print(f"\n🔍 Análise JSON:")
        try:
            json_data = response.json()
            print(f"   ✅ JSON válido!")
            print(f"   • Keys: {list(json_data.keys())}")
            print(f"   • Conteúdo: {json_data}")
            
            # Procura por token
            if "token" in json_data:
                print(f"   ✅ Token encontrado: {json_data['token'][:50]}...")
            elif "access_token" in json_data:
                print(f"   ✅ Access token encontrado: {json_data['access_token'][:50]}...")
            else:
                print(f"   ⚠️  Nenhum token nas keys")
        
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON INVÁLIDO!")
            print(f"   • Erro: {str(e)}")
            print(f"   • Status Code: {response.status_code}")
            if response.status_code == 200:
                print(f"   ⚠️  Status é 200 mas resposta não é JSON!")
        
        # Análise baseada no status code
        print(f"\n✅ Análise:")
        if response.status_code == 200:
            print(f"   ✅ Status 200 - OK")
        elif response.status_code == 401:
            print(f"   ❌ Status 401 - Credenciais inválidas")
        elif response.status_code == 403:
            print(f"   ❌ Status 403 - Acesso negado")
        elif response.status_code == 404:
            print(f"   ❌ Status 404 - Endpoint não encontrado")
        elif response.status_code == 500:
            print(f"   ❌ Status 500 - Erro no servidor")
        else:
            print(f"   ⚠️  Status {response.status_code} - Desconhecido")
    
    except requests.exceptions.Timeout:
        print(f"   ❌ TIMEOUT - Conexão expirou após 10s")
    
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ ERRO DE CONEXÃO: {str(e)}")
    
    except requests.exceptions.RequestException as e:
        print(f"   ❌ ERRO NA REQUISIÇÃO: {str(e)}")
    
    except Exception as e:
        print(f"   ❌ ERRO INESPERADO: {str(e)}")

print(f"\n{'=' * 80}")
print("📊 RESUMO DOS TESTES")
print("=" * 80)
print("""
✅ Se Status 200 e JSON válido com token:
   → Credenciais e endpoint estão OK
   → Problema pode ser na integração Streamlit

❌ Se Status 401:
   → Credenciais inválidas
   → Verifique usuário/senha

❌ Se Status 404:
   → Endpoint não encontrado
   → Verifique a URL e se ambiente existe

❌ Se TIMEOUT:
   → Verifique conectividade
   → Verifique se firewall está bloqueando

❌ Se resposta não é JSON:
   → API está retornando erro (HTML/texto)
   → Verifique com admin do ConfirmationCall
""")
