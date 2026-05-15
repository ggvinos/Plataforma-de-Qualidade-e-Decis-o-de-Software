# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the application
streamlit run app.py

# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run a single test file
pytest tests/unit/test_calculos.py -v

# Run only unit tests (fast)
pytest -m unit

# Run with coverage
pytest --cov=modulos --cov-report=term-missing
```

## Architecture

**Entry point:** `app.py` — this is the only file that should be run. `app_modularizado.py` and `app_develop.py` are legacy/dev backups, not production code.

**Startup sequence (order matters):**
1. `configure_page()` — must be called before any Streamlit output
2. `verificar_e_bloquear()` — blocks unauthenticated users immediately
3. Permission loading from `config/colaboradores.json` + `config/permissoes.json`
4. Data fetch from Jira API (cached 5 min via `@st.cache_data(ttl=300)`)
5. Dynamic tab rendering based on user permissions

**Module layout (`modulos/`):**

| Module | Responsibility |
|--------|---------------|
| `config.py` | All constants: `JIRA_BASE_URL`, `CUSTOM_FIELDS`, `STATUS_FLOW`, `STATUS_CORES`, `TOOLTIPS`, `CATALOGO_METRICAS` |
| `jira_api.py` | Jira REST API calls, pagination, card detail fetching, icon/badge rendering |
| `processamento.py` | Raw Jira issues → pandas DataFrame, filter application |
| `calculos.py` | All metric calculations: Fator K, DDP, FPY, Lead Time, Health Score |
| `permissoes_usuario.py` | Email → collaborator lookup → tab permissions; reads `config/colaboradores.json` and `config/permissoes.json` |
| `confirmation_call_auth.py` | JWT authentication via ConfirmationCall API; cookie-based session persistence |
| `abas/` | One file per tab: `qa.py`, `dev.py`, `governanca.py`, `produto.py`, `backlog.py`, `clientes.py`, `suporte.py`, `historico.py`, `lideranca.py`, `admin.py`, `visao_geral.py`, `sobre.py` |
| `cards.py` | Detailed card view with timeline, comments, linked cards |
| `graficos.py` | All Plotly chart builders (funnel, trends, throughput, lead time) |
| `widgets.py` | Reusable UI components (KPI cards, scrollable lists, header) |
| `helpers.py` | Generic metric calculators, CSV/Excel export, HTML card generation |
| `consultas.py` | Saved custom query system (persisted via cookies) |

**Projects supported:** SD (Software Development), QA, PB (Product Backlog), VALPROD — each has different tab sets and status flows defined in `config.py::STATUS_FLOW`.

**Tab access control:** `construir_abas_permitidas()` in `app_modularizado.py` filters tabs based on `st.session_state.user_permissions["abas_permitidas"]`, which comes from the user's `perfil_acesso` in `colaboradores.json` crossed with `permissoes.json`.

**Jira custom fields** are mapped by ID in `config.py::CUSTOM_FIELDS` — any new field must be added there and to the `fields` list in `jira_api.py::buscar_dados_jira_cached`.

## Configuration Files

- `.streamlit/secrets.toml` — Jira credentials (`[jira] email`, `token`) and ConfirmationCall API keys. Never commit.
- `.streamlit/config.toml` — Theme (primary color `#AF0C37`), port 8501
- `config/colaboradores.json` — User registry: name → `{email, perfil_acesso, times, is_admin, ativo}`
- `config/permissoes.json` — Profile → allowed tabs mapping
- `config/acessos.json` — Auto-generated access log (do not edit manually)

## Key Patterns

**Authentication environments:** ConfirmationCall has three environments configured by URL — `api.develop.`, `api.homolog.`, `api.confirmationcall.com.br`. The active one is set in secrets.

**Metric calculations** all take a pandas DataFrame (output of `processar_issues()`) and return scalar values or dicts. The DataFrame columns are defined in `processamento.py::processar_issues()` — check there before accessing any column.

**Jira data cache TTL** is 5 minutes (`REGRAS["cache_ttl_minutos"] = 5`). To force refresh during development: `st.cache_data.clear()`.

**Cards with `v2` or `_backup` suffix** (`cards_v2.py`, `confirmation_call_auth_backup.py`, `visao_geral_v2.py`) are in-progress or superseded versions — the active code imports from the non-suffixed versions unless explicitly noted in `app_modularizado.py`.
