"""BTC Trader Strategy.

This strategy buys BTC when price dips or shows upward momentum and
takes profit dynamically based on volatility.
"""
import backtrader as bt
from strategies import BaseStrategy


class BTCTraderStrategy(BaseStrategy):
    """BTC trading strategy with dynamic profit targets and stop losses."""

    params = (
        ('chunk_size', 100),
        ('max_allocation', 1000),
        ('atr_period', 14),
        ('momentum_period', 3),
        ('printlog', True),
    )

    def _initialize_indicators(self) -> None:
        """Set up indicators for 24h statistics and momentum."""
        self.atr = bt.indicators.ATR(self.data, period=self.params.atr_period)
        self.high24 = bt.indicators.Highest(self.data.high, period=24)
        self.low24 = bt.indicators.Lowest(self.data.low, period=24)
        self.avg24 = bt.indicators.SimpleMovingAverage(self.data.close, period=24)
        self.momentum = bt.indicators.Momentum(self.data.close, period=self.params.momentum_period)
        self.lots = []
        self.allocated = 0.0
        self._sell_reason = ""
        self._lot_to_sell = None

    def should_buy(self) -> bool:
        """Check if market conditions warrant a new buy."""
        price = self.data.close[0]
        dip = price < self.avg24[0]
        momentum = (
            price > self.data.close[-1]
            and price <= self.high24[0] * 0.98
        )
        return (
            (dip or momentum)
            and self.allocated < self.params.max_allocation
        )

    def should_sell(self) -> bool:
        """Check all open lots for sell signals."""
        price = self.data.close[0]
        for lot in self.lots:
            target = lot['entry'] * (1 + lot['target_pct'] / 100)
            stop = lot['entry'] * 0.995
            if price >= target:
                self._sell_reason = f"Profit target {lot['target_pct']:.2f}%"
                self._lot_to_sell = lot
                return True
            if price <= stop:
                self._sell_reason = 'Stop loss hit'
                self._lot_to_sell = lot
                return True
            if self.momentum[0] < 0 and price > lot['entry']:
                self._sell_reason = 'Weak momentum'
                self._lot_to_sell = lot
                return True
        return False

    def get_buy_reason(self) -> str:
        """Return reason for the current buy signal."""
        price = self.data.close[0]
        return 'Buy the dip' if price < self.avg24[0] else 'Momentum play'

    def get_sell_reason(self) -> str:
        """Return reason for the current sell signal."""
        return self._sell_reason

    def _profit_target_pct(self) -> float:
        """Calculate dynamic profit target based on volatility."""
        atr_pct = (self.atr[0] / self.data.close[0]) * 100
        return max(0.3, min(1.5, 0.3 + atr_pct))

    def next(self) -> None:
        if self.order:
            return

        if self.should_sell():
            price = self.data.close[0]
            lot = self._lot_to_sell
            self.log_sell_signal(price, self._sell_reason)
            self.log(f'SELL CREATE: Price: {price:.2f}')
            self.order = self.sell(size=lot['size'])
            self.lots.remove(lot)
            self.allocated -= lot['entry'] * lot['size']
            self._lot_to_sell = None
            return

        if self.should_buy():
            price = self.data.close[0]
            trade_value = min(
                self.params.chunk_size,
                self.params.max_allocation - self.allocated,
            )
            size = trade_value / price
            target_pct = self._profit_target_pct()
            reason = self.get_buy_reason()
            self.log_buy_signal(price, reason)
            self.log(
                f'BUY CREATE: Price: {price:.2f}, Value: {trade_value:.2f}'
            )
            self.order = self.buy(size=size)
            self.lots.append(
                {'entry': price, 'size': size, 'target_pct': target_pct}
            )
            self.allocated += trade_value

    @classmethod
    def get_params(cls) -> dict:
        return {
            'chunk_size': {
                'type': 'int',
                'default': 100,
                'min': 50,
                'max': 500,
                'description': 'Dollar value per trade',
            },
            'max_allocation': {
                'type': 'int',
                'default': 1000,
                'min': 100,
                'max': 5000,
                'description': 'Maximum capital allocation',
            },
            'atr_period': {
                'type': 'int',
                'default': 14,
                'min': 5,
                'max': 50,
                'description': 'ATR period',
            },
        }
