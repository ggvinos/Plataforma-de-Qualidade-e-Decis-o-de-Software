#!/usr/bin/env python3
"""
Test for PB Backlog Fix
=======================

Simulates the flow when user selects PB project and clicks Backlog tab.
Verifies that calcular_metricas_backlog() returns all required keys.
"""

import pandas as pd
import sys
from datetime import datetime, timedelta

# Suppress Streamlit warnings
import os
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'

sys.path.insert(0, '.')

print("=" * 70)
print("🧪 TEST: PB BACKLOG TAB FIX")
print("=" * 70)

# Test 1: Import all required functions
print("\n[1/4] Testing imports...")
try:
    from modulos.calculos import calcular_metricas_backlog
    from modulos.graficos import (
        criar_grafico_aging_backlog,
        criar_grafico_prioridade_backlog,
        criar_grafico_tipo_backlog,
        criar_grafico_backlog_por_produto
    )
    from modulos.abas import aba_backlog
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test 2: Create sample PB data
print("\n[2/4] Creating sample PB backlog data...")
try:
    now = datetime.now()
    df = pd.DataFrame({
        'ticket_id': [f'PB-{i}' for i in range(1, 11)],
        'titulo': [f'Task {i}' for i in range(1, 11)],
        'status': ['BACKLOG'] * 8 + ['DONE', 'DEFERRED'],
        'status_cat': ['backlog'] * 8 + ['done', 'deferred'],
        'tipo': ['TAREFA', 'BUG', 'SUGESTÃO', 'TAREFA', 'BUG', 'TAREFA', 'HOTFIX', 'TAREFA', 'TAREFA', 'TAREFA'],
        'criado': [now - timedelta(days=d) for d in [5, 15, 25, 35, 45, 55, 65, 75, 85, 90]],
        'atualizado': [now - timedelta(days=d) for d in [3, 5, 8, 10, 15, 20, 25, 30, 35, 40]],
        'sp': [5, 3, 0, 8, 0, 13, 0, 21, 8, 3],
        'desenvolvedor': ['Dev1', 'Dev2', 'Não atribuído', 'Dev1', 'Não atribuído', 'Dev3', 'Dev1', 'Dev2', 'Dev1', 'Dev3'],
        'prioridade': ['High', 'Highest', 'Low', 'High', 'Medium', 'High', 'Low', 'Highest', 'Medium', 'Low'],
        'produto': ['Prod1', 'Prod1', 'Prod2', 'Prod2', 'Prod1', 'Prod3', 'Prod1', 'Prod2', 'Prod1', 'Prod3'],
        'sprint': ['Sem Sprint'] * 10,
        'resumo': [f'Summary {i}' for i in range(1, 11)],
        'responsavel': ['Dev1', 'Dev2', 'Não atribuído', 'Dev1', 'Não atribuído', 'Dev3', 'Dev1', 'Dev2', 'Dev1', 'Dev3'],
    })
    print(f"✅ Created sample PB data with {len(df)} cards")
except Exception as e:
    print(f"❌ Error creating sample data: {e}")
    sys.exit(1)

# Test 3: Call calcular_metricas_backlog() and verify all keys
print("\n[3/4] Testing calcular_metricas_backlog() function...")
try:
    metricas = calcular_metricas_backlog(df)
    
    # List of all required keys
    required_keys = [
        'score_saude', 'status_saude', 'total_itens', 'sp_pendentes',
        'idade_media', 'idade_mediana', 'pct_sem_sp', 'pct_sem_responsavel',
        'cards_aging', 'por_prioridade', 'por_tipo', 'por_produto',
        'faixas_idade', 'cards_sem_sprint', 'cards_sem_responsavel',
        'cards_sem_sp', 'cards_estagnados', 'mais_antigo', 'df_backlog',
        'recomendacoes'
    ]
    
    # Check for missing keys
    missing_keys = [k for k in required_keys if k not in metricas]
    
    if missing_keys:
        print(f"❌ Missing keys: {missing_keys}")
        print(f"   Available keys: {list(metricas.keys())}")
        sys.exit(1)
    
    print("✅ Function returns all required keys")
    
    # Display sample values
    print(f"\n   Sample metrics:")
    print(f"   - score_saude: {metricas['score_saude']} (type: {type(metricas['score_saude']).__name__})")
    print(f"   - status_saude: {metricas['status_saude']}")
    print(f"   - total_itens: {metricas['total_itens']}")
    print(f"   - sp_pendentes: {metricas['sp_pendentes']}")
    print(f"   - idade_media: {metricas['idade_media']}")
    print(f"   - pct_sem_sp: {metricas['pct_sem_sp']}%")
    print(f"   - faixas_idade: {metricas['faixas_idade']}")
    print(f"   - recomendacoes: {len(metricas['recomendacoes'])} recommendations")
    
except KeyError as e:
    print(f"❌ KeyError accessing metricas: {e}")
    print(f"   This is the exact error that was occurring!")
    print(f"   Available keys: {list(metricas.keys()) if 'metricas' in locals() else 'N/A'}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error calling calcular_metricas_backlog(): {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Verify key types and values
print("\n[4/4] Verifying metric types and values...")
try:
    checks = [
        ("score_saude is float/int", isinstance(metricas['score_saude'], (int, float))),
        ("status_saude is string", isinstance(metricas['status_saude'], str)),
        ("total_itens is int", isinstance(metricas['total_itens'], int)),
        ("sp_pendentes is int", isinstance(metricas['sp_pendentes'], int)),
        ("cards_aging is DataFrame", isinstance(metricas['cards_aging'], pd.DataFrame)),
        ("por_prioridade is dict", isinstance(metricas['por_prioridade'], dict)),
        ("recomendacoes is list", isinstance(metricas['recomendacoes'], list)),
        ("score_saude in range 0-100", 0 <= metricas['score_saude'] <= 100),
    ]
    
    all_passed = True
    for check_name, check_result in checks:
        if check_result:
            print(f"   ✅ {check_name}")
        else:
            print(f"   ❌ {check_name}")
            all_passed = False
    
    if not all_passed:
        sys.exit(1)
    
    print("\n✅ All type checks passed!")
    
except Exception as e:
    print(f"❌ Error in type checking: {e}")
    sys.exit(1)

# Final Summary
print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED!")
print("=" * 70)
print("\nThe Backlog tab should now work without KeyError 'score_saude'")
print("\nTo test in the app:")
print("1. Run: streamlit run app_modularizado.py")
print("2. Select 'PB' project from sidebar")
print("3. Click '📋 Backlog' tab")
print("4. Should render without errors ✅")
print("\n" + "=" * 70)
