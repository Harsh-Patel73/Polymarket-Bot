# PolyMarketBot

Automated Polymarket trading bot powered by Claude AI.

## Setup

1. Copy `.env.template` to `.env` and fill in your keys
2. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Run the bot:
   ```bash
   python -m src.main
   ```

## Architecture

| Layer | Modules | Purpose |
|-------|---------|---------|
| Data | `src/data/` | Polymarket CLOB API, Polygon RPC, WebSocket feeds |
| AI | `src/ai/` | Claude probability estimation, prompt management |
| Math | `src/math_engine/` | EV, Kelly Criterion, Bayesian updating, log returns |
| Execution | `src/execution/` | GTC orders, slippage protection, position tracking |
| Monitoring | `src/monitoring/` | Telegram alerts, logging, error recovery |
| Orchestration | `src/bot/` | Scanner, analyzer, pipeline loop |

Polymarket Trading Bot - Implementation Plan
Context
Build a full Polymarket automated trading bot based on the tooling stack from @LunarResearcher's article. The project directory is currently empty. The bot scans 50+ markets, estimates probabilities with Claude AI, calculates position sizes via Kelly Criterion, executes trades on Polygon, and monitors everything via Telegram.

Project Structure
PolyMarketBot/
├── pyproject.toml
├── requirements.txt
├── .env.template
├── .gitignore
├── README.md
│
├── src/
│   ├── __init__.py
│   ├── main.py                    # Entry point: asyncio.run(main())
│   ├── config.py                  # Pydantic Settings config from .env
│   ├── constants.py               # Chain IDs, contract addresses, USDC.e address
│   │
│   ├── data/                      # Layer 1: Data & Market Access
│   │   ├── __init__.py
│   │   ├── clob_client.py         # Async wrapper around py-clob-client
│   │   ├── websocket_client.py    # Real-time price feeds via WebSocket
│   │   ├── blockchain.py          # web3.py: balances, approvals, contract calls
│   │   └── market_types.py        # Dataclasses for market data
│   │
│   ├── ai/                        # Layer 2: AI Brain
│   │   ├── __init__.py
│   │   ├── claude_client.py       # AsyncAnthropic client, structured JSON output
│   │   ├── prompt_manager.py      # Load/render prompts from /prompts folder
│   │   └── analysis_types.py      # MarketAnalysis dataclass
│   │
│   ├── math_engine/               # Layer 3: Math Engine
│   │   ├── __init__.py
│   │   ├── expected_value.py      # EV = P(win)*Profit - P(lose)*Loss, 5% edge threshold
│   │   ├── kelly.py               # Kelly Criterion, quarter-Kelly (0.25x)
│   │   ├── bayesian.py            # Bayesian updating for mid-trade probability revision
│   │   └── returns.py             # Log returns for P&L
│   │
│   ├── execution/                 # Layer 4: Execution
│   │   ├── __init__.py
│   │   ├── order_manager.py       # GTC order creation, placement, cancellation
│   │   ├── slippage.py            # Orderbook depth analysis, max 2% slippage
│   │   ├── position_tracker.py    # SQLite CRUD for positions
│   │   └── balance_checker.py     # Pre-trade balance verification via RPC
│   │
│   ├── monitoring/                # Layer 5: Monitoring & Alerts
│   │   ├── __init__.py
│   │   ├── telegram_bot.py        # aiogram Bot + Dispatcher setup
│   │   ├── telegram_handlers.py   # /status, /positions, /pnl, /close commands
│   │   ├── notifier.py            # Proactive alerts (edge found, fill, error)
│   │   └── logger.py              # Rotating file handler setup
│   │
│   ├── db/                        # Database layer
│   │   ├── __init__.py
│   │   ├── database.py            # aiosqlite connection manager
│   │   ├── models.py              # Table creation DDL
│   │   └── queries.py             # Named query functions
│   │
│   └── bot/                       # Core orchestration
│       ├── __init__.py
│       ├── scanner.py             # Market scanning & filtering
│       ├── analyzer.py            # Scan → AI analysis → math → decision
│       └── pipeline.py            # Full pipeline loop
│
├── prompts/                       # Prompt versioning
│   ├── active.json                # Points to active version
│   └── v1/
│       ├── market_analysis.json   # System + user prompt template
│       └── metadata.json          # Version info, changelog
│
├── data/                          # Runtime data (gitignored)
├── logs/                          # Log files (gitignored)
│
├── scripts/
│   └── setup_approvals.py         # One-time USDC.e token approval
│
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── test_math_engine/
        ├── test_expected_value.py
        ├── test_kelly.py
        └── test_bayesian.py
Dependencies (pyproject.toml)
Package	Purpose	Layer
py-clob-client>=0.15.0	Polymarket CLOB SDK	Data
web3>=7.0.0	Polygon blockchain interactions	Data
websockets>=13.0	Real-time price feeds	Data
python-dotenv>=1.0.0	Secrets from .env	Data
anthropic>=0.40.0	Claude API (AsyncAnthropic)	AI
httpx>=0.27.0	Async HTTP client	AI
numpy>=1.26.0	Math operations	Math
aiosqlite>=0.20.0	Async SQLite	Execution
aiogram>=3.13.0	Telegram bot framework	Monitoring
pydantic>=2.9.0	Config validation	Infra
pydantic-settings>=2.6.0	.env → typed config	Infra
Dev dependencies: pytest, pytest-asyncio, pytest-cov, ruff, mypy

Key Design Decisions
Async-first: Entire bot uses asyncio. The sync py-clob-client is wrapped via run_in_executor() with a bounded thread pool.
GTC orders over FOK — higher fill rate on thin orderbooks.
Quarter Kelly (0.25x) for conservative position sizing.
5% minimum EV edge to filter out marginal trades.
Max 2% slippage protection — skip if orderbook too thin.
Pydantic Settings loads and validates all config from .env at startup.
SQLite with WAL mode for position tracking (via aiosqlite).
Prompt versioning in /prompts folder with active.json pointer.
Main Bot Loop (4 concurrent async tasks)
Scanner Pipeline (every 5 min): fetch markets → filter → Claude analysis → EV/Kelly math → execute if edge → notify
WebSocket Monitor (continuous): real-time price feeds for open positions → Bayesian updates → exit checks
Telegram Bot (continuous): listens for /status, /positions, /pnl, /close commands
Position Monitor (every 1 min): check open positions → calculate P&L → stop-loss/take-profit checks
SQLite Schema (4 tables)
positions: market_id, token_id, question, side, entry_price, current_price, size, shares, order_id, status, ai_probability, ai_confidence, ai_reasoning, pnl_usd, pnl_pct, timestamps
orders: order_id, position_id, market_id, side, order_type (GTC), price, size, filled_size, status, timestamps
scans: markets_scanned, edges_found, orders_placed, errors, duration_ms, timestamp
ai_analyses: market_id, question, market_price, prompt_version, ai_probability, ai_confidence, ai_reasoning, model, token counts, latency, timestamp
.env Template
Secrets for: Polymarket CLOB (host, private key, API creds), Alchemy RPC URL, Anthropic API key, Telegram bot token + chat ID, trading parameters (scan interval, min edge, max slippage, kelly fraction, max position size).

Build Order
Scaffolding: pyproject.toml, .env.template, .gitignore, config.py, constants.py, logger.py
Database: db/models.py, db/database.py, db/queries.py
Data layer: clob_client.py (async wrapper), blockchain.py, market_types.py, websocket_client.py
AI layer: prompts/v1/*, prompt_manager.py, claude_client.py, analysis_types.py
Math engine: expected_value.py, kelly.py, bayesian.py, returns.py
Execution: slippage.py, balance_checker.py, order_manager.py, position_tracker.py
Monitoring: notifier.py, telegram_bot.py, telegram_handlers.py
Orchestration: scanner.py, analyzer.py, pipeline.py, main.py
Scripts & tests: setup_approvals.py, math engine tests
Verification
pip install -e ".[dev]" — all dependencies install cleanly
python -c "from src.config import BotConfig" — config loads without .env (shows validation errors)
pytest tests/test_math_engine/ — math functions produce correct outputs
With a valid .env: python -m src.main starts the bot, connects to Polymarket API, and begins scanning