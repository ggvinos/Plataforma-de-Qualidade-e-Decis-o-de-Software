#!/usr/bin/env python3
"""
Script de debug para analisar comentários do Jira.
Mostra TODOS os dados brutos e processados.
"""

import sys
sys.path.insert(0, '.')

from modulos.jira_api import buscar_card_especifico, extrair_texto_adf
from modulos.cards import filtrar_e_classificar_comentarios

# Pega o ticket como argumento ou usa padrão
ticket_id = sys.argv[1] if len(sys.argv) > 1 else "SD-799"

print(f"\n{'='*60}")
print(f"DEBUG COMENTÁRIOS - {ticket_id}")
print(f"{'='*60}\n")

# Busca o card
issue, links, comentarios, historico = buscar_card_especifico(ticket_id)

if not issue:
    print("❌ Erro ao buscar card!")
    sys.exit(1)

print(f"✅ Card encontrado: {issue['fields'].get('summary', 'N/A')[:50]}...")
print(f"\n{'='*60}")
print(f"COMENTÁRIOS BRUTOS ({len(comentarios) if comentarios else 0})")
print(f"{'='*60}\n")

if not comentarios:
    print("❌ Nenhum comentário retornado pela API!")
else:
    for i, com in enumerate(comentarios, 1):
        print(f"--- Comentário {i} ---")
        print(f"  Autor: {com.get('autor', 'N/A')}")
        print(f"  Data: {com.get('data', 'N/A')[:19]}")
        print(f"  Texto ({len(com.get('texto', ''))} chars):")
        texto = com.get('texto', '')
        if texto:
            # Mostra primeiros 200 chars
            print(f"    \"{texto[:200]}{'...' if len(texto) > 200 else ''}\"")
        else:
            print("    ⚠️ TEXTO VAZIO!")
        print()

print(f"\n{'='*60}")
print("FILTRAGEM E CLASSIFICAÇÃO")
print(f"{'='*60}\n")

# Aplica filtro
comentarios_filtrados = filtrar_e_classificar_comentarios(comentarios)

# Padrões de automação usados
padroes_automacao = [
    "mentioned this issue in a commit",
    "mentioned this issue in a branch",
    "mentioned this issue in a pull request",
    "linked a pull request",
    "connected this issue",
    "disconnected this issue",
    "moved this issue",
    "added a commit",
    "referenced this issue",
    "mentioned this page",
    "opened a pull request",
    "closed a pull request",
    "merged a pull request",
    "pushed a commit",
    "created a branch",
    "deleted branch",
]

# Analisa cada comentário
filtrados = 0
validos = 0

for i, com in enumerate(comentarios or [], 1):
    texto = com.get('texto', '').lower()
    autor = com.get('autor', '').lower()
    
    # Verifica se seria filtrado
    eh_automacao = False
    motivo_filtro = None
    
    for padrao in padroes_automacao:
        if padrao.lower() in texto:
            eh_automacao = True
            motivo_filtro = f"Padrão: '{padrao}'"
            break
    
    if any(bot in autor for bot in ['automation', 'bot', 'github', 'bitbucket', 'gitlab', 'jira']):
        eh_automacao = True
        motivo_filtro = f"Autor bot: '{autor}'"
    
    if eh_automacao:
        filtrados += 1
        print(f"❌ Comentário {i} FILTRADO")
        print(f"   Motivo: {motivo_filtro}")
        print(f"   Autor: {com.get('autor', 'N/A')}")
        print(f"   Texto: \"{texto[:100]}...\"")
    else:
        validos += 1
        # Busca classificação
        classificacao = "normal"
        if comentarios_filtrados:
            for cf in comentarios_filtrados:
                if cf.get('autor') == com.get('autor') and cf.get('data') == com.get('data'):
                    classificacao = cf.get('classificacao', 'normal')
                    break
        
        print(f"✅ Comentário {i} VÁLIDO [{classificacao}]")
        print(f"   Autor: {com.get('autor', 'N/A')}")
        print(f"   Texto: \"{com.get('texto', '')[:100]}...\"")
    print()

print(f"\n{'='*60}")
print("RESUMO")
print(f"{'='*60}")
print(f"  Total bruto: {len(comentarios) if comentarios else 0}")
print(f"  Filtrados (automação): {filtrados}")
print(f"  Válidos: {validos}")
print(f"  Após filtro função: {len(comentarios_filtrados) if comentarios_filtrados else 0}")
print()

if comentarios_filtrados:
    print("Comentários que DEVERIAM aparecer:")
    for i, cf in enumerate(comentarios_filtrados[:5], 1):
        print(f"  {i}. [{cf.get('classificacao')}] {cf.get('autor')}: {cf.get('texto', '')[:60]}...")
