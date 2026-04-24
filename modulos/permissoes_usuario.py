"""
================================================================================
PERMISSÕES DE USUÁRIO - NinaDash v8.82
================================================================================
Módulo para gerenciar permissões de acesso baseado no email do usuário logado.

Funcionalidades:
- Normaliza emails (remove +sufixos de teste)
- Cruza email com colaboradores.json
- Retorna abas permitidas para o perfil
- Trata usuários não mapeados

Author: Time de Qualidade NINA
Version: 8.82 (Abril 2026)
"""

import json
import os
import re
from typing import Dict, List, Optional, Tuple

# Tenta importar unidecode, se não disponível usa fallback
try:
    from unidecode import unidecode as _unidecode
    def remover_acentos(texto: str) -> str:
        return _unidecode(texto)
except ImportError:
    import unicodedata
    def remover_acentos(texto: str) -> str:
        """Fallback para remover acentos sem unidecode."""
        nfkd = unicodedata.normalize('NFKD', texto)
        return ''.join(c for c in nfkd if not unicodedata.combining(c))

# ==============================================================================
# CONFIGURAÇÃO
# ==============================================================================

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
COLABORADORES_FILE = os.path.join(CONFIG_DIR, "colaboradores.json")
PERMISSOES_FILE = os.path.join(CONFIG_DIR, "permissoes.json")

# Abas padrão para usuários não mapeados
ABAS_NAO_MAPEADO = ["visao_geral", "sobre"]

# ==============================================================================
# FUNÇÕES DE NORMALIZAÇÃO
# ==============================================================================

def normalizar_email(email: str) -> str:
    """
    Normaliza o email removendo sufixos de teste e convertendo para minúsculas.
    
    Exemplos:
        vinicios.ferreira+teste@confirmationcall.com.br -> vinicios.ferreira@confirmationcall.com.br
        JOAO.SILVA@ConfirmationCall.com.br -> joao.silva@confirmationcall.com.br
    """
    if not email:
        return ""
    
    email = email.lower().strip()
    
    # Remove sufixo +algo antes do @
    # Ex: vinicios.ferreira+teste@... -> vinicios.ferreira@...
    if "+" in email and "@" in email:
        partes = email.split("@")
        usuario = partes[0].split("+")[0]  # Remove tudo após o +
        dominio = partes[1]
        email = f"{usuario}@{dominio}"
    
    return email


def extrair_username(email: str) -> str:
    """
    Extrai o username (parte antes do @) do email.
    
    Exemplo:
        vinicios.ferreira@confirmationcall.com.br -> vinicios.ferreira
    """
    email_normalizado = normalizar_email(email)
    if "@" in email_normalizado:
        return email_normalizado.split("@")[0]
    return email_normalizado


def username_para_nome(username: str) -> str:
    """
    Converte username para nome formatado.
    
    Exemplo:
        vinicios.ferreira -> Vinicios Ferreira
    """
    if not username:
        return ""
    
    # Remove números e caracteres especiais, mantém pontos e underscores
    nome = username.replace(".", " ").replace("_", " ")
    # Capitaliza cada palavra
    nome = " ".join(word.capitalize() for word in nome.split())
    return nome


def normalizar_nome_para_busca(nome: str) -> str:
    """
    Normaliza nome para comparação (remove acentos, lowercase).
    
    Exemplo:
        "Vinícios Ferreira" -> "vinicios ferreira"
    """
    if not nome:
        return ""
    
    # Remove acentos e converte para lowercase
    return remover_acentos(nome.lower().strip())


# ==============================================================================
# FUNÇÕES DE CARREGAMENTO
# ==============================================================================

def carregar_colaboradores() -> Dict:
    """Carrega colaboradores do JSON."""
    if os.path.exists(COLABORADORES_FILE):
        try:
            with open(COLABORADORES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def carregar_permissoes() -> Dict:
    """Carrega permissões do JSON."""
    if os.path.exists(PERMISSOES_FILE):
        try:
            with open(PERMISSOES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


# ==============================================================================
# FUNÇÕES DE BUSCA DE COLABORADOR
# ==============================================================================

def buscar_colaborador_por_email(email: str, colaboradores: Dict) -> Optional[Dict]:
    """
    Busca colaborador pelo email normalizado.
    
    Retorna os dados do colaborador se encontrado, None caso contrário.
    """
    email_normalizado = normalizar_email(email)
    username = extrair_username(email)
    
    for nome, dados in colaboradores.items():
        # Verifica se o email está cadastrado
        email_cadastrado = dados.get("email", "")
        if email_cadastrado:
            email_cad_normalizado = normalizar_email(email_cadastrado)
            if email_cad_normalizado == email_normalizado:
                return {"nome_chave": nome, **dados}
        
        # Verifica se o nome corresponde ao username
        # Ex: "Vinicios Ferreira" vs "vinicios.ferreira"
        nome_normalizado = normalizar_nome_para_busca(nome)
        username_como_nome = normalizar_nome_para_busca(username_para_nome(username))
        
        if nome_normalizado == username_como_nome:
            return {"nome_chave": nome, **dados}
        
        # Verifica também se o nome do cadastro corresponde
        nome_cadastro = dados.get("nome", "")
        if nome_cadastro:
            nome_cadastro_normalizado = normalizar_nome_para_busca(nome_cadastro)
            if nome_cadastro_normalizado == username_como_nome:
                return {"nome_chave": nome, **dados}
    
    return None


def buscar_colaborador_por_nome(nome_busca: str, colaboradores: Dict) -> Optional[Dict]:
    """
    Busca colaborador pelo nome.
    """
    nome_busca_normalizado = normalizar_nome_para_busca(nome_busca)
    
    for nome, dados in colaboradores.items():
        nome_normalizado = normalizar_nome_para_busca(nome)
        if nome_normalizado == nome_busca_normalizado:
            return {"nome_chave": nome, **dados}
        
        # Verifica também pelo campo nome dentro dos dados
        nome_cadastro = dados.get("nome", "")
        if normalizar_nome_para_busca(nome_cadastro) == nome_busca_normalizado:
            return {"nome_chave": nome, **dados}
    
    return None


# ==============================================================================
# FUNÇÕES DE PERMISSÕES
# ==============================================================================

def obter_abas_por_perfil(perfil: str, permissoes: Dict = None) -> List[str]:
    """
    Retorna lista de abas permitidas para um perfil de acesso.
    """
    if permissoes is None:
        permissoes = carregar_permissoes()
    
    dados_perfil = permissoes.get(perfil, {})
    abas = dados_perfil.get("abas", [])
    
    # Se não encontrou ou está vazio, retorna abas padrão
    if not abas:
        # ADMIN sempre tem acesso total
        if perfil == "ADMIN":
            return ["visao_geral", "qa", "dev", "suporte", "clientes", "governanca", 
                    "produto", "historico", "lideranca", "sobre", "admin"]
        return ABAS_NAO_MAPEADO
    
    return abas


def obter_permissoes_usuario(email: str) -> Tuple[Dict, List[str], bool]:
    """
    Obtém as permissões do usuário baseado no email.
    
    Retorna:
        Tuple[colaborador_data, lista_abas, is_mapeado]
        
        - colaborador_data: dados do colaborador ou dados mínimos para não mapeado
        - lista_abas: lista de abas que o usuário pode acessar
        - is_mapeado: True se o usuário foi encontrado em colaboradores.json
    """
    colaboradores = carregar_colaboradores()
    permissoes = carregar_permissoes()
    
    # Tenta encontrar o colaborador pelo email
    colaborador = buscar_colaborador_por_email(email, colaboradores)
    
    if colaborador:
        # Usuário mapeado
        perfil = colaborador.get("perfil_acesso", "VIEWER")
        is_admin = colaborador.get("is_admin", False)
        ativo = colaborador.get("ativo", True)
        
        # Se não estiver ativo, trata como não mapeado
        if not ativo:
            dados_minimos = {
                "nome": username_para_nome(extrair_username(email)),
                "email": normalizar_email(email),
                "perfil_acesso": "VIEWER",
                "is_admin": False,
                "times": [],
                "ativo": False
            }
            return dados_minimos, ABAS_NAO_MAPEADO, False
        
        # Admin tem acesso total
        if is_admin or perfil == "ADMIN":
            abas = obter_abas_por_perfil("ADMIN", permissoes)
        else:
            abas = obter_abas_por_perfil(perfil, permissoes)
        
        return colaborador, abas, True
    
    else:
        # Usuário não mapeado - apenas visão geral e sobre
        dados_minimos = {
            "nome": username_para_nome(extrair_username(email)),
            "email": normalizar_email(email),
            "perfil_acesso": "NAO_MAPEADO",
            "is_admin": False,
            "times": [],
            "ativo": True
        }
        return dados_minimos, ABAS_NAO_MAPEADO, False


def verificar_acesso_aba(email: str, aba: str) -> bool:
    """
    Verifica se o usuário tem acesso a uma aba específica.
    """
    _, abas_permitidas, _ = obter_permissoes_usuario(email)
    return aba in abas_permitidas


def usuario_eh_admin(email: str) -> bool:
    """
    Verifica se o usuário é um Super Admin.
    """
    colaboradores = carregar_colaboradores()
    colaborador = buscar_colaborador_por_email(email, colaboradores)
    
    if colaborador:
        return colaborador.get("is_admin", False)
    return False


# ==============================================================================
# FUNÇÕES DE GERENCIAMENTO
# ==============================================================================

def adicionar_colaborador(
    nome: str,
    email: str,
    times: List[str],
    perfil_acesso: str,
    is_admin: bool = False
) -> bool:
    """
    Adiciona um novo colaborador ao arquivo JSON.
    
    Retorna True se sucesso, False caso contrário.
    """
    colaboradores = carregar_colaboradores()
    
    # Normaliza o email
    email_normalizado = normalizar_email(email)
    
    # Verifica se já existe
    existente = buscar_colaborador_por_email(email_normalizado, colaboradores)
    if existente:
        return False  # Já existe
    
    # Adiciona o novo colaborador
    colaboradores[nome] = {
        "nome": nome,
        "email": email_normalizado,
        "times": times,
        "perfil_acesso": perfil_acesso,
        "is_admin": is_admin,
        "ativo": True
    }
    
    # Salva o arquivo
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(COLABORADORES_FILE, 'w', encoding='utf-8') as f:
            json.dump(colaboradores, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


def atualizar_email_colaborador(nome: str, email: str) -> bool:
    """
    Atualiza o email de um colaborador existente.
    """
    colaboradores = carregar_colaboradores()
    
    if nome in colaboradores:
        colaboradores[nome]["email"] = normalizar_email(email)
        
        try:
            with open(COLABORADORES_FILE, 'w', encoding='utf-8') as f:
                json.dump(colaboradores, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    return False


# ==============================================================================
# FUNÇÕES AUXILIARES PARA UI
# ==============================================================================

def get_info_usuario_logado(email: str) -> Dict:
    """
    Retorna informações formatadas do usuário logado para exibição na UI.
    """
    colaborador, abas, is_mapeado = obter_permissoes_usuario(email)
    
    return {
        "nome": colaborador.get("nome", username_para_nome(extrair_username(email))),
        "email": normalizar_email(email),
        "perfil": colaborador.get("perfil_acesso", "NAO_MAPEADO"),
        "times": colaborador.get("times", []),
        "is_admin": colaborador.get("is_admin", False),
        "is_mapeado": is_mapeado,
        "abas_permitidas": abas,
        "mensagem": None if is_mapeado else "⚠️ Seu perfil ainda não foi mapeado. Acesso limitado."
    }


# ==============================================================================
# REGISTRO DE ACESSOS E VINCULAÇÃO AUTOMÁTICA
# ==============================================================================

ACESSOS_FILE = os.path.join(CONFIG_DIR, "acessos.json")


def carregar_acessos() -> Dict:
    """Carrega histórico de acessos."""
    if os.path.exists(ACESSOS_FILE):
        try:
            with open(ACESSOS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"acessos": [], "nao_vinculados": {}}
    return {"acessos": [], "nao_vinculados": {}}


def salvar_acessos(acessos: Dict) -> bool:
    """Salva histórico de acessos."""
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(ACESSOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(acessos, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


def registrar_acesso(email: str) -> Dict:
    """
    Registra um acesso ao sistema e tenta vincular automaticamente.
    
    Retorna:
        Dict com informações sobre o acesso e se foi vinculado.
    """
    from datetime import datetime
    
    email_normalizado = normalizar_email(email)
    username = extrair_username(email)
    nome_do_email = username_para_nome(username)
    
    colaboradores = carregar_colaboradores()
    acessos = carregar_acessos()
    
    # Registra o acesso
    agora = datetime.now().isoformat()
    registro = {
        "email": email_normalizado,
        "nome_extraido": nome_do_email,
        "data": agora
    }
    
    # Mantém apenas os últimos 1000 acessos
    acessos["acessos"] = acessos.get("acessos", [])[-999:] + [registro]
    
    # Verifica se já está mapeado
    colaborador = buscar_colaborador_por_email(email, colaboradores)
    
    if colaborador:
        # Já está vinculado
        resultado = {
            "status": "vinculado",
            "colaborador": colaborador.get("nome_chave"),
            "perfil": colaborador.get("perfil_acesso"),
            "auto_vinculado": False
        }
    else:
        # Tenta vincular automaticamente pelo nome
        vinculado = tentar_vincular_automatico(email_normalizado, nome_do_email, colaboradores)
        
        if vinculado:
            resultado = {
                "status": "auto_vinculado",
                "colaborador": vinculado,
                "auto_vinculado": True
            }
        else:
            # Adiciona aos não vinculados
            if email_normalizado not in acessos.get("nao_vinculados", {}):
                acessos["nao_vinculados"] = acessos.get("nao_vinculados", {})
                acessos["nao_vinculados"][email_normalizado] = {
                    "nome_extraido": nome_do_email,
                    "primeiro_acesso": agora,
                    "ultimo_acesso": agora,
                    "qtd_acessos": 1
                }
            else:
                acessos["nao_vinculados"][email_normalizado]["ultimo_acesso"] = agora
                acessos["nao_vinculados"][email_normalizado]["qtd_acessos"] += 1
            
            resultado = {
                "status": "nao_vinculado",
                "colaborador": None,
                "sugestoes": encontrar_sugestoes(nome_do_email, colaboradores)
            }
    
    salvar_acessos(acessos)
    return resultado


def tentar_vincular_automatico(email: str, nome_do_email: str, colaboradores: Dict) -> Optional[str]:
    """
    Tenta vincular automaticamente um email a um colaborador pelo nome.
    
    Se encontrar um colaborador cujo nome seja igual ao nome extraído do email
    E que não tenha email cadastrado, vincula automaticamente.
    
    Retorna o nome do colaborador vinculado ou None.
    """
    nome_normalizado = normalizar_nome_para_busca(nome_do_email)
    
    for nome_colab, dados in colaboradores.items():
        # Só vincula se não tiver email cadastrado
        if dados.get("email"):
            continue
        
        # Compara os nomes
        nome_colab_normalizado = normalizar_nome_para_busca(nome_colab)
        nome_dados_normalizado = normalizar_nome_para_busca(dados.get("nome", ""))
        
        if nome_normalizado == nome_colab_normalizado or nome_normalizado == nome_dados_normalizado:
            # Match encontrado! Vincula automaticamente
            colaboradores[nome_colab]["email"] = email
            
            try:
                with open(COLABORADORES_FILE, 'w', encoding='utf-8') as f:
                    json.dump(colaboradores, f, ensure_ascii=False, indent=2)
                return nome_colab
            except:
                return None
    
    return None


def encontrar_sugestoes(nome_do_email: str, colaboradores: Dict, limite: int = 3) -> List[str]:
    """
    Encontra colaboradores com nomes similares para sugestão de vínculo.
    """
    nome_normalizado = normalizar_nome_para_busca(nome_do_email)
    partes_nome = set(nome_normalizado.split())
    
    sugestoes = []
    
    for nome_colab, dados in colaboradores.items():
        # Só sugere se não tiver email
        if dados.get("email"):
            continue
        
        nome_colab_normalizado = normalizar_nome_para_busca(nome_colab)
        partes_colab = set(nome_colab_normalizado.split())
        
        # Calcula similaridade por partes do nome em comum
        comum = partes_nome & partes_colab
        if comum:
            score = len(comum) / max(len(partes_nome), len(partes_colab))
            sugestoes.append((nome_colab, score))
    
    # Ordena por score e retorna os melhores
    sugestoes.sort(key=lambda x: x[1], reverse=True)
    return [s[0] for s in sugestoes[:limite]]


def obter_nao_vinculados() -> Dict:
    """
    Retorna lista de emails que acessaram mas não estão vinculados.
    """
    acessos = carregar_acessos()
    return acessos.get("nao_vinculados", {})


def vincular_email_colaborador(email: str, nome_colaborador: str) -> bool:
    """
    Vincula manualmente um email a um colaborador.
    """
    colaboradores = carregar_colaboradores()
    acessos = carregar_acessos()
    
    if nome_colaborador in colaboradores:
        colaboradores[nome_colaborador]["email"] = normalizar_email(email)
        
        try:
            with open(COLABORADORES_FILE, 'w', encoding='utf-8') as f:
                json.dump(colaboradores, f, ensure_ascii=False, indent=2)
            
            # Remove dos não vinculados
            email_norm = normalizar_email(email)
            if email_norm in acessos.get("nao_vinculados", {}):
                del acessos["nao_vinculados"][email_norm]
                salvar_acessos(acessos)
            
            return True
        except:
            return False
    
    return False
