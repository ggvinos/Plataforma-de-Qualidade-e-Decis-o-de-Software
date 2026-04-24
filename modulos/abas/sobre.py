"""
================================================================================
ABA SOBRE - NinaDash v8.82
================================================================================
Página Sobre - Objetivo do Dashboard, Arquitetura e Documentação.

Funcionalidades:
- Sobre a NINA
- Objetivo do dashboard
- Arquitetura modularizada
- Métricas implementadas
- Fórmulas e fundamentos teóricos
- Tomada de decisão por perfil
- Governança técnica
- Abas disponíveis

Author: Time de Qualidade NINA
Version: 8.82 (Abril 2026)
"""

import streamlit as st
from datetime import datetime


def aba_sobre():
    """Aba Sobre - Objetivo do Dashboard e Fontes das Métricas."""
    
    # ===== HERO BANNER NINA (SEMPRE VISÍVEL) =====
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
    
    # ===== FEATURES PRINCIPAIS (SEMPRE VISÍVEIS) =====
    st.markdown("##### ✨ Principais Funcionalidades")
    
    def feature_card(icone, titulo, desc, cor):
        return f'''<div style="background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; height: 140px; display: flex; flex-direction: column;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span style="background: {cor}15; padding: 8px; border-radius: 8px; font-size: 20px;">{icone}</span>
                <span style="font-weight: 600; color: #1f2937; font-size: 14px;">{titulo}</span>
            </div>
            <p style="margin: 0; color: #64748b; font-size: 12px; line-height: 1.5; flex: 1;">{desc}</p>
        </div>'''
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(feature_card("🏥", "Health Score", "Score composto para decisão Go/No-Go de release com base em 5 indicadores", "#22c55e"), unsafe_allow_html=True)
    with col2:
        st.markdown(feature_card("🏆", "Fator K", "Classificação de maturidade dos devs: Gold, Silver, Bronze baseado em SP/Bugs", "#f59e0b"), unsafe_allow_html=True)
    with col3:
        st.markdown(feature_card("⏰", "Janela Release", "Monitoramento de 3 dias úteis para validação segura antes do deploy", "#3b82f6"), unsafe_allow_html=True)
    with col4:
        st.markdown(feature_card("🔗", "Deep Links", "URLs compartilháveis para abas, pessoas e cards específicos", "#8b5cf6"), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
    
    # ===== PERFIS DE USO (SEMPRE VISÍVEIS) =====
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
        st.markdown(perfil_card("🔬", "QA", ["Priorizar cards", "Gestão de carga", "Janela release", "Funil validação"]), unsafe_allow_html=True)
    with col2:
        st.markdown(perfil_card("👨‍💻", "Dev", ["Fator K pessoal", "Selo maturidade", "Tempo de ciclo", "WIP e Review"]), unsafe_allow_html=True)
    with col3:
        st.markdown(perfil_card("🎯", "Tech Lead", ["Visão do time", "Concentração", "Performance", "Distribuição"]), unsafe_allow_html=True)
    with col4:
        st.markdown(perfil_card("👔", "Liderança", ["Go/No-Go", "Health Score", "Tendências", "Riscos"]), unsafe_allow_html=True)
    with col5:
        st.markdown(perfil_card("🏢", "Suporte", ["Meus cards", "Multi-projeto", "Validação prod", "Links rápidos"]), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
    
    # ===== QUICK STATS (MENORES, MAIS ABAIXO) =====
    def stat_card_mini(valor, titulo, icone):
        return f'''<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 10px; text-align: center;">
            <div style="font-size: 18px; margin-bottom: 2px;">{icone}</div>
            <div style="font-size: 20px; font-weight: 700; color: #374151;">{valor}</div>
            <div style="font-size: 10px; color: #64748b; margin-top: 2px;">{titulo}</div>
        </div>'''
    
    st.markdown("###### 📊 Números do Sistema")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(stat_card_mini("16", "Métricas ISTQB", "📊"), unsafe_allow_html=True)
    with col2:
        st.markdown(stat_card_mini("5", "Projetos Jira", "📂"), unsafe_allow_html=True)
    with col3:
        st.markdown(stat_card_mini("11", "Abas", "📑"), unsafe_allow_html=True)
    with col4:
        st.markdown(stat_card_mini("16", "Módulos", "🧩"), unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    
    # ===== DOCUMENTAÇÃO DETALHADA (EXPANDERS) =====
    st.markdown("##### 📚 Documentação Detalhada")
    
    # Sobre a NINA
    with st.expander("Sobre a NINA Tecnologia", expanded=False):
        st.markdown("""
        A **NINA** é uma empresa de tecnologia especializada em **soluções digitais inovadoras**, 
        com foco em desenvolvimento de software de alta qualidade.
        
        | Aspecto | Descrição |
        |---------|-----------|
        | **🎯 Missão** | Entregar software de qualidade com excelência operacional |
        | **👁️ Visão** | Ser referência em qualidade de software no Brasil |
        | **💎 Valores** | Qualidade, Transparência, Inovação |
        """)
    
    # Objetivo do Dashboard
    with st.expander("🎯 Objetivo do Dashboard", expanded=False):
        st.markdown("""
        ### 📊 NinaDash v8.82 — Dashboard de Inteligência e Qualidade
        
        **Propósito central:** Transformar o processo de QA em um **sistema de inteligência operacional baseado em dados**, 
        fornecendo visibilidade completa para toda a organização.
        
        ---
        
        #### 🚨 Problema que resolve
        
        | Antes do NinaDash | Depois do NinaDash |
        |---|---|
        | ❌ Falta de mensuração real do tempo de validação | ✅ Coleta automatizada de métricas |
        | ❌ Zero previsibilidade de entregas | ✅ Cálculo em tempo real de SLAs |
        | ❌ Uso do Notion como controle manual | ✅ Integração direta com Jira |
        | ❌ Falta de segurança na validação de cards | ✅ Monitoramento da janela de release (3 dias úteis) |
        | ❌ Decisões baseadas em "feeling" | ✅ Decisão orientada por dados |
        | ❌ Código monolítico difícil de manter | ✅ Arquitetura modularizada por responsabilidade |
        
        ---
        
        #### ⚡ Diferencial
        
        | Dashboards Comuns | NinaDash |
        |---|---|
        | Métricas genéricas | Métricas baseadas em QA (ISTQB) |
        | Dados estáticos | Integração em tempo real com Jira API |
        | Foco em volume | Foco em **qualidade e maturidade** |
        | Sem contexto de QA | Janela de release com dias úteis |
        | Métricas isoladas | Health Score para decisão Go/No-Go |
        | Sem autenticação | Sistema de login seguro |
        """)
    
    # Projetos Suportados
    with st.expander("📂 Projetos Jira Integrados", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🔹 Projetos Principais
            
            | Projeto | Descrição | Abas Disponíveis |
            |---------|-----------|------------------|
            | **SD** | Service Desk (Suporte) | Todas as 10 abas |
            | **QA** | Quality Assurance | Todas as 10 abas |
            | **DVG** | Desenvolvimento | Todas as 10 abas |
            | **PB** | Product Backlog | 5 abas (foco em Backlog) |
            | **VALPROD** | Validação Produção | Via aba Suporte |
            """)
        
        with col2:
            st.markdown("""
            ### 🔹 Dados Consolidados
            
            A aba **Suporte/Implantação** consolida dados de **todos os projetos** simultaneamente:
            
            - **SD** — Cards de suporte
            - **QA** — Cards de qualidade  
            - **PB** — Product Backlog
            - **VALPROD** — Validação em produção
            
            Permite acompanhar **onde estão seus cards** independente do projeto.
            """)
    
    # Métricas implementadas
    with st.expander("📊 Métricas Implementadas (ISTQB-Aligned)", expanded=False):
        st.markdown("""
        O dashboard implementa métricas fundamentais do **ISTQB Foundation Level**, fornecendo uma visão completa do ciclo de qualidade:
        
        | Métrica | Descrição | Impacto |
        |---------|-----------|---------|
        | **FPY (First Pass Yield)** | Cards aprovados de primeira sem bugs | Mede eficiência do desenvolvimento |
        | **DDP (Defect Detection Percentage)** | Eficácia do QA em encontrar bugs | Indica maturidade do processo de testes |
        | **Fator K** | Relação SP/Bugs (SP/(Bugs+1)) | Classifica maturidade individual |
        | **Lead Time** | Tempo do início ao fim do card | Identifica gargalos no fluxo |
        | **Health Score** | Score composto de saúde da release | Suporta decisão Go/No-Go |
        | **WIP (Work In Progress)** | Cards simultâneos por pessoa | Controla sobrecarga |
        | **Throughput** | Vazão de entrega por sprint | Indica capacidade do time |
        | **Aging** | Tempo em cada etapa do fluxo | Detecta cards parados |
        | **Concentração de Conhecimento** | Distribuição de responsabilidades | Evita dependência de pessoas |
        """)
    
    # Fórmulas
    with st.expander("🧮 Fórmulas Principais", expanded=False):
        st.markdown("""
        ### Fator K (Maturidade do Desenvolvedor)
        ```
        FK = SP / (Bugs + 1)
        ```
        - **🥇 Gold (≥3.0):** Excelente qualidade — Padrão de referência
        - **🥈 Silver (2.0-2.9):** Boa qualidade — Acima da média
        - **🥉 Bronze (1.0-1.9):** Regular — Acompanhar evolução
        - **⚠️ Risco (<1.0):** Crítico — Requer atenção imediata
        
        ---
        
        ### Health Score (Saúde da Release)
        ```
        HS = (Conclusão×30 + DDP×25 + FPY×20 + Gargalos×15 + LeadTime×10) / 100
        ```
        - **🟢 ≥75:** Saudável — Release pode seguir
        - **🟡 50-74:** Atenção — Monitorar riscos
        - **🟠 25-49:** Alerta — Ação necessária
        - **🔴 <25:** Crítico — Avaliar adiamento
        
        ---
        
        ### First Pass Yield (FPY)
        ```
        FPY = (Cards sem bugs / Total de cards) × 100
        ```
        Indica a porcentagem de cards aprovados **de primeira**, sem retrabalho.
        
        ---
        
        ### Defect Detection Percentage (DDP)
        ```
        DDP = (Bugs QA / (Bugs QA + Bugs Prod)) × 100
        ```
        Mede a eficácia do QA em **detectar bugs antes da produção**.
        
        ---
        
        ### Janela de Release
        ```
        ≥ 3 dias úteis antes da release = Dentro da janela ✅
        < 3 dias úteis = Fora da janela ⚠️
        ```
        Garante tempo mínimo para validação segura.
        """)
    
    # Fundamentos Teóricos
    with st.expander("📚 Fundamentos Teóricos", expanded=False):
        st.markdown("""
        ### 🎓 ISTQB/CTFL - International Software Testing Qualifications Board
        
        O **ISTQB Foundation Level (CTFL)** define padrões globais para métricas de teste:
        
        **Métricas de Processo** (implementadas no dashboard):
        - *Defect Detection Percentage (DDP)*: Eficácia do QA
        - *First Pass Yield (FPY)*: Qualidade na primeira entrega
        - *Rework Effort Ratio*: Esforço gasto em correções
        
        **Métricas de Produto**:
        - *Defect Density*: Bugs por unidade de tamanho (SP)
        - *Test Coverage*: Cobertura de testes automatizados
        
        > *"We cannot improve what we cannot measure"* - ISTQB Syllabus
        
        ---
        
        ### 🔄 TDD - Test-Driven Development (Kent Beck)
        
        O **TDD** segue o ciclo **Red-Green-Refactor**:
        1. 🔴 **Red**: Escrever um teste que falha
        2. 🟢 **Green**: Escrever código mínimo para passar
        3. 🔵 **Refactor**: Melhorar o código mantendo testes passando
        
        **Como o Fator K se relaciona com TDD**:
        - Devs que praticam TDD tendem a ter **FK mais alto**
        - Menos bugs = maior proporção SP/Bugs
        - Selo Gold incentiva a prática
        
        ---
        
        ### 📈 Shift-Left Testing
        
        O conceito move as atividades de teste para o início do ciclo:
        
        ```
        Tradicional:  Requisitos → Desenvolvimento → [TESTES] → Deploy
        Shift-Left:   [TESTES] → Requisitos → [TESTES] → Dev → [TESTES] → Deploy
        ```
        
        **ROI comprovado pela indústria**:
        | Fase de Detecção | Custo de Correção |
        |------------------|-------------------|
        | Desenvolvimento | ~$100 |
        | QA/Testes | ~$1.500 |
        | Produção | ~$10.000+ |
        
        > O NinaDash ajuda a NINA a encontrar bugs mais cedo, **economizando recursos**.
        """)
    
    # Governança
    with st.expander("🏛️ Governança Técnica", expanded=False):
        current_year = datetime.now().year
        current_month = datetime.now().strftime("%B %Y")
        
        st.markdown(f"""
        ### Informações do Sistema
        
        | Informação | Valor |
        |------------|-------|
        | **Nome** | NinaDash |
        | **Versão** | 8.82 |
        | **Desenvolvido por** | Time de Qualidade NINA |
        | **Mantido por** | Vinícios Ferreira |
        | **Última atualização** | Abril 2026 |
        | **Arquitetura** | Modularizada (16 módulos) |
        
        ---
        
        ### Stack Tecnológica
        
        | Componente | Tecnologia | Versão |
        |------------|------------|--------|
        | **Linguagem** | Python | 3.13+ |
        | **Framework Web** | Streamlit | Latest |
        | **Visualização** | Plotly Express | Latest |
        | **Dados** | Pandas | Latest |
        | **Autenticação** | Cookies seguros | - |
        | **API** | Jira REST API | v3 |
        | **Deploy** | Local/Server | - |
        
        ---
        
        ### Módulos do Sistema
        
        | Categoria | Módulos | Responsabilidade |
        |-----------|---------|------------------|
        | **Core** | config, auth, jira_api | Configuração e integração |
        | **Processamento** | calculos, processamento, helpers | Lógica de negócio |
        | **Visualização** | graficos, widgets, cards | Interface |
        | **Abas** | 11 módulos em `abas/` | Páginas do dashboard |
        """)
    
    # Abas Disponíveis
    with st.expander("📑 Guia de Abas", expanded=False):
        st.markdown("""
        ### Visão Geral das Abas
        
        | Aba | Ícone | Descrição | Público-Alvo |
        |-----|-------|-----------|---------------|
        | **Visão Geral** | 📊 | KPIs principais, Health Score, alertas, progresso da release | Todos |
        | **QA** | 🔬 | Funil de validação, carga por QA, aging, bugs, comparativo | QA, Liderança |
        | **Dev** | 👨‍💻 | Ranking Fator K, performance, WIP, Code Review, Tech Lead | Devs, Tech Lead |
        | **Suporte/Implantação** | 🎯 | "Onde estão meus cards?", validação produção, multi-projeto | Suporte |
        | **Clientes** | 🏢 | Análise por cliente/tema, dev pago, bugs | Comercial |
        | **Governança** | 📋 | Qualidade dos dados, campos obrigatórios, compliance | PO, Liderança |
        | **Produto** | 📦 | Métricas por produto, Health Score, tendências | PO, Stakeholders |
        | **Backlog** | 📋 | Saúde do backlog, aging, gargalos, recomendações | PO, Liderança |
        | **Histórico** | 📈 | Evolução de métricas, tendências entre releases | Liderança |
        | **Liderança** | 🎯 | Go/No-Go, riscos, simulações, pontos de atenção | Gerentes, Diretores |
        | **Sobre** | ℹ️ | Esta documentação | Todos |
        
        ---
        
        ### 🔗 Links Compartilháveis
        
        O NinaDash suporta **deep linking** para compartilhar visões específicas:
        
        ```
        ?aba=suporte&pessoa=Nome%20Pessoa   → Abre aba Suporte filtrado
        ?aba=qa&qa=Nome%20QA                → Abre aba QA filtrado
        ?aba=dev&dev=Nome%20Dev             → Abre aba Dev filtrado
        ?card=SD-1234&projeto=SD            → Abre card específico
        ```
        
        Use o botão **📋 Copiar Link** presente em cada aba para gerar o link automaticamente.
        """)
    
    # ===== FOOTER RICO =====
    st.markdown("---")
    
    # Footer com cards informativos
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
    
    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; padding: 16px; color: #94a3b8; font-size: 12px;">
        Feito com ❤️ em Python + Streamlit • Métricas baseadas em ISTQB Foundation Level
    </div>
    """, unsafe_allow_html=True)
