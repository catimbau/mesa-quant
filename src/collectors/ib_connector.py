"""
Interactive Brokers Connector
Wrapper da TWS API usando ib_insync
"""
from loguru import logger
from ib_insync import IB, Stock, Future, Option, Contract
import yaml


class IBConnector:
    def __init__(self, config_path="configs/config.yaml"):
        with open(config_path) as f:
            cfg = yaml.safe_load(f)["interactive_brokers"]
        self.host = cfg["host"]
        self.port = cfg["port"]
        self.client_id = cfg["client_id"]
        self.account = cfg["account"]
        self.ib = IB()

    def connect(self) -> bool:
        try:
            self.ib.connect(self.host, self.port, clientId=self.client_id)
            logger.info(f"Conectado ao IB em {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar ao IB: {e}")
            return False

    def disconnect(self):
        self.ib.disconnect()
        logger.info("Desconectado do IB")

    def get_stock(self, symbol: str, exchange="SMART", currency="USD") -> Stock:
        contract = Stock(symbol, exchange, currency)
        self.ib.qualifyContracts(contract)
        return contract

    def get_future(self, symbol: str, expiry: str, exchange="CME") -> Future:
        """expiry formato: YYYYMM"""
        contract = Future(symbol, expiry, exchange)
        self.ib.qualifyContracts(contract)
        return contract

    def get_historical_data(self, contract: Contract, duration="1 Y",
                             bar_size="1 day", what_to_show="TRADES"):
        bars = self.ib.reqHistoricalData(
            contract, endDateTime="", durationStr=duration,
            barSizeSetting=bar_size, whatToShow=what_to_show,
            useRTH=True, formatDate=1
        )
        logger.info(f"{len(bars)} barras obtidas para {contract.symbol}")
        return bars

    def get_account_summary(self) -> dict:
        summary = self.ib.accountSummary(self.account)
        return {item.tag: item.value for item in summary}

    @property
    def is_connected(self) -> bool:
        return self.ib.isConnected()
