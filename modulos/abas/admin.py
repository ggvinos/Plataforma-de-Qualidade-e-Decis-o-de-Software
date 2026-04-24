"""
================================================================================
ABA ADMIN - NinaDash v8.82 (Simplificado)
================================================================================
Painel Administrativo - Visualização de Colaboradores e Permissões.

Author: Time de Qualidade NINA
Version: 8.82 (Abril 2026)
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Any

# Import das funções de acessos
from modulos.permissoes_usuario import (
    obter_nao_vinculados,
    vincular_email_colaborador,
    carregar_acessos,
)

# ================================================================================
# CONSTANTES
# ================================================================================

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config")
COLABORADORES_FILE = os.path.join(CONFIG_DIR, "colaboradores.json")
PERMISSOES_FILE = os.path.join(CONFIG_DIR, "permissoes.json")

TIMES_CONFIG = {
    "DEV": {"cor": "#3b82f6", "icone": "👨‍💻"},
    "QA": {"cor": "#22c55e", "icone": "🔬"},
    "SUPORTE": {"cor": "#f59e0b", "icone": "🎧"},
    "PRODUTO": {"cor": "#8b5cf6", "icone": "📦"},
    "IMPLANTAÇÃO": {"cor": "#ec4899", "icone": "🚀"},
    "LIDERANÇA": {"cor": "#ef4444", "icone": "👑"},
    "CS": {"cor": "#06b6d4", "icone": "🤝"},
    "COMERCIAL": {"cor": "#84cc16", "icone": "💼"},
}

# ================================================================================
# FUNÇÕES
# ================================================================================

def carregar_colaboradores() -> Dict[str, Any]:
    """Carrega colaboradores do JSON."""
    if os.path.exists(COLABORADORES_FILE):
        with open(COLABORADORES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def carregar_permissoes() -> Dict[str, Any]:
    """Carrega permissões do JSON."""
    if os.path.exists(PERMISSOES_FILE):
        with open(PERMISSOES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def salvar_colaboradores(colaboradores: Dict[str, Any]) -> bool:
    """Salva colaboradores no JSON."""
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(COLABORADORES_FILE, 'w', encoding='utf-8') as f:
            json.dump(colaboradores, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def salvar_permissoes(permissoes: Dict[str, Any]) -> bool:
    """Salva permissões no JSON."""
    try:
        with open(PERMISSOES_FILE, 'w', encoding='utf-8') as f:
            json.dump(permissoes, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

# ================================================================================
# ABA ADMIN SIMPLIFICADA
# ================================================================================

def aba_admin():
    """Painel Administrativo Simplificado."""
    
    # Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 20px 24px; border-radius: 12px; margin-bottom: 20px;">
        <h2 style="margin: 0; color: #fff; font-size: 22px;">⚙️ Painel Administrativo</h2>
        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 13px;">Colaboradores e Permissões de Acesso</p>
    </div>
    """, unsafe_allow_html=True)
    
    colaboradores = carregar_colaboradores()
    permissoes = carregar_permissoes()
    nao_vinculados = obter_nao_vinculados()
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 Colaboradores", 
        "🔗 Vincular Acessos", 
        "➕ Novo Colaborador", 
        "🔐 Permissões por Grupo", 
        "📥 Exportar"
    ])
    
    # ===== TAB 1: COLABORADORES =====
    with tab1:
        # Estatísticas rápidas
        total = len([c for c in colaboradores.values() if c.get("ativo", True)])
        admins = len([c for c in colaboradores.values() if c.get("is_admin", False)])
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Ativos", total)
        col2.metric("Super Admins", f"👑 {admins}")
        
        # Contagem por time
        contagem = {}
        for c in colaboradores.values():
            for t in c.get("times", []):
                contagem[t] = contagem.get(t, 0) + 1
        col3.metric("Times Ativos", len(contagem))
        col4.metric("Perfis", len(set(c.get("perfil_acesso") for c in colaboradores.values())))
        
        st.markdown("---")
        
        # Grid de times com membros
        st.markdown("### 📊 Distribuição por Time")
        
        cols = st.columns(4)
        for i, (time, config) in enumerate(TIMES_CONFIG.items()):
            membros = [nome for nome, dados in colaboradores.items() 
                      if time in dados.get("times", []) and dados.get("ativo", True)]
            
            with cols[i % 4]:
                st.markdown(f"""
                <div style="background: {config['cor']}10; border: 2px solid {config['cor']}50; 
                            border-radius: 10px; padding: 12px; margin-bottom: 12px; min-height: 120px;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <span style="font-size: 20px;">{config['icone']}</span>
                        <span style="font-weight: 700; color: {config['cor']};">{time}</span>
                        <span style="background: {config['cor']}; color: white; padding: 2px 8px; 
                                    border-radius: 10px; font-size: 11px; margin-left: auto;">{len(membros)}</span>
                    </div>
                    <div style="font-size: 11px; color: #64748b; line-height: 1.4;">
                        {', '.join(membros[:5])}{' +' + str(len(membros)-5) if len(membros) > 5 else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Tabela completa com email
        st.markdown("### 📋 Lista de Colaboradores")
        
        # Filtro de colaboradores sem email
        sem_email = [nome for nome, dados in colaboradores.items() 
                     if not dados.get("email") and dados.get("ativo", True)]
        
        if sem_email:
            st.warning(f"⚠️ {len(sem_email)} colaborador(es) sem email cadastrado")
        
        rows = []
        for nome, dados in sorted(colaboradores.items()):
            if dados.get("ativo", True):
                email = dados.get("email", "")
                rows.append({
                    "Nome": nome,
                    "Email": email if email else "❌ Sem email",
                    "Times": ", ".join(dados.get("times", [])) or "—",
                    "Perfil": dados.get("perfil_acesso", "VIEWER"),
                    "Admin": "👑" if dados.get("is_admin") else ""
                })
        
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True, height=400)
        
        # Seção para adicionar email aos colaboradores sem email
        if sem_email:
            st.markdown("---")
            st.markdown("### ✏️ Adicionar Email a Colaboradores")
            st.caption("Selecione um colaborador e adicione o email corporativo.")
            
            col1, col2 = st.columns([2, 3])
            with col1:
                colab_selecionado = st.selectbox(
                    "Colaborador",
                    options=sem_email,
                    key="colab_add_email",
                    help="Selecione um colaborador sem email"
                )
            
            with col2:
                email_input = st.text_input(
                    "Email",
                    placeholder="nome.sobrenome@confirmationcall.com.br",
                    key="email_add_colab"
                )
            
            if st.button("💾 Salvar Email", use_container_width=True, key="btn_salvar_email"):
                if email_input and "@" in email_input:
                    colaboradores[colab_selecionado]["email"] = email_input.lower().strip()
                    if salvar_colaboradores(colaboradores):
                        st.success(f"✅ Email adicionado para '{colab_selecionado}'!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao salvar")
                else:
                    st.error("❌ Email inválido")
    
    # ===== TAB 2: VINCULAR ACESSOS =====
    with tab2:
        st.markdown("### 🔗 Vincular Acessos Não Mapeados")
        st.info("💡 Usuários que acessaram o sistema mas não estão vinculados a nenhum colaborador. Vincule-os manualmente.")
        
        if nao_vinculados:
            st.warning(f"⚠️ {len(nao_vinculados)} email(s) aguardando vinculação")
            
            # Lista os não vinculados
            for email, dados in nao_vinculados.items():
                with st.expander(f"📧 {email}", expanded=True):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.markdown(f"""
                        **Nome extraído:** {dados.get('nome_extraido', '?')}  
                        **Primeiro acesso:** {dados.get('primeiro_acesso', '?')[:10]}  
                        **Último acesso:** {dados.get('ultimo_acesso', '?')[:10]}  
                        **Qtd. acessos:** {dados.get('qtd_acessos', 0)}
                        """)
                    
                    with col2:
                        # Lista colaboradores sem email para vincular
                        sem_email = [nome for nome, d in colaboradores.items() 
                                    if not d.get("email") and d.get("ativo", True)]
                        
                        if sem_email:
                            colab_vincular = st.selectbox(
                                "Vincular a:",
                                options=["-- Selecione --"] + sem_email,
                                key=f"vincular_{email}"
                            )
                        else:
                            st.caption("Todos os colaboradores já têm email")
                            colab_vincular = None
                    
                    with col3:
                        if sem_email and st.button("✅ Vincular", key=f"btn_vincular_{email}"):
                            if colab_vincular and colab_vincular != "-- Selecione --":
                                if vincular_email_colaborador(email, colab_vincular):
                                    st.success(f"✅ Vinculado!")
                                    st.rerun()
                                else:
                                    st.error("❌ Erro")
        else:
            st.success("✅ Todos os acessos estão vinculados!")
        
        st.markdown("---")
        
        # Histórico de acessos recentes
        st.markdown("### 📊 Acessos Recentes")
        acessos = carregar_acessos()
        ultimos = acessos.get("acessos", [])[-20:][::-1]  # Últimos 20, mais recente primeiro
        
        if ultimos:
            rows = []
            for acesso in ultimos:
                rows.append({
                    "Data": acesso.get("data", "")[:16].replace("T", " "),
                    "Email": acesso.get("email", ""),
                    "Nome": acesso.get("nome_extraido", "")
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum acesso registrado ainda.")
    
    # ===== TAB 3: NOVO COLABORADOR =====
    with tab3:
        st.markdown("### ➕ Cadastrar Novo Colaborador")
        st.info("💡 Adicione um novo colaborador ao sistema. O email será usado para identificação no login.")
        
        with st.form("form_novo_colaborador", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                novo_nome = st.text_input(
                    "Nome Completo *",
                    placeholder="Ex: João Silva",
                    help="Nome completo do colaborador"
                )
                
                novo_email = st.text_input(
                    "Email Corporativo *",
                    placeholder="Ex: joao.silva@confirmationcall.com.br",
                    help="Email usado para login"
                )
            
            with col2:
                perfis_disponiveis = ["VIEWER", "DEV", "QA", "SUPORTE", "IMPLANTAÇÃO", "PRODUTO", "CS", "COMERCIAL", "LIDERANÇA", "ADMIN"]
                novo_perfil = st.selectbox(
                    "Perfil de Acesso *",
                    options=perfis_disponiveis,
                    index=0,
                    help="Define quais abas o colaborador pode acessar"
                )
                
                novo_admin = st.checkbox(
                    "👑 É Super Admin?",
                    value=False,
                    help="Super Admins têm acesso total ao sistema"
                )
            
            # Times (multiselect)
            novos_times = st.multiselect(
                "Times",
                options=list(TIMES_CONFIG.keys()),
                default=[],
                help="Selecione os times aos quais o colaborador pertence"
            )
            
            submitted = st.form_submit_button("✅ Cadastrar Colaborador", type="primary", use_container_width=True)
            
            if submitted:
                # Validações
                erros = []
                if not novo_nome or len(novo_nome.strip()) < 3:
                    erros.append("Nome deve ter pelo menos 3 caracteres")
                if not novo_email or "@" not in novo_email:
                    erros.append("Email inválido")
                elif not novo_email.lower().endswith("@confirmationcall.com.br"):
                    erros.append("Email deve ser do domínio @confirmationcall.com.br")
                
                # Verifica se já existe
                if novo_nome.strip() in colaboradores:
                    erros.append(f"Já existe um colaborador com o nome '{novo_nome}'")
                
                # Verifica email duplicado
                email_normalizado = novo_email.lower().strip()
                for nome, dados in colaboradores.items():
                    if dados.get("email", "").lower() == email_normalizado:
                        erros.append(f"Email já cadastrado para '{nome}'")
                        break
                
                if erros:
                    for erro in erros:
                        st.error(f"❌ {erro}")
                else:
                    # Adiciona o colaborador
                    colaboradores[novo_nome.strip()] = {
                        "nome": novo_nome.strip(),
                        "email": email_normalizado,
                        "times": novos_times,
                        "perfil_acesso": novo_perfil,
                        "is_admin": novo_admin,
                        "ativo": True
                    }
                    
                    if salvar_colaboradores(colaboradores):
                        st.success(f"✅ Colaborador '{novo_nome}' cadastrado com sucesso!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Erro ao salvar. Tente novamente.")
        
        st.markdown("---")
        
        # Edição rápida de emails
        st.markdown("### ✏️ Atualizar Email de Colaborador Existente")
        st.caption("Use para mapear colaboradores que ainda não têm email cadastrado.")
        
        # Lista colaboradores sem email
        sem_email = [nome for nome, dados in colaboradores.items() 
                     if not dados.get("email") and dados.get("ativo", True)]
        
        if sem_email:
            col1, col2 = st.columns([2, 3])
            with col1:
                colab_selecionado = st.selectbox(
                    "Colaborador",
                    options=sem_email,
                    help="Selecione um colaborador para adicionar email"
                )
            
            with col2:
                email_atualizar = st.text_input(
                    "Email",
                    placeholder="email@confirmationcall.com.br",
                    key="email_atualizar"
                )
            
            if st.button("💾 Atualizar Email", use_container_width=True):
                if email_atualizar and "@" in email_atualizar:
                    colaboradores[colab_selecionado]["email"] = email_atualizar.lower().strip()
                    if salvar_colaboradores(colaboradores):
                        st.success(f"✅ Email atualizado para '{colab_selecionado}'!")
                        st.rerun()
                else:
                    st.error("❌ Email inválido")
        else:
            st.success("✅ Todos os colaboradores já possuem email cadastrado!")
    
    # ===== TAB 4: PERMISSÕES =====
    with tab4:
        st.markdown("### 🔐 Configuração de Permissões por Perfil")
        st.info("💡 Configure quais abas cada perfil de acesso pode visualizar.")
        
        abas_disponiveis = ["visao_geral", "qa", "dev", "suporte", "clientes", "governanca", "produto", "historico", "lideranca", "sobre", "admin"]
        abas_labels = {
            "visao_geral": "📊 Visão Geral",
            "qa": "🔬 QA",
            "dev": "👨‍💻 Dev",
            "suporte": "🎯 Suporte/Implantação",
            "clientes": "🏢 Clientes",
            "governanca": "📋 Governança",
            "produto": "📦 Produto",
            "historico": "📈 Histórico",
            "lideranca": "🎯 Liderança",
            "sobre": "ℹ️ Sobre",
            "admin": "⚙️ Admin"
        }
        
        perfis = ["ADMIN", "LIDERANÇA", "DEV", "QA", "SUPORTE", "IMPLANTAÇÃO", "PRODUTO", "CS", "COMERCIAL", "VIEWER"]
        
        # Carrega ou inicializa permissões
        if not permissoes or "_meta" not in permissoes:
            permissoes = carregar_permissoes()
        
        # Tabela de permissões
        st.markdown("#### Matriz de Permissões")
        
        # Header
        header_cols = st.columns([2] + [1] * len(abas_disponiveis))
        header_cols[0].markdown("**Perfil**")
        for i, aba in enumerate(abas_disponiveis):
            header_cols[i+1].markdown(f"**{abas_labels[aba].split()[0]}**", help=abas_labels[aba])
        
        st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)
        
        # Linhas editáveis
        permissoes_editadas = {}
        for perfil in perfis:
            cols = st.columns([2] + [1] * len(abas_disponiveis))
            cols[0].markdown(f"**{perfil}**")
            
            abas_perfil = permissoes.get(perfil, {}).get("abas", [])
            novas_abas = []
            
            for i, aba in enumerate(abas_disponiveis):
                checked = cols[i+1].checkbox(
                    aba, 
                    value=aba in abas_perfil,
                    key=f"perm_{perfil}_{aba}",
                    label_visibility="collapsed"
                )
                if checked:
                    novas_abas.append(aba)
            
            permissoes_editadas[perfil] = {
                "descricao": permissoes.get(perfil, {}).get("descricao", ""),
                "abas": novas_abas
            }
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Salvar Permissões", type="primary", use_container_width=True):
                permissoes_editadas["_meta"] = permissoes.get("_meta", {
                    "descricao": "Configuração de permissões",
                    "atualizado": datetime.now().isoformat()
                })
                permissoes_editadas["_meta"]["atualizado"] = datetime.now().isoformat()
                
                if salvar_permissoes(permissoes_editadas):
                    st.success("✅ Permissões salvas!")
                    st.rerun()
    
    # ===== TAB 5: EXPORTAR =====
    with tab5:
        st.markdown("### 📥 Exportar Configurações")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Colaboradores")
            json_colab = json.dumps(colaboradores, ensure_ascii=False, indent=2)
            st.download_button(
                "📥 Baixar colaboradores.json",
                data=json_colab,
                file_name="colaboradores.json",
                mime="application/json",
                use_container_width=True
            )
            
            # CSV
            rows = []
            for nome, dados in colaboradores.items():
                rows.append({
                    "Nome": nome,
                    "Email": dados.get("email", ""),
                    "Times": "|".join(dados.get("times", [])),
                    "Perfil": dados.get("perfil_acesso", ""),
                    "Ativo": dados.get("ativo", True),
                    "Admin": dados.get("is_admin", False)
                })
            csv_data = pd.DataFrame(rows).to_csv(index=False)
            st.download_button(
                "📥 Baixar colaboradores.csv",
                data=csv_data,
                file_name="colaboradores.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            st.markdown("#### Permissões")
            json_perm = json.dumps(permissoes, ensure_ascii=False, indent=2)
            st.download_button(
                "📥 Baixar permissoes.json",
                data=json_perm,
                file_name="permissoes.json",
                mime="application/json",
                use_container_width=True
            )
        
        st.markdown("---")
        st.markdown("#### 📊 Resumo")
        
        # Resumo visual
        st.markdown(f"""
        | Métrica | Valor |
        |---------|-------|
        | Total Colaboradores | {len(colaboradores)} |
        | Ativos | {len([c for c in colaboradores.values() if c.get('ativo', True)])} |
        | Super Admins | {len([c for c in colaboradores.values() if c.get('is_admin')])} |
        | Perfis Configurados | {len([p for p in permissoes if not p.startswith('_')])} |
        """)
