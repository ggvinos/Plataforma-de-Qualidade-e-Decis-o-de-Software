"""
🔍 Script para mapear todos os colaboradores que aparecem nos cards do Jira

Este script extrai todos os nomes únicos de:
- Desenvolvedores (assignee)
- QAs responsáveis 
- Relatores (reporter)

Gera um arquivo JSON para classificação por time.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from collections import defaultdict
import requests
from modulos.config import CUSTOM_FIELDS, JIRA_BASE_URL
from modulos.utils import get_secrets

def buscar_dados_jira_direto(projeto: str, jql: str):
    """Busca dados do Jira diretamente (sem cache Streamlit)."""
    secrets = get_secrets()
    if not secrets["email"] or not secrets["token"]:
        return None
    
    base_url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
    headers = {"Accept": "application/json"}
    
    fields = [
        "key", "summary", "status", "issuetype", "assignee", "created", "updated",
        "resolutiondate", "priority", "project", "labels", "reporter", "resolution",
        CUSTOM_FIELDS["qa_responsavel"],
    ]
    
    all_issues = []
    next_page_token = None
    
    while True:
        params = {
            "jql": jql,
            "maxResults": 100,
            "fields": ",".join(fields)
        }
        if next_page_token:
            params["nextPageToken"] = next_page_token
        
        response = requests.get(
            base_url, 
            headers=headers, 
            params=params, 
            auth=(secrets["email"], secrets["token"]),
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        
        issues = data.get('issues', [])
        all_issues.extend(issues)
        
        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break
    
    return all_issues

def extrair_colaboradores():
    """Extrai todos os colaboradores únicos dos projetos."""
    
    colaboradores = defaultdict(lambda: {
        'aparece_como': set(),
        'projetos': set(),
        'total_cards': 0,
        'como_dev': 0,
        'como_qa': 0,
        'como_relator': 0
    })
    
    projetos = ['PB', 'SD', 'QA', 'VALPROD']
    
    for projeto in projetos:
        print(f"\n📂 Buscando projeto {projeto}...")
        
        # JQL para pegar todos os cards dos últimos 6 meses
        jql = f'project = {projeto} AND created >= -180d ORDER BY created DESC'
        
        try:
            issues = buscar_dados_jira_direto(projeto, jql)
            if not issues:
                print(f"  ⚠️ Nenhum card encontrado")
                continue
            
            print(f"  ✅ {len(issues)} cards encontrados")
            
            for issue in issues:
                f = issue.get('fields', {})
                
                # Desenvolvedor (assignee)
                if f.get('assignee'):
                    nome = f['assignee'].get('displayName', '')
                    if nome and nome != 'Não atribuído':
                        colaboradores[nome]['aparece_como'].add('DEV')
                        colaboradores[nome]['projetos'].add(projeto)
                        colaboradores[nome]['total_cards'] += 1
                        colaboradores[nome]['como_dev'] += 1
                
                # QA Responsável
                qa_f = f.get(CUSTOM_FIELDS['qa_responsavel'])
                if qa_f:
                    if isinstance(qa_f, dict):
                        nome = qa_f.get('displayName', '')
                    elif isinstance(qa_f, list) and qa_f:
                        nome = qa_f[0].get('displayName', '')
                    else:
                        nome = ''
                    
                    if nome and nome != 'Não atribuído':
                        colaboradores[nome]['aparece_como'].add('QA')
                        colaboradores[nome]['projetos'].add(projeto)
                        colaboradores[nome]['total_cards'] += 1
                        colaboradores[nome]['como_qa'] += 1
                
                # Relator (reporter)
                if f.get('reporter'):
                    nome = f['reporter'].get('displayName', '')
                    if nome and nome not in ['Sistema', 'Não informado', '']:
                        colaboradores[nome]['aparece_como'].add('RELATOR')
                        colaboradores[nome]['projetos'].add(projeto)
                        colaboradores[nome]['como_relator'] += 1
        
        except Exception as e:
            print(f"  ❌ Erro: {e}")
    
    return colaboradores


def gerar_relatorio(colaboradores):
    """Gera relatório e arquivo JSON para classificação."""
    
    # Converte sets para listas para JSON
    resultado = {}
    for nome, dados in sorted(colaboradores.items()):
        resultado[nome] = {
            'aparece_como': list(dados['aparece_como']),
            'projetos': list(dados['projetos']),
            'total_cards': dados['total_cards'],
            'como_dev': dados['como_dev'],
            'como_qa': dados['como_qa'],
            'como_relator': dados['como_relator'],
            # Campos para preencher manualmente
            'time': '',  # DEV, QA, SUPORTE, PRODUTO, LIDERANCA, etc
            'perfil': '',  # desenvolvedor, qa, analista, gestor, etc
            'ativo': True
        }
    
    # Salva JSON
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'colaboradores_raw.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Arquivo salvo em: {output_path}")
    
    # Relatório no console
    print("\n" + "="*80)
    print("📊 RELATÓRIO DE COLABORADORES")
    print("="*80)
    
    # Agrupa por papel predominante
    devs = []
    qas = []
    outros = []
    
    for nome, dados in resultado.items():
        if 'DEV' in dados['aparece_como'] and dados['como_dev'] > dados['como_qa']:
            devs.append((nome, dados))
        elif 'QA' in dados['aparece_como'] and dados['como_qa'] > 0:
            qas.append((nome, dados))
        else:
            outros.append((nome, dados))
    
    print(f"\n👨‍💻 APARECEM COMO DESENVOLVEDORES ({len(devs)} pessoas):")
    print("-"*60)
    for nome, dados in sorted(devs, key=lambda x: x[1]['como_dev'], reverse=True):
        print(f"  {nome}")
        print(f"    📊 {dados['como_dev']} cards como DEV | Projetos: {', '.join(dados['projetos'])}")
    
    print(f"\n🧪 APARECEM COMO QA ({len(qas)} pessoas):")
    print("-"*60)
    for nome, dados in sorted(qas, key=lambda x: x[1]['como_qa'], reverse=True):
        print(f"  {nome}")
        print(f"    📊 {dados['como_qa']} cards como QA | Projetos: {', '.join(dados['projetos'])}")
    
    print(f"\n👥 OUTROS (relatores, etc) ({len(outros)} pessoas):")
    print("-"*60)
    for nome, dados in sorted(outros, key=lambda x: x[0]):
        print(f"  {nome}")
        print(f"    📊 Aparece como: {', '.join(dados['aparece_como'])} | Projetos: {', '.join(dados['projetos'])}")
    
    print("\n" + "="*80)
    print(f"📈 TOTAIS: {len(resultado)} colaboradores únicos")
    print(f"   - {len(devs)} aparecem como DEV")
    print(f"   - {len(qas)} aparecem como QA") 
    print(f"   - {len(outros)} outros (relatores, etc)")
    print("="*80)
    
    return resultado


if __name__ == "__main__":
    print("🔍 Mapeando colaboradores do Jira...")
    print("="*80)
    
    colaboradores = extrair_colaboradores()
    resultado = gerar_relatorio(colaboradores)
    
    print("\n💡 PRÓXIMOS PASSOS:")
    print("   1. Edite o arquivo config/colaboradores_raw.json")
    print("   2. Preencha os campos 'time' e 'perfil' para cada pessoa")
    print("   3. Execute o script de validação para criar colaboradores.json final")
