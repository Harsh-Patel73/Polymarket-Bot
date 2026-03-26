# Polygon chain
POLYGON_CHAIN_ID = 137
POLYGON_MUMBAI_CHAIN_ID = 80001

# USDC.e on Polygon
USDC_E_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
USDC_E_DECIMALS = 6

# Polymarket contracts
CTF_EXCHANGE_ADDRESS = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"
NEG_RISK_CTF_EXCHANGE_ADDRESS = "0xC5d563A36AE78145C45a50134d48A1215220f80a"
NEG_RISK_ADAPTER_ADDRESS = "0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296"
CONDITIONAL_TOKENS_ADDRESS = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"

# Polymarket API
POLYMARKET_CLOB_URL = "https://clob.polymarket.com"
POLYMARKET_WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
POLYMARKET_GAMMA_URL = "https://gamma-api.polymarket.com"

# Trading
SIDE_BUY = "BUY"
SIDE_SELL = "SELL"
ORDER_TYPE_GTC = "GTC"
ORDER_TYPE_FOK = "FOK"

# Position statuses
STATUS_OPEN = "OPEN"
STATUS_CLOSED = "CLOSED"
STATUS_PENDING = "PENDING"
STATUS_CANCELLED = "CANCELLED"

# Order statuses
ORDER_LIVE = "LIVE"
ORDER_FILLED = "FILLED"
ORDER_PARTIAL = "PARTIAL"
ORDER_CANCELLED = "CANCELLED"
ORDER_EXPIRED = "EXPIRED"

# ERC20 ABI (minimal for balance + approve)
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [
            {"name": "_owner", "type": "address"},
            {"name": "_spender", "type": "address"},
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
]
