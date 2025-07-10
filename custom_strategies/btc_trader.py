"""BTC Trader Strategy
This strategy buys dips or momentum on BTC and takes profits dynamically.
"""
import backtrader as bt
from strategies import BaseStrategy


class BTCTraderStrategy(BaseStrategy):
    """BTC trading strategy with dynamic profit targets."""

    params = (
        ('chunk_size', 100),
        ('max_allocation', 1000),
        ('atr_period', 14),
        ('momentum_period', 3),
        ('printlog', True),
    )

    def _initialize_indicators(self):
        self.atr = bt.indicators.ATR(self.data, period=self.params.atr_period)
        self.high24 = bt.indicators.Highest(self.data.high, period=24)
        self.low24 = bt.indicators.Lowest(self.data.low, period=24)
        self.avg24 = bt.indicators.SimpleMovingAverage(self.data.close, period=24)
        self.momentum = bt.indicators.Momentum(self.data.close, period=self.params.momentum_period)
        self.lots = []
        self.allocated = 0.0

    def should_buy(self) -> bool:
        return False

    def should_sell(self) -> bool:
        return False

    def get_buy_reason(self) -> str:
        return ""

    def get_sell_reason(self) -> str:
        return ""

    def _profit_target_pct(self) -> float:
        atr_pct = (self.atr[0] / self.data.close[0]) * 100
        return max(0.3, min(1.5, 0.3 + atr_pct))

    def next(self):
        if self.order:
            return

        price = self.data.close[0]

        # SELL conditions for open lots
        for lot in list(self.lots):
            target_price = lot['entry'] * (1 + lot['target_pct'] / 100)
            stop_price = lot['entry'] * 0.995
            if price >= target_price:
                self.log_sell_signal(price, f"Profit target {lot['target_pct']:.2f}%")
                self.log(f'SELL CREATE: Price: {price:.2f}')
                self.order = self.sell(size=lot['size'])
                self.lots.remove(lot)
                self.allocated -= lot['entry'] * lot['size']
                continue
            if price <= stop_price:
                self.log_sell_signal(price, 'Stop loss hit')
                self.log(f'SELL CREATE: Price: {price:.2f}')
                self.order = self.sell(size=lot['size'])
                self.lots.remove(lot)
                self.allocated -= lot['entry'] * lot['size']
                continue
            if self.momentum[0] < 0 and price > lot['entry']:
                self.log_sell_signal(price, 'Weak momentum')
                self.log(f'SELL CREATE: Price: {price:.2f}')
                self.order = self.sell(size=lot['size'])
                self.lots.remove(lot)
                self.allocated -= lot['entry'] * lot['size']

        if self.allocated >= self.params.max_allocation:
            return

        dip_condition = price < self.avg24[0]
        momentum_condition = price > self.data.close[-1] and price <= self.high24[0] * 0.98

        if dip_condition or momentum_condition:
            trade_value = min(self.params.chunk_size, self.params.max_allocation - self.allocated)
            size = trade_value / price
            target_pct = self._profit_target_pct()
            reason = 'Buy the dip' if dip_condition else 'Momentum play'
            self.log_buy_signal(price, reason)
            self.log(f'BUY CREATE: Price: {price:.2f}, Value: {trade_value:.2f}')
            self.order = self.buy(size=size)
            self.lots.append({'entry': price, 'size': size, 'target_pct': target_pct})
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

