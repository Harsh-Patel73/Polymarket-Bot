import logging

from web3 import AsyncWeb3
from web3.providers import WebSocketProvider

from src.config import BotConfig
from src.constants import CTF_EXCHANGE_ADDRESS, ERC20_ABI, USDC_E_ADDRESS, USDC_E_DECIMALS

logger = logging.getLogger("polybot.blockchain")


class BlockchainClient:
    """web3.py async client for Polygon balance checks and token approvals."""

    def __init__(self, config: BotConfig):
        self._w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(config.alchemy_rpc_url))
        self._account = self._w3.eth.account.from_key(config.private_key)
        self._address = self._account.address
        self._usdc_contract = self._w3.eth.contract(
            address=AsyncWeb3.to_checksum_address(USDC_E_ADDRESS),
            abi=ERC20_ABI,
        )

    @property
    def address(self) -> str:
        return self._address

    async def get_usdc_balance(self) -> float:
        """Get USDC.e balance in human-readable units."""
        raw = await self._usdc_contract.functions.balanceOf(self._address).call()
        balance = raw / (10**USDC_E_DECIMALS)
        logger.debug(f"USDC.e balance: {balance:.2f}")
        return balance

    async def get_matic_balance(self) -> float:
        """Get MATIC/POL balance for gas."""
        raw = await self._w3.eth.get_balance(self._address)
        return float(self._w3.from_wei(raw, "ether"))

    async def get_allowance(self, spender: str) -> float:
        """Check USDC.e allowance for a spender."""
        raw = await self._usdc_contract.functions.allowance(
            self._address,
            AsyncWeb3.to_checksum_address(spender),
        ).call()
        return raw / (10**USDC_E_DECIMALS)

    async def approve_usdc(self, spender: str, amount_usd: float | None = None) -> str:
        """Approve USDC.e spending. None = max approval."""
        if amount_usd is None:
            raw_amount = 2**256 - 1  # Max uint256
        else:
            raw_amount = int(amount_usd * (10**USDC_E_DECIMALS))

        spender_checksum = AsyncWeb3.to_checksum_address(spender)
        tx = await self._usdc_contract.functions.approve(
            spender_checksum, raw_amount
        ).build_transaction(
            {
                "from": self._address,
                "nonce": await self._w3.eth.get_transaction_count(self._address),
                "gas": 100_000,
                "gasPrice": await self._w3.eth.gas_price,
            }
        )
        signed = self._account.sign_transaction(tx)
        tx_hash = await self._w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = await self._w3.eth.wait_for_transaction_receipt(tx_hash)
        logger.info(f"USDC.e approval tx: {tx_hash.hex()}")
        return tx_hash.hex()

    async def is_connected(self) -> bool:
        return await self._w3.is_connected()
