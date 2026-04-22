"""
Risk Manager — Controles de risco do portfólio
"""
from loguru import logger
import yaml


class RiskManager:
    def __init__(self, config_path="configs/config.yaml"):
        with open(config_path) as f:
            cfg = yaml.safe_load(f)["risk"]
        self.max_position_size = cfg["max_position_size"]
        self.max_drawdown_pct = cfg["max_drawdown_pct"]
        self.max_daily_loss_pct = cfg["max_daily_loss_pct"]

    def check_position_size(self, position_value: float, portfolio_value: float) -> bool:
        pct = position_value / portfolio_value
        if pct > self.max_position_size:
            logger.warning(f"Posição {pct:.1%} excede limite de {self.max_position_size:.1%}")
            return False
        return True

    def check_daily_loss(self, daily_pnl: float, portfolio_value: float) -> bool:
        pct = abs(daily_pnl) / portfolio_value
        if daily_pnl < 0 and pct >= self.max_daily_loss_pct:
            logger.warning(f"Stop diário atingido: {pct:.1%}")
            return False
        return True

    def calc_position_size(self, portfolio_value: float, risk_per_trade: float,
                            stop_distance: float, price: float) -> int:
        """Calcula tamanho da posição com risco fixo."""
        risk_amount = portfolio_value * risk_per_trade
        qty = int(risk_amount / stop_distance)
        logger.info(f"Position sizing: {qty} unidades | Risco: ${risk_amount:.2f}")
        return qty
