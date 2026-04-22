"""
Script de debug para verificar as colunas do DataFrame
"""

import pandas as pd
from modulos.calculos import processar_issues
from modulos.jira_api import buscar_dados_jira_cached

print("🔍 VERIFICANDO ESTRUTURA DO DATAFRAME\n")

try:
    # Simula o carregamento de dados como o app faz
    print("1️⃣ Buscando dados do Jira (SD)...")
    issues, _ = buscar_dados_jira_cached("SD", "project = SD ORDER BY created DESC LIMIT 10")
    
    if issues:
        print(f"   ✅ {len(issues)} cards encontrados\n")
        
        print("2️⃣ Processando issues...")
        df = processar_issues(issues)
        
        print(f"   ✅ DataFrame criado: {df.shape[0]} linhas x {df.shape[1]} colunas\n")
        
        print("3️⃣ Colunas disponíveis:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i:2}. {col}")
        
        print("\n4️⃣ Verificando colunas críticas para abas:")
        colunas_criticas = {
            'QA': ['qa', 'status_categoria', 'status', 'responsavel'],
            'DEV': ['responsavel', 'status', 'status_categoria', 'complexidade'],
            'Produto': ['produto', 'status', 'resumo'],
        }
        
        for aba, cols in colunas_criticas.items():
            print(f"\n   {aba}:")
            for col in cols:
                if col in df.columns:
                    print(f"      ✅ {col}")
                else:
                    print(f"      ❌ FALTA: {col}")
        
        print("\n5️⃣ Amostra de dados (primeiras 3 linhas):")
        print(df.head(3).to_string())
        
    else:
        print("   ❌ Nenhum card encontrado")
        
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
