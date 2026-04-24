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
    st.markdown("### ℹ️ Sobre o NinaDash")
    st.caption("Dashboard de Inteligência e Qualidade • Versão 8.82 • Arquitetura Modularizada")
    
    # Sobre a NINA
    with st.expander("🤖 NINA Tecnologia", expanded=False):
        st.markdown("""
        <div style="background: linear-gradient(135deg, #AF0C37 0%, #8B0A2C 100%); padding: 24px; border-radius: 12px; margin-bottom: 16px;">
            <h3 style="margin: 0 0 12px 0; color: #ffffff;">🤖 NINA Tecnologia</h3>
            <p style="margin: 0 0 16px 0; color: #fecdd3; font-size: 15px; line-height: 1.6;">
                A <b style="color: #fff;">NINA</b> é uma empresa de tecnologia especializada em <b style="color: #fff;">soluções digitais inovadoras</b>, 
                com foco em desenvolvimento de software de alta qualidade. Nossa missão é transformar ideias em produtos 
                digitais que geram valor real para nossos clientes.
            </p>
            <div style="display: flex; gap: 16px; flex-wrap: wrap;">
                <div style="background: rgba(255,255,255,0.15); padding: 12px 16px; border-radius: 8px; flex: 1; min-width: 200px;">
                    <p style="margin: 0; color: #fecdd3; font-size: 12px;">🎯 MISSÃO</p>
                    <p style="margin: 4px 0 0 0; color: #fff; font-size: 14px; font-weight: 500;">Entregar software de qualidade com excelência operacional</p>
                </div>
                <div style="background: rgba(255,255,255,0.15); padding: 12px 16px; border-radius: 8px; flex: 1; min-width: 200px;">
                    <p style="margin: 0; color: #fecdd3; font-size: 12px;">👁️ VISÃO</p>
                    <p style="margin: 4px 0 0 0; color: #fff; font-size: 14px; font-weight: 500;">Ser referência em qualidade de software no Brasil</p>
                </div>
                <div style="background: rgba(255,255,255,0.15); padding: 12px 16px; border-radius: 8px; flex: 1; min-width: 200px;">
                    <p style="margin: 0; color: #fecdd3; font-size: 12px;">💎 VALORES</p>
                    <p style="margin: 4px 0 0 0; color: #fff; font-size: 14px; font-weight: 500;">Qualidade, Transparência, Inovação</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
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
    
    # Tomada de Decisão
    with st.expander("🧠 Tomada de Decisão por Perfil", expanded=False):
        st.markdown("""
        ### Como cada perfil utiliza o NinaDash
        """)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            #### 👥 QA
            - Priorização de cards por risco
            - Gestão de carga de trabalho
            - Avaliação de janela de release
            - Identificação de aging crítico
            - Funil de validação
            - Comparativo entre QAs
            """)
        
        with col2:
            st.markdown("""
            #### 🧑‍💼 Liderança
            - Decisão **Go/No-Go** de release
            - Health Score da sprint
            - Performance do time
            - Identificação de gargalos
            - Pontos de atenção
            - Análise de tendências
            """)
        
        with col3:
            st.markdown("""
            #### 👨‍💻 Desenvolvedores
            - Feedback de qualidade (Fator K)
            - Selo de maturidade
            - Taxa de retrabalho
            - Tempo de ciclo
            - Cards pendentes
            - WIP e Code Review
            """)
        
        st.markdown("---")
        
        col4, col5 = st.columns(2)
        
        with col4:
            st.markdown("""
            #### 🎯 Suporte/Implantação
            - **"Onde estão meus cards?"**
            - Cards aguardando ação
            - Validação em produção
            - Visão consolidada multi-projeto
            - Link compartilhável
            """)
        
        with col5:
            st.markdown("""
            #### 🏢 Clientes/Comercial
            - Análise por cliente/tema
            - Desenvolvimento pago
            - Bugs por cliente
            - Métricas de entrega
            - Visibilidade de demandas
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
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 20px; color: #64748b;">
        <p style="margin: 0; font-size: 14px;">
            <strong>NinaDash v8.82</strong> — Dashboard de Inteligência e Qualidade
        </p>
        <p style="margin: 8px 0 0 0; font-size: 12px;">
            Desenvolvido com ❤️ pelo Time de Qualidade NINA • Abril 2026
        </p>
    </div>
    """, unsafe_allow_html=True)
