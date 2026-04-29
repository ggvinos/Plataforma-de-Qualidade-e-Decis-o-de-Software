"""
================================================================================
ABA SOBRE - NinaDash v8.82
================================================================================
Página Sobre - Objetivo do Dashboard e Funcionalidades Principais.

Author: Time de Qualidade NINA
Version: 8.82 (Abril 2026)
"""

import streamlit as st
from datetime import datetime


def aba_sobre():
    """Aba Sobre - Objetivo do Dashboard e Funcionalidades."""
    
    # ===== HERO BANNER NINA =====
    st.markdown("""
    <div style="background: linear-gradient(135deg, #AF0C37 0%, #8B0A2C 100%); padding: 28px 32px; border-radius: 16px; margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 20px;">
            <div>
                <h2 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700;">NINA Tecnologia</h2>
                <p style="margin: 4px 0 0 0; color: #fecdd3; font-size: 14px;">NinaDash • Dashboard de Inteligência e Qualidade • v8.82</p>
            </div>
            <span style="margin-left: auto; background: rgba(255,255,255,0.2); padding: 6px 14px; border-radius: 20px; color: #fff; font-size: 12px; font-weight: 600;">
                Abril 2026
            </span>
        </div>
        <div style="display: flex; gap: 12px; flex-wrap: wrap;">
            <div style="background: rgba(255,255,255,0.15); padding: 10px 14px; border-radius: 8px; flex: 1; min-width: 180px;">
                <p style="margin: 0; color: #fecdd3; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px;">🎯 Missão</p>
                <p style="margin: 4px 0 0 0; color: #fff; font-size: 13px; font-weight: 500;">Entregar software de qualidade com excelência operacional</p>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 10px 14px; border-radius: 8px; flex: 1; min-width: 180px;">
                <p style="margin: 0; color: #fecdd3; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px;">👁️ Visão</p>
                <p style="margin: 4px 0 0 0; color: #fff; font-size: 13px; font-weight: 500;">Ser referência em qualidade de software no Brasil</p>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 10px 14px; border-radius: 8px; flex: 1; min-width: 180px;">
                <p style="margin: 0; color: #fecdd3; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px;">💎 Valores</p>
                <p style="margin: 4px 0 0 0; color: #fff; font-size: 13px; font-weight: 500;">Qualidade, Transparência, Inovação</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== POR QUE O NINADASH EXISTE =====
    st.markdown("##### 🎯 Por Que o NinaDash Existe?")
    
    st.markdown("""
    <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
        <p style="margin: 0 0 12px 0; font-size: 15px; color: #166534; font-weight: 600;">
            O NinaDash nasceu para resolver um problema real: <strong>falta de visibilidade sobre o que está acontecendo com nossos cards.</strong>
        </p>
        <p style="margin: 0; font-size: 14px; color: #374151; line-height: 1.6;">
            Antes, cada pessoa tinha que abrir o Jira, filtrar manualmente, e ainda assim não conseguia responder perguntas simples como 
            "onde estão meus cards?", "quanto tempo esse card ficou parado?", ou "quem está sobrecarregado?".
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 16px; border-radius: 0 8px 8px 0;">
            <p style="margin: 0 0 8px 0; font-weight: 600; color: #dc2626;">❌ Antes do NinaDash</p>
            <ul style="margin: 0; padding-left: 20px; color: #7f1d1d; font-size: 13px; line-height: 1.8;">
                <li>Cada um olhava só o próprio Jira</li>
                <li>Sem visão do tempo em cada status</li>
                <li>Não sabia onde os cards estavam parados</li>
                <li>Decisões baseadas em "achismo"</li>
                <li>Sem métricas individuais de performance</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #f0fdf4; border-left: 4px solid #22c55e; padding: 16px; border-radius: 0 8px 8px 0;">
            <p style="margin: 0 0 8px 0; font-weight: 600; color: #16a34a;">✅ Com o NinaDash</p>
            <ul style="margin: 0; padding-left: 20px; color: #166534; font-size: 13px; line-height: 1.8;">
                <li>Visão consolidada de todos os projetos</li>
                <li>Histórico visual de cada card</li>
                <li>Métricas em tempo real</li>
                <li>Decisões baseadas em dados</li>
                <li>Performance individual de QA e Dev</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    
    # ===== FUNCIONALIDADES PRINCIPAIS =====
    st.markdown("##### ✨ Funcionalidades Principais")
    
    # PESQUISA RÁPIDA DE CARD
    st.markdown("""
    <div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border: 2px solid #3b82f6; border-radius: 16px; padding: 24px; margin-bottom: 16px;">
        <div style="display: flex; align-items: flex-start; gap: 16px;">
            <div style="background: #3b82f6; color: white; padding: 16px; border-radius: 12px; font-size: 32px;">🔍</div>
            <div style="flex: 1;">
                <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 18px;">Pesquisa Rápida de Card</h4>
                <p style="margin: 0 0 12px 0; color: #374151; font-size: 14px; line-height: 1.6;">
                    Digite o código de qualquer card (ex: SD-1234) e veja instantaneamente tudo sobre ele:
                </p>
                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                    <span style="background: white; border: 1px solid #93c5fd; padding: 6px 12px; border-radius: 20px; font-size: 12px; color: #1e40af;">📊 Métricas do Card</span>
                    <span style="background: white; border: 1px solid #93c5fd; padding: 6px 12px; border-radius: 20px; font-size: 12px; color: #1e40af;">📜 Timeline Visual</span>
                    <span style="background: white; border: 1px solid #93c5fd; padding: 6px 12px; border-radius: 20px; font-size: 12px; color: #1e40af;">⏱️ Tempo em Cada Status</span>
                    <span style="background: white; border: 1px solid #93c5fd; padding: 6px 12px; border-radius: 20px; font-size: 12px; color: #1e40af;">🔗 Vínculos com Outros Cards</span>
                    <span style="background: white; border: 1px solid #93c5fd; padding: 6px 12px; border-radius: 20px; font-size: 12px; color: #1e40af;">💬 Comentários</span>
                    <span style="background: white; border: 1px solid #93c5fd; padding: 6px 12px; border-radius: 20px; font-size: 12px; color: #1e40af;">📋 Link Compartilhável</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # VISÃO INDIVIDUAL
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%); border: 2px solid #8b5cf6; border-radius: 16px; padding: 20px; height: 100%;">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                <div style="background: #8b5cf6; color: white; padding: 12px; border-radius: 10px; font-size: 24px;">👨‍💻</div>
                <h4 style="margin: 0; color: #6d28d9; font-size: 16px;">Visão Individual do Dev</h4>
            </div>
            <p style="margin: 0 0 12px 0; color: #374151; font-size: 13px; line-height: 1.5;">
                Cada desenvolvedor pode ver suas próprias métricas:
            </p>
            <ul style="margin: 0; padding-left: 18px; color: #5b21b6; font-size: 12px; line-height: 1.8;">
                <li><strong>Fator K</strong> - Qualidade das entregas</li>
                <li><strong>Selo de Maturidade</strong> - Gold, Silver, Bronze</li>
                <li><strong>Cards em andamento</strong> - WIP atual</li>
                <li><strong>Tempo médio de ciclo</strong></li>
                <li><strong>Histórico de entregas</strong></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border: 2px solid #22c55e; border-radius: 16px; padding: 20px; height: 100%;">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                <div style="background: #22c55e; color: white; padding: 12px; border-radius: 10px; font-size: 24px;">🔬</div>
                <h4 style="margin: 0; color: #166534; font-size: 16px;">Visão Individual do QA</h4>
            </div>
            <p style="margin: 0 0 12px 0; color: #374151; font-size: 13px; line-height: 1.5;">
                Cada QA pode acompanhar seu trabalho:
            </p>
            <ul style="margin: 0; padding-left: 18px; color: #166534; font-size: 12px; line-height: 1.8;">
                <li><strong>Cards na fila</strong> - O que precisa validar</li>
                <li><strong>Carga de trabalho</strong> - SP em validação</li>
                <li><strong>Bugs encontrados</strong> - Eficácia do QA</li>
                <li><strong>Tempo médio de validação</strong></li>
                <li><strong>Janela de release</strong> - Cards dentro/fora</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    
    # OUTRAS FUNCIONALIDADES
    st.markdown("###### Outras Funcionalidades")
    
    def feature_mini(icone, titulo, desc, cor):
        return f'''<div style="background: white; border: 1px solid #e5e7eb; border-radius: 10px; padding: 14px;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                <span style="background: {cor}15; padding: 6px; border-radius: 6px; font-size: 18px;">{icone}</span>
                <span style="font-weight: 600; color: #1f2937; font-size: 13px;">{titulo}</span>
            </div>
            <p style="margin: 0; color: #64748b; font-size: 11px; line-height: 1.4;">{desc}</p>
        </div>'''
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(feature_mini("🎯", "Suporte/Implantação", "Veja onde estão seus cards em todos os projetos", "#ef4444"), unsafe_allow_html=True)
    with col2:
        st.markdown(feature_mini("🏥", "Health Score", "Score para decisão Go/No-Go de release", "#22c55e"), unsafe_allow_html=True)
    with col3:
        st.markdown(feature_mini("⏰", "Janela Release", "Monitora 3 dias úteis para validação segura", "#3b82f6"), unsafe_allow_html=True)
    with col4:
        st.markdown(feature_mini("🔗", "Links Compartilháveis", "Compartilhe visões específicas com a equipe", "#8b5cf6"), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    
    # ===== QUEM USA =====
    st.markdown("##### 👥 Quem Usa o NinaDash")
    
    def perfil_card(icone, nome, acoes):
        acoes_html = "".join([f'<div style="font-size: 11px; color: #64748b; padding: 2px 0;">• {a}</div>' for a in acoes])
        return f'''<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                <span style="font-size: 24px;">{icone}</span>
                <span style="font-weight: 600; color: #1f2937; font-size: 13px;">{nome}</span>
            </div>
            {acoes_html}
        </div>'''
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(perfil_card("🔬", "QA", ["Priorizar validações", "Ver carga de trabalho", "Janela de release", "Bugs encontrados"]), unsafe_allow_html=True)
    with col2:
        st.markdown(perfil_card("👨‍💻", "Dev", ["Ver Fator K pessoal", "Cards em andamento", "Histórico de entregas", "Selo de maturidade"]), unsafe_allow_html=True)
    with col3:
        st.markdown(perfil_card("🎯", "Suporte", ["Onde estão meus cards?", "Multi-projeto (SD, QA, PB)", "Status de validação", "Links rápidos"]), unsafe_allow_html=True)
    with col4:
        st.markdown(perfil_card("👔", "Liderança", ["Go/No-Go release", "Health Score", "Visão do time", "Alertas de risco"]), unsafe_allow_html=True)
    with col5:
        st.markdown(perfil_card("📦", "Produto", ["Funil do backlog", "Demandas por etapa", "Idade das demandas", "Priorização"]), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    
    # ===== DOCUMENTAÇÃO TÉCNICA (EXPANDIDA) =====
    st.markdown("##### 📚 Documentação Técnica")
    
    with st.expander("📊 Métricas e Fórmulas", expanded=False):
        st.markdown("""
        ### Fator K (Maturidade do Desenvolvedor)
        ```
        FK = SP / (Bugs + 1)
        ```
        
        | Selo | Fator K | Classificação |
        |------|---------|---------------|
        | 🥇 Gold | ≥ 3.0 | Excelente - Referência para o time |
        | 🥈 Silver | 2.0 - 2.9 | Bom - Acima da média |
        | 🥉 Bronze | 1.0 - 1.9 | Regular - Acompanhar evolução |
        | ⚠️ Risco | < 1.0 | Crítico - Requer atenção |
        
        ---
        
        ### Health Score (Saúde da Release)
        Score composto que considera: Conclusão, DDP, FPY, Gargalos e Lead Time.
        
        | Score | Status | Ação |
        |-------|--------|------|
        | 🟢 ≥75 | Saudável | Release pode seguir |
        | 🟡 50-74 | Atenção | Monitorar riscos |
        | 🟠 25-49 | Alerta | Ação necessária |
        | 🔴 <25 | Crítico | Avaliar adiamento |
        
        ---
        
        ### Janela de Release
        Para validação segura, o card deve entrar em validação com **≥ 3 dias úteis** antes da release.
        """)
    
    with st.expander("📑 Guia de Abas", expanded=False):
        st.markdown("""
        | Aba | Para Quem | O Que Mostra |
        |-----|-----------|--------------|
        | **Visão Geral** | Todos | KPIs principais, progresso da sprint, alertas |
        | **QA** | QA, Liderança | Fila de validação, carga por QA, aging, bugs |
        | **Dev** | Devs, Tech Lead | Ranking Fator K, performance individual, WIP |
        | **Suporte/Implantação** | Suporte | "Onde estão meus cards?" em todos os projetos |
        | **Clientes** | Comercial | Análise por cliente/tema |
        | **Governança** | PO, Liderança | Qualidade dos dados, compliance |
        | **Produto** | PO, Stakeholders | Métricas por produto |
        | **Backlog (PB)** | PO, Liderança | Saúde do backlog, funil de produto |
        | **Histórico** | Liderança | Evolução entre releases |
        | **Liderança** | Gerentes | Go/No-Go, riscos, simulações |
        """)
    
    with st.expander("🔗 Links Compartilháveis", expanded=False):
        st.markdown("""
        O NinaDash suporta **deep linking** para compartilhar visões específicas:
        
        | Tipo | Formato | Exemplo |
        |------|---------|---------|
        | Card específico | `?card=XX-1234&projeto=XX` | `?card=SD-1234&projeto=SD` |
        | Aba com pessoa | `?aba=suporte&pessoa=Nome` | `?aba=suporte&pessoa=João%20Silva` |
        | QA específico | `?aba=qa&qa=Nome` | `?aba=qa&qa=Maria%20QA` |
        | Dev específico | `?aba=dev&dev=Nome` | `?aba=dev&dev=Pedro%20Dev` |
        
        Use o botão **📋 Copiar Link** presente em cada aba para gerar o link automaticamente.
        """)
        with st.expander("📚 Base Teórica (ISTQB)", expanded=False):
            st.markdown("""
            As métricas do NinaDash são baseadas no **ISTQB** (International Software Testing Qualifications Board), 
        um padrão internacional de qualidade de software.
        
        **Por que isso importa?**
        - Métricas reconhecidas mundialmente
        - Permite comparação com outras empresas
        - Fundamentação técnica sólida
        
        **Principais conceitos usados:**
        
        | Conceito | O que significa | Como usamos |
        |----------|-----------------|-------------|
        | **FPY** | Cards aprovados de primeira | Mede qualidade das entregas |
        | **DDP** | Bugs encontrados antes de prod | Mede eficácia do QA |
        | **Shift-Left** | Testar mais cedo | Encontrar bugs antes = mais barato |
        """)
    
    with st.expander("🛠️ Tecnologias Utilizadas", expanded=False):
        st.markdown("""
        | O que | Tecnologia |
        |-------|------------|
        | **Linguagem** | Python 3.13 |
        | **Interface** | Streamlit |
        | **Gráficos** | Plotly |
        | **Dados** | Pandas |
        | **Integração** | Jira REST API |
        """)
        # ===== FOOTER =====
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    def footer_card(icone, titulo, valor, subtitulo):
        return f'''<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px; text-align: center;">
            <div style="font-size: 20px; margin-bottom: 6px;">{icone}</div>
            <div style="font-size: 10px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">{titulo}</div>
            <div style="font-size: 16px; font-weight: 600; color: #1f2937; margin: 4px 0;">{valor}</div>
            <div style="font-size: 11px; color: #64748b;">{subtitulo}</div>
        </div>'''
    
    with col1:
        st.markdown(footer_card("🛠️", "Versão", "8.82", "Abril 2026"), unsafe_allow_html=True)
    with col2:
        st.markdown(footer_card("👨‍💻", "Mantido por", "Vinícios Ferreira", "Time de Qualidade"), unsafe_allow_html=True)
    with col3:
        st.markdown(footer_card("🏢", "Desenvolvido para", "NINA Tecnologia", "Confirmation Call"), unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; padding: 16px; color: #94a3b8; font-size: 12px; margin-top: 16px;">
        Feito com ❤️ em Python + Streamlit
    </div>
    """, unsafe_allow_html=True)
