"""
Trading Strategies Module
Contains plug-and-play trading strategies with signal logging
"""
import backtrader as bt
from abc import abstractmethod
from typing import Dict, Any
from signal_extractor import StrategySignalLogger


class BaseStrategy(bt.Strategy, StrategySignalLogger):
    """Base class for all trading strategies with signal logging"""
    
    params = (
        ('printlog', True),
    )
    
    def __init__(self):
        bt.Strategy.__init__(self)
        StrategySignalLogger.__init__(self)
        self.order = None
        self._execution_log = []  # Log execution prices
        self._initialize_indicators()
    
    @abstractmethod
    def _initialize_indicators(self):
        """Initialize strategy-specific indicators"""
        pass
    
    @abstractmethod
    def should_buy(self) -> bool:
        """Define buy condition"""
        pass
    
    @abstractmethod
    def should_sell(self) -> bool:
        """Define sell condition"""
        pass
    
    @abstractmethod
    def get_buy_reason(self) -> str:
        """Get reason for buy signal"""
        pass
    
    @abstractmethod
    def get_sell_reason(self) -> str:
        """Get reason for sell signal"""
        pass
    
    def log(self, txt: str, dt=None):
        """Logging function"""
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()}: {txt}')
    
    def notify_order(self, order):
        """Handle order notifications"""
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            # Log execution for extraction later
            execution_record = {
                'side': 'buy' if order.isbuy() else 'sell',
                'price': order.executed.price,
                'size': order.executed.size,
                'value': order.executed.value,
                'commission': order.executed.comm,
                'datetime': self.datas[0].datetime.datetime(0)
            }
            self._execution_log.append(execution_record)
            
            if order.isbuy():
                self.log(f'BUY EXECUTED: Price: {order.executed.price:.2f}, '
                        f'Size: {order.executed.size:.6f}, '
                        f'Cost: {order.executed.value:.2f}, '
                        f'Comm: {order.executed.comm:.2f}')
            else:
                self.log(f'SELL EXECUTED: Price: {order.executed.price:.2f}, '
                        f'Size: {order.executed.size:.6f}, '
                        f'Cost: {order.executed.value:.2f}, '
                        f'Comm: {order.executed.comm:.2f}')

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f'Order Canceled/Margin/Rejected - Status: {order.getstatusname()}')

        self.order = None
    
    def next(self):
        """Main strategy logic"""
        # Check if an order is pending
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # Not in market, check if we should buy
            if self.should_buy():
                # Calculate position size (use 95% of available cash)
                cash = self.broker.getcash()
                price = self.data.close[0]
                size = (cash * 0.95) / price

                # Log the buy signal
                reason = self.get_buy_reason()
                self.log_buy_signal(price, reason)
                
                self.log(f'BUY CREATE: Price: {price:.2f}, Size: {size:.6f}, Cash: {cash:.2f}')
                self.order = self.buy(size=size)
        else:
            # In market, check if we should sell
            if self.should_sell():
                price = self.data.close[0]
                
                # Log the sell signal
                reason = self.get_sell_reason()
                self.log_sell_signal(price, reason)
                
                self.log(f'SELL CREATE: Price: {price:.2f}')
                self.order = self.sell(size=self.position.size)
    
    def stop(self):
        """Called when strategy ends"""
        self.log(f'Strategy ended with portfolio value: {self.broker.getvalue():.2f}')


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


# Strategy registry for easy access
STRATEGIES = {
    'SMA Crossover': SMAStrategy,
    'RSI': RSIStrategy,
    'MACD': MACDStrategy,
    'Bollinger Bands': BollingerBandsStrategy
}


def get_available_strategies() -> Dict[str, type]:
    """Get all available strategies"""
    return STRATEGIES


def get_strategy_class(name: str) -> type:
    """Get strategy class by name"""
    return STRATEGIES.get(name)