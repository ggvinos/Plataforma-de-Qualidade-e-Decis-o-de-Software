"""
🏷️ Script Interativo para Classificar Colaboradores

Permite classificar rapidamente cada colaborador por time e cargo.
"""

import json
import os

# Caminho dos arquivos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, 'config', 'colaboradores_raw.json')
OUTPUT_FILE = os.path.join(BASE_DIR, 'config', 'colaboradores.json')

# Opções de times
TIMES = {
    '1': 'DEV',
    '2': 'QA', 
    '3': 'SUPORTE',
    '4': 'PRODUTO',
    '5': 'IMPLANTACAO',
    '6': 'LIDERANCA',
    '7': 'CS',
    '8': 'COMERCIAL',
    '9': 'EXTERNO',
    '0': 'SISTEMA'  # Para automações
}

# Opções de cargos/perfis
CARGOS = {
    '1': 'desenvolvedor',
    '2': 'qa',
    '3': 'analista_suporte',
    '4': 'analista_produto',
    '5': 'analista_implantacao',
    '6': 'gestor',
    '7': 'techlead',
    '8': 'cs',
    '9': 'comercial',
    '0': 'sistema'
}

# Níveis de acesso
ACESSOS = {
    '1': 'admin',      # Acesso total + painel admin
    '2': 'lider',      # Vê métricas do time
    '3': 'membro',     # Vê suas próprias métricas
    '4': 'visualizador' # Apenas visualiza
}


def carregar_dados():
    """Carrega dados existentes."""
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    elif os.path.exists(INPUT_FILE):
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def salvar_dados(dados):
    """Salva dados no arquivo de saída."""
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Salvo em: {OUTPUT_FILE}")


def mostrar_menu_times():
    """Mostra menu de times."""
    print("\n📋 TIMES:")
    for k, v in TIMES.items():
        print(f"  [{k}] {v}")


def mostrar_menu_cargos():
    """Mostra menu de cargos."""
    print("\n👤 CARGOS:")
    for k, v in CARGOS.items():
        print(f"  [{k}] {v}")


def mostrar_menu_acessos():
    """Mostra menu de níveis de acesso."""
    print("\n🔐 ACESSO:")
    for k, v in ACESSOS.items():
        print(f"  [{k}] {v}")


def mostrar_info_colaborador(nome, dados):
    """Mostra informações do colaborador."""
    print("\n" + "="*60)
    print(f"👤 {nome}")
    print("-"*60)
    print(f"  📊 Aparece como: {', '.join(dados.get('aparece_como', []))}")
    print(f"  📁 Projetos: {', '.join(dados.get('projetos', []))}")
    print(f"  🔢 Cards: DEV={dados.get('como_dev', 0)} | QA={dados.get('como_qa', 0)} | Relator={dados.get('como_relator', 0)}")
    
    if dados.get('time'):
        print(f"  ✅ Time atual: {dados['time']}")
    if dados.get('cargo'):
        print(f"  ✅ Cargo atual: {dados['cargo']}")
    if dados.get('acesso'):
        print(f"  ✅ Acesso atual: {dados['acesso']}")


def classificar_rapido():
    """Modo de classificação rápida."""
    dados = carregar_dados()
    
    # Filtra apenas os não classificados
    pendentes = [(nome, d) for nome, d in dados.items() 
                 if not d.get('time') or not d.get('cargo')]
    
    if not pendentes:
        print("\n✅ Todos os colaboradores já foram classificados!")
        return
    
    print(f"\n📋 {len(pendentes)} colaboradores pendentes de classificação")
    print("💡 Dica: Digite 's' para pular, 'q' para sair e salvar")
    
    mostrar_menu_times()
    mostrar_menu_cargos()
    mostrar_menu_acessos()
    
    for nome, info in pendentes:
        mostrar_info_colaborador(nome, info)
        
        # Time
        while True:
            time_input = input("\n🏢 Time [1-9, 0=Sistema, s=pular, q=sair]: ").strip().lower()
            if time_input == 'q':
                salvar_dados(dados)
                return
            if time_input == 's':
                break
            if time_input in TIMES:
                dados[nome]['time'] = TIMES[time_input]
                break
            print("❌ Opção inválida")
        
        if time_input == 's':
            continue
        
        # Cargo
        while True:
            cargo_input = input("👤 Cargo [1-9, 0=Sistema, s=pular]: ").strip().lower()
            if cargo_input == 's':
                break
            if cargo_input in CARGOS:
                dados[nome]['cargo'] = CARGOS[cargo_input]
                break
            print("❌ Opção inválida")
        
        # Acesso
        while True:
            acesso_input = input("🔐 Acesso [1=admin, 2=lider, 3=membro, 4=visualizador]: ").strip().lower()
            if acesso_input == 's':
                break
            if acesso_input in ACESSOS:
                dados[nome]['acesso'] = ACESSOS[acesso_input]
                break
            print("❌ Opção inválida")
        
        # Múltiplos times?
        multi = input("🔄 Tem outro time? (s/n): ").strip().lower()
        if multi == 's':
            times_extras = []
            while True:
                extra = input("  Time adicional [1-9 ou Enter para terminar]: ").strip()
                if not extra:
                    break
                if extra in TIMES:
                    times_extras.append(TIMES[extra])
            if times_extras:
                dados[nome]['times_adicionais'] = times_extras
        
        print(f"✅ {nome} classificado!")
    
    salvar_dados(dados)
    print("\n🎉 Classificação concluída!")


def modo_batch():
    """Modo batch - classifica vários de uma vez com mesmo time."""
    dados = carregar_dados()
    
    print("\n📦 MODO BATCH - Classificar múltiplos colaboradores")
    mostrar_menu_times()
    
    time_input = input("\n🏢 Escolha o time: ").strip()
    if time_input not in TIMES:
        print("❌ Time inválido")
        return
    
    time_escolhido = TIMES[time_input]
    
    mostrar_menu_cargos()
    cargo_input = input("👤 Escolha o cargo padrão: ").strip()
    if cargo_input not in CARGOS:
        print("❌ Cargo inválido")
        return
    
    cargo_escolhido = CARGOS[cargo_input]
    
    mostrar_menu_acessos()
    acesso_input = input("🔐 Escolha o acesso padrão: ").strip()
    if acesso_input not in ACESSOS:
        print("❌ Acesso inválido")
        return
    
    acesso_escolhido = ACESSOS[acesso_input]
    
    print(f"\n📋 Colaboradores não classificados:")
    pendentes = [(i, nome) for i, (nome, d) in enumerate(dados.items(), 1) 
                 if not d.get('time')]
    
    for i, nome in pendentes:
        print(f"  [{i}] {nome}")
    
    selecao = input("\n🎯 Digite os números separados por vírgula (ex: 1,3,5): ").strip()
    
    try:
        indices = [int(x.strip()) for x in selecao.split(',')]
        nomes_para_classificar = [pendentes[i-1][1] for i in indices if 0 < i <= len(pendentes)]
        
        for nome in nomes_para_classificar:
            dados[nome]['time'] = time_escolhido
            dados[nome]['cargo'] = cargo_escolhido
            dados[nome]['acesso'] = acesso_escolhido
            print(f"  ✅ {nome} → {time_escolhido}/{cargo_escolhido}")
        
        salvar_dados(dados)
        
    except (ValueError, IndexError) as e:
        print(f"❌ Erro na seleção: {e}")


def listar_classificados():
    """Lista colaboradores já classificados."""
    dados = carregar_dados()
    
    # Agrupa por time
    por_time = {}
    for nome, info in dados.items():
        time = info.get('time', 'NÃO CLASSIFICADO')
        if time not in por_time:
            por_time[time] = []
        por_time[time].append((nome, info))
    
    print("\n" + "="*60)
    print("📊 COLABORADORES POR TIME")
    print("="*60)
    
    for time in sorted(por_time.keys()):
        pessoas = por_time[time]
        print(f"\n🏢 {time} ({len(pessoas)} pessoas)")
        print("-"*40)
        for nome, info in sorted(pessoas):
            cargo = info.get('cargo', '?')
            acesso = info.get('acesso', '?')
            extras = info.get('times_adicionais', [])
            extra_str = f" + {', '.join(extras)}" if extras else ""
            print(f"  • {nome}")
            print(f"    └─ {cargo} | {acesso}{extra_str}")


def editar_colaborador():
    """Edita um colaborador específico."""
    dados = carregar_dados()
    
    print("\n🔍 Digite parte do nome para buscar:")
    busca = input("> ").strip().lower()
    
    encontrados = [(nome, d) for nome, d in dados.items() 
                   if busca in nome.lower()]
    
    if not encontrados:
        print("❌ Nenhum colaborador encontrado")
        return
    
    print("\n📋 Encontrados:")
    for i, (nome, _) in enumerate(encontrados, 1):
        print(f"  [{i}] {nome}")
    
    sel = input("\nEscolha [número]: ").strip()
    try:
        idx = int(sel) - 1
        nome, info = encontrados[idx]
        
        mostrar_info_colaborador(nome, info)
        mostrar_menu_times()
        mostrar_menu_cargos()
        mostrar_menu_acessos()
        
        time_input = input("\n🏢 Novo time [Enter para manter]: ").strip()
        if time_input in TIMES:
            dados[nome]['time'] = TIMES[time_input]
        
        cargo_input = input("👤 Novo cargo [Enter para manter]: ").strip()
        if cargo_input in CARGOS:
            dados[nome]['cargo'] = CARGOS[cargo_input]
        
        acesso_input = input("🔐 Novo acesso [Enter para manter]: ").strip()
        if acesso_input in ACESSOS:
            dados[nome]['acesso'] = ACESSOS[acesso_input]
        
        salvar_dados(dados)
        print(f"✅ {nome} atualizado!")
        
    except (ValueError, IndexError):
        print("❌ Seleção inválida")


def main():
    """Menu principal."""
    while True:
        print("\n" + "="*60)
        print("🏷️  CLASSIFICADOR DE COLABORADORES")
        print("="*60)
        print("\n  [1] 🚀 Classificar pendentes (um por um)")
        print("  [2] 📦 Modo batch (classificar vários de uma vez)")
        print("  [3] 📋 Listar classificados")
        print("  [4] ✏️  Editar colaborador")
        print("  [5] 💾 Salvar e sair")
        print("  [0] 🚪 Sair sem salvar")
        
        opcao = input("\n👉 Escolha: ").strip()
        
        if opcao == '1':
            classificar_rapido()
        elif opcao == '2':
            modo_batch()
        elif opcao == '3':
            listar_classificados()
        elif opcao == '4':
            editar_colaborador()
        elif opcao == '5':
            print("\n👋 Até logo!")
            break
        elif opcao == '0':
            print("\n⚠️ Saindo sem salvar alterações...")
            break
        else:
            print("❌ Opção inválida")


if __name__ == "__main__":
    main()
