# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mesa Quant is a personal quantitative trading platform (written in Portuguese) targeting American markets — stocks, options, futures, and crypto. The project is in early-stage development (Phase 1 — Infrastructure).

**Developer context:** Beginner in quantitative trading, intermediate Python developer. Prefers didactic code over premature optimization. Should be warned explicitly when implementations carry financial risk.

## Commands

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy and edit config before running anything
cp configs/config.example.yaml configs/config.yaml

# Tests
pytest tests/ -v

# Run a single test file
pytest tests/path/to/test_file.py -v
```

## Architecture

Data flows top-to-bottom through three layers:

**Collection → Persistence → Analysis/Execution**

- **`src/collectors/`** — Data ingestion. `ib_connector.py` wraps `ib_insync` for Interactive Brokers (stocks, futures, historical bars). Crypto via `ccxt` is planned but not yet implemented.
- **`src/utils/database.py`** — `DatabaseManager` handles TimescaleDB/PostgreSQL via SQLAlchemy. OHLCV data is stored in hypertables for time-series efficiency.
- **`src/risk/risk_manager.py`** — Portfolio-level guardrails: max position size (5%), max daily loss (2%), max drawdown (10%). Also computes Kelly-based position sizing.
- **`src/backtest/`** and **`src/execution/`** — Currently empty placeholders; VectorBT is the intended backtesting library; `ib_insync` for order execution.
- **`tools/`** — Auxiliary Streamlit tools for research (seasonality analysis, etc.)

Jupyter notebooks in `notebooks/` are for research and strategy development. Logs go to `logs/mesa_quant.log`.

## Configuration

All runtime config lives in `configs/config.yaml` (gitignored). Copy from `configs/config.example.yaml`.

Key sections:
- `interactive_brokers`: TWS/Gateway connection (paper port 7497/4002, live 7496/4001)
- `database`: PostgreSQL/TimescaleDB credentials
- `crypto`: Binance API keys
- `risk`: Position and drawdown limits
- `logging`: Log level and file path

## Infrastructure Dependencies

The platform requires external services to function:
- **TimescaleDB** (PostgreSQL extension) — see `docs/setup_server.md` for server setup
- **IB TWS or IB Gateway** — must be running and API connections enabled before `IBConnector` will work; on headless servers, use Xvfb

## Risk Rules (non-negotiable)

These limits are hardcoded in `src/risk/risk_manager.py` and must NOT be relaxed without explicit review:
- Max position size: **5%** of portfolio per trade
- Max daily loss: **2%** of portfolio (daily stop)
- Max drawdown: **10%** (global stop)
- Every new strategy must pass paper trading before going live

## Git Workflow

- `main` branch for production-ready code
- `develop` branch for integration
- Feature branches from `develop`
- Commit format: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`

## Current Roadmap

- [x] Initial project structure
- [ ] **Phase 1** — Ubuntu Server + TimescaleDB setup
- [ ] **Phase 2** — Historical data ingestion (IB + CCXT)
- [ ] **Phase 3** — First backtests with VectorBT
- [ ] **Phase 4** — Paper Trading
- [ ] **Phase 5** — Live Trading with small capital

## Language Note

Code comments, docstrings, variable names, and documentation are written in Portuguese. User-facing messages and interactions with the developer are in Portuguese (BR). Follow this convention when adding new code.