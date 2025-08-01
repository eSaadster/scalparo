"""
Trading Strategies Module
Contains plug-and-play trading strategies with signal logging
"""
import backtrader as bt
from typing import Dict, Any
from base_strategy import BaseStrategy


class SMAStrategy(BaseStrategy):
    """Simple Moving Average Crossover Strategy"""
    
    params = (
        ('sma_period', 15),
        ('printlog', True),
    )
    
    def _initialize_indicators(self):
        """Initialize SMA indicators"""
        self.sma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.sma_period
        )
        self.crossover = bt.indicators.CrossOver(self.data.close, self.sma)
    
    def should_buy(self) -> bool:
        """Buy when price crosses above SMA"""
        return self.crossover[0] > 0
    
    def should_sell(self) -> bool:
        """Sell when price crosses below SMA"""
        return self.crossover[0] < 0
    
    def get_buy_reason(self) -> str:
        """Get reason for buy signal"""
        return f"Price crossed above SMA({self.params.sma_period})"
    
    def get_sell_reason(self) -> str:
        """Get reason for sell signal"""
        return f"Price crossed below SMA({self.params.sma_period})"
    
    @classmethod
    def get_params(cls) -> Dict[str, Any]:
        """Get strategy parameters for UI"""
        return {
            'sma_period': {
                'type': 'int',
                'default': 15,
                'min': 5,
                'max': 200,
                'description': 'Simple Moving Average period'
            }
        }


class RSIStrategy(BaseStrategy):
    """RSI-based Trading Strategy"""
    
    params = (
        ('rsi_period', 14),
        ('rsi_upper', 70),
        ('rsi_lower', 30),
        ('printlog', True),
    )
    
    def _initialize_indicators(self):
        """Initialize RSI indicator"""
        self.rsi = bt.indicators.RelativeStrengthIndex(
            self.data.close, period=self.params.rsi_period
        )
    
    def should_buy(self) -> bool:
        """Buy when RSI is oversold"""
        return self.rsi[0] < self.params.rsi_lower
    
    def should_sell(self) -> bool:
        """Sell when RSI is overbought"""
        return self.rsi[0] > self.params.rsi_upper
    
    def get_buy_reason(self) -> str:
        """Get reason for buy signal"""
        return f"RSI oversold: {self.rsi[0]:.1f} < {self.params.rsi_lower}"
    
    def get_sell_reason(self) -> str:
        """Get reason for sell signal"""
        return f"RSI overbought: {self.rsi[0]:.1f} > {self.params.rsi_upper}"
    
    @classmethod
    def get_params(cls) -> Dict[str, Any]:
        """Get strategy parameters for UI"""
        return {
            'rsi_period': {
                'type': 'int',
                'default': 14,
                'min': 5,
                'max': 50,
                'description': 'RSI calculation period'
            },
            'rsi_upper': {
                'type': 'int',
                'default': 70,
                'min': 60,
                'max': 90,
                'description': 'RSI overbought threshold'
            },
            'rsi_lower': {
                'type': 'int',
                'default': 30,
                'min': 10,
                'max': 40,
                'description': 'RSI oversold threshold'
            }
        }


class MACDStrategy(BaseStrategy):
    """MACD Trading Strategy"""
    
    params = (
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
        ('printlog', True),
    )
    
    def _initialize_indicators(self):
        """Initialize MACD indicators"""
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.params.macd_fast,
            period_me2=self.params.macd_slow,
            period_signal=self.params.macd_signal
        )
        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
    
    def should_buy(self) -> bool:
        """Buy when MACD crosses above signal"""
        return self.crossover[0] > 0
    
    def should_sell(self) -> bool:
        """Sell when MACD crosses below signal"""
        return self.crossover[0] < 0
    
    def get_buy_reason(self) -> str:
        """Get reason for buy signal"""
        return f"MACD bullish crossover: MACD({self.macd.macd[0]:.4f}) > Signal({self.macd.signal[0]:.4f})"
    
    def get_sell_reason(self) -> str:
        """Get reason for sell signal"""
        return f"MACD bearish crossover: MACD({self.macd.macd[0]:.4f}) < Signal({self.macd.signal[0]:.4f})"
    
    @classmethod
    def get_params(cls) -> Dict[str, Any]:
        """Get strategy parameters for UI"""
        return {
            'macd_fast': {
                'type': 'int',
                'default': 12,
                'min': 5,
                'max': 50,
                'description': 'Fast EMA period'
            },
            'macd_slow': {
                'type': 'int',
                'default': 26,
                'min': 20,
                'max': 100,
                'description': 'Slow EMA period'
            },
            'macd_signal': {
                'type': 'int',
                'default': 9,
                'min': 5,
                'max': 20,
                'description': 'Signal line period'
            }
        }


class BollingerBandsStrategy(BaseStrategy):
    """Bollinger Bands Trading Strategy"""
    
    params = (
        ('bb_period', 20),
        ('bb_devfactor', 2.0),
        ('printlog', True),
    )
    
    def _initialize_indicators(self):
        """Initialize Bollinger Bands"""
        self.bb = bt.indicators.BollingerBands(
            self.data.close,
            period=self.params.bb_period,
            devfactor=self.params.bb_devfactor
        )
    
    def should_buy(self) -> bool:
        """Buy when price touches lower band"""
        return self.data.close[0] <= self.bb.lines.bot[0]
    
    def should_sell(self) -> bool:
        """Sell when price touches upper band"""
        return self.data.close[0] >= self.bb.lines.top[0]
    
    def get_buy_reason(self) -> str:
        """Get reason for buy signal"""
        return f"Price touched lower Bollinger Band: {self.data.close[0]:.2f} <= {self.bb.lines.bot[0]:.2f}"
    
    def get_sell_reason(self) -> str:
        """Get reason for sell signal"""
        return f"Price touched upper Bollinger Band: {self.data.close[0]:.2f} >= {self.bb.lines.top[0]:.2f}"
    
    @classmethod
    def get_params(cls) -> Dict[str, Any]:
        """Get strategy parameters for UI"""
        return {
            'bb_period': {
                'type': 'int',
                'default': 20,
                'min': 10,
                'max': 50,
                'description': 'Bollinger Bands period'
            },
            'bb_devfactor': {
                'type': 'float',
                'default': 2.0,
                'min': 1.0,
                'max': 3.0,
                'step': 0.1,
                'description': 'Standard deviation factor'
            }
        }

class FibonacciRetracementStrategy(BaseStrategy):
    """Fibonacci Retracement Trading Strategy"""

    params = (
        ('lookback', 50),
        ('printlog', True),
    )

    def _initialize_indicators(self):
        """Initialize Fibonacci levels"""
        self.highest = bt.indicators.Highest(self.data.high, period=self.params.lookback)
        self.lowest = bt.indicators.Lowest(self.data.low, period=self.params.lookback)
        diff = self.highest - self.lowest
        self.level382 = self.highest - diff * 0.382
        self.level618 = self.highest - diff * 0.618

    def _cross_above(self, level) -> bool:
        return self.data.close[-1] < level[-1] and self.data.close[0] > level[0]

    def _cross_below(self, level) -> bool:
        return self.data.close[-1] > level[-1] and self.data.close[0] < level[0]

    def should_buy(self) -> bool:
        """Buy when price crosses above 38.2% or 61.8% level"""
        return self._cross_above(self.level382) or self._cross_above(self.level618)

    def should_sell(self) -> bool:
        """Sell when price crosses below 38.2% or 61.8% level"""
        return self._cross_below(self.level382) or self._cross_below(self.level618)

    def get_buy_reason(self) -> str:
        """Get reason for buy signal"""
        if self._cross_above(self.level618):
            level = 61.8
        else:
            level = 38.2
        return f"Price crossed above Fibonacci {level}% level"

    def get_sell_reason(self) -> str:
        """Get reason for sell signal"""
        if self._cross_below(self.level618):
            level = 61.8
        else:
            level = 38.2
        return f"Price crossed below Fibonacci {level}% level"

    @classmethod
    def get_params(cls) -> Dict[str, Any]:
        """Get strategy parameters for UI"""
        return {
            'lookback': {
                'type': 'int',
                'default': 50,
                'min': 20,
                'max': 200,
                'description': 'Lookback period for Fibonacci levels',
            }
        }


class SimpleStrategy(BaseStrategy):
    """Zone based trend following strategy"""

    params = (
        # Chunk sizes for zones A, B and C respectively
        ('chunk_sizes', (150, 100, 50)),
        ('max_allocation', 1000),
        ('profit_target_percent', 0.5),
        ('atr_period', 14),
        ('weighted_period', 24),
        ('printlog', True),
    )

    def _initialize_indicators(self):
        """Initialize ATR and weighted average price indicators"""
        self.atr = bt.indicators.ATR(self.data, period=self.params.atr_period)
        weighted_close = (self.data.high + self.data.low + self.data.close * 2) / 4
        self.weighted_avg = bt.indicators.SimpleMovingAverage(
            weighted_close, period=self.params.weighted_period
        )

        self.lots = []  # track individual entry prices and sizes
        self.allocated = 0.0
        self.last_buy_time = None
        self.last_buy_zone = None

    def should_buy(self) -> bool:  # not used but required
        return False

    def should_sell(self) -> bool:  # not used but required
        return False

    def get_buy_reason(self) -> str:
        return ""

    def get_sell_reason(self) -> str:
        return ""

    def _pick_chunk_size(self, zone: str) -> float:
        """Return the appropriate trade chunk based on the current zone"""
        mapping = {'A': 0, 'B': 1, 'C': 2}
        idx = mapping.get(zone)
        if idx is None:
            return 0
        remaining = self.params.max_allocation - self.allocated
        size = self.params.chunk_sizes[idx]
        return size if size <= remaining else 0

    def next(self):
        if self.order:
            return

        price = self.data.close[0]

        # Check sell conditions for each open lot
        for lot in list(self.lots):
            target = lot['entry'] * (1 + self.params.profit_target_percent / 100)
            if price >= target:
                self.log_sell_signal(price, 'Profit target hit')
                self.log(f'SELL CREATE: Price: {price:.2f}')
                self.order = self.sell(size=lot['size'])
                self.lots.remove(lot)
                self.allocated -= lot['entry'] * lot['size']

        avg_price = self.weighted_avg[0]

        # Determine zone based on price vs weighted average
        if price >= avg_price * 0.99:
            zone = 'A'
        elif price >= avg_price * 0.97:
            zone = 'B'
        elif price >= avg_price * 0.95:
            zone = 'C'
        else:
            zone = 'D'

        dt = self.datas[0].datetime.datetime(0)

        # Cooldown logic
        cooldown_map = {'A': 1, 'B': 3, 'C': 6}
        cooldown = cooldown_map.get(zone, 0)
        if self.last_buy_time is not None and cooldown > 0:
            elapsed = (dt - self.last_buy_time).total_seconds() / 3600
            if elapsed < cooldown:
                return

        # Avoid multiple buys in same zone
        if self.last_buy_zone == zone and zone != 'D':
            return

        # Additional check for zone C bounce
        if zone == 'C':
            period = self.params.atr_period
            lookback = min(period, len(self))
            lows = [self.data.low[-i] for i in range(lookback)]
            min_low = min(lows)
            bounce = (price - min_low) / min_low * 100
            if bounce < 0.5:
                return

        if zone != 'D':
            trade_value = self._pick_chunk_size(zone)
            if trade_value > 0:
                size = trade_value / price
                self.log_buy_signal(price, f'Zone {zone} entry')
                self.log(
                    f'BUY CREATE: Zone {zone} Price: {price:.2f}, Value: {trade_value:.2f}'
                )
                self.order = self.buy(size=size)
                self.lots.append({'entry': price, 'size': size})
                self.allocated += trade_value


        self.last_buy_time = dt
        self.last_buy_zone = zone

# Load custom strategies after BaseStrategy definition to avoid circular imports
from custom_strategies.btc_trader import BTCTraderStrategy
from custom_strategies.multi_symbol_momentum import MultiSymbolMomentumStrategy

# Strategy registry for easy access
STRATEGIES = {
    'SMA Crossover': SMAStrategy,
    'RSI': RSIStrategy,
    'MACD': MACDStrategy,
    'Fibonacci Retracement': FibonacciRetracementStrategy,
    'Bollinger Bands': BollingerBandsStrategy,
    'Simple': SimpleStrategy,
    'BTC Trader': BTCTraderStrategy,
    'Multi-Symbol Momentum': MultiSymbolMomentumStrategy
}


def get_available_strategies() -> Dict[str, type]:
    """Get all available strategies"""
    return STRATEGIES


def get_strategy_class(name: str) -> type:
    """Get strategy class by name"""
    return STRATEGIES.get(name)
